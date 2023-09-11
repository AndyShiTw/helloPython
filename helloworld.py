import tkinter as tk
from tkinter import messagebox

def main():
    root = tk.Tk()
    root.withdraw()  # 隱藏主視窗

    messagebox.showinfo("Hello", "Hello, World!")

if __name__ == "__main__":
    main()