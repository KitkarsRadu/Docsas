import customtkinter as ctk
from tkinter import filedialog, messagebox, Canvas, colorchooser
from PIL import Image, ImageOps
import fitz  
import os
import sys
import re
import threading
from modules.pdf_araclari import PasswordDialog, ProgressWindow, ActionDialog
from modules.language_manager import get_text

def center_window(window, parent):
    window.update_idletasks()
    pw, ph = parent.winfo_width(), parent.winfo_height()
    px, py = parent.winfo_rootx(), parent.winfo_rooty()
    ww, wh = window.winfo_width(), window.winfo_height()
    x = px + (pw - ww) // 2
    y = py + (ph - wh) // 2
    window.geometry(f"+{x}+{y}")

class RegexHelpDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(get_text("regex_title"))
        self.geometry("550x380")
        self.transient(parent) # Chrome'un üstüne zorla çıkmasını engeller
        center_window(self, parent)
        self.grab_set()

        lbl_title = ctk.CTkLabel(self, text=get_text("regex_title"), font=ctk.CTkFont(size=18, weight="bold"), text_color="#1976D2")
        lbl_title.pack(pady=(20, 10))

        textbox = ctk.CTkTextbox(self, width=500, height=230, font=ctk.CTkFont(size=14))
        textbox.pack(padx=20, pady=10, fill="both", expand=True)
        textbox.insert("1.0", get_text("regex_desc"))
        textbox.configure(state="disabled")

        ctk.CTkButton(self, text=get_text("dialog_ok"), width=150, height=40, command=self.destroy).pack(pady=15)


