#!/usr/bin/env python3
"""
Precision@k from DuckDB v_recs_* views. See README_precision_at_k.md.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

import duckdb

_REPO = Path(__file__).resolve().parents[2]
_VIEWS = frozenset({"v_recs_tfidf", "v_recs_lda", "v_recs_nmf", "v_recs_equal"})


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Precision@k for work-level recommendations (DuckDB).")
    p.add_argument("--duckdb", type=Path, default=_REPO / "goodreads_work_v2.duckdb")
    p.add_argument("--view", choices=sorted(_VIEWS), default="v_recs_tfidf")
    p.add_argument("--all-views", action="store_true")
    p.add_argument("--k", type=int, default=10)
    p.add_argument(
        "--mode",
        choices=("genre_overlap", "high_rating"),
        default="genre_overlap",
        help="genre_overlap: any shared genres_top tag vs seed; high_rating: rec_average_rating > threshold.",
    )
    p.add_argument("--min-rating", type=float, default=4.0, help="Used when --mode high_rating.")
    p.add_argument(
        "--min-ratings-count",
        type=int,
        default=0,
        help="When mode=high_rating, also require rec_ratings_count >= this (0 = off).",
    )
    p.add_argument("--sample-seeds", type=int, default=0)
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


def _pick(sample_seeds: int) -> tuple[str, str]:
    if sample_seeds <= 0:
        return "", ""
    lim = int(sample_seeds)
    return (
        f"""
        , picked AS (
            SELECT src_work_id FROM (SELECT DISTINCT src_work_id FROM src_rows)
            ORDER BY random() LIMIT {lim}
        )""",
        "INNER JOIN picked p ON b.src_work_id = p.src_work_id",
    )


def hit_genre_overlap() -> str:
    return """
        CASE
            WHEN len(list_intersect(
                list_filter(string_split(coalesce(base.src_genres_top, ''), '|'), x -> trim(x) <> ''),
                list_filter(string_split(coalesce(base.rec_genres_top, ''), '|'), x -> trim(x) <> '')
            )) > 0 THEN 1
            ELSE 0
        END
    """


def hit_high_rating(min_rating: float, min_rc: int) -> str:
    return f"""
        CASE
            WHEN base.rec_average_rating IS NULL THEN 0
            WHEN base.rec_average_rating <= {float(min_rating)} THEN 0
            WHEN {int(min_rc)} > 0
                AND (base.rec_ratings_count IS NULL OR base.rec_ratings_count < {int(min_rc)})
            THEN 0
            ELSE 1
        END
    """


def query(view: str, k: int, mode: str, min_rating: float, min_rc: int, sample_seeds: int) -> str:
    if view not in _VIEWS:
        raise ValueError(view)
    hit = hit_genre_overlap() if mode == "genre_overlap" else hit_high_rating(min_rating, min_rc)
    pick_cte, pick_join = _pick(sample_seeds)
    return f"""
        WITH src_rows AS (
            SELECT * FROM {view} WHERE rank_variant <= {int(k)}
        )
        {pick_cte}
        , base AS (
            SELECT b.* FROM src_rows b {pick_join}
        )
        , per_seed AS (
            SELECT
                src_work_id,
                COUNT(*)::BIGINT AS n_rec,
                SUM({hit})::DOUBLE AS hits
            FROM base
            GROUP BY src_work_id
        )
        SELECT
            COUNT(*)::BIGINT AS n_seeds,
            SUM(CASE WHEN n_rec < {int(k)} THEN 1 ELSE 0 END)::BIGINT AS short_lists,
            AVG(hits / {float(k)}) AS mean_precision,
            quantile_cont(hits / {float(k)}, 0.5) AS median_precision
        FROM per_seed
        WHERE n_rec > 0
        ;
    """


def _setseed(con: duckdb.DuckDBPyConnection, seed: int) -> None:
    f = (seed % 1_000_000) / 1_000_000.0 or 0.5
    con.execute(f"SELECT setseed({f});")


def run(con: duckdb.DuckDBPyConnection, view: str, args: argparse.Namespace) -> None:
    if args.sample_seeds > 0:
        _setseed(con, args.seed)
    q = query(view, args.k, args.mode, args.min_rating, args.min_ratings_count, args.sample_seeds)
    r = con.execute(q).fetchone()
    n = con.execute(f"SELECT COUNT(*) FROM {view}").fetchone()[0]
    print(f"=== {view}  (table rows {n:,}) ===")
    print(f"  k={args.k}  mode={args.mode}  sample_seeds={args.sample_seeds or 'all'}")
    if args.mode == "high_rating":
        print(f"  min_rating (>): {args.min_rating}  min_ratings_count: {args.min_ratings_count or 'off'}")
    if r:
        ns, sh, mp, med = r
        print(f"  seeds: {ns:,}  lists_with_fewer_than_k: {sh:,}")
        print(f"  mean_precision@{args.k}: {mp:.6f}")
        print(f"  median_precision@{args.k}: {med:.6f}")
    print()


def main() -> None:
    args = parse_args()
    if not args.duckdb.is_file():
        print(f"error: missing {args.duckdb}", file=sys.stderr)
        sys.exit(1)
    views: Sequence[str] = sorted(_VIEWS) if args.all_views else (args.view,)
    con = duckdb.connect(str(args.duckdb), read_only=True)
    try:
        for v in views:
            run(con, v, args)
    finally:
        con.close()


if __name__ == "__main__":
    main()
