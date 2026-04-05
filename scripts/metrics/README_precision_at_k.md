# Precision@k (`precision_at_k.py`)

## What this measures

For each **source work** (`src_work_id`), look at its top-**k** recommended neighbors (`rank_variant` 1…k). **Precision@k** is the fraction of those neighbors that count as **relevant** under a chosen rule, then we report the **mean and median** of that fraction over all evaluated sources.

There are no per-user labels in this project, so “relevance” is always a **proxy**.

## Relevance modes (`--mode`)

### `genre_overlap` (default)

A neighbor is **relevant** if its `rec_genres_top` shares **at least one** normalized tag with the seed’s `src_genres_top` (pipe-delimited shelf tags, same representation as the rest of the pipeline).

**Why this default:** It is **query-dependent**: a neighbor is “good” only if it looks like the seed in the same tag space users see in Goodreads-style metadata. It aligns better with “right kind of book for this seed” than a global rule like average rating.

### `high_rating`

A neighbor is **relevant** if `rec_average_rating > --min-rating` (default `4.0`), optionally gated by `--min-ratings-count` on the neighbor.

**Why you might use it:** It measures how often recommendations surface **generally well-liked** works. It is **not** personalized: the same threshold applies to every seed.

## Inputs

- DuckDB from `10_build_duckdb_for_tableau_v2.py` (default path: repo root `goodreads_work_v2.duckdb`).
- Views: `v_recs_tfidf`, `v_recs_lda`, `v_recs_nmf`, `v_recs_equal`.

## Usage

From the **repository root**, with `duckdb` installed:

```bash
python3 scripts/metrics/precision_at_k.py --view v_recs_tfidf --k 10
python3 scripts/metrics/precision_at_k.py --all-views --k 20 --mode high_rating --min-rating 4.0
python3 scripts/metrics/precision_at_k.py --view v_recs_equal --k 10 --sample-seeds 5000 --seed 42
```

## Interpretation

- Compare **ranking variants** (`--all-views`) at the same **k** and **mode**.
- **Median** precision highlights the typical seed; **mean** can be pulled by outliers.
- **Genre overlap** precision rewards lists that stay on-tag; **high_rating** precision rewards surfacing popular books regardless of fit to the seed.
