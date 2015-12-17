"""
bbofuser: apps.v1api
FILE: fhir_elements
Created: 8/21/15 10:15 AM

FHIR Profiles have sub-resources that are often repeated.
This set of functions is meant to enable processing of those sub-elements

"""
__author__ = 'Mark Scrimshire:@ekivemark'

import json
from django.conf import settings

from apps.v1api.views.fhir_utils import (assign_str,
                                         build_str,
                                         assign_bool,)


def human_name(source):
    """
    Receive a dict with Name elements
    :param source: {}
    :return: hn {}

{
  "resourceType" : "HumanName",
  // from Element: extension
  "use" : "<code>", // usual | official | temp | nickname | anonymous | old | maiden
  "text" : "<string>", // Text representation of the full name
  "family" : ["<string>"], // Family name (often called 'Surname')
  "given" : ["<string>"], // Given names (not always 'first'). Includes middle names
  "prefix" : ["<string>"], // Parts that come before the name
  "suffix" : ["<string>"], // Parts that come after the name
  "period" : { Period } // Time period when name was/is in use
}

    """
    # Setup the dictionary
    hn = {}

    if settings.DEBUG:
        print("Source:", source)
    # Map values across to new dictionary
    hn['resourceType'] = "HumanName"
    hn['use'] = assign_str(source, 'use', "usual")
    hn['suffix'] = assign_str(source, 'suffix',)
    hn['prefix'] = assign_str(source, 'prefix',)
    hn['family'] = assign_str(source, 'family')
    hn['given']  = assign_str(source, 'given')
    hn['period'] = assign_str(source, 'period')

    # Build the Text section
    if 'text' in source:
        hn['text'] = source['text']
    else:
        hn['text'] = build_str("", 'prefix', source)
        hn['text'] = build_str(hn['text'], 'given', source)
        hn['text'] = build_str(hn['text'], 'family', source)
        hn['text'] = build_str(hn['text'], 'suffix', source)

    # Return the dictionary
    # if settings.DEBUG:
        # print("Human_Name element:", hn)

    return hn

def contact_point(source):
    """
    Receive a dict with Contact elements
    :param source: {}
    :return: cp {}

{
  "resourceType" : "ContactPoint",
  // from Element: extension
  "system" : "<code>", // C? phone | fax | email | pager | other
  "value" : "<string>", // The actual contact point details
  "use" : "<code>", // home | work | temp | old | mobile - purpose of this contact point
  "rank" : "<positiveInt>", // Specify preferred order of use (1 = highest)
  "period" : { Period } // Time period when the contact point was/is in use
}
    """
    # Setup the Dictionary
    cp = {}

    # if settings.DEBUG:
    #    print("Contact Point source:", source)

    # Map values across to new dictionary
    cp['resourceType'] = "ContactPoint"
    cp['system'] = assign_str(source, 'system', "usual")
    cp['value']  = assign_str(source, 'value',)
    cp['use']    = assign_str(source, 'use')
    if 'rank' in source:
        get_rank = assign_str(source, 'rank')
        if get_rank:
            cp['rank'] = int(get_rank)
    cp['period'] = assign_str(source, 'period')

    # if settings.DEBUG:
    #     print("Returning CP:", cp)
    #return the dictionary
    return cp

def address(source):
    """
    Receive a dict with Address Elements
    :param source:
    :return: Ad {}

{
  "resourceType" : "Address",
  // from Element: extension
  "use" : "<code>", // home | work | temp | old - purpose of this address
  "type" : "<code>", // postal | physical | both
  "text" : "<string>", // Text representation of the address
  "line" : ["<string>"], // Street name, number, direction & P.O. Box etc
  "city" : "<string>", // Name of city, town etc.
  "district" : "<string>", // District name (aka county)
  "state" : "<string>", // Sub-unit of country (abbreviations ok)
  "postalCode" : "<string>", // Postal code for area
  "country" : "<string>", // Country (can be ISO 3166 3 letter code)
  "period" : { Period } // Time period when address was/is in use
}

    """
    # Setup dictionary
    ad = {}

    # Map values across to new dictionary
    ad['resourceType'] = "Address"
    ad['use']        = assign_str(source, 'use',)
    ad['type']       = assign_str(source, 'type',)
    ad['line']       = assign_str(source, 'line',)
    ad['city']       = assign_str(source, 'city',)
    ad['district']   = assign_str(source, 'district',)
    ad['state']      = assign_str(source, 'state',)
    ad['postalCode'] = assign_str(source, 'postalCode',)
    ad['country']    = assign_str(source, 'country',)
    ad['period']     = assign_str(source, 'period',)

    if 'text' in source:
        ad['text'] = source['text']
    else:
        ad['text'] = build_str("", 'line', source, delimiter=", ")
        ad['text'] = build_str(ad['text'], 'city', source, delimiter=", ")
        ad['text'] = build_str(ad['text'], 'state', source)
        ad['text'] = build_str(ad['text'], 'postalCode', source, delimiter=", ")
        ad['text'] = build_str(ad['text'], 'country', source, delimiter=".")

    return ad


