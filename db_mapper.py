#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:sts=4:ai:et:fileencoding=utf-8:number

import db_layer
import db_log
import json
import cgi
from Config import Config
import urllib

DEBUGCALL = Config.DEBUG['db_mapper.DEBUGCALL']
DEBUGANSWER = Config.DEBUG['db_mapper.DEBUGANSWER']
DEBUG =  Config.DEBUG['db_mapper.DEBUG']


class db_handler():
    __db__ = None
    __log__ = None

    def __init__(self):
        self.__db__ = db_layer.Database()
        self.__log__ = db_log.Database()

    def answer_wrapper(self, to_type, answer):
        if DEBUGCALL: print("answer_wrapper.call: (to_type %r, parms: %r)" % (to_type, answer))
        wrapped_answer = { 'typeinfo': '',
                           'answer': '',
                           'size': 0,
                           'code': 0}
        wrapped_answer['typeinfo'] = to_type
        if to_type == 'json':
            wrapped_answer['answer'] = answer
        elif to_type == 'html':
            wrapped_answer['answer'] = '<HTML><BODY><PRE>%r</PRE><a href="javascript: self.close()">Close Window</a></BODY></HTML>' % answer
        wrapped_answer['size'] = len(str(wrapped_answer['answer']))
        if DEBUGANSWER: print("answer_wrapper.return: (%r)" % wrapped_answer)
        return wrapped_answer


    def map_db2answer(self, query, answer):
        if DEBUGCALL: print("map_db2answer.call (query: %r, type %r, answer: %r)" % (query, type(answer), answer))

        if query in ['findUser', 'findGroup', 'groupsuserISmember', 'groupsuserNOTmember', 'getWords', 'getUris', 'getMimes', 'getLog']:
            printed_answer = self.answer_wrapper('json', answer)
        else:
            printed_answer = self.answer_wrapper('html', answer)

        if DEBUGANSWER: print("map_db2answer.return: (%r)" %  printed_answer)
        return printed_answer


    def handle_request(self, query, parms):
        if DEBUGCALL: print("handle_request.call: (query: %r parms: %r)" % (query, parms))
        #function =
        #print(function)
        #answer = function(parms)
        #print(answer)

        hook = self.map_query2db(query)
        #print("->>>> %r" % str(self.map_parms2db(query, parms)))
        if hook:
            answer =  self.map_db2answer(query, hook(self.map_parms2db(query, parms)))
        else:
            answer = None

        if DEBUGANSWER: print("handle_request.return: (%r)" % answer )

        return answer


    def map_query2db(self, query):
        if DEBUGCALL: print("map_query2db.call (query: %r)" % (query))

        q2db = {
            'findUser': self.__db__.findUser,
            'addUser': self.__db__.addUser,
            'modUser': self.__db__.changeUser,
            'delUser': self.__db__.delUser,
            'findGroup': self.__db__.findGroup,
            'addGroup': self.__db__.addGroup,
            'modGroup': self.__db__.changeGroup,
            'delGroup': self.__db__.delGroup,
            'groupsuserISmember': self.__db__.findGroupsByUser,
            'groupsuserNOTmember': self.__db__.findNotGroupsByUser,
            'addUserToGroup': self.__db__.wr_addRelation,
            'delUserFromGroup': self.__db__.wr_delRelation,
            'getWords': self.__db__.findWORDSbyGID,
            'getUris': self.__db__.findURISbyGID,
            'getMimes': self.__db__.findMIMESbyGID,
            'saveWords': self.__db__.wr_insertWORDSbyGID,
            'saveUris': self.__db__.wr_insertURISbyGID,
            'saveMimes': self.__db__.wr_insertMIMESbyGID,
            'getLog': self.__log__.getLastLines,
        }

        if query in q2db.keys():
            answer = q2db[query]
        else:
            answer = None

        if DEBUGANSWER: print("map_query2db.return (%r)" % answer)
        return answer

    def map_parms2db(self, query, parms):
        if DEBUGCALL: print("map_parms2db.call: (query: %r parms: %r)" % (query, parms))
        parms_dict = dict(cgi.parse_qsl(parms))

        def getparm(name): return parms_dict.get(name, '%' )
        def getparmint(name): return int(parms_dict.get(name, '0'))
        def getUser(): return self.map_dict2User(parms_dict)
        def getGroup(): return self.map_dict2Group(parms_dict)

        if query in ['findUser', 'groupsuserISmember', 'groupsuserNOTmember']:
            answer =  getparm('username')
        elif query in ['findGroup']:
            answer =  getparm('groupname')
        elif query in ['addUser', 'modUser', 'delUser']:
            answer =  getUser()
        elif query in ['addGroup', 'modGroup', 'delGroup']:
            answer =  getGroup()
        elif query in ['addUserToGroup', 'delUserFromGroup']:
            answer = parms_dict
        elif query in ['getWords', 'getUris', 'getMimes']:
            answer =  getparmint('gid')
        elif query in ['saveWords', 'saveUris', 'saveMimes']:
            answer = parms_dict
        elif query in ['getLog']:
            answer =  getparmint('numLines')

        if DEBUGANSWER: print("map_parms2db.return (%r)" % answer)
        return answer

    def map_dict2User(self, parms):
        if DEBUGCALL: print("map_dict2User.call: (type %s parms: %r)" % (type(parms), parms))
        if parms == None:
            answer = None
        elif(type(parms) == dict):
            newUser = db_layer.User()
            for k in parms:
                if k in newUser.intColumns():
                    try:
                        parms[k] = int(parms[k])
                    except:
                        pass
            newUser.fromdict(parms)
            answer = newUser
        if DEBUGANSWER: print("map_dict2User.return (%r)" % answer)
        return answer

    def map_dict2Group(self, parms):
        if DEBUGCALL: print("map_dict2Group.call: (type %s parms: %r)" % (type(parms), parms))
        if parms == None:
            answer = None
        elif(type(parms) == dict):
            newGroup = db_layer.Group()
            for k in parms:
                if k in newGroup.intColumns():
                    try:
                        parms[k] = int(parms[k])
                    except:
                        pass
            newGroup.fromdict(parms)
            answer = newGroup
        if DEBUGANSWER: print("map_dict2Group.return (%r)" % answer)
        return answer

    def map_dict2URIS(self, parms):
        if DEBUGCALL: print("map_dict2URIS.call: (type %s parms: %r)" % (type(parms), parms))
        if parms == None:
            answer = None
        elif(type(parms) == dict):
            newURIS = db_layer.URIS()
            for k in parms:
                if k in newURIS.intColumns():
                    try:
                        parms[k] = int(parms[k])
                    except:
                        pass

            newURIS.fromdict(parms)
            answer = newURIS

        if DEBUGANSWER: print("map_dict2URIS.return (%r)" % answer)
        return answer

    def map_dict2WORDS(self, parms):
        if DEBUGCALL: print("map_dict2WORDS.call: (type %s parms: %r)" % (type(parms), parms))
        if parms == None:
            answer = None
        elif(type(parms) == dict):
            newWORDS = db_layer.WORDS()
            for k in parms:
                if k in newWORDS.intColumns():
                    try:
                        parms[k] = int(parms[k])
                    except:
                        pass
            newWORDS.fromdict(parms)
            answer = newWORDS
        if DEBUGANSWER: print("map_dict2WORDS.return (%r)" % answer)
        return answer

    def map_dict2MIMES(self, parms):
        if DEBUGCALL: print("map_dict2MIMES.call: (type %s parms: %r)" % (type(parms), parms))
        if parms == None:
            answer = None
        elif(type(parms) == dict):
            newMIMES = db_layer.MIMES()
            for k in parms:
                if k in newMIMES.intColumns():
                    try:
                        parms[k] = int(parms[k])
                    except:
                        pass
            newMIMES.fromdict(parms)
            answer = newMIMES
        if DEBUGANSWER: print("map_dict2MIMES.return (%r)" % answer)
        return answer



if __name__ == "__main__":

    handler = db_handler()
    answer = handler.handle_request(query="findUser", parms="username=%")
    if answer != None:
        #print(answer.JSONdump())
        #for instance in answer:
        print(answer)
        #print( json.dumps(answer, cls=AlchemyEncoder))

