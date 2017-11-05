import logging
import boto3

from random import randint
import json

from flask import Flask, render_template

from flask_ask import Ask, question, statement, session, audio

from sql_alchemy_tables import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

import json

user_key = "keydaniel"

app = Flask(__name__)

ask = Ask(app, "/")

logging.getLogger("flask_ask").setLevel(logging.DEBUG)

engine = create_engine('sqlite:///memories.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

@ask.launch

def new_game():

    welcome_msg = render_template('go')

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

    return question(msg)


def getStep(StepNumber, Everydayrecipies, CookingActions,WeightIngredients, Ingredients, CookingTime,CookingTemperature):
 
    if(CookingTemperature>0):
        step = render_template('ins_step_2',StepNumber=StepNumber, Everydayrecipies=Everydayrecipies, CookingActions=CookingActions,WeightIngredients=WeightIngredients, Ingredients=Ingredients, CookingTime=CookingTime, CookingTemperature=CookingTemperature)
    elif(WeightIngredients>0):
        step = render_template('ins_step_1',StepNumber=StepNumber, Everydayrecipies=Everydayrecipies, CookingActions=CookingActions,WeightIngredients=WeightIngredients, Ingredients=Ingredients, CookingTime=CookingTime)
    else:
        step = render_template('ins_step_3',StepNumber=StepNumber, Everydayrecipies=Everydayrecipies, CookingActions=CookingActions,WeightIngredients=WeightIngredients, Ingredients=Ingredients, CookingTime=CookingTime)

    return step


@ask.intent("InsertNewStep", convert={'StepNumber': int, 'WeightIngredients': int, 'CookingTime': int, 'CookingTemperature': int})

def insert_new_step(StepNumber, Everydayrecipies, CookingActions,WeightIngredients, Ingredients, CookingTime, CookingTemperature):
    if(len(Everydayrecipies) < 2):
        return question(render_template('couldnt_follow',title='recipe'))

    db_session = DBSession()
    recipes = db_session.query(Memory).filter(Memory.name.like('%%%s%%' %(Everydayrecipies))).all()
    if len(recipes) == 0:
        recipe = Memory()
        recipe.name = Everydayrecipies
        recipe.type = 1
        db_session.add(recipe)
        db_session.commit()
    recipe_mem = db_session.query(Memory).filter(Memory.name.like('%%%s%%' %(Everydayrecipies))).first()
    print 'recipe_mem is %s, Rec.mem id is %s'%(recipe_mem.name, recipe_mem.id)    
    recipe = db_session.query(Recipe).filter(Recipe.memory_id == recipe_mem.id).first()
    if(recipe==None):
        recipe = Recipe()
        recipe.memory_id = recipe_mem.id
        recipe.ingredients = json.dumps({})
        recipe.steps = json.dumps([])
        db_session.add(recipe)
        db_session.commit()
    steps = json.loads(recipe.steps)
    ingredients = json.loads(recipe.ingredients)
    print recipe.steps, StepNumber != len(steps)+1, StepNumber, 
    if(StepNumber != len(steps)+1):
        return question("That step number is not available")

    if(WeightIngredients>0):
        ingredients[Ingredients] = WeightIngredients
    

    steps.append(getStep(StepNumber, Everydayrecipies, CookingActions,WeightIngredients, Ingredients, CookingTime,CookingTemperature))
    recipe.steps = json.dumps(steps)
    recipe.ingredients = json.dumps(ingredients)
    db_session.add(recipe)
    db_session.commit()

    msg = render_template('added_new_step',StepNumber=StepNumber, Everydayrecipies=Everydayrecipies, CookingActions=CookingActions,WeightIngredients=WeightIngredients, Ingredients=Ingredients, CookingTime=CookingTime)

    return question(msg)


@ask.intent("AskLex")


def ask_lex(Question):
    if(Question==None):
        return statement("Okay, Cool. I will let Lex Know ")
    else:
        client = boto3.client('lex-runtime')
        response = client.post_text(
            botName='OrderFlowers',
            botAlias='flower',
            userId=user_key,
            sessionAttributes={
                'string': 'string'
            },
            requestAttributes={
                'string': 'string'
            },
            inputText=Question
        )
        print response.keys()
        return question(response['message'])



@ask.intent("SendEmail")

def gmail_help():

    return statement("Step 1, Open Gmail... Step 2, In the top left, click Compose... Step 3, In the To field, add recipients..." +
    "Note that, if you want, you can also add recipients in the cc and bcc fields... Step 4, Add a subject to the email. " +
    "Step 5, Write your message... Step 6, At the bottom of the page click Send. Your email will be sent.")

@ask.intent("ShareOnFB")

def fb_help():
    string_help_fb="Step 1, From the top of your timeline or News Feed, " +"click on what type of story you want to share, like status or a photo or a video...Step 2, Type in any details you want to add...Step 3, Select an audience for your post..."+"Step 4, finally Click post. Your message will be posted"
    return statement(string_help_fb)

@ask.intent("BirthdayEvents")
def bday_event():
    bday_gifts="In year 2016, it was a keyboard. In 2015, it was a smart phone and in year 2014, it was a pair of Nike shoes."
    return statement(bday_gifts)


def all_steps(steps):
    s = " "
    for i in range(len(steps)):
        s+= "Step " + str(i+1) + " " + steps[i] + ", "
    return s

@ask.intent("ModifyStep", convert={'StepNumber': int})

def modify_step(StepNumber, Everydayrecipies, CookingActions,WeightIngredients, Ingredients, CookingTime, CookingTemperature):
    if(len(Everydayrecipies) < 2):
        return question(render_template('couldnt_follow',title='recipe'))

    db_session = DBSession()
    recipes = db_session.query(Memory).filter(Memory.name.like('%%%s%%' %(Everydayrecipies))).all()
    if len(recipes) == 0:
        return question('not_present',Everydayrecipies=Everydayrecipies)
    recipe_mem = db_session.query(Memory).filter(Memory.name.like('%%%s%%' %(Everydayrecipies))).first()
    print 'recipe_mem is %s, Rec.mem id is %s'%(recipe_mem.name, recipe_mem.id)    
    recipe = db_session.query(Recipe).filter(Recipe.memory_id == recipe_mem.id).first()
    if(recipe==None):
        return question('not_present',Everydayrecipies=Everydayrecipies)
    steps = json.loads(recipe.steps)
    if((StepNumber-1) not in range(1,len(steps)+1)):
        return question("That step number is not available")
    steps.pop(StepNumber-1)
    recipe.steps = json.dumps(steps)
    db_session.add(recipe)
    db_session.commit()

    # msg = render_template('added_new_step',StepNumber=StepNumber, Everydayrecipies=Everydayrecipies, CookingActions=CookingActions,WeightIngredients=WeightIngredients, Ingredients=Ingredients, CookingTime=CookingTime)

    return question(render_template('removed',Everydayrecipies=Everydayrecipies) + all_steps(steps))

def getAllExperience(recipe_mem,db_session,Everydayrecipies):
    exp = db_session.query(Memory).filter(Memory.name.like('%%%s%%' %(Everydayrecipies))).first()
    if(exp==None):
        return question(render_template("exp_not_available"))
    recipe_exp = db_session.query(Experience).filter(Experience.memory_id == recipe_mem.id).all()
    res = ""
    for rec_exp in recipe_exp:
        # print rec_exp
        res+=rec_exp.experience + " on " + rec_exp.date.strftime("%m-%d-%y") + "  ... "
    return res


@ask.intent("QueryStep", convert={'StepNumber': int,'AddedWeight' : int})

def query_step(StepNumber, Everydayrecipies, AddedWeight, QueryKey, Ingredients):
    if(len(Everydayrecipies) < 2):
        return question(render_template('couldnt_follow',title='recipe'))

    db_session = DBSession()
    recipes = db_session.query(Memory).filter(Memory.name.like('%%%s%%' %(Everydayrecipies))).all()
    if len(recipes) == 0:
        return question(render_template('not_present',Everydayrecipies=Everydayrecipies))
    recipe_mem = db_session.query(Memory).filter(Memory.name.like('%%%s%%' %(Everydayrecipies))).first()
    print 'recipe_mem is %s, Rec.mem id is %s'%(recipe_mem.name, recipe_mem.id)    
    recipe = db_session.query(Recipe).filter(Recipe.memory_id == recipe_mem.id).first()
    print recipe
    if(recipe==None):
        return question(render_template('not_present',Everydayrecipies=Everydayrecipies))
    steps = json.loads(recipe.steps)
    ingredients = json.loads(recipe.ingredients)
    res = ""
    if(StepNumber and StepNumber-1<len(steps)):
        return question(steps[StepNumber-1])
    if(QueryKey and (QueryKey.lower())=="experiences"):
        return question(getAllExperience(recipe_mem,db_session,Everydayrecipies))
    if(QueryKey and (QueryKey.lower()=="list" or QueryKey.lower()=="ingredients" )):
        print ingredients
        for k,v in ingredients.iteritems():
            res+=" "+k+" "+str(v)+" grams , "
        return question(render_template('ingredients',Everydayrecipies=Everydayrecipies, ingredients=res))

    if(QueryKey and (QueryKey.lower())=="steps"):
        return question(all_steps(steps))
    if(AddedWeight and AddedWeight>0):
        if(AddedWeight - ingredients[Ingredients] > 0):
            return question(render_template('addedmore',Everydayrecipies=Everydayrecipies))
        else:
            return question(render_template('addsome',Everydayrecipies=Everydayrecipies, value=(ingredients[Ingredients]-AddedWeight)))
    if(Ingredients in ingredients):
        return question(render_template('addsome',Everydayrecipies=Everydayrecipies))
    if(QueryKey and (QueryKey.lower()=="grams" )):
        if(Ingredients in ingredients):
            return question(render_template('add',Everydayrecipies=Everydayrecipies,value=ingredients[Ingredients]))
        else:
            return question(render_template("not_present_ing"))

    # msg = render_template('added_new_step',StepNumber=StepNumber, Everydayrecipies=Everydayrecipies, CookingActions=CookingActions,WeightIngredients=WeightIngredients, Ingredients=Ingredients, CookingTime=CookingTime)

    return question(render_template('unable',Everydayrecipies=Everydayrecipies) + all_steps(steps))


@ask.intent("PlayRecoIntent")
def play_music():
    stream_url='https://archive.org/download/plpl011/plpl011_05-johnny_ripper-rain.mp3'
    speech="Warm Greetings , music recommended by your mom is rain by johnny ripper. "
    return audio(speech).play(stream_url)

@ask.intent("StopRecoIntent")
def stop_music():
    speech="Stopping the music."
    return audio(speech).stop()


@ask.intent("AddMemory")

def addmemory(Everydayrecipies,EverydayRate):
    if(len(Everydayrecipies) < 2):
        return question(render_template('couldnt_follow',title='recipe'))

    db_session = DBSession()
    recipes = db_session.query(Memory).filter(Memory.name.like('%%%s%%' %(Everydayrecipies))).all()
    if len(recipes) == 0:
        return question(render_template('not_present',Everydayrecipies=Everydayrecipies))
    recipe_mem = db_session.query(Memory).filter(Memory.name.like('%%%s%%' %(Everydayrecipies))).first()
    print 'recipe_mem is %s, Rec.mem id is %s'%(recipe_mem.name, recipe_mem.id)    
    
    exp = Experience()
    exp.experience = EverydayRate
    exp.memory_id = recipe_mem.id
    db_session.add(exp)
    db_session.commit()
    return question("Your comment has been saved")


@ask.intent("AddRecommendations")
def add_recommendation(BookTitle, MediaType, MovieTitle):
    db_session = DBSession()
    if(MediaType == "movie"):
        title = MovieTitle 
    else:
        title = BookTitle
    print title, MediaType
    media = db_session.query(Memory).filter(Memory.name.like('%%%s%%' %(MediaType))).all()
    if len(media) == 0:
        media = Memory()
        media.name = MediaType
        media.type = 3
        db_session.add(media)
        db_session.commit()
    else:
        media = media[0]
    print 'Media is %s, media.id is %s'%(media, media.id)    
    memory = media
    media = db_session.query(Recommendation).filter(Recommendation.memory_id == memory.id).all()
    if len(media) == 0:
        media = Recommendation()
        media.memory_id = memory.id
        media.list = json.dumps([])
        db_session.add(media)
        db_session.commit()
    else:
        media = media[0]
    
    media_list = media.list
    list_json = json.loads(media_list)
    list_json.append(title)
    
    media_list = json.dumps(list_json)
    media.list = media_list
    print('Media is %s, media.memory_id is %s'%(media, media.memory_id))
    db_session.add(media)
    db_session.commit()
    
    msg = render_template('add_rec', MediaType=MediaType, title = title)
    return question(msg)

if __name__ == '__main__':

    app.run(debug=True)
