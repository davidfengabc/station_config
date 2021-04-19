# tested against
# Nanobeam AC Gen2 NBE-5AC-Gen2 WA.V8.5.9
# Nanobeam AC Gen2 NBE-5AC-Gen2 WA.V8.7.4

import requests

from stationdevice import StationDevice


class NanobeamAC(StationDevice):
    def nb_get_config(self, port=443, secure=True):
        url = super().get_http_url(port, secure)

        login_url = url + '/api/auth'
        login_data = {'username': self.username, 'password': self.password}

        cfg_url = url + '/cfg.cgi?timestamp=0'

        s = requests.Session()

        resp = s.post(login_url, data=login_data, verify=False)
        resp.raise_for_status()

        resp = s.get(cfg_url, cookies=resp.cookies, verify=False)
        resp.raise_for_status()

        return resp.text


if __name__ == "__main__":
    ip_addr = '192.168.1.20'
    username = 'ubnt'
    password = 'ubnt'

    dev = NanobeamAC(ip_addr, username, password)
    try:
        print(dev.nb_get_config(443, True))
    except Exception as e:
        print(e)