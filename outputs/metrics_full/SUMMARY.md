# Findings: full-corpus metrics (k = 10)

All numbers are **aggregates over 498,776 source works**. Scripts and definitions live under `scripts/metrics/` and the per-metric READMEs there.

---

## 1. Precision@k (genre overlap, default)

**Rule:** a neighbor counts if it shares **at least one** `genres_top` tag with the seed (see `README_precision_at_k.md`).

| View | Mean precision@10 | Median precision@10 |
|------|-------------------|---------------------|
| v_recs_equal | **0.490** | **0.60** |
| v_recs_lda | 0.486 | 0.60 |
| v_recs_nmf | 0.445 | 0.50 |
| v_recs_tfidf | 0.420 | 0.40 |

**Takeaway:** **Equal-weight** and **LDA** blends surface slightly **more genre-aligned** neighbors on average than **TF-IDF** or **NMF**. The **median** tells the same story for half of seeds: equal/LDA more often sit at 60% of slots sharing a genre tag with the seed; TF-IDF’s median is 40%. This is a **metadata proxy**, not user truth, but it is **query-specific** (unlike rating-only precision).

---

## 2. Precision@k (high average rating)

**Rule:** neighbor `rec_average_rating > 4.0` (no minimum ratings count).

| View | Mean precision@10 | Median precision@10 |
|------|-------------------|---------------------|
| v_recs_equal | 0.411 | 0.40 |
| v_recs_tfidf | 0.410 | 0.40 |
| v_recs_lda | 0.407 | 0.40 |
| v_recs_nmf | 0.407 | 0.40 |

**Takeaway:** Under this **global** popularity rule, all four rankers are **very close** (~41% mean, median 0.4). Content-based ordering does not strongly separate “fraction of neighbors above 4 stars” at k=10; differences show up more clearly under **genre overlap** than under **rating**.

---

## 3. Diversity@k

**Metrics:** (a) **consecutive genre distance** — mean of \(1 - \text{Jaccard}\) on `rec_genres_top` between adjacent ranks; (b) **author distinct ratio** — distinct normalized neighbor authors / 10.

| View | Mean consec. genre distance | Median consec. genre distance | Mean author distinct | Median author distinct |
|------|----------------------------|-------------------------------|----------------------|-------------------------|
| v_recs_nmf | **0.930** | **0.953** | **0.944** | 1.00 |
| v_recs_lda | 0.914 | 0.938 | 0.927 | 1.00 |
| v_recs_tfidf | 0.922 | 0.953 | 0.895 | 1.00 |
| v_recs_equal | 0.911 | 0.938 | 0.920 | 1.00 |

**Takeaway:** **NMF** produces the **highest** step-to-step genre churn and the **most distinct authors** on average; **equal-weight** is the **lowest** on consecutive genre distance. **Median author distinct is 1.0** for all views (for most seeds, all ten neighbors are different authors). Diversity is **not** inherently good—it trades against tight topical fit—but it differentiates rankers more than the rating-based precision line.

---

## 4. Novelty@k (catalog tail)

**Metrics:** (a) **novelty_rarity** — mean of \(1 - \text{PERCENT\_RANK}(ratings\_count)\) over neighbors (higher ⇒ more tail); (b) **mean log popularity** — \(\mathrm{mean}(\ln(ratings\_count+1))\) (lower ⇒ more tail).

| View | Mean novelty_rarity | Median novelty_rarity | Mean log popularity | Median log popularity |
|------|--------------------|-----------------------|---------------------|------------------------|
| v_recs_tfidf | **0.511** | **0.509** | **4.537** | **4.492** |
| v_recs_nmf | 0.506 | 0.500 | 4.582 | 4.572 |
| v_recs_lda | 0.499 | 0.487 | 4.634 | 4.657 |
| v_recs_equal | 0.497 | 0.487 | 4.648 | 4.655 |

**Takeaway:** **TF-IDF** lists lean **slightly more** toward **less popular** (longer-tail) neighbors by both signals; **equal** and **LDA** lean **more head-heavy**. Differences are **modest** (novelty_rarity spans ~0.497–0.511); nothing is recommending only obscure books.

---

## Overall read

- **Genre-aligned recommendations:** **equal** ≈ **LDA** > **NMF** > **TF-IDF**.
- **“Bestseller-ish” neighbors (>4★):** all four **similar**.
- **List spread (genres + authors):** **NMF** most diverse; **equal** least on consecutive genre distance.
- **Popularity / tail:** **TF-IDF** most tail-leaning; **equal** and **LDA** most mainstream.

Choosing a variant is a **tradeoff**: e.g. equal-weight improves **genre overlap** vs TF-IDF but pulls recommendations toward **more popular** works and slightly **tighter** consecutive-genre paths than NMF.

---

*Generated from logs in this folder; re-run with the commands in `README.md` after rebuilding DuckDB or changing k.*
