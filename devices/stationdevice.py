class StationDevice():

    device_fw_version = None

    def __init__(self, ip_addr, username, password):
        self.ip_addr = ip_addr
        self.username = username
        self.password = password

    def get_http_url(self, port=443, secure=True):
        if secure:
            return f'https://{self.ip_addr}:{port}'
        else:
            return f'http://{self.ip_addr}:{port}'

    def ubnt_fw_version(self):
        pass
