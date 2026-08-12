---
name: vae-dsaa-known-defects
description: "The KL/latent-space failure and ablation-fairness problems in VAE-With-DSAA, with the evidence that establishes each."
metadata: 
  node_type: memory
  type: project
  originSessionId: fc09e84b-ca85-4491-bc91-8da1dfc27495
  modified: 2026-08-10T08:47:56.055Z
---

Defects in `d:\Research\VAE-With-DSAA` as of 2026-08-10, from the executed v2 notebooks
(`notebooks/v2/*.ipynb` — the .py files mirror the code but not the runtime logs):

1. **Neither configuration is a working VAE — two opposite KL failures.**
   *Config A:* `kl_loss` falls to 0.0847 by epoch 11 and stays there for 39 epochs. Free
   Bits is 0.01 × 8 dims = 0.0800, so KL is pinned at the clamp — total posterior collapse.
   *Configs B/C/D:* all three log `Epoch 6: early stopping / Restoring model weights from
   the end of the best epoch: 1.` β = epoch/10, so epoch 1 is β = 0 — one epoch of plain
   autoencoder. Corroborated by `kl_mean` 132.8 / 255.3 in `stratified_config.json`.
   This breaks DSAA Signal 2 and fails NFR3 (98% collapse prevention), one of only two
   numeric targets in the proposal.

2. **Free Bits at 0.01 is ~50× too small.** The code comment records lowering it from 0.1
   to 0.01 in response to observed collapse. That is backwards — Free Bits is a floor that
   keeps dimensions active, so lowering it removes the protection. Literature value
   (Kingma et al. NeurIPS 2016, already ref [9]) is 0.5–2 nats/dim.

3. **Config D leaks its own tuning split.** It evaluates on the full 2,770,409 rows with all
   8,213 frauds, while B and C correctly use the 70% test split.

4. **Config A vs B/C/D is not controlled** — differs in scoring function, threshold metric
   (F1 vs F2), training schedule and scaler simultaneously.

5. **Signal-2 zero-padding encodes transaction type.** TRANSFER (8 latent dims) is
   zero-padded to 16, so every TRANSFER fingerprint has 8 exact zeros no CASH_OUT row has.
   All 19 DBSCAN clusters are 100% single-type — the typologies may be recovering the
   stratification, not fraud behaviour.

**Why:** items 1–2 undermine the DSAA novelty claim itself; 3–5 undermine the ablation that
validates it.

**How to apply:** fix 1 and 2 before rerunning anything downstream — Signal 2, fingerprints
and typologies all depend on the latent space. Related: [[deepsentinel-vae-dsaa-project]],
[[vae-dsaa-benchmarking-position]].
