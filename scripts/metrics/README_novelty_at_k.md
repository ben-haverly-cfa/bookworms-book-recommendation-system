# Novelty@k (`novelty_at_k.py`)

## What this measures

**Novelty** (without user click data) is approximated from **how niche each recommended work is in the global catalog**. For every neighbor in positions 1…k, we attach a **popularity profile** from `v_works`, then average within each source list and report **means over sources**.

### Primary: rarity score (higher = more novel / more tail)

On `v_works`, compute `PERCENT_RANK()` over `ratings_count` **ascending** (low counts = rare books get low percentile ranks). For each neighbor:

\[
\text{rarity\_score} = 1 - \text{PERCENT\_RANK}
\]

So **bestsellers** (large `ratings_count`) sit near the top of the percentile scale and get a **low** score; **obscure** works get a **high** score. We report the **mean** of this score over the k neighbors (`novelty_rarity`).

### Secondary: mean log popularity (lower = more tail)

For each neighbor we also take \(\ln(\text{ratings\_count} + 1)\) from the same join and average over k. **Smaller** averages indicate lists tilt toward **less-reviewed** books.

**Interpretation:** These are **catalog-frequency** notions of novelty, not “surprising to this user.” They answer: “Am I mostly recommending **head** or **tail** books?”

## Inputs

- Same DuckDB and `v_recs_*` views as the other metric scripts.
- **`v_works`** must exist (built by `10_build_duckdb_for_tableau_v2.py`). Neighbors join on `rec_work_id = v_works.work_id`. Missing joins are treated as popularity zero for the percentile side (conservative).

## Usage

```bash
python3 scripts/metrics/novelty_at_k.py --view v_recs_lda --k 10
python3 scripts/metrics/novelty_at_k.py --all-views --k 20 --sample-seeds 5000
```

## Caveats

- **Tail ≠ quality:** obscure books can be obscure for a reason.
- **Ties:** many works share similar `ratings_count`; `PERCENT_RANK` spreads them in a simple way that may not match a true “global rank.”
- Novelty here does **not** use embedding distance from the seed; combining with similarity or precision metrics shows the tradeoff.
