from .config.settings import BASE_DIR
from .utils import path_to_str
import os
import tkinter as tk
from tkinter import ttk
import time
from pprint import pprint
from pathlib import Path
import subprocess
import filetype


class FileDirectoryManager:
    
    __current_dir: Path = BASE_DIR
    
    @property
    def current_dir(self):
        return self.__current_dir

    @current_dir.setter
    def current_dir(self, val):
        if isinstance(val, Path) and val.is_dir():
            self.__current_dir = val
        self.update_directory_tree()
        self.update_program_tree()
    
    def __init__(self, root):
        self.root = root
        self.root.title("파일 디렉토리 관리 with Grid")

        self.left_frame = ttk.Frame(root)
        self.left_frame.grid(row=0, column=0)

        self.right_frame = ttk.Frame(root)
        self.right_frame.grid(row=0, column=1)

        # 1열 상단: 디렉토리 경로 표시 레이블 추가
        self.directory_path_label = ttk.Label(self.left_frame, text="현재 디렉토리: " + path_to_str(self.current_dir))
        self.directory_path_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

        # 1열: 파일 디렉토리 탐색
        self.directory_tree = ttk.Treeview(self.left_frame)
        self.directory_tree["columns"] = ("Type", "Size")
        self.directory_tree.heading("#0", text="이름", anchor=tk.W)
        self.directory_tree.heading("Type", text="타입", anchor=tk.W)
        self.directory_tree.heading("Size", text="크기", anchor=tk.W)
        self.directory_tree.column("#0", width=200, anchor=tk.W)
        self.directory_tree.column("Type", width=70, anchor=tk.W)
        self.directory_tree.column("Size", width=70, anchor=tk.W)
        self.directory_tree.grid(row=1, column=0, padx=10, pady=5)

        # 1열 스크롤바 추가
        directory_scrollbar = ttk.Scrollbar(self.left_frame, orient="vertical", command=self.directory_tree.yview)
        directory_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.directory_tree.config(yscrollcommand=directory_scrollbar.set)

        self.update_directory_tree()

        # 2열 상단: Recent Editted
        self.frontend_text = ttk.Label(self.right_frame, text="Recent Editted", font=("Helvetica", 14, "bold"))
        self.frontend_text.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

        # 2열: 최근 변경된 프로그램
        self.program_tree = ttk.Treeview(self.right_frame)
        self.program_tree["columns"] = ("LastModified", "Size")
        self.program_tree.heading("#0", text="프로그램", anchor=tk.W)
        self.program_tree.heading("LastModified", text="최근 수정일", anchor=tk.W)
        self.program_tree.heading("Size", text="크기", anchor=tk.W)
        self.program_tree.column("#0", width=200, anchor=tk.W)
        self.program_tree.column("LastModified", width=100, anchor=tk.W)
        self.program_tree.column("Size", width=70, anchor=tk.W)
        self.program_tree.grid(row=1, column=0, padx=10, pady=5)

        # 2열 스크롤바 추가
        program_scrollbar = ttk.Scrollbar(self.right_frame, orient="vertical", command=self.program_tree.yview)
        program_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.program_tree.config(yscrollcommand=program_scrollbar.set)

        self.update_program_tree()

        # 더블 클릭 이벤트 연결
        self.directory_tree.bind("<Double-1>", self.double_click_directory)


    def update_directory_tree(self):
        path = self.current_dir
        self.directory_tree.delete(*self.directory_tree.get_children())

        # "(Parent Directory)" 항목 추가
        if path != "/":
            parent_dir = path.parent
            self.directory_tree.insert("", "end", text="...(Parent Directory)", values=("폴더", ""))
        for item in os.listdir(path):
            item_path = path / item
            item_type = "파일"
            if os.path.isdir(item_path):
                item_type = "폴더"
            item_size = os.path.getsize(item_path)
            self.directory_tree.insert("", "end", text=item, values=(item_type, item_size))

        # 업데이트된 디렉토리 경로를 표시
        self.directory_path_label.config(text="현재 디렉토리: " + path_to_str(path))

    def double_click_directory(self, event):
        item = self.directory_tree.selection()[0]
        item_text = self.directory_tree.item(item).get("text")

        item_path:Path
        if item_text == "...(Parent Directory)":
            item_path = self.current_dir.parent
        else:
            item_path = self.current_dir / item_text
        if item_path.is_dir():
            self.current_dir = item_path
            return
        if filetype.is_image(item_path):
            return subprocess.Popen(f"start {item_path}")
        # if item_path.suffix in ('.exe', ):
        #     return subprocess.Popen(["Start-Process", "-FilePath", item_path])
        if item_path.suffix == 'exe':
            return subprocess.Popen(["start", item_path])
        if filetype.is_audio(item_path) or filetype.is_video(item_path):
            return subprocess.Popen(["./bin/mpv.exe", item_path])
        if filetype.is_video(item_path):
            return subprocess.Popen(["./bin/mpv.exe", item_path])
        return subprocess.Popen(["notepad", item_path])
        

    def update_program_tree(self):
        path = self.current_dir
        self.program_tree.delete(*self.program_tree.get_children())
        program_list = [{"name": "name1.exe", "LastModified": time.ctime(), "Size": "2MB"},
                        {"name": "name2.exe", "LastModified": time.ctime(), "Size": "1.5MB"},
                        {"name": "name3.exe", "LastModified": time.ctime(), "Size": "3MB"}]

        for program in program_list:
            self.program_tree.insert("", "end", text=program["name"], values=(program["LastModified"], program["Size"]))


def runGUI():
    root = tk.Tk()
    app = FileDirectoryManager(root)
    root.mainloop()

    
if __name__ == "__main__":
    runGUI()