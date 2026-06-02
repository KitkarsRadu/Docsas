import customtkinter as ctk
from tkinter import messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
import os
import sys
import platform
import subprocess
import json
import ctypes

# ==========================================
# --- SINGLE INSTANCE (ÇİFT AÇILMAYI ENGELLEME MOTORU) ---
# ==========================================
if platform.system() == "Windows":
    mutex_name = "Docsas_Kurumsal_Mutex_v1"
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
    if ctypes.windll.kernel32.GetLastError() == 183: 
        sys.exit(0) 

def get_resource_path(relative_path):
    """ PyInstaller ile paketlendiğinde veya terminalde ikonların doğru yolunu bulur """
    try:
        base_path = sys._MEIPASS
    except Exception:
        # Terminalden çalıştırıldığında kesin olarak main.py'nin yanına bakması için güncellendi
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

from modules.pdf_islemleri import PDFIslemleriSayfasi
from modules.ofis_islemleri import OfisIslemleriSayfasi
from modules.resim_islemleri import ResimIslemleriSayfasi
from modules.pdf_araclari import PDFAraclariSayfasi
from modules.pdf_karsilastirma import PDFKarsilastirmaSayfasi
from modules.gelismis_duzenleme import GelismisDuzenlemeSayfasi
from modules.hakkinda import HakkindaSayfasi
from modules.language_manager import lang_manager, get_text
from modules.form_islemleri import FormIslemleriSayfasi
from modules.makro_islemleri import MakroVeKaseSayfasi
from modules.pdf_olustur import PdfOlusturSayfasi

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")

