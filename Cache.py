#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:sts=4:ai:et:fileencoding=utf-8:number
import sys
if sys.version_info < (3, 0):
    python_OldVersion = True
else:
    python_OldVersion = False

import hashlib
from Config import Config
from Log import Log

import os
import pprint

def remove_html_markup(s):
    tag = False
    quote = False
    out = ""

    for c in s:
        if c == '<' and not quote:
            tag = True
        elif c == '>' and not quote:
            tag = False
        elif (c == '"' or c == "'") and tag:
            quote = not quote
        elif not tag:
            out = out + c
    return out

class FileCache:
    path = ''
    md5hash_str = ''
    cache_filename_base = ''
    cache_filename_meta = ''
    cache_filename_cache = ''
    cache_filename_strip = ''
    cache_filename_header = ''
    content_is_text = False
    content_stripped = bytes()
    logger = Log()


    is_initialized = False
    DEBUG = Config.DEBUG['Cache.DEBUG']

    def remove_html_markup(self,s):
        tag = False
        quote = False
        out = ""

        for c in s:
            if c == '<' and not quote:
                tag = True
            elif c == '>' and not quote:
                tag = False
            elif (c == '"' or c == "'") and tag:
                quote = not quote
            elif not tag:
                out = out + c
        return out


    def __init__(self):
        if not os.path.exists(Config.cache_Path):
            os.makedirs(Config.cache_Path)
        self.was_checked = False
        self.DEBUG = False
        return

    def setup(self, path, debug=False, ip='', port=''):
        self.path=path
        md5hash = hashlib.md5()
        if python_OldVersion:
            md5hash.update(self.path.encode("utf_8"))
        else:
            md5hash.update(bytes(self.path,encoding='utf_8'))

        self.md5hash = md5hash.hexdigest()

        self.cache_filename_base = Config.cache_Path + '/' + self.md5hash.upper()
        self.cache_filename_meta = self.cache_filename_base + '.url'
        self.cache_filename_cache = self.cache_filename_base + '.cache'
        self.cache_filename_header = self.cache_filename_base + '.head'
        self.cache_filename_strip = self.cache_filename_base + '.strip'
        self.is_initialized = True

        if debug == True or self.DEBUG == True:
            self.logger.pdebug('Filecache.setup dump:')
            self.logger.pdebug(vars(self))

        return

    def is_cached(self, path, debug=False, ip='', port=''):
        returncode = False
        meta_file_path = ''

        if not self.is_initialized:
            self.setup(path=path)

        if os.path.exists(self.cache_filename_cache):
            try:
                with open(self.cache_filename_meta, 'r') as meta_file:
                    meta_file_path = meta_file.read()
            except Exception as e:
                self.logger.pdebug('!!! exception %s:%s %s, ::: Control Cache is_cached' % (ip, port, self.cache_filename_base, e))

                pass
        if (meta_file_path == path):
            returncode = True
        return returncode


    def put(self, path, content, headers, strip_text, debug=False, ip='', port=''):
        succeded = False
        if not self.is_initialized:
            self.setup(path=path)

        #self.setup(path)
        #self.cache_filename_base = Config.cache_Path + '/' + self.md5hash
        #self.cache_filename_meta = self.cache_filename_base + '.meta'
        #self.cache_filename_cache = self.cache_filename_base + '.cache'

        try:
            with open(self.cache_filename_meta, 'wb') as meta_file:
                if python_OldVersion:
                    meta_file.write(path.encode('utf_8'))
                else:
                    meta_file.write(bytes(path,encoding='utf_8'))

            with open(self.cache_filename_cache, 'wb') as cache_file:
                cache_file.write(content)

            with open(self.cache_filename_header, 'wb') as header_file:
                for k,v in headers:
                    if python_OldVersion:
                        header_file.write(str(k+': '+str(v)+'\n').encode('UTF-8'))
                    else:
                        header_file.write(bytes(k+': '+str(v)+'\n','UTF-8'))

            if strip_text:
                content_is_text = strip_text
                self.content_stripped = bytes()
                with open(self.cache_filename_strip, 'wb') as strip_file:
                    if python_OldVersion:
                        self.content_stripped = bytes(self.remove_html_markup(content.decode('utf-8')))
                        strip_file.write(self.content_stripped,'UTF-8')
                    else:
                        self.content_stripped = self.remove_html_markup(content.decode('utf-8')).encode('UTF-8')
                        strip_file.write(self.content_stripped)

            succeded = True

            if debug == True:
                self.logger.pdebug('%s:%s, ::: CCH filename: %s' % (ip, port, self.cache_filename_base))
                self.logger.pdebug('%s:%s, ::: CCH path: %s' % (ip, port, path))
                self.logger.pdebug('%s:%s, ::: CCH size %s' % (ip, port, len(content)))

        except Exception as e:
            self.logger.pdebug('!!! exception %s:%s %s, ::: Control Cache put %s' % (ip, port, str(e), self.cache_filename_base))

        return succeded


    def get(self, path, debug=False, ip='', port=''):
        succeded = False
        if python_OldVersion:
            content= u''
        else:
            content= bytes('','UTF-8')
        headers= []

        if not self.is_initialized:
            self.setup(path=path)

        try:
            with open(self.cache_filename_cache, 'rb') as cache_file:
                content=cache_file.read()

            # El fichero de cabeceras debe leerse en modo Ascii en windows, si no, retorna un '\n' adicional al final de la cadena
            with open(self.cache_filename_header, 'r') as headers_file:
                headers=headers_file.readlines()
            succeded = True
        except Exception as e:
            self.logger.pdebug('!!! exception %s:%s %s, ::: Control Cache get %s' % (ip, port, str(e), self.cache_filename_base))

        return content, headers
