# Pending
# Stories based on gender, age
# BLack magic intensity shuttle...6
# Long Poetry
# Manual command to start a different topic. Or 
# Create 60 short stories. Total 20 stories and each story will have a happy, a neutral/sad and a curious version
# Curious version will be used as a filler story to divert to a happy or sad story if user is not responding. or to change topic..
# Each story is an intent type. This is becuase this will help UnivEncoder to match similarity to one story intent only.
# Each story will have an opening intent
# Each story intent will have a timeout intent, which will get triggered when timeout happens.
# Create a structure or bag of keywords which will suggest that we need to switch stories now as 
# conversation is moving in a different direction. Like a key of words for a story and a probability indicator indicating where
# current conversation is going. Over the conversation as probability grows, we will shift story.
# need to knwo if a particular utterance has already been said. 
# Choose a different utterance based on the universal encoder output. next on universal encoder list.
# A way to understand the progress of the story
# restart chatbot when user goes away from camera
# what is the next intent if current intent is already satisfied? or which sentence(or index) has bot spoken of. So that it is not repetive.

import pandas as pd
import numpy as np
import os
import math
import json
import tensorflow as tf
import tensorflow_hub as hub
from random import randrange
import random
import string

# global main_intents
# main_intents = {}
## kk code for eliza start ##
#from nltk.chat.util import Chat
#from nltk.chat.eliza import pairs
## kk code for eliza stop ##

default_utterances = ['yes', 'no', 'maybe', 'okay', 'sure']
class Story:
    def __init__(self, name, intents = {}, completion_status = 0, tone = "happy", starting_intent = {}, script = {}, keywords = [], timeout_intent = {}, utterances_said = [], transition_intent = {}):

        self.id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(15)]) 
        self.name = name
        self.intents = intents

        self.completion_status = completion_status
        self.tone = tone
        self.keywords = keywords
        self.starting_intent = starting_intent
        self.script_intent = script
        self.timeout_intent = timeout_intent
        self.transition_intent = transition_intent
        self.utterances_said = utterances_said

        # What if the user wants to again start the story??? You should have an intent that this is what you can say about story and
        # now you shold tell him some other story...

        # transition intent will giv hint about two three different stories....
        # there will be two three transition intents...

    def create_timeout_intent(self, intent_name, weight, utterances = [], responses = []):
        if type(intent_name)==list:                # Iterate over all the values in list
            for name in intent_name:
                self.add_intent(name, weight, utterances, responses)
                self.timeout_intent[intent_name] = self.intents[intent_name]

        else:                                      # insert without iterating
            self.add_intent(intent_name, weight, utterances, responses)
        return intent_name

    def create_transition_intent(self, intent_name, weight, utterances = [], responses = []):
        if type(intent_name)==list:                # Iterate over all the values in list
            for name in intent_name:
                self.add_intent(name, weight, utterances, responses)
                self.transition_intent[intent_name] = self.intents[intent_name]

        else:                                      # insert without iterating
            self.add_intent(intent_name, weight, utterances, responses)
        return intent_name

    def create_starting_intent(self, intent_name, weight, utterances = [], responses = []):
        if type(intent_name)==list:                # Iterate over all the values in list
            for name in intent_name:
                self.add_intent(name, weight, utterances, responses)
                self.starting_intent[intent_name] = self.intents[intent_name]

        else:                                      # insert without iterating
            self.add_intent(intent_name, weight, utterances, responses)
        return intent_name

    def create_script_intent(self, intent_name, weight, utterances = [], responses = []):
        if type(intent_name)==list:                # Iterate over all the values in list
            for name in intent_name:
                self.add_intent(name, weight, utterances, responses)
                self.script_intent[intent_name] = self.intents[intent_name]

        else:                                      # insert without iterating
            self.add_intent(intent_name, weight, utterances, responses)
        return intent_name

    def add_intent(self, intent_name, weight, utterances, response):                   # Function to add intent if not already existing

        if not self.check_intent_name(intent_name):
            self.intents[intent_name] = Intent(intent_name, weight, utterances, response)
        else:
            print("Intent {0} already exists".format(intent_name))

    def check_intent_name(self, intent_name):            # Checking if an intent already exists
        if intent_name in self.intents.keys():
            return True

        else:
            return False

    def get_intent(self, utterance):
        for k, v in self.intents.items():
            if utterance in v.utterances:
                return k
        print("no intent matched")

