import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageOps
import fitz  
import os
import sys
import threading
from modules.language_manager import get_text, lang_manager

# --- EVRENSEL PENCERE ORTALAMA MOTORU ---
def center_window(window, parent):
    window.update_idletasks()
    pw = parent.winfo_width()
    ph = parent.winfo_height()
    px = parent.winfo_rootx()
    py = parent.winfo_rooty()
    
    if pw <= 1 or ph <= 1:
        pw = window.winfo_screenwidth()
        ph = window.winfo_screenheight()
        px, py = 0, 0
        
    ww = window.winfo_width()
    wh = window.winfo_height()
    
    x = px + (pw - ww) // 2
    y = py + (ph - wh) // 2
    window.geometry(f"+{int(x)}+{int(y)}")


# --- 1. ŞİFRE GİRİŞ PENCERESİ ---
class PasswordDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, text):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x200")
        self.attributes("-topmost", True)
        self.transient(parent)
        
        self.result = None
        
        ctk.CTkLabel(self, text=text, font=ctk.CTkFont(weight="bold")).pack(pady=(20, 10))
        self.entry = ctk.CTkEntry(self, show="*", width=250)
        self.entry.pack(pady=10)
        self.entry.bind("<Return>", lambda e: self.on_ok())
        self.entry.focus()
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Tamam" if lang_manager.current_lang=="TR" else "OK", width=100, command=self.on_ok).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="İptal" if lang_manager.current_lang=="TR" else "Cancel", width=100, fg_color="gray", command=self.destroy).pack(side="left", padx=10)
        
        center_window(self, parent)
        self.grab_set()
        self.wait_window(self)

    def on_ok(self):
        self.result = self.entry.get()
        self.destroy()

    def get_result(self):
        return self.result


# --- 2. YÜKLENİYOR (İŞLEM YAPILIYOR) PENCERESİ ---
# --- YÜKLENİYOR (İŞLEM YAPILIYOR) PENCERESİ ---
class ProgressWindow(ctk.CTkToplevel):
    def __init__(self, parent, message=""):
        if not message: message = get_text("progress_processing")
        super().__init__(parent)
        self.title(get_text("progress_wait"))
        self.geometry("350x150")
        self.transient(parent) # Chrome üstüne zorla çıkmaz
        center_window(self, parent)
        self.protocol("WM_DELETE_WINDOW", self.disable_close)
        
        self.lbl_msg = ctk.CTkLabel(self, text=message, font=ctk.CTkFont(weight="bold", size=13))
        self.lbl_msg.pack(pady=(30, 15))
        
        # ÇÖZÜM: Sonsuz döngü bug'ını önlemek için modu determinate yapıyoruz ve start() demiyoruz!
        self.progressbar = ctk.CTkProgressBar(self, width=250, mode="determinate")
        self.progressbar.pack()
        self.progressbar.set(0.0)
        
        center_window(self, parent)
        self.grab_set()

    def disable_close(self):
        pass


# --- 3. BAŞARI / SONUÇ PENCERESİ (DOĞRUDAN DOSYA AÇMA DESTEKLİ) ---
class ActionDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, message, folder_path=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("450x200")
    
        self.transient(parent)
        self.folder_path = folder_path

        ctk.CTkLabel(self, text=message, font=ctk.CTkFont(weight="bold", size=14), wraplength=400).pack(pady=(30, 20))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text=get_text("dialog_ok"), width=120, command=self.destroy).pack(side="left", padx=10)
        
        if self.folder_path:
            ctk.CTkButton(btn_frame, text=get_text("btn_open_file"), width=120, fg_color="#1976D2", hover_color="#1565C0", 
                          command=self.open_file_direct).pack(side="left", padx=10)

        center_window(self, parent)
        self.grab_set()

    def open_file_direct(self):
        import platform
        import subprocess
        
        path = self.folder_path
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        self.destroy()


