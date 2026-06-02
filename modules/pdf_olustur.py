import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, colorchooser
from PIL import Image, ImageTk
import fitz  
import os
import sys
import copy
import uuid
import tempfile
from modules.pdf_araclari import center_window
from modules.language_manager import get_text, lang_manager

class StudioSuccessDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, message, file_path):
        super().__init__(parent)
        self.title(title)
        self.geometry("450x200")
        self.transient(parent) # Sadece Docsas uygulamasının üzerinde kalır
        center_window(self, parent)
        self.file_path = file_path
        
        ctk.CTkLabel(self, text="✅ " + message, font=ctk.CTkFont(size=14, weight="bold"), wraplength=400).pack(pady=(30, 20))
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20)
        ctk.CTkButton(btn_frame, text=get_text("btn_open_file_direct"), font=ctk.CTkFont(weight="bold"), fg_color="#4CAF50", hover_color="#388E3C", command=self.open_file).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(btn_frame, text="Tamam", fg_color="gray40", command=self.destroy).pack(side="right", expand=True, padx=5)
        
    def open_file(self):
        try:
            if sys.platform == "win32": os.startfile(self.file_path)
            elif sys.platform == "darwin": os.system(f"open '{self.file_path}'")
            else: os.system(f"xdg-open '{self.file_path}'")
        except: pass
        self.destroy()

