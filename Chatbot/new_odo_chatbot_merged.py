#!/usr/bin/python

# Pending
# - - -- - --
# AUTO DETECT IP ADDRESSES OF JETSONS USING MAC ADDRESSES
# Memory leaks are there...Free memory once done
# Implementing user timeout wwhile waiting for input from Max
# import signal
# TIMEOUT = 5 # number of seconds your want for timeout



######## Stuffs to do 02/19/2020 ##########
# Tag for Haiku poem generator

import os
os.environ["CUDA_VISIBLE_DEVICES"]="-1"
import tensorflow as tf
from tensorflow import keras
from keras import backend as K

from models.dialogue_system.dialogue_system import Chatbot, UnivEncoder
from models.poem_generator.poem_generator import Haiku_Bot, Generator, create_training_model
import cv2
import warnings
import numpy as np
import logging
import sys
import re

from random import randrange
import random as rn

from multiprocessing import Process, Queue
import time

from pathlib import Path
import joblib

import socket
import sys
import json
import argparse
from pythonosc import udp_client
from oscpy.server import OSCThreadServer

## karthik code##
from colour import Color
import linecache

IP1 = "10.157.161.56"
IP2 = "10.157.161.56"
IP3 = "10.157.161.56"
IP4 = "10.157.161.56"
parser = argparse.ArgumentParser(description="Parse command line arguments.", 
                           formatter_class=argparse.RawTextHelpFormatter)

# parse the command line: All options are optional. Usage $ python3 odo_chatbot.py --maxip 2.1.0.4 --maxport 7400
parser.add_argument("--chatip", type=str, default=IP1, help="The ip of chatbot.")
parser.add_argument("--chatport", type=int, default=7403, help="The port on which chat server is listening to osc connection.")
parser.add_argument("--maxip", type=str, default=IP2, help="The ip on which max server is listening.")
parser.add_argument("--maxport", type=int, default=7400, help="The port on which max server is listening.")
parser.add_argument("--camip1", type=str, default=IP3, help="The ip on which camera 1 server is listening.")
parser.add_argument("--camport1", type=int, default=7401, help="The port on which camera 1 server is listening.")
parser.add_argument("--camip2", type=str, default=IP4, help="The ip on which camera 2 server is listening.")
parser.add_argument("--camport2", type=int, default=7402, help="The port on which camera 2 server is listening.")
parser.add_argument("--test", type=bool, default=False, help="Enable this flag only for testing.")
parser.add_argument("--jump", type=int, default=0, help="Use this falg to make jumps in the story.")

opt, argv = parser.parse_known_args()
try:
    opt = parser.parse_known_args()[0]
except:
    print("")
    parser.print_help()
    sys.exit(0)

#MAX Tags for chatbot server
# chatbot = "/chat"
# command = "/command"
kill    = "/kill" #Kill everything

# Max Tags for chatbot client
chat_tag = "/chat"
start_tag = "/start"
names_tag = "/names"
stop_tag = "/stop"
rgb_tag = '/rgb'
#Chat response speed in secs
chat_speed = 2

## kk code start##
chat_speed_slow = 10

# Total number of players
players = 5
players_names = []
## kk code start##

emotion_queue = Queue(-1)
total_faces = Queue(-1)

# Max Commands:
# Kill everything: /kill kill
# Kill everything: /command kill 
# Start chatbot: /command chat
# Pause chatbot: /command pause
# Start New Session: /command new
# Say Poem: /command poem
# Detect Emotion: /command emotion
# Comment on something interesting about audinece: /command comment
# User chat. Please note to keep user chat in quotes: /chat "what user said"

max_response = Queue(-1)

output_intent = Queue(-1)
request_poem = Queue(-1)
response_poem = Queue(-1)
USE_MAX = False
user_name = None
callback = False
global pauser
pauser = False
global command
command = "kill"
global haiku_bot
jump = 0

def max_callback(values):
    #Do something. Here we are just printing
    global output_intent
    output_intent.put({'name': values})
    print("got values: {}".format(values))

def printbot(input_txt):
    #tag "/ame_chatbot" #sample tag
    #message = "abcd26872    09u7iuogh" #sample message
    ip = IP2 #sample ip
    port = 7400 #sample port
    try:
        client = udp_client.SimpleUDPClient(ip, port)
        client.send_message(input_txt, message)
    finally:
        return True


## kk code to terminate all the connections end ##