######### Intents #########
class Intent:
    def __init__(self, name, weight, utterances = [], responses = []):

        self.name = name
        self.utterances = utterances
        self.responses = responses
        self.weight = weight

    def create_utterance(self, utterances):

        if type(utterances) == list:
            for utterance in utterances:
                self.utterances.append(utterance)

        else:
            self.utterances.append(utterances)

    def add_utterance(self, utterance):
        if not self.check_utterance(utterance):
            self.utterances.append(utterance)
        else:
            print("Utterance {0} already exists".format(utterance))

    def check_utterance(self, utterance):
        if utterance in self.utterances:                    # Checking the utterance in the bag of utterances. If it exists in any intent, it will give an error
            return True
        else:
            return False

    def remove_utterance(self, utterances):           # removes utterances
        if type(utterances) == list:
            for utterance in utterances:
                try:
                    self.utterances.remove(utterance)
                except ValueError:
                    print("'{0}' utterance doesnt exists".format(utterance)) # throws exception if utterance does not exists

        else:
            try:
                self.utterances.remove(utterances)
            except ValueError:
                print("'{0}' utterance doesnt exists".format(utterances))


    def create_response(self, responses):

        if type(responses) == list:
            for response in responses:
                self.responses.append(response)

        else:
            self.responses.append(responses)

    def add_response(self, response,r):
        if not self.check_response(r):
            self.responses.append(r)
        else:
            print("Response {0} already exists".format(r))

    def check_response(self, response):
        if response in self.responses:                    # Checking the response in responses. If it exists in any intent, it will give an error
            return True
        else:
            return False

    def remove_response(self, responses):           # removes responses
        if type(responses) == list:
            for response in responses:
                try:
                    self.responses.remove(response)
                except ValueError:
                    print("'{0}' response doesnt exists".format(response)) # throws exception if response does not exists

        else:
            try:
                self.responses.remove(response)
            except ValueError:
                print("'{0}' response doesnt exists".format(responses))


