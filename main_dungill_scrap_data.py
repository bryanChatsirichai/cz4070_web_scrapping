
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
link = "http://p66slxmtum2ox4jpayco6ai3qfehd5urgrs4oximjzklxcol264driqd.onion/"

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
    data_header = ['victim_name','publication_date','victim_website','victim_information','attack_information']
    victims_data = []
    victims_data.append(data_header)

    driver = webdriver.Firefox(options=firefox_options)
    wait = WebDriverWait(driver, 90)

    driver.get(link)
    # wait page loaded
    wait.until(EC.presence_of_element_located((By.CLASS_NAME,'elem_list')))

    # multiple post === custom-container in a page
    posts = driver.find_elements(By.CLASS_NAME, "custom-container")
    # print('posts ',posts)
    # Simulate clicking on posts (replace with actual selector)
    # open new tab for every victim post in a page
    for post in posts:
        #try every post in a page
        try:
            # get the link
            a_tag = post.find_element(By.TAG_NAME,'a')
            #click to open new
            sub_page_id = a_tag.get_attribute('href')
            #print(sub_page_id)
            
            # open new tab
            driver.execute_script("window.open('');")

            # Wait for the subpage content to load (you may need to adjust the wait time)
            wait.until(EC.number_of_windows_to_be(2))
            driver.switch_to.window(driver.window_handles[1])
            driver.get(sub_page_id)
            
            # wait new tab to load
            wait.until(EC.presence_of_element_located((By.TAG_NAME,'main')))
            print('--------Start Victim Info--------')
            # temp_arr will be a row / entry in the excel
            temp_arr = []
            # try web scrab every new tab opened
            try:
                # scrap new tab ... 
                section = driver.find_element(By.TAG_NAME, "section")
                main_div = section.find_element(By.CLASS_NAME,"custom-container")
                # print(main_div.text)
                divs = main_div.find_elements(By.TAG_NAME,'div')
                
                # first two divs give 
                # 'victim_name','publication_date','victim_website','victim_information'
                # hard code - as no time
                print('-----Get company information-----')
                for index,div in enumerate(divs):
                    # print(div.text)
                    if index == 0:
                        # company name and publication_date
                        # print(div.text)
                        arr1 = div.text.splitlines()
                        victim_name = arr1[0]
                        publication_date = arr1[1]
                        temp_arr.append(victim_name)
                        temp_arr.append(publication_date)
                        # print('************')
                    elif index == 4:
                        # 'victim_website','victim_information'
                        # print(div.text)
                        
                        arr2 = div.text.splitlines()
                        print(arr2)

                        # append all links to related to company
                        # victim_websites = ''
                        # for str in arr2:
                        #     if str[0:4] == 'http':
                        #         print(str)
                        #         victim_websites = victim_websites + str  + '\n'
                        # else:
                        #     pass
                        # print('-------')
                        # print(victim_websites)
                        # temp_arr.append(victim_websites)

                        # only the suppose main website
                        victim_website = arr2[1]
                        temp_arr.append(victim_website)

                        start_victim_information_index = 0
                        for index,str in enumerate(arr2):
                            if index == 0:
                                continue
                            elif str[0:4] == 'http':
                                continue
                            else:
                                start_victim_information_index = index
                                break
                        str_arr = arr2[start_victim_information_index::]
                        victim_information = ' '.join(str_arr)
                        temp_arr.append(victim_information)
                        # print('************')
                    elif index > 5:
                        break
                attack_information_pre_tag = main_div.find_element(By.TAG_NAME,'pre')
                attack_information = attack_information_pre_tag.text
                temp_arr.append(attack_information)
            except Exception as error:
                    print('error-2 ',error)
            finally:
                # close current victim tab and go back to main tab
                print(temp_arr)
                victims_data.append(temp_arr)
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                wait.until(EC.number_of_windows_to_be(1))
                # maybe can remove
                time.sleep(1)
            
            print('--------End Victim Info--------')


        except Exception as error:
            print('error-1 ',error)

finally:
    # save the information into excel regardless
    # print(victims_data)
    # print(len(victims_data))
    df = pd.DataFrame(victims_data[1:],columns=victims_data[0])
    excel_file = 'dungill_scrap_data.xlsx'
    df.to_excel(excel_file,index=False,sheet_name='victims')
    print('=====END=====')    
    # Close the WebDriver when done
    driver.quit()