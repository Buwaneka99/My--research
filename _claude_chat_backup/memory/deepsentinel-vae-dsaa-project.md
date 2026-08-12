---
name: deepsentinel-vae-dsaa-project
description: "Buwaneka's SLIIT final-year research component (VAE-With-DSAA) inside the 4-person DeepSentinel project, its hard deadline and delivery gaps."
metadata: 
  node_type: memory
  type: project
  originSessionId: fc09e84b-ca85-4491-bc91-8da1dfc27495
  modified: 2026-08-09T21:18:32.538Z
---

`d:\Research\VAE-With-DSAA` is Buwaneka's own research component (R26-IT-121, IT22109194,
supervisor Mrs. Anjalie Gamage): a **Stratified VAE with Dual-Signal Anomaly Attribution
(DSAA) + DBSCAN fraud-typology discovery** on PaySim. The sibling folders `Graphsage`
(Member 1, Ewaduge) and `TS-TCN` (Member 3, Pathirana) belong to teammates; Member 4
(Vidanaarachchi) builds the LLM/RAG fusion engine that consumes all three REST outputs.
Do not modify the sibling folders.

Stated hard deadline: **finish by ~24 August 2026** (2 weeks from 2026-08-10), which is far
earlier than the proposal's Gantt chart (runs to October 2026). Everything through
notebook 05 (feature engineering → EDA → global VAE → stratified VAE → DSAA/DBSCAN) is done
and has saved results; **ablation Configs E/F/G, the FastAPI `/api/v1/behavioral/classify`
endpoint, and the final report are not started.**

**Why:** the compressed deadline changes what "done" means — prioritise the missing
deliverables over further model tuning.

**How to apply:** when asked to improve the project, weigh work against the two-week window
and the four unfinished deliverables first. See [[vae-dsaa-known-defects]] for the training
and ablation-fairness problems found on first read.
