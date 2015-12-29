"""
bbofuser:account
FILE: ldap
Created: 8/11/15 3:17 PM

LDAP Utilities for Account

"""
__author__ = 'Mark Scrimshire:@ekivemark'

from ldap3 import (Server, Connection,
                   ALL, SUBTREE, ANONYMOUS,
                   SIMPLE, SYNC, ASYNC,
                   LDAPExceptionError, LDAPException, LDAPSocketOpenError,
                   LDAPOperationResult,
                   )

from django.conf import settings
from django.contrib import messages


def validate_ldap_user(request, email):
    """ Search LDAP for user
        return email if there is a match
    """
    if settings.DEBUG:
        print("in accounts.views.ldap.validate_ldap_user with email:", email)
    result = {}
    if email == "":
        return result

    if not settings.REMOTE_LDAP_CHECK:
        if settings.DEBUG:
            print("LDAP Remote Checking is set to:", settings.REMOTE_LDAP_CHECK)
        return email.lower()

    ##############
    # REMOTE_LDAP_CHECK is True
    # So we need to we need to reach out to the LDAP Server

    server = Server(settings.AUTH_LDAP_SERVER_URI, get_info=ALL)
    try:
        c = Connection(server, auto_bind=True, raise_exceptions=False)
        bound = c.bind()
        if settings.DEBUG:
            print("Connect:",c)
            print("Bind:", bound)
            pass
    except LDAPSocketOpenError:
        c = {}
        if settings.DEBUG:
            print("Server is not reachable")
            print("Connection Exception:",LDAPOperationResult.__str__)
        messages.error(request,
                       "We are having problems reaching the MyMedicare.gov server"
                       " to check your email address. Try again later.")
        result = "ERROR" + str(LDAPExceptionError) + str(LDAPSocketOpenError)
        return result
    if settings.DEBUG:
        #print("Server_Info:", server.info)
        pass

    # ldap_result = c.search(search_base=settings.AUTH_LDAP_SCOPE,
    #                         search_filter="(objectClass=inetOrgPerson)",
    #                        search_scope=SUBTREE,
    #                        attributes = settings.LDAP_AUTH_GET_FIELDS
    #                        )

    # if settings.DEBUG:
    #     print("LDAP_RESULT for ",settings.AUTH_LDAP_SCOPE)
    #     print("response:",c.response)

    user_scope = "cn=" + email.strip() + "," + settings.AUTH_LDAP_SCOPE

    ldap_email_check = c.search(search_base=user_scope,
                                search_filter="(objectClass=inetOrgPerson)",
                                search_scope=SUBTREE,
                                attributes = settings.LDAP_AUTH_GET_FIELDS
                                )
    if settings.DEBUG:
        # print("LDAP_Result for ",user_scope)
        # print("Response:", c.response)
        pass

    ldap_email = ""
    for r in c.response:
        print(r['dn'],r['attributes'])
        ldap_email = r['attributes']['mail']

        print("LDAP_EMAIL:", ldap_email[0] )
    # Patch
    return ldap_email[0].lower()
    # Patch


