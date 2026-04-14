## Testbed

**Testbed.** Evaluation is offline on DuckDB **`goodreads_work_v2.duckdb`** (repo root), built for Tableau-style analytics. Recommendations are read from views **`v_recs_tfidf`**, **`v_recs_lda`**, **`v_recs_nmf`**, and **`v_recs_equal`**. Each view holds **24,938,800** rows (seed × ranked neighbor). We aggregate over **all 498,776** seed works, use **k = 10** (`rank_variant` 1–10), and **do not** subsample seeds (`sample_seeds=all` in the logs). Scripts live under `scripts/metrics/`; definitions are in the per-metric READMEs referenced from `SUMMARY.md`.

**Questions the experiments are designed to answer**

1. **Relevance proxy:** Which ranker puts more neighbors in the top-10 that **share at least one** `genres_top` shelf tag with the seed (**mean** precision over seeds)?
2. **List diversity:** Which ranker’s top-10 **changes genre mix more** between adjacent slots, and which shows **more distinct neighbor authors** (means over seeds)?
3. **Catalog novelty / popularity:** Which ranker’s neighbors skew toward **globally rarer** works (low `ratings_count` tail) vs **more-reviewed** “head” books (means over seeds)?

---

## Detailed experiments

**Procedure.** Three batch runs are archived in this folder (`README.md`): `precision_at_k.py --all-views --k 10`, `diversity_at_k.py --all-views --k 10`, `novelty_at_k.py --all-views --k 10`. Raw numbers below match **`precision_genre_overlap_k10.log`**, **`diversity_k10.log`**, and **`novelty_k10.log`**.

### Precision@10 (genre overlap)

| View | mean@10 |
|------|---------|
| v_recs_equal | 0.489818 |
| v_recs_lda | 0.486126 |
| v_recs_nmf | 0.445050 |
| v_recs_tfidf | 0.419898 |

- **Ordering** on mean precision is **equal > LDA > NMF > TF-IDF**.
- **TF-IDF** is **~7 points** (absolute) behind LDA on mean—material on a 0–1 scale.
- **NMF** is clearly **between** the blend/topic leaders and TF-IDF.
- Every view reports **`lists_with_fewer_than_k: 0`**: stored top-10 lists are **complete** for all seeds in this snapshot.
- Precision is a **metadata proxy** (crowd tags), not user truth, but it is **seed-conditioned**, unlike a global popularity rule.

### Diversity@10

| View | consecutive genre distance (mean) | author distinct ratio (mean) |
|------|-----------------------------------|-------------------------------|
| v_recs_nmf | 0.929900 | 0.943580 |
| v_recs_tfidf | 0.921664 | 0.894576 |
| v_recs_lda | 0.913974 | 0.926593 |
| v_recs_equal | 0.911460 | 0.920224 |

- **Consecutive genre distance** (average of \(1 - \text{Jaccard}\) on `rec_genres_top` between **adjacent** ranks): **NMF** is highest (**~0.93**), **equal** lowest (**~0.91**); lists **step through genre space** most abruptly under NMF.
- **Author distinct ratio** (distinct normalized authors / 10): **NMF** leads on the **mean**; **TF-IDF is lowest (~0.895)**—more **author repetition** in the top-10 on average despite fairly high genre churn.
- **Diversity is not “good” by itself** (random lists can be diverse); read next to precision.

### Novelty@10 (catalog tail)

| View | novelty_rarity (mean) | mean_log_popularity (mean) |
|------|----------------------|----------------------------|
| v_recs_tfidf | 0.511033 | 4.536704 |
| v_recs_nmf | 0.505806 | 4.581715 |
| v_recs_lda | 0.498823 | 4.633850 |
| v_recs_equal | 0.497163 | 4.647811 |

- **`novelty_rarity`** (higher ⇒ more tail): **TF-IDF** is highest, **equal** lowest; **NMF** is closer to TF-IDF than to equal.
- **`mean_log_popularity`** (lower ⇒ more tail): **TF-IDF** is lowest; **equal** is highest—**head-heavier** neighbors when blending equally.
- The **absolute spread** on `novelty_rarity` mean is only **~0.014** across views; effects are **consistent but modest**—no variant recommends only obscure books.
- Novelty here is **catalog frequency**, not “surprising to this user,” and **tail ≠ quality**.

### Cross-cutting observations

- **Equal ≈ LDA** on **genre precision** (means within **~0.004**); both beat **NMF** and **TF-IDF** decisively.
- **Precision vs diversity tension:** **NMF** best on diversity means, **mid** on precision; **equal** best on precision, **lowest** consecutive genre distance.
- **Precision vs novelty tension:** **TF-IDF** best tail novelty, **worst** genre overlap; **equal** best precision, **most mainstream** neighbors.
- **Fair comparison:** same **k**, same seeds, same DuckDB build—differences are due to **ranking variant**, not sample size or missing ranks in this run.

---

## How did you evaluate your approaches?

On **`goodreads_work_v2.duckdb`**, we scored **all 498,776** seed works using full top-**10** lists from **`v_recs_tfidf`**, **`v_recs_lda`**, **`v_recs_nmf`**, and **`v_recs_equal`** (no subsampling). Three offline metrics from `outputs/metrics_full`: **precision@10** (genre overlap: neighbor shares ≥1 `genres_top` tag with the seed), **diversity@10** (consecutive \(1-\)Jaccard genre distance between adjacent ranks; distinct-author ratio), **novelty@10** (catalog tail via `novelty_rarity` and mean \(\ln(\text{ratings\_count}+1)\) on neighbors). We report **means** over seeds. No user clicks or human labels—metadata and catalog popularity only.

## What are the results?

**Precision@10 (mean):** equal **0.490**, LDA **0.486**, NMF **0.445**, TF-IDF **0.420**. **Diversity (means):** NMF highest consecutive genre distance (**~0.93**) and author distinct ratio (**~0.94**); equal lowest on genre distance (**~0.91**). **Novelty (means):** TF-IDF most tail-leaning (**novelty_rarity ~0.51**, lowest **mean_log_popularity ~4.54**); equal most head-leaning (**rarity ~0.50**, **~4.65** log popularity). All lists were complete at \(k=10\) (`lists_with_fewer_than_k: 0`).

## How do your methods compare to other methods?

The four views are **the comparators** (single-signal vs blends vs topic models). **Equal and LDA** win on **genre overlap**; **NMF** wins on **intra-list diversity**; **TF-IDF** favors **rarer books** but **worst genre overlap** and **fewer distinct authors** on average. **NMF** sits between **equal/LDA** and **TF-IDF** on precision; **novelty differences are small** (~0.497–0.511 on mean rarity) but **consistent**. Overall: **better tag fit (equal/LDA)** trades off against **more tail / more churn (TF-IDF/NMF)** depending on which axis matters.
