import logging
from random import randint
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session, audio

class Room(object):
    def __init__(self,objects,goal,level,hint,state,prompt):
        self._objects=objects #Objects in the room
        self._goal=goal #Goal required to cross the level
        self._level=level #Level Number
        self._hint=hint
        self._state=[]
        self._prompt=prompt

    def cleared(self):
        for i in self._goal:
            if i not in self._state:
                return -1 #All required items not present
        for i in self._state:
            if i not in self._goal:
                return -2 #More than required being carried
        return 1

    def setState(self,lst): #STATE OF ROOM CLEARED BEFORE APPENDING!!
        self._state=[]
        for i in lst:
            self._state.append(i)
        
    def getObjects_string(self):
        txt="a "
        for i in self._objects:
            txt+=i+', a '
        return txt[:-3]+'.'
    def getObjects_list(self):
        return self._objects
    def getGoal(self):
        return self._goal
    def getHint(self):
        return "Hint: "+self._hint
    def getLevel(self):
        return self._level
    def getPrompt(self):
        return self._prompt

app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger("flask_ask").setLevel(logging.DEBUG)

@ask.launch
def new_game():
    welcome_msg=("I don't need no welcome message. You want me to play you music your mom recommended me?")
    return question(welcome_msg)

@ask.intent("LevelOneIntentQ")
def level_1_q():
    room1=Room(["bottle","pen-drive","nail","spoon","hammer"],["hammer","nail"],1,"You need to choose a hammer and nail.",[],"Hello. You need to affix a photo frame onto a wall in future rooms. Please pick the necessary items, to leave this room.")  
    return question(room1.getPrompt())

@ask.intent("LevelOneIntentA")
def level_1_a(DailyObjects):
    

@ask.intent("YesIntent")
def next_round():
    numbers = [randint(0, 9) for _ in range(3)]
    round_msg = render_template('round', numbers=numbers)
    session.attributes['numbers'] = numbers[::-1]  # reverse
    return question(round_msg)

@ask.intent("PlayRecoIntent")
def play_music():
    stream_url='https://archive.org/download/plpl011/plpl011_05-johnny_ripper-rain.mp3'
    speech="Warm Greetings you idiot."
    return audio(speech).play(stream_url)

@ask.intent("StopRecoIntent")
def stop_music():
    speech="Stopping the music."
    return audio(speech).stop()

@ask.intent("AnswerIntent", convert={'first': int, 'second': int, 'third': int})
def answer(first, second, third):
    winning_numbers = session.attributes['numbers']
    if [first, second, third] == winning_numbers:
        msg = render_template('win')
    else:
        msg = render_template('lose')
    return statement(msg)

if __name__ == '__main__':
    app.run(debug=True)