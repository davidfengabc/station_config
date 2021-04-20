class StationDevice():

    device_fw_version = None
    config = None

    def __init__(self, ip_addr, username, password, http_port=443, http_secure=True):
        self.ip_addr = ip_addr
        self.username = username
        self.password = password
        self.http_port = http_port
        self.http_secure = http_secure

    def get_http_url(self):
        if self.http_secure:
            return f'https://{self.ip_addr}:{self.http_port}'
        else:
            return f'http://{self.ip_addr}:{self.http_port}'

    def get_fw_version(self):
        pass
