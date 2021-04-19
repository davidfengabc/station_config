import requests
from requests.auth import HTTPDigestAuth
import json

from stationdevice import StationDevice


class Xeta9(StationDevice):
    def x9_get_config(self, port=443, secure=True):
        url = super().get_http_url(port, secure)

        get_files = '/cgi-bin/cgimain.cgi?fn=12'
        post_dl_cfg = '/cgi-bin/cgimain.cgi?fn=14'
        auth = HTTPDigestAuth(username=username, password=password)

        resp = requests.get(url + get_files, auth=auth)
        resp.raise_for_status()

        output = json.loads(resp.text)
        running_conf = {}

        for cfgfile in output['cfgfiles']:
            if cfgfile['runningConf'] == 'true':
                running_conf = cfgfile

        conf_dl_data = {'downloadfilename': running_conf['filename'], 'downloaddirname': 'cfg'}


        resp = requests.post(url + post_dl_cfg, data=conf_dl_data, auth=auth)
        resp.raise_for_status()

        return resp.text


if __name__ == "__main__":
    ip_addr = '192.168.0.3'
    username = 'admin'
    password = 'admin'

    dev = Xeta9(ip_addr, username, password)

    try:
        print(dev.x9_get_config(port=80, secure=False))
    except Exception as e:
        print(e)
