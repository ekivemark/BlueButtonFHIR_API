#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

"""
BlueButtonFHIR_API
FILE: signals.py
Created: 2/24/16 1:23 PM


"""
__author__ = 'Mark Scrimshire:@ekivemark'

import json

from collections import OrderedDict

from django.conf import settings

from django.dispatch import receiver
from django.db.models.signals import post_save
from oauth2_provider.models import AccessToken

from appmgmt.utils import write_fhir, build_fhir_id
from fhir_io_hapi.utils import fhir_datetime


@receiver(post_save, sender=AccessToken)
def write_consent(sender, **kwargs):
    if settings.DEBUG:
        print("Model post_save:", sender)
        print('Saved: {}'.format(kwargs['instance'].__dict__))

    A_Tkn = kwargs['instance'].__dict__

    body = OrderedDict()
    body['resourceType'] = "Contract"
    body['issued'] = fhir_datetime()
    body['type'] =   {"text": "Consent Directive"}
    body['subType'] = {"text": "Application Data Access"}

    # actor1 = OrderedDict()
    # actor1['resourceType'] = "Device"
    # actor1['entity'] = {build_fhir_id("system", settings.DOMAIN,
    #                                   "type", {"text": "BBApplication"},
    #                                   "value", A_Tkn['_application_cache'].fhir_reference.split("/")[1])
    #                     }
    # actor1['role'] = "Application"

    # actor2 = OrderedDict()
    # actor2['entity'] = OrderedDict([("resourceType", "Patient"),("identifier", str(A_Tkn['user_id']))])
    # actor2['role'] = "Beneficiary"

    # body['actor'] = [actor1] #, actor2]

    friendly_language = "Beneficiary (%s) gave [%s] permission to application (%s)" % (str(A_Tkn['user_id']),
                                                                                       A_Tkn['scope'],
                                                                                       A_Tkn['_application_cache'].fhir_reference)

    body['term'] = [{"text":friendly_language }]

    result = write_fhir("POST",
                        "Contract",
                        json.dumps(body),
                        "")

    if settings.DEBUG:
        print("A_Tkn:", A_Tkn)
        print("Body:", body)
        print("json:", json.dumps(body))
        print("Result:", result)


# Awesome POST_SAVE detected: Saved:
# {'_application_cache': <BBApplication: PMI>,
# 'expires': datetime.datetime(2016, 2, 25, 4, 46, 36, 630047, tzinfo=<UTC>),
# '_state': <django.db.models.base.ModelState object at 0x106d87a20>,
# '_user_cache': <User: ekivemark>, 'application_id': 1, 'user_id': 1,
# 'scope': 'read write_consent', 'id': 24, 'token': '29nNwYcYqiSbZBhSRm11dBZ9MlqIii'}

