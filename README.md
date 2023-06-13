# Prestashop
Prestashop is a library for Python to interact with the PrestaShop's Web Service API.

Learn more about the Prestashop Web Service from the [Official Documentation](https://devdocs.prestashop-project.org/1.7/webservice/)

## Installation

using pip :

`pip install prestashop`

the git repo:

```bash
git clone https://github.com/AiSyS-Next/prestashop 
cd prestashop
pip install . 
```

## Usage

### init api

for json data format

```python
from prestashop import Prestashop, Format

api = Prestashop(
    url = "https://myprestashop.com",
    api_key="4MV3E41MFR7E3N9VNJE2W5EHS83E2EMI",
    default_lang=1,
    debug=True,
    data_format=Format.JSON,
)
```

for xml data format

```python
from prestashop import Prestashop, Format

api = Prestashop(
    url = "https://myprestashop.com",
    api_key="4MV3E41MFR7E3N9VNJE2W5EHS83E2EMI",
    default_lang=1,
    debug=True,
    data_format=Format.XML,
)
```

### Test API

test if you webservice run

```python
api.ping()
```

### Create Record

```python
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

rec = api.create('taxes',data)
```
#### Add product image

```python
file_name = 'sample.jpg'

api.create_binary('images/products/30',file=file_name , _type='image')
```



### Update record

```python
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
```
### Remove record

```python
api.unlink('taxes',str(rec['id']))
```

remove many records at once

```python
api.unlink('taxes',[2,4,5])
```

### Read

```python
import pprint
result = api.read('taxes','2',display='[id,name]')

pprint(result)
```

### Search

```python
 # search the first 3 taxes with 5 in the name 
import pprint
recs = api.search('taxes',_filter='[name]=%[5]%',limit='3')

for rec in recs:
    pprint(rec)


# search with id = 3 or id = 5

recs = api.search('taxes' ,_filter='[id]=[3 | 5]')
```


## Copyright and License

prestashop is copyright (c) 2023 Aymen Jemi (AISYSNEXT)

prestashop is free software: you can redistribute it and/or modify
it under the terms of the GPLv3 General Public License as
published by the Free Software Foundation, version 3 of
the License .
