# -*- coding: utf-8 -*-

"""
Prestashop is a Python library to interact with PrestaShop's Web Service API.

:copyright: (c) 2023 Aymen Jemi
:copyright: (c) 2023 AISYSNEXT
:license: GPLv3, see LICENSE for more details
"""
from enum import Enum
import mimetypes

from http.client import HTTPConnection
from xml.etree import ElementTree
from xml.parsers.expat import ExpatError

from requests import Session
from requests.models import PreparedRequest

from .exceptions import PrestaShopError,PrestaShopAuthenticationError
from .utils import dict2xml

class Format(Enum):
    """Data types return (JSON,XML)

    Args:
        Enum (int): 1 => JSON, 2 => XML
    """
    JSON = 1
    XML = 2


class Prestashop():
    """ Interact with Prestashop webservice API, using JSON and XML for message

    Raises:
        PrestaShopAuthenticationError: Authentication error.
        when: wrong api key or api key not exist.
        PrestaShopError: Generic PrestaShop WebServices error .

    Example:

    from prestashop import Prestashop, Format

    api = Prestashop(
        url = "https://myprestashop.com",
        api_key="4MV3E41MFR7E3N9VNJE2W5EHS83E2EMI",
        default_lang=1,
        debug=True,
        data_format=Format.JSON,
    )

    api.ping()

    data = {
        'tax':{
            'rate' : 3.000,
            'active': '1',
            'name' : {
                'language' : {
                    'attrs' : {'id' : '1'},
                    'value' : '3% tax'
                }
            }
        }
    }

    # create tax record
    rec = api.create('taxes',data)

    # update the same tax record

    update_data = {
        'tax':{
            'id' : str(rec['id']),
            'rate' : 3.000,
            'active': '1',
            'name' : {
                'language' : {
                    'attrs' : {'id' : '1'},
                    'value' : '3% tax'
                }
            }
        }
    }

    update_rec = api.write('taxes',update_data)

    # remove this tax
    api.unlink('taxes',str(rec['id']))

    # search the first 3 taxes with 5 in the name 
    import pprint
    recs = api.search('taxes',_filter='[name]=%[5]%',limit='3')

    for rec in recs:
        pprint(rec)


    """
    api_key = ''
    url = ''
    client = None
    debug = False
    lang = None
    data_format = Format.JSON

    def __init__(self,url:str, api_key:str,data_format=Format.JSON,default_lang:str=None,session:Session=None,debug:bool=False) -> None:
        """ Prestashop class

        Args:
            url (str): url of your shop (https://myprestashop.com)
            api_key (str): api key generate from prestashop 
            https://devdocs.prestashop-project.org/1.7/webservice/tutorials/creating-access/
            data_format (Format, optional): default data format (Format.JSON or Format.XML). Defaults to Format.JSON.
            default_lang (str, optional): default language id (1). Defaults to None.
            session (Session, optional): requests.Session() for old sessing. Defaults to None.
            debug (bool, optional): activate debug mode. Defaults to False.
        """
        
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
            self.client = Session()
        else:
            self.client = session

        if not self.client.auth:
            self.client.auth = (self.api_key , '')

    def ping(self):
        """ Test if webservice work perfectly else raise error

        Returns:
            bool: Result of ping test
        """
        response = self.client.request(
            method='HEAD',
            url=self.url
        )
        content = {
            "errors": [
                {
                    "code": 0,
                    "message": "Ping not working "
                }
            ]
        }

        return self._error(response.status_code,content)

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

    def _exec(self,resource,_id=None,ids=None, method='GET',data=None,_headers=None,display='full',_filter=None,sort=None,limit=None):
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
            if _headers:
                headers = _headers
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
        if _headers:
            headers = _headers
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
    
    def _get_content_type(self, filename):
        """Retrieve filename mimetype.

        :param filename: file name.
        :return: mimetype.
        """
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
    
    def _encode_multipart_formdata(self, files):
        """Encode files to an http multipart/form-data.

        :param files: a sequence of (type, filename, value)
            elements for data to be uploaded as files.
        :return: headers and body.
        """
        BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
        CRLF = b'\r\n'
        L = []
        for (key, filename, value) in files:
            L.append('--' + BOUNDARY)
            L.append(
                'Content-Disposition: form-data; \
                    name="%s"; filename="%s"' % (key, filename))
            L.append('Content-Type: %s' % self._get_content_type(filename))
            L.append('')
            L.append(value)
        L.append('--' + BOUNDARY + '--')
        L.append('')
        L = map(lambda l: l if isinstance(l, bytes) else l.encode('utf-8'), L)
        body = CRLF.join(L)
        headers = {
            'Content-Type': 'multipart/form-data; boundary=%s' % BOUNDARY
        }
        return headers, body
    
    def search(self,resource,display='full',_filter=None,sort=None,limit=None):
        """search from prestashop with options, for more details check the official doc \n
        https://devdocs.prestashop-project.org/1.7/webservice/tutorials/advanced-use/additional-list-parameters/

        Args:
            resource (str): resource to search ( taxes,customers,products ...)
            display (str, optional): display parameter (full | [field1,field2]). Defaults to 'full'.
            _filter (str, optional): filter parameter ([id]=[1|5] , [name]=[app]%). Defaults to None.
            sort (str, optional): sort parameter ([{fieldname}_{ASC|DESC}] ,[lastname_ASC,id_DESC] ). Defaults to None.
            limit (str, optional): limit parameter ('offset,limit' , '9,2' , '5'). Defaults to None.

        Returns:
            dict : result of search
        """
        return self._exec(resource=resource,method='GET',display=display,_filter=_filter,sort=sort,limit=limit)

    def read(self,resource:str,_id:str=None,display:str='full',sort:str=None,limit:str=None) -> dict:
        """get one or more result from prestashop with options .
        for more details check the official doc \n
        https://devdocs.prestashop-project.org/1.7/webservice/tutorials/advanced-use/additional-list-parameters/

        Args:
            resource (str): resource to search ( taxes,customers,products ...)
            _id (str, optional): the id if you wan one record. Defaults to None.
            display (str, optional): display parameter (full | [field1,field2]). Defaults to 'full'.
            sort (str, optional): sort parameter ([{fieldname}_{ASC|DESC}] ,[lastname_ASC,id_DESC] ). Defaults to None.
            limit (str, optional): limit parameter ('offset,limit' , '9,2' , '5'). Defaults to None.

        Returns:
            dict : result of get request
        """
        return self._exec(resource,_id,'GET',display=display,sort=sort,limit=limit)

    def write(self,resource:str,data:dict):
        """update record from prestashop

        Args:
            resource (str): resource to search ( taxes,customers,products ...)
            data (dict): data in dict format (
                    data = {
                        'tax':{
                            'id': 2,
                            'rate' : 3.000,
                            'active': '1',
                            'name' : {
                                'language' : {
                                    'attrs' : {'id' : '1'},
                                    'value' : '3% tax'
                                }
                            }
                        }
                    }
        )

        Returns:
            dict: the updated record.
        """
        data  = {'prestashop' : data}
        _data = dict2xml(data)
        return self._exec(resource=resource,method='PUT',data=_data,display=None)

    def unlink(self,resource:str,ids:list[int]):
        """remove one or multiple records

        Args:
            resource (str): resource to search ( taxes,customers,products ...)
            ids (list[int] | tuple(int) | str): list|tuple|str of ids to remove. ([1,3,9] , [9] , '3')

        Returns:
            boolean: result of remove (True,False)
        """
        if isinstance(ids , (tuple,list)):
            resource_ids = ','.join([str(id) for id in ids])
            resource_ids = '[{}]'.format(resource_ids)
            return self._exec(resource=resource ,ids=resource_ids, method='DELETE' , display=None)
            
        else:
            return self._exec(resource=resource ,ids=ids, method='DELETE' , display=None)
    
    def create(self,resource:str,data:dict=None,files=None):
        """create record 

        Args:
            resource (str): resource to search ( taxes,customers,products ...).
            files (list[tuple], optional):  a sequence of (type, filename, value). Defaults to None.
            data (dict, optional): data (dict): data in dict format (
                    data = {
                        'tax':{
                            'rate' : 3.000,
                            'active': '1',
                            'name' : {
                                'language' : {
                                    'attrs' : {'id' : '1'},
                                    'value' : '3% tax'
                                }
                            }
                        }
                    }
        ). Defaults to None.

            

        Raises:
            PrestaShopError: raise when data and files is None.

        Returns:
            dict: record added.
        """

        if files is not None:
            headers , data = self._encode_multipart_formdata(files)
            return self._exec(resource=resource, method='POST' , data=data,_headers=headers,display=None)
        elif data is None:
            raise PrestaShopError('Undefined data.',404)
        data  = {'prestashop' : data}
        _data = dict2xml(data)
        return self._exec(resource=resource,data=_data,method='POST',display=None)


