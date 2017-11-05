# -*- coding: utf-8 -*-
"""

"""
from sql_alchemy_tables import Base, Memory, Recipe, Instruction, Experience
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime

engine = create_engine('sqlite:///memories.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

memory = Memory()
memory.name = 'Butter Chicken Recipe'
memory.type = 1

memory2 = Memory()
memory2.name = 'Send Email Instruction'
memory2.type = 2

memory3 = Memory()
memory3.name = 'Connect to Wifi Instruction'
memory3.type = 2

memory4 = Memory()
memory4.name = 'Smoked Salmon Recipe'
memory4.type = 1

session.add(memory)
session.add(memory2)
session.add(memory3)
session.add(memory4)

session.commit()

exp = Experience()
exp.memory_id = 1
exp.date = datetime.now()
exp.experience = 'Horrible'

exp2 = Experience()
exp.memory_id = 2
exp.date= datetime.now()
exp.experience = 'Awesome'

session.add(exp)
session.add(exp2)

session.commit()

ins = Instruction()
ins.memory_id = 2
ins.steps = ''