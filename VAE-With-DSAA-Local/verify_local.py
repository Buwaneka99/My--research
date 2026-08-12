"""Smoke test — proves the local environment can actually run the project.

    .\.venv\Scripts\python.exe verify_local.py

Checks, in order:
  1. every required package imports
  2. the six preprocessed CSVs are reachable
  3. the trained VAE weights load
  4. a real slice of TRANSFER data scores end-to-end (encode -> decode ->
     Signal 1 -> Signal 2), and the fraud rows score higher than normal ones

Reads only. Writes nothing anywhere.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

OK, BAD = "  [ok]  ", "  [!!]  "
failures: list[str] = []


def check(label: str, fn):
    t0 = time.time()
    try:
        detail = fn()
        print(f"{OK}{label:<44} {detail}   ({time.time() - t0:.1f}s)")
    except Exception as exc:  # noqa: BLE001
        print(f"{BAD}{label:<44} {type(exc).__name__}: {exc}")
        failures.append(label)


print("=" * 78)
print("  LOCAL ENVIRONMENT VERIFICATION")
print("=" * 78)

# ---- 1. packages -------------------------------------------------------- #


def _packages():
    import matplotlib
    import numpy
    import pandas
    import seaborn
    import sklearn
    import scipy

    return (
        f"numpy {numpy.__version__} · pandas {pandas.__version__} · "
        f"sklearn {sklearn.__version__}"
    )


def _tensorflow():
    import tensorflow as tf

    gpus = tf.config.list_physical_devices("GPU")
    where = f"{len(gpus)} GPU" if gpus else "CPU only (expected on Windows)"
    return f"TF {tf.__version__} · {where}"


check("packages import", _packages)
check("tensorflow imports", _tensorflow)

# ---- 2. paths ----------------------------------------------------------- #

import local_setup as L  # noqa: E402


def _csvs():
    missing = [n for n in L.CSV_NAMES if not (Path(L.output_dir) / n).exists()]
    if missing:
        raise FileNotFoundError(f"{len(missing)} missing, e.g. {missing[0]}")
    total = sum((Path(L.output_dir) / n).stat().st_size for n in L.CSV_NAMES)
    src = "local copy" if L.CSV_SOURCE_IS_LOCAL else "original mirror (read-only)"
    return f"6 files · {total / 1024**3:.1f} GB · {src}"


def _write_guard():
    try:
        L.guard_write(Path(L.SOURCE_ROOT) / "anything.csv")
    except PermissionError:
        return "source folder is protected"
    raise AssertionError("guard_write did NOT block a write into the source tree")


check("preprocessed CSVs reachable", _csvs)
check("read-only guard works", _write_guard)

# ---- 3 + 4. models and a real forward pass ------------------------------ #


def _end_to_end():
    import json
    import pickle

    import numpy as np
    import pandas as pd
    from tensorflow import keras
    from tensorflow.keras import Model
    from tensorflow.keras import layers as KL

    md = Path(L.model_dir_read)

    # Rebuild the TRANSFER encoder/decoder and load weights — the same trick
    # notebook 05 uses, because the saved encoder contains a Lambda layer
    # Keras cannot deserialise across runtimes.
    def encoder(name, h1, h2, ld, in_dim=13):
        inp = keras.Input(shape=(in_dim,), name=f"{name}_enc_input")
        x = KL.Dense(h1, activation="relu", name=f"{name}_enc_h1")(inp)
        x = KL.Dense(h2, activation="relu", name=f"{name}_enc_h2")(x)
        return Model(
            inp,
            [KL.Dense(ld, name=f"{name}_z_mean")(x),
             KL.Dense(ld, name=f"{name}_z_log_var")(x)],
            name=f"{name}_encoder",
        )

    def decoder(name, h1, h2, ld, in_dim=13):
        inp = keras.Input(shape=(ld,), name=f"{name}_dec_input")
        x = KL.Dense(h2, activation="relu", name=f"{name}_dec_h1")(inp)
        x = KL.Dense(h1, activation="relu", name=f"{name}_dec_h2")(x)
        out = KL.Dense(in_dim, activation="sigmoid", name=f"{name}_dec_out")(x)
        return Model(inp, out, name=f"{name}_decoder")

    enc = encoder("vae_transfer", 32, 16, 8)
    dec = decoder("vae_transfer", 32, 16, 8)
    enc.load_weights(md / "vae_transfer_encoder.keras", skip_mismatch=True)
    dec.load_weights(md / "vae_transfer_decoder.keras", skip_mismatch=True)

    with open(md / "scaler_transfer.pkl", "rb") as f:
        scaler = pickle.load(f)
    cfg = json.loads((md / "stratified_config.json").read_text())

    feature_cols = [
        "F1_log_amount", "F2_amount_balance_ratio", "F3_balance_consistency",
        "F4_balance_change_ratio", "F5_dest_balance_ratio", "F6_hour",
        "F7_day", "F8_is_large", "F9_dest_starts_empty",
        "F10_recipient_emptied", "F11_account_velocity", "F12_round_amount",
        "F13_zero_dest_history",
    ]

    df = pd.read_csv(Path(L.output_dir) / "TRANSFER_all_features.csv", nrows=60_000)
    X = scaler.transform(df[feature_cols].values)
    y = df["isFraud"].values

    zm, zlv = enc.predict(X, batch_size=4096, verbose=0)
    xr = dec.predict(zm, batch_size=4096, verbose=0)

    err = (X - xr) ** 2
    recon = err.sum(axis=1)
    kl = np.sum(-0.5 * (1 + zlv - zm**2 - np.exp(zlv)), axis=1)

    s = cfg["TRANSFER"]
    score = 0.5 * (recon - s["recon_mean"]) / s["recon_std"] \
        + 0.3 * (kl - s["kl_mean"]) / s["kl_std"]

    # Signal 1 / Signal 2, exactly as DSAA computes them
    sig1 = err / (err.sum(axis=1, keepdims=True) + 1e-8)
    klp = np.maximum(-0.5 * (1 + zlv - zm**2 - np.exp(zlv)), 0.0)
    sig2 = klp / (klp.sum(axis=1, keepdims=True) + 1e-8)

    n_fraud = int(y.sum())
    if n_fraud == 0:
        return f"{len(df):,} rows scored (no fraud in this slice)"

    gap = score[y == 1].mean() - score[y == 0].mean()
    dom = feature_cols[int(sig1[y == 1].mean(axis=0).argmax())]
    assert abs(sig1.sum(axis=1) - 1).max() < 1e-4, "Signal 1 rows must sum to 1"
    assert abs(sig2.sum(axis=1) - 1).max() < 1e-4, "Signal 2 rows must sum to 1"
    assert gap > 0, "fraud must score higher than normal"

    return (
        f"{len(df):,} rows · {n_fraud} fraud · score gap +{gap:.2f} · "
        f"top Signal-1 feature {dom}"
    )


check("VAE weights + full DSAA forward pass", _end_to_end)

# ---- summary ------------------------------------------------------------ #

print("=" * 78)
if failures:
    print(f"  {len(failures)} check(s) failed: {', '.join(failures)}")
    print("  See README-LOCAL.md -> 'Troubleshooting'.")
    sys.exit(1)

print("  All checks passed. The project runs on this laptop.")
print("=" * 78)
