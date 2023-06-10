# -*- coding: utf-8 -*-

"""
Prestashop is a Python library to interact with PrestaShop's Web Service API.

:copyright: (c) 2023 Aymen Jemi
:copyright: (c) 2023 AISYSNEXT
:license: GPLv3, see LICENSE for more details
"""
from enum import Enum
import warnings

from http.client import HTTPConnection
from xml.etree import ElementTree
from xml.parsers.expat import ExpatError

import requests
from requests.models import PreparedRequest


from .exceptions import PrestaShopError,PrestaShopAuthenticationError
from .utils import dict2xml

class Format(Enum):
    JSON = 1
    XML = 2


class Prestashop():

    api_key = ''
    url = ''
    client = None
    debug = False
    lang = None
    data_format = Format.JSON

    def __init__(self,url, api_key,data_format=Format.JSON,default_lang=None,session=None,debug=False) -> None:
        self.url = url
        self.api_key = api_key
        self.debug = debug
        self.lang = default_lang
        self.data_format = data_format


        # fix url 
        if not self.url.endswith('/'):
            self.url += '/'
        if not self.url.endswith('/api/'):
            self.url += 'api/'


        if session is None:
            self.client = requests.Session()
        else:
            self.client = session

        if not self.client.auth:
            self.client.auth = (self.api_key , '')

    # test if you have the access right you need
    def _ping(self):
        pass

    def _error(self,status_code,content):
        message_by_code = {204: 'No content',
                           400: 'Bad Request',
                           401: 'Unauthorized',
                           404: 'Not Found',
                           405: 'Method Not Allowed',
                           500: 'Internal Server Error',
                           }
        if status_code in (200, 201):
            return True
        elif status_code == 401:
            # the content is empty for auth errors
            raise PrestaShopAuthenticationError(
                message_by_code[status_code],
                status_code
            )
        elif status_code in message_by_code:
            ps_error_code, ps_error_msg = self._parse_error(content)
            raise PrestaShopError(
                message_by_code[status_code],
                status_code,
                ps_error_msg=ps_error_msg,
                ps_error_code=ps_error_code,
            )
        else:
            ps_error_code, ps_error_msg = self._parse_error(content)
            raise PrestaShopError(
                'Unknown error',
                status_code,
                ps_error_msg=ps_error_msg,
                ps_error_code=ps_error_code,
            )
        
    def _parse_error(self,content):
        if self.data_format == Format.JSON:
            code = content['errors'][0]['code']
            msg = content['errors'][0]['message']
            return (code, msg)

        error_answer = self._parse(content)
        if isinstance(error_answer, dict):
            error_content = (error_answer
                             .get('prestashop', {})
                             .get('errors', {})
                             .get('error', {})
                             )
            if isinstance(error_content, list):
                error_content = error_content[0]
            code = error_content.get('code')
            message = error_content.get('message')
        elif isinstance(error_answer, type(ElementTree.Element(None))):
            error = error_answer.find('errors/error')
            code = error.find('code').text
            message = error.find('message').text
        return (code, message)
    
    def _prepare(self,url,params):
        req = PreparedRequest()
        req.prepare_url(url , params)
        return req.url

    def _exec(self,resource,_id=None,ids=None, method='GET',data=None,display='full',_filter=None,sort=None,limit=None):
        params = {}

        if self.lang:
            params.update({'language' : self.lang})

        if self.data_format == Format.JSON:
            params.update({'io_format' : 'JSON' , 'output_format' : 'JSON'})
        
        if display:
            params.update({'display' : display})

        if _filter:
            lst = _filter.split('=',1)
            key = 'filter{}'.format(lst[0])
            params.update({key : lst[1]})
        if sort:
            params.update({'sort' : sort})
        if limit:
            params.update({'limit' : limit})

        if _id:
            _url = '{}{}/{}'.format(self.url,resource,_id)
        else:
            _url = '{}{}'.format(self.url,resource)
        
        if ids:
            params.update({'id' : ids})

        url = self._prepare(_url,params)

        if self.debug:
            HTTPConnection.debuglevel = 1


        if self.data_format == Format.JSON:
            headers = {'Content-Type': 'application/json'}
            response = self.client.request(
                method=method,
                url=url,
                data=data,
                headers=headers
            )

            if response.content == b'' and response.status_code == 200:
                return True
            self._error(response.status_code,response.json())
            return response.json()
        
        headers = {'Content-Type': 'text/xml'}
        response = self.client.request(
                method=method,
                url=url,
                data=data,
                headers=headers
        )

        if response.content == b'' and response.status_code == 200:
            return True
        
        self._error(response.status_code,response.content)
        return self._parse(response.content)

    def _parse(self, content):
        """Parse the response of the webservice.

        :param content: response from the webservice
        :return: an ElementTree of the content
        """
        if not content:
            raise PrestaShopError('HTTP response is empty')

        try:
            parsed_content = ElementTree.fromstring(content)
        except ExpatError as err:
            raise PrestaShopError(
                'HTTP XML response is not parsable : %s' % (err,)
            )
        except ElementTree.ParseError as e:
            raise PrestaShopError(
                'HTTP XML response is not parsable : %s. %s' %
                (e, content[:512])
            )

        return parsed_content
    
    def search(self,resource,display='full',_filter=None,sort=None,limit=None):
        return self._exec(resource=resource,method='GET',display=display,_filter=_filter,sort=sort,limit=limit)

    def read(self,resource,_id=None,display='full'):
        return self._exec(resource,_id,'GET',display=display)

    def write(self,resource,data):
        data  = {'prestashop' : data}
        _data = dict2xml(data)
        return self._exec(resource=resource,method='PUT',data=_data,display=None)

    def unlink(self,resource,ids):
        if isinstance(ids , (tuple,list)):
            resource_ids = ','.join([str(id) for id in ids])
            resource_ids = '[{}]'.format(resource_ids)
            return self._exec(resource=resource ,ids=resource_ids, method='DELETE' , display=None)
            
        else:
            return self._exec(resource=resource ,ids=ids, method='DELETE' , display=None)
    
    def create(self,resource,data,files=None):
        pass


