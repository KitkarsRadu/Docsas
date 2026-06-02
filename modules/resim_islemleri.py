import customtkinter as ctk
from tkinter import filedialog, messagebox, Canvas, colorchooser
from PIL import Image, ImageOps, ImageTk
import fitz  
import os
import io
import sys
import tempfile
import threading
from modules.pdf_araclari import PasswordDialog, center_window
from modules.language_manager import get_text, lang_manager

# --- İŞLEM SONUCU İÇİN ÖZEL DİYALOG KUTUSU ---
class ActionDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, message, target_path=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x160")
        self.transient(parent) # Sadece ana pencerenin üstünde kilitlenir
        center_window(self, parent)
        self.target_path = target_path

        lbl = ctk.CTkLabel(self, text=message, font=ctk.CTkFont(size=14))
        lbl.pack(pady=30)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text=get_text("dialog_ok"), width=120, command=self.destroy).pack(side="left", padx=10)

        if target_path and os.path.exists(target_path):
            btn_open = ctk.CTkButton(btn_frame, text=get_text("dialog_open"), width=120, fg_color="#2E7D32", hover_color="#1B5E20", command=self.open_path)
            btn_open.pack(side="left", padx=10)

    def open_path(self):
        try:
            if sys.platform == "win32": os.startfile(self.target_path)
            elif sys.platform == "darwin":
                import subprocess
                subprocess.call(["open", self.target_path])
        except Exception: pass
        self.destroy()

# --- YÜKLENİYOR (PROGRESS) DİYALOGU ---
class ProgressWindow(ctk.CTkToplevel):
    def __init__(self, parent, message=""):
        if not message:
            message = get_text("progress_processing")
            
        super().__init__(parent)
        self.title(get_text("progress_wait"))
        self.geometry("350x150")
        self.transient(parent) # Chrome'un üstüne yapışmasını engeller
        center_window(self, parent)
        self.protocol("WM_DELETE_WINDOW", self.disable_close)
        self.grab_set()

        lbl = ctk.CTkLabel(self, text=message, font=ctk.CTkFont(size=14, weight="bold"))
        lbl.pack(pady=(30, 10))

        self.progressbar = ctk.CTkProgressBar(self, mode="indeterminate", width=250)
        self.progressbar.pack(pady=10)
        self.progressbar.start()

    def disable_close(self): 
        pass
