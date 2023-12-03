## 시스템 보안(AICS306)
----
### FEWT
File Explorer With Tracking

파일 탐색기에 실시간으로 변조된 파일을 추적하고 보여주는 프로그램.

### 팀원
- 2019270116 인공지능사이버보안학과 고용훈 **Backend dev**
- 2022272001 스마트도시학부 박재형 **Leader / DB, Backend dev.**
- 2019270123 인공지능사이버보안학과 배강민 **Frontend dev.**


## 설치방법
```powershell
git clone git@github.com:explainpark101/KU-system-sec.git
python -m venv myvenv
.\myvenv\Scripts\pip.exe install -r requirements.txt
.\myvenv\Scripts\python.exe manage.py
```

기본적으로 프로그램을 실행하면, **C:\\Users\\{Username}** 디렉토리의 변경사항을 트래킹합니다.

변경사항이 저장된 database를 초기화하려면 
```powershell
python manage.py -f [watch-directory]
```

특정 디렉토리의 변경사항만 확인하려면
```powershell
python manage.py [watch-directory]
```

### 파일변경사항 트래킹 블랙리스트
`apps/config/settings.py` 의 `TRACKING_IGNORE_LIST` 항목을 수정하시면 됩니다.

해당 리스트에 포함되어있는 디렉토리는 변경사항에 대한 로그를 남기지 않습니다.