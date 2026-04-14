# Precision@k (`precision_at_k.py`)

## What this measures

For each **source work** (`src_work_id`), look at its top-**k** recommended neighbors (`rank_variant` 1…k). **Precision@k** is the fraction of those neighbors that count as **relevant** under the rule below, then we report the **mean** of that fraction over all evaluated sources.

There are no per-user labels in this project, so “relevance” is always a **proxy**.

## Relevance rule (genre overlap)

A neighbor is **relevant** if its `rec_genres_top` shares **at least one** normalized tag with the seed’s `src_genres_top` (pipe-delimited shelf tags, same representation as the rest of the pipeline).

**Why this definition:** It is **query-dependent**: a neighbor is “good” only if it looks like the seed in the same tag space users see in Goodreads-style metadata.

## Inputs

- DuckDB from `10_build_duckdb_for_tableau_v2.py` (default path: repo root `goodreads_work_v2.duckdb`).
- Views: `v_recs_tfidf`, `v_recs_lda`, `v_recs_nmf`, `v_recs_equal`.

## Usage

From the **repository root**, with `duckdb` installed:

```bash
python3 scripts/metrics/precision_at_k.py --view v_recs_tfidf --k 10
python3 scripts/metrics/precision_at_k.py --all-views --k 20
python3 scripts/metrics/precision_at_k.py --view v_recs_equal --k 10 --sample-seeds 5000 --seed 42
```

## Interpretation

- Compare **ranking variants** (`--all-views`) at the same **k**.
- **Mean** precision summarizes average on-tag rate across seeds.
- Precision rewards lists that stay **on-tag** relative to the seed’s genres.

