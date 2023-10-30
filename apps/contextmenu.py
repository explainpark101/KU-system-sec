import tkinter as tk
from tkinter import Menu
import win32com.client

def display_context_menu(event):
    try:
        shell = win32com.client.Dispatch("Shell.Application")
        folder = shell.Namespace("C:\\Users\\me2nuk\\Desktop\\")  # 폴더 경로를 지정하세요.
        file_item = folder.ParseName("TEST.PHP")  # 파일 이름을 지정하세요.
        
        context_menu = file_item.Verbs()
        if context_menu:
            tk_menu = Menu(root, tearoff=0)
            for verb in context_menu:
                tk_menu.add_command(label=verb.Name, command=lambda v=verb: v.DoIt())
            
            x, y = event.x_root, event.y_root
            tk_menu.post(x, y)
    except Exception as e:
        print(f"Error: {e}")

root = tk.Tk()
root.title("File Explorer")

label = tk.Label(root, text="Right-click here")
label.pack()

label.bind("<Button-3>", display_context_menu)

root.mainloop()