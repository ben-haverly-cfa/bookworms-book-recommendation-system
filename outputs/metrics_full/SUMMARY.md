# Findings: full-corpus metrics (k = 10)

All numbers are **aggregates over 498,776 source works**. Scripts and definitions live under `scripts/metrics/` and the per-metric READMEs there.

---

## 1. Precision@k (genre overlap)

**Rule:** a neighbor counts if it shares **at least one** `genres_top` tag with the seed (see `README_precision_at_k.md`).

| View | Mean precision@10 |
|------|-------------------|
| v_recs_equal | **0.490** |
| v_recs_lda | 0.486 |
| v_recs_nmf | 0.445 |
| v_recs_tfidf | 0.420 |

**Takeaway:** **Equal-weight** and **LDA** blends surface slightly **more genre-aligned** neighbors on average than **TF-IDF** or **NMF**. This is a **metadata proxy**, not user truth, but it is **query-specific**.

---

## 2. Diversity@k

**Metrics:** (a) **consecutive genre distance** — mean of \(1 - \text{Jaccard}\) on `rec_genres_top` between adjacent ranks; (b) **author distinct ratio** — distinct normalized neighbor authors / 10.

| View | Mean consec. genre distance | Mean author distinct |
|------|----------------------------|----------------------|
| v_recs_nmf | **0.930** | **0.944** |
| v_recs_lda | 0.914 | 0.927 |
| v_recs_tfidf | 0.922 | 0.895 |
| v_recs_equal | 0.911 | 0.920 |

**Takeaway:** **NMF** produces the **highest** step-to-step genre churn and the **most distinct authors** on average; **equal-weight** is the **lowest** on consecutive genre distance. Diversity is **not** inherently good—it trades against tight topical fit—but it differentiates rankers on list spread.

---

## 3. Novelty@k (catalog tail)

**Metrics:** (a) **novelty_rarity** — mean of \(1 - \text{PERCENT\_RANK}(ratings\_count)\) over neighbors (higher ⇒ more tail); (b) **mean log popularity** — \(\mathrm{mean}(\ln(ratings\_count+1))\) (lower ⇒ more tail).

| View | Mean novelty_rarity | Mean log popularity |
|------|--------------------|---------------------|
| v_recs_tfidf | **0.511** | **4.537** |
| v_recs_nmf | 0.506 | 4.582 |
| v_recs_lda | 0.499 | 4.634 |
| v_recs_equal | 0.497 | 4.648 |

**Takeaway:** **TF-IDF** lists lean **slightly more** toward **less popular** (longer-tail) neighbors by both signals; **equal** and **LDA** lean **more head-heavy**. Differences are **modest** (novelty_rarity spans ~0.497–0.511); nothing is recommending only obscure books.

---

## Overall read

- **Genre-aligned recommendations:** **equal** ≈ **LDA** > **NMF** > **TF-IDF**.
- **List spread (genres + authors):** **NMF** most diverse; **equal** least on consecutive genre distance.
- **Popularity / tail:** **TF-IDF** most tail-leaning; **equal** and **LDA** most mainstream.

Choosing a variant is a **tradeoff**: e.g. equal-weight improves **genre overlap** vs TF-IDF but pulls recommendations toward **more popular** works and slightly **tighter** consecutive-genre paths than NMF.

---

*Generated from logs in this folder; re-run with the commands in `README.md` after rebuilding DuckDB or changing k.*
