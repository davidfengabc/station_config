from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from pathlib import Path
from time import sleep
from datetime import datetime


now = datetime.now()

def abort(drv, code, msg):
    print('aborting: ' + msg)
    drv.quit()
    quit(code)


def rv5x_template_download(url, username, password, filename, subdir, headless):
    homedir = Path.home()

    dir_path = str(homedir) + subdir
    dir_pathc = Path(dir_path)
    filename = f'{filename}_{now.strftime("%Y%m%d_%H%M%S")}'

    if dir_pathc.exists():
        if not dir_pathc.is_dir():
            print(f'Directory: {dir_path} exists and is not a directory. I quit')
            return (40, f'Directory: {dir_path} exists and is not a directory. I quit')
    else:
        print(f'Creating directory {dir_path}')
        dir_pathc.mkdir()

    if Path(f'{dir_path}/{filename}.xml').exists():
        return (41, f'File {dir_path}/{filename}.xml exists. I quit')


    options = ChromeOptions()
    options.headless = headless
    options.add_argument('ignore-certificate-errors')
    prefs = {"download.default_directory" : dir_path}
    options.add_experimental_option("prefs", prefs)

    driver = Chrome(executable_path="./chromedriver", options=options)

    try:
        driver.get(url)
    except Exception as e:
        abort(driver, 30, "Error opening url")

    # wait for status table to load
    try:
        WebDriverWait(driver, 60)\
            .until(expected_conditions.visibility_of_element_located((By.ID, 'idStatus')))
    except TimeoutException:
        abort(driver, 15, "Timeout waiting for login page to load")

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
            print("SM1 found")
            return True
        except NoSuchElementException:
            print("SM1 not found")
            try:
                # check visibility of user/pw incorrect message
                element = drv.find_element_by_id("Lst")
                if element.value_of_css_property("display") != "none":
                    abort(driver, 10, "Did not advance past login")
                return False
            except NoSuchElementException:
                return False


    try:
        WebDriverWait(driver, 60).until(wrong_pw)
    except TimeoutException:
        abort(driver, 11, 'Timeout waiting to login:  slow connection or wrong user/pw')

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
            print("Timed out waiting for template button")
        except:
            i = i + 1
            if i > 3:
                abort(driver, 12, "Three tries to open template dialog")
            print("Exception sending keys for filename, clicking template again")

    template_dl_btn = driver.find_element(By.NAME, "download_template")
    template_dl_btn.click()

    try:
        WebDriverWait(driver, 60)\
            .until(expected_conditions.\
                   visibility_of_element_located((By.CLASS_NAME, 'success')))
    except TimeoutException:
        abort(driver, 14, "Timed out waiting for template to generate")

    file_check_iterations = 0
    while True:
        if Path(f'{dir_path}/{filename}.xml').exists():
            break
        else:
            if file_check_iterations >= 10:
                abort(driver, 88, "file failed to download")
            sleep(1)
            file_check_iterations = file_check_iterations + 1

    # clean up needed?  more possibility for errors
    # close_template = driver.find_element(By.CLASS_NAME, "dlg_close")
    # close_template.click()
    #
    # logout = driver.find_element(By.CLASS_NAME, "top_btn")
    # logout.click()

    driver.quit()

    return (0, 'Success!')


if __name__ == "__main__":
    url = "https://192.168.13.31:9191"
    username = 'user'
    password = 'test'
    filename = 'TEST'
    subdir = '/Downloads/rv55template'
    headless = False

    print(rv5x_template_download(url, username, password, filename, subdir, headless))
