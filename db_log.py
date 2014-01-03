#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:sts=4:ai:et:fileencoding=utf-8:number
import sys
if sys.version_info < (3, 0):
    python_OldVersion = True
else:
    python_OldVersion = False

from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Table, or_, CHAR, Enum,  create_engine, MetaData, event, Index, desc, TIMESTAMP
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base,  DeclarativeMeta
from sqlalchemy.pool import NullPool, StaticPool, SingletonThreadPool
import datetime
if python_OldVersion:
    import string
else:
    import binascii

from Config import Config

DRIVER = Config.dbFiles['log']
TraceSQL = Config.dbTrace['log']

engine = create_engine(DRIVER,
    connect_args={'check_same_thread':False},
    echo=TraceSQL,
    poolclass=NullPool)
    #poolclass=StaticPool)
    #poolclass=SingletonThreadPool)

@event.listens_for(engine, "connect")
def _fk_pragma_on_connect(dbapi_con, con_record):
    dbapi_con.execute('PRAGMA journal_mode=MEMORY')


Base = declarative_base()
#Base.metadata.bind = engine

class Database:
    __initialized__ = False
    __engine__ = None
    __DBSession__ = None
    __BASE__ = None
    session = None
    def __init__(self):
        if not self.__initialized__:
            #print("not initialized")
            #self.__initialized__ = True
            self.__engine__ = engine
            self.__metadata__ = MetaData()
            self.__BASE__=Base
            self.__BASE__.metadata.bind=self.__engine__
            self.__BASE__.metadata.create_all(self.__engine__)
            #self.__DBSession__ =sessionmaker()
            self.__DBSession__ = scoped_session(sessionmaker(autoflush=True))
            #scoped_session(sessionmaker())
            self.__DBSession__.configure(bind=self.__engine__)
            self.session = self.__DBSession__()


    def getLastLines(self, numLines):
        session = self.__DBSession__()
        theLines = session.\
            query(Lines).\
            order_by(desc(Lines.lineid)).\
            limit(numLines).\
            all()

        return theLines

    def addLine(self, data):
        session = self.__DBSession__()
        newLine = Lines()
        newLine.line = str(data).rstrip('\n')
        session.add(newLine)
        session.merge(newLine)
        session.commit()
        return None


class Lines(Base):
    __tablename__ = 'LINES'
    lineid = Column(Integer, primary_key=True, autoincrement=True, index=True)
    timestamp = Column(TIMESTAMP(timezone=True), primary_key=False, nullable=False, default=datetime.datetime.now())
    line = Column(String(400), nullable=False)
    __table_args__ = (
        Index('idx_lineid_asc', lineid.asc()),
        Index('idx_lineid_desc', lineid.desc()),
        )



    def stringColumns(self):
        return ['line', 'timestamp']

    def intColumns(self):
        return ['lineid' ]

    def fromdict(self, jsondata):
        self.lineid = dict_data.get('lineid', 0)
        self.timestamp = dict_data.get('timestamp', '')
        self.line = dict_data.line('line', '')
        return self

    def fromjson(self, jsondata):
        dict_data = json.loads(jsondata)
        self.lineid = dict_data.get('lineid', 0)
        self.timestamp = dict_data.get('timestamp', '')
        self.line = dict_data.line('line', '')
        return self

    def __repr__(self):
        return '{\n\t"lineid": %r,\n\t"timestamp": "%s",\n\t"line": "%s"\n}' % (self.lineid, self.timestamp, self.line)

    def __toString__(self):
        return "Lines(%r,%r,%r)" % (self.lineid, self.timestamp, self.line)




