import tkinter as tk
from selenium import webdriver
from pynput import keyboard
from tkinter import messagebox

## 按鍵控制區塊
ctrlPresse = False
f1Pressed = False
f2Pressed = False

# 创建一个顶层窗口
root = tk.Tk()
root.withdraw()  # 隱藏主視窗

def keyboardPressFunction(key):
    global ctrlPresse,f1Pressed,f2Pressed
    if key == keyboard.Key.ctrl_l and ctrlPresse == False:
        print('按了CTRL')
        ctrlPresse = True
    elif key == keyboard.Key.f1 and f1Pressed == False:
        f1Pressed = True
        if ctrlPresse == True:
            print('按了CTRL+F1')
    elif key == keyboard.Key.f2  and f2Pressed == False:
        f2Pressed = True
        if ctrlPresse == True:
            print('按了CTRL+F2')
            messagebox.showinfo('123','你關閉了程式')
            driver.quit()
            root.destroy()
            exit()

def keyboardReleaseFunction(key):
    global ctrlPresse,f1Pressed,f2Pressed
    if key == keyboard.Key.ctrl_l and ctrlPresse == True:
        print('鬆開CTRL')
        ctrlPresse = False 
    elif key == keyboard.Key.f1 and f1Pressed == True:
        f1Pressed =False
    elif key == keyboard.Key.f2 and f2Pressed == True: 
        f2Pressed =False


def startKeyboardListener():
    # 创建一个键盘监听器
    keyboard_listener = keyboard.Listener(on_press=keyboardPressFunction,on_release=keyboardReleaseFunction)
    # 启动监听器
    keyboard_listener.start()
    # keyboard_listener.join()
    # 监听器在后台线程运行，这里没有使用join，而是通过定时事件来保持程序运行
    root.after(1000, startKeyboardListener)  # 1秒重新启动监听器


## chrmoe模擬區塊
options = webdriver.ChromeOptions() 
# options.add_argument("start-maximized")
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument("--disable-popup-blocking")

driver = webdriver.Chrome(options=options)
driver.get("https://www.selenium.dev/selenium/web/web-form.html")
title = driver.title

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