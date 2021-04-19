# tested against
# Nanobeam AC Gen2 NBE-5AC-Gen2 WA.V8.5.9
# Nanobeam AC Gen2 NBE-5AC-Gen2 WA.V8.7.4

import requests


def nb_get_config(url, username, password):
    login_url = url + '/api/auth'
    login_data = {'username': username, 'password': password}

    cfg_url = url + '/cfg.cgi?timestamp=0'

    s = requests.Session()

    try:
        resp = s.post(login_url, data=login_data, verify=False)
        resp.raise_for_status()

        resp = s.get(cfg_url, cookies=resp.cookies, verify=False)
        resp.raise_for_status()

        return 0, resp.text
    except requests.exceptions.HTTPError as e:
        return resp.status_code, e
    except Exception as e:
        return 2, e


if __name__ == "__main__":
    url = "https://192.168.1.20"
    username = 'ubnt'
    password = 'ubnt'

    code, e = nb_get_config(url, username, password)

    print(f'{code} {e}')