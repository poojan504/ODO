#!/usr/bin/python

#TODO:
#set jetson time upon startup
#scan for 4-5 cameras
#plug and play camera compatibility
#camera transfer format

import os
os.environ["CUDA_VISIBLE_DEVICES"]="-1"


#from models.face_recognition import new_emotions
import warnings
import logging

from keras.models import load_model
import time
import numpy as np
import socket
import sys
import signal
import argparse
from multiprocessing import Process, Queue
import json

chatbot_request = Queue(-1)
chatbot_response = Queue(-1)
stop_camera = Queue(-1)

dispW=640
dispH=480
flip=2

parser = argparse.ArgumentParser(description="Parse command line arguments.", 
                           formatter_class=argparse.RawTextHelpFormatter)

# parse the command line
parser.add_argument("--port", type=int, default=7401, help="The port on which camera server is listening.")
parser.add_argument("--ip", type=str, default="10.157.136.246", help="The ip on which camera server is listening.")

opt, argv = parser.parse_known_args()
try:
    opt = parser.parse_known_args()[0]
except:
    print("")
    parser.print_help()
    sys.exit(0)

stop_detecting = False

#For handling CTRL + Z
def handler(signum, frame):
    global stop_detecting
    stop_detecting = True

#Chatbot Process to receive chatbot communication
def chatbot_process(chatbot_socket, chatbot_request, chatbot_response, stop_camera):
    while True:
        data = chatbot_socket.recv(1024).decode('utf-8')
        if data == 'send_emotion':
            chatbot_request.put({'request': data})
            while chatbot_response.empty():
                stopping = False
            camera_response = chatbot_response.get()
            response = camera_response['response']
            chatbot_socket.send(response.encode('utf-8'))
        elif data == 'stop_camera':
            stop_camera.put({'request': data})
            response = "stopping"
            chatbot_socket.send(response.encode('utf-8'))
            break
        ###################Vishal#####################
        elif data == 'all_cached':
            response = get_cached_emotion()
            chatbot_socket.send(response.encode('utf-8'))
        #############################################
        else:
            response = 'Request Not Understood'
            chatbot_socket.send(response.encode('utf-8'))

    chatbot_socket.close()

##################Vishal#####################
def get_cached_emotion():
    avg_emotion = {}
    str_emotion = ""
    emotion_cache = []
    with open('listfile.txt', 'r') as filehandle:
        for line in filehandle:
            currentPlace = line[:-1]
            emotion_cache.append(currentPlace)
    lenn = len(emotion_cache)+1
    #emotions = ["angry" ,"disgust","scared", "happy", "sad", "surprised", "neutral"]
    emotions = ["happy" ,"surprised","neutral", "sad", "angry", "disgust","scared"]
    for emo in emotions:
        avg_emotion = emotion_cache.count(emo)/lenn
        str_emotion = str_emotion + " " + "{:.3f}".format(avg_emotion)
    avg_emotion = str_emotion.lstrip()

    
    #avg_emotion = json.dumps(avg_emotion)
    return avg_emotion
#############################################


from utils.datasets import get_labels
from utils.inference import detect_faces
from utils.inference import draw_text
from utils.inference import draw_bounding_box
from utils.inference import apply_offsets
from utils.inference import load_detection_model
from utils.preprocessor import preprocess_input
import cv2
from statistics import mode
import time

