from ..config.settings import BASE_DIR
from ..utils import path_to_str
import os
import tkinter as tk
from tkinter import ttk, Menu
import time
from pprint import pprint
from pathlib import Path
from datetime import datetime, timedelta
from apps.config.utils import fire_and_forget, optionalIndex
from ..fileapi import getFileInfo_fromDB
from ..utils.MessageBox import alert, confirm
from ..database.utils import dictfetchall
import sqlite3
from ..documenting import create_markdown_document, create_pdf
from ..cursor import change_cursor

class AbstractManager(tk.Frame):
    __current_dir: Path = BASE_DIR
    def __initsmart__(self, root=None):
        if root is None:
            root = tk.Tk()

        tk.Frame.__init__(self, root)
        
    @property
    def root(self):
        return self.master
    
    @property
    def current_dir(self):
        return self.__current_dir

    @current_dir.setter
    def current_dir(self, val):
        if isinstance(val, Path) and val.is_dir():
            self.__current_dir = val
        self.update_directory_tree()

    def closing(self):
        global app1, app2, running
        if not confirm("Do you wish to close FEWT?"):
            return
        change_cursor()
        if app1 is not None and (app1_master:=getattr(app1, 'master')):
            app1_master.destroy()
        running = False
        # if self==app2:
        #     self.root.destroy()
        #     exit()
        # else:
        #     app2.root.quit()
        #     self.root.destroy()
        #     exit()
            

class FileDirectoryManager(AbstractManager):
    
    def __init__(self, root=None):
        self.__initsmart__(root)
        self.master.protocol("WM_DELETE_WINDOW", self.closing)
        self.root.title("파일 디렉토리 관리 with Grid")
        self.root.resizable(False, False)
        
        
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)


        self.left_frame = ttk.Frame(root)
        self.left_frame.grid(row=0, column=0, sticky="nsew")
        

        # 1창 상단: 디렉토리 경로 표시 레이블 추가
        # self.directory_path_indicator = ttk.Label(self.left_frame, text="현재 디렉토리:")
        # self.directory_path_indicator.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.directory_path_label = ttk.Label(self.left_frame, text=self.current_dir)
        self.directory_path_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)

        # 1창: 파일 디렉토리 탐색
        self.directory_tree = ttk.Treeview(self.left_frame, selectmode="extended", columns=("Type", "Size"), height=20)
        self.directory_tree.heading("#0", text="이름", anchor=tk.W)
        self.directory_tree.heading("Type", text="타입", anchor=tk.W)
        self.directory_tree.heading("Size", text="크기(kb)", anchor=tk.W)
        self.directory_tree.column("#0", width=650, anchor=tk.W)
        self.directory_tree.column("Type", width=130, anchor=tk.W)
        self.directory_tree.column("Size", width=130, anchor=tk.W)
        self.directory_tree.grid(row=2, column=0, padx=10, pady=5)

        # 1창 스크롤바 추가
        directory_scrollbar = ttk.Scrollbar(self.left_frame, orient="vertical", command=self.directory_tree.yview)
        directory_scrollbar.grid(row=2, column=1, sticky=(tk.N, tk.S))
        self.directory_tree.config(yscrollcommand=directory_scrollbar.set)


        self.update_directory_tree()

        # 더블 클릭 이벤트 연결
        self.directory_tree.bind("<Double-1>", self.double_click_directory)

        global app2
        root2 = tk.Toplevel(self.master)
        app2 = RecentEdittedManager(root2)

    def get_file_name_from_directory_tree(self):
        return self.directory_tree.item(self.directory_tree.selection()[0]).get("text")


    def update_directory_tree(self):
        path = self.current_dir
        self.directory_tree.delete(*self.directory_tree.get_children())

        # "(Parent Directory)" 항목 추가
        if path.as_posix().__len__() != 3:
            parent_dir = path.parent
            self.directory_tree.insert("", "end", text="...(Parent Directory)", values=("폴더", ""))
        for item in path.iterdir():
            item_path = path / item
            item_type = "파일" if item_path.is_file() else "폴더"
            try:
                item_size = item_path.stat().st_size
            except FileNotFoundError:
                continue
            self.directory_tree.insert("", "end", text=item.name, values=(item_type, item_size))

        # 업데이트된 디렉토리 경로를 표시
        self.directory_path_label.config(text="현재 디렉토리: " + path_to_str(path))
        change_cursor()
        

    

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
        # if filetype.is_image(item_path):
        #     return subprocess.Popen(f"start {item_path}")
        # # if item_path.suffix in ('.exe', ):
        # #     return subprocess.Popen(["Start-Process", "-FilePath", item_path])
        # if item_path.suffix == 'exe':
        #     return subprocess.Popen(["start", item_path])
        # if filetype.is_audio(item_path) or filetype.is_video(item_path):
        #     return subprocess.Popen(["./bin/mpv.exe", item_path])
        # if filetype.is_video(item_path):
        #     return subprocess.Popen(["./bin/mpv.exe", item_path])
        return os.startfile(item_path)

    
        
