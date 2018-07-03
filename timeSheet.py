import csv
from selenium import webdriver
from time import sleep

# load csv file
def load_csv(file):
    with open(file) as fp:
        return list(csv.reader(fp))

def create_update_list(csvInput, timeSheetCdTag):

    startTimeTag = "__xmlview1--0WorkingHoursS-inner"
    endTimeTag = "__xmlview1--0WorkingHoursE-inner"
    
    """
    timeSheetCdTag1 = "__input9-__clone0-inner"
    timeSheetHourTag1 = "__input11-__clone0-inner"
    ApproverTag1 = "__input18-__clone0-inner"

    timeSheetCdTag2 = "__input43-__clone1-inner"
    timeSheetHourTag2 = "__input45-__clone1-inner"
    """
    updateList = []
    
    print(csvInput)

    # create update list
    for i in range(1,len(csvInput)):
        for j in range(1,6):

            # start time
            if (csvInput[i][0]=='start'):
                tagName = startTimeTag[:12] + str(j-1) + startTimeTag[13:]
                updateList.append([tagName, csvInput[i][j]])
            # end time
            elif (csvInput[i][0]=='end'):
                tagName = endTimeTag[:12] + str(j-1) + endTimeTag[13:]
                updateList.append([tagName, csvInput[i][j]])

            # charge
            else:
                for k in range(0, len(timeSheetCdTag)):
                    # temporary set
                    tagTemp = timeSheetCdTag[k]
                    inputNum = int(tagTemp[7:len(tagTemp)-15])
                    # searchTag
                    tagName = tagTemp[:7] + str(inputNum+2+j-1) + tagTemp[len(tagTemp)-15:]
                    updateList.append([tagName, csvInput[i][j]])
                    # Approver
                    if (j==5):
                        tagName = tagTemp[:7] + str(inputNum+2+j-1+3) + tagTemp[len(tagTemp)-15:]
                        updateList.append([tagName, csvInput[i][j+1]])

    return updateList

# main
# import CSV
csv_list = load_csv('TimeSheet.csv')

# open Browser
chrome_driver_path = "C:/Users/hiadachi/auto_python/chromedriver.exe"

browser = webdriver.Chrome(executable_path=chrome_driver_path)

#待機時間の指定
browser.implicitly_wait(30)

#URL Open
browser.get('https://timesheet_url')

# ログイン画面発生時の処理
# loginfmtを検索し、キーを送信
emailElem = browser.find_element_by_name('loginfmt')
emailElem.send_keys('your_username')

submitButton = browser.find_element_by_id('idSIButton9')
submitButton.click()

"""
# パスワード入力画面発生時
try:
    passwordElem = browser.find_element_by_id('passwordInput')
    passwordElem.send_keys('your_password')
    submitButton2 = browser.find_element_by_id('submitButton')
    submitButton2.click()
except:
    pass

# パスワード保持画面発生時
try:
    submitButton3 = browser.find_element_by_id('idBtn_Back')
    submitButton3.click()
except:
    pass
"""

#ログイン後のパネル選択画面
# sleep(5)
timeSheetWeekly = browser.find_element_by_id('__tile3')
timeSheetWeekly.click()

# 当該ValueのIDを取得
# sleep(5)
timeSheetCdTag = []
for i in range (3, len(csv_list)):
    timeSheetCdTag.append(browser.find_element_by_xpath("//input[@value='" + csv_list[i][0] + "']").get_attribute("id"))

# timeSheetCdTag = ["__input9-__clone0-inner", "__input43-__clone1-inner"]

updateList = create_update_list(csv_list, timeSheetCdTag)
#updateList = [['__xmlview1--0WorkingHoursS-inner', '09:00'], ['__xmlview1--1WorkingHoursS-inner', '09:00'], ['__xmlview1--2WorkingHoursS-inner', '09:00'], ['__xmlview1--3WorkingHoursS-inner', '09:00'], ['__xmlview1--4WorkingHoursS-inner', '09:00'], ['__xmlview1--0WorkingHoursE-inner', '18:00'], ['__xmlview1--1WorkingHoursE-inner', '18:00'], ['__xmlview1--2WorkingHoursE-inner', '18:00'], ['__xmlview1--3WorkingHoursE-inner', '18:00'], ['__xmlview1--4WorkingHoursE-inner', '18:00'], ['__input11-__clone0-inner', '8'], ['__input45-__clone1-inner', '8'], ['__input12-__clone0-inner', '8'], ['__input46-__clone1-inner', '8'], ['__input13-__clone0-inner', '8'], ['__input47-__clone1-inner', '8'], ['__input14-__clone0-inner', '8'], ['__input48-__clone1-inner', '8'], ['__input15-__clone0-inner', '8'], ['__input18-__clone0-inner', '50009086'], ['__input49-__clone1-inner', '8'], ['__input52-__clone1-inner', '50009086']]

# チェックボックスにチェックを入れる
# id="__box0-CbBg"
for i in range(0, 5):
    checkbox = browser.find_element_by_id("__box" + str(i) +"-CbBg")
    checkbox.click()

# updateListの値を検索して入力
for i in range(0,len(updateList)):
    elem =  browser.find_element_by_id(updateList[i][0])
    elem.send_keys(updateList[i][1])
