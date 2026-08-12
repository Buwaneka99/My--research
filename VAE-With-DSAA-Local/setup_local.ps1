# ============================================================
#  VAE-With-DSAA — local environment setup (Windows / PowerShell)
# ============================================================
#  Run once, from inside this folder:
#
#      cd d:\Research\VAE-With-DSAA-Local
#      .\setup_local.ps1
#
#  If PowerShell blocks the script:
#      powershell -ExecutionPolicy Bypass -File .\setup_local.ps1
#
#  Builds .venv from Python 3.12 (TensorFlow has no Python 3.14 wheels),
#  installs everything in requirements-local.txt, and registers a Jupyter
#  kernel named "deepsentinel" that the notebooks are already pointed at.
#
#  Touches nothing outside this folder.
# ============================================================

$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
Set-Location $root

Write-Host ""
Write-Host "============================================================"
Write-Host "  VAE-With-DSAA  ->  local setup"
Write-Host "============================================================"

# ---- 1. Python 3.12 present? --------------------------------
Write-Host "`n[1/5] Looking for Python 3.12..."

$py312 = $null
try {
    $out = & py -3.12 -c "import sys; print(sys.executable)" 2>$null
    if ($LASTEXITCODE -eq 0) { $py312 = $out.Trim() }
} catch { }

if (-not $py312) {
    Write-Host ""
    Write-Host "  Python 3.12 not found." -ForegroundColor Yellow
    Write-Host "  You have Python 3.14, but TensorFlow has no 3.14 wheels yet."
    Write-Host ""
    Write-Host "  Install it (3.14 stays exactly as it is):" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "      winget install -e --id Python.Python.3.12" -ForegroundColor White
    Write-Host ""
    Write-Host "  Then CLOSE this terminal, open a new one, and run this script again."
    exit 1
}
Write-Host "      found: $py312"

# ---- 2. venv ------------------------------------------------
Write-Host "`n[2/5] Creating .venv ..."
if (Test-Path "$root\.venv") {
    Write-Host "      .venv already exists - reusing it"
} else {
    & py -3.12 -m venv "$root\.venv"
    Write-Host "      created"
}
$venvPy = "$root\.venv\Scripts\python.exe"

# ---- 3. packages --------------------------------------------
Write-Host "`n[3/5] Installing packages (a few minutes - TensorFlow is ~250 MB)..."
& $venvPy -m pip install --upgrade pip --quiet
& $venvPy -m pip install -r "$root\requirements-local.txt"

# ---- 4. Jupyter kernel --------------------------------------
Write-Host "`n[4/5] Registering the Jupyter kernel 'deepsentinel'..."
& $venvPy -m ipykernel install --user --name deepsentinel --display-name "Python (deepsentinel)"

# ---- 5. verify ----------------------------------------------
Write-Host "`n[5/5] Verifying..."
& $venvPy "$root\verify_local.py"

Write-Host ""
Write-Host "============================================================"
Write-Host "  Done. Start working with:" -ForegroundColor Green
Write-Host ""
Write-Host "      .\.venv\Scripts\Activate.ps1"
Write-Host "      jupyter lab"
Write-Host ""
Write-Host "  Then open notebooks\05_DSAA_Framework_local.ipynb first -"
Write-Host "  it runs in about a minute on the weights you already have."
Write-Host "============================================================"
