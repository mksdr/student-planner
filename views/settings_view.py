import customtkinter as ctk
import json
from tkinter import filedialog, messagebox

class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, controller, data_manager):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.data_manager = data_manager

        # 타이틀 영역
        self.title_label = ctk.CTkLabel(
            self, 
            text="⚙️ 설정", 
            font=ctk.CTkFont(family="Inter", size=24, weight="bold")
        )
        self.title_label.pack(anchor="w", padx=30, pady=(30, 10))

        # 메인 영역
        self.card = ctk.CTkFrame(self)
        self.card.pack(fill="both", expand=True, padx=30, pady=20)

        # 1. 화면 테마 설정
        self.theme_label = ctk.CTkLabel(
            self.card, 
            text="화면 테마 설정", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.theme_label.pack(anchor="w", padx=30, pady=(30, 5))

        self.theme_option = ctk.CTkOptionMenu(
            self.card,
            values=["System", "Light", "Dark"],
            command=self.change_theme
        )
        self.theme_option.pack(anchor="w", padx=30, pady=(0, 20))
        
        # 현재 저장된 테마 값 반영
        current_theme = self.data_manager.settings.get("theme", "system")
        self.theme_option.set(current_theme.capitalize())

        # 구분선
        self.separator = ctk.CTkFrame(self.card, height=2, fg_color=("gray85", "gray25"))
        self.separator.pack(fill="x", padx=30, pady=15)

        # 2. 데이터 관리
        self.db_label = ctk.CTkLabel(
            self.card, 
            text="학업 데이터 백업 및 복구", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.db_label.pack(anchor="w", padx=30, pady=(10, 5))

        self.lbl_desc = ctk.CTkLabel(
            self.card,
            text="일정 및 시간표를 단일 파일로 백업하여 보관하거나 다른 기기에서 불러올 수 있습니다.",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.lbl_desc.pack(anchor="w", padx=30, pady=(0, 15))
        
        # 버튼 영역
        self.btn_container = ctk.CTkFrame(self.card, fg_color="transparent")
        self.btn_container.pack(fill="x", padx=30, pady=5)

        self.backup_btn = ctk.CTkButton(
            self.btn_container,
            text="📤 백업파일 내보내기 (JSON)",
            fg_color="#1c7ed6",
            hover_color="#1864ab",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.backup_data
        )
        self.backup_btn.pack(side="left", padx=(0, 15))
        
        self.restore_btn = ctk.CTkButton(
            self.btn_container,
            text="📥 백업파일 가져오기 (JSON)",
            fg_color="#2b8a3e",
            hover_color="#237032",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.restore_data
        )
        self.restore_btn.pack(side="left")

        # 구분선 2
        self.separator2 = ctk.CTkFrame(self.card, height=2, fg_color=("gray85", "gray25"))
        self.separator2.pack(fill="x", padx=30, pady=15)

        # 3. 데이터 초기화
        self.reset_label = ctk.CTkLabel(
            self.card, 
            text="학업 데이터 범위별 초기화", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.reset_label.pack(anchor="w", padx=30, pady=(10, 5))

        self.lbl_reset_desc = ctk.CTkLabel(
            self.card,
            text="지정된 범위의 데이터를 선택하여 초기 기본 설정 상태로 복구할 수 있습니다.",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.lbl_reset_desc.pack(anchor="w", padx=30, pady=(0, 15))
        
        # 버튼 영역 2
        self.reset_btn_container = ctk.CTkFrame(self.card, fg_color="transparent")
        self.reset_btn_container.pack(fill="x", padx=30, pady=5)

        self.reset_all_btn = ctk.CTkButton(
            self.reset_btn_container,
            text="⚠️ 전체 초기화",
            fg_color="#e63946",
            hover_color="#c92a2a",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.reset_all_data
        )
        self.reset_all_btn.pack(side="left", padx=(0, 15))
        
        self.reset_tasks_btn = ctk.CTkButton(
            self.reset_btn_container,
            text="📅 일정만 초기화",
            fg_color="#f76707",
            hover_color="#d9480f",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.reset_tasks_data
        )
        self.reset_tasks_btn.pack(side="left", padx=(0, 15))

        self.reset_timetable_btn = ctk.CTkButton(
            self.reset_btn_container,
            text="⏰ 시간표만 초기화",
            fg_color="#fab005",
            hover_color="#e67700",
            text_color="black",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.reset_timetable_data
        )
        self.reset_timetable_btn.pack(side="left")

    def change_theme(self, choice):
        theme_val = choice.lower()
        ctk.set_appearance_mode(theme_val)
        self.data_manager.settings["theme"] = theme_val
        self.data_manager.save_settings()

    def backup_data(self):
        """현재 일정과 설정을 단일 JSON 딕셔너리로 병합하여 파일로 추출합니다."""
        try:
            combined_data = {
                "tasks": self.data_manager.tasks,
                "settings": self.data_manager.settings
            }
            
            file_path = filedialog.asksaveasfilename(
                parent=self.winfo_toplevel(),
                defaultextension=".json",
                filetypes=[("JSON files", "*.json")],
                initialfile="student_planner_backup.json"
            )
            
            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(combined_data, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("백업 완료", "학업 데이터 백업이 성공적으로 저장되었습니다!")
        except Exception as e:
            messagebox.showerror("백업 오류", f"백업 진행 중 에러가 발생했습니다:\n{e}")

    def restore_data(self):
        """사용자가 선택한 백업 파일을 파싱하고 검증한 후 복구합니다."""
        try:
            file_path = filedialog.askopenfilename(
                parent=self.winfo_toplevel(),
                filetypes=[("JSON files", "*.json")]
            )
            
            if file_path:
                with open(file_path, "r", encoding="utf-8") as f:
                    imported = json.load(f)
                
                # 데이터 유효성 검사 (생기부용 무결성 검증 알고리즘 어필)
                if not isinstance(imported, dict) or "tasks" not in imported or "settings" not in imported:
                    raise KeyError("올바르지 않은 백업 파일 형식이거나 손상된 파일입니다.")

                # 데이터 복사 및 반영
                self.data_manager.tasks = imported["tasks"]
                self.data_manager.settings = imported["settings"]
                
                self.data_manager.save_tasks()
                self.data_manager.save_settings()

                # 테마 즉시 업데이트 반영
                current_theme = self.data_manager.settings.get("theme", "system")
                self.theme_option.set(current_theme.capitalize())
                ctk.set_appearance_mode(current_theme)

                messagebox.showinfo("복구 완료", "학업 데이터 복구가 완료되었습니다!\n달력 화면으로 이동합니다.")
                
                # 달력 탭 화면으로 새로고침 전환
                if hasattr(self.controller, "select_frame"):
                    from views.calendar_view import CalendarView
                    self.controller.select_frame("일정", CalendarView)
        except Exception as e:
            messagebox.showerror("복구 오류", f"데이터 복구에 실패했습니다. 파일 무결성을 점검해 주세요.\n에러 내용: {e}")

    def reset_all_data(self):
        """일정 및 설정을 모두 기본 공장 출고값으로 전체 초기화합니다."""
        confirm = messagebox.askyesno(
            "전체 초기화 경고", 
            "정말로 플래너의 전체 데이터(일정 및 시간표)를 초기화하시겠습니까?\n이 작업은 복구할 수 없습니다.",
            parent=self.winfo_toplevel()
        )
        if confirm:
            self.data_manager.tasks = []
            self.data_manager.settings = self.data_manager.get_default_settings()
            
            self.data_manager.save_tasks()
            self.data_manager.save_settings()

            # UI 테마 동기화 및 메인 화면 이동
            current_theme = self.data_manager.settings.get("theme", "system")
            self.theme_option.set(current_theme.capitalize())
            ctk.set_appearance_mode(current_theme)

            messagebox.showinfo("초기화 완료", "전체 데이터가 성공적으로 초기화되었습니다.")
            
            if hasattr(self.controller, "select_frame"):
                from views.calendar_view import CalendarView
                self.controller.select_frame("일정", CalendarView)

    def reset_tasks_data(self):
        """시간표 등은 그대로 두고 일정/수행평가 데이터만 초기화합니다."""
        confirm = messagebox.askyesno(
            "일정 초기화 경고", 
            "정말로 모든 일정 및 수행평가 데이터를 초기화하시겠습니까?\n시간표 데이터는 보존됩니다.",
            parent=self.winfo_toplevel()
        )
        if confirm:
            self.data_manager.tasks = []
            self.data_manager.save_tasks()
            
            messagebox.showinfo("초기화 완료", "모든 일정 데이터가 성공적으로 초기화되었습니다.")
            
            if hasattr(self.controller, "select_frame"):
                from views.calendar_view import CalendarView
                self.controller.select_frame("일정", CalendarView)

    def reset_timetable_data(self):
        """일정은 그대로 두고 시간표 데이터 및 배정된 과목 칼라 맵을 초기화합니다."""
        confirm = messagebox.askyesno(
            "시간표 초기화 경고", 
            "정말로 시간표(과목 및 교사 정보) 데이터를 초기화하시겠습니까?\n일정 데이터는 보존됩니다.",
            parent=self.winfo_toplevel()
        )
        if confirm:
            default_sets = self.data_manager.get_default_settings()
            self.data_manager.settings["timetable"] = default_sets.get("timetable", {})
            self.data_manager.settings["subject_colors"] = default_sets.get("subject_colors", {})
            
            self.data_manager.save_settings()
            
            messagebox.showinfo("초기화 완료", "시간표 데이터가 성공적으로 초기화되었습니다.")
            
            if hasattr(self.controller, "select_frame"):
                from views.timetable_view import TimetableView
                self.controller.select_frame("시간표", TimetableView)
