# Recommendation metrics (work-level)

Scripts in this folder evaluate **top-k neighbor lists** from DuckDB views `v_recs_*`, built by [`../10_build_duckdb_for_tableau_v2.py`](../10_build_duckdb_for_tableau_v2.py).

| Script | README |
|--------|--------|
| `precision_at_k.py` | [README_precision_at_k.md](README_precision_at_k.md) |
| `diversity_at_k.py` | [README_diversity_at_k.md](README_diversity_at_k.md) |
| `novelty_at_k.py` | [README_novelty_at_k.md](README_novelty_at_k.md) |

**Default database path:** `<repository root>/goodreads_work_v2.duckdb` (override with `--duckdb`).

**Dependency:** `duckdb` (see repo root `requirements.txt`).
