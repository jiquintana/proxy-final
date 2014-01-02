#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:sts=4:ai:et:fileencoding=utf-8:number
import sys
if sys.version_info < (3, 0):
    python_OldVersion = True
else:
    python_OldVersion = False

from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Table, or_, CHAR, Enum,  create_engine, MetaData, event
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base,  DeclarativeMeta
from sqlalchemy.pool import NullPool
import datetime

if python_OldVersion:
    import string
else:
    import binascii

from Config import Config
MAXUSERS = 1024
MAXGROUPS = 65536

DRIVER = Config.dbFiles['proxy']
TraceSQL = Config.dbTrace['proxy']

engine = create_engine(DRIVER, echo=TraceSQL,poolclass=NullPool)

Base = declarative_base()


HOURS_IDX = {
     0: 'H00_M',  1: 'H01_M',  2: 'H02_M',  3: 'H03_M',
     4: 'H04_M',  5: 'H05_M',  6: 'H06_M',  7: 'H07_M',
     8: 'H08_M',  9: 'H09_M', 10: 'H10_M', 11: 'H11_M',
    12: 'H12_M', 13: 'H13_M', 14: 'H14_M', 15: 'H15_M',
    16: 'H16_M', 17: 'H17_M', 18: 'H18_M', 19: 'H19_M',
    20: 'H20_M', 21: 'H21_M', 22: 'H22_M', 23: 'H23_M'
}

HOURS_MASK = {
    #              2         1         0
    #           321098765432109876543210
    'NON_M' : 0b000000000000000000000000,  # NONE ASIGNED
    'H00_M' : 0b000000000000000000000001,  # 00.xxh mask
    'H01_M' : 0b000000000000000000000010,  # 01.xxh mask
    'H02_M' : 0b000000000000000000000100,  # 02.xxh mask
    'H03_M' : 0b000000000000000000001000,  # 03.xxh mask
    'H04_M' : 0b000000000000000000010000,  # 04.xxh mask
    'H05_M' : 0b000000000000000000100000,  # 05.xxh mask
    'H06_M' : 0b000000000000000001000000,  # 06.xxh mask
    'H07_M' : 0b000000000000000010000000,  # 07.xxh mask
    'H08_M' : 0b000000000000000100000000,  # 08.xxh mask
    'H09_M' : 0b000000000000001000000000,  # 09.xxh mask
    'H10_M' : 0b000000000000010000000000,  # 10.xxh mask
    'H11_M' : 0b000000000000100000000000,  # 11.xxh mask
    'H12_M' : 0b000000000001000000000000,  # 12.xxh mask
    'H13_M' : 0b000000000010000000000000,  # 13.xxh mask
    'H14_M' : 0b000000000100000000000000,  # 14.xxh mask
    'H15_M' : 0b000000001000000000000000,  # 15.xxh mask
    'H16_M' : 0b000000010000000000000000,  # 16.xxh mask
    'H17_M' : 0b000000100000000000000000,  # 17.xxh mask
    'H18_M' : 0b000001000000000000000000,  # 18.xxh mask
    'H19_M' : 0b000010000000000000000000,  # 19.xxh mask
    'H20_M' : 0b000100000000000000000000,  # 20.xxh mask
    'H21_M' : 0b001000000000000000000000,  # 21.xxh mask
    'H22_M' : 0b010000000000000000000000,  # 22.xxh mask
    'H23_M' : 0b100000000000000000000000,  # 23.xxh mask
    'NIG_M' : 0b111000000000000011111111,  # 00.xxh - 07.xxh && 21.xxh-23.xxh mask
    'DAY_M' : 0b000111111111111100000000,  # 08.xxh - 20.xxh mask
    'ALL_M' : 0b111111111111111111111111   # ALL hours mask

}


import json
#import simplejson as json

class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data) # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            # a json-encodable dict
            return fields
        return json.JSONEncoder.default(self, obj)


def __bitwise_not_hours(hours):
    return hours ^ 0xFFFFFF
