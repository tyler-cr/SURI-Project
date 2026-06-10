#!/usr/bin/sh

# As noted, this script doesn't really work... but if you run the commands step 
# by step, it should be all good

curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash ./Miniconda3-latest-Linux-x86_64.sh

conda --create SURI_project
conda activate SURI

python -m ensurepip --upgrade
pip3 install --upgrade pip

pip3 install tensorflow pydub