# VAE-With-DSAA — Local (laptop) edition

**R26-IT-121 · IT22109194 · Wijesinghe L P D B**

Colab නැතුව, Google Drive නැතුව, ඔයාගේ laptop එකේම run කරන්න පුළුවන් version එක.

> **පරණ folder එකට කිසිම වෙනසක් වෙන්නේ නෑ.**
> `d:\Research\VAE-With-DSAA\` එක **read-only source** එකක් විදිහට විතරයි පාවිච්චි කරන්නේ —
> එතනින් CSV ටිකයි trained weights ටිකයි කියවනවා. අලුතෙන් හැදෙන හැම දෙයක්ම යන්නේ
> මේ folder එකේ `outputs\` එකට. `local_setup.guard_write()` එකෙන් source එකට
> write කරන්න හැදුවොත් error එකක් දෙනවා.

---

## 1. මුලින්ම කරන්න ඕන දේ — Python 3.12

ඔයාගේ machine එකේ දැන් තියෙන්නේ **Python 3.14** විතරයි. TensorFlow තාම 3.14 support
කරන්නේ නෑ (max 3.13). ඒ නිසා Python 3.12 එකක් **තව එකක් විදිහට** install කරන්න ඕන —
3.14 එකට කිසිම බලපෑමක් නෑ, දෙකම එකට තියෙන්න පුළුවන්.

PowerShell එකේ:

```powershell
winget install -e --id Python.Python.3.12
```

ඉවර වුනාම **terminal එක close කරලා අලුත් එකක් open කරන්න** (PATH refresh වෙන්න).

Check කරන්න:

```powershell
py -3.12 --version      # Python 3.12.x කියලා එන්න ඕන
py -0p                  # install වෙලා තියෙන Python ඔක්කොම
```

---

## 2. Environment එක හදන්න

```powershell
cd d:\Research\VAE-With-DSAA-Local
.\setup_local.ps1
```

PowerShell script එක block කළොත්:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup_local.ps1
```

මේකෙන් වෙන්නේ:

1. `py -3.12` තියෙනවද බලනවා
2. `.venv\` හදනවා (මේ folder එකේ ඇතුළේ — system Python එකට අත තියන්නේ නෑ)
3. `requirements-local.txt` install කරනවා — TensorFlow ~250 MB, විනාඩි කීපයක් යනවා
4. `deepsentinel` කියලා Jupyter kernel එකක් register කරනවා
5. `verify_local.py` run කරලා ඇත්තටම වැඩ කරනවද කියලා බලනවා

---

## 3. Run කරන්න

```powershell
.\.venv\Scripts\Activate.ps1

