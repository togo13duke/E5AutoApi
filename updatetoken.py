# -*- coding: UTF-8 -*-
import requests as req
import json
import os
from base64 import b64encode
from nacl import encoding, public

app_num=os.getenv('APP_NUM')
if app_num == '':
    app_num='1'
gh_token=os.getenv('GH_TOKEN')
gh_repo=os.getenv('GH_REPO')
Auth=r'token '+gh_token
geturl=r'https://api.github.com/repos/'+gh_repo+r'/actions/secrets/public-key'
key_id='togo13duke'

#公钥获取
def getpublickey(Auth,geturl):
    headers={'Accept': 'application/vnd.github.v3+json','Authorization': Auth}
    html = req.get(geturl,headers=headers)
    jsontxt = json.loads(html.text)
    public_key = jsontxt['key']
    global key_id 
    key_id = jsontxt['key_id']
    return public_key

#微软refresh_token获取
def getmstoken(ms_token):
    headers={'Content-Type':'application/x-www-form-urlencoded'
            }
    data={'grant_type': 'refresh_token',
          'refresh_token': ms_token,
          'client_id':client_id,
          'client_secret':client_secret,
          'redirect_uri':'http://localhost:53682/'
         }
    html = req.post('https://login.microsoftonline.com/common/oauth2/v2.0/token',data=data,headers=headers)
    jsontxt = json.loads(html.text)
    refresh_token = jsontxt['refresh_token']
    access_token = jsontxt['access_token']
    return refresh_token
#是否要保存access，以降低微软token刷新率???

#token加密
def createsecret(public_key,secret_value):
    public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return b64encode(encrypted).decode("utf-8")

#token上传
def setsecret(encrypted_value,key_id,puturl):
    headers={'Accept': 'application/vnd.github.v3+json','Authorization': Auth}
    #data={'encrypted_value': encrypted_value,'key_id': key_id}  ->400error
    data_str=r'{"encrypted_value":"'+encrypted_value+r'",'+r'"key_id":"'+key_id+r'"}'
    putstatus=req.put(puturl,headers=headers,data=data_str)
    return putstatus
    
#调用 
for a in range(1, int(app_num)+1):
    if a==1:
        client_id=os.getenv('CLIENT_ID')
        client_secret=os.getenv('CLIENT_SECRET')
        ms_token=os.getenv('MS_TOKEN')
        puturl=r'https://api.github.com/repos/'+gh_repo+r'/actions/secrets/MS_TOKEN'
        encrypted_value=createsecret(getpublickey(Auth,geturl),getmstoken(ms_token))
        setsecret(encrypted_value,key_id,puturl)
    else:
        client_id=os.getenv('CLIENT_ID_'+str(a))
        client_secret=os.getenv('CLIENT_SECRET_'+str(a))
        ms_token=os.getenv('MS_TOKEN_'+str(a))
        puturl=r'https://api.github.com/repos/'+gh_repo+r'/actions/secrets/MS_TOKEN_'+str(a)
        encrypted_value=createsecret(getpublickey(Auth,geturl),getmstoken(ms_token))
        setsecret(encrypted_value,key_id,puturl)
