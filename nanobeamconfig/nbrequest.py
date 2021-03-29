import requests

def get_config(url, username, password, file_out):
  login_url = url + 'api/auth'
  login_data = {'username':username, 'password':password}
  
  cfg_url = url + 'cfg.cgi?timestamp=0'
  
  r = requests.post(login_url, data = login_data, verify=False)
  
  r = requests.get(cfg_url,cookies=r.cookies,verify=False)
  
  with open (file_out, 'w') as file:
    file.write(r.text)

station1 = {'name':'BLAH', 'username':'admin', 'password':'AdminAdmin1', 'url':'https://192.168.1.20/'}
station2 = {'name':'HAHA', 'username':'admin', 'password':'AdminAdmin1', 'url':'https://192.168.1.21/'}
#url = 'https://192.168.1.21/'
#username = 'admin'
#password = 'AdminAdmin1'
#file_out = station + '.cfg'
stations = [station1, station2]

for station in stations:
  get_config(station['url'], station['username'], station['password'], station['name'] + '.cfg')

