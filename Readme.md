ODO is a multimodal AI chatbot, which uses state of the art Machine learning models to create an attractive and engaging theater play. This system uses many multi-media mediums like stage lightings, microphone and cameras. Detailed description of the system can be found in the MDPI paper - [ODO- Design of Multimodal Chatbot for an Experiential Media System](https://web.asu.edu/sites/default/files/imaging-lyceum/files/mti-04-00068.pdf)


This system is built on Nvidia Jetson Nano - a low cost AI system. This repo contains all the code needed to run on Jetson and also on local machines for training and testing. Please use test branch to test the chatbot conversation. More about testing is found in Readme of test branch. 

 
Setup for Linux Environment(Ubuntu 18.0.4 +):

## Requirements 

### Local Environment:

1. Install anaconda following this link [anaconda](https://www.digitalocean.com/community/tutorials/how-to-install-anaconda-on-ubuntu-18-04-quickstart)

2. Use environmet.yml to create conda environment required in your local machine. Incase any of the package doesnt get built, please use manual conda install or pip install with the specific version which can be found in the environment.yml 


### Nividia Jetson Nano:

<!-- 1. In the terminal, execute the following commands: -->

$ sudo fallocate -l 8G /swapfile    
$ sudo chmod 600 /swapfile    
$ sudo mkswap /swapfile    
$ sudo swapon /swapfile    
$ swapon --show    
$ echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab  
$ sudo apt-get install libhdf5-serial-dev hdf5-tools libhdf5-dev    
$ sudo apt-get install libblas-dev liblapack-dev libatlas-base-dev gfortran    
$ sudo apt-get install python3-pip    
$ sudo pip3 install Cython    
$ sudo apt-get install python3-numpy    
$ sudo pip3 install pybind11    
$ sudo pip3 install scipy    
$ sudo pip3 install keras    
$ wget https://developer.download.nvidia.com/compute/redist/jp/v42/tensorflow-gpu/tensorflow_gpu-1.15.0+nv19.11-cp36-cp36m-linux_aarch64.whl  
$ sudo pip3 install tensorflow_gpu-1.15.0+nv19.11-cp36-cp36m-linux_aarch64.whl  
$ sudo pip3 install pandas  
$ sudo pip3 install --upgrade Cython  
$ sudo pip3 install scikit-learn  
$ sudo pip3 install tensorflow-hub  

<i>Using same environment.yml file even in Jetson Nano instead of pip install, should work as well.</i>

2. If you have done a ssh to Jetson Nano and no display is attached to it, then please execute the below command:\
$ export DISPLAY=:0

3. Execute the below command to start the chatbot:\
$ python3 odo.py

### Pre-Trained Models:

#### Chatbot
Please use this link [model](https://drive.google.com/file/d/1VNNr1U5kWRGYTYoy5cTxXAF1v6eOqMTp/view?usp=sharing) to download the necessary model required to run the chatbot. Place this in the following directory Chatbot/models/dialogue_system/3/variables/

Please use this link [model](https://drive.google.com/file/d/1GyZxCUs-QFonI8fRnNu51HHvKQmrOg4L/view?usp=sharing) to download the poem generator model. Place this in the following directory Chatbot/models/poem_generator/trained_models/

#### Camera
Please use this link [model](https://drive.google.com/file/d/1quNv1ZQC4ayqMbCPxgrhNRi9k4L4_T0G/view?usp=sharing) to download the necessary model required to run the chatbot. Place this in the following directory Camera_1/models/face_recognition/trained_models

What to expect:\
If you are using a laptop, then your webcam will start and it will try to detect a face. Only after face is detected will the chatbot start. If you are using Jetson, then this will activate the USB camera connected to jetson and wait till it detects the face.

#### Chat tag list:
Communication between chatbot and Max system happens with using several tags, each performing an action. Tags from Max to chatbot needs a message along with it to perfom the task. Below is the table. 

| Tag 			|	Function 			|
|---------------|-----------------------|
|/start "start"	|	Start the chatbot 	|
|/chat "message"	|	Conversation from user to chatbot|
|/names "names"| Retrieves the names of the players|
|/stop "true/false"| Pauses/Resumes chatbot|
|/rgb | Tag with which chatbot sends rgb values of chosen color back to MAX|
|/haiku "haiku"| Generates a random haiku poem to the user|
|/emotions | Tag with which chatbot sends user's emotion to Max|  
|/jump | Perform jumps in the story - **Need to fix bugs**|