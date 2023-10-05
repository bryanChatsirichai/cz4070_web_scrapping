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

# 8_base url
link = "http://basemmnnqwxevlymli5bs36o5ynti55xojzvn246spahniugwkff2pad.onion/"

try:    
    print("=====START=====")
    # Set up Firefox WebDriver with Tor proxy settings
    firefox_options = Options()
    firefox_options.set_preference('network.proxy.type', 1)
    firefox_options.set_preference('network.proxy.socks', '127.0.0.1')
    firefox_options.set_preference('network.proxy.socks_port', 9150)
    firefox_options.set_preference('network.proxy.socks_version', 5)
    firefox_options.set_preference('network.proxy.socks_remote_dns', True)

    # array of array victims data
    data_header = ['victim_name','downloaded','publish','views','company_info','company_link','comment']
    victims_data = []
    victims_data.append(data_header)

    driver = webdriver.Firefox(options=firefox_options)
    wait = WebDriverWait(driver, 90)

    # Navigate to the website
    driver.get(link)
    # wait page loaded
    wait.until(EC.presence_of_element_located((By.CLASS_NAME,'container')))
    print('Page loaded!')

    # multi class in an element
    posts = driver.find_elements(By.CSS_SELECTOR, ".list-group-item.rounded-3.py-3.bg-body-secondary.text-bg-dark.mb-2.position-relative")

    # go through each post in the page
    for index,post in enumerate(posts):
        try:
            print('=====Start Victim Info=====')
            # extract the relevent fields inside each post
            # temp_arr will be a row / entry in the excel
            temp_arr = []
            # victim name
            victim_name = post.find_element(By.CSS_SELECTOR,'.stretched-link').text
            print(victim_name)
            temp_arr.append(victim_name)

            # dates info
            dates_info_div = post.find_element(By.CSS_SELECTOR,'.d-flex.gap-2.small.mt-1.opacity-25')
            '''
            In order
            downloaded:
            publish:
            views:
            '''
            print("Date information")
            for date_info in dates_info_div.find_elements(By.TAG_NAME,'b'):
                data_info_text = date_info.text
                print(data_info_text) 
                temp_arr.append(data_info_text)
                print('-------')
            
            # company info and comment text under div class='small opacity-50'
            '''
            In order
            1st main_info_div -outer_index 0
                company_info:-inner_index 0
                potentially more then 1 line of company info so index will change
                company_link:-inner_index 1
            

            2nd main_info_div comment -outer_index 1
    
            
            any thing else ignore    
            for inner sometimes no p tag, they use div tag etc...

            '''
            print("Company info and comment")              
            company_info = ''
            compan_website = ''
            main_info_divs = post.find_elements(By.CSS_SELECTOR,'.small.opacity-50')
            for outer_index,main_info_div in enumerate(main_info_divs):
                # print(main_info_div.text)
                print('***************')             
                if outer_index == 0:
                    '''
                    [info,...,info,http:...//]
                    '''
                    company_info_arr = main_info_div.text.splitlines()
                    #print(company_info_arr)
                    for str in company_info_arr:
                        if str[0:4] == 'http':
                            compan_website = str
                        else:
                            company_info = company_info + str + '\n'
                    print(company_info)
                    print(compan_website)
                    temp_arr.append(company_info)
                    temp_arr.append(compan_website)
                    
                elif outer_index == 1:
                    commet = main_info_div.text
                    comment_with_no_links = ''
                    # certain comment has http link below could remove them if needed
                    comment_arr = commet.splitlines()
                    for str in comment_arr:
                        if str[0:4] == 'http':
                            pass
                        else:
                            comment_with_no_links = comment_with_no_links + str + '\n'

                    # append comments with links
                    # print(commet)
                    # temp_arr.append(commet)

                    # append comment without links
                    print(comment_with_no_links)
                    temp_arr.append(comment_with_no_links)

                else:
                    break
            
            # add victim data in victims_data array
            victims_data.append(temp_arr)

            print('=====End Victim Info=====')

        # if any error skip this victim entry post
        except Exception as error:
            print('error-2 ',error)
        
        finally:
            pass

except Exception as error:
    print('error-1 ',error)

finally:
    # save the information into excel regardless
    # print(victims_data)
    print(len(victims_data))
    df = pd.DataFrame(victims_data[1:],columns=victims_data[0])
    excel_file = '8base_scrap_data.xlsx'
    df.to_excel(excel_file,index=False,sheet_name='victims')
    print('=====END=====')    
    # Close the WebDriver when done
    driver.quit()