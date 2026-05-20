import customtkinter as ctk
import random
from data_manager import DataManager

class TimetableCellEditor(ctk.CTkToplevel):
    def __init__(self, parent, data_manager, day_key, period_idx, refresh_callback):
        super().__init__(parent)
        self.data_manager = data_manager
        self.day_key = day_key
        self.period_idx = period_idx
        self.refresh_callback = refresh_callback

        # 모달 설정
        day_names_kr = {"mon": "월", "tue": "화", "wed": "수", "thu": "목", "fri": "금"}
        self.title(f"{day_names_kr[day_key]}요일 {period_idx + 1}교시 편집")
        self.geometry("380x300")
        
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        # 현재 저장된 값 로드
        day_data = self.data_manager.settings.get("timetable", {}).get(day_key, [])
        self.current_data = day_data[period_idx] if period_idx < len(day_data) else {"subject": "", "teacher": ""}

        self.setup_ui()
        self.bind("<Escape>", lambda event: self.destroy())

    def setup_ui(self):
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=25, pady=25)

        # 1. 안내 헤더
        day_names_kr = {"mon": "월", "tue": "화", "wed": "수", "thu": "목", "fri": "금"}
        self.header_lbl = ctk.CTkLabel(
            self.main_container,
            text=f"📌 {day_names_kr[self.day_key]}요일 {self.period_idx + 1}교시 정보 입력",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.header_lbl.pack(anchor="w", pady=(0, 15))

        # 2. 과목명 입력
        self.lbl_sub = ctk.CTkLabel(self.main_container, text="과목명", font=ctk.CTkFont(weight="bold"))
        self.lbl_sub.pack(anchor="w", pady=(5, 2))
        self.ent_sub = ctk.CTkEntry(self.main_container, placeholder_text="예: 수학 II")
        self.ent_sub.pack(fill="x", pady=(0, 10))
        self.ent_sub.insert(0, self.current_data.get("subject", ""))

        # 3. 담당 교사 입력
        self.lbl_teacher = ctk.CTkLabel(self.main_container, text="담당 교사", font=ctk.CTkFont(weight="bold"))
        self.lbl_teacher.pack(anchor="w", pady=(5, 2))
        self.ent_teacher = ctk.CTkEntry(self.main_container, placeholder_text="예: 홍길동 선생님")
        self.ent_teacher.pack(fill="x", pady=(0, 20))
        self.ent_teacher.insert(0, self.current_data.get("teacher", ""))

        # 4. 하단 버튼
        self.btn_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.btn_frame.pack(fill="x")

        self.btn_save = ctk.CTkButton(
            self.btn_frame, text="저장", fg_color="#2b8a3e", hover_color="#237032",
            width=80, command=self.save_cell
        )
        self.btn_save.pack(side="right", padx=(10, 0))

        self.btn_cancel = ctk.CTkButton(
            self.btn_frame, text="취소", fg_color="gray", hover_color="#555555",
            width=70, command=self.destroy
        )
        self.btn_cancel.pack(side="right")

    def save_cell(self):
        sub = self.ent_sub.get().strip()
        teacher = self.ent_teacher.get().strip()

        # 데이터 업데이트
        timetable = self.data_manager.settings.get("timetable", {})
        if self.day_key not in timetable:
            timetable[self.day_key] = [{"subject": "", "teacher": ""} for _ in range(7)]

        timetable[self.day_key][self.period_idx] = {
            "subject": sub,
            "teacher": teacher
        }

        # 새로운 과목이 들어왔을 때 색상이 정의되어 있지 않으면 파스텔 계열 무작위 자동 배정 (생기부 알고리즘 요소)
        if sub:
            sub_colors = self.data_manager.settings.get("subject_colors", {})
            if sub not in sub_colors:
                pastel_palette = ["#FF6B6B", "#FF922B", "#FCC419", "#51CF66", "#339AF0", "#845EF7", "#CC5DE8", "#F06595", "#20C997", "#94D82D"]
                sub_colors[sub] = random.choice(pastel_palette)
                self.data_manager.settings["subject_colors"] = sub_colors

        self.data_manager.save_settings()
        self.refresh_callback()
        self.destroy()


class TimetableView(ctk.CTkFrame):
    def __init__(self, parent, controller, data_manager):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.data_manager = data_manager

        self.setup_ui()
        self.refresh_table()

    def setup_ui(self):
        # 상단 타이틀 영역
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=30, pady=(25, 10))

        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="📅 학급 시간표", 
            font=ctk.CTkFont(family="Inter", size=24, weight="bold")
        )
        self.title_label.pack(side="left")

        self.lbl_guide = ctk.CTkLabel(
            self.header_frame, 
            text="💡 각 교시를 클릭하면 과목명과 교사명을 편집할 수 있습니다.",
            font=ctk.CTkFont(size=12), text_color="gray"
        )
        self.lbl_guide.pack(side="right", padx=10, pady=10)

        # 시간표 그리드 전체 컨테이너
        self.table_container = ctk.CTkFrame(self, fg_color=("gray95", "gray15"), corner_radius=12)
        self.table_container.pack(fill="both", expand=True, padx=30, pady=(5, 20))

    def refresh_table(self):
        # 이전 위젯 전체 파괴
        for widget in self.table_container.winfo_children():
            widget.destroy()

        # 그리드 가중치 비율 설정 (0열은 교시 레이블용 고정, 1~5열은 요일용 균등 분배)
        self.table_container.grid_columnconfigure(0, weight=1, minsize=60)
        for col in range(1, 6):
            self.table_container.grid_columnconfigure(col, weight=2, uniform="equal")

        # 0행은 요일 헤더, 1~7행은 교시 데이터용 비율 분할
        for row in range(8):
            self.table_container.grid_rowconfigure(row, weight=1, uniform="equal")

        # 1. 요일 헤더 그리기
        days_header = ["월요일", "화요일", "수요일", "목요일", "금요일"]
        # 빈 칸 (0열 0행)
        empty_lbl = ctk.CTkLabel(self.table_container, text="", font=ctk.CTkFont(size=12))
        empty_lbl.grid(row=0, column=0, sticky="nsew")
        
        for col_idx, day_name in enumerate(days_header, start=1):
            lbl = ctk.CTkLabel(
                self.table_container, text=day_name, 
                font=ctk.CTkFont(family="Inter", size=14, weight="bold")
            )
            lbl.grid(row=0, column=col_idx, sticky="nsew", pady=5)

        # 2. 좌측 교시 번호 라벨 그리기 (1~7교시)
        for period in range(1, 8):
            lbl = ctk.CTkLabel(
                self.table_container, text=f"{period}교시",
                font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                text_color="gray50"
            )
            lbl.grid(row=period, column=0, sticky="nsew")

        # 3. 시간표 셀 렌더링
        days_keys = ["mon", "tue", "wed", "thu", "fri"]
        timetable_data = self.data_manager.settings.get("timetable", {})
        sub_colors = self.data_manager.settings.get("subject_colors", {})

        for col_idx, day_key in enumerate(days_keys, start=1):
            day_list = timetable_data.get(day_key, [])
            
            for period_idx in range(7):
                # 데이터 유효성 방어 코드
                cell_data = day_list[period_idx] if period_idx < len(day_list) else {"subject": "", "teacher": ""}
                
                subject = cell_data.get("subject", "")
                teacher = cell_data.get("teacher", "")

                # 과목 배경색 설정 (과목이 지정된 경우 settings.json의 칼라 매핑)
                cell_color = sub_colors.get(subject, ("gray90", "gray22")) if subject else ("gray90", "gray22")

                # 셀 컨테이너 (둥근 카드 형태)
                # 과목이 기입되었으면 둥근 카드 배경에 과목 컬러 입히기
                cell_frame = ctk.CTkFrame(
                    self.table_container,
                    fg_color=cell_color if subject else ("gray90", "gray20"),
                    border_color=("gray80", "gray25") if not subject else None,
                    border_width=1 if not subject else 0,
                    corner_radius=6
                )
                cell_frame.grid(row=period_idx + 1, column=col_idx, sticky="nsew", padx=3, pady=3)

                # 셀 내부 라벨 배치
                if subject:
                    # 대비를 위해 폰트 색상을 흰색으로 고정 (과목 칼라가 지정된 경우)
                    text_color = "white"
                    
                    lbl_sub = ctk.CTkLabel(
                        cell_frame, text=subject,
                        font=ctk.CTkFont(size=13, weight="bold"),
                        text_color=text_color
                    )
                    lbl_sub.pack(expand=True, pady=(6, 0))

                    teacher_text = f"({teacher})" if teacher else ""
                    lbl_teach = ctk.CTkLabel(
                        cell_frame, text=teacher_text,
                        font=ctk.CTkFont(size=10, weight="normal"),
                        text_color="white"
                    )
                    lbl_teach.pack(expand=True, pady=(0, 6))
                else:
                    # 빈 칸일 때의 플레이스홀더
                    lbl_empty = ctk.CTkLabel(
                        cell_frame, text="-",
                        font=ctk.CTkFont(size=12),
                        text_color="gray50"
                    )
                    lbl_empty.pack(expand=True)

                # 마우스 클릭 바인딩
                # 클로저 변수 스코프 묶기 위해 인자 지정
                self.bind_click_event(cell_frame, day_key, period_idx)
                if cell_frame.winfo_children():
                    for child in cell_frame.winfo_children():
                        self.bind_click_event(child, day_key, period_idx)

    def bind_click_event(self, widget, day_key, period_idx):
        widget.bind(
            "<Button-1>", 
            lambda event, dk=day_key, pi=period_idx: self.open_cell_editor(dk, pi)
        )

    def open_cell_editor(self, day_key, period_idx):
        TimetableCellEditor(
            self.winfo_toplevel(), self.data_manager, 
            day_key, period_idx, self.refresh_table
        )