def npid(source):
    """
    Build NPI Identifier Section
    :param source:
    :return: npi {}

{
  // from Element: extension
  "use" : "<code>", // usual | official | temp | secondary (If known)
  "type" : { CodeableConcept }, // Description of identifier
  "system" : "<uri>", // The namespace for the identifier
  "value" : "<string>", // The value that is unique
  "period" : { Period }, // Time period when id is/was valid for use
  "assigner" : { Reference(Organization) } // Organization that issued id (may be just text)
}

CodeableConcept:
{
  // from Element: extension
  "coding" : [{ Coding }], // Code defined by a terminology system
  "text" : "<string>" // Plain text representation of the concept
}

CodeableConcept:Coding:
{
  // from Element: extension
  "system" : "<uri>", // Identity of the terminology system
  "version" : "<string>", // Version of the system - if relevant
  "code" : "<code>", // Symbol in syntax defined by the system
  "display" : "<string>", // Representation defined by the system
  "userSelected" : <boolean> // If this coding was chosen directly by the user
}

Identifier:assigner
Identifier:assigner:Reference
{
  // from Element: extension
  "reference" : "<string>", // C? Relative, internal or absolute URL reference
  "display" : "<string>" // Text alternative for the resource
}
Identifier:assigner:Reference:Organization
{
  "resourceType" : "Organization",
  // from Resource: id, meta, implicitRules, and language
  // from DomainResource: text, contained, extension, and modifierExtension
  "identifier" : [{ Identifier }], // C? Identifies this organization  across multiple systems
  "active" : <boolean>, // Whether the organization's record is still in active use
  "type" : { CodeableConcept }, // Kind of organization
  "name" : "<string>", // C? Name used for the organization
  "telecom" : [{ ContactPoint }], // C? A contact detail for the organization
  "address" : [{ Address }], // C? An address for the organization
  "partOf" : { Reference(Organization) }, // The organization of which this organization forms a part
  "contact" : [{ // Contact for the organization for a certain purpose
    "purpose" : { CodeableConcept }, // The type of contact
    "name" : { HumanName }, // A name associated with the contact
    "telecom" : [{ ContactPoint }], // Contact details (telephone, email, etc)  for a contact
    "address" : { Address } // Visiting or postal addresses for the contact
  }]
}

    """

    # HL7 OID Registry Code for National Provider Identity
    # 2.16.840.1.113883.4.6
    # http://www.hl7.org/oid/OID_view.cfm?&Comp_OID=2.16.840.1.113883.4.6
    # http://www.hl7.org/oid/index.cfm

    # URI for NPI Coding System
    sys_uri = "http://www.hl7.org/oid/OID_view.cfm?&Comp_OID=2.16.840.1.113883.4.6"

    # NPI Coding Data
    npi_coding = {'system' : sys_uri,
                  'code' : source['value'],
                  'display' : source['value'],
                  'userSelected' : False }

    npi_type = {'coding' : [npi_coding],
                'text' : source['value']}

    # Setup the dictionary

    # TODO: Define a full Organization Reference for CMS
    assigner_ref = "{'resourceType': 'Organization','identifier': [{'use': 'official','value': 'Centers for Medicare and Medicaid Services'}], 'name': 'Centers for Medicare and Medicaid Services'}"

    npi = {}

    # Map values across to new dictionary
    npi['use']        = assign_str(source, 'use', "official")
    #npi['type']       = assign_str(source, 'type', str(npi_type))
    npi['type']       = npi_type
    npi['system']     = assign_str(source, 'system', sys_uri)
    npi['value']      = assign_str(source, 'value',)
    npi['period']     = assign_str(source, 'period',)
    #npi['assigner']   = assign_str(source, 'assigner', str(assigner_ref))
    #npi['assigner']   = assigner_ref

    return npi

def organization(source):
    """
    Receive a dict with Organization elements
    :param source:
    :return: org {}

Organization:
{
  "resourceType" : "Organization",
  // from Resource: id, meta, implicitRules, and language
  // from DomainResource: text, contained, extension, and modifierExtension
  "identifier" : [{ Identifier }], // C? Identifies this organization  across multiple systems
  "active" : <boolean>, // Whether the organization's record is still in active use
  "type" : { CodeableConcept }, // Kind of organization
  "name" : "<string>", // C? Name used for the organization
  "telecom" : [{ ContactPoint }], // C? A contact detail for the organization
  "address" : [{ Address }], // C? An address for the organization
  "partOf" : { Reference(Organization) }, // The organization of which this organization forms a part
  "contact" : [{ // Contact for the organization for a certain purpose
    "purpose" : { CodeableConcept }, // The type of contact
    "name" : { HumanName }, // A name associated with the contact
    "telecom" : [{ ContactPoint }], // Contact details (telephone, email, etc)  for a contact
    "address" : { Address } // Visiting or postal addresses for the contact
  }]
}

Organization:Contact
See Contact Definition below

    """

    # Setup dictionary
    org = {}

    # Map values across to new dictionary
    org['resourceType'] = "Organization"
    org['identifier']   = assign_str(source, 'identifier',)
    org['active']       = assign_bool(source, 'active',)
    org['type']         = assign_str(source, 'type',)
    org['name']         = assign_str(source, 'name',)
    org['telecom']      = assign_str(source, 'telecom',)
    org['address']      = assign_str(source, 'address',)
    org['partOf']       = assign_str(source, 'partOf',)
    org['contact']      = assign_str(source, 'contact',)

    return org

