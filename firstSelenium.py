import tkinter as tk
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from pynput import keyboard
from tkinter import messagebox
import re
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
import numpy

## 編譯說明
#1 
# 請記得調整 dateBtn = findHTMLDomElement((By.CSS_SELECTOR, 'li[data-perfday="20230924"] button'))
# 這邊要根據實際的演唱會日期去調整
#2 
# 請記得調整creditCradSelectorOption.select_by_visible_text("FOREIGN_VISA")
# 這邊要根據使用的信用卡去調整

def patch_asscalar(a):
    return a.item()

setattr(numpy, "asscalar", patch_asscalar)


## 按鍵控制區塊if key.char == '1':
altPresse = False
f1Pressed = False
f2Pressed = False
f3Pressed = False
f4Pressed = False

# 创建一个顶层窗口
root = tk.Tk()
root.withdraw()  # 隱藏主視窗

def rgbStringToRGB(rgbString):
    match = re.match(r'rgba\((\d+),\s*(\d+),\s*(\d+),\s*(\d+(\.\d+)?)\)', rgbString)
    if match:
        r, g, b, a = map(int, match.groups()[:4])  # 將浮點數轉換為整數
        return r, g, b
    else:
        return None
    
def rgbPercent(rgb1=(190, 168, 134), rgb2=(190, 168, 128)):
    try:
        # 定義兩個 RGB 顏色
        color1_rgb = sRGBColor(rgb1[0], rgb1[1], rgb1[2])
        color2_rgb = sRGBColor(rgb2[0], rgb2[1], rgb2[2])

        # 轉換 RGB 顏色到 CIELab 顏色空間
        color1_lab = convert_color(color1_rgb, LabColor)
        color2_lab = convert_color(color2_rgb, LabColor)

        # 計算 CIEDE2000 色差
        delta_e = delta_e_cie2000(color1_lab, color2_lab)
        return delta_e    
    except Exception as e:
        print(f"Error calculating delta_e for rgb1={rgb1} and rgb2={rgb2}. Error: {str(e)}")
        return None

    # 定義兩個 RGB 顏色
    color1_rgb = sRGBColor(red=rgb1[0], green=rgb1[1], blue=rgb1[2])
    color2_rgb = sRGBColor(red=rgb2[0], green=rgb2[1], blue=rgb2[2])

    # 轉換 RGB 顏色到 CIELab 顏色空間
    color1_lab = convert_color(color1_rgb, LabColor)
    color2_lab = convert_color(color2_rgb, LabColor)

    # 計算 CIEDE2000 色差
    delta_e = delta_e_cie2000(color1_lab, color2_lab)
    return delta_e    

def rgb_to_hex(rgb_string):
    # 使用正則表達式來解析RGB或RGBA格式的顏色
    matches = re.search(r"rgba?\((\d+),\s*(\d+),\s*(\d+)", rgb_string)
    if matches:
        r = int(matches.group(1))
        g = int(matches.group(2))
        b = int(matches.group(3))
        return "#{:02x}{:02x}{:02x}".format(r, g, b)
    else:
        return None
    
def hex_to_rgb(hex_value):
    hex_value = hex_value.lstrip('#')  # 移除開頭的'#'字符，如果存在的話
    length = len(hex_value)
    # 將縮短的形式(例如 #ABC)轉換成標準形式(#AABBCC)
    if length == 3:
        hex_value = ''.join([char*2 for char in hex_value])
        
    r = int(hex_value[0:2], 16)
    g = int(hex_value[2:4], 16)
    b = int(hex_value[4:6], 16)
    
    return r, g, b    

def keyboardPressFunction(key):
    global altPresse,f1Pressed,f2Pressed,f3Pressed,f4Pressed,mainWindowHandle
    if key == keyboard.Key.alt_l and altPresse == False:
        # print('按了ALT')
        altPresse = True
    elif key == keyboard.KeyCode.from_char('1') and f1Pressed == False:
        f1Pressed = True
        if altPresse == True:
            print('按了ALT+1')
            melonTikectClickOrderButton() # 自動點預定
    elif key == keyboard.KeyCode.from_char('2') and f2Pressed == False:
        f2Pressed = True
        if altPresse == True:
            print('按了ALT+2')
            melonTikectBuyTicketInfo(2) # 自動輸入購票資訊
    elif key == keyboard.KeyCode.from_char('3') and f3Pressed == False:
        f3Pressed = True
        if altPresse == True:
            print('按了ALT+3，切回主視窗')
            driver.switch_to.window(mainWindowHandle)
    elif key == keyboard.KeyCode.from_char('4') and f4Pressed == False:
        f4Pressed = True
        if altPresse == True:
            print('按了ALT+4')        
            messagebox.showinfo('123','你關閉了程式')
            driver.quit()
            root.destroy()
            exit()   
                 

