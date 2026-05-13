import customtkinter as ctk
import os
import winreg
import re
import subprocess
import time

# --- ألوان برلين (Berlin Signature) ---
MAIN_BG = "#0f0c29"
SIDEBAR_BG = "#1b1b2f"
ACCENT_COLOR = "#ff007f"
SECONDARY_ACCENT = "#00d2ff"

class BerlinSteamApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("BERLIN STORE - STEAM SWITCHER")
        self.geometry("1100x700")

        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(self, fg_color=SIDEBAR_BG, corner_radius=0, width=250)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="BERLIN", 
                                        font=ctk.CTkFont(size=35, weight="bold", family="Orbitron"),
                                        text_color=ACCENT_COLOR)
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 50))

        # زرار الحسابات
        self.steam_btn = ctk.CTkButton(self.sidebar_frame, text="  🎮  STEAM ACCOUNTS", 
                                        fg_color=ACCENT_COLOR, anchor="w", height=45)
        self.steam_btn.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        # زرار إضافة حساب جديد (اللي كان عامل المشكلة)
        self.add_acc_btn = ctk.CTkButton(self.sidebar_frame, text="  ➕  ADD NEW ACCOUNT", 
                                          fg_color="transparent", border_width=1, 
                                          border_color=SECONDARY_ACCENT, height=45,
                                          command=self.open_steam_login)
        self.add_acc_btn.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        # زرار Refresh
        self.refresh_btn = ctk.CTkButton(self.sidebar_frame, text="  🔄  REFRESH LIST", 
                                          fg_color="transparent", height=45,
                                          command=self.load_accounts)
        self.refresh_btn.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        # --- Main Content ---
        self.main_view = ctk.CTkFrame(self, fg_color=MAIN_BG, corner_radius=20)
        self.main_view.grid(row=0, column=1, padx=30, pady=30, sticky="nsew")

        self.content_title = ctk.CTkLabel(self.main_view, text="Steam Account Manager", 
                                           font=ctk.CTkFont(size=26, weight="bold"),
                                           text_color=SECONDARY_ACCENT)
        self.content_title.pack(pady=(40, 10), padx=40, anchor="w")

        self.scroll_frame = ctk.CTkScrollableFrame(self.main_view, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=30, pady=20)

        self.load_accounts()

    def get_steam_path(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
            path, _ = winreg.QueryValueEx(key, "SteamPath")
            return path.replace("/", "\\")
        except: return None

    def load_accounts(self):
        # مسح القائمة الحالية قبل إعادة التحميل
        for child in self.scroll_frame.winfo_children():
            child.destroy()
            
        steam_path = self.get_steam_path()
        if not steam_path: return
        
        config_path = os.path.join(steam_path, "config", "loginusers.vdf")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                content = f.read()
                matches = re.findall(r'"\d+"\s+{(.*?)}', content, re.DOTALL)
                for match in matches:
                    acc_name = re.search(r'"AccountName"\s+"(.*?)"', match)
                    persona_name = re.search(r'"PersonaName"\s+"(.*?)"', match)
                    if acc_name and persona_name:
                        self.add_account_card(persona_name.group(1), acc_name.group(1))

    def add_account_card(self, nickname, username):
        card = ctk.CTkFrame(self.scroll_frame, fg_color="#1a1a2e", height=90, corner_radius=15)
        card.pack(fill="x", pady=10, padx=5)
        
        ctk.CTkLabel(card, text=f"👤 {nickname}", font=ctk.CTkFont(size=18, weight="bold")).place(x=25, y=20)
        ctk.CTkLabel(card, text=f"User: {username}", text_color="gray").place(x=25, y=45)

        btn = ctk.CTkButton(card, text="SWITCH", width=120, height=35,
                            fg_color="transparent", border_width=2, border_color=ACCENT_COLOR,
                            hover_color=ACCENT_COLOR,
                            command=lambda u=username: self.switch_process(u))
        btn.place(x=680, y=28)

    def open_steam_login(self):
        subprocess.call("taskkill /f /im steam.exe", shell=True)
        time.sleep(1)
        steam_path = self.get_steam_path()
        if steam_path:
            steam_exe = os.path.join(steam_path, "steam.exe")
            subprocess.Popen([steam_exe, "-login"])
            print("Opening Steam Login Screen...")

    def switch_process(self, username):
        subprocess.call("taskkill /f /im steam.exe", shell=True)
        time.sleep(1)
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam", 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, "AutoLoginUser", 0, winreg.REG_SZ, username)
            winreg.SetValueEx(key, "RememberPassword", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Error: {e}")

        steam_path = self.get_steam_path()
        if steam_path:
            steam_exe = os.path.join(steam_path, "steam.exe")
            subprocess.Popen([steam_exe])

if __name__ == "__main__":
    app = BerlinSteamApp()
    app.mainloop()