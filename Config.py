#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:sts=4:ai:et:fileencoding=utf-8:number:syntax=on:set filetype indent plugin on


class Config:
    MAX_LEN_MSG = 140
    NUM_THREADS = 180
    PORT = 8002

    config_Path = "./db"
    cache_Path = "./cache"
    log_Path = "./cache"

    dbFiles = {
        'proxy': 'sqlite:///' + config_Path+'/proxy.db',
        'log': 'sqlite:///' + config_Path+'/log.db'
    }

    dbTrace = {
        'proxy': False,
        'log': False
    }

    DEBUG = {
        'db_mapper.DEBUGCALL' : False,
        'db_mapper.DEBUGANSWER' : False,
        'db_mapper.DEBUG' : False,
        'Proxy.DEBUG': False,
        'Proxy.DEBUG_BEFORE_HANDLING': False,
        'Cache.DEBUG': False,
        'ClientHeaders.DEBUG': False,
        'ServerHeaders.DEBUG': False,
    }

    TRACE = {
        'Log_TRACE': True
    }