"""Local (no-Colab) bootstrap for the VAE-With-DSAA notebooks.

Every local notebook starts with::

    import local_setup as _L
    _L.banner()

and then uses ``_L.output_dir``, ``_L.results_dir``, ``_L.eda_dir``,
``_L.dsaa_dir``, ``_L.model_dir`` in place of the Google Drive paths.

READ-ONLY GUARANTEE
-------------------
The original project (``d:\\Research\\VAE-With-DSAA``) is treated as a
read-only source. It supplies the 1.2 GB of preprocessed CSVs and the
already-trained ``.keras`` weights, and nothing in this folder ever writes
back into it. Every write path returned by this module lives under
``VAE-With-DSAA-Local/outputs/``, and :func:`guard_write` raises if a path
inside the source tree is ever handed to a writer.

PATH RESOLUTION
---------------
Reads prefer your own local outputs and fall back to the source mirror, so
the notebooks work on day one (before you have regenerated anything) and
automatically switch to your own artefacts once you have::

    output_dir     CSVs      local outputs/Output_v2  -> else source mirror
    model_dir      weights   local outputs/Results_v2/models -> else source
    results_dir    metrics   always local
    eda_dir        figures   always local
    dsaa_dir       DSAA      always local
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# --------------------------------------------------------------------- #
# Roots
# --------------------------------------------------------------------- #

PROJECT_ROOT = Path(__file__).resolve().parent

# The original, untouched project. Override with DS_SOURCE_ROOT if you ever
# move it (e.g. to another drive).
SOURCE_ROOT = Path(
    os.environ.get("DS_SOURCE_ROOT", PROJECT_ROOT.parent / "VAE-With-DSAA")
).resolve()

SOURCE_MIRROR = SOURCE_ROOT / "DeepSentinel-VAE-Results"
SRC_OUTPUT = SOURCE_MIRROR / "DeepSentinel_Output_v2"
SRC_RESULTS = SOURCE_MIRROR / "DeepSentinel_Results_v2"
SRC_MODELS = SRC_RESULTS / "models"
SRC_DSAA = SOURCE_MIRROR / "DeepSentinel_DSAA_v2"

# Everything this project writes.
OUT_ROOT = PROJECT_ROOT / "outputs"
LOCAL_OUTPUT = OUT_ROOT / "Output_v2"
LOCAL_EDA = OUT_ROOT / "EDA_v2"
LOCAL_RESULTS = OUT_ROOT / "Results_v2"
LOCAL_MODELS = LOCAL_RESULTS / "models"
LOCAL_DSAA = OUT_ROOT / "DSAA_v2"
LOCAL_RAW = PROJECT_ROOT / "data" / "raw"

for _d in (LOCAL_OUTPUT, LOCAL_EDA, LOCAL_RESULTS, LOCAL_MODELS, LOCAL_DSAA, LOCAL_RAW):
    _d.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------- #
# Write guard
# --------------------------------------------------------------------- #


def guard_write(path: str | Path) -> Path:
    """Raise if *path* would write inside the original project folder."""
    p = Path(path).resolve()
    if SOURCE_ROOT == p or SOURCE_ROOT in p.parents:
        raise PermissionError(
            f"Refusing to write inside the original project.\n"
            f"  attempted : {p}\n"
            f"  source    : {SOURCE_ROOT}\n"
            f"Write to {OUT_ROOT} instead."
        )
    return p


# --------------------------------------------------------------------- #
# Resolution
# --------------------------------------------------------------------- #

CSV_NAMES = [
    f"{t}_{kind}_features.csv"
    for t in ("TRANSFER", "CASH_OUT", "PAYMENT")
    for kind in ("normal", "all")
]

MODEL_NAMES = [
    "vae_transfer_encoder.keras",
    "vae_cashout_encoder.keras",
    "vae_payment_encoder.keras",
    "scaler_transfer.pkl",
    "stratified_config.json",
]


def _has_all(folder: Path, names: list[str]) -> bool:
    return folder.is_dir() and all((folder / n).exists() for n in names)


_csv_local = _has_all(LOCAL_OUTPUT, CSV_NAMES)
_csv_source = _has_all(SRC_OUTPUT, CSV_NAMES)
_models_local = _has_all(LOCAL_MODELS, MODEL_NAMES)
_models_source = _has_all(SRC_MODELS, MODEL_NAMES)

# Read paths — prefer your own regenerated artefacts.
_output_read = LOCAL_OUTPUT if _csv_local else SRC_OUTPUT
_models_read = LOCAL_MODELS if _models_local else SRC_MODELS

# Exported as plain strings so every existing f-string in the notebooks
# (f"{output_dir}/TRANSFER_all_features.csv") behaves exactly as before.
output_dir = str(_output_read)          # read: the six feature CSVs
output_dir_write = str(LOCAL_OUTPUT)    # write: feature-engineering output
results_dir = str(LOCAL_RESULTS)        # write: config_*_metrics.json, figures
model_dir = str(LOCAL_MODELS)           # write: newly trained weights
model_dir_read = str(_models_read)      # read: weights for DSAA / inference
eda_dir = str(LOCAL_EDA)                # write: EDA figures
dsaa_dir = str(LOCAL_DSAA)              # write: fingerprints, typologies

CSV_SOURCE_IS_LOCAL = _csv_local
MODEL_SOURCE_IS_LOCAL = _models_local

# --------------------------------------------------------------------- #
# Raw PaySim (only notebook 01 needs it)
# --------------------------------------------------------------------- #


def find_raw_csv() -> Path | None:
    """Locate the raw PaySim CSV without contacting Kaggle.

    Looks in this project's data/raw, then the original project's data/raw,
    then any existing kagglehub cache. Returns None if it is nowhere.
    """
    candidates: list[Path] = []
    for folder in (LOCAL_RAW, SOURCE_ROOT / "data" / "raw"):
        if folder.is_dir():
            candidates += sorted(folder.glob("*.csv"))

    cache = Path.home() / ".cache" / "kagglehub" / "datasets" / "ealaxi" / "paysim1"
    if cache.is_dir():
        candidates += sorted(cache.rglob("*.csv"))

    for c in candidates:
        if c.stat().st_size > 100 * 1024 * 1024:  # the real file is ~470 MB
            return c
    return candidates[0] if candidates else None


def download_raw_csv() -> Path:
    """Fetch PaySim through kagglehub into the local cache. Needs credentials."""
    import kagglehub

    path = Path(kagglehub.dataset_download("ealaxi/paysim1"))
    csvs = sorted(path.glob("*.csv"))
    if not csvs:
        raise FileNotFoundError(f"No CSV inside {path}")
    return csvs[0]


# --------------------------------------------------------------------- #
# CPU-friendly TensorFlow defaults
# --------------------------------------------------------------------- #

# TensorFlow reads these at import time, so they must be set before the
# notebook's `import tensorflow` cell runs — which is why the bootstrap cell
# is inserted above it.
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")   # hide INFO/WARNING spam
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "1")  # CPU speedup for dense nets

BATCH_SIZE = int(os.environ.get("DS_BATCH", "256"))  # matches the Colab runs

# --------------------------------------------------------------------- #
# Banner
# --------------------------------------------------------------------- #


def banner() -> None:
    """Print the resolved environment. Call once at the top of a notebook."""
    import platform

    try:
        import psutil  # optional

        ram = f"{psutil.virtual_memory().total / 1024**3:.0f} GB"
    except Exception:
        ram = "?"

    line = "=" * 66
    print(line)
    print("  LOCAL RUN — no Google Drive, no Colab")
    print(line)
    print(f"  Python        : {platform.python_version()}  ({sys.executable})")
    print(f"  CPU cores     : {os.cpu_count()}   RAM: {ram}")
    print(f"  Source (read) : {SOURCE_ROOT}")
    print(f"  Outputs (write): {OUT_ROOT}")
    print()
    print(f"  output_dir    : {output_dir}")
    print(f"                  [{'your local copy' if _csv_local else 'original mirror, read-only'}]"
          f" {'OK' if (_csv_local or _csv_source) else 'MISSING — run notebook 01 first'}")
    print(f"  model_dir_read: {model_dir_read}")
    print(f"                  [{'your retrained weights' if _models_local else 'original weights, read-only'}]"
          f" {'OK' if (_models_local or _models_source) else 'MISSING — run notebook 04 first'}")
    print(f"  results_dir   : {results_dir}")
    print(f"  eda_dir       : {eda_dir}")
    print(f"  dsaa_dir      : {dsaa_dir}")
    print(line)
    print("  Nothing is ever written into the source folder.")
    print(line)


if __name__ == "__main__":
    banner()
    raw = find_raw_csv()
    print(f"\n  raw PaySim CSV: {raw if raw else 'not found (only notebook 01 needs it)'}")