def keyboardReleaseFunction(key):
    global altPresse,f1Pressed,f2Pressed,f3Pressed,f4Pressed
    if key == keyboard.Key.alt_l and altPresse == True:
        # print('鬆開CTRL')
        altPresse = False 
    elif key == keyboard.KeyCode.from_char('1') and f1Pressed == True:
        f1Pressed =False
    elif key == keyboard.KeyCode.from_char('2') and f2Pressed == True: 
        f2Pressed =False
    elif key == keyboard.KeyCode.from_char('3') and f3Pressed == True: 
        f3Pressed =False        
    elif key == keyboard.KeyCode.from_char('4') and f4Pressed == True: 
        f4Pressed =False            


def startKeyboardListener():
    # 创建一个键盘监听器
    keyboard_listener = keyboard.Listener(on_press=keyboardPressFunction,on_release=keyboardReleaseFunction)
    # 启动监听器
    keyboard_listener.start()
    # keyboard_listener.join()
    # 监听器在后台线程运行，这里没有使用join，而是通过定时事件来保持程序运行
    root.after(1000, startKeyboardListener)  # 1秒重新启动监听器

def melonTikectClickOrderButton():
    global mainWindowHandle
    try:
        # 設置最長等待時間（例如10秒），直到該元素出現
        reservationBtn = findHTMLDomElement((By.CLASS_NAME, 'reservationBtn'),3600)
        dateTypeList = findHTMLDomElement((By.CLASS_NAME, 'type_list'))
        ## 特別注意要改這邊的時間單位
        dateBtn = findHTMLDomElement((By.CSS_SELECTOR, 'li[data-perfday="20230924"] button'))
        ## 特別注意要改這邊的時間單位
        
        # 此時元素已確認存在
        # print("Element exists.")
        # 將日期改為條列式
        dateTypeList[0].click()
        # 點選日期
        dateBtn[0].click()
        # 點選時間
        timeBtn = findHTMLDomElement((By.CSS_SELECTOR, 'li.item_time.first'))
        timeBtn[0].click()
        # 點選預定
        reservationBtn[0].click()
        # 跳到彈出視窗
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
        for handle in driver.window_handles:
            if handle != mainWindowHandle:
                # print('Switch to second window.')
                driver.switch_to.window(handle)
                break
    except TimeoutException:
        print("Element not found.")