# {
#   "resourceType" : "Contract",
#   // from Resource: id, meta, implicitRules, and language
#   // from DomainResource: text, contained, extension, and modifierExtension
#   "identifier" : { Identifier }, // Contract identifier
#   "issued" : "<dateTime>", // When this Contract was issued
#   "applies" : { Period }, // Effective time
#   "subject" : [{ Reference(Any) }], // Subject of this Contract
#   "authority" : [{ Reference(Organization) }], //
#      Authority under which this Contract has standing
#   "domain" : [{ Reference(Location) }], // Domain in which this Contract applies
#   "type" : { CodeableConcept }, // Contract Tyoe
#   "subType" : [{ CodeableConcept }], // Contract Subtype
#   "action" : [{ CodeableConcept }], // Contract Action
#   "actionReason" : [{ CodeableConcept }], // Contract Action Reason
#   "actor" : [{ // Contract Actor
#     "entity" : { Reference(Contract|Device|Group|Location|Organization|Patient|
#     Practitioner|RelatedPerson|Substance|Supply) }, // R!  Contract Actor Type
#     "role" : [{ CodeableConcept }] // Contract  Actor Role
#   }],
#   "valuedItem" : [{ // Contract Valued Item
#     // entity[x]: Contract Valued Item Type. One of these 2:
#     "entityCodeableConcept" : { CodeableConcept },
#     "entityReference" : { Reference(Any) },
#     "identifier" : { Identifier }, // Contract Valued Item Identifier
#     "effectiveTime" : "<dateTime>", // Contract Valued Item Effective Tiem
#     "quantity" : { Quantity }, // Count of Contract Valued Items
#     "unitPrice" : { Money }, // Contract Valued Item fee, charge, or cost
#     "factor" : <decimal>, // Contract Valued Item Price Scaling Factor
#     "points" : <decimal>, // Contract Valued Item Difficulty Scaling Factor
#     "net" : { Money } // Total Contract Valued Item Value
#   }],
#   "signer" : [{ // Contract Signer
#     "type" : { Coding }, // R!  Contract Signer Type
#     "party" : { Reference(Organization|Patient|Practitioner|RelatedPerson) }, // R!
#       Contract Signatory Party
#     "signature" : "<string>" // R!  Contract Documentation Signature
#   }],
#   "term" : [{ // Contract Term List
#     "identifier" : { Identifier }, // Contract Term identifier
#     "issued" : "<dateTime>", // Contract Term Issue Date Time
#     "applies" : { Period }, // Contract Term Effective Time
#     "type" : { CodeableConcept }, // Contract Term Type
#     "subType" : { CodeableConcept }, // Contract Term Subtype
#     "subject" : { Reference(Any) }, // Subject of this Contract Term
#     "action" : [{ CodeableConcept }], // Contract Term Action
#     "actionReason" : [{ CodeableConcept }], // Contract Term Action Reason
#     "actor" : [{ // Contract Term Actor List
#       "entity" : { Reference(Contract|Device|Group|Location|Organization|
#      Patient|Practitioner|RelatedPerson|Substance|Supply) }, // R!  Contract Term Actor
#       "role" : [{ CodeableConcept }] // Contract Term Actor Role
#     }],
#     "text" : "<string>", // Human readable Contract term text
#     "valuedItem" : [{ // Contract Term Valued Item
#       // entity[x]: Contract Term Valued Item Type. One of these 2:
#       "entityCodeableConcept" : { CodeableConcept },
#       "entityReference" : { Reference(Any) },
#       "identifier" : { Identifier }, // Contract Term Valued Item Identifier
#       "effectiveTime" : "<dateTime>", // Contract Term Valued Item Effective Tiem
#       "quantity" : { Quantity }, // Contract Term Valued Item Count
#       "unitPrice" : { Money }, // Contract Term Valued Item fee, charge, or cost
#       "factor" : <decimal>, // Contract Term Valued Item Price Scaling Factor
#       "points" : <decimal>, // Contract Term Valued Item Difficulty Scaling Factor
#       "net" : { Money } // Total Contract Term Valued Item Value
#     }],
#     "group" : [{ Content as for Contract.term }] // Nested Contract Term Group
#   }],
#   // binding[x]: Binding Contract. One of these 2:
#   "bindingAttachment" : { Attachment },
#   "bindingReference" : { Reference(Composition|DocumentReference|
#    QuestionnaireAnswers) },
#   "friendly" : [{ // Contract Friendly Language
#     // content[x]: Easily comprehended representation of this Contract. One of these 2:
#     "contentAttachment" : { Attachment }
#     "contentReference" : { Reference(Composition|DocumentReference|
#     QuestionnaireAnswers) }
#   }],
#   "legal" : [{ // Contract Legal Language
#     // content[x]: Contract Legal Text. One of these 2:
#     "contentAttachment" : { Attachment }
#     "contentReference" : { Reference(Composition|DocumentReference|
#     QuestionnaireAnswers) }
#   }],
#   "rule" : [{ // Computable Contract Language
#     // content[x]: Computable Contract Rules. One of these 2:
#     "contentAttachment" : { Attachment }
#     "contentReference" : { Reference(DocumentReference) }
#   }]
# }
#