class PDFAraclariSayfasi(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.data_list = []
        self.cards_list = []
        self.show_pass = False
        
        self.tab_main_name = get_text("tab_pdf_tools_main")
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        self.tab_main = self.tabview.add(self.tab_main_name)
        
        self.setup_ui()
        self.update_language()

    def setup_ui(self):
        self.tab_main.grid_columnconfigure(0, weight=1)
        self.tab_main.grid_columnconfigure(1, weight=0, minsize=350)
        self.tab_main.grid_rowconfigure(0, weight=1)

        left_frame = ctk.CTkFrame(self.tab_main, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        top_bar = ctk.CTkFrame(left_frame, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 10))

        self.btn_add_file = ctk.CTkButton(top_bar, text=get_text("btn_add_file"), font=ctk.CTkFont(weight="bold"), command=self.add_pdfs, fg_color="#2E7D32", hover_color="#1B5E20")
        self.btn_add_file.pack(side="left", padx=5)
        self.btn_del_selected = ctk.CTkButton(top_bar, text=get_text("btn_del_selected"), width=100, fg_color="#E53935", hover_color="#C62828", command=self.batch_delete)
        self.btn_del_selected.pack(side="left", padx=5)
        self.btn_clear = ctk.CTkButton(top_bar, text=get_text("btn_clear"), width=80, command=self.clear_all, fg_color="transparent", border_width=1, border_color=("gray60", "gray40"), text_color=("black", "white"), hover_color=("gray85", "gray25"))
        self.btn_clear.pack(side="right")

        self.scroll_frame = ctk.CTkScrollableFrame(left_frame)
        self.scroll_frame.pack(fill="both", expand=True)

        right_frame = ctk.CTkFrame(self.tab_main, width=350)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        right_frame.pack_propagate(False)

        # Üst Ayarlar Bölümü
        top_settings = ctk.CTkFrame(right_frame, fg_color="transparent")
        top_settings.pack(side="top", fill="both", expand=True)

        self.lbl_action_select = ctk.CTkLabel(top_settings, text=get_text("lbl_action_select"), font=ctk.CTkFont(size=18, weight="bold"))
        self.lbl_action_select.pack(pady=(15, 5))
        
        self.var_tool_type = ctk.StringVar(value=get_text("opt_compress"))
        opts_tool = [get_text("opt_compress"), get_text("opt_encrypt"), get_text("opt_compress_encrypt"), get_text("opt_unlock")]
        
        self.tool_menu = ctk.CTkOptionMenu(top_settings, values=opts_tool, variable=self.var_tool_type, command=self.toggle_tool_ui)
        self.tool_menu.pack(fill="x", padx=20, pady=10)

        # Sıkıştırma Ayar Paneli
        self.frame_compress = ctk.CTkFrame(top_settings, fg_color="transparent")
        
        self.lbl_comp_method = ctk.CTkLabel(self.frame_compress, text="Sıkıştırma Yöntemi", anchor="w", font=ctk.CTkFont(weight="bold"))
        self.lbl_comp_method.pack(fill="x", pady=(5,0))
        self.var_comp_method = ctk.StringVar(value="Kayıpsız (Standart)")
        self.opt_method = ctk.CTkOptionMenu(self.frame_compress, values=["Kayıpsız (Standart)", "DPI Düşürme (Yüksek Sıkıştırma)"], variable=self.var_comp_method, command=self.on_method_change)
        self.opt_method.pack(fill="x", pady=5)

        self.lbl_comp_level = ctk.CTkLabel(self.frame_compress, text=get_text("lbl_compress_power"), anchor="w", font=ctk.CTkFont(weight="bold"))
        self.lbl_comp_level.pack(fill="x", pady=(5,0))
        self.var_comp_level = ctk.StringVar(value=get_text("opt_standard"))
        opts_comp = [get_text("opt_light"), get_text("opt_standard"), get_text("opt_maximum")]
        self.opt_comp_level = ctk.CTkOptionMenu(self.frame_compress, values=opts_comp, variable=self.var_comp_level)
        self.opt_comp_level.pack(fill="x", pady=5)

        # Şifreleme Ayar Paneli
        self.frame_encrypt = ctk.CTkFrame(top_settings, fg_color="transparent")
        self.lbl_pwd_ops = ctk.CTkLabel(self.frame_encrypt, text=get_text("lbl_pwd_ops"), anchor="w", font=ctk.CTkFont(weight="bold"))
        self.lbl_pwd_ops.pack(fill="x")
        
        pass_entry_frame = ctk.CTkFrame(self.frame_encrypt, fg_color="transparent")
        pass_entry_frame.pack(fill="x")
        self.entry_pass1 = ctk.CTkEntry(pass_entry_frame, show="*", placeholder_text=get_text("ph_password"))
        self.entry_pass1.pack(side="left", fill="x", expand=True, pady=2)
        self.btn_show_pass = ctk.CTkButton(pass_entry_frame, text="👁", width=30, fg_color="gray30", command=self.toggle_pass_visibility)
        self.btn_show_pass.pack(side="right", padx=(5, 0))

        self.lbl_pass2 = ctk.CTkLabel(self.frame_encrypt, text=get_text("lbl_pwd_again"), anchor="w")
        self.lbl_pass2.pack(fill="x", pady=(5,0))
        self.entry_pass2 = ctk.CTkEntry(self.frame_encrypt, show="*", placeholder_text=get_text("ph_pwd_again"))
        self.entry_pass2.pack(fill="x", pady=2)

        # Gelişmiş Güvenlik ve İzin Yönetimi Paneli (Her Zaman Görünür)
        self.frame_advanced = ctk.CTkFrame(top_settings, fg_color="transparent")
        self.frame_advanced.pack(fill="x", padx=20, pady=10)
        
        self.lbl_adv_sec = ctk.CTkLabel(self.frame_advanced, text="Ek Güvenlik & İzin Yönetimi", anchor="w", font=ctk.CTkFont(weight="bold"))
        self.lbl_adv_sec.pack(fill="x", pady=(5, 5))
        
        self.chk_flatten = ctk.CTkCheckBox(self.frame_advanced, text="Belgeyi Düzleştir (Katmanları Resme Çevir)", font=ctk.CTkFont(size=12))
        self.chk_flatten.pack(fill="x", pady=4)
        
        self.chk_no_copy = ctk.CTkCheckBox(self.frame_advanced, text="Metin Kopyalamayı Engelle", font=ctk.CTkFont(size=12))
        self.chk_no_copy.pack(fill="x", pady=4)
        
        self.chk_no_modify = ctk.CTkCheckBox(self.frame_advanced, text="Değişiklik Yapılmasını Engelle", font=ctk.CTkFont(size=12))
        self.chk_no_modify.pack(fill="x", pady=4)

        # Alt Uyarı ve Buton Bölümü
        bottom_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        bottom_frame.pack(side="bottom", fill="x", pady=10)

        self.warning_box = ctk.CTkFrame(bottom_frame, fg_color=("#FFF3E0", "#332B1A"), corner_radius=10, border_width=1, border_color="#FFA726")
        self.warning_box.pack(fill="x", padx=10, pady=10)
        self.warn_lbl = ctk.CTkLabel(self.warning_box, text="", text_color=("#E65100", "#FFB74D"), font=ctk.CTkFont(size=11), justify="left", wraplength=310)
        self.warn_lbl.pack(padx=10, pady=10)

        self.toggle_tool_ui(self.var_tool_type.get())
        
        self.btn_start_process = ctk.CTkButton(bottom_frame, text=get_text("btn_start_process"), font=ctk.CTkFont(size=16, weight="bold"), height=50, 
                      fg_color="#2E7D32", hover_color="#1B5E20", command=self.start_process)
        self.btn_start_process.pack(fill="x", padx=20, pady=10)

    # --- TAM DİL ENTEGRASYONU ---
    def update_language(self):
        is_en = (lang_manager.current_lang == "EN")
        try:
            self.tabview._segmented_button._buttons_dict[self.tab_main_name].configure(text=get_text("tab_pdf_tools_main"))
        except: pass

        if hasattr(self, 'btn_add_file'): self.btn_add_file.configure(text=get_text("btn_add_file"))
        if hasattr(self, 'btn_del_selected'): self.btn_del_selected.configure(text=get_text("btn_del_selected"))
        if hasattr(self, 'btn_clear'): self.btn_clear.configure(text=get_text("btn_clear"))
        if hasattr(self, 'lbl_action_select'): self.lbl_action_select.configure(text=get_text("lbl_action_select"))
        if hasattr(self, 'btn_start_process'): self.btn_start_process.configure(text=get_text("btn_start_process"))

        # --- SEÇİMLERİN KAYBOLMASINI ENGELLEYEN AKILLI EŞLEŞTİRMELER ---
        if hasattr(self, 'tool_menu'):
            old_vals_tr = ["Sıkıştır", "Şifrele", "Sıkıştır & Şifrele", "Şifre Kaldır"]
            old_vals_en = ["Compress", "Encrypt", "Compress & Encrypt", "Unlock"]
            curr_tool = self.var_tool_type.get()
            idx = 0
            if curr_tool in old_vals_tr: idx = old_vals_tr.index(curr_tool)
            elif curr_tool in old_vals_en: idx = old_vals_en.index(curr_tool)
            opts_tool = [get_text("opt_compress"), get_text("opt_encrypt"), get_text("opt_compress_encrypt"), get_text("opt_unlock")]
            self.tool_menu.configure(values=opts_tool)
            self.var_tool_type.set(opts_tool[idx])

        if hasattr(self, 'lbl_comp_method'):
            self.lbl_comp_method.configure(text="Compression Method" if is_en else "Sıkıştırma Yöntemi")
            
        if hasattr(self, 'opt_method'):
            m_vals_tr = ["Kayıpsız (Standart)", "DPI Düşürme (Yüksek Sıkıştırma)"]
            m_vals_en = ["Lossless (Standard)", "DPI Reduction (High Compression)"]
            m_vals = m_vals_en if is_en else m_vals_tr
            curr_m = self.var_comp_method.get()
            m_idx = 0
            if curr_m in m_vals_tr: m_idx = m_vals_tr.index(curr_m)
            elif curr_m in m_vals_en: m_idx = m_vals_en.index(curr_m)
            self.opt_method.configure(values=m_vals)
            self.var_comp_method.set(m_vals[m_idx])

        if hasattr(self, 'lbl_comp_level'): self.lbl_comp_level.configure(text=get_text("lbl_compress_power"))
        
        if hasattr(self, 'opt_comp_level'):
            tr_levels = ["Hafif", "Standart", "Maksimum"]
            en_levels = ["Light", "Standard", "Maximum"]
            curr_l = self.var_comp_level.get()
            l_idx = 1
            if curr_l in tr_levels: l_idx = tr_levels.index(curr_l)
            elif curr_l in en_levels: l_idx = en_levels.index(curr_l)
            opts_comp = [get_text("opt_light"), get_text("opt_standard"), get_text("opt_maximum")]
            self.opt_comp_level.configure(values=opts_comp)
            self.var_comp_level.set(opts_comp[l_idx])
            
        if hasattr(self, 'lbl_pwd_ops'): self.lbl_pwd_ops.configure(text=get_text("lbl_pwd_ops"))
        if hasattr(self, 'lbl_pass2'): self.lbl_pass2.configure(text=get_text("lbl_pwd_again"))
        
        if hasattr(self, 'entry_pass1'):
            if self.var_tool_type.get() == get_text("opt_unlock"):
                self.entry_pass1.configure(placeholder_text=get_text("ph_pwd_current"))
            else:
                self.entry_pass1.configure(placeholder_text=get_text("ph_password"))
        if hasattr(self, 'entry_pass2'): self.entry_pass2.configure(placeholder_text=get_text("ph_pwd_again"))
        
        if hasattr(self, 'lbl_adv_sec'):
            self.lbl_adv_sec.configure(text="Extra Security & Permissions" if is_en else "Ek Güvenlik & İzin Yönetimi")
        if hasattr(self, 'chk_flatten'):
            self.chk_flatten.configure(text="Flatten Document (Layers to Image)" if is_en else "Belgeyi Düzleştir (Katmanları Resme Çevir)")
        if hasattr(self, 'chk_no_copy'):
            self.chk_no_copy.configure(text="Prevent Text Copying" if is_en else "Metin Kopyalamayı Engelle")
        if hasattr(self, 'chk_no_modify'):
            self.chk_no_modify.configure(text="Prevent Modifications" if is_en else "Değişiklik Yapılmasını Engelle")

        # Birleşik akıllı uyarı kutusunu anlık günceller
        self.toggle_tool_ui(self.var_tool_type.get())
        
        for data in self.data_list:
            if 'w_chk' in data and data['w_chk'].winfo_exists():
                data['w_chk'].configure(text=get_text("chk_select"))

    def on_method_change(self, val):
        self.toggle_tool_ui(self.var_tool_type.get())

    def toggle_tool_ui(self, value):
        self.frame_compress.pack_forget()
        self.frame_encrypt.pack_forget()
        self.lbl_pass2.pack_forget()
        self.entry_pass2.pack_forget()
        
        is_en = (lang_manager.current_lang == "EN")
        is_compress = (value == get_text("opt_compress") or value == get_text("opt_compress_encrypt"))
        is_encrypt = (value == get_text("opt_encrypt") or value == get_text("opt_compress_encrypt"))
        is_unlock = (value == get_text("opt_unlock"))

        # Dinamik olarak tüm yönergeleri ve ek güvenlik notlarını tek kutuda toplar
        lines = []

        if is_compress: 
            self.frame_compress.pack(fill="x", padx=20, pady=5)
            curr_method = self.var_comp_method.get()
            if "DPI" in curr_method or "High" in curr_method or "Yüksek" in curr_method:
                lines.append("⚠️ HIGH COMPRESSION (DPI):\nSignificantly reduces file size by lowering image resolution. Ideal for Email/WhatsApp." if is_en else "⚠️ YÜKSEK SIKIŞTIRMA (DPI):\nBelgedeki görsellerin çözünürlüğünü düşürür. E-Posta ve WhatsApp için devasa boyut tasarrufu sağlar.")
            else:
                lines.append("⚠️ LOSSLESS COMPRESSION:\nClears garbage data and unused fonts. Quality remains 100%, but size reduction is limited." if is_en else "⚠️ KAYIPSIZ SIKIŞTIRMA:\nÇöp verileri ve görünmeyen fontları siler. Kalite bozulmaz ancak boyut düşüşü sınırlıdır.")
        
        if is_encrypt: 
            self.frame_encrypt.pack(fill="x", padx=20, pady=5)
            self.lbl_pass2.pack(fill="x", pady=(5,0))
            self.entry_pass2.pack(fill="x", pady=2)
            self.entry_pass1.configure(placeholder_text=get_text("ph_password"))
            lines.append("🔒 ENCRYPTION:\nSecures the document with AES-256 military-grade encryption." if is_en else "🔒 ŞİFRELEME:\nBelgeyi AES-256 askeri düzeyde şifreleme ile koruma altına alır.")

        if is_unlock:
            self.frame_encrypt.pack(fill="x", padx=20, pady=5)
            self.entry_pass1.configure(placeholder_text=get_text("ph_pwd_current"))
            lines.append("🔓 UNLOCK:\nRemoves security passwords and restriction profiles from the file." if is_en else "🔓 ŞİFRE KALDIRMA:\nDosyadaki güvenlik şifrelerini ve kısıtlama profillerini temizler.")

        # Ek güvenlik ipuçları tasarım birliği için her zaman en alta eklenir
        lines.append("💡 FLATTEN:\nConverts all layers to an image, preventing any modification or tampering." if is_en else "💡 DÜZLEŞTİRME:\nPDF'teki her şeyi tek bir fotoğrafa çevirir, üzerinde oynamayı imkansız kılar.")
        lines.append("💡 PERMISSIONS:\nLocks content copying and modification in the background, even without a password." if is_en else "💡 İZİN KİLİDİ:\nŞifre koymasanız dahi belgeden yazı kopyalanmasını ve düzenlenmesini engeller.")

        # Tüm yönergeleri şık boşluklarla tek kutuya basar
        self.warn_lbl.configure(text="\n\n".join(lines))

    def toggle_pass_visibility(self):
        self.show_pass = not self.show_pass
        char = "" if self.show_pass else "*"
        self.entry_pass1.configure(show=char)
        self.entry_pass2.configure(show=char)
        self.btn_show_pass.configure(text="🔒" if self.show_pass else "👁")

    def add_dropped_files(self, files):
        pdf_files = [f for f in files if f.lower().endswith('.pdf')]
        if pdf_files:
            self.progress = ProgressWindow(self.winfo_toplevel(), get_text("msg_analyzing"))
            self.after(200, lambda: threading.Thread(target=self._thread_add_pdfs, args=(pdf_files,), daemon=True).start())

    def add_pdfs(self):
        files = filedialog.askopenfilenames(title=get_text("fd_select_pdf"), filetypes=[("PDF", "*.pdf")])
        if not files: return
        self.progress = ProgressWindow(self.winfo_toplevel(), get_text("msg_analyzing"))
        threading.Thread(target=self._thread_add_pdfs, args=(files,), daemon=True).start()

    def _thread_add_pdfs(self, files):
        try:
            new_data = []
            for f in files:
                doc = fitz.open(f)
                file_password = ""
                
                if doc.is_encrypted:
                    self.after(0, lambda: self.progress.withdraw())
                    dialog = PasswordDialog(self.winfo_toplevel(), get_text("msg_pwd_file"), 
                                          get_text("msg_pwd_prompt_2").format(os.path.basename(f)))
                    user_pass = dialog.get_result()
                    self.after(0, lambda: self.progress.deiconify())
                    
                    if user_pass:
                        if doc.authenticate(user_pass):
                            file_password = user_pass
                        else:
                            # Lambda Kapatması (Closure) Onarıldı
                            self.after(0, lambda bn=os.path.basename(f): messagebox.showerror(get_text("dialog_error"), get_text("msg_pwd_wrong").format(bn)))
                            doc.close(); continue
                    else:
                        doc.close(); continue
                
                size_mb = os.path.getsize(f) / (1024 * 1024)
                page = doc.load_page(0)
                pix = page.get_pixmap(dpi=60)
                pil_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                doc.close()
                
                new_data.append({
                    'path': f, 
                    'selected': False, 
                    'thumb': ImageOps.expand(pil_img, border=1, fill="#b0b0b0"), 
                    'name': f"{os.path.basename(f)[:15]}... ({size_mb:.1f} MB)",
                    'current_password': file_password
                })
            
            self.data_list.extend(new_data)
            self.after(0, self.rebuild_cards)
        except Exception as e: 
            err_msg = f"{get_text('dialog_error')}: {str(e)}"
            self.after(0, lambda m=err_msg: self.on_error(m))

    def rebuild_cards(self):
        if hasattr(self, 'progress') and self.progress.winfo_exists(): self.progress.destroy()
        for w in self.scroll_frame.winfo_children(): w.destroy()
        self.cards_list.clear()
        for i in range(3): self.scroll_frame.grid_columnconfigure(i, weight=1)
        for data in self.data_list:
            card = ctk.CTkFrame(self.scroll_frame, corner_radius=10, fg_color=("gray85", "gray25"))
            ctk_img = ctk.CTkImage(light_image=data['thumb'], size=(260, 360))
            ctk.CTkLabel(card, image=ctk_img, text="").pack(pady=(5, 0), padx=5)
            ctk.CTkLabel(card, text=data['name'], font=ctk.CTkFont(size=12, weight="bold")).pack()
            
            if data.get('current_password'):
                ctk.CTkLabel(card, text=get_text("lbl_pwd_solved"), text_color="green", font=ctk.CTkFont(size=10)).pack()

            controls = ctk.CTkFrame(card, fg_color="transparent")
            controls.pack(pady=(4, 8))
            
            chk_var = ctk.BooleanVar(value=data.get('selected', False))
            chk = ctk.CTkCheckBox(controls, text=get_text("chk_select"), variable=chk_var, width=50, command=lambda d=data, c=chk_var: self.toggle_selection(d, c))
            chk.pack(side="left", padx=(0, 10))
            
            data['w_chk'] = chk
            ctk.CTkButton(controls, text="X", width=30, height=25, fg_color="#E53935", command=lambda c=card: self.delete_single_card(c)).pack(side="left")
            self.cards_list.append(card)
        self.refresh_grid()

    def refresh_grid(self):
        for idx, card in enumerate(self.cards_list): card.grid(row=idx//3, column=idx%3, padx=2, pady=5, sticky="n")

    def toggle_selection(self, data, checkbox):
        data['selected'] = checkbox.get()
        
    def delete_single_card(self, card):
        idx = self.cards_list.index(card)
        self.cards_list.pop(idx); self.data_list.pop(idx); card.destroy(); self.refresh_grid()
        
    def batch_delete(self):
        self.data_list = [d for d in self.data_list if not d['selected']]; self.rebuild_cards()
        
    def clear_all(self): 
        self.data_list.clear(); self.rebuild_cards()

    def start_process(self):
        if not self.data_list: messagebox.showwarning(get_text("dialog_warning"), get_text("msg_warn_no_file")); return
        
        mode = self.var_tool_type.get()
        p1, p2 = self.entry_pass1.get(), self.entry_pass2.get()
        
        is_encrypt = (mode == get_text("opt_encrypt") or mode == get_text("opt_compress_encrypt"))
        if is_encrypt:
            if not p1: messagebox.showwarning(get_text("dialog_error"), get_text("msg_err_no_pwd")); return
            if p1 != p2: messagebox.showwarning(get_text("dialog_error"), get_text("msg_err_pwd_mismatch")); return

        save_path = filedialog.asksaveasfilename(title=get_text("fd_save_new_pdf"), defaultextension=".pdf", 
                                                filetypes=[("PDF", "*.pdf")], initialfile="islenmis_belge.pdf")
        if not save_path: return

        self.progress = ProgressWindow(self.winfo_toplevel(), get_text("progress_processing"))
        threading.Thread(target=self._thread_process, args=(save_path, mode, p1), daemon=True).start()

    # ====================================================
    # --- YÜKSEK PERFORMANSLI GELİŞMİŞ İŞLEME MOTORU ---
    # ====================================================
    def _thread_process(self, save_path, mode, password):
        try:
            final_pdf = fitz.open()
            
            is_compress = (mode == get_text("opt_compress") or mode == get_text("opt_compress_encrypt"))
            is_encrypt = (mode == get_text("opt_encrypt") or mode == get_text("opt_compress_encrypt"))
            is_dpi_compression = is_compress and ("DPI" in self.var_comp_method.get() or "Yüksek" in self.var_comp_method.get() or "High" in self.var_comp_method.get())
            is_flatten = self.chk_flatten.get()

            # --- SIKIŞTIRMA, DÜZLEŞTİRME VE RE-SAMPLING ADIMI ---
            for data in self.data_list:
                # Her PDF dosyası ele alınırken yüklenme kutusunu yenile
                if hasattr(self, 'progress') and self.progress.winfo_exists():
                    self.progress.update()

                doc = fitz.open(data['path'])
                if doc.is_encrypted:
                    doc.authenticate(data['current_password'])
                
                # Eğer DPI düşürmeli sıkıştırma veya Düzleştirme (Flatten) modu aktifse sayfaları yeniden üret
                if is_dpi_compression or is_flatten:
                    target_dpi = 120
                    if is_dpi_compression:
                        level = self.var_comp_level.get()
                        if level in [get_text("opt_light"), "Hafif", "Light"]: target_dpi = 150
                        elif level in [get_text("opt_standard"), "Standart", "Standard"]: target_dpi = 120
                        else: target_dpi = 90 # Maksimum sıkıştırma gücü

                    for page in doc:
                        # Ağır sayfa dönüşümlerinde yüklenme kutusunun donmasını engelle
                        if hasattr(self, 'progress') and self.progress.winfo_exists():
                            self.progress.update()

                        # Sayfayı resme dönüştür
                        pix = page.get_pixmap(dpi=target_dpi, colorspace=fitz.csRGB)
                        
                        # ÇÖZÜM: Yeni PyMuPDF sürümlerinde 'quality' parametresi kaldırıldığı için tıkama/sıkıştırma
                        # işlemini doğrudan pil_save_kwargs veya format yapısı üzerinden bytes dizisine çıkartıyoruz.
                        import io
                        from PIL import Image
                        
                        pil_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        img_byte_arr = io.BytesIO()
                        
                        # Kaliteyi is_dpi ise 80'e, değilse 95'e çekerek PIL üzerinden güvenle sıkıştırıyoruz
                        pil_img.save(img_byte_arr, format='JPEG', quality=80 if is_dpi_compression else 95)
                        img_data = img_byte_arr.getvalue()
                        
                        new_page = final_pdf.new_page(width=page.rect.width, height=page.rect.height)
                        new_page.insert_image(new_page.rect, stream=img_data)
                else:
                    # Kayıpsız standart kopyalama modu
                    final_pdf.insert_pdf(doc)
                doc.close()

            # --- KAYDETME VE İZİN MASKELEME AYARLARI ---
            save_args = {"garbage": 3, "deflate": True}
            
            # Kayıpsız standart sıkıştırma parametreleri
            if is_compress and not is_dpi_compression:
                level = self.var_comp_level.get()
                if level in [get_text("opt_maximum"), "Maksimum", "Maximum"]: 
                    save_args["garbage"] = 4
                    save_args["clean"] = True

            # İzin Yönetimi (Kopyalama ve Düzenleme Engeli)
            if self.chk_no_copy.get() or self.chk_no_modify.get():
                perm_mask = 0
                perm_mask |= fitz.PDF_PERM_PRINT        # Yazdırmaya her koşulda izin ver
                perm_mask |= fitz.PDF_PERM_ACCESSIBILITY # Ekran okuyuculara izin ver
                
                if not self.chk_no_copy.get():
                    perm_mask |= fitz.PDF_PERM_COPY     # Tik seçili değilse kopyalamayı serbest bırak
                if not self.chk_no_modify.get():
                    perm_mask |= fitz.PDF_PERM_MODIFY   # Tik seçili değilse düzenlemeyi serbest bırak
                    perm_mask |= fitz.PDF_PERM_ANNOTATE

                save_args["permissions"] = perm_mask
                save_args["encryption"] = fitz.PDF_ENCRYPT_AES_256
                
                # Eğer kullanıcı kendisi bir şifre belirlemediyse, arka planda gizli sahip anahtarı ata (Docsas Güvenli Kalıbı)
                # Böylece belge açılırken şifre sormaz ama kopyalama/düzenleme kısıtlamaları aktif kalır!
                owner_pwd = password if (is_encrypt and password) else "DocsasSecureOwnerPerms123!"
                user_pwd = password if is_encrypt else ""
                
                save_args["user_pw"] = user_pwd
                save_args["owner_pw"] = owner_pwd
            else:
                # Standart Kullanıcı Şifrelemesi
                if is_encrypt:
                    save_args["encryption"] = fitz.PDF_ENCRYPT_AES_256
                    save_args["user_pw"] = password
                    save_args["owner_pw"] = password

            # --- UYAP UYUMLULUK VE GÜVENLİK ENTEGRASYONU ---
            # 1. Eğer DPI sıkıştırması veya düzleştirme (flatten) kullanılmadıysa (Lossless kopya moduysa), 
            # UYAP'ın imza kuralı için mevcut etkileşimli alanları/katmanları sabitleyip düzleştiriyoruz.
            if not is_dpi_compression and not is_flatten:
                try:
                    for page in final_pdf:
                        page.flatten_widgets()
                except: pass

            # 2. Yerel bilgisayar adını ve dosya yollarını (Geçersiz Yol Hatasını) temizlemek için meta veriyi uçuruyoruz.
            final_pdf.set_metadata({})
            try: final_pdf.set_xml_metadata("")
            except: pass

            # 3. Çöp nesne ayıklama düzeyini (XREF temizliği için) en üst seviye olan 4'e çekiyoruz.
            save_args["garbage"] = 4
            save_args["clean"] = True

            final_pdf.save(save_path, **save_args)
            final_pdf.close()
            
            from modules.history_manager import add_history
            add_history("🛠️", "history_action_generic", ["Çoklu PDF İşlemi", os.path.basename(save_path)], save_path)
            
            # Lambda Kapatması Onarıldı
            self.after(0, lambda p=save_path: self.on_success(p))
            
        except Exception as e: 
            err_msg = str(e)
            self.after(0, lambda m=err_msg: self.on_error(m))

    def on_success(self, path):
        if hasattr(self, 'progress') and self.progress.winfo_exists(): self.progress.destroy()
        msg_text = get_text("msg_process_success")
        ActionDialog(self.winfo_toplevel(), get_text("dialog_success"), msg_text, path)
        self.clear_all()

    def on_error(self, err):
        if hasattr(self, 'progress') and self.progress.winfo_exists(): self.progress.destroy()
        messagebox.showerror(get_text("dialog_error"), err)