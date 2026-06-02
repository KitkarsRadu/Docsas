import customtkinter as ctk
from tkinter import filedialog, messagebox, Canvas
from PIL import Image, ImageOps
import fitz  
import os
import sys
import re
import threading
from modules.pdf_araclari import PasswordDialog, ProgressWindow, center_window
from modules.language_manager import lang_manager, get_text

class MacroSuccessDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, message, file_path):
        super().__init__(parent)
        self.title(title)
        self.geometry("450x200")
        # transient eklenerek sadece Docsas'ın üstünde kalması sağlanır (Chrome arkasında kalabilir)
        self.transient(parent)
        center_window(self, parent)
        self.file_path = file_path
        
        ctk.CTkLabel(self, text="✅ " + message, font=ctk.CTkFont(size=14, weight="bold"), wraplength=400).pack(pady=(30, 20))
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20)
        
        ctk.CTkButton(btn_frame, text=get_text("btn_open_file_direct"), font=ctk.CTkFont(weight="bold"), fg_color="#4CAF50", hover_color="#388E3C", command=self.open_file).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(btn_frame, text=get_text("dialog_ok"), fg_color="gray40", command=self.destroy).pack(side="right", expand=True, padx=5)
        
    def open_file(self):
        try:
            if sys.platform == "win32": os.startfile(self.file_path)
            elif sys.platform == "darwin": os.system(f"open '{self.file_path}'")
            else: os.system(f"xdg-open '{self.file_path}'")
        except: pass
        self.destroy()

