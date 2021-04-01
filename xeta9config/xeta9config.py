import requests
from requests.auth import HTTPDigestAuth
import json
from datetime import datetime


def x9_fetch_config(url, username, password, filename, subdir):
    now = datetime.now()
    filename = f'{filename}_{now.strftime("%Y%m%d_%H%M%S")}'
    get_files = '/cgi-bin/cgimain.cgi?fn=12'
    post_dl_cfg = '/cgi-bin/cgimain.cgi?fn=14'
    auth = HTTPDigestAuth(username=username, password=password)

    try:
        resp = requests.get(url + get_files, auth=auth)
        if resp.status_code != 200:
            return 1, "bad user/pw"

    except Exception as e:
        print(e)
        return 1, "failed to open url"

    output = json.loads(resp.text)
    running_conf = {}

    for cfgfile in output['cfgfiles']:
        if cfgfile['runningConf'] == 'true':
            print(cfgfile['filename'])
            running_conf = cfgfile

    conf_dl_data = {'downloadfilename': running_conf['filename'], 'downloaddirname': 'cfg'}

    try:
        resp = requests.post(url + post_dl_cfg, data=conf_dl_data, auth=auth)
    except Exception as e:
        print(e)
        return 1, f"failed to download file: {url+post_dl_cfg}"

    try:
        with open(f'{subdir}/{filename}', 'w') as f:
            f.write(resp.text)
    except FileNotFoundError as e:
        return 1, f'unable to write to {subdir}/{filename}'

    return 0, 'Success'


if __name__ == "__main__":
    url = "http://192.168.0.3/"
    username = 'admin'
    password = 'admin'
    filename = 'TEST'
    subdir = '/Downloads/rv55template'

    x9_fetch_config(url, username, password, filename, subdir)