'''
@event.listens_for(engine, "connect")
def _fk_pragma_on_connect(dbapi_con, con_record):
    dbapi_con.execute('PRAGMA journal_mode=MEMORY')
'''
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

    def findUser(self, str2find):
        #self.session =
        session = self.__DBSession__()
        '''
        users_found = session.\
            query(User).\
            filter( \
                or_( User.username==str2find, User.description==str2find )
                ).\
            all()
        '''
        #if users_found == []:
        users_found = session.\
            query(User).\
            filter( \
                or_( User.username.ilike("%"+str2find+"%"), User.description.ilike("%"+str2find+"%"))
            ).\
            all()

        return users_found

    def findUserByUsername(self, username):
        session = self.__DBSession__()

        users_found = session.\
            query(User).\
            filter(User.username==username).\
            first()

        return users_found

    def isUserAllowed(self, username, password):
        session = self.__DBSession__()

        result = False
        theUser = self.findUserByUsername(username)
        if theUser != None:
            if theUser.password == password:
                result = True
        return result

    def isAdminAllowed(self, username, password):
        session = self.__DBSession__()

        result = False
        theUser = self.findUserByUsername(username)

        if theUser != None:
            if theUser.password == password and self.isUserAdmin(username):
                result = True
        return result


    def findUserByUID(self, uid):
        session = self.__DBSession__()

        users_found = session.\
            query(User).\
            filter(User.uid==uid).\
            first()

        return users_found

    def getAllUser(self):
        session = self.__DBSession__()

        users_found = session.\
            query(User).\
            all()
        return users_found

    def getLowestUnusedUIDfromUser(self):
        session = self.__DBSession__()

        theUID=None
        uids_found = [r for (r, ) in session.query(User.uid).all()]
        for testUID in range(1,MAXUSERS+1):
            if (theUID == None) and  not (testUID in uids_found):
                theUID = testUID
        return theUID

    def addUser(self,newUser):
        session = self.__DBSession__()

        theUID = None
        theGID = -1
        transaction_succesful=False


        # Obtenemos el UID libre mas bajo; el uid no supera el máximo de MAXUSERS usrs
        theUID = self.getLowestUnusedUIDfromUser()

        # Comprobamos que el grupo no exista, y si esta libre, creamos el UID y GID con el mismo valor:
        # Correspondencia 1:1 entre usuario y grupo cuando el UID<MAXUSERS
        if (theUID != None) and (self.findGroupByGID(theUID) == None):
            theGID = theUID

        testUSR = self.findUserByUsername(newUser.username)
        testGRP = self.findGroupByGroupname('dfl_grp_'+newUser.username)

        # Comprobamos si ya existe un usuario o grupo con igual clave primaria
        if (testUSR != None) or (testGRP != None):
            # Existe: forzamos NO ejecucion...
            theGID = -1

        # Si hemos encontrado un usuario libre y el grupo libre...
        # y ademas no existen las claves primarias de usuario.username y grupo.groupname...
        #  => (todo OK hasta el momento...)
        # en la inicializacion hemos forzado valores diferentes para evitar que esta comparacion sea
        # cierta por defecto
        if theUID == theGID:
            # Todos los valores recibidos en newUser, salvo el UID, son validos. Ahora alocamos el UID
            newUser.uid = theUID
            newGroup = Group()
            newGroup.gid=theGID
            newGroup.description='Grupo de '+newUser.description
            newGroup.groupname='dfl_grp_'+newUser.username

            relacionUsrGrp = Groups(newUser, newGroup)

            # Tenemos todo preparado... intentamos ejecutar la transaccion
            try:
                #session.begin_nested()
                session.add(newUser)
                session.add(newGroup)
                session.add(relacionUsrGrp)
                session.merge(newUser)
                session.merge(newGroup)
                session.merge(relacionUsrGrp)
                session.commit()
                transaction_succesful=True
            except e:
                print(e)
                session.rollback()
        # Si todo ha ido bien (creacion del usuario, creacion del grupo y creacion de acl), devolvemos
        # un registro con el usuario creado
        # si ha ido mal, devolvemos None
        if transaction_succesful:
            storedUser = self.findUserByUID(theUID)
        else:
            storedUser = None

        return storedUser

    def addRelation(self, uid, gid):
        session = self.__DBSession__()

        theUSR = self.findUserByUID(uid)
        theGRP = self.findGroupByGID(gid)

        relacionUsrGrp = Groups(theUSR, theGRP)
        session.add(relacionUsrGrp)
        session.commit()

    def wr_addRelation(self, theDict):
        session = self.__DBSession__()

        uid = theDict.get('uid')
        gid = theDict.get('gid')
        #print(">>>> db.wr_addRelation:: %r, %r" % (uid, gid))
        return self.addRelation(uid, gid)
        #return None

    def delRelation(self, uid, gid):
        session = self.__DBSession__()

        theGroups = session.\
            query(Groups).\
            filter(Groups.uid==uid).\
            filter(Groups.gid==gid).\
            delete()
        session.commit()


    def wr_delRelation(self, theDict):
        session = self.__DBSession__()

        uid = theDict.get('uid')
        gid = theDict.get('gid')
        #print(">>>> db.wr_delRelation:: %r, %r" % (uid, gid))
        return self.delRelation(uid, gid)
        #return None

    def delUser(self,usertoDelete):
        session = self.__DBSession__()


        theGroups = session.\
            query(Groups).\
            filter(Groups.uid==usertoDelete.uid).\
            delete()

        theGroup = session.\
            query(Group).\
            filter(Group.gid==usertoDelete.uid).\
            delete()

        theUser = session.\
             query(User).\
             filter(User.uid==usertoDelete.uid).\
             delete()

        session.commit()

        return None


    def setUserAdmin(self,requestedUser):
        session = self.__DBSession__()

        if requestedUser != None:
            storedUser=self.findUserByUsername(requestedUser.username)
            rol = RolType()
            if storedUser != None:
                theUser = session.query(User).\
                    filter(User.uid==storedUser.uid).\
                    update({'rol': rol.get_adm_user_key()})

                session.commit()
            return self.findUserByUsername(requestedUser.username)
        else:
            return None

    def changeUser(self,requestedUser):
        session = self.__DBSession__()

        if requestedUser != None:
            storedUser=self.findUserByUID(requestedUser.uid)
            if storedUser != None:

                storedUser.username = requestedUser.username
                storedUser.rol = requestedUser.rol
                storedUser.password = requestedUser.password
                storedUser.description = requestedUser.description

                storedUser.L_AH = requestedUser.L_AH
                storedUser.M_AH = requestedUser.M_AH
                storedUser.X_AH = requestedUser.X_AH
                storedUser.J_AH = requestedUser.J_AH
                storedUser.V_AH = requestedUser.V_AH
                storedUser.S_AH = requestedUser.S_AH
                storedUser.D_AH = requestedUser.D_AH
                session.merge(storedUser)
                session.commit()

            return self.findUserByUsername(requestedUser.username)
        else:
            return None

    def setUserAdvanced(self,requestedUser):
        session = self.__DBSession__()

        if requestedUser != None:
            storedUser=self.findUserByUsername(requestedUser.username)
            rol = RolType()
            if storedUser != None:
                theUser = session.query(User).\
                    filter(User.uid==storedUser.uid).\
                    update({'rol': rol.get_adv_user_key()})

                session.commit()
            return self.findUserByUsername(requestedUser.username)
        else:
            return None

    def setUserKid(self,requestedUser):
            session = self.__DBSession__()

            if requestedUser != None:
                storedUser=self.findUserByUsername(requestedUser.username)
                rol = RolType()
                if storedUser != None:
                    theUser = session.query(User).\
                        filter(User.uid==storedUser.uid).\
                        update({'rol': rol.get_kid_user_key()})

                    session.commit()
                return self.findUserByUsername(requestedUser.username)
            else:
                return None

    def setUserGuest(self,requestedUser):
            session = self.__DBSession__()

            if requestedUser != None:
                storedUser=self.findUserByUsername(requestedUser.username)
                RolType = rol
                if storedUser != None:
                    theUser = session.query(User).\
                        filter(User.uid==storedUser.uid).\
                        update({'rol': rol.get_guest_user_key()})

                    session.commit()
                return self.findUserByUsername(requestedUser.username)
            else:
                return None

    def changeUserPassword(self,requestedUser):
        session = self.__DBSession__()

        if requestedUser != None:
            storedUser=self.findUserByUsername(requestedUser.username)
            if storedUser != None:
                theUser = session.\
                    query(User).\
                    filter(User.uid==storedUser.uid).\
                    update({'password': requestedUser.password})
                session.commit()
            return self.findUserByUsername(requestedUser.username)
        else:
            return None

    def changeUserDescription(self,requestedUser):
        session = self.__DBSession__()

        if requestedUser != None:
            storedUser=self.findUserByUsername(requestedUser.username)
            if storedUser != None:
                theUser = session.\
                    query(User).\
                    filter(User.uid==storedUser.uid).\
                    update({'description': requestedUser.description})
                session.commit()
            return self.findUserByUsername(requestedUser.username)
        else:
            return None

    def commitDBChanges(self):
        session = self.__DBSession__()

        #print('commit DB changes')
        if session.dirty or session.deleted:
            #print("pending changes saving")
            session.commit()


    def findGroup(self, str2find):
        session = self.__DBSession__()

        groups_found = session.\
            query(Group).\
            filter( \
                or_( Group.groupname==str2find, Group.description==str2find )
            ).\
            all()
        if groups_found == []:
            groups_found = session.\
                query(Group).\
                filter(
                    or_( Group.groupname.ilike("%"+str2find+"%"),
                         Group.description.ilike("%"+str2find+"%")
                         )
                    ).\
                all()
        return groups_found

    def findGroupByGroupname(self, groupname):
        session = self.__DBSession__()

        groups_found = session.\
            query(Group).\
            filter(Group.groupname==groupname).\
            first()
        return groups_found

    def findGroupByGID(self, gid):
        session = self.__DBSession__()

        groups_found = session.\
            query(Group).\
            filter(Group.gid==gid).\
            first()
        return groups_found

    def delGroup(self,grouptoDelete):
        session = self.__DBSession__()


        theGroups = session.\
            query(Groups).\
            filter(Groups.gid==grouptoDelete.gid).\
            delete();

        theGroup = session.\
            query(Group).\
            filter(Group.gid==grouptoDelete.gid).\
            delete()

        session.commit()

        return None


    def changeGroup(self,requestedGroup):
        session = self.__DBSession__()

        #print(requestedGroup.__repr__())
        if requestedGroup != None:
            storedGroup=self.findGroupByGID(requestedGroup.gid)
            if storedGroup != None:

                storedGroup.groupname = requestedGroup.groupname
                storedGroup.description = requestedGroup.description
                session.commit()

            return self.findGroupByGroupname(requestedGroup.groupname)
        else:
            return None

    def getAllGroups(self):
        session = self.__DBSession__()

        groups_found = session.query(Group).all()
        return groups_found

    def getAllCustomGroups(self):
        session = self.__DBSession__()

        groups_found = session.\
            query(Group).\
            filter(Group.gid>MAXUSERS).\
            all()
        return groups_found

    def getLowestUnusedGIDfromGroup(self):
        session = self.__DBSession__()

        theGID=None
        gids_found = [r for (r, ) in session.query(Group.gid).all()]
        for testGID in range(MAXUSERS+1,MAXGROUPS+1):
            if (theGID == None) and  not (testGID in gids_found):
                theGID = testGID
        return theGID

    def addGroup(self,newGroup):
        session = self.__DBSession__()

        theGID = None
        transaction_succesful=False

        # Obtenemos el GID libre mas bajo...
        theGID = self.getLowestUnusedGIDfromGroup()
        # e intentamos localizar un grupo con el mismo nombre
        testGRP = self.findGroupByGroupname(newGroup.groupname)

        # si el GID esta libre y no hemos encontrado un grupo con la misma clave primaria..
        if theGID != None and testGRP == None:
            # Todos los valores recibidos en newUser, salvo el UID, son validos. Ahora alocamos el UID
            newGroup.gid = theGID
            try:
                session.add(newGroup)
                session.commit()
                transaction_succesful=True
            except:
                session.rollback()

        # Si todo ha ido bien (creacion del grupo), devolvemos
        # un registro con el grupo creado, M, X, J, V, S, D
        # si ha ido mal, devolvemos None
        if transaction_succesful:
            storedGroup = self.findGroupByGID(theGID)
        else:
            storedGroup = None
        return storedGroup

    def changeGroupDescription(self,requestedGroup):
        session = self.__DBSession__()

        if requestedGroup != None:
            storedGroup=self.findGroupByGroupname(requestedGroup.groupname)
            if storedGroup != None:
                theGroup = session.query(Group).filter(
                    Group.gid==storedGroup.gid
                    ).update({'description': requestedGroup.description})
                session.commit()
            return self.findGroupByGroupname(requestedGroup.groupname)
        else:
            return None

    def isUserAllowedNow(self, username):
        session = self.__DBSession__()

        is_authorized=False
        storedUser=self.findUserByUsername(username)
        if storedUser != None:
            now=datetime.datetime.now()
            h=now.time().hour
            dow=now.weekday()
            # calculamos la mascara de hora haciendo shift a la izquierda de h bits basado en 0b000000000000000000000001
            # ej:
            #                                                   2         1         0
            #                                                321098765432109876543210
            #    00h =>  0b000000000000000000000001 <  0 = 0b000000000000000000000001
            #    22h =>  0b000000000000000000000001 < 22 = 0b010000000000000000000000
            hour_mask = HOURS_MASK['H00_M']<< h
            ## print('hour_mask:                 {0:24b}'.format(hour_mask))
            if dow == 0:    # Lunes
                ##print("L %rh" % h )
                hours_bit_mask =  storedUser.L_AH
            elif dow == 1:  # Martes
                ##print("M %rh" % h )
                hours_bit_mask =  storedUser.M_AH
            elif dow == 2:  # Miercoles
                ##print("X %rh" % h )
                hours_bit_mask =  storedUser.X_AH
            elif dow == 3:  # Jueves
                ##print("J %rh" % h )
                hours_bit_mask =  storedUser.J_AH
            elif dow == 4:  # Viernes
                ##print("V %rh" % h )
                hours_bit_mask =  storedUser.V_AH
            elif dow == 5:  # Sabado
                ##print("S %rh" % h )
                hours_bit_mask =  storedUser.S_AH
            elif dow == 6:  # Domingo
                ##print("D %rh" % h )
                hours_bit_mask =  storedUser.D_AH
            else:   # Si llegamos aqui, tenemos un problema
                ##print("Unknownday")
                hours_bit_mask = 0

            ##print('hours_bit_mask:            {0:24b}'.format(hours_bit_mask))
            # Una vez obtenido el registro del dia, enmascaramos con la hora activa
            resulting_hours_bit_mask = hours_bit_mask & hour_mask
            ##print('resulting_hours_bit_mask:  {0:24b}'.format(resulting_hours_bit_mask))
            if resulting_hours_bit_mask != 0:
                is_authorized = True
        return is_authorized

    def isUserAdmin(self, username):
        session = self.__DBSession__()

        is_admin=False
        storedUser= self.findUserByUsername(username)
        rol = RolType()
        if storedUser != None:
            if storedUser.rol == rol.get_adm_user_key():
                is_admin = True
        return is_admin

    def isUserAdvanced(self, username):
        session = self.__DBSession__()

        is_advanced=False
        storedUser=self.findUserByUsername(username)
        if storedUser != None:
            rol = RolType()
            if storedUser.rol == rol.get_adv_user_key():
                is_advanced = True
        return is_advanced

    def isUserKid(self, username):
        session = self.__DBSession__()

        is_kid=False
        storedUser=self.findUserByUsername(username)
        if storedUser != None:
            rol = RolType()
            if storedUser.rol == rol.get_kid_user_key():
                is_kid = True
        return is_kid

    def isUserGuest(self, username):
        session = self.__DBSession__()

        is_guest=False
        storedUser= self.findUserByUsername(username)
        if storedUser != None:
            rol = RolType()
            if storedUser.rol == rol.get_guest_user_key():
                is_guest = True
        return is_guest

    def findGroupsByUser(self, username):
        session = self.__DBSession__()

        membership = []
        if username != '%':

            theUser = self.findUserByUsername(username)
            if theUser != None:
                membergroups = session.\
                    query(Groups).\
                    join(User).\
                    join(Group).\
                    filter(Groups.gid>MAXUSERS).\
                    filter(Groups.uid==User.uid).\
                    filter(Groups.gid==Group.gid).\
                    filter(User.uid==theUser.uid).\
                    all()

                for member in membergroups:
                    theGroup = self.findGroupByGID(member.gid)
                    membership.append(theGroup)
        return membership

    def findNotGroupsByUser(self, username):
        session = self.__DBSession__()

        notMembership = []
        membership = []
        all_groups = []
        if username != '%':
            theUser = self.findUserByUsername(username)
            if theUser != None:
                all_groups = self.getAllCustomGroups()

                if theUser != None:
                    membership =  self.findGroupsByUser(theUser.username)

                for member in membership:
                    the_member_group = self.findGroupByGID(member.gid)
                    all_groups.remove(the_member_group)

        return all_groups

    def findURISbyGID(self, gid):
        session = self.__DBSession__()

        theUris = session.\
            query(URIS).\
            filter(URIS.gid==gid).\
            all()
        return theUris

    def deleteURISbyGID(self, gid):
        session = self.__DBSession__()

        #print ('------------')
        theUris = session.\
            query(URIS).\
            filter(URIS.gid==gid).\
            delete()
        session.commit()
        #print ('------------')
        return None

    def insertURISbyGID(self, gid, data):
        session = self.__DBSession__()

        numLine = 0
        self.deleteURISbyGID(gid)
        for line in data.split('\n'):
            if line != "":
                numLine += 1
                newUri = URIS()
                newUri.uriid = numLine
                newUri.gid = gid
                newUri.uri = line
                #print('uri: %r' % newUri)
                session.add(newUri)
        session.merge(newUri)
        session.commit()

        return self.findURISbyGID(gid)

    def wr_insertURISbyGID(self, theDict):
        session = self.__DBSession__()

        gid = theDict.get('gid')
        data = theDict.get('data')
        #print(">>>> db.wr_insertURISbyGID:: %r, %r" % (gid, data))
        return self.insertURISbyGID(gid, data)
        #return None


    def findWORDSbyGID(self, gid):
        session = self.__DBSession__()

        theWords = session.\
            query(WORDS).\
            filter(WORDS.gid==gid).\
            all()
        return theWords

    def deleteWORDSbyGID(self, gid):
        session = self.__DBSession__()

        theWords = session.\
            query(WORDS).\
            filter(WORDS.gid==gid).\
            delete()
        return None

    def insertWORDSbyGID(self, gid, data):
        session = self.__DBSession__()

        numLine = 0
        self.deleteWORDSbyGID(gid)
        for line in data.split('\n'):
            if line != "":
                numLine += 1
                newWords = WORDS()
                newWords.wordsid = numLine
                newWords.gid = gid
                newWords.words= line
                #print('words: %r' % newWords)
                session.add(newWords)
        session.commit()

        return self.findWORDSbyGID(gid)

    def wr_insertWORDSbyGID(self, theDict):
        session = self.__DBSession__()

        gid = theDict.get('gid')
        data = theDict.get('data')
        #print(">>>> db.wr_insertWORDSbyGID:: %r, %r" % (gid, data))
        return self.insertWORDSbyGID(gid, data)
        #return None

    def findMIMESbyGID(self, gid):
        session = self.__DBSession__()

        theMimes = session.\
            query(MIMES).\
            filter(MIMES.gid==gid).\
            all()
        return theMimes

    def deleteMIMESbyGID(self, gid):
        session = self.__DBSession__()

        theMimes = session.\
            query(MIMES).\
            filter(MIMES.gid==gid).\
            delete()
        return None

    def insertMIMESbyGID(self, gid, data):
        session = self.__DBSession__()

        numLine = 0
        self.deleteMIMESbyGID(gid)
        for line in data.split('\n'):
            if line != "":
                numLine += 1
                newMimes = MIMES()
                newMimes.mimeid = numLine
                newMimes.gid = gid
                newMimes.mimes= line
                #print('mimes: %r' % newMimes)
                session.add(newMimes)
        session.commit()

        return self.findMIMESbyGID(gid)

    def wr_insertMIMESbyGID(self, theDict):
        session = self.__DBSession__()

        gid = theDict.get('gid')
        data = theDict.get('data')
        #print(">>>> db.wr_insertMIMESbyGID:: %r, %r" % (gid, data))
        return self.insertMIMESbyGID(gid, data)
        #return None


    def getRULES(self, kind, username):
        session = self.__DBSession__()
        if kind == 'MIME':
            table = MIMES
            tableid = MIMES.mimeid
            datacol = MIMES.mimes
        elif kind == 'URIS':
            table = URIS
            tableid = URIS.uriid
            datacol = URIS.uri
        elif kind == 'WORD':
            table = WORDS
            tableid = WORDS.wordsid
            datacol = WORDS.words

        theRules = session.\
            query(Groups).\
            join(User).\
            join(Group).\
            join(table).\
            add_entity(User).\
            add_entity(Group).\
            add_entity(table).\
            filter(Groups.uid==User.uid).\
            filter(Groups.gid==Group.gid).\
            filter(Groups.gid==table.gid).\
            filter(User.username==username).\
            all()

        theanswer = []

        for rule in theRules:
            theRule = Rule()

            theRule.fromData(rule)
            theanswer.append(theRule)
        return(theanswer)



