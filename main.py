import ctypes
myappid = 'BerlinStoreApp' # اكتب أي اسم هنا
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
import customtkinter as ctk
import tkinter as tk
import os
import winreg
import re
import subprocess
import time
import logging
import webbrowser
import json
from threading import Thread
from typing import Optional, List, Dict, Any
from datetime import datetime
# Theme definitions
THEMES = {
    "dark": {
        "colors": {
            "main_bg": "#0f0c29",
            "sidebar_bg": "#1b1b2f",
            "card_bg": "#1a1a2e",
            "accent": "#ff007f",
            "accent_hover": "#ffffff",
            "secondary": "#00d2ff",
            "success": "#00b894",
            "error": "#d63031",
            "text_main": "#ffffff",
            "text_muted": "#a4b0be",
            "border": "#2d3436"
        }
    },
    #"light": {
        "colors": {
         #   "main_bg": "#f8f9fa",
        #    "sidebar_bg": "#ffffff",
         #   "card_bg": "#ffffff",
        #    "accent": "#007bff",
        #    "accent_hover": "#0056b3",
         #   "secondary": "#6c757d",
        #    "success": "#28a745",
        #    "error": "#dc3545",
        #    "text_main": "#212529",
        #    "text_muted": "#6c757d",
        #    "border": "#dee2e6"
        #}
    },
    "cyberpunk": {
        "colors": {
            "main_bg": "#0c0c0c",
            "sidebar_bg": "#1a0a1e",
            "card_bg": "#2a1a2e",
            "accent": "#ff0080",
            "accent_hover": "#ff1493",
            "secondary": "#00ffff",
            "success": "#00ff41",
            "error": "#ff0040",
            "text_main": "#ffffff",
            "text_muted": "#c0c0c0",
            "border": "#ff0080"
        }
    },
    "ocean": {
        "colors": {
            "main_bg": "#0a1628",
            "sidebar_bg": "#0f172a",
            "card_bg": "#1e293b",
            "accent": "#06b6d4",
            "accent_hover": "#0891b2",
            "secondary": "#3b82f6",
            "success": "#10b981",
            "error": "#ef4444",
            "text_main": "#f8fafc",
            "text_muted": "#94a3b8",
            "border": "#334155"
        }
    },
    "neon": {
        "colors": {
            "main_bg": "#000000",
            "sidebar_bg": "#0f0f0f",
            "card_bg": "#1a1a1a",
            "accent": "#ff00ff",
            "accent_hover": "#ff33ff",
            "secondary": "#00ffff",
            "success": "#00ff00",
            "error": "#ff0000",
            "text_main": "#ffffff",
            "text_muted": "#cccccc",
            "border": "#ff00ff"
        }
    }
}

STYLES = THEMES["dark"].copy()
STYLES.update({
    "fonts": {
        "h1": ("Segoe UI", 45, "bold"),
        "h2": ("Segoe UI", 28, "bold"),
        "h3": ("Segoe UI", 20, "bold"),
        "body_large": ("Segoe UI", 16, "normal"),
        "body_large_bold": ("Segoe UI", 16, "bold"),
        "body": ("Segoe UI", 14, "normal"),
        "small": ("Segoe UI", 12, "bold"),
        "logo": ("Segoe UI Black", 40, "bold")
    },
    "layout": {
        "corner_radius_large": 20,
        "corner_radius_medium": 15,
        "corner_radius_small": 8,
        "padding_large": 30,
        "padding_medium": 15
    }
})

class ThemeManager:
    @staticmethod
    def load_theme() -> str:
        try:
            with open("theme_config.json", "r") as f:
                config = json.load(f)
                return config.get("theme", "dark")
        except:
            return "dark"

    @staticmethod
    def save_theme(theme_name: str):
        try:
            with open("theme_config.json", "w") as f:
                json.dump({"theme": theme_name}, f)
        except Exception as e:
            logging.error(f"Failed to save theme: {e}")

    @staticmethod
    def apply_theme(theme_name: str) -> dict:
        global STYLES
        if theme_name in THEMES:
            STYLES["colors"] = THEMES[theme_name]["colors"].copy()
            ThemeManager.save_theme(theme_name)
            return STYLES
        return STYLES

class AnimationManager:
    @staticmethod
    def fade_in(widget, duration=300, steps=20):
        """Fade in animation for widgets"""
        if not hasattr(widget, '_animation_alpha'):
            widget._animation_alpha = 0.0

        def animate():
            widget._animation_alpha += 1.0 / steps
            if widget._animation_alpha >= 1.0:
                widget._animation_alpha = 1.0
                try:
                    widget.attributes("-alpha", 1.0)
                except:
                    pass  # Some widgets don't support alpha
            else:
                try:
                    widget.attributes("-alpha", widget._animation_alpha)
                except:
                    pass
                widget.after(int(duration / steps), animate)

        animate()

    @staticmethod
    def slide_in(widget, direction="right", duration=400, distance=50):
        """Slide in animation for widgets"""
        if direction == "right":
            start_x = -distance
            end_x = 0
        elif direction == "left":
            start_x = distance
            end_x = 0
        elif direction == "up":
            start_y = distance
            end_y = 0
        elif direction == "down":
            start_y = -distance
            end_y = 0
        else:
            return

        steps = 20
        step_duration = duration // steps

        if direction in ["right", "left"]:
            current_x = start_x
            step_size = (end_x - start_x) / steps

            def animate_x():
                nonlocal current_x
                current_x += step_size
                if abs(current_x - end_x) < abs(step_size):
                    current_x = end_x
                widget.place_configure(x=current_x)
                if current_x != end_x:
                    widget.after(step_duration, animate_x)

            animate_x()
        else:
            current_y = start_y
            step_size = (end_y - start_y) / steps

            def animate_y():
                nonlocal current_y
                current_y += step_size
                if abs(current_y - end_y) < abs(step_size):
                    current_y = end_y
                widget.place_configure(y=current_y)
                if current_y != end_y:
                    widget.after(step_duration, animate_y)

            animate_y()

