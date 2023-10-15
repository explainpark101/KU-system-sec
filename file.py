import os
import tkinter as tk
from tkinter import ttk
import time

class FileDirectoryManager:
    def __init__(self, root):
        self.root = root
        self.root.title("파일 디렉토리 관리 with Grid")

        self.left_frame = ttk.Frame(root)
        self.left_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W, tk.E))

        self.right_frame = ttk.Frame(root)
        self.right_frame.grid(row=0, column=1, sticky=(tk.N, tk.S, tk.W, tk.E))

        # 1열 상단: 디렉토리 경로 표시 레이블 추가
        self.directory_path_label = ttk.Label(self.left_frame, text="현재 디렉토리: " + os.getcwd())
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
        self.directory_tree.grid(row=1, column=0, padx=10, pady=5, sticky=(tk.N, tk.S, tk.W, tk.E))

        # 1열 스크롤바 추가
        directory_scrollbar = ttk.Scrollbar(self.left_frame, orient="vertical", command=self.directory_tree.yview)
        directory_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.directory_tree.config(yscrollcommand=directory_scrollbar.set)

        self.update_directory_tree()

        # 2열 상단: "프론트엔드가 담당할 부분" 레이블 추가
        self.frontend_text = ttk.Label(self.right_frame, text="Recent Editted", font=("Helvetica", 14, "bold"))
        self.frontend_text.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

        # 2열: 최근 변경된 프로그램 속성
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

        # 디렉토리 트리에 더블 클릭 이벤트를 연결
        self.directory_tree.bind("<Double-1>", self.double_click_directory)


    def update_directory_tree(self):
        path = os.getcwd()
        self.directory_tree.delete(*self.directory_tree.get_children())

        # "(Parent Directory)" 항목 추가
        if path != "/":
            parent_dir = os.path.dirname(path)
            self.directory_tree.insert("", "end", text="...(Parent Directory)", values=("폴더", ""))
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            item_type = "파일"
            if os.path.isdir(item_path):
                item_type = "폴더"
            item_size = os.path.getsize(item_path)
            self.directory_tree.insert("", "end", text=item, values=(item_type, item_size))

        # 업데이트된 디렉토리 경로를 표시
        self.directory_path_label.config(text="현재 디렉토리: " + path)

    def double_click_directory(self, event):
        item = self.directory_tree.selection()[0]
        item_text = self.directory_tree.item(item)["text"]
        item_path = os.path.join(os.getcwd(), item_text)
        if item_text == "...(Parent Directory)":
            parent_dir = os.path.dirname(os.getcwd())
            os.chdir(parent_dir)
        elif os.path.isdir(item_path):
            os.chdir(item_path)
        self.update_directory_tree()

    def update_program_tree(self):
        path = os.getcwd()
        self.program_tree.delete(*self.program_tree.get_children())
        program_list = [{"프로그램": "프로그램1.exe", "LastModified": time.ctime(), "Size": "2MB"},
                        {"프로그램": "프로그램2.exe", "LastModified": time.ctime(), "Size": "1.5MB"},
                        {"프로그램": "프로그램3.exe", "LastModified": time.ctime(), "Size": "3MB"}]

        for program in program_list:
            self.program_tree.insert("", "end", text=program["프로그램"], values=(program["LastModified"], program["Size"]))

if __name__ == "__main__":
    root = tk.Tk()
    app = FileDirectoryManager(root)
    root.mainloop()