class Rule(object):
    tableid = ''
    ruleid = 0
    uid = 0
    gid = 0
    username = ''
    groupname = ''
    rulecontent = ''

    def fromData(self, data):
        [groups, user, group, ruleset] = data
        self.uid = user.uid
        self.gid = group.gid
        self.username = user.username
        self.groupname = group.groupname
        if (type(ruleset)) == URIS:
            self.tableid = 'URIS'
            self.ruleid = ruleset.uriid
            self.rulecontent = ruleset.uri
        elif (type(ruleset)) == WORDS:
            self.tableid = 'WORD'
            self.ruleid = ruleset.wordsid
            self.rulecontent = ruleset.words
            WORDS.words
        elif (type(ruleset)) == MIMES:
            self.tableid = 'MIME'
            self.ruleid = ruleset.mimeid
            self.rulecontent = ruleset.mimes

    def __repr__(self):
        return '{\n\t"tableid": "%s",\n\t"ruleid": %r,\n\t"uid": %r,\n\t"gid": %r,\n\t"username": "%s",\n\t"groupname": "%s",\n\t"rulecontent": "%s"\n}' \
               % (self.tableid, self.ruleid, self.uid, self.gid, self.username, self.groupname, self.rulecontent)
    def __toString__(self):
        return "Rule(%r,%r,%r,%r,%r,%r,%r)" % (self.tableid, self.ruleid, self.uid, self.gid, self.username, self.groupname, self.rulecontent)



