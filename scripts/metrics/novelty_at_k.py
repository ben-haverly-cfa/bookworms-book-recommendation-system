#!/usr/bin/env python3
"""
Novelty @k from DuckDB v_recs_* + v_works. See README_novelty_at_k.md.
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
    p = argparse.ArgumentParser(description="Novelty@k from global popularity stats (DuckDB).")
    p.add_argument("--duckdb", type=Path, default=_REPO / "goodreads_work_v2.duckdb")
    p.add_argument("--view", choices=sorted(_VIEWS), default="v_recs_tfidf")
    p.add_argument("--all-views", action="store_true")
    p.add_argument("--k", type=int, default=10)
    p.add_argument("--sample-seeds", type=int, default=0)
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


def _pick(sample_seeds: int) -> tuple[str, str]:
    if sample_seeds <= 0:
        return "", ""
    lim = int(sample_seeds)
    cte = f"""
        , picked AS (
            SELECT src_work_id FROM (SELECT DISTINCT src_work_id FROM src_rows)
            ORDER BY random() LIMIT {lim}
        )"""
    join = "INNER JOIN picked p ON r.src_work_id = p.src_work_id"
    return cte, join


def query(view: str, k: int, sample_seeds: int) -> str:
    if view not in _VIEWS:
        raise ValueError(view)
    pick_cte, pick_join = _pick(sample_seeds)
    return f"""
        WITH pop AS (
            SELECT
                work_id,
                COALESCE(ratings_count, 0)::BIGINT AS rc,
                PERCENT_RANK() OVER (ORDER BY COALESCE(ratings_count, 0) ASC) AS pr_low_is_rare
            FROM v_works
        )
        , src_rows AS (
            SELECT src_work_id, rec_work_id, rank_variant
            FROM {view}
            WHERE rank_variant <= {int(k)}
        )
        {pick_cte}
        , recs AS (
            SELECT r.* FROM src_rows r {pick_join}
        )
        , scored AS (
            SELECT
                r.src_work_id,
                (1.0 - COALESCE(p.pr_low_is_rare, 0.0)) AS rarity_score,
                LN(COALESCE(p.rc, 0) + 1.0) AS log_pop
            FROM recs r
            LEFT JOIN pop p ON p.work_id = r.rec_work_id
        )
        , per_seed AS (
            SELECT
                src_work_id,
                AVG(rarity_score) AS mean_rarity,
                AVG(log_pop) AS mean_log_pop
            FROM scored
            GROUP BY src_work_id
        )
        SELECT
            COUNT(*)::BIGINT AS n_seeds,
            AVG(mean_rarity) AS mean_novelty_rarity,
            quantile_cont(mean_rarity, 0.5) AS median_novelty_rarity,
            AVG(mean_log_pop) AS mean_log_popularity,
            quantile_cont(mean_log_pop, 0.5) AS median_log_popularity
        FROM per_seed
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
        ns, m_nr, med_nr, m_lp, med_lp = r
        print(f"  seeds: {ns:,}")
        print(f"  novelty_rarity (higher=more tail)     mean={m_nr:.6f}  median={med_nr:.6f}")
        print(f"  mean_log_popularity (lower=more tail) mean={m_lp:.6f}  median={med_lp:.6f}")
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
