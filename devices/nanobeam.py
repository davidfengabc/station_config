# tested against
# Nanobeam AC Gen2 NBE-5AC-Gen2 WA.V8.5.9
# Nanobeam AC Gen2 NBE-5AC-Gen2 WA.V8.7.4

import requests
import re

from devices.stationdevice import StationDevice


class NanobeamAC(StationDevice):

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

        login_url = url + '/api/auth'
        login_data = {'username': self.username, 'password': self.password}

        cfg_url = url + '/cfg.cgi?timestamp=0'

        s = requests.Session()

        resp = s.post(login_url, data=login_data, verify=False)
        resp.raise_for_status()

        resp = s.get(cfg_url, cookies=resp.cookies, verify=False)
        resp.raise_for_status()

        self.config = resp.text

        return resp.text

    def get_fw_version(self):
        if self.config is None:
            self.get_config()

        m = re.search('^##(\S*v\d+\.\d+.\d+$)', self.config, flags=re.MULTILINE)

        assert (m.group(1)), "Unable to determine firmware version"

        return m.group(1)


if __name__ == "__main__":
    ip_addr = '192.168.1.20'
    username = 'ubnt'
    password = 'ubnt'
    http_port = 443
    http_secure = True

    dev = NanobeamAC(ip_addr, username, password, http_port, http_secure)
    try:
        print(dev.get_config())
    except Exception as e:
        print(e)