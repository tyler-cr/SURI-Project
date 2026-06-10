#!/bin/bash
set -e

echo "Downloading Conda for software package handling"

INSTALLER="Miniconda3-latest-Linux-x86_64.sh"
URL="https://repo.anaconda.com/miniconda/$INSTALLER"
INSTALL_PATH="$HOME/miniconda3"

curl -L "$URL" -o "$INSTALLER"

echo "Installing Miniconda"

bash "$INSTALLER" -b -p "$INSTALL_PATH"

rm "$INSTALLER"

source "$INSTALL_PATH/etc/profile.d/conda.sh"

conda init bash

echo "Creating conda environment for all dependencies..."
echo "NOTE: whenever working on project, you must first run 'conda activate SURI_project'"

conda config --add channels conda-forge
conda config --set channel_priority strict

conda create --name SURI_project python=3.10 -y

conda install -n SURI_project -c conda-forge librosa numpy scipy pandas scikit-learn matplotlib -y

conda run -n SURI_project python -m pip install --upgrade pip
conda run -n SURI_project python -m pip install tensorflow

echo ""
echo "Setup complete!"
echo "Close and reopen your terminal, then run:"
echo "conda activate SURI_project"