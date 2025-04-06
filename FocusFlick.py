import customtkinter as ctk
import random
import json
import os
import time
from datetime import datetime, timedelta
import platform
import webbrowser
from PIL import Image
import threading

# Sound compatibility
SOUND_ENABLED = platform.system() == "Windows"
if SOUND_ENABLED:
    import winsound

class FocusFlickPro(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # ===== App Configuration =====
        self.title("🌟 FocusFlick Pro")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        # ===== Data Structures =====
        self.current_view = None
        self.timer_running = False
        self.session_active = False
        self.mode = "focus"  # focus, stopwatch, pomodoro
        self.phrases = [
            "The expert in anything was once a beginner.",
            "Quality is not an act, it's a habit.",
            "Small daily improvements lead to stunning results.",
            "Your future is created by what you do today.",
            "Success is the sum of small efforts repeated daily.",
            "Concentration is the secret of strength.",
            "Productivity is never an accident. It's the result of commitment.",
            "Discipline is choosing between what you want now and what you want most."
        ]
        
        # New greeting messages
        self.greetings = [
            "Welcome back, {}!",
            "Great to see you, {}!",
            "Hello again, {}!",
            "Ready to focus, {}?",
            "Let's get productive, {}!",
            "Time to shine, {}!",
            "Welcome to your workspace, {}!",
            "Let's make today count, {}!",
            "Your focus awaits, {}!",
            "Ready for an amazing session, {}?"
        ]
        
        # Initialize App
        self.configure_appearance()
        self.load_data()
        self.create_widgets()
        self.show_view("dashboard")
        
        # Start background services
        self.update_clock()
        self.check_daily_reset()

    def configure_appearance(self):
        """Configure visual elements"""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Custom fonts
        self.title_font = ("Segoe UI", 28, "bold")
        self.subtitle_font = ("Segoe UI", 18)
        self.body_font = ("Segoe UI", 14)
        self.timer_font = ("Roboto Mono", 72, "bold")
        self.small_font = ("Segoe UI", 12)
        
        # Colors
        self.primary_color = "#4B8DF8"
        self.secondary_color = "#2ECC71"
        self.danger_color = "#FF5555"
        self.warning_color = "#F39C12"
        self.info_color = "#3498DB"
        self.success_color = "#27AE60"

    def load_data(self):
        """Load user data with error handling"""
        self.data_file = "focusflick_data.json"
        default_data = {
            "user": {
                "name": "Student",
                "streak": 0,
                "total_seconds": 0,
                "sessions": 0,
                "last_session": None,
                "daily_goal": 120,
                "xp": 0,
                "level": 1,
                "tasks": [],
                "habits": [],
                "achievements": [],
                "last_reset": datetime.now().isoformat()
            },
            "settings": {
                "theme": "dark",
                "sounds": True,
                "focus_duration": 25,
                "short_break": 5,
                "long_break": 15,
                "pomodoro_cycles": 4,
                "notifications": True,
                "auto_start_breaks": True,
                "auto_start_pomodoros": True
            }
        }
        
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    loaded_data = json.load(f)
                    # Merge with default data for any new fields
                    self.data = self.deep_merge(default_data, loaded_data)
            else:
                self.data = default_data
        except Exception as e:
            print(f"Error loading data: {e}")
            self.data = default_data

    def deep_merge(self, default, loaded):
        """Deep merge two dictionaries"""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def save_data(self):
        """Save data safely"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")

    def create_widgets(self):
        """Create main application interface"""
        # Configure grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.content_frame = ctk.CTkFrame(self, corner_radius=0)
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Create status bar
        self.create_status_bar()
        
        # Initialize all views
        self.views = {}
        self.init_dashboard()
        self.init_focus_mode()
        self.init_stopwatch_mode()
        self.init_pomodoro_mode()
        self.init_tasks()
        self.init_habits()
        self.init_stats()
        self.init_settings()

    def create_sidebar(self):
        """Create navigation sidebar"""
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(8, weight=1)
        
        # App logo
        self.logo_label = ctk.CTkLabel(
            self.sidebar, 
            text="FocusFlick Pro", 
            font=self.title_font,
            padx=10
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Navigation buttons
        nav_options = [
            ("📊 Dashboard", "dashboard"),
            ("🎯 Focus Mode", "focus"),
            ("⏱️ Stopwatch", "stopwatch"),
            ("🍅 Pomodoro", "pomodoro"),
            ("✅ Tasks", "tasks"),
            ("📅 Habits", "habits"),
            ("📈 Statistics", "stats"),
            ("⚙️ Settings", "settings")
        ]
        
        for i, (text, view) in enumerate(nav_options, start=1):
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=lambda v=view: self.show_view(v),
                anchor="w",
                font=self.subtitle_font,
                fg_color="transparent",
                hover_color=("gray70", "gray30"),
                width=220,
                height=40,
                corner_radius=8
            )
            btn.grid(row=i, column=0, padx=10, pady=5, sticky="ew")
        
        # User profile
        self.user_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.user_frame.grid(row=9, column=0, sticky="s", pady=20)
        
        self.user_avatar = ctk.CTkLabel(
            self.user_frame, 
            text="👤", 
            font=("Segoe UI", 32)
        )
        self.user_avatar.pack()
        
        self.user_name = ctk.CTkLabel(
            self.user_frame, 
            text=self.data["user"]["name"], 
            font=self.subtitle_font
        )
        self.user_name.pack()
        
        self.user_level = ctk.CTkLabel(
            self.user_frame,
            text=f"Level {self.data['user']['level']}",
            font=self.small_font,
            text_color=self.secondary_color
        )
        self.user_level.pack()

    def create_status_bar(self):
        """Create bottom status bar"""
        self.status_bar = ctk.CTkFrame(self, height=30)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        # Clock
        self.clock_label = ctk.CTkLabel(
            self.status_bar, 
            text="00:00:00", 
            font=("Consolas", 12)
        )
        self.clock_label.pack(side="left", padx=10)
        
        # Status message
        self.status_label = ctk.CTkLabel(
            self.status_bar, 
            text="", 
            font=self.small_font
        )
        self.status_label.pack(side="left", padx=10, expand=True)
        
        # XP progress
        self.xp_bar = ctk.CTkProgressBar(self.status_bar, height=15, width=150)
        self.xp_bar.pack(side="right", padx=10)
        
        self.xp_label = ctk.CTkLabel(
            self.status_bar, 
            text="Lvl 1", 
            font=self.small_font
        )
        self.xp_label.pack(side="right")

    def init_dashboard(self):
        """Initialize dashboard view"""
        frame = ctk.CTkFrame(self.content_frame)
        self.views["dashboard"] = frame
        
        # Header
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(pady=(20, 10), fill="x")
        
        self.dash_title = ctk.CTkLabel(
            header,
            text="",
            font=self.title_font
        )
        self.dash_title.pack(side="left", padx=20)
        
        # Quick stats
        quick_stats_frame = ctk.CTkFrame(header, fg_color="transparent")
        quick_stats_frame.pack(side="right", padx=20)
        
        ctk.CTkLabel(
            quick_stats_frame,
            text=f"🔥 {self.data['user']['streak']} day streak",
            font=self.small_font,
            text_color=self.warning_color
        ).pack(side="left", padx=10)
        
        ctk.CTkLabel(
            quick_stats_frame,
            text=f"🎯 {self.data['user']['daily_goal']} min goal",
            font=self.small_font,
            text_color=self.primary_color
        ).pack(side="left", padx=10)
        
        # Motivational phrase
        self.phrase_label = ctk.CTkLabel(
            frame,
            text=random.choice(self.phrases),
            font=self.subtitle_font,
            wraplength=800,
            pady=10
        )
        self.phrase_label.pack(fill="x")
        
        # Main content area
        content = ctk.CTkFrame(frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left column - Quick actions
        left_col = ctk.CTkFrame(content, fg_color="transparent", width=300)
        left_col.pack(side="left", fill="y", padx=10)
        
        # Quick actions
        ctk.CTkLabel(
            left_col,
            text="Quick Actions",
            font=self.subtitle_font
        ).pack(pady=(0, 10), anchor="w")
        
        actions = [
            ("Start Focus Session", "focus", self.primary_color),
            ("Start Stopwatch", "stopwatch", self.info_color),
            ("Start Pomodoro", "pomodoro", self.danger_color),
            ("Add New Task", "add_task", self.secondary_color)
        ]
        
        for text, view, color in actions:
            btn = ctk.CTkButton(
                left_col,
                text=text,
                command=lambda v=view: self.show_view(v) if v != "add_task" else self.add_task_dialog(),
                height=40,
                width=280,
                font=self.body_font,
                fg_color=color,
                corner_radius=8
            )
            btn.pack(pady=5, fill="x")
        
        # Right column - Stats and tasks
        right_col = ctk.CTkFrame(content, fg_color="transparent")
        right_col.pack(side="right", fill="both", expand=True, padx=10)
        
        # Stats cards
        stats_frame = ctk.CTkFrame(right_col)
        stats_frame.pack(fill="x", pady=(0, 20))
        
        stats = [
            ("⏱️ Today's Focus", f"{self.get_today_seconds()//60} min", self.primary_color),
            ("📊 Completed Tasks", f"{self.get_completed_tasks_count()}", self.secondary_color),
            ("📅 Active Habits", f"{len([h for h in self.data['user']['habits'] if h['active']])}", self.info_color),
            ("🏆 Achievements", f"{len(self.data['user']['achievements'])}", self.warning_color)
        ]
        
        for i, (title, value, color) in enumerate(stats):
            card = ctk.CTkFrame(
                stats_frame,
                height=100,
                border_color=color,
                border_width=2,
                corner_radius=12
            )
            card.grid(row=0, column=i, padx=10, sticky="nsew")
            stats_frame.grid_columnconfigure(i, weight=1)
            
            ctk.CTkLabel(
                card,
                text=title,
                font=self.small_font
            ).pack(pady=(10, 5))
            
            ctk.CTkLabel(
                card,
                text=value,
                font=("Segoe UI", 24, "bold"),
                text_color=color
            ).pack()
        
        # Recent tasks
        tasks_frame = ctk.CTkFrame(right_col)
        tasks_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(
            tasks_frame,
            text="Recent Tasks",
            font=self.subtitle_font
        ).pack(pady=(0, 10), anchor="w")
        
        self.task_list_frame = ctk.CTkFrame(tasks_frame, fg_color="transparent")
        self.task_list_frame.pack(fill="both", expand=True)
        self.update_task_list()

    def init_focus_mode(self):
        """Initialize focus mode view"""
        frame = ctk.CTkFrame(self.content_frame)
        self.views["focus"] = frame
        
        # Header
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(pady=20, fill="x")
        
        ctk.CTkLabel(
            header,
            text="Deep Focus Mode",
            font=self.title_font
        ).pack(side="left", padx=20)
        
        # Mode switcher
        mode_frame = ctk.CTkFrame(header, fg_color="transparent")
        mode_frame.pack(side="right", padx=20)
        
        ctk.CTkLabel(mode_frame, text="Mode:").pack(side="left", padx=5)
        self.mode_switch = ctk.CTkSegmentedButton(
            mode_frame,
            values=["Focus", "Stopwatch", "Pomodoro"],
            command=self.switch_mode,
            font=self.body_font
        )
        self.mode_switch.pack(side="left")
        self.mode_switch.set("Focus")
        
        # Main content
        content = ctk.CTkFrame(frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=50, pady=20)
        
        # Timer display
        self.timer_frame = ctk.CTkFrame(content, height=200)
        self.timer_frame.pack(pady=20)
        
        self.timer_display = ctk.CTkLabel(
            self.timer_frame,
            text=f"{self.data['settings']['focus_duration']:02d}:00",
            font=self.timer_font
        )
        self.timer_display.pack(pady=40)
        
        # Timer controls
        controls_frame = ctk.CTkFrame(content, fg_color="transparent")
        controls_frame.pack(pady=10)
        
        self.start_button = ctk.CTkButton(
            controls_frame,
            text="Start",
            command=self.start_session,
            height=40,
            width=100,
            font=self.subtitle_font,
            fg_color=self.primary_color,
            corner_radius=8
        )
        self.pause_button = ctk.CTkButton(
            controls_frame,
            text="Pause",
            command=self.pause_session,
            height=40,
            width=100,
            font=self.subtitle_font,
            state="disabled",
            corner_radius=8
        )
        self.stop_button = ctk.CTkButton(
            controls_frame,
            text="Stop",
            command=self.stop_session,
            height=40,
            width=100,
            font=self.subtitle_font,
            fg_color=self.danger_color,
            state="disabled",
            corner_radius=8
        )
        
        self.start_button.pack(side="left", padx=5)
        self.pause_button.pack(side="left", padx=5)
        self.stop_button.pack(side="left", padx=5)
        
        # Session settings
        settings_frame = ctk.CTkFrame(content)
        settings_frame.pack(fill="x", padx=50, pady=20)
        
        ctk.CTkLabel(settings_frame, text="Duration (min):").pack(side="left", padx=10)
        self.duration_menu = ctk.CTkOptionMenu(
            settings_frame,
            values=["15", "25", "45", "60", "90", "120"],
            width=80,
            font=self.body_font
        )
        self.duration_menu.pack(side="left", padx=10)
        self.duration_menu.set(str(self.data["settings"]["focus_duration"]))
        
        # Task selection
        task_frame = ctk.CTkFrame(content, fg_color="transparent")
        task_frame.pack(fill="x", padx=50, pady=10)
        
        ctk.CTkLabel(task_frame, text="Work on:").pack(side="left", padx=10)
        self.task_var = ctk.StringVar(value="None")
        self.task_menu = ctk.CTkOptionMenu(
            task_frame,
            variable=self.task_var,
            values=self.get_task_options(),
            width=200,
            font=self.body_font
        )
        self.task_menu.pack(side="left", padx=10)
        
        # Notes area
        self.notes_frame = ctk.CTkFrame(content)
        self.notes_frame.pack(fill="both", expand=True, padx=50, pady=10)
        
        ctk.CTkLabel(self.notes_frame, text="Session Notes:").pack(anchor="w", padx=5, pady=5)
        self.notes_text = ctk.CTkTextbox(self.notes_frame, height=100, font=self.body_font)
        self.notes_text.pack(fill="both", expand=True, padx=5, pady=5)

    def init_stopwatch_mode(self):
        """Initialize stopwatch mode view"""
        frame = ctk.CTkFrame(self.content_frame)
        self.views["stopwatch"] = frame
        
        # Header
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(pady=20, fill="x")
        
        ctk.CTkLabel(
            header,
            text="Stopwatch Mode",
            font=self.title_font
        ).pack(side="left", padx=20)
        
        # Mode switcher
        mode_frame = ctk.CTkFrame(header, fg_color="transparent")
        mode_frame.pack(side="right", padx=20)
        
        ctk.CTkLabel(mode_frame, text="Mode:").pack(side="left", padx=5)
        self.mode_switch_sw = ctk.CTkSegmentedButton(
            mode_frame,
            values=["Focus", "Stopwatch", "Pomodoro"],
            command=self.switch_mode,
            font=self.body_font
        )
        self.mode_switch_sw.pack(side="left")
        self.mode_switch_sw.set("Stopwatch")
        
        # Main content
        content = ctk.CTkFrame(frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=50, pady=20)
        
        # Timer display
        self.sw_timer_frame = ctk.CTkFrame(content, height=200)
        self.sw_timer_frame.pack(pady=20)
        
        self.sw_timer_display = ctk.CTkLabel(
            self.sw_timer_frame,
            text="00:00:00",
            font=self.timer_font
        )
        self.sw_timer_display.pack(pady=40)
        
        # Timer controls
        controls_frame = ctk.CTkFrame(content, fg_color="transparent")
        controls_frame.pack(pady=10)
        
        self.sw_start_button = ctk.CTkButton(
            controls_frame,
            text="Start",
            command=self.start_stopwatch,
            height=40,
            width=100,
            font=self.subtitle_font,
            fg_color=self.primary_color,
            corner_radius=8
        )
        self.sw_pause_button = ctk.CTkButton(
            controls_frame,
            text="Pause",
            command=self.pause_stopwatch,
            height=40,
            width=100,
            font=self.subtitle_font,
            state="disabled",
            corner_radius=8
        )
        self.sw_stop_button = ctk.CTkButton(
            controls_frame,
            text="Stop",
            command=self.stop_stopwatch,
            height=40,
            width=100,
            font=self.subtitle_font,
            fg_color=self.danger_color,
            state="disabled",
            corner_radius=8
        )
        self.sw_lap_button = ctk.CTkButton(
            controls_frame,
            text="Lap",
            command=self.record_lap,
            height=40,
            width=100,
            font=self.subtitle_font,
            state="disabled",
            corner_radius=8
        )
        
        self.sw_start_button.pack(side="left", padx=5)
        self.sw_pause_button.pack(side="left", padx=5)
        self.sw_stop_button.pack(side="left", padx=5)
        self.sw_lap_button.pack(side="left", padx=5)
        
        # Lap times
        self.lap_frame = ctk.CTkScrollableFrame(content, height=150)
        self.lap_frame.pack(fill="both", expand=True, padx=50, pady=10)
        
        self.lap_times = []
        
        # Task selection
        task_frame = ctk.CTkFrame(content, fg_color="transparent")
        task_frame.pack(fill="x", padx=50, pady=10)
        
        ctk.CTkLabel(task_frame, text="Work on:").pack(side="left", padx=10)
        self.sw_task_var = ctk.StringVar(value="None")
        self.sw_task_menu = ctk.CTkOptionMenu(
            task_frame,
            variable=self.sw_task_var,
            values=self.get_task_options(),
            width=200,
            font=self.body_font
        )
        self.sw_task_menu.pack(side="left", padx=10)

    def init_pomodoro_mode(self):
        """Initialize pomodoro mode view"""
        frame = ctk.CTkFrame(self.content_frame)
        self.views["pomodoro"] = frame
        
        # Header
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(pady=20, fill="x")
        
        ctk.CTkLabel(
            header,
            text="Pomodoro Timer",
            font=self.title_font
        ).pack(side="left", padx=20)
        
        # Mode switcher
        mode_frame = ctk.CTkFrame(header, fg_color="transparent")
        mode_frame.pack(side="right", padx=20)
        
        ctk.CTkLabel(mode_frame, text="Mode:").pack(side="left", padx=5)
        self.mode_switch_pomo = ctk.CTkSegmentedButton(
            mode_frame,
            values=["Focus", "Stopwatch", "Pomodoro"],
            command=self.switch_mode,
            font=self.body_font
        )
        self.mode_switch_pomo.pack(side="left")
        self.mode_switch_pomo.set("Pomodoro")
        
        # Main content
        content = ctk.CTkFrame(frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=50, pady=20)
        
        # Timer display
        self.pomo_timer_frame = ctk.CTkFrame(content, height=200)
        self.pomo_timer_frame.pack(pady=20)
        
        self.pomo_timer_display = ctk.CTkLabel(
            self.pomo_timer_frame,
            text=f"{self.data['settings']['focus_duration']:02d}:00",
            font=self.timer_font
        )
        self.pomo_timer_display.pack(pady=20)
        
        # Session info
        self.pomo_session_label = ctk.CTkLabel(
            self.pomo_timer_frame,
            text="Focus Session 1 of 4",
            font=self.subtitle_font
        )
        self.pomo_session_label.pack(pady=10)
        
        # Timer controls
        controls_frame = ctk.CTkFrame(content, fg_color="transparent")
        controls_frame.pack(pady=10)
        
        self.pomo_start_button = ctk.CTkButton(
            controls_frame,
            text="Start",
            command=self.start_pomodoro,
            height=40,
            width=100,
            font=self.subtitle_font,
            fg_color=self.primary_color,
            corner_radius=8
        )
        self.pomo_pause_button = ctk.CTkButton(
            controls_frame,
            text="Pause",
            command=self.pause_pomodoro,
            height=40,
            width=100,
            font=self.subtitle_font,
            state="disabled",
            corner_radius=8
        )
        self.pomo_stop_button = ctk.CTkButton(
            controls_frame,
            text="Stop",
            command=self.stop_pomodoro,
            height=40,
            width=100,
            font=self.subtitle_font,
            fg_color=self.danger_color,
            state="disabled",
            corner_radius=8
        )
        self.pomo_skip_button = ctk.CTkButton(
            controls_frame,
            text="Skip",
            command=self.skip_pomodoro_phase,
            height=40,
            width=100,
            font=self.subtitle_font,
            state="disabled",
            corner_radius=8
        )
        
        self.pomo_start_button.pack(side="left", padx=5)
        self.pomo_pause_button.pack(side="left", padx=5)
        self.pomo_stop_button.pack(side="left", padx=5)
        self.pomo_skip_button.pack(side="left", padx=5)
        
        # Settings frame
        settings_frame = ctk.CTkFrame(content)
        settings_frame.pack(fill="x", padx=50, pady=20)
        
        # Focus duration
        focus_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        focus_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(focus_frame, text="Focus Duration (min):").pack(side="left", padx=10)
        self.pomo_focus_menu = ctk.CTkOptionMenu(
            focus_frame,
            values=["15", "20", "25", "30", "45"],
            width=80,
            font=self.body_font
        )
        self.pomo_focus_menu.pack(side="left", padx=10)
        self.pomo_focus_menu.set(str(self.data["settings"]["focus_duration"]))
        
        # Short break
        short_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        short_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(short_frame, text="Short Break (min):").pack(side="left", padx=10)
        self.pomo_short_menu = ctk.CTkOptionMenu(
            short_frame,
            values=["3", "5", "7", "10"],
            width=80,
            font=self.body_font
        )
        self.pomo_short_menu.pack(side="left", padx=10)
        self.pomo_short_menu.set(str(self.data["settings"]["short_break"]))
        
        # Long break
        long_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        long_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(long_frame, text="Long Break (min):").pack(side="left", padx=10)
        self.pomo_long_menu = ctk.CTkOptionMenu(
            long_frame,
            values=["10", "15", "20", "25"],
            width=80,
            font=self.body_font
        )
        self.pomo_long_menu.pack(side="left", padx=10)
        self.pomo_long_menu.set(str(self.data["settings"]["long_break"]))
        
        # Cycles
        cycles_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        cycles_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(cycles_frame, text="Cycles before long break:").pack(side="left", padx=10)
        self.pomo_cycles_menu = ctk.CTkOptionMenu(
            cycles_frame,
            values=["2", "3", "4", "5", "6"],
            width=80,
            font=self.body_font
        )
        self.pomo_cycles_menu.pack(side="left", padx=10)
        self.pomo_cycles_menu.set(str(self.data["settings"]["pomodoro_cycles"]))
        
        # Task selection
        task_frame = ctk.CTkFrame(content, fg_color="transparent")
        task_frame.pack(fill="x", padx=50, pady=10)
        
        ctk.CTkLabel(task_frame, text="Work on:").pack(side="left", padx=10)
        self.pomo_task_var = ctk.StringVar(value="None")
        self.pomo_task_menu = ctk.CTkOptionMenu(
            task_frame,
            variable=self.pomo_task_var,
            values=self.get_task_options(),
            width=200,
            font=self.body_font
        )
        self.pomo_task_menu.pack(side="left", padx=10)

    def init_tasks(self):
        """Initialize tasks view"""
        frame = ctk.CTkFrame(self.content_frame)
        self.views["tasks"] = frame
        
        # Header
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(pady=20, fill="x")
        
        ctk.CTkLabel(
            header,
            text="Task Manager",
            font=self.title_font
        ).pack(side="left", padx=20)
        
        # Add task button
        ctk.CTkButton(
            header,
            text="+ Add Task",
            command=self.add_task_dialog,
            height=30,
            width=100,
            font=self.body_font,
            fg_color=self.secondary_color,
            corner_radius=8
        ).pack(side="right", padx=20)
        
        # Main content
        content = ctk.CTkFrame(frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Task list
        self.tasks_list_frame = ctk.CTkScrollableFrame(content)
        self.tasks_list_frame.pack(fill="both", expand=True)
        
        self.update_tasks_list()

    def init_habits(self):
        """Initialize habits view"""
        frame = ctk.CTkFrame(self.content_frame)
        self.views["habits"] = frame
        
        # Header
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(pady=20, fill="x")
        
        ctk.CTkLabel(
            header,
            text="Habit Tracker",
            font=self.title_font
        ).pack(side="left", padx=20)
        
        # Add habit button
        ctk.CTkButton(
            header,
            text="+ Add Habit",
            command=self.add_habit_dialog,
            height=30,
            width=100,
            font=self.body_font,
            fg_color=self.secondary_color,
            corner_radius=8
        ).pack(side="right", padx=20)
        
        # Main content
        content = ctk.CTkFrame(frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Habit list
        self.habits_list_frame = ctk.CTkScrollableFrame(content)
        self.habits_list_frame.pack(fill="both", expand=True)
        
        self.update_habits_list()

    def init_stats(self):
        """Initialize statistics view"""
        frame = ctk.CTkFrame(self.content_frame)
        self.views["stats"] = frame
        
        # Header
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(pady=20, fill="x")
        
        ctk.CTkLabel(
            header,
            text="Your Statistics",
            font=self.title_font
        ).pack(side="left", padx=20)
        
        # Time period selector
        period_frame = ctk.CTkFrame(header, fg_color="transparent")
        period_frame.pack(side="right", padx=20)
        
        ctk.CTkLabel(period_frame, text="Period:").pack(side="left", padx=5)
        self.stats_period = ctk.CTkOptionMenu(
            period_frame,
            values=["Today", "This Week", "This Month", "All Time"],
            command=self.update_stats,
            width=120,
            font=self.body_font
        )
        self.stats_period.pack(side="left")
        self.stats_period.set("Today")
        
        # Main content
        content = ctk.CTkFrame(frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Stats tabs
        self.stats_tabs = ctk.CTkTabview(content)
        self.stats_tabs.pack(fill="both", expand=True)
        
        self.stats_tabs.add("Overview")
        self.stats_tabs.add("Focus")
        self.stats_tabs.add("Tasks")
        self.stats_tabs.add("Habits")
        
        # Will be populated when shown
        self.stats_labels = {}

    def init_settings(self):
        """Initialize settings view"""
        frame = ctk.CTkFrame(self.content_frame)
        self.views["settings"] = frame
        
        # Header
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(pady=20, fill="x")
        
        ctk.CTkLabel(
            header,
            text="Settings",
            font=self.title_font
        ).pack(side="left", padx=20)
        
        # Main content
        content = ctk.CTkFrame(frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Settings tabs
        self.settings_tabs = ctk.CTkTabview(content)
        self.settings_tabs.pack(fill="both", expand=True)
        
        self.settings_tabs.add("General")
        self.settings_tabs.add("Timer")
        self.settings_tabs.add("Account")
        
        # General settings
        general_frame = self.settings_tabs.tab("General")
        
        # Theme selection
        theme_frame = ctk.CTkFrame(general_frame, fg_color="transparent")
        theme_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(theme_frame, text="Appearance Mode:").pack(side="left", padx=10)
        self.theme_var = ctk.StringVar(value=self.data["settings"]["theme"])
        theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            values=["dark", "light", "system"],
            variable=self.theme_var,
            command=self.change_theme,
            width=120,
            font=self.body_font
        )
        theme_menu.pack(side="right", padx=10)
        
        # Sound toggle
        sound_frame = ctk.CTkFrame(general_frame, fg_color="transparent")
        sound_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(sound_frame, text="Enable Sounds:").pack(side="left", padx=10)
        self.sound_var = ctk.BooleanVar(value=self.data["settings"]["sounds"])
        sound_switch = ctk.CTkSwitch(
            sound_frame,
            text="",
            variable=self.sound_var,
            command=self.toggle_sounds
        )
        sound_switch.pack(side="right", padx=10)
        
        # Notifications toggle
        notif_frame = ctk.CTkFrame(general_frame, fg_color="transparent")
        notif_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(notif_frame, text="Enable Notifications:").pack(side="left", padx=10)
        self.notif_var = ctk.BooleanVar(value=self.data["settings"]["notifications"])
        notif_switch = ctk.CTkSwitch(
            notif_frame,
            text="",
            variable=self.notif_var,
            command=self.toggle_notifications
        )
        notif_switch.pack(side="right", padx=10)
        
        # Timer settings
        timer_frame = self.settings_tabs.tab("Timer")
        
        # Daily goal
        goal_frame = ctk.CTkFrame(timer_frame, fg_color="transparent")
        goal_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(goal_frame, text="Daily Focus Goal (min):").pack(side="left", padx=10)
        self.goal_var = ctk.StringVar(value=str(self.data["user"]["daily_goal"]))
        goal_entry = ctk.CTkEntry(
            goal_frame,
            textvariable=self.goal_var,
            width=80,
            font=self.body_font
        )
        goal_entry.pack(side="right", padx=10)
        goal_entry.bind("<FocusOut>", self.update_daily_goal)
        
        # Auto-start breaks
        autobreak_frame = ctk.CTkFrame(timer_frame, fg_color="transparent")
        autobreak_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(autobreak_frame, text="Auto-start breaks:").pack(side="left", padx=10)
        self.autobreak_var = ctk.BooleanVar(value=self.data["settings"]["auto_start_breaks"])
        autobreak_switch = ctk.CTkSwitch(
            autobreak_frame,
            text="",
            variable=self.autobreak_var,
            command=self.toggle_auto_breaks
        )
        autobreak_switch.pack(side="right", padx=10)
        
        # Auto-start pomodoros
        autopomo_frame = ctk.CTkFrame(timer_frame, fg_color="transparent")
        autopomo_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(autopomo_frame, text="Auto-start pomodoros:").pack(side="left", padx=10)
        self.autopomo_var = ctk.BooleanVar(value=self.data["settings"]["auto_start_pomodoros"])
        autopomo_switch = ctk.CTkSwitch(
            autopomo_frame,
            text="",
            variable=self.autopomo_var,
            command=self.toggle_auto_pomodoros
        )
        autopomo_switch.pack(side="right", padx=10)
        
        # Account settings
        account_frame = self.settings_tabs.tab("Account")
        
        # User name
        name_frame = ctk.CTkFrame(account_frame, fg_color="transparent")
        name_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(name_frame, text="Your Name:").pack(side="left", padx=10)
        self.name_var = ctk.StringVar(value=self.data["user"]["name"])
        name_entry = ctk.CTkEntry(
            name_frame,
            textvariable=self.name_var,
            width=200,
            font=self.body_font
        )
        name_entry.pack(side="right", padx=10)
        name_entry.bind("<FocusOut>", self.update_user_name)
        
        # Export/import
        data_frame = ctk.CTkFrame(account_frame, fg_color="transparent")
        data_frame.pack(fill="x", pady=20)
        
        ctk.CTkButton(
            data_frame,
            text="Export Data",
            command=self.export_data,
            width=120,
            font=self.body_font
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            data_frame,
            text="Import Data",
            command=self.import_data,
            width=120,
            font=self.body_font
        ).pack(side="left", padx=10)
        
        # Help section
        help_frame = ctk.CTkFrame(account_frame, fg_color="transparent")
        help_frame.pack(fill="x", pady=20)
        
        ctk.CTkButton(
            help_frame,
            text="Help & Documentation",
            command=self.open_docs,
            width=180,
            font=self.body_font
        ).pack(side="left", padx=10)

    def show_view(self, view_name):
        """Show a specific view"""
        self.current_view = view_name
        
        # Hide all views
        for view in self.views.values():
            view.pack_forget()
        
        # Show selected view
        self.views[view_name].pack(fill="both", expand=True)
        self.update_status(f"{view_name.capitalize()} view loaded")
        
        # Update view-specific content
        if view_name == "dashboard":
            self.update_dashboard()
        elif view_name == "stats":
            self.update_stats()
        elif view_name == "tasks":
            self.update_tasks_list()
        elif view_name == "habits":
            self.update_habits_list()

    # ===== Timer Functions =====
    def switch_mode(self, mode):
        """Switch between timer modes"""
        self.mode = mode.lower()
        if self.mode == "focus":
            self.show_view("focus")
        elif self.mode == "stopwatch":
            self.show_view("stopwatch")
        elif self.mode == "pomodoro":
            self.show_view("pomodoro")

    def start_session(self):
        """Start focus session"""
        self.session_active = True
        self.start_time = time.time()
        self.selected_duration = int(self.duration_menu.get()) * 60
        self.start_button.configure(state="disabled")
        self.pause_button.configure(state="normal")
        self.stop_button.configure(state="normal")
        
        # Play sound if enabled
        if self.data["settings"]["sounds"] and SOUND_ENABLED:
            winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
        
        self.update_status("Focus session started")
        self.update_timer()

    def update_timer(self):
        """Update timer display"""
        if self.session_active:
            elapsed = time.time() - self.start_time
            remaining = max(0, self.selected_duration - elapsed)
            
            mins = int(remaining // 60)  # Convert to integer
            secs = int(remaining % 60)   # Convert to integer
            self.timer_display.configure(text=f"{mins:02d}:{secs:02d}")
            
            if remaining > 0:
                self.after(1000, self.update_timer)
            else:
                self.complete_session()

    def pause_session(self):
        """Pause focus session"""
        if self.session_active:
            self.session_active = False
            self.pause_button.configure(text="Resume")
            self.paused_time = time.time()
            self.update_status("Session paused")
        else:
            # Adjust start time for the pause duration
            pause_duration = time.time() - self.paused_time
            self.start_time += pause_duration
            self.session_active = True
            self.pause_button.configure(text="Pause")
            self.update_status("Session resumed")
            self.update_timer()

    def stop_session(self):
        """Stop focus session"""
        self.session_active = False
        elapsed = int(time.time() - self.start_time)
        
        # Only count if at least 1 minute was completed
        if elapsed >= 60:
            # Update stats
            self.data["user"]["sessions"] += 1
            self.data["user"]["total_seconds"] += elapsed
            self.data["user"]["xp"] += elapsed // 60 * 10
            
            # Check level up
            self.check_level_up()
            
            # Update streak
            self.update_streak()
            
            # Save session notes
            notes = self.notes_text.get("1.0", "end-1c").strip()
            if notes:
                task = self.task_var.get()
                if task != "None":
                    for t in self.data["user"]["tasks"]:
                        if t["name"] == task:
                            if "notes" not in t:
                                t["notes"] = []
                            t["notes"].append({
                                "date": datetime.now().isoformat(),
                                "content": notes
                            })
            
            self.save_data()
            
            # Play sound if enabled
            if self.data["settings"]["sounds"] and SOUND_ENABLED:
                winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
            
            self.update_status(f"Session completed: {elapsed//60} minutes")
        
        # Reset UI
        self.start_button.configure(state="normal")
        self.pause_button.configure(state="disabled", text="Pause")
        self.stop_button.configure(state="disabled")
        self.timer_display.configure(text=f"{self.data['settings']['focus_duration']:02d}:00")
        
        # Show dashboard if not already there
        if self.current_view != "dashboard":
            self.show_view("dashboard")

    def complete_session(self):
        """Handle completed focus session"""
        self.session_active = False
        elapsed = self.selected_duration
        
        # Update stats
        self.data["user"]["sessions"] += 1
        self.data["user"]["total_seconds"] += elapsed
        self.data["user"]["xp"] += elapsed // 60 * 10
        
        # Check level up
        self.check_level_up()
        
        # Update streak
        self.update_streak()
        
        # Save session notes
        notes = self.notes_text.get("1.0", "end-1c").strip()
        if notes:
            task = self.task_var.get()
            if task != "None":
                for t in self.data["user"]["tasks"]:
                    if t["name"] == task:
                        if "notes" not in t:
                            t["notes"] = []
                        t["notes"].append({
                            "date": datetime.now().isoformat(),
                            "content": notes
                        })
        
        self.save_data()
        
        # Play sound if enabled
        if self.data["settings"]["sounds"] and SOUND_ENABLED:
            winsound.PlaySound("SystemHand", winsound.SND_ALIAS)
        
        # Show completion dialog
        self.show_completion_dialog(f"Completed {self.duration_menu.get()} minute session!")
        
        # Reset UI
        self.start_button.configure(state="normal")
        self.pause_button.configure(state="disabled", text="Pause")
        self.stop_button.configure(state="disabled")
        self.timer_display.configure(text=f"{self.data['settings']['focus_duration']:02d}:00")
        self.notes_text.delete("1.0", "end")
        
        # Show dashboard
        self.show_view("dashboard")

    # ===== Stopwatch Functions =====
    def start_stopwatch(self):
        """Start stopwatch"""
        self.sw_running = True
        self.sw_start_time = time.time()
        self.sw_start_button.configure(state="disabled")
        self.sw_pause_button.configure(state="normal")
        self.sw_stop_button.configure(state="normal")
        self.sw_lap_button.configure(state="normal")
        
        self.update_status("Stopwatch started")
        self.update_stopwatch()

    def update_stopwatch(self):
        """Update stopwatch display"""
        if self.sw_running:
            elapsed = time.time() - self.sw_start_time
            hours = int(elapsed // 3600)
            mins = int((elapsed % 3600) // 60)
            secs = int(elapsed % 60)
            self.sw_timer_display.configure(text=f"{hours:02d}:{mins:02d}:{secs:02d}")
            self.after(1000, self.update_stopwatch)

    def pause_stopwatch(self):
        """Pause stopwatch"""
        self.sw_running = False
        self.sw_pause_time = time.time()
        self.sw_pause_button.configure(text="Resume")
        self.update_status("Stopwatch paused")

    def resume_stopwatch(self):
        """Resume stopwatch"""
        pause_duration = time.time() - self.sw_pause_time
        self.sw_start_time += pause_duration
        self.sw_running = True
        self.sw_pause_button.configure(text="Pause")
        self.update_status("Stopwatch resumed")
        self.update_stopwatch()

    def stop_stopwatch(self):
        """Stop stopwatch and record session"""
        self.sw_running = False
        elapsed = int(time.time() - self.sw_start_time)
        
        # Only count if at least 1 minute was completed
        if elapsed >= 60:
            # Update stats
            self.data["user"]["sessions"] += 1
            self.data["user"]["total_seconds"] += elapsed
            self.data["user"]["xp"] += elapsed // 60 * 10
            
            # Check level up
            self.check_level_up()
            
            # Update streak
            self.update_streak()
            
            self.save_data()
            
            # Play sound if enabled
            if self.data["settings"]["sounds"] and SOUND_ENABLED:
                winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
            
            self.update_status(f"Stopwatch session: {elapsed//60} minutes")
        
        # Reset UI
        self.sw_start_button.configure(state="normal")
        self.sw_pause_button.configure(state="disabled", text="Pause")
        self.sw_stop_button.configure(state="disabled")
        self.sw_lap_button.configure(state="disabled")
        self.sw_timer_display.configure(text="00:00:00")
        
        # Clear lap times
        for widget in self.lap_frame.winfo_children():
            widget.destroy()
        self.lap_times = []
        
        # Show dashboard if not already there
        if self.current_view != "dashboard":
            self.show_view("dashboard")

    def record_lap(self):
        """Record a lap time"""
        if self.sw_running:
            elapsed = time.time() - self.sw_start_time
            self.lap_times.append(elapsed)
            
            # Add lap to display
            lap_num = len(self.lap_times)
            lap_time = self.format_time(elapsed)
            
            if lap_num > 1:
                lap_diff = self.format_time(elapsed - self.lap_times[-2])
            else:
                lap_diff = lap_time
            
            lap_frame = ctk.CTkFrame(self.lap_frame, fg_color="transparent")
            lap_frame.pack(fill="x", pady=2)
            
            ctk.CTkLabel(
                lap_frame,
                text=f"Lap {lap_num}:",
                font=self.small_font,
                width=80
            ).pack(side="left")
            
            ctk.CTkLabel(
                lap_frame,
                text=lap_time,
                font=self.small_font,
                width=120
            ).pack(side="left")
            
            ctk.CTkLabel(
                lap_frame,
                text=f"+{lap_diff}",
                font=self.small_font,
                text_color=self.secondary_color,
                width=80
            ).pack(side="left")

    def format_time(self, seconds):
        """Format seconds into HH:MM:SS"""
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{mins:02d}:{secs:02d}"

    # ===== Pomodoro Functions =====
    def start_pomodoro(self):
        """Start pomodoro session"""
        self.pomo_running = True
        self.pomo_start_time = time.time()
        self.pomo_phase = "focus"  # focus, short_break, long_break
        self.pomo_cycles_completed = 0
        self.pomo_start_button.configure(state="disabled")
        self.pomo_pause_button.configure(state="normal")
        self.pomo_stop_button.configure(state="normal")
        self.pomo_skip_button.configure(state="normal")
        
        # Update settings from menu
        self.data["settings"]["focus_duration"] = int(self.pomo_focus_menu.get())
        self.data["settings"]["short_break"] = int(self.pomo_short_menu.get())
        self.data["settings"]["long_break"] = int(self.pomo_long_menu.get())
        self.data["settings"]["pomodoro_cycles"] = int(self.pomo_cycles_menu.get())
        self.save_data()
        
        # Set initial timer
        self.pomo_remaining = self.data["settings"]["focus_duration"] * 60
        self.pomo_session_label.configure(text=f"Focus Session 1 of {self.data['settings']['pomodoro_cycles']}")
        
        # Play sound if enabled
        if self.data["settings"]["sounds"] and SOUND_ENABLED:
            winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
        
        self.update_status("Pomodoro session started")
        self.update_pomodoro()

    def update_pomodoro(self):
        """Update pomodoro timer"""
        if self.pomo_running:
            elapsed = time.time() - self.pomo_start_time
            remaining = max(0, self.pomo_remaining - elapsed)
            
            mins = int(remaining // 60)
            secs = int(remaining % 60)
            self.pomo_timer_display.configure(text=f"{mins:02d}:{secs:02d}")
            
            if remaining > 0:
                self.after(1000, self.update_pomodoro)
            else:
                self.next_pomodoro_phase()

    def pause_pomodoro(self):
        """Pause pomodoro session"""
        if self.pomo_running:
            self.pomo_running = False
            self.pomo_pause_time = time.time()
            self.pomo_pause_button.configure(text="Resume")
            self.update_status("Pomodoro paused")
        else:
            # Adjust start time for the pause duration
            pause_duration = time.time() - self.pomo_pause_time
            self.pomo_start_time += pause_duration
            self.pomo_running = True
            self.pomo_pause_button.configure(text="Pause")
            self.update_status("Pomodoro resumed")
            self.update_pomodoro()

    def stop_pomodoro(self):
        """Stop pomodoro session"""
        self.pomo_running = False
        
        # Only count completed phases
        elapsed = int(time.time() - self.pomo_start_time)
        if self.pomo_phase == "focus" and elapsed >= 60:  # At least 1 minute of focus
            # Update stats
            self.data["user"]["sessions"] += 1
            self.data["user"]["total_seconds"] += elapsed
            self.data["user"]["xp"] += elapsed // 60 * 10
            
            # Check level up
            self.check_level_up()
            
            # Update streak
            self.update_streak()
            
            self.save_data()
            
            # Play sound if enabled
            if self.data["settings"]["sounds"] and SOUND_ENABLED:
                winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
            
            self.update_status(f"Pomodoro session: {elapsed//60} minutes")
        
        # Reset UI
        self.pomo_start_button.configure(state="normal")
        self.pomo_pause_button.configure(state="disabled", text="Pause")
        self.pomo_stop_button.configure(state="disabled")
        self.pomo_skip_button.configure(state="disabled")
        self.pomo_timer_display.configure(text=f"{self.data['settings']['focus_duration']:02d}:00")
        self.pomo_session_label.configure(text=f"Focus Session 1 of {self.data['settings']['pomodoro_cycles']}")
        
        # Show dashboard if not already there
        if self.current_view != "dashboard":
            self.show_view("dashboard")

    def skip_pomodoro_phase(self):
        """Skip current pomodoro phase"""
        self.next_pomodoro_phase(skipped=True)

    def next_pomodoro_phase(self, skipped=False):
        """Move to next pomodoro phase"""
        if not skipped and self.pomo_phase == "focus":
            # Only count completed focus phases
            elapsed = self.data["settings"]["focus_duration"] * 60
            self.data["user"]["sessions"] += 1
            self.data["user"]["total_seconds"] += elapsed
            self.data["user"]["xp"] += elapsed // 60 * 10
            self.pomo_cycles_completed += 1
            
            # Check level up
            self.check_level_up()
            
            # Update streak
            self.update_streak()
            
            self.save_data()
        
        # Determine next phase
        if self.pomo_phase == "focus":
            if self.pomo_cycles_completed % self.data["settings"]["pomodoro_cycles"] == 0:
                next_phase = "long_break"
                duration = self.data["settings"]["long_break"] * 60
                phase_name = "Long Break"
            else:
                next_phase = "short_break"
                duration = self.data["settings"]["short_break"] * 60
                phase_name = "Short Break"
        else:
            next_phase = "focus"
            duration = self.data["settings"]["focus_duration"] * 60
            phase_name = f"Focus Session {self.pomo_cycles_completed + 1} of {self.data['settings']['pomodoro_cycles']}"
        
        self.pomo_phase = next_phase
        self.pomo_remaining = duration
        self.pomo_start_time = time.time()
        self.pomo_session_label.configure(text=phase_name)
        
        # Play sound if enabled
        if self.data["settings"]["sounds"] and SOUND_ENABLED:
            winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
        
        # Show notification
        if self.data["settings"]["notifications"]:
            self.show_notification(f"Pomodoro: {phase_name}")
        
        # Auto-start next phase if enabled
        if ((next_phase == "focus" and self.data["settings"]["auto_start_pomodoros"]) or 
            (next_phase in ["short_break", "long_break"] and self.data["settings"]["auto_start_breaks"])):
            self.update_pomodoro()
        else:
            self.pomo_running = False
            self.pomo_pause_button.configure(text="Resume")

    # ===== Task Management =====
    def get_task_options(self):
        """Get list of task names for dropdown"""
        return ["None"] + [task["name"] for task in self.data["user"]["tasks"] if not task.get("completed", False)]

    def update_task_list(self):
        """Update the task list on dashboard"""
        for widget in self.task_list_frame.winfo_children():
            widget.destroy()
        
        # Show recent incomplete tasks (max 5)
        tasks = [t for t in self.data["user"]["tasks"] if not t.get("completed", False)]
        tasks = sorted(tasks, key=lambda x: x.get("priority", 3))[:5]
        
        if not tasks:
            ctk.CTkLabel(
                self.task_list_frame,
                text="No active tasks. Add some tasks to get started!",
                font=self.body_font,
                text_color="gray"
            ).pack(pady=10)
            return
        
        for task in tasks:
            self.create_task_widget(self.task_list_frame, task, dashboard=True)

    def update_tasks_list(self):
        """Update the full tasks list"""
        for widget in self.tasks_list_frame.winfo_children():
            widget.destroy()
        
        if not self.data["user"]["tasks"]:
            ctk.CTkLabel(
                self.tasks_list_frame,
                text="No tasks yet. Click 'Add Task' to create your first task!",
                font=self.body_font,
                text_color="gray"
            ).pack(pady=10)
            return
        
        # Separate completed and active tasks
        active_tasks = [t for t in self.data["user"]["tasks"] if not t.get("completed", False)]
        completed_tasks = [t for t in self.data["user"]["tasks"] if t.get("completed", False)]
        
        # Sort active tasks by priority then creation date
        active_tasks.sort(key=lambda x: (x.get("priority", 3), x.get("created", "")))
        
        # Show active tasks first
        if active_tasks:
            ctk.CTkLabel(
                self.tasks_list_frame,
                text="Active Tasks:",
                font=self.subtitle_font
            ).pack(anchor="w", pady=(0, 5))
            
            for task in active_tasks:
                self.create_task_widget(self.tasks_list_frame, task)
        
        # Show completed tasks
        if completed_tasks:
            ctk.CTkLabel(
                self.tasks_list_frame,
                text="Completed Tasks:",
                font=self.subtitle_font
            ).pack(anchor="w", pady=(10, 5))
            
            for task in completed_tasks:
                self.create_task_widget(self.tasks_list_frame, task)

    def create_task_widget(self, parent, task, dashboard=False):
        """Create a task widget for display"""
        task_frame = ctk.CTkFrame(parent, fg_color="transparent")
        task_frame.pack(fill="x", pady=2)
        
        # Checkbox for completion
        completed = task.get("completed", False)
        check_var = ctk.BooleanVar(value=completed)
        
        def toggle_completion():
            task["completed"] = check_var.get()
            if task["completed"]:
                task["completed_date"] = datetime.now().isoformat()
                # Award XP for completion
                self.data["user"]["xp"] += task.get("priority", 1) * 25
                self.check_level_up()
            self.save_data()
            if dashboard:
                self.update_task_list()
            else:
                self.update_tasks_list()
            self.update_dashboard()
        
        checkbox = ctk.CTkCheckBox(
            task_frame,
            text="",
            variable=check_var,
            command=toggle_completion,
            width=20
        )
        checkbox.pack(side="left", padx=5)
        
        # Task name with priority indicator
        priority = task.get("priority", 3)
        if priority == 1:
            color = self.danger_color
        elif priority == 2:
            color = self.warning_color
        else:
            color = "gray"
        
        name_label = ctk.CTkLabel(
            task_frame,
            text=task["name"],
            font=self.body_font,
            text_color="gray" if completed else None
        )
        name_label.pack(side="left", padx=5, fill="x", expand=True)
        
        # Priority indicator
        ctk.CTkLabel(
            task_frame,
            text="⬤",
            text_color=color,
            font=("Arial", 10)
        ).pack(side="left", padx=5)
        
        # Due date if exists
        if "due_date" in task and not dashboard:
            due_date = datetime.fromisoformat(task["due_date"]).strftime("%m/%d")
            due_label = ctk.CTkLabel(
                task_frame,
                text=due_date,
                font=self.small_font,
                text_color="gray"
            )
            due_label.pack(side="left", padx=10)
        
        # Edit button if not on dashboard
        if not dashboard:
            edit_btn = ctk.CTkButton(
                task_frame,
                text="✏️",
                width=30,
                height=30,
                fg_color="transparent",
                hover_color=("gray70", "gray30"),
                command=lambda t=task: self.edit_task_dialog(t)
            )
            edit_btn.pack(side="left", padx=2)
        
        # Notes indicator if exists
        if "notes" in task and len(task["notes"]) > 0 and not dashboard:
            notes_btn = ctk.CTkButton(
                task_frame,
                text=f"📝 ({len(task['notes'])})",
                width=50,
                height=30,
                fg_color="transparent",
                hover_color=("gray70", "gray30"),
                command=lambda t=task: self.show_task_notes(t)
            )
            notes_btn.pack(side="left", padx=2)
        
        # Delete button if not on dashboard
        if not dashboard:
            del_btn = ctk.CTkButton(
                task_frame,
                text="🗑️",
                width=30,
                height=30,
                fg_color="transparent",
                hover_color=("gray70", "gray30"),
                command=lambda t=task: self.delete_task(t)
            )
            del_btn.pack(side="left", padx=2)

    def add_task_dialog(self):
        """Show add task dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New Task")
        dialog.geometry("400x400")
        dialog.grab_set()
        
        ctk.CTkLabel(
            dialog,
            text="Add New Task",
            font=self.subtitle_font
        ).pack(pady=10)
        
        # Task name
        name_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        name_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(name_frame, text="Task Name:").pack(side="left")
        name_entry = ctk.CTkEntry(name_frame)
        name_entry.pack(side="right", fill="x", expand=True)
        
        # Priority
        priority_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        priority_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(priority_frame, text="Priority:").pack(side="left")
        self.priority_var = ctk.IntVar(value=3)
        
        ctk.CTkRadioButton(
            priority_frame,
            text="High",
            variable=self.priority_var,
            value=1,
            fg_color=self.danger_color
        ).pack(side="left", padx=5)
        
        ctk.CTkRadioButton(
            priority_frame,
            text="Medium",
            variable=self.priority_var,
            value=2,
            fg_color=self.warning_color
        ).pack(side="left", padx=5)
        
        ctk.CTkRadioButton(
            priority_frame,
            text="Low",
            variable=self.priority_var,
            value=3
        ).pack(side="left", padx=5)
        
        # Due date
        due_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        due_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(due_frame, text="Due Date (optional):").pack(side="left")
        self.due_date_var = ctk.StringVar()
        due_entry = ctk.CTkEntry(
            due_frame,
            textvariable=self.due_date_var,
            placeholder_text="MM/DD/YYYY"
        )
        due_entry.pack(side="right", fill="x", expand=True)
        
        # Description
        desc_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        desc_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(desc_frame, text="Description:").pack(anchor="w")
        desc_text = ctk.CTkTextbox(dialog, height=100)
        desc_text.pack(fill="x", padx=20, pady=5)
        
        # Buttons
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        def add_task():
            name = name_entry.get().strip()
            if not name:
                self.show_error("Task name cannot be empty!")
                return
            
            task = {
                "name": name,
                "priority": self.priority_var.get(),
                "created": datetime.now().isoformat(),
                "completed": False
            }
            
            due_date = self.due_date_var.get().strip()
            if due_date:
                try:
                    # Validate date format
                    datetime.strptime(due_date, "%m/%d/%Y")
                    task["due_date"] = datetime.strptime(due_date, "%m/%d/%Y").isoformat()
                except ValueError:
                    self.show_error("Invalid date format. Use MM/DD/YYYY")
                    return
            
            description = desc_text.get("1.0", "end-1c").strip()
            if description:
                task["description"] = description
            
            self.data["user"]["tasks"].append(task)
            self.save_data()
            
            # Update task dropdowns
            self.task_menu.configure(values=self.get_task_options())
            self.sw_task_menu.configure(values=self.get_task_options())
            self.pomo_task_menu.configure(values=self.get_task_options())
            
            self.update_task_list()
            self.update_tasks_list()
            self.update_dashboard()
            
            dialog.destroy()
            self.update_status(f"Task '{name}' added")
        
        ctk.CTkButton(
            btn_frame,
            text="Add Task",
            command=add_task,
            fg_color=self.secondary_color
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=dialog.destroy
        ).pack(side="right", padx=5)

    def edit_task_dialog(self, task):
        """Show edit task dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Task")
        dialog.geometry("400x400")
        dialog.grab_set()
        
        ctk.CTkLabel(
            dialog,
            text="Edit Task",
            font=self.subtitle_font
        ).pack(pady=10)
        
        # Task name
        name_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        name_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(name_frame, text="Task Name:").pack(side="left")
        name_entry = ctk.CTkEntry(name_frame)
        name_entry.insert(0, task["name"])
        name_entry.pack(side="right", fill="x", expand=True)
        
        # Priority
        priority_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        priority_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(priority_frame, text="Priority:").pack(side="left")
        self.edit_priority_var = ctk.IntVar(value=task.get("priority", 3))
        
        ctk.CTkRadioButton(
            priority_frame,
            text="High",
            variable=self.edit_priority_var,
            value=1,
            fg_color=self.danger_color
        ).pack(side="left", padx=5)
        
        ctk.CTkRadioButton(
            priority_frame,
            text="Medium",
            variable=self.edit_priority_var,
            value=2,
            fg_color=self.warning_color
        ).pack(side="left", padx=5)
        
        ctk.CTkRadioButton(
            priority_frame,
            text="Low",
            variable=self.edit_priority_var,
            value=3
        ).pack(side="left", padx=5)
        
        # Due date
        due_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        due_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(due_frame, text="Due Date:").pack(side="left")
        self.edit_due_date_var = ctk.StringVar()
        if "due_date" in task:
            self.edit_due_date_var.set(datetime.fromisoformat(task["due_date"]).strftime("%m/%d/%Y"))
        due_entry = ctk.CTkEntry(
            due_frame,
            textvariable=self.edit_due_date_var,
            placeholder_text="MM/DD/YYYY"
        )
        due_entry.pack(side="right", fill="x", expand=True)
        
        # Description
        desc_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        desc_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(desc_frame, text="Description:").pack(anchor="w")
        desc_text = ctk.CTkTextbox(dialog, height=100)
        if "description" in task:
            desc_text.insert("1.0", task["description"])
        desc_text.pack(fill="x", padx=20, pady=5)
        
        # Buttons
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        def save_task():
            name = name_entry.get().strip()
            if not name:
                self.show_error("Task name cannot be empty!")
                return
            
            task["name"] = name
            task["priority"] = self.edit_priority_var.get()
            
            due_date = self.edit_due_date_var.get().strip()
            if due_date:
                try:
                    # Validate date format
                    datetime.strptime(due_date, "%m/%d/%Y")
                    task["due_date"] = datetime.strptime(due_date, "%m/%d/%Y").isoformat()
                except ValueError:
                    self.show_error("Invalid date format. Use MM/DD/YYYY")
                    return
            elif "due_date" in task:
                del task["due_date"]
            
            description = desc_text.get("1.0", "end-1c").strip()
            if description:
                task["description"] = description
            elif "description" in task:
                del task["description"]
            
            self.save_data()
            
            # Update task dropdowns
            self.task_menu.configure(values=self.get_task_options())
            self.sw_task_menu.configure(values=self.get_task_options())
            self.pomo_task_menu.configure(values=self.get_task_options())
            
            self.update_task_list()
            self.update_tasks_list()
            self.update_dashboard()
            
            dialog.destroy()
            self.update_status(f"Task '{name}' updated")
        
        ctk.CTkButton(
            btn_frame,
            text="Save",
            command=save_task,
            fg_color=self.secondary_color
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=dialog.destroy
        ).pack(side="right", padx=5)

    def delete_task(self, task):
        """Delete a task"""
        self.data["user"]["tasks"].remove(task)
        self.save_data()
        
        # Update task dropdowns
        self.task_menu.configure(values=self.get_task_options())
        self.sw_task_menu.configure(values=self.get_task_options())
        self.pomo_task_menu.configure(values=self.get_task_options())
        
        self.update_task_list()
        self.update_tasks_list()
        self.update_dashboard()
        
        self.update_status(f"Task '{task['name']}' deleted")

    def show_task_notes(self, task):
        """Show notes for a task"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Notes for {task['name']}")
        dialog.geometry("500x400")
        dialog.grab_set()
        
        notes = task.get("notes", [])
        
        if not notes:
            ctk.CTkLabel(
                dialog,
                text="No notes for this task yet.",
                font=self.body_font
            ).pack(pady=20)
            return
        
        tabview = ctk.CTkTabview(dialog)
        tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        for note in notes:
            date = datetime.fromisoformat(note["date"]).strftime("%b %d, %Y %H:%M")
            tabview.add(date)
            
            textbox = ctk.CTkTextbox(tabview.tab(date))
            textbox.insert("1.0", note["content"])
            textbox.configure(state="disabled")
            textbox.pack(fill="both", expand=True, padx=5, pady=5)

    def get_completed_tasks_count(self):
        """Get count of completed tasks today"""
        today = datetime.now().date()
        count = 0
        for task in self.data["user"]["tasks"]:
            if task.get("completed", False):
                completed_date = datetime.fromisoformat(task.get("completed_date", "")).date()
                if completed_date == today:
                    count += 1
        return count

    # ===== Habit Tracking =====
    def update_habits_list(self):
        """Update the habits list"""
        for widget in self.habits_list_frame.winfo_children():
            widget.destroy()
        
        if not self.data["user"]["habits"]:
            ctk.CTkLabel(
                self.habits_list_frame,
                text="No habits yet. Click 'Add Habit' to create your first habit!",
                font=self.body_font,
                text_color="gray"
            ).pack(pady=10)
            return
        
        # Separate active and inactive habits
        active_habits = [h for h in self.data["user"]["habits"] if h["active"]]
        inactive_habits = [h for h in self.data["user"]["habits"] if not h["active"]]
        
        # Show active habits first
        if active_habits:
            ctk.CTkLabel(
                self.habits_list_frame,
                text="Active Habits:",
                font=self.subtitle_font
            ).pack(anchor="w", pady=(0, 5))
            
            for habit in active_habits:
                self.create_habit_widget(self.habits_list_frame, habit)
        
        # Show inactive habits
        if inactive_habits:
            ctk.CTkLabel(
                self.habits_list_frame,
                text="Inactive Habits:",
                font=self.subtitle_font
            ).pack(anchor="w", pady=(10, 5))
            
            for habit in inactive_habits:
                self.create_habit_widget(self.habits_list_frame, habit)

    def create_habit_widget(self, parent, habit):
        """Create a habit widget for display"""
        habit_frame = ctk.CTkFrame(parent, fg_color="transparent")
        habit_frame.pack(fill="x", pady=2)
        
        # Checkbox for today's completion
        today = datetime.now().date().isoformat()
        completed_today = today in habit.get("completions", [])
        check_var = ctk.BooleanVar(value=completed_today)
        
        def toggle_completion():
            if check_var.get():
                if "completions" not in habit:
                    habit["completions"] = []
                if today not in habit["completions"]:
                    habit["completions"].append(today)
                    # Award XP for completion
                    self.data["user"]["xp"] += 15
                    self.check_level_up()
            else:
                if "completions" in habit and today in habit["completions"]:
                    habit["completions"].remove(today)
            self.save_data()
            self.update_habits_list()
            self.update_dashboard()
        
        checkbox = ctk.CTkCheckBox(
            habit_frame,
            text="",
            variable=check_var,
            command=toggle_completion,
            width=20
        )
        checkbox.pack(side="left", padx=5)
        
        # Habit name
        name_label = ctk.CTkLabel(
            habit_frame,
            text=habit["name"],
            font=self.body_font,
            text_color="gray" if not habit["active"] else None
        )
        name_label.pack(side="left", padx=5, fill="x", expand=True)
        
        # Streak counter
        streak = self.calculate_habit_streak(habit)
        streak_label = ctk.CTkLabel(
            habit_frame,
            text=f"🔥 {streak}",
            font=self.small_font,
            text_color=self.warning_color
        )
        streak_label.pack(side="left", padx=10)
        
        # Edit button
        edit_btn = ctk.CTkButton(
            habit_frame,
            text="✏️",
            width=30,
            height=30,
            fg_color="transparent",
            hover_color=("gray70", "gray30"),
            command=lambda h=habit: self.edit_habit_dialog(h)
        )
        edit_btn.pack(side="left", padx=2)
        
        # Toggle active button
        toggle_text = "✅" if habit["active"] else "⚪"
        toggle_btn = ctk.CTkButton(
            habit_frame,
            text=toggle_text,
            width=30,
            height=30,
            fg_color="transparent",
            hover_color=("gray70", "gray30"),
            command=lambda h=habit: self.toggle_habit_active(h)
        )
        toggle_btn.pack(side="left", padx=2)
        
        # Delete button
        del_btn = ctk.CTkButton(
            habit_frame,
            text="🗑️",
            width=30,
            height=30,
            fg_color="transparent",
            hover_color=("gray70", "gray30"),
            command=lambda h=habit: self.delete_habit(h)
        )
        del_btn.pack(side="left", padx=2)

    def calculate_habit_streak(self, habit):
        """Calculate current streak for a habit"""
        if "completions" not in habit or not habit["completions"]:
            return 0
        
        # Sort dates in descending order
        dates = sorted([datetime.fromisoformat(d).date() for d in habit["completions"]], reverse=True)
        
        streak = 0
        today = datetime.now().date()
        expected_date = today
        
        for date in dates:
            if date == expected_date:
                streak += 1
                expected_date -= timedelta(days=1)
            else:
                break
        
        return streak

    def add_habit_dialog(self):
        """Show add habit dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New Habit")
        dialog.geometry("400x300")
        dialog.grab_set()
        
        ctk.CTkLabel(
            dialog,
            text="Add New Habit",
            font=self.subtitle_font
        ).pack(pady=10)
        
        # Habit name
        name_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        name_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(name_frame, text="Habit Name:").pack(side="left")
        name_entry = ctk.CTkEntry(name_frame)
        name_entry.pack(side="right", fill="x", expand=True)
        
        # Description
        desc_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        desc_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(desc_frame, text="Description:").pack(anchor="w")
        desc_text = ctk.CTkTextbox(dialog, height=100)
        desc_text.pack(fill="x", padx=20, pady=5)
        
        # Buttons
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        def add_habit():
            name = name_entry.get().strip()
            if not name:
                self.show_error("Habit name cannot be empty!")
                return
            
            habit = {
                "name": name,
                "created": datetime.now().isoformat(),
                "active": True
            }
            
            description = desc_text.get("1.0", "end-1c").strip()
            if description:
                habit["description"] = description
            
            self.data["user"]["habits"].append(habit)
            self.save_data()
            
            self.update_habits_list()
            self.update_dashboard()
            
            dialog.destroy()
            self.update_status(f"Habit '{name}' added")
        
        ctk.CTkButton(
            btn_frame,
            text="Add Habit",
            command=add_habit,
            fg_color=self.secondary_color
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=dialog.destroy
        ).pack(side="right", padx=5)

    def edit_habit_dialog(self, habit):
        """Show edit habit dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Habit")
        dialog.geometry("400x300")
        dialog.grab_set()
        
        ctk.CTkLabel(
            dialog,
            text="Edit Habit",
            font=self.subtitle_font
        ).pack(pady=10)
        
        # Habit name
        name_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        name_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(name_frame, text="Habit Name:").pack(side="left")
        name_entry = ctk.CTkEntry(name_frame)
        name_entry.insert(0, habit["name"])
        name_entry.pack(side="right", fill="x", expand=True)
        
        # Description
        desc_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        desc_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(desc_frame, text="Description:").pack(anchor="w")
        desc_text = ctk.CTkTextbox(dialog, height=100)
        if "description" in habit:
            desc_text.insert("1.0", habit["description"])
        desc_text.pack(fill="x", padx=20, pady=5)
        
        # Buttons
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        def save_habit():
            name = name_entry.get().strip()
            if not name:
                self.show_error("Habit name cannot be empty!")
                return
            
            habit["name"] = name
            
            description = desc_text.get("1.0", "end-1c").strip()
            if description:
                habit["description"] = description
            elif "description" in habit:
                del habit["description"]
            
            self.save_data()
            
            self.update_habits_list()
            self.update_dashboard()
            
            dialog.destroy()
            self.update_status(f"Habit '{name}' updated")
        
        ctk.CTkButton(
            btn_frame,
            text="Save",
            command=save_habit,
            fg_color=self.secondary_color
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=dialog.destroy
        ).pack(side="right", padx=5)

    def toggle_habit_active(self, habit):
        """Toggle habit active status"""
        habit["active"] = not habit["active"]
        self.save_data()
        self.update_habits_list()
        self.update_dashboard()
        
        status = "activated" if habit["active"] else "deactivated"
        self.update_status(f"Habit '{habit['name']}' {status}")

    def delete_habit(self, habit):
        """Delete a habit"""
        self.data["user"]["habits"].remove(habit)
        self.save_data()
        self.update_habits_list()
        self.update_dashboard()
        
        self.update_status(f"Habit '{habit['name']}' deleted")

    # ===== Stats Functions =====
    def update_stats(self, period=None):
        """Update statistics view"""
        if not period:
            period = self.stats_period.get()
        
        # Clear existing stats
        for tab in self.stats_tabs._tab_dict:
            for widget in self.stats_tabs.tab(tab).winfo_children():
                widget.destroy()
        
        # Calculate time range based on period
        today = datetime.now().date()
        if period == "Today":
            start_date = today
            end_date = today
        elif period == "This Week":
            start_date = today - timedelta(days=today.weekday())
            end_date = today
        elif period == "This Month":
            start_date = today.replace(day=1)
            end_date = today
        else:  # All Time
            start_date = None
            end_date = None
        
        # Overview tab
        overview_tab = self.stats_tabs.tab("Overview")
        
        # Total focus time
        total_seconds = self.get_focus_time_in_range(start_date, end_date)
        hours = total_seconds / 3600
        mins = total_seconds / 60
        
        ctk.CTkLabel(
            overview_tab,
            text=f"Total Focus Time: {hours:.1f} hours ({mins:.0f} minutes)",
            font=self.subtitle_font
        ).pack(pady=10)
        
        # Sessions completed
        sessions = self.get_sessions_in_range(start_date, end_date)
        ctk.CTkLabel(
            overview_tab,
            text=f"Sessions Completed: {sessions}",
            font=self.subtitle_font
        ).pack(pady=10)
        
        # Tasks completed
        tasks = self.get_completed_tasks_in_range(start_date, end_date)
        ctk.CTkLabel(
            overview_tab,
            text=f"Tasks Completed: {tasks}",
            font=self.subtitle_font
        ).pack(pady=10)
        
        # Habits tracked
        habits = self.get_habit_completions_in_range(start_date, end_date)
        ctk.CTkLabel(
            overview_tab,
            text=f"Habit Completions: {habits}",
            font=self.subtitle_font
        ).pack(pady=10)
        
        # Focus tab
        focus_tab = self.stats_tabs.tab("Focus")
        
        # Daily focus time chart (simplified)
        daily_data = self.get_daily_focus_data(start_date, end_date)
        if daily_data:
            max_time = max(daily_data.values()) / 60  # in minutes
            
            for date, seconds in daily_data.items():
                date_str = datetime.strptime(date, "%Y-%m-%d").strftime("%a %m/%d")
                mins = seconds / 60
                percent = (mins / max_time) * 100 if max_time > 0 else 0
                
                frame = ctk.CTkFrame(focus_tab, fg_color="transparent")
                frame.pack(fill="x", padx=20, pady=2)
                
                ctk.CTkLabel(
                    frame,
                    text=date_str,
                    width=100,
                    font=self.small_font
                ).pack(side="left")
                
                ctk.CTkLabel(
                    frame,
                    text=f"{mins:.0f} min",
                    width=60,
                    font=self.small_font
                ).pack(side="left")
                
                ctk.CTkProgressBar(
                    frame,
                    orientation="horizontal",
                    width=200,
                    height=15
                ).set(percent / 100)
                frame.pack(side="left")
        else:
            ctk.CTkLabel(
                focus_tab,
                text="No focus data available",
                font=self.body_font,
                text_color="gray"
            ).pack(pady=20)
        
        # Tasks tab
        tasks_tab = self.stats_tabs.tab("Tasks")
        
        # Completed tasks
        completed_tasks = [t for t in self.data["user"]["tasks"] if t.get("completed", False)]
        if start_date:
            completed_tasks = [
                t for t in completed_tasks 
                if "completed_date" in t and 
                datetime.fromisoformat(t["completed_date"]).date() >= start_date
            ]
            if end_date:
                completed_tasks = [
                    t for t in completed_tasks 
                    if datetime.fromisoformat(t["completed_date"]).date() <= end_date
                ]
        
        if completed_tasks:
            for task in completed_tasks:
                frame = ctk.CTkFrame(tasks_tab, fg_color="transparent")
                frame.pack(fill="x", padx=10, pady=2)
                
                date_str = datetime.fromisoformat(task["completed_date"]).strftime("%m/%d")
                ctk.CTkLabel(
                    frame,
                    text=date_str,
                    width=60,
                    font=self.small_font
                ).pack(side="left")
                
                ctk.CTkLabel(
                    frame,
                    text=task["name"],
                    font=self.small_font
                ).pack(side="left", fill="x", expand=True)
        else:
            ctk.CTkLabel(
                tasks_tab,
                text="No completed tasks",
                font=self.body_font,
                text_color="gray"
            ).pack(pady=20)
        
        # Habits tab
        habits_tab = self.stats_tabs.tab("Habits")
        
        # Habit streaks
        active_habits = [h for h in self.data["user"]["habits"] if h["active"]]
        if active_habits:
            for habit in active_habits:
                frame = ctk.CTkFrame(habits_tab, fg_color="transparent")
                frame.pack(fill="x", padx=10, pady=5)
                
                streak = self.calculate_habit_streak(habit)
                ctk.CTkLabel(
                    frame,
                    text=f"{habit['name']}: {streak} day streak",
                    font=self.body_font
                ).pack(side="left")
        else:
            ctk.CTkLabel(
                habits_tab,
                text="No active habits",
                font=self.body_font,
                text_color="gray"
            ).pack(pady=20)

    def get_focus_time_in_range(self, start_date, end_date):
        """Get total focus time in date range"""
        if not start_date:
            return self.data["user"]["total_seconds"]
        
        # This is a simplified version - in a real app you'd track sessions with timestamps
        if start_date == end_date:
            # For today, we can use the current session if active
            if hasattr(self, 'session_active') and self.session_active:
                elapsed = int(time.time() - self.start_time)
                return elapsed
            return 0
        
        # For demo purposes, we'll return a fraction of total time
        # In a real app, you'd have proper session tracking with timestamps
        if (datetime.now().date() - start_date).days <= 7:  # This week
            return self.data["user"]["total_seconds"] // 4
        elif (datetime.now().date() - start_date).days <= 30:  # This month
            return self.data["user"]["total_seconds"] // 2
        else:
            return self.data["user"]["total_seconds"]

    def get_sessions_in_range(self, start_date, end_date):
        """Get number of sessions in date range"""
        if not start_date:
            return self.data["user"]["sessions"]
        
        # Simplified - in a real app you'd track sessions with timestamps
        if start_date == end_date:
            return 1 if (hasattr(self, 'session_active') and self.session_active) else 0
        
        if (datetime.now().date() - start_date).days <= 7:  # This week
            return self.data["user"]["sessions"] // 4
        elif (datetime.now().date() - start_date).days <= 30:  # This month
            return self.data["user"]["sessions"] // 2
        else:
            return self.data["user"]["sessions"]

    def get_completed_tasks_in_range(self, start_date, end_date):
        """Get number of completed tasks in date range"""
        count = 0
        for task in self.data["user"]["tasks"]:
            if task.get("completed", False):
                if "completed_date" in task:
                    completed_date = datetime.fromisoformat(task["completed_date"]).date()
                    if (not start_date or completed_date >= start_date) and (not end_date or completed_date <= end_date):
                        count += 1
        return count

    def get_habit_completions_in_range(self, start_date, end_date):
        """Get number of habit completions in date range"""
        count = 0
        for habit in self.data["user"]["habits"]:
            if "completions" in habit:
                for date_str in habit["completions"]:
                    date = datetime.fromisoformat(date_str).date()
                    if (not start_date or date >= start_date) and (not end_date or date <= end_date):
                        count += 1
        return count

    def get_daily_focus_data(self, start_date, end_date):
        """Get daily focus time data (simplified for demo)"""
        if not start_date:
            start_date = datetime.now().date() - timedelta(days=30)
        
        if not end_date:
            end_date = datetime.now().date()
        
        data = {}
        current_date = start_date
        total_days = (end_date - start_date).days + 1
        
        # Distribute total seconds over the period
        total_seconds = self.get_focus_time_in_range(start_date, end_date)
        avg_seconds = total_seconds / total_days if total_days > 0 else 0
        
        while current_date <= end_date:
            # Add some randomness to make it look realistic
            seconds = max(0, int(avg_seconds * random.uniform(0.7, 1.3)))
            if seconds > 0:
                data[current_date.isoformat()] = seconds
            current_date += timedelta(days=1)
        
        return data

    # ===== Dashboard Functions =====
    def update_dashboard(self):
        """Update dashboard content with typewriter effect"""
        # Select a random greeting
        greeting = random.choice(self.greetings).format(self.data["user"]["name"])
        
        # Clear existing text
        self.dash_title.configure(text="")
        
        # Start typewriter effect
        self.typewriter_effect(self.dash_title, greeting, 0)
        
        self.user_name.configure(text=self.data["user"]["name"])
        self.user_level.configure(text=f"Level {self.data['user']['level']}")
        
        # Update phrase
        current = self.phrase_label.cget("text")
        new = random.choice([p for p in self.phrases if p != current])
        self.phrase_label.configure(text=new)
        
        # Update XP bar
        self.update_xp_bar()
        
        # Update task list
        self.update_task_list()

    def typewriter_effect(self, label, text, index):
        """Create a typewriter effect for text display"""
        if index < len(text):
            current_text = label.cget("text") + text[index]
            label.configure(text=current_text)
            # Randomize speed slightly for more natural effect
            speed = random.randint(30, 70)
            self.after(speed, lambda: self.typewriter_effect(label, text, index + 1))
        else:
            # Add blinking cursor effect at the end
            self.cursor_blink_effect(label)

    def cursor_blink_effect(self, label):
        """Add blinking cursor effect to label"""
        current_text = label.cget("text")
        
        def blink(on):
            if on:
                label.configure(text=current_text + "|")
            else:
                label.configure(text=current_text)
            self.after(500, lambda: blink(not on))
        
        blink(True)

    def get_today_seconds(self):
        """Get today's focus time in seconds"""
        # Simplified - in a real app you'd track sessions with timestamps
        if hasattr(self, 'session_active') and self.session_active:
            return int(time.time() - self.start_time)
        return 0

    # ===== Utility Functions =====
    def update_clock(self):
        """Update the clock in status bar"""
        now = datetime.now().strftime("%H:%M:%S")
        self.clock_label.configure(text=now)
        self.after(1000, self.update_clock)

    def update_status(self, message):
        """Update the status bar message"""
        self.status_label.configure(text=message)

    def update_xp_bar(self):
        """Update the XP progress bar"""
        xp = self.data["user"]["xp"]
        level = self.data["user"]["level"]
        xp_needed = level * 1000
        progress = min(1.0, xp / xp_needed)
        
        self.xp_bar.set(progress)
        self.xp_label.configure(text=f"Lvl {level} ({xp}/{xp_needed} XP)")

    def check_level_up(self):
        """Check if user has leveled up"""
        xp = self.data["user"]["xp"]
        level = self.data["user"]["level"]
        xp_needed = level * 1000
        
        if xp >= xp_needed:
            self.data["user"]["level"] += 1
            self.data["user"]["xp"] -= xp_needed
            self.show_level_up()
            self.save_data()
            return True
        return False

    def update_streak(self):
        """Update the user's streak"""
        today = datetime.now().date()
        last_session = datetime.fromisoformat(self.data["user"]["last_session"]).date() if self.data["user"]["last_session"] else None
        
        if last_session == today:
            pass  # Already updated today
        elif last_session is None or (today - last_session).days == 1:
            self.data["user"]["streak"] += 1
        else:
            self.data["user"]["streak"] = 1
        
        self.data["user"]["last_session"] = datetime.now().isoformat()

    def check_daily_reset(self):
        """Check if we need to reset daily stats"""
        today = datetime.now().date()
        last_reset = datetime.fromisoformat(self.data["user"]["last_reset"]).date() if self.data["user"]["last_reset"] else None
        
        if last_reset != today:
            # Reset daily stats
            self.data["user"]["last_reset"] = datetime.now().isoformat()
            # In a real app, you might reset daily counters here
            self.save_data()
        
        # Check again in 1 hour
        self.after(3600000, self.check_daily_reset)

    def show_level_up(self):
        """Show level up notification"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Level Up!")
        dialog.geometry("400x250")
        dialog.grab_set()
        
        ctk.CTkLabel(
            dialog,
            text="🎉 Level Up!",
            font=("Segoe UI", 24, "bold")
        ).pack(pady=20)
        
        ctk.CTkLabel(
            dialog,
            text=f"Congratulations! You've reached Level {self.data['user']['level']}!",
            font=self.subtitle_font,
            wraplength=350
        ).pack(pady=10)
        
        ctk.CTkButton(
            dialog,
            text="Continue",
            command=dialog.destroy,
            width=100,
            height=40,
            font=self.subtitle_font
        ).pack(pady=20)
        
        # Play sound if enabled
        if self.data["settings"]["sounds"] and SOUND_ENABLED:
            winsound.PlaySound("SystemHand", winsound.SND_ALIAS)

    def show_completion_dialog(self, message):
        """Show session completion dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Session Complete!")
        dialog.geometry("400x300")
        dialog.grab_set()
        
        ctk.CTkLabel(
            dialog,
            text="🎉 Great Job!",
            font=("Segoe UI", 24, "bold")
        ).pack(pady=20)
        
        ctk.CTkLabel(
            dialog,
            text=message,
            font=self.subtitle_font,
            wraplength=350
        ).pack(pady=10)
        
        # XP earned
        xp_earned = int(self.selected_duration / 60) * 10
        ctk.CTkLabel(
            dialog,
            text=f"+{xp_earned} XP",
            font=self.subtitle_font,
            text_color=self.secondary_color
        ).pack(pady=5)
        
        ctk.CTkButton(
            dialog,
            text="Continue",
            command=dialog.destroy,
            width=100,
            height=40,
            font=self.subtitle_font
        ).pack(pady=20)
        
        # Play sound if enabled
        if self.data["settings"]["sounds"] and SOUND_ENABLED:
            winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)

    def show_notification(self, message):
        """Show a notification (simplified for demo)"""
        # In a real app, you'd use a proper notification system
        self.update_status(f"Notification: {message}")

    def show_error(self, message):
        """Show an error message"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Error")
        dialog.geometry("300x150")
        dialog.grab_set()
        
        ctk.CTkLabel(
            dialog,
            text="⚠️ Error",
            font=self.subtitle_font,
            text_color=self.danger_color
        ).pack(pady=10)
        
        ctk.CTkLabel(
            dialog,
            text=message,
            font=self.body_font,
            wraplength=250
        ).pack(pady=5)
        
        ctk.CTkButton(
            dialog,
            text="OK",
            command=dialog.destroy,
            width=80,
            height=30
        ).pack(pady=10)

    def change_theme(self, choice):
        """Change application theme"""
        ctk.set_appearance_mode(choice)
        self.data["settings"]["theme"] = choice
        self.save_data()
        self.update_status(f"Theme changed to {choice}")

    def toggle_sounds(self):
        """Toggle sound effects"""
        self.data["settings"]["sounds"] = self.sound_var.get()
        self.save_data()
        status = "enabled" if self.data["settings"]["sounds"] else "disabled"
        self.update_status(f"Sounds {status}")

    def toggle_notifications(self):
        """Toggle notifications"""
        self.data["settings"]["notifications"] = self.notif_var.get()
        self.save_data()
        status = "enabled" if self.data["settings"]["notifications"] else "disabled"
        self.update_status(f"Notifications {status}")

    def toggle_auto_breaks(self):
        """Toggle auto-start breaks"""
        self.data["settings"]["auto_start_breaks"] = self.autobreak_var.get()
        self.save_data()
        status = "enabled" if self.data["settings"]["auto_start_breaks"] else "disabled"
        self.update_status(f"Auto-start breaks {status}")

    def toggle_auto_pomodoros(self):
        """Toggle auto-start pomodoros"""
        self.data["settings"]["auto_start_pomodoros"] = self.autopomo_var.get()
        self.save_data()
        status = "enabled" if self.data["settings"]["auto_start_pomodoros"] else "disabled"
        self.update_status(f"Auto-start pomodoros {status}")

    def update_daily_goal(self, event=None):
        """Update daily focus goal"""
        try:
            goal = int(self.goal_var.get())
            if goal <= 0:
                raise ValueError
            self.data["user"]["daily_goal"] = goal
            self.save_data()
            self.update_status(f"Daily goal updated to {goal} minutes")
        except ValueError:
            self.show_error("Daily goal must be a positive number")
            self.goal_var.set(str(self.data["user"]["daily_goal"]))

    def update_user_name(self, event=None):
        """Update user name"""
        name = self.name_var.get().strip()
        if name:
            self.data["user"]["name"] = name
            self.save_data()
            self.user_name.configure(text=name)
            self.update_status(f"Name updated to {name}")
        else:
            self.show_error("Name cannot be empty")
            self.name_var.set(self.data["user"]["name"])

    def export_data(self):
        """Export user data to file"""
        file_path = ctk.filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Export Data"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.data, f, indent=2)
                self.update_status(f"Data exported to {file_path}")
            except Exception as e:
                self.show_error(f"Error exporting data: {e}")

    def import_data(self):
        """Import user data from file"""
        file_path = ctk.filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")],
            title="Import Data"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    imported_data = json.load(f)
                
                # Ask for confirmation
                confirm = ctk.CTkToplevel(self)
                confirm.title("Confirm Import")
                confirm.geometry("400x200")
                confirm.grab_set()
                
                ctk.CTkLabel(
                    confirm,
                    text="This will overwrite your current data.",
                    font=self.subtitle_font
                ).pack(pady=20)
                
                ctk.CTkLabel(
                    confirm,
                    text="Are you sure you want to continue?",
                    font=self.body_font
                ).pack(pady=10)
                
                def do_import():
                    self.data = imported_data
                    self.save_data()
                    self.load_data()  # Reload to update UI
                    confirm.destroy()
                    self.update_status(f"Data imported from {file_path}")
                    self.show_view("dashboard")  # Refresh UI
                
                btn_frame = ctk.CTkFrame(confirm, fg_color="transparent")
                btn_frame.pack(pady=10)
                
                ctk.CTkButton(
                    btn_frame,
                    text="Import",
                    command=do_import,
                    fg_color=self.danger_color
                ).pack(side="left", padx=10)
                
                ctk.CTkButton(
                    btn_frame,
                    text="Cancel",
                    command=confirm.destroy
                ).pack(side="left", padx=10)
                
            except Exception as e:
                self.show_error(f"Error importing data: {e}")

    def open_docs(self):
        """Open documentation in browser"""
        webbrowser.open("https://github.com/Hamzaiscooly/FocusFlick")

    def on_closing(self):
        """Handle window closing"""
        if hasattr(self, 'session_active') and self.session_active:
            elapsed = int(time.time() - self.start_time)
            if elapsed >= 60:  # Only save if at least 1 minute
                self.data["user"]["total_seconds"] += elapsed
                self.save_data()
        
        self.destroy()

if __name__ == "__main__":
    app = FocusFlickPro()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()