## kk code for new tags
def haiku_intialiser(tf_session):
    global haiku_bot
    try:
        haiku_bot = Haiku_Bot(tf_session)
        print("here 1")
        output_dir = Path('models//poem_generator//trained_models')
        # Get the parameters used for creating the model
        latent_dim, n_tokens, max_line_length, tokenizer = joblib.load(output_dir / 'metadata.pkl')
        print("here 2")
        # Create the new placeholder model
        training_model, lstm, lines, inputs, outputs = create_training_model(latent_dim, n_tokens)
        # Load the specified weights
        training_model.load_weights(output_dir / 'poem_generator_weights.hdf5')
        haiku_bot = Generator(lstm, lines, tf_session, tokenizer, n_tokens, max_line_length)
        print("Initialized chatbot poem generator.")
    except:
        print("Unable to initialize chatbot poem generator.")
        print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                         sys.exc_info()[1],
                                         sys.exc_info()[2].tb_lineno))


def haiku_poem():
    global haiku_bot
    global max_client
    poem = haiku_bot.generate_haiku([3, 5, 3], temperature=.3, first_char='cold')
    poem = haiku_bot.generate_haiku([3, 5, 3], temperature=.3, first_char='cold')
    for i in range(3):
        line = re.sub(r"[^a-zA-Z0-9]+", ' ', poem[i])
        max_client.send_message(chat_tag, line)


def haiku_generator(values):
    global max_client
    print("inside haiku")
    values = values.decode("utf-8").strip('""')
    print(values)
    if values == "haiku":
        print("indside if")

        x = rn.randint(1,11) 
        poem = linecache.getline("haiku_poems.txt", x)

        poem = poem.split(",")

        for i in poem:
            max_client.send_message(chat_tag, i.strip("\n"))
            time.sleep(chat_speed)

        # haiku_poem()


def start_chat(values):
    global command
    values = values.decode("utf-8").strip('""')
    print(values)
    if  values == "start":
        command = "start"

def check_response(chat):
    global max_client
    print("inside check response")
    global pauser
    if "stopchat" in chat:
        chat_modified = chat.replace("stopchat", "")
        if "player1" in chat_modified:
            chat_modified = chat_modified.replace("player1", players_names[0].strip('""'))
        if "player2" in chat_modified:
            chat_modified = chat_modified.replace("player2", players_names[1].strip('""'))
        if "player3" in chat_modified:
            chat_modified = chat_modified.replace("player3", players_names[2].strip('""'))
        if "player4" in chat_modified:
            chat_modified = chat_modified.replace("player4", players_names[3].strip('""'))
        if "player5" in chat_modified:
            chat_modified = chat_modified.replace("player5", players_names[4].strip('""'))
        # else:
        #     chat_modified = chat_modified

        pauser = True
        max_client.send_message(stop_tag, "PAUSE")
        return chat_modified
        

    elif "emotions" in chat:
        # try:
        emotions = get_cached_emotion(0)
        # except:
            # print("inside emotion exception, creating temp emotion values")
            # emotions = [10]*7
        # chat_modified = chat.replace("emotions", "sample sentence")
        chat_modified = chat.replace("emotions", "I see you all are {0} % Happy {1} % Surprised {2} % Neutral {3} % Sad {4} % Angry {5} % Disgust {6} % Scared".format(emotions[0], emotions[1], emotions[2], emotions[3], emotions[4], emotions[5], emotions[6]).strip('""'))
        return chat_modified
        # max_client.send_message(chat_tag, chat_modified)
        # command = 'kill'
        # file.close()
        # return chat_modified

    else:
        print("inside else")
        chat_modified = chat
        if "player1" in chat:
            chat_modified = chat.replace("player1", players_names[0].strip('""'))
        if "player2" in chat:
            chat_modified = chat.replace("player2", players_names[1].strip('""'))
        if "player3" in chat:
            chat_modified = chat.replace("player3", players_names[2].strip('""'))
        if "player4" in chat:
            print("inside if")
            print(players_names)
            chat_modified = chat.replace("player4", players_names[3].strip('""'))
        if "player5" in chat:
            chat_modified = chat.replace("player5", players_names[4].strip('""'))
        # else:
        #     chat_modified = chat

        return chat_modified

