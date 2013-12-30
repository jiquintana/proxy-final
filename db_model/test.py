#!/bin/python
# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:sts=4:ai:et:fileencoding=utf-8:number

import pprint
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base, declared_attr, DeferredReflection
from sqlalchemy.orm import relation, sessionmaker, relationship,scoped_session, sessionmaker


engine = create_engine('sqlite:///pepe.db', echo=True)
DBSession = scoped_session(sessionmaker())
DBSession.configure(bind=engine)




class uBase(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.upper()    

#Base = declarative_base(cls=Base)
Base = declarative_base()

class Rows(object):
    def __init__(self, header, rows):
        self.header = header
        self.rows = rows
 
    def commit(self, model, session=DBSession, commiter=DBSession):
        header = self.header
        for row in self.rows:
            o = model(**dict(zip(header,row)))
            session.add(o)
            commiter.commit()


#DeferredReflection.prepare(engine)
   
    
groups = Table(
    'groups', Base.metadata,
    Column('uid', Integer, ForeignKey('USER.uid'), nullable=False, primary_key=True, index=True),
    Column('gid', Integer, ForeignKey('GROUP.gid'), nullable=False, primary_key=True, index=True),

    #rel_uid = relationship("USER", backref="_map_user2group", primaryjoin="_M_U2G.uid==USER.uid")
    #rel_gid = relationship("GROUPS", backref="_map_user2group",primaryjoin="_M_U2G.gid==GROUPS.gid")
)

class User(Base):
    __tablename__ = 'USER'
    
    uid = Column(Integer, primary_key=True, autoincrement=True, unique=True, index=True)
    name = Column(String(20), nullable=False, unique=True, index=True)
    password_hash = Column(String(16), nullable=False)
    description = Column(String(80), nullable=False)
    # many to many User <-> Group
    #relationship("pertenece", secondary = groups, backref = Base.__tablename__)

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return "User(%r)" % (self.name)


class Group(Base):
    #__table_args__ = ({'autoload': True},)
    __tablename__ = 'GROUP'
    

    gid = Column(Integer, primary_key=True, autoincrement=True, unique=True, index=True)
    name = Column(String(80), nullable=False)
    #teams = relationship('pk_group', backref="_M_G2T")
    #componentes = relationship('componentes', secondary = groups, backref = Base.__tablename__)

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return "Groups(%r)" % (self.name)


class rules_time(Base):
    __tablename__ = 'RULES_TIME'
    #__table_args__ = (Index('idx_rtid' , 'rtid'),)

    rtid = Column(Integer, primary_key=True, autoincrement=True, unique=True, index=True)

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return "RuleTime(%r)" % (self.rtid)


class rules_uris(Base):
    __tablename__ = 'RULES_URIS'
    ruid = Column(Integer, primary_key=True, autoincrement=True, unique=True, name='ruid', index=True)
    rule_uri = Column(String(256))

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return "RuleURI(%r)" % (self.ruid)    

class rules_words(Base):
    __tablename__ = 'RULES_WORDS'
    rwid = Column(Integer, primary_key=True, autoincrement=True, unique=True, index=True)
    words = Column(String(256), nullable=False)

    def __init__(self, name=None):
        self.name = name

    def __repr__(self):
        return "RuleURI(%r)" % (self.ruid)    

class _m_g2t(Base):
    __tablename__ = '_M_G2T'
    gid = Column(Integer, ForeignKey('GROUP.gid', name='allowed_time'), nullable=False, primary_key=True, index=True)
    rtid = Column(Integer, ForeignKey('RULES_TIME.rtid', name='time_allowed'), nullable=False, primary_key=True, index=True)

    def __repr__(self):
        return "MAP G2T (%r:%r)" % (self.gid, self.rtid)    

class _m_g2u(Base):
    __tablename__ = '_M_G2U'
    gid = Column(Integer, ForeignKey('GROUP.gid', name='allowed_uris'), nullable=False, primary_key=True, index=True)
    ruid = Column(Integer, ForeignKey('RULES_URIS.ruid', name='uris_allowed'), nullable=False, primary_key=True, index=True)
    #rel_gid = relationship("GROUPS", backref="_m_g2u",primaryjoin="_M_G2U.gid==GROUP.gid")
    #rel_rtid = relationship("RULES_URIS", backref="_m_g2u", primaryjoin="_M_G2U.rtid==RULES_URIS.ruid")

    def __repr__(self):
        return "MAP G2U (%r:%r)" % (self.gid, self.ruid)

class _m_g2w(Base):
    __tablename__ = '_M_G2W'
    #__table_args__ = (Index('idx_g2wo_1rwid' , 'rwid'), Index('idx_g2wo_gid' , 'gid'))

    gid = Column(Integer, ForeignKey('GROUP.gid', name='allowed_words'), nullable=False, primary_key=True, index=True)
    rwid = Column(Integer, ForeignKey('RULES_WORDS.rwid', name='words_allowed'), nullable=False, primary_key=True, index=True)
    #rel_gid = relationship("GROUPS", backref="_m_g2w",primaryjoin="_M_G2W.gid==GROUPS.gid")
    #rel_rwid = relationship("RULES_WORDS", backref="_m_g2w", primaryjoin="_M_G2W.rwid==RULES_WORDS.rwid")

    def __repr__(self):
        return "MAP G2W (%r:%r)" % (self.gid, self.rwid)

class _m_u2g(Base):
    __tablename__ = '_M_U2G'
    uid = Column(Integer, ForeignKey('USER.uid', name='pertenece'), nullable=False, primary_key=True, index=True)
    gid = Column(Integer, ForeignKey('GROUP.gid', name='contiene'), nullable=False, primary_key=True, index=True)
    #rel_uid = relationship("USER", backref="_m_u2g", primaryjoin="_M_U2G.uid==USER.uid")
    #rel_gid = relationship("GROUPS", backref="_m_u2g",primaryjoin="_M_U2G.gid==GROUPS.gid")

    def __repr__(self):
        return "MAP U2G (%r:%r)" % (self.uid, self.gid)


class database():

    def create(self):
        #engine = create_engine('sqlite:///pepe.db', echo=True)
        #DeferredReflection.prepare(engine)
        #Base.metadata.bind=engine
        #Base.metadata.create_all(engine)
        print("init")
        Base.metadata.create_all(engine)
    
    def load(self):
        print("load")
        
        self.metadata = MetaData()
        self.metadata.reflect(bind=engine)
        for i in self.metadata.tables:
            print(i)
        #    meta.tables[i]
        
        #print(len(us))
        #pprint(us)#self.gro=meta.tables['GROUP']
        #self.relu2g=meta.tables['_M_U2G']
    
    def query(self, thisobject):
        self.metadata.query(thisobject)
    
    def p(self):
        print("print")
        
        print(len(self.user))
        

if __name__ == "__main__":
    Base.metadata.bind = engine
    Base.metadata.create_all()
    DBSession.configure(bind=engine)
    
    db = database()
    db.create()
    db.load()
    db.query(User)
    print(User.query())