class PDFGuvenlikSayfasi(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        
        self.current_pdf_path = None
        self.current_password = ""
        self.current_page_index = 0
        self.total_pages = 0
        self.zoom_factor = 1.0
        self.base_high_res_image = None
        
        self.custom_txt_color_rgb = None
        
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
        
        ctk.CTkButton(top_bar, text=get_text("lbl_select_pdf_adv"), font=ctk.CTkFont(weight="bold"), fg_color="#B71C1C", hover_color="#880E4F", command=self.load_pdf).pack(side="left", padx=5)
        self.btn_clear = ctk.CTkButton(top_bar, text=get_text("btn_clear"), width=80, fg_color="transparent", border_width=1, border_color=("gray60", "gray40"), text_color=("black", "white"), text_color_disabled=("gray50", "gray60"), hover_color=("gray85", "gray25"), command=self.clear_all)
        self.btn_clear.pack(side="left", padx=5)
                      
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

        self.nav_bar = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.btn_prev = ctk.CTkButton(self.nav_bar, text="<", width=50, command=self.prev_page)
        self.btn_prev.pack(side="left", padx=10)
        self.lbl_page_info = ctk.CTkLabel(self.nav_bar, text="", font=ctk.CTkFont(weight="bold"))
        self.lbl_page_info.pack(side="left", expand=True)
        self.btn_next = ctk.CTkButton(self.nav_bar, text=">", width=50, command=self.next_page)
        self.btn_next.pack(side="right", padx=10)
        self.nav_bar.pack(fill="x", pady=5)
        self.nav_bar.pack_forget()

        # ==========================================
        # --- SAĞ TARAF: ALT ALTA ENTEGRE ARAYÜZ ---
        # ==========================================
        self.right_frame = ctk.CTkScrollableFrame(self, width=420)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        guide_box = ctk.CTkFrame(self.right_frame, fg_color=("#FFEBEE", "#2C1212"), border_width=1, border_color="#B71C1C", corner_radius=10)
        guide_box.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(guide_box, text="🛑 " + get_text("tab_kvkk_guide"), font=ctk.CTkFont(weight="bold"), text_color="#B71C1C").pack(pady=(10, 2))
        ctk.CTkLabel(guide_box, text=get_text("msg_redact_guide"), font=ctk.CTkFont(size=11), justify="center", wraplength=340).pack(pady=(0, 10), padx=10)

        # ----------------------------------------------------
        # BÖLÜM 1: SADECE KARARTMA (SANSÜR) AYARLARI
        # ----------------------------------------------------
        ctk.CTkLabel(self.right_frame, text=get_text("lbl_redact_section"), font=ctk.CTkFont(size=14, weight="bold"), text_color="#E53935").pack(anchor="w", padx=15, pady=(15, 5))
        frame_redact = ctk.CTkFrame(self.right_frame, fg_color=("gray85", "gray20"), corner_radius=10)
        frame_redact.pack(fill="x", padx=10, pady=5)

        self.var_redact_type = ctk.StringVar(value=get_text("opt_redact_words"))
        self.type_menu = ctk.CTkSegmentedButton(frame_redact, values=[get_text("opt_redact_words"), get_text("opt_redact_regex")], variable=self.var_redact_type, command=lambda v: self.update_live_preview())
        self.type_menu.pack(fill="x", padx=10, pady=10)

        self.txt_redact = ctk.CTkTextbox(frame_redact, height=80, border_width=1)
        self.txt_redact.pack(fill="x", padx=10, pady=5)
        self.txt_redact.bind("<KeyRelease>", lambda e: self.update_live_preview())
        
        self.lbl_regex_help = ctk.CTkLabel(frame_redact, text=get_text("lbl_help_regex"), text_color="#1976D2", font=ctk.CTkFont(size=11, underline=True), cursor="hand2")
        self.lbl_regex_help.pack(anchor="e", padx=10)
        self.lbl_regex_help.bind("<Button-1>", lambda e: RegexHelpDialog(self.winfo_toplevel()))

        ctk.CTkLabel(frame_redact, text=get_text("lbl_bant_color"), font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10, pady=(5,0))
        self.var_color_name = ctk.StringVar(value=get_text("opt_color_black"))
        colors = [get_text("opt_color_black"), get_text("opt_color_transparent"), get_text("opt_color_gray"), get_text("opt_color_red"), get_text("opt_color_blue")]
        ctk.CTkSegmentedButton(frame_redact, values=colors, variable=self.var_color_name, command=lambda v: self.update_live_preview()).pack(fill="x", padx=10, pady=5)

        self.var_wipe_data = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(frame_redact, text=get_text("chk_wipe_data"), variable=self.var_wipe_data, font=ctk.CTkFont(weight="bold", size=11), text_color="#B71C1C", command=self.update_live_preview).pack(anchor="w", padx=10, pady=(10, 15))

        # ----------------------------------------------------
        # BÖLÜM 2: BAĞIMSIZ METİN VE MİLİMETRİK KOORDİNATLAR
        # ----------------------------------------------------
        ctk.CTkLabel(self.right_frame, text=get_text("lbl_free_text_section"), font=ctk.CTkFont(size=14, weight="bold"), text_color="#1E88E5").pack(anchor="w", padx=15, pady=(15, 5))
        frame_free_text = ctk.CTkFrame(self.right_frame, fg_color=("#E3F2FD", "#0D1B2A"), border_width=1, border_color="#1976D2", corner_radius=10)
        frame_free_text.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(frame_free_text, text=get_text("lbl_free_text_input"), font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10, pady=(10, 0))
        self.ent_free_text = ctk.CTkEntry(frame_free_text, placeholder_text="Örn: GİZLİDİR")
        self.ent_free_text.pack(fill="x", padx=10, pady=5)
        self.ent_free_text.bind("<KeyRelease>", lambda e: self.update_live_preview())

        # MİLİMETRİK X EKSENİ
        frame_x = ctk.CTkFrame(frame_free_text, fg_color="transparent")
        frame_x.pack(fill="x", padx=10, pady=(10, 5))
        ctk.CTkLabel(frame_x, text=get_text("lbl_x_axis"), font=ctk.CTkFont(size=11, weight="bold"), width=130, anchor="w", text_color="#1976D2").pack(side="left")
        self.var_x = ctk.DoubleVar(value=50.0)
        self.slider_x = ctk.CTkSlider(frame_x, from_=0, to=100, number_of_steps=1000, variable=self.var_x, command=self._sync_x_slider)
        self.slider_x.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.slider_x.bind("<ButtonRelease-1>", lambda e: self.update_live_preview())
        self.ent_x = ctk.CTkEntry(frame_x, width=50, height=25)
        self.ent_x.pack(side="right")
        self.ent_x.insert(0, "50.0")
        self.ent_x.bind("<KeyRelease>", self._sync_x_entry)

        # MİLİMETRİK Y EKSENİ
        frame_y = ctk.CTkFrame(frame_free_text, fg_color="transparent")
        frame_y.pack(fill="x", padx=10, pady=(0, 5))
        ctk.CTkLabel(frame_y, text=get_text("lbl_y_axis"), font=ctk.CTkFont(size=11, weight="bold"), width=130, anchor="w", text_color="#1976D2").pack(side="left")
        self.var_y = ctk.DoubleVar(value=50.0)
        self.slider_y = ctk.CTkSlider(frame_y, from_=0, to=100, number_of_steps=1000, variable=self.var_y, command=self._sync_y_slider)
        self.slider_y.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.slider_y.bind("<ButtonRelease-1>", lambda e: self.update_live_preview())
        self.ent_y = ctk.CTkEntry(frame_y, width=50, height=25)
        self.ent_y.pack(side="right")
        self.ent_y.insert(0, "50.0")
        self.ent_y.bind("<KeyRelease>", self._sync_y_entry)

        # OLUMLU DÜZELTME: SAYDAMLIK (OPACITY) 
        frame_op = ctk.CTkFrame(frame_free_text, fg_color="transparent")
        frame_op.pack(fill="x", padx=10, pady=(0, 5))
        ctk.CTkLabel(frame_op, text=get_text("lbl_wm_opacity"), font=ctk.CTkFont(size=11, weight="bold"), width=130, anchor="w", text_color="#1976D2").pack(side="left")
        self.slider_txt_opacity = ctk.CTkSlider(frame_op, from_=0.1, to=1.0, number_of_steps=9, command=lambda v: self.update_live_preview())
        self.slider_txt_opacity.set(1.0)
        self.slider_txt_opacity.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(frame_op, text="", width=50).pack(side="right") 

        # OLUMLU DÜZELTME: 360 DERECE DÖNDÜRME (ROTATION)
        frame_rot = ctk.CTkFrame(frame_free_text, fg_color="transparent")
        frame_rot.pack(fill="x", padx=10, pady=(0, 15))
        ctk.CTkLabel(frame_rot, text=get_text("lbl_wm_rot"), font=ctk.CTkFont(size=11, weight="bold"), width=130, anchor="w", text_color="#1976D2").pack(side="left")
        
        self.var_txt_rot = ctk.DoubleVar(value=0.0)
        self.ent_txt_rot = ctk.CTkEntry(frame_rot, width=50, height=25)
        self.ent_txt_rot.pack(side="right")
        self.ent_txt_rot.insert(0, "0.0")
        
        def on_txt_rot_slider(val):
            self.ent_txt_rot.delete(0, "end"); self.ent_txt_rot.insert(0, f"{float(val):.1f}"); self.update_live_preview()
        def on_txt_rot_entry(e):
            try:
                v = float(self.ent_txt_rot.get())
                if -180 <= v <= 180: self.var_txt_rot.set(v); self.update_live_preview()
            except: pass

        self.slider_txt_rot = ctk.CTkSlider(frame_rot, from_=-180, to=180, number_of_steps=360, variable=self.var_txt_rot, command=on_txt_rot_slider)
        self.slider_txt_rot.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.ent_txt_rot.bind("<KeyRelease>", on_txt_rot_entry)

        # Yazı Stili Ayarları
        style_frame = ctk.CTkFrame(frame_free_text, fg_color=("gray90", "gray15"), corner_radius=8)
        style_frame.pack(fill="x", padx=10, pady=(0, 10))

        font_frame = ctk.CTkFrame(style_frame, fg_color="transparent")
        font_frame.pack(fill="x", padx=5, pady=(10, 5))
        ctk.CTkLabel(font_frame, text=get_text("lbl_font_family"), font=ctk.CTkFont(size=11)).pack(side="left")
        self.var_font_family = ctk.StringVar(value="Arial")
        ctk.CTkOptionMenu(font_frame, values=["Arial", "Times New Roman", "Courier", "Comic Sans"], variable=self.var_font_family, command=lambda v: self.update_live_preview()).pack(side="right", fill="x", expand=True, padx=(10, 0))

        row_opts = ctk.CTkFrame(style_frame, fg_color="transparent")
        row_opts.pack(fill="x", padx=5, pady=(0, 10))
        
        # OLUMLU DÜZELTME: RENK PALETİ SEÇİCİSİ (🎨)
        color_frame = ctk.CTkFrame(row_opts, fg_color="transparent")
        color_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(color_frame, text=get_text("lbl_text_color"), font=ctk.CTkFont(size=11)).pack(anchor="w")
        
        inner_color = ctk.CTkFrame(color_frame, fg_color="transparent")
        inner_color.pack(fill="x")
        
        self.var_txt_color = ctk.StringVar(value=get_text("opt_txt_black"))
        txt_colors = [get_text("opt_txt_black"), get_text("opt_txt_white"), get_text("opt_txt_red"), get_text("opt_txt_blue")]
        self.opt_txt_color = ctk.CTkOptionMenu(inner_color, values=txt_colors, variable=self.var_txt_color, command=self._on_txt_color_preset)
        self.opt_txt_color.pack(side="left", fill="x", expand=True)
        
        self.btn_txt_custom_color = ctk.CTkButton(inner_color, text="🎨", width=30, font=ctk.CTkFont(size=15), fg_color=("gray75", "gray30"), text_color=("black", "white"), command=self.pick_txt_custom_color)
        self.btn_txt_custom_color.pack(side="right", padx=(5,0))

        size_frame = ctk.CTkFrame(row_opts, fg_color="transparent")
        size_frame.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkLabel(size_frame, text=get_text("lbl_text_size"), font=ctk.CTkFont(size=11)).pack(anchor="w")
        self.var_txt_size = ctk.StringVar(value="24")
        ctk.CTkOptionMenu(size_frame, values=["10", "12", "14", "16", "20", "24", "36", "48", "72"], variable=self.var_txt_size, command=lambda v: self.update_live_preview()).pack(fill="x")

        style_opt_frame = ctk.CTkFrame(row_opts, fg_color="transparent")
        style_opt_frame.pack(side="left", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(style_opt_frame, text=get_text("lbl_text_style"), font=ctk.CTkFont(size=11)).pack(anchor="w")
        self.var_txt_style = ctk.StringVar(value=get_text("opt_bold"))
        ctk.CTkOptionMenu(style_opt_frame, values=[get_text("opt_normal"), get_text("opt_bold"), get_text("opt_italic"), get_text("opt_bold_italic")], variable=self.var_txt_style, command=lambda v: self.update_live_preview()).pack(fill="x")

        # ----------------------------------------------------
        # BÖLÜM 3: SAYFA VE KAYIT
        # ----------------------------------------------------
        ctk.CTkLabel(self.right_frame, text=get_text("tab_page_num"), font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15, pady=(20, 2))
        self.var_all_pages = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(self.right_frame, text=get_text("chk_all_pages"), variable=self.var_all_pages, command=self._toggle_page_entry).pack(anchor="w", padx=20, pady=5)
        
        self.ent_pages = ctk.CTkEntry(self.right_frame, placeholder_text=get_text("ph_page_ranges"))
        self.ent_pages.pack(fill="x", padx=20, pady=5)
        self.ent_pages.configure(state="disabled")
        self.ent_pages.bind("<KeyRelease>", lambda e: self.update_live_preview())

        self.btn_save = ctk.CTkButton(self.right_frame, text=get_text("btn_apply_save_redact"), font=ctk.CTkFont(size=16, weight="bold"), height=55, fg_color="#B71C1C", hover_color="#880E4F", command=self.start_save_process)
        self.btn_save.pack(side="bottom", fill="x", padx=20, pady=30)
        self.btn_save.configure(state="disabled")

    # ==========================================
    # --- MANTIK VE MOTOR FONKSİYONLARI ---
    # ==========================================
    
    def _on_txt_color_preset(self, val):
        self.custom_txt_color_rgb = None
        self.btn_txt_custom_color.configure(fg_color=("gray75", "gray30"), text_color=("black", "white"))
        self.update_live_preview()

    def pick_txt_custom_color(self):
        color_data = colorchooser.askcolor(title="Renk Seç")
        if color_data and color_data[0]:
            r, g, b = color_data[0]
            self.custom_txt_color_rgb = (r/255.0, g/255.0, b/255.0)
            self.var_txt_color.set("") 
            
            fg_hex = color_data[1]
            text_c = "white" if (r*0.299 + g*0.587 + b*0.114) < 186 else "black"
            self.btn_txt_custom_color.configure(fg_color=fg_hex, text_color=text_c)
            self.update_live_preview()

    def _sync_x_slider(self, val):
        self.ent_x.delete(0, "end")
        self.ent_x.insert(0, f"{float(val):.1f}")

    def _sync_x_entry(self, event):
        try:
            val = float(self.ent_x.get())
            if 0 <= val <= 100:
                self.var_x.set(val)
                self.update_live_preview()
        except ValueError: pass

    def _sync_y_slider(self, val):
        self.ent_y.delete(0, "end")
        self.ent_y.insert(0, f"{float(val):.1f}")

    def _sync_y_entry(self, event):
        try:
            val = float(self.ent_y.get())
            if 0 <= val <= 100:
                self.var_y.set(val)
                self.update_live_preview()
        except ValueError: pass

    def create_preview_label(self):
        if hasattr(self, 'lbl_large_preview') and self.lbl_large_preview:
            self.canvas.delete(self.canvas_window)
            self.lbl_large_preview.destroy()
            
        self.lbl_large_preview = ctk.CTkLabel(self.canvas, text=get_text("msg_adv_info"), font=ctk.CTkFont(size=14), text_color="gray")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.lbl_large_preview, anchor="center")
        self.lbl_large_preview.bind("<MouseWheel>", self._on_mousewheel)
        self.center_canvas_content()

    def _toggle_page_entry(self):
        state = "disabled" if self.var_all_pages.get() else "normal"
        self.ent_pages.configure(state=state)
        self.update_live_preview()

    def get_color_tuple(self, color_name):
        c_map = {
            get_text("opt_color_black"): (0, 0, 0), get_text("opt_txt_black"): (0, 0, 0),
            get_text("opt_txt_white"): (1, 1, 1), get_text("opt_color_gray"): (0.6, 0.6, 0.6),
            get_text("opt_color_red"): (0.8, 0.1, 0.1), get_text("opt_txt_red"): (0.8, 0.1, 0.1),
            get_text("opt_color_blue"): (0.1, 0.3, 0.8), get_text("opt_txt_blue"): (0.1, 0.3, 0.8),
            get_text("opt_color_transparent"): None
        }
        return c_map.get(color_name, (0,0,0))

    def get_turkish_font(self, page, font_family, is_bold=False, is_italic=False):
        if sys.platform == "win32":
            f_path = ""
            if font_family == "Arial": f_path = f"C:/Windows/Fonts/arial{'bi' if is_bold and is_italic else 'bd' if is_bold else 'i' if is_italic else ''}.ttf"
            elif font_family == "Times New Roman": f_path = f"C:/Windows/Fonts/times{'bi' if is_bold and is_italic else 'bd' if is_bold else 'i' if is_italic else ''}.ttf"
            elif font_family == "Courier": f_path = f"C:/Windows/Fonts/cour{'bi' if is_bold and is_italic else 'bd' if is_bold else 'i' if is_italic else ''}.ttf"
            elif font_family == "Comic Sans": f_path = f"C:/Windows/Fonts/comic{'bd' if is_bold else ''}.ttf"
            
            if os.path.exists(f_path):
                font_key = f"cus_{font_family[:3]}_{'b' if is_bold else ''}{'i' if is_italic else ''}"
                try: page.insert_font(fontname=font_key, fontfile=f_path); return font_key
                except: pass
        return "hebi" if is_bold and is_italic else "hebo" if is_bold else "heit" if is_italic else "helv"

    def parse_page_ranges(self, range_str, max_pages):
        if self.var_all_pages.get(): return list(range(max_pages))
        if not range_str: return []
        pages = set()
        for part in range_str.split(','):
            part = part.strip()
            if '-' in part:
                try: s, e = map(int, part.split('-')); pages.update(range(s-1, e))
                except: continue
            else:
                try: pages.add(int(part)-1)
                except: continue
        return [p for p in pages if 0 <= p < max_pages]


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
            if not pw or not doc.authenticate(pw): messagebox.showerror("Hata", "Yanlış Şifre!"); doc.close(); return
        
        self.total_pages = len(doc)
        doc.close()
        
        self.current_pdf_path = path
        self.current_password = pw
        self.current_page_index = 0
        
        self.nav_bar.pack(fill="x", pady=5)
        self.btn_save.configure(state="normal")
        self.update_live_preview()

    # --- ÖNİZLEME MOTORU ---
    def load_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if not path: return
        self.clear_all()
        
        doc = fitz.open(path)
        pw = ""
        if doc.is_encrypted:
            dialog = PasswordDialog(self.winfo_toplevel(), get_text("dialog_warning"), f"'{os.path.basename(path)}' şifreli. Şifreyi girin:")
            pw = dialog.get_result()
            if not pw or not doc.authenticate(pw): messagebox.showerror("Hata", "Yanlış Şifre!"); doc.close(); return
        
        self.total_pages = len(doc)
        doc.close()
        
        self.current_pdf_path = path
        self.current_password = pw
        self.current_page_index = 0
        
        self.nav_bar.pack(fill="x", pady=5)
        self.btn_save.configure(state="normal")
        self.update_live_preview()

    def update_live_preview(self):
        if not self.current_pdf_path: return
        
        target_pages = self.parse_page_ranges(self.ent_pages.get(), self.total_pages)
        
        is_regex = (get_text("opt_redact_regex") == self.var_redact_type.get())
        raw_redact = self.txt_redact.get("1.0", "end").strip()
        wipe_data = self.var_wipe_data.get()
        box_color = self.get_color_tuple(self.var_color_name.get())
        
        free_text = self.ent_free_text.get().strip()
        pos_x = self.var_x.get()
        pos_y = self.var_y.get()
        
        # OLUMLU DÜZELTME: Renk, Opacity ve Rotation Değerlerini Thread'e Aktar
        txt_op = self.slider_txt_opacity.get()
        txt_rot = self.var_txt_rot.get()
        
        if self.custom_txt_color_rgb:
            text_color = self.custom_txt_color_rgb
        else:
            text_color = self.get_color_tuple(self.var_txt_color.get())
            if text_color is None: text_color = (0,0,0)
            
        font_family = self.var_font_family.get()
        try: font_size = int(self.var_txt_size.get())
        except: font_size = 24
        
        style_val = self.var_txt_style.get()
        is_b = (style_val in [get_text("opt_bold"), get_text("opt_bold_italic")])
        is_i = (style_val in [get_text("opt_italic"), get_text("opt_bold_italic")])
        
        threading.Thread(target=self._thread_render_page, args=(raw_redact, is_regex, box_color, text_color, free_text, font_family, font_size, is_b, is_i, pos_x, pos_y, target_pages, wipe_data, txt_op, txt_rot), daemon=True).start()

    def _thread_render_page(self, raw_redact, is_regex, box_color, text_color, free_text, font_family, font_size, is_b, is_i, pos_x, pos_y, target_pages, wipe_data, txt_op, txt_rot):
        try:
            doc = fitz.open(self.current_pdf_path)
            if doc.is_encrypted: doc.authenticate(self.current_password)
            page = doc.load_page(self.current_page_index)

            if self.current_page_index in target_pages:
                
                if raw_redact:
                    rects_to_process = []
                    patterns = [x.strip() for x in raw_redact.split(',') if x.strip()]
                    
                    if is_regex:
                        try:
                            words = page.get_text("words")
                            full_text = page.get_text("text") 
                            for pat in patterns:
                                for match in re.finditer(pat, full_text):
                                    matched_str = match.group().strip()
                                    if len(matched_str) > 0: rects_to_process.extend(page.search_for(matched_str))
                                for w in words:
                                    if re.search(pat, w[4]): rects_to_process.append(fitz.Rect(w[:4]))
                        except: pass
                    else:
                        for kw in patterns: rects_to_process.extend(page.search_for(kw))
                    
                    rects_to_process = list(set(rects_to_process))
                    
                    if wipe_data:
                        for rect in rects_to_process: page.add_redact_annot(rect, fill=box_color, cross_out=False)
                        page.apply_redactions() 
                    else:
                        if box_color is not None:
                            for rect in rects_to_process: page.draw_rect(rect, color=box_color, fill=box_color, overlay=True)

                if free_text:
                    font_name = self.get_turkish_font(page, font_family, is_b, is_i)
                    x_px = page.rect.width * (pos_x / 100.0)
                    y_px = page.rect.height * (pos_y / 100.0)
                    
                    try: 
                        # OLUMLU DÜZELTME: Opacity ve Rotation Matrisi Entegrasyonu
                        tw = fitz.Font("hebo" if is_b else "helv").text_length(free_text.split('\n')[0], fontsize=font_size)
                        center_pt = fitz.Point(x_px + tw/2, y_px - font_size/2)
                        mat = fitz.Matrix(-txt_rot)
                        page.insert_text(fitz.Point(x_px, y_px), free_text, color=text_color, fontname=font_name, fontsize=font_size, fill_opacity=txt_op, morph=(center_pt, mat))
                    except: pass
            
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
        def _do_center():
            cw = self.canvas.winfo_width()
            ch = self.canvas.winfo_height()
            
            if cw <= 1 or ch <= 1: 
                self.after(50, _do_center)
                return
                
            iw = self.lbl_large_preview.winfo_reqwidth()
            ih = self.lbl_large_preview.winfo_reqheight()
            
            x = cw / 2 if cw > iw else iw / 2
            y = ch / 2 if ch > ih else ih / 2
            
            self.canvas.coords(self.canvas_window, x, y)
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        self.after(20, _do_center)

    def _on_mousewheel(self, event): self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    def prev_page(self): self.current_page_index -= 1; self.update_live_preview()
    def next_page(self): self.current_page_index += 1; self.update_live_preview()

    def clear_all(self):
        self.current_pdf_path = None
        self.current_password = ""
        self.current_page_index = 0
        self.total_pages = 0
        self.base_high_res_image = None
        
        self.create_preview_label()
        self.canvas.bind("<Configure>", self.center_canvas_content)
        
        self.nav_bar.pack_forget()
        self.btn_save.configure(state="disabled")

    # --- NÜKLEER KAYIT SÜRECİ ---
    def start_save_process(self):
        raw_redact = self.txt_redact.get("1.0", "end").strip()
        free_text = self.ent_free_text.get().strip()
        
        if not raw_redact and not free_text: 
            messagebox.showwarning("Uyarı", "Lütfen karartılacak veya eklenecek bir metin girin."); return
        
        target_pages = self.parse_page_ranges(self.ent_pages.get(), self.total_pages)
        if not target_pages: messagebox.showwarning("Uyarı", "Lütfen geçerli bir sayfa numarası girin."); return

        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], initialfile="Islem_Yapilmis_Belge.pdf")
        if not save_path: return
        
        is_regex = (get_text("opt_redact_regex") == self.var_redact_type.get())
        wipe_data = self.var_wipe_data.get()
        box_color = self.get_color_tuple(self.var_color_name.get())
        
        txt_op = self.slider_txt_opacity.get()
        txt_rot = self.var_txt_rot.get()
        
        if self.custom_txt_color_rgb:
            text_color = self.custom_txt_color_rgb
        else:
            text_color = self.get_color_tuple(self.var_txt_color.get())
            if text_color is None: text_color = (0,0,0)
        
        font_family = self.var_font_family.get()
        try: font_size = int(self.var_txt_size.get())
        except: font_size = 24
        
        style_val = self.var_txt_style.get()
        is_b = (style_val in [get_text("opt_bold"), get_text("opt_bold_italic")])
        is_i = (style_val in [get_text("opt_italic"), get_text("opt_bold_italic")])
        
        pos_x = self.var_x.get()
        pos_y = self.var_y.get()

        prog_win = ProgressWindow(self.winfo_toplevel(), "Belge İşleniyor...")
        center_window(prog_win, self.winfo_toplevel())
        self.progress = prog_win

        threading.Thread(target=self._thread_actual_redact, args=(save_path, raw_redact, is_regex, box_color, text_color, free_text, font_family, font_size, is_b, is_i, pos_x, pos_y, target_pages, wipe_data, txt_op, txt_rot), daemon=True).start()

    def _thread_actual_redact(self, save_path, raw_redact, is_regex, box_color, text_color, free_text, font_family, font_size, is_b, is_i, pos_x, pos_y, target_pages, wipe_data, txt_op, txt_rot):
        try:
            doc = fitz.open(self.current_pdf_path)
            if doc.is_encrypted: doc.authenticate(self.current_password)
            
            for p_idx in target_pages:
                # Her sayfa sansürlenirken yüklenme kutusunun donmasını engelle
                if hasattr(self, 'progress') and self.progress.winfo_exists():
                    self.progress.update()

                page = doc.load_page(p_idx)
                
                if raw_redact:
                    rects_to_process = []
                    patterns = [x.strip() for x in raw_redact.split(',') if x.strip()]
                    
                    if is_regex:
                        try:
                            words = page.get_text("words")
                            full_text = page.get_text("text")
                            for pat in patterns:
                                for match in re.finditer(pat, full_text):
                                    matched_str = match.group().strip()
                                    if len(matched_str) > 0: rects_to_process.extend(page.search_for(matched_str))
                                for w in words:
                                    if re.search(pat, w[4]): rects_to_process.append(fitz.Rect(w[:4]))
                        except: pass
                    else:
                        for kw in patterns: rects_to_process.extend(page.search_for(kw))
                    
                    rects_to_process = list(set(rects_to_process))
                    
                    if wipe_data:
                        for rect in rects_to_process: page.add_redact_annot(rect, fill=box_color, cross_out=False)
                        page.apply_redactions()
                    else:
                        if box_color is not None:
                            for rect in rects_to_process: page.draw_rect(rect, color=box_color, fill=box_color, overlay=True)

                if free_text:
                    font_name = self.get_turkish_font(page, font_family, is_b, is_i)
                    x_px = page.rect.width * (pos_x / 100.0)
                    y_px = page.rect.height * (pos_y / 100.0)
                    try: 
                        tw = fitz.Font("hebo" if is_b else "helv").text_length(free_text.split('\n')[0], fontsize=font_size)
                        center_pt = fitz.Point(x_px + tw/2, y_px - font_size/2)
                        mat = fitz.Matrix(-txt_rot)
                        page.insert_text(fitz.Point(x_px, y_px), free_text, color=text_color, fontname=font_name, fontsize=font_size, fill_opacity=txt_op, morph=(center_pt, mat))
                    except: pass
            
            # --- UYAP UYUMLULUK VE GÜVENLİK ENTEGRASYONU ---
            # 1. Eklenen bağımsız metinlerin veya gizlenen sansür katmanlarının imza yapısını bozmaması için düzleştiriyoruz
            try:
                for page in doc:
                    page.flatten_widgets()
            except: pass

            # 2. Yerel bilgisayar adını ve gizli dosya yollarını (Geçersiz Yol Hatasını) temizlemek için meta veriyi uçuruyoruz
            doc.set_metadata({})
            try: doc.set_xml_metadata("")
            except: pass

            # 3. Kaydetme sorununa yol açacak linear=True parametresini eklemeden derin temizlikle (garbage=4) kaydediyoruz
            doc.save(
                save_path, 
                deflate=True,
                garbage=4, 
                clean=True
            )
            doc.close()

            from modules.history_manager import add_history
            add_history("🛡️", "history_action_kvkk", [os.path.basename(self.current_pdf_path), os.path.basename(save_path)], save_path)
            
            def on_success():
                dialog = ActionDialog(self.winfo_toplevel(), get_text("dialog_success"), get_text("msg_redact_success"), save_path)
                center_window(dialog, self.winfo_toplevel())
                
            self.after(0, on_success)
        except Exception as e: self.after(0, lambda: messagebox.showerror("Hata", str(e)))
        finally: self.after(0, self.progress.destroy)