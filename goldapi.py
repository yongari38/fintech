import hmac, hashlib
import codecs
import requests

#Generate Hash Key

#for i in range(20140629, 20190629)
#string_in_string = "Shepherd {} is on duty.".format(shepherd)

data1 = '{"dataHeader":{"udId" : "단말기 고유ID(UDID)",     "subChannel" : "채널구분(앱 구분용)",     "deviceModel" : "단말기 모델명",     "deviceOs" : "단말기OS명",     "carrier" : "캐리어명",     "connectionType" : "연결정보",     "appName" : "앱이름",     "appVersion" : "앱버전",     "scrNo" : "화면번호",     "scrName" : "화면명"   },   "dataBody" : { 	"기준년월일":"20170323", 	"적용회차":"" 	}  }'
key1 = 'l7xxd3d3817c16c24fa1a64ea99085bab7c5'
data = data1.encode()
key = key1.encode()

hmac_code = hmac.new(key=key, msg=data, digestmod=hashlib.sha256)
hmac_hexdigest = hmac_code.hexdigest()

hmac_base64 = codecs.encode(codecs.decode(hmac_hexdigest, 'hex'), 'base64').decode()

print('HMAC base64: ', hmac_base64)
#1cWwjbgMx+dzTgi78s4TmPxTvH8O6nz3JrMnH74qlpU=

# defining the api-endpoint  
API_ENDPOINT = "https://dev-openapi.kbstar.com:8443/hackathon/getGoldPrice"
  
# your API key here 
API_KEY = key1
  
# your source code here 
#source_code = 
''' 
print("Hello, world!") 
a = 1 
b = 2 
print(a + b) 
'''

headers = {'apikey': key1, 'hskey': hmac_base64.strip(), 'Content-Type': 'application/json', 'charset':'utf-8'}

# data to be sent to api 
data = data1.encode('utf-8')
# sending post request and saving response as response object 
r = requests.post(url = API_ENDPOINT, data = data, headers=headers) 

# extracting response text  
pastebin_url = r.text 
print("The pastebin URL is:%s"%pastebin_url) 