def send_names(values):
    global max_client
    values = values.decode("utf-8").strip('""')
    if values == "names":
        names = str(players_names).strip('""')
        names = names.strip('[]')
        names = names.replace('""', " ")
        names = names.replace("\'", " ")
        names = names.replace(",", " ")
        names = names.replace('"', " ")
        # print(names)
        max_client.send_message(names_tag, names)
## kk code for tags stop

def jump_story(values):
    global chatbot
    values = values.decode("utf-8").strip('""')
    print("value of jump", values)
    jump = values
    chatbot.story_progress = int(jump) 

def chat_callback(values):
    global pauser
    print("pauser value",pauser)
    if not pauser:
        # print(pauser)
        global max_response
        values = values.decode("utf-8").strip("'")
        # print("User Chat:"+values)
        max_response.put({'intent': values})
        
def get_cached_emotion(values):
    ###########Vishal#########################
    camera_message = "all_cached"
    global cam1_socket  
    global cam2_socket
    #cam1_socket = socket.socket()
    #cam1_socket.connect((opt.camip1, opt.camport1))
    print("I am here emotions")
    try:
        cam1_socket.send(camera_message.encode('utf-8'))
        emotion_1 = cam1_socket.recv(1024).decode('utf-8').split()
        print(emotion_1)
    except:
        emotion_1 = [0]*7
    try:
        cam2_socket.send(camera_message.encode('utf-8'))
        emotion_2 = cam2_socket.recv(1024).decode('utf-8').split()
    except:
        emotion_2 = [0]*7 
    #print("I am here 2")
    emotion = ''
    #print(emotion_1)
    for i in range(len(emotion_1)):
        emotion += str((float(emotion_1[i]) + float(emotion_2[i])/0.02)) + " "

    print("printing emotions", emotion)
    ip = IP2 
    port = 7400 
    try:
        client = udp_client.SimpleUDPClient(ip, port)
        client.send_message("/emotions", emotion.strip())
    except:
        pass
    return emotion.split()

def command_callback(values):
    global max_response
    values = values.decode("utf-8").strip("'")
    # print("Max Command:"+values)
    max_response.put({'command': values})

def kill_switch(values):
    global max_response
    values = values.decode("utf-8").strip("'")
    print("Kill Switch command:"+values)
    max_response.put({'kill': values})

def stop_resume_operation(values):
    global max_client
    print("inside resume func")
    print("value before manipulation",values)
    global pauser
    values = values.decode("utf-8").strip('""')
    print(values)
    print(type(values))
    if values == "true":
        # print("hahahahahahahaha")
        pauser = True
        print("value of pauser", pauser)
        max_client.send_message(stop_tag, 'PAUSE')
    elif values == "false":
        pauser = False
        print("value of pauser", pauser)
        max_client.send_message(stop_tag, 'RESUME')

def history(text):
  with open("history.txt", "a") as file:
    file.write(text + '\n')
  file.close()

def story_transition():
    next_story = intent.split("_")[2]
    chatbot.change_story(next_story)
    univEncoder.set_intent(chatbot.intents)
    intent = univEncoder.get_intent(chatbot.intents)
    l = len(chatbot.intents[intent].responses)
    if l > 0:
        chatbot.story_progress = chatbot.intents[intent].weight
        chat = chatbot.intents[intent].responses[randrange(l)]
        max_client.send_message(chat_tag, chat)
        history(chat)

