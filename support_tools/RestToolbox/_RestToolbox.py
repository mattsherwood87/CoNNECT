# RestToolbox.py
import httplib2 as _httplib2
import json as _json
from urllib.parse import urlencode as _urlencode

_credentials = None

def SetCredentials(username, password):
    """
    This function sets the login credentials for Orthanc PACS. The username/password combination are stored to the global variable _credentials (tuple).

    :param username: username for Orthanc PACS
    :type username: str

    :param password: password for user `username`
    :type password: str

    """
    
    global _credentials
    _credentials = (username, password)

def _SetupCredentials(h):
    """
    Sets credentials for the HTTP client library object

    :param h: HTTP client library object 
    :type h: httplib2.Http
    """
    global _credentials
    if _credentials != None:
        h.add_credentials(_credentials[0], _credentials[1])

def DoGet(uri, data = {}, interpretAsJson = True):
    """
    Performs an HTTP GET request on the PACS server

    :param uri: URI to the Orthanc PACS server
    :type uri: str

    :param data: supplemental items for the http request, defaults to {}
    :type data: dict, optional

    :param interpretAsJson: _description_, defaults to True
    :type interpretAsJson: bool, optional

    :raises Exception: generic error connecting to PACS server

    :return: results of the HTTP GET request on the PACS server
    :rtype: dict
    """
    d = ''
    if len(data.keys()) > 0:
        d = '?' + _urlencode(data)

    h = _httplib2.Http()
    _SetupCredentials(h)
    resp, content = h.request(uri + d, 'GET')
    if not (resp.status in [ 200 ]):
        raise Exception(resp.status)
    elif not interpretAsJson:
        return content
    else:
        try:
            return _json.loads(content)
        except:
            return content


def _DoPutOrPost(uri, method, data, contentType):
    """
    Performs an HTTP PUT or POST request on the PACS server

    :param uri: URI to the Orthanc PACS server
    :type uri: str

    :param method: httplib2.HTTP request method PUT or POST
    :type method: str

    :param data: information to post to the PACS server
    :type data: str, dict

    :param contentType: header content-type if data is str, "" sets contentType to text/plain
    :type contentType: str

    :raises Exception: generic error connecting to PACS server

    :return: results of the HTTP PUT or POST request on the PACS server
    :rtype: dict
    """
    h = _httplib2.Http()
    _SetupCredentials(h)

    if isinstance(data, str):
        body = data
        if len(contentType) != 0:
            headers = { 'content-type' : contentType }
        else:
            headers = { 'content-type' : 'text/plain' }
    else:
        body = _json.dumps(data)
        headers = { 'content-type' : 'application/json' }
    
    resp, content = h.request(
        uri, method,
        body = body,
        headers = headers)

    if not (resp.status in [ 200, 302 ]):
        raise Exception(resp.status)
    else:
        try:
            return _json.loads(content)
        except:
            return content


def DoDelete(uri):
    """
    Perform an HTTP DELETE on the PACS server

    :param uri: URI to the Orthanc PACS server
    :type uri: str

    :raises Exception: generic error connecting to PACS server

    :return: results of the HTTP PUT or POST request on the PACS server
    :rtype: dict
    """
    h = _httplib2.Http()
    _SetupCredentials(h)
    resp, content = h.request(uri, 'DELETE')

    if not (resp.status in [ 200 ]):
        raise Exception(resp.status)
    else:
        try:
            return _json.loads(content)
        except:
            return content


def DoPut(uri, data = {}, contentType = ''):
    """
    Performs an HTTP PUT request on the PACS server

    :param uri: URI to the Orthanc PACS server
    :type uri: str

    :param data: information to post to the PACS server
    :type data: str, dict

    :param contentType: header content-type if data is str, "" sets contentType to text/plain
    :type contentType: str

    :raises Exception: generic error connecting to PACS server

    :return: results of the HTTP PUT or POST request on the PACS server
    :rtype: dict
    """
    return _DoPutOrPost(uri, 'PUT', data, contentType)


def DoPost(uri, data = {}, contentType = ''):
    """
    Performs an HTTP POST request on the PACS server

    :param uri: URI to the Orthanc PACS server
    :type uri: str

    :param data: information to post to the PACS server
    :type data: str, dict

    :param contentType: header content-type if data is str, "" sets contentType to text/plain
    :type contentType: str

    :raises Exception: generic error connecting to PACS server

    :return: results of the HTTP PUT or POST request on the PACS server
    :rtype: dict
    """
    return _DoPutOrPost(uri, 'POST', data, contentType)