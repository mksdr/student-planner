import customtkinter as ctk
from datetime import datetime, date
from views.task_editor import TaskEditor, TaskViewer

class ListView(ctk.CTkFrame):
    def __init__(self, parent, controller, data_manager):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.data_manager = data_manager

        # 현재 렌더링 필터 조건
        self.filter_status = "전체"  # 전체, 미완료, 완료
        self.filter_subject = "전체 과목"
        self.filter_priority_only = False
        self.click_timer = None
        
        self.setup_ui()
        self.refresh_list()

    def setup_ui(self):
        # 상단 타이틀 및 일정 추가 버튼 프레임
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=30, pady=(25, 10))

        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="📝 수행평가 & 과제 목록", 
            font=ctk.CTkFont(family="Inter", size=24, weight="bold")
        )
        self.title_label.pack(side="left")

        # "+ 일정 추가" 버튼
        self.btn_add_task = ctk.CTkButton(
            self.header_frame,
            text="➕ 일정 추가",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            fg_color="#1c7ed6",
            hover_color="#1864ab",
            width=110,
            command=self.open_task_add_dialog
        )
        self.btn_add_task.pack(side="right")

        # 필터링 바 프레임
        self.filter_bar = ctk.CTkFrame(self, fg_color=("gray95", "gray15"), height=50)
        self.filter_bar.pack(fill="x", padx=30, pady=(5, 15))

        # 1. 완료 상태 필터 (전체/미완료/완료)
        self.seg_filter = ctk.CTkSegmentedButton(
            self.filter_bar,
            values=["전체", "미완료", "완료"],
            command=self.change_status_filter
        )
        self.seg_filter.set("미완료")  # 디폴트는 미완료 리스트 표시
        self.filter_status = "미완료"
        self.seg_filter.pack(side="left", padx=15, pady=10)

        # 2. 과목 필터 콤보박스
        subjects = ["전체 과목"] + list(self.data_manager.settings.get("subject_colors", {}).keys())
        self.combo_subject_filter = ctk.CTkComboBox(
            self.filter_bar,
            values=subjects,
            width=130,
            command=self.change_subject_filter
        )
        self.combo_subject_filter.set("전체 과목")
        self.combo_subject_filter.pack(side="left", padx=10, pady=10)

        # 3. 중요 일정 스위치
        self.switch_priority = ctk.CTkSwitch(
            self.filter_bar,
            text="⭐ 중요 일정만",
            font=ctk.CTkFont(size=12),
            command=self.toggle_priority_filter
        )
        self.switch_priority.pack(side="right", padx=15, pady=10)

        # 메인 일정 카드 리스트 영역 (스크롤 가능 프레임)
        self.list_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_container.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    # --- 필터링 이벤트 핸들러 ---
    
    def change_status_filter(self, val):
        self.filter_status = val
        self.refresh_list()

    def change_subject_filter(self, val):
        self.filter_subject = val
        self.refresh_list()

    def toggle_priority_filter(self):
        self.filter_priority_only = self.switch_priority.get() == 1
        self.refresh_list()

    # --- 다이얼로그 호출 ---

    def open_task_add_dialog(self):
        # Toplevel 윈도우 생성
        TaskEditor(self.winfo_toplevel(), self.data_manager, refresh_callback=self.refresh_list)

    def open_task_edit_dialog(self, task_id):
        # 특정 일정 클릭 시 편집 모달 로드
        TaskEditor(self.winfo_toplevel(), self.data_manager, task_id=task_id, refresh_callback=self.refresh_list)

    def open_task_view_dialog(self, task_id):
        # 특정 일정 클릭 시 상세 조회 모달 로드
        TaskViewer(self.winfo_toplevel(), self.data_manager, task_id=task_id, refresh_callback=self.refresh_list)

    def on_task_click(self, task_id):
        if self.click_timer:
            self.after_cancel(self.click_timer)
            self.click_timer = None
            self.open_task_edit_dialog(task_id)
        else:
            self.click_timer = self.after(250, lambda: self._execute_single_click(task_id))

    def _execute_single_click(self, task_id):
        self.click_timer = None
        self.open_task_view_dialog(task_id)

    def on_task_double_click(self, task_id):
        if self.click_timer:
            self.after_cancel(self.click_timer)
            self.click_timer = None
        self.open_task_edit_dialog(task_id)

    # --- 리스트 갱신 알고리즘 ---

    def calculate_dday(self, due_date_str):
        """오늘 기준 일정의 D-day를 계산하고 경고 레벨에 맞추어 색상을 매핑합니다 (컴퓨팅 알고리즘)."""
        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            today = date.today()
            delta = (due_date - today).days
            if delta == 0:
                return "D-Day", "#e63946"  # 강한 적색
            elif delta > 0:
                if delta <= 3:
                    return f"D-{delta}", "#fd7e14"  # 경고 주황색
                else:
                    return f"D-{delta}", "#2b8a3e"  # 안정 초록색
            else:
                return f"D+{abs(delta)}", "gray"  # 기한 지남
        except ValueError:
            return "D-?", "gray"

    def refresh_list(self):
        # 기존 카드들 삭제
        for widget in self.list_container.winfo_children():
            widget.destroy()

        # 데이터 매니저로부터 최신 일정 로드 및 마감일/마감시간 기준 2차 정렬 (알고리즘 고도화)
        sorted_tasks = sorted(
            self.data_manager.tasks, 
            key=lambda t: (t.get("due_date", "9999-12-31"), t.get("due_time", "23:59"))
        )

        count = 0
        for task in sorted_tasks:
            # 1. 완료 상태 필터 적용
            is_completed = task.get("completed", False)
            if self.filter_status == "미완료" and is_completed:
                continue
            elif self.filter_status == "완료" and not is_completed:
                continue

            # 2. 과목 필터 적용
            subject_name = task.get("subject", "")
            if self.filter_subject != "전체 과목" and subject_name != self.filter_subject:
                continue

            # 3. 중요도 필터 적용
            is_priority = task.get("priority", False)
            if self.filter_priority_only and not is_priority:
                continue

            count += 1
            self.render_task_card(task)

        # 리스트가 비어있을 때 플레이스홀더 출력
        if count == 0:
            self.no_task_lbl = ctk.CTkLabel(
                self.list_container,
                text="조건에 맞는 일정이 없습니다.",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            self.no_task_lbl.pack(pady=50)

    def render_task_card(self, task):
        # 개별 카드의 외부 테두리/바탕 프레임
        # 중요 일정일 경우 테두리에 골드 하이라이트 효과 적용
        border_color = ("#ffc01a", "#d4a317") if task.get("priority", False) else None
        border_width = 1.5 if task.get("priority", False) else 0

        card = ctk.CTkFrame(
            self.list_container,
            fg_color=("white", "gray20"),
            border_color=border_color,
            border_width=border_width,
            height=70
        )
        card.pack(fill="x", pady=6, ipady=4)

        # 1. 완료 체크박스
        chk_var = ctk.BooleanVar(value=task.get("completed", False))
        chk = ctk.CTkCheckBox(
            card,
            text="",
            variable=chk_var,
            width=24,
            command=lambda t_id=task.get("id"), cv=chk_var: self.toggle_task_complete(t_id, cv.get())
        )
        chk.pack(side="left", padx=(15, 10))

        # 2. 과목 컬러 뱃지 (Badge)
        sub_colors = self.data_manager.settings.get("subject_colors", {})
        bg_col = sub_colors.get(task.get("subject", ""), "gray50")
        
        badge = ctk.CTkFrame(
            card, 
            fg_color=bg_col,
            corner_radius=6,
            height=26,
            width=65
        )
        badge.pack(side="left", padx=5)
        badge.pack_propagate(False)
        
        # 뱃지 안의 과목 텍스트
        badge_lbl = ctk.CTkLabel(
            badge, 
            text=task.get("subject", ""), 
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="white"
        )
        badge_lbl.pack(expand=True)

        # 3. 마감 D-day 정보 및 라벨
        dday_text, dday_color = self.calculate_dday(task.get("due_date", ""))
        dday_lbl = ctk.CTkLabel(
            card,
            text=dday_text,
            text_color=dday_color,
            font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
            width=50
        )
        dday_lbl.pack(side="left", padx=10)

        # 4. 일정 제목 및 세부 설명 (텍스트 취소선 효과 또는 연하게 처리)
        text_color = "gray50" if task.get("completed", False) else ("black", "white")
        font_style = ctk.CTkFont(
            size=14, 
            weight="bold",
            overstrike=task.get("completed", False)  # 완료 시 가볍게 가로선 처리
        )
        
        title_lbl = ctk.CTkLabel(
            card,
            text=task.get("title", ""),
            font=font_style,
            text_color=text_color,
            anchor="w"
        )
        title_lbl.pack(side="left", fill="x", expand=True, padx=10)

        # 마감 시각 표기
        time_lbl = ctk.CTkLabel(
            card,
            text=f"⏰ {task.get('due_time', '23:59')}",
            font=ctk.CTkFont(size=12),
            text_color="gray50"
        )
        time_lbl.pack(side="left", padx=15)

        # 5. 선택적 진행률 바 (Sub-checklist가 있는 경우에만 렌더링)
        checklist = task.get("checklist", [])
        if checklist:
            total_items = len(checklist)
            done_items = sum(1 for item in checklist if item.get("done", False))
            progress_ratio = done_items / total_items
            percent_val = int(progress_ratio * 100)

            # 진행 바 프레임
            progress_container = ctk.CTkFrame(card, fg_color="transparent")
            progress_container.pack(side="left", padx=15)

            pbar = ctk.CTkProgressBar(
                progress_container,
                width=80,
                height=8,
                progress_color="#2b8a3e"
            )
            pbar.set(progress_ratio)
            pbar.pack(pady=(0, 2))

            p_lbl = ctk.CTkLabel(
                progress_container,
                text=f"{percent_val}% 완료",
                font=ctk.CTkFont(size=10, weight="normal"),
                text_color="gray"
            )
            p_lbl.pack()

            # 하위 체크리스트 빠른 보기/토글 영역 (클릭으로 세부 완료 처리 가능)
            # 프리미엄 기능: 카드를 클릭하여 펼치지 않고 간편하게 접힌 상태에서 토글
            # UI 복잡성을 덜기 위해 이 창은 편집 다이얼로그에서 처리하지만 진행률은 실시간 반영됩니다.

        # 연필(✎) 버튼을 가장 오른쪽에 오도록 먼저 pack
        btn_modify = ctk.CTkButton(
            card,
            text="✎",
            width=28,
            height=28,
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            border_width=1,
            border_color=("gray60", "gray40"),
            text_color=("gray10", "gray90"),
            hover_color=("gray85", "gray25"),
            command=lambda t_id=task.get("id"): self.open_task_edit_dialog(t_id)
        )
        btn_modify.pack(side="right", padx=(5, 15))

        # 보기(👁️) 버튼을 그 왼쪽에 배치하도록 나중에 pack
        btn_edit = ctk.CTkButton(
            card,
            text="👁️ 보기",
            width=50,
            height=28,
            fg_color="transparent",
            border_width=1,
            border_color=("gray60", "gray40"),
            text_color=("gray10", "gray90"),
            hover_color=("gray85", "gray25"),
            command=lambda t_id=task.get("id"): self.open_task_view_dialog(t_id)
        )
        btn_edit.pack(side="right", padx=(5, 5))

        # 카드 정보 영역 좌클릭(상세) / 더블클릭(편집) 단축 바인딩
        t_id = task.get("id")
        for widget in [card, title_lbl, time_lbl, dday_lbl]:
            widget.bind("<Button-1>", lambda event, tid=t_id: self.on_task_click(tid))
            widget.bind("<Double-Button-1>", lambda event, tid=t_id: self.on_task_double_click(tid))

    def toggle_task_complete(self, task_id, is_completed):
        """목록에서 체크박스 클릭 시 바로 JSON에 저장하고 뷰를 갱신합니다."""
        task = self.data_manager.get_task_by_id(task_id)
        if task:
            task["completed"] = is_completed
            # 체크리스트가 있으면 일괄 완료 처리 또는 해제할 수도 있으나, 
            # 개별 조작 유지를 위해 일단 이대로 두고 저장합니다.
            self.data_manager.save_tasks()
            # 딜레이를 주지 않고 즉각 갱신
            self.refresh_list()
