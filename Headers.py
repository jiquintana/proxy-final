#!/usr/bin/python
# -*- coding: utf-8 -*-
# header_valueim: ts=4:sw=4:sts=4:ai:et:fileencoding=utf-8:number
import sys
import re
from Log import Log
from Config import Config

class ClientHeaders:
    DEBUG = Config.DEBUG['ClientHeaders.DEBUG']
    __orig_headers = {}
    __headers = {}
    __cookies = {}
    ip = ''
    port = ''
    log = Log()

    def __init__(self,  headers, debug =False,
                     ip='', port=''):
        self.__orig_headers = {}
        self.__headers = {}
        self.__cookies = {}
        self.DEBUG = debug
        self.ip = ip
        self.port = port

        if self.DEBUG: self.log.pdebug ('ClientHeaders.__init__')
        if headers != []:
            self.__orig_headers = headers

    def parse(self):
        lines=self.__orig_headers.splitlines()[:-1]
        for line in lines:
            header_key, header_value = line.split(': ',1)      # Solo partimos una vez
            header_key = header_key.capitalize()

            got_text_headers = False

            if self.DEBUG: self.log.pdebug('%s:%s: * IH %s -> %s' % (self.ip, self.port, header_key, header_value))
            # Evitamos copiar la autorizacion del proxy y el host
            if header_key not in ['Proxy-authorization','Host', 'Accept-encoding']:
                # Eliminamos la cabecera de autenticacion proxy,
                # Eliminamos la traza del Host y
                # Eliminamos las cabeceras que no sean texto plano p.ej: "Accept-encoding -> gzip, deflate"
                # Si tenemos la cabecera
                if (header_key== 'Content-length') and self.DEBUG:
                    self.log.pdebug("::: HDR - %s:%s Content-length => hdr %s\n" % (self.ip,self.port,header_value))

                if self.DEBUG: self.log.pdebug('%s:%s: . FH %s -> %s' % (self.ip, self.port, header_key, header_value))
                if header_key in self.__headers:
                    # Copiamos el antiguo valor y hacemos un append
                    oldvalue=self.__headers[header_key]
                    self.__headers[header_key]=oldvalue+' '+header_value
                    if self.DEBUG: self.log.pdebug('%s:%s: *********** Append header %s -> %s' % (self.ip, self.port, header_key, self.__headers[header_key]))
                else:
                    self.__headers[header_key]=header_value
                    if self.DEBUG: self.log.pdebug('%s:%s: + OH %s -> %s' % (self.ip, self.port, header_key, self.__headers[header_key]))
            else:
                if self.DEBUG: self.log.pdebug('%s:%s: - OH %s -> %s' % (self.ip, self.port, header_key, header_value))

        return self.__headers