def main():
    warnings.filterwarnings("ignore")
    logging.disable(logging.CRITICAL)
    global emotion_cache #Vishal
    emotion_cache = [] #Vishal
    global stop_detecting

    #Create server client for socket connection
    port = opt.port
    #host_name = socket.gethostname() 
    #host_ip = socket.gethostbyname(host_name) 
    host_ip = opt.ip
    mySocket = socket.socket()
    mySocket.bind((host_ip, port))

    print ("Camera server listening on port {0} ".format(port)+ "and IP " + str(host_ip))
    
    mySocket.listen(1)

    chatbot_socket, adress = mySocket.accept()
    print("Connection established to: " + str(adress))

    #Start socket process to listen to chatbot requests 
    chatbot = Process(target = chatbot_process, args = (chatbot_socket, chatbot_request, chatbot_response, stop_camera))
    chatbot.start()

    signal.signal(signal.SIGTSTP, handler)

    #face_recognizer = Face_Recognizer(True)# True to show video feed
    # parameters for loading data and images

    detection_model_path = './models/face_recognition/trained_models/haarcascade_frontalface_default.xml'
    emotion_model_path = './models/face_recognition/trained_models/fer2013_mini_XCEPTION.102-0.66.hdf5'
    emotion_labels = get_labels('fer2013')

    # hyper-parameters for bounding boxes shape
    frame_window = 10
    emotion_offsets = (20, 40)

    # loading models
    face_detection = load_detection_model(detection_model_path)
    emotion_classifier = load_model(emotion_model_path, compile=False)

    # getting input model shapes for inference
    emotion_target_size = emotion_classifier.input_shape[1:3]

    # starting lists for calculating modes
    emotion_window = []
    emotion_text = 'Happy'	
    # starting video streaming
    cv2.namedWindow('ODO_frame')
    OdoSet='nvarguscamerasrc !  video/x-raw(memory:NVMM), width=3820, height=2464, format=NV12,  framerate=21/1 ! nvvidconv flip-method='+str(flip)+' ! video/x-raw, width='+str(dispW)+', height='+str(dispH)+', format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink'

    video_capture = cv2.VideoCapture(OdoSet)

    fps = video_capture.get(cv2.CAP_PROP_FPS)
    print(f'FPS: {fps}')
    num_frames = 21;



    if video_capture.isOpened():
        print("True")
    else:
        print("Error")
    ##################Vishal#####################
    while stop_detecting == False:
    #############################################
        # Detect Emotion
        #print("Check")

        start = time.time() #starting FPS timer

        bgr_image = video_capture.read()[1]
        gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
        rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
        faces = detect_faces(face_detection, gray_image)

        for face_coordinates in faces:

            x1, x2, y1, y2 = apply_offsets(face_coordinates, emotion_offsets)
            gray_face = gray_image[y1:y2, x1:x2]
            try:
                gray_face = cv2.resize(gray_face, (emotion_target_size))
            except:
                continue

            gray_face = preprocess_input(gray_face, True)
            gray_face = np.expand_dims(gray_face, 0)
            gray_face = np.expand_dims(gray_face, -1)

            emotion_prediction = emotion_classifier.predict(gray_face)

            emotion_probability = np.max(emotion_prediction)
            emotion_label_arg = np.argmax(emotion_prediction)
            emotion_text = emotion_labels[emotion_label_arg]
            emotion_window.append(emotion_text)

            if len(emotion_window) > frame_window:
                emotion_window.pop(0)
            try:
                emotion_mode = mode(emotion_window)
            except:
               continue

            if emotion_text == 'angry':
                color = emotion_probability * np.asarray((255, 0, 0))
            elif emotion_text == 'sad':
                color = emotion_probability * np.asarray((0, 0, 255))
            elif emotion_text == 'happy':
                color = emotion_probability * np.asarray((255, 255, 0))
            elif emotion_text == 'surprise':
                color = emotion_probability * np.asarray((0, 255, 255))
            else:
                color = emotion_probability * np.asarray((0, 255, 0))

            emotion_cache.append(emotion_text)
            with open('listfile.txt', 'w') as filehandle:
                filehandle.writelines("%s\n" % emotions for emotions in emotion_cache)
            if len(emotion_cache) > 500:
                emotion_cache = emotion_cache[:-500]
            ##########################################
            total_faces = len(faces)
            current_time = time.time()
            if chatbot_request.empty() == False:
                request = chatbot_request.get()
                data_request = request['request']
                if data_request.lower() == 'send_emotion':
                    data = {}
                    data['emotion'] = emotion_detected
                    data['total_faces'] = total_faces
                    data['time'] = current_time
                    json_data = json.dumps(data)
                    chatbot_response.put({'response': json_data})

            
            color = color.astype(int)
            color = color.tolist()
            #print(face_coordinates, rgb_image, color)
            draw_bounding_box(face_coordinates, rgb_image, color)
            draw_text(face_coordinates, rgb_image, emotion_mode,
                  color, 0, -45, 1, 1)

        if stop_camera.empty() == False:
            stop_detecting = True
        end = time.time() #end time for FPS
        bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
        seconds = end - start #FPS
        fps = num_frames/seconds #FPS
        fps_coords = (0,30)
        framerate_str = 'Framerate: ' + str(int(fps))
        cv2.putText(bgr_image, framerate_str, fps_coords, cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,200))
        print(framerate_str)
        cv2.imshow('ODO_frame', bgr_image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        

    video_capture.release()
    cv2.destroyAllWindows()
    print("Closing chatbot socket")
    chatbot.terminate()
    chatbot.join()

if __name__== "__main__":
  main()
  print('Exiting the application')
  exit()