def contact(source):
    """
    Create Contact Record from dict
    :param source:
    :return:

{ // Contact for the organization for a certain purpose
    "purpose" : { CodeableConcept }, // The type of contact
    "name" : { HumanName }, // A name associated with the contact
    "telecom" : [{ ContactPoint }], // Contact details (telephone, email, etc)  for a contact
    "address" : { Address } // Visiting or postal addresses for the contact
  }

    """

    # Setup Dictionary
    cn = {}

    # Map values across to new dictionary
    cn['purpose'] = assign_str(source, 'purpose',)
    cn['name']    = assign_str(source, 'name',)
    cn['telecom'] = assign_str(source, 'telecom',)
    cn['address'] = assign_str(source, 'address',)

    return cn


def unique_id(source):
    """
    Build Unique Identifier Section
    :param source:
    :return: npi {}

{
  // from Element: extension
  "use" : "<code>", // usual | official | temp | secondary (If known)
  "type" : { CodeableConcept }, // Description of identifier
  "system" : "<uri>", // The namespace for the identifier
  "value" : "<string>", // The value that is unique
  "period" : { Period }, // Time period when id is/was valid for use
  "assigner" : { Reference(Organization) } // Organization that issued id (may be just text)
}

CodeableConcept:
{
  // from Element: extension
  "coding" : [{ Coding }], // Code defined by a terminology system
  "text" : "<string>" // Plain text representation of the concept
}

CodeableConcept:Coding:
{
  // from Element: extension
  "system" : "<uri>", // Identity of the terminology system
  "version" : "<string>", // Version of the system - if relevant
  "code" : "<code>", // Symbol in syntax defined by the system
  "display" : "<string>", // Representation defined by the system
  "userSelected" : <boolean> // If this coding was chosen directly by the user
}

Identifier:assigner
Identifier:assigner:Reference
{
  // from Element: extension
  "reference" : "<string>", // C? Relative, internal or absolute URL reference
  "display" : "<string>" // Text alternative for the resource
}
Identifier:assigner:Reference:Organization
{
  "resourceType" : "Organization",
  // from Resource: id, meta, implicitRules, and language
  // from DomainResource: text, contained, extension, and modifierExtension
  "identifier" : [{ Identifier }], // C? Identifies this organization  across multiple systems
  "active" : <boolean>, // Whether the organization's record is still in active use
  "type" : { CodeableConcept }, // Kind of organization
  "name" : "<string>", // C? Name used for the organization
  "telecom" : [{ ContactPoint }], // C? A contact detail for the organization
  "address" : [{ Address }], // C? An address for the organization
  "partOf" : { Reference(Organization) }, // The organization of which this organization forms a part
  "contact" : [{ // Contact for the organization for a certain purpose
    "purpose" : { CodeableConcept }, // The type of contact
    "name" : { HumanName }, // A name associated with the contact
    "telecom" : [{ ContactPoint }], // Contact details (telephone, email, etc)  for a contact
    "address" : { Address } // Visiting or postal addresses for the contact
  }]
}

    """

    # URI for Medicare Beneficiary Coding System
    sys_uri = "http://www.MyMedicare.gov"

    # UUID Coding Data
    uuid_coding = {"system" : sys_uri,
                   "code" : source['value'],
                   "display" : source['value'],
                   "userSelected" : False }

    uuid_type = {"coding" : [uuid_coding],
                 "text" : source['value']}

    if settings.DEBUG:
        print("uuid_coding:", uuid_coding, "|", str(uuid_coding))
        print("uuid_type:", uuid_type, "|", str(uuid_type))

    # Setup the dictionary

    # TODO: Define a full Organization Reference for CMS
    assigner_ref = "{'resourceType': 'Organization','identifier': [{'use': 'official','value': 'Centers for Medicare and Medicaid Services'}], 'name': 'Centers for Medicare and Medicaid Services'}"

    uuid = {}

    # Map values across to new dictionary
    uuid['use']        = assign_str(source, 'use', "official")
    #npi['type']       = assign_str(source, 'type', str(npi_type))
    uuid['type']       = uuid_type
    uuid['system']     = assign_str(source, 'system', sys_uri)
    uuid['value']      = assign_str(source, 'value',)
    if 'period' in source:
        uuid['period']     = assign_str(source, 'period',)
    #uuid['assigner']   = assign_str(source, 'assigner', str(assigner_ref))
    #uuid['assigner']   = assigner_ref

    return uuid
