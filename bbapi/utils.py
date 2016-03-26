"""
bbofuser
FILE: utils
Created: 6/16/15 12:11 AM
Basic conversion tools
"""
__author__ = 'Mark Scrimshire:@ekivemark'

import socket

from threading import local
from django.conf import settings

_user = local()

class CurrentUserMiddleware(object):
    ###
    ### Add to MIDDLEWARE_CLASSES after Authentication middleware
    ###
    def process_request(selfself,request):
        _user.value = request.user


def get_current_user():
    return _user.value


def str2bool(inp):
    output = False
    if inp.upper() == "TRUE":
        output = True
    elif inp.upper() == "FALSE":
        output = False

    return output


def str2int(inp):
    output = 0 + int(inp)

    return output


def Server_Ip():
    # use socket to get ip address for this server
    return socket.gethostbyname(socket.gethostname())


def Server_Name():
    # use socket to return server name
    return socket.gethostname()

def FhirServerUrl(server=None,path=None, release=None ):
    # fhir_server_configuration = {"SERVER":"http://fhir-test.bbonfhir.com:8081",
    #                              "PATH":"",
    #                              "RELEASE":"/baseDstu2"}
    # FHIR_SERVER_CONF = fhir_server_configuration
    # FHIR_SERVER = FHIR_SERVER_CONF['SERVER'] + FHIR_SERVER_CONF['PATH']


    if server == None:
        fhir_server = settings.FHIR_SERVER_CONF['SERVER']
    else:
        fhir_server = server

    if path == None:
        fhir_path = settings.FHIR_SERVER_CONF['PATH']
    else:
        fhir_path = path


    if release == None:
        fhir_release = settings.FHIR_SERVER_CONF['RELEASE']
    else:
        fhir_release = release

    return fhir_server + fhir_path + fhir_release

