# tested against airFiber 4x AF4X.V4.1.0


import requests
import re


class LoginError(Exception):
    def __init__(self, message="Unable to login"):
        self.message = message
        super().__init__(self.message)


# afx_get_config(url, username, password)
# returns tuple (a, b)
# if a == 0, then b contains config file data (ready to write to file)
# if a != 0, then b contains an Exception
def afx_get_config(url, username, password):
    login_url = url + '/login.cgi'
    login_data = {'username': username, 'password': password}
    cfg_url = url + '/cfg.cgi'

    s = requests.Session()

    root_resp = s.post(url, data=login_data, verify=False)
    root_resp.raise_for_status()

    login_resp = s.post(login_url, data=login_data, verify=False)
    login_resp.raise_for_status()
    if re.search(r"login\.cgi$", login_resp.url) != None:
        raise LoginError

    resp = s.get(cfg_url, verify=False)
    resp.raise_for_status()
    return resp.text



if __name__ == "__main__":
    url = "https://192.168.1.20"
    username = 'ubnt'
    password = 'ubnt'

    try:
        print(afx_get_config(url, username, password))
    except Exception as e:
        print(e)


