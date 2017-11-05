import logging

from random import randint

from flask import Flask, render_template

from flask_ask import Ask, statement, question, session

from sql_alchemy_tables import *

import json

app = Flask(__name__)

ask = Ask(app, "/")

logging.getLogger("flask_ask").setLevel(logging.DEBUG)

engine = create_engine('sqlite:///memories.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

@ask.launch

def new_game():

    welcome_msg = render_template('welcome')

    return question(welcome_msg)



@ask.intent("QueryStepIntent")

def next_round():

    numbers = [randint(0, 9) for _ in range(3)]

    round_msg = render_template('round', numbers=numbers)

    session.attributes['numbers'] = numbers[::-1]  # reverse

    return question(round_msg)



@ask.intent("YesIntent")

def next_round():

    numbers = [randint(0, 9) for _ in range(3)]

    round_msg = render_template('round', numbers=numbers)

    session.attributes['numbers'] = numbers[::-1]  # reverse

    return question(round_msg)


@ask.intent("AnswerIntent", convert={'first': int, 'second': int, 'third': int})

def answer(first, second, third):

    winning_numbers = session.attributes['numbers']

    if [first, second, third] == winning_numbers:

        msg = render_template('win')

    else:

        msg = render_template('lose')

    return statement(msg)


@ask.intent("InsertNewStepIntent", convert={'StepNumber': int, 'WeightIngredients': int, 'CookingTime': int, 'CookingTemperature': int})

def insert_new_step(StepNumber, Everydayrecipies, CookingActions,WeightIngredients, Ingredients, CookingTime):

    if(StepNumber > 0 and len(Everydayrecipies)>0 and len(CookingActions)>0 and len(WeightIngredients)>0 and len(Ingredients) > 0):
        msg = render_template('insert_new_step')
    return statement(msg)


@ask.intent("AddMemoryIntent")

def addmemory():

    return statement("Your comment has been saved")


@ask.intent("AddRecommendations")
def add_recommendation(title, media_type):
    db_session = DBSession()
    media = db_session.query(Memory).filter(Memory.name.like('%%%s%%').format(media_type)).all()
    if len(media) == 0:
        media = Memory()
        media.name = media_type
        media.type = 3
        session.add(media)
        session.commit()
    else:
        media = media.first()
        
    media = db.session.query(Recommendation).filter(Recommendation.memory_id == media.id).all()
    if len(media) == 0:
        media = Recommendation()
        media.memory_id = media.id
        media.list = json.dumps([])
        session.add(media)
        session.commit()
    else:
        media = media.first()
        
    media_list = media.list
    list_json = json.loads(media_list)
    list_json.add(title)
    
    media_list = json.dumps(list_json)
    media.list = media_list
    session.add(media)
    session.commit()
    
    msg = render_template('add_rec')
    return statement(msg)
    
if __name__ == '__main__':

    app.run(debug=True)
