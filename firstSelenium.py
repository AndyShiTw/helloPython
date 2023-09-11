import tkinter as tk

from selenium import webdriver
from tkinter import messagebox

driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/selenium/web/web-form.html")
title = driver.title
# assert title == "Web form"

root = tk.Tk()
root.withdraw()  # 隱藏主視窗

messagebox.showinfo('123',title)
driver.quit()