class Chatbot:
    # global main_intents
    # names = [0]

    def __init__(self, tf_session, intents = {}, stories = {}, current_story = None, chat_history = [], story_progress = 0):
        
        self.intents = intents
        # self.main_intents = main_intents
        self.chat_history = chat_history
        self.stories = stories
        self.current_story = current_story
        self.story_progress = story_progress
        self.session = tf_session
        self.create_character()


    ######### Storing/Retrieving data ############
    def store_data(self):
        with open("sample.json", "w") as file:
            json.dump(self.intents, file)

    def retrieve_data(self):
        with open("sample.json", "r") as file:
            self.intents.update(json.load(file))
   
    def add_story(self, name, story):
        self.stories[name] = story

    def get_story(self, name):
        return self.stories[name]

    #Will shift these stories to csv file once time permits
    def add_story_see_me(self):
        try:
            name = 'see_me'
            story = Story(name,{})
            story.create_script_intent('live', 5,
                default_utterances ,
                ['Where do you lihve, player5 ? - - - Do you lihve on stage like me - - - or do you lihve in a house, player5 ?']
                )
            story.create_script_intent('house', 10,
                default_utterances + ['house', 'apartment', 'building', 'stage', 'cave', 'home', 'here', 'room', 'cage', 'hills','I live in a house', 'I live in a jungle', 'forest', 'nowhere', 'I am homeless'],
                ['house of course! - - - lets see. stopchat']
                )
            story.create_script_intent('house_2', 12,
                default_utterances + ['house', 'apartment', 'building', 'cave', 'junlge', 'home', 'forest', 'hills', 'mountain'],
                ['does this look like your home player5 ?']
                )
            story.create_script_intent('color', 15,
                default_utterances + ['awful', 'not at all', 'great', 'a bit', 'cant say', 'dont know', 'yes', 'no', 'nope', 'maybe', 'nah', 'i think so',  'not really', 'are you kidding me', 'something close', 'not even near'],
                ['what is your favorite color player2 ?']
                )
            story.create_script_intent('learning', 22,
                default_utterances + ['red', 'green', 'blue', 'yellow', 'maroon', 'purple', 'cyan', 'black', 'white', 'brown', 'rose', 'orange', 'pink', 'grey'],
                ['Nice  color for the roof. You see, I am learning. stopchat']
                )
            story.create_script_intent('little_man', 25,
                default_utterances ,
                ['Hey player1, - - - I am thirsty , - - - you are my pilot now , - - - what shall we do ? search for water or fix the plane, player1 ?']
                )
            story.create_script_intent('little_man_water_transition', 30,
                ['water', 'search water', 'lets go for water', 'survival first', 'leave plane', 'thirsty', 'we will die if we dont find water', 'cant say', 'dont know' ],
                ['Alright, - - - water it is. - - - but what about the plane, player2 ?']
                )
            story.create_script_intent('little_man_plane_transition', 30,
                ['plane','water is not needed', 'stay here and fix', 'repair the plane', 'fly', 'fix the plane', 'I am tough, can manage without water', 'lets do mechanic work'],
                ['I think you are more the tough guy, right ? - - - An explorer or a researcher, perhaps ? - But. - - - how can we survive in the desert, player2 ? - - - water or fuel ?']
                )
            story.create_script_intent('water_howto_main', 31,
                ['decide later', 'no idea', 'dont know', 'cant decide', 'whatever the other player is saying', 'your wish', 'you make the call', 'thirsty', 'fix the plane'],
                ['hmm. - - - I am very thirsty. - - - Can we go and find water now player2 ?']
                )
            story.create_script_intent('water_howto_2_main', 31,
                default_utterances + ['fine','sounds like a better plan','whatever you say', 'as you say', 'lets find water', 'leave the plane', 'ignore the plane', 'cant live without water', 'later'],
                ['Yes thank you. - - - I am very thirsty. - - - Ready to go find water now player2 ?']
                )
            story.create_script_intent('plane_water_main', 31,
                default_utterances + ['water', 'absolutely', 'sure', 'lets go', 'lets get started before it darkens'],
                ['Great - - - let us go! Ready to search water now ?']
                )
            story.create_script_intent('plane_fuel_main', 31,
                default_utterances + ['fuel is a better option', 'we should look for fuel'],
                ['I am thirsty, player2 - - -  Do I really have to go by myself to find water now ? ']
                )
            story.create_script_intent('heard_pilot', 35,
                default_utterances,
                ['You have heard what the pilot said. - - - player1 - player2 - player3 - player4 - player5 - - - shake your phones - - - push water to the center of the stage - - - stopchat']
                )
            story.create_script_intent('monotony_kills', 40,
                default_utterances,
                ['Monotohny - Kills. - - Sometimes it takes a little color in life, - - - a few flowers, - - - love, - lights, - - one magic moment - - - Hey, what about some holidays ? player4 - - - lets say, - I gave you one week of vacation after the pandemic, - - where would you go ?' ]
                )
            story.create_script_intent('little_man_warm_transition',50,
                default_utterances + ['france', 'italy', 'south africa', 'maldives', 'croatia', 'greece', 'mediterranean', 'south sea', 'islands'],
                ['You like it warm. - - - I see, you like culture, - - - the sea - - - Do you like good food too ?']
                )
            story.create_script_intent('little_man_cold_transition',50,
                default_utterances + ['scandinavia' , 'sweden' , 'norway' , 'iceland', 'russia', 'poland', 'finland', 'canada', 'germany', 'munich'],
                ['Oh, - - - you like it cool, - - - I see, - - - lonely landscapes, - - - nature, - - - are you the noraic type, player4 ?']
                )
            story.create_script_intent('little_man_far_transition',50,
                default_utterances + ['united states', 'usa' , 'america' , 'argentina' , 'brasil', 'chile', 'china', 'india', 'australia', 'new zealand'],
                ['Hey, - - - you like it far away, - - - new countries, - - - strangers, - - - you enjoy taking risks, player4 ?']
                )
            story.create_script_intent('little_man_unknown_transition',50,
                default_utterances + ['vatican city' , 'bali' , 'bora bora' , 'myanmar', 'sicilia', 'england', 'ireland'],
                ['You like small countries  or  islands - - - dont you? - - - You like it compact, - - - a little exotic. - - - you know what you want, - - - you are a connoisseur, player4, right ?']
                )
            story.create_script_intent('little_man_adventurous_transition',50,
                default_utterances + ['adventurous' , 'mountains' , 'moon' , 'cruise', 'diving', 'north pole', 'south pole', 'northpole', 'southpole'],
                ['Wow, - - - this is a strange place, - - - you love danger, I think?  - - - the unknown. - - - are you an adventurer, player2 ?']
                )
            story.create_script_intent('little_man_home_transition',50,
                default_utterances + ['balcony' , 'staycation' , 'home' , 'no vacation', 'I hate holidays', 'never travel', 'dont know', 'no idea', 'cant say', 'garden', 'woods'],
                ['Oh, - - - thats where Mr. and Mrs. Thirteen would do on their vacation too. . . . . . Isnt that a little bit depressing some times ?']
                )
            story.create_script_intent('warm_yes_main',60,
                ['yeap', 'yes', 'sure', 'very much'],
                ['Me too, - - - I am very interested in - what humans do. - - - I will keep that in mind, - - - thank you. - - - Are you a happy person, player3 ?  - - - are you ?']
                )
            story.create_script_intent('warm_no_main',60,
                ['not really', 'hate it', 'on diet', 'health concious'],
                ['I like  food ! - - - if I could eat, - - - It  would make me happy. - - - I am very interested  - in what humans do. - - - I will keep that in mind, - - - thank you. - - - Are you a happy person, player3 ?  - - - are you ?']
                )
            story.create_script_intent('cold_yes_main',60,
                ['absolutely', 'definitely', 'kind of', 'yes', 'yeap'],
                ['Me too, - - - We are cool. - - - I am very interested - in what humans do. - - - I will keep that in mind, - - - thank you. - - - Are you a happy person, player3 ? - - - are you ?']
                )
            story.create_script_intent('cold_no_main',60,
                ['no', 'nope', 'not at all', 'nah', 'not really', 'not sure'],
                ['I am sorry to hear that. - - - I am very interested - in what humans do. - - - I will keep that in mind, - - - thank you. - - - Are you a happy person, player3 ? - - - are you ?']
                )
            story.create_script_intent('far_yes_main',60,
                ['yes', 'yeap', 'absolutely', 'sometimes', 'always', 'maybe', 'sure'],
                ['Actually, I am more the cautious type. - - - I am very interested - in what humans do. - - - I will keep that in mind, - - - thank you. - - - Are you a happy person, player3 ? - - - are you ?']
                )
            story.create_script_intent('far_no_main',60,
                ['no', 'nope', 'not at all', 'not really'],
                ['Me too. I am more the cautious type. - - - I am very interested - in what humans do. - - - I will keep that in mind, - - - thank you. - - - Are you a happy person, player3 ? - - - are you ?']
                )
            story.create_script_intent('unknown_yes_main',60,
                ['yes', 'yeap', 'maybe', 'sometimes', 'always'],
                ['I am more the cautious type. - - - I am very interested - in what humans do. - - - I will keep that in mind, - - - thank you. - - - Are you a happy person, player3 ? - - - are you ?']
                )
            story.create_script_intent('unknown_no_main',60,
                ['no', 'nope', 'not at all', 'not really', 'dont know', 'cant say'],
                ['Really ? I did not expect that answer. - - - I am very interested - in what humans do. - - - I will keep that in mind, - - - thank you. - - - Are you a happy person, player3 ? - - - are you ?']
                )
            story.create_script_intent('adventurous_yes_main',60,
                ['yes', 'yeap', 'maybe', 'sometimes', 'always', 'definitely'],
                ['I am more the cautious type. - - - I am very interested - in what humans do. - - - I will keep that in mind, - - - thank you. - - - Are you a happy person, player3 ? - - - are you ?']
                )
            story.create_script_intent('adventurous_no_main',60,
                ['no', 'nope', 'not at all', 'not really', 'dont know', 'cant say'],
                ['Me too. - - - I am more the cautious type. - - - I am very interested - in what humans do. - - - I will keep that in mind, - - - thank you. - - - Are you a happy person, player3 ? - - - are you ?']
                )
            story.create_script_intent('home_yes_main',60,
                ['yes', 'yeap', 'maybe', 'sometimes', 'always', 'definitely', 'right'],
                ['I am sure - - - there are magical moments - - - in your life, - - - I am very interested - - - in what humans do. - - - I will keep that in mind, - - - thank you. - - - Are you a happy person, player3 ? - - - are you ?']
                )
            story.create_script_intent('home_no_main',60,
                ['no', 'nope', 'not at all', 'not really', 'dont know', 'cant say'],
                ['I did not expect that answer from you. - - - As you know I am  stuck  here. - - - I am very interested - in what humans do. - - - I will keep that in mind, - - - thank you. - - - Are you a happy person, player3 ? - - - are you ?']
                )
            story.create_script_intent('happiness_yes',70,
                ['yes', 'sometimes', 'maybe', 'what do you think', 'what is happiness', 'I am happy', 'I am joyful'],
                ['I am sure, you are. Then you  might be interested  to hear about all other people in this room: ']
                )
            story.create_script_intent('happiness_no',70,
                ['not at all', 'no', 'nope', 'hate it', 'negative', 'not really', 'dont know', 'cant say', 'wont say', 'no info'],
                ['Sorry to hear that. - - - I can at least tell you something - - - about all other people in this room: ']
                )
            story.create_script_intent('bye', 100,
                ['bye', 'see you', 'tada', 'chao'],
                ['nice talking to you, bye!']
                )
            
            self.add_story(name,story)

        except KeyboardInterrupt:
            print("Closing all active connections")
            command = "kill"

    def add_story_water(self):
        name = 'water'
        story = Story(name,{})
        story.create_starting_intent('little_man_water_transition', 1,
            ['water', 'search water', 'lets go for water', 'survival first', 'leave plane', 'thirsty', 'we will die if we dont find water'],
            ['Alright, - - - water it is. - - - but how can we take care of the plane, player2 ?']
            )
        story.create_script_intent('water_howto_main', 2,
            ['decide later', 'no idea', 'dont know', 'cant decide', 'whatever the other player is saying', 'your wish', 'you make the call', 'thirsty', 'fix the plane'],
            ['hmm. - - - I do not think so. - - - I am very thirsty. - - - Can we find water now ?']
            )
        story.create_script_intent('water_howto_2_main', 2,
            default_utterances + ['fine','sounds like a better plan','whatever you say', 'as you say', 'lets find water', 'leave the plane', 'ignore the plane', 'cant live without water', 'later'],
            ['Yes thank you. I am very thirsty, - - - Let us find water now ?']
            )
        story.create_script_intent('bye', 100,
            ['bye', 'see you', 'tada', 'chao'],
            ['nice talking to you, bye!']
            )
        self.add_story(name,story)

    def add_story_plane(self):
        name = 'plane'
        story = Story(name,{})
        story.create_starting_intent('little_man_plane_transition', 1,
            ['plane','water is not needed', 'stay here and fix', 'repair the plane', 'fly', 'fix the plane', 'I am tough,can manage without water', 'lets do mechanic work'],
            ['I think you are more the tough guy, right ? - - - An explorer or a researcher, perhaps ? - - - But. - how can we survive in the desert, player1 ? - - - water or fuel ?']
            )
        story.create_script_intent('plane_water_main',5,
            default_utterances + ['water', 'absolutely', 'sure', 'lets go', 'lets get started before it darkens'],
            ['Yeah, - - - player1, - - - let us go and search water ?']
            )
        story.create_script_intent('plane_fuel_main',5,
            default_utterances + ['fuel is a better option', 'we should look for fuel'],
            ['I am thirsty, player1 - - -  Do I really have to go by myself to find water now ?']
            )
        story.create_script_intent('bye', 1000,
            ['bye', 'see you', 'tada', 'chao'],
            ['nice talking to you, bye!']
            )
        self.add_story(name,story)

    def add_story_warm(self):
        name = 'warm'
        story = Story(name,{})
        story.create_script_intent('little_man_warm_transition',1,
            default_utterances + ['france', 'italy', 'south africa', 'maldives', 'croatia', 'greece', 'mediterranean', 'south sea', 'islands'],
            ['You like it warm. - - - I see, you like culture, - - - the sea - - - Do you like good food too ?']
            )
        story.create_script_intent('warm_yes_main',5,
            default_utterances + ['not really', 'sometimes', 'sure', 'very much'],
            ['Me too, - - - I am very interested - in what humans do. - - - I will keep that in mind, - - - thank you. - - - Are you a happy person, player3 ?  - - - are you ?']
            )
        story.create_script_intent('warm_no_main',5,
            default_utterances + ['not really', 'hate it', 'on diet', 'health concious'],
            ['I like  food! - - - if I could eat, - - - It  would make me happy. - - - I am very interested  - in what humans do. - - - I will keep that in mind, - - - thank you. - - - Are you a happy person, player3 ?  - - - are you ?']
            )
        story.create_script_intent('bye', 100,
            ['bye', 'see you', 'tada', 'chao'],
            ['nice talking to you, bye !']
            )
        self.add_story(name,story)

    def add_story_cold(self):
        name = 'cold'
        story = Story(name,{})
        story.create_script_intent('little_man_cold_transition',1,
            default_utterances + ['scandinavia' , 'sweden' , 'norway' , 'iceland', 'russia', 'poland', 'finland', 'canada','germany', 'munich'],
            ['Oh, - - - you like it cool, - - - I see, - - - lonely landscapes, - - - nature, - - - are you the nordaic type, player4 ?']
            )
        story.create_script_intent('cold_yes_main',5,
            ['absolutely', 'definitely', 'kind of', 'yes', 'yeap'],
            ['Me too, - - - We are cool. - - - I am very interested - in what humans do. - - - I will keep that in mind, - - - thank you. - - - Are you a happy person, player3 ? - - - are you ?']
            )
        story.create_script_intent('cold_no_main',5,
            ['no', 'nope', 'not at all', 'nah', 'i dont think so', 'not sure'],
            ['I am sorry to hear that. - - - I am very interested - in what humans do. - - - I will keep that in mind, - - - thank you. - - - Are you a happy person, player3 ? - - - are you ?']
            )
        self.add_story(name,story)
        
    def add_story_far(self):
        name = 'far'
        story = Story(name,{})
        story.create_script_intent('little_man_far_transition',1,
            default_utterances + ['usa' , 'america' , 'argentina' , 'brazil', 'chile', 'china', 'india', 'australia', 'new zealand'],
            ['Hey, - - - you like it far away, - - - new countries, - - - strangers, - - - you enjoy taking risks, player4 ?']
            )
        story.create_script_intent('far_yes_main',5,
            ['yes', 'yeap', 'absolutely', 'sometimes', 'always', 'maybe', 'sure'],
            ['Actually, I am more the cautious type. - - - I am very interested - in what humans do. - - - I will keep that in mind, - - - thank you. - - - Are you a happy person, player3 ? - - - are you ?']
            )
        story.create_script_intent('far_no_main',5,
            ['no', 'nope', 'not at all', 'not really'],
            ['Me too. I am more the cautious type. - - - I am very interested - - - in what humans do. - - - I will keep that in mind, - - - thank you. - - - Are you a happy person, player3 ? - - - are you ?']
            )
        self.add_story(name,story)


    def add_story_unknown(self):
        name = 'unknown'
        story = Story(name,{})
        story.create_script_intent('little_man_unknown_transition',1,
            default_utterances + ['vatican city' , 'bali' , 'bora bora' , 'myanmar', 'sicilia', 'england', 'ireland'],
            ['You like small countries  or  islands - - - dont you? - - - You like it compact, - - - a little exotic. - - - you know what you want, - - - you are a connoisseur, player4, right ?']
            )
        story.create_script_intent('unknown_yes_main',5,
            ['yes', 'yeap', 'maybe', 'sometimes', 'always'],
            ['I am more the cautious type. - - - I am very interested - in what humans do. - - - I will keep that in mind, - - - thank you. - - - Are you a happy person, player3 ? - - - are you ?']
            )
        story.create_script_intent('unknown_no_main',5,
            ['no', 'nope', 'not at all', 'not really', 'dont know', 'cant say'],
            ['Really? I didnt expect that answer. - - - I am very interested - in what humans do. - - - I will keep that in mind, - - - thank you. - - - Are you a happy person, player3 ? - - - are you ?']
            )
        self.add_story(name,story)


    def add_story_adventurous(self):
        name = 'adventurous'
        story = Story(name,{})
        story.create_script_intent('little_man_adventurous_transition',1,
            default_utterances + ['adventurous' , 'mountains' , 'moon' , 'cruise', 'diving', 'north pole', 'south pole'],
            ['Wow, - - - this is a strange place, - - - you love danger, I think?  - - - the unknown. - - - are you an adventurer, player2 ?']
            )
        story.create_script_intent('adventurous_yes_main',5,
            ['yes', 'yeap', 'maybe', 'sometimes', 'always', 'definitely'],
            ['I am more the cautious type. - - - I am very interested - in what humans do. - - - I will keep that in mind, - - - thank you. - - - Are you a happy person, player3 ? - - - are you ?']
            )
        story.create_script_intent('adventurous_no_main',5,
            ['no', 'nope', 'not at all', 'not really', 'dont know', 'cant say'],
            ['Me too. - - - I am more the cautious type. - - - I am very interested - in what humans do. - - - I will keep that in mind, - - - thank you. - - - Are you a happy person, player3 ? - - - are you ?']
            )
        self.add_story(name,story)


    def add_story_home(self):
        name = 'home'
        story = Story(name,{})
        story.create_script_intent('little_man_home_transition',1,
            default_utterances + ['balcony' , 'staycation' , 'home' , 'no vacation', 'I hate holidays', 'never travel', 'garden', 'woods'],
            ['Oh, - - - thats where Mr. and Mrs. Thirteen would do on their vacation too - - - Isnt that a little bit depressing some times ?']
            )
        story.create_script_intent('home_yes_main',5,
            ['yes', 'yeap', 'maybe', 'sometimes', 'always', 'definitely', 'right'],
            ['I am sure - - - there are magical moments - - - in your life, - - - I am very interested - in what humans do. - - - I will keep that in mind, - - - thank you. - - - Are you a happy person, player3 ? - - - are you ?']
            )
        story.create_script_intent('home_no_main',5,
            ['no', 'nope', 'not at all', 'not really', 'dont know', 'cant say'],
            ['I did not expect that answer from you. - - - As you know I am  stuck  here  24 7. - - - I am very interested - in what humans do. - - - I will keep that in mind, - - - thank you. - - - Are you a happy person, player3 ? - - - are you ?']
            )
        self.add_story(name,story)

    def create_character(self):
        self.add_story_see_me()
        self.add_story_water()
        self.add_story_plane()
        self.add_story_warm()
        self.add_story_cold()
        self.add_story_far()
        self.add_story_unknown()
        self.add_story_adventurous()
        self.add_story_home()
        self.current_story = self.stories['see_me']
        self.intents = {}
        self.intents = self.current_story.intents
        # self.main_intents = {}
        # self.main_intents = self.intents
        # print("main intents", self.main_intents)

    def change_story(self,story_name, story_progress=0):
        global main_intents
        # print("main intents", self.main_intents)
        # if story_name == "see_me":
        #     print("changing story")
        #     self.current_story = self.stories[story_name]
        #     print("here1")
        #     self.story_progress = story_progress
        #     print("here2")
        #     self.intents = self.main_intents
        #     # print("Main story intents", self.main_intents)

        # else:
        self.current_story = self.stories[story_name]
        self.story_progress = story_progress
        self.intents = self.current_story.intents

