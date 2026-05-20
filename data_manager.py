import os
import json

class DataManager:
    TASKS_FILE = "tasks.json"
    SETTINGS_FILE = "settings.json"

    def __init__(self):
        self.tasks = []
        self.settings = {}
        self.load_all_data()

    def get_default_settings(self):
        # 1교시부터 7교시까지 초기화하기 위한 헬퍼 구조
        default_timetable = {}
        days = ["mon", "tue", "wed", "thu", "fri"]
        for day in days:
            default_timetable[day] = [{"subject": "", "teacher": ""} for _ in range(7)]
            
        return {
            "theme": "system",
            "subject_colors": {
                "국어": "#FF6B6B",
                "수학 II": "#FF922B",
                "영어": "#51CF66",
                "정보": "#CC5DE8",
                "물리 I": "#339AF0"
            },
            "timetable": default_timetable
        }

    def load_all_data(self):
        """설정 및 태스크 데이터를 파일로부터 로드합니다. 파일이 손상되었거나 없을 시 기본값으로 복원합니다."""
        # 1. 설정 로드
        if not os.path.exists(self.SETTINGS_FILE):
            self.settings = self.get_default_settings()
            self.save_settings()
        else:
            try:
                with open(self.SETTINGS_FILE, "r", encoding="utf-8") as f:
                    self.settings = json.load(f)
            except (json.JSONDecodeError, IOError):
                # 데이터가 깨졌거나 읽을 수 없으면 예외 처리를 통해 자동 기본 복원 (생기부 어필 포인트)
                self.settings = self.get_default_settings()
                self.save_settings()

        # 2. 태스크 로드
        if not os.path.exists(self.TASKS_FILE):
            self.tasks = []
            self.save_tasks()
        else:
            try:
                with open(self.TASKS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.tasks = data.get("tasks", [])
            except (json.JSONDecodeError, IOError):
                # 태스크 데이터 손상 시 예외 처리
                self.tasks = []
                self.save_tasks()

    def save_settings(self):
        """설정 데이터를 settings.json 파일에 저장합니다."""
        try:
            with open(self.SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Error saving settings: {e}")

    def save_tasks(self):
        """일정 데이터를 tasks.json 파일에 저장합니다."""
        try:
            with open(self.TASKS_FILE, "w", encoding="utf-8") as f:
                json.dump({"tasks": self.tasks}, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Error saving tasks: {e}")

    # --- 태스크 CRUD 헬퍼 함수 ---
    
    def add_task(self, task_data):
        self.tasks.append(task_data)
        self.save_tasks()

    def update_task(self, task_id, updated_data):
        for i, task in enumerate(self.tasks):
            if task.get("id") == task_id:
                self.tasks[i] = updated_data
                self.save_tasks()
                return True
        return False

    def delete_task(self, task_id):
        self.tasks = [task for task in self.tasks if task.get("id") != task_id]
        self.save_tasks()
        
    def get_task_by_id(self, task_id):
        for task in self.tasks:
            if task.get("id") == task_id:
                return task
        return None
