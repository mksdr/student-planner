import customtkinter as ctk
import calendar
from datetime import datetime, date

class DatePickerDialog(ctk.CTkToplevel):
    def __init__(self, parent, initial_date_str, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("날짜 선택")
        self.geometry("350x400")
        
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        # 초기 날짜 설정 파싱
        try:
            init_d = datetime.strptime(initial_date_str, "%Y-%m-%d").date()
        except ValueError:
            init_d = date.today()
        
        self.year = init_d.year
        self.month = init_d.month

        self.setup_ui()
        self.draw_calendar()
        self.bind("<Escape>", lambda event: self.destroy())

    def setup_ui(self):
        # 년/월 네비게이션 헤더
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=15, pady=15)

        self.btn_prev = ctk.CTkButton(
            self.header, text="◀", width=35, height=30,
            fg_color=("gray85", "gray25"), text_color=("black", "white"),
            hover_color=("gray75", "gray35"), command=self.prev_month
        )
        self.btn_prev.pack(side="left")

        self.lbl_month = ctk.CTkLabel(
            self.header, text="",
            font=ctk.CTkFont(family="Inter", size=15, weight="bold")
        )
        self.lbl_month.pack(side="left", fill="x", expand=True)

        self.btn_next = ctk.CTkButton(
            self.header, text="▶", width=35, height=30,
            fg_color=("gray85", "gray25"), text_color=("black", "white"),
            hover_color=("gray75", "gray35"), command=self.next_month
        )
        self.btn_next.pack(side="right")

        # 달력 그리드 영역
        self.grid_frame = ctk.CTkFrame(self, fg_color=("gray95", "gray15"), corner_radius=8)
        self.grid_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def prev_month(self):
        if self.month == 1:
            self.month = 12
            self.year -= 1
        else:
            self.month -= 1
        self.draw_calendar()

    def next_month(self):
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        self.draw_calendar()

    def draw_calendar(self):
        self.lbl_month.configure(text=f"{self.year}년 {self.month:02d}월")

        # 이전 위젯 소멸
        for w in self.grid_frame.winfo_children():
            w.destroy()

        # 7열 7행 격자 매핑
        for col in range(7):
            self.grid_frame.grid_columnconfigure(col, weight=1, uniform="equal")
        for row in range(7):
            self.grid_frame.grid_rowconfigure(row, weight=1, uniform="equal")

        # 1. 요일 이름 그리기
        day_names = ["일", "월", "화", "수", "목", "금", "토"]
        day_colors = ["#e63946", "gray50", "gray50", "gray50", "gray50", "gray50", "#1c7ed6"]
        for col, (day, col_color) in enumerate(zip(day_names, day_colors)):
            lbl = ctk.CTkLabel(
                self.grid_frame, text=day, text_color=col_color, 
                font=ctk.CTkFont(size=11, weight="bold")
            )
            lbl.grid(row=0, column=col, sticky="nsew", pady=2)

        # 2. 날짜 격자 렌더링
        first_weekday, num_days = calendar.monthrange(self.year, self.month)
        start_col = (first_weekday + 1) % 7

        row = 1
        col = start_col

        for day in range(1, num_days + 1):
            date_str = f"{self.year}-{self.month:02d}-{day:02d}"
            
            # 주말 및 평일 색상 텍스트 지정
            lbl_color = "black" if col not in [0, 6] else ("#e63946" if col == 0 else "#1c7ed6")
            if ctk.get_appearance_mode() == "Dark":
                lbl_color = "white" if col not in [0, 6] else ("#ff6b6b" if col == 0 else "#4dadf7")

            btn = ctk.CTkButton(
                self.grid_frame, 
                text=str(day),
                fg_color=("white", "gray22"),
                text_color=lbl_color,
                hover_color=("gray85", "gray30"),
                corner_radius=4,
                font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                command=lambda d_str=date_str: self.select_date(d_str)
            )
            btn.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)

            col += 1
            if col > 6:
                col = 0
                row += 1

    def select_date(self, selected_date_str):
        self.callback(selected_date_str)
        self.destroy()