# version 1:自動輸入資訊 2:自動挑選最佳位子，並自動輸入資訊
def melonTikectBuyTicketInfo(version=1):
    try:
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
        for handle in driver.window_handles:
            if handle != mainWindowHandle:
                # print('Switch to second window.')
                driver.switch_to.window(handle)
                break
        driver.switch_to.frame("oneStopFrame")

        if version == 2:
            # 先蒐集座位標籤，但我們按照右側的順序來定義最佳到最差的位置
            # 正常來說座位優先順序 VIP => R => S => A
            # 有兩種售票方式 divGradeSummary和partSeatGrade
            # divGradeSummary代表要展開才能選座位
            # partSeatGrade直接選右邊的座位
            seatList = findHTMLDomElement((By.CSS_SELECTOR,'tbody#partSeatGrade th.seat_color em.seat_color'),0.1,0.1)
            if seatList is None:
                fininshJob = False
                seatList = findHTMLDomElement((By.ID,'divGradeSummary'),0.1,0.1)
                # 定位該tbody內的所有tr元素
                rows = seatList[0].find_elements(By.TAG_NAME,"tr")
                groupedRows = [rows[i:i+2] for i in range(0, len(rows), 2)]

                for group in groupedRows:
                    if fininshJob == True:
                        break
                    colorDiffCache = {}
                    # 展開座位列表
                    group[0].click()
                    # 取得座位顏色
                    seatColor = group[0].find_element(By.TAG_NAME,'em').value_of_css_property('background-color')
                    seatColorRgb = rgbStringToRGB(seatColor)
                    # 測試是否可以讀到第二個狀態列表，還是需要重新讀取
                    ticketLiBtnList = group[1].find_elements(By.TAG_NAME,"li")
                    for ticketLiBtn in ticketLiBtnList:
                        if fininshJob == True:
                            break
                        # 檢查是否有座位
                        ticketNum = ticketLiBtn.find_element(By.TAG_NAME,'strong')
                        if ticketNum.text != '0':
                            # 有座位，點擊
                            ticketLiBtn.click()
                            # 展開詳細座位列表，並搜尋座位色碼，進行購票
                            ticketBlock = findHTMLDomElement((By.ID,'ez_canvas'))
                            rectElements = ticketBlock[0].find_elements(By.TAG_NAME,'rect')

                            for rect in rectElements:
                                rectColor = rect.get_attribute('fill')

                                # fill可能沒有設定任何顏色，或是設定為none
                                if rectColor == 'none':
                                    continue

                                if rectColor == '#DDDDDD':
                                    continue

                                # 若色碼相同，則存快取字典中取出，不再重複比對
                                if rectColor in colorDiffCache:
                                    colorDiffPercent = colorDiffCache[rectColor]
                                else:
                                    r, g, b = hex_to_rgb(rectColor)
                                    colorDiffPercent = rgbPercent((r, g, b), seatColorRgb)
                                    if colorDiffPercent is None:
                                        continue
                                    colorDiffCache[rectColor] = colorDiffPercent

                                # print('#1')
                                # print(rgb_to_hex(seatColor),rectColor)
                                # print((r, g, b), seatColorRgb)
                                # print(colorDiffPercent)
                                # print('#2')
                                # 比對顏色是否小於20，超過20視為不同顏色，因為melon的可選座位色碼會浮動調整
                                if colorDiffPercent < 0.2:
                                    rect.click()
                                    nextTicketSelectionBtn = findHTMLDomElement((By.ID,'nextTicketSelection'),0.3,0.3)
                                    nextTicketSelectionBtn.click()
                                    nextPaymentBtn = findHTMLDomElement((By.ID,'nextPayment'),0.3,0.3)
                                    nextPaymentBtn.click()
                                    group[0].click()
                                    # 完成購票，跳出查詢位置的迴圈
                                    if fininshJob == True:
                                        break
                    # 關閉座位列表
                    group[0].click()
            else:
            # 沒有找到區域下拉按鈕，直接選擇座位
                print('1')
        return None
        # 輸入付款資料
        telInput = findHTMLDomElement((By.ID, 'tel'))
        creditCradRadio = findHTMLDomElement((By.ID, 'payMethodCode001'))
        chkAgreeAllBtn = findHTMLDomElement((By.ID, 'chkAgreeAll'))
        finalPaymentBtn = findHTMLDomElement((By.ID, 'btnFinalPayment'))
        
        # 輸入電話
        telInput[0].send_keys('886928780630')
        # 點選海外信用卡
        creditCradRadio[0].click()
        # 選擇信用卡類型
        creditCradSelector = findHTMLDomElement((By.ID, 'cardCode'))
        creditCradSelectorOption = Select(creditCradSelector[0])
        creditCradSelectorOption.select_by_value("FOREIGN_VISA")
        # 同意退費規則
        chkAgreeAllBtn[0].click()
        # 進行結算
        finalPaymentBtn[0].click()
    except TimeoutException:
        print("Element not found.")

def findHTMLDomElement(elementLocator,timer=2,poll_frequency=0.5):
    try:
        # element = WebDriverWait(driver, timer).until(EC.presence_of_element_located(elementLocator))
        element = WebDriverWait(driver, timer,poll_frequency).until(EC.presence_of_all_elements_located(elementLocator))
        return element
    except TimeoutException:
        print(f"Element {elementLocator} not found.")
        return None

## chrmoe模擬區塊
options = webdriver.ChromeOptions() 
# options.add_argument("start-maximized")
options.add_experimental_option('excludeSwitches', ['enable-logging','enable-automation'])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-popup-blocking")
# 設定允許所有彈出視窗
prefs = {"profile.default_content_setting_values.notifications": 1,
         "profile.default_content_setting_values.popups": 1}
options.add_experimental_option("prefs", prefs)


url = 'https://tkglobal.melon.com/main/index.htm?langCd=CN&'

driver = webdriver.Chrome(options=options)
driver.get(url)
# 主視窗
mainWindowHandle = driver.current_window_handle 
# title = driver.title
# 搜尋是否有預定按鈕

startKeyboardListener()
# 启动键盘监听器线程作为守护线程
# keyboard_thread = threading.Thread(target=start_keyboard_listener)
# keyboard_thread.daemon = True
# keyboard_thread.start()
# 进入 tkinter 主循环
root.mainloop()

# time.sleep(10)
# # 退出WebDriver
# driver.quit()
# root.destroy()
# exit()