class Groups(Base):
    __tablename__ = 'GRUPOS'
    uid=Column(Integer, ForeignKey('USUARIO.uid'), nullable=False, primary_key=True, index=True)
    gid=Column(Integer, ForeignKey('GRUPO.gid'), nullable=False, primary_key=True, index=True)
    #_usuario = relationship("User", backref="GRUPOS")
    #_grupo = relationship("Group", backref="GRUPOS")


    def __init__(self, user, group):
        self.uid=user.uid
        self.gid=group.gid

    def fromjson(self, jsondata):
        dict_data = json.loads(jsondata)
        self.uid = dict_data.get('uid', 0)
        self.gid = dict_data.get('gid', 0)
        return self

    def __repr__(self):
        return "{'uid': %r,\n\t'gid': %r}\n" % (self.uid, self.gid)

    def __toSring__(self):
        return "Groups(%r,%r)" % (self.uid,self.gid)

    def JSONdump(self):
        return json.dumps(self, cls=AlchemyEncoder)

    def __eq__(self, other):
        #print(". %r" % self.__repr__())
        #print(". %r" % other.__repr__())
        return self.__dict__ == other.__dict__

    def pertenece(self, user):
        if user.uid == self.uid:
            return True
        else:
            return False

    def contiene(self, group):
        if group.gid == self.gid:
            return True
        else:
            return False


