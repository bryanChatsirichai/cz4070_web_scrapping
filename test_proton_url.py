
import socks
import socket
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

import time

def get_tor_session():
    session = requests.session()
    # Tor uses the 9050 port as the default socks port
    session.proxies = {'http':  'socks5h://127.0.0.1:9150',
                       'https': 'socks5h://127.0.0.1:9150'}
    return session

# Make a request through the Tor connection
# IP visible through Tor
session = get_tor_session()
# print(session.get("http://httpbin.org/ip").text)
# # Above should print an IP different than your public IP

# # Following prints your normal public IP
# print(requests.get("http://httpbin.org/ip").text)

# link = "https://httpbin.org/user-agent"
link = "https://protonmailrmez3lotccipshtkleegetolb73fuirgj7r4o4vfu7ozyd.onion/"
# response = session.get(link)
# soup = BeautifulSoup(response.text, 'html.parser')
#print(soup.prettify())
print("================")

# Set up Firefox WebDriver with Tor proxy settings
firefox_options = Options()
# firefox_options.add_argument('--proxy-server=socks5h://localhost:9150')  # Use Tor as a proxy
firefox_options.set_preference('network.proxy.type', 1)
firefox_options.set_preference('network.proxy.socks', '127.0.0.1')
firefox_options.set_preference('network.proxy.socks_port', 9150)
firefox_options.set_preference('network.proxy.socks_version', 5)
firefox_options.set_preference('network.proxy.socks_remote_dns', True)

driver = webdriver.Firefox(options=firefox_options)
# wait = WebDriverWait(driver, 10)

# Navigate to the website
driver.get(link)
driver.implicitly_wait(20)

# Store the ID of the original window
original_window = driver.current_window_handle

print("original url")
print(driver.current_url)
post = driver.find_element(By.CLASS_NAME, "capitalize")
post.click()


# open new tab
driver.execute_script("window.open('');")
print(driver.window_handles)
# switch to new tab
# driver.switch_to.window(driver.window_handles[1])

# hard code testing
new_tab_url = 'https://protonmailrmez3lotccipshtkleegetolb73fuirgj7r4o4vfu7ozyd.onion/mail'
driver.get(new_tab_url)

driver.implicitly_wait(10)

# Get the HTML of the subpage
subpage_html = driver.page_source
print("new url")
print(driver.current_url)
# Parse the subpage HTML with BeautifulSoup
# subpage_soup = BeautifulSoup(subpage_html, 'html.parser')
# print(subpage_soup.prettify())
print('*****************')
driver.quit()