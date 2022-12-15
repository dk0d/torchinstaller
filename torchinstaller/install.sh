#!/bin/bash

##### ARGUMENTS ######
PYTHON_VERSION=${1-3.9}
PYTORCH_VERSION=${2-latest}
CUDA_VERSION=${3-}
#####################

if [[ -z "$CUDA_VERSION" ]]; then
  if ! command -v nvidia-smi &>/dev/null; then
    CUDA_VERSION="cpu"
  else
    CUDA_VERSION="$(nvidia-smi | egrep -o 'CUDA Version:\s([0-9.])+' | egrep -o '[0-9.]+')"
    echo "FOUND CUDA Version: $CUDA_VERSION"
  fi
fi

if [[ "$PYTORCH_VERSION" == "latest" ]]; then
  TORCH_STRING="pytorch"
  PYTORCH_VERSION="1.13.0"
else
  TORCH_STRING="pytorch=$PYTORCH_VERSION"
fi

# Pytorch 


# Pytorch-geometric
#conda install -n $ENV_NAME pyg -c pyg -y
pip install pyg-lib torch-scatter torch-sparse torch-cluster torch-spline-conv torch-geometric \
  -f https://data.pyg.org/whl/torch-$PYTORCH_VERSION+$CUDA_VERSION.html
