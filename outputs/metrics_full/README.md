# Full-corpus metrics run

**Database:** `goodreads_work_v2.duckdb` at repository root  
**Scope:** All **498,776** seed works with full top-**10** lists (`rank_variant` 1–10) per `v_recs_*` view. No `--sample-seeds`.

**Logs:**

| File | Script / mode |
|------|----------------|
| `precision_genre_overlap_k10.log` | `metrics/precision_at_k.py --all-views --k 10 --mode genre_overlap` |
| `precision_high_rating_k10.log` | `metrics/precision_at_k.py --all-views --k 10 --mode high_rating --min-rating 4.0` |
| `diversity_k10.log` | `metrics/diversity_at_k.py --all-views --k 10` |
| `novelty_k10.log` | `metrics/novelty_at_k.py --all-views --k 10` |

See **`SUMMARY.md`** in this folder for interpretation.