roles = {'A' : 'Admin User', 'V' : 'Advanced User', 'K' : 'Kid User', 'G' : 'Guest User'}


class RolType(object):
    def getValue(key):
        return roles.get(key)
    def getKeys():
        return roles.keys()
    def getValues():
        return roles.values()
    def dbTypes():
        return getValues()
    def get_adm_user_key(self):
        return 'A'
    def get_adv_user_key(self):
        return 'V'
    def get_kid_user_key(self):
        return 'K'
    def get_guest_user_key(self):
        return 'G'
    def get_adm_user():
        return getValue('A')
    def get_adv_user():
        return getValue('V')
    def get_kid_user():
        return getValue('K')
    def get_guest_user():
        return getValue('G')

class User(Base):

    #'NON_M','HXX_M', 'NIG_M', 'DAY_M', 'ALL_M'

    __tablename__ = 'USUARIO'
    uid = Column(Integer, primary_key=True, autoincrement=True, unique=True, index=True)
    username = Column(String(20), nullable=False, unique=True, index=True)
    rol = Column(Enum('A', 'V', 'K', 'G'), default = 'G')
    password= Column(String(16), nullable=False)
    description = Column(String(80), nullable=False)
    L_AH = Column(Integer, default=HOURS_MASK['NON_M'])
    M_AH = Column(Integer, default=HOURS_MASK['NON_M'])
    X_AH = Column(Integer, default=HOURS_MASK['NON_M'])
    J_AH = Column(Integer, default=HOURS_MASK['NON_M'])
    V_AH = Column(Integer, default=HOURS_MASK['NON_M'])
    S_AH = Column(Integer, default=HOURS_MASK['NON_M'])
    D_AH = Column(Integer, default=HOURS_MASK['NON_M'])
    #_usuarios = relationship("Groups", backref="USUARIO")

    def stringColumns(self):
        return ['username', 'rol', 'password', 'description']

    def intColumns(self):
        return ['uid', 'L_AH', 'M_AH', 'X_AH', 'J_AH', 'V_AH', 'S_AH', 'D_AH' ]

    def fromdict(self, dict_data):
        #dict_data = json.loads(jsondata)
        self.uid = dict_data.get('uid', 0)
        self.username = dict_data.get('username','')
        self.rol = dict_data.get('rol', 'G')
        self.password = dict_data.get('password', '')
        self.description = dict_data.get('description', '')
        self.L_AH = dict_data.get('L_AH', 0)
        self.M_AH = dict_data.get('M_AH', 0)
        self.X_AH = dict_data.get('X_AH', 0)
        self.J_AH = dict_data.get('J_AH', 0)
        self.V_AH = dict_data.get('V_AH', 0)
        self.S_AH = dict_data.get('S_AH', 0)
        self.D_AH = dict_data.get('D_AH', 0)
        return self

    def __repr__(self):
        return ('{\n\t"uid": %r,\n\t"username": "%s",\n\t"rol": "%s",\n\t"password": "%s",\n\t"description": "%s",\n\t' %
                (self.uid,self.username,self.rol,self.password,self.description)+
                '"L_AH": %r,\n\t"M_AH": %r,\n\t"X_AH": %r,\n\t"J_AH": %r,\n\t"V_AH": %r,\n\t"S_AH": %r,\n\t"D_AH": %r\n}\n' %
                (self.L_AH, self.M_AH, self.X_AH, self.J_AH, self.V_AH, self.S_AH, self.D_AH))

    def toString(self):
        if python_OldVersion:
            return ('User(%r,%r,%r,%r,%r)' % (self.uid,self.username,self.rol,self.password,self.description) +
                   '\n\t    %s' % (' 0         1         2   ') +
                   '\n\t    %s' % (' 012345678901234567890123') +
                   '\n\t    %s' % (' ========================') +
                   '\n\tL:  %r' % ('  {0:24b}'.format(self.L_AH)[::-1]).translate(maketrans('01', ' o'))+
                   '\n\tM:  %r' % ('  {0:24b}'.format(self.M_AH)[::-1]).translate(maketrans('01', ' o'))+
                   '\n\tX:  %r' % ('  {0:24b}'.format(self.X_AH)[::-1]).translate(maketrans('01', ' o'))+
                   '\n\tJ:  %r' % ('  {0:24b}'.format(self.J_AH)[::-1]).translate(maketrans('01', ' o'))+
                   '\n\tV:  %r' % ('  {0:24b}'.format(self.V_AH)[::-1]).translate(maketrans('01', ' o'))+
                   '\n\tS:  %r' % ('  {0:24b}'.format(self.S_AH)[::-1]).translate(maketrans('01', ' o'))+
                   '\n\tD:  %r' % ('  {0:24b}'.format(self.D_AH)[::-1]).translate(maketrans('01', ' o'))+
                   '\n')
        else:
            return ('User(%r,%r,%r,%r,%r)' % (self.uid,self.username,self.rol,self.password,self.description) +
                   '\n\t    %s' % (' 0         1         2   ') +
                   '\n\t    %s' % (' 012345678901234567890123') +
                   '\n\t    %s' % (' ========================') +
                   '\n\tL:  %r' % ('  {0:24b}'.format(self.L_AH)[::-1]).translate(str.maketrans('01', ' o'))+
                   '\n\tM:  %r' % ('  {0:24b}'.format(self.M_AH)[::-1]).translate(str.maketrans('01', ' o'))+
                   '\n\tX:  %r' % ('  {0:24b}'.format(self.X_AH)[::-1]).translate(str.maketrans('01', ' o'))+
                   '\n\tJ:  %r' % ('  {0:24b}'.format(self.J_AH)[::-1]).translate(str.maketrans('01', ' o'))+
                   '\n\tV:  %r' % ('  {0:24b}'.format(self.V_AH)[::-1]).translate(str.maketrans('01', ' o'))+
                   '\n\tS:  %r' % ('  {0:24b}'.format(self.S_AH)[::-1]).translate(str.maketrans('01', ' o'))+
                   '\n\tD:  %r' % ('  {0:24b}'.format(self.D_AH)[::-1]).translate(str.maketrans('01', ' o'))+
                   '\n')

