import customtkinter as ctk
import webbrowser
import os
import sys
import threading
import urllib.request
import json
from tkinter import messagebox
from PIL import Image, ImageDraw
from modules.language_manager import get_text, lang_manager

# --- GİZLİLİK VE KULLANIM ŞARTLARI PENCERESİ ---
class PrivacyDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(get_text("privacy_title"))
        self.geometry("600x450")
        self.attributes("-topmost", True)
        self.transient(parent)
        self.grab_set()

        lbl_title = ctk.CTkLabel(self, text=get_text("privacy_title"), font=ctk.CTkFont(size=18, weight="bold"), text_color="#1976D2")
        lbl_title.pack(pady=(20, 10))

        self.textbox = ctk.CTkTextbox(self, width=500, height=300, font=ctk.CTkFont(size=13))
        self.textbox.pack(padx=20, pady=10, fill="both", expand=True)
        self.textbox.insert("1.0", get_text("privacy_text"))
        self.textbox.configure(state="disabled")

        ctk.CTkButton(self, text=get_text("dialog_ok"), width=150, height=40, command=self.destroy).pack(pady=15)


class HakkindaSayfasi(ctk.CTkScrollableFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        
        self.is_persistent = True 
        
        # Uygulamanın merkezi sürüm sabiti (Burayı değiştirmeniz yeterlidir)
        self.CURRENT_VERSION = "1.0.1" 
        
        # --- ÜST BAŞLIK VE ŞİRKET ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(20, 10))
        
        ctk.CTkLabel(self.header_frame, text="KITKARS-RADU MOBILE STUDIOS", font=ctk.CTkFont(size=36, weight="bold"), text_color="#F57C00").pack()
        self.lbl_mission = ctk.CTkLabel(self.header_frame, text=get_text("about_mission"), font=ctk.CTkFont(size=14), text_color="gray")
        self.lbl_mission.pack(pady=5)

        # --- GÜNCELLEME VE SÜRÜM BİLGİSİ ---
        self.version_frame = ctk.CTkFrame(self, fg_color=("gray85", "gray20"), corner_radius=15)
        self.version_frame.pack(fill="x", padx=60, pady=10)
        
        self.version_frame.grid_columnconfigure(0, weight=1)
        self.version_frame.grid_columnconfigure(1, weight=1)
        
        info_part = ctk.CTkFrame(self.version_frame, fg_color="transparent")
        info_part.grid(row=0, column=0, sticky="w", padx=30, pady=20)
        
        # ÇÖZÜM 1: Sürüm başlığını dil dosyasından bağımsız, CURRENT_VERSION sabitiyle dinamikleştiriyoruz
        self.lbl_version_title = ctk.CTkLabel(info_part, text=f"Docsas v{self.CURRENT_VERSION}", font=ctk.CTkFont(size=18, weight="bold"), text_color="#2E7D32")
        self.lbl_version_title.pack(anchor="w")
        self.lbl_update_info = ctk.CTkLabel(info_part, text=get_text("lbl_update_info"), font=ctk.CTkFont(size=12))
        self.lbl_update_info.pack(anchor="w", pady=(5,0))

        self.btn_update = ctk.CTkButton(
            self.version_frame, text=get_text("btn_check_update"), 
            font=ctk.CTkFont(size=14, weight="bold"), height=45, fg_color="#1565C0", hover_color="#0D47A1",
            command=self.check_update_systematically
        )
        self.btn_update.grid(row=0, column=1, sticky="e", padx=30, pady=20)

        # --- GÜVENLİK ROZETİ ---
        self.security_box = ctk.CTkFrame(self, fg_color=("#E3F2FD", "#0D1B2A"), border_width=2, border_color="#1976D2", corner_radius=15)
        self.security_box.pack(fill="x", padx=60, pady=(10, 10))
        
        self.lbl_sec_title = ctk.CTkLabel(self.security_box, text=get_text("lbl_security_title"), font=ctk.CTkFont(size=24, weight="bold"), text_color="#1976D2")
        self.lbl_sec_title.pack(pady=(25, 10))
        self.lbl_sec_desc = ctk.CTkLabel(self.security_box, text=get_text("lbl_security_desc"), font=ctk.CTkFont(size=16), justify="center", wraplength=700)
        self.lbl_sec_desc.pack(pady=(0, 25), padx=20)

        # --- UYGULAMA VİTRİNİ ---
        self.apps_container = ctk.CTkFrame(self, fg_color="transparent")
        self.apps_container.pack(fill="x", padx=50, pady=(10, 20))
        self.apps_container.grid_columnconfigure((0, 1), weight=1)

        self.radu_desc_lbl, self.radu_btn = self.create_app_card(
            parent=self.apps_container, col=0, image_filename="radu_logo.png", fallback_icon="🏆", 
            title="Radu Clash", desc_key="desc_radu", link="https://play.google.com/store/apps/details?id=com.kitkars.raduclash",
            box_color="#E65100", text_color="white", btn_color="#FF9800", btn_hover="#FB8C00"
        )

        self.deutsch_desc_lbl, self.deutsch_btn = self.create_app_card(
            parent=self.apps_container, col=1, image_filename="deutsch_logo.png", fallback_icon="🔤", 
            title="Deutschzone", desc_key="desc_deutsch", link="https://play.google.com/store/apps/details?id=com.kitkars.deutschzone38",
            box_color="#0D47A1", text_color="white", btn_color="#1E88E5", btn_hover="#1976D2"
        )

        # --- İLETİŞİM, WEB SİTESİ VE GİZLİLİK LİNKLERİ ---
        self.links_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.links_frame.pack(pady=10)

        self.btn_contact = ctk.CTkButton(
            self.links_frame, text=get_text("btn_contact"), font=ctk.CTkFont(weight="bold"), 
            fg_color="#388E3C", hover_color="#2E7D32", height=40,
            command=lambda: webbrowser.open("mailto:radugames58@gmail.com?subject=Docsas - Geri Bildirim")
        )
        self.btn_contact.pack(side="left", padx=10)

        # Yeni Eklenen Resmi Web Sitesi Butonu (Dil dosyası korumalı)
        site_text = "Resmi Web Sitemiz" if lang_manager.current_lang == "TR" else "Official Website"
        self.btn_website = ctk.CTkButton(
            self.links_frame, text=get_text("btn_web_site") if get_text("btn_web_site") != "btn_web_site" else site_text, 
            font=ctk.CTkFont(weight="bold"), fg_color="#6A1B9A", hover_color="#4A148C", height=40,
            command=lambda: webbrowser.open("https://kitkarsradu.github.io/kitkarsmobile/")
        )
        self.btn_website.pack(side="left", padx=10)

        self.btn_privacy = ctk.CTkButton(
            self.links_frame, text=get_text("btn_privacy"), font=ctk.CTkFont(weight="bold"), 
            fg_color="#D32F2F", hover_color="#B71C1C", height=40, command=self.show_privacy_policy
        )
        self.btn_privacy.pack(side="left", padx=10)

        # --- FOOTER ---
        self.lbl_footer = ctk.CTkLabel(self, text=get_text("footer_text"), font=ctk.CTkFont(size=11), text_color="gray")
        self.lbl_footer.pack(pady=(20, 5))
        
        ctk.CTkLabel(self, text="Prepared by Kitkars", font=ctk.CTkFont(size=15, weight="bold"), text_color="gray").pack(pady=(0, 30))

    def update_language(self):
        self.lbl_mission.configure(text=get_text("about_mission"))
        self.lbl_version_title.configure(text=f"Docsas v{self.CURRENT_VERSION}")
        self.lbl_update_info.configure(text=get_text("lbl_update_info"))
        self.btn_update.configure(text=get_text("btn_check_update"))
        
        self.lbl_sec_title.configure(text=get_text("lbl_security_title"))
        self.lbl_sec_desc.configure(text=get_text("lbl_security_desc"))
        
        self.radu_desc_lbl.configure(text=get_text("desc_radu"))
        self.radu_btn.configure(text=get_text("btn_visit_googleplay"))
        
        self.deutsch_desc_lbl.configure(text=get_text("desc_deutsch"))
        self.deutsch_btn.configure(text=get_text("btn_visit_googleplay"))
        
        self.btn_contact.configure(text=get_text("btn_contact"))
        self.btn_website.configure(text=get_text("btn_web_site")) # Dil tazeleyici eklendi
        self.btn_privacy.configure(text=get_text("btn_privacy"))
        self.lbl_footer.configure(text=get_text("footer_text"))

    def show_privacy_policy(self):
        PrivacyDialog(self.winfo_toplevel())

    def load_local_image(self, filename):
        if hasattr(sys, "_MEIPASS"):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        
        img_path = os.path.join(base_path, filename)

        if os.path.exists(img_path):
            try:
                img = Image.open(img_path).convert("RGBA")
                icon_size = (100, 100)
                img = img.resize(icon_size, Image.Resampling.LANCZOS)

                mask = Image.new("L", icon_size, 0)
                draw = ImageDraw.Draw(mask)
                draw.rounded_rectangle((0, 0, icon_size[0], icon_size[1]), radius=22, fill=255)

                white_bg = Image.new("RGBA", icon_size, (255, 255, 255, 255))
                white_bg.paste(img, (0, 0), img)

                icon_rounded = Image.new("RGBA", icon_size, (0, 0, 0, 0))
                icon_rounded.paste(white_bg, (0, 0), mask)

                canvas_size = (116, 116)
                final_img = Image.new("RGBA", canvas_size, (0, 0, 0, 0))

                shadow_mask = Image.new("L", icon_size, 0)
                shadow_draw = ImageDraw.Draw(shadow_mask)
                shadow_draw.rounded_rectangle((0, 0, icon_size[0], icon_size[1]), radius=22, fill=70)

                final_img.paste((0, 0, 0), (8, 10), shadow_mask)
                final_img.paste(icon_rounded, (5, 5), icon_rounded)

                return ctk.CTkImage(light_image=final_img, dark_image=final_img, size=canvas_size)
            except Exception:
                 return None
        return None

    def create_app_card(self, parent, col, image_filename, fallback_icon, title, desc_key, link, box_color, text_color, btn_color, btn_hover):
        card = ctk.CTkFrame(parent, corner_radius=20, fg_color=box_color, border_width=2, border_color=box_color)
        card.grid(row=0, column=col, padx=20, pady=10, sticky="nsew")
        
        img_ctk = self.load_local_image(image_filename)
        if img_ctk:
            icon_lbl = ctk.CTkLabel(card, text="", image=img_ctk)
            icon_lbl.pack(pady=(25, 5))
        else:
            icon_lbl = ctk.CTkLabel(card, text=fallback_icon, font=ctk.CTkFont(size=65), text_color=text_color)
            icon_lbl.pack(pady=(30, 10))
        
        title_lbl = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=22, weight="bold"), text_color=text_color)
        title_lbl.pack(pady=5)
        
        desc_lbl = ctk.CTkLabel(card, text=get_text(desc_key), font=ctk.CTkFont(size=13), text_color=text_color, wraplength=250, justify="center", height=60)
        desc_lbl.pack(pady=10, padx=20)
        
        btn = ctk.CTkButton(
            card, text=get_text("btn_visit_googleplay"), height=45, font=ctk.CTkFont(weight="bold", size=14),
            fg_color=btn_color, hover_color=btn_hover, text_color=text_color,
            command=lambda l=link: webbrowser.open(link)
        )
        btn.pack(pady=(10, 30))

        def on_enter(e): card.configure(border_color="white")
        def on_leave(e): card.configure(border_color=box_color)

        card.bind("<Enter>", on_enter); card.bind("<Leave>", on_leave)
        icon_lbl.bind("<Enter>", on_enter); title_lbl.bind("<Enter>", on_enter); desc_lbl.bind("<Enter>", on_enter)
        return desc_lbl, btn
    
    def check_update_systematically(self):
        """ Butona basıldığında arayüzü dondurmamak için kontrolü arka planda başlatır """
        self.btn_update.configure(state="disabled", text="Denetleniyor..." if lang_manager.current_lang == "TR" else "Checking...")
        threading.Thread(target=self._offline_safe_update_worker, daemon=True).start()

    def _offline_safe_update_worker(self):
        """GitHub üzerinden Docsas için güncel sürüm kontrolü yapar."""
        url = "https://raw.githubusercontent.com/KitkarsRadu/kitkarsmobile/refs/heads/main/version.json"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Docsas_App'})
            with urllib.request.urlopen(req, timeout=5) as response:
                raw_data = response.read().decode('utf-8').strip()
                data = json.loads(raw_data)
                
                remote_version = str(data.get("version", "1.0.0")).strip()
                update_url = str(data.get("url", "https://kitkarsradu.blogspot.com/")).strip()
                
                # ÇÖZÜM 2: Karşılaştırma ve GUI tetiklemesini daha izole ve garanti yolla paslıyoruz
                self.after(10, lambda: self._eval_update_result(remote_version, update_url))
        except Exception:
            # Hata durumunda (veya internet yoksa) doğrudan arayüze hata fırlat
            self.after(10, lambda: self._set_offline_ui())

    def _eval_update_result(self, remote_version, update_url):
        """Sürümleri dil dosyasından bağımsız koruma kuralıyla test eder."""
        self.btn_update.configure(state="normal", text=get_text("btn_check_update"))
        
        curr_v = str(self.CURRENT_VERSION).strip()
        rem_v = str(remote_version).strip()
        
        # ÇÖZÜM 3: Eğer dil dosyasındaki anahtarlar okunamazsa uygulamanın kilitlenmesini el yazısı yedeklerle önlüyoruz
        if rem_v > curr_v:
            title = get_text("update_dialog_title")
            if title == "update_dialog_title": title = "Yeni Sürüm Mevcut" # Dil yedeği
            
            raw_msg = get_text("update_dialog_msg")
            if raw_msg == "update_dialog_msg": 
                msg = f"Docsas için yeni bir güncelleme bulundu!\nMevcut Sürümünüz: v{curr_v}\nEn Son Sürüm: v{rem_v}"
            else:
                msg = raw_msg.format(curr_v, rem_v)
                
            if messagebox.askyesno(title, msg):
                webbrowser.open(update_url)
        else:
            title = get_text("update_latest_title")
            if title == "update_latest_title": title = "Sistem Güncel" # Dil yedeği
            
            raw_msg = get_text("update_latest_msg")
            if raw_msg == "update_latest_msg":
                msg = f"Docsas yazılımınız zaten en son sürümde (v{curr_v})."
            else:
                msg = raw_msg.format(curr_v)
                
            messagebox.showinfo(title, msg)

    def _set_offline_ui(self):
        """Çevrimdışı durum uyarısı"""
        self.btn_update.configure(state="normal", text=get_text("btn_check_update"))
        title = get_text("update_error_title")
        if title == "update_error_title": title = "Bağlantı Hatası"
        
        msg = get_text("update_error_msg")
        if msg == "update_error_msg": msg = "Güncelleme sunucusuna erişilemedi. İnternet bağlantınızı kontrol edin."
        
        messagebox.showwarning(title, msg)