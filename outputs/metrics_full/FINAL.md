# What to take away from the results

## 1. Blends and LDA are the strongest default if “looks like the seed” matters

If your product story is “readers who liked *this* book should see **similar shelf DNA**,” **equal** and **LDA** are the evidence-backed leaders on the only **query-conditioned** relevance proxy we measured. The gap to **TF-IDF** is not trivial on a 0–1 scale. That does **not** prove user satisfaction—tags are noisy and incomplete—but it is the axis where the models separate most clearly.

## 2. NMF is the diversity play, not the precision play

**NMF** sits in the **middle** on genre overlap but **wins** on list spread. Use it when you want **exploration** or richer **serendipity-style** lists at the cost of slightly weaker tag alignment than the top two. **Diversity is not an unalloyed good**; random or irrelevant lists can score high on spread metrics.

## 3. TF-IDF is the tail-popularity (novelty) play, with the weakest tag match

**TF-IDF** is best if the goal is to surface **less reviewed** books (catalog tail) and you accept **lower genre overlap** and **more repeated authors** in the top-10 on average. Novelty differences across views are **real but small**; no method is hiding in the long tail only—differences are shifts in emphasis, not a different universe of books.

## 4. Practical bottom line

- Prefer **equal** or **LDA** as the **default** if the priority is **coherent, seed-aligned** lists.  
- Consider **NMF** when you want **more varied** adjacent recommendations and can accept **moderately lower** tag overlap.  
- Consider **TF-IDF** when you want **slightly more long-tail** exposure and can accept **weaker** tag overlap and **more author repetition** in the top slots.  

The models are **different knobs on the same catalog**, not a clear ordering from “bad” to “good.” The right choice is the one that matches how you want the product to behave—and that should be confirmed with **user-facing** metrics when you have them.