class Group(Base):
    __tablename__ = 'GRUPO'
    gid = Column(Integer, primary_key=True, autoincrement=True, unique=True, index=True)
    groupname = Column(String(20), nullable=False, unique=True, index=True)
    description = Column(String(80), nullable=False)
    #_grupos = relationship("Groups", backref="GRUPO")

    def stringColumns(self):
        return ['groupname', 'description']

    def intColumns(self):
        return ['gid']

    def fromdict(self, dict_data):
        #dict_data = json.loads(jsondata)
        self.gid = dict_data.get('gid', 0)
        self.groupname = dict_data.get('groupname','')
        self.description = dict_data.get('description', '')
        return self

    def fromjson(self, jsondata):
        dict_data = json.loads(jsondata)
        self.gid = dict_data.get('gid', 0)
        self.groupname = dict_data.get('groupname','')
        self.description = dict_data.get('description', '')
        return self

    def __repr__(self):
        return '{\n\t"gid": %r,\n\t"groupname": "%s",\n\t"description": "%s"\n}\n' % (self.gid, self.groupname, self.description)

    def __toSring__(self):
        return "Group(%r,%r,%r)" % (self.gid, self.groupname, self.description)



class URIS(Base):
    __tablename__ = 'URIS'
    uriid = Column(Integer, primary_key=True, autoincrement=True, index=True)
    gid = Column(Integer, ForeignKey('GRUPO.gid'), nullable=False, primary_key=True, index=True)
    uri = Column(String(250), nullable=False)


    def stringColumns(self):
        return ['uri']

    def intColumns(self):
        return ['uriid', 'gid']

    def fromdict(self, jsondata):
        self.uriid = dict_data.get('uriid', 0)
        self.gid = dict_data.get('gid', 0)
        self.uri = dict_data.get('uri', '')
        return self

    def fromjson(self, jsondata):
        dict_data = json.loads(jsondata)
        self.uriid = dict_data.get('uriid', 0)
        self.gid = dict_data.get('gid', 0)
        self.uri = dict_data.get('uri', '')
        return self

    def __repr__(self):
        return '{\n\t"uriid": %r,\n\t"gid": %r,\n\t"uri": "%s"\n}\n' % (self.uriid, self.gid, self.uri)

    def __toString__(self):
        return "URIS(%r,%r,%r)" % (self.uriid, self.gid, self.uri)



