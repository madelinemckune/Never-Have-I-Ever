from __future__ import print_function
import random
import json

global QUESTION_LIST
QUESTION_LIST = []
global ASKED_QUESTIONS
ASKED_QUESTIONS = []
global CURR_ROUND
CURR_ROUND = 0
global PLAY_ROUNDS_GAME
PLAY_ROUNDS_GAME = False
# --------------- Helper Functions ----------------------
def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Session Functions ------------------
def get_question_response():
    session_attributes = {}
    speech_output = ""
    card_title = "Question"
    global QUESTION_LIST
    global CURR_ROUND
    global PLAY_ROUNDS_GAME
    global ASKED_QUESTIONS
    # check that QUESTION_LIST is not undefined
    try:
        QUESTION_LIST
    except:
        return build_response(session_attributes, build_speechlet_response(
                    card_title, "Sorry, question list does not exist.", "Sorry, try again later!", True))
    else:
        # pick a random index
        index = random.randint(0,len(QUESTION_LIST)-1)
        # make sure we don't get stuck in an infinite loop
        loops = 0
        while (QUESTION_LIST[index]["asked"] == True):
            # choose a new question
            index = random.randint(0,len(QUESTION_LIST)-1)
            loops = loops + 1
            if (loops == len(QUESTION_LIST)):
                write_to_output()
                # break if there are no more questions to ask
                return build_response(session_attributes, build_speechlet_response(
                    card_title, "There are no more questions to ask!", "Are you still playing?", True))
        if (PLAY_ROUNDS_GAME == True and CURR_ROUND == 8):
            speech_output = "This is the last question! " + QUESTION_LIST[index]["question"]
            CURR_ROUND = CURR_ROUND + 1
            QUESTION_LIST[index]["asked"] = True
            ASKED_QUESTIONS.append(QUESTION_LIST[index]["question"])
            reprompt_text = "Do you want to play again?"
            should_end_session = True
            return build_response(session_attributes, build_speechlet_response(
                card_title, speech_output, reprompt_text, should_end_session))
        elif (PLAY_ROUNDS_GAME == True and CURR_ROUND == 9):
            return handle_session_end_request()
            
        else:
            if (PLAY_ROUNDS_GAME):
                speech_output +="This is round " + str(CURR_ROUND) + ". "
                CURR_ROUND = CURR_ROUND + 1
            # ask current question
            speech_output += QUESTION_LIST[index]["question"]
            # set current question to asked
            QUESTION_LIST[index]["asked"] = True
            ASKED_QUESTIONS.append(QUESTION_LIST[index]["question"])
            reprompt_text = "Are you still playing?"
            should_end_session = False
            return build_response(session_attributes, build_speechlet_response(
                card_title, speech_output, reprompt_text, should_end_session))

def get_welcome_response():
    # session_attributes = {"question_list":[], "asked_questions":[], "curr_round": 0, "play_rounds_game":False}
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to Madeline's CSCI 101 Final Project, Never Have I Ever! You can say Alexa start game or Alexa read me the rules, to get started!"
    # If the user either does not reply to the welcome message
    reprompt_text = "I don't know if you heard me, welcome to Madeline's CSCI 101 project!"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
        
def get_rules_response():
    session_attributes = {}
    card_title = "Rules"
    speech_output = "The game Never Have I Ever is a game where participants put down a finger if they have done the action that I read off. There are two ways to play Madeline's Alexa, Never Have I ever version. The first is to play with 10 rounds. Each person will start with 10 fingers up. I will ask 10 questions in a row. At the end of the 10 rounds, the person with the most fingers is the winner. The second is to play until the first person is out of fingers. I will continue asking questions until you ask me to stop. If you are ready, say alexa start the game!"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, "Would you like me to read the rules again?", should_end_session))

def get_play_game_response():
    session_attributes = {}
    card_title = "Play Game"
    speech_output = "Would you like to play 10 rounds or until the first person is out?"
    reprompt_text = "I don't know if you heard me, would you like to play 10 rounds or until the first person is out?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_rounds_response():
    global PLAY_ROUNDS_GAME
    PLAY_ROUNDS_GAME = True
    session_attributes = {}
    card_title = "Play Rounds"
    speech_output = "Alright! Ten rounds it is. Let me know when you are ready for your first question by saying alexa, ask a question!"
    reprompt_text = "Are you ready for your first question?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_unlimited_response():
    session_attributes = {}
    card_title = "Unlimited"
    speech_output = "Alright! Let me know when you are ready to begin by saying, Alexa, ask a question. You can end the game at any time by saying, Alexa, stop."
    reprompt_text = "Are you ready for your first question?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
        

def write_to_output():
    # write asked questions to file
    asked_questions_json = json.dumps(ASKED_QUESTIONS)
    print(asked_questions_json)
    

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for playing Never Have I Ever!" \
                    "Have a nice day! "
    # End the session && exit the skill
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

# --------------- Events ------------------
#Called when the session starts.
def on_session_started(session_started_request, session):
    #read in from the file
    f = open('questions.json',)
    global QUESTION_LIST
    QUESTION_LIST = json.load(f)
    f.close()
    #initialize a list of questions that were asked
    if (len(QUESTION_LIST) == 0):
        # break if there are no questions
        return build_response(session_attributes, build_speechlet_response(
            card_title, "There are no questions in the file!", "Are you still playing?", True))
    pass

# Called when the user launches the skill without specif intent
def on_launch(launch_request, session):
    # Call launch message
    return get_welcome_response()

# Called when the user launches the skill with specif intent
def on_intent(intent_request, session):

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']


    # Intent handler
    if intent_name == "play":
        return get_play_game_response()
    elif intent_name == "rules":
        return get_rules_response()
    elif intent_name == "question":
        return get_question_response()
    elif intent_name == "rounds":
        return get_rounds_response()
    elif intent_name == "unlimited":
        return get_unlimited_response()
    elif intent_name == "stop":
        return handle_session_end_request()
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

# Called when the session ends
def on_session_ended(session_ended_request, session):
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])


# --------------- Main handler ------------------
#Boiler plate from AWS
def lambda_handler(event, context):
    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
