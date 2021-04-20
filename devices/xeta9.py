# tested against
# Xeta9-EL              xw-EBX.5.2.18d
# XETA9-22DMLFC         xw-EBX.5.2.18e

import requests
import re
import json

from requests.auth import HTTPDigestAuth

from devices.stationdevice import StationDevice


class Xeta9(StationDevice):

    # get_config
    # force: boolean (True/False), force request of config file if True.  If False, and config has already been retrieved
    #   then the config will be returned from memory
    # sets self.config to device configuration
    # return config
    def get_config(self, force=False):
        if force is True:
            self.config = None

        if self.config is not None:
            return self.config

        url = super().get_http_url()

        get_files = '/cgi-bin/cgimain.cgi?fn=12'
        post_dl_cfg = '/cgi-bin/cgimain.cgi?fn=14'
        auth = requests.auth.HTTPDigestAuth(username=self.username, password=self.password)

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

        self.config = resp.text

        return resp.text

    def get_fw_version(self):
        if self.config is None:
            self.get_config()

        m = re.search("//\s+Firmware\s+:\s+(.+)", self.config)
        assert(m.group(1)), "Unable to determine firmware version"
        return m.group(1)


if __name__ == "__main__":
    ip_addr = '192.168.0.3'
    username = 'admin'
    password = 'admin'
    http_port = 443
    http_secure = True

    dev = Xeta9(ip_addr, username, password, http_port, http_secure)

    try:
        print(dev.get_config())
    except Exception as e:
        print(e)
