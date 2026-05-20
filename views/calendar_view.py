import customtkinter as ctk
import calendar
from datetime import datetime, date
from views.task_editor import TaskEditor, TaskViewer

class CalendarView(ctk.CTkFrame):
    def __init__(self, parent, controller, data_manager):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.data_manager = data_manager

        # 현재 달력 기준 일자 설정
        today = date.today()
        self.current_year = today.year
        self.current_month = today.month
        self.click_timer = None

        # 격자 및 레이아웃 설정 (자식 크기 변화에 의한 레이아웃 비율 붕괴 방지용 uniform 및 minsize 지정)
        self.grid_columnconfigure(0, weight=3, uniform="main_layout", minsize=600)  # 좌측 캘린더 영역 (75%)
        self.grid_columnconfigure(1, weight=1, uniform="main_layout", minsize=240)  # 우측 대시보드 영역 (25%)
        self.grid_rowconfigure(0, weight=1)

        self.setup_ui()
        self.refresh_view()

    def setup_ui(self):
        # ==========================================
        # 1. 좌측 영역 (캘린더 헤더 & 달력 판)
        # ==========================================
        self.left_container = ctk.CTkFrame(self, fg_color="transparent")
        self.left_container.grid(row=0, column=0, sticky="nsew", padx=(10, 10), pady=10)
        self.left_container.grid_columnconfigure(0, weight=1)
        self.left_container.grid_rowconfigure(1, weight=1)  # 캘린더 바디 행 확장

        self.cal_header = ctk.CTkFrame(self.left_container, fg_color="transparent")
        self.cal_header.grid(row=0, column=0, pady=(10, 15), sticky="ew")
        
        self.btn_prev = ctk.CTkButton(
            self.cal_header, text="◀", width=40, height=32, 
            fg_color=("gray85", "gray25"), text_color=("black", "white"),
            hover_color=("gray75", "gray35"), command=self.prev_month
        )
        self.btn_prev.pack(side="left", padx=5)

        self.lbl_month = ctk.CTkLabel(
            self.cal_header, text="2026년 05월",
            font=ctk.CTkFont(family="Inter", size=20, weight="bold")
        )
        self.lbl_month.pack(side="left", padx=20)

        self.btn_next = ctk.CTkButton(
            self.cal_header, text="▶", width=40, height=32,
            fg_color=("gray85", "gray25"), text_color=("black", "white"),
            hover_color=("gray75", "gray35"), command=self.next_month
        )
        self.btn_next.pack(side="left", padx=5)

        # 캘린더 날짜 입력 바로가기 가이드 텍스트
        self.lbl_guide = ctk.CTkLabel(
            self.cal_header, text="💡 날짜 빈 칸을 더블 클릭하면 해당 날짜로 새 과제를 등록합니다.",
            font=ctk.CTkFont(size=11), text_color="gray"
        )
        self.lbl_guide.pack(side="right", padx=10)

        # 1.2. 캘린더 격자판 프레임
        self.cal_body = ctk.CTkFrame(self.left_container, fg_color=("gray95", "gray15"), corner_radius=12)
        self.cal_body.grid(row=1, column=0, sticky="nsew")

        # ==========================================
        # 2. 우측 영역 (오늘의 대시보드 - 임박한 일정 요약)
        # ==========================================
        self.right_container = ctk.CTkFrame(self, fg_color=("gray95", "gray15"), corner_radius=12)
        self.right_container.grid(row=0, column=1, sticky="nsew", padx=(10, 10), pady=10)
        
        self.dash_title = ctk.CTkLabel(
            self.right_container, text="🔥 마감 임박 요약",
            font=ctk.CTkFont(family="Inter", size=16, weight="bold")
        )
        self.dash_title.pack(anchor="w", padx=20, pady=(20, 10))

        # 스크롤 가능한 대시보드 리스트
        self.dash_scroll = ctk.CTkScrollableFrame(self.right_container, fg_color="transparent")
        self.dash_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 15))

    # --- 달력 탐색 함수 ---
    def prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.refresh_view()

    def next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.refresh_view()

    # --- 뷰 갱신 컨트롤러 ---
    def refresh_view(self):
        self.lbl_month.configure(text=f"{self.current_year}년 {self.current_month:02d}월")
        self.draw_calendar_grid()
        self.draw_dashboard()

    # --- 달력 그리기 알고리즘 ---
    def draw_calendar_grid(self):
        # 이전 격자 요소 파괴
        for widget in self.cal_body.winfo_children():
            widget.destroy()

        # 그리드 구성: 7열(요일) 및 7행(1행 요일명, 6행 날짜 그리드)
        for col in range(7):
            self.cal_body.grid_columnconfigure(col, weight=1, uniform="equal")
        for row in range(7):
            self.cal_body.grid_rowconfigure(row, weight=1, uniform="equal")

        # 1. 요일 헤더 그리기
        day_names = ["일", "월", "화", "수", "목", "금", "토"]
        day_colors = ["#e63946", "gray50", "gray50", "gray50", "gray50", "gray50", "#1c7ed6"] # 일요일 적색, 토요일 청색
        for col, (day, col_color) in enumerate(zip(day_names, day_colors)):
            lbl = ctk.CTkLabel(
                self.cal_body, text=day, 
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=col_color
            )
            lbl.grid(row=0, column=col, sticky="nsew", pady=5)

        # 2. 날짜 계산 (calendar 모듈 사용)
        # monthrange: (시작 요일(0=월, 6=일), 해당 월 총 일수)
        first_weekday, num_days = calendar.monthrange(self.current_year, self.current_month)
        
        # 일요일 시작 달력으로 변환하기 위한 계산
        # first_weekday가 월=0이므로 일=6, 이를 일=0 시작 인덱스로 보정
        start_col = (first_weekday + 1) % 7

        # 셀 배치 개수 루프
        row = 1
        col = start_col

        # 오늘 날짜 정보
        today = date.today()

        # 1일부터 말일까지 그리기
        for day in range(1, num_days + 1):
            cell_date_str = f"{self.current_year}-{self.current_month:02d}-{day:02d}"
            
            # 오늘 여부 체크
            is_today = (self.current_year == today.year and 
                        self.current_month == today.month and 
                        day == today.day)

            # 날짜 프레임 생성
            # 오늘 날짜는 테두리 강조 처리
            border_color = ("#1c7ed6", "#3b5bdb") if is_today else ("gray80", "gray30")
            border_width = 2 if is_today else 1

            cell = ctk.CTkFrame(
                self.cal_body, 
                fg_color=("white", "gray20") if not is_today else ("#e7f5ff", "#1c2c40"),
                border_color=border_color, 
                border_width=border_width, 
                corner_radius=4
            )
            cell.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)

            # 날짜 번호 표시
            day_text_color = "#e63946" if col == 0 else ("#1c7ed6" if col == 6 else ("black", "white"))
            lbl_num = ctk.CTkLabel(
                cell, text=str(day), 
                font=ctk.CTkFont(size=11, weight="bold" if is_today else "normal"),
                text_color=day_text_color
            )
            lbl_num.pack(anchor="nw", padx=6, pady=4)

            # 날짜 프레임 더블클릭 시 일정 추가 팝업 열기
            # Toplevel 창의 레이어 포커스를 유지하기 위해 winfo_toplevel() 전달
            cell.bind("<Double-Button-1>", lambda event, d_str=cell_date_str: self.open_add_dialog_with_date(d_str))
            lbl_num.bind("<Double-Button-1>", lambda event, d_str=cell_date_str: self.open_add_dialog_with_date(d_str))

            # 당일 마감인 수행평가 데이터 검색 및 렌더링
            day_tasks = [t for t in self.data_manager.tasks if t.get("due_date") == cell_date_str]
            # 마감일 정렬
            day_tasks = sorted(day_tasks, key=lambda t: t.get("due_time", "23:59"))

            # 공간 절약을 위해 최대 3개까지만 달력 셀 내부에 표시
            for i, task in enumerate(day_tasks[:3]):
                self.render_mini_task_tag(cell, task)
            
            # 3개 초과인 경우 '+더보기' 라벨 출력
            if len(day_tasks) > 3:
                more_lbl = ctk.CTkLabel(
                    cell, text=f"+{len(day_tasks)-3}개 더보기", 
                    font=ctk.CTkFont(size=9), text_color="gray"
                )
                more_lbl.pack(anchor="w", padx=6)

            # 격자 위치 이동
            col += 1
            if col > 6:
                col = 0
                row += 1
                if row > 6:
                    break

    def render_mini_task_tag(self, parent_cell, task):
        """달력 일자 셀 내부에 작은 수행평가 뱃지를 표시합니다."""
        subject = task.get("subject", "")
        title = task.get("title", "")
        is_completed = task.get("completed", False)

        sub_colors = self.data_manager.settings.get("subject_colors", {})
        color = sub_colors.get(subject, "gray")

        # 완료된 태스크는 흐리게 연출
        fg_col = color if not is_completed else "gray"
        
        tag = ctk.CTkFrame(
            parent_cell, 
            fg_color=fg_col, 
            corner_radius=3, 
            height=16
        )
        tag.pack(fill="x", padx=4, pady=1)
        tag.pack_propagate(False)

        # 뱃지 내부 텍스트 표시
        # 완료 표시 여부에 따라 줄 표시 (또는 아이콘)
        font_style = ctk.CTkFont(size=10, weight="bold", overstrike=is_completed)
        text_disp = f"[{subject}] {title}"
        
        lbl = ctk.CTkLabel(
            tag, text=text_disp, 
            font=font_style, 
            text_color="white",
            anchor="w"
        )
        lbl.pack(fill="both", expand=True, padx=4)

        # 미니 태그 단일 좌클릭 -> 상세 조회, 더블클릭 -> 수정/편집 (이벤트 전파 차단)
        tag.bind("<Button-1>", lambda event, t_id=task.get("id"): self.on_mini_tag_click(event, t_id))
        lbl.bind("<Button-1>", lambda event, t_id=task.get("id"): self.on_mini_tag_click(event, t_id))
        tag.bind("<Double-Button-1>", lambda event, t_id=task.get("id"): self.on_mini_tag_double_click(event, t_id))
        lbl.bind("<Double-Button-1>", lambda event, t_id=task.get("id"): self.on_mini_tag_double_click(event, t_id))

    # --- 우측 오늘의 대시보드 렌더링 ---
    def draw_dashboard(self):
        # 기존 스크롤 내부 요소 비우기
        for widget in self.dash_scroll.winfo_children():
            widget.destroy()

        # 미완료 일정만 필터링하여 가져옴
        unfinished_tasks = [t for t in self.data_manager.tasks if not t.get("completed", False)]
        
        # D-day 기준으로 정렬 (1차: 잔여 일수, 2차: 마감 시간)
        # 기한이 경과한 것이 우선(D+), 그다음 임박한 일정(D-0, D-1) 순서
        def get_dday_sort_val(task_dict):
            due_str = task_dict.get("due_date", "9999-12-31")
            due_time = task_dict.get("due_time", "23:59")
            try:
                due_d = datetime.strptime(due_str, "%Y-%m-%d").date()
                days = (due_d - date.today()).days
                return (days, due_time)
            except ValueError:
                return (99999, due_time)

        sorted_dashboard = sorted(unfinished_tasks, key=get_dday_sort_val)

        if not sorted_dashboard:
            placeholder = ctk.CTkLabel(
                self.dash_scroll, text="남은 수행평가나\n과제가 없습니다. 🎉",
                font=ctk.CTkFont(size=13), text_color="gray"
            )
            placeholder.pack(pady=40)
            return

        # 대시보드 카드 생성
        for task in sorted_dashboard:
            due_str = task.get("due_date", "")
            dday_lbl, dday_color = self.get_dday_info(due_str)

            # 카드 프레임
            card = ctk.CTkFrame(self.dash_scroll, fg_color=("white", "gray20"), corner_radius=6)
            card.pack(fill="x", pady=4, padx=5)

            # D-day 표시 영역
            lbl_dday = ctk.CTkLabel(
                card, text=dday_lbl, text_color=dday_color,
                font=ctk.CTkFont(family="Inter", size=13, weight="bold")
            )
            lbl_dday.pack(side="left", padx=10, pady=8)

            # 타이틀 및 과목
            title_text = f"[{task.get('subject')}] {task.get('title')}"
            lbl_info = ctk.CTkLabel(
                card, text=title_text, anchor="w",
                font=ctk.CTkFont(size=12, weight="bold")
            )
            lbl_info.pack(side="left", fill="x", expand=True, padx=(5, 10))

            # 단일 좌클릭 -> 상세 조회, 더블클릭 -> 수정/편집
            card.bind("<Button-1>", lambda event, t_id=task.get("id"): self.on_mini_tag_click(event, t_id))
            lbl_dday.bind("<Button-1>", lambda event, t_id=task.get("id"): self.on_mini_tag_click(event, t_id))
            lbl_info.bind("<Button-1>", lambda event, t_id=task.get("id"): self.on_mini_tag_click(event, t_id))
            card.bind("<Double-Button-1>", lambda event, t_id=task.get("id"): self.on_mini_tag_double_click(event, t_id))
            lbl_dday.bind("<Double-Button-1>", lambda event, t_id=task.get("id"): self.on_mini_tag_double_click(event, t_id))
            lbl_info.bind("<Double-Button-1>", lambda event, t_id=task.get("id"): self.on_mini_tag_double_click(event, t_id))

    def get_dday_info(self, due_date_str):
        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            today = date.today()
            delta = (due_date - today).days
            if delta == 0:
                return "D-Day", "#e63946"
            elif delta > 0:
                if delta <= 3:
                    return f"D-{delta}", "#fd7e14"
                else:
                    return f"D-{delta}", "#2b8a3e"
            else:
                return f"D+{abs(delta)}", "gray50"
        except ValueError:
            return "D-?", "gray"

    # --- 팝업창 연동 헬퍼 ---
    def open_add_dialog_with_date(self, target_date_str):
        # 더블 클릭한 날짜가 마감일 기본값으로 채워진 채 에디터가 열림
        editor = TaskEditor(self.winfo_toplevel(), self.data_manager, refresh_callback=self.refresh_view)
        editor.ent_date.delete(0, "end")
        editor.ent_date.insert(0, target_date_str)

    def open_edit_dialog(self, task_id):
        TaskEditor(self.winfo_toplevel(), self.data_manager, task_id=task_id, refresh_callback=self.refresh_view)

    def open_view_dialog(self, task_id):
        TaskViewer(self.winfo_toplevel(), self.data_manager, task_id=task_id, refresh_callback=self.refresh_view)

    def on_mini_tag_click(self, event, task_id):
        if self.click_timer:
            self.after_cancel(self.click_timer)
            self.click_timer = None
            self.open_edit_dialog(task_id)
        else:
            self.click_timer = self.after(250, lambda: self._execute_single_click(task_id))
        return "break"  # 부모 날짜 셀로 더블클릭/단일클릭 이벤트 버블링 차단

    def _execute_single_click(self, task_id):
        self.click_timer = None
        self.open_view_dialog(task_id)

    def on_mini_tag_double_click(self, event, task_id):
        if self.click_timer:
            self.after_cancel(self.click_timer)
            self.click_timer = None
        self.open_edit_dialog(task_id)
        return "break"  # 부모 날짜 셀로 더블클릭/단일클릭 이벤트 버블링 차단