if __name__ == "__main__":



    db=Database()
    print(db.getLastLines(5))
    '''
    db.insertURISbyGID(1, "\na\nb\nc\n\nd\n\n\n\n\nabcdfef\n ieie, \n")

    db.insertURISbyGID(8, "\na\nb\nc\n\nd\n\n\n\n\nabcdfef\n ieie, \n")

    db.insertMIMESbyGID(1, "application/x-shockwave-flash\napplication/atom+xml")
    '''
    '''
    a = db.findURISbyGID(1)
    print(a)
    b = db.findWORDSbyGID(1)
    print(b)
    '''
    #db.addRelation( 1, 1026)

    #print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>")


    '''
    theUser = db.findUserByUID(1)

    print( theUser )
    #print(db.findUserByUsername('pepe1'))
    mytestGroup=Group(groupname='josi', description='Josi User ')
    storedGRP=db.addGroup(mytestGroup)

    theMembership= db.findGroupsByUser("aaaaa")
    print(theMembership)

    print("-----")

    theNotMembership = db.findNotGroupsByUser("aaaaa")
    print(theNotMembership)
    '''
    '''
        ed_user = User(username='ed', password='Ed Jones', description='ed')
        #db.session.add(ed_user)
        #db.session.commit()1


        try:
            db.session.add(ed_user)
            db.session.commit()
        except:
            db.session.rollback()

        storedUser=db.findUserByUsername('ed')
        print("...1")
        print(db.setUserAdmin(storedUser))
        print("...2")
        #print(db.unsetUserAdmin(storedUser))
        storedUser=db.findUserByUsername('ed')
        #storedUser.password='patata'
        print("...3")
        print(db.changeUserPassword(storedUser))
        print("...4")
        print("...1")
        print(db.setUserGuest(storedUser))
        #print(db.setUserGuest(storedUser))

        storedUser.description='cambio de descripcion4'
        storedUser.L_AH = HOURS_MASK['H09_M'] | HOURS_MASK['H07_M'] | HOURS_MASK['H08_M']
        storedUser.X_AH = __bitwise_not_hours(HOURS_MASK['NIG_M']) | HOURS_MASK['H04_M']
        storedUser.J_AH = HOURS_MASK['NON_M'] | HOURS_MASK['H23_M'] | HOURS_MASK['H01_M'] | HOURS_MASK['H00_M']
        storedUser.D_AH = HOURS_MASK['NON_M'] | HOURS_MASK['H10_M'] | HOURS_MASK['H01_M'] | HOURS_MASK['H00_M']

        #| HOURS_MASK['H08_M']
        print("...5")

        print(db.changeUserDescription(storedUser))
        print("...6")

        newGroup = Group(groupname='nuevo_grupo', description='nuevo grupo de prueba')
        print(db.addGroup(newGroup))
        newGroup.description='otra descripcion'
        print(db.changeGroupDescription(newGroup))

        print(db.isUserAllowedNow('ed'))
        print(db.setUserAdmin(storedUser))
        print(db.setUserAdvanced(storedUser))
        print(db.setUserKid(storedUser))
        print(db.setUserGuest(storedUser))
        print(db.isUserAdmin('ed'))
        print(db.isUserAdvanced('ed'))
        print(db.isUserKid('ed'))
        print(db.isUserGuest('ed'))
        storedUser.S_AH = HOURS_MASK['NON_M'] | HOURS_MASK['H02_M'] | HOURS_MASK['H01_M'] | HOURS_MASK['H00_M']
        db.commitDBChanges()
    '''
    '''
    mytestGroup=Group(groupname='josi', description='Josi User ')
    storedGRP=db.addGroup(mytestGroup)
    print(mytestGroup)
    print(storedGRP)
    '''
    '''
    for idx in range(4096): # esto va desde 0..MAXUSERS, debiendo fallar en el numero MAXUSERS
        mytestUsr=User(username='josi'+str(idx), password='password', description='Josi User '+str(idx))
        result=db.addUser(mytestUsr)
        print(result)

        if result != None:
            print("success idx "+str(idx))                print("aborted")

            print(mytestUsr)
            print(result)
    '''
    '''
    for instance in db.findUser("ep"):
        print("....%r" % inUSERstance)

    for instance in db.findGroup("%e"):
        print("....%r" % instance)
    print("----")
    for instance in db.getAllUser():
        print("....%r" % instance)
    print("----")        USER
    for instance in db.getAllGroups():
        print("....%r" % instance)
    print("----")
    '''

    '''
        for instance in db.findUser(u"ñ"):
        print("....%r" % instance)

    for instance in db.findGroup("b"):
        print("....%r" % instance)

    print("-----")
    print(db.findUserByUID(1))
    print(db.findUserByUsername('ed'))
    print("-----")
    print(db.findGroupByGID(8))
    print("-----")
    print(db.findGroupByGroupname('e'))
    print(db.getLowestUnusedUIDfromUsers())
    otherUser = User(username='josi3', password='password', description='Josi User')
    result=db.addUser(otherUser)
    '''

    '''
    db2=Database()
    print (User.__table__)

    print(db)
    print(db2)

    print(db.session.query(User).count())
    for instance in db.session.query(User):
        print(instance)



    ed_user = User(username='ed', password='Ed Jones', description='edspassword')
    ed_group = Group(groupname='ed', description='ed group')

    try:
        db.session.add(ed_user)
        db.session.commit()
    except:
        db.session.rollback()

    try:
        db.session.add(ed_group)
        db.session.commit()
    except:
        db.session.rollback()
    print('.---------------------')
    find_user = db.session.query(User).filter(User.username==ed_user.username).first()
    print (find_user)
    find_group = db.session.query(Group).filter(Group.groupname==ed_group.groupname).first()
    #filter(Address.person == person).all()
    print('.---------------------')
    print(find_user)
    print(find_group)
    membership=Groups(find_user,find_group)
    print('X---------------------')
    print(membership)
    print('X---------------------')

    try:
        db.session.add(membership)
        db.session.commit()
    except:
        db.session.rollback()

    #for instance in db.session.query(User).order_by(User.uid):
    #    print("%r %r" % (instance.name, instance.fullname))



    print(db.session.query(User).order_by(User.uid))

    for instance in db2.session.query(User).join(Groups, User.uid==Groups.uid):
    #for instance in db2.session.query(User).all():
        print(instance)

    for instance in db.session.query(Groups).join(User).outerjoin(Group).add_entity(User).add_entity(Group):
        print(instance)
    #(Groups(1,1), User(1,'ed','Ed Jones','edspassword'), Group(1,'ed','ed','ed group'))
    #(Groups(1,3), INSERT INTO "GROUP" VALUES(33,'e','e');User(1,'ed','Ed Jones','edspassword'), Group(3,'b','b','b'))

    '''
