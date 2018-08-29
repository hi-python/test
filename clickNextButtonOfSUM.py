import configparser
import datetime, sys
import urllib.request, html2text
import hashlib
import base64
from selenium import webdriver
from time import sleep

# read the config file
config = configparser.ConfigParser()
config.read('../settings.ini')

#  store the config to variables
current_num = int(config['input']['current_num'])
max_num = int(config['input']['max_num'])
sum_url = config['input']['url']
user = config['input']['user']
password = config['input']['password']

user_and_password = user + ":" + password
basic_user_and_password = base64.b64encode(user_and_password.encode('utf-8'))
sum_url_auth = sum_url[:7] + user + ":" + password + "@" + sum_url[7:]
next_button_id = "_slui_actn_btn_next_btntpe_slp.action.SUBMIT"

# get url content and return it with text format
def getContent(sum_url):
    try:
        # BASIC authentication
        req = urllib.request.Request(sum_url,headers={"Authorization": "Basic " + basic_user_and_password.decode('utf-8')})
        res = urllib.request.urlopen(req).read().decode("utf-8","ignore")
        urltext = html2text.html2text(res)
    except:
        print("Can't get the content of the url : {}".format(sum_url) )
    else:
        return urltext

# create Hash value and return hash value
def createHash(urldata):
    urldata = urldata.encode("utf-8")
    md5hash = hashlib.md5()
    md5hash.update(urldata)
    return md5hash.hexdigest()

# search anc click a next button
def clickNext(sum_url_auth, current_num):
    chrome_driver_path = "../driver/chromedriver.exe"
    browser = webdriver.Chrome(executable_path=chrome_driver_path)
    # wait time to open the content
    browser.implicitly_wait(20)
    
    # Open the browser
    browser.get(sum_url_auth)
    
    # search next button
    date = datetime.datetime.now().strftime( "%d.%m.%Y %H:%M:%S" )
    try:
        submitButton = browser.find_element_by_id(next_button_id)
    except:
        print("{}: Can't find a next button".format(date))
    
    # push next button, take a screenshot and count up the current_num
    else:
        submitButton.click()
        print("{}: Next button was clicked".format(date))
        browser.save_screenshot("../images/" + "{0:%Y%m%d-%H%M%S}.png".format(datetime.datetime.now()) )
        current_num += 1
        
        # you can input a value like below if you need it.
        # emailElem.send_keys('hiadachi')
    finally:
        sleep(10)
        browser.close()
        return current_num

## Main
date = datetime.datetime.now().strftime( "%d.%m.%Y %H:%M:%S" )

# exit if the current_num reach the max_num
if current_num >= max_num:
    print('{}: Skip execution since it reached the max num'.format(date))
    sys.exit(0)
else:
    pass

# get tha hash value of URL
urldata = getContent(sum_url)
urlhash = createHash(urldata)

# compare hash
if(urlhash == config['2nd execution']['hash']):
    print("{}: nothing has changed, skip to execute".format(date))
else:
    print("{}: content has changed".format(date))
    # Open URL and search next button
    current_num = clickNext(sum_url_auth, current_num)

# update config file
old_date = config['2nd execution']['date']
old_urlhash = config['2nd execution']['hash']
config['input']['current_num'] = str(current_num)
config['1st execution'] = {'date': old_date,
                           'hash': old_urlhash}
config['2nd execution'] = {'date': date,
                           'hash': urlhash}
with open('../settings.ini','w') as file:
    config.write(file)