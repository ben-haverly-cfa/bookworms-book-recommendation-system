#!/usr/bin/env python3
"""
Intra-list diversity @k from DuckDB v_recs_* views. See README_diversity_at_k.md.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

import duckdb

_REPO = Path(__file__).resolve().parents[2]
_VIEWS = frozenset({"v_recs_tfidf", "v_recs_lda", "v_recs_nmf", "v_recs_equal"})
_WS = "'\\\\s+'"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Diversity@k for top-k neighbor lists (DuckDB).")
    p.add_argument("--duckdb", type=Path, default=_REPO / "goodreads_work_v2.duckdb")
    p.add_argument("--view", choices=sorted(_VIEWS), default="v_recs_tfidf")
    p.add_argument("--all-views", action="store_true")
    p.add_argument("--k", type=int, default=10)
    p.add_argument("--sample-seeds", type=int, default=0)
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


def _pick(sample_seeds: int, row_alias: str) -> tuple[str, str]:
    if sample_seeds <= 0:
        return "", ""
    lim = int(sample_seeds)
    cte = f"""
        , picked AS (
            SELECT src_work_id FROM (SELECT DISTINCT src_work_id FROM src_rows)
            ORDER BY random() LIMIT {lim}
        )"""
    join = f"INNER JOIN picked p ON {row_alias}.src_work_id = p.src_work_id"
    return cte, join


def query(view: str, k: int, sample_seeds: int) -> str:
    if view not in _VIEWS:
        raise ValueError(view)
    pick_cte, pick_join = _pick(sample_seeds, "t")
    ws = _WS
    return f"""
        WITH src_rows AS (
            SELECT src_work_id, rank_variant, rec_genres_top, rec_author_name
            FROM {view}
            WHERE rank_variant <= {int(k)}
        )
        {pick_cte}
        , tagged AS (
            SELECT
                t.src_work_id,
                t.rank_variant,
                list_filter(string_split(coalesce(t.rec_genres_top, ''), '|'), x -> trim(x) <> '') AS rg,
                NULLIF(
                    lower(trim(regexp_replace(coalesce(t.rec_author_name, ''), {ws}, ' ', 'g'))),
                    ''
                ) AS auth_norm
            FROM src_rows t
            {pick_join}
        )
        , pairs AS (
            SELECT
                a.src_work_id,
                len(list_intersect(a.rg, b.rg))::DOUBLE
                    / NULLIF(len(list_distinct(list_concat(a.rg, b.rg))), 0) AS jac
            FROM tagged a
            INNER JOIN tagged b
                ON a.src_work_id = b.src_work_id AND b.rank_variant = a.rank_variant + 1
        )
        , consec AS (
            SELECT
                src_work_id,
                AVG((1.0 - jac)) AS mean_consec_genre_dist
            FROM pairs
            WHERE jac IS NOT NULL
            GROUP BY src_work_id
        )
        , authors AS (
            SELECT
                src_work_id,
                COUNT(DISTINCT auth_norm)::DOUBLE / {float(k)} AS author_distinct_ratio
            FROM tagged
            GROUP BY src_work_id
        )
        , merged AS (
            SELECT
                a.src_work_id,
                c.mean_consec_genre_dist AS consec_div,
                a.author_distinct_ratio
            FROM authors a
            LEFT JOIN consec c USING (src_work_id)
        )
        SELECT
            COUNT(*)::BIGINT AS n_seeds,
            AVG(consec_div) AS mean_consecutive_genre_distance,
            quantile_cont(consec_div, 0.5) AS median_consecutive_genre_distance,
            AVG(author_distinct_ratio) AS mean_author_distinct_ratio,
            quantile_cont(author_distinct_ratio, 0.5) AS median_author_distinct_ratio
        FROM merged
        ;
    """


def _setseed(con: duckdb.DuckDBPyConnection, seed: int) -> None:
    f = (seed % 1_000_000) / 1_000_000.0 or 0.5
    con.execute(f"SELECT setseed({f});")


def run(con: duckdb.DuckDBPyConnection, view: str, args: argparse.Namespace) -> None:
    if args.sample_seeds > 0:
        _setseed(con, args.seed)
    q = query(view, args.k, args.sample_seeds)
    r = con.execute(q).fetchone()
    n = con.execute(f"SELECT COUNT(*) FROM {view}").fetchone()[0]
    print(f"=== {view}  (table rows {n:,}) ===")
    print(f"  k={args.k}  sample_seeds={args.sample_seeds or 'all'}")
    if r:
        ns, m_cgd, med_cgd, m_adr, med_adr = r
        print(f"  seeds: {ns:,}")
        print(f"  consecutive_genre_distance  mean={m_cgd:.6f}  median={med_cgd:.6f}")
        print(f"  author_distinct_ratio       mean={m_adr:.6f}  median={med_adr:.6f}")
    print()


def main() -> None:
    args = parse_args()
    if args.k < 2:
        print("error: use k >= 2 for consecutive-genre diversity", file=sys.stderr)
        sys.exit(1)
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
