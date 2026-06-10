Write-Host "=== Setting up SURI Project Environment ===" -ForegroundColor Cyan

$installerUrl = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
$installerPath = ".\Miniconda3-latest-Windows-x86_64.exe"
$installDir = "$env:USERPROFILE\miniconda3"
$CONDA_EXE = "$installDir\Scripts\conda.exe"

Write-Host "Downloading Miniconda..."
Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath

Write-Host "Installing Miniconda..."
Start-Process -FilePath $installerPath -ArgumentList "/InstallationType=JustMe", "/AddToPath=1", "/RegisterPython=1", "/S", "/D=$installDir" -Wait

Remove-Item $installerPath

Write-Host "Initializing Conda..."
& $CONDA_EXE init powershell

Write-Host "Configuring channels..."
& $CONDA_EXE config --add channels conda-forge
& $CONDA_EXE config --set channel_priority strict

Write-Host "Creating conda environment 'SURI_project'..."
& $CONDA_EXE create --name SURI_project python=3.10 -y

Write-Host "Installing conda packages..."
& $CONDA_EXE install -n SURI_project -c conda-forge librosa numpy scipy pandas scikit-learn matplotlib -y

Write-Host "Installing pip packages..."
& $CONDA_EXE run -n SURI_project python -m pip install --upgrade pip
& $CONDA_EXE run -n SURI_project python -m pip install tensorflow

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Close and reopen PowerShell, then run:" -ForegroundColor Yellow
Write-Host "  conda activate SURI_project" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Green