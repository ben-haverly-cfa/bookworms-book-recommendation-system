# Diversity@k (`diversity_at_k.py`)

## What this measures

For each source work, we look at the **top-k recommended neighbors only** (not the seed). **Diversity** here means “how different those neighbors are from **each other**,” aggregated over all sources (mean and median).

We report two complementary signals:

### 1. Consecutive genre distance

Neighbors are ordered by `rank_variant`. For each adjacent pair \((i, i+1)\), we take the **Jaccard similarity** of their `rec_genres_top` tag sets (pipe-split shelves), then use **one minus similarity** as a distance. The score for a source is the **average** of these distances across the \(k-1\) adjacent pairs.

**Why this shape:** Full pairwise diversity over all \(\binom{k}{2}\) neighbor pairs is accurate but very expensive at large \(k\) on millions of seeds. Consecutive pairs track how much the list **changes as you move down the ranking** with only \(O(k)\) work per source—enough to compare rankers fairly at the same \(k\).

**Interpretation:** Higher values mean neighboring slots in the list tend to jump to **different genre mixes**. Very low values mean the top-k is **genre-homogeneous** step to step.

### 2. Author distinct ratio

\(\text{distinct normalized neighbor authors} / k\)

Author strings are compared after lowercasing, trimming, and collapsing internal whitespace (`regexp_replace` on runs of spaces).

**Interpretation:** Higher values mean the list spans **more unique authors**; low values mean a few authors dominate the top-k (often sequels or same pen name).

**Requirement:** Use **`k >= 2`** so the consecutive-genre path exists. (The script exits with an error if `k < 2`.)

## Inputs

- DuckDB from `10_build_duckdb_for_tableau_v2.py` (default: repo root `goodreads_work_v2.duckdb`).
- Views: `v_recs_tfidf`, `v_recs_lda`, `v_recs_nmf`, `v_recs_equal`.

## Usage

```bash
python3 scripts/metrics/diversity_at_k.py --view v_recs_tfidf --k 10
python3 scripts/metrics/diversity_at_k.py --all-views --k 10 --sample-seeds 8000 --seed 42
```

## Caveats

- Genre tags are **noisy** crowd shelves; distance is a proxy, not a semantic embedding distance.
- **Diversity is not “good” by itself:** random lists can look diverse but irrelevant. Read alongside precision-style metrics.
