# 학생 플래너 (Student Planner)

학생의 수행평가와 과제를 한눈에 관리할 수 있도록 만든 Python 데스크톱 플래너입니다.  
달력, 목록, 시간표, 설정 화면을 통해 학업 일정을 체계적으로 정리할 수 있습니다.

## 주요 기능

- **달력 화면**
  - 월별 일정 확인
  - 날짜 더블클릭으로 빠른 일정 추가
  - 마감 임박(D-day) 대시보드 제공
- **목록 화면**
  - 일정/과제 카드형 목록 표시
  - 완료 상태, 과목, 중요도(⭐) 필터링
  - 체크리스트 진행률 표시
- **시간표 화면**
  - 월\~금, 1~7교시 시간표 편집
  - 과목별 색상 자동 매핑
- **설정 화면**
  - 라이트/다크/시스템 테마 전환
  - 데이터 백업/복구(JSON)
  - 전체/일정/시간표 범위별 초기화

## 기술 스택

- Python 3
- CustomTkinter
- JSON 파일 기반 로컬 데이터 저장

## 실행 방법

1. 저장소 루트로 이동합니다.
2. 필요 시 가상환경을 생성/활성화합니다.
3. 의존성을 설치합니다.
4. 앱을 실행합니다.

```bash
pip install customtkinter
python main.py
```

## 데이터 파일

- `tasks.json`: 일정/과제 데이터 저장
- `settings.json`: 테마, 과목 색상, 시간표 설정 저장

앱 실행 시 파일이 없으면 기본값으로 자동 생성됩니다.

## 프로젝트 구조

```text
student-planner/
├── main.py
├── data_manager.py
├── settings.json
├── tasks.json
└── views/
    ├── calendar_view.py
    ├── list_view.py
    ├── settings_view.py
    ├── task_editor.py
    └── timetable_view.py
```

## 라이선스

이 프로젝트는 `LICENSE` 파일의 내용을 따릅니다.
