import threading
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
from collections import defaultdict
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import sys


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

# 當前已按下的按鍵集合
currentKeys = set()

cmdPressed = False

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
    global currentKeys,cmdPressed
    if key == keyboard.Key.esc:
        print(f"{key} 被按下，準備關閉程式")
        driver.quit()
        # messagebox.showinfo('結束程式','你關閉了程式')
        # root.quit()
        return False  # 結束監聽
    
    # 記錄這個按鈕按過，不要一直重複監聽，避免重複執行，直到他被放開
    if key not in currentKeys:
        # 這是新的鍵被按下
        print(f"{key} 被按下")
        currentKeys.add(key)

        if key == keyboard.Key.cmd:
            cmdPressed = True

    # mac要額外紀錄cmd按鈕是否被按下   

    if str(key) == r"<49>":
        melonTikectClickOrderButton()
    elif str(key) == r"<50>":
        melonTikectBuyTicketInfo(2,1)
    elif key == keyboard.KeyCode.from_char('1') and cmdPressed == True:
        melonTikectClickOrderButton()
    elif key == keyboard.KeyCode.from_char('2') and cmdPressed == True:  
        melonTikectBuyTicketInfo(2,1)      

    # if any([key in COMBO for COMBO in hotkeys]):
    #     currentKeys.add(key)
    #     if any(all(k in currentKeys for k in COMBO) for COMBO in hotkeys):
    #         execute()

    # if any([key in hotkey for hotkey in hotkeys]):
    #     currentKeys.add(key)
    #     # 檢查是否匹配任何熱鍵組合
    #     for hotkey, action in hotkeys.items():
    #         if hotkey <= currentKeys:
    #             action()  # 執行對應的功能


    # global ctrlOrCmdPressed,f1Pressed,f2Pressed,f3Pressed,f4Pressed,mainWindowHandle
    # if key == Key.ctrl_l or key == Key.cmd:
    #     # print('按下ctrl或cmd')
    #     ctrlOrCmdPressed = True

    # if (hasattr(key, 'char') and key.char == '1') or str(key) == r"<49>":
    #     print(key.vk)
    #     print('1')
    #     f1Pressed = True        

    # if (key == keyboard.Key.ctrl or keyboard.Key.cmd) and ctrlOrCmdPressed == False:
    #     print('按了CTRL')
    #     ctrlOrCmdPressed = True

    # elif key == keyboard.KeyCode.from_char('1') and f1Pressed == False:
    #     f1Pressed = True
    #     print('#1')
    #     if ctrlOrCmdPressed == True:
    #         print('按了CTRL+1')
    #         # melonTikectClickOrderButton() # 自動點預定

    # elif key == keyboard.KeyCode.from_char('2') and f2Pressed == False:
    #     f2Pressed = True
    #     if ctrlOrCmdPressed == True:
    #         print('按了CTRL+2')
    #         # melonTikectBuyTicketInfo(2,1) # 自動輸入購票資訊

    # elif key == keyboard.KeyCode.from_char('3') and f3Pressed == False:
    #     f3Pressed = True
    #     if ctrlOrCmdPressed == True:
    #         print('按了CTRL+3')
    #         driver.switch_to.window(mainWindowHandle)

    # elif key == keyboard.KeyCode.from_char('4') and f4Pressed == False:
    #     f4Pressed = True
    #     if ctrlOrCmdPressed == True:
    #         print('按了CTRL+4')        
    #         messagebox.showinfo('123','你關閉了程式')
    #         driver.quit()
    #         root.destroy()
    #         exit()   
                 

