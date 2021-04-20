# tested against airFiber 4x AF4X.V4.1.0


import requests
import re
from devices.stationdevice import StationDevice


class AirFiberX(StationDevice):

    # get_config
    # force: boolean (True/False), force request of config file if True.  If False, and config has already been retrieved
    #   then the config will be returned from memory
    # sets self.config to device configuration
    # return config
    def get_config(self, force=False):
        url = super().get_http_url()

        login_url = url + '/login.cgi'
        login_data = {'username': self.username, 'password': self.password}
        cfg_url = url + '/cfg.cgi'

        s = requests.Session()

        root_resp = s.post(url, data=login_data, verify=False)
        root_resp.raise_for_status()

        login_resp = s.post(login_url, data=login_data, verify=False)
        login_resp.raise_for_status()

        assert(re.search(r"login\.cgi$", login_resp.url) == None), "Unable to login"

        resp = s.get(cfg_url, verify=False)
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

    try:
        dev = AirFiberX(ip_addr, username, password, http_port=http_port, http_secure=http_secure)
        print(dev.get_config(force=True))
    except Exception as e:
        print(e)


