import os
import tkinter as tk
from tkinter import ttk
import time

class FileDirectoryManager:
    def __init__(self, root):
        self.root = root
        self.root.title("파일 디렉토리 관리")

        self.left_frame = ttk.Frame(root)
        self.left_frame.grid(row=0, column=0)

        # 1창 상단: 디렉토리 경로 표시 레이블 추가
        self.directory_path_label = ttk.Label(self.left_frame, text="현재 디렉토리: " + os.getcwd())
        self.directory_path_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

        # 1창: 파일 디렉토리 탐색
        self.directory_tree = ttk.Treeview(self.left_frame)
        self.directory_tree["columns"] = ("Type", "Size")
        self.directory_tree.heading("#0", text="이름", anchor=tk.W)
        self.directory_tree.heading("Type", text="타입", anchor=tk.W)
        self.directory_tree.heading("Size", text="크기", anchor=tk.W)
        self.directory_tree.column("#0", width=200, anchor=tk.W)
        self.directory_tree.column("Type", width=70, anchor=tk.W)
        self.directory_tree.column("Size", width=70, anchor=tk.W)
        self.directory_tree.grid(row=1, column=0, padx=10, pady=5)

        # 1창 스크롤바 추가
        directory_scrollbar = ttk.Scrollbar(self.left_frame, orient="vertical", command=self.directory_tree.yview)
        directory_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.directory_tree.config(yscrollcommand=directory_scrollbar.set)

        self.update_directory_tree()

        # 더블 클릭 이벤트 연결
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


class RecentEdittedManager:
    def __init__(self, root, program_list):
        self.root = root
        self.root.title("Recent Editted")

        self.right_frame = ttk.Frame(root)
        self.right_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=10, pady=10)

        # 2창 상단: Recent Editted
        self.frontend_text = ttk.Label(self.right_frame, text="Recent Editted", font=("Helvetica", 14, "bold"))
        self.frontend_text.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

        # 메뉴바 추가
        self.add_menu_bar()

        # 버튼 1
        self.markdown_button = ttk.Button(self.right_frame, text="버튼 1", command=self.empty_function_1, width=20)
        self.markdown_button.grid(row=1, column=0, pady=5, padx=(10, 5), sticky=tk.W)

        # 버튼 2
        self.pdf_button = ttk.Button(self.right_frame, text="버튼 2", command=self.empty_function_2, width=20)
        self.pdf_button.grid(row=1, column=0, pady=5, padx=(5, 10), sticky=tk.E)

        # 2창: 최근 변경된 프로그램
        self.program_frame = ttk.Frame(self.right_frame, borderwidth=2, relief="groove")
        self.program_frame.grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)

        self.program_tree = ttk.Treeview(self.program_frame, height=5)
        self.program_tree["columns"] = ("LastModified", "Size", "Safety")  # Add "Safety" column
        self.program_tree.heading("#0", text="프로그램", anchor=tk.W)
        self.program_tree.heading("LastModified", text="최근 수정일", anchor=tk.W)
        self.program_tree.heading("Size", text="크기", anchor=tk.W)
        self.program_tree.heading("Safety", text="안전도", anchor=tk.W)  # Header for "Safety" column
        self.program_tree.column("#0", width=200, anchor=tk.W)
        self.program_tree.column("LastModified", width=100, anchor=tk.W)
        self.program_tree.column("Size", width=70, anchor=tk.W)
        self.program_tree.column("Safety", width=70, anchor=tk.W)  # Width for "Safety" column
        self.program_tree.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

        # 2창 스크롤바 추가
        program_scrollbar = ttk.Scrollbar(self.program_frame, orient="vertical", command=self.program_tree.yview)
        program_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.program_tree.config(yscrollcommand=program_scrollbar.set)

        # 파일 안전도 체크 버튼 추가
        self.add_safety_buttons(program_list)

        self.update_program_tree(program_list)

    def update_program_tree(self, program_list):
        self.program_tree.delete(*self.program_tree.get_children())

        for program in program_list:
            item_id = self.program_tree.insert("", "end", text=program["프로그램"],
                                               values=(program["LastModified"], program["Size"], program["Safety"]))
            self.update_program_description_background(item_id, program["Safety"])

    def add_safety_buttons(self, program_list):
        self.safety_buttons = {}

        safety_frame = ttk.Frame(self.program_frame)
        safety_frame.grid(row=0, column=2, pady=5, padx=10, sticky=tk.W)

        for index, program in enumerate(program_list):
            safety_button = ttk.Button(safety_frame, text="안전", command=lambda i=index: self.toggle_safety(i), width=10)
            safety_button.grid(row=index, column=1, pady=2, padx=5, sticky=tk.E)
            self.safety_buttons[index] = safety_button

    def toggle_safety(self, index):
        program = program_list[index]
        if program["Safety"] == "안전":
            program["Safety"] = "위험"
        elif program["Safety"] == "위험":
            program["Safety"] = "고위험"
        elif program["Safety"] == "고위험":
            program["Safety"] = "안전"

        item_id = self.program_tree.get_children()[index]
        self.program_tree.set(item_id, "Safety", program["Safety"])
        self.update_program_description_background(item_id, program["Safety"])

    def update_program_description_background(self, item_id, safety_text):
        self.program_tree.tag_configure("Safe.Background", background="white")
        self.program_tree.tag_configure("Warning.Background", background="yellow")
        self.program_tree.tag_configure("Danger.Background", background="red")

        if safety_text == "안전":
            self.program_tree.item(item_id, tags=("Safe.Background",))
        elif safety_text == "위험":
            self.program_tree.item(item_id, tags=("Warning.Background",))
        elif safety_text == "고위험":
            self.program_tree.item(item_id, tags=("Danger.Background",))

    def add_menu_bar(self):
        # 메뉴바 생성
        menubar = tk.Menu(self.root)
        menubar.add_cascade(label="마크다운 문서 변환", command=self.convert_markdown)
        menubar.add_cascade(label="PDF 문서 변환", command=self.convert_pdf)

        # 메뉴바 적용
        self.root.config(menu=menubar)

    def convert_markdown(self):
        # 마크다운 변환 로직 구현
        pass

    def convert_pdf(self):
        # PDF 변환 로직 구현
        pass

    # 빈 함수 1
    def empty_function_1(self):
        pass

    # 빈 함수 2
    def empty_function_2(self):
        pass


if __name__ == "__main__":
    root1 = tk.Tk()
    app1 = FileDirectoryManager(root1)

    # 두 번째 창을 생성
    root2 = tk.Tk()
    program_list = [
        {"프로그램": "프로그램1.exe", "LastModified": time.ctime(), "Size": "2MB", "Safety": "안전"},
        {"프로그램": "프로그램2.exe", "LastModified": time.ctime(), "Size": "1.5MB", "Safety": "안전"},
        {"프로그램": "프로그램3.exe", "LastModified": time.ctime(), "Size": "3MB", "Safety": "고위험"},
        {"프로그램": "프로그램4.exe", "LastModified": time.ctime(), "Size": "1MB", "Safety": "안전"},
        {"프로그램": "프로그램5.exe", "LastModified": time.ctime(), "Size": "1MB", "Safety": "위험"},
    ]
    app2 = RecentEdittedManager(root2, program_list)
    root2.mainloop()
    root1.mainloop()
