# tested against airFiber 4x AF4X.V4.1.0


import requests
import re
from stationdevice import StationDevice


class AirFiberX(StationDevice):

    # afx_get_config(url, username, password)
    # returns tuple (a, b)
    # if a == 0, then b contains config file data (ready to write to file)
    # if a != 0, then b contains an Exception
    def afx_get_config(self, port=443, secure=True):
        url = super().get_http_url(port, secure)

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
        return resp.text



if __name__ == "__main__":
    ip_addr = '192.168.1.20'
    username = 'ubnt'
    password = 'ubnt'

    try:
        dev = AirFiberX(ip_addr, username, password)
        print(dev.afx_get_config(443, True))
    except Exception as e:
        print(e)


