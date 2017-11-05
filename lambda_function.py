import urllib2
import json

API_BASE=""

def lambda_handler(event, context):
    print event
    if (event["session"]["application"]["applicationId"] !=
            "amzn1.ask.skill.c0651192-1303-434d-9425-33bd9623a061"):
        raise ValueError("Invalid Application ID")
    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])

    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])

def on_session_started(session_started_request, session):
    print "Starting new session."

def on_launch(launch_request, session):
    return get_welcome_response()

def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]

    if intent_name == "Email":
        return get_email_help()
    elif intent_name == "Facebook":
        return get_fb_help()
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    print "Ending session."
    # Cleanup goes here...

def handle_session_end_request():
    card_title = "PLATO - Thanks"
    speech_output = "Thank you for using the PLATO skill.  See you next time!"
    should_end_session = True

    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))

def get_welcome_response():
    session_attributes = {}
    card_title = "PLATO"
    speech_output = "Welcome to the Alexa PLATO tech help for techno illiterate. " \
                    "You can ask me for tech help."
                    
    reprompt_text = "Please ask me for tech help, " \
                    "for example how to send an email."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_system_status():
    session_attributes = {}
    card_title = "PLATO Status"
    reprompt_text = ""
    should_end_session = False

    #response = urllib2.urlopen(API_BASE + "/status")
    #bart_system_status = json.load(response)   

    speech_output = "There are currently " + bart_system_status["traincount"] + " trains operating. "

    if len(bart_system_status["message"]) > 0:
        speech_output += bart_system_status["message"]
    else:
        speech_output += "The trains are running normally."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_email_help():
    session_attributes = {}
    card_title = "PLATO  Email help"
    reprompt_text = "I'm not sure if you wanted help with email."\
                    "Can you repeat again."
    should_end_session = False
    #response = ""
    #response = urllib2.urlopen(API_BASE + "/emailhelp")
    #bart_elevator_status = json.load(response) 

    speech_output = "Open Gmail. In the top left, click Compose. In the To field, add recipients."\
    "If you want, you can also add recipients in the cc and bcc fields.Add a subject."\
    "Write your message. At the bottom of the page click Send."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_fb_help(intent):
    session_attributes = {}
    card_title = "PLATO facebook help"
    
    reprompt_text = "I'm not sure if you wanted help with facebook."\
                    "Can you repeat again."
    
    speech_output = "From the top of your timeline or News Feed, " \
                    "click what type of story you want to share, like status, photo or video."\
                    "Type in any details you want to add."\
                    "Select an audience for your post"\
                    "Click post."


    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }



def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
}