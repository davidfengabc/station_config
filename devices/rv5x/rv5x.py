# Tested w/ selenium 3.141.0
# chromedriver 89.0.4389.23
# Chrome Version 89.0.4389.90 (Official Build) (64-bit)
# Ubuntu 20.04 and macOS 11.2.1

# Download chromedriver:  https://chromedriver.storage.googleapis.com/index.html?path=89.0.4389.23/
# code expects chromedriver in the same directory

# tested against RV50 - 4.14.0.014

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


# rv5x_get_config
# dir - default download directory (set by Chromedriver)
# headless - True will prevent a Chrome window from displaying
# note:  browser will save a copy to dir  timestamp added to filename
# return:  (a, b) tuple
# if a == 0, b is the contents of the template file
# if a != 0, b is an error msg


def rv5x_get_config(url, username, password, filename, dir, headless, driver_path='./chromedriver'):
    now = datetime.now()

    dir_path = dir
    dir_pathc = Path(dir_path)
    filename = f'{filename}_{now.strftime("%Y%m%d_%H%M%S")}'

    if dir_pathc.exists():
        assert(dir_pathc.is_dir()), f'Error: Directory: {dir_path} exists and is not a directory.'
    else:
        dir_pathc.mkdir()

    assert(not Path(f'{dir_path}/{filename}.xml').exists()), f'Error: File {dir_path}/{filename}.xml exists'


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
        username_txt.send_keys(username)

        password_txt = driver.find_element(By.ID, "password")
        password_txt.clear()
        password_txt.send_keys(password)

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
        if Path(f'{dir_path}/{filename}.xml').exists():
            with open(f'{dir_path}/{filename}.xml', 'r') as f:
                file_contents = f.read()
            break
        else:
            assert(file_check_iterations >= 10), 'file failed to download'
            sleep(1)
            file_check_iterations = file_check_iterations + 1

    driver.quit()

    return file_contents


if __name__ == "__main__":
    url = "https://192.168.13.31:9191"
    username = 'user'
    password = 'test'
    filename = 'TEST'
    subdir = '/Downloads/rv5x'
    headless = False

    print(rv5x_get_config(url, username, password, filename, subdir, headless)[1])
