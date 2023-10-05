
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
    # Tor uses the 9050 or 9150 port as the default socks port need check system
    session.proxies = {'http':  'socks5h://127.0.0.1:9150',
                       'https': 'socks5h://127.0.0.1:9150'}
    return session

# Make a request through the Tor connection
# IP visible through Tor
session = get_tor_session()

# just to check session
# print(session.get("http://httpbin.org/ip").text)
# # Above should print an IP different than your public IP
# # Following prints your normal public IP
# print(requests.get("http://httpbin.org/ip").text)

# start from page 1
link = "http://mbrlkbtq5jonaqkurjwmxftytyn2ethqvbxfu4rgjbkkknndqwae6byd.onion/index.php?page={}"

try:    
    print("=====START=====")
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
    victims_data = []
    victims_data.append(data_header)

    driver = webdriver.Firefox(options=firefox_options)
    wait = WebDriverWait(driver, 90)

    # explore all the pages, hard code unless page number change then need adjust range
    page_range = range(1,16)
    for page in page_range :
        # print(link.format(page))
        # Navigate to the website
        driver.get(link.format(page))
        # wait page loaded
        wait.until(EC.presence_of_element_located((By.CLASS_NAME,'News')))
        print("current page {}".format(page))
        #print(driver.current_url)

        # Store the ID of the original window
        # original_window = driver.current_window_handle
        #test with multiple posts in a page
        posts = driver.find_elements(By.CLASS_NAME, "News")

        # Simulate clicking on posts (replace with actual selector)
        # open new tab for every victim post in a page
        for post in posts:
            #try every post in a page
            try:
                #click to open new
                post.click()
                # Wait for the subpage content to load (you may need to adjust the wait time)
                wait.until(EC.number_of_windows_to_be(2))
                driver.switch_to.window(driver.window_handles[1])
                # wait new tab to load
                wait.until(EC.presence_of_element_located((By.CLASS_NAME,'News')))

                # extract the information
                victim_information = driver.find_element(By.CLASS_NAME,'News')
                # split the text from elements into array
                victim_information_array = victim_information.text.splitlines()
                # clean up the text
                for i in victim_information_array:
                    if(len(i)==0):
                        victim_information_array.remove(i)
                # check the information
                # print(len(victim_information_array))
                print('--------Start Victim Info--------')
                # temp_arr will be a row / entry in the excel
                temp_arr = []
                # try web scrab every new tab opened
                try:
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
                    #check temp_arr correct amount of items
                    if(len(temp_arr)==len(data_header)):
                        victims_data.append(temp_arr)
                    print('--------End Victim Info--------')
                    # # close current victim tab and go back to main tab
                    # driver.close()
                    # driver.switch_to.window(driver.window_handles[0])
                    # wait.until(EC.number_of_windows_to_be(1))
                    # # maybe can remove
                    # time.sleep(1)
                except Exception as error:
                    print('error-3 ',error)
                finally:
                    # close current victim tab and go back to main tab
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    wait.until(EC.number_of_windows_to_be(1))
                    # maybe can remove
                    time.sleep(1)
            except Exception as error:
                print('error-2 ',error)
            finally:
                pass
        print("End of Page {}".format(page))

except Exception as error:
    print('error-1 ',error)

finally:
    # save the information into excel regardless
    # print(victims_data)
    print(len(victims_data))
    df = pd.DataFrame(victims_data[1:],columns=victims_data[0])
    excel_file = 'playnews_scrap_data.xlsx'
    df.to_excel(excel_file,index=False,sheet_name='victims')
    print('=====END=====')    
    # Close the WebDriver when done
    driver.quit()