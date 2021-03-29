import requests
from requests.auth import HTTPDigestAuth
import json

url = 'http://192.168.0.3/'
get_files = 'cgi-bin/cgimain.cgi?fn=12'
post_dl_cfg = 'cgi-bin/cgimain.cgi?fn=14'
auth = HTTPDigestAuth('admin','admin')

requests.get(url, auth=auth)

resp = requests.get(url, auth=auth)

resp = requests.get(url + get_files, auth=auth)

print(resp.text)

output = json.loads(resp.text)
running_conf = {}

for cfgfile in output['cfgfiles']:
  if cfgfile['runningConf'] == 'true':
    print(cfgfile['filename'])
    running_conf = cfgfile

conf_dl_data = {'downloadfilename': running_conf['filename'], 'downloaddirname': 'cfg'}

resp = requests.post(url + post_dl_cfg, data = conf_dl_data, auth=auth)

print(resp.text)