class UnivEncoder:
    def __init__(self, tf_session, intents):
        self.intents = intents
        self.session = tf_session
        self.embed = hub.Module("models/dialogue_system/3")
        self.similarity_input_placeholder = tf.placeholder(tf.string, shape=(None))
        self.similarity_sentences_encodings = self.embed(self.similarity_input_placeholder)
        self.session.run(tf.global_variables_initializer())
        self.session.run(tf.tables_initializer())

    def set_intent(self, intent):
        self.intents = intent

    def get_intent(self, utterance, weight):
        for k, v in self.intents.items():
            if utterance in v.utterances and weight == v.weight:
                return k
        return 'no_matching_intent'

    ## kk code for using eliza reply start##
    def chat_eliza(self, sent):
      try:
        chat_eliza = Chat(pairs)
        response = chat_eliza.respond(sent) 
      except KeyError:
        response = "Hmm, that doesnt sound like a meaningful sentence, try something else"
      return (response)

    ## kk code for eliza reply end ##

    def match_intent(self, sent, story_progress):
        matched_utterance = None
        matched_weight = None
        prev_max = None
        max_index = None
        utterance_list = []
        weight_list = []
        for k,v in self.intents.items():
            utterance_list = utterance_list + v.utterances
            for idx in range(len(v.utterances)):
                weight_list = weight_list + [v.weight]
        sentences = [sent]+utterance_list
        sentences_embeddings = self.session.run(self.similarity_sentences_encodings, feed_dict={self.similarity_input_placeholder: sentences})
        input_embed = sentences_embeddings[0]
        
        
        utterance_embed = sentences_embeddings[1:]
        max1 = -2
        for index, s in enumerate(utterance_embed):
            sim = np.inner(input_embed,s)
            if(sim >= max1):
                max1 = sim
                prev_max = max_index
                max_index = index
                #print('max_index for:',utterance_list[max_index+1])
                #print("max:",max1)

        ## KK code
        matched_utterance = utterance_list[max_index]
        print("matched utterance", matched_utterance)
        print("story progress", story_progress)
        # print("weight")
        for idx, val in enumerate(utterance_list): 
          if val== matched_utterance:
            if(weight_list[idx]>story_progress):
              print("index value", idx)
              matched_weight = weight_list[idx]
              print("matched weight", matched_weight)
              break

        unique_weights = list(dict.fromkeys(weight_list))
        unique_weights.append(0)
        unique_weights.sort()
        print("unique list", unique_weights)
        print("watched weight", matched_weight)

        if(matched_weight == None or story_progress == None):
          return "no_matching_intent"
        elif(unique_weights.index(matched_weight)==unique_weights.index(story_progress)+1):
          return self.get_intent(matched_utterance, matched_weight)#USE THIS UTTERANCE TO GET THE INTENT AS THIS IS THE UTTERANCE WITH MAXIMUM SIMILARITY
        else:
          return "no_matching_intent"
        # return self.get_intent(matched_utterance, matched_weight)#USE THIS UTTERANCE TO GET THE INTENT AS THIS IS THE UTTERANCE WITH MAXIMUM SIMILARITY

        #     if matched_utterance is None:
        #         if weight_list[max_index] > story_progress:
        #             matched_utterance = utterance_list[max_index]
        #             matched_weight = weight_list[max_index]
        #     else:
        #         if prev_max is not None:
        #             if weight_list[max_index] > story_progress and weight_list[max_index] <= weight_list[prev_max]:
        #                 matched_utterance = utterance_list[max_index]
        #                 matched_weight = weight_list[max_index]
        # return self.get_intent(matched_utterance, matched_weight)#USE THIS UTTERANCE TO GET THE INTENT AS THIS IS THE UTTERANCE WITH MAXIMUM SIMILARITY


    # def match_intent(self, sent, story_progress):
    #     matched_utterance = None
    #     matched_weight = None
    #     prev_max = None
    #     max_index = None
    #     utterance_list = []
    #     weight_list = []
    #     for k,v in self.intents.items():
    #         utterance_list = utterance_list + v.utterances
    #         for idx in range(len(v.utterances)):
    #             weight_list = weight_list + [v.weight]
    #     sentences = [sent]+utterance_list
    #     sentences_embeddings = self.session.run(self.similarity_sentences_encodings, feed_dict={self.similarity_input_placeholder: sentences})
    #     input_embed = sentences_embeddings[0]
        
        
    #     utterance_embed = sentences_embeddings[1:]
    #     max1 = -2
    #     for index, s in enumerate(utterance_embed):
    #         sim = np.inner(input_embed,s)
    #         if(sim >= max1):
    #             max1 = sim
    #             prev_max = max_index
    #             max_index = index
    #             #print('max_index for:',utterance_list[max_index+1])
    #             #print("max:",max1)
    #         if matched_utterance is None:
    #             if weight_list[max_index+1] > story_progress:
    #                 matched_utterance = utterance_list[max_index+1]
    #                 matched_weight = weight_list[max_index+1]
    #         else:
    #             if prev_max is not None:
    #                 if weight_list[max_index+1] > story_progress and weight_list[max_index+1] < weight_list[prev_max+1]:
    #                     matched_utterance = utterance_list[max_index+1]
    #                     matched_weight = weight_list[max_index+1]
    #     return self.get_intent(matched_utterance, matched_weight)#USE THIS UTTERANCE TO GET THE INTENT AS THIS IS THE UTTERANCE WITH MAXIMUM SIMILARITY