class PdfOlusturSayfasi(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.is_persistent = True 
        self.a4_w, self.a4_h = 595, 842
        
        self.pages_data = {1: {"items": [], "bg_color": "white", "bg_image_path": None}}
        self.current_page = 1
        self.total_pages = 1
        
        self.history = []
        self.history_pos = -1
        
        self.selected_id = None
        self.drag_data = {"x": 0, "y": 0, "id": None}
        
        self.bg_image_tk = None
        self.tk_images = {}
        self.zoom_factor = 1.0
        
        self.setup_ui()
        self.save_state()
        
        self.after(50, self.render_canvas)
        self.after(100, self.center_canvas_content)

    def setup_ui(self):
        # SAĞ MENÜ GENİŞLETİLDİ (minsize=340)
        self.grid_columnconfigure(0, weight=0, minsize=180) 
        self.grid_columnconfigure(1, weight=1)              
        self.grid_columnconfigure(2, weight=0, minsize=340) 
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # --- SOL: ARAÇ KUTUSU ---
        # ==========================================
        self.left_frame = ctk.CTkScrollableFrame(self, fg_color=("gray85", "gray20"))
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        
        self.lbl_toolbox = ctk.CTkLabel(self.left_frame, text=get_text("lbl_studio_tools"), font=ctk.CTkFont(weight="bold", size=16), text_color="#2E7D32")
        self.lbl_toolbox.pack(pady=(15, 10))
        
        self.tools_container = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.tools_container.pack(fill="x")
        self.build_toolbox_buttons()

        self.lbl_bg = ctk.CTkLabel(self.left_frame, text=get_text("lbl_bg_color"), font=ctk.CTkFont(weight="bold"))
        self.lbl_bg.pack(pady=(20, 5), padx=15, anchor="w")
        
        self.var_bg = ctk.StringVar(value="Beyaz (White)")
        self.opt_bg = ctk.CTkOptionMenu(self.left_frame, values=["Beyaz (White)", "Krem (Cream)", "Siyah (Black)"], variable=self.var_bg, command=self.change_bg)
        self.opt_bg.pack(fill="x", padx=15)
        
        self.btn_bg_custom = ctk.CTkButton(self.left_frame, text=get_text("btn_custom_color"), fg_color="gray40", command=self.pick_bg_color)
        self.btn_bg_custom.pack(fill="x", padx=15, pady=5)

        # ==========================================
        # --- ORTA: TUVAL VE ÜST BAR ---
        # ==========================================
        self.center_frame = ctk.CTkFrame(self, fg_color=("gray90", "gray15"))
        self.center_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=10)
        
        top_bar = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        top_bar.pack(fill="x", pady=5, padx=10)
        
        self.btn_undo = ctk.CTkButton(top_bar, text=get_text("btn_undo"), width=60, fg_color="gray40", command=self.undo)
        self.btn_undo.pack(side="left", padx=2)
        self.btn_redo = ctk.CTkButton(top_bar, text=get_text("btn_redo"), width=60, fg_color="gray40", command=self.redo)
        self.btn_redo.pack(side="left", padx=2)

        self.btn_guide = ctk.CTkButton(top_bar, text=get_text("btn_guide_studio"), width=60, fg_color="#F57C00", hover_color="#E65100", command=self.show_guide)
        self.btn_guide.pack(side="left", padx=(10, 2))
        
        self.btn_import = ctk.CTkButton(top_bar, text=get_text("btn_import_pdf"), width=100, fg_color="#8E24AA", hover_color="#6A1B9A", command=self.import_pdf_bg)
        self.btn_import.pack(side="left", padx=2)

        self.btn_save = ctk.CTkButton(top_bar, text=get_text("btn_save_pdf"), font=ctk.CTkFont(weight="bold"), fg_color="#1565C0", hover_color="#0D47A1", command=self.generate_pdf)
        self.btn_save.pack(side="right", padx=2)
        self.btn_clear = ctk.CTkButton(top_bar, text=get_text("btn_clear"), width=60, fg_color="#D32F2F", hover_color="#B71C1C", command=self.clear_all)
        self.btn_clear.pack(side="right", padx=(2, 10))

        page_bar = ctk.CTkFrame(self.center_frame, fg_color="gray70", height=30)
        page_bar.pack(fill="x", padx=10, pady=(0, 5))
        
        self.btn_prev_pg = ctk.CTkButton(page_bar, text="<", width=30, fg_color="gray40", command=self.prev_page)
        self.btn_prev_pg.pack(side="left", padx=5, pady=2)
        self.lbl_page_info = ctk.CTkLabel(page_bar, text=get_text("lbl_page_counter").format(self.current_page, self.total_pages), font=ctk.CTkFont(weight="bold"), text_color="black")
        self.lbl_page_info.pack(side="left")
        self.btn_next_pg = ctk.CTkButton(page_bar, text=">", width=30, fg_color="gray40", command=self.next_page)
        self.btn_next_pg.pack(side="left", padx=5, pady=2)
        
        self.btn_add_pg = ctk.CTkButton(page_bar, text=get_text("btn_new_page"), width=80, fg_color="#2E7D32", hover_color="#1B5E20", command=self.add_page)
        self.btn_add_pg.pack(side="left", padx=(15,2))
        
        self.btn_del_pg = ctk.CTkButton(page_bar, text=get_text("btn_del_page"), width=80, fg_color="#D32F2F", hover_color="#B71C1C", command=self.delete_page)
        self.btn_del_pg.pack(side="left", padx=2)

        self.btn_zoom_out = ctk.CTkButton(page_bar, text=get_text("btn_zoom_out_text"), width=40, fg_color="gray30", command=lambda: self.change_zoom(-0.2))
        self.btn_zoom_out.pack(side="right", padx=2)
        self.btn_fit = ctk.CTkButton(page_bar, text=get_text("btn_fit"), width=60, fg_color="gray30", command=lambda: self.change_zoom("fit"))
        self.btn_fit.pack(side="right", padx=2)
        self.btn_zoom_in = ctk.CTkButton(page_bar, text=get_text("btn_zoom_in_text"), width=40, fg_color="gray30", command=lambda: self.change_zoom(0.2))
        self.btn_zoom_in.pack(side="right", padx=2)

        self.canvas_container = ctk.CTkFrame(self.center_frame, fg_color="#2B2B2B")
        self.canvas_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.v_scroll = ctk.CTkScrollbar(self.canvas_container, orientation="vertical")
        self.h_scroll = ctk.CTkScrollbar(self.canvas_container, orientation="horizontal")
        
        self.viewport = tk.Canvas(self.canvas_container, bg="#2B2B2B", highlightthickness=0)
        self.v_scroll.configure(command=self.viewport.yview)
        self.h_scroll.configure(command=self.viewport.xview)
        self.viewport.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)
        
        self.v_scroll.pack(side="right", fill="y")
        self.h_scroll.pack(side="bottom", fill="x")
        self.viewport.pack(side="left", fill="both", expand=True)

        self.paper_canvas = tk.Canvas(self.viewport, bg="white", width=self.a4_w, height=self.a4_h, highlightthickness=1, highlightbackground="black")
        self.viewport_window = self.viewport.create_window((0, 0), window=self.paper_canvas, anchor="center")

        self.viewport.bind("<Configure>", self.center_canvas_content)

        # MOUSE SCROLL OLAYLARI (Fare tekerleği)
        self.viewport.bind("<MouseWheel>", self._on_mousewheel)
        self.paper_canvas.bind("<MouseWheel>", self._on_mousewheel)

        self.paper_canvas.bind("<ButtonPress-1>", self.on_press)
        self.paper_canvas.bind("<B1-Motion>", self.on_drag)
        self.paper_canvas.bind("<ButtonRelease-1>", self.on_release)
        
        self.winfo_toplevel().bind("<Delete>", self.on_delete_key)
        self.winfo_toplevel().bind("<Control-z>", self.undo)
        self.winfo_toplevel().bind("<Control-y>", self.redo)

        # ==========================================
        # --- SAĞ: KATMANLAR VE ÖZELLİKLER ---
        # ==========================================
        self.right_frame = ctk.CTkFrame(self, fg_color=("gray85", "gray20"))
        self.right_frame.grid(row=0, column=2, sticky="nsew", padx=(5, 10), pady=10)
        
        self.lbl_layers = ctk.CTkLabel(self.right_frame, text=get_text("lbl_layers"), font=ctk.CTkFont(weight="bold", size=14), text_color="#F57C00")
        self.lbl_layers.pack(pady=(10, 5))
        
        self.layer_frame = ctk.CTkScrollableFrame(self.right_frame, height=120, fg_color=("gray80", "gray15"))
        self.layer_frame.pack(fill="x", padx=10, pady=5)

        self.lbl_prop = ctk.CTkLabel(self.right_frame, text=get_text("lbl_properties"), font=ctk.CTkFont(weight="bold", size=15), text_color="#1565C0")
        self.lbl_prop.pack(pady=(15, 5))
        
        self.prop_scroll = ctk.CTkScrollableFrame(self.right_frame, fg_color="transparent")
        self.prop_scroll.pack(fill="both", expand=True, padx=5)
        
        self.prop_widgets = []
        self.refresh_props()

    def build_toolbox_buttons(self):
        for widget in self.tools_container.winfo_children(): widget.destroy()
        tools = [
            (get_text("btn_add_text"), self.add_text),
            (get_text("btn_add_rect"), self.add_rect),
            (get_text("btn_add_square"), self.add_square),
            (get_text("btn_add_circle"), self.add_circle),
            (get_text("btn_add_triangle"), self.add_triangle),
            (get_text("btn_add_line"), self.add_line),
            (get_text("btn_add_table"), self.add_table),
            (get_text("btn_add_image"), self.add_image),
            (get_text("btn_add_checkbox"), self.add_checkbox),
            (get_text("btn_add_whiteout"), self.add_whiteout)
        ]
        for text, cmd in tools:
            c_hover = "#E65100" if "Tipeks" in text or "Whiteout" in text else "#2E7D32"
            ctk.CTkButton(self.tools_container, text=text, fg_color="gray40", hover_color=c_hover, anchor="w", width=160, command=cmd).pack(fill="x", padx=15, pady=4)

    def center_canvas_content(self, event=None):
        cw, ch = self.viewport.winfo_width(), self.viewport.winfo_height()
        if cw <= 1 or ch <= 1: 
            self.after(50, self.center_canvas_content)
            return
        iw, ih = self.paper_canvas.winfo_reqwidth(), self.paper_canvas.winfo_reqheight()
        x = cw / 2 if cw > iw else iw / 2
        y = ch / 2 if ch > ih else ih / 2
        self.viewport.coords(self.viewport_window, x, y)
        self.viewport.configure(scrollregion=self.viewport.bbox("all"))

    def _on_mousewheel(self, event):
        # Mouse tekerleğiyle kaydırma (Windows ve Mac için standart)
        self.viewport.yview_scroll(int(-1*(event.delta/120)), "units")

    def update_language(self):
        self.lbl_toolbox.configure(text=get_text("lbl_studio_tools"))
        self.lbl_bg.configure(text=get_text("lbl_bg_color"))
        self.btn_bg_custom.configure(text=get_text("btn_custom_color"))
        self.btn_clear.configure(text=get_text("btn_clear"))
        self.btn_guide.configure(text=get_text("btn_guide_studio"))
        self.btn_save.configure(text=get_text("btn_save_pdf"))
        self.btn_import.configure(text=get_text("btn_import_pdf"))
        self.btn_add_pg.configure(text=get_text("btn_new_page"))
        self.btn_del_pg.configure(text=get_text("btn_del_page"))
        self.btn_undo.configure(text=get_text("btn_undo"))
        self.btn_redo.configure(text=get_text("btn_redo"))
        self.btn_zoom_in.configure(text=get_text("btn_zoom_in_text"))
        self.btn_zoom_out.configure(text=get_text("btn_zoom_out_text"))
        self.btn_fit.configure(text=get_text("btn_fit"))
        self.lbl_layers.configure(text=get_text("lbl_layers"))
        self.lbl_prop.configure(text=get_text("lbl_properties"))
        self.lbl_page_info.configure(text=get_text("lbl_page_counter").format(self.current_page, self.total_pages))
        self.build_toolbox_buttons()
        self.refresh_props()
        
    def show_guide(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title(get_text("btn_guide_studio"))
        dialog.geometry("550x450")
        dialog.attributes("-topmost", True)
        center_window(dialog, self.winfo_toplevel())
        ctk.CTkLabel(dialog, text="ZİNCİRLEME OTOMASYON REHBERİ" if lang_manager.current_lang == "TR" else "STUDIO GUIDE", font=ctk.CTkFont(size=16, weight="bold"), text_color="#1565C0").pack(pady=(20,10))
        ctk.CTkLabel(dialog, text=get_text("msg_guide_studio"), font=ctk.CTkFont(size=12), justify="left", wraplength=480).pack(padx=20, pady=10)
        ctk.CTkButton(dialog, text="Tamam / OK", command=dialog.destroy).pack(pady=20)

    # ==========================================
    # --- ÇOKLU SAYFA VE ARKA PLAN ---
    # ==========================================
    def add_page(self):
        self.total_pages += 1
        self.current_page = self.total_pages
        self.pages_data[self.current_page] = {"items": [], "bg_color": "white", "bg_image_path": None}
        self.bg_image_tk = None
        self.save_state(); self.update_page_ui()
        
    def delete_page(self):
        if self.total_pages <= 1:
            messagebox.showwarning(get_text("dialog_warning"), get_text("msg_cannot_delete_last_page"))
            return
        del self.pages_data[self.current_page]
        new_data, new_idx = {}, 1
        for k in sorted(self.pages_data.keys()):
            new_data[new_idx] = self.pages_data[k]; new_idx += 1
        self.pages_data = new_data
        self.total_pages -= 1
        if self.current_page > self.total_pages: self.current_page = self.total_pages
        self.bg_image_tk = None
        self.save_state(); self.update_page_ui()

    def prev_page(self):
        if self.current_page > 1: self.current_page -= 1; self.bg_image_tk = None; self.update_page_ui()

    def next_page(self):
        if self.current_page < self.total_pages: self.current_page += 1; self.bg_image_tk = None; self.update_page_ui()

    def update_page_ui(self):
        self.lbl_page_info.configure(text=get_text("lbl_page_counter").format(self.current_page, self.total_pages))
        self.selected_id = None
        self.render_canvas()
        self.refresh_props()

    def change_bg(self, val):
        m = {"Beyaz (White)": "white", "Krem (Cream)": "#FDF5E6", "Siyah (Black)": "black"}
        self.pages_data[self.current_page]["bg_color"] = m.get(val, "white")
        self.pages_data[self.current_page]["bg_image_path"] = None
        self.bg_image_tk = None
        self.save_state(); self.render_canvas()

    def pick_bg_color(self):
        color = colorchooser.askcolor(title="Renk Seçin")[1]
        if color:
            self.pages_data[self.current_page]["bg_color"] = color
            self.pages_data[self.current_page]["bg_image_path"] = None
            self.bg_image_tk = None
            self.save_state(); self.render_canvas()

    def import_pdf_bg(self):
        path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if not path: return
        
        # Ağır render işlemi için yüklenme diyalogunu çağırıyoruz
        from modules.pdf_araclari import ProgressWindow
        self.progress = ProgressWindow(self.winfo_toplevel(), get_text("progress_processing"))
        
        try:
            doc = fitz.open(path)
            total = len(doc)
            self.pages_data.clear()
            self.total_pages = total
            self.current_page = 1
            
            temp_dir = tempfile.gettempdir()
            for i in range(total):
                # Her sayfa arka plan resmine dönüştürülürken yüklenme kutusunun donmasını engelle
                if hasattr(self, 'progress') and self.progress.winfo_exists():
                    self.progress.update()

                page = doc.load_page(i)
                pix = page.get_pixmap(dpi=150)
                temp_path = os.path.join(temp_dir, f"bg_{uuid.uuid4().hex}.png")
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                img.save(temp_path)
                self.pages_data[i+1] = {"items": [], "bg_color": "white", "bg_image_path": temp_path}
                
            doc.close()
            self.bg_image_tk = None
            self.update_page_ui(); self.save_state()
        except Exception as e:
            messagebox.showerror("Hata", str(e))
        finally:
            # İşlem bittiğinde yüklenme kutusunu güvenli şekilde yok et
            if hasattr(self, 'progress') and self.progress.winfo_exists():
                self.progress.destroy()

    # ==========================================
    # --- TEMİZ HAFIZA YÖNETİMİ ---
    # ==========================================
    def get_clean_state(self):
        state = {}
        for p, d in self.pages_data.items():
            clean_items = [{k: v for k, v in item.items() if k != "tk_id"} for item in d["items"]]
            state[p] = {"bg_color": d["bg_color"], "bg_image_path": d["bg_image_path"], "items": clean_items}
        return state

    def save_state(self):
        clean_state = self.get_clean_state()
        self.history = self.history[:self.history_pos + 1]
        self.history.append(clean_state)
        self.history_pos += 1

    def undo(self, event=None):
        if self.history_pos > 0:
            self.history_pos -= 1
            self.pages_data = self.get_clean_state_from_history(self.history_pos)
            self.bg_image_tk = None; self.selected_id = None
            self.render_canvas(); self.refresh_props()

    def redo(self, event=None):
        if self.history_pos < len(self.history) - 1:
            self.history_pos += 1
            self.pages_data = self.get_clean_state_from_history(self.history_pos)
            self.bg_image_tk = None; self.selected_id = None
            self.render_canvas(); self.refresh_props()
            
    def get_clean_state_from_history(self, index):
        new_data = {}
        for p, d in self.history[index].items():
            new_data[p] = {"bg_color": d["bg_color"], "bg_image_path": d["bg_image_path"], "items": [{k: v for k, v in item.items()} for item in d["items"]]}
        return new_data

    # ==========================================
    # --- NESNE EKLEYİCİLER ---
    # ==========================================
    def _add_item(self, data):
        self.pages_data[self.current_page]["items"].append(data)
        self.selected_id = data["id"]
        self.save_state(); self.render_canvas(); self.refresh_props()

    def add_text(self): self._add_item({"id": str(uuid.uuid4()), "type": "text", "text": "Yeni Metin", "x": 100, "y": 100, "size": 16, "color": "black", "font": "Arial", "bold": False, "italic": False, "underline": False, "strike": False})
    def add_rect(self): self._add_item({"id": str(uuid.uuid4()), "type": "rect", "x": 100, "y": 100, "w": 150, "h": 100, "color": "black", "fill": ""}) # Şeffaf eklenebilir, artık matematiksel seçilecek
    def add_square(self): self._add_item({"id": str(uuid.uuid4()), "type": "square", "x": 100, "y": 100, "w": 100, "h": 100, "color": "black", "fill": ""})
    def add_circle(self): self._add_item({"id": str(uuid.uuid4()), "type": "circle", "x": 100, "y": 100, "w": 100, "h": 100, "color": "black", "fill": ""})
    def add_triangle(self): self._add_item({"id": str(uuid.uuid4()), "type": "triangle", "x": 100, "y": 100, "w": 100, "h": 100, "color": "black", "fill": ""})
    def add_line(self): self._add_item({"id": str(uuid.uuid4()), "type": "line", "x": 100, "y": 100, "w": 200, "h": 4, "color": "black"})
    def add_checkbox(self): self._add_item({"id": str(uuid.uuid4()), "type": "checkbox", "text": "☐", "x": 100, "y": 100, "size": 24, "color": "black", "font": "Arial", "bold": False, "italic": False})
    def add_whiteout(self): self._add_item({"id": str(uuid.uuid4()), "type": "whiteout", "x": 100, "y": 100, "w": 200, "h": 30, "color": "white", "fill": "white"})

    def add_table(self):
        r = simpledialog.askinteger("Tablo", "Satır Sayısı:", initialvalue=3, minvalue=1, maxvalue=20, parent=self)
        if not r: return
        c = simpledialog.askinteger("Tablo", "Sütun Sayısı:", initialvalue=3, minvalue=1, maxvalue=20, parent=self)
        if not c: return
        self._add_item({"id": str(uuid.uuid4()), "type": "table", "x": 100, "y": 100, "w": 300, "h": 200, "rows": r, "cols": c, "color": "black", "fill": ""})

    def add_image(self):
        path = filedialog.askopenfilename(filetypes=[("Resim", "*.png *.jpg *.jpeg")])
        if not path: return
        try:
            img = Image.open(path)
            w, h = img.size
            ratio = 200.0 / max(w, h)
            self._add_item({"id": str(uuid.uuid4()), "type": "image", "x": 100, "y": 100, "w": int(w*ratio), "h": int(h*ratio), "path": path})
        except: pass

    # ==========================================
    # --- YENİ NESİL TUVAL ÇİZİM MOTORU ---
    # ==========================================
    def clear_all(self):
        self.pages_data[self.current_page]["items"].clear()
        self.pages_data[self.current_page]["bg_image_path"] = None
        self.bg_image_tk = None
        self.save_state(); self.selected_id = None; self.render_canvas(); self.refresh_props()

    def change_zoom(self, amount):
        if amount == "fit": self.zoom_factor = 1.0
        else: self.zoom_factor = max(0.2, min(self.zoom_factor + amount, 3.0))
        self.bg_image_tk = None 
        
        cw, ch = int(self.a4_w * self.zoom_factor), int(self.a4_h * self.zoom_factor)
        self.paper_canvas.configure(width=cw, height=ch)
        self.render_canvas()
        self.center_canvas_content()

    def render_canvas(self):
        self.paper_canvas.delete("all")
        page_d = self.pages_data[self.current_page]
        
        cw, ch = int(self.a4_w * self.zoom_factor), int(self.a4_h * self.zoom_factor)
        
        self.paper_canvas.configure(bg=page_d["bg_color"])
        
        if page_d["bg_image_path"] and os.path.exists(page_d["bg_image_path"]):
            if not self.bg_image_tk:
                img = Image.open(page_d["bg_image_path"]).resize((cw, ch), Image.Resampling.LANCZOS)
                self.bg_image_tk = ImageTk.PhotoImage(img)
            self.paper_canvas.create_image(0, 0, anchor="nw", image=self.bg_image_tk, tags="bg_paper")

        for item in page_d["items"]:
            i_type = item["type"]
            x, y = item["x"] * self.zoom_factor, item["y"] * self.zoom_factor
            w, h = item.get("w",0) * self.zoom_factor, item.get("h",0) * self.zoom_factor
            
            is_sel = (item["id"] == self.selected_id)
            
            if i_type == "whiteout":
                out_color = "gray" if is_sel else "white"
                out_dash = (4,4) if is_sel else None
                out_width = 2 if is_sel else 0
                item["tk_id"] = self.paper_canvas.create_rectangle(x, y, x+w, y+h, outline=out_color, width=out_width, fill="white", dash=out_dash)
                continue

            out_color = "red" if is_sel else item.get("color", "black")
            out_width = 3 if is_sel else 2
            f_color = item.get("fill", "")

            try:
                if i_type in ["rect", "square"]:
                    item["tk_id"] = self.paper_canvas.create_rectangle(x, y, x+w, y+h, outline=out_color, width=out_width, fill=f_color if f_color else "", stipple="gray12" if not f_color else "")
                    
                elif i_type == "table":
                    item["tk_id"] = self.paper_canvas.create_rectangle(x, y, x+w, y+h, outline=out_color, width=out_width, fill=f_color if f_color else "", stipple="gray12" if not f_color else "")
                    r, c = item["rows"], item["cols"]
                    for row in range(1, r): self.paper_canvas.create_line(x, y + (h/r)*row, x+w, y + (h/r)*row, fill="gray")
                    for col in range(1, c): self.paper_canvas.create_line(x + (w/c)*col, y, x + (w/c)*col, y+h, fill="gray")
                        
                elif i_type == "circle":
                    item["tk_id"] = self.paper_canvas.create_oval(x, y, x+w, y+h, outline=out_color, width=out_width, fill=f_color if f_color else "", stipple="gray12" if not f_color else "")
                
                elif i_type == "triangle":
                    pts = [x + w/2, y, x, y + h, x + w, y + h]
                    item["tk_id"] = self.paper_canvas.create_polygon(pts, outline=out_color, width=out_width, fill=f_color if f_color else "", stipple="gray12" if not f_color else "")
                    
                elif i_type == "line":
                    item["tk_id"] = self.paper_canvas.create_line(x, y + h/2, x+w, y + h/2, fill=out_color, width=max(1, item["h"]*self.zoom_factor))
                
                elif i_type == "image":
                    img_key = f"{item['id']}_{self.zoom_factor}"
                    if img_key not in self.tk_images:
                        img = Image.open(item["path"]).resize((int(w), int(h)), Image.Resampling.LANCZOS)
                        self.tk_images[img_key] = ImageTk.PhotoImage(img)
                    item["tk_id"] = self.paper_canvas.create_image(x, y, anchor="nw", image=self.tk_images[img_key])
                    if is_sel: self.paper_canvas.create_rectangle(x-2, y-2, x+w+2, y+h+2, outline="red", width=2)
                
                elif i_type in ["text", "checkbox"]:
                    mods = []
                    if item.get("bold"): mods.append("bold")
                    if item.get("italic"): mods.append("italic")
                    if item.get("underline"): mods.append("underline")
                    if item.get("strike"): mods.append("overstrike")
                    fnt = [item.get("font", "Arial"), int(item["size"] * self.zoom_factor)] + mods
                    
                    item["tk_id"] = self.paper_canvas.create_text(x, y, text=item["text"], font=tuple(fnt), fill=item.get("color", "black"), anchor="nw", justify="left")
                    if is_sel:
                        bbox = self.paper_canvas.bbox(item["tk_id"])
                        if bbox: self.paper_canvas.create_rectangle(bbox[0]-4, bbox[1]-4, bbox[2]+4, bbox[3]+4, outline="red", width=2)
            except: pass

    # ==========================================
    # --- MOUSE ETKİLEŞİMİ (MATEMATİKSEL KUTU SEÇİMİ) ---
    # ==========================================
    def on_press(self, event):
        x, y = self.paper_canvas.canvasx(event.x), self.paper_canvas.canvasy(event.y)
        self.selected_id = None
        
        # OLUMLU DÜZELTME: Şeffaf Alanlar İçin Bounding Box (Kutu İçi) Tarama
        items = self.pages_data[self.current_page]["items"]
        for item in reversed(items): 
            tol = 5 * self.zoom_factor 
            
            ix = item["x"] * self.zoom_factor
            iy = item["y"] * self.zoom_factor
            iw = item.get("w", 50) * self.zoom_factor
            ih = item.get("h", 50) * self.zoom_factor
            
            if item["type"] in ["text", "checkbox"] and "tk_id" in item:
                bbox = self.paper_canvas.bbox(item["tk_id"])
                if bbox:
                    ix, iy = bbox[0], bbox[1]
                    iw, ih = bbox[2] - bbox[0], bbox[3] - bbox[1]
            elif item["type"] == "line":
                ih = max(10, item.get("h", 4) * self.zoom_factor)
                iy = iy + (item.get("h",4)*self.zoom_factor/2) - (ih/2)
                
            ex1, ey1 = ix - tol, iy - tol
            ex2, ey2 = ix + iw + tol, iy + ih + tol
            
            if ex1 <= x <= ex2 and ey1 <= y <= ey2:
                self.selected_id = item["id"]
                self.drag_data = {"id": item["id"], "x": x, "y": y, "ox": item["x"], "oy": item["y"]}
                break

        self.render_canvas(); self.refresh_props()

    def on_drag(self, event):
        if self.selected_id:
            x, y = self.paper_canvas.canvasx(event.x), self.paper_canvas.canvasy(event.y)
            dx, dy = (x - self.drag_data["x"]) / self.zoom_factor, (y - self.drag_data["y"]) / self.zoom_factor
            
            for item in self.pages_data[self.current_page]["items"]:
                if item["id"] == self.selected_id:
                    new_x, new_y = self.drag_data["ox"] + dx, self.drag_data["oy"] + dy
                    
                    self.paper_canvas.delete("snap_line")
                    c_x, c_y = self.a4_w / 2, self.a4_h / 2
                    
                    item_w, item_h = item.get("w", 50), item.get("h", 50)
                    if item["type"] in ["text", "checkbox"]:
                        bbox = self.paper_canvas.bbox(item.get("tk_id"))
                        if bbox: item_w, item_h = (bbox[2]-bbox[0])/self.zoom_factor, (bbox[3]-bbox[1])/self.zoom_factor
                        
                    i_cx, i_cy = new_x + (item_w / 2), new_y + (item_h / 2)
                    
                    if abs(i_cx - c_x) < 10:
                        new_x = c_x - (item_w / 2)
                        self.paper_canvas.create_line(c_x*self.zoom_factor, 0, c_x*self.zoom_factor, self.a4_h*self.zoom_factor, fill="red", dash=(4,4), tags="snap_line")
                    
                    if abs(i_cy - c_y) < 10:
                        new_y = c_y - (item_h / 2)
                        self.paper_canvas.create_line(0, c_y*self.zoom_factor, self.a4_w*self.zoom_factor, c_y*self.zoom_factor, fill="red", dash=(4,4), tags="snap_line")
                    
                    item["x"], item["y"] = new_x, new_y
                    self.render_canvas()
                    break

    def on_release(self, event):
        self.paper_canvas.delete("snap_line")
        if self.selected_id: self.save_state()

    def on_delete_key(self, event=None):
        if self.selected_id:
            items = self.pages_data[self.current_page]["items"]
            self.pages_data[self.current_page]["items"] = [i for i in items if i["id"] != self.selected_id]
            self.selected_id = None
            self.save_state(); self.render_canvas(); self.refresh_props()

    # ==========================================
    # --- SAĞ PANEL (KATMANLAR VE ÖZELLİKLER) ---
    # ==========================================
    def refresh_props(self):
        for w in self.layer_frame.winfo_children(): w.destroy()
        for w in self.prop_scroll.winfo_children(): w.destroy()
        
        items = self.pages_data[self.current_page]["items"]
        
        counts = {}
        for item in reversed(items):
            i_type = item["type"]
            counts[i_type] = counts.get(i_type, 0) + 1
            t_name = get_text(f"item_{i_type}")
            name = f"{t_name} {counts[i_type]}"
            
            btn_col = "#2E7D32" if item["id"] == self.selected_id else "gray40"
            btn = ctk.CTkButton(self.layer_frame, text=name, fg_color=btn_col, anchor="w", height=28, command=lambda id=item["id"]: self.select_from_layer(id))
            btn.pack(fill="x", pady=2)

        sel_item = next((i for i in items if i["id"] == self.selected_id), None)
        if not sel_item:
            ctk.CTkLabel(self.prop_scroll, text=get_text("msg_select_object"), text_color="gray").pack(pady=20)
            return

        f_layer = ctk.CTkFrame(self.prop_scroll, fg_color="transparent")
        f_layer.pack(fill="x", pady=(0, 15))
        ctk.CTkButton(f_layer, text=get_text("btn_bring_forward"), fg_color="gray40", command=lambda: self.change_z_index("up")).pack(side="left", padx=2, expand=True, fill="x")
        ctk.CTkButton(f_layer, text=get_text("btn_send_backward"), fg_color="gray40", command=lambda: self.change_z_index("down")).pack(side="left", padx=2, expand=True, fill="x")

        def make_updater(key, is_int=False):
            def updater(val):
                sel_item[key] = int(val) if is_int else val
                self.render_canvas()
            return updater
        def make_save_state(e=None): self.save_state()

        if sel_item["type"] in ["text", "checkbox"]:
            ctk.CTkLabel(self.prop_scroll, text=get_text("lbl_item_text"), anchor="w", font=ctk.CTkFont(weight="bold")).pack(fill="x", pady=(0,5))
            box = ctk.CTkTextbox(self.prop_scroll, height=80, border_width=1, border_color="gray")
            box.insert("1.0", sel_item["text"]); box.pack(fill="x", pady=(0, 10))
            def on_text_edit(e): sel_item["text"] = box.get("1.0", "end-1c"); self.render_canvas()
            box.bind("<KeyRelease>", on_text_edit); box.bind("<FocusOut>", make_save_state)

            f_fnt = ctk.CTkFrame(self.prop_scroll, fg_color="transparent"); f_fnt.pack(fill="x", pady=5)
            var_font = ctk.StringVar(value=sel_item.get("font", "Arial"))
            ctk.CTkOptionMenu(f_fnt, values=["Arial", "Times New Roman", "Courier", "Helvetica"], variable=var_font, command=lambda v: [make_updater("font")(v), make_save_state()]).pack(side="left", expand=True, fill="x", padx=(0,5))

            slider = ctk.CTkSlider(f_fnt, from_=8, to=120, number_of_steps=112, width=100, command=make_updater("size", True))
            slider.set(sel_item["size"]); slider.pack(side="right"); slider.bind("<ButtonRelease-1>", make_save_state)

            f_s1 = ctk.CTkFrame(self.prop_scroll, fg_color="transparent"); f_s1.pack(fill="x", pady=2)
            var_b = ctk.BooleanVar(value=sel_item.get("bold", False))
            ctk.CTkCheckBox(f_s1, text="Kalın (B)", variable=var_b, command=lambda: [make_updater("bold")(var_b.get()), make_save_state()]).pack(side="left", padx=5)
            var_i = ctk.BooleanVar(value=sel_item.get("italic", False))
            ctk.CTkCheckBox(f_s1, text="İtalik (I)", variable=var_i, command=lambda: [make_updater("italic")(var_i.get()), make_save_state()]).pack(side="left", padx=5)

            f_s2 = ctk.CTkFrame(self.prop_scroll, fg_color="transparent"); f_s2.pack(fill="x", pady=(2, 10))
            var_u = ctk.BooleanVar(value=sel_item.get("underline", False))
            ctk.CTkCheckBox(f_s2, text=get_text("opt_underline"), variable=var_u, command=lambda: [make_updater("underline")(var_u.get()), make_save_state()]).pack(side="left", padx=5)
            var_s = ctk.BooleanVar(value=sel_item.get("strike", False))
            ctk.CTkCheckBox(f_s2, text=get_text("opt_strike"), variable=var_s, command=lambda: [make_updater("strike")(var_s.get()), make_save_state()]).pack(side="left", padx=5)

        if sel_item["type"] in ["rect", "square", "circle", "triangle", "table", "image", "whiteout", "line"]:
            ctk.CTkLabel(self.prop_scroll, text=get_text("lbl_item_width"), anchor="w", font=ctk.CTkFont(weight="bold")).pack(fill="x", pady=(5,0))
            slider_w = ctk.CTkSlider(self.prop_scroll, from_=10, to=800, number_of_steps=790)
            slider_w.set(sel_item.get("w", 50)); slider_w.pack(fill="x", pady=(5,10))
            def on_w_resize(val): 
                sel_item["w"] = int(val)
                if sel_item["type"] == "square": sel_item["h"] = int(val)
                
                # Görsel büyütme önbelleğini temizle
                if sel_item["type"] == "image":
                    keys_to_del = [k for k in self.tk_images.keys() if k.startswith(f"{sel_item['id']}_")]
                    for k in keys_to_del: del self.tk_images[k]
                    
                self.render_canvas()
            slider_w.configure(command=on_w_resize); slider_w.bind("<ButtonRelease-1>", make_save_state)

            if sel_item["type"] not in ["square"]:
                ctk.CTkLabel(self.prop_scroll, text=get_text("lbl_item_height") if sel_item["type"] != "line" else "Kalınlık:", anchor="w", font=ctk.CTkFont(weight="bold")).pack(fill="x", pady=(5,0))
                slider_h = ctk.CTkSlider(self.prop_scroll, from_=1 if sel_item["type"]=="line" else 10, to=800, number_of_steps=790)
                slider_h.set(sel_item.get("h", 50)); slider_h.pack(fill="x", pady=(5,10))
                def on_h_resize(val): 
                    sel_item["h"] = int(val)
                    
                    # Görsel büyütme önbelleğini temizle
                    if sel_item["type"] == "image":
                        keys_to_del = [k for k in self.tk_images.keys() if k.startswith(f"{sel_item['id']}_")]
                        for k in keys_to_del: del self.tk_images[k]
                        
                    self.render_canvas()
                slider_h.configure(command=on_h_resize); slider_h.bind("<ButtonRelease-1>", make_save_state)

        def pick_color_for(key):
            color = colorchooser.askcolor(title="Renk Seç")[1]
            if color: sel_item[key] = color; self.render_canvas(); make_save_state(); self.refresh_props()

        if "color" in sel_item and sel_item["type"] != "whiteout":
            ctk.CTkLabel(self.prop_scroll, text=get_text("lbl_item_color"), anchor="w", font=ctk.CTkFont(weight="bold")).pack(fill="x", pady=(10,2))
            ctk.CTkButton(self.prop_scroll, text=get_text("btn_change_out_color"), fg_color=sel_item["color"] if sel_item["color"] else "gray", text_color="white" if sel_item["color"]!="white" else "black", command=lambda: pick_color_for("color")).pack(fill="x")

        if "fill" in sel_item and sel_item["type"] not in ["whiteout", "line"]:
            ctk.CTkLabel(self.prop_scroll, text=get_text("lbl_item_fill"), anchor="w", font=ctk.CTkFont(weight="bold")).pack(fill="x", pady=(15,2))
            f_fill = ctk.CTkFrame(self.prop_scroll, fg_color="transparent"); f_fill.pack(fill="x")
            
            # OLUMLU DÜZELTME: Buton İsimleri Dinamik Olarak language_manager'dan Çekildi
            ctk.CTkButton(f_fill, text=get_text("btn_change_in_color"), fg_color=sel_item["fill"] if sel_item["fill"] else "gray", text_color="white" if sel_item["fill"]!="white" else "black", command=lambda: pick_color_for("fill")).pack(side="left", fill="x", expand=True, padx=(0,2))
            ctk.CTkButton(f_fill, text=get_text("btn_make_transp"), fg_color="gray40", command=lambda: [make_updater("fill")(""), make_save_state(), self.refresh_props()]).pack(side="right", fill="x", expand=True, padx=(2,0))

        ctk.CTkButton(self.prop_scroll, text=get_text("btn_del_item"), fg_color="#D32F2F", hover_color="#B71C1C", command=self.on_delete_key).pack(fill="x", pady=20)

    def select_from_layer(self, item_id):
        self.selected_id = item_id; self.render_canvas(); self.refresh_props()

    def change_z_index(self, direction):
        items = self.pages_data[self.current_page]["items"]
        idx = next((i for i, item in enumerate(items) if item["id"] == self.selected_id), None)
        if idx is not None:
            if direction == "up" and idx < len(items) - 1: items[idx], items[idx+1] = items[idx+1], items[idx]
            elif direction == "down" and idx > 0: items[idx], items[idx-1] = items[idx-1], items[idx]
            self.save_state(); self.render_canvas(); self.refresh_props()

    # ==========================================
    # --- PDF ÜRETİM MOTORU ---
    # ==========================================
    def hex_to_rgb(self, hx):
        if not hx: return None
        if hx in ["white", "black", "red", "blue", "green", "gray"]:
            m = {"white":(1,1,1), "black":(0,0,0), "red":(1,0,0), "blue":(0,0,1), "green":(0,1,0), "gray":(0.5,0.5,0.5)}
            return m[hx]
        hx = hx.lstrip('#')
        try: return tuple(int(hx[i:i+2], 16)/255.0 for i in (0, 2, 4))
        except: return (0,0,0)

    def generate_pdf(self):
        save_path = filedialog.asksaveasfilename(title="PDF'i Kaydet", defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], initialfile="Yeni_Belge.pdf")
        if not save_path: return

        try:
            doc = fitz.open()
            fonts = {"Arial": "helv", "Times New Roman": "tiro", "Courier": "cour", "Helvetica": "helv"}
            if sys.platform == "win32" and os.path.exists("C:/Windows/Fonts/arial.ttf"): fonts["Arial"] = "arial_tr"
            
            for p_num in range(1, self.total_pages + 1):
                page = doc.new_page(width=self.a4_w, height=self.a4_h)
                p_data = self.pages_data[p_num]
                
                if p_data["bg_image_path"] and os.path.exists(p_data["bg_image_path"]):
                    try: page.insert_image(page.rect, filename=p_data["bg_image_path"])
                    except: pass
                elif p_data["bg_color"] and p_data["bg_color"] != "white":
                    bg_rgb = self.hex_to_rgb(p_data["bg_color"])
                    page.draw_rect(page.rect, color=bg_rgb, fill=bg_rgb)
                
                if "arial_tr" in fonts.values() and sys.platform == "win32":
                    page.insert_font(fontname="arial_tr", fontfile="C:/Windows/Fonts/arial.ttf")
                    page.insert_font(fontname="arial_tr_b", fontfile="C:/Windows/Fonts/arialbd.ttf")
                    page.insert_font(fontname="arial_tr_i", fontfile="C:/Windows/Fonts/ariali.ttf")
                    page.insert_font(fontname="arial_tr_bi", fontfile="C:/Windows/Fonts/arialbi.ttf")

                for item in p_data["items"]:
                    rgb_c = self.hex_to_rgb(item.get("color", "black"))
                    rgb_f = self.hex_to_rgb(item.get("fill", ""))
                    x, y = item["x"], item["y"]
                    
                    if item["type"] in ["text", "checkbox"]:
                        base_f = fonts.get(item.get("font", "Arial"), "helv")
                        if base_f == "arial_tr":
                            if item.get("bold") and item.get("italic"): fn = "arial_tr_bi"
                            elif item.get("bold"): fn = "arial_tr_b"
                            elif item.get("italic"): fn = "arial_tr_i"
                            else: fn = "arial_tr"
                        else:
                            if item.get("bold") and item.get("italic"): fn = "hebo" 
                            elif item.get("bold"): fn = "hebo"
                            elif item.get("italic"): fn = "heit"
                            else: fn = base_f
                            
                        lines = item["text"].split("\n")
                        cur_y = y + item["size"]
                        for line in lines:
                            page.insert_text(fitz.Point(x, cur_y), line, fontname=fn, fontsize=item["size"], color=rgb_c)
                            if item.get("underline") or item.get("strike"):
                                tw = fitz.Font(fn if fn in ["helv","hebo","heit"] else "helv").text_length(line, fontsize=item["size"])
                                if item.get("underline"): page.draw_line(fitz.Point(x, cur_y + item["size"]*0.1), fitz.Point(x+tw, cur_y + item["size"]*0.1), color=rgb_c, width=max(1, item["size"]*0.06))
                                if item.get("strike"): page.draw_line(fitz.Point(x, cur_y - item["size"]*0.3), fitz.Point(x+tw, cur_y - item["size"]*0.3), color=rgb_c, width=max(1, item["size"]*0.06))
                            cur_y += item["size"] * 1.2
                            
                    elif item["type"] in ["rect", "square", "whiteout"]:
                        if item["type"] == "whiteout" or (item.get("color")=="white" and item.get("fill")=="white"):
                            page.draw_rect(fitz.Rect(x, y, x+item["w"], y+item["h"]), color=(1,1,1), fill=(1,1,1), width=0)
                        else:
                            page.draw_rect(fitz.Rect(x, y, x+item["w"], y+item["h"]), color=rgb_c, fill=rgb_f, width=2)
                        
                    elif item["type"] == "circle":
                        page.draw_circle(fitz.Point(x+item["w"]/2, y+item["h"]/2), item["w"]/2, color=rgb_c, fill=rgb_f, width=2)
                        
                    elif item["type"] == "triangle":
                        p1, p2, p3 = fitz.Point(x+item["w"]/2, y), fitz.Point(x, y+item["h"]), fitz.Point(x+item["w"], y+item["h"])
                        if rgb_f:
                            try: page.draw_polygon([p1, p2, p3], color=rgb_c, fill=rgb_f, width=2)
                            except: pass
                        else:
                            page.draw_line(p1, p2, color=rgb_c, width=2); page.draw_line(p2, p3, color=rgb_c, width=2); page.draw_line(p3, p1, color=rgb_c, width=2)
                    
                    elif item["type"] == "line":
                        page.draw_line(fitz.Point(x, y+item["h"]/2), fitz.Point(x+item["w"], y+item["h"]/2), color=rgb_c, width=item["h"])
                        
                    elif item["type"] == "table":
                        w, h, r, c = item["w"], item["h"], item["rows"], item["cols"]
                        page.draw_rect(fitz.Rect(x, y, x+w, y+h), color=rgb_c, fill=rgb_f, width=2)
                        for row in range(1, r): page.draw_line(fitz.Point(x, y+(h/r)*row), fitz.Point(x+w, y+(h/r)*row), color=(0.5,0.5,0.5))
                        for col in range(1, c): page.draw_line(fitz.Point(x+(w/c)*col, y), fitz.Point(x+(w/c)*col, y+h), color=(0.5,0.5,0.5))
                        
                    elif item["type"] == "image":
                        if os.path.exists(item["path"]):
                            try: page.insert_image(fitz.Rect(x, y, x+item["w"], y+item["h"]), filename=item["path"])
                            except: pass

            # --- UYAP UYUMLULUK VE GÜVENLİK ENTEGRASYONU ---
            # 1. Tuval üzerine eklenen tüm metin, şekil ve görsel katmanlarını PDF yapısına düzleştirerek sabitliyoruz
            try:
                for page in doc:
                    page.flatten_widgets()
            except: pass

            # 2. Yerel bilgisayar adını ve dosya yollarını temizlemek için meta verileri sıfırlıyoruz
            doc.set_metadata({})
            try: doc.set_xml_metadata("")
            except: pass
            
            # 3. Çökme hatasını önlemek için 'linear=True' parametresini kaldırarak derin temizlikle kaydediyoruz
            doc.save(
                save_path, 
                deflate=True, 
                garbage=4, 
                clean=True
            )
            doc.close()
            
            for p in self.pages_data.values():
                if p["bg_image_path"] and os.path.exists(p["bg_image_path"]):
                    try: os.remove(p["bg_image_path"])
                    except: pass
            
            from modules.history_manager import add_history
            add_history("✨", "history_action_generic", ["PDF Stüdyosu", os.path.basename(save_path)], save_path)
            StudioSuccessDialog(self.winfo_toplevel(), get_text("dialog_success"), get_text("msg_saved_studio"), save_path)
        except Exception as e:
            messagebox.showerror(get_text("dialog_error"), str(e))