# ====================================================
# --- MOUSE İLE ETKİLEŞİMLİ 4 KENARLI GÖRSEL KIRPMA EDİTÖRÜ ---
# ====================================================
class InteractiveCropDialog(ctk.CTkToplevel):
    def __init__(self, parent, data, safe_doc_func, on_apply_callback):
        super().__init__(parent)
        self.title(get_text("crop_editor_title"))
        self.geometry("1100x850")
        self.transient(parent) # Bağımsız masaüstü kilidini kaldırır
        self.update_idletasks() 
        center_window(self, parent)
        self.grab_set()
        
        self.data = data
        self.safe_doc_func = safe_doc_func
        self.on_apply_callback = on_apply_callback
        self.zoom_factor = 1.0
        
        top_wrapper = ctk.CTkFrame(self, fg_color="transparent")
        top_wrapper.pack(fill="x", pady=10, padx=20)
        
        row1 = ctk.CTkFrame(top_wrapper, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 10))
        
        mod_frame = ctk.CTkFrame(row1, fg_color=("gray85", "gray20"), corner_radius=8)
        mod_frame.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(mod_frame, text=get_text("crop_mode_title"), font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10, pady=5)
        self.var_crop_mode = ctk.StringVar(value=data.get('crop_mode', get_text("opt_mode_shrink")))
        ctk.CTkSegmentedButton(mod_frame, values=[get_text("opt_mode_shrink"), get_text("opt_mode_mask")], variable=self.var_crop_mode, command=lambda v: self.redraw()).pack(side="left", padx=10)
        
        self.color_container = ctk.CTkFrame(mod_frame, fg_color="transparent")
        self.color_container.pack(side="left", padx=10)
        
        self.custom_color_rgb = data.get('crop_color_custom_rgb', None)
        saved_color = data.get('crop_color_name', "")
        
        current_values = [get_text("opt_mask_white"), get_text("opt_mask_black")]
        custom_text = "Custom Color" if lang_manager.current_lang == "EN" else "Özel Renk"
        
        if self.custom_color_rgb:
            start_val = custom_text
        elif "black" in saved_color.lower() or "siyah" in saved_color.lower():
            start_val = get_text("opt_mask_black")
        else:
            start_val = get_text("opt_mask_white")
            
        self.var_mask_color = ctk.StringVar(value=start_val)
        self.opt_mask = ctk.CTkOptionMenu(self.color_container, values=current_values, variable=self.var_mask_color, width=120, command=self._on_preset_color)
        self.opt_mask.pack(side="left")
        
        self.btn_custom_color = ctk.CTkButton(self.color_container, text="🎨", width=30, fg_color=("gray75", "gray30"), text_color=("black", "white"), command=self.pick_custom_color)
        self.btn_custom_color.pack(side="left", padx=5)

        if self.custom_color_rgb:
            r, g, b = [int(x*255) for x in self.custom_color_rgb]
            hex_c = f"#{r:02x}{g:02x}{b:02x}"
            text_c = "white" if (r*0.299 + g*0.587 + b*0.114) < 186 else "black"
            self.btn_custom_color.configure(fg_color=hex_c, text_color=text_c)
            self.opt_mask.configure(values=current_values + [custom_text])

        self.var_gray = ctk.BooleanVar(value=data.get('grayscale', False))
        ctk.CTkCheckBox(row1, text=get_text("chk_page_gray"), variable=self.var_gray, text_color=("black", "white"), command=self.load_and_draw_image).pack(side="right", padx=10)

        row2 = ctk.CTkFrame(top_wrapper, fg_color="transparent")
        row2.pack(fill="x")
        
        zoom_frame = ctk.CTkFrame(row2, fg_color="transparent")
        zoom_frame.pack(side="top", anchor="center")
        ctk.CTkButton(zoom_frame, text="🔄 Döndür", width=100, fg_color="#1E88E5", hover_color="#1565C0", text_color="white", command=self.rotate_inside).pack(side="left", padx=5)
        ctk.CTkButton(zoom_frame, text=get_text("btn_zoom_out_text"), width=100, fg_color=("gray75", "gray30"), hover_color=("gray65", "gray20"), text_color=("black", "white"), command=lambda: self.change_zoom(-0.2)).pack(side="left", padx=5)
        ctk.CTkButton(zoom_frame, text=get_text("btn_fit"), width=100, fg_color=("gray75", "gray30"), hover_color=("gray65", "gray20"), text_color=("black", "white"), command=lambda: self.change_zoom("fit")).pack(side="left", padx=5)
        ctk.CTkButton(zoom_frame, text=get_text("btn_zoom_in_text"), width=100, fg_color=("gray75", "gray30"), hover_color=("gray65", "gray20"), text_color=("black", "white"), command=lambda: self.change_zoom(0.2)).pack(side="left", padx=5)

        self.canvas_frame = ctk.CTkFrame(self)
        self.canvas_frame.pack(fill="both", expand=True, pady=5, padx=20)
        
        canvas_bg = "#2B2B2B" if ctk.get_appearance_mode() == "Dark" else "#E0E0E0"
        self.canvas = Canvas(self.canvas_frame, bg=canvas_bg, highlightthickness=0)
        self.v_scroll = ctk.CTkScrollbar(self.canvas_frame, orientation="vertical", command=self.canvas.yview)
        self.h_scroll = ctk.CTkScrollbar(self.canvas_frame, orientation="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)
        
        self.v_scroll.pack(side="right", fill="y")
        self.h_scroll.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.crop_left = 0; self.crop_top = 0
        self.crop_right = 800; self.crop_bottom = 650
        self.active_edge = None
        self.resize_timer = None
        
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        bot_frame = ctk.CTkFrame(self, fg_color="transparent")
        bot_frame.pack(fill="x", pady=10, padx=20)

        ctk.CTkButton(bot_frame, text=get_text("btn_reset"), width=120, fg_color=("gray75", "gray30"), hover_color=("gray65", "gray20"), text_color=("black", "white"), command=self.reset).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(bot_frame, text=get_text("btn_crop_apply"), width=200, font=ctk.CTkFont(weight="bold"), fg_color="#F57C00", hover_color="#E65100", text_color="white", command=self.apply).pack(side="left", expand=True, padx=5)

        self.after(200, self.load_and_draw_image)

    def rotate_inside(self):
        if self.crop_left == self.cx and self.crop_top == self.cy and self.crop_right == self.cx + self.disp_w and self.crop_bottom == self.cy + self.disp_h:
            self.data['crop_box_pct'] = None
        else:
            x1 = (self.crop_left - self.cx) / self.disp_w
            y1 = (self.crop_top - self.cy) / self.disp_h
            x2 = (self.crop_right - self.cx) / self.disp_w
            y2 = (self.crop_bottom - self.cy) / self.disp_h
            self.data['crop_box_pct'] = (x1, y1, x2, y2)

        self.data['rotation'] = (self.data['rotation'] + 90) % 360
        if self.data.get('crop_box_pct'):
            x1, y1, x2, y2 = self.data['crop_box_pct']
            self.data['crop_box_pct'] = (1.0 - y2, x1, 1.0 - y1, x2)
            
        self.load_and_draw_image()

    def _on_canvas_resize(self, event):
        if self.resize_timer: self.after_cancel(self.resize_timer)
        self.resize_timer = self.after(100, self.apply_zoom_and_draw)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _on_preset_color(self, val):
        self.custom_color_rgb = None
        self.btn_custom_color.configure(fg_color=("gray75", "gray30"), text_color=("black", "white"))
        current_values = [get_text("opt_mask_white"), get_text("opt_mask_black")]
        self.opt_mask.configure(values=current_values)
        self.redraw()

    def pick_custom_color(self):
        color_data = colorchooser.askcolor(title="Renk Seç", parent=self)
        if color_data and color_data[0]:
            r, g, b = color_data[0]
            self.custom_color_rgb = (r/255.0, g/255.0, b/255.0)
            custom_text = "Custom Color" if lang_manager.current_lang == "EN" else "Özel Renk"
            current_values = [get_text("opt_mask_white"), get_text("opt_mask_black")]
            self.opt_mask.configure(values=current_values + [custom_text])
            self.var_mask_color.set(custom_text) 
            hex_c = color_data[1]
            text_c = "white" if (r*0.299 + g*0.587 + b*0.114) < 186 else "black"
            self.btn_custom_color.configure(fg_color=hex_c, text_color=text_c)
            self.redraw()

    def change_zoom(self, amount):
        if amount == "fit": 
            self.zoom_factor = 1.0
        else: 
            self.zoom_factor = max(0.2, min(self.zoom_factor + amount, 3.0))
        self.apply_zoom_and_draw()
        if amount == "fit":
            self.canvas.xview_moveto(0)
            self.canvas.yview_moveto(0)

    def load_and_draw_image(self):
        doc = self.safe_doc_func(self.data['source_path'], self.data.get('password', ''))
        page = doc.load_page(self.data.get('page_num', 0))
        
        cs = fitz.csGRAY if self.var_gray.get() else fitz.csRGB
        pix = page.get_pixmap(dpi=150, colorspace=cs)
        mode = "L" if self.var_gray.get() else ("RGBA" if pix.alpha else "RGB")
        img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
        if mode == "L": img = img.convert("RGB")
        doc.close()

        if self.data['rotation'] != 0:
            img = img.rotate(-self.data['rotation'], expand=True, resample=Image.BICUBIC)
            
        self.base_pil_image = img
        self.img_w, self.img_h = img.size
        self.apply_zoom_and_draw()

    def apply_zoom_and_draw(self):
        if not hasattr(self, 'img_w') or not hasattr(self, 'img_h'): return
        self.canvas_frame.update_idletasks()
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        
        if cw < 10 or ch < 10: return

        base_scale = min((cw - 40) / self.img_w, (ch - 40) / self.img_h)
        scale = base_scale * self.zoom_factor
        
        self.disp_w = int(self.img_w * scale)
        self.disp_h = int(self.img_h * scale)
        
        self.display_img = self.base_pil_image.resize((self.disp_w, self.disp_h), Image.Resampling.LANCZOS)
        
        self.cx = max(20, (cw - self.disp_w) // 2)
        self.cy = max(20, (ch - self.disp_h) // 2)

        if self.data.get('crop_box_pct'):
            x1, y1, x2, y2 = self.data['crop_box_pct']
            self.crop_left = self.cx + int(x1 * self.disp_w)
            self.crop_top = self.cy + int(y1 * self.disp_h)
            self.crop_right = self.cx + int(x2 * self.disp_w)
            self.crop_bottom = self.cy + int(y2 * self.disp_h)
        else:
            self.crop_left = self.cx; self.crop_top = self.cy
            self.crop_right = self.cx + self.disp_w; self.crop_bottom = self.cy + self.disp_h

        self.tk_img = ImageTk.PhotoImage(self.display_img)
        self.redraw()

    def center_canvas(self):
        max_w = max(self.canvas.winfo_width(), self.disp_w + 40)
        max_h = max(self.canvas.winfo_height(), self.disp_h + 40)
        self.canvas.config(scrollregion=(0, 0, max_w, max_h))

    def redraw(self):
        self.canvas.delete("all")
        self.canvas.create_image(self.cx, self.cy, image=self.tk_img, anchor="nw")
        
        overlay_color = "black"
        if self.var_crop_mode.get() == get_text("opt_mode_mask"):
            if self.custom_color_rgb:
                r, g, b = [int(x*255) for x in self.custom_color_rgb]
                overlay_color = f"#{r:02x}{g:02x}{b:02x}"
            else:
                color_name = self.var_mask_color.get()
                overlay_color = "white" if color_name == get_text("opt_mask_white") else "black"
                
        self.canvas.create_rectangle(self.cx, self.cy, self.cx + self.disp_w, self.crop_top, fill=overlay_color, stipple="gray50", outline="")
        self.canvas.create_rectangle(self.cx, self.crop_bottom, self.cx + self.disp_w, self.cy + self.disp_h, fill=overlay_color, stipple="gray50", outline="")
        self.canvas.create_rectangle(self.cx, self.crop_top, self.crop_left, self.crop_bottom, fill=overlay_color, stipple="gray50", outline="")
        self.canvas.create_rectangle(self.crop_right, self.crop_top, self.cx + self.disp_w, self.crop_bottom, fill=overlay_color, stipple="gray50", outline="")
        
        self.canvas.create_rectangle(self.crop_left, self.crop_top, self.crop_right, self.crop_bottom, outline="#00E676", width=3)
        
        r = 8
        self.canvas.create_oval(self.crop_left-r, (self.crop_top+self.crop_bottom)//2-r, self.crop_left+r, (self.crop_top+self.crop_bottom)//2+r, fill="#00E676")
        self.canvas.create_oval(self.crop_right-r, (self.crop_top+self.crop_bottom)//2-r, self.crop_right+r, (self.crop_top+self.crop_bottom)//2+r, fill="#00E676")
        self.canvas.create_oval((self.crop_left+self.crop_right)//2-r, self.crop_top-r, (self.crop_left+self.crop_right)//2+r, self.crop_top+r, fill="#00E676")
        self.canvas.create_oval((self.crop_left+self.crop_right)//2-r, self.crop_bottom-r, (self.crop_left+self.crop_right)//2+r, self.crop_bottom+r, fill="#00E676")
        self.center_canvas()

    def on_press(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        threshold = 20; self.active_edge = None
        if abs(x - self.crop_left) < threshold and self.crop_top <= y <= self.crop_bottom: self.active_edge = "left"
        elif abs(x - self.crop_right) < threshold and self.crop_top <= y <= self.crop_bottom: self.active_edge = "right"
        elif abs(y - self.crop_top) < threshold and self.crop_left <= x <= self.crop_right: self.active_edge = "top"
        elif abs(y - self.crop_bottom) < threshold and self.crop_left <= x <= self.crop_right: self.active_edge = "bottom"

    def on_drag(self, event):
        if not self.active_edge: return
        x = max(self.cx, min(self.canvas.canvasx(event.x), self.cx + self.disp_w))
        y = max(self.cy, min(self.canvas.canvasy(event.y), self.cy + self.disp_h))
        
        if self.active_edge == "left": self.crop_left = min(x, self.crop_right - 20)
        elif self.active_edge == "right": self.crop_right = max(x, self.crop_left + 20)
        elif self.active_edge == "top": self.crop_top = min(y, self.crop_bottom - 20)
        elif self.active_edge == "bottom": self.crop_bottom = max(y, self.crop_top + 20)
        self.redraw()

    def on_release(self, event): self.active_edge = None

    def reset(self):
        self.crop_left = self.cx; self.crop_top = self.cy; self.crop_right = self.cx + self.disp_w; self.crop_bottom = self.cy + self.disp_h
        self.redraw()

    def apply(self):
        self.data['grayscale'] = self.var_gray.get()
        self.data['crop_mode'] = self.var_crop_mode.get()
        self.data['crop_color_name'] = self.var_mask_color.get()
        self.data['crop_color_custom_rgb'] = self.custom_color_rgb
        
        if self.crop_left == self.cx and self.crop_top == self.cy and self.crop_right == self.cx + self.disp_w and self.crop_bottom == self.cy + self.disp_h:
            self.data['crop_box_pct'] = None
        else:
            x1 = (self.crop_left - self.cx) / self.disp_w
            y1 = (self.crop_top - self.cy) / self.disp_h
            x2 = (self.crop_right - self.cx) / self.disp_w
            y2 = (self.crop_bottom - self.cy) / self.disp_h
            self.data['crop_box_pct'] = (x1, y1, x2, y2)
            
        self.on_apply_callback()
        self.destroy()


class ResimIslemleriSayfasi(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        
        self.t1_data_list = []; self.t1_cards_list = []
        self.t2_data_list = []; self.t2_cards_list = []

        self.odd_state_t1 = False; self.even_state_t1 = False
        self.odd_state_t2 = False; self.even_state_t2 = False

        self.is_dragging = False
        self.temp_dir = tempfile.mkdtemp()
        
        self.tab_img_to_pdf_name = get_text("tab_img_to_pdf")
        self.tab_pdf_to_img_name = get_text("tab_pdf_to_img")

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_img_to_pdf = self.tabview.add(self.tab_img_to_pdf_name)
        self.tab_pdf_to_img = self.tabview.add(self.tab_pdf_to_img_name)
        
        self.setup_img_to_pdf_tab()
        self.setup_pdf_to_img_tab()
        
        self.update_language()

    def update_language(self):
        try:
            self.tabview._segmented_button._buttons_dict[self.tab_img_to_pdf_name].configure(text=get_text("tab_img_to_pdf"))
            self.tabview._segmented_button._buttons_dict[self.tab_pdf_to_img_name].configure(text=get_text("tab_pdf_to_img"))
        except: pass

        # Buton Çevirileri
        if hasattr(self, 'btn_add_t1'): self.btn_add_t1.configure(text=get_text("btn_add_img"))
        if hasattr(self, 'btn_blank_t1'): self.btn_blank_t1.configure(text=get_text("btn_add_blank"))
        if hasattr(self, 'btn_del_t1'): self.btn_del_t1.configure(text=get_text("btn_del_selected"))
        if hasattr(self, 'btn_rot_t1'): self.btn_rot_t1.configure(text=get_text("btn_rot_selected"))
        if hasattr(self, 'btn_gray_t1'): self.btn_gray_t1.configure(text=get_text("btn_grayscale"))
        if hasattr(self, 'btn_clear_t1'): self.btn_clear_t1.configure(text=get_text("btn_clear"))
        
        if hasattr(self, 'lbl_set_t1'): self.lbl_set_t1.configure(text=get_text("lbl_save_settings"))
        if hasattr(self, 'lbl_pap_t1'): self.lbl_pap_t1.configure(text=get_text("lbl_paper_size"))
        if hasattr(self, 'lbl_mar_t1'): self.lbl_mar_t1.configure(text=get_text("lbl_margin"))
    
        if hasattr(self, 'btn_save_t1'): self.btn_save_t1.configure(text=get_text("btn_save_as_pdf"))

        if hasattr(self, 'btn_add_t2'): self.btn_add_t2.configure(text=get_text("btn_select_pdf"))
        if hasattr(self, 'btn_blank_t2'): self.btn_blank_t2.configure(text=get_text("btn_add_blank"))
        if hasattr(self, 'btn_del_t2'): self.btn_del_t2.configure(text=get_text("btn_del_selected"))
        if hasattr(self, 'btn_rot_t2'): self.btn_rot_t2.configure(text=get_text("btn_rot_selected"))
        if hasattr(self, 'btn_gray_t2'): self.btn_gray_t2.configure(text=get_text("btn_grayscale"))
        if hasattr(self, 'btn_clear_t2'): self.btn_clear_t2.configure(text=get_text("btn_clear"))
        
        if hasattr(self, 'lbl_set_t2'): self.lbl_set_t2.configure(text=get_text("lbl_target_format"))
        if hasattr(self, 'lbl_pap_t2'): self.lbl_pap_t2.configure(text=get_text("lbl_paper_size"))
        if hasattr(self, 'lbl_mar_t2'): self.lbl_mar_t2.configure(text=get_text("lbl_margin"))
        if hasattr(self, 'btn_save_t2'): self.btn_save_t2.configure(text=get_text("btn_extract_images"))

    

        # Bilgi Notları Çevirisi
        if hasattr(self, 'lbl_info_t1'):
            info_text = "Docsas: Önizlemede gördüğünüz tüm resimler, sayfa ayarlarınıza uygun şekilde TEK BİR PDF belgesi olarak birleştirilir." if lang_manager.current_lang == "TR" else "Docsas: All previewed images will be combined into a SINGLE PDF document according to your page settings."
            self.lbl_info_t1.configure(text=info_text)

        if hasattr(self, 'lbl_info_t2'):
            info_text2 = "Docsas: Önizlemede gördüğünüz HER BİR sayfa, seçeceğiniz klasörün içine (Docsas_Resim_Ciktilari) ayrı ayrı resim dosyaları olarak kaydedilecektir." if lang_manager.current_lang == "TR" else "Docsas: EACH page previewed will be saved as a separate image file inside your chosen folder (Docsas_Resim_Ciktilari)."
            self.lbl_info_t2.configure(text=info_text2)

        opts_paper = [get_text("opt_paper_orig"), "A4 (210x297mm)", "A3 (297x420mm)", "A5 (148x210mm)", "Letter (8.5x11\")", "Legal (8.5x14\")"]
        if hasattr(self, 'opt_paper_t1'):
            self.opt_paper_t1.configure(values=opts_paper)
            if self.var_paper_t1.get() not in opts_paper: self.var_paper_t1.set(opts_paper[0])
        if hasattr(self, 'opt_paper_t2'):
            self.opt_paper_t2.configure(values=opts_paper)
            if self.var_paper_t2.get() not in opts_paper: self.var_paper_t2.set(opts_paper[0])

        self._update_odd_even_btn_texts(1)
        self._update_odd_even_btn_texts(2)

        for data in self.t1_data_list + self.t2_data_list:
            if 'w_chk' in data and data['w_chk'].winfo_exists():
                data['w_chk'].configure(text=get_text("chk_select"))

    def _get_safe_doc(self, filepath, password=""):
        if filepath == "BLANK": return None
        if filepath.lower().endswith(('.png', '.jpg', '.jpeg')):
            img_doc = fitz.open(filepath)
            pdf_bytes = img_doc.convert_to_pdf()
            img_doc.close()
            return fitz.open(stream=pdf_bytes, filetype="pdf")
        else:
            doc = fitz.open(filepath)
            if doc.is_encrypted and password: doc.authenticate(password)
            return doc

    # ==========================================
    # --- 1. SEKME: RESİMDEN PDF'E EKRANI ---
    # ==========================================
    def setup_img_to_pdf_tab(self):
        self.tab_img_to_pdf.grid_columnconfigure(0, weight=1)
        self.tab_img_to_pdf.grid_columnconfigure(1, weight=0, minsize=350)
        self.tab_img_to_pdf.grid_rowconfigure(0, weight=1)

        left_frame = ctk.CTkFrame(self.tab_img_to_pdf, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        top_bar = ctk.CTkFrame(left_frame, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 10))
        
        btn_frame1 = ctk.CTkFrame(top_bar, fg_color="transparent")
        btn_frame1.pack(side="left")
        self.btn_add_t1 = ctk.CTkButton(btn_frame1, text=get_text("btn_add_img"), width=130, font=ctk.CTkFont(weight="bold"), command=lambda: self.add_files(1), fg_color="#E53935", hover_color="#C62828")
        self.btn_add_t1.pack(side="left", padx=5)
        self.btn_blank_t1 = ctk.CTkButton(btn_frame1, text=get_text("btn_add_blank"), width=130, fg_color="gray50", command=lambda: self.add_blank_page(1))
        self.btn_blank_t1.pack(side="left", padx=5)

        btn_frame2 = ctk.CTkFrame(top_bar, fg_color="transparent")
        btn_frame2.pack(side="left", padx=10)
        self.btn_odd_t1 = ctk.CTkButton(btn_frame2, text=get_text("btn_sel_odd"), width=140, fg_color="#1E88E5", command=lambda: self.select_odd_even(1, "odd"))
        self.btn_odd_t1.pack(side="left", padx=5)
        self.btn_even_t1 = ctk.CTkButton(btn_frame2, text=get_text("btn_sel_even"), width=140, fg_color="#1E88E5", command=lambda: self.select_odd_even(1, "even"))
        self.btn_even_t1.pack(side="left", padx=5)

        btn_frame3 = ctk.CTkFrame(top_bar, fg_color="transparent")
        btn_frame3.pack(side="left")
        self.btn_del_t1 = ctk.CTkButton(btn_frame3, text=get_text("btn_del_selected"), width=130, fg_color="#E53935", hover_color="#C62828", command=lambda: self.batch_delete(1))
        self.btn_del_t1.pack(side="left", padx=5)
        self.btn_rot_t1 = ctk.CTkButton(btn_frame3, text=get_text("btn_rot_selected"), width=130, fg_color="#F57C00", hover_color="#E65100", command=lambda: self.batch_rotate(1))
        self.btn_rot_t1.pack(side="left", padx=5)
        self.btn_gray_t1 = ctk.CTkButton(btn_frame3, text=get_text("btn_grayscale"), width=130, fg_color="#424242", hover_color="#212121", command=lambda: self.batch_grayscale(1))
        self.btn_gray_t1.pack(side="left", padx=5)

        self.btn_clear_t1 = ctk.CTkButton(top_bar, text=get_text("btn_clear"), width=90, command=lambda: self.clear_all(1), fg_color="transparent", border_width=1, text_color=("black", "white"))
        self.btn_clear_t1.pack(side="right")

        self.t1_scroll_frame = ctk.CTkScrollableFrame(left_frame)
        self.t1_scroll_frame.pack(fill="both", expand=True)

        # Sağ Menü Ayarları (350px Genişlik)
        right_frame = ctk.CTkFrame(self.tab_img_to_pdf, width=350)
        right_frame.grid(row=0, column=1, sticky="ns", padx=10, pady=10)
        right_frame.pack_propagate(False)

        top_settings = ctk.CTkFrame(right_frame, fg_color="transparent")
        top_settings.pack(side="top", fill="both", expand=True)

        self.lbl_set_t1 = ctk.CTkLabel(top_settings, text=get_text("lbl_save_settings"), font=ctk.CTkFont(size=18, weight="bold"))
        self.lbl_set_t1.pack(pady=(20, 10))

        

        self.lbl_pap_t1 = ctk.CTkLabel(top_settings, text=get_text("lbl_paper_size"), anchor="w", font=ctk.CTkFont(weight="bold"))
        self.lbl_pap_t1.pack(fill="x", padx=20, pady=(15, 0))
        self.var_paper_t1 = ctk.StringVar(value=get_text("opt_paper_orig"))
        opts_paper = [get_text("opt_paper_orig"), "A4 (210x297mm)", "A3 (297x420mm)", "A5 (148x210mm)", "Letter (8.5x11\")", "Legal (8.5x14\")"]
        self.opt_paper_t1 = ctk.CTkOptionMenu(top_settings, values=opts_paper, variable=self.var_paper_t1, command=lambda v: self.apply_right_menu_settings(1))
        self.opt_paper_t1.pack(fill="x", padx=20, pady=5)

        self.lbl_mar_t1 = ctk.CTkLabel(top_settings, text=get_text("lbl_margin"), anchor="w", font=ctk.CTkFont(weight="bold"))
        self.lbl_mar_t1.pack(fill="x", padx=20, pady=(15, 0))
        self.var_padding_t1 = ctk.StringVar(value="%0")
        opts_pad = ["%0", "%1", "%2", "%3", "%4", "%5", "%10", "%15", "%20", "%25"]
        self.opt_padding_t1 = ctk.CTkOptionMenu(top_settings, values=opts_pad, variable=self.var_padding_t1, command=lambda v: self.apply_right_menu_settings(1))
        self.opt_padding_t1.pack(fill="x", padx=20, pady=5)
        
        bottom_settings = ctk.CTkFrame(right_frame, fg_color="transparent")
        bottom_settings.pack(side="bottom", fill="x", pady=20)

        info_box = ctk.CTkFrame(bottom_settings, fg_color=("#FFEBEE", "#1565C0"), corner_radius=8)
        info_box.pack(fill="x", padx=10, pady=(0, 15))
        
        # Dinamik Bilgi Kutusu
        self.lbl_info_t1 = ctk.CTkLabel(info_box, text="", text_color=("#B71C1C", "#BBDEFB"), font=ctk.CTkFont(size=11, weight="bold"), justify="center", wraplength=310)
        self.lbl_info_t1.pack(padx=10, pady=10)

        self.btn_save_t1 = ctk.CTkButton(bottom_settings, text=get_text("btn_save_as_pdf"), font=ctk.CTkFont(size=16, weight="bold"), height=50, fg_color="#E53935", hover_color="#C62828", command=self.start_save_to_pdf)
        self.btn_save_t1.pack(fill="x", padx=20)

    # ==========================================
    # --- 2. SEKME: PDF'Yİ RESİMLERE ÇEVİR ---
    # ==========================================
    def setup_pdf_to_img_tab(self):
        self.tab_pdf_to_img.grid_columnconfigure(0, weight=1)
        self.tab_pdf_to_img.grid_columnconfigure(1, weight=0, minsize=350)
        self.tab_pdf_to_img.grid_rowconfigure(0, weight=1)

        left_frame = ctk.CTkFrame(self.tab_pdf_to_img, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        top_bar = ctk.CTkFrame(left_frame, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 10))

        btn_frame1 = ctk.CTkFrame(top_bar, fg_color="transparent")
        btn_frame1.pack(side="left")
        self.btn_add_t2 = ctk.CTkButton(btn_frame1, text=get_text("btn_select_pdf"), width=130, font=ctk.CTkFont(weight="bold"), command=lambda: self.add_files(2), fg_color="#1E88E5", hover_color="#1565C0")
        self.btn_add_t2.pack(side="left", padx=5)
        self.btn_blank_t2 = ctk.CTkButton(btn_frame1, text=get_text("btn_add_blank"), width=130, fg_color="gray50", command=lambda: self.add_blank_page(2))
        self.btn_blank_t2.pack(side="left", padx=5)
        
        btn_frame2 = ctk.CTkFrame(top_bar, fg_color="transparent")
        btn_frame2.pack(side="left", padx=10)
        self.btn_odd_t2 = ctk.CTkButton(btn_frame2, text=get_text("btn_sel_odd"), width=140, fg_color="#1E88E5", command=lambda: self.select_odd_even(2, "odd"))
        self.btn_odd_t2.pack(side="left", padx=5)
        self.btn_even_t2 = ctk.CTkButton(btn_frame2, text=get_text("btn_sel_even"), width=140, fg_color="#1E88E5", command=lambda: self.select_odd_even(2, "even"))
        self.btn_even_t2.pack(side="left", padx=5)

        btn_frame3 = ctk.CTkFrame(top_bar, fg_color="transparent")
        btn_frame3.pack(side="left")
        self.btn_del_t2 = ctk.CTkButton(btn_frame3, text=get_text("btn_del_selected"), width=130, fg_color="#E53935", hover_color="#C62828", command=lambda: self.batch_delete(2))
        self.btn_del_t2.pack(side="left", padx=5)
        self.btn_rot_t2 = ctk.CTkButton(btn_frame3, text=get_text("btn_rot_selected"), width=130, fg_color="#F57C00", hover_color="#E65100", command=lambda: self.batch_rotate(2))
        self.btn_rot_t2.pack(side="left", padx=5)
        self.btn_gray_t2 = ctk.CTkButton(btn_frame3, text=get_text("btn_grayscale"), width=130, fg_color="#424242", hover_color="#212121", command=lambda: self.batch_grayscale(2))
        self.btn_gray_t2.pack(side="left", padx=5)

        self.btn_clear_t2 = ctk.CTkButton(top_bar, text=get_text("btn_clear"), width=90, command=lambda: self.clear_all(2), fg_color="transparent", border_width=1, text_color=("black", "white"))
        self.btn_clear_t2.pack(side="right")

        self.t2_scroll_frame = ctk.CTkScrollableFrame(left_frame)
        self.t2_scroll_frame.pack(fill="both", expand=True)

        right_frame = ctk.CTkFrame(self.tab_pdf_to_img, width=350)
        right_frame.grid(row=0, column=1, sticky="ns", padx=10, pady=10)
        right_frame.pack_propagate(False)

        top_settings = ctk.CTkFrame(right_frame, fg_color="transparent")
        top_settings.pack(side="top", fill="both", expand=True)

        self.lbl_set_t2 = ctk.CTkLabel(top_settings, text=get_text("lbl_target_format"), font=ctk.CTkFont(size=18, weight="bold"))
        self.lbl_set_t2.pack(pady=(20, 10))
        
        self.var_target_format = ctk.StringVar(value="PNG")
        formats = ["PNG", "JPG", "JPEG"]
        self.opt_target_format = ctk.CTkOptionMenu(top_settings, values=formats, variable=self.var_target_format)
        self.opt_target_format.pack(fill="x", padx=20, pady=10)

        self.lbl_pap_t2 = ctk.CTkLabel(top_settings, text=get_text("lbl_paper_size"), anchor="w", font=ctk.CTkFont(weight="bold"))
        self.lbl_pap_t2.pack(fill="x", padx=20, pady=(15, 0))
        self.var_paper_t2 = ctk.StringVar(value=get_text("opt_paper_orig"))
        opts_paper = [get_text("opt_paper_orig"), "A4 (210x297mm)", "A3 (297x420mm)", "A5 (148x210mm)", "Letter (8.5x11\")", "Legal (8.5x14\")"]
        self.opt_paper_t2 = ctk.CTkOptionMenu(top_settings, values=opts_paper, variable=self.var_paper_t2, command=lambda v: self.apply_right_menu_settings(2))
        self.opt_paper_t2.pack(fill="x", padx=20, pady=5)

        self.lbl_mar_t2 = ctk.CTkLabel(top_settings, text=get_text("lbl_margin"), anchor="w", font=ctk.CTkFont(weight="bold"))
        self.lbl_mar_t2.pack(fill="x", padx=20, pady=(15, 0))
        self.var_padding_t2 = ctk.StringVar(value="%0")
        opts_pad = ["%0", "%1", "%2", "%3", "%4", "%5", "%10", "%15", "%20", "%25"]
        self.opt_padding_t2 = ctk.CTkOptionMenu(top_settings, values=opts_pad, variable=self.var_padding_t2, command=lambda v: self.apply_right_menu_settings(2))
        self.opt_padding_t2.pack(fill="x", padx=20, pady=5)

        bottom_settings = ctk.CTkFrame(right_frame, fg_color="transparent")
        bottom_settings.pack(side="bottom", fill="x", pady=20)

        info_box2 = ctk.CTkFrame(bottom_settings, fg_color=("#E3F2FD", "#1565C0"), corner_radius=8)
        info_box2.pack(fill="x", padx=10, pady=(0, 15))
        
        self.lbl_info_t2 = ctk.CTkLabel(info_box2, text="", text_color=("#0D47A1", "#BBDEFB"), font=ctk.CTkFont(size=11, weight="bold"), justify="center", wraplength=310)
        self.lbl_info_t2.pack(padx=10, pady=10)

        self.btn_save_t2 = ctk.CTkButton(bottom_settings, text=get_text("btn_extract_images"), font=ctk.CTkFont(size=16, weight="bold"), height=50, fg_color="#1E88E5", hover_color="#1565C0", command=self.start_save_pdf_to_images)
        self.btn_save_t2.pack(fill="x", padx=20)

    # ==========================================
    # --- YARDIMCI VE ÖNİZLEME MOTORLARI ---
    # ==========================================
    def _get_color_tuple(self, color_name):
        c_map = {get_text("opt_mask_white"): (255, 255, 255), get_text("opt_mask_black"): (0, 0, 0)}
        return c_map.get(color_name, None)

    def _get_paper_dimensions(self, paper_str, is_landscape):
        dims = {"A4 (210x297mm)": (595, 842), "A3 (297x420mm)": (842, 1190), "A5 (148x210mm)": (420, 595), "Letter (8.5x11\")": (612, 792), "Legal (8.5x14\")": (612, 1008)}
        w, h = dims.get(paper_str, (595, 842))
        return (h, w) if is_landscape else (w, h)

    def generate_page_preview(self, data, pw="", tab_id=1):
        dpi_for_preview = 60
        try:
            if data['source_path'] == "BLANK":
                pil_page = Image.new('RGB', (595, 842), 'white')
            else:
                doc = self._get_safe_doc(data['source_path'], pw)
                page = doc.load_page(data.get('page_num', 0))
                
                cs = fitz.csGRAY if data.get('grayscale', False) else fitz.csRGB
                pix = page.get_pixmap(dpi=dpi_for_preview, colorspace=cs)
                mode = "L" if data.get('grayscale', False) else ("RGBA" if pix.alpha else "RGB")
                pil_page = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
                if mode == "L": pil_page = pil_page.convert("RGB")
                doc.close()
                
                if data['rotation'] != 0:
                    pil_page = pil_page.rotate(-data['rotation'], expand=True, resample=Image.BICUBIC)

                clip_box = data.get('crop_box_pct')
                crop_mode = data.get('crop_mode', get_text("opt_mode_shrink"))
                
                if clip_box:
                    x1, y1, x2, y2 = clip_box
                    w, h = pil_page.size
                    crop_coords = (int(w*x1), int(h*y1), int(w*x2), int(h*y2))
                    
                    if crop_mode == get_text("opt_mode_shrink"):
                        pil_page = pil_page.crop(crop_coords)
                    else:
                        mask_c = self._get_color_tuple(data.get('crop_color_name'))
                        if data.get('crop_color_custom_rgb'):
                            r, g, b = [int(x*255) for x in data.get('crop_color_custom_rgb')]
                            mask_c = (r, g, b)
                        if mask_c:
                            mask_layer = Image.new('RGB', pil_page.size, mask_c)
                            cropped_part = pil_page.crop(crop_coords)
                            mask_layer.paste(cropped_part, (crop_coords[0], crop_coords[1]))
                            pil_page = mask_layer

            paper_setting = data.get('paper_setting', get_text("opt_paper_orig"))
            padding_pct = float(data.get('padding_pct', "%0").replace('%', '')) / 100.0
            
            # Resmin kendi en-boy oranına göre otomatik kağıt yönü belirlenir (Standart akıllı mod)
            is_landscape = pil_page.width > pil_page.height

            bg_hex = '#2B2B2B' if ctk.get_appearance_mode() == "Dark" else "#E0E0E0"
            card_canvas = Image.new('RGB', (260, 360), bg_hex)
            
            margin_bg_color = 'white'
            if data.get('crop_mode') == get_text("opt_mode_mask"):
                mask_c = self._get_color_tuple(data.get('crop_color_name'))
                if data.get('crop_color_custom_rgb'):
                    r, g, b = [int(x*255) for x in data.get('crop_color_custom_rgb')]
                    mask_c = (r, g, b)
                if mask_c: margin_bg_color = mask_c

            if paper_setting == get_text("opt_paper_orig"):
                t_w, t_h = pil_page.width, pil_page.height
                if padding_pct > 0:
                    n_w = int(t_w * (1 - 2 * padding_pct))
                    n_h = int(t_h * (1 - 2 * padding_pct))
                    if n_w < 10: n_w = 10; 
                    if n_h < 10: n_h = 10
                    resized_page = pil_page.resize((n_w, n_h), Image.Resampling.LANCZOS)
                    paper_sheet = Image.new('RGB', (t_w, t_h), margin_bg_color)
                    paper_sheet.paste(resized_page, ((t_w - n_w)//2, (t_h - n_h)//2))
                    pil_page = paper_sheet
                
                pil_page.thumbnail((250, 350), Image.Resampling.LANCZOS)
                cw, ch = card_canvas.size
                pw, ph = pil_page.size
                card_canvas.paste(pil_page, ((cw - pw)//2, (ch - ph)//2))
            else:
                tw, th = self._get_paper_dimensions(paper_setting, is_landscape)
                
                max_pw, max_ph = 250, 350
                ratio = min(max_pw / tw, max_ph / th)
                p_w = int(tw * ratio)
                p_h = int(th * ratio)
                
                paper_sheet = Image.new('RGB', (p_w, p_h), margin_bg_color)
                
                avail_w = p_w * (1 - 2 * padding_pct)
                avail_h = p_h * (1 - 2 * padding_pct)
                
                pil_page.thumbnail((int(avail_w), int(avail_h)), Image.Resampling.LANCZOS)
                paper_sheet.paste(pil_page, ((p_w - pil_page.width)//2, (p_h - pil_page.height)//2))
                card_canvas.paste(paper_sheet, ((260 - p_w)//2, (360 - p_h)//2))

            p_name = paper_setting.split(' ')[0]
            if p_name != "Orijinal":
                import PIL.ImageDraw as ImageDraw
                draw = ImageDraw.Draw(card_canvas)
                draw.rectangle([0, 0, 48, 20], fill="#F57C00")
                draw.text((6, 2), p_name, fill="white")

            return ImageOps.expand(card_canvas, border=1, fill="#b0b0b0")
        except Exception as e:
            return Image.new('RGB', (180, 254), 'gray')

    # ==========================================
    # --- YÜKSEK PERFORMANSLI KART MOTORU ---
    # ==========================================
    def add_dropped_files(self, files):
        tab_id = 1 if self.tabview.get() == get_text("tab_img_to_pdf") else 2
        
        if tab_id == 1: 
            valid_exts = ('.png', '.jpg', '.jpeg')
            valid_files = [f for f in files if f.lower().endswith(valid_exts)]
        else: 
            valid_files = [f for f in files if f.lower().endswith('.pdf')]
            
        if valid_files:
            self.progress = ProgressWindow(self.winfo_toplevel(), get_text("msg_reading_files"))
            self.after(200, lambda: threading.Thread(target=self._thread_add_files, args=(valid_files, tab_id), daemon=True).start())

    def add_files(self, tab_id):
        if tab_id == 1:
            files = filedialog.askopenfilenames(title=get_text("fd_select_images"), filetypes=[("Resim", "*.png *.jpg *.jpeg")])
        else:
            files = filedialog.askopenfilenames(title=get_text("fd_select_pdf"), filetypes=[("PDF", "*.pdf")])
            
        if not files: return
        self.progress = ProgressWindow(self.winfo_toplevel(), get_text("msg_reading_files"))
        threading.Thread(target=self._thread_add_files, args=(files, tab_id), daemon=True).start()

    def add_blank_page(self, tab_id):
        data_list = self.t1_data_list if tab_id == 1 else self.t2_data_list
        temp_data = {
            'source_path': "BLANK", 'page_num': 0, 'rotation': 0, 'selected': False, 
            'name': get_text("lbl_blank_page"), 'password': "",
            'grayscale': False, 'crop_box_pct': None,
            'crop_mode': get_text("opt_mode_shrink"), 'crop_color_name': get_text("opt_mask_white"),
            'paper_setting': get_text("opt_paper_orig"), 'padding_pct': "%0"
        }
        temp_data['thumb'] = self.generate_page_preview(temp_data, "", tab_id)
        data_list.append(temp_data)
        self.rebuild_cards(tab_id)

    def select_odd_even(self, tab_id, mode):
        data_list = self.t1_data_list if tab_id == 1 else self.t2_data_list
        if mode == "odd":
            state = not getattr(self, f"odd_state_t{tab_id}")
            setattr(self, f"odd_state_t{tab_id}", state)
            for i, data in enumerate(data_list):
                if i % 2 == 0: 
                    data['selected'] = state
                    if 'w_chk' in data: data['w_chk'].select() if state else data['w_chk'].deselect()
        elif mode == "even":
            state = not getattr(self, f"even_state_t{tab_id}")
            setattr(self, f"even_state_t{tab_id}", state)
            for i, data in enumerate(data_list):
                if i % 2 != 0: 
                    data['selected'] = state
                    if 'w_chk' in data: data['w_chk'].select() if state else data['w_chk'].deselect()
        self._update_odd_even_btn_texts(tab_id)

    def _update_odd_even_btn_texts(self, tab_id):
        if tab_id == 1:
            if hasattr(self, 'btn_odd_t1') and hasattr(self, 'btn_even_t1'):
                btn_odd = self.btn_odd_t1; btn_even = self.btn_even_t1
                odd_state = self.odd_state_t1; even_state = self.even_state_t1
                btn_odd.configure(text=get_text("btn_desel_odd") if odd_state else get_text("btn_sel_odd"))
                btn_even.configure(text=get_text("btn_desel_even") if even_state else get_text("btn_sel_even"))
        else:
            if hasattr(self, 'btn_odd_t2') and hasattr(self, 'btn_even_t2'):
                btn_odd = self.btn_odd_t2; btn_even = self.btn_even_t2
                odd_state = getattr(self, "odd_state_t2", False); even_state = getattr(self, "even_state_t2", False)
                btn_odd.configure(text=get_text("btn_desel_odd") if odd_state else get_text("btn_sel_odd"))
                btn_even.configure(text=get_text("btn_desel_even") if even_state else get_text("btn_sel_even"))

    def batch_grayscale(self, tab_id):
        data_list = self.t1_data_list if tab_id == 1 else self.t2_data_list
        selected_pages = [d for d in data_list if d.get('selected', False)]
        
        if not selected_pages:
            messagebox.showinfo(get_text("dialog_info"), get_text("msg_select_to_gray"))
            return

        self.progress = ProgressWindow(self.winfo_toplevel(), "Filtre Uygulanıyor...")
        for data in selected_pages: data['grayscale'] = not data.get('grayscale', False)
        threading.Thread(target=self._thread_update_previews, args=(selected_pages, tab_id), daemon=True).start()

    def _thread_add_files(self, files, tab_id):
        try:
            data_list = self.t1_data_list if tab_id == 1 else self.t2_data_list
            new_data = []

            for f in files:
                doc = self._get_safe_doc(f)
                base_name = os.path.basename(f)
                if len(base_name) > 12: base_name = base_name[:9] + "..."
                
                file_password = ""
                if doc.is_encrypted:
                    self.after(0, lambda: self.progress.withdraw())
                    dialog = PasswordDialog(self.winfo_toplevel(), get_text("msg_pwd_file"), get_text("msg_pwd_prompt").format(base_name))
                    user_pass = dialog.get_result()
                    self.after(0, lambda: self.progress.deiconify())
                    
                    if user_pass and doc.authenticate(user_pass):
                        file_password = user_pass
                    else:
                        self.after(0, lambda bn=base_name: messagebox.showerror(get_text("dialog_error"), get_text("msg_pwd_wrong").format(bn)))
                        doc.close()
                        continue
                
                for page_num in range(len(doc)):
                    name_str = base_name if tab_id == 1 else f"{base_name} - S{page_num+1}"
                    temp_data = {
                        'source_path': f, 'page_num': page_num, 'rotation': 0, 'selected': False, 
                        'name': name_str, 'password': file_password,
                        'grayscale': False, 'crop_box_pct': None,
                        'crop_mode': get_text("opt_mode_shrink"), 'crop_color_name': get_text("opt_mask_white"),
                        'paper_setting': get_text("opt_paper_orig"), 'padding_pct': "%0"
                    }
                    temp_data['thumb'] = self.generate_page_preview(temp_data, file_password, tab_id)
                    new_data.append(temp_data)
                doc.close()
            
            data_list.extend(new_data)
            self.after(0, self.finish_processing, tab_id)
        except Exception as e:
            self.after(0, self.on_error, get_text("msg_load_err").format(str(e)))

    def finish_processing(self, tab_id):
        if hasattr(self, 'progress') and self.progress.winfo_exists(): self.progress.destroy()
        self.rebuild_cards(tab_id)

    def apply_right_menu_settings(self, tab_id, _=None):
        data_list = self.t1_data_list if tab_id == 1 else self.t2_data_list
        paper_setting = self.var_paper_t1.get() if tab_id == 1 else getattr(self, 'var_paper_t2', ctk.StringVar(value=get_text("opt_paper_orig"))).get()
        padding_pct = self.var_padding_t1.get() if tab_id == 1 else getattr(self, 'var_padding_t2', ctk.StringVar(value="%0")).get()

        selected_count = sum(1 for d in data_list if d.get('selected', False))
        target_list = data_list if selected_count == 0 else [d for d in data_list if d.get('selected', False)]

        for data in target_list:
            data['paper_setting'] = paper_setting
            data['padding_pct'] = padding_pct

        threading.Thread(target=self._thread_update_previews, args=(target_list, tab_id), daemon=True).start()

    def _thread_update_previews(self, target_list, tab_id):
        def _update_ui(img_dict, d):
            if 'w_img' in d and d['w_img'].winfo_exists():
                new_ctk = ctk.CTkImage(light_image=img_dict['new_pil'], dark_image=img_dict['new_pil'], size=(260, 360))
                d['w_img'].configure(image=new_ctk)
                d['w_img'].image = new_ctk

        for data in target_list:
            pw = data.get('password', '') 
            new_pil = self.generate_page_preview(data, pw, tab_id)
            data['thumb'] = new_pil
            self.after(0, _update_ui, {'new_pil': new_pil}, data)
                
        self.after(0, lambda: self.progress.destroy() if hasattr(self, 'progress') and self.progress.winfo_exists() else None)

    # --- TOPLU İŞLEMLER (SİLME / DÖNDÜRME) ---
    def batch_delete(self, tab_id):
        cards_list = self.t1_cards_list if tab_id == 1 else self.t2_cards_list
        data_list = self.t1_data_list if tab_id == 1 else self.t2_data_list
        
        indices_to_delete = [i for i, d in enumerate(data_list) if d.get('selected', False)]
        if not indices_to_delete:
            messagebox.showinfo(get_text("dialog_info"), get_text("msg_select_to_delete"))
            return
            
        for i in reversed(indices_to_delete):
            if cards_list[i] and cards_list[i].winfo_exists(): cards_list[i].destroy()
            cards_list.pop(i)
            data_list.pop(i)
            
        self.refresh_grid(cards_list)

    def batch_rotate(self, tab_id):
        data_list = self.t1_data_list if tab_id == 1 else self.t2_data_list
        selected_pages = [d for d in data_list if d.get('selected', False)]
        if not selected_pages:
            messagebox.showinfo(get_text("dialog_info"), get_text("msg_select_to_rotate"))
            return

        self.progress = ProgressWindow(self.winfo_toplevel(), get_text("msg_rotating"))
        for data in selected_pages: 
            data['rotation'] = (data['rotation'] + 90) % 360
            if data.get('crop_box_pct'):
                x1, y1, x2, y2 = data['crop_box_pct']
                data['crop_box_pct'] = (1.0 - y2, x1, 1.0 - y1, x2)
                
        threading.Thread(target=self._thread_update_previews, args=(selected_pages, tab_id), daemon=True).start()

    def rotate_single_page(self, data, lbl_img, tab_id):
        data['rotation'] = (data['rotation'] + 90) % 360
        if data.get('crop_box_pct'):
            x1, y1, x2, y2 = data['crop_box_pct']
            data['crop_box_pct'] = (1.0 - y2, x1, 1.0 - y1, x2)
        threading.Thread(target=self._thread_update_previews, args=([data], tab_id), daemon=True).start()

    def open_page_settings(self, data, lbl_img, tab_id):
        def on_apply():
            threading.Thread(target=self._thread_update_previews, args=([data], tab_id), daemon=True).start()
        InteractiveCropDialog(self.winfo_toplevel(), data, self._get_safe_doc, on_apply)

    def toggle_selection(self, data, checkbox):
        data['selected'] = checkbox.get()

    def rebuild_cards(self, tab_id):
        if self.is_dragging:
            self.is_dragging = False
            if hasattr(self, 'float_win') and self.float_win.winfo_exists(): self.float_win.destroy()

        container = self.t1_scroll_frame if tab_id == 1 else self.t2_scroll_frame
        cards_list = self.t1_cards_list if tab_id == 1 else self.t2_cards_list
        data_list = self.t1_data_list if tab_id == 1 else self.t2_data_list
        
        for w in container.winfo_children(): w.destroy()
        cards_list.clear()

        for i in range(3): container.grid_columnconfigure(i, weight=1)

        for data in data_list:
            card_color = ("gray90", "gray30") if data.get('source_path') == "BLANK" else ("gray85", "gray25")
            card = ctk.CTkFrame(container, corner_radius=10, fg_color=card_color)
            
            ctk_img = ctk.CTkImage(light_image=data['thumb'], dark_image=data['thumb'], size=(260, 360)) 
            lbl_img = ctk.CTkLabel(card, image=ctk_img, text="", cursor="hand2")
            lbl_img.pack(pady=(5, 0), padx=5)

            ctk.CTkLabel(card, text=data['name'], font=ctk.CTkFont(size=12, weight="bold")).pack()
            
            if data.get('password'):
                ctk.CTkLabel(card, text=get_text("lbl_pwd_solved"), text_color="green", font=ctk.CTkFont(size=10)).pack()

            controls = ctk.CTkFrame(card, fg_color="transparent")
            controls.pack(pady=(4, 8))

            chk_var = ctk.CTkCheckBox(controls, text=get_text("chk_select"), width=50)
            if data.get('selected', False): chk_var.select()
            chk_var.configure(command=lambda d=data, c=chk_var: self.toggle_selection(d, c))
            chk_var.pack(side="left", padx=(0, 10))

            data['w_card'] = card
            data['w_img'] = lbl_img
            data['w_chk'] = chk_var

            btn_del = ctk.CTkButton(
                controls,
                text="✕",
                width=32,
                height=32,
                corner_radius=8,
                font=ctk.CTkFont(size=15, weight="bold"),
                fg_color="#C62828",
                hover_color="#B71C1C",
                border_width=1,
                border_color="#555555",
                command=lambda c=card, t=tab_id: self.delete_single_card(c, t)
            )
            btn_del.pack(side="left", padx=3)

            if data.get('source_path') != "BLANK":

                btn_rot = ctk.CTkButton(
                    controls,
                    text="↻",
                    width=32,
                    height=32,
                    corner_radius=8,
                    font=ctk.CTkFont(size=16, weight="bold"),
                    fg_color="#3A3A3A",
                    hover_color="#4A4A4A",
                    border_width=1,
                    border_color="#555555",
                    command=lambda d=data, l=lbl_img, t=tab_id:
                        self.rotate_single_page(d, l, t)
                )
                btn_rot.pack(side="left", padx=3)

                btn_set = ctk.CTkButton(
                    controls,
                    text="✂",
                    width=32,
                    height=32,
                    corner_radius=8,
                    font=ctk.CTkFont(size=15, weight="bold"),
                    fg_color="#D97706",
                    hover_color="#B45309",
                    border_width=1,
                    border_color="#555555",
                    command=lambda d=data, l=lbl_img, t=tab_id:
                        self.open_page_settings(d, l, t)
                )
                btn_set.pack(side="left", padx=3)

            lbl_img.bind("<ButtonPress-1>", lambda e, c=card, d=data, c_lst=cards_list, d_lst=data_list, cnt=container, img=ctk_img: self.drag_start(e, c, d, c_lst, d_lst, cnt, img))
            lbl_img.bind("<B1-Motion>", self.drag_motion)
            lbl_img.bind("<ButtonRelease-1>", self.drag_release)

            cards_list.append(card)

        self.refresh_grid(cards_list)

    def delete_single_card(self, card, tab_id):
        cards_list = self.t1_cards_list if tab_id == 1 else self.t2_cards_list
        data_list = self.t1_data_list if tab_id == 1 else self.t2_data_list
        if card in cards_list:
            idx = cards_list.index(card)
            cards_list.pop(idx)
            data_list.pop(idx)
            card.destroy()
            self.refresh_grid(cards_list)

    def refresh_grid(self, cards_list):
        columns = 3
        for index, card in enumerate(cards_list):
            row = index // columns
            col = index % columns
            if card.winfo_exists(): card.grid(row=row, column=col, padx=2, pady=5, sticky="n")

    def clear_all(self, tab_id):
        if tab_id == 1: self.t1_data_list.clear(); self.odd_state_t1 = False; self.even_state_t1 = False
        else: self.t2_data_list.clear(); self.odd_state_t2 = False; self.even_state_t2 = False
        self._update_odd_even_btn_texts(tab_id)
        self.rebuild_cards(tab_id)

    # Sürükle Bırak Fonksiyonları
    def drag_start(self, event, card, data, cards_list, data_list, container, img_ctk):
        try:
            if hasattr(self, "float_win") and self.float_win.winfo_exists(): self.float_win.destroy()
        except: pass

        try:
            if hasattr(self, "spacer") and self.spacer.winfo_exists(): self.spacer.destroy()
        except: pass

        self.float_win = None
        self.spacer = None
        self.is_dragging = True
        self.drag_card = card
        self.drag_cards_list = cards_list
        self.drag_data_list = data_list
        self.drag_data = data

        self.float_win = ctk.CTkToplevel(self.winfo_toplevel())
        self.float_win.withdraw()
        self.float_win.overrideredirect(True)
        self.float_win.transient(self.winfo_toplevel())
        self.float_win.attributes("-topmost", True)
        self.float_win.attributes("-alpha", 0.8) 

        w, h = img_ctk.cget("size")
        float_img = ctk.CTkImage(light_image=img_ctk._light_image, size=(int(w*0.8), int(h*0.8)))
        
        lbl_float = ctk.CTkLabel(self.float_win, image=float_img, text="")
        lbl_float.pack(padx=5, pady=5)
        self.float_win.geometry(f"+{event.x_root+10}+{event.y_root+10}")
        self.float_win.deiconify() 

        self.float_win.bind("<B1-Motion>", self.drag_motion)
        self.float_win.bind("<ButtonRelease-1>", self.drag_release)
        lbl_float.bind("<B1-Motion>", self.drag_motion)
        lbl_float.bind("<ButtonRelease-1>", self.drag_release)

        self.spacer = ctk.CTkFrame(container, width=260, height=360, corner_radius=10, fg_color="transparent", border_width=2, border_color="#E53935")
        
        idx = cards_list.index(card)
        card.grid_forget()
        cards_list[idx] = self.spacer
        self.refresh_grid(cards_list)

    def drag_motion(self, event):
        if not hasattr(self, "float_win") or self.float_win is None: return
        if not self.float_win.winfo_exists(): return
        if not self.is_dragging or not hasattr(self, 'float_win') or not self.float_win.winfo_exists():
            self.is_dragging = False; return
            
        self.float_win.geometry(f"+{event.x_root+10}+{event.y_root+10}")
        mx, my = event.x_root, event.y_root
        target_idx = -1
        for i, c in enumerate(self.drag_cards_list):
            if c == self.spacer: continue
            cx, cy = c.winfo_rootx(), c.winfo_rooty()
            cw, ch = c.winfo_width(), c.winfo_height()
            if cx <= mx <= cx + cw and cy <= my <= cy + ch:
                target_idx = i; break

        if target_idx != -1:
            current_idx = self.drag_cards_list.index(self.spacer)
            if target_idx != current_idx:
                self.drag_cards_list.pop(current_idx)
                self.drag_cards_list.insert(target_idx, self.spacer)
                item_data = self.drag_data_list.pop(current_idx)
                self.drag_data_list.insert(target_idx, item_data)

        self.refresh_grid(self.drag_cards_list)

    def drag_release(self, event):
        if not self.is_dragging: return
        self.is_dragging = False
        
        try:
            if self.float_win and self.float_win.winfo_exists():
                self.float_win.withdraw()
                self.float_win.destroy()
        except: pass

        self.float_win = None

        try:
            if self.spacer and self.spacer.winfo_exists():
                idx = self.drag_cards_list.index(self.spacer)
                self.spacer.destroy()
                self.drag_cards_list[idx] = self.drag_card
                self.refresh_grid(self.drag_cards_list)
        except Exception:
            tab_id = 1 if self.tabview.get() == get_text("tab_to_pdf") else 2
            self.rebuild_cards(tab_id)
        finally:
            self.spacer = None
            self.drag_card = None

    def _get_fitz_color(self, data):
        if data.get('crop_color_custom_rgb'):
            return data.get('crop_color_custom_rgb')
        c = self._get_color_tuple(data.get('crop_color_name'))
        return (c[0]/255.0, c[1]/255.0, c[2]/255.0) if c else (1.0, 1.0, 1.0)

    # ==========================================
    # --- THREAD DESTEKLİ KAYDETME MOTORLARI ---
    # ==========================================
    def process_and_insert_page(self, new_pdf, source_doc, data, tab_id):
        if data.get('source_path') == "BLANK":
            w, h = (595, 842)
            paper_setting = data.get('paper_setting', get_text("opt_paper_orig"))
            is_landscape = False # Boş sayfalar için varsayılan dikey başlar
                 
            if paper_setting != get_text("opt_paper_orig"): w, h = self._get_paper_dimensions(paper_setting, is_landscape)
            new_pdf.new_page(width=w, height=h)
            return

        is_grayscale = data.get('grayscale', False)
        crop_mode = data.get('crop_mode', get_text("opt_mode_shrink"))
        paper_setting = data.get('paper_setting', get_text("opt_paper_orig"))
        padding_pct = float(data.get('padding_pct', "%0").replace('%', '')) / 100.0
        clip_box = data.get('crop_box_pct')

        # Vektörel Koruma ve Hızlı Klonlama (Yalnızca Siyah-Beyaz değilse)
        if not is_grayscale:
            if paper_setting == get_text("opt_paper_orig") and padding_pct == 0.0:
                new_pdf.insert_pdf(source_doc, from_page=data['page_num'], to_page=data['page_num'])
                target_page = new_pdf[-1]
                target_page.set_rotation(data['rotation'])
                
                if clip_box:
                    x1, y1, x2, y2 = clip_box
                    rect = target_page.rect
                    w, h = rect.width, rect.height
                    
                    if crop_mode == get_text("opt_mode_shrink"):
                        new_crop = fitz.Rect(rect.x0 + w*x1, rect.y0 + h*y1, rect.x0 + w*x2, rect.y0 + h*y2)
                        target_page.set_cropbox(new_crop)
                    else:
                        c_left, c_top, c_right, c_bottom = rect.x0 + w*x1, rect.y0 + h*y1, rect.x0 + w*x2, rect.y0 + h*y2
                        f_color = self._get_fitz_color(data)
                        target_page.draw_rect(fitz.Rect(rect.x0, rect.y0, rect.x1, c_top), color=f_color, fill=f_color)
                        target_page.draw_rect(fitz.Rect(rect.x0, c_bottom, rect.x1, rect.y1), color=f_color, fill=f_color)
                        target_page.draw_rect(fitz.Rect(rect.x0, c_top, c_left, c_bottom), color=f_color, fill=f_color)
                        target_page.draw_rect(fitz.Rect(c_right, c_top, rect.x1, c_bottom), color=f_color, fill=f_color)
                return

            src_page = source_doc.load_page(data['page_num'])
            src_page.set_rotation(data['rotation'])
            rect = src_page.rect
            img_w, img_h = rect.width, rect.height
            
            orig_crop = src_page.cropbox
            if clip_box and crop_mode == get_text("opt_mode_shrink"):
                x1, y1, x2, y2 = clip_box
                new_crop = fitz.Rect(rect.x0 + img_w*x1, rect.y0 + img_h*y1, rect.x0 + img_w*x2, rect.y0 + img_h*y2)
                src_page.set_cropbox(new_crop)
                img_w, img_h = new_crop.width, new_crop.height
                
            margin_bg_color_fitz = (1.0, 1.0, 1.0) 
            if crop_mode == get_text("opt_mode_mask"): margin_bg_color_fitz = self._get_fitz_color(data)

            if paper_setting == get_text("opt_paper_orig"):
                tw, th = img_w, img_h
                if padding_pct > 0:
                    tw = tw / (1 - 2 * padding_pct)
                    th = th / (1 - 2 * padding_pct)
                target_page = new_pdf.new_page(width=tw, height=th)
                if padding_pct > 0: target_page.draw_rect(fitz.Rect(0, 0, tw, th), color=margin_bg_color_fitz, fill=margin_bg_color_fitz)
                dx, dy = (tw - img_w) / 2, (th - img_h) / 2
                fit_rect = fitz.Rect(dx, dy, dx + img_w, dy + img_h)
            else:
                is_landscape = False
                if tab_id == 1 and hasattr(self, 'var_orientation'):
                    curr = self.var_orientation.get()
                    if curr in [get_text("opt_landscape"), "Yatay", "Landscape"]:
                        is_landscape = True
                elif tab_id != 1:
                    is_landscape = img_w > img_h
                tw, th = self._get_paper_dimensions(paper_setting, is_landscape)
                
                target_page = new_pdf.new_page(width=tw, height=th)
                target_page.draw_rect(fitz.Rect(0, 0, tw, th), color=margin_bg_color_fitz, fill=margin_bg_color_fitz)
                
                avail_w, avail_h = tw * (1 - 2 * padding_pct), th * (1 - 2 * padding_pct)
                ratio = min(avail_w / img_w, avail_h / img_h)
                fit_w, fit_h = img_w * ratio, img_h * ratio
                dx, dy = (tw - fit_w) / 2, (th - fit_h) / 2
                fit_rect = fitz.Rect(dx, dy, dx + fit_w, dy + fit_h)
            
            target_page.show_pdf_page(fit_rect, source_doc, data['page_num'])
            
            if clip_box and crop_mode == get_text("opt_mode_mask"):
                x1, y1, x2, y2 = clip_box
                fw, fh = fit_rect.width, fit_rect.height
                c_left, c_top, c_right, c_bottom = fit_rect.x0 + fw*x1, fit_rect.y0 + fh*y1, fit_rect.x0 + fw*x2, fit_rect.y0 + fh*y2
                f_color = self._get_fitz_color(data)
                target_page.draw_rect(fitz.Rect(fit_rect.x0, fit_rect.y0, fit_rect.x1, c_top), color=f_color, fill=f_color)
                target_page.draw_rect(fitz.Rect(fit_rect.x0, c_bottom, fit_rect.x1, fit_rect.y1), color=f_color, fill=f_color)
                target_page.draw_rect(fitz.Rect(fit_rect.x0, c_top, c_left, c_bottom), color=f_color, fill=f_color)
                target_page.draw_rect(fitz.Rect(c_right, c_top, fit_rect.x1, c_bottom), color=f_color, fill=f_color)
            
            src_page.set_cropbox(orig_crop)

        else:
            src_page = source_doc.load_page(data['page_num'])
            src_page.set_rotation(data['rotation'])
            orig_pt_w, orig_pt_h = src_page.rect.width, src_page.rect.height

            pix = src_page.get_pixmap(colorspace=fitz.csGRAY, dpi=200)
            img = Image.frombytes("L", [pix.width, pix.height], pix.samples).convert("RGB")

            if clip_box:
                x1, y1, x2, y2 = clip_box
                px_w, px_h = img.size
                crop_coords = (int(px_w*x1), int(px_h*y1), int(px_w*x2), int(px_h*y2))

                if crop_mode == get_text("opt_mode_shrink"):
                    img = img.crop(crop_coords)
                    orig_pt_w = orig_pt_w * (x2 - x1)
                    orig_pt_h = orig_pt_h * (y2 - y1)
                else:
                    mask_c = self._get_color_tuple(data.get('crop_color_name'))
                    if data.get('crop_color_custom_rgb'): r, g, b = [int(x*255) for x in data.get('crop_color_custom_rgb')]; mask_c = (r, g, b)
                    if mask_c:
                        mask_layer = Image.new('RGB', (px_w, px_h), mask_c)
                        mask_layer.paste(img.crop(crop_coords), (crop_coords[0], crop_coords[1]))
                        img = mask_layer

            margin_bg_color_fitz = (1.0, 1.0, 1.0) 
            if crop_mode == get_text("opt_mode_mask"): margin_bg_color_fitz = self._get_fitz_color(data)

            if paper_setting == get_text("opt_paper_orig"):
                tw, th = orig_pt_w, orig_pt_h
                if padding_pct > 0:
                    tw = tw / (1 - 2 * padding_pct)
                    th = th / (1 - 2 * padding_pct)
                target_page = new_pdf.new_page(width=tw, height=th)
                target_page.draw_rect(fitz.Rect(0, 0, tw, th), color=margin_bg_color_fitz, fill=margin_bg_color_fitz)
                dx, dy = (tw - orig_pt_w) / 2, (th - orig_pt_h) / 2
                fit_rect = fitz.Rect(dx, dy, dx + orig_pt_w, dy + orig_pt_h)
            else:
                is_landscape = orig_pt_w > orig_pt_h
                tw, th = self._get_paper_dimensions(paper_setting, is_landscape)
                
                target_page = new_pdf.new_page(width=tw, height=th)
                target_page.draw_rect(fitz.Rect(0, 0, tw, th), color=margin_bg_color_fitz, fill=margin_bg_color_fitz)
                avail_w, avail_h = tw * (1 - 2 * padding_pct), th * (1 - 2 * padding_pct)
                ratio = min(avail_w / orig_pt_w, avail_h / orig_pt_h)
                fit_w, fit_h = orig_pt_w * ratio, orig_pt_h * ratio
                dx, dy = (tw - fit_w) / 2, (th - fit_h) / 2
                fit_rect = fitz.Rect(dx, dy, dx + fit_w, dy + fit_h)

            import io
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG', quality=95)
            target_page.insert_image(fit_rect, stream=img_byte_arr.getvalue())

    def start_save_to_pdf(self):
        if not self.t1_data_list:
            messagebox.showwarning(get_text("dialog_warning"), get_text("msg_add_files_to_convert"))
            return
            
        save_path = filedialog.asksaveasfilename(title=get_text("fd_save_pdf_name"), defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not save_path: return

        self.progress = ProgressWindow(self.winfo_toplevel(), get_text("msg_converting_img_to_pdf"))
        threading.Thread(target=self._thread_save_to_pdf, args=(save_path,), daemon=True).start()

    def _thread_save_to_pdf(self, save_path):
        try:
            final_pdf = fitz.open()
            doc_cache = {}

            for data in self.t1_data_list:
                # Her resim PDF sayfasına basılırken yüklenme kutusunu canlı tut
                if hasattr(self, 'progress') and self.progress.winfo_exists():
                    self.progress.update()

                if data['source_path'] == "BLANK":
                    self.process_and_insert_page(final_pdf, None, data, 1)
                    continue

                pdf_path = data['source_path']
                if pdf_path not in doc_cache: 
                    doc_cache[pdf_path] = self._get_safe_doc(pdf_path, data.get('password', ''))
                        
                self.process_and_insert_page(final_pdf, doc_cache[pdf_path], data, 1)

            # --- UYAP UYUMLULUK VE GÜVENLİK ENTEGRASYONU ---
            # 1. Birleştirilen resim sayfalarındaki olası katmanları PDF yapısına düzleştiriyoruz
            try:
                for page in final_pdf:
                    page.flatten_widgets()
            except: pass

            # 2. Yerel bilgisayar adını ve dosya yollarını temizlemek için meta verileri sıfırlıyoruz
            final_pdf.set_metadata({})
            try: final_pdf.set_xml_metadata("")
            except: pass
            
            # 3. Çökme hatasını önlemek için 'linear=True' parametresini kaldırarak derin temizlikle kaydediyoruz
            final_pdf.save(
                save_path, 
                deflate=True, 
                garbage=4, 
                clean=True
            )
            final_pdf.close()
            from modules.history_manager import add_history
            add_history("🖼️", "history_action_convert", ["Seçili Resimler", os.path.basename(save_path)], save_path)
            for doc in doc_cache.values(): doc.close()

            self.after(0, self.on_success, save_path, get_text("msg_pdf_created_success"), 1)
        except Exception as e:
            self.after(0, self.on_error, get_text("msg_process_err").format(str(e)))

    def start_save_pdf_to_images(self):
        if not self.t2_data_list:
            messagebox.showwarning(get_text("dialog_warning"), get_text("msg_add_pdfs_to_convert"))
            return
            
        save_dir = filedialog.askdirectory(title=get_text("fd_save_img_folder"))
        if not save_dir: return

        self.progress = ProgressWindow(self.winfo_toplevel(), get_text("msg_extracting_pdf_to_img"))
        threading.Thread(target=self._thread_save_pdf_to_images, args=(save_dir,), daemon=True).start()

    def _thread_save_pdf_to_images(self, save_dir):
        try:
            target_format = self.var_target_format.get().lower()
            if target_format == 'jpg': target_format = 'jpeg'

            # Docsas Klasörünü Otomatik Oluştur
            docsas_dir = os.path.join(save_dir, "Docsas_Resim_Ciktilari")
            os.makedirs(docsas_dir, exist_ok=True)

            temp_pdf_path = os.path.join(self.temp_dir, f"{os.urandom(4).hex()}_temp.pdf")
            temp_pdf = fitz.open()
            doc_cache = {}

            # Vektörel/Ön Düzenlenmiş halini Geçici PDF'e çıkar
            for data in self.t2_data_list:
                # Geçici PDF harmanlanırken donmayı kırar
                if hasattr(self, 'progress') and self.progress.winfo_exists():
                    self.progress.update()

                if data['source_path'] == "BLANK":
                    self.process_and_insert_page(temp_pdf, None, data, 2)
                    continue
                pdf_path = data['source_path']
                if pdf_path not in doc_cache: 
                    doc_cache[pdf_path] = fitz.open(pdf_path)
                    if doc_cache[pdf_path].is_encrypted:
                        doc_cache[pdf_path].authenticate(data.get('password', ''))
                        
                self.process_and_insert_page(temp_pdf, doc_cache[pdf_path], data, 2)

            # Geçici PDF dökümanının iç yapısını ve meta verilerini temizleyerek kaydediyoruz
            temp_pdf.set_metadata({})
            temp_pdf.save(
                temp_pdf_path, 
                deflate=True,
                garbage=4,
                clean=True
            )
            temp_pdf.close()
            for doc in doc_cache.values(): doc.close()

            # Geçici PDF'i oku ve sayfaları resim olarak Docsas_Resim_Ciktilari klasörüne kaydet
            final_doc = fitz.open(temp_pdf_path)
            base_name = os.path.splitext(os.path.basename(self.t2_data_list[0]['source_path']))[0] if self.t2_data_list and self.t2_data_list[0]['source_path'] != "BLANK" else "Docsas_Belgesi"

            for i, page in enumerate(final_doc):
                # Sayfalar tek tek JPEG/PNG dosyalarına dönüştürülürken donmayı kırar
                if hasattr(self, 'progress') and self.progress.winfo_exists():
                    self.progress.update()

                pix = page.get_pixmap(dpi=200)
                img = Image.frombytes("RGB" if not pix.alpha else "RGBA", [pix.width, pix.height], pix.samples)
                if target_format == 'jpeg' and img.mode == 'RGBA':
                    img = img.convert('RGB')
                out_name = os.path.join(docsas_dir, f"{base_name}_Sayfa_{i+1}.{target_format}")
                img.save(out_name)
                
            final_doc.close()

            from modules.history_manager import add_history
            add_history("🖼️", "history_action_convert", [base_name, f"Resim Klasörü ({target_format.upper()})"], docsas_dir)
            
            self.after(0, self.on_success, docsas_dir, get_text("msg_extracted_img_success"), 2)
        except Exception as e:
            self.after(0, self.on_error, get_text("msg_process_err").format(str(e)))

    # GUI Tetikleyicileri
    def on_success(self, path, message, tab_id):
        if hasattr(self, 'progress') and self.progress.winfo_exists(): self.progress.destroy()
        ActionDialog(self.winfo_toplevel(), get_text("dialog_success"), message, path)
        self.clear_all(tab_id)

    def on_error(self, error_message):
        if hasattr(self, 'progress') and self.progress.winfo_exists(): self.progress.destroy()
        messagebox.showerror(get_text("dialog_error"), error_message)