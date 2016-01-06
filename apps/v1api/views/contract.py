#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

"""
BlueButtonFHIR_API
FILE: apps.v1api.contract
Created: 1/4/16 1:22 AM

Write consent by beneficiary to allow use of their data by third party application

Status: Experimental

Get FHIR Contract format from http://hl7.org/fhir/contract.html

{
  "resourceType" : "Contract",
  // from Resource: id, meta, implicitRules, and language
  // from DomainResource: text, contained, extension, and modifierExtension
  "identifier" : { Identifier }, // Contract identifier
  "issued" : "<dateTime>", // When this Contract was issued
  "applies" : { Period }, // Effective time
  "subject" : [{ Reference(Any) }], // Subject of this Contract
  "authority" : [{ Reference(Organization) }], // Authority under which this Contract has standing
  "domain" : [{ Reference(Location) }], // Domain in which this Contract applies
  "type" : { CodeableConcept }, // Contract Tyoe
  "subType" : [{ CodeableConcept }], // Contract Subtype
  "action" : [{ CodeableConcept }], // Contract Action
  "actionReason" : [{ CodeableConcept }], // Contract Action Reason
  "actor" : [{ // Contract Actor
    "entity" : { Reference(Contract|Device|Group|Location|Organization|Patient|
    Practitioner|RelatedPerson|Substance) }, // R!  Contract Actor Type
    "role" : [{ CodeableConcept }] // Contract  Actor Role
  }],
  "valuedItem" : [{ // Contract Valued Item
    // entity[x]: Contract Valued Item Type. One of these 2:
    "entityCodeableConcept" : { CodeableConcept },
    "entityReference" : { Reference(Any) },
    "identifier" : { Identifier }, // Contract Valued Item Identifier
    "effectiveTime" : "<dateTime>", // Contract Valued Item Effective Tiem
    "quantity" : { Quantity(SimpleQuantity) }, // Count of Contract Valued Items
    "unitPrice" : { Quantity(Money) }, // Contract Valued Item fee, charge, or cost
    "factor" : <decimal>, // Contract Valued Item Price Scaling Factor
    "points" : <decimal>, // Contract Valued Item Difficulty Scaling Factor
    "net" : { Quantity(Money) } // Total Contract Valued Item Value
  }],
  "signer" : [{ // Contract Signer
    "type" : { Coding }, // R!  Contract Signer Type
    "party" : { Reference(Organization|Patient|Practitioner|RelatedPerson) }, // R!  Contract Signatory Party
    "signature" : "<string>" // R!  Contract Documentation Signature
  }],
  "term" : [{ // Contract Term List
    "identifier" : { Identifier }, // Contract Term identifier
    "issued" : "<dateTime>", // Contract Term Issue Date Time
    "applies" : { Period }, // Contract Term Effective Time
    "type" : { CodeableConcept }, // Contract Term Type
    "subType" : { CodeableConcept }, // Contract Term Subtype
    "subject" : { Reference(Any) }, // Subject of this Contract Term
    "action" : [{ CodeableConcept }], // Contract Term Action
    "actionReason" : [{ CodeableConcept }], // Contract Term Action Reason
    "actor" : [{ // Contract Term Actor List
      "entity" : { Reference(Contract|Device|Group|Location|Organization|
     Patient|Practitioner|RelatedPerson|Substance) }, // R!  Contract Term Actor
      "role" : [{ CodeableConcept }] // Contract Term Actor Role
    }],
    "text" : "<string>", // Human readable Contract term text
    "valuedItem" : [{ // Contract Term Valued Item
      // entity[x]: Contract Term Valued Item Type. One of these 2:
      "entityCodeableConcept" : { CodeableConcept },
      "entityReference" : { Reference(Any) },
      "identifier" : { Identifier }, // Contract Term Valued Item Identifier
      "effectiveTime" : "<dateTime>", // Contract Term Valued Item Effective Tiem
      "quantity" : { Quantity(SimpleQuantity) }, // Contract Term Valued Item Count
      "unitPrice" : { Quantity(Money) }, // Contract Term Valued Item fee, charge, or cost
      "factor" : <decimal>, // Contract Term Valued Item Price Scaling Factor
      "points" : <decimal>, // Contract Term Valued Item Difficulty Scaling Factor
      "net" : { Quantity(Money) } // Total Contract Term Valued Item Value
    }],
    "group" : [{ Content as for Contract.term }] // Nested Contract Term Group
  }],
  // binding[x]: Binding Contract. One of these 2:
  "bindingAttachment" : { Attachment },
  "bindingReference" : { Reference(Composition|DocumentReference|
   QuestionnaireResponse) },
  "friendly" : [{ // Contract Friendly Language
    // content[x]: Easily comprehended representation of this Contract. One of these 2:
    "contentAttachment" : { Attachment }
    "contentReference" : { Reference(Composition|DocumentReference|
    QuestionnaireResponse) }
  }],
  "legal" : [{ // Contract Legal Language
    // content[x]: Contract Legal Text. One of these 2:
    "contentAttachment" : { Attachment }
    "contentReference" : { Reference(Composition|DocumentReference|
    QuestionnaireResponse) }
  }],
  "rule" : [{ // Computable Contract Language
    // content[x]: Computable Contract Rules. One of these 2:
    "contentAttachment" : { Attachment }
    "contentReference" : { Reference(DocumentReference) }
  }]
}

"""
__author__ = 'Mark Scrimshire:@ekivemark'

from django.conf import settings

def contract_create(contract_info={}):
    # Create a new contract
    if settings.DEBUG:
        print("In contract_create with contract_info:", contract_info)
    pass

    return True

