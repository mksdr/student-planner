import customtkinter as ctk
from data_manager import DataManager
from views import CalendarView, ListView, TimetableView, SettingsView

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. 데이터 매니저 초기화 및 테마 적용
        self.data_manager = DataManager()
        initial_theme = self.data_manager.settings.get("theme", "system")
        ctk.set_appearance_mode(initial_theme)
        ctk.set_default_color_theme("blue")  # 기본 테마 칼라

        # 2. 윈도우 설정
        self.title("학업 플래너 - 수행평가 및 과제 관리 시스템")
        self.geometry("1100x750")
        self.minimum_width = 900
        self.minimum_height = 600
        self.minsize(self.minimum_width, self.minimum_height)

        # 3. 레이아웃 그리드 설정
        # 0번 열: 좌측 네비게이션 바 (가중치 0, 고정 너비)
        # 1번 열: 우측 메인 콘텐츠 영역 (가중치 1, 유연한 너비)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 4. 좌측 네비게이션 프레임 생성
        self.nav_frame = ctk.CTkFrame(self, corner_radius=0, width=200)
        self.nav_frame.grid(row=0, column=0, sticky="nsew")
        self.nav_frame.grid_rowconfigure(5, weight=1)  # 하단 여백용 행

        # 네비게이션 타이틀
        self.logo_label = ctk.CTkLabel(
            self.nav_frame, 
            text="🎓 STUDENT\nPLANNER", 
            font=ctk.CTkFont(family="Inter", size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=35)

        # 네비게이션 버튼들 생성
        self.nav_buttons = {}
        button_specs = [
            ("일정", "📅 일정", CalendarView),
            ("목록", "📝 목록", ListView),
            ("시간표", "🕒 시간표", TimetableView),
            ("설정", "⚙️ 설정", SettingsView)
        ]

        for i, (key, label, view_class) in enumerate(button_specs, start=1):
            btn = ctk.CTkButton(
                self.nav_frame,
                text=label,
                corner_radius=8,
                height=40,
                border_spacing=10,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
                anchor="w",
                font=ctk.CTkFont(family="Inter", size=14, weight="normal"),
                command=lambda k=key, vc=view_class: self.select_frame(k, vc)
            )
            btn.grid(row=i, column=0, padx=15, pady=8, sticky="ew")
            self.nav_buttons[key] = btn

        # 프로그램 하단 버젼 표시 (생기부용 프로페셔널 브랜딩)
        self.version_label = ctk.CTkLabel(
            self.nav_frame, 
            text="v1.0.0 (MVP)", 
            font=ctk.CTkFont(size=11), 
            text_color="gray50"
        )
        self.version_label.grid(row=6, column=0, pady=20)

        # 5. 우측 메인 콘텐츠 컨테이너 및 초기 화면 진입
        self.current_frame = None
        self.select_frame("일정", CalendarView)

    def select_frame(self, name, view_class):
        """좌측 네비게이션 클릭 시 우측 메인 뷰를 전환하는 컨트롤러 역할을 합니다."""
        # 모든 버튼 비활성화 시각 효과 적용
        for btn_name, btn in self.nav_buttons.items():
            if btn_name == name:
                btn.configure(fg_color=("gray75", "gray25"))  # 선택된 버튼 강조
            else:
                btn.configure(fg_color="transparent")

        # 기존 프레임 파괴 및 메모리 해제
        if self.current_frame is not None:
            self.current_frame.destroy()

        # 새로운 프레임 인스턴스 생성 및 배치
        self.current_frame = view_class(self, self, self.data_manager)
        self.current_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

if __name__ == "__main__":
    app = App()
    app.mainloop()
