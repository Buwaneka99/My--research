---
name: vae-dsaa-benchmarking-position
description: "How Buwaneka's unsupervised VAE results actually compare to his supervised teammates, and the agreed strategy for defending it."
metadata: 
  node_type: memory
  type: project
  originSessionId: fc09e84b-ca85-4491-bc91-8da1dfc27495
  modified: 2026-08-10T08:48:05.115Z
---

Buwaneka worries his metrics look weak next to teammates who use supervised learning. The
premise is mostly wrong: his Config B (VAE_TRANSFER) reaches **F1 0.693 / AUC 0.995**, above
Member 1's best GraphSAGE result (**F1 0.539 / AUC 0.950**, `Graphsage/reports/ablation_tuned.json`),
and Member 3's TS-TCN has **no measured results** — F1 > 0.88 is a target in their proposal,
not a result. The real gap is confined to CASH_OUT (F1 0.177), which holds 4,116 of 8,213
frauds and so drags the aggregate Config D to 0.422.

Agreed defence, in order: correct the premise; note the comparison is invalid anyway
(account-level vs transaction-level, different splits); add the correct peer group
(Isolation Forest, LOF, PCA, plain autoencoder); add a supervised ceiling on identical
features and quote the recovery ratio; explain CASH_OUT structurally — the discriminating
signal lives in the linked preceding TRANSFER, invisible to a single-transaction model,
which is the motivation for the multi-modal platform.

Also agreed: **Config H**, a logistic regression over the 29-dim DSAA fingerprints plus the
three scalar signals, framed as a *downstream separability analysis of the DSAA
representation* — not as switching the project to supervised learning.

**Why:** he was close to rewriting the project as supervised to chase comparable numbers,
which would discard the component's distinct role in DeepSentinel.

**How to apply:** if he raises the comparison again, lead with Config B's numbers, not with
"unsupervised is unfair". Related: [[deepsentinel-vae-dsaa-project]], [[vae-dsaa-known-defects]].