jupyter notebook        # classic UI
# හෝ
jupyter lab             # JupyterLab
```

දෙකම වැඩ කරනවා — කැමති එකක් පාවිච්චි කරන්න.

Notebook එකක් open කරලා, උඩ දකුණේ kernel එක **Python (deepsentinel)** කියලා
තියෙනවද බලන්න (notebooks වල default එකම ඒක). වෙන එකක් තෝරලා තිබ්බොත්
*Kernel → Change kernel → Python (deepsentinel)*.

**VS Code එකේ notebook editor එකේ run කරනවා නම්:** උඩ දකුණේ *Select Kernel* →
*Python Environments* → `.venv` (Python 3.12) එක තෝරන්න.

> ⚠️ Kernel එක වැරදුනොත් `import tensorflow` එකේදී `ModuleNotFoundError` එකක්
> එනවා — ඒ කියන්නේ Python 3.14 kernel එකට වැටිලා. Kernel එක මාරු කරන්න.

### Notebook order

වෙලාව ගැන කියලා තියෙන ඒවා **estimates** — CPU එකේ මනිනකම් හරි අගය දන්නේ නෑ.
(Colab GPU එකේ: notebook 03 = 50 min, notebook 04 = 7 min.)

| # | Notebook | මොකද කරන්නේ | කොපමණ වෙලාවක් (CPU, approx.) | ඕනම ද? |
|---|---|---|---|---|
| 01 | `01_Feature_Engineering_local.ipynb` | Raw PaySim → F1–F13 → 6 CSV | ~10–15 min | **නෑ** — CSV ටික දැනටමත් තියෙනවා (raw CSV එකත් cache එකේ, ඕන නම් run කරන්න පුළුවන්) |
| 02 | `02_EDA_local.ipynb` | Distributions, effect sizes, KS tests, 13 figures | ~10 min | නෑ (figures ඕන නම් විතරයි) |
| 03 | `03_Global_VAE_Baseline_local.ipynb` | Config A — global VAE, 50 epochs | **~1–2 hours** | Config A rerun කරනවා නම් විතරයි |
| 04 | `04_Stratified_VAE_local.ipynb` | Configs B/C/D — VAE 3ක් | ~20–40 min | ඔව් — retrain කරන්න |
| 05 | `05_DSAA_Framework_local.ipynb` | Signal 1+2, fingerprints, DBSCAN, typologies | **~2–5 min** | ඔව් |

> **පළවෙනියටම 05 run කරන්න.** ඒක දැනටමත් තියෙන weights පාවිච්චි කරනවා,
> විනාඩි කීපයයි යන්නේ, ඔක්කොම pipeline එක වැඩ කරනවද කියලා ඒකෙන් පේනවා.

---

## 4. Colab version එකට වඩා වෙනස් වුනේ මොනවද

Research code එකේ **එකම line එකක්වත්** වෙනස් කරලා නෑ. වෙනස් වුනේ මේ ටික විතරයි:

| Colab එකේ | Local එකේ |
|---|---|
| `from google.colab import drive` / `drive.mount(...)` | comment කරලා — `# [local] removed:` |
| `!pip install kagglehub -q` | comment කරලා — packages `requirements-local.txt` එකේ |
| `output_dir = '/content/drive/MyDrive/...'` | `output_dir = _L.output_dir` |
| `results_dir`, `eda_dir`, `dsaa_dir`, `model_dir` | ඒ විදිහටම `_L.` වලින් |
| `kagglehub.dataset_download(...)` හැම run එකකම (notebook 01) | disk එකේ මුලින්ම හොයනවා, නැත්නම් විතරයි download |
| GPU (T4) | CPU |

හැම notebook එකකටම උඩින්ම **CELL 0 (local)** කියලා අලුත් cell එකක් දාලා තියෙනවා —
ඒක `local_setup.py` හොයාගෙන path ඔක්කොම resolve කරලා banner එකක් print කරනවා.

Notebook ටික generate කරේ `d:\Research\VAE-With-DSAA\notebooks\v2\*.ipynb` වලින්
script එකකින්, ඒ නිසා ඒවා original ඒවාට ගැළපෙනවා (outputs ටික strip කරලා තියෙනවා).

---

## 5. Paths — කොහෙන් කියවනවද, කොහෙට ලියනවද

`local_setup.py` එකෙන් තීරණය වෙනවා:

| Variable | Resolve වෙන්නේ |
|---|---|
| `output_dir` | **read** — `outputs\Output_v2\` (ඔයාගේම එක) නැත්නම් original mirror එක |
| `output_dir_write` | **write** — `outputs\Output_v2\` (notebook 01 විතරයි) |
| `model_dir_read` | **read** — `outputs\Results_v2\models\` නැත්නම් original weights |
| `results_dir` | **write** — `outputs\Results_v2\` |
| `model_dir` | **write** — `outputs\Results_v2\models\` |
| `eda_dir` | **write** — `outputs\EDA_v2\` |
| `dsaa_dir` | **write** — `outputs\DSAA_v2\` |

මේකේ තේරුම: **පළවෙනි දවසේම වැඩ කරනවා** (original artefacts කියවනවා), ඒත් ඔයා
notebook 04 run කරලා අලුත් weights හැදුවම, ඊට පස්සේ ඒවා automatically පාවිච්චි වෙනවා.

Path එකක් check කරන්න ඕන නම්:

```powershell
.\.venv\Scripts\python.exe local_setup.py
```

---

## 6. Raw data (notebook 01ට විතරයි)

**හොඳ ආරංචියක්: raw CSV එකත් දැනටමත් ඔයාගේ machine එකේ තියෙනවා.**

```
C:\Users\Buwaneka\.cache\kagglehub\datasets\ealaxi\paysim1\versions\2\
    PS_20174392719_1491204439457_log.csv          (471 MB)