class TaskEditor(ctk.CTkToplevel):
    def __init__(self, parent, data_manager, task_id=None, refresh_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.data_manager = data_manager
        self.task_id = task_id
        self.refresh_callback = refresh_callback

        # 1. 모달 팝업 창 정보 설정
        self.title("수행평가/과제 추가 및 편집" if not task_id else "수행평가/과제 상세 및 편집")
        self.geometry("550x700")
        
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        # 기존 일정 데이터 로드
        self.task_data = None
        if task_id:
            self.task_data = self.data_manager.get_task_by_id(task_id)

        # 하위 체크리스트 상태
        self.checklist_items = []

        self.setup_ui()
        if self.task_data:
            self.load_task_data()
        self.bind("<Escape>", lambda event: self.destroy())

    def setup_ui(self):
        # 메인 스크롤 패널
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # ① 과목 선택 (드롭다운)
        self.lbl_subject = ctk.CTkLabel(
            self.scroll_frame, 
            text="과목명", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_subject.pack(anchor="w", pady=(5, 5))
        
        subjects = list(self.data_manager.settings.get("subject_colors", {}).keys())
        if not subjects:
            subjects = ["국어", "수학 II", "영어", "정보", "물리 I"]
        self.combo_subject = ctk.CTkComboBox(self.scroll_frame, values=subjects)
        self.combo_subject.pack(fill="x", pady=(0, 15))

        # ② 일정 제목
        self.lbl_title = ctk.CTkLabel(
            self.scroll_frame, 
            text="일정 및 과제 제목", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_title.pack(anchor="w", pady=(5, 5))
        self.ent_title = ctk.CTkEntry(
            self.scroll_frame, 
            placeholder_text="예: 물리 실험 기획서 작성"
        )
        self.ent_title.pack(fill="x", pady=(0, 15))

        # ③ 마감 일시 선택기 (가로 병렬 및 시각화 전형 교체)
        time_container = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        time_container.pack(fill="x", pady=(0, 15))
        time_container.grid_columnconfigure(0, weight=1)
        time_container.grid_columnconfigure(1, weight=1)

        # 마감 날짜 선택기
        self.lbl_date = ctk.CTkLabel(
            time_container, 
            text="마감 날짜", 
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.lbl_date.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.date_select_frame = ctk.CTkFrame(time_container, fg_color="transparent")
        self.date_select_frame.grid(row=1, column=0, sticky="ew", padx=(0, 10))
        
        self.ent_date = ctk.CTkEntry(self.date_select_frame, placeholder_text="YYYY-MM-DD")
        self.ent_date.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.ent_date.insert(0, datetime.now().strftime("%Y-%m-%d"))  # 오늘 자동기입
        
        self.btn_pick_date = ctk.CTkButton(
            self.date_select_frame, 
            text="📅", 
            width=32, 
            fg_color=("gray85", "gray25"), 
            text_color=("black", "white"),
            hover_color=("gray75", "gray35"),
            command=self.open_date_picker
        )
        self.btn_pick_date.pack(side="right")

        # 마감 시간 선택기 (콤보박스 2중 결합)
        self.lbl_time = ctk.CTkLabel(
            time_container, 
            text="마감 시간", 
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.lbl_time.grid(row=0, column=1, sticky="w", pady=(0, 5))
        
        self.time_select_frame = ctk.CTkFrame(time_container, fg_color="transparent")
        self.time_select_frame.grid(row=1, column=1, sticky="ew", padx=(10, 0))
        
        hours = [f"{i:02d}" for i in range(24)]
        self.combo_hour = ctk.CTkComboBox(self.time_select_frame, values=hours, width=65)
        self.combo_hour.pack(side="left", padx=(0, 5))
        self.combo_hour.set("23") # 기본값
        
        self.lbl_colon = ctk.CTkLabel(self.time_select_frame, text=":", font=ctk.CTkFont(size=14, weight="bold"))
        self.lbl_colon.pack(side="left", padx=2)
        
        minutes = [f"{i:02d}" for i in range(0, 60, 5)]
        if "59" not in minutes:
            minutes.append("59")
        self.combo_minute = ctk.CTkComboBox(self.time_select_frame, values=minutes, width=65)
        self.combo_minute.pack(side="left", padx=(5, 0))
        self.combo_minute.set("59") # 기본값

        # ④ 중요도 설정
        self.var_priority = ctk.BooleanVar(value=False)
        self.chk_priority = ctk.CTkCheckBox(
            self.scroll_frame, 
            text="⭐ 중요 일정으로 지정 (D-day 및 목록에서 하이라이트)", 
            variable=self.var_priority,
            font=ctk.CTkFont(size=13)
        )
        self.chk_priority.pack(anchor="w", pady=(5, 20))

        # ⑤ 상세 내용 텍스트 영역
        self.lbl_desc = ctk.CTkLabel(
            self.scroll_frame, 
            text="상세 내용 설명", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_desc.pack(anchor="w", pady=(5, 5))
        self.txt_desc = ctk.CTkTextbox(self.scroll_frame, height=140)
        self.txt_desc.pack(fill="x", pady=(0, 20))

        # ⑥ 하위 체크리스트 영역
        self.lbl_checklist = ctk.CTkLabel(
            self.scroll_frame, 
            text="하위 체크리스트 (선택사항 - 존재할 시 진행률 표시)", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_checklist.pack(anchor="w", pady=(5, 5))

        chk_input_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        chk_input_frame.pack(fill="x", pady=(0, 10))
        
        self.ent_chk_item = ctk.CTkEntry(
            chk_input_frame, 
            placeholder_text="하위 작업 추가 (예: 자료 조사)"
        )
        self.ent_chk_item.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.ent_chk_item.bind("<Return>", lambda event: self.add_checklist_item())
        
        self.btn_chk_add = ctk.CTkButton(
            chk_input_frame, 
            text="추가", 
            width=60, 
            command=self.add_checklist_item
        )
        self.btn_chk_add.pack(side="right")

        self.checklist_area = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.checklist_area.pack(fill="x", pady=(0, 20))

        # ⑦ 저장, 삭제 및 하단 동작 버튼
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(fill="x", side="bottom", padx=20, pady=20)

        self.btn_save = ctk.CTkButton(
            self.btn_frame, 
            text="저장", 
            fg_color="#2b8a3e", 
            hover_color="#237032", 
            width=100, 
            command=self.save_task
        )
        self.btn_save.pack(side="right", padx=(10, 0))

        self.btn_cancel = ctk.CTkButton(
            self.btn_frame, 
            text="취소", 
            fg_color="gray", 
            hover_color="#555555", 
            width=80, 
            command=self.destroy
        )
        self.btn_cancel.pack(side="right")

        if self.task_id:
            self.btn_delete = ctk.CTkButton(
                self.btn_frame, 
                text="삭제", 
                fg_color="#c92a2a", 
                hover_color="#a61e1e", 
                width=80, 
                command=self.delete_task
            )
            self.btn_delete.pack(side="left")

    def open_date_picker(self):
        """날짜 픽커 다이얼로그 창을 띄웁니다."""
        DatePickerDialog(self, self.ent_date.get().strip(), self.set_selected_date)

    def set_selected_date(self, date_str):
        """캘린더 다이얼로그로부터 콜백되어 날짜를 필드에 채워넣습니다."""
        self.ent_date.delete(0, "end")
        self.ent_date.insert(0, date_str)

    def load_task_data(self):
        t = self.task_data
        self.combo_subject.set(t.get("subject", ""))
        
        self.ent_title.delete(0, "end")
        self.ent_title.insert(0, t.get("title", ""))
        
        self.ent_date.delete(0, "end")
        self.ent_date.insert(0, t.get("due_date", ""))
        
        due_time = t.get("due_time", "23:59")
        try:
            h, m = due_time.split(":")
            self.combo_hour.set(h)
            self.combo_minute.set(m)
        except ValueError:
            self.combo_hour.set("23")
            self.combo_minute.set("59")
        
        self.var_priority.set(t.get("priority", False))
        self.txt_desc.insert("1.0", t.get("description", ""))

        self.checklist_items = list(t.get("checklist", []))
        self.render_checklist()

    def add_checklist_item(self):
        text = self.ent_chk_item.get().strip()
        if text:
            self.checklist_items.append({"item": text, "done": False})
            self.ent_chk_item.delete(0, "end")
            if self.task_id and self.task_data:
                self.task_data["checklist"] = self.checklist_items
                self.data_manager.save_tasks()
                if self.refresh_callback:
                    self.refresh_callback()
            self.render_checklist()

    def remove_checklist_item(self, idx):
        self.checklist_items.pop(idx)
        if self.task_id and self.task_data:
            self.task_data["checklist"] = self.checklist_items
            self.data_manager.save_tasks()
            if self.refresh_callback:
                self.refresh_callback()
        self.render_checklist()

    def toggle_checklist_item(self, idx, is_done):
        self.checklist_items[idx]["done"] = is_done
        if self.task_id and self.task_data:
            self.task_data["checklist"] = self.checklist_items
            self.data_manager.save_tasks()
            if self.refresh_callback:
                self.refresh_callback()
        self.render_checklist()

    def render_checklist(self):
        for widget in self.checklist_area.winfo_children():
            widget.destroy()

        for i, item in enumerate(self.checklist_items):
            item_card = ctk.CTkFrame(self.checklist_area, fg_color=("gray95", "gray15"), height=36)
            item_card.pack(fill="x", pady=3)
            
            chk_var = ctk.BooleanVar(value=item.get("done", False))
            chk = ctk.CTkCheckBox(
                item_card, 
                text=item['item'], 
                variable=chk_var,
                font=ctk.CTkFont(size=12, overstrike=item.get("done", False)),
                command=lambda index=i, cv=chk_var: self.toggle_checklist_item(index, cv.get())
            )
            chk.pack(side="left", padx=12, fill="x", expand=True)

            btn_del = ctk.CTkButton(
                item_card, 
                text="✕", 
                width=24, 
                height=24,
                fg_color="transparent",
                hover_color=("gray85", "gray25"),
                text_color="gray50",
                command=lambda index=i: self.remove_checklist_item(index)
            )
            btn_del.pack(side="right", padx=8)

    def save_task(self):
        subject = self.combo_subject.get().strip()
        title = self.ent_title.get().strip()
        due_date = self.ent_date.get().strip()
        due_time = f"{self.combo_hour.get().strip()}:{self.combo_minute.get().strip()}"
        priority = self.var_priority.get()
        description = self.txt_desc.get("1.0", "end-1c").strip()

        # 데이터 입력 무결성 검증
        if not subject or not title:
            self.combo_subject.configure(border_color="red" if not subject else ("gray65", "gray35"))
            self.ent_title.configure(border_color="red" if not title else ("gray65", "gray35"))
            return

        # 날짜 포맷 검증
        try:
            datetime.strptime(due_date, "%Y-%m-%d")
            self.ent_date.configure(border_color=("gray65", "gray35"))
        except ValueError:
            self.ent_date.configure(border_color="red")
            return

        # 시간 포맷 검증
        try:
            datetime.strptime(due_time, "%H:%M")
        except ValueError:
            return

        if not self.task_id:
            # 추가 모드
            task_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            new_task = {
                "id": task_id,
                "subject": subject,
                "title": title,
                "due_date": due_date,
                "due_time": due_time,
                "priority": priority,
                "completed": False,
                "description": description,
                "checklist": self.checklist_items
            }
            self.data_manager.add_task(new_task)
        else:
            # 편집 모드
            updated_task = {
                "id": self.task_id,
                "subject": subject,
                "title": title,
                "due_date": due_date,
                "due_time": due_time,
                "priority": priority,
                "completed": self.task_data.get("completed", False),
                "description": description,
                "checklist": self.checklist_items
            }
            self.data_manager.update_task(self.task_id, updated_task)

        if self.refresh_callback:
            self.refresh_callback()
        
        self.destroy()

    def delete_task(self):
        if self.task_id:
            self.data_manager.delete_task(self.task_id)
            if self.refresh_callback:
                self.refresh_callback()
            self.destroy()


class TaskViewer(ctk.CTkToplevel):
    def __init__(self, parent, data_manager, task_id, refresh_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.data_manager = data_manager
        self.task_id = task_id
        self.refresh_callback = refresh_callback

        self.title("수행평가/과제 상세 조회")
        self.geometry("520x650")
        
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        self.task_data = self.data_manager.get_task_by_id(task_id)
        self.checklist_items = list(self.task_data.get("checklist", [])) if self.task_data else []

        self.setup_ui()
        if self.task_data:
            self.load_task_data()
        self.bind("<Escape>", lambda event: self.destroy())

    def setup_ui(self):
        # 메인 스크롤 영역
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # ① 과목 뱃지 영역
        self.lbl_subject_title = ctk.CTkLabel(
            self.scroll_frame, text="과목명", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_subject_title.pack(anchor="w", pady=(5, 2))
        
        self.badge_frame = ctk.CTkFrame(self.scroll_frame, height=32, corner_radius=6)
        self.badge_frame.pack(anchor="w", pady=(0, 15))
        
        self.lbl_subject = ctk.CTkLabel(
            self.badge_frame, text="", font=ctk.CTkFont(size=13, weight="bold"), text_color="white"
        )
        self.lbl_subject.pack(padx=15, pady=4)

        # ② 일정 제목
        self.lbl_title_title = ctk.CTkLabel(
            self.scroll_frame, text="일정 및 과제 제목", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_title_title.pack(anchor="w", pady=(5, 2))
        
        self.lbl_title = ctk.CTkLabel(
            self.scroll_frame, text="", font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w", justify="left"
        )
        self.lbl_title.pack(fill="x", pady=(0, 15))

        # ③ 마감 일시 정보
        self.lbl_due_title = ctk.CTkLabel(
            self.scroll_frame, text="마감 기한 및 시간", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_due_title.pack(anchor="w", pady=(5, 2))
        
        self.lbl_due = ctk.CTkLabel(
            self.scroll_frame, text="", font=ctk.CTkFont(size=14, weight="normal"),
            anchor="w"
        )
        self.lbl_due.pack(fill="x", pady=(0, 15))

        # ④ 중요도 설정 여부
        self.chk_priority = ctk.CTkCheckBox(
            self.scroll_frame, 
            text="⭐ 중요 일정으로 지정됨", 
            state="disabled",
            font=ctk.CTkFont(size=13)
        )
        self.chk_priority.pack(anchor="w", pady=(5, 20))

        # ⑤ 상세 설명
        self.lbl_desc_title = ctk.CTkLabel(
            self.scroll_frame, text="상세 설명 내용", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_desc_title.pack(anchor="w", pady=(5, 2))
        
        self.txt_desc = ctk.CTkTextbox(self.scroll_frame, height=140)
        self.txt_desc.pack(fill="x", pady=(0, 20))

        # ⑥ 하위 체크리스트 영역 (읽기 모드로 제공하되, 체크 토글은 지원)
        self.lbl_checklist_title = ctk.CTkLabel(
            self.scroll_frame, text="하위 체크리스트 진행 현황", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_checklist_title.pack(anchor="w", pady=(5, 2))

        self.checklist_area = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.checklist_area.pack(fill="x", pady=(0, 20))

        # ⑦ 하단 닫기 단일 동작
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(fill="x", side="bottom", padx=20, pady=20)

        self.btn_close = ctk.CTkButton(
            self.btn_frame, 
            text="닫기", 
            fg_color="gray", 
            hover_color="#555555", 
            height=36,
            command=self.destroy
        )
        self.btn_close.pack(fill="x")

    def load_task_data(self):
        t = self.task_data
        
        sub_name = t.get("subject", "")
        self.lbl_subject.configure(text=sub_name)
        sub_colors = self.data_manager.settings.get("subject_colors", {})
        bg_col = sub_colors.get(sub_name, "gray50")
        self.badge_frame.configure(fg_color=bg_col)
        
        self.lbl_title.configure(text=t.get("title", ""))
        
        due_date = t.get("due_date", "")
        due_time = t.get("due_time", "")
        self.lbl_due.configure(text=f"📅  {due_date}   ⏰  {due_time}")
        
        if t.get("priority", False):
            self.chk_priority.select()
        else:
            self.chk_priority.deselect()
            
        self.txt_desc.insert("1.0", t.get("description", ""))
        self.txt_desc.configure(state="disabled")

        self.render_checklist()

    def toggle_checklist_item(self, idx, is_done):
        self.checklist_items[idx]["done"] = is_done
        if self.task_data:
            self.task_data["checklist"] = self.checklist_items
            self.data_manager.save_tasks()
            if self.refresh_callback:
                self.refresh_callback()
        self.render_checklist()

    def render_checklist(self):
        for widget in self.checklist_area.winfo_children():
            widget.destroy()

        if not self.checklist_items:
            lbl_none = ctk.CTkLabel(
                self.checklist_area, 
                text="등록된 하위 체크리스트가 없습니다.", 
                text_color="gray50", 
                font=ctk.CTkFont(size=12, slant="italic")
            )
            lbl_none.pack(anchor="w", pady=5)
            return

        for i, item in enumerate(self.checklist_items):
            item_card = ctk.CTkFrame(self.checklist_area, fg_color=("gray95", "gray15"), height=36)
            item_card.pack(fill="x", pady=3)
            
            chk_var = ctk.BooleanVar(value=item.get("done", False))
            chk = ctk.CTkCheckBox(
                item_card, 
                text=item['item'], 
                variable=chk_var,
                font=ctk.CTkFont(size=12, overstrike=item.get("done", False)),
                command=lambda index=i, cv=chk_var: self.toggle_checklist_item(index, cv.get())
            )
            chk.pack(side="left", padx=12, fill="x", expand=True)
