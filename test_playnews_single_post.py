
import socks
import socket
import requests
import pandas as pd
import numpy as np
import time
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



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

link = "http://mbrlkbtq5jonaqkurjwmxftytyn2ethqvbxfu4rgjbkkknndqwae6byd.onion/"

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

# array of array victims data
data_header = ['victim_name','victim_country','victim_website','post_views','amount_of_data','added_date','publication_date','information','comment','download_links','rar_password']
victims_data = [data_header]


driver = webdriver.Firefox(options=firefox_options)
wait = WebDriverWait(driver, 10)

# Navigate to the website
driver.get(link)
driver.implicitly_wait(20)

# Store the ID of the original window
original_window = driver.current_window_handle

# Check we don't have other windows open already
# assert len(driver.window_handles) == 1

# Simulate clicking on posts (replace with actual selector)
# posts = driver.find_elements(By.CSS_SELECTOR, 'body > table:nth-child(2) > tbody:nth-child(1) > tr:nth-child(3) > th:nth-child(2) > div:nth-child(1)')
# posts = driver.find_element(By.CLASS_NAME, "News")
# print(posts)

#test with 1 sub page
post = driver.find_element(By.CLASS_NAME, "News")
onclick_value = post.get_attribute('onclick')
# print(onclick_value)
# print('click')
post.click()

# Wait for the subpage content to load (you may need to adjust the wait time)
wait.until(EC.number_of_windows_to_be(2))
driver.switch_to.window(driver.window_handles[1])
# wait new tab to load
wait.until(EC.presence_of_element_located((By.CLASS_NAME,'News')))

# extract he information
victim_information = driver.find_element(By.CLASS_NAME,'News')
victim_information_array = victim_information.text.splitlines()
for i in victim_information_array:
    if(len(i)==0):
        victim_information_array.remove(i)
# check the information
# print(len(victim_information_array))
temp_arr = []
for index,info in enumerate(victim_information_array):
    print(index)
    # remove white space infront(left)
    info = info.lstrip()
    #get the data after :
    if info.find(':') != -1:
        info = info[info.find(':') + 1 :]
        info = info.lstrip()
    temp_arr.append(info)
    print(info)
    print('=====')
victims_data.append(temp_arr)

#close current victim tab and go back to main tab
driver.close()
driver.switch_to.window(driver.window_handles[0])
wait.until(EC.number_of_windows_to_be(1))

#can remove i think
time.sleep(1)
driver.quit()

# save the information into excel
df = pd.DataFrame(victims_data[1:],columns=victims_data[0])
excel_file = 'playnews_scrap_data.xlsx'
df.to_excel(excel_file,index=False,sheet_name='victims')

print('*****************')
