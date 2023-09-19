import tkinter as tk
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from pynput import keyboard
from tkinter import messagebox

## 編譯說明
#1 
# 請記得調整 dateBtn = findHTMLDomElement((By.CSS_SELECTOR, 'li[data-perfday="20230924"] button'))
# 這邊要根據實際的演唱會日期去調整
#2 
# 請記得調整creditCradSelectorOption.select_by_visible_text("FOREIGN_VISA")
# 這邊要根據使用的信用卡去調整


## 按鍵控制區塊if key.char == '1':
altPresse = False
f1Pressed = False
f2Pressed = False
f3Pressed = False
f5Pressed = False

# 创建一个顶层窗口
root = tk.Tk()
root.withdraw()  # 隱藏主視窗

def keyboardPressFunction(key):
    global altPresse,f1Pressed,f2Pressed,f3Pressed,f5Pressed,mainWindowHandle
    if key == keyboard.Key.alt_l and altPresse == False:
        print('按了ALT')
        altPresse = True
    elif key == keyboard.Key.f1 and f1Pressed == False:
        f1Pressed = True
        if altPresse == True:
            print('按了ALT+F1')
            melonTikectClickOrderButton() # 自動點預定
    elif key == keyboard.Key.f2  and f2Pressed == False:
        f2Pressed = True
        if altPresse == True:
            print('按了ALT+F2')
            melonTikectBuyTicketInfo() # 自動輸入購票資訊
    elif key == keyboard.Key.f3  and f3Pressed == False:
        f3Pressed = True
        if altPresse == True:
            print('按了ALT+F3，切回主視窗')
            driver.switch_to.window(mainWindowHandle)
    elif key == keyboard.Key.f5  and f5Pressed == False:
        f5Pressed = True
        if altPresse == True:
            print('按了ALT+f5')        
            messagebox.showinfo('123','你關閉了程式')
            driver.quit()
            root.destroy()
            exit()   
                 

def keyboardReleaseFunction(key):
    global altPresse,f1Pressed,f2Pressed,f3Pressed,f5Pressed
    if key == keyboard.Key.alt_l and altPresse == True:
        # print('鬆開CTRL')
        altPresse = False 
    elif key == keyboard.Key.f1 and f1Pressed == True:
        f1Pressed =False
    elif key == keyboard.Key.f2 and f2Pressed == True: 
        f2Pressed =False
    elif key == keyboard.Key.f3 and f3Pressed == True: 
        f3Pressed =False        
    elif key == keyboard.Key.f5 and f5Pressed == True: 
        f5Pressed =False            


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
        print("Element exists.")
        # 將日期改為條列式
        dateTypeList.click()
        # 點選日期
        dateBtn.click()
        # 點選時間
        timeBtn = findHTMLDomElement((By.CSS_SELECTOR, 'li.item_time.first'))
        timeBtn.click()
        # 點選預定
        reservationBtn.click()
        # 跳到彈出視窗
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
        for handle in driver.window_handles:
            if handle != mainWindowHandle:
                print('Switch to second window.')
                driver.switch_to.window(handle)
                break
    except TimeoutException:
        print("Element not found.")

def melonTikectBuyTicketInfo():
    try:
        driver.switch_to.frame("oneStopFrame")
        # 設置最長等待時間（例如10秒），直到該元素出現
        telInput = findHTMLDomElement((By.ID, 'tel'))
        creditCradRadio = findHTMLDomElement((By.ID, 'payMethodCode001'))
        chkAgreeAllBtn = findHTMLDomElement((By.ID, 'chkAgreeAll'))
        finalPaymentBtn = findHTMLDomElement((By.ID, 'btnFinalPayment'))
        
        # 此時元素已確認存在
        print("Element exists.")
        # 輸入電話
        telInput.send_keys('886928780630')
        # 點選海外信用卡
        creditCradRadio.click()
        # 選擇信用卡類型
        creditCradSelector = findHTMLDomElement((By.ID, 'cardCode'))
        creditCradSelectorOption = Select(creditCradSelector)
        creditCradSelectorOption.select_by_value("FOREIGN_VISA")
        # 同意退費規則
        chkAgreeAllBtn.click()
        # 進行結算
        finalPaymentBtn.click()
    except TimeoutException:
        print("Element not found.")

def findHTMLDomElement(elementLocator,timer=2):
    try:
        element = WebDriverWait(driver, timer).until(EC.presence_of_element_located(elementLocator))
        return element
    except TimeoutException:
        print(f"Element {elementLocator} not found.")

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


url = 'https://tkglobal.melon.com/main/index.htm?langCd=EN'

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