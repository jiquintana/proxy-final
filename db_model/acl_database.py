#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:sts=4:ai:et:fileencoding=utf-8:number
import pprint

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from sqlalchemy import create_engine, MetaData


DRIVER = 'sqlite:///proxy.db'
Base = declarative_base()
#metadata = MetaData()

class Singleton(object):
    __instance = None
    def __new__(cls):
        if Singleton.__instance is None:
            Singleton.__instance = object.__new__(cls)
        return Singleton.__instance    

class Database(Singleton):
    __initialized__ = False
    __engine__ = None
    __DBSession__ = None
    __BASE__ = None
    session = None
    def __init__(self):
        if not self.__initialized__:
            print("not initialized")
            self.__initialized__ = True
            self.__engine__ = create_engine(DRIVER, echo=True)
            self.__BASE__= Base
            self.__BASE__.metadata.bind =self.__engine__
            self.__metadata__ = MetaData()
            self.__metadata__.create_all(self.__engine__)            
            self.__DBSession__ = scoped_session(sessionmaker())
            self.__DBSession__.configure(bind=self.__engine__)       
            self.session = self.__DBSession__()

            
        else:
            print("already initialized")
    
    def getBase(self):
        return(self.__BASE__)
    
    def print(self):
        print(self.__engine__)

class Users(Base):
    __tablename__ = 'USERS'
    uid = Column(Integer, primary_key=True, autoincrement=True, unique=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    description = Column(String, nullable=False)
    # many to many User <-> Group
    #relationship("pertenece", secondary = groups, backref = Base.__tablename__)

    def __repr__(self):
        return "User(%r)" % (self.name)


if __name__ == "__main__":
    
    db=Database()
    db2=Database()
    print (Users.__table__)

    print(db)
    print(db2)
    
    print(db.session.query(Users).count())
    for instance in db.session.query(Users):
        print(instance)
    ed_user = Users(name='ed', password_hash='Ed Jones', description='edspassword')
    
    try:
        db.session.add(ed_user)
        db.session.commit()
    except:
        db.session.rollback()
    
    #for instance in db.session.query(User).order_by(User.uid):
    #    print("%r %r" % (instance.name, instance.fullname))
        
    

    print(db.session.query(Users).order_by(Users.uid))
    db2.print()