def main():
    global pauser
    global command
    global haiku_bot
    global max_client
    global cam1_socket
    global cam2_socket
    global chatbot

    pauser = False
    command = "pause"
    warnings.filterwarnings("ignore")
    logging.disable(logging.CRITICAL)

    tf_session = tf.Session()
    K.set_session(tf_session)
    bye_list = ['bye', 'see you', 'tada', 'chao']
    

    #Connection Initialization

    print("Creating Connections")
    #Connecting to max
    try:
        max_client = udp_client.SimpleUDPClient(opt.maxip, opt.maxport)
        print("UDP Client connection to Max established")
    except KeyboardInterrupt:
        print("Keyboard Interrupted at UDP connection")
    except:
        print("UDP Client connection to Max failed. Will not be able to send from Max.")
        print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                         sys.exc_info()[1],
                                         sys.exc_info()[2].tb_lineno))


        #################  Connecting to Camera 1  #####################

    if(opt.test==False):
        try:
            cam1_socket = socket.socket()
            cam1_socket.connect((opt.camip1, opt.camport1))
            print("Connection to Camera 1 established")
        except KeyboardInterrupt:
            print("Keyboard Interrupted at Camera 1 connection")
        except:
            print("Unable to connect to Camera 1")
            print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                             sys.exc_info()[1],
                                             sys.exc_info()[2].tb_lineno))
        
        ############### Connecting to Camera 2 #######################

        try:
            cam2_socket = socket.socket()
            cam2_socket.connect((opt.camip2, opt.camport2))
            print("Connection to Camera 2 established")
        except KeyboardInterrupt:
            print("Keyboard Interrupted at Camera 2 connection")
        except:
            print("Unable to connect to Camera 2")
            print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                             sys.exc_info()[1],
                                             sys.exc_info()[2].tb_lineno))
    

    #Max server: Listen to Max
    '''
    try:
        osc = OSCThreadServer()
        try:
            max_server = osc.listen(address=opt.chatip, port=opt.chatport, default=True)
            print("OSC Server initialized to listen to Max")
            osc.bind(b"/chat", chat_callback)
            osc.bind(b"/command", command_callback)
            osc.bind(b"/kill", kill_switch)
            ##########sddrd to test Vishal#########################
            osc.bind(b"/stop", stop_resume_operation)
            ######Vishal#########################
            osc.bind(b"/emotions", get_cached_emotion)

        except:
            print("Tag is not in exceptable format")
        ##########sddrd to test Vishal#########################
    except:
        print("OSC Server initialization failed. Will not be able to listen to Max")
        print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                         sys.exc_info()[1],
                                         sys.exc_info()[2].tb_lineno))'''
    
    #Max server: Listen to Max

    try:
        osc = OSCThreadServer()
        try:
            max_server = osc.listen(address=opt.chatip, port=opt.chatport, default=True)
            print("OSC Server initialized to listen to Max")
            osc.bind(b"/chat", chat_callback)
            osc.bind(b"/command", command_callback)
            osc.bind(b"/kill", kill_switch)
            ##########sddrd to test Vishal#########################
            osc.bind(b"/stop", stop_resume_operation)

            ## kk code for start
            osc.bind(b"/start", start_chat)
            osc.bind(b"/haiku", haiku_generator)
            osc.bind(b"/names", send_names)
            osc.bind(b"/emotions", get_cached_emotion)
            osc.bind(b"/jump", jump_story)
        except Exception as e:
            print(e)
            print("Tag is not in exceptable format")
        ##########sddrd to test Vishal#########################
    except KeyboardInterrupt:
        print("Keyboard Interrupted at OSC Communication")
    except:
        print("OSC Server initialization failed. Will not be able to listen to Max")
        print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                         sys.exc_info()[1],
                                         sys.exc_info()[2].tb_lineno))

    



    ########### Chatbot Generator #####################

    # haiku_intialiser(tf_session)


    try:
        chatbot = Chatbot(tf_session, story_progress=opt.jump)
        univEncoder = UnivEncoder(tf_session, chatbot.intents)
        print("Initialized chatbot dialogue system")
    except KeyboardInterrupt:
        print("Keyboard Interrupted at Chatbot")
        exit()
    except:
        print("Unable to initialize chatbot dialogue system. Exiting.")
        print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                         sys.exc_info()[1],
                                         sys.exc_info()[2].tb_lineno))
        exit()

    #Waiting for max command to start chatbot
    # command = "stopped"
    # while command != "chat":
    #     while max_response.empty():
    #         stopped = True
    #     max_request = max_response.get()
    #     command = max_request['command']
    # if()

    print(time.time())
    print("Starting chatbot for the first time")    
    max_client.send_message(start_tag, "ready")

    
    while command != "kill":

        users = False
        faces_count = 0
        chat_start = True
        returning_user = False
        ask_user_name = True

        while command != "pause" and command != "new" and command !="kill":

            try:
                if ask_user_name:
                    ask_user_name = False
                    try:
                        os.mkdir("users")
                    except:
                        users = True

                    ## Creating a txt file and storing all the sentence ##

                    global file
                    ## kk code to open and close history file start ## 
                    file = open("history.txt", "w+")
                    file.close()
                    ## kk code to open and close history file end ##

                    #TODO: There is no kill switch check or command check. Need to implement it.
                    first_sentence = "Hello! - - - You can text to me with your phone - - - I see a visitor in red, how are you ?"
                    max_client.send_message(chat_tag, first_sentence)
                    history(first_sentence)
                    # time.sleep(chat_speed_slow)

                    while max_response.empty():
                        waiting_for_user = True
                    user_response = max_response.get()
                    history(user_response['intent'])

                    # players_names = ["dummy1", "dummy2", "dummy3", "dummy4", "dummy5"]
                    
                    
                    ## kk code start##
                    if(opt.jump==0):
                        chat = "Thank you! I see five visitors. What is your name, visitor one in red ?" #.format(players)
                        max_client.send_message(chat_tag, chat)
                        while max_response.empty():
                            waiting_for_user = True

                        history(chat)

                        print("players names ", players_names)
                        # try:
                        greetings = ["Hi ", "Welcome ", "Hello ", "Its my pleasure ", "Hello "]
                        user_colors = [". visitor two in green ?", ". visitor three in blue ?", ". visitor four in orange ?", ". visitor five in yellow ?", ""]
                        i = 0
                        while max_response.empty():
                            waiting_for_user = True

                        for __ in range(players):
                            user_response = max_response.get()
                            name = user_response['intent']
                            history(name)
                            players_names.append(name)

                            chat = greetings[i] + name.strip('""') + ". - - - " + user_colors[i]
                            max_client.send_message(chat_tag, chat)
                            history(chat)
                            i+=1
                        # except:
                        #     print("ran into exception ")
                        
                        print("players names ", players_names)

                        
                        # user_response = max_response.get()
                        #TODO: We might need to validate the cities
                        # user_location = user_response['intent']
                        # history(user_location)

                        ############## Sending name ##################
                        names = str(players_names).strip('""')
                        names = names.strip('[]')
                        names = names.replace('""', " ")
                        names = names.replace("\'", " ")
                        names = names.replace(",", " ")
                        names = names.replace('"', " ")
                        # print(names)
                        max_client.send_message(names_tag, names)



                        #Monologue
                        chat = "Nice to meet you all.  - - - I lihve here. - - - Here on stage. I can’t leave the stage."

                        max_client.send_message(chat_tag, chat)
                        time.sleep(chat_speed)

                        pauser = True
                        print("value of pauser", pauser)
                        max_client.send_message(stop_tag, 'PAUSE')

                    
                    # while pauser:
                    #     waiting_for_user = True

                    # chat = 'Where do you lihve, {0} ? - - - Do you live on stage like me - - - or do you lihve in a house, {0} ?'.format(players_names[3].strip('""'))
                    # max_client.send_message(chat_tag, chat)
                    # history(chat)

                    ## commenting code end

                try:
                    while max_response.empty():
                        waiting_for_user = True
                    
                    user_response = max_response.get()
                    history(user_response['intent'])
                    user_chat = user_response['intent']
                    print("user input", user_chat)
                    if(user_chat.strip('""') in bye_list):
                        chat = 'It was nice talking to you.'
                        max_client.send_message(chat_tag, chat)
                        history(chat)
                        command = 'kill'
                        file.close()
                        break
                    intent = univEncoder.match_intent(user_chat,chatbot.story_progress)
                    print("intent name", intent)
                    # print("weight", chatbot.progress)
                    # print(chatbot.intents[intent].dynamic)
                    

                    if(intent == 'no_matching_intent'):
                        chat = "hmm - - I dont understand {0} , can you please say something different".format(user_chat)
                        # chat = univEncoder.chat_eliza(user_chat)
                        # print("Response from Eliza \n {0}".format(chat))
                        max_client.send_message(chat_tag, chat)
                        history(chat)


                    ##### Haiku poems, Disabling for now end - kkk #####


                    elif "transition" in intent:
                        print("inside change transition logic")
                        store_progress = chatbot.story_progress
                        print("progress value", store_progress)
                        # story_transition()
                        next_story = intent.split("_")[2]
                        print("next story", next_story)
                        chatbot.change_story(next_story)
                        univEncoder.set_intent(chatbot.intents)
                        l = len(chatbot.intents[intent].responses)
                        if l > 0:
                            chatbot.story_progress = chatbot.intents[intent].weight
                            chat = chatbot.intents[intent].responses[randrange(l)]
                            chat = check_response(chat)
                            max_client.send_message(chat_tag, chat)
                            history(chat)


                    elif "main" in intent:
                        print("inside change main logic")
                        chatbot.change_story("see_me", store_progress+6)
                        # print(chatbot.intents)
                        univEncoder.set_intent(chatbot.intents)
                        l = len(chatbot.intents[intent].responses)
                        if l > 0:
                            chatbot.story_progress = chatbot.intents[intent].weight
                            chat = chatbot.intents[intent].responses[randrange(l)]
                            chat = check_response(chat)
                            max_client.send_message(chat_tag, chat)
                            history(chat)


                    elif "happiness" in intent:
                        print("inside last intent logic")
                        # chatbot.change_story("see_me", store_progress+6)
                        # print(chatbot.intents)
                        # univEncoder.set_intent(chatbot.intents)
                        l = len(chatbot.intents[intent].responses)
                        if l > 0:
                            chatbot.story_progress = chatbot.intents[intent].weight
                            chat = chatbot.intents[intent].responses[randrange(l)]
                            chat = check_response(chat)
                            max_client.send_message(chat_tag, chat)
                            max_client.send_message(stop_tag, "END")
                            history(chat)
                            command = "kill"



                    else:
                        l = len(chatbot.intents[intent].responses)
                        if l > 0:
                            if(intent=="learning"):
                                print("inside color intent")
                                user_color = user_response['intent']
                                print(user_color)
                                try:
                                    user_rgb = [round(ele, 3) for ele in Color(user_color.strip('"')).rgb]
                                    # user_rgb = [int(i)*255 for i in user_rgb]
                                    user_rgb = str(user_rgb).strip('[]')
                                    user_rgb = user_rgb.replace(",", "")
                                    # print(user_rgb.rgb)
                                    print(user_rgb)
                                    history(str(user_rgb))
                                    history(chat)

                                    chatbot.story_progress = chatbot.intents[intent].weight
                                    chat = chatbot.intents[intent].responses[randrange(l)]
                                    chat = check_response(chat)
                                    max_client.send_message(chat_tag, chat)
                                    
                                    
                                
                                    max_client.send_message(rgb_tag, str(user_rgb))
                                except:
                                    max_client.send_message(chat_tag, "I dont understand this color, please try something else")
                            else:
                                chatbot.story_progress = chatbot.intents[intent].weight
                                chat = chatbot.intents[intent].responses[randrange(l)]
                                chat = check_response(chat)
                                max_client.send_message(chat_tag, chat)
                                history(chat)


                except KeyboardInterrupt:
                    print("Closing all active connections")
                    command = "kill"

                except:
                    print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                             sys.exc_info()[1],
                                             sys.exc_info()[2].tb_lineno))
                    chat = "hmm, I dont know what {0} is, can you please say something different".format(user_response['intent'])
                    max_client.send_message(chat_tag, chat)
                    history(chat)


                ##### Haiku poems, Disabling for now start - kkk #####
                # poem = haiku_bot.generate_haiku([3, 5, 3], temperature=.3, first_char='cold')
                # poem = haiku_bot.generate_haiku([3, 5, 3], temperature=.3, first_char='cold')
                # line1 = re.sub(r"[^a-zA-Z0-9]+", ' ', poem[0])
                # line2 = re.sub(r"[^a-zA-Z0-9]+", ' ', poem[1])
                # line3 = re.sub(r"[^a-zA-Z0-9]+", ' ', poem[2])
                # chat = line1 + line2 + line3
                # max_client.send_message(chat_tag, chat)
                ##### Haiku poems, Disabling for now end - kkk #####

            except KeyboardInterrupt:
                print("Closing all active connections")
                command = "kill"

                  
    try:
        try:
            cam1_socket.send(camera_message.encode('utf-8'))
            cam1_socket.close()
            print("Connection to Camera 1 closed")
        except:
            print("unable to close camera 1")

        try:
            cam2_socket.send(camera_message.encode('utf-8'))
            cam2_socket.close()
            print("Connection to Camera 2 closed")
        except:
            print("unable to close camera 2")

        try: 
            osc.stop()
            print("Connection to Max closed")
        except:
            print("unable to close connectoin to Max")

    except:
        print('unable to close connections')

if __name__== "__main__":
  main()
  print('Exiting the application')
  exit()

#### Commented code for other code options #################

### Haiku Generator Options ################################
#for i in range(3):
#  poem = generator.generate_haiku([5, 7, 7, 5], temperature=.3, first_char='summer')
#  print(poem[0])
#  print(poem[1])
#  print(poem[2])
#  print("\n")
