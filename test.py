#%%
from prestashop import Prestashop, Format

api = Prestashop(
    url = "https://prestademo.aisysacademy.com",
    api_key="4MV3E41MFR7E3N9VNJE2W5EHS83E2EMI",
    default_lang=1,
    debug=True,
    data_format=Format.JSON,
)

#%%
api._exec(resource='taxes',method='GET',display="[id,name]",_filter="[id]=[1|5]",sort="[name_DESC]",limit=3)
# %%
api.unlink('taxes',[5,9])
# %%


data = {'tax':{
            'id' : '1',
            'rate' : 3.000,
        }
        }
data['tax']['name'] = api._lang({'name' : 'sdf jjf'})
api.write('taxes',data)
# %%