class WORDS(Base):
    __tablename__ = 'WORDS'
    wordsid = Column(Integer, primary_key=True, autoincrement=True, index=True)
    gid = Column(Integer, ForeignKey('GRUPO.gid'), nullable=False, primary_key=True, index=True)
    words = Column(String(250), nullable=False)

    def stringColumns(self):
        return ['words']

    def intColumns(self):
        return ['wordsid', 'gid']

    def fromdict(self, jsondata):
        self.wordsid = dict_data.get('wordsid', 0)
        self.gid = dict_data.get('gid', 0)
        self.words = dict_data.get('words', '')
        return self

    def fromjson(self, jsondata):
        dict_data = json.loads(jsondata)
        self.wordsid = dict_data.get('wordsid', 0)
        self.gid = dict_data.get('gid', 0)
        self.words = dict_data.get('words', '')
        return self

    def __repr__(self):
        return '{\n\t"wordsid": %r,\n\t"gid": %r,\n\t"words": "%s"\n}\n' % (self.wordsid, self.gid, self.words)


    def __toString__(self):
        return "WORDS(%r,%r,%r)" % (self.wordsid, self.gid, self.words)

class MIMES(Base):
    __tablename__ = 'MIMES'
    mimeid = Column(Integer, primary_key=True, autoincrement=True, index=True)
    gid = Column(Integer, ForeignKey('GRUPO.gid'), nullable=False, primary_key=True, index=True)
    mimes = Column(String(250), nullable=False)

    def stringColumns(self):
        return ['mimes']

    def intColumns(self):
        return ['mimeid', 'gid']

    def fromdict(self, jsondata):
        self.wordsid = dict_data.get('mimeid', 0)
        self.gid = dict_data.get('gid', 0)
        self.words = dict_data.get('mimes', '')
        return self

    def fromjson(self, jsondata):
        dict_data = json.loads(jsondata)
        self.wordsid = dict_data.get('mimeid', 0)
        self.gid = dict_data.get('gid', 0)
        self.words = dict_data.get('mimes', '')
        return self

    def __repr__(self):
        return '{\n\t"mimeid": %r,\n\t"gid": %r,\n\t"mimes": "%s"\n}\n' % (self.mimeid, self.gid, self.mimes)


    def __toString__(self):
        return "MIMES(%r,%r,%r)" % (self.mimeid, self.gid, self.mimes)





if __name__ == "__main__":


    db=Database()
    TraceSQL = True

    rules = db.getRULES('MIME', 'kid1')
    for rule in rules:
        print(rule.__toString__())

    rules = db.getRULES('URIS', 'kid1')
    for rule in rules:
        print(rule.__toString__())

    rules = db.getRULES('WORD', 'kid1')
    for rule in rules:
        print(rule.__toString__())

    #print(rules)
    #print(db.isAdminAllowed('pep1', 'none1'))


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