def keyboardReleaseFunction(key):
    global currentKeys,cmdPressed
    if key in currentKeys:
        # print(f"{key} 被放開")
        currentKeys.remove(key)    
        if key == keyboard.Key.cmd:
            cmdPressed = False
    # if any([key in hotkey for hotkey in hotkeys]):
    #     currentKeys.remove(key)
    # global ctrlOrCmdPressed,f1Pressed,f2Pressed,f3Pressed,f4Pressed
    # if key == Key.ctrl_l or key == Key.cmd:
    #     # print('鬆開ctrl或cmd')
    #     ctrlOrCmdPressed = False

    # if hasattr(key, 'char') and key.char == '1':
    #     # print('鬆開1')
    #     f1Pressed = False        
        
    # if (key == keyboard.Key.ctrl or keyboard.Key.cmd) and ctrlOrCmdPressed == False:
    #     # print('鬆開CTRL')
    #     ctrlOrCmdPressed = False 
    # if key == keyboard.KeyCode.from_char('1') and f1Pressed == True:
    #     f1Pressed =False
    # elif key == keyboard.KeyCode.from_char('2') and f2Pressed == True: 
    #     f2Pressed =False
    # elif key == keyboard.KeyCode.from_char('3') and f3Pressed == True: 
    #     f3Pressed =False        
    # elif key == keyboard.KeyCode.from_char('4') and f4Pressed == True: 
    #     f4Pressed =False            


def startKeyboardListener():
    # 创建一个键盘监听器
    with keyboard.Listener(on_press=keyboardPressFunction,on_release=keyboardReleaseFunction) as listener:
        listener.join()
    # keyboard_listener = keyboard.Listener(on_press=keyboardPressFunction,on_release=keyboardReleaseFunction)
    # # 启动监听器
    # keyboard_listener.start()
    # keyboard_listener.join()
    # 监听器在后台线程运行，这里没有使用join，而是通过定时事件来保持程序运行
    # root.after(1000, startKeyboardListener)  # 1秒重新启动监听器

def melonTikectClickOrderButton():
    global mainWindowHandle,txtFileParams
    try:
        driver.switch_to.window(mainWindowHandle)
        # 設置最長等待時間（例如10秒），直到該元素出現
        reservationBtn = findHTMLDomElement((By.CLASS_NAME, 'reservationBtn'),3600)
        dateTypeList = findHTMLDomElement((By.CLASS_NAME, 'type_list'))
        ## 特別注意要改這邊的時間單位
        dateBtn = findHTMLDomElement((By.CSS_SELECTOR, 'li[data-perfday="'+txtFileParams['show_date']+'"] button'))
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
        driver.switch_to.window(driver.window_handles[-1])
        # 點到驗證碼視窗，避免還要再用手點一次
        # captchaTxt = findHTMLDomElement((By.ID, 'label-for-captcha'))
        # captchaTxt[0].click()
    except TimeoutException:
        print("Element not found.")

