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
import base64
# from PIL import Image
from io import BytesIO
from ddddocr import DdddOcr


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
        # driver.quit()
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
        # driver.switch_to.window(mainWindowHandle)
        # # 設置最長等待時間（例如10秒），直到該元素出現
        # reservationBtn = findHTMLDomElement((By.CLASS_NAME, 'reservationBtn'),3600)
        # dateTypeList = findHTMLDomElement((By.CLASS_NAME, 'type_list'))
        # ## 特別注意要改這邊的時間單位
        # dateBtn = findHTMLDomElement((By.CSS_SELECTOR, 'li[data-perfday="'+txtFileParams['show_date']+'"] button'))
        # ## 特別注意要改這邊的時間單位
        
        # # 此時元素已確認存在
        # # print("Element exists.")
        # # 將日期改為條列式
        # dateTypeList[0].click()
        # # 點選日期
        # dateBtn[0].click()
        # # 點選時間
        # timeBtn = findHTMLDomElement((By.CSS_SELECTOR, 'li.item_time.first'))
        # timeBtn[0].click()
        # # 點選預定
        # reservationBtn[0].click()
        # # 跳到彈出視窗
        # WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
        # driver.switch_to.window(driver.window_handles[-1])
        # # 點到驗證碼視窗，避免還要再用手點一次
        # captchaInput = findHTMLDomElement((By.ID, 'label-for-captcha'),10)
        # captchaImg = findHTMLDomElement((By.ID, 'captchaImg'),10)
        try:
            # driver.set_script_timeout(10)
            # form_verifyCode_base64 = driver.execute_async_script("""
            #     var canvas = document.createElement('canvas');
            #     var context = canvas.getContext('2d');
            #     var img = document.getElementById('%s');
            #     if(img!=null) {
            #     canvas.height = img.naturalHeight;
            #     canvas.width = img.naturalWidth;
            #     context.drawImage(img, 0, 0);
            #     callback = arguments[arguments.length - 1];
            #     callback(canvas.toDataURL()); }
            #     """ % ('#captchaImg'))
            # img_base64 = base64.b64decode(captchaImg[0].get_attribute('src').split(',')[1])
            # image = Image.open(BytesIO(img_base64))
            # # 將PIL圖像對象轉換為PNG格式的bytes對象
            # buffered = BytesIO()
            # image.save(buffered, format="PNG")
            # img_as_bytes = buffered.getvalue()

            img_base64 = "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"
            image_data = base64.b64decode(img_base64)
            ocr = DdddOcr()
            # with open("output.png", "wb") as f:
            #     f.write(image_data)

            with open("test.png", 'rb') as f:
                image = f.read()

            res = ocr.classification(image)
            print(res)
            # ocr_answer = ocr.classification(img_as_bytes)
            # print(ocr_answer)
        except Exception as exc:
            print("canvas exception:", str(exc))
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

# driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
# driver.set_window_size(1440, 900)
# driver.get(url)
# # 主視窗
# mainWindowHandle = driver.current_window_handle 

startKeyListener()
# root.after_idle(lambda: threading.Thread(target=startKeyListener).start())

# root.mainloop()
# root.destroy()
# sys.exit(0)