class MakroVeKaseSayfasi(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        
        self.current_pdf_path = None
        self.current_password = ""
        self.current_page_index = 0
        self.total_pages = 0
        self.zoom_factor = 1.0
        self.base_high_res_image = None
        self.current_preview_image = None
        self.custom_stamp_path = None
        
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=3)
        # OLUMLU DÜZELTME 1: Sağ menü 330 piksele (kompakt) düşürüldü
        self.grid_columnconfigure(1, weight=1, minsize=330)
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # --- SOL TARAF: CANLI ÖNİZLEME ALANI ---
        # ==========================================
        self.left_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        top_bar = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 10))
        
        ctk.CTkButton(top_bar, text=get_text("btn_select_file"), font=ctk.CTkFont(weight="bold"), fg_color="#F57C00", hover_color="#E65100", command=self.load_pdf).pack(side="left", padx=5)
        self.btn_clear = ctk.CTkButton(top_bar, text=get_text("btn_clear"), width=80, fg_color="transparent", border_width=1, border_color=("gray60", "gray40"), text_color=("black", "white"), command=self.clear_all)
        self.btn_clear.pack(side="left", padx=5)
        
        self.btn_zoom_in = ctk.CTkButton(top_bar, text=get_text("btn_zoom_in_text"), width=100, fg_color=("gray75", "gray30"), text_color=("black", "white"), command=lambda: self.change_zoom(0.2))
        self.btn_zoom_in.pack(side="right", padx=2)
        self.btn_fit = ctk.CTkButton(top_bar, text=get_text("btn_fit"), width=100, fg_color=("gray75", "gray30"), text_color=("black", "white"), command=lambda: self.change_zoom("fit"))
        self.btn_fit.pack(side="right", padx=2)
        self.btn_zoom_out = ctk.CTkButton(top_bar, text=get_text("btn_zoom_out_text"), width=100, fg_color=("gray75", "gray30"), text_color=("black", "white"), command=lambda: self.change_zoom(-0.2))
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

        self.nav_bar_pdf = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.btn_prev_page = ctk.CTkButton(self.nav_bar_pdf, text="<", width=50, fg_color="gray40", command=self.prev_pdf_page)
        self.btn_prev_page.pack(side="left", padx=10)
        self.lbl_pdf_page_info = ctk.CTkLabel(self.nav_bar_pdf, text="", font=ctk.CTkFont(weight="bold", size=13))
        self.lbl_pdf_page_info.pack(side="left", expand=True)
        self.btn_next_page = ctk.CTkButton(self.nav_bar_pdf, text=">", width=50, fg_color="gray40", command=self.next_pdf_page)
        self.btn_next_page.pack(side="right", padx=10)
        self.nav_bar_pdf.pack_forget()

        # ==========================================
        # --- SAĞ TARAF: DEV KONTROL PANELİ ---
        # ==========================================
        # OLUMLU DÜZELTME 1: Sağ menü 330 piksele (kompakt) düşürüldü
        self.right_frame = ctk.CTkScrollableFrame(self, width=330)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        header_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 5))
        ctk.CTkButton(header_frame, text=get_text("btn_guide_modal"), fg_color="#1976D2", hover_color="#1565C0", command=self.open_guide_modal).pack(side="right", padx=5)
        self.lbl_pdf_name = ctk.CTkLabel(header_frame, text=get_text("msg_waiting_file"), text_color="gray", font=ctk.CTkFont(size=12, slant="italic"))
        self.lbl_pdf_name.pack(side="left", padx=5)

        self.tabview = ctk.CTkTabview(self.right_frame)
        self.tabview.pack(fill="both", expand=True, padx=5, pady=(0, 10))

        self.tab_kvkk = self.tabview.add(get_text("tab_kvkk_sec"))
        self.tab_bates = self.tabview.add(get_text("tab_bates"))
        self.tab_stamp = self.tabview.add(get_text("tab_stamp"))

        self._setup_kvkk_tab()
        self._setup_bates_tab()
        self._setup_stamp_tab()

        action_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        action_frame.pack(fill="x", padx=10, pady=10)
        
        self.var_auto_preview = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(action_frame, text=get_text("chk_auto_preview"), variable=self.var_auto_preview, text_color="#F57C00", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0,10))
        
        self.btn_refresh = ctk.CTkButton(action_frame, text="👁️ Değişiklikleri Önizle", font=ctk.CTkFont(weight="bold"), text_color="white", text_color_disabled="white", fg_color="#4CAF50", hover_color="#388E3C", command=self.update_live_preview)
        self.btn_refresh.pack(fill="x", pady=(0, 10))
        
        self.btn_process = ctk.CTkButton(action_frame, text="Zincirleme İşlemi Başlat", font=ctk.CTkFont(size=16, weight="bold"), height=55, text_color="white", text_color_disabled="white", fg_color="#1565C0", hover_color="#0D47A1", command=self.start_macro_process)
        self.btn_process.pack(fill="x")
        
        self._toggle_ui_state("disabled")

    def open_guide_modal(self):
        modal = ctk.CTkToplevel(self)
        modal.title(get_text("btn_guide_modal"))
        modal.geometry("550x450")
        modal.attributes("-topmost", True)
        center_window(modal, self.winfo_toplevel())
        modal.grab_set()

        ctk.CTkLabel(modal, text=get_text("guide_macro_title"), font=ctk.CTkFont(size=16, weight="bold"), text_color="#F57C00").pack(pady=(20,10))
        ctk.CTkLabel(modal, text=get_text("guide_macro_text"), font=ctk.CTkFont(size=12), justify="left", wraplength=480).pack(padx=20, pady=10)
        ctk.CTkButton(modal, text=get_text("dialog_ok"), command=modal.destroy).pack(pady=20)

    def _auto_trigger(self, *args):
        if self.var_auto_preview.get() and self.current_pdf_path:
            if hasattr(self, '_timer_id'): self.after_cancel(self._timer_id)
            self._timer_id = self.after(400, self.update_live_preview)

    def _toggle_page_entry(self, chk_var, entry_widget):
        state = "disabled" if chk_var.get() else "normal"
        entry_widget.configure(state=state)
        self._auto_trigger()

    # ==========================================
    # --- SEKME 1: KVKK & GÜVENLİK ---
    # ==========================================
    def _setup_kvkk_tab(self):
        is_tr = lang_manager.current_lang == "TR"
        
        ctk.CTkLabel(self.tab_kvkk, text=get_text("lbl_kvkk_regex_title"), font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(5,2))
        
        self.var_kvkk_tc = ctk.BooleanVar(value=False)
        self.var_kvkk_id = ctk.BooleanVar(value=False)
        self.var_kvkk_passport = ctk.BooleanVar(value=False)
        self.var_kvkk_iban = ctk.BooleanVar(value=False)
        self.var_kvkk_phone = ctk.BooleanVar(value=False)
        self.var_kvkk_nums = ctk.BooleanVar(value=False)
        
        f1 = ctk.CTkFrame(self.tab_kvkk, fg_color="transparent")
        f1.pack(fill="x")
        ctk.CTkCheckBox(f1, text=get_text("chk_kvkk_tc"), variable=self.var_kvkk_tc, command=self._auto_trigger).pack(side="left", padx=5, pady=5)
        ctk.CTkCheckBox(f1, text=get_text("chk_kvkk_id"), variable=self.var_kvkk_id, command=self._auto_trigger).pack(side="left", padx=5, pady=5)
        ctk.CTkCheckBox(f1, text=get_text("chk_kvkk_passport"), variable=self.var_kvkk_passport, command=self._auto_trigger).pack(side="left", padx=5, pady=5)
        
        f2 = ctk.CTkFrame(self.tab_kvkk, fg_color="transparent")
        f2.pack(fill="x")
        ctk.CTkCheckBox(f2, text=get_text("chk_kvkk_iban"), variable=self.var_kvkk_iban, command=self._auto_trigger).pack(side="left", padx=5, pady=5)
        ctk.CTkCheckBox(f2, text=get_text("chk_kvkk_phone"), variable=self.var_kvkk_phone, command=self._auto_trigger).pack(side="left", padx=5, pady=5)
        ctk.CTkCheckBox(f2, text=get_text("chk_kvkk_nums"), variable=self.var_kvkk_nums, command=self._auto_trigger).pack(side="left", padx=5, pady=5)

        ctk.CTkLabel(self.tab_kvkk, text=get_text("lbl_redact_custom"), font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10,2))
        
        ph_redact = "Örn: Radu (Virgülle ayırın)" if is_tr else "e.g., Radu (Separate with commas)"
        self.ent_custom_redact = ctk.CTkEntry(self.tab_kvkk, placeholder_text=ph_redact)
        self.ent_custom_redact.pack(fill="x", padx=5)
        self.ent_custom_redact.bind("<KeyRelease>", self._auto_trigger)

        ctk.CTkLabel(self.tab_kvkk, text=get_text("lbl_redact_color"), font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10,2))
        self.var_redact_color = ctk.StringVar(value=get_text("opt_color_black"))
        opts_c = [get_text("opt_color_black"), get_text("opt_color_red"), get_text("opt_color_blue"), get_text("opt_color_gray"), get_text("opt_transparent")]
        ctk.CTkOptionMenu(self.tab_kvkk, values=opts_c, variable=self.var_redact_color, command=self._auto_trigger).pack(fill="x", padx=5)

        ctk.CTkLabel(self.tab_kvkk, text=get_text("lbl_compression_lvl"), font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(15,2))
        self.var_compress = ctk.StringVar(value=get_text("opt_comp_none"))
        opts_comp = [get_text("opt_comp_none"), get_text("opt_comp_mid"), get_text("opt_comp_max")]
        ctk.CTkOptionMenu(self.tab_kvkk, values=opts_comp, variable=self.var_compress).pack(fill="x", padx=5)

        ctk.CTkLabel(self.tab_kvkk, text=get_text("lbl_encryption"), font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(15,5))
        pw_frame = ctk.CTkFrame(self.tab_kvkk, fg_color="transparent")
        pw_frame.pack(fill="x", padx=5)
        
        pw_inputs = ctk.CTkFrame(pw_frame, fg_color="transparent")
        pw_inputs.pack(side="left", fill="x", expand=True)
        self.ent_encrypt1 = ctk.CTkEntry(pw_inputs, placeholder_text=get_text("lbl_pw_1"), show="*")
        self.ent_encrypt1.pack(fill="x", pady=2)
        self.ent_encrypt2 = ctk.CTkEntry(pw_inputs, placeholder_text=get_text("lbl_pw_2"), show="*")
        self.ent_encrypt2.pack(fill="x", pady=2)
        
        self.btn_eye = ctk.CTkButton(pw_frame, text="👁️", width=40, height=60, fg_color=("gray75", "gray30"), text_color=("black", "white"), command=self._toggle_pw_visibility)
        self.btn_eye.pack(side="right", padx=(5,0))

    def _toggle_pw_visibility(self):
        if self.ent_encrypt1.cget("show") == "*":
            self.ent_encrypt1.configure(show=""); self.ent_encrypt2.configure(show="")
            self.btn_eye.configure(fg_color="#1976D2", text_color="white")
        else:
            self.ent_encrypt1.configure(show="*"); self.ent_encrypt2.configure(show="*")
            self.btn_eye.configure(fg_color=("gray75", "gray30"), text_color=("black", "white"))

    # ==========================================
    # --- SEKME 2: BATES NUMARALANDIRMA ---
    # ==========================================
    def _setup_bates_tab(self):
        is_tr = lang_manager.current_lang == "TR"
        
        self.var_bates_enable = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(self.tab_bates, text=get_text("lbl_bates_enable"), variable=self.var_bates_enable, font=ctk.CTkFont(weight="bold"), text_color="#1976D2", command=self._auto_trigger).pack(anchor="w", pady=(5, 10))
        
        f_pages = ctk.CTkFrame(self.tab_bates, fg_color="transparent")
        f_pages.pack(fill="x", pady=5)
        ctk.CTkLabel(f_pages, text=get_text("lbl_macro_pages")).pack(anchor="w")
        
        self.var_bates_all_pages = ctk.BooleanVar(value=True)
        self.chk_bates_all = ctk.CTkCheckBox(f_pages, text=get_text("chk_all_pages"), variable=self.var_bates_all_pages, command=lambda: self._toggle_page_entry(self.var_bates_all_pages, self.ent_bates_pages))
        self.chk_bates_all.pack(anchor="w", pady=2)
        
        self.ent_bates_pages = ctk.CTkEntry(f_pages, placeholder_text=get_text("lbl_custom_pages"))
        self.ent_bates_pages.pack(fill="x", pady=2)
        self.ent_bates_pages.configure(state="disabled")
        self.ent_bates_pages.bind("<KeyRelease>", self._auto_trigger)
        
        f_custom = ctk.CTkFrame(self.tab_bates, fg_color="transparent")
        f_custom.pack(fill="x", pady=5)
        ctk.CTkLabel(f_custom, text=get_text("lbl_bates_custom_group")).pack(anchor="w")
        ph_custom = "Örn: 1-3=EK-1, 4-9=EK-2" if is_tr else "e.g., 1-3=APP-1, 4-9=APP-2"
        self.ent_bates_custom = ctk.CTkEntry(f_custom, placeholder_text=ph_custom)
        self.ent_bates_custom.pack(fill="x", pady=2)
        self.ent_bates_custom.bind("<KeyRelease>", self._auto_trigger)

        f_rep = ctk.CTkFrame(self.tab_bates, fg_color="transparent")
        f_rep.pack(fill="x", pady=(5,0))
        ctk.CTkLabel(f_rep, text=get_text("lbl_bates_repeat")).pack(side="left")
        self.ent_bates_rep = ctk.CTkEntry(f_rep, width=60); self.ent_bates_rep.insert(0, "1"); self.ent_bates_rep.pack(side="right")
        self.ent_bates_rep.bind("<KeyRelease>", self._auto_trigger)

        f_num = ctk.CTkFrame(self.tab_bates, fg_color="transparent")
        f_num.pack(fill="x", pady=5)
        ph_prefix = "EK-" if is_tr else "APP-"
        self.ent_bates_prefix = ctk.CTkEntry(f_num, width=80, placeholder_text=ph_prefix)
        self.ent_bates_prefix.pack(side="left", padx=2)
        self.ent_bates_prefix.bind("<KeyRelease>", self._auto_trigger)
        
        self.ent_bates_start = ctk.CTkEntry(f_num, width=50); self.ent_bates_start.insert(0, "1"); self.ent_bates_start.pack(side="left", padx=2)
        self.ent_bates_start.bind("<KeyRelease>", self._auto_trigger)
        
        self.var_bates_zeros = ctk.StringVar(value=get_text("opt_bates_z4"))
        opts_z = [get_text("opt_bates_z0"), get_text("opt_bates_z2"), get_text("opt_bates_z3"), get_text("opt_bates_z4")]
        ctk.CTkOptionMenu(f_num, values=opts_z, variable=self.var_bates_zeros, command=self._auto_trigger).pack(side="left", padx=2, fill="x", expand=True)

        ctk.CTkLabel(self.tab_bates, text=get_text("lbl_bates_style"), anchor="w").pack(fill="x", pady=(10, 2))
        f_font = ctk.CTkFrame(self.tab_bates, fg_color="transparent")
        f_font.pack(fill="x")
        self.var_bates_style = ctk.StringVar(value=get_text("opt_bold"))
        opts_st = [get_text("opt_normal"), get_text("opt_bold"), get_text("opt_italic"), get_text("opt_bold_italic")]
        ctk.CTkOptionMenu(f_font, values=opts_st, variable=self.var_bates_style, width=120, command=self._auto_trigger).pack(side="left", padx=2)
        self.slider_bates_size = ctk.CTkSlider(f_font, from_=8, to=48, number_of_steps=40, command=self._auto_trigger)
        self.slider_bates_size.set(14)
        self.slider_bates_size.pack(side="left", padx=10, fill="x", expand=True)

        ctk.CTkLabel(self.tab_bates, text=get_text("lbl_wm_opacity"), anchor="w").pack(fill="x", pady=(10, 2))
        self.slider_bates_opacity = ctk.CTkSlider(self.tab_bates, from_=0.1, to=1.0, number_of_steps=9, command=self._auto_trigger)
        self.slider_bates_opacity.set(1.0)
        self.slider_bates_opacity.pack(fill="x", padx=5)

        # OLUMLU DÜZELTME 2: BATES ROTASYON İÇİN DERECE GİRİŞ KUTUSU EKLENDİ
        ctk.CTkLabel(self.tab_bates, text=get_text("lbl_wm_rot"), anchor="w").pack(fill="x", pady=(10, 2))
        f_brot = ctk.CTkFrame(self.tab_bates, fg_color="transparent")
        f_brot.pack(fill="x", padx=5)
        
        self.var_bates_rot = ctk.DoubleVar(value=0.0)
        self.ent_bates_rot = ctk.CTkEntry(f_brot, width=50, height=25)
        self.ent_bates_rot.pack(side="right")
        self.ent_bates_rot.insert(0, "0.0")

        def on_brot_slider(val):
            self.ent_bates_rot.delete(0, "end")
            self.ent_bates_rot.insert(0, f"{float(val):.1f}")
            self._auto_trigger()
            
        def on_brot_entry(e):
            try:
                v = float(self.ent_bates_rot.get())
                if -180 <= v <= 180:
                    self.var_bates_rot.set(v)
                    self._auto_trigger()
            except: pass

        self.slider_bates_rot = ctk.CTkSlider(f_brot, from_=-180, to=180, number_of_steps=360, variable=self.var_bates_rot, command=on_brot_slider)
        self.slider_bates_rot.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.ent_bates_rot.bind("<KeyRelease>", on_brot_entry)

        self._build_position_ui(self.tab_bates, "bates", get_text("opt_pos_tr")) 

    # ==========================================
    # --- SEKME 3: MÜHÜR VE KAŞE ---
    # ==========================================
    def _setup_stamp_tab(self):
        ctk.CTkLabel(self.tab_stamp, text=get_text("lbl_stamp_title"), font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(5, 5))
        
        self.var_stamp_preset = ctk.StringVar(value=get_text("opt_stamp_none"))
        opts = [get_text("opt_stamp_none"), get_text("opt_stamp_asli"), get_text("opt_stamp_gizli"), get_text("opt_stamp_onay"), get_text("opt_stamp_custom")]
        ctk.CTkOptionMenu(self.tab_stamp, values=opts, variable=self.var_stamp_preset, command=self._on_stamp_change).pack(fill="x", padx=5)
        
        self.btn_upload_stamp = ctk.CTkButton(self.tab_stamp, text=get_text("btn_upload_img"), fg_color="gray40", command=self._upload_custom_stamp)
        self.btn_upload_stamp.pack(fill="x", padx=5, pady=5)
        self.btn_upload_stamp.pack_forget()

        f_stamp_pages = ctk.CTkFrame(self.tab_stamp, fg_color="transparent")
        f_stamp_pages.pack(fill="x", pady=5)
        ctk.CTkLabel(f_stamp_pages, text=get_text("lbl_macro_pages")).pack(anchor="w")
        
        self.var_stamp_all_pages = ctk.BooleanVar(value=True)
        self.chk_stamp_all = ctk.CTkCheckBox(f_stamp_pages, text=get_text("chk_all_pages"), variable=self.var_stamp_all_pages, command=lambda: self._toggle_page_entry(self.var_stamp_all_pages, self.ent_stamp_pages))
        self.chk_stamp_all.pack(anchor="w", pady=2)
        
        self.ent_stamp_pages = ctk.CTkEntry(f_stamp_pages, placeholder_text=get_text("lbl_custom_pages"))
        self.ent_stamp_pages.pack(fill="x", pady=2)
        self.ent_stamp_pages.configure(state="disabled")
        self.ent_stamp_pages.bind("<KeyRelease>", self._auto_trigger)

        ctk.CTkLabel(self.tab_stamp, text=get_text("lbl_stamp_scale"), anchor="w").pack(fill="x", pady=(10, 2))
        self.slider_stamp_scale = ctk.CTkSlider(self.tab_stamp, from_=0.2, to=3.0, number_of_steps=28, command=self._auto_trigger)
        self.slider_stamp_scale.set(1.0)
        self.slider_stamp_scale.pack(fill="x", padx=5)

        ctk.CTkLabel(self.tab_stamp, text=get_text("lbl_wm_opacity"), anchor="w").pack(fill="x", pady=(10, 2))
        self.slider_stamp_opacity = ctk.CTkSlider(self.tab_stamp, from_=0.1, to=1.0, number_of_steps=9, command=self._auto_trigger)
        self.slider_stamp_opacity.set(0.6) 
        self.slider_stamp_opacity.pack(fill="x", padx=5)

        # OLUMLU DÜZELTME 2: MÜHÜR ROTASYON İÇİN DERECE GİRİŞ KUTUSU EKLENDİ
        ctk.CTkLabel(self.tab_stamp, text=get_text("lbl_wm_rot"), anchor="w").pack(fill="x", pady=(10, 2))
        f_srot = ctk.CTkFrame(self.tab_stamp, fg_color="transparent")
        f_srot.pack(fill="x", padx=5)
        
        self.var_stamp_rot = ctk.DoubleVar(value=-15.0)
        self.ent_stamp_rot = ctk.CTkEntry(f_srot, width=50, height=25)
        self.ent_stamp_rot.pack(side="right")
        self.ent_stamp_rot.insert(0, "-15.0")

        def on_srot_slider(val):
            self.ent_stamp_rot.delete(0, "end")
            self.ent_stamp_rot.insert(0, f"{float(val):.1f}")
            self._auto_trigger()
            
        def on_srot_entry(e):
            try:
                v = float(self.ent_stamp_rot.get())
                if -180 <= v <= 180:
                    self.var_stamp_rot.set(v)
                    self._auto_trigger()
            except: pass

        self.slider_stamp_rot = ctk.CTkSlider(f_srot, from_=-180, to=180, number_of_steps=360, variable=self.var_stamp_rot, command=on_srot_slider)
        self.slider_stamp_rot.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.ent_stamp_rot.bind("<KeyRelease>", on_srot_entry)

        self._build_position_ui(self.tab_stamp, "stamp", get_text("opt_pos_center")) 

    # ==========================================
    # --- SENKRONİZE X/Y SLIDER MOTORU ---
    # ==========================================
    def _build_position_ui(self, parent, prefix, default_pos):
        ctk.CTkLabel(parent, text=get_text("lbl_position"), anchor="w").pack(fill="x", pady=(15, 2))
        var_pos = ctk.StringVar(value=default_pos)
        setattr(self, f"var_{prefix}_pos", var_pos)
        
        pos_opts = [get_text("opt_pos_tl"), get_text("opt_pos_tc"), get_text("opt_pos_tr"), get_text("opt_pos_ml"), get_text("opt_pos_center"), get_text("opt_pos_mr"), get_text("opt_pos_bl"), get_text("opt_pos_bc"), get_text("opt_pos_br"), get_text("opt_pos_custom")]
        menu = ctk.CTkOptionMenu(parent, values=pos_opts, variable=var_pos, command=lambda e, p=prefix: self._on_pos_change(e, p))
        menu.pack(fill="x", padx=5)

        frame_xy = ctk.CTkFrame(parent, fg_color="transparent")
        setattr(self, f"frame_{prefix}_xy", frame_xy)
        
        row_x = ctk.CTkFrame(frame_xy, fg_color="transparent")
        row_x.pack(fill="x", pady=5)
        ctk.CTkLabel(row_x, text=get_text("lbl_x_pct")).pack(side="left")
        
        var_x = ctk.DoubleVar(value=50.0)
        setattr(self, f"var_{prefix}_x", var_x)
        
        ent_x = ctk.CTkEntry(row_x, width=50); ent_x.insert(0, "50.0"); ent_x.pack(side="right", padx=2)
        slider_x = ctk.CTkSlider(row_x, from_=0, to=100, variable=var_x)
        slider_x.pack(side="right", fill="x", expand=True, padx=10)

        row_y = ctk.CTkFrame(frame_xy, fg_color="transparent")
        row_y.pack(fill="x", pady=5)
        ctk.CTkLabel(row_y, text=get_text("lbl_y_pct")).pack(side="left")
        
        var_y = ctk.DoubleVar(value=50.0)
        setattr(self, f"var_{prefix}_y", var_y)
        
        ent_y = ctk.CTkEntry(row_y, width=50); ent_y.insert(0, "50.0"); ent_y.pack(side="right", padx=2)
        slider_y = ctk.CTkSlider(row_y, from_=0, to=100, variable=var_y)
        slider_y.pack(side="right", fill="x", expand=True, padx=10)

        def on_slider_x(val): ent_x.delete(0, "end"); ent_x.insert(0, f"{float(val):.1f}"); self._auto_trigger()
        def on_entry_x(e):
            try: var_x.set(float(ent_x.get())); self._auto_trigger()
            except: pass
            
        def on_slider_y(val): ent_y.delete(0, "end"); ent_y.insert(0, f"{float(val):.1f}"); self._auto_trigger()
        def on_entry_y(e):
            try: var_y.set(float(ent_y.get())); self._auto_trigger()
            except: pass

        slider_x.configure(command=on_slider_x); ent_x.bind("<KeyRelease>", on_entry_x)
        slider_y.configure(command=on_slider_y); ent_y.bind("<KeyRelease>", on_entry_y)

    def _on_pos_change(self, selected, prefix):
        frame = getattr(self, f"frame_{prefix}_xy")
        if selected == get_text("opt_pos_custom"): frame.pack(fill="x", padx=5, pady=5)
        else: frame.pack_forget()
        self._auto_trigger()

    def _on_stamp_change(self, selected):
        if selected == get_text("opt_stamp_custom"): self.btn_upload_stamp.pack(fill="x", padx=5, pady=5)
        else: self.btn_upload_stamp.pack_forget()
        self._auto_trigger()

    def _upload_custom_stamp(self):
        path = filedialog.askopenfilename(filetypes=[("Resimler", "*.png *.jpg *.jpeg")])
        if path:
            self.custom_stamp_path = path
            self.btn_upload_stamp.configure(text=os.path.basename(path), fg_color="#388E3C")
            self._auto_trigger()

    # ==========================================
    # --- KOORDİNAT HESAPLAYICI ---
    # ==========================================
    def _get_xy(self, rect, pos_mode, tw, th, prefix):
        if pos_mode == get_text("opt_pos_tl"): return 15, 15
        elif pos_mode == get_text("opt_pos_tc"): return (rect.width - tw) / 2, 15
        elif pos_mode == get_text("opt_pos_tr"): return rect.width - tw - 15, 15
        elif pos_mode == get_text("opt_pos_ml"): return 15, (rect.height - th) / 2
        elif pos_mode == get_text("opt_pos_center"): return (rect.width - tw) / 2, (rect.height - th) / 2
        elif pos_mode == get_text("opt_pos_mr"): return rect.width - tw - 15, (rect.height - th) / 2
        elif pos_mode == get_text("opt_pos_bl"): return 15, rect.height - th - 15
        elif pos_mode == get_text("opt_pos_bc"): return (rect.width - tw) / 2, rect.height - th - 15
        elif pos_mode == get_text("opt_pos_br"): return rect.width - tw - 15, rect.height - th - 15
        else: 
            try:
                x_pct = getattr(self, f"var_{prefix}_x").get()
                y_pct = getattr(self, f"var_{prefix}_y").get()
                max_x = rect.width - tw
                max_y = rect.height - th
                return max_x * (x_pct / 100.0), max_y * (y_pct / 100.0)
            except: return 15, 15

    def _toggle_ui_state(self, state):
        self.btn_refresh.configure(state=state)
        self.btn_process.configure(state=state)
        if state == "normal" and self.total_pages > 1: self.nav_bar_pdf.pack(fill="x", pady=5)
        else: self.nav_bar_pdf.pack_forget()

    def load_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if path: self._load_file_logic(path)

    def _load_file_logic(self, path):
        try:
            doc = fitz.open(path)
            pw = ""
            if doc.is_encrypted:
                dialog = PasswordDialog(self.winfo_toplevel(), get_text("dialog_warning"), "Şifreyi girin:")
                pw = dialog.get_result()
                if not pw or not doc.authenticate(pw): doc.close(); return
            self.total_pages = len(doc)
            doc.close()
            
            self.current_pdf_path = path
            self.current_password = pw
            self.current_page_index = 0
            self.lbl_pdf_name.configure(text=os.path.basename(path), text_color=("black", "white"))
            
            self._toggle_ui_state("normal")
            self.update_live_preview()
        except: pass

    def clear_all(self):
        self.current_pdf_path = None; self.current_page_index = 0; self.total_pages = 0; self.base_high_res_image = None
        self.lbl_pdf_name.configure(text=get_text("msg_waiting_file"), text_color="gray")
        self._toggle_ui_state("disabled")
        self.create_preview_label()

    def _parse_pages(self, text, total):
        if not text or "tüm" in text.lower() or "all" in text.lower(): return list(range(total))
        pages = set()
        try:
            for part in text.split(","):
                part = part.strip()
                if "-" in part:
                    s, e = map(int, part.split("-")); pages.update(range(s-1, e))
                else: pages.add(int(part)-1)
            return [p for p in pages if 0 <= p < total]
        except: return list(range(total))

    def _get_font(self, page, style):
        is_b, is_i = get_text("opt_bold") in style, get_text("opt_italic") in style
        if is_b and is_i: f_path = "C:/Windows/Fonts/arialbi.ttf"
        elif is_b: f_path = "C:/Windows/Fonts/arialbd.ttf"
        elif is_i: f_path = "C:/Windows/Fonts/ariali.ttf"
        else: f_path = "C:/Windows/Fonts/arial.ttf"
        
        if sys.platform == "win32" and os.path.exists(f_path):
            try: page.insert_font(fontname="tr_cst", fontfile=f_path); return "tr_cst"
            except: pass
        if is_b and is_i: return "hebi" 
        elif is_b: return "hebo"
        elif is_i: return "hebo" 
        return "helv"

    def _apply_features_to_page(self, page, p_idx):
        rect = page.rect
        
        # 1. BATES NUMARASI VE DİNAMİK ROTASYON / SAYDAMLIK (Gelişmiş Filtre)
        bates_range = list(range(self.total_pages)) if self.var_bates_all_pages.get() else self._parse_pages(self.ent_bates_pages.get(), self.total_pages)
        if self.var_bates_enable.get() and p_idx in bates_range:
            bates_val = None
            custom_rules = self.ent_bates_custom.get().strip()
            
            if custom_rules:
                for rule in custom_rules.split(","):
                    if "=" in rule or ":" in rule:
                        delim = "=" if "=" in rule else ":"
                        rng, val = rule.split(delim, 1)
                        rng, val = rng.strip(), val.strip()
                        if "-" in rng:
                            s, e = map(int, rng.split("-"))
                            if s <= (p_idx + 1) <= e: bates_val = val; break
                        elif rng.isdigit() and int(rng) == (p_idx + 1):
                            bates_val = val; break

            if bates_val is not None:
                txt = bates_val
            else:
                prefix = self.ent_bates_prefix.get()
                try: start_no = int(self.ent_bates_start.get())
                except: start_no = 1
                try: rep_count = max(1, int(self.ent_bates_rep.get()))
                except: rep_count = 1
                
                try: order_idx = bates_range.index(p_idx)
                except: order_idx = 0
                
                current_num = start_no + (order_idx // rep_count)
                
                z_mode = self.var_bates_zeros.get()
                if "1" in z_mode or "Yok" in z_mode or "No" in z_mode: str_num = str(current_num)
                else: str_num = str(current_num).zfill(int(re.findall(r'\d+', z_mode)[0]))
                txt = f"{prefix}{str_num}"

            fn = self._get_font(page, self.var_bates_style.get())
            fz = self.slider_bates_size.get()
            tw = fitz.Font("hebo").text_length(txt, fontsize=fz)
            
            x, y = self._get_xy(rect, self.var_bates_pos.get(), tw, fz, "bates")
            
            b_op = self.slider_bates_opacity.get()
            b_rot = self.var_bates_rot.get()
            center_pt = fitz.Point(x + tw/2, y + fz/2)
            
            page.insert_text(fitz.Point(x, y + fz), txt, fontname=fn, fontsize=fz, color=(0.1, 0.1, 0.1), fill_opacity=b_op, morph=(center_pt, fitz.Matrix(-b_rot)))

        # 2. MÜHÜR & KAŞE VE DİNAMİK ROTASYON / SAYDAMLIK (Gelişmiş Filtre)
        stamp_range = list(range(self.total_pages)) if self.var_stamp_all_pages.get() else self._parse_pages(self.ent_stamp_pages.get(), self.total_pages)
        if stamp_mode := self.var_stamp_preset.get():
            if stamp_mode != get_text("opt_stamp_none") and p_idx in stamp_range:
                scale = self.slider_stamp_scale.get()
                s_op = self.slider_stamp_opacity.get()
                s_rot = self.var_stamp_rot.get()
                
                if stamp_mode == get_text("opt_stamp_custom") and self.custom_stamp_path:
                    try:
                        img = Image.open(self.custom_stamp_path).convert("RGBA")
                        
                        if s_op < 1.0:
                            alpha = img.split()[3]
                            alpha = alpha.point(lambda p: p * s_op)
                            img.putalpha(alpha)
                        
                        if s_rot != 0:
                            img = img.rotate(-s_rot, expand=True, resample=Image.BICUBIC)
                            
                        w, h = img.size
                        ratio = 150.0 / max(w, h) * scale
                        fw, fh = w * ratio, h * ratio
                        x, y = self._get_xy(rect, self.var_stamp_pos.get(), fw, fh, "stamp")
                        
                        import io
                        b = io.BytesIO(); img.save(b, format='PNG')
                        page.insert_image(fitz.Rect(x, y, x + fw, y + fh), stream=b.getvalue(), overlay=True)
                    except: pass
                elif stamp_mode != get_text("opt_stamp_custom"):
                    is_en = lang_manager.current_lang == "EN"
                    if get_text("opt_stamp_asli") == stamp_mode: color, txt = (0.1, 0.3, 0.8), "TRUE COPY" if is_en else "ASLI GİBİDİR"
                    elif get_text("opt_stamp_gizli") == stamp_mode: color, txt = (0.8, 0.1, 0.1), "CONFIDENTIAL" if is_en else "GİZLİDİR"
                    elif get_text("opt_stamp_onay") == stamp_mode: color, txt = (0.1, 0.6, 0.2), "APPROVED" if is_en else "ONAYLANDI"
                    else: color, txt = (0,0,0), "STAMP" if is_en else "MÜHÜR"
                    
                    fn = self._get_font(page, get_text("opt_bold"))
                    fz = 35 * scale
                    tw = fitz.Font("hebo").text_length(txt, fontsize=fz)
                    
                    x, y = self._get_xy(rect, self.var_stamp_pos.get(), tw, fz, "stamp")
                    center_pt = fitz.Point(x + tw/2, y + fz/2)
                    
                    page.insert_text(fitz.Point(x, y + fz), txt, fontname=fn, fontsize=fz, color=color, fill_opacity=s_op, morph=(center_pt, fitz.Matrix(-s_rot)))

        # 3. KVKK KARARTMA MOTORU
        c_mode = self.var_redact_color.get()
        if c_mode == get_text("opt_color_black"): rgb = (0,0,0)
        elif c_mode == get_text("opt_color_red"): rgb = (1,0,0)
        elif c_mode == get_text("opt_color_blue"): rgb = (0,0,1)
        elif c_mode == get_text("opt_color_gray"): rgb = (0.6,0.6,0.6)
        else: rgb = None 

        rects_to_process = []
        full_text = page.get_text("text")

        if self.var_kvkk_tc.get():
            for m in re.finditer(r"\b\d{11}\b", full_text): rects_to_process.extend(page.search_for(m.group()))
        if self.var_kvkk_id.get():
            for m in re.finditer(r"\b[A-Z0-9]{6,14}\b", full_text): rects_to_process.extend(page.search_for(m.group()))
        if self.var_kvkk_passport.get():
            for m in re.finditer(r"\b[A-Z]{1,2}\d{6,9}\b", full_text): rects_to_process.extend(page.search_for(m.group()))
        if self.var_kvkk_iban.get():
            for m in re.finditer(r"TR\d{24}", full_text): rects_to_process.extend(page.search_for(m.group()))
        if self.var_kvkk_phone.get():
            for m in re.finditer(r"\b(05\d{9}|5\d{9}|\+\d{10,13})\b", full_text): rects_to_process.extend(page.search_for(m.group()))
        if self.var_kvkk_nums.get():
            for m in re.finditer(r"\b\d+\b", full_text): rects_to_process.extend(page.search_for(m.group()))
            
        custom_txt = self.ent_custom_redact.get().strip()
        if custom_txt:
            for word in custom_txt.split(","):
                w = word.strip()
                if w: rects_to_process.extend(page.search_for(w))

        if rects_to_process:
            for r in set(rects_to_process): page.add_redact_annot(r, fill=rgb)
            page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)

    # ==========================================
    # --- ANTI-CRASH ÖNİZLEME MOTORU ---
    # ==========================================
    def create_preview_label(self):
        if hasattr(self, 'lbl_large_preview') and self.lbl_large_preview:
            self.canvas.delete(self.canvas_window)
            self.lbl_large_preview.destroy()
        self.lbl_large_preview = ctk.CTkLabel(self.canvas, text="Sol üstten bir dosya seçin.", font=ctk.CTkFont(size=14), text_color="gray")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.lbl_large_preview, anchor="center")
        self.lbl_large_preview.bind("<MouseWheel>", self._on_mousewheel)
        self.center_canvas_content()

    def update_live_preview(self):
        if not self.current_pdf_path: return
        self.create_preview_label()
        self.lbl_large_preview.configure(text=get_text("progress_wait"))
        threading.Thread(target=self._thread_render_preview, daemon=True).start()

    def _thread_render_preview(self):
        try:
            doc = fitz.open(self.current_pdf_path)
            if doc.is_encrypted: doc.authenticate(self.current_password)
            
            temp_bytes = doc.tobytes()
            doc.close()
            
            mem_doc = fitz.open("pdf", temp_bytes)
            page = mem_doc.load_page(self.current_page_index)
            
            self._apply_features_to_page(page, self.current_page_index)
            
            c_lvl = self.var_compress.get()
            dpi_val = 72 if "72" in c_lvl else 150
            
            pix = page.get_pixmap(dpi=dpi_val)
            mode = "RGBA" if pix.alpha else "RGB"
            pil_img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
            mem_doc.close()
            
            self.base_high_res_image = pil_img
            self.after(0, self.apply_zoom)
        except: pass

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
                
            self.lbl_pdf_page_info.configure(text=f"{self.current_page_index+1} / {self.total_pages}")
        except: pass

    def center_canvas_content(self, event=None):
        def _do_center():
            cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
            if cw <= 1 or ch <= 1: self.after(50, _do_center); return
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
        if self.current_page_index > 0: self.current_page_index -= 1; self.update_live_preview()
    def next_pdf_page(self): 
        if self.current_page_index < self.total_pages - 1: self.current_page_index += 1; self.update_live_preview()

    def start_macro_process(self):
        if not self.current_pdf_path: return
        
        pw1, pw2 = self.ent_encrypt1.get(), self.ent_encrypt2.get()
        if pw1 or pw2:
            if pw1 != pw2: messagebox.showwarning("Hata", "Girdiğiniz şifreler birbiriyle eşleşmiyor!"); return
            
        save_path = filedialog.asksaveasfilename(title="İşlenmiş PDF'i Kaydet", defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], initialfile="Makro_Islem_Sonucu.pdf")
        if not save_path: return

        self.progress = ProgressWindow(self.winfo_toplevel(), "Zincirleme İşlemler Uygulanıyor...\nLütfen Bekleyin.")
        threading.Thread(target=self._thread_process_save, args=(save_path,), daemon=True).start()

    def _thread_process_save(self, save_path):
        try:
            doc = fitz.open(self.current_pdf_path)
            if doc.is_encrypted: doc.authenticate(self.current_password)
            
            for p_idx in range(self.total_pages):
                # Her sayfa işlenirken yüklenme kutusunun donmasını engellemek için arayüzü zorla yenile
                if hasattr(self, 'progress') and self.progress.winfo_exists():
                    self.progress.update()

                page = doc.load_page(p_idx)
                self._apply_features_to_page(page, p_idx)
            
            c_lvl = self.var_compress.get()
            is_compress = "Yok" not in c_lvl and "No" not in c_lvl
            
            save_params = {"garbage": 4 if is_compress else 1, "clean": is_compress, "deflate": is_compress}
            
            enc_pw = self.ent_encrypt1.get()
            if enc_pw:
                save_params["encryption"] = fitz.PDF_ENCRYPT_AES_256
                save_params["owner_pw"] = enc_pw
                save_params["user_pw"] = enc_pw
            
            # --- UYAP UYUMLULUK VE GÜVENLİK GÜNCELLEMESİ ---
            # 1. Eklenen mühürlerin, Bates numaralarının veya form alanlarının imza yapısını bozmaması için düzleştiriyoruz
            try:
                for page in doc:
                    page.flatten_widgets()
            except: pass

            # 2. Yerel dosya yollarını ve bilgisayar adını temizlemek için meta veriyi sıfırlıyoruz
            doc.set_metadata({})
            try: doc.set_xml_metadata("")
            except: pass

            # 3. Sıkıştırma seçilmese bile UYAP yapısı için derin nesne temizliğini (garbage=4) zorunlu kılıyoruz
            save_params["garbage"] = 4
            save_params["clean"] = True
            save_params["deflate"] = True
            
            doc.save(save_path, **save_params)
            doc.close()

            from modules.history_manager import add_history
            add_history("🪄", "history_action_generic", ["Makro İşlemi", os.path.basename(save_path)], save_path)

            self.after(0, lambda: MacroSuccessDialog(self.winfo_toplevel(), get_text("dialog_success"), get_text("msg_macro_success"), save_path))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror(get_text("dialog_error"), str(e)))
        finally:
            if hasattr(self, 'progress'): self.after(0, self.progress.destroy)