# version 1:自動輸入資訊 2:自動挑選最佳位子，並自動輸入資訊
def melonTikectBuyTicketInfo(version=1,buyTicketNum=1):
    global txtFileParams
    try:
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
        driver.switch_to.window(driver.window_handles[-1])
        driver.switch_to.frame("oneStopFrame")
        finishSeatJob = False
        clickTicketNum = 0

        if version == 2:
            # 先蒐集座位標籤，但我們按照右側的順序來定義最佳到最差的位置
            # 正常來說座位優先順序 VIP => R => S => A
            # 有兩種售票方式 divGradeSummary和partSeatGrade
            # divGradeSummary代表要展開才能選座位
            # partSeatGrade直接選右邊的座位
            seatList = findHTMLDomElement((By.ID,'partSeatGrade'),0.5,0.5)
            if seatList is None:
                seatList = findHTMLDomElement((By.ID,'divGradeSummary'),0.1,0.1)
                if seatList is not None:
                    # 是否搜尋所有座位，還是根據頁面上的剩餘座位數量決定是否選位
                    clickAllSeatBtn = True 
                    # 定位該tbody內的所有tr元素
                    rows = seatList[0].find_elements(By.TAG_NAME,"tr")
                    groupedRows = [rows[i:i+2] for i in range(0, len(rows), 2)]

                    for i in range(2):
                        if finishSeatJob == True:
                            break
                        print(f'第{i+1}次開始搜尋是否有座位')
                        for group in groupedRows:
                            if finishSeatJob == True:
                                break
                            # colorDiffCache = {}
                            # 展開座位列表
                            group[0].click()
                            # 取得座位顏色
                            # seatColor = group[0].find_element(By.TAG_NAME,'em').value_of_css_property('background-color')
                            # seatColorRgb = rgbStringToRGB(seatColor)
                            # 測試是否可以讀到第二個狀態列表，還是需要重新讀取
                            ticketLiBtnList = group[1].find_elements(By.TAG_NAME,"li")
                            for ticketLiBtn in ticketLiBtnList:
                                if finishSeatJob == True:
                                    break
                                # 檢查是否有座位
                                ticketNum = ticketLiBtn.find_element(By.TAG_NAME,'strong')
                                if ticketNum.text != '0' or clickAllSeatBtn == True:
                                    # 有座位，點擊
                                    ticketLiBtn.click()
                                    # 展開詳細座位列表，並搜尋座位色碼，進行購票
                                    ticketBlock = findHTMLDomElement((By.ID,'ez_canvas'),3)
                                    rectElements = ticketBlock[0].find_elements(By.TAG_NAME,'rect')

                                    for index,rect in enumerate(rectElements):
                                        rectColor = rect.get_attribute('fill')

                                        # fill可能沒有設定任何顏色，或是設定為none
                                        if rectColor == 'none':
                                            continue

                                        if rectColor == '#DDDDDD':
                                            continue

                                        # 若色碼相同，則存快取字典中取出，不再重複比對
                                        # if rectColor in colorDiffCache:
                                        #     colorDiffPercent = colorDiffCache[rectColor]
                                        # else:
                                        #     r, g, b = hex_to_rgb(rectColor)
                                        #     colorDiffPercent = rgbPercent((r, g, b), seatColorRgb)
                                        #     if colorDiffPercent is None:
                                        #         continue
                                        #     colorDiffCache[rectColor] = colorDiffPercent

                                        # print('#1')
                                        # print(rgb_to_hex(seatColor),rectColor)
                                        # print((r, g, b), seatColorRgb)
                                        # print(colorDiffPercent)
                                        # print('#2')
                                        # 比對顏色是否小於20，超過20視為不同顏色，因為melon的可選座位色碼會浮動調整
                                        # if colorDiffPercent < 0.2:
                                        rect.click()

                                        # 購買指定的票券數量
                                        clickTicketNum += 1

                                        if clickTicketNum == buyTicketNum:
                                            nextTicketSelectionBtn = findHTMLDomElement((By.ID,'nextTicketSelection'),0.3,0.3)
                                            nextTicketSelectionBtn[0].click()
                                            nextPaymentBtn = findHTMLDomElement((By.ID,'nextPayment'))
                                            # 找不到付款按鈕，代表該位置已經被搶走了，繼續找下一個位置
                                            if nextPaymentBtn is None:
                                                # 購票失敗，繼續找兩個位置
                                                clickTicketNum = 0
                                                continue

                                            nextPaymentBtn[0].click()
                                            # 完成購票，跳出查詢位置的迴圈
                                            finishSeatJob = True
                                            break
                            # 關閉座位列表
                            if finishSeatJob == False:
                                group[0].click()
                    if finishSeatJob == False:
                        print(f"重複找不到座位，請重新搜尋")
                        # root.after(0, lambda:messagebox.showinfo('找不到座位','嘗試刷新了10次座位列表，但找不到座位，請重新搜尋座位'))
                        return None
            # else:
            #     # 先找出票種的顏色
            #     seatColorList = []
            #     seatDictionary = defaultdict(list)
            #     colorDiffCache = {}
            #     row = seatList[0].find_elements(By.TAG_NAME,"tr")
            #     for seatColor in row:
            #         seatColorList.append(seatColor.find_element(By.TAG_NAME,'em').value_of_css_property('background-color'))

            #     # 沒有找到區域下拉按鈕，直接選擇座位
            #     # 將所有rect標籤取出，利用XY座標排序，避免買到縱向的位置
            #     # 以Y座標越小越前面，X座標相等代表同一列
            #     for i in range(2):
            #         if finishSeatJob == True:
            #             break
            #         print(f'第{i+1}次開始搜尋是否有座位')
            #         ticketBlock = findHTMLDomElement((By.ID,'ez_canvas'),3)
            #         rectElements = ticketBlock[0].find_elements(By.TAG_NAME,'rect')

            #         # 將座位儲存成Y軸的字典
            #         for index,rect in enumerate(rectElements):
            #             # 取出XY座標與座位色碼，若讀不到色碼或已經售出，則不存入
            #             rectColor = rect.get_attribute('fill')
            #             # fill可能沒有設定任何顏色，或是設定為none
            #             if rectColor == 'none':
            #                 continue

            #             rectXAxis = rect.get_attribute('x')
            #             rectYAxis = rect.get_attribute('y')
            #             seatDictionary[rectYAxis].append({'x':rectXAxis,'y':rectYAxis,'color':rectColor,'webEelement':rect})
            #         # 將每個Y軸再用X軸排序
            #         for y, seatData in seatDictionary.items():
            #             seatDictionary[y].sort(key=lambda d: (d['x']))

            #         # 計算每一列的平均距離，小於平均距離的視為鄰座，可以連著購買
            #         distances = defaultdict(lambda: {"sum": 0, "count": 0})
            #         for y, seatData in seatDictionary.items():
            #             prevSeat = 0
            #             for key,data in enumerate(seatData):
            #                 if key > 0:
            #                     distances[y]["sum"] += data['x'] - prevSeat
            #                 distances[y]["count"] += 1
            #                 prevSeat = data['x']
            #                 if data["color"] == '#DDDDDD':
            #                     seatDictionary[y].pop(key)
                    
            #         averageDistances = {y: data["sum"]/data["count"] for y, data in distances.items()}

            #         prevWebEelmentSeat = []
            #         # 根據色碼找票
            #         for seatColor in seatColorList:
            #             if finishSeatJob == True:
            #                 break
            #             # 首先將色碼轉RGB
            #             seatColorRgb = rgbStringToRGB(seatColor)
            #             # 開始找座位
            #             for seatBlock in seatDictionary:
            #                 # 比對座位色碼
            #                 # 若色碼相同，則存快取字典中取出，不再重複比對
            #                 if seatBlock['color'] in colorDiffCache:
            #                     colorDiffPercent = colorDiffCache[seatBlock['color']]
            #                 else:
            #                     r, g, b = hex_to_rgb(seatBlock['color'])
            #                     colorDiffPercent = rgbPercent((r, g, b), seatColorRgb)
            #                     if colorDiffPercent is None:
            #                         continue
            #                     colorDiffCache[seatBlock['color']] = colorDiffPercent

            #                 # 如果只要買一張票，色碼相似就可以完成購買
            #                 if buyTicketNum == 1:
            #                     if colorDiffPercent < 15:
            #                         seatBlock['webEelement'].click()
            #                         nextTicketSelectionBtn = findHTMLDomElement((By.ID,'nextTicketSelection'),0.3,0.3)
            #                         nextTicketSelectionBtn[0].click()
            #                         nextPaymentBtn = findHTMLDomElement((By.ID,'nextPayment'))
            #                         # 找不到付款按鈕，代表該位置已經被搶走了，繼續找下一個位置
            #                         if nextPaymentBtn is None:
            #                             # 購票失敗，繼續找位置
            #                             continue
            #                         nextPaymentBtn[0].click()
            #                         # 完成購票，跳出查詢位置的迴圈
            #                         finishSeatJob = True
            #                         break
            #                 else:
            #                     # 要找到連號並可購買的座位
            #                     if colorDiffPercent < 15:
            #                         # 第一個座位直接選
            #                         if buyTicketNum == 0:
            #                             seatBlock['webEelement'].click()
            #                             prevWebEelmentSeat.append(seatBlock)
            #                         else:
            #                             print('購買多張連號的票')
            #                             # 購買多張連號的票
            #                             # 檢查這張座位的X軸和前一張座位的X軸是否小於平均距離
            #                             if seatBlock['x'] - prevWebEelmentSeat[-1]['x'] <= averageDistances[seatBlock['y']]:
            #                                 # 如果小於平均距離，則代表是連號的座位，可以購買
            #                                 seatBlock['webEelement'].click()
            #                                 prevWebEelmentSeat.append(seatBlock)
            #                                 clickTicketNum += 1
            #                                 # 如果把票買齊了，則跳出迴圈
            #                                 if clickTicketNum == buyTicketNum:
            #                                     finishSeatJob = True
            #                                 break
            #         # 刷新按鈕，因為這種購票方式不存在選位機制，當找不到座位時要點刷新重新讀取API，取得最新的座位資訊
            #         refreshSeatBtn = findHTMLDomElement((By.ID,'btnReloadSchedule'))

            

        # 輸入付款資料
        telInput = findHTMLDomElement((By.ID, 'tel'))
        creditCradRadio = findHTMLDomElement((By.ID, 'payMethodCode001'))
        chkAgreeAllBtn = findHTMLDomElement((By.ID, 'chkAgreeAll'))
        finalPaymentBtn = findHTMLDomElement((By.ID, 'btnFinalPayment'))
        
        creditCrad = txtFileParams['credit_card']
        creditCradType = {'VISA':0,'MASTER':1}
        phone = txtFileParams['phone']
        # 輸入電話
        telInput[0].send_keys(phone)
        # 點選海外信用卡
        creditCradRadio[0].click()
        # 選擇信用卡類型
        creditCradSelector = findHTMLDomElement((By.ID, 'cardCode'))
        creditCradSelectorOption = Select(creditCradSelector[0])
        creditCradSelectorOption.select_by_value("FOREIGN_"+creditCrad)
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
        # print(f"Element {elementLocator} not found.")
        return None
    