class RecentEdittedManager(AbstractManager):
    def __init__(self, root):
        self.__initsmart__(root)
        self.root.title("Recent Editted")
        self.root.resizable(False, False)
        self.master.protocol("WM_DELETE_WINDOW", self.closing)

        self.right_frame = ttk.Frame(root)
        self.right_frame.pack(expand=True, fill='both')

        self.wrapper_frame = ttk.Frame(self.right_frame)
        self.wrapper_frame.grid(row=3, column=1)

        menubar = tk.Menu(self.root)
        menubar.add_cascade(label="마크다운 문서 변환", command=self.convert_markdown)
        menubar.add_cascade(label="PDF 문서 변환", command=self.convert_pdf)

        # 메뉴바 적용
        self.root.config(menu=menubar)

        self.change_safety_btn = ttk.Button(self.wrapper_frame, text="위험도 변경", command=self.toggle_safety, width=20)
        self.change_safety_btn.grid(row=2, column=0, pady=5, padx=(10, 5), sticky=tk.W)

        # 2창 상단: Recent Editted
        self.frontend_text = ttk.Label(self.wrapper_frame, text="Recently Editted", font=("Helvetica", 14, "bold"))
        self.frontend_text.grid(row=0, column=0, padx=10, pady=5, sticky='ns')
        
        self.current_watching_dir = ttk.Label(self.wrapper_frame, text="Current Watching:", font=("Helvetica", 11))
        self.current_watching_dir.grid(row=1, column=0, padx=10, pady=3, sticky='ns')
        self.current_watching_dir.bind("<Double-1>", self.change_watching_dir)

        self.label_01 = ttk.Label(self.wrapper_frame, 
                                text=(
                                  '여기에는 파일 변경사항이 기록됩니다.\n'+
                                  '파일을 더블 클릭하여 위험도를 변경하고, markdown 문서 또는 pdf 문서로 출력할 수 있습니다.\n'+
                                  '크기의 숫자가 아닌 항목은 다음을 의미합니다.\n'+
                                  'del=삭제된항목\n'+
                                  'PermErr=권한제한으로 알 수 없음\n'+
                                  'notFile=폴더임'
                                )
        )
        self.label_01.grid(row=2, column=0)

        # 2창: 최근 변경된 프로그램
        self.program_tree = ttk.Treeview(self.wrapper_frame, height=35)
        self.program_tree["columns"] = ("LastModified", "Size", "Safety")
        self.program_tree.heading("#0", text="프로그램", anchor=tk.W)
        self.program_tree.heading("LastModified", text="최근 수정일", anchor=tk.W)
        self.program_tree.heading("Size", text="크기(kb)", anchor=tk.W)
        self.program_tree.heading("Safety", text="안전도", anchor=tk.W)  # Header for "Safety" column
        self.program_tree.column("#0", width=550, anchor=tk.W)
        self.program_tree.column("LastModified", width=100, anchor=tk.W)
        self.program_tree.column("Size", width=70, anchor=tk.W)
        self.program_tree.column("Safety", width=70, anchor=tk.W)  # Width for "Safety" column
        self.program_tree.grid(row=4, column=0, padx=10, pady=5, columnspan=1, rowspan=1)
        
        self.program_tree.bind()

        # 2창 스크롤바 추가
        program_scrollbar = ttk.Scrollbar(self.wrapper_frame, orient="vertical", command=self.program_tree.yview)
        program_scrollbar.grid(row=4, column=1, sticky=(tk.N, tk.S))
        self.program_tree.config(yscrollcommand=program_scrollbar.set)

        self.program_tree.bind("<Double-1>", self.toggle_safety)
        
    def change_watching_dir(self):
        ...
        
    def change_watching_dir_label(self, value:Path):
        if not isinstance(value, Path):
            return
        self.current_watching_dir.config(text=f"Watching: {value.absolute()}")
        return 
    
    def update_program_tree(self):
        """
        Database에서 변경사항 목록을 가져옵니다.

        """
        path = self.current_dir
        self.program_tree.delete(*self.program_tree.get_children())
        change_cursor("loading")
        with sqlite3.connect("FEWT.sqlite3") as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT *
                FROM "fileContent"
                WHERE record_time > ?
            """, [(datetime.now() - timedelta(hours=-1)).timestamp()])
            program_list = dictfetchall(cur)
        change_cursor()
        for program in program_list:
            self.program_tree.insert("", "end", text=program["file_path"], values=(datetime.fromtimestamp(program["record_time"]).strftime("%Y-%m-%d %H:%M:%S.%f"), program["size"]))
            
        return 
        
    def insert_into_program_tree(self, data:dict):
        file_path, record_time, size = data.get('file_path'), data.get('record_time'), data.get('size')
        self.program_tree.insert("", 0, text=file_path, values=(datetime.fromtimestamp(record_time).strftime("%Y-%m-%d %H:%M:%S.%f"), size))
        return
    
    def add_menu_bar(self):
        # 메뉴바 생성
        menubar = tk.Menu(self.root)
        menubar.add_cascade(label="마크다운 문서 변환", command=self.convert_markdown)
        menubar.add_cascade(label="PDF 문서 변환", command=self.convert_pdf)

        # 메뉴바 적용
        self.root.config(menu=menubar)
    
    def toggle_safety_one(self, selection, blur=True):
        item = self.program_tree.item(selection)
        item_id = [self.program_tree.item(child) for child in self.program_tree.get_children()].index(item)
        item_id = self.program_tree.get_children()[item_id]
        list_of_safety = ["안전", "위험", "고위험"]
        current_index_of_safety = list_of_safety.index(optionalIndex(item.get("values"), 2, "고위험"))
        item["Safety"] = list_of_safety[(current_index_of_safety + 1) % 3]

        self.program_tree.set(item_id, "Safety", item["Safety"])
        self.update_program_description_background(item_id, item["Safety"])

        if blur:
            self.program_tree.selection_remove(selection)
    
    
    def toggle_safety(self, event=None):    
        if len(self.program_tree.get_children()) == 0: 
            return
        selections = self.program_tree.selection()
        if len(selections) == 0: return
        if event is None: # batch toggle
            list_of_safety = ["안전", "위험", "고위험"]
            current_index_of_safety = list_of_safety.index(optionalIndex(self.program_tree.item(selections[0]).get("values"), 2, "고위험"))
            for selection in selections:
                item = self.program_tree.item(selection)
                item_id = [self.program_tree.item(child) for child in self.program_tree.get_children()].index(item)
                item_id = self.program_tree.get_children()[item_id]
                item["Safety"] = list_of_safety[(current_index_of_safety + 1) % 3]

                self.program_tree.set(item_id, "Safety", item["Safety"])
                self.update_program_description_background(item_id, item["Safety"])
            return 
            
        for selection in selections:
            self.toggle_safety_one(selection, event is not None)

    
    def update_program_description_background(self, item_id, safety_text):
        self.program_tree.tag_configure("Safe.Background", background="white", foreground="black")
        self.program_tree.tag_configure("Warning.Background", background="#ffc107", foreground="black")
        self.program_tree.tag_configure("Danger.Background", background="#dc3545", foreground="white")

        if safety_text == "안전":
            self.program_tree.item(item_id, tags=("Safe.Background",))
        elif safety_text == "위험":
            self.program_tree.item(item_id, tags=("Warning.Background",))
        elif safety_text == "고위험":
            self.program_tree.item(item_id, tags=("Danger.Background",))
    
    def convert_markdown(self):
        # 마크다운 변환 로직 구현
        files = []
        for child in self.program_tree.get_children():
            child = self.program_tree.item(child)
            path = child.get('text')
            log_time = child.get('values')[0]
            file_size = child.get('values')[1]
            safety = optionalIndex(child.get('values'), 2, None)
            files.append({"path": path, "logged_time": log_time, "file_size": file_size, "safety": safety})
        
        return create_markdown_document(files, BASE_DIR / f'{datetime.now().strftime("%Y-%m-%d")} 파일변경사항 보고서.md')
            

    def convert_pdf(self):
        # PDF 변환 로직 구현
        fire_and_forget(alert, "pdf문서로 변환중입니다...")
        files = []
        for child in self.program_tree.get_children():
            child = self.program_tree.item(child)
            path = child.get('text')
            log_time = child.get('values')[0]
            file_size = child.get('values')[1]
            safety = optionalIndex(child.get('values'), 2, None)
            files.append({"path": path, "logged_time": log_time, "file_size": file_size, "safety": safety})
        return create_pdf(files, BASE_DIR / f'{datetime.now().strftime("%Y-%m-%d")} 파일변경사항 보고서.pdf')

        
app1:FileDirectoryManager = None
app2:RecentEdittedManager = None
running:bool = True

def get_app1():
    global app1
    return app1
def get_app2():
    global app2
    return app2

def is_gui_running():
    global running
    return running

def _runGUI():
    global app1
    root = tk.Tk()
    app1 = FileDirectoryManager(root)
    app1.mainloop()
# def _runGUI2():
#     global app2
#     root2 = tk.Tk()
#     app2 = RecentEdittedManager(root2)
#     app2.mainloop()
    

def update_program_tree(app):
    while True:
        if app is None: 
            time.sleep(.001)
            continue
        app.update_program_tree()
        time.sleep(.001)


def runGUI():
    global app1
    import threading
    thd = threading.Thread(target=_runGUI)
    thd.daemon = True
    # thd.start()
    # thd = threading.Thread(target=_runGUI2)
    # thd.daemon = True
    thd.start()
    thd2 = threading.Thread(target=update_program_tree, args=(app2, ))
    thd2.daemon = True
    thd2.start()
    
if __name__ == "__main__":
    runGUI()