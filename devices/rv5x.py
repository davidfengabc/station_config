# Tested w/ selenium 3.141.0
# chromedriver 89.0.4389.23
# Chrome Version 89.0.4389.90 (Official Build) (64-bit)
# Ubuntu 20.04 and macOS 11.2.1

# Download chromedriver:  https://chromedriver.storage.googleapis.com/index.html?path=89.0.4389.23/
# code expects chromedriver in the same directory

# tested against RV50 - 4.14.0.014

import tempfile
from xml.dom.minidom import parseString as xml_parse


from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from pathlib import Path
from time import sleep
from datetime import datetime

from devices.stationdevice import StationDevice


class Rv5x(StationDevice):

    # get_config
    # tmp_dir - temporary directory for Chrome to save files to
    # headless - True will prevent a Chrome window from displaying
    # driver_path - path to chromedriver
    # return:  config file contents

    def get_config(self, tmp_dir, headless=False, driver_path='./chromedriver'):
        url = super().get_http_url()

        now = datetime.now()

        dir_path = tmp_dir
        dir_pathc = Path(tmp_dir)
        filename = f'tmp_{now.strftime("%Y%m%d_%H%M%S")}'
        full_path = f'{dir_path}/{filename}.xml'

        if dir_pathc.exists():
            assert(dir_pathc.is_dir()), f'Error: Directory: {dir_path} exists and is not a directory.'
        else:
            dir_pathc.mkdir()

        assert(not Path(full_path).exists()), f'Error: File {full_path} exists'


        options = ChromeOptions()
        options.headless = headless
        options.add_argument('ignore-certificate-errors')
        prefs = {"download.default_directory" : dir_path}
        options.add_experimental_option("prefs", prefs)

        driver = Chrome(executable_path=driver_path, options=options)

        try:
            driver.get(url)

            # wait for status table to load
            WebDriverWait(driver, 60)\
                .until(expected_conditions.visibility_of_element_located((By.ID, 'idStatus')))


            username_txt = driver.find_element(By.ID, "username")
            username_txt.clear()
            username_txt.send_keys(self.username)

            password_txt = driver.find_element(By.ID, "password")
            password_txt.clear()
            password_txt.send_keys(self.password)

            login_btn = driver.find_element(By.NAME, "Login")
            login_btn.click()

            ignored_exceptions = (NoSuchElementException, StaleElementReferenceException,)

            def wrong_pw(drv):
                try:
                    element = drv.find_element_by_id("SM1_Status")
                    return element
                except NoSuchElementException:
                    try:
                        # check visibility of user/pw incorrect message
                        element = drv.find_element_by_id("Lst")
                        if element.value_of_css_property("display") != "none":
                            return 10
                        return False
                    except StaleElementReferenceException:
                        return False
                    except NoSuchElementException:
                        return False



            element = WebDriverWait(driver, 60).until(wrong_pw)

            # wrong_pw returns 10 if wrong password (might need optimization here)
            if element == 10:
                driver.quit()
                assert False, "Error:  Unable to login"

            i = 0
            while True:
                try:
                    template_btn = WebDriverWait(driver, 60, ignored_exceptions=ignored_exceptions) \
                        .until(expected_conditions.element_to_be_clickable((By.ID, 'btn_tpl')))
                    template_btn.click()
                    template_name = driver.find_element(By.ID, "template_name")
                    template_name.send_keys(filename)
                    break
                except TimeoutException:
                    # retry
                    pass
                except Exception as e:
                    i = i + 1
                    if i > 3:
                        driver.quit()
                        raise e
                    # print("Exception sending keys for filename, clicking template again")

            template_dl_btn = driver.find_element(By.NAME, "download_template")
            template_dl_btn.click()


            WebDriverWait(driver, 60)\
                .until(expected_conditions.\
                       visibility_of_element_located((By.CLASS_NAME, 'success')))
        except Exception as e:
            driver.quit()
            raise e


        file_check_iterations = 0
        file_contents = None
        while True:
            if Path(full_path).exists():
                with open(full_path, 'r') as f:
                    file_contents = f.read()
                break
            else:
                assert(file_check_iterations < 10), f'{full_path} failed to download'
                sleep(1)
                file_check_iterations = file_check_iterations + 1

        driver.quit()

        self.config = file_contents
        return file_contents

    def get_fw_version(self):
        if self.config is None:
            with tempfile.TemporaryDirectory() as td:
                self.get_config(headless=True, driver_path='./chromedriver', tmp_dir=td)

        x = xml_parse(self.config)
        template = x.documentElement
        dev_info = template.getElementsByTagName("DeviceInfo")[0]
        for item in dev_info.getElementsByTagName("item"):
            if item.hasAttribute("FwVersion"):
                return item.getAttribute("FwVersion")

        assert False, "unable to determine F/W version"




if __name__ == "__main__":
    ip = "192.168.13.31"
    username = 'user'
    password = 'test'
    http_port = 9191
    http_secure = True
    headless = False

    with tempfile.TemporaryDirectory() as td:
        print(
            Rv5x(ip, username, password, http_port=http_port, http_secure=http_secure,)
                .get_config(headless=headless,
                            driver_path='./chromedriver',
                            tmp_dir=td)
        )