class ServerHeaders:
    DEBUG = Config.DEBUG['ServerHeaders.DEBUG']
    via_header_seen = False
    headers_have_been_parsed = False
    __response = []
    __headers = []
    ip = ''
    port = ''
    log = Log()
    __is_text = False
    __content_type = ""

    def __init__(self,  response, debug =False,
                 ip='', port='', server_version='HTTP_Proxy/0.1'):
        self.__headers = []
        self.__headers [:] = []
        self.ip = ''
        self.port = ''
        self.DEBUG = debug
        self.ip = ip
        self.port = port
        self.server_version = server_version
        self.headers_have_been_parsed = False
        self.__is_text = False
        self.__content_type = ""

        if self.DEBUG: self.log.pdebug ('ServerHeaders.__init__')
        if response != []:
            self.__response = response

    def is_text(self):
        return self.__is_text

    def get_content_type(self):
        return self.__content_type

    def parsed_headers(self):
        if self.DEBUG: self.log.pdebug ('Headers.parsed_headers')
        if not self.headers_have_been_parsed:
            self.__parse()
        return self.__headers

    def dump(self):
        if self.DEBUG: self.log.pdebug ('Headers.dump')

        for i in self.__response.headers:
            self.log.pdebug(' > %s %s: %s' % (self.port, i, self.__response.headers[i]))
        if self.headers_have_been_parsed:
            for i in self.__headers:
                self.log.pdebug(' < %s %s:' % (self.port, i))

    def __parse(self):
        if self.DEBUG: self.log.pdebug ('Headers.parse')
        for header_name, header_value in self.__response.headers.items():

            if self.DEBUG and header_name in ['content-length','transfer-encoding','te','content-encoding','content-md5'] :
                self.log.pdebug('::: HDR - %s:%s header %s-> value %s\n' % (self.ip,self.port,header_name, header_value))

            if self.DEBUG: self.log.pdebug('IN header: %s - %s: %s' % (self.port,header_name.capitalize(),header_value))
            if (header_name == 'date'):
                pass
            elif (header_name== 'content-length'):
                # Debido a que la librería request hace descompresion automatica, no nos podemos
                # fiar del header 'content-length' en caso de codificacion deflate/gzip, asi que
                # reescribimos la cabecera incondicionalmente

                if self.DEBUG: sys.stderr.write(":::: Content-length => hdr %s vs cont %s\n" % (header_value,len(self.__response.content)))
                self.__headers.append([header_name.capitalize(), len(self.__response.content)])
                if self.DEBUG:
                    self.log.pdebug('OU header CL: %s - %s: %s' % (self.port,header_name.capitalize(),header_value))
                    self.log.pdebug('OU header SZ: %s -   : %s' % (self.port, len(self.__response.content)))
                pass
            elif (header_name == 'transfer-encoding'):
                # Eliminamos transfer-encoding por la misma razon anterior
                if self.DEBUG: self.log.pdebug('SU header: %s - %s: %s' % (self.port,header_name.capitalize(),header_value))

            elif (header_name=='content-encoding'):
                # Eliminamos transfer-encoding por la misma razon anterior
                if self.DEBUG: self.log.pdebug('SU header: %s - %s: %s' % (self.port,header_name.capitalize(),header_value))
            elif (header_name== 'via'):
                self.via_header_seen = True
                # Agnadimos la cabecera via
                header_value+=', http/1.0 '+self.server_version
                self.__headers.append([header_name.capitalize(),header_value])
                if self.DEBUG: self.log.pdebug('OU header: %s - %s: %s' % (self.port,header_name.capitalize(),header_value))

            elif (header_name == 'server'):
                # la escribe directamente el servidor BaseHTTPServer
                if self.DEBUG: self.log.pdebug('SU header: %s - %s: %s' % (self.port,header_name.capitalize(),header_value))

            elif (header_name == 'set-cookie'):
                from requests.cookies import get_cookie_header
                # Este bloque gestiona las cookies; Requests devuelve todas las cookies en un array 'set-cookie', pero indistinguible si hay varias.
                # para obtener todos los parámetros y reenviarlos, parseamos la cadena.
                def allindices(string, sub, listindex=[], offset=0):
                    i = string.find(sub, offset)
                    while i >= 0:
                        listindex.append(i)
                        i = string.find(sub, i + 1)
                    return listindex

                # inicializamos el vector POS con valor 0 y longitud de la cadena
                POS = [0,len(header_value)]

                # Para cada una de las cookies encontradas en los headers...
                # Caso excepcional cuando la cookie está en la primera posición de la cadena: no la buscamos porque hemos añadido la posición 0,
                # así que buscaremos la cadena ' ,<COOKIE>=' y ' <COOKIE>='
                for cookie in self.__response.cookies.keys():
                    # buscamos la cookie en formato ", cookie=" y agnadimos todas las posiciones al vector POS
                    for i in allindices(header_value, ', '+cookie+'='): POS.append(i)
                    # buscamos la cookie en formato " cookie=" y agnadimos todas las posiciones al vector POS
                    for i in allindices(header_value, ' '+cookie+'='): POS.append(i)


                #for header_nameey in resp.cooheader_nameies.header_nameeys():
                #   for i in allindices(header_value, ', '+header_nameey+'='): POS.append(i)
                #  for i in allindices(header_value, header_nameey+'='): POS.append(i)

                # Eliminamos los valores duplicados en el array POS
                POS=list(set(POS))
                # y lo ordenamos
                POS.sort()

                # ahora tenemos un array con las posiciones de las cookies a cortar
                while (POS != []):
                    parsed_cookie=header_value[POS[0]:POS[1]]
                    #self.send_header('Set-Cookie',parsed_cookie)
                    self.__headers.append(['Set-Cookie',parsed_cookie])
                    if self.DEBUG:
                        self.log.pdebug("\t... cookie: Set-cookie=%s" % (header_value[POS[0]:POS[1]]))

                    # eliminamos las posiciones 0 y 1; como eliminamos primero el valor [0], el valor [1]
                    # se convierte en la segunda llamada en [0]
                    POS.remove(POS[0])
                    POS.remove(POS[0])
                pass



            else:
                if self.DEBUG: self.log.pdebug('OU header: %s - %s: %s' % (self.port,header_name.capitalize(),header_value))
                self.__headers.append([header_name.capitalize(),header_value])
                if header_name == "content-type":
                    #print("!!!!!!!!!!!!!!!!!!!!!!!!!!!! got content-type %r" % (header_value))
                    self.__content_type = header_value.lower()
                    text_matching = re.compile("(json|text|html|javascript|css|php)", re.IGNORECASE)
                    match = text_matching.search(header_value)
                    if match != None:
                        self.__is_text = True
                        #print("!!!!!!!!!!!!!!!!!!!!!!!!!!!! got content-type %r" % (self.__is_text))



        if (not self.via_header_seen):
            # Agnadimos a cabecera via
            header_name='Via'
            header_value='http/1.0 '+self.server_version
            self.__headers.append([header_name.capitalize(),header_value])
            if self.DEBUG: self.log.pdebug('OU header: %s - %s: %s' % (self.port,header_name,header_value))

        self.headers_have_been_parsed = True

        return

    def headers():
        return self.__headers