```

`local_setup.find_raw_csv()` ඒක automatically හොයාගන්නවා, ඒ නිසා **notebook 01ත්
download එකක් නැතුව run වෙනවා**. Internet එකවත් Kaggle credentials එකවත් ඕන නෑ.

හොයන order එක: `data\raw\` → original project එකේ `data\raw\` → kagglehub cache.

CSV එක නැති වුනොත් විතරයි: [kaggle.com/datasets/ealaxi/paysim1](https://www.kaggle.com/datasets/ealaxi/paysim1)
එකෙන් download කරලා `data\raw\` එකට දාන්න, නැත්නම් `~\.kaggle\kaggle.json` දාලා
notebook එකට download කරගන්න දෙන්න.

---

## 7. Troubleshooting

**`py -3.12` හම්බෙන්නේ නෑ**
Install කරලා terminal එක close කරලා අලුත් එකක් open කළාද? `py -0p` එකෙන් බලන්න.

**`ModuleNotFoundError: No module named 'tensorflow'`**
Wrong Python. `.\.venv\Scripts\Activate.ps1` කරලා තියෙනවද බලන්න — prompt එකේ
`(.venv)` කියලා තියෙන්න ඕන. Jupyter එකේදී kernel එක **Python (deepsentinel)** ද කියලා බලන්න.

**TensorFlow install වෙන්නේ නෑ**
Python version එක බලන්න: `.\.venv\Scripts\python.exe --version` → 3.12.x වෙන්න ඕන.
3.14 නම් venv එක වැරදියට හැදිලා — `.venv` folder එක delete කරලා `setup_local.ps1`
ආයෙත් run කරන්න.

**"Refusing to write inside the original project"**
ඒක වැඩ කරන එකේ ලකුණක් — `guard_write` එකෙන් පරණ folder එක ආරක්ෂා කරනවා.
Write path එකක් `outputs\` එකට හරවන්න.

**Notebook 03 හරිම හෙමින්**
50 epochs × 15,356 steps CPU එකේ. Smoke test එකකට cell එකේ `EPOCHS = 50` කියන එක
`EPOCHS = 3` කරලා බලන්න. **Report එකට යන numbers ගන්නවා නම් 50ම run කරන්න.**

**Memory error**
Notebook 03 එකේ 4.9M rows එකට load වෙනවා. RAM 31 GB තියෙන නිසා ප්‍රශ්නයක් වෙන්න
බෑ, ඒත් වුනොත් browser tabs වහලා ආයෙත් බලන්න.

**GPU පාවිච්චි වෙන්නේ නෑ**
ඒක හරි. Windows එකේ TensorFlow ≥ 2.11 CPU-only (GPU support WSL2 එකට ගියා).
Models පොඩි නිසා (~2,400 parameters) CPU එකෙන් ප්‍රශ්නයක් නෑ.

---

## 8. මොනවද මේ folder එකේ

```
VAE-With-DSAA-Local\
├── README-LOCAL.md              ← මේ file එක
├── setup_local.ps1              ← එක පාරක් run කරන setup එක
├── requirements-local.txt       ← packages
├── local_setup.py               ← path resolver + write guard + banner
├── verify_local.py              ← smoke test (environment එක වැඩ ද?)
├── data\raw\                    ← raw PaySim CSV එක දාන්න (optional)
├── notebooks\
│   ├── 01_Feature_Engineering_local.ipynb
│   ├── 02_EDA_local.ipynb
│   ├── 03_Global_VAE_Baseline_local.ipynb
│   ├── 04_Stratified_VAE_local.ipynb
│   └── 05_DSAA_Framework_local.ipynb
└── outputs\                     ← අලුතෙන් හැදෙන හැම දෙයක්ම මෙතන
    ├── Output_v2\               (notebook 01)
    ├── EDA_v2\                  (notebook 02)
    ├── Results_v2\models\       (notebooks 03, 04)
    └── DSAA_v2\                 (notebook 05)
```

---

## 9. මීළඟට

මේක local run කරන්න විතරයි. **VAE training එකේ තියෙන defect එක මේකෙන් හැදෙන්නේ නෑ** —
notebook 04 එකේ තාම `FREE_BITS = 0.01` සහ EarlyStopping එක `val_total_loss` monitor
කරනවා, ඒ නිසා තාමත් epoch 1ට restore වෙනවා (β = 0).

Fix එක තියෙන්නේ පරණ folder එකේ: `DeepSentinel_VAE_Fix_v3.py`.
ඒක local notebook 04 එකට apply කරන්න ඕන නම් කියන්න — **තව අලුත් copy එකක්** විදිහට
හදන්නම්, දැන් තියෙන ඒවා වෙනස් නොකර.
