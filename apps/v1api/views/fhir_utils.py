"""
bbofuser
FILE: fhir_utils
Created: 8/21/15 11:19 AM


"""
__author__ = 'Mark Scrimshire:@ekivemark'

from django.conf import settings

def remove_empty_string(source):
    """
    Receive a list of text strings and remove any empty strings from the list
    :param source:
    :return:
    """
    result = []

    for item in source:
        if item:
            result.append(str(item))

    return result

def assign_str(source, key, default=""):
    """
    Get the key value from source
    or return the default
    or return nothing
    :param source:
    :param key:
    :param default:
    :return:
    """
    if key in source:
        if not source[key] == "":
            # if settings.DEBUG:
            #     print("Got Source[key]:", key, ":", source[key])
            if isinstance(source[key], str):
                return source[key]
            if isinstance(source[key], (int, float, complex)):
                return str(source[key])
            elif isinstance(source[key], list):
                ret_val = False
                for i in source[key]:
                    if len(i) > 0:
                        # We have something to return
                        ret_val = True
                        # Otherwise all values are "" or empty


                if ret_val:
                    #print("returning source[key] list:", source[key],
                    #      "with length:", len(source[key]))
                    return source[key]

            elif isinstance(source[key], dict):
                ret_val = False
                for i in source[key]:
                    if len(source[key][i]) > 0:
                        ret_val = True

                if ret_val:
                    # print("returning source[key] dict:", source[key],
                    #      "with length:", len(source[key]))
                    return source[key]

    # We didn't have a source[key] value
    # so...
    if default:
        #print("Returning default:!", default,"!")
        return default
    #print("Returning Nothing")
    return  # Nothing


def build_str(inp, fld, source, delimiter=" "):
    """
    add to the in string with the field in source
    delimiter allows override from space to other character eg. , comma
    :param fld:
    :param source:
    :return:
    """

    if inp == "":
        out = ""
    else:
        out = inp
    if fld in source:
        if isinstance(source[fld], list):
            for item in source[fld]:
                if not item == "":
                    out = out + item + delimiter
        if isinstance(source[fld], str):
            if not source[fld] == "":
                out = out + source[fld] + delimiter

    return out


def assign_bool(source, key, default=""):
    """
    Convert input to boolean response
    :param source:
    :param key:
    :param default:
    :return:
    """

    if key in source:

        if isinstance(source[key], bool):
            return source[key]
        if isinstance((source[key], int)):
            if source[key] == 0:
                return False
            else:
                return True
        if not isinstance(source[key], str):

           raise ValueError('invalid literal for boolean. Not a string.')

        lower_key = source[key].lower()
        valid = {'true': True, 't': True, '1': True,
             'false': False, 'f': False, '0': False,
             }
        if lower_key in valid:
            return valid[lower_key]
        else:
            raise ValueError('invalid literal for boolean: "%s"' % source[key])

    # We didn't have a source[key] value
    # so...
    if default:
        #print("Returning default:!", default,"!")
        return default
    #print("Returning Nothing")
    return  # Nothing
