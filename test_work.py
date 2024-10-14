import json
import time
import os
import zipfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from loguru import logger
from concurrent.futures import ThreadPoolExecutor

logger.add('log.log')

options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--disable-dev-shm-usage')
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("--enable-javascript")
options.add_argument("--enable-cookies")
options.add_argument('--disable-web-security')
options.add_experimental_option("excludeSwitches", ["enable-automation"])


def create_extension():
    PROXY_HOST = 'ap1.socks.expert'  # your SOCKS5 proxy host
    PROXY_PORT = 44681  # your SOCKS5 proxy port
    PROXY_USER = 'wlseo'  # your SOCKS5 proxy username
    PROXY_PASS = 'QweasdzxC123!'  # your SOCKS5 proxy password

    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = """
    var config = {
        mode: "fixed_servers",
        rules: {
            singleProxy: {
                scheme: "socsk5",
                host: "%s",
                port: parseInt(%s)
            },
            bypassList: ["localhost"]
        }
    };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
        callbackFn,
        {urls: ["<all_urls>"]},
        ['blocking']
    );
    """ % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)
    pluginfile = 'proxy_auth_plugin.zip'
    with zipfile.ZipFile(pluginfile, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    options.add_extension(pluginfile)


def load_credentials(json_file):
    with open(json_file, 'r') as file:
        credentials = json.load(file)
    return credentials


def save_credentials_with_cookies(json_file, new_credential):
    if os.path.exists(json_file):
        with open(json_file, 'r') as file:
            try:
                credentials = json.load(file)
            except json.JSONDecodeError:
                credentials = []
    else:
        credentials = []
    credentials.append(new_credential)

    with open(json_file, 'w') as file:
        json.dump(credentials, file, indent=4)


# Main function where we log in
def log_in(credential):
    driver = webdriver.Chrome(options=options)
    username = credential['login']
    haslo = credential['password']
    driver.get('https://pl-pl.facebook.com/')
    driver.find_element(By.CSS_SELECTOR,
                        'body > div._10.uiLayer._4-hy._3qw > div._59s7._9l2g > div > div > div > div > div:nth-child(3) > div.x1exxf4d.x13fuv20.x178xt8z.x1l90r2v.x1pi30zi.x1swvt13 > div > div:nth-child(2) > div.x1i10hfl.xjbqb8w.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x972fbf.xcfux6l.x1qhh985.xm0m39n.x1ypdohk.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1o1ewxj.x3x9cwd.x1e5q0jg.x13rtm0m.x87ps6o.x1lku1pv.x1a2a7pz.x9f619.x3nfvp2.xdt5ytf.xl56j7k.x1n2onr6.xh8yej3 > div > div.x6s0dn4.x78zum5.xl56j7k.x1608yet.xljgi0e.x1e0frkt > div > span > span').click()
    driver.find_element(By.CSS_SELECTOR, '#email').send_keys(username)
    time.sleep(2)
    driver.find_element(By.CSS_SELECTOR, '#pass').send_keys(haslo)
    time.sleep(2)
    driver.find_element(By.CSS_SELECTOR, '#pass').send_keys(Keys.ENTER)
    # We wait until page url don't change
    WebDriverWait(driver, 20).until(EC.url_changes('https://pl-pl.facebook.com/'))
    if driver.current_url == 'https://www.facebook.com/':
        # If we correctly log in adress changed
        logger.info('We have successfully logged into your account')
        credential['cookies'] = driver.get_cookies()
        save_credentials_with_cookies('successful_logins.json', credential)
        return
    else:
        logger.error("We don't logged .Script changed proxy")
        driver.get(
            'https://api.ltesocks.io/v2/port/reset/395bc511ccd51db8de4b778aa5c011560f8abd6a75e48e33a80ce4911f039576')
        credential['cookies'] = driver.get_cookies()
        save_credentials_with_cookies('successful_logins.json', credential)
        return


if __name__ == '__main__':
    credentials = load_credentials('accounts.json')
    create_extension()
    max_threads = 2
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        executor.map(log_in, credentials)
