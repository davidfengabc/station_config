import requests
from requests.auth import HTTPDigestAuth
import json


def x9_get_config(url, username, password):
    get_files = '/cgi-bin/cgimain.cgi?fn=12'
    post_dl_cfg = '/cgi-bin/cgimain.cgi?fn=14'
    auth = HTTPDigestAuth(username=username, password=password)

    try:
        resp = requests.get(url + get_files, auth=auth)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return resp.status_code, e
    except Exception as e:
        return 1, e

    output = json.loads(resp.text)
    running_conf = {}

    for cfgfile in output['cfgfiles']:
        if cfgfile['runningConf'] == 'true':
            running_conf = cfgfile

    conf_dl_data = {'downloadfilename': running_conf['filename'], 'downloaddirname': 'cfg'}

    try:
        resp = requests.post(url + post_dl_cfg, data=conf_dl_data, auth=auth)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return resp.status_code, e
    except Exception as e:
        return 2, e

    return 0, resp.text


if __name__ == "__main__":
    url = "http://192.168.0.3/"
    username = 'admin'
    password = 'admin'

    x9_get_config(url, username, password)
