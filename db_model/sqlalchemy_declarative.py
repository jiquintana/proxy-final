import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

engine = create_engine('sqlite:///proxy.db',echo=True)
Base = declarative_base()
Base.metadata.bind = engine


groups = Table(
    '_GROUPS', Base.metadata,
    Column('uid', Integer, ForeignKey('USER.uid'), nullable=False, primary_key=True, index=True),
    Column('gid', Integer, ForeignKey('GROUP.gid'), nullable=False, primary_key=True, index=True),

    #rel_uid = relationship("USER", backref="_map_user2group", primaryjoin="_M_U2G.uid==USER.uid")
    #rel_gid = relationship("GROUPS", backref="_map_user2group",primaryjoin="_M_U2G.gid==GROUPS.gid")
)

class User(Base):
    __tablename__ = 'USER'
    #__table_args__ = ({'autoload':True},)
    uid = Column(Integer, primary_key=True, autoincrement=True, unique=True, index=True)
    username = Column(String(20), nullable=False, unique=True, index=True)
    password= Column(String(16), nullable=False)
    description = Column(String(80), nullable=False)
    #pertenece=relationship("pertenece", secondary = groups, backref = __tablename__)

    def __repr__(self):
        return "User(%r,%r,%r,%r)" % (self.uid,self.username,self.password,self.description)


class Group(Base):
    #__table_args__ = ({'autoload': True},)
    __tablename__ = 'GROUP'
    #__table_args__ = ({'autoload':True},)
    gid = Column(Integer, primary_key=True, autoincrement=True, unique=True, index=True)
    groupname = Column(String(20), nullable=False)
    description = Column(String(80), nullable=False)    
    #componentes = relationship('componentes', secondary = groups, backref = __tablename__)

    def __repr__(self):
        return "Group(%r,%r,%r,%r)" % (self.gid, self.groupname, self.groupname, self.description)
   

# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
#engine = create_engine('sqlite:///proxy.db')
 
# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)