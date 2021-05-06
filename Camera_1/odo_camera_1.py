#!/usr/bin/python

#TODO:
#set jetson time upon startup
#scan for 4-5 cameras
#plug and play camera compatibility
#camera transfer format

import os
os.environ["CUDA_VISIBLE_DEVICES"]="-1"


from models.face_recognition.face_recognition import Face_Recognizer
import warnings
import logging


import time

import socket
import sys
import signal
import argparse
from multiprocessing import Process, Queue
import json

chatbot_request = Queue(-1)
chatbot_response = Queue(-1)
stop_camera = Queue(-1)

parser = argparse.ArgumentParser(description="Parse command line arguments.", 
                           formatter_class=argparse.RawTextHelpFormatter)

# parse the command line
parser.add_argument("--port", type=int, default=7401, help="The port on which camera server is listening.")
parser.add_argument("--ip", type=str, default="2.1.0.11", help="The ip on which camera server is listening.")

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

    face_recognizer = Face_Recognizer(True)# True to show video feed
    ##################Vishal#####################
    while stop_detecting == False:
    #############################################
        # Detect Emotion
        try:
            face_recognizer.start_detection()
            emotion_detected = face_recognizer.current_emotion
            ###############Vishal#####################
            emotion_cache.append(emotion_detected)
            with open('listfile.txt', 'w') as filehandle:
                filehandle.writelines("%s\n" % emotions for emotions in emotion_cache)
            if len(emotion_cache) > 500:
                emotion_cache = emotion_cache[:-500]
            ##########################################
            total_faces = face_recognizer.total_faces
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

            if stop_camera.empty() == False:
                stop_detecting = True
            
        except KeyboardInterrupt:
            print("Ctrl+C encountered. Stopping Camera.")
            stop_detecting = True
            #n=1
            #print("Detection Error")
        except:
            n=1
            print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                         sys.exc_info()[1],
                                         sys.exc_info()[2].tb_lineno))
            
            #TODO:Reinitializing incase of camera disconnected
            #face_recognizer.total_cameras = 0
            #while face_recognizer.total_cameras == 0:
                #face_recognizer.reinitialize_camera(True)

    try:
        print('Closing Camera')
        face_recognizer.stop_detection()
        print("Closing chatbot socket")
        chatbot.terminate()
        chatbot.join()
    except:
        print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                         sys.exc_info()[1],
                                         sys.exc_info()[2].tb_lineno))

if __name__== "__main__":
  main()
  print('Exiting the application')
  exit()