def startKeyListener():
    with keyboard.Listener(on_press=keyboardPressFunction,on_release=keyboardReleaseFunction) as listener:
        listener.join()

    
# 创建一个顶层窗口
# root = tk.Tk()
# root.withdraw()  # 隱藏主視窗
# root.call('wm', 'attributes', '.', '-topmost', True)    
    
## 檢查必要的資料是否有輸入正確
txtFileParams = {}
try:
    with open('payment_info.txt', 'r', encoding='utf-8') as file:
        for line in file:
            # 不讀取開頭結尾是#的文字，避免註解被使用
            if not line.strip().startswith('#'):
                key, value = line.strip().split('=')
                if key in ['phone','credit_card','show_date']:
                    txtFileParams[key] = value
except FileNotFoundError:
    print(f"缺少txt檔案")
    # messagebox.showinfo('缺少txt檔案','無法自動輸入訂購人資訊')
    # root.destroy()
    exit()

for key in ['phone','credit_card','show_date']:
    if key not in txtFileParams:
        print(f"個人資訊中的'{key}'沒有找到，請參照範例填寫!")
        # messagebox.showinfo('信用卡僅支援VISA/MASTER','請先確認信用卡是否照範例設定')
        # root.destroy()
        exit()

if txtFileParams['credit_card'] not in ['VISA','MASTER']:
    print(f"信用卡僅支援VISA/MASTER")
    # messagebox.showinfo('信用卡僅支援VISA/MASTER','請先確認信用卡是否照範例設定')
    # root.destroy()
    exit()

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

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
driver.set_window_size(1440, 900)
driver.get(url)
# 主視窗
mainWindowHandle = driver.current_window_handle 

startKeyListener()
# root.after_idle(lambda: threading.Thread(target=startKeyListener).start())

# root.mainloop()
# root.destroy()
# sys.exit(0)