# -*- coding: utf-8 -*-
"""
"""
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Person(Base):
    id = Column(Integer, primary_key=True)
    first_name = Column(String(250), nullable=False)
    last_name = Column(String(250), nullable=False)
    alias = Column(String(250), nullable=False, index=True)
    
class Memory(Base):
    __tablename__ = 'memory'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    type = Column(Integer, nullable=False)
    p_from = Column(Integer, ForeignKey('person.id'))
    p_to   = Column(Integer, ForeignKey('person.id'))
    meta  = Column(Text)

class Experience(Base):
    __tablename__ = 'experience'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    experience=Column(Text, nullable=False)
    memory_id = Column(Integer, ForeignKey('memory.id'))
    #memory = relationship('Memory', back_populates='experiences')

class Instruction(Base):
    __tablename__ = 'instruction'
    id = Column(Integer, primary_key=True)
    steps = Column(Text, nullable=False)
    memory_id = Column(Integer, ForeignKey('memory.id'))
    #memory = relationship('Memory', back_populates='instruction')

class Recipe(Base):
    __tablename__ = 'recipe'
    id = Column(Integer, primary_key=True)
    steps = Column(Text, nullable=False)
    memory_id = Column(Integer, ForeignKey('memory.id'))
    #memory = relationship('Memory', back_populates='recipe')

class Recommendation(Base):
    __tablename__ = 'movie_list'
    id = Column(Integer, primary_key=True)
    list = Column(Text, nullable=False)
    memory_id = Column(Integer, ForeignKey('memory.id'))


engine = create_engine('sqlite:///memories.db')

Base.metadata.create_all(engine)