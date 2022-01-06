# implemented per instructions from Nanometrics support for Etna, 
# but so far only tested against Centaur
# tested against Centaur 4.5.22


import requests
from stationdevice import StationDevice
from paramiko import SSHClient, WarningPolicy
import json
from invoke.exceptions import UnexpectedExit


class Nanometrics(StationDevice):

    # get_config
    # per Nanometrics support:  config.ttl contains the latest committed config, but not any applied but uncommitted changes
    # if the default config is committed, then config.ttl will not exist
    def get_config(self, user, password, port=22):
        client = SSHClient()
        client.set_missing_host_key_policy(WarningPolicy)
        try:
            client.connect(hostname = self.get_ip_addr(), username = user, password=password, port=port)
        except:
            raise

        stdin, stdout, stderr = client.exec_command('cat /etc/nanometrics/config/current/config.ttl')
        
        return stdout.read()


    def get_fw_version(self):
        url = super().get_http_url()

        api_url = url + '/api/v1/instruments/soh'
        headers = {'Accept-Encoding': None}
        
        #s = requests.Session()
        
        resp = requests.get(api_url, headers=headers)
        resp.raise_for_status()

        api_dict = json.loads(resp.text)
        dev_key = list(api_dict)[0]

        return api_dict[dev_key]['systemSoftwareVersion']['value']
        




if __name__ == "__main__":
    ip_addr = ''
    username = ''
    password = ''
    http_port = 80
    http_secure = False

    try:
        dev = Nanometrics(ip_addr, username, password, http_port=http_port, http_secure=http_secure)
        try:
            print(dev.get_config(username, password))
        except Exception as e:
            print(e)

        print(dev.get_fw_version())
    except Exception as e:
        print(e)


