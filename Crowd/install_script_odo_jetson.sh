#!/bin/bash
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
swapon --show
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
sudo apt-get update
sudo apt-get install libhdf5-serial-dev hdf5-tools libhdf5-dev
sudo apt-get install libblas-dev liblapack-dev libatlas-base-dev gfortran
#Cannot install pip using this
#sudo apt-get install python3-pip
sudo pip3 install Cython
echo 'Installed Cython'
sudo apt-get install python3-numpy
echo 'Installed Numpy'
sudo pip3 install pybind11
echo 'Installed pybind11'
sudo pip3 install scipy
echo 'Installed scipy'
sudo pip3 install keras
echo 'Installed keras'
wget https://developer.download.nvidia.com/compute/redist/jp/v42/tensorflow-gpu/tensorflow_gpu-1.15.0+nv19.11-cp36-cp36m-linux_aarch64.whl
sudo pip3 install tensorflow_gpu-1.15.0+nv19.11-cp36-cp36m-linux_aarch64.whl
echo 'Installed tensorflow'
sudo pip3 install pandas
echo 'Installed pandas'
sudo pip3 install --upgrade Cython
sudo pip3 install scikit-learn
echo 'Installed scikit learn'
sudo pip3 install tensorflow-hub
echo 'Installed tensorflow-hub'
sudo apt-get install libcanberra-gtk-module
sudo pip3 install python-osc
sudo pip3 install oscpy
echo 'Installed osc'