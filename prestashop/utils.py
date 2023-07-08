from xml.dom.minidom import getDOMImplementation
from builtins import str
from past.types import basestring
import base64
import tempfile
import mimetypes
import os


def _process(doc, tag, tag_value):
    """
    Generate dom object for tag: tag_value

    @param doc: xml doc
    @param tag: tag
    @param tag_value: tag value
    @return: node or nodelist, be careful
    """
    if isinstance(tag_value, dict) and 'value' in list(tag_value.keys()) == ['value']:
        tag_value = tag_value['value']

    if tag_value is None:
        tag_value = ''

    # Create a new node for simple values
    if (isinstance(tag_value, (float, int)) or
            isinstance(tag_value, basestring)):
        return _process_simple(doc, tag, tag_value)

    # Return a list of nodes with same tag
    if isinstance(tag_value, list):
        # Only care nodelist for list type, drop attrs
        return _process_complex(doc, [(tag, x) for x in tag_value])[0]

    # Create a new node, and insert all subnodes in dict to it
    if isinstance(tag_value, dict):
        if set(tag_value.keys()) == set(['attrs', 'value']):
            node = _process(doc, tag, tag_value['value'])
            attrs = _process_attr(doc, tag_value['attrs'])
            for attr in attrs:
                node.setAttributeNode(attr)
            return node
        else:
            node = doc.createElement(tag)
            nodelist, attrs = _process_complex(doc, list(tag_value.items()))
            for child in nodelist:
                node.appendChild(child)
            for attr in attrs:
                node.setAttributeNode(attr)
            return node

def _process_complex(doc, children):
    """
    Generate multi nodes for list, dict
    @param doc: xml doc
    @param children: tuple of (tag, value)
    @return: nodelist
    """
    nodelist = []
    attrs = []
    for tag, value in children:
        # If tag is attrs, all the nodes should be added to attrs
        # FIXME: Assume all values in attrs are simple values.
        if tag == 'attrs':
            attrs = _process_attr(doc, value)
            continue
        nodes = _process(doc, tag, value)
        if not isinstance(nodes, list):
            nodes = [nodes]
        nodelist += nodes
    return nodelist, attrs

def _process_attr(doc, attr_value):
    """
    Generate attributes of an element

    @param doc: xml doc
    @param attr_value: attribute value
    @return: list of attributes
    """
    attrs = []
    for attr_name, attr_value in list(attr_value.items()):
        if isinstance(attr_value, dict):
            # FIXME: NS is not in the final xml, check why
            attr = doc.createAttributeNS(attr_value.get('xmlns', ''), attr_name)
            attr.nodeValue = attr_value.get('value', '')
        else:
            attr = doc.createAttribute(attr_name)
            attr.nodeValue = attr_value
        attrs.append(attr)
    return attrs

def _process_simple(doc, tag, tag_value):
    """
    Generate node for simple types (int, str)
    @param doc: xml doc
    @param tag: tag
    @param tag_value: tag value
    @return: node
    """
    node = doc.createElement(tag)
    node.appendChild(doc.createTextNode(str(tag_value)))
    return node

def dict2xml(data, encoding='UTF-8'):
    """
    Generate a xml string from a dict
    @param data:     data as a dict
    @param encoding: data encoding, default: UTF-8
    @return: the data as a xml string
    """
    doc = getDOMImplementation().createDocument(None, None, None)
    if len(data) > 1:
        raise Exception('Only one root node allowed')
    root, _ = _process_complex(doc, list(data.items()))
    doc.appendChild(root[0])
    return doc.toxml(encoding)

def base64_to_tmpfile(content,file_name):
    _,ext = os.path.splitext(file_name)
    path = ''
    with  tempfile.NamedTemporaryFile(delete=False,suffix=ext) as tmp:
        tmp.write(base64.b64decode(content))
        path = tmp.name

    return path


