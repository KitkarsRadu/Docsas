import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, Canvas
from PIL import Image, ImageOps
import fitz  
import os
import threading
import pytesseract
from modules.pdf_araclari import PasswordDialog, ProgressWindow, ActionDialog, center_window
from modules.language_manager import get_text, lang_manager

# Tesseract'ın Windows'taki varsayılan kurulum yollarını kontrol et
if os.path.exists(r"C:\Program Files\Tesseract-OCR\tesseract.exe"):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
elif os.path.exists(r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"

class OCRSayfasi(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.current_pdf_path = None
        self.current_password = ""
        self.current_page_index = 0
        self.total_pages = 0
        self.zoom_factor = 1.0
        self.base_high_res_image = None
        
        # Etkileşimli kutu sürükleme ve boyutlandırma hafıza değişkenleri
        self.active_edge = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.orig_box_x = 0.0
        self.orig_box_y = 0.0
        self.orig_box_w = 0.0
        self.orig_box_h = 0.0
        
        self.setup_ui()
        self.update_language()

    def setup_ui(self):
        # KİLİT NOKTASI: Sağ menünün genişliğini esnememesi için 450'de donduruyoruz.
        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=0, minsize=450) 
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # --- SOL TARAF: CANLI ÖNİZLEME ALANI ---
        # ==========================================
        self.left_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        top_bar = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 10))
        
        # KİLİT NOKTASI: Üst Butonların "width" değerleri sabitlendi.
        self.btn_select_pdf = ctk.CTkButton(top_bar, text=get_text("lbl_select_pdf_adv"), font=ctk.CTkFont(weight="bold"), 
                      fg_color="#FBC02D", hover_color="#F57F17", text_color="black", command=self.load_pdf, width=180)
        self.btn_select_pdf.pack(side="left", padx=5)
        
        self.btn_clear = ctk.CTkButton(top_bar, text=get_text("btn_clear"), width=100, fg_color="transparent", border_width=1, border_color=("gray60", "gray40"), text_color=("black", "white"), text_color_disabled=("gray50", "gray60"), hover_color=("gray85", "gray25"), command=self.clear_all)
        self.btn_clear.pack(side="left", padx=5)
                      
        self.btn_zoom_in = ctk.CTkButton(top_bar, text=get_text("btn_zoom_in_text"), width=110, fg_color=("gray75", "gray30"), hover_color=("gray65", "gray20"), text_color=("black", "white"), text_color_disabled=("gray50", "gray60"), command=lambda: self.change_zoom(0.2))
        self.btn_zoom_in.pack(side="right", padx=2)
        
        self.btn_fit = ctk.CTkButton(top_bar, text=get_text("btn_fit"), width=100, fg_color=("gray75", "gray30"), hover_color=("gray65", "gray20"), text_color=("black", "white"), text_color_disabled=("gray50", "gray60"), command=lambda: self.change_zoom("fit"))
        self.btn_fit.pack(side="right", padx=2)
        
        self.btn_zoom_out = ctk.CTkButton(top_bar, text=get_text("btn_zoom_out_text"), width=110, fg_color=("gray75", "gray30"), hover_color=("gray65", "gray20"), text_color=("black", "white"), text_color_disabled=("gray50", "gray60"), command=lambda: self.change_zoom(-0.2))
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

        # KİLİT ÇÖZÜM: Önizleme etiketinin kendisi en önde durduğu için fare olaylarını doğrudan ona bağlıyoruz
        self.lbl_large_preview.bind("<ButtonPress-1>", self._on_crop_press)
        self.lbl_large_preview.bind("<B1-Motion>", self._on_crop_drag)
        self.lbl_large_preview.bind("<ButtonRelease-1>", self._on_crop_release)

        self.nav_bar = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        
        # Navigasyon butonlarının sabit genişlikleri
        self.btn_prev = ctk.CTkButton(self.nav_bar, text="<", width=120, command=self.prev_page)
        self.btn_prev.pack(side="left", padx=10)
        self.lbl_page_info = ctk.CTkLabel(self.nav_bar, text="", font=ctk.CTkFont(weight="bold", size=14))
        self.lbl_page_info.pack(side="left", expand=True)
        self.btn_next = ctk.CTkButton(self.nav_bar, text=">", width=120, command=self.next_page)
        self.btn_next.pack(side="right", padx=10)
        self.nav_bar.pack(fill="x", pady=5)
        self.nav_bar.pack_forget()

        # ==========================================
        # --- SAĞ TARAF: AYARLAR PANELİ ---
        # ==========================================
        self.right_frame = ctk.CTkScrollableFrame(self, width=450)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        guide_box = ctk.CTkFrame(self.right_frame, fg_color=("#FFF9C4", "#3E2723"), border_width=1, border_color="#FBC02D", corner_radius=10)
        guide_box.pack(fill="x", padx=10, pady=5)
        self.lbl_guide_title = ctk.CTkLabel(guide_box, text="👁️ " + get_text("tab_ocr_title"), font=ctk.CTkFont(weight="bold"), text_color=("#F57F17", "#FFF59D"))
        self.lbl_guide_title.pack(pady=(10, 2))
        self.lbl_guide_info = ctk.CTkLabel(guide_box, text=get_text("msg_ocr_info"), font=ctk.CTkFont(size=11), justify="center", wraplength=380)
        self.lbl_guide_info.pack(pady=(0, 10), padx=10)

        self.lbl_ocr_mode_title = ctk.CTkLabel(self.right_frame, text=get_text("lbl_ocr_mode"), font=ctk.CTkFont(weight="bold"))
        self.lbl_ocr_mode_title.pack(anchor="w", padx=15, pady=(15, 5))
        
        self.var_ocr_mode = ctk.StringVar(value=get_text("opt_ocr_pdf"))
        self.mode_menu = ctk.CTkSegmentedButton(self.right_frame, values=[get_text("opt_ocr_pdf"), get_text("opt_ocr_region")], variable=self.var_ocr_mode, command=self._on_mode_change)
        self.mode_menu.pack(fill="x", padx=15, pady=5)

        self.lbl_ocr_lang_title = ctk.CTkLabel(self.right_frame, text=get_text("lbl_ocr_lang"), font=ctk.CTkFont(weight="bold"))
        self.lbl_ocr_lang_title.pack(anchor="w", padx=15, pady=(15, 5))
        self.var_ocr_lang = ctk.StringVar(value=get_text("opt_lang_tr"))
        opts_lang = [get_text("opt_lang_tr"), get_text("opt_lang_en"), get_text("opt_lang_de")]
        self.opt_ocr_lang = ctk.CTkOptionMenu(self.right_frame, values=opts_lang, variable=self.var_ocr_lang)
        self.opt_ocr_lang.pack(fill="x", padx=15, pady=5)

        # MİLİMETRİK KOORDİNAT KUTUSU (Sadece Bölgesel Modda Görünür)
        self.frame_coordinates = ctk.CTkFrame(self.right_frame, fg_color=("#E3F2FD", "#0D1B2A"), border_width=1, border_color="#1976D2", corner_radius=10)
        
        def add_slider(parent, label_text, var, default_val, attr_name):
            frame = ctk.CTkFrame(parent, fg_color="transparent")
            frame.pack(fill="x", padx=10, pady=5)
            lbl = ctk.CTkLabel(frame, text=label_text, font=ctk.CTkFont(size=11, weight="bold"), width=130, anchor="w", text_color="#1976D2")
            lbl.pack(side="left")
            setattr(self, attr_name, lbl) # Etikete dinamik isim atama (update_language için)
            
            slider = ctk.CTkSlider(frame, from_=0, to=100, number_of_steps=1000, variable=var, command=lambda v: self._sync_slider(v, entry))
            slider.pack(side="left", fill="x", expand=True, padx=(0, 10))
            slider.bind("<ButtonRelease-1>", lambda e: self.update_live_preview())
            
            entry = ctk.CTkEntry(frame, width=50, height=25)
            entry.pack(side="right")
            entry.insert(0, str(default_val))
            entry.bind("<KeyRelease>", lambda e: self._sync_entry(entry, var))
            var.set(default_val)
            return slider, entry

        self.var_x = ctk.DoubleVar(); add_slider(self.frame_coordinates, get_text("lbl_pos_x"), self.var_x, 10.0, "lbl_coord_x")
        self.var_y = ctk.DoubleVar(); add_slider(self.frame_coordinates, get_text("lbl_pos_y"), self.var_y, 10.0, "lbl_coord_y")
        self.var_w = ctk.DoubleVar(); add_slider(self.frame_coordinates, get_text("lbl_region_w"), self.var_w, 80.0, "lbl_coord_w")
        self.var_h = ctk.DoubleVar(); add_slider(self.frame_coordinates, get_text("lbl_region_h"), self.var_h, 20.0, "lbl_coord_h")

        self.btn_start = ctk.CTkButton(self.right_frame, text=get_text("btn_start_ocr"), font=ctk.CTkFont(size=16, weight="bold"), height=55, fg_color="#FBC02D", hover_color="#F57F17", text_color="black", command=self.start_ocr_process)
        self.btn_start.pack(side="bottom", fill="x", padx=15, pady=30)
        self.btn_start.configure(state="disabled")

        self._on_mode_change(self.var_ocr_mode.get())

    # ==========================================
    # --- MANTIK VE MOTOR FONKSİYONLARI ---
    # ==========================================
    def _sync_slider(self, val, entry_widget):
        entry_widget.delete(0, "end"); entry_widget.insert(0, f"{float(val):.1f}")
    
    def _sync_entry(self, entry_widget, var):
        try:
            val = float(entry_widget.get())
            if 0 <= val <= 100: var.set(val); self.update_live_preview()
        except ValueError: pass

    def _get_canvas_image_corners(self):
        """ Resmin tuval üzerindeki gerçek ekran koordinatlarını ve boyutlarını döner """
        if not self.base_high_res_image: return 0, 0, 0, 0
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        nw = int(self.base_high_res_image.width * self.zoom_factor)
        nh = int(self.base_high_res_image.height * self.zoom_factor)
        cx = max(0, (cw - nw) // 2)
        cy = max(0, (ch - nh) // 2)
        return cx, cy, nw, nh

    def _on_crop_press(self, event):
        if not self.base_high_res_image: return
        mode = self.var_ocr_mode.get()
        if not (mode == get_text("opt_ocr_region") or mode == "Bölgesel Metin Kopyalama" or mode == "Regional Text Copy"): return

        # Doğrudan resim etiketinin pikselleri üzerinden çalıştığımız için ofsetleri sıfırlıyoruz
        nw = self.lbl_large_preview.winfo_width()
        nh = self.lbl_large_preview.winfo_height()
        if nw <= 1 or nh <= 1: return
        
        # Kutunun resim üzerindeki piksel bazlı gerçek koordinatları
        kx = (self.var_x.get() / 100.0 * nw)
        ky = (self.var_y.get() / 100.0 * nh)
        kw = (self.var_w.get() / 100.0 * nw)
        kh = (self.var_h.get() / 100.0 * nh)
        
        mx, my = event.x, event.y
        tol = 25 # Kenar ve köşe yakalama hassasiyet alanı (piksel)

        self.drag_start_x = mx
        self.drag_start_y = my
        self.orig_box_x = self.var_x.get()
        self.orig_box_y = self.var_y.get()
        self.orig_box_w = self.var_w.get()
        self.orig_box_h = self.var_h.get()

        # Fare koordinatı kutunun sınırları içinde mi kontrolü
        if (kx - tol <= mx <= kx + kw + tol) and (ky - tol <= my <= ky + kh + tol):
            is_left = abs(mx - kx) < tol
            is_right = abs(mx - (kx + kw)) < tol
            is_top = abs(my - ky) < tol
            is_bottom = abs(my - (ky + kh)) < tol

            if is_left and is_top: self.active_edge = "top_left"
            elif is_right and is_top: self.active_edge = "top_right"
            elif is_left and is_bottom: self.active_edge = "bottom_left"
            elif is_right and is_bottom: self.active_edge = "bottom_right"
            elif is_left: self.active_edge = "left"
            elif is_right: self.active_edge = "right"
            elif is_top: self.active_edge = "top"
            elif is_bottom: self.active_edge = "bottom"
            else: self.active_edge = "move" # Hiçbir kenara yakın değilse kutuyu komple taşı
        else:
            # Kutunun tamamen dışına tıklandıysa, tıklandığı yerde sıfırdan yeni kutu açmaya başla
            self.var_x.set(max(0.0, min(mx / nw * 100.0, 100.0)))
            self.var_y.set(max(0.0, min(my / nh * 100.0, 100.0)))
            self.var_w.set(1.0)
            self.var_h.set(1.0)
            self.orig_box_x = self.var_x.get()
            self.orig_box_y = self.var_y.get()
            self.orig_box_w = 1.0
            self.orig_box_h = 1.0
            self.active_edge = "bottom_right"

    def _on_crop_drag(self, event):
        if not self.active_edge or not self.base_high_res_image: return
        nw = self.lbl_large_preview.winfo_width()
        nh = self.lbl_large_preview.winfo_height()
        if nw <= 1 or nh <= 1: return

        # Farenin hareket farkını yüzdesel cinsten hesapla
        dx = (event.x - self.drag_start_x) / nw * 100.0
        dy = (event.y - self.drag_start_y) / nh * 100.0

        if self.active_edge == "move":
            self.var_x.set(max(0.0, min(self.orig_box_x + dx, 100.0 - self.var_w.get())))
            self.var_y.set(max(0.0, min(self.orig_box_y + dy, 100.0 - self.var_h.get())))
        elif self.active_edge == "right":
            self.var_w.set(max(1.0, min(self.orig_box_w + dx, 100.0 - self.var_x.get())))
        elif self.active_edge == "bottom":
            self.var_h.set(max(1.0, min(self.orig_box_h + dy, 100.0 - self.var_y.get())))
        elif self.active_edge == "left":
            val = max(0.0, min(self.orig_box_x + dx, self.orig_box_x + self.orig_box_w - 1.0))
            self.var_w.set(self.orig_box_x + self.orig_box_w - val)
            self.var_x.set(val)
        elif self.active_edge == "top":
            val = max(0.0, min(self.orig_box_y + dy, self.orig_box_y + self.orig_box_h - 1.0))
            self.var_h.set(self.orig_box_y + self.orig_box_h - val)
            self.var_y.set(val)
        elif self.active_edge == "bottom_right":
            self.var_w.set(max(1.0, min(self.orig_box_w + dx, 100.0 - self.var_x.get())))
            self.var_h.set(max(1.0, min(self.orig_box_h + dy, 100.0 - self.var_y.get())))
        elif self.active_edge == "top_left":
            vx = max(0.0, min(self.orig_box_x + dx, self.orig_box_x + self.orig_box_w - 1.0))
            self.var_w.set(self.orig_box_x + self.orig_box_w - vx); self.var_x.set(vx)
            vy = max(0.0, min(self.orig_box_y + dy, self.orig_box_y + self.orig_box_h - 1.0))
            self.var_h.set(self.orig_box_y + self.orig_box_h - vy); self.var_y.set(vy)

        self.update_live_preview()

    def _on_crop_release(self, event):
        self.active_edge = None

    def _on_mode_change(self, val):
        # Eğer İngilizce'deki değeri seçtiyse de doğru panele girmesi için kontrol
        is_region = (val == get_text("opt_ocr_region") or val == "Bölgesel Metin Kopyalama" or val == "Regional Text Copy")
        if is_region: self.frame_coordinates.pack(fill="x", padx=15, pady=10, before=self.btn_start)
        else: self.frame_coordinates.pack_forget()
        self.update_live_preview()

    def create_preview_label(self):
        if hasattr(self, 'lbl_large_preview') and self.lbl_large_preview:
            self.canvas.delete(self.canvas_window)
            self.lbl_large_preview.destroy()
        self.lbl_large_preview = ctk.CTkLabel(self.canvas, text=get_text("msg_adv_info"), font=ctk.CTkFont(size=14), text_color="gray")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.lbl_large_preview, anchor="center")
        self.lbl_large_preview.bind("<MouseWheel>", self._on_mousewheel)
        self.center_canvas_content()

    # --- SÜRÜKLE BIRAK KARŞILAMA MOTORU ---
    def add_dropped_files(self, files):
        pdf_files = [f for f in files if f.lower().endswith('.pdf')]
        if not pdf_files: return
        
        path = pdf_files[0]
        self.clear_all()
        doc = fitz.open(path)
        pw = ""
        if doc.is_encrypted:
            dialog = PasswordDialog(self.winfo_toplevel(), get_text("dialog_warning"), f"'{os.path.basename(path)}' şifreli. Şifreyi girin:")
            pw = dialog.get_result()
            if not pw or not doc.authenticate(pw): messagebox.showerror(get_text("dialog_error"), "Yanlış Şifre!"); doc.close(); return
        self.total_pages = len(doc); doc.close()
        self.current_pdf_path = path; self.current_password = pw; self.current_page_index = 0
        self.nav_bar.pack(fill="x", pady=5); self.btn_start.configure(state="normal")
        self.update_live_preview()
    
    def load_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if not path: return
        self.clear_all()
        doc = fitz.open(path)
        pw = ""
        if doc.is_encrypted:
            dialog = PasswordDialog(self.winfo_toplevel(), get_text("dialog_warning"), f"'{os.path.basename(path)}' şifreli. Şifreyi girin:")
            pw = dialog.get_result()
            if not pw or not doc.authenticate(pw): messagebox.showerror(get_text("dialog_error"), "Yanlış Şifre!"); doc.close(); return
        self.total_pages = len(doc); doc.close()
        self.current_pdf_path = path; self.current_password = pw; self.current_page_index = 0
        self.nav_bar.pack(fill="x", pady=5); self.btn_start.configure(state="normal")
        self.update_live_preview()

    def update_live_preview(self):
        if not self.current_pdf_path: return
        mode = self.var_ocr_mode.get()
        x = self.var_x.get() / 100.0
        y = self.var_y.get() / 100.0
        w = self.var_w.get() / 100.0
        h = self.var_h.get() / 100.0
        threading.Thread(target=self._thread_render_page, args=(mode, x, y, w, h), daemon=True).start()

    def _thread_render_page(self, mode, x_pct, y_pct, w_pct, h_pct):
        try:
            doc = fitz.open(self.current_pdf_path)
            if doc.is_encrypted: doc.authenticate(self.current_password)
            page = doc.load_page(self.current_page_index)

            # Bölgesel OCR için Kırmızı Kılavuz Kutu Çizimi
            is_region = (mode == get_text("opt_ocr_region") or mode == "Bölgesel Metin Kopyalama" or mode == "Regional Text Copy")
            if is_region:
                x0 = page.rect.width * x_pct
                y0 = page.rect.height * y_pct
                x1 = x0 + (page.rect.width * w_pct)
                y1 = y0 + (page.rect.height * h_pct)
                rect = fitz.Rect(x0, y0, x1, y1)
                page.draw_rect(rect, color=(1, 0, 0), width=3) # Kırmızı Çerçeve

            pix = page.get_pixmap(dpi=150)
            mode_color = "RGBA" if pix.alpha else "RGB"
            pil_img = Image.frombytes(mode_color, [pix.width, pix.height], pix.samples)
            doc.close()
            self.base_high_res_image = pil_img
            self.after(0, self.apply_zoom)
        except: pass

    def change_zoom(self, amount):
        if not self.base_high_res_image: return
        if amount == "fit": self.zoom_factor = (self.canvas.winfo_width() - 40) / self.base_high_res_image.width 
        else: self.zoom_factor = max(0.2, min(self.zoom_factor + amount, 3.0))
        self.apply_zoom()

    def apply_zoom(self):
        if not self.base_high_res_image: return
        nw, nh = int(self.base_high_res_image.width * self.zoom_factor), int(self.base_high_res_image.height * self.zoom_factor)
        resized = ImageOps.expand(self.base_high_res_image.resize((nw, nh), Image.Resampling.LANCZOS), border=2, fill="#757575")
        ctk_img = ctk.CTkImage(light_image=resized, dark_image=resized, size=(nw, nh))
        self.lbl_large_preview.configure(image=ctk_img, text="")
        self.lbl_large_preview.update_idletasks()
        self.center_canvas_content()
        self.lbl_page_info.configure(text=f"{self.current_page_index + 1} / {self.total_pages}")
        self.btn_prev.configure(state="normal" if self.current_page_index > 0 else "disabled")
        self.btn_next.configure(state="normal" if self.current_page_index < self.total_pages - 1 else "disabled")

    def center_canvas_content(self, event=None):
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        
        if cw <= 1 or ch <= 1: 
            return
            
        iw = self.lbl_large_preview.winfo_reqwidth()
        ih = self.lbl_large_preview.winfo_reqheight()
        
        x = cw / 2 if cw > iw else iw / 2
        y = ch / 2 if ch > ih else ih / 2
        
        self.canvas.coords(self.canvas_window, x, y)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_mousewheel(self, event): self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    def prev_page(self): self.current_page_index -= 1; self.update_live_preview()
    def next_page(self): self.current_page_index += 1; self.update_live_preview()
    def clear_all(self):
        self.current_pdf_path = None; self.current_password = ""; self.current_page_index = 0; self.total_pages = 0; self.base_high_res_image = None
        self.create_preview_label(); self.nav_bar.pack_forget(); self.btn_start.configure(state="disabled")

    # ==========================================
    # --- DEV OCR MOTORU ---
    # ==========================================
    def start_ocr_process(self):
        try:
            pytesseract.get_tesseract_version() # Tesseract yüklü mü kontrol et
        except Exception:
            messagebox.showerror(get_text("dialog_error"), get_text("msg_tesseract_error"))
            return

        mode = self.var_ocr_mode.get()
        lang_map = {get_text("opt_lang_tr"): "tur", get_text("opt_lang_en"): "eng", get_text("opt_lang_de"): "deu", "Türkçe": "tur", "English": "eng", "German": "deu", "Almanca": "deu"}
        lang_code = lang_map.get(self.var_ocr_lang.get(), "tur")
        
        is_region = (mode == get_text("opt_ocr_region") or mode == "Bölgesel Metin Kopyalama" or mode == "Regional Text Copy")
        
        if is_region:
            x = self.var_x.get() / 100.0; y = self.var_y.get() / 100.0; w = self.var_w.get() / 100.0; h = self.var_h.get() / 100.0
            self.progress = ProgressWindow(self.winfo_toplevel(), get_text("progress_processing"))
            threading.Thread(target=self._thread_regional_ocr, args=(lang_code, x, y, w, h), daemon=True).start()
        else:
            save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], initialfile="Aranabilir_Belge.pdf")
            if not save_path: return
            self.progress = ProgressWindow(self.winfo_toplevel(), get_text("progress_processing"))
            threading.Thread(target=self._thread_full_ocr, args=(save_path, lang_code), daemon=True).start()

    def _thread_regional_ocr(self, lang_code, x_pct, y_pct, w_pct, h_pct):
        try:
            doc = fitz.open(self.current_pdf_path)
            if doc.is_encrypted: doc.authenticate(self.current_password)
            page = doc.load_page(self.current_page_index)
            
            x0 = page.rect.width * x_pct
            y0 = page.rect.height * y_pct
            x1 = x0 + (page.rect.width * w_pct)
            y1 = y0 + (page.rect.height * h_pct)
            rect = fitz.Rect(x0, y0, x1, y1)
            
            pix = page.get_pixmap(clip=rect, dpi=300) # OCR için yüksek çözünürlük
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            doc.close()
            
            extracted_text = pytesseract.image_to_string(img, lang=lang_code)
            
            def show_result():
                dialog = ctk.CTkToplevel(self.winfo_toplevel())
                dialog.title(get_text("lbl_extracted_text"))
                dialog.geometry("600x400")
                dialog.transient(self.winfo_toplevel())
                center_window(dialog, self.winfo_toplevel())
                
                txt = ctk.CTkTextbox(dialog, font=ctk.CTkFont(size=14))
                txt.pack(fill="both", expand=True, padx=20, pady=20)
                txt.insert("1.0", extracted_text)

                # --- ÇÖZÜM: CTK UYUMLU GÜVENLİ SAĞ TIK MENÜSÜ ---
                m_menu = tk.Menu(dialog, tearoff=0, fg="black", bg="white")
                
                def copy_text():
                    dialog.clipboard_clear()
                    # Eğer seçili metin varsa onu, yoksa tümünü kopyala
                    if txt.tag_ranges("sel"):
                        dialog.clipboard_append(txt.get("sel.first", "sel.last"))
                    else:
                        dialog.clipboard_append(txt.get("1.0", "end-1c"))
                        
                def select_all():
                    txt.tag_add("sel", "1.0", "end")

                m_menu.add_command(label="Kopyala (Copy)", command=copy_text)
                m_menu.add_command(label="Tümünü Seç (Select All)", command=select_all)

                def popup_trigger(event):
                    m_menu.post(event.x_root, event.y_root)

                txt.bind("<Button-3>", popup_trigger) # Windows / Linux sağ tık
                txt.bind("<Button-2>", popup_trigger) # MacOS sağ tık
                
            self.after(0, show_result)
        except Exception as e: self.after(0, lambda: messagebox.showerror(get_text("dialog_error"), str(e)))
        finally: self.after(0, self.progress.destroy)

    def _thread_full_ocr(self, save_path, lang_code):
        try:
            doc = fitz.open(self.current_pdf_path)
            if doc.is_encrypted: doc.authenticate(self.current_password)
            
            out_pdf = fitz.open()
            
            for i in range(len(doc)):
                # Her ağır Tesseract OCR sayfa geçişinde yüklenme kutusunu tazeleyerek donmayı kırın
                if hasattr(self, 'progress') and self.progress.winfo_exists():
                    self.progress.update()

                page = doc.load_page(i)
                pix = page.get_pixmap(dpi=300) # OCR kalitesi
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # SİHİRLİ KOMUT: Tesseract arka planda resmi pdf'e çevirip görünmez metin katar
                try:
                    ppdf_bytes = pytesseract.image_to_pdf_or_hocr(img, extension='pdf', lang=lang_code)
                    page_pdf = fitz.open("pdf", ppdf_bytes)
                    out_pdf.insert_pdf(page_pdf)
                    page_pdf.close()
                except Exception as ocr_err:
                    print(f"Sayfa OCR Hatası: {ocr_err}")
                    continue
            
            # --- UYAP UYUMLULUK VE GÜVENLİK ENTEGRASYONU ---
            # 1. OCR sonrasında dökümanın iç yapısında oluşabilecek geçici form alanlarını sabitleyip düzleştiriyoruz
            try:
                for page in out_pdf:
                    page.flatten_widgets()
            except: pass

            # 2. Yerel dosya yollarını ve bilgisayar adını (Geçersiz Yol Hatasını) önlemek için meta veriyi uçuruyoruz
            out_pdf.set_metadata({})
            try: out_pdf.set_xml_metadata("")
            except: pass

            # 3. Kaydetme sorununa yol açacak linear=True parametresini eklemeden derin temizlikle (garbage=4) kaydediyoruz
            out_pdf.save(
                save_path, 
                deflate=True,
                garbage=4, 
                clean=True
            )
            out_pdf.close()
            doc.close()
            from modules.history_manager import add_history
            add_history("🔍", "history_action_ocr", [os.path.basename(self.current_pdf_path), os.path.basename(save_path)], save_path)
            
            self.after(0, lambda: ActionDialog(self.winfo_toplevel(), get_text("dialog_success"), get_text("msg_process_success"), save_path))
        except Exception as e: self.after(0, lambda: messagebox.showerror(get_text("dialog_error"), str(e)))
        finally: self.after(0, self.progress.destroy)

    # ==========================================
    # --- GERÇEK ZAMANLI KUSURSUZ ÇEVİRİ MOTORU ---
    # ==========================================
    def update_language(self):
        # Sol Taraf Butonları
        if hasattr(self, 'btn_select_pdf'): self.btn_select_pdf.configure(text=get_text("lbl_select_pdf_adv"))
        if hasattr(self, 'btn_clear'): self.btn_clear.configure(text=get_text("btn_clear"))
        if hasattr(self, 'btn_zoom_in'): self.btn_zoom_in.configure(text=get_text("btn_zoom_in_text"))
        if hasattr(self, 'btn_fit'): self.btn_fit.configure(text=get_text("btn_fit"))
        if hasattr(self, 'btn_zoom_out'): self.btn_zoom_out.configure(text=get_text("btn_zoom_out_text"))
        if not self.current_pdf_path and hasattr(self, 'lbl_large_preview'):
            self.lbl_large_preview.configure(text=get_text("msg_adv_info"))

        # Sağ Taraf Bilgi Ekranı
        if hasattr(self, 'lbl_guide_title'): self.lbl_guide_title.configure(text="👁️ " + get_text("tab_ocr_title"))
        if hasattr(self, 'lbl_guide_info'): self.lbl_guide_info.configure(text=get_text("msg_ocr_info"))
        
        # Başlık ve Seçenekler
        if hasattr(self, 'lbl_ocr_mode_title'): self.lbl_ocr_mode_title.configure(text=get_text("lbl_ocr_mode"))
        if hasattr(self, 'lbl_ocr_lang_title'): self.lbl_ocr_lang_title.configure(text=get_text("lbl_ocr_lang"))
        
        # OCR Modu Değer Koruyucusu (Segmented Button)
        if hasattr(self, 'mode_menu'):
            curr_mode = self.var_ocr_mode.get()
            m_idx = 0
            m_tr = ["Tam Sayfa OCR (Aranabilir PDF)", "Bölgesel Metin Kopyalama"]
            m_en = ["Full Page OCR (Searchable PDF)", "Regional Text Copy"]
            if curr_mode in m_tr: m_idx = m_tr.index(curr_mode)
            if curr_mode in m_en: m_idx = m_en.index(curr_mode)
            opts_mode = [get_text("opt_ocr_pdf"), get_text("opt_ocr_region")]
            self.mode_menu.configure(values=opts_mode)
            self.var_ocr_mode.set(opts_mode[m_idx])
            
        # Dil Seçimi Değer Koruyucusu (Option Menu)
        if hasattr(self, 'opt_ocr_lang'):
            curr_lang = self.var_ocr_lang.get()
            l_idx = 0
            l_tr = ["Türkçe", "İngilizce", "Almanca"]
            l_en = ["Turkish", "English", "German"]
            if curr_lang in l_tr: l_idx = l_tr.index(curr_lang)
            if curr_lang in l_en: l_idx = l_en.index(curr_lang)
            opts_lang = [get_text("opt_lang_tr"), get_text("opt_lang_en"), get_text("opt_lang_de")]
            self.opt_ocr_lang.configure(values=opts_lang)
            self.var_ocr_lang.set(opts_lang[l_idx])

        # Koordinat Etiketleri
        if hasattr(self, 'lbl_coord_x'): self.lbl_coord_x.configure(text=get_text("lbl_pos_x"))
        if hasattr(self, 'lbl_coord_y'): self.lbl_coord_y.configure(text=get_text("lbl_pos_y"))
        if hasattr(self, 'lbl_coord_w'): self.lbl_coord_w.configure(text=get_text("lbl_region_w"))
        if hasattr(self, 'lbl_coord_h'): self.lbl_coord_h.configure(text=get_text("lbl_region_h"))

        # Başlat Butonu
        if hasattr(self, 'btn_start'): self.btn_start.configure(text=get_text("btn_start_ocr"))