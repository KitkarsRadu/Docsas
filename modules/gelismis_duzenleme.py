import customtkinter as ctk
from tkinter import filedialog, messagebox, Canvas, colorchooser
from PIL import Image, ImageOps
import fitz  
import os
import sys
import io
import threading
from modules.pdf_araclari import PasswordDialog, ProgressWindow, ActionDialog
from modules.language_manager import get_text, lang_manager
from modules.history_manager import add_history

class GelismisDuzenlemeSayfasi(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        
        self.current_pdf_path = None
        self.current_password = ""
        self.current_page_index = 0
        self.total_pages = 0
        
        self.zoom_factor = 1.0
        self.base_high_res_image = None
        self.sig_image_path = ""
        self.custom_wm_color_rgb = None
        
        # Dil değişimlerinde sekmelerin çökmesini önleyen anahtar isimler
        self.tab_wm_name = get_text("tab_watermark")
        self.tab_sig_name = get_text("tab_signature")
        self.tab_pn_name = get_text("tab_page_num")
        self.tab_meta_name = get_text("tab_metadata")
        
        self.setup_ui()
        self.update_language()

    def setup_ui(self):
        # 1. KİLİT NOKTASI: Sağ menüyü her iki dil için ideal ve SABİT (450px) hale getiriyoruz
        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=0, minsize=480) 
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # --- SOL TARAF: CANLI DEV ÖNİZLEME ALANI ---
        # ==========================================
        self.left_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        top_bar = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 10))
        
        # 2. KİLİT NOKTASI: Üst Butonların "width" değerleri her dile yetecek kadar büyük ve sabit.
        self.btn_select_pdf = ctk.CTkButton(top_bar, text=get_text("lbl_select_pdf_adv"), font=ctk.CTkFont(weight="bold"), 
                      fg_color="#F57C00", hover_color="#E65100", command=self.load_pdf, width=180)
        self.btn_select_pdf.pack(side="left", padx=5)
                      
        self.btn_clear = ctk.CTkButton(top_bar, text=get_text("btn_clear"), width=100, fg_color="transparent", border_width=1, border_color=("gray60", "gray40"), text_color=("black", "white"), text_color_disabled=("gray50", "gray60"), hover_color=("gray85", "gray25"), command=self.clear_all)
        self.btn_clear.pack(side="left", padx=5)
        
        self.btn_zoom_in = ctk.CTkButton(top_bar, text=get_text("btn_zoom_in"), width=110, fg_color=("gray75", "gray30"), hover_color=("gray65", "gray20"), text_color=("black", "white"), text_color_disabled=("gray50", "gray60"), command=lambda: self.change_zoom(0.2))
        self.btn_zoom_in.pack(side="right", padx=2)
        
        self.btn_fit = ctk.CTkButton(top_bar, text=get_text("btn_fit"), width=100, fg_color=("gray75", "gray30"), hover_color=("gray65", "gray20"), text_color=("black", "white"), text_color_disabled=("gray50", "gray60"), command=lambda: self.change_zoom("fit"))
        self.btn_fit.pack(side="right", padx=2)
        
        self.btn_zoom_out = ctk.CTkButton(top_bar, text=get_text("btn_zoom_out"), width=110, fg_color=("gray75", "gray30"), hover_color=("gray65", "gray20"), text_color=("black", "white"), text_color_disabled=("gray50", "gray60"), command=lambda: self.change_zoom(-0.2))
        self.btn_zoom_out.pack(side="right", padx=2)

        self.preview_container = ctk.CTkFrame(self.left_frame, fg_color=("gray90", "gray15"))
        self.preview_container.pack(fill="both", expand=True, pady=(10, 0))

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

        self.nav_bar = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        
        # 3. KİLİT NOKTASI: Alt sayfa geçiş butonlarının genişliği sabit.
        self.btn_prev = ctk.CTkButton(self.nav_bar, text=get_text("btn_prev_page"), width=120, fg_color="gray40", command=self.prev_page)
        self.btn_prev.pack(side="left", padx=10)
        self.lbl_page_info = ctk.CTkLabel(self.nav_bar, text="", font=ctk.CTkFont(weight="bold", size=14))
        self.lbl_page_info.pack(side="left", expand=True)
        self.btn_next = ctk.CTkButton(self.nav_bar, text=get_text("btn_next_page"), width=120, fg_color="gray40", command=self.next_page)
        self.btn_next.pack(side="right", padx=10)

        self.nav_bar.pack_forget()
        self.btn_zoom_in.configure(state="disabled")
        self.btn_zoom_out.configure(state="disabled")
        self.btn_fit.configure(state="disabled")
        self.btn_clear.configure(state="disabled")

        # ==========================================
        # --- SAĞ TARAF: DÜZENLEME ARAÇLARI ---
        # ==========================================
        self.right_frame = ctk.CTkFrame(self, width=480)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        # 4. KİLİT NOKTASI: İçeriğin dış çerçeveyi büyütmesini kesin olarak engeller.
        self.right_frame.pack_propagate(False)

        self.tabview = ctk.CTkTabview(self.right_frame)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=(10, 5))

        self.tab_watermark = self.tabview.add(self.tab_wm_name)
        self.tab_signature = self.tabview.add(self.tab_sig_name)
        self.tab_pagenum = self.tabview.add(self.tab_pn_name)
        self.tab_metadata = self.tabview.add(self.tab_meta_name)

        self.setup_watermark_tab()
        self.setup_signature_tab()
        self.setup_pagenum_tab()
        self.setup_metadata_tab()

        self.btn_apply_and_save = ctk.CTkButton(self.right_frame, text=get_text("btn_apply_and_save"), 
                                                font=ctk.CTkFont(size=16, weight="bold"), height=55, 
                                                fg_color="#2E7D32", hover_color="#1B5E20", command=self.start_unified_save)
        self.btn_apply_and_save.pack(side="bottom", fill="x", padx=10, pady=10)
        self.btn_apply_and_save.configure(state="disabled")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def create_preview_label(self):
        if hasattr(self, 'lbl_large_preview') and self.lbl_large_preview:
            self.canvas.delete(self.canvas_window)
            self.lbl_large_preview.destroy()
            
        self.lbl_large_preview = ctk.CTkLabel(self.canvas, text=get_text("msg_adv_info"), font=ctk.CTkFont(size=14), text_color="gray")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.lbl_large_preview, anchor="center")
        self.lbl_large_preview.bind("<MouseWheel>", self._on_mousewheel)
        self.center_canvas_content()

    # ==========================================
    # --- MİLİMETRİK KOORDİNAT SENKRONİZASYONLARI ---
    # ==========================================
    def _sync_wm_x_slider(self, val): self.ent_wm_x.delete(0, "end"); self.ent_wm_x.insert(0, f"{float(val):.1f}")
    def _sync_wm_x_entry(self, event):
        try:
            v = float(self.ent_wm_x.get())
            if 0 <= v <= 100: self.var_wm_x.set(v); self.update_live_preview()
        except: pass

    def _sync_wm_y_slider(self, val): self.ent_wm_y.delete(0, "end"); self.ent_wm_y.insert(0, f"{float(val):.1f}")
    def _sync_wm_y_entry(self, event):
        try:
            v = float(self.ent_wm_y.get())
            if 0 <= v <= 100: self.var_wm_y.set(v); self.update_live_preview()
        except: pass

    def _sync_sig_x_slider(self, val): self.ent_sig_x.delete(0, "end"); self.ent_sig_x.insert(0, f"{float(val):.1f}")
    def _sync_sig_x_entry(self, event):
        try:
            v = float(self.ent_sig_x.get())
            if 0 <= v <= 100: self.var_sig_x.set(v); self.update_live_preview()
        except: pass

    def _sync_sig_y_slider(self, val): self.ent_sig_y.delete(0, "end"); self.ent_sig_y.insert(0, f"{float(val):.1f}")
    def _sync_sig_y_entry(self, event):
        try:
            v = float(self.ent_sig_y.get())
            if 0 <= v <= 100: self.var_sig_y.set(v); self.update_live_preview()
        except: pass

    def _sync_pn_x_slider(self, val): self.ent_pn_x.delete(0, "end"); self.ent_pn_x.insert(0, f"{float(val):.1f}")
    def _sync_pn_x_entry(self, event):
        try:
            v = float(self.ent_pn_x.get())
            if 0 <= v <= 100: self.var_pn_x.set(v); self.update_live_preview()
        except: pass

    def _sync_pn_y_slider(self, val): self.ent_pn_y.delete(0, "end"); self.ent_pn_y.insert(0, f"{float(val):.1f}")
    def _sync_pn_y_entry(self, event):
        try:
            v = float(self.ent_pn_y.get())
            if 0 <= v <= 100: self.var_pn_y.set(v); self.update_live_preview()
        except: pass

    # ==========================================
    # --- YARDIMCI FONKSİYONLAR ---
    # ==========================================
    def get_turkish_font(self, page, is_bold=False, is_italic=False):
        if sys.platform == "win32":
            base_dir = "C:/Windows/Fonts/"
            if is_bold and is_italic: font_file = base_dir + "arialbi.ttf"
            elif is_bold: font_file = base_dir + "arialbd.ttf"
            elif is_italic: font_file = base_dir + "ariali.ttf"
            else: font_file = base_dir + "arial.ttf"
            if os.path.exists(font_file):
                font_key = f"tr_{'b' if is_bold else ''}{'i' if is_italic else ''}"
                try: page.insert_font(fontname=font_key, fontfile=font_file); return font_key
                except: pass
        if is_bold and is_italic: return "hebi"
        if is_bold: return "hebo"
        if is_italic: return "heit"
        return "helv"

    def select_signature_image(self):
        path = filedialog.askopenfilename(filetypes=[("Resim Formatları", "*.png *.jpg *.jpeg")])
        if path: 
            self.sig_image_path = path
            self.lbl_sig_file.configure(text=os.path.basename(path))
            self.update_live_preview()

    def toggle_page_entry(self, chk_var, entry_widget):
        state = "disabled" if chk_var.get() else "normal"
        entry_widget.configure(state=state)
        self.update_live_preview()

    def apply_preset_position(self, pos_str, var_x, var_y, ent_x, ent_y):
        presets = {
            get_text("opt_pos_tl"): (5.0, 5.0), get_text("opt_pos_tc"): (50.0, 5.0), get_text("opt_pos_tr"): (95.0, 5.0),
            get_text("opt_pos_ml"): (5.0, 50.0), get_text("opt_pos_mc"): (50.0, 50.0), get_text("opt_pos_mr"): (95.0, 50.0),
            get_text("opt_pos_bl"): (5.0, 95.0), get_text("opt_pos_bc"): (50.0, 95.0), get_text("opt_pos_br"): (95.0, 95.0),
        }
        if pos_str in presets:
            x, y = presets[pos_str]
            var_x.set(x); var_y.set(y)
            ent_x.delete(0, "end"); ent_x.insert(0, str(x))
            ent_y.delete(0, "end"); ent_y.insert(0, str(y))
            self.update_live_preview()

    def apply_wm_pos_preset(self, pos_str):
        presets = {
            get_text("opt_wm_mc"): (50.0, 50.0, 0.0), get_text("opt_wm_bc"): (50.0, 90.0, 0.0), get_text("opt_wm_tc"): (50.0, 10.0, 0.0),
            get_text("opt_wm_lv"): (10.0, 50.0, 90.0), get_text("opt_wm_rv"): (90.0, 50.0, -90.0), get_text("opt_wm_cv"): (50.0, 50.0, 90.0),
        }
        if pos_str in presets:
            x, y, rot = presets[pos_str]
            self.var_wm_x.set(x); self.var_wm_y.set(y)
            self.var_wm_rot.set(rot)
            self.ent_wm_rot.delete(0, "end"); self.ent_wm_rot.insert(0, str(rot))
            self.ent_wm_x.delete(0, "end"); self.ent_wm_x.insert(0, str(x))
            self.ent_wm_y.delete(0, "end"); self.ent_wm_y.insert(0, str(y))
            self.update_live_preview()

    def apply_wm_text_preset(self, selected):
        if selected == get_text("opt_custom_text"): return
        self.entry_wm_text.delete("1.0", 'end'); self.entry_wm_text.insert("1.0", selected)
        if selected in [get_text("wm_t1"), get_text("wm_t5"), get_text("wm_t6")]: 
            self._on_wm_color_preset(get_text("opt_color_red")); self.var_wm_color.set(get_text("opt_color_red")); self.var_wm_rot.set(45.0); self.ent_wm_rot.delete(0, "end"); self.ent_wm_rot.insert(0, "45.0"); self.slider_wm_size.set(110); self.slider_wm_opacity.set(0.3)
        elif selected == get_text("wm_t4"): 
            self._on_wm_color_preset(get_text("opt_color_blue")); self.var_wm_color.set(get_text("opt_color_blue")); self.var_wm_rot.set(0.0); self.ent_wm_rot.delete(0, "end"); self.ent_wm_rot.insert(0, "0.0"); self.slider_wm_size.set(35); self.slider_wm_opacity.set(0.8)
            self.var_wm_x.set(50.0); self.ent_wm_x.delete(0, "end"); self.ent_wm_x.insert(0, "50.0")
            self.var_wm_y.set(85.0); self.ent_wm_y.delete(0, "end"); self.ent_wm_y.insert(0, "85.0")
        elif selected == get_text("wm_t3"): 
            self._on_wm_color_preset(get_text("opt_color_blue")); self.var_wm_color.set(get_text("opt_color_blue")); self.var_wm_rot.set(45.0); self.ent_wm_rot.delete(0, "end"); self.ent_wm_rot.insert(0, "45.0"); self.slider_wm_size.set(90); self.slider_wm_opacity.set(0.4)
        else: 
            self._on_wm_color_preset(get_text("opt_color_gray")); self.var_wm_color.set(get_text("opt_color_gray")); self.var_wm_rot.set(45.0); self.ent_wm_rot.delete(0, "end"); self.ent_wm_rot.insert(0, "45.0"); self.slider_wm_size.set(120); self.slider_wm_opacity.set(0.2)
        self.update_live_preview()

    def apply_pn_template(self, selected):
        templates = {
            get_text("opt_pn_t1"): "{0}", get_text("opt_pn_t2"): "{0} / {1}", get_text("opt_pn_t3"): "{0} - {1}",
            get_text("opt_pn_t4"): "Sayfa {0}", get_text("opt_pn_t5"): "Sayfa {0} / {1}", get_text("opt_pn_t6"): "EK-{0}", get_text("opt_pn_t7"): "[ {0} ]"
        }
        if selected in templates:
            self.entry_pn_format.delete(0, 'end'); self.entry_pn_format.insert(0, templates[selected]); self.update_live_preview()

    def _on_wm_color_preset(self, val):
        self.custom_wm_color_rgb = None
        self.btn_wm_custom_color.configure(fg_color=("gray75", "gray30"), text_color=("black", "white"))
        self.update_live_preview()

    def pick_wm_custom_color(self):
        color_data = colorchooser.askcolor(title="Renk Seç")
        if color_data and color_data[0]:
            r, g, b = color_data[0]
            self.custom_wm_color_rgb = (r/255.0, g/255.0, b/255.0)
            self.var_wm_color.set("") 
            
            fg_hex = color_data[1]
            text_c = "white" if (r*0.299 + g*0.587 + b*0.114) < 186 else "black"
            self.btn_wm_custom_color.configure(fg_color=fg_hex, text_color=text_c)
            self.update_live_preview()

    # ==========================================
    # --- SEKMELERİN İNŞASI (TÜMÜ SELF KİMLİKLİ) ---
    # ==========================================
    def setup_watermark_tab(self):
        self.scroll_wm = ctk.CTkScrollableFrame(self.tab_watermark, fg_color="transparent")
        self.scroll_wm.pack(fill="both", expand=True)
        
        self.var_enable_wm = ctk.BooleanVar(value=False)
        self.chk_enable_wm = ctk.CTkCheckBox(self.scroll_wm, text=get_text("chk_enable_wm"), variable=self.var_enable_wm, font=ctk.CTkFont(weight="bold"), command=self.update_live_preview)
        self.chk_enable_wm.pack(pady=(10, 10), anchor="w", padx=10)
        
        self.var_wm_behind = ctk.BooleanVar(value=False)
        self.chk_wm_behind = ctk.CTkCheckBox(self.scroll_wm, text=get_text("chk_wm_behind"), variable=self.var_wm_behind, font=ctk.CTkFont(size=11), command=self.update_live_preview)
        self.chk_wm_behind.pack(anchor="w", padx=10, pady=(0,15))
        
        self.var_wm_all_pages = ctk.BooleanVar(value=True)
        self.chk_wm_all_pages = ctk.CTkCheckBox(self.scroll_wm, text=get_text("chk_all_pages"), variable=self.var_wm_all_pages, command=lambda: self.toggle_page_entry(self.var_wm_all_pages, self.entry_wm_pages))
        self.chk_wm_all_pages.pack(anchor="w", padx=10, pady=(0, 5))
        
        self.entry_wm_pages = ctk.CTkEntry(self.scroll_wm, placeholder_text=get_text("lbl_custom_pages"))
        self.entry_wm_pages.pack(fill="x", padx=10, pady=(0,10)); self.entry_wm_pages.configure(state="disabled")
        self.entry_wm_pages.bind("<KeyRelease>", lambda e: self.update_live_preview())
        
        self.lbl_wm_preset_text = ctk.CTkLabel(self.scroll_wm, text=get_text("lbl_wm_preset_text"), anchor="w")
        self.lbl_wm_preset_text.pack(fill="x", padx=10, pady=(5,0))
        
        opts_wm_tmpl = [get_text("opt_custom_text"), get_text("wm_t1"), get_text("wm_t2"), get_text("wm_t3"), get_text("wm_t4"), get_text("wm_t5"), get_text("wm_t6"), get_text("wm_t7")]
        self.var_wm_template = ctk.StringVar(value=get_text("opt_custom_text"))
        self.opt_wm_template = ctk.CTkOptionMenu(self.scroll_wm, values=opts_wm_tmpl, variable=self.var_wm_template, command=self.apply_wm_text_preset)
        self.opt_wm_template.pack(fill="x", padx=10, pady=5)
        
        self.lbl_wm_text_title = ctk.CTkLabel(self.scroll_wm, text=get_text("lbl_wm_text"), anchor="w")
        self.lbl_wm_text_title.pack(fill="x", padx=10)
        self.entry_wm_text = ctk.CTkTextbox(self.scroll_wm, height=70)
        self.entry_wm_text.pack(fill="x", padx=10, pady=5); self.entry_wm_text.bind("<KeyRelease>", lambda e: self.update_live_preview())
        
        self.lbl_wm_color_title = ctk.CTkLabel(self.scroll_wm, text=get_text("lbl_wm_color"), anchor="w")
        self.lbl_wm_color_title.pack(fill="x", padx=10, pady=(5,0))
        
        color_frame = ctk.CTkFrame(self.scroll_wm, fg_color="transparent")
        color_frame.pack(fill="x", padx=10, pady=5)
        self.var_wm_color = ctk.StringVar(value=get_text("opt_color_gray"))
        opts_color = [get_text("opt_color_gray"), get_text("opt_color_red"), get_text("opt_color_blue"), get_text("opt_color_black")]
        self.seg_color = ctk.CTkSegmentedButton(color_frame, values=opts_color, variable=self.var_wm_color, command=self._on_wm_color_preset)
        self.seg_color.pack(side="left", fill="x", expand=True)
        self.btn_wm_custom_color = ctk.CTkButton(color_frame, text="🎨", width=40, font=ctk.CTkFont(size=18), fg_color=("gray75", "gray30"), text_color=("black", "white"), command=self.pick_wm_custom_color)
        self.btn_wm_custom_color.pack(side="right", padx=(5,0))

        self.lbl_wm_pos_preset_title = ctk.CTkLabel(self.scroll_wm, text=get_text("lbl_wm_pos_preset"), anchor="w")
        self.lbl_wm_pos_preset_title.pack(fill="x", padx=10, pady=(10,0))
        opts_pos = [get_text("opt_wm_mc"), get_text("opt_wm_bc"), get_text("opt_wm_tc"), get_text("opt_wm_lv"), get_text("opt_wm_rv"), get_text("opt_wm_cv")]
        self.var_wm_pos_preset = ctk.StringVar(value=get_text("opt_wm_mc"))
        self.opt_wm_pos_preset = ctk.CTkOptionMenu(self.scroll_wm, values=opts_pos, variable=self.var_wm_pos_preset, command=self.apply_wm_pos_preset)
        self.opt_wm_pos_preset.pack(fill="x", padx=10, pady=5)

        # MİLİMETRİK X EKSENİ (FİLİGRAN)
        frame_wm_x = ctk.CTkFrame(self.scroll_wm, fg_color="transparent")
        frame_wm_x.pack(fill="x", padx=10, pady=(5, 0))
        self.lbl_wm_x_title = ctk.CTkLabel(frame_wm_x, text=get_text("lbl_pos_x"), font=ctk.CTkFont(size=11, weight="bold"), width=100, anchor="w", text_color="#1976D2")
        self.lbl_wm_x_title.pack(side="left")
        self.var_wm_x = ctk.DoubleVar(value=50.0)
        self.slider_wm_x = ctk.CTkSlider(frame_wm_x, from_=0, to=100, number_of_steps=1000, variable=self.var_wm_x, command=self._sync_wm_x_slider)
        self.slider_wm_x.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.slider_wm_x.bind("<ButtonRelease-1>", lambda e: self.update_live_preview())
        self.ent_wm_x = ctk.CTkEntry(frame_wm_x, width=50, height=25)
        self.ent_wm_x.pack(side="right")
        self.ent_wm_x.insert(0, "50.0")
        self.ent_wm_x.bind("<KeyRelease>", self._sync_wm_x_entry)
        
        # MİLİMETRİK Y EKSENİ (FİLİGRAN)
        frame_wm_y = ctk.CTkFrame(self.scroll_wm, fg_color="transparent")
        frame_wm_y.pack(fill="x", padx=10, pady=(5, 5))
        self.lbl_wm_y_title = ctk.CTkLabel(frame_wm_y, text=get_text("lbl_pos_y"), font=ctk.CTkFont(size=11, weight="bold"), width=100, anchor="w", text_color="#1976D2")
        self.lbl_wm_y_title.pack(side="left")
        self.var_wm_y = ctk.DoubleVar(value=50.0)
        self.slider_wm_y = ctk.CTkSlider(frame_wm_y, from_=0, to=100, number_of_steps=1000, variable=self.var_wm_y, command=self._sync_wm_y_slider)
        self.slider_wm_y.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.slider_wm_y.bind("<ButtonRelease-1>", lambda e: self.update_live_preview())
        self.ent_wm_y = ctk.CTkEntry(frame_wm_y, width=50, height=25)
        self.ent_wm_y.pack(side="right")
        self.ent_wm_y.insert(0, "50.0")
        self.ent_wm_y.bind("<KeyRelease>", self._sync_wm_y_entry)

        # FİLİGRAN ROTASYON
        self.lbl_wm_rot_title = ctk.CTkLabel(self.scroll_wm, text=get_text("lbl_wm_rot"), anchor="w")
        self.lbl_wm_rot_title.pack(fill="x", padx=10, pady=(10,0))
        f_wm_rot = ctk.CTkFrame(self.scroll_wm, fg_color="transparent")
        f_wm_rot.pack(fill="x", padx=10, pady=5)
        self.var_wm_rot = ctk.DoubleVar(value=45.0)
        self.ent_wm_rot = ctk.CTkEntry(f_wm_rot, width=50, height=25)
        self.ent_wm_rot.pack(side="right")
        self.ent_wm_rot.insert(0, "45.0")
        def on_wm_rot_slider(val):
            self.ent_wm_rot.delete(0, "end"); self.ent_wm_rot.insert(0, f"{float(val):.1f}"); self.update_live_preview()
        def on_wm_rot_entry(e):
            try:
                v = float(self.ent_wm_rot.get())
                if -180 <= v <= 180: self.var_wm_rot.set(v); self.update_live_preview()
            except: pass
        self.slider_wm_rot = ctk.CTkSlider(f_wm_rot, from_=-180, to=180, number_of_steps=360, variable=self.var_wm_rot, command=on_wm_rot_slider)
        self.slider_wm_rot.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.ent_wm_rot.bind("<KeyRelease>", on_wm_rot_entry)

        self.lbl_wm_size_title = ctk.CTkLabel(self.scroll_wm, text=get_text("lbl_wm_size"), anchor="w")
        self.lbl_wm_size_title.pack(fill="x", padx=10, pady=(5,0))
        self.slider_wm_size = ctk.CTkSlider(self.scroll_wm, from_=10, to=200, number_of_steps=38, command=lambda v: self.update_live_preview()); self.slider_wm_size.set(100); self.slider_wm_size.pack(fill="x", padx=10, pady=5)
        
        self.lbl_wm_opacity_title = ctk.CTkLabel(self.scroll_wm, text=get_text("lbl_wm_opacity"), anchor="w")
        self.lbl_wm_opacity_title.pack(fill="x", padx=10, pady=(5,0))
        self.slider_wm_opacity = ctk.CTkSlider(self.scroll_wm, from_=0.1, to=1.0, number_of_steps=9, command=lambda v: self.update_live_preview()); self.slider_wm_opacity.set(0.3); self.slider_wm_opacity.pack(fill="x", padx=10, pady=5)

    def setup_signature_tab(self):
        self.scroll_sig = ctk.CTkScrollableFrame(self.tab_signature, fg_color="transparent")
        self.scroll_sig.pack(fill="both", expand=True)
        
        self.var_enable_sig = ctk.BooleanVar(value=False)
        self.chk_enable_sig = ctk.CTkCheckBox(self.scroll_sig, text=get_text("chk_enable_sig"), variable=self.var_enable_sig, font=ctk.CTkFont(weight="bold"), command=self.update_live_preview)
        self.chk_enable_sig.pack(pady=(10, 10), anchor="w", padx=10)
        
        self.var_sig_behind = ctk.BooleanVar(value=False)
        self.chk_sig_behind = ctk.CTkCheckBox(self.scroll_sig, text=get_text("chk_sig_behind"), variable=self.var_sig_behind, font=ctk.CTkFont(size=11), command=self.update_live_preview)
        self.chk_sig_behind.pack(anchor="w", padx=10, pady=(0,15))
        
        self.btn_select_sig = ctk.CTkButton(self.scroll_sig, text=get_text("btn_select_sig"), command=self.select_signature_image)
        self.btn_select_sig.pack(fill="x", padx=10, pady=5)
        self.lbl_sig_file = ctk.CTkLabel(self.scroll_sig, text=get_text("msg_no_sig_selected"), text_color="gray", font=ctk.CTkFont(size=11)); self.lbl_sig_file.pack(padx=10, pady=(0, 10))
        
        self.var_sig_all_pages = ctk.BooleanVar(value=True)
        self.chk_sig_all_pages = ctk.CTkCheckBox(self.scroll_sig, text=get_text("chk_all_pages"), variable=self.var_sig_all_pages, command=lambda: self.toggle_page_entry(self.var_sig_all_pages, self.entry_sig_pages))
        self.chk_sig_all_pages.pack(anchor="w", padx=10, pady=(0, 5))
        
        self.entry_sig_pages = ctk.CTkEntry(self.scroll_sig, placeholder_text=get_text("lbl_custom_pages"))
        self.entry_sig_pages.pack(fill="x", padx=10, pady=(0,10)); self.entry_sig_pages.configure(state="disabled")
        self.entry_sig_pages.bind("<KeyRelease>", lambda e: self.update_live_preview())
        
        self.lbl_sig_scale_title = ctk.CTkLabel(self.scroll_sig, text=get_text("lbl_sig_scale"), anchor="w")
        self.lbl_sig_scale_title.pack(fill="x", padx=10, pady=(5,0))
        self.slider_sig_scale = ctk.CTkSlider(self.scroll_sig, from_=0.1, to=2.0, number_of_steps=19, command=lambda v: self.update_live_preview()); self.slider_sig_scale.set(0.5); self.slider_sig_scale.pack(fill="x", padx=10, pady=5)
        
        self.lbl_sig_opacity_title = ctk.CTkLabel(self.scroll_sig, text=get_text("lbl_sig_opacity"), anchor="w")
        self.lbl_sig_opacity_title.pack(fill="x", padx=10, pady=(5,0))
        self.slider_sig_opacity = ctk.CTkSlider(self.scroll_sig, from_=0.1, to=1.0, number_of_steps=9, command=lambda v: self.update_live_preview()); self.slider_sig_opacity.set(1.0); self.slider_sig_opacity.pack(fill="x", padx=10, pady=5)
        
        self.lbl_sig_preset_pos_title = ctk.CTkLabel(self.scroll_sig, text=get_text("lbl_preset_pos"), anchor="w")
        self.lbl_sig_preset_pos_title.pack(fill="x", padx=10, pady=(10,0))
        opts_pos = [get_text("opt_pos_tl"), get_text("opt_pos_tc"), get_text("opt_pos_tr"), get_text("opt_pos_ml"), get_text("opt_pos_mc"), get_text("opt_pos_mr"), get_text("opt_pos_bl"), get_text("opt_pos_bc"), get_text("opt_pos_br")]
        self.var_sig_pos_preset = ctk.StringVar(value=get_text("opt_pos_br"))
        self.opt_sig_pos_preset = ctk.CTkOptionMenu(self.scroll_sig, values=opts_pos, variable=self.var_sig_pos_preset, command=lambda v: self.apply_preset_position(v, self.var_sig_x, self.var_sig_y, self.ent_sig_x, self.ent_sig_y))
        self.opt_sig_pos_preset.pack(fill="x", padx=10, pady=5)

        # MİLİMETRİK X EKSENİ (İMZA)
        frame_sig_x = ctk.CTkFrame(self.scroll_sig, fg_color="transparent")
        frame_sig_x.pack(fill="x", padx=10, pady=(5, 0))
        self.lbl_sig_x_title = ctk.CTkLabel(frame_sig_x, text=get_text("lbl_pos_x"), font=ctk.CTkFont(size=11, weight="bold"), width=100, anchor="w", text_color="#1976D2")
        self.lbl_sig_x_title.pack(side="left")
        self.var_sig_x = ctk.DoubleVar(value=95.0)
        self.slider_sig_x = ctk.CTkSlider(frame_sig_x, from_=0, to=100, number_of_steps=1000, variable=self.var_sig_x, command=self._sync_sig_x_slider)
        self.slider_sig_x.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.slider_sig_x.bind("<ButtonRelease-1>", lambda e: self.update_live_preview())
        self.ent_sig_x = ctk.CTkEntry(frame_sig_x, width=50, height=25)
        self.ent_sig_x.pack(side="right")
        self.ent_sig_x.insert(0, "95.0")
        self.ent_sig_x.bind("<KeyRelease>", self._sync_sig_x_entry)

        # MİLİMETRİK Y EKSENİ (İMZA)
        frame_sig_y = ctk.CTkFrame(self.scroll_sig, fg_color="transparent")
        frame_sig_y.pack(fill="x", padx=10, pady=(5, 5))
        self.lbl_sig_y_title = ctk.CTkLabel(frame_sig_y, text=get_text("lbl_pos_y"), font=ctk.CTkFont(size=11, weight="bold"), width=100, anchor="w", text_color="#1976D2")
        self.lbl_sig_y_title.pack(side="left")
        self.var_sig_y = ctk.DoubleVar(value=95.0)
        self.slider_sig_y = ctk.CTkSlider(frame_sig_y, from_=0, to=100, number_of_steps=1000, variable=self.var_sig_y, command=self._sync_sig_y_slider)
        self.slider_sig_y.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.slider_sig_y.bind("<ButtonRelease-1>", lambda e: self.update_live_preview())
        self.ent_sig_y = ctk.CTkEntry(frame_sig_y, width=50, height=25)
        self.ent_sig_y.pack(side="right")
        self.ent_sig_y.insert(0, "95.0")
        self.ent_sig_y.bind("<KeyRelease>", self._sync_sig_y_entry)

        # İMZA ROTASYON
        self.lbl_sig_rot_title = ctk.CTkLabel(self.scroll_sig, text=get_text("lbl_wm_rot"), anchor="w")
        self.lbl_sig_rot_title.pack(fill="x", padx=10, pady=(10,0))
        f_sig_rot = ctk.CTkFrame(self.scroll_sig, fg_color="transparent")
        f_sig_rot.pack(fill="x", padx=10, pady=5)
        self.var_sig_rot = ctk.DoubleVar(value=0.0)
        self.ent_sig_rot = ctk.CTkEntry(f_sig_rot, width=50, height=25)
        self.ent_sig_rot.pack(side="right")
        self.ent_sig_rot.insert(0, "0.0")
        def on_sig_rot_slider(val):
            self.ent_sig_rot.delete(0, "end"); self.ent_sig_rot.insert(0, f"{float(val):.1f}"); self.update_live_preview()
        def on_sig_rot_entry(e):
            try:
                v = float(self.ent_sig_rot.get())
                if -180 <= v <= 180: self.var_sig_rot.set(v); self.update_live_preview()
            except: pass
        self.slider_sig_rot = ctk.CTkSlider(f_sig_rot, from_=-180, to=180, number_of_steps=360, variable=self.var_sig_rot, command=on_sig_rot_slider)
        self.slider_sig_rot.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.ent_sig_rot.bind("<KeyRelease>", on_sig_rot_entry)

    def setup_pagenum_tab(self):
        self.scroll_pn = ctk.CTkScrollableFrame(self.tab_pagenum, fg_color="transparent")
        self.scroll_pn.pack(fill="both", expand=True)
        
        self.var_enable_pn = ctk.BooleanVar(value=False)
        self.chk_enable_pn = ctk.CTkCheckBox(self.scroll_pn, text=get_text("chk_enable_pn"), variable=self.var_enable_pn, font=ctk.CTkFont(weight="bold"), command=self.update_live_preview)
        self.chk_enable_pn.pack(pady=(10, 10), anchor="w", padx=10)
        
        self.var_pn_all_pages = ctk.BooleanVar(value=True)
        self.chk_pn_all_pages = ctk.CTkCheckBox(self.scroll_pn, text=get_text("chk_all_pages"), variable=self.var_pn_all_pages, command=lambda: self.toggle_page_entry(self.var_pn_all_pages, self.entry_pn_pages))
        self.chk_pn_all_pages.pack(anchor="w", padx=10, pady=(0, 5))
        
        self.entry_pn_pages = ctk.CTkEntry(self.scroll_pn, placeholder_text=get_text("lbl_custom_pages"))
        self.entry_pn_pages.pack(fill="x", padx=10, pady=(0,10)); self.entry_pn_pages.configure(state="disabled")
        self.entry_pn_pages.bind("<KeyRelease>", lambda e: self.update_live_preview())
        
        self.lbl_pn_template_title = ctk.CTkLabel(self.scroll_pn, text=get_text("lbl_pn_template"), anchor="w")
        self.lbl_pn_template_title.pack(fill="x", padx=10)
        self.var_pn_template = ctk.StringVar(value=get_text("opt_custom_text"))
        opts_tmpl = [get_text("opt_custom_text"), get_text("opt_pn_t1"), get_text("opt_pn_t2"), get_text("opt_pn_t3"), get_text("opt_pn_t4"), get_text("opt_pn_t5"), get_text("opt_pn_t6"), get_text("opt_pn_t7")]
        self.opt_pn_template = ctk.CTkOptionMenu(self.scroll_pn, values=opts_tmpl, variable=self.var_pn_template, command=self.apply_pn_template)
        self.opt_pn_template.pack(fill="x", padx=10, pady=5)
        
        self.lbl_pn_format_title = ctk.CTkLabel(self.scroll_pn, text=get_text("lbl_pn_format"), anchor="w")
        self.lbl_pn_format_title.pack(fill="x", padx=10, pady=(5,0))
        self.entry_pn_format = ctk.CTkEntry(self.scroll_pn); self.entry_pn_format.insert(0, "Sayfa {0} / {1}"); self.entry_pn_format.pack(fill="x", padx=10, pady=5); self.entry_pn_format.bind("<KeyRelease>", lambda e: self.update_live_preview())
        
        self.lbl_pn_start_title = ctk.CTkLabel(self.scroll_pn, text=get_text("lbl_pn_start"), anchor="w")
        self.lbl_pn_start_title.pack(fill="x", padx=10, pady=(5,0))
        self.entry_pn_start = ctk.CTkEntry(self.scroll_pn); self.entry_pn_start.insert(0, "1"); self.entry_pn_start.pack(fill="x", padx=10, pady=5); self.entry_pn_start.bind("<KeyRelease>", lambda e: self.update_live_preview())
        
        self.lbl_font_style_title = ctk.CTkLabel(self.scroll_pn, text=get_text("lbl_font_style"), anchor="w")
        self.lbl_font_style_title.pack(fill="x", padx=10, pady=(5,0))
        self.var_pn_font_style = ctk.StringVar(value=get_text("opt_normal"))
        opts_font = [get_text("opt_normal"), get_text("opt_bold"), get_text("opt_italic"), get_text("opt_bold_italic")]
        self.opt_pn_font_style = ctk.CTkOptionMenu(self.scroll_pn, values=opts_font, variable=self.var_pn_font_style, command=lambda v: self.update_live_preview())
        self.opt_pn_font_style.pack(fill="x", padx=10, pady=5)
        
        self.lbl_pn_preset_pos_title = ctk.CTkLabel(self.scroll_pn, text=get_text("lbl_preset_pos"), anchor="w")
        self.lbl_pn_preset_pos_title.pack(fill="x", padx=10, pady=(10,0))
        opts_pos = [get_text("opt_pos_tl"), get_text("opt_pos_tc"), get_text("opt_pos_tr"), get_text("opt_pos_ml"), get_text("opt_pos_mc"), get_text("opt_pos_mr"), get_text("opt_pos_bl"), get_text("opt_pos_bc"), get_text("opt_pos_br")]
        self.var_pn_pos_preset = ctk.StringVar(value=get_text("opt_pos_bc"))
        self.opt_pn_pos_preset = ctk.CTkOptionMenu(self.scroll_pn, values=opts_pos, variable=self.var_pn_pos_preset, command=lambda v: self.apply_preset_position(v, self.var_pn_x, self.var_pn_y, self.ent_pn_x, self.ent_pn_y))
        self.opt_pn_pos_preset.pack(fill="x", padx=10, pady=5)

        # MİLİMETRİK X EKSENİ (SAYFA NO)
        frame_pn_x = ctk.CTkFrame(self.scroll_pn, fg_color="transparent")
        frame_pn_x.pack(fill="x", padx=10, pady=(5, 0))
        self.lbl_pn_x_title = ctk.CTkLabel(frame_pn_x, text=get_text("lbl_pos_x"), font=ctk.CTkFont(size=11, weight="bold"), width=100, anchor="w", text_color="#1976D2")
        self.lbl_pn_x_title.pack(side="left")
        self.var_pn_x = ctk.DoubleVar(value=50.0)
        self.slider_pn_x = ctk.CTkSlider(frame_pn_x, from_=0, to=100, number_of_steps=1000, variable=self.var_pn_x, command=self._sync_pn_x_slider)
        self.slider_pn_x.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.slider_pn_x.bind("<ButtonRelease-1>", lambda e: self.update_live_preview())
        self.ent_pn_x = ctk.CTkEntry(frame_pn_x, width=50, height=25)
        self.ent_pn_x.pack(side="right")
        self.ent_pn_x.insert(0, "50.0")
        self.ent_pn_x.bind("<KeyRelease>", self._sync_pn_x_entry)

        # MİLİMETRİK Y EKSENİ (SAYFA NO)
        frame_pn_y = ctk.CTkFrame(self.scroll_pn, fg_color="transparent")
        frame_pn_y.pack(fill="x", padx=10, pady=(5, 5))
        self.lbl_pn_y_title = ctk.CTkLabel(frame_pn_y, text=get_text("lbl_pos_y"), font=ctk.CTkFont(size=11, weight="bold"), width=100, anchor="w", text_color="#1976D2")
        self.lbl_pn_y_title.pack(side="left")
        self.var_pn_y = ctk.DoubleVar(value=95.0)
        self.slider_pn_y = ctk.CTkSlider(frame_pn_y, from_=0, to=100, number_of_steps=1000, variable=self.var_pn_y, command=self._sync_pn_y_slider)
        self.slider_pn_y.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.slider_pn_y.bind("<ButtonRelease-1>", lambda e: self.update_live_preview())
        self.ent_pn_y = ctk.CTkEntry(frame_pn_y, width=50, height=25)
        self.ent_pn_y.pack(side="right")
        self.ent_pn_y.insert(0, "95.0")
        self.ent_pn_y.bind("<KeyRelease>", self._sync_pn_y_entry)

        # SAYFA NO ROTASYON
        self.lbl_pn_rot_title = ctk.CTkLabel(self.scroll_pn, text=get_text("lbl_wm_rot"), anchor="w")
        self.lbl_pn_rot_title.pack(fill="x", padx=10, pady=(10,0))
        f_pn_rot = ctk.CTkFrame(self.scroll_pn, fg_color="transparent")
        f_pn_rot.pack(fill="x", padx=10, pady=5)
        self.var_pn_rot = ctk.DoubleVar(value=0.0)
        self.ent_pn_rot = ctk.CTkEntry(f_pn_rot, width=50, height=25)
        self.ent_pn_rot.pack(side="right")
        self.ent_pn_rot.insert(0, "0.0")
        def on_pn_rot_slider(val):
            self.ent_pn_rot.delete(0, "end"); self.ent_pn_rot.insert(0, f"{float(val):.1f}"); self.update_live_preview()
        def on_pn_rot_entry(e):
            try:
                v = float(self.ent_pn_rot.get())
                if -180 <= v <= 180: self.var_pn_rot.set(v); self.update_live_preview()
            except: pass
        self.slider_pn_rot = ctk.CTkSlider(f_pn_rot, from_=-180, to=180, number_of_steps=360, variable=self.var_pn_rot, command=on_pn_rot_slider)
        self.slider_pn_rot.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.ent_pn_rot.bind("<KeyRelease>", on_pn_rot_entry)

        # Uzun metinlerin alt satıra geçmesi için wraplength ayarı eklendi
        self.lbl_pn_multi_rule_title = ctk.CTkLabel(self.scroll_pn, text=get_text("lbl_pn_multi_rule"), anchor="w", font=ctk.CTkFont(weight="bold"))
        self.lbl_pn_multi_rule_title.pack(fill="x", padx=10, pady=(20,0))
        self.lbl_pn_multi_info = ctk.CTkLabel(self.scroll_pn, text=get_text("msg_pn_multi_info"), anchor="w", text_color="gray", font=ctk.CTkFont(size=11), justify="left", wraplength=410)
        self.lbl_pn_multi_info.pack(fill="x", padx=10, pady=2)
        self.textbox_pn_rules = ctk.CTkTextbox(self.scroll_pn, height=90); self.textbox_pn_rules.pack(fill="x", padx=10, pady=5); self.textbox_pn_rules.bind("<KeyRelease>", lambda e: self.update_live_preview())

    def setup_metadata_tab(self):
        info_box = ctk.CTkFrame(self.tab_metadata, fg_color=("#E3F2FD", "#1565C0"), corner_radius=8)
        info_box.pack(fill="x", padx=10, pady=(20, 10))
        self.lbl_metadata_info = ctk.CTkLabel(info_box, text=get_text("lbl_metadata_info"), text_color=("#0D47A1", "#BBDEFB"), justify="left", wraplength=410)
        self.lbl_metadata_info.pack(padx=10, pady=10)
        
        self.lbl_current_metadata_title = ctk.CTkLabel(self.tab_metadata, text=get_text("lbl_current_metadata"), font=ctk.CTkFont(weight="bold"))
        self.lbl_current_metadata_title.pack(pady=(10, 5), padx=10, anchor="w")
        self.txt_metadata_display = ctk.CTkTextbox(self.tab_metadata, height=180, font=ctk.CTkFont(size=11))
        self.txt_metadata_display.pack(fill="x", padx=10, pady=5)
        self.txt_metadata_display.configure(state="disabled")

        self.var_clean_meta = ctk.BooleanVar(value=False)
        self.chk_clean_meta = ctk.CTkCheckBox(self.tab_metadata, text=get_text("chk_clean_meta"), variable=self.var_clean_meta, font=ctk.CTkFont(weight="bold"))
        self.chk_clean_meta.pack(pady=20, padx=10, anchor="w")

    def parse_page_ranges(self, range_str, max_pages):
        range_str = range_str.strip()
        if not range_str or range_str == "*": return list(range(max_pages))
        pages = set()
        for part in range_str.split(','):
            part = part.strip()
            if '-' in part:
                try: s, e = map(int, part.split('-')); pages.update(range(s-1, e))
                except: pass
            else:
                try: pages.add(int(part)-1)
                except: pass
        return [p for p in pages if 0 <= p < max_pages]

    def get_current_settings(self):
        try: start_n = int(self.entry_pn_start.get())
        except: start_n = 1
        def get_pages(all_checked, entry_str):
            if all_checked: return list(range(self.total_pages))
            return self.parse_page_ranges(entry_str, self.total_pages)
        return {
            'wm_enabled': self.var_enable_wm.get(), 'wm_text': self.entry_wm_text.get("1.0", "end").strip(), 'wm_behind': self.var_wm_behind.get(), 'wm_rot': self.var_wm_rot.get(), 'wm_size': self.slider_wm_size.get(), 'wm_op': self.slider_wm_opacity.get(), 
            'wm_x': self.var_wm_x.get() / 100.0, 'wm_y': self.var_wm_y.get() / 100.0, 'wm_color': self.var_wm_color.get(), 'wm_custom_color': self.custom_wm_color_rgb, 'wm_pages': get_pages(self.var_wm_all_pages.get(), self.entry_wm_pages.get()),
            
            'sig_enabled': self.var_enable_sig.get(), 'sig_behind': self.var_sig_behind.get(), 'sig_path': self.sig_image_path, 'sig_scale': self.slider_sig_scale.get(), 'sig_opacity': self.slider_sig_opacity.get(), 
            'sig_x': self.var_sig_x.get() / 100.0, 'sig_y': self.var_sig_y.get() / 100.0, 'sig_rot': self.var_sig_rot.get(), 'sig_pages': get_pages(self.var_sig_all_pages.get(), self.entry_sig_pages.get()),
            
            'pn_enabled': self.var_enable_pn.get(), 'pn_start': start_n, 'pn_format': self.entry_pn_format.get(), 
            'pn_x': self.var_pn_x.get() / 100.0, 'pn_y': self.var_pn_y.get() / 100.0, 'pn_rot': self.var_pn_rot.get(), 'pn_font_style': self.var_pn_font_style.get(), 'pn_pages': get_pages(self.var_pn_all_pages.get(), self.entry_pn_pages.get()), 'pn_multi_rules': self.textbox_pn_rules.get("1.0", "end").strip()
        }

    def clear_all(self):
        self.current_pdf_path = None; self.current_password = ""; self.base_high_res_image = None; 
        self.create_preview_label(); 
        self.nav_bar.pack_forget(); self.btn_zoom_in.configure(state="disabled"); self.btn_zoom_out.configure(state="disabled"); self.btn_fit.configure(state="disabled"); self.btn_clear.configure(state="disabled"); self.btn_apply_and_save.configure(state="disabled"); self.canvas.configure(scrollregion=(0,0,0,0))
        self.update_metadata_display({})
    
    def add_dropped_files(self, files):
        pdf_files = [f for f in files if f.lower().endswith('.pdf')]
        if pdf_files:
            filepath = pdf_files[0]
            self.progress = ProgressWindow(self.winfo_toplevel(), get_text("progress_processing"))
            threading.Thread(target=self._thread_load_pdf, args=(filepath,), daemon=True).start()

    def load_pdf(self):
        filepath = filedialog.askopenfilename(title=get_text("lbl_select_pdf_adv"), filetypes=[("PDF", "*.pdf")])
        if not filepath: return
        self.progress = ProgressWindow(self.winfo_toplevel(), get_text("progress_processing"))
        threading.Thread(target=self._thread_load_pdf, args=(filepath,), daemon=True).start()

    def _thread_load_pdf(self, filepath):
        try:
            doc = fitz.open(filepath)
            file_pass = ""
            if doc.is_encrypted:
                self.after(0, lambda: self.progress.withdraw())
                dialog = PasswordDialog(self.winfo_toplevel(), get_text("dialog_warning"), f"'{os.path.basename(filepath)}' şifreli. Şifreyi girin:")
                user_pass = dialog.get_result(); self.after(0, lambda: self.progress.deiconify())
                if user_pass and doc.authenticate(user_pass): file_pass = user_pass
                else: self.after(0, lambda: messagebox.showerror(get_text("dialog_error"), "Yanlış Şifre!")); doc.close(); return

            self.total_pages = len(doc)
            meta = doc.metadata
            doc.close()

            self.current_pdf_path = filepath; self.current_password = file_pass; self.current_page_index = 0; self.zoom_factor = 1.0 
            
            self.after(0, lambda m=meta: self.update_metadata_display(m))
            self.after(0, self.init_preview_display)
        except Exception as e: self.after(0, lambda: messagebox.showerror(get_text("dialog_error"), str(e)))
        finally:
            if hasattr(self, 'progress') and self.progress.winfo_exists(): self.after(0, self.progress.destroy)

    def update_metadata_display(self, meta):
        self.txt_metadata_display.configure(state="normal")
        self.txt_metadata_display.delete("1.0", "end")
        if not meta or all(not v for v in meta.values()):
            self.txt_metadata_display.insert("end", get_text("msg_meta_empty"))
        else:
            self.txt_metadata_display.insert("end", f"{get_text('meta_author')}{meta.get('author', '-')}\n")
            self.txt_metadata_display.insert("end", f"{get_text('meta_creator')}{meta.get('creator', '-')}\n")
            self.txt_metadata_display.insert("end", f"{get_text('meta_producer')}{meta.get('producer', '-')}\n")
            self.txt_metadata_display.insert("end", f"{get_text('meta_date')}{meta.get('creationDate', '-')}")
        self.txt_metadata_display.configure(state="disabled")

    def init_preview_display(self):
        self.nav_bar.pack(fill="x", pady=(0, 10)); self.btn_zoom_in.configure(state="normal"); self.btn_zoom_out.configure(state="normal"); self.btn_fit.configure(state="normal"); self.btn_clear.configure(state="normal"); self.btn_apply_and_save.configure(state="normal"); self.update_live_preview()

    def update_live_preview(self):
        if not self.current_pdf_path: return
        settings = self.get_current_settings(); self.btn_prev.configure(state="disabled"); self.btn_next.configure(state="disabled")
        self.lbl_large_preview.configure(text=get_text("progress_wait"), image=None)
        threading.Thread(target=self._thread_render_single_page, args=(settings,), daemon=True).start()

    def apply_features_to_page(self, page, page_index, total_pages, settings):
        rect = page.rect
        if settings['pn_enabled']:
            text_to_draw = None; multi_rules_active = False; multi_rules = settings.get('pn_multi_rules', "")
            if multi_rules:
                multi_rules_active = True
                for line in multi_rules.split('\n'):
                    if '=' in line:
                        parts = line.split('=', 1)
                        if len(parts) == 2:
                            target_pages = self.parse_page_ranges(parts[0].strip(), total_pages)
                            if page_index in target_pages: text_to_draw = parts[1].strip(); break 
            if not multi_rules_active and (page_index in settings['pn_pages']) and settings['pn_format']: text_to_draw = settings['pn_format']
            if text_to_draw:
                text = text_to_draw.replace('{0}', str(settings['pn_start'] + page_index)).replace('{1}', str(total_pages))
                font_style = settings['pn_font_style']; is_b = "Kalın" in font_style or "Bold" in font_style; is_i = "İtalik" in font_style or "Italic" in font_style
                fn = self.get_turkish_font(page, is_bold=is_b, is_italic=is_i)
                tw = fitz.Font("hebo" if is_b else "helv").text_length(text, fontsize=12)
                px = (rect.width - tw) * settings['pn_x']; py = rect.height * settings['pn_y']
                if py < 17: py = 17
                if py > rect.height - 5: py = rect.height - 5
                
                center_pt = fitz.Point(px + tw/2, py - 6) 
                mat = fitz.Matrix(-settings['pn_rot'])
                page.insert_text(fitz.Point(px, py), text, fontname=fn, fontsize=12, color=(0,0,0), morph=(center_pt, mat))
        
        if settings['wm_enabled'] and settings['wm_text'] and (page_index in settings['wm_pages']):
            text = settings['wm_text']; size = settings['wm_size']; fn = self.get_turkish_font(page, is_bold=True, is_italic=False)
            
            if settings.get('wm_custom_color'):
                current_color = settings['wm_custom_color']
            else:
                color_map = {get_text("opt_color_gray"): (0.7, 0.7, 0.7), get_text("opt_color_red"): (0.8, 0.1, 0.1), get_text("opt_color_blue"): (0.1, 0.3, 0.8), get_text("opt_color_black"): (0.1, 0.1, 0.1)}
                current_color = color_map.get(settings['wm_color'], (0.7, 0.7, 0.7))
                
            lines = text.split('\n'); line_height = size * 1.15; total_height = len(lines) * line_height
            px = rect.width * settings['wm_x']; py = rect.height * settings['wm_y']; center = fitz.Point(px, py); mat = fitz.Matrix(-settings['wm_rot']); start_y = py - (total_height / 2) + (size * 0.8)
            for i, line in enumerate(lines):
                line = line.strip()
                if not line: continue
                tw = fitz.Font("hebo").text_length(line, fontsize=size)
                page.insert_text(fitz.Point(px - tw/2, start_y + i * line_height), line, fontname=fn, fontsize=size, color=current_color, fill_opacity=settings['wm_op'], morph=(center, mat), overlay=not settings['wm_behind'])
        
        if settings['sig_enabled'] and settings['sig_path'] and (page_index in settings['sig_pages']):
            try:
                img = Image.open(settings['sig_path']).convert("RGBA")
                opacity = settings.get('sig_opacity', 1.0)
                if opacity < 1.0:
                    alpha = img.split()[3]; alpha = alpha.point(lambda p: p * opacity); img.putalpha(alpha)
                
                if settings['sig_rot'] != 0.0:
                    img = img.rotate(-settings['sig_rot'], expand=True, resample=Image.BICUBIC)
                    
                w, h = img.size; scale = settings['sig_scale']; ratio = 200.0 / w; final_w = w * ratio * scale; final_h = h * ratio * scale
                x_pos = (rect.width - final_w) * settings['sig_x']; y_pos = (rect.height - final_h) * settings['sig_y']
                img_byte_arr = io.BytesIO(); img.save(img_byte_arr, format='PNG')
                page.insert_image(fitz.Rect(x_pos, y_pos, x_pos + final_w, y_pos + final_h), stream=img_byte_arr.getvalue(), overlay=not settings.get('sig_behind', False))
            except: pass

    def _thread_render_single_page(self, settings):
        try:
            doc = fitz.open(self.current_pdf_path)
            if doc.is_encrypted: doc.authenticate(self.current_password)
            page = doc.load_page(self.current_page_index)
            self.apply_features_to_page(page, self.current_page_index, self.total_pages, settings)
            pix = page.get_pixmap(dpi=150)
            mode = "RGBA" if pix.alpha else "RGB"
            pil_img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
            doc.close()
            self.base_high_res_image = pil_img
            self.after(0, self.apply_zoom)
        except Exception as e: self.after(0, lambda: messagebox.showerror(get_text("dialog_error"), str(e)))

    def change_zoom(self, amount):
        if not self.base_high_res_image: return
        if amount == "fit": self.zoom_factor = (self.canvas.winfo_width() - 40) / self.base_high_res_image.width 
        else: self.zoom_factor += amount
        if self.zoom_factor < 0.2: self.zoom_factor = 0.2
        if self.zoom_factor > 3.0: self.zoom_factor = 3.0
        self.apply_zoom()

    def apply_zoom(self):
        if not self.base_high_res_image: return
        new_w = int(self.base_high_res_image.width * self.zoom_factor)
        new_h = int(self.base_high_res_image.height * self.zoom_factor)
        resized_img = self.base_high_res_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        resized_img = ImageOps.expand(resized_img, border=2, fill="#757575") 
        ctk_img = ctk.CTkImage(light_image=resized_img, dark_image=resized_img, size=(new_w, new_h))
        
        self.lbl_large_preview.configure(image=ctk_img, text="")
        self.lbl_large_preview.image = ctk_img
        self.lbl_large_preview.update_idletasks()
        self.center_canvas_content()
        self.lbl_page_info.configure(text=get_text("lbl_page_indicator").format(self.current_page_index + 1, self.total_pages))
        self.btn_prev.configure(state="normal" if self.current_page_index > 0 else "disabled")
        self.btn_next.configure(state="normal" if self.current_page_index < self.total_pages - 1 else "disabled")

    def center_canvas_content(self, event=None):
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw <= 1 or ch <= 1: return
        iw = self.lbl_large_preview.winfo_reqwidth()
        ih = self.lbl_large_preview.winfo_reqheight()
        x = cw / 2 if cw > iw else iw / 2
        y = ch / 2 if ch > ih else ih / 2
        self.canvas.coords(self.canvas_window, x, y)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def prev_page(self):
        if self.current_page_index > 0: self.current_page_index -= 1; self.update_live_preview()
    def next_page(self):
        if self.current_page_index < self.total_pages - 1: self.current_page_index += 1; self.update_live_preview()

    def start_unified_save(self):
        save_path = filedialog.asksaveasfilename(title="Düzenlenmiş Dosyayı Kaydet", defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not save_path: return
        settings = self.get_current_settings(); self.progress = ProgressWindow(self.winfo_toplevel(), "Tüm Özellikler Uygulanıyor..."); threading.Thread(target=self._thread_unified_save, args=(save_path, settings), daemon=True).start()

    def _thread_unified_save(self, save_path, settings):
        try:
            doc = fitz.open(self.current_pdf_path)
            if doc.is_encrypted: doc.authenticate(self.current_password)
            
            for page_index in range(self.total_pages):
                # Her sayfa işlenirken yüklenme kutusunun donmasını engellemek için arayüzü zorla yenile
                if hasattr(self, 'progress') and self.progress.winfo_exists():
                    self.progress.update()

                self.apply_features_to_page(doc.load_page(page_index), page_index, self.total_pages, settings)
            
            # UYAP'ın hata vermemesi için dökümandaki etkileşimli formları ve alanları sabitleyip düzleştiriyoruz
            try:
                for p in doc:
                    p.flatten_widgets()
            except: pass

            # Kullanıcı kutucuğu işaretlemese bile UYAP için meta verileri zorunlu ve tamamen boş küme olarak sıfırlıyoruz
            doc.set_metadata({}) 
            try: doc.set_xml_metadata("")
            except: pass
            
            # Kaydetme sorunu yaratmaması için 'linear=True' eklemeden en derin temizlik moduyla (garbage=4) kaydediyoruz
            doc.save(
                save_path, 
                deflate=True,
                garbage=4, 
                clean=True
            )
            doc.close()

            add_history("⚙️", "history_action_advanced", [os.path.basename(self.current_pdf_path), os.path.basename(save_path)], save_path)
            self.after(0, lambda: ActionDialog(self.winfo_toplevel(), get_text("dialog_success"), get_text("msg_saved_unified"), save_path))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror(get_text("dialog_error"), str(e)))
        finally:
            if hasattr(self, 'progress') and self.progress.winfo_exists(): self.after(0, self.progress.destroy)

    # ==========================================
    # --- GERÇEK ZAMANLI KUSURSUZ ÇEVİRİ MOTORU ---
    # ==========================================
    def update_language(self):
        # 1. Sekme İsimlerinin Çökmeden Değişimi
        try:
            self.tabview._segmented_button._buttons_dict[self.tab_wm_name].configure(text=get_text("tab_watermark"))
            self.tabview._segmented_button._buttons_dict[self.tab_sig_name].configure(text=get_text("tab_signature"))
            self.tabview._segmented_button._buttons_dict[self.tab_pn_name].configure(text=get_text("tab_page_num"))
            self.tabview._segmented_button._buttons_dict[self.tab_meta_name].configure(text=get_text("tab_metadata"))
        except: pass

        # 2. Üst Bar ve Navigasyon Elemanları
        if hasattr(self, 'btn_select_pdf'): self.btn_select_pdf.configure(text=get_text("lbl_select_pdf_adv"))
        if hasattr(self, 'btn_clear'): self.btn_clear.configure(text=get_text("btn_clear"))
        if hasattr(self, 'btn_zoom_in'): self.btn_zoom_in.configure(text=get_text("btn_zoom_in"))
        if hasattr(self, 'btn_zoom_out'): self.btn_zoom_out.configure(text=get_text("btn_zoom_out"))
        if hasattr(self, 'btn_fit'): self.btn_fit.configure(text=get_text("btn_fit"))
        if hasattr(self, 'btn_prev'): self.btn_prev.configure(text=get_text("btn_prev_page"))
        if hasattr(self, 'btn_next'): self.btn_next.configure(text=get_text("btn_next_page"))
        if hasattr(self, 'btn_apply_and_save'): self.btn_apply_and_save.configure(text=get_text("btn_apply_and_save"))
        
        if not self.current_pdf_path and hasattr(self, 'lbl_large_preview'):
            self.lbl_large_preview.configure(text=get_text("msg_adv_info"))

        # 3. FİLİGRAN SEKMESİ ÇEVİRİLERİ
        if hasattr(self, 'chk_enable_wm'): self.chk_enable_wm.configure(text=get_text("chk_enable_wm"))
        if hasattr(self, 'chk_wm_behind'): self.chk_wm_behind.configure(text=get_text("chk_wm_behind"))
        if hasattr(self, 'chk_wm_all_pages'): self.chk_wm_all_pages.configure(text=get_text("chk_all_pages"))
        if hasattr(self, 'entry_wm_pages'): self.entry_wm_pages.configure(placeholder_text=get_text("lbl_custom_pages"))
        if hasattr(self, 'lbl_wm_preset_text'): self.lbl_wm_preset_text.configure(text=get_text("lbl_wm_preset_text"))
        if hasattr(self, 'lbl_wm_text_title'): self.lbl_wm_text_title.configure(text=get_text("lbl_wm_text"))
        if hasattr(self, 'lbl_wm_color_title'): self.lbl_wm_color_title.configure(text=get_text("lbl_wm_color"))
        if hasattr(self, 'lbl_wm_pos_preset_title'): self.lbl_wm_pos_preset_title.configure(text=get_text("lbl_wm_pos_preset"))
        if hasattr(self, 'lbl_wm_x_title'): self.lbl_wm_x_title.configure(text=get_text("lbl_pos_x"))
        if hasattr(self, 'lbl_wm_y_title'): self.lbl_wm_y_title.configure(text=get_text("lbl_pos_y"))
        if hasattr(self, 'lbl_wm_rot_title'): self.lbl_wm_rot_title.configure(text=get_text("lbl_wm_rot"))
        if hasattr(self, 'lbl_wm_size_title'): self.lbl_wm_size_title.configure(text=get_text("lbl_wm_size"))
        if hasattr(self, 'lbl_wm_opacity_title'): self.lbl_wm_opacity_title.configure(text=get_text("lbl_wm_opacity"))

        # Şablon Seçim Listesi Değer Koruyucusu
        if hasattr(self, 'opt_wm_template'):
            curr = self.var_wm_template.get()
            idx = 0
            v_tr = ["Özel Metin", "GİZLİ", "KOPYALANMAZ", "TASLAK", "ONAYLANDI", "ACİL", "REVİZYON", "KİŞİSEL"]
            v_en = ["Custom Text", "CONFIDENTIAL", "DO NOT COPY", "DRAFT", "APPROVED", "URGENT", "REVISION", "PERSONAL"]
            if curr in v_tr: idx = v_tr.index(curr)
            elif curr in v_en: idx = v_en.index(curr)
            opts = [get_text("opt_custom_text"), get_text("wm_t1"), get_text("wm_t2"), get_text("wm_t3"), get_text("wm_t4"), get_text("wm_t5"), get_text("wm_t6"), get_text("wm_t7")]
            self.opt_wm_template.configure(values=opts)
            self.var_wm_template.set(opts[idx])

        # Renk Buton Listesi Değer Koruyucusu
        if hasattr(self, 'seg_color'):
            curr = self.var_wm_color.get()
            idx = 0
            c_tr = ["Gri", "Kırmızı", "Mavi", "Siyah"]
            c_en = ["Gray", "Red", "Blue", "Black"]
            if curr in c_tr: idx = c_tr.index(curr)
            elif curr in c_en: idx = c_en.index(curr)
            opts_c = [get_text("opt_color_gray"), get_text("opt_color_red"), get_text("opt_color_blue"), get_text("opt_color_black")]
            self.seg_color.configure(values=opts_c)
            self.var_wm_color.set(opts_c[idx])

        # Konum Seçim Listesi Değer Koruyucusu
        if hasattr(self, 'opt_wm_pos_preset'):
            curr = self.var_wm_pos_preset.get()
            idx = 0
            p_tr = ["Merkez Ortalanmış", "Alt Ortalanmış", "Üst Ortalanmış", "Sol Dikey Kenar", "Sağ Dikey Kenar", "Çapraz Tam Ekran"]
            p_en = ["Center Balanced", "Bottom Balanced", "Top Balanced", "Left Vertical Margin", "Right Vertical Margin", "Diagonal Fullscreen"]
            if curr in p_tr: idx = p_tr.index(curr)
            elif curr in p_en: idx = p_en.index(curr)
            opts_p = [get_text("opt_wm_mc"), get_text("opt_wm_bc"), get_text("opt_wm_tc"), get_text("opt_wm_lv"), get_text("opt_wm_rv"), get_text("opt_wm_cv")]
            self.opt_wm_pos_preset.configure(values=opts_p)
            self.var_wm_pos_preset.set(opts_p[idx])

        # 4. İMZA SEKMESİ ÇEVİRİLERİ
        if hasattr(self, 'chk_enable_sig'): self.chk_enable_sig.configure(text=get_text("chk_enable_sig"))
        if hasattr(self, 'chk_sig_behind'): self.chk_sig_behind.configure(text=get_text("chk_sig_behind"))
        if hasattr(self, 'btn_select_sig'): self.btn_select_sig.configure(text=get_text("btn_select_sig"))
        if not self.sig_image_path and hasattr(self, 'lbl_sig_file'): self.lbl_sig_file.configure(text=get_text("msg_no_sig_selected"))
        if hasattr(self, 'chk_sig_all_pages'): self.chk_sig_all_pages.configure(text=get_text("chk_all_pages"))
        if hasattr(self, 'entry_sig_pages'): self.entry_sig_pages.configure(placeholder_text=get_text("lbl_custom_pages"))
        if hasattr(self, 'lbl_sig_scale_title'): self.lbl_sig_scale_title.configure(text=get_text("lbl_sig_scale"))
        if hasattr(self, 'lbl_sig_opacity_title'): self.lbl_sig_opacity_title.configure(text=get_text("lbl_sig_opacity"))
        if hasattr(self, 'lbl_sig_preset_pos_title'): self.lbl_sig_preset_pos_title.configure(text=get_text("lbl_preset_pos"))
        if hasattr(self, 'lbl_sig_x_title'): self.lbl_sig_x_title.configure(text=get_text("lbl_pos_x"))
        if hasattr(self, 'lbl_sig_y_title'): self.lbl_sig_y_title.configure(text=get_text("lbl_pos_y"))
        if hasattr(self, 'lbl_sig_rot_title'): self.lbl_sig_rot_title.configure(text=get_text("lbl_wm_rot"))

        if hasattr(self, 'opt_sig_pos_preset'):
            curr = self.var_sig_pos_preset.get()
            idx = 8
            ps_tr = ["Sol Üst", "Orta Üst", "Sağ Üst", "Sol Orta", "Merkez", "Sağ Orta", "Sol Alt", "Orta Alt", "Sağ Alt"]
            ps_en = ["Top Left", "Top Center", "Top Right", "Middle Left", "Center", "Middle Right", "Bottom Left", "Bottom Center", "Bottom Right"]
            if curr in ps_tr: idx = ps_tr.index(curr)
            elif curr in ps_en: idx = ps_en.index(curr)
            opts_ps = [get_text("opt_pos_tl"), get_text("opt_pos_tc"), get_text("opt_pos_tr"), get_text("opt_pos_ml"), get_text("opt_pos_mc"), get_text("opt_pos_mr"), get_text("opt_pos_bl"), get_text("opt_pos_bc"), get_text("opt_pos_br")]
            self.opt_sig_pos_preset.configure(values=opts_ps)
            self.var_sig_pos_preset.set(opts_ps[idx])

        # 5. SAYFA NUMARASI SEKMESİ ÇEVİRİLERİ
        if hasattr(self, 'chk_enable_pn'): self.chk_enable_pn.configure(text=get_text("chk_enable_pn"))
        if hasattr(self, 'chk_pn_all_pages'): self.chk_pn_all_pages.configure(text=get_text("chk_all_pages"))
        if hasattr(self, 'entry_pn_pages'): self.entry_pn_pages.configure(placeholder_text=get_text("lbl_custom_pages"))
        if hasattr(self, 'lbl_pn_template_title'): self.lbl_pn_template_title.configure(text=get_text("lbl_pn_template"))
        if hasattr(self, 'lbl_pn_format_title'): self.lbl_pn_format_title.configure(text=get_text("lbl_pn_format"))
        if hasattr(self, 'lbl_pn_start_title'): self.lbl_pn_start_title.configure(text=get_text("lbl_pn_start"))
        if hasattr(self, 'lbl_font_style_title'): self.lbl_font_style_title.configure(text=get_text("lbl_font_style"))
        if hasattr(self, 'lbl_pn_preset_pos_title'): self.lbl_pn_preset_pos_title.configure(text=get_text("lbl_preset_pos"))
        if hasattr(self, 'lbl_pn_x_title'): self.lbl_pn_x_title.configure(text=get_text("lbl_pos_x"))
        if hasattr(self, 'lbl_pn_y_title'): self.lbl_pn_y_title.configure(text=get_text("lbl_pos_y"))
        if hasattr(self, 'lbl_pn_rot_title'): self.lbl_pn_rot_title.configure(text=get_text("lbl_wm_rot"))
        if hasattr(self, 'lbl_pn_multi_rule_title'): self.lbl_pn_multi_rule_title.configure(text=get_text("lbl_pn_multi_rule"))
        if hasattr(self, 'lbl_pn_multi_info'): self.lbl_pn_multi_info.configure(text=get_text("msg_pn_multi_info"))

        if hasattr(self, 'opt_pn_template'):
            curr = self.var_pn_template.get()
            idx = 0
            pn_tr = ["Özel Format", "Yalnızca Sayfa No", "Mevcut / Toplam", "Mevcut - Toplam", "Sayfa X", "Sayfa X / Y", "Ek Numarası", "Köşeli Parantez"]
            pn_en = ["Custom Text", "Page Number Only", "Current / Total", "Current - Total", "Page X", "Page X / Y", "Appendix Number", "Square Brackets"]
            if curr in pn_tr: idx = pn_tr.index(curr)
            elif curr in pn_en: idx = pn_en.index(curr)
            opts_pn = [get_text("opt_custom_text"), get_text("opt_pn_t1"), get_text("opt_pn_t2"), get_text("opt_pn_t3"), get_text("opt_pn_t4"), get_text("opt_pn_t5"), get_text("opt_pn_t6"), get_text("opt_pn_t7")]
            self.opt_pn_template.configure(values=opts_pn)
            self.var_pn_template.set(opts_pn[idx])

        if hasattr(self, 'opt_pn_font_style'):
            curr = self.var_pn_font_style.get()
            idx = 0
            f_tr = ["Normal", "Kalın", "İtalik", "Kalın İtalik"]
            f_en = ["Normal", "Bold", "Italic", "Bold Italic"]
            if curr in f_tr: idx = f_tr.index(curr)
            elif curr in f_en: idx = f_en.index(curr)
            opts_f = [get_text("opt_normal"), get_text("opt_bold"), get_text("opt_italic"), get_text("opt_bold_italic")]
            self.opt_pn_font_style.configure(values=opts_f)
            self.var_pn_font_style.set(opts_f[idx])

        if hasattr(self, 'opt_pn_pos_preset'):
            curr = self.var_pn_pos_preset.get()
            idx = 7
            p_tr = ["Sol Üst", "Orta Üst", "Sağ Üst", "Sol Orta", "Merkez", "Sağ Orta", "Sol Alt", "Orta Alt", "Sağ Alt"]
            p_en = ["Top Left", "Top Center", "Top Right", "Middle Left", "Center", "Middle Right", "Bottom Left", "Bottom Center", "Bottom Right"]
            if curr in p_tr: idx = p_tr.index(curr)
            elif curr in p_en: idx = p_en.index(curr)
            opts_p = [get_text("opt_pos_tl"), get_text("opt_pos_tc"), get_text("opt_pos_tr"), get_text("opt_pos_ml"), get_text("opt_pos_mc"), get_text("opt_pos_mr"), get_text("opt_pos_bl"), get_text("opt_pos_bc"), get_text("opt_pos_br")]
            self.opt_pn_pos_preset.configure(values=opts_p)
            self.var_pn_pos_preset.set(opts_p[idx])

        # 6. META VERİ SEKMESİ ÇEVİRİLERİ
        if hasattr(self, 'lbl_metadata_info'): self.lbl_metadata_info.configure(text=get_text("lbl_metadata_info"))
        if hasattr(self, 'lbl_current_metadata_title'): self.lbl_current_metadata_title.configure(text=get_text("lbl_current_metadata"))
        if hasattr(self, 'chk_clean_meta'): self.chk_clean_meta.configure(text=get_text("chk_clean_meta"))