class BelgeDonusturucuApp(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)

        self.title("Docsas - Modern ve Güvenli Kurumsal Belge Çözümleri" if lang_manager.current_lang == "TR" else "Docsas - Modern and Secure Corporate Document Solutions")
        self.after(0, lambda: self.state('zoomed'))
        self.current_active_frame_func = None 
        self.current_frame_instance = None
        self.settings_file = os.path.join(
            os.environ["APPDATA"],
            "Docsas",
            "app_settings.json"
        )
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)

        # ==========================================
        # --- LOGO VE GÖREV ÇUBUĞU (TASKBAR) AYARI ---
        # ==========================================
        try:
            icon_path = get_resource_path("icon.ico")
            self.iconbitmap(icon_path)
            if platform.system() == "Windows":
                myappid = 'docsas.kurumsal.yazilim.v1'
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

        # --- SÜRÜKLE BIRAK (DND) KAYDI ---
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.on_file_drop)

        self.all_tools = [
            {"id": "create", "text": "btn_create_pdf", "icon": "✨", "cmd": self.show_pdf_olustur_frame, "color": "#2E7D32", "hover": "#1B5E20"},
            {"id": "pdf", "text": "btn_pdf", "icon": "📄", "cmd": self.show_pdf_frame, "color": "#2B5B84", "hover": "#1E4364"},
            {"id": "word", "text": "btn_word", "icon": "📝", "cmd": self.show_ofis_frame, "color": "#276D49", "hover": "#1B5235"},
            {"id": "img", "text": "btn_img", "icon": "🖼️", "cmd": self.show_resim_frame, "color": "#6B3D82", "hover": "#4F2B61"},
            {"id": "tools", "text": "btn_pdf_tools", "icon": "🛠️", "cmd": self.show_pdf_araclari_frame, "color": "#0288D1", "hover": "#01579B"},
            {"id": "compare", "text": "btn_compare", "icon": "⚖️", "cmd": self.show_karsilastirma_frame, "color": "#8E24AA", "hover": "#6A1B9A"},
            {"id": "org", "text": "btn_org", "icon": "🗂️", "cmd": self.show_org_frame, "color": "#00897B", "hover": "#004D40"},
            {"id": "adv", "text": "btn_advanced", "icon": "⚙️", "cmd": self.show_gelismis_frame, "color": "#A85324", "hover": "#823F1A"},
            {"id": "ocr", "text": "btn_ocr", "icon": "🔍", "cmd": self.show_ocr_frame, "color": "#B8701E", "hover": "#8C5314"},
            {"id": "kvkk", "text": "btn_kvkk", "icon": "🛡️", "cmd": self.show_kvkk_frame, "color": "#9E2A2B", "hover": "#751E1F"},
            {"id": "form", "text": "btn_form", "icon": "📊", "cmd": self.show_form_frame, "color": "#1565C0", "hover": "#0D47A1"},
            {"id": "macro", "text": "btn_macro", "icon": "🪄", "cmd": self.show_makro_frame, "color": "#E65100", "hover": "#BF360C"}
        ]

        self.load_quick_access()

        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.pack(side="left", fill="y")

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text=get_text("menu_title"), font=ctk.CTkFont(size=20, weight="bold"), cursor="hand2")
        self.logo_label.pack(pady=20, padx=20)
        self.logo_label.bind("<Button-1>", lambda e: self.show_welcome_screen())

        self.btn_home = ctk.CTkButton(self.sidebar_frame, text=get_text("btn_home"), fg_color="gray30", hover_color="gray25", command=self.show_welcome_screen)
        self.btn_home.pack(pady=(0, 10), padx=20)

        btn_width = 190

        self.btn_create_pdf = ctk.CTkButton(self.sidebar_frame, text=get_text("btn_create_pdf"), width=btn_width, font=ctk.CTkFont(weight="bold"), fg_color="#2E7D32", hover_color="#1B5E20", command=self.show_pdf_olustur_frame)
        self.btn_create_pdf.pack(pady=8, padx=15)
        self.btn_pdf_islemleri = ctk.CTkButton(self.sidebar_frame, text=get_text("btn_pdf"), width=btn_width, command=self.show_pdf_frame)
        self.btn_pdf_islemleri.pack(pady=8, padx=15)
        self.btn_ofis_islemleri = ctk.CTkButton(self.sidebar_frame, text=get_text("btn_word"), width=btn_width, command=self.show_ofis_frame)
        self.btn_ofis_islemleri.pack(pady=8, padx=15)
        self.btn_resim_islemleri = ctk.CTkButton(self.sidebar_frame, text=get_text("btn_img"), width=btn_width, command=self.show_resim_frame)
        self.btn_resim_islemleri.pack(pady=8, padx=15)
        self.btn_pdf_araclari = ctk.CTkButton(self.sidebar_frame, text=get_text("btn_pdf_tools"), width=btn_width, command=self.show_pdf_araclari_frame)
        self.btn_pdf_araclari.pack(pady=8, padx=15)
        self.btn_compare = ctk.CTkButton(self.sidebar_frame, text=get_text("btn_compare"), width=btn_width, fg_color="#8E24AA", hover_color="#6A1B9A", command=self.show_karsilastirma_frame)
        self.btn_compare.pack(pady=8, padx=15)
        self.btn_org = ctk.CTkButton(self.sidebar_frame, text=get_text("btn_org"), width=btn_width, fg_color="#00897B", hover_color="#004D40", command=self.show_org_frame)
        self.btn_org.pack(pady=8, padx=15)
        self.btn_gelismis = ctk.CTkButton(self.sidebar_frame, text=get_text("btn_advanced"), width=btn_width, fg_color="#A85324", hover_color="#823F1A", command=self.show_gelismis_frame)
        self.btn_gelismis.pack(pady=8, padx=15)
        self.btn_ocr = ctk.CTkButton(self.sidebar_frame, text=get_text("btn_ocr"), width=btn_width, fg_color="#B8701E", hover_color="#8C5314", command=self.show_ocr_frame)
        self.btn_ocr.pack(pady=8, padx=15)
        self.btn_kvkk = ctk.CTkButton(self.sidebar_frame, text=get_text("btn_kvkk"), width=btn_width, font=ctk.CTkFont(weight="bold"), fg_color="#9E2A2B", hover_color="#751E1F", command=self.show_kvkk_frame)
        self.btn_kvkk.pack(pady=8, padx=15)
        self.btn_form = ctk.CTkButton(self.sidebar_frame, text=get_text("btn_form"), width=btn_width, font=ctk.CTkFont(weight="bold"), fg_color="#1565C0", hover_color="#0D47A1", command=self.show_form_frame)
        self.btn_form.pack(pady=8, padx=15) 
        self.btn_macro = ctk.CTkButton(self.sidebar_frame, text=get_text("btn_macro"), width=btn_width, font=ctk.CTkFont(weight="bold"), fg_color="#E65100", hover_color="#BF360C", command=self.show_makro_frame)
        self.btn_macro.pack(pady=(8, 20), padx=15) 

        self.btn_lang = ctk.CTkButton(self.sidebar_frame, text="Türkçe" if lang_manager.current_lang == "TR" else "English", width=btn_width, fg_color=("gray75", "gray30"), hover_color=("gray65", "gray20"), text_color=("black", "white"), command=self.toggle_language)
        self.btn_lang.pack(side="bottom", pady=(5, 20), padx=20)

        initial_theme_text = get_text("theme_light") if ctk.get_appearance_mode() == "Dark" else get_text("theme_dark")
        self.btn_theme = ctk.CTkButton(self.sidebar_frame, text=initial_theme_text, width=btn_width, fg_color=("gray75", "gray30"), hover_color=("gray65", "gray20"), text_color=("black", "white"), command=self.toggle_theme)
        self.btn_theme.pack(side="bottom", pady=5, padx=20)

        self.btn_about = ctk.CTkButton(self.sidebar_frame, text=get_text("btn_about"), width=btn_width, fg_color="transparent", border_width=1, border_color=("gray60", "gray40"), text_color=("black", "white"), hover_color=("gray85", "gray25"), command=self.show_about_frame)
        self.btn_about.pack(side="bottom", pady=5, padx=20)

        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self.show_welcome_screen()

    def load_quick_access(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    saved_ids = data.get("quick_access", [])
                    if len(saved_ids) == 6:
                        loaded_slots = []
                        for sid in saved_ids:
                            for t in self.all_tools:
                                if t["id"] == sid:
                                    loaded_slots.append(t)
                                    break
                        if len(loaded_slots) == 6:
                            self.quick_access_slots = loaded_slots
                            return
        except: pass
        
        self.quick_access_slots = [
            self.all_tools[0], self.all_tools[3], self.all_tools[6],
            self.all_tools[9], self.all_tools[7], self.all_tools[2]
        ]

    def save_quick_access(self):
        try:
            data = {}
            if os.path.exists(self.settings_file):
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    try: data = json.load(f)
                    except: pass
            
            data["quick_access"] = [slot["id"] for slot in self.quick_access_slots]
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except: pass

    def toggle_theme(self):
        if ctk.get_appearance_mode() == "Dark":
            ctk.set_appearance_mode("Light")
            self.btn_theme.configure(text=get_text("theme_dark"))
        else:
            ctk.set_appearance_mode("Dark")
            self.btn_theme.configure(text=get_text("theme_light"))

    def on_file_drop(self, event):
        if not hasattr(self, 'current_frame_instance') or self.current_frame_instance is None:
            return
        files = self.tk.splitlist(event.data)
        if hasattr(self.current_frame_instance, "add_dropped_files"):
            self.current_frame_instance.add_dropped_files(files)
        else:
            self.ask_what_to_do(files)

    def ask_what_to_do(self, files):
        dialog = ctk.CTkToplevel(self)
        dialog.title(get_text("msg_dnd_dialog_title"))
        dialog.geometry("800x550")
        dialog.attributes("-topmost", True)
        
        from modules.pdf_araclari import center_window
        dialog.update_idletasks()
        center_window(dialog, self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=get_text("msg_dnd_question"), font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 10))
        
        file_list_frame = ctk.CTkFrame(dialog, fg_color=("gray85", "gray20"), corner_radius=10)
        file_list_frame.pack(fill="x", padx=40, pady=10)
        
        ctk.CTkLabel(file_list_frame, text=get_text("lbl_dropped_files"), font=ctk.CTkFont(size=13, weight="bold"), text_color="gray").pack(pady=(5, 0))
        
        file_names = ", ".join([os.path.basename(f) for f in files])
        if len(file_names) > 150: file_names = file_names[:147] + "..."
        
        ctk.CTkLabel(file_list_frame, text=file_names, font=ctk.CTkFont(size=12), wraplength=700).pack(pady=(2, 10), padx=20)

        grid_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        grid_frame.pack(padx=20, pady=10, expand=True)

        for i, tool in enumerate(self.all_tools):
            r = i // 3
            c = i % 3
            btn = ctk.CTkButton(grid_frame, text=f"{tool['icon']} {get_text(tool['text'])}", width=220, height=50, fg_color=tool['color'], hover_color=tool['hover'], font=ctk.CTkFont(weight="bold"), command=lambda t=tool: route_files(t))
            btn.grid(row=r, column=c, padx=10, pady=10)
            
        def route_files(selected_tool):
            dialog.destroy()
            selected_tool['cmd']()
            self.after(150, lambda: self.current_frame_instance.add_dropped_files(files) if hasattr(self.current_frame_instance, "add_dropped_files") else None)

    def toggle_language(self):
        new_lang = "EN" if lang_manager.current_lang == "TR" else "TR"
        lang_manager.set_language(new_lang)
        
        self.btn_lang.configure(text="English" if new_lang == "EN" else "Türkçe")
        self.logo_label.configure(text=get_text("menu_title"))
        self.btn_home.configure(text=get_text("btn_home"))
        self.btn_create_pdf.configure(text=get_text("btn_create_pdf"))
        self.btn_pdf_islemleri.configure(text=get_text("btn_pdf"))
        self.btn_ofis_islemleri.configure(text=get_text("btn_word"))
        self.btn_resim_islemleri.configure(text=get_text("btn_img"))
        self.btn_pdf_araclari.configure(text=get_text("btn_pdf_tools"))
        self.btn_compare.configure(text=get_text("btn_compare"))
        self.btn_org.configure(text=get_text("btn_org"))
        self.btn_gelismis.configure(text=get_text("btn_advanced"))
        self.btn_ocr.configure(text=get_text("btn_ocr"))
        self.btn_kvkk.configure(text=get_text("btn_kvkk"))
        self.btn_form.configure(text=get_text("btn_form"))
        self.btn_macro.configure(text=get_text("btn_macro"))
        self.btn_about.configure(text=get_text("btn_about"))

        if ctk.get_appearance_mode() == "Dark": self.btn_theme.configure(text=get_text("theme_light"))
        else: self.btn_theme.configure(text=get_text("theme_dark"))

        if hasattr(self, "btn_guide_modal") and self.btn_guide_modal.winfo_exists():
            self.btn_guide_modal.configure(text="App Guide & Privacy" if lang_manager.current_lang == "EN" else "Rehber & Gizlilik")
            self.lbl_welcome_title.configure(text=get_text("menu_title"))
            self.lbl_welcome_sub.configure(text=get_text("welcome_subtitle"))
            self.lbl_qa_title.configure(text=get_text("quick_access_title"))
            self.lbl_shortcut_info.configure(text=get_text("msg_shortcut_info"))
            self.lbl_history_title.configure(text=get_text("lbl_history_title"))
            self.refresh_quick_access_slots()
            self.refresh_history_list()

        frame_names = ["pdf_frame_instance", "ofis_frame_instance", "resim_frame_instance", "pdf_araclari_instance", 
                       "kvkk_frame_instance", "karsilastirma_frame_instance", "gelismis_frame_instance", "org_frame_instance", 
                       "ocr_frame_instance", "about_frame_instance", "form_frame_instance", "makro_frame_instance", "pdf_olustur_instance"]
        for fn in frame_names:
            if hasattr(self, fn):
                inst = getattr(self, fn)
                if hasattr(inst, "update_language"): inst.update_language()
            
        if self.current_active_frame_func: self.current_active_frame_func()

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.pack_forget()

    def show_app_guide_modal(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Uygulama Rehberi & Gizlilik Politikası" if lang_manager.current_lang == "TR" else "App Guide & Privacy Policy")
        dialog.geometry("850x700")
        dialog.attributes("-topmost", True)
        
        dialog.update_idletasks()
        from modules.pdf_araclari import center_window
        center_window(dialog, self)
        
        scroll = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(scroll, text="🛡️ GÜVENLİK VE GİZLİLİK MANİFESTOSU" if lang_manager.current_lang == "TR" else "🛡️ SECURITY AND PRIVACY MANIFESTO", font=ctk.CTkFont(size=20, weight="bold"), text_color="#1565C0").pack(pady=(10, 10), anchor="w")
                     
        kvkk_text_tr = "Tüm işlemleriniz tamamen cihazınızda (yerel olarak) gerçekleşir. Belgeleriniz hiçbir şekilde uzak bir sunucuya yüklenmez, yapay zeka modelleriyle eğitilmez veya internet üzerinden paylaşılmaz. Avukatlık, muhasebe ve insan kaynakları gibi kritik sektörlerin standartlarına uygun, %100 çevrimdışı (offline) ve kapalı devre bir güvenlik altyapısı kullanmaktasınız."
        kvkk_text_en = "All your operations are processed entirely on your device (locally). Your documents are never uploaded to a remote server, used to train AI models, or shared over the internet. You are using a 100% offline and closed-loop security infrastructure compliant with strict legal, accounting, and HR standards."
        
        ctk.CTkLabel(scroll, text=kvkk_text_tr if lang_manager.current_lang == "TR" else kvkk_text_en, font=ctk.CTkFont(size=14), justify="left", wraplength=750).pack(pady=(0, 30), anchor="w", padx=10)
                     
        ctk.CTkLabel(scroll, text="🚀 MODÜLLER VE KULLANIM REHBERİ" if lang_manager.current_lang == "TR" else "🚀 MODULES AND USER GUIDE", font=ctk.CTkFont(size=20, weight="bold"), text_color="#E65100").pack(pady=(10, 15), anchor="w")

        explanations_tr = [
            "Sıfırdan etkileşimli formlar, profesyonel delil panoları, İK şablonları veya sözleşmeler tasarlayabileceğiniz gelişmiş stüdyo. Katman yönetimi, tipeks aracı ve zengin şekil kütüphanesiyle yaratıcılığınızı serbest bırakın.",
            "Mevcut PDF dosyalarınızı birleştirin, bölün, sayfalarını ayıklayın veya PDF'lerinizi yüksek çözünürlüklü resim formatlarına kayıpsız bir şekilde dönüştürün. Sayfa silme ve döndürme gibi temel işlemler burada yer alır.",
            "Ofis belgelerinizi (Word, Excel, PowerPoint) saniyeler içinde PDF formatına dönüştürün. Ayrıca PDF belgelerinizi düzenlenebilir Word (.docx) dosyaları haline getirerek metinleri dilediğiniz gibi değiştirin.",
            "Bilgisayarınızdaki fotoğrafları ve görselleri tek tıkla PDF albümlerine dönüştürün. Tersine işlemle de PDF'lerinizin içindeki sayfaları JPEG/PNG olarak yüksek çözünürlükte dışa aktarın.",
            "Günlük pratik ihtiyaçlarınızı çözen hızlı araçlar. PDF dosya boyutunu sıkıştırıp küçültme, sayfa numarası ekleme veya belgeye kurumsal damga/filigran (watermark) basma işlemlerini kolayca yapın.",
            "İki farklı sözleşme veya PDF raporu arasındaki metin farklarını hızla analiz edin. Değişen, silinen veya eklenen kelimeleri yan yana ekranda kırmızı ve yeşil vurgularla detaylıca görün.",
            "Birden fazla PDF belgesini görsel bir masaüstünde bir araya getirin. Sayfaları sürükleyip bırakarak yerlerini değiştirin, istemediğiniz sayfaları çöpe atın ve kusursuz yeni bir dosya olarak dışa aktarın.",
            "PDF'lerinizi adeta bir Word belgesi gibi satır satır, kelime kelime düzenleyin. Mevcut metinleri değiştirin, yeni paragraflar ekleyin veya belgelerin üzerine serbestçe çizim yapıp notlar alın.",
            "Taranmış fotoğraflardan, ekran görüntülerinden veya kilitli belgelerden metinleri okuyup çıkartın. Gelişmiş karakter tanıma (OCR) teknolojisi sayesinde resimleri kopyalanabilir gerçek yazılara çevirin.",
            "Belgelerinizi askeri düzeyde algoritmalarla şifreleyin veya mevcut şifreleri kaldırın. En önemlisi; yasal metinlerde görünmesini istemediğiniz isim, TC No gibi alanları kalıcı olarak siyah bantla karartın (Redaction).",
            "Yüzlerce satırlık Excel listelerindeki verileri, PDF şablonlarındaki boşluklara otomatik olarak basın. Tek tıkla binlerce kişiye özel mutabakat formu, bordro veya dilekçe üretip zamandan devasa tasarruf edin.",
            "Sürekli tekrarladığınız 3-4 farklı işlemi (örneğin: birleştir -> sıkıştır -> filigran ekle) tek bir butona bağlayıp zincirleme (makro) çalıştırın. Ayrıca yüzlerce sayfaya otomatik yasal kaşe ve Bates numarası basın."
        ]
        explanations_en = [
            "Advanced studio to design interactive forms, professional evidence boards, HR templates, or contracts from scratch. Unleash your creativity with layer management, whiteout tool, and rich shape library.",
            "Merge, split, extract pages from your existing PDF files or losslessly convert PDFs to high-resolution image formats. Basic operations like page deletion and rotation are located here.",
            "Convert your office documents (Word, Excel, PowerPoint) to PDF format in seconds. Alternatively, transform your PDF documents into editable Word (.docx) files to modify texts as you wish.",
            "Turn photos and images on your computer into PDF albums with a single click. Conversely, extract pages from your PDFs as high-resolution JPEG/PNG files.",
            "Quick tools solving practical daily needs. Easily compress and reduce PDF file size, add page numbers, or stamp your documents with corporate watermarks.",
            "Simple analysis of text differences between two contracts or PDF reports. See changed, deleted, or added words side-by-side with detailed red and green highlights.",
            "Bridge multiple PDF documents together on a visual desktop. Drag and drop pages to rearrange, trash unwanted pages, and export as a flawless new file.",
            "Edit your PDFs line-by-line, word-by-word almost like a Word document. Modify existing texts, add new paragraphs, or freely draw and take notes on documents.",
            "Extract and read text from scanned photos, screenshots, or locked documents. Turn images into actual, copyable text using advanced Optical Character Recognition (OCR) technology.",
            "Encrypt your documents with military-grade algorithms or remove existing passwords. Crucially, permanently redact sensitive areas like names or IDs with black bands (Redaction).",
            "Automatically populate blank spaces in PDF templates with data from hundreds of Excel rows. Generate personalized reconciliation forms, payrolls, or petitions for thousands of people with one click.",
            "Bind 3-4 repetitive actions (e.g., merge -> compress -> watermark) to a single button and run them in a chain (macro). Also, automatically apply legal stamps and Bates numbers to hundreds of pages."
        ]

        for i, tool in enumerate(self.all_tools):
            frame = ctk.CTkFrame(scroll, fg_color="transparent")
            frame.pack(fill="x", pady=8)
            
            badge = ctk.CTkFrame(frame, width=15, height=15, corner_radius=15, fg_color=tool["color"])
            badge.pack(side="left", padx=(10, 15), pady=5, anchor="n")
            
            text_frame = ctk.CTkFrame(frame, fg_color="transparent")
            text_frame.pack(side="left", fill="x", expand=True)
            
            tool_title = f"{tool['icon']} {get_text(tool['text'])}"
            desc = explanations_tr[i] if lang_manager.current_lang == "TR" else explanations_en[i]
            
            ctk.CTkLabel(text_frame, text=tool_title, font=ctk.CTkFont(size=15, weight="bold"), text_color=tool["color"]).pack(anchor="w")
            ctk.CTkLabel(text_frame, text=desc, font=ctk.CTkFont(size=13), justify="left", wraplength=700).pack(anchor="w", pady=(2, 0))

        ctk.CTkButton(scroll, text="Kapat / Close", fg_color="gray40", command=dialog.destroy).pack(pady=30)

    def show_welcome_screen(self):
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkToplevel):
                try: widget.destroy()
                except: pass

        self.clear_main_frame()
        self.current_active_frame_func = self.show_welcome_screen
        self.current_frame_instance = None
        
        if not hasattr(self, "welcome_frame"):
            self.welcome_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
            
            top_section = ctk.CTkFrame(self.welcome_frame, fg_color="transparent")
            top_section.pack(fill="x", pady=(10, 20))

            self.btn_guide_modal = ctk.CTkButton(top_section, text="Rehber & Gizlilik" if lang_manager.current_lang == "TR" else "App Guide & Privacy", width=160, fg_color="#1565C0", hover_color="#0D47A1", text_color="white", font=ctk.CTkFont(weight="bold"), command=self.show_app_guide_modal)
            self.btn_guide_modal.pack(side="right", anchor="n", padx=10)

            center_frame = ctk.CTkFrame(top_section, fg_color="transparent")
            center_frame.pack(expand=True)

            ctk.CTkLabel(center_frame, text="📄", font=ctk.CTkFont(size=60)).pack(pady=(0, 5))
            self.lbl_welcome_title = ctk.CTkLabel(center_frame, text=get_text("menu_title"), font=ctk.CTkFont(size=24, weight="bold"))
            self.lbl_welcome_title.pack()
            self.lbl_welcome_sub = ctk.CTkLabel(center_frame, text=get_text("welcome_subtitle"), font=ctk.CTkFont(size=14), text_color="gray")
            self.lbl_welcome_sub.pack(pady=(0, 20))
            self.lbl_qa_title = ctk.CTkLabel(center_frame, text=get_text("quick_access_title"), font=ctk.CTkFont(size=16, weight="bold"))
            self.lbl_qa_title.pack(pady=(0, 10))

            self.grid_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
            self.grid_frame.pack()
            
            self.lbl_shortcut_info = ctk.CTkLabel(center_frame, text=get_text("msg_shortcut_info"), text_color="gray", font=ctk.CTkFont(size=12, slant="italic"))
            self.lbl_shortcut_info.pack(pady=(10, 0))

            bottom_section = ctk.CTkFrame(self.welcome_frame, fg_color=("gray90", "gray15"), corner_radius=10)
            bottom_section.pack(fill="both", expand=True, padx=40, pady=(10, 10))

            self.lbl_history_title = ctk.CTkLabel(bottom_section, text=get_text("lbl_history_title"), font=ctk.CTkFont(size=15, weight="bold"))
            self.lbl_history_title.pack(anchor="w", padx=20, pady=(15, 10))

            self.history_container = ctk.CTkScrollableFrame(bottom_section, fg_color="transparent", height=300)
            self.history_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
            self.history_container.grid_columnconfigure(1, weight=1) 
            
        self.welcome_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        self.refresh_quick_access_slots()
        self.refresh_history_list()

    def refresh_quick_access_slots(self):
        for widget in self.grid_frame.winfo_children(): widget.destroy()
        self.slot_buttons = []
        for i in range(6):
            row = i // 3; col = i % 3
            slot_data = self.quick_access_slots[i]
            slot_container = ctk.CTkFrame(self.grid_frame, fg_color="transparent")
            slot_container.grid(row=row, column=col, padx=12, pady=12)
            btn_text = f"{slot_data['icon']}  {get_text(slot_data['text'])}"
            btn = ctk.CTkButton(slot_container, text=btn_text, width=210, height=55, fg_color=slot_data['color'], hover_color=slot_data['hover'], font=ctk.CTkFont(weight="bold"), command=slot_data['cmd'])
            btn.pack(side="top")
            btn.bind("<Button-3>", lambda e, idx=i: self.open_quick_access_editor(idx))
            btn.bind("<Button-2>", lambda e, idx=i: self.open_quick_access_editor(idx))
            self.slot_buttons.append(btn)

    def refresh_history_list(self):
        for widget in self.history_container.winfo_children(): widget.destroy()
        from modules.history_manager import get_history
        
        full_history = get_history()
        
        # En son eklenen elemanın gerçek konumunu bulup listeyi her koşulda EN YENİ EN ÜSTTE olacak şekilde hizalıyoruz
        # Eğer liste sonuna ekleme yapılıyorsa ters çevirir, başına yapılıyorsa düz alır
        if len(full_history) > 1 and full_history[0].get("time", "") > full_history[-1].get("time", ""):
            history_data = full_history[:10]
            is_prepended = True
        else:
            history_data = full_history[-10:]
            history_data.reverse()
            is_prepended = False

        if not history_data:
            ctk.CTkLabel(self.history_container, text=get_text("msg_empty_history"), text_color="gray", font=ctk.CTkFont(slant="italic")).grid(row=0, column=1, pady=20)
        else:
            for i, item in enumerate(history_data):
                try: desc_text = get_text(item["action"]).format(*item["params"])
                except: desc_text = "İşlem detayı okunamadı."
                
                ctk.CTkLabel(self.history_container, text=item.get("icon", "📄"), font=ctk.CTkFont(size=18)).grid(row=i, column=0, padx=(0, 10), pady=8, sticky="w")
                ctk.CTkLabel(self.history_container, text=desc_text, font=ctk.CTkFont(size=13)).grid(row=i, column=1, pady=8, sticky="w")
                ctk.CTkLabel(self.history_container, text=item.get("time", ""), text_color="gray", font=ctk.CTkFont(size=11)).grid(row=i, column=2, padx=15, pady=8, sticky="e")
                
                btn_frame = ctk.CTkFrame(self.history_container, fg_color="transparent")
                btn_frame.grid(row=i, column=3, pady=8, sticky="e")
                
                ctk.CTkButton(btn_frame, text=get_text("btn_open_file"), width=70, height=28, 
                              fg_color="transparent", border_width=1, text_color=("black", "white"), border_color=("gray60", "gray40"),
                              command=lambda p=item.get("path"): self.open_saved_file(p)).pack(side="left", padx=2)
                              
                # Silme butonunun indeksini dizilim moduna göre hatasız eşleştiriyoruz
                actual_index = i if is_prepended else (len(full_history) - 1 - i)
                ctk.CTkButton(btn_frame, text="X", width=30, height=28, fg_color="#E53935", hover_color="#B71C1C", text_color="white", command=lambda idx=actual_index: self.delete_history_entry(idx)).pack(side="left", padx=2)
    def delete_history_entry(self, index):
        from modules.history_manager import remove_history_item
        remove_history_item(index)
        self.refresh_history_list()

    def open_saved_file(self, path):
        if not path or not os.path.exists(path):
            hata_baslik = "Dosya Bulunamadı" if lang_manager.current_lang == "TR" else "File Not Found"
            hata_mesaj = "Dosya taşınmış, silinmiş veya ismi değiştirilmiş olabilir." if lang_manager.current_lang == "TR" else "The file may have been moved, deleted, or renamed."
            messagebox.showwarning(hata_baslik, hata_mesaj)
            return
        try:
            if platform.system() == "Windows": os.startfile(path)
            elif platform.system() == "Darwin": subprocess.Popen(["open", path])
            else: subprocess.Popen(["xdg-open", path])
        except Exception as e:
            messagebox.showerror("Hata / Error", str(e))

    def open_quick_access_editor(self, slot_index):
        dialog = ctk.CTkToplevel(self)
        dialog.title(get_text("edit_slot"))
        dialog.geometry("780x450")
        dialog.attributes("-topmost", True)
        dialog.resizable(False, False)
        
        dialog.update_idletasks()
        from modules.pdf_araclari import center_window
        center_window(dialog, self)
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text=get_text("lbl_slot_choose"), font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(30, 15))
        
        grid_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        grid_frame.pack(padx=20, pady=10, expand=True)
        
        for i, tool in enumerate(self.all_tools):
            r = i // 3; c = i % 3
            btn = ctk.CTkButton(grid_frame, text=f"{tool['icon']} {get_text(tool['text'])}", width=200, height=50, fg_color=tool['color'], hover_color=tool['hover'], font=ctk.CTkFont(weight="bold"), command=lambda t=tool: select_tool(t))
            btn.grid(row=r, column=c, padx=15, pady=15)
            
        def select_tool(selected_tool):
            self.quick_access_slots[slot_index] = selected_tool
            self.save_quick_access()
            dialog.destroy()
            self.refresh_quick_access_slots()

    def show_pdf_frame(self):
        self.clear_main_frame(); self.current_active_frame_func = self.show_pdf_frame
        if not hasattr(self, "pdf_frame_instance"): self.pdf_frame_instance = PDFIslemleriSayfasi(self.main_frame)
        self.current_frame_instance = self.pdf_frame_instance
        self.current_frame_instance.pack(fill="both", expand=True)

    def show_ofis_frame(self):
        self.clear_main_frame(); self.current_active_frame_func = self.show_ofis_frame
        if not hasattr(self, "ofis_frame_instance"): self.ofis_frame_instance = OfisIslemleriSayfasi(self.main_frame)
        self.current_frame_instance = self.ofis_frame_instance
        self.current_frame_instance.pack(fill="both", expand=True)

    def show_resim_frame(self):
        self.clear_main_frame(); self.current_active_frame_func = self.show_resim_frame
        if not hasattr(self, "resim_frame_instance"): self.resim_frame_instance = ResimIslemleriSayfasi(self.main_frame)
        self.current_frame_instance = self.resim_frame_instance
        self.current_frame_instance.pack(fill="both", expand=True)

    def show_pdf_araclari_frame(self):
        self.clear_main_frame(); self.current_active_frame_func = self.show_pdf_araclari_frame
        if not hasattr(self, "pdf_araclari_instance"): self.pdf_araclari_instance = PDFAraclariSayfasi(self.main_frame)
        self.current_frame_instance = self.pdf_araclari_instance
        self.current_frame_instance.pack(fill="both", expand=True)
    
    def show_kvkk_frame(self):
        self.clear_main_frame(); self.current_active_frame_func = self.show_kvkk_frame
        if not hasattr(self, "kvkk_frame_instance"): 
            from modules.pdf_guvenlik import PDFGuvenlikSayfasi
            self.kvkk_frame_instance = PDFGuvenlikSayfasi(self.main_frame)
        self.current_frame_instance = self.kvkk_frame_instance
        self.current_frame_instance.pack(fill="both", expand=True)

    def show_karsilastirma_frame(self):
        self.clear_main_frame(); self.current_active_frame_func = self.show_karsilastirma_frame
        if not hasattr(self, "karsilastirma_frame_instance"): self.karsilastirma_frame_instance = PDFKarsilastirmaSayfasi(self.main_frame)
        self.current_frame_instance = self.karsilastirma_frame_instance
        self.current_frame_instance.pack(fill="both", expand=True)

    def show_gelismis_frame(self):
        self.clear_main_frame(); self.current_active_frame_func = self.show_gelismis_frame
        if not hasattr(self, "gelismis_frame_instance"): self.gelismis_frame_instance = GelismisDuzenlemeSayfasi(self.main_frame)
        self.current_frame_instance = self.gelismis_frame_instance
        self.current_frame_instance.pack(fill="both", expand=True)

    def show_org_frame(self):
        self.clear_main_frame(); self.current_active_frame_func = self.show_org_frame
        if not hasattr(self, "org_frame_instance"): 
            from modules.pdf_organizasyon import AkilliOrganizasyonSayfasi
            self.org_frame_instance = AkilliOrganizasyonSayfasi(self.main_frame)
        self.current_frame_instance = self.org_frame_instance
        self.current_frame_instance.pack(fill="both", expand=True)

    def show_ocr_frame(self):
        self.clear_main_frame(); self.current_active_frame_func = self.show_ocr_frame
        if not hasattr(self, "ocr_frame_instance"): 
            from modules.pdf_ocr import OCRSayfasi
            self.ocr_frame_instance = OCRSayfasi(self.main_frame)
        self.current_frame_instance = self.ocr_frame_instance
        self.current_frame_instance.pack(fill="both", expand=True)

    def show_about_frame(self):
        self.clear_main_frame(); self.current_active_frame_func = self.show_about_frame
        if not hasattr(self, "about_frame_instance"): self.about_frame_instance = HakkindaSayfasi(self.main_frame)
        self.current_frame_instance = self.about_frame_instance
        self.current_frame_instance.pack(fill="both", expand=True)
    
    def show_form_frame(self):
        self.clear_main_frame(); self.current_active_frame_func = self.show_form_frame
        if not hasattr(self, "form_frame_instance"): self.form_frame_instance = FormIslemleriSayfasi(self.main_frame)
        self.current_frame_instance = self.form_frame_instance
        self.current_frame_instance.pack(fill="both", expand=True)

    def show_makro_frame(self):
        self.clear_main_frame(); self.current_active_frame_func = self.show_makro_frame
        if not hasattr(self, "makro_frame_instance"): self.makro_frame_instance = MakroVeKaseSayfasi(self.main_frame)
        self.current_frame_instance = self.makro_frame_instance
        self.current_frame_instance.pack(fill="both", expand=True)

    def show_pdf_olustur_frame(self):
        self.clear_main_frame(); self.current_active_frame_func = self.show_pdf_olustur_frame
        if not hasattr(self, "pdf_olustur_instance"): self.pdf_olustur_instance = PdfOlusturSayfasi(self.main_frame)
        self.current_frame_instance = self.pdf_olustur_instance
        self.current_frame_instance.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = BelgeDonusturucuApp()
    try:
        app.mainloop()
    except KeyboardInterrupt:
        # VS Code terminalinin gönderdiği sahte "Ctrl+C" kapatma sinyallerini yoksay
        pass