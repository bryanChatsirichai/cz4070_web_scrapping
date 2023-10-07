
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

# start from main page
link = "http://noescapemsqxvizdxyl7f7rmg5cdjwp33pg2wpmiaaibilb4btwzttad.onion/archive"

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
    data_header = ['victim_name','victim_location','victim_website','victim_hotline','victim_email','victim_background','attack_information','total_data','publish_date']
    victims_data = []
    victims_data.append(data_header)

    driver = webdriver.Firefox(options=firefox_options)
    wait = WebDriverWait(driver, 90)

    # Navigate to the website
    driver.get(link)
    # wait page loaded
    wait.until(EC.presence_of_element_located((By.ID,'app')))
    #page has some loading animation
    time.sleep(20)
    # print(driver.current_url)

    # Store the ID of the original window
    # original_window = driver.current_window_handle
    #test with multiple posts in a page
    posts_outer_div = driver.find_element(By.CSS_SELECTOR, ".row.mx-0")
    # print('get posts')
    posts_divs  = posts_outer_div.find_elements(By.CSS_SELECTOR, ".col-xxl-3.col-xl-4.col-md-6.px-2.mb-3.d-flex")
    # Simulate clicking on posts (replace with actual selector)
    # open new tab for every victim post in a page
    # print(posts_divs)
    for post_div in posts_divs:
        #try every post in a page
        try:
            read_more_link = post_div.find_element(By.CSS_SELECTOR,'.btn.btn-sm.btn-primary.h2.mb-0').get_attribute('href')
            # print(read_more_link)
            # open new tab
            driver.execute_script("window.open('');")
            # Wait for the subpage content to load (you may need to adjust the wait time)
            wait.until(EC.number_of_windows_to_be(2))
            driver.switch_to.window(driver.window_handles[1])
            driver.get(read_more_link)
            # wait new tab to load
            wait.until(EC.presence_of_element_located((By.ID,'app')))
            # page has some loading animation
            time.sleep(20)
            
            # temp_arr will be a row / entry in the excel
            temp_arr = []
            # try web scrab every new tab opened
            try:    
                print('--------Start Victim Info--------')
                
                # get from the top 'header'
                publish_date_div = driver.find_element(By.CSS_SELECTOR,'.me-4.d-flex.align-items-center')
                publish_date = publish_date_div.find_element(By.TAG_NAME,'small').text
                # print(publish_date)
                print('***************')

                # 'victim_name','victim_location','victim_website','victim_hotline','victim_email'
                company_basic_info_div = driver.find_element(By.CSS_SELECTOR,'.bg-cover.rounded-2.p-4.mb-3')
                # print(company_basic_info_div.text)
                arr1 = company_basic_info_div.text.splitlines()
                # print(arr1)
                arr1_length = len(arr1)

                # minimum 'victim_name','victim_location','victim_website' should always be available
                victim_name = arr1[0]
                victim_location = arr1[1]   
                victim_website = arr1[2]

                #'victim_hotline','victim_email' may or may not be available
                if arr1_length == 4:
                    victim_hotline = arr1[3]
                    victim_email = 'NA'
                elif arr1_length == 5:
                    victim_hotline = arr1[3]
                    victim_email = arr1[4]
                else:
                    victim_hotline = "NA"
                    victim_email = "NA"
                
                temp_arr.append(victim_name)
                temp_arr.append(victim_location)
                temp_arr.append(victim_website)
                temp_arr.append(victim_hotline)
                temp_arr.append(victim_email)

                print('***************')
                company_main_info_div = driver.find_element(By.CSS_SELECTOR,'.bg-cover.rounded-2.p-4.mb-3.fs-5.text-justify')
                # print(company_main_info_div.text)
                arr2 = company_main_info_div.text.splitlines()
                # print(arr2)
                # arr2[0] should always be about company background
                victim_background = arr2[0]
                attack_information = ''
                for index,str in enumerate(arr2):
                    if index == 0:
                        continue
                    else:
                        attack_information = attack_information + str + '\n'
                # print(attack_information)
                temp_arr.append(victim_background)
                temp_arr.append(attack_information)
                print('***************')

                #'total_data','publish_date'
                total_data_div = driver.find_element(By.CSS_SELECTOR,'.text-danger.h2.mb-0.fs-5')
                total_data = total_data_div.find_element(By.CLASS_NAME,'fw-bold').text
                temp_arr.append(total_data)
                temp_arr.append(publish_date)
                print('--------End Victim Info--------')
            except Exception as error:
                print('error-3 ',error)
            finally:
                # close current victim tab and go back to main tab
                print(temp_arr)
                print(len(temp_arr))
                victims_data.append(temp_arr)
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                wait.until(EC.number_of_windows_to_be(1))
                # maybe can remove
                time.sleep(1)
        except Exception as error:
            print('error-2 ',error)
        finally:
            pass

except Exception as error:
    print('error-1 ',error)

finally:
    # save the information into excel regardless
    # print(victims_data)
    # print(len(victims_data))
    df = pd.DataFrame(victims_data[1:],columns=victims_data[0])
    excel_file = 'noescape_scrap_archive_data.xlsx'
    df.to_excel(excel_file,index=False,sheet_name='victims')
    print('=====END=====')    
    # Close the WebDriver when done
    driver.quit()