logging.basicConfig(
    filename='berlin_steam.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("BerlinSteamApp")

class SteamManager:
    @staticmethod
    def get_steam_path() -> Optional[str]:
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
            path, _ = winreg.QueryValueEx(key, "SteamPath")
            return path.replace("/", "\\")
        except Exception as e:
            logger.error(f"Error: {e}")
            return None

    @staticmethod
    def get_accounts(steam_path: str) -> List[Dict[str, str]]:
        accounts = []
        config_path = os.path.join(steam_path, "config", "loginusers.vdf")
        if not os.path.exists(config_path):
            logger.warning(f"loginusers.vdf not found at {config_path}")
            return accounts
        try:
            # Try different encodings
            content = None
            for encoding in ['utf-8', 'utf-16', 'latin-1', 'cp1252']:
                try:
                    with open(config_path, "r", encoding=encoding) as f:
                        content = f.read()
                        break
                except:
                    continue
            
            if content is None:
                logger.error(f"Could not read {config_path} with any encoding")
                return accounts
            
            logger.info(f"File content length: {len(content)} characters")
            
            # Match Steam VDF format: "SteamID" on one line, { on next, then fields
            matches = re.findall(r'"(\d+)"\s*\n\s*{(.*?)}\s*\n', content, re.DOTALL)
            logger.info(f"Found {len(matches)} account entries")
            
            for steam_id, match in matches:
                # Use flexible whitespace matching for field names
                acc_name = re.search(r'"AccountName"\s+"([^"]*)"', match)
                persona_name = re.search(r'"PersonaName"\s+"([^"]*)"', match)
                most_recent = re.search(r'"MostRecent"\s+"([^"]*)"', match)
                
                if acc_name and persona_name:
                    account = {
                        "username": acc_name.group(1),
                        "nickname": persona_name.group(1),
                        "is_recent": most_recent.group(1) == "1" if most_recent else False
                    }
                    accounts.append(account)
                    logger.info(f"Added account: {account['username']}")
        except Exception as e:
            logger.error(f"Error reading accounts: {e}")
            import traceback
            logger.error(traceback.format_exc())
        return accounts

    @staticmethod
    def kill_steam():
        try:
            subprocess.call("taskkill /f /im steam.exe", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1.5)
        except Exception as e:
            logger.error(f"Error: {e}")

    @staticmethod
    def flush_steam_config():
        try:
            webbrowser.open("steam://flushconfig")
            return True
        except Exception as e:
            logger.error(f"Error: {e}")
            return False

class AccountCard(ctk.CTkFrame):
    def __init__(self, master, account_data: dict, switch_callback, **kwargs):
        super().__init__(master, fg_color=STYLES["colors"]["card_bg"], height=95, corner_radius=STYLES["layout"]["corner_radius_medium"], **kwargs)
        self.username = account_data["username"]
        self.nickname = account_data["nickname"]
        self.is_recent = account_data["is_recent"]
        self.switch_callback = switch_callback
        
        name_color = STYLES["colors"]["secondary"] if self.is_recent else STYLES["colors"]["text_main"]
        status_text = " • Last Active" if self.is_recent else ""
        
        self.lbl_nickname = ctk.CTkLabel(self, text=f"👤 {self.nickname} {status_text}", font=ctk.CTkFont(*STYLES["fonts"]["h3"]), text_color=name_color)
        self.lbl_nickname.place(x=25, y=20)
        
        self.lbl_username = ctk.CTkLabel(self, text=f"Steam ID: {self.username}", font=ctk.CTkFont(*STYLES["fonts"]["body"]), text_color=STYLES["colors"]["text_muted"])
        self.lbl_username.place(x=25, y=50)
        
        self.btn_switch = ctk.CTkButton(self, text="SWITCH & LOGIN", width=150, height=40, font=ctk.CTkFont("Segoe UI", 16, "bold"), fg_color="transparent", border_width=2, border_color=STYLES["colors"]["accent"], hover_color=STYLES["colors"]["accent"], corner_radius=STYLES["layout"]["corner_radius_small"], command=self.on_switch)
        self.btn_switch.place(relx=0.97, rely=0.5, anchor="e")
        
    def on_switch(self):
        self.btn_switch.configure(state="disabled", text="SWITCHING...")
        self.switch_callback(self.username, self.btn_switch)

class BerlinSteamApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.iconbitmap("logo.ico")  # Fallback for older Windows versions
        self.title("BerlinStoreApp")
        self.after(0, lambda: self.state('zoomed'))        
        self.configure(fg_color=STYLES["colors"]["main_bg"])
        self.minsize(950, 650)
    
        

        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (1150 // 2)
        y = (screen_height // 2) - (750 // 2)
        self.geometry(f"+{x}+{y}")

        self.steam_manager = SteamManager()
        self.nav_buttons = {}
        self.current_page = "home"
        self.theme_manager = ThemeManager()
        self.animation_manager = AnimationManager()
        self.start_time = datetime.now()  # For uptime tracking

        # Load saved theme
        saved_theme = self.theme_manager.load_theme()
        self.theme_manager.apply_theme(saved_theme)

        self._build_layout()
        self._build_sidebar()
        self._build_pages()
        self._build_statusbar()

        self.show_page("home", animate=True)
        self.set_status("System Ready", STYLES["colors"]["success"])

    def _build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar_frame = ctk.CTkFrame(self, fg_color=STYLES["colors"]["sidebar_bg"], corner_radius=0, width=280)
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=1, sticky="nsew", padx=30, pady=(30, 0))

    def _build_sidebar(self):
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="BERLIN", font=ctk.CTkFont(*STYLES["fonts"]["logo"]), text_color=STYLES["colors"]["accent"])
        self.logo_label.grid(row=0, column=0, padx=20, pady=(40, 5))
        
        # السطر المتصلح
        self.sub_logo = ctk.CTkLabel(self.sidebar_frame, text="DISTRICT v1.0 PRO", 
                              font=ctk.CTkFont(*STYLES["fonts"]["small"]), # شيلنا weight="bold"
                              text_color=STYLES["colors"]["text_muted"])
        self.sub_logo.grid(row=1, column=0, padx=20, pady=(0, 60))

        self.nav_buttons["home"] = self._create_nav_btn("🏠   DASHBOARD", lambda: self.show_page("home"), 2)
        self.nav_buttons["accounts"] = self._create_nav_btn("🎮   ACCOUNTS", lambda: self.show_page("accounts"), 3)
        self.nav_buttons["settings"] = self._create_nav_btn("⚙️   SETTINGS", lambda: self.show_page("settings"), 4)

    def _create_nav_btn(self, text: str, command, row: int):
    # التعديل هنا: نستخدم body_large_bold ونشيل الـ weight التاني
        btn = ctk.CTkButton(self.sidebar_frame, 
                         text=text, 
                         fg_color="transparent", 
                         anchor="w", 
                         height=55, 
                         font=ctk.CTkFont(*STYLES["fonts"]["body_large_bold"]), 
                         hover_color=STYLES["colors"]["card_bg"], 
                         corner_radius=STYLES["layout"]["corner_radius_small"], 
                         command=command)
        btn.grid(row=row, column=0, padx=20, pady=5, sticky="ew")
        return btn

    def _build_pages(self):
        self.pages = {
            "home": ctk.CTkFrame(self.container, fg_color=STYLES["colors"]["main_bg"]),
            "accounts": ctk.CTkFrame(self.container, fg_color=STYLES["colors"]["main_bg"]),
            "settings": ctk.CTkFrame(self.container, fg_color=STYLES["colors"]["main_bg"])
        }
        for frame in self.pages.values():
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self._setup_home_page()
        self._setup_accounts_page()
        self._setup_settings_page()

    def _build_statusbar(self):
        self.status_bar = ctk.CTkFrame(self, height=35, fg_color=STYLES["colors"]["sidebar_bg"], corner_radius=0)
        self.status_bar.grid(row=1, column=1, sticky="ew")
        self.status_bar.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(self.status_bar, text="Initializing...", font=ctk.CTkFont(*STYLES["fonts"]["small"]), text_color=STYLES["colors"]["text_muted"])
        self.status_label.pack(side="left", padx=20)
        
        self.time_label = ctk.CTkLabel(self.status_bar, text="", font=ctk.CTkFont(*STYLES["fonts"]["small"]), text_color=STYLES["colors"]["text_muted"])
        self.time_label.pack(side="right", padx=20)
        self._update_clock()

    def _update_clock(self):
        now = datetime.now().strftime("%I:%M %p")
        self.time_label.configure(text=now)
        self.after(60000, self._update_clock)

    def set_status(self, message: str, color: str = STYLES["colors"]["text_main"]):
        self.status_label.configure(text=message, text_color=color)

    def show_page(self, page_name: str, animate: bool = True):
        if page_name == self.current_page:
            return

        # Update navigation buttons
        for key, btn in self.nav_buttons.items():
            btn.configure(fg_color=STYLES["colors"]["accent"] if key == page_name else "transparent")

        # Animate page transition
        if animate:
            self._animate_page_transition(page_name)
        else:
            self.pages[page_name].lift()

        self.current_page = page_name

        # Page-specific actions
        if page_name == "accounts":
            self.refresh_accounts_list()
            self.set_status("Scanning for Steam accounts...", STYLES["colors"]["text_muted"])
        elif page_name == "home":
            self._update_home_stats()

    def _animate_page_transition(self, new_page: str):
        """Animate the transition between pages"""
        current_frame = self.pages[self.current_page]
        new_frame = self.pages[new_page]

        # Slide out current page
        AnimationManager.slide_in(current_frame, direction="left", duration=200)

        # After slide out, bring new page to front and slide in
        def bring_new_page():
            new_frame.lift()
            AnimationManager.slide_in(new_frame, direction="right", duration=300)
            AnimationManager.fade_in(new_frame, duration=300)

        self.after(150, bring_new_page)

    def _setup_home_page(self):
        # Main container with scrollable content
        main_container = ctk.CTkScrollableFrame(self.pages["home"], fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Welcome section
        welcome_frame = ctk.CTkFrame(main_container, fg_color=STYLES["colors"]["card_bg"], corner_radius=STYLES["layout"]["corner_radius_large"])
        welcome_frame.pack(fill="x", pady=(0, 20))

        title_label = ctk.CTkLabel(welcome_frame, text="🏠 WELCOME TO BERLIN DISTRICT",
                                  font=ctk.CTkFont(*STYLES["fonts"]["h1"]), text_color=STYLES["colors"]["accent"])
        title_label.pack(pady=(30, 10))

        subtitle_label = ctk.CTkLabel(welcome_frame, text="Advanced Steam Account Management Suite",
                                     font=ctk.CTkFont(*STYLES["fonts"]["body_large"]), text_color=STYLES["colors"]["text_muted"])
        subtitle_label.pack(pady=(0, 30))

        # Quick Actions
        actions_frame = ctk.CTkFrame(welcome_frame, fg_color="transparent")
        actions_frame.pack(fill="x", padx=30, pady=(0, 30))

        # Row 1: Main actions
        actions_row1 = ctk.CTkFrame(actions_frame, fg_color="transparent")
        actions_row1.pack(fill="x", pady=(0, 15))

        manage_btn = ctk.CTkButton(actions_row1, text="🎮 MANAGE ACCOUNTS", width=200, height=50,
                                  font=ctk.CTkFont(*STYLES["fonts"]["body_large"]),
                                  fg_color=STYLES["colors"]["secondary"], text_color="#000000",
                                  hover_color="#00a8cc", command=lambda: self.show_page("accounts"))
        manage_btn.pack(side="left", padx=(0, 15))

        settings_btn = ctk.CTkButton(actions_row1, text="⚙️ SETTINGS", width=150, height=50,
                                    font=ctk.CTkFont(*STYLES["fonts"]["body_large"]),
                                    fg_color=STYLES["colors"]["card_bg"], hover_color=STYLES["colors"]["sidebar_bg"],
                                    command=lambda: self.show_page("settings"))
        settings_btn.pack(side="left", padx=(0, 15))

        # Row 2: Utility actions
        actions_row2 = ctk.CTkFrame(actions_frame, fg_color="transparent")
        actions_row2.pack(fill="x")

        flush_btn = ctk.CTkButton(actions_row2, text="🧹 FLUSH CACHE", width=150, height=40,
                                 font=ctk.CTkFont(*STYLES["fonts"]["body"]),
                                 fg_color=STYLES["colors"]["error"], hover_color="#b02a2a",
                                 command=self.flush_steam)
        flush_btn.pack(side="left", padx=(0, 15))

        add_account_btn = ctk.CTkButton(actions_row2, text="➕ ADD ACCOUNT", width=150, height=40,
                                       font=ctk.CTkFont(*STYLES["fonts"]["body"]),
                                       fg_color=STYLES["colors"]["success"], hover_color="#2d7d32",
                                       command=self.open_steam_login)
        add_account_btn.pack(side="left")

        # Statistics section
        self.stats_frame = ctk.CTkFrame(main_container, fg_color=STYLES["colors"]["card_bg"],
                                       corner_radius=STYLES["layout"]["corner_radius_medium"])
        self.stats_frame.pack(fill="x", pady=(0, 20))

        stats_title = ctk.CTkLabel(self.stats_frame, text="📊 SYSTEM STATISTICS",
                                  font=ctk.CTkFont(*STYLES["fonts"]["h3"]), text_color=STYLES["colors"]["secondary"])
        stats_title.pack(pady=(20, 15))

        # Stats grid
        stats_container = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
        stats_container.pack(fill="x", padx=20, pady=(0, 20))

        # Row 1
        stats_row1 = ctk.CTkFrame(stats_container, fg_color="transparent")
        stats_row1.pack(fill="x", pady=(0, 10))

        self.accounts_stat = self._create_stat_card(stats_row1, "🎮 ACCOUNTS", "0", "Total Steam accounts detected")
        self.accounts_stat.pack(side="left", padx=(0, 10), fill="x", expand=True)

        self.steam_status_stat = self._create_stat_card(stats_row1, "🔗 STEAM STATUS", "Unknown", "Steam installation status")
        self.steam_status_stat.pack(side="left", padx=(0, 10), fill="x", expand=True)

        self.theme_stat = self._create_stat_card(stats_row1, "🎨 THEME", "Dark", "Current UI theme")
        self.theme_stat.pack(side="right", fill="x", expand=True)

        # Row 2
        stats_row2 = ctk.CTkFrame(stats_container, fg_color="transparent")
        stats_row2.pack(fill="x")

        self.uptime_stat = self._create_stat_card(stats_row2, "⏱️ UPTIME", "00:00:00", "Application runtime")
        self.uptime_stat.pack(side="left", padx=(0, 10), fill="x", expand=True)

        self.last_refresh_stat = self._create_stat_card(stats_row2, "🔄 LAST SCAN", "Never", "Last account scan time")
        self.last_refresh_stat.pack(side="left", fill="x", expand=True)

        # Recent Activity section
        activity_frame = ctk.CTkFrame(main_container, fg_color=STYLES["colors"]["card_bg"],
                                     corner_radius=STYLES["layout"]["corner_radius_medium"])
        activity_frame.pack(fill="x", pady=(0, 20))

        activity_title = ctk.CTkLabel(activity_frame, text="📝 RECENT ACTIVITY",
                                     font=ctk.CTkFont(*STYLES["fonts"]["h3"]), text_color=STYLES["colors"]["accent"])
        activity_title.pack(pady=(20, 15))

        self.activity_list = ctk.CTkScrollableFrame(activity_frame, fg_color="transparent", height=120)
        self.activity_list.pack(fill="x", padx=20, pady=(0, 20))

        # Add some initial activity items
        self._add_activity_item("🔄 Application started", "Just now")
        self._add_activity_item("🎨 Theme loaded: Dark", "Just now")
        self._add_activity_item("📊 Statistics initialized", "Just now")

        # Tips section
        tips_frame = ctk.CTkFrame(main_container, fg_color=STYLES["colors"]["card_bg"],
                                 corner_radius=STYLES["layout"]["corner_radius_medium"])
        tips_frame.pack(fill="x")

        tips_title = ctk.CTkLabel(tips_frame, text="💡 PRO TIPS",
                                 font=ctk.CTkFont(*STYLES["fonts"]["h3"]), text_color=STYLES["colors"]["success"])
        tips_title.pack(pady=(20, 15))

        tips = [
            "• Use 'FLUSH CACHE' to fix download/login issues",
            "• Switch accounts instantly without Steam restart",
            "• Customize themes in Settings for your preferred look",
            "• Monitor your account activity and statistics",
            "• Add multiple accounts for easy switching"
        ]

        for tip in tips:
            tip_label = ctk.CTkLabel(tips_frame, text=tip, font=ctk.CTkFont(*STYLES["fonts"]["body"]),
                                    text_color=STYLES["colors"]["text_muted"], anchor="w")
            tip_label.pack(fill="x", padx=20, pady=2)

        ctk.CTkLabel(tips_frame, text="", font=ctk.CTkFont(*STYLES["fonts"]["small"])).pack(pady=10)

    def _create_stat_card(self, parent, title: str, value: str, description: str):
        """Create a statistics card"""
        card = ctk.CTkFrame(parent, fg_color=STYLES["colors"]["sidebar_bg"],
                           corner_radius=STYLES["layout"]["corner_radius_small"])

        title_label = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(*STYLES["fonts"]["small"]),
                                  text_color=STYLES["colors"]["text_muted"])
        title_label.pack(pady=(15, 5))

        value_label = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(*STYLES["fonts"]["h2"]),
                                  text_color=STYLES["colors"]["accent"])
        value_label.pack()

        desc_label = ctk.CTkLabel(card, text=description, font=ctk.CTkFont(*STYLES["fonts"]["small"]),
                                 text_color=STYLES["colors"]["text_muted"])
        desc_label.pack(pady=(5, 15))

        # Store references for updates
        card.value_label = value_label
        card.title = title

        return card

    def _add_activity_item(self, action: str, timestamp: str):
        """Add an activity item to the recent activity list"""
        item_frame = ctk.CTkFrame(self.activity_list, fg_color="transparent")
        item_frame.pack(fill="x", pady=2)

        action_label = ctk.CTkLabel(item_frame, text=action, font=ctk.CTkFont(*STYLES["fonts"]["body"]),
                                   text_color=STYLES["colors"]["text_main"], anchor="w")
        action_label.pack(side="left", fill="x", expand=True)

        time_label = ctk.CTkLabel(item_frame, text=timestamp, font=ctk.CTkFont(*STYLES["fonts"]["small"]),
                                 text_color=STYLES["colors"]["text_muted"])
        time_label.pack(side="right")

    def _update_home_stats(self):
        """Update home page statistics"""
        try:
            # Update accounts count
            steam_path = self.steam_manager.get_steam_path()
            if steam_path:
                accounts = self.steam_manager.get_accounts(steam_path)
                self.accounts_stat.value_label.configure(text=str(len(accounts)))
                self.steam_status_stat.value_label.configure(text="Installed ✓", text_color=STYLES["colors"]["success"])
            else:
                self.accounts_stat.value_label.configure(text="0")
                self.steam_status_stat.value_label.configure(text="Not Found ✗", text_color=STYLES["colors"]["error"])

            # Update theme
            current_theme = self.theme_manager.load_theme()
            self.theme_stat.value_label.configure(text=current_theme.title())

            # Update last refresh time
            self.last_refresh_stat.value_label.configure(text=datetime.now().strftime("%H:%M:%S"))

        except Exception as e:
            logger.error(f"Error updating stats: {e}")

    def _update_uptime(self):
        """Update application uptime"""
        if hasattr(self, 'start_time'):
            uptime = datetime.now() - self.start_time
            hours, remainder = divmod(int(uptime.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            uptime_str = "06d"
            if hasattr(self, 'uptime_stat'):
                self.uptime_stat.value_label.configure(text=uptime_str)
        self.after(1000, self._update_uptime)
    def _setup_accounts_page(self):
        header = ctk.CTkFrame(self.pages["accounts"], fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(20, 10))
        
        ctk.CTkLabel(header, text="DETECTED ACCOUNTS", font=ctk.CTkFont(*STYLES["fonts"]["h2"]), text_color=STYLES["colors"]["secondary"]).pack(side="left")
        
        ctk.CTkButton(header, 
                      text="🔄 REFRESH", 
                      width=120, 
                      height=35, 
                      font=ctk.CTkFont(*STYLES["fonts"]["body"]), 
                      fg_color=STYLES["colors"]["card_bg"], 
                      hover_color=STYLES["colors"]["sidebar_bg"], 
                      command=self.refresh_accounts_list).pack(side="right")
        
        self.scroll_frame = ctk.CTkScrollableFrame(self.pages["accounts"], fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, pady=10)

    def _setup_settings_page(self):
        container = ctk.CTkScrollableFrame(self.pages["settings"], fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Theme Customization Section
        self._create_settings_section_title(container, "🎨 Theme Customization")
        theme_frame = self._create_settings_card(container)

        # Current theme display
        current_theme = self.theme_manager.load_theme()
        theme_label = ctk.CTkLabel(theme_frame, text=f"Current Theme: {current_theme.title()}",
                                  font=ctk.CTkFont(*STYLES["fonts"]["body_large"]))
        theme_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Theme selector
        theme_options = ["Dark", "Cyberpunk", "Ocean", "Neon"]
        self.theme_var = ctk.StringVar(value=current_theme.title())
        theme_menu = ctk.CTkOptionMenu(theme_frame, values=theme_options, variable=self.theme_var,
                                      command=self.change_theme, fg_color=STYLES["colors"]["sidebar_bg"],
                                      button_color=STYLES["colors"]["accent"], font=ctk.CTkFont(*STYLES["fonts"]["body"]))
        theme_menu.grid(row=0, column=1, padx=20, pady=(20, 10), sticky="e")

        # Theme preview cards
        preview_frame = ctk.CTkFrame(theme_frame, fg_color="transparent")
        preview_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=(10, 20), sticky="ew")

        themes = ["dark", "cyberpunk", "ocean", "neon"]
        for i, theme_name in enumerate(themes):
            preview_card = self._create_theme_preview(preview_frame, theme_name)
            preview_card.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            preview_frame.grid_columnconfigure(i, weight=1)

        # Appearance & UI Section
        self._create_settings_section_title(container, "🎯 Appearance & UI")
        app_frame = self._create_settings_card(container)

        # Interface scaling
        scaling_label = ctk.CTkLabel(app_frame, text="Interface Scaling:", font=ctk.CTkFont(*STYLES["fonts"]["body_large"]))
        scaling_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        self.scaling_var = ctk.StringVar(value="100%")
        scaling_menu = ctk.CTkOptionMenu(app_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                        variable=self.scaling_var, command=self.change_scaling,
                                        fg_color=STYLES["colors"]["sidebar_bg"], button_color=STYLES["colors"]["accent"],
                                        font=ctk.CTkFont(*STYLES["fonts"]["body"]))
        scaling_menu.grid(row=0, column=1, padx=20, pady=20, sticky="e")

        # Animation settings
        anim_label = ctk.CTkLabel(app_frame, text="Page Transitions:", font=ctk.CTkFont(*STYLES["fonts"]["body_large"]))
        anim_label.grid(row=1, column=0, padx=20, pady=(10, 20), sticky="w")

        self.animations_enabled = ctk.BooleanVar(value=True)
        anim_switch = ctk.CTkSwitch(app_frame, text="Enable smooth animations", variable=self.animations_enabled,
                                   command=self.toggle_animations, font=ctk.CTkFont(*STYLES["fonts"]["body"]))
        anim_switch.grid(row=1, column=1, padx=20, pady=(10, 20), sticky="e")

        app_frame.grid_columnconfigure(1, weight=1)

        # Steam Utilities Section
        self._create_settings_section_title(container, "🔧 Steam Utilities")
        util_frame = self._create_settings_card(container)

        flush_desc = ctk.CTkLabel(util_frame, text="Clear Steam Cache:\n(Fixes download/login loops)",
                                 font=ctk.CTkFont(*STYLES["fonts"]["body_large"]), justify="left")
        flush_desc.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        flush_btn = ctk.CTkButton(util_frame, text="FLUSH CONFIG", fg_color=STYLES["colors"]["error"],
                                 hover_color="#b02a2a", font=ctk.CTkFont(*STYLES["fonts"]["body"]),
                                 command=self.flush_steam)
        flush_btn.grid(row=0, column=1, padx=20, pady=20, sticky="e")

        # Auto-refresh settings
        auto_refresh_label = ctk.CTkLabel(util_frame, text="Auto-refresh accounts:",
                                         font=ctk.CTkFont(*STYLES["fonts"]["body_large"]))
        auto_refresh_label.grid(row=1, column=0, padx=20, pady=(10, 20), sticky="w")

        self.auto_refresh_var = ctk.BooleanVar(value=False)
        auto_refresh_switch = ctk.CTkSwitch(util_frame, text="Enable auto-refresh every 30s",
                                           variable=self.auto_refresh_var, command=self.toggle_auto_refresh,
                                           font=ctk.CTkFont(*STYLES["fonts"]["body"]))
        auto_refresh_switch.grid(row=1, column=1, padx=20, pady=(10, 20), sticky="e")

        util_frame.grid_columnconfigure(1, weight=1)

        # System Information Section
        self._create_settings_section_title(container, "ℹ️ System Information")
        info_frame = self._create_settings_card(container)

        steam_path = self.steam_manager.get_steam_path() or "Not Found on this system!"
        steam_path_label = ctk.CTkLabel(info_frame, text="Steam Path:", font=ctk.CTkFont("Segoe UI", 16, "bold"))
        steam_path_label.pack(anchor="w", padx=20, pady=(20, 5))

        steam_path_value = ctk.CTkLabel(info_frame, text=steam_path, font=ctk.CTkFont(*STYLES["fonts"]["body"]),
                                       text_color=STYLES["colors"]["text_muted"])
        steam_path_value.pack(anchor="w", padx=20, pady=(0, 10))

        # App version
        version_label = ctk.CTkLabel(info_frame, text="Version: Berlin District v3.0 PRO",
                                    font=ctk.CTkFont(*STYLES["fonts"]["body"]))
        version_label.pack(anchor="w", padx=20, pady=(10, 5))

        # Log file location
        log_label = ctk.CTkLabel(info_frame, text=f"Log File: {os.path.abspath('berlin_steam.log')}",
                                font=ctk.CTkFont(*STYLES["fonts"]["body"]), text_color=STYLES["colors"]["text_muted"])
        log_label.pack(anchor="w", padx=20, pady=(5, 20))

    def _create_theme_preview(self, parent, theme_name: str):
        """Create a theme preview card"""
        card = ctk.CTkFrame(parent, fg_color=THEMES[theme_name]["colors"]["card_bg"],
                           border_width=2, border_color=THEMES[theme_name]["colors"]["accent"],
                           corner_radius=STYLES["layout"]["corner_radius_small"])

        # Theme name
        name_label = ctk.CTkLabel(card, text=theme_name.title(),
                                 font=ctk.CTkFont(*STYLES["fonts"]["body_large_bold"]),
                                 text_color=THEMES[theme_name]["colors"]["text_main"])
        name_label.pack(pady=(10, 5))

        # Color indicators
        colors_frame = ctk.CTkFrame(card, fg_color="transparent")
        colors_frame.pack(pady=(0, 10))

        # Show accent, secondary, and background colors
        accent_indicator = ctk.CTkFrame(colors_frame, width=20, height=20,
                                       fg_color=THEMES[theme_name]["colors"]["accent"])
        accent_indicator.pack(side="left", padx=2)

        secondary_indicator = ctk.CTkFrame(colors_frame, width=20, height=20,
                                          fg_color=THEMES[theme_name]["colors"]["secondary"])
        secondary_indicator.pack(side="left", padx=2)

        bg_indicator = ctk.CTkFrame(colors_frame, width=20, height=20,
                                   fg_color=THEMES[theme_name]["colors"]["main_bg"])
        bg_indicator.pack(side="left", padx=2)

        # Select button
        select_btn = ctk.CTkButton(card, text="SELECT", width=80, height=25,
                                  font=ctk.CTkFont(*STYLES["fonts"]["small"]),
                                  fg_color=THEMES[theme_name]["colors"]["accent"],
                                  command=lambda: self.change_theme(theme_name.title()))
        select_btn.pack(pady=(5, 10))

        return card

    def change_theme(self, theme_name: str):
        """Change the application theme"""
        theme_key = theme_name.lower()
        if theme_key in THEMES:
            self.theme_manager.apply_theme(theme_key)
            self._apply_theme_to_ui()
            self.set_status(f"Theme changed to {theme_name}", STYLES["colors"]["success"])

            # Update theme selector
            self.theme_var.set(theme_name)

            # Add to activity log
            self._add_activity_item(f"🎨 Theme changed to {theme_name}", datetime.now().strftime("%H:%M:%S"))

    def _apply_theme_to_ui(self):
        """Apply the current theme to all UI elements"""
        try:
            # Update main window
            self.configure(fg_color=STYLES["colors"]["main_bg"])

            # Update sidebar
            self.sidebar_frame.configure(fg_color=STYLES["colors"]["sidebar_bg"])

            # Update logo colors
            self.logo_label.configure(text_color=STYLES["colors"]["accent"])
            self.sub_logo.configure(text_color=STYLES["colors"]["text_muted"])

            # Update navigation buttons
            for btn in self.nav_buttons.values():
                if btn == self.nav_buttons.get(self.current_page):
                    btn.configure(fg_color=STYLES["colors"]["accent"])
                else:
                    btn.configure(fg_color="transparent", hover_color=STYLES["colors"]["card_bg"])

            # Update all pages background
            for page in self.pages.values():
                page.configure(fg_color=STYLES["colors"]["main_bg"])

            # Update status bar
            self.status_bar.configure(fg_color=STYLES["colors"]["sidebar_bg"])
            self.status_label.configure(text_color=STYLES["colors"]["text_muted"])
            self.time_label.configure(text_color=STYLES["colors"]["text_muted"])

            # Update container
            self.container.configure(fg_color="transparent")

            # Force complete redraw
            self.update_idletasks()

            # Update home page stats if they exist
            if hasattr(self, 'stats_frame'):
                self._update_home_stats()

        except Exception as e:
            logger.error(f"Error applying theme: {e}")
            # Fallback to basic theme application
            self.configure(fg_color=STYLES["colors"]["main_bg"])
            self.sidebar_frame.configure(fg_color=STYLES["colors"]["sidebar_bg"])
            for page in self.pages.values():
                page.configure(fg_color=STYLES["colors"]["main_bg"])
            self.status_bar.configure(fg_color=STYLES["colors"]["sidebar_bg"])

    def toggle_animations(self):
        """Toggle page transition animations"""
        enabled = self.animations_enabled.get()
        self.set_status(f"Animations {'enabled' if enabled else 'disabled'}", STYLES["colors"]["success"])

    def toggle_auto_refresh(self):
        """Toggle automatic account list refresh"""
        enabled = self.auto_refresh_var.get()
        if enabled:
            self._start_auto_refresh()
            self.set_status("Auto-refresh enabled", STYLES["colors"]["success"])
        else:
            self._stop_auto_refresh()
            self.set_status("Auto-refresh disabled", STYLES["colors"]["text_muted"])

    def _start_auto_refresh(self):
        """Start automatic account refresh"""
        if hasattr(self, '_auto_refresh_id'):
            self.after_cancel(self._auto_refresh_id)
        self._auto_refresh_id = self.after(30000, self._auto_refresh_accounts)

    def _stop_auto_refresh(self):
        """Stop automatic account refresh"""
        if hasattr(self, '_auto_refresh_id'):
            self.after_cancel(self._auto_refresh_id)
            delattr(self, '_auto_refresh_id')

    def _auto_refresh_accounts(self):
        """Automatically refresh accounts list"""
        if self.current_page == "accounts" and self.auto_refresh_var.get():
            self.refresh_accounts_list()
            self._add_activity_item("🔄 Auto-refreshed accounts", datetime.now().strftime("%H:%M:%S"))
        if self.auto_refresh_var.get():
            self._start_auto_refresh()

    def _create_settings_section_title(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(*STYLES["fonts"]["h3"]), text_color=STYLES["colors"]["text_main"]).pack(anchor="w", pady=(20, 10))

    def _create_settings_card(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=STYLES["colors"]["card_bg"], corner_radius=STYLES["layout"]["corner_radius_medium"])
        frame.pack(fill="x", pady=5)
        return frame

    def change_scaling(self, new_scaling: str):
        scale_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(scale_float)
        self.set_status(f"UI Scale changed to {new_scaling}", STYLES["colors"]["success"])

    def flush_steam(self):
        success = self.steam_manager.flush_steam_config()
        if success:
            self.set_status("Steam config flush triggered.", STYLES["colors"]["success"])
        else:
            self.set_status("Failed to trigger Steam flush.", STYLES["colors"]["error"])

    def refresh_accounts_list(self):
        for child in self.scroll_frame.winfo_children():
            child.destroy()
        add_card = ctk.CTkFrame(self.scroll_frame, fg_color="transparent", height=80, corner_radius=STYLES["layout"]["corner_radius_medium"], border_width=2, border_color=STYLES["colors"]["secondary"])
        add_card.pack(fill="x", pady=(0, 25))
        ctk.CTkButton(add_card, text="➕   ADD NEW STEAM ACCOUNT", fg_color="transparent", font=ctk.CTkFont(*STYLES["fonts"]["h3"]), text_color=STYLES["colors"]["secondary"], hover_color=STYLES["colors"]["sidebar_bg"], command=self.open_steam_login).pack(fill="both", expand=True)

        steam_path = self.steam_manager.get_steam_path()
        if not steam_path:
            ctk.CTkLabel(self.scroll_frame, text="Steam is not installed on this system!", text_color=STYLES["colors"]["error"]).pack(pady=20)
            self.set_status("Error: Steam path not found", STYLES["colors"]["error"])
            return

        accounts = self.steam_manager.get_accounts(steam_path)
        if not accounts:
            ctk.CTkLabel(self.scroll_frame, text="No accounts found. Login to Steam first.", font=ctk.CTkFont(*STYLES["fonts"]["body_large"]), text_color=STYLES["colors"]["text_muted"]).pack(pady=40)
            self.set_status("No accounts found", STYLES["colors"]["text_muted"])
            return

        for acc in accounts:
            AccountCard(self.scroll_frame, acc, self.switch_account_process).pack(fill="x", pady=8)
        self.set_status(f"Loaded {len(accounts)} accounts successfully.", STYLES["colors"]["success"])

    def open_steam_login(self):
        self.set_status("Preparing to add new account...", STYLES["colors"]["secondary"])
        def task():
            self.steam_manager.kill_steam()
            path = self.steam_manager.get_steam_path()
            if path:
                steam_exe = os.path.join(path, "steam.exe")
                os.startfile(steam_exe, arguments="-login")
                self.after(0, lambda: self.set_status("Awaiting new account login.", STYLES["colors"]["success"]))
        Thread(target=task, daemon=True).start()

    def switch_account_process(self, username: str, btn_reference: ctk.CTkButton):
        self.set_status(f"Switching to {username}...", STYLES["colors"]["secondary"])
        def task():
            self.steam_manager.kill_steam()
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam", 0, winreg.KEY_WRITE)
                winreg.SetValueEx(key, "AutoLoginUser", 0, winreg.REG_SZ, username)
                winreg.SetValueEx(key, "RememberPassword", 0, winreg.REG_DWORD, 1)
                winreg.CloseKey(key)
            except Exception as e:
                logger.error(f"Error: {e}")
                self.after(0, lambda: self.set_status("Registry error occurred!", STYLES["colors"]["error"]))
                self.after(0, lambda: btn_reference.configure(state="normal", text="SWITCH & LOGIN"))
                return
            path = self.steam_manager.get_steam_path()
            if path:
                os.startfile(os.path.join(path, "steam.exe"))
            self.after(0, lambda: self.set_status(f"Successfully switched to {username}!", STYLES["colors"]["success"]))
            self.after(1000, lambda: btn_reference.configure(state="normal", text="SWITCH & LOGIN"))
            self.after(1000, self.refresh_accounts_list)
        Thread(target=task, daemon=True).start()

    def _auto_refresh_accounts(self):
        """Automatically refresh accounts list"""
        if self.current_page == "accounts" and self.auto_refresh_var.get():
            self.refresh_accounts_list()
            self._add_activity_item("🔄 Auto-refreshed accounts", datetime.now().strftime("%H:%M:%S"))
        if self.auto_refresh_var.get():
            self._start_auto_refresh()

if __name__ == "__main__":
    app = BerlinSteamApp()
    app._update_uptime()  # Start uptime tracking
    app.mainloop()