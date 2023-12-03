from markdown import markdown
from .config.settings import DEBUG, BASE_DIR
from datetime import datetime, timedelta
import sqlite3
from .utils.MessageBox import confirm
from .database.utils import dictfetchall
from .config.utils import optionalIndex, process_f_string
from pyhtml2pdf import converter
from .cursor import change_cursor

import pathlib, os

COLOR_MAP = {
    "안전": "background: white; color: black;",
    "위험": "background: #ffc107; color: black;",
    "고위험": "background: #dc3545; color: white;",
    None: "background: white; color: black;"
}

def convert_time(time_string):
    dt = datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S.%f")
    return dt.timestamp()

def create_markdown_document(files, output_path:pathlib.Path|None=None) -> pathlib.Path|None:
    if len(files) == 0:
        if not confirm("기록된 파일 변경사항이 없습니다. 빈 보고서를 생성하시겠습니까?"):
            return None
    
    all_files_table = []
    time_sort_files = sorted(files, key=lambda x: x.get('logged_time'))
    for file in time_sort_files:
        con = "\n".join([_ for _ in process_f_string(f"""
            <tr style='{COLOR_MAP[file.get("safety")]}'>
                <td>{file.get("path")}</td>
                <td>{file.get("logged_time")}</td>
                <td>{file.get("file_size")}</td>
                <td>{file.get("safety")}</td>
            </tr>
        """).split("\n")])
        all_files_table.append(con)
    document_content = [
        f"""# {datetime.now().strftime("%Y년 %m월 %d일")} 파일변경 보고서""",
        "----",
        "",
        "## 변경된 파일 목록",
        "<table>\n"+
        "   <thead>\n"+
        "       <tr>\n"+
        "           <th>파일경로</th>\n"+
        "           <th>수정시각</th>\n"+
        "           <th>파일크기</th>\n"+
        "           <th>위험도</th>\n"+
        "       </tr>\n"+
        "   </thead>\n"+
        "   <tbody>"
    ]
    document_content += all_files_table
    document_content += [
        "   </tbody>",
        "</table>",
        "\n\n"
    ]
    
    # return 
    with sqlite3.connect(BASE_DIR / 'FEWT.sqlite3') as conn:
        highdanger_count = [file for file in files if file.get('safety') == '고위험'].__len__()
        document_content += [f"\n## 고위험 파일 목록 ({highdanger_count}개)\n"]
        cur = conn.cursor()
        for file in files:
            if file.get('safety') != '고위험':
                continue
            cur.execute("""
                SELECT content
                FROM fileContent
                WHERE file_path=?
                    AND record_time = ?
            """, [file.get('path').replace("\\", '/'), convert_time(file.get('logged_time'))])
            file_data = optionalIndex(dictfetchall(cur), 0, {}).get('content', 'None')
            ext = file.get('path').split('.')[-1]
            file_name = file.get('path').split("\\")[-1]
            document_content += [process_f_string(f"""
                ### {file_name}
                경로: {file.get('path')}
                
                수정 시각: {file.get('logged_time')}

                파일크기 : {file.get('file_size')}bytes
            """), f"""```{ext}\n{file_data}\n```""" "\n\n"]

        danger_count = [file for file in files if file.get('safety') == '위험'].__len__()
        document_content += [f"\n## 위험 파일 목록 ({danger_count}개)\n"]
        for file in files:
            if file.get('safety') != '위험':
                continue
            cur.execute("""
                SELECT content
                FROM fileContent
                WHERE file_path=?
                    AND record_time = ?
            """, [file.get('path').replace("\\", '/'), convert_time(file.get('logged_time'))])
            file_data = optionalIndex(dictfetchall(cur), 0, {}).get('content')
            ext = file.get('path').split('.')[-1]
            file_name = file.get('path').split("\\")[-1]
            document_content += [process_f_string(f"""
                ### {file_name}
                경로: {file.get('path')}
                
                수정 시각: {file.get('logged_time')}

                파일크기 : {file.get('file_size')}bytes
            """),f"""```{ext}\n{file_data}\n```""" "\n\n" , "\n\n"]
    document_content = "\n\n".join(document_content)
    
    if output_path is not None:
        with open(output_path, 'w', encoding='UTF8') as f:
            f.write(document_content)
        
        if confirm("마크다운 파일을 완성하였습니다. 마크다운 파일을 여시겠습니까?"):
            os.startfile(output_path)
    return document_content

def create_pdf(files, output_path:pathlib.Path):
    change_cursor("loading")
    doc_content = create_markdown_document(files, output_path=None)
    with open(BASE_DIR / '.output.markdown.html', 'w', encoding="UTF8") as f:
        f.write(f"""<link rel="stylesheet" href="./code-styles.css"/>""")
        f.write(markdown(doc_content, extensions=['fenced_code', 'codehilite']))
    converter.convert((BASE_DIR / '.output.markdown.html').as_uri(), output_path.__str__())
    if not DEBUG:
        os.remove(BASE_DIR / '.output.markdown.html')
    change_cursor("default")
    if confirm("PDF 파일이 완성되었습니다! 여시겠습니까?"):
        os.startfile(output_path)
    change_cursor("default")