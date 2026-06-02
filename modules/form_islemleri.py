import customtkinter as ctk
from tkinter import filedialog, messagebox, Canvas
from PIL import Image, ImageOps
import fitz  
import os
import sys
import openpyxl
import threading
import datetime
from modules.pdf_araclari import ProgressWindow, ActionDialog
from modules.language_manager import get_text

class FormIslemleriSayfasi(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        
        self.template_pdf_path = None
        self.excel_data_path = None
        
        self.zoom_factor = 1.0
        self.base_high_res_image = None
        
        # Otomasyon ve Sayfalama Hafızası
        self.excel_records = []
        self.total_records = 0
        self.current_record_index = 0
        self.current_page_index = 0
        self.total_pages = 0
        
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1, minsize=420)
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # --- SOL TARAF: CANLI ÖNİZLEME ALANI ---
        # ==========================================
        self.left_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        top_bar = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(top_bar, text=get_text("lbl_preview_form"), font=ctk.CTkFont(weight="bold", size=15), text_color="#1565C0").pack(side="left", padx=5)
        
        self.btn_clear = ctk.CTkButton(top_bar, text=get_text("btn_clear"), width=80, fg_color="transparent", border_width=1, border_color=("gray60", "gray40"), text_color=("black", "white"), text_color_disabled=("gray50", "gray60"), hover_color=("gray85", "gray25"), command=self.clear_all)
        self.btn_clear.pack(side="left", padx=(15, 5))
        
        self.btn_zoom_in = ctk.CTkButton(top_bar, text=get_text("btn_zoom_in_text"), width=100, fg_color=("gray75", "gray30"), hover_color=("gray65", "gray20"), text_color=("black", "white"), text_color_disabled=("gray50", "gray60"), command=lambda: self.change_zoom(0.2))
        self.btn_zoom_in.pack(side="right", padx=2)
        self.btn_fit = ctk.CTkButton(top_bar, text=get_text("btn_fit"), width=100, fg_color=("gray75", "gray30"), hover_color=("gray65", "gray20"), text_color=("black", "white"), text_color_disabled=("gray50", "gray60"), command=lambda: self.change_zoom("fit"))
        self.btn_fit.pack(side="right", padx=2)
        self.btn_zoom_out = ctk.CTkButton(top_bar, text=get_text("btn_zoom_out_text"), width=100, fg_color=("gray75", "gray30"), hover_color=("gray65", "gray20"), text_color=("black", "white"), text_color_disabled=("gray50", "gray60"), command=lambda: self.change_zoom(-0.2))
        self.btn_zoom_out.pack(side="right", padx=2)

        self.preview_container = ctk.CTkFrame(self.left_frame, fg_color=("gray90", "gray15"))
        self.preview_container.pack(fill="both", expand=True)

        self.canvas = Canvas(self.preview_container, bg="#2B2B2B", highlightthickness=0)
        self.v_scrollbar = ctk.CTkScrollbar(self.preview_container, orientation="vertical", command=self.canvas.yview)
        self.h_scrollbar = ctk.CTkScrollbar(self.preview_container, orientation="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        self.v_scrollbar.pack(side="right", fill="y")
        self.h_scrollbar.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.create_preview_label()
        self.canvas.bind("<Configure>", self.center_canvas_content)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)

        self.nav_bar_pdf = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.btn_prev_page = ctk.CTkButton(self.nav_bar_pdf, text="<", width=50, fg_color="gray40", command=self.prev_pdf_page)
        self.btn_prev_page.pack(side="left", padx=10)
        self.lbl_pdf_page_info = ctk.CTkLabel(self.nav_bar_pdf, text="", font=ctk.CTkFont(weight="bold", size=13))
        self.lbl_pdf_page_info.pack(side="left", expand=True)
        self.btn_next_page = ctk.CTkButton(self.nav_bar_pdf, text=">", width=50, fg_color="gray40", command=self.next_pdf_page)
        self.btn_next_page.pack(side="right", padx=10)
        self.nav_bar_pdf.pack_forget()

        self.btn_zoom_in.configure(state="disabled")
        self.btn_zoom_out.configure(state="disabled")
        self.btn_fit.configure(state="disabled")
        self.btn_clear.configure(state="disabled")

        # ==========================================
        # --- SAĞ TARAF: KONTROL PANELİ VE REHBER ---
        # ==========================================
        self.right_frame = ctk.CTkScrollableFrame(self, width=420)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        guide_box = ctk.CTkFrame(self.right_frame, fg_color=("gray88", "gray18"), corner_radius=10, border_color=("gray75", "gray28"), border_width=1)
        guide_box.pack(fill="x", padx=10, pady=(0, 15))
        
        ctk.CTkLabel(guide_box, text=get_text("lbl_guide_title"), font=ctk.CTkFont(size=14, weight="bold"), text_color="#1565C0").pack(anchor="w", padx=15, pady=(10, 5))
        ctk.CTkLabel(guide_box, text=get_text("msg_guide_text"), font=ctk.CTkFont(size=11), justify="left", wraplength=370, text_color=("gray30", "gray70")).pack(padx=15, pady=(0, 15))

        pdf_box = ctk.CTkFrame(self.right_frame, fg_color=("gray85", "gray20"), corner_radius=10, border_width=1, border_color=("gray70", "gray30"))
        pdf_box.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(pdf_box, text=get_text("lbl_template_pdf"), font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))
        self.lbl_pdf_name = ctk.CTkLabel(pdf_box, text=get_text("msg_waiting_file"), text_color="gray")
        self.lbl_pdf_name.pack(pady=2)
        self.btn_select_pdf = ctk.CTkButton(pdf_box, text=get_text("btn_select_file"), fg_color="#D32F2F", hover_color="#B71C1C", command=self.select_pdf)
        self.btn_select_pdf.pack(pady=(5, 15))

        excel_box = ctk.CTkFrame(self.right_frame, fg_color=("gray85", "gray20"), corner_radius=10, border_width=1, border_color=("gray70", "gray30"))
        excel_box.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(excel_box, text=get_text("lbl_excel_data"), font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))
        
        self.lbl_excel_name = ctk.CTkLabel(excel_box, text=get_text("msg_waiting_excel"), text_color="gray")
        self.lbl_excel_name.pack(pady=2)
        self.btn_select_excel = ctk.CTkButton(excel_box, text=get_text("btn_select_file"), fg_color="#2E7D32", hover_color="#1B5E20", command=self.select_excel)
        self.btn_select_excel.pack(pady=(5, 10))
        
        self.nav_bar_excel = ctk.CTkFrame(excel_box, fg_color="transparent")
        self.btn_prev_ex = ctk.CTkButton(self.nav_bar_excel, text="<", width=40, command=self.prev_record)
        self.btn_prev_ex.pack(side="left", padx=10)
        self.lbl_record_info = ctk.CTkLabel(self.nav_bar_excel, text="", font=ctk.CTkFont(weight="bold", size=12))
        self.lbl_record_info.pack(side="left", expand=True)
        self.btn_next_ex = ctk.CTkButton(self.nav_bar_excel, text=">", width=40, command=self.next_record)
        self.btn_next_ex.pack(side="right", padx=10)

        # ÇIKTI AYARLARI VE AKILLI İSİMLENDİRME
        settings_frame = ctk.CTkFrame(self.right_frame, fg_color=("gray85", "gray20"), corner_radius=10)
        settings_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(settings_frame, text=get_text("lbl_output_settings"), font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))
        
        ctk.CTkLabel(settings_frame, text=get_text("lbl_name_format"), font=ctk.CTkFont(size=12)).pack(anchor="w", padx=15, pady=(5,0))
        self.entry_name_format = ctk.CTkEntry(settings_frame, placeholder_text=get_text("ph_name_format"))
        self.entry_name_format.pack(fill="x", padx=15, pady=(5, 10))

        # Dinamik Etiket (Chip) Taşıyıcısı
        ctk.CTkLabel(settings_frame, text=get_text("lbl_dynamic_tags"), text_color="gray", font=ctk.CTkFont(size=10)).pack(anchor="w", padx=15)
        self.tags_container = ctk.CTkFrame(settings_frame, fg_color="transparent")
        self.tags_container.pack(fill="x", padx=15, pady=(0, 15))

        self.btn_start = ctk.CTkButton(self.right_frame, text=get_text("btn_start_form"), font=ctk.CTkFont(size=16, weight="bold"), height=55, fg_color="#1565C0", hover_color="#0D47A1", command=self.start_processing)
        self.btn_start.pack(fill="x", padx=10, pady=(10, 30))
        self.btn_start.configure(state="disabled")

    # ==========================================
    # --- AKILLI İSİMLENDİRME MOTORU (YENİ) ---
    # ==========================================
    def _add_tag_to_name(self, tag):
        current_text = self.entry_name_format.get().strip()
        if current_text.endswith(".pdf"): current_text = current_text[:-4]
        if current_text and not current_text.endswith("_"): current_text += "_"
        
        new_text = f"{current_text}{{{tag}}}.pdf"
        self.entry_name_format.delete(0, "end")
        self.entry_name_format.insert(0, new_text)

    def generate_smart_naming(self, headers):
        # Önce eski etiketleri temizle
        for w in self.tags_container.winfo_children(): w.destroy()
        if not headers: return
        
        # 1. Otomatik En İyi Formatı Bul
        best_tags = []
        keywords = ['tc', 'kimlik', 'ad', 'soyad', 'isim', 'personel', 'dosya', 'no', 'id']
        
        for kw in keywords:
            for h in headers:
                if kw in h.lower() and h not in best_tags:
                    best_tags.append(h)
                    
        if best_tags:
            # Bulduğu ilk 2 anahtar kelimeyi birleştirir (Örn: {TC_Kimlik}_{Ad_Soyad}.pdf)
            smart_format = "_".join([f"{{{t}}}" for t in best_tags[:2]]) + ".pdf"
        else:
            smart_format = f"{{{headers[0]}}}_{{index}}.pdf"
            
        self.entry_name_format.delete(0, "end")
        self.entry_name_format.insert(0, smart_format)

        # 2. Kullanıcı İçin Tıklanabilir Butonlar (Chipler) Oluştur
        for h in headers[:8]: # Maksimum 8 başlığı buton yap (arayüz taşmasın diye)
            btn = ctk.CTkButton(self.tags_container, text=f"+ {h}", width=40, height=22, 
                                font=ctk.CTkFont(size=11), fg_color="#388E3C", hover_color="#2E7D32", 
                                command=lambda h=h: self._add_tag_to_name(h))
            btn.pack(side="left", padx=(0, 5), pady=2)


    # ==========================================
    # --- JİLET GİBİ TÜRKÇE FONT & KORUMALI HİZALAMA ---
    # ==========================================
    def get_turkish_font(self, doc, page):
        font_path = None
        if sys.platform == "win32":
            possible_path = "C:/Windows/Fonts/arial.ttf"
            if os.path.exists(possible_path): font_path = possible_path
        elif sys.platform == "darwin":
            possible_path = "/Library/Fonts/Arial.ttf"
            if os.path.exists(possible_path): font_path = possible_path
            
        if font_path:
            try:
                page.insert_font(fontname="tr_arial", fontfile=font_path)
                return "tr_arial"
            except: pass
        return "helv"

    def apply_data_to_page_flatten(self, doc, page, row_data):
        font_name = self.get_turkish_font(doc, page)
        
        for widget in list(page.widgets()):
            field_name = widget.field_name
            if field_name in row_data:
                val = str(row_data[field_name])
                rect = widget.rect
                
                try:
                    widget.field_value = ""
                    widget.update()
                except: pass
                
                adjusted_rect = fitz.Rect(rect.x0 + 4, rect.y0 + 3, rect.x1, rect.y1)
                
                try: page.insert_textbox(adjusted_rect, val, fontname=font_name, fontsize=11, color=(0,0,0), align=0)
                except: pass

    # ==========================================
    # --- ÇÖKMEYEN (ANTI-CRASH) ÖNİZLEME MOTORU ---
    # ==========================================
    def create_preview_label(self):
        if hasattr(self, 'lbl_large_preview') and self.lbl_large_preview:
            self.canvas.delete(self.canvas_window)
            self.lbl_large_preview.destroy()
        
        self.lbl_large_preview = ctk.CTkLabel(self.canvas, text=get_text("msg_adv_info"), font=ctk.CTkFont(size=14), text_color="gray")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.lbl_large_preview, anchor="center")
        self.lbl_large_preview.bind("<MouseWheel>", self._on_mousewheel)
        self.center_canvas_content()

    def update_live_preview(self):
        if not self.template_pdf_path: return
        
        self.create_preview_label()
        self.lbl_large_preview.configure(text=get_text("progress_wait"))
        
        self.btn_zoom_in.configure(state="normal")
        self.btn_zoom_out.configure(state="normal")
        self.btn_fit.configure(state="normal")
        self.btn_clear.configure(state="normal")
        
        if self.excel_records:
            self.btn_start.configure(state="normal")
            self.nav_bar_excel.pack(fill="x", pady=(0, 10))
            self.lbl_record_info.configure(text=get_text("lbl_record_indicator").format(self.current_record_index + 1, self.total_records))
            self.btn_prev_ex.configure(state="normal" if self.current_record_index > 0 else "disabled")
            self.btn_next_ex.configure(state="normal" if self.current_record_index < self.total_records - 1 else "disabled")
        else:
            self.btn_start.configure(state="disabled")
            self.nav_bar_excel.pack_forget()

        threading.Thread(target=self._thread_render_preview, daemon=True).start()

    def _thread_render_preview(self):
        try:
            doc = fitz.open(self.template_pdf_path)
            
            if self.excel_records:
                temp_bytes = doc.tobytes()
                doc.close()
                
                doc = fitz.open("pdf", temp_bytes)
                page = doc.load_page(self.current_page_index) 
                
                row_data = self.excel_records[self.current_record_index]
                self.apply_data_to_page_flatten(doc, page, row_data)
            else:
                page = doc.load_page(self.current_page_index)
                
            pix = page.get_pixmap(dpi=150)
            mode = "RGBA" if pix.alpha else "RGB"
            pil_img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
            doc.close()
            
            self.base_high_res_image = pil_img
            self.after(0, self.apply_zoom)
        except Exception as e:
            self.after(0, lambda e=e: self.lbl_large_preview.configure(text=f"Önizleme Hatası:\n{str(e)}", text_color="red"))

    def apply_zoom(self):
        if not self.base_high_res_image: return
        try:
            nw, nh = int(self.base_high_res_image.width * self.zoom_factor), int(self.base_high_res_image.height * self.zoom_factor)
            resized = ImageOps.expand(self.base_high_res_image.resize((nw, nh), Image.Resampling.LANCZOS), border=2, fill="#757575")
            
            self.current_preview_image = ctk.CTkImage(light_image=resized, dark_image=resized, size=(nw, nh))
            
            if hasattr(self, 'lbl_large_preview') and self.lbl_large_preview.winfo_exists():
                self.lbl_large_preview.configure(image=self.current_preview_image, text="")
                self.lbl_large_preview.update_idletasks()
                self.center_canvas_content()
        except Exception as e:
            pass

    def center_canvas_content(self, event=None):
        def _do_center():
            cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
            if cw <= 1 or ch <= 1: 
                self.after(50, _do_center); return
            iw, ih = self.lbl_large_preview.winfo_reqwidth(), self.lbl_large_preview.winfo_reqheight()
            x = cw / 2 if cw > iw else iw / 2
            y = ch / 2 if ch > ih else ih / 2
            self.canvas.coords(self.canvas_window, x, y)
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.after(20, _do_center)

    def change_zoom(self, amount):
        if not self.base_high_res_image: return
        if amount == "fit": self.zoom_factor = (self.canvas.winfo_width() - 40) / self.base_high_res_image.width 
        else: self.zoom_factor = max(0.2, min(self.zoom_factor + amount, 3.0))
        self.apply_zoom()

    def _on_mousewheel(self, event): self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def prev_pdf_page(self):
        if self.current_page_index > 0:
            self.current_page_index -= 1
            self.lbl_pdf_page_info.configure(text=f"{self.current_page_index+1} / {self.total_pages}")
            self.update_live_preview()
            
    def next_pdf_page(self):
        if self.current_page_index < self.total_pages - 1:
            self.current_page_index += 1
            self.lbl_pdf_page_info.configure(text=f"{self.current_page_index+1} / {self.total_pages}")
            self.update_live_preview()

    def prev_record(self):
        if self.current_record_index > 0:
            self.current_record_index -= 1
            self.update_live_preview()
            
    def next_record(self):
        if self.current_record_index < self.total_records - 1:
            self.current_record_index += 1
            self.update_live_preview()

    def clear_all(self):
        self.template_pdf_path = None
        self.excel_data_path = None
        self.excel_records = []
        self.base_high_res_image = None
        self.current_preview_image = None
        
        self.lbl_pdf_name.configure(text=get_text("msg_waiting_file"), text_color="gray")
        self.lbl_excel_name.configure(text=get_text("msg_waiting_excel"), text_color="gray")
        self.entry_name_format.delete(0, "end")
        for w in self.tags_container.winfo_children(): w.destroy()
        
        self.create_preview_label()
        self.nav_bar_pdf.pack_forget()
        self.nav_bar_excel.pack_forget()
        self.btn_start.configure(state="disabled")

    # ==========================================
    # --- DOSYA SEÇİMLERİ ---
    # ==========================================
    def select_pdf(self):
        filepath = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if filepath:
            self.template_pdf_path = filepath
            self.lbl_pdf_name.configure(text=os.path.basename(filepath), text_color=("black", "white"))
            self.current_page_index = 0
            
            try:
                doc = fitz.open(filepath)
                self.total_pages = len(doc)
                doc.close()
                if self.total_pages > 1:
                    self.nav_bar_pdf.pack(fill="x", pady=5)
                    self.lbl_pdf_page_info.configure(text=f"1 / {self.total_pages}")
                else:
                    self.nav_bar_pdf.pack_forget()
            except: pass
            
            self.update_live_preview()

    def select_excel(self):
        filepath = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx *.xls")])
        if filepath:
            self.excel_data_path = filepath
            self.lbl_excel_name.configure(text=os.path.basename(filepath), text_color=("black", "white"))
            self.load_excel_data()

    def load_excel_data(self):
        if not self.excel_data_path or not os.path.exists(self.excel_data_path):
            self.excel_records = []
            return
        try:
            wb = openpyxl.load_workbook(self.excel_data_path, data_only=True)
            sheet = wb.active
            rows = list(sheet.iter_rows(values_only=True))
            wb.close()
            
            if len(rows) > 1:
                headers = [str(h).strip() if h else "" for h in rows[0]]
                self.excel_records = []
                for row in rows[1:]:
                    if not any(row): continue
                    row_data = {headers[i]: str(cell) if cell is not None else "" for i, cell in enumerate(row)}
                    self.excel_records.append(row_data)
                
                self.total_records = len(self.excel_records)
                self.current_record_index = 0
                
                # AKILLI İSİMLENDİRME MOTORUNU TETİKLE
                self.generate_smart_naming(headers)
                
                self.update_live_preview()
            else:
                self.excel_records = []
        except:
            self.excel_records = []

    def add_dropped_files(self, files):
        for f in files:
            if f.lower().endswith('.pdf'):
                self.template_pdf_path = f
                self.lbl_pdf_name.configure(text=os.path.basename(f), text_color=("black", "white"))
                self.current_page_index = 0
                
                try:
                    doc = fitz.open(f)
                    self.total_pages = len(doc)
                    doc.close()
                    if self.total_pages > 1:
                        self.nav_bar_pdf.pack(fill="x", pady=5)
                        self.lbl_pdf_page_info.configure(text=f"1 / {self.total_pages}")
                    else:
                        self.nav_bar_pdf.pack_forget()
                except: pass

                self.update_live_preview()
            elif f.lower().endswith(('.xlsx', '.xls')):
                self.excel_data_path = f
                self.lbl_excel_name.configure(text=os.path.basename(f), text_color=("black", "white"))
                self.load_excel_data()

    # ==========================================
    # --- KAYDETME VE TOPLU OTOMASYON MOTORU ---
    # ==========================================
    def start_processing(self):
        if not self.template_pdf_path or not self.excel_records:
            return
            
        base_dir = filedialog.askdirectory(title="Doldurulan PDF'lerin Kaydedileceği Ana Klasörü Seçin")
        if not base_dir: return

        timestamp = datetime.datetime.now().strftime("%d%m_%H%M")
        save_dir = os.path.join(base_dir, f"Otomasyon_Ciktilari_{timestamp}")
        os.makedirs(save_dir, exist_ok=True)

        self.progress = ProgressWindow(self.winfo_toplevel(), get_text("msg_form_reading"))
        threading.Thread(target=self._thread_process, args=(save_dir,), daemon=True).start()

    def _thread_process(self, save_dir):
        try:
            naming_template = self.entry_name_format.get()
            if not naming_template: naming_template = "Belge_{index}.pdf"

            for idx, row_data in enumerate(self.excel_records, start=1):
                # Her Excel satırı işlenirken yüklenme kutusunun donmasını engellemek için arayüzü zorla yenile
                if hasattr(self, 'progress') and self.progress.winfo_exists():
                    self.progress.update()

                file_name = naming_template.replace("{index}", str(idx))
                
                # Excel'deki verilere göre ismi oluştur
                for key, val in row_data.items():
                    if f"{{{key}}}" in file_name:
                        # İşletim sisteminin dosya isimlerinde kızdığı (/ \ : * ? " < > |) karakterleri siler.
                        safe_val = "".join([c for c in str(val) if c.isalnum() or c in (' ', '-', '_')]).strip()
                        file_name = file_name.replace(f"{{{key}}}", safe_val)
                
                if not file_name.lower().endswith(".pdf"): file_name += ".pdf"
                
                doc = fitz.open(self.template_pdf_path)
                for page in doc:
                    self.apply_data_to_page_flatten(doc, page, row_data)
                
                out_path = os.path.join(save_dir, file_name)
                
                # UYAP'ın imza/form hatası vermemesi için dökümandaki form alanlarını düzleştir (Metne çevir)
                try:
                    for p in doc:
                        p.flatten_widgets()
                except: pass

                # UYAP uyumluluğu için meta verileri sıfırla ve optimize ederek güvenli kaydet
                doc.set_metadata({})
                doc.save(
                    out_path, 
                    deflate=True, 
                    garbage=4, 
                    clean=True
                )
                doc.close()

            from modules.history_manager import add_history
            add_history("📊", "history_action_generic", ["Form Otomasyonu", os.path.basename(save_dir)], save_dir)

            self.after(0, lambda: ActionDialog(self.winfo_toplevel(), get_text("dialog_success"), get_text("msg_form_success"), save_dir))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror(get_text("dialog_error"), str(e)))
        finally:
            if hasattr(self, 'progress'): self.after(0, self.progress.destroy)