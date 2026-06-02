import customtkinter as ctk
from tkinter import filedialog, messagebox
import fitz  
import os
import sys
import difflib
import webbrowser
import tempfile
import threading
import time
from modules.history_manager import add_history
from modules.pdf_araclari import PasswordDialog, ProgressWindow, ActionDialog
from modules.language_manager import get_text, lang_manager

class PDFKarsilastirmaSayfasi(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        
        self.orig_pdf_path = None
        self.mod_pdf_path = None
        self.orig_password = ""
        self.mod_password = ""
        
        self.setup_ui()
        self.check_page_limits_and_warnings()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        main_card = ctk.CTkFrame(self, fg_color=("gray90", "gray15"), corner_radius=15)
        main_card.pack(expand=True, fill="both", padx=40, pady=40)

        self.title_lbl = ctk.CTkLabel(main_card, text=get_text("tab_compare_title"), font=ctk.CTkFont(size=24, weight="bold"), text_color="#6A1B9A")
        self.title_lbl.pack(pady=(30, 20))

        # --- SEÇİM ALANLARI ---
        selection_frame = ctk.CTkFrame(main_card, fg_color="transparent")
        selection_frame.pack(fill="x", padx=30, pady=20)
        selection_frame.grid_columnconfigure(0, weight=1)
        selection_frame.grid_columnconfigure(1, weight=1)

        # Orijinal Dosya Kutusu
        orig_box = ctk.CTkFrame(selection_frame, fg_color=("gray85", "gray20"), corner_radius=10)
        orig_box.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.lbl_orig_box = ctk.CTkLabel(orig_box, text=get_text("lbl_orig_pdf"), font=ctk.CTkFont(weight="bold"))
        self.lbl_orig_box.pack(pady=(15, 5))
        self.lbl_orig_name = ctk.CTkLabel(orig_box, text=get_text("msg_waiting_file"), text_color="gray")
        self.lbl_orig_name.pack(pady=5)
        self.btn_select_orig = ctk.CTkButton(orig_box, text=get_text("btn_select_file"), fg_color="#1976D2", hover_color="#1565C0", 
                              command=lambda: self.select_pdf("orig"))
        self.btn_select_orig.pack(pady=(10, 15))

        # Değiştirilmiş Dosya Kutusu
        mod_box = ctk.CTkFrame(selection_frame, fg_color=("gray85", "gray20"), corner_radius=10)
        mod_box.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.lbl_mod_box = ctk.CTkLabel(mod_box, text=get_text("lbl_mod_pdf"), font=ctk.CTkFont(weight="bold"))
        self.lbl_mod_box.pack(pady=(15, 5))
        self.lbl_mod_name = ctk.CTkLabel(mod_box, text=get_text("msg_waiting_file"), text_color="gray")
        self.lbl_mod_name.pack(pady=5)
        self.btn_select_mod = ctk.CTkButton(mod_box, text=get_text("btn_select_file"), fg_color="#388E3C", hover_color="#2E7D32", 
                              command=lambda: self.select_pdf("mod"))
        self.btn_select_mod.pack(pady=(10, 15))
        
        # --- 3 AKSİYON BUTONU ---
        btn_frame = ctk.CTkFrame(main_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=30)
        
        self.btn_html = ctk.CTkButton(btn_frame, text=get_text("btn_diff_html"), height=55, font=ctk.CTkFont(size=14, weight="bold"), 
                                      fg_color="#0277BD", hover_color="#01579B", command=self.generate_html_diff)
        self.btn_html.pack(side="left", fill="x", expand=True, padx=5)

        self.btn_visual = ctk.CTkButton(btn_frame, text=get_text("btn_diff_visual"), height=55, font=ctk.CTkFont(size=14, weight="bold"), 
                                        fg_color="#2E7D32", hover_color="#1B5E20", command=self.generate_visual_diff)
        self.btn_visual.pack(side="left", fill="x", expand=True, padx=5)

        self.btn_pdf = ctk.CTkButton(btn_frame, text=get_text("btn_diff_pdf"), height=55, font=ctk.CTkFont(size=14, weight="bold"), 
                                     fg_color="#D84315", hover_color="#E65100", command=self.generate_pdf_diff)
        self.btn_pdf.pack(side="left", fill="x", expand=True, padx=5)

    def check_page_limits_and_warnings(self):
        """ 5 Sayfa sınırını denetleyen ve dil kurallarına göre kullanıcıyı anlık bilgilendiren akıllı panel """
        if not hasattr(self, 'warning_box'):
            self.warning_box = ctk.CTkFrame(self.title_lbl.master, fg_color=("#FFF3E0", "#332B1A"), corner_radius=10, border_width=1, border_color="#FFA726")
            self.warning_box.pack(fill="x", padx=40, pady=(10, 20))
            self.warn_lbl = ctk.CTkLabel(self.warning_box, text="", text_color=("#E65100", "#FFB74D"), font=ctk.CTkFont(size=12), justify="center", wraplength=700)
            self.warn_lbl.pack(padx=15, pady=10)

        is_en = (lang_manager.current_lang == "EN")
        orig_pages, mod_pages = 0, 0
        
        if self.orig_pdf_path:
            try:
                d = fitz.open(self.orig_pdf_path)
                orig_pages = len(d)
                d.close()
            except: pass
            
        if self.mod_pdf_path:
            try:
                d = fitz.open(self.mod_pdf_path)
                mod_pages = len(d)
                d.close()
            except: pass

        max_pages = max(orig_pages, mod_pages)

        if max_pages == 0:
            msg = "💡 Hint: HTML and Text reports work flawlessly on all sizes. Visual PDF marking is active up to 5 pages." if is_en else "💡 İpucu: HTML ve Metin raporları tüm boyutlarda sorunsuz çalışır. Görsel PDF işaretleme en fazla 5 sayfaya kadar aktiftir."
            self.warn_lbl.configure(text=msg)
            self.btn_visual.configure(state="normal")
        elif max_pages > 5:
            msg = f"⚠️ Visual PDF marking is disabled because the document exceeds the 5-page limit ({max_pages} pages). Please use HTML or Text Report for maximum performance." if is_en else f"⚠️ Belge 5 sayfa sınırını aştığı için ({max_pages} sayfa) doğrudan PDF üzerinde işaretleme kapatıldı. Maksimum performans için lütfen HTML veya Metin Raporunu kullanın."
            self.warn_lbl.configure(text=msg)
            self.btn_visual.configure(state="disabled")
        else:
            msg = f"¼ Belge boyutu uygun ({max_pages} sayfa). Tüm karşılaştırma yöntemleri işleme hazır." if not is_en else f"¼ Document size is suitable ({max_pages} pages). All comparison methods are ready to process."
            # Dil kuralı düzeltmesi (¼ işareti get_text'e uyumlu yazıldı)
            msg = f"✅ Belge boyutu uygun ({max_pages} sayfa). Tüm karşılaştırma yöntemleri işleme hazır." if not is_en else f"✅ Document size is suitable ({max_pages} pages). All comparison methods are ready to process."
            self.warn_lbl.configure(text=msg)
            self.btn_visual.configure(state="normal")

    def update_language(self):
        """ Dil anlık değiştiğinde kasmadan tüm buton ve yazıları çevirir. """
        if hasattr(self, 'title_lbl'): self.title_lbl.configure(text=get_text("tab_compare_title"))
        if hasattr(self, 'lbl_orig_box'): self.lbl_orig_box.configure(text=get_text("lbl_orig_pdf"))
        if hasattr(self, 'btn_select_orig'): self.btn_select_orig.configure(text=get_text("btn_select_file"))
        
        # Eğer kullanıcı dosya seçmediyse "Dosya Bekleniyor..." yazısını yeni dile çevir
        if not self.orig_pdf_path and hasattr(self, 'lbl_orig_name'):
            self.lbl_orig_name.configure(text=get_text("msg_waiting_file"))
            
        if hasattr(self, 'lbl_mod_box'): self.lbl_mod_box.configure(text=get_text("lbl_mod_pdf"))
        if hasattr(self, 'btn_select_mod'): self.btn_select_mod.configure(text=get_text("btn_select_file"))
        
        if not self.mod_pdf_path and hasattr(self, 'lbl_mod_name'):
            self.lbl_mod_name.configure(text=get_text("msg_waiting_file"))
            
        if hasattr(self, 'btn_html'): self.btn_html.configure(text=get_text("btn_diff_html"))
        if hasattr(self, 'btn_visual'): self.btn_visual.configure(text=get_text("btn_diff_visual"))
        if hasattr(self, 'btn_pdf'): self.btn_pdf.configure(text=get_text("btn_diff_pdf"))
        
        # Dil değiştiğinde akıllı uyarı kutusunu da anlık olarak yeniden tercüme et
        self.check_page_limits_and_warnings()

    # --- AKILLI SÜRÜKLE BIRAK KARŞILAMA MOTORU ---
    def add_dropped_files(self, files):
        pdf_files = [f for f in files if f.lower().endswith('.pdf')]
        if not pdf_files: return
        
        def process_file(filepath, target):
            doc = fitz.open(filepath)
            password = ""
            if doc.is_encrypted:
                dialog = PasswordDialog(self.winfo_toplevel(), get_text("dialog_warning"), f"'{os.path.basename(filepath)}' şifreli. Şifreyi girin:")
                password = dialog.get_result()
                if not password or not doc.authenticate(password):
                    messagebox.showerror(get_text("dialog_error"), "Yanlış Şifre!")
                    doc.close(); return False
            doc.close()

            if target == "orig":
                self.orig_pdf_path = filepath
                self.orig_password = password
                self.lbl_orig_name.configure(text=os.path.basename(filepath), text_color=("black", "white"))
            else:
                self.mod_pdf_path = filepath
                self.mod_password = password
                self.lbl_mod_name.configure(text=os.path.basename(filepath), text_color=("black", "white"))
            return True

        # Kullanıcı 1 dosya atarsa onu boş olan kutuya veya varsayılan olarak "orig" kutusuna koy
        if len(pdf_files) == 1:
            target = "mod" if self.orig_pdf_path else "orig"
            process_file(pdf_files[0], target)
        # Kullanıcı birden fazla dosya atarsa ilkini "orig" ikincisini "mod" kutusuna koy
        elif len(pdf_files) >= 2:
            process_file(pdf_files[0], "orig")
            process_file(pdf_files[1], "mod")
            
        self.check_page_limits_and_warnings()

    # --- DOSYA SEÇİMİ ---
    def select_pdf(self, target):
        filepath = filedialog.askopenfilename(title=get_text("btn_select_file"), filetypes=[("PDF", "*.pdf")])
        if not filepath: return
        
        doc = fitz.open(filepath)
        password = ""
        if doc.is_encrypted:
            dialog = PasswordDialog(self.winfo_toplevel(), get_text("dialog_warning"), f"'{os.path.basename(filepath)}' şifreli. Şifreyi girin:")
            password = dialog.get_result()
            if not password or not doc.authenticate(password):
                messagebox.showerror(get_text("dialog_error"), "Yanlış Şifre!")
                doc.close()
                return
        doc.close()

        if target == "orig":
            self.orig_pdf_path = filepath
            self.orig_password = password
            self.lbl_orig_name.configure(text=os.path.basename(filepath), text_color=("black", "white"))
        else:
            self.mod_pdf_path = filepath
            self.mod_password = password
            self.lbl_mod_name.configure(text=os.path.basename(filepath), text_color=("black", "white"))
            
        self.check_page_limits_and_warnings()

    # --- METİN ÇIKARMA MOTORU ---
    def extract_text_from_pdf(self, filepath, password):
        doc = fitz.open(filepath)
        if doc.is_encrypted: doc.authenticate(password)
        text = ""
        for page in doc:
            text += page.get_text("text") + "\n"
        doc.close()
        return text.splitlines()

    # ==========================================
    # --- 1. SEÇENEK: MODERN HTML RAPORU ---
    # ==========================================
    def generate_html_diff(self):
        if not self.orig_pdf_path or not self.mod_pdf_path:
            messagebox.showwarning(get_text("dialog_warning"), get_text("msg_select_both"))
            return
            
        self.progress = ProgressWindow(self.winfo_toplevel(), get_text("msg_diff_reading"))
        threading.Thread(target=self._thread_html_diff, daemon=True).start()

    def _thread_html_diff(self):
        try:
            orig_lines = self.extract_text_from_pdf(self.orig_pdf_path, self.orig_password)
            mod_lines = self.extract_text_from_pdf(self.mod_pdf_path, self.mod_password)

            html_differ = difflib.HtmlDiff(wrapcolumn=70)
            html_content = html_differ.make_file(orig_lines, mod_lines, 
                                                 "1. Eski Sürüm (Orijinal)", "2. Yeni Sürüm (Değiştirilmiş)", context=True, numlines=3)
            
            # --- MUTLAK İTAAT CSS ENJEKSİYONU (!important) ---
            modern_css = """
            <style type="text/css">
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8f9fa; color: #212529; margin: 20px; }
                table.diff { width: 100%; border-collapse: collapse; background: #ffffff; box-shadow: 0px 4px 15px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden; font-size: 14px; }
                th.diff_header { background-color: #e9ecef; border-bottom: 2px solid #dee2e6; padding: 12px; text-align: center; color: #495057; font-size: 16px; font-weight: bold;}
                td.diff_header { background-color: #f8f9fa; border-right: 1px solid #dee2e6; text-align: center; width: 40px; color: #6c757d; font-weight: bold; }
                td { padding: 8px 12px; border-bottom: 1px solid #f1f3f5; vertical-align: top; }
                
                /* Buradaki !important etiketleri python'un eski css kodlarını mutlak suretle ezer */
                span.diff_add, td.diff_add { background-color: #d1e7dd !important; color: #0f5132 !important; font-weight: bold !important; padding: 3px 6px; border-radius: 4px; display: inline-block; }
                span.diff_chg, td.diff_chg { background-color: #fff3cd !important; color: #664d03 !important; padding: 3px 6px; border-radius: 4px; display: inline-block; }
                span.diff_sub, td.diff_sub { background-color: #f8d7da !important; color: #842029 !important; text-decoration: line-through !important; font-weight: bold !important; padding: 3px 6px; border-radius: 4px; display: inline-block; }
                .diff_next { background-color: #f8f9fa !important; }
            </style>
            """
            # CSS'i dosyanın en güçlü yerine (head bitimine) yapıştırıyoruz
            html_content = html_content.replace('</head>', modern_css + '\n</head>')
            
            temp_dir = tempfile.gettempdir()
            html_path = os.path.join(temp_dir, f"PDF_Karsilastirma_Modern_{os.urandom(4).hex()}.html")
            
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
                
            webbrowser.open('file://' + os.path.realpath(html_path))
            
            self.after(0, lambda: ActionDialog(self.winfo_toplevel(), get_text("dialog_success"), get_text("msg_diff_html_success")))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror(get_text("dialog_error"), str(e)))
        finally:
            if hasattr(self, 'progress'): self.after(0, self.progress.destroy)

    # ==========================================
    # --- 2. SEÇENEK: DOĞRUDAN PDF ÜZERİNDE İŞARETLEME ---
    # ==========================================
    def generate_visual_diff(self):
        if not self.orig_pdf_path or not self.mod_pdf_path:
            messagebox.showwarning(get_text("dialog_warning"), get_text("msg_select_both"))
            return
            
        # Dosya adı yerine ana dizin seçtiriyoruz
        save_dir = filedialog.askdirectory(title="Karşılaştırma Sonuçlarını Kaydetmek İçin Klasör Seçin")
        if not save_dir: return

        # Zaman damgası ile çakışmayan benzersiz klasör adı türetme
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        final_dir = os.path.join(save_dir, f"Docsas_Karsilastirma_{timestamp}")
        
        try:
            os.makedirs(final_dir, exist_ok=False)
        except Exception as e:
            messagebox.showerror("Hata", f"Klasör oluşturulamadı: {str(e)}")
            return

        self.progress = ProgressWindow(self.winfo_toplevel(), get_text("msg_diff_reading"))
        threading.Thread(target=self._thread_visual_diff, args=(final_dir,), daemon=True).start()

    def _thread_visual_diff(self, base_save_path):
        try:
            doc_orig = fitz.open(self.orig_pdf_path)
            if doc_orig.is_encrypted: doc_orig.authenticate(self.orig_password)
            
            doc_mod = fitz.open(self.mod_pdf_path)
            if doc_mod.is_encrypted: doc_mod.authenticate(self.mod_password)

            orig_lines = self.extract_text_from_pdf(self.orig_pdf_path, self.orig_password)
            mod_lines = self.extract_text_from_pdf(self.mod_pdf_path, self.mod_password)
            
            # KELİME KELİME EN İNCE DETAYINA KADAR KARŞILAŞTIRAN HASSAS MOTOR (ndiff)
            diff = difflib.ndiff(orig_lines, mod_lines)
            
            for line in diff:
                # Simge durumuna küçültme halinde çökmemesi için zırh sarmalı
                try:
                    if hasattr(self, 'progress') and self.progress.winfo_exists() and self.winfo_toplevel().wm_state() != "iconic":
                        self.progress.update_idletasks()
                except: pass

                code = line[:2]
                text = line[2:].strip()
                if not text or len(text) < 3: continue 
                
                if code == '- ': 
                    for page in doc_orig:
                        rects = page.search_for(text)
                        for r in rects:
                            try:
                                annot = page.add_highlight_annot(r)
                                annot.set_colors(stroke=(1, 0, 0)) # Kırmızı
                                try: annot.set_opacity(0.35) 
                                except: pass
                                annot.update()
                            except: pass
                            
                elif code == '+ ': 
                    for page in doc_mod:
                        rects = page.search_for(text)
                        for r in rects:
                            try:
                                annot = page.add_highlight_annot(r)
                                annot.set_colors(stroke=(0, 1, 0)) # Yeşil
                                try: annot.set_opacity(0.35) 
                                except: pass
                                annot.update()
                            except: pass
            
            # Gelen parametre artık doğrudan oluşturduğumuz benzersiz klasör yoludur
            final_dir = base_save_path 
            base_name = "Karsilastirma"
            
            orig_save = os.path.join(final_dir, f"{base_name}_1_Eski_Silinenler.pdf")
            mod_save = os.path.join(final_dir, f"{base_name}_2_Yeni_Eklenenler.pdf")
            
            # --- UYAP UYUMLULUK VE GÜVENLİK ENTEGRASYONU ---
            # 1. Eklenen fosforlu işaretleme katmanlarının imza yapısını bozmaması için düzleştiriyoruz
            try:
                for page in doc_orig: page.flatten_widgets()
                for page in doc_mod: page.flatten_widgets()
            except: pass

            # 2. Yerel dosya yollarını ve bilgisayar adını temizlemek için meta verileri sıfırlıyoruz
            doc_orig.set_metadata({})
            doc_mod.set_metadata({})
            try:
                doc_orig.set_xml_metadata("")
                doc_mod.set_xml_metadata("")
            except: pass
            
            # 3. Çöp nesne temizliği (garbage=4) uygulayarak güvenli şekilde kaydediyoruz
            doc_orig.save(orig_save, deflate=True, garbage=4, clean=True)
            doc_mod.save(mod_save, deflate=True, garbage=4, clean=True)
            
            doc_orig.close()
            doc_mod.close()
            add_history("⚖️", "history_action_generic", ["Görsel Karşılaştırma", os.path.basename(final_dir)], final_dir)
            
            # ActionDialog'a hedef dosya yerine doğrudan final_dir klasör yolunu veriyoruz
            self.after(0, lambda: ActionDialog(self.winfo_toplevel(), get_text("dialog_success"), get_text("msg_diff_visual_success"), final_dir))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror(get_text("dialog_error"), str(e)))
        finally:
            if hasattr(self, 'progress') and self.progress.winfo_exists():
                self.after(0, self.progress.destroy)

    # ==========================================
    # --- 3. SEÇENEK: METİN TABANLI PDF RAPORU ---
    # ==========================================
    def generate_pdf_diff(self):
        if not self.orig_pdf_path or not self.mod_pdf_path:
            messagebox.showwarning(get_text("dialog_warning"), get_text("msg_select_both"))
            return
            
        save_path = filedialog.asksaveasfilename(title="Fark Raporunu Kaydet", defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not save_path: return

        self.progress = ProgressWindow(self.winfo_toplevel(), get_text("msg_diff_reading"))
        threading.Thread(target=self._thread_pdf_diff, args=(save_path,), daemon=True).start()

    def get_turkish_font(self, page):
        if sys.platform == "win32":
            font_file = "C:/Windows/Fonts/arial.ttf"
            if os.path.exists(font_file):
                try: page.insert_font(fontname="tr_arial", fontfile=font_file); return "tr_arial"
                except: pass
        return "helv"

    def _thread_pdf_diff(self, save_path):
        try:
            orig_lines = self.extract_text_from_pdf(self.orig_pdf_path, self.orig_password)
            mod_lines = self.extract_text_from_pdf(self.mod_pdf_path, self.mod_password)

            diff_engine = difflib.ndiff(orig_lines, mod_lines)
            
            doc = fitz.open()
            page = doc.new_page()
            font_key = self.get_turkish_font(page)
            
            y_pos = 50
            x_pos = 40
            line_height = 16
            max_y = 800

            page.insert_text(fitz.Point(x_pos, y_pos), "--- PDF KARŞILAŞTIRMA RAPORU ---", fontname=font_key, fontsize=14, color=(0,0,0))
            y_pos += 25
            
            page.draw_rect(fitz.Rect(x_pos, y_pos-10, x_pos+200, y_pos+5), color=(1,0.8,0.8), fill=(1,0.8,0.8))
            page.insert_text(fitz.Point(x_pos+5, y_pos), "KIRMIZI = Silinen Metinler", fontname=font_key, fontsize=11, color=(0.7,0,0))
            y_pos += 20
            page.draw_rect(fitz.Rect(x_pos, y_pos-10, x_pos+200, y_pos+5), color=(0.8,1,0.8), fill=(0.8,1,0.8))
            page.insert_text(fitz.Point(x_pos+5, y_pos), "YEŞİL = Eklenen Metinler", fontname=font_key, fontsize=11, color=(0,0.5,0))
            y_pos += 35

            for line in diff_engine:
                try:
                    if hasattr(self, 'progress') and self.progress.winfo_exists() and self.winfo_toplevel().wm_state() != "iconic":
                        self.progress.update_idletasks()
                except: pass

                if line.startswith('? '): continue 
                
                clean_line = line[2:].strip()
                if not clean_line: continue
                
                color = (0, 0, 0) 
                bg_color = None
                prefix = ""
                
                if line.startswith('- '): 
                    color = (0.7, 0, 0)
                    bg_color = (1, 0.9, 0.9)
                    prefix = "[-] "
                elif line.startswith('+ '): 
                    color = (0, 0.5, 0) 
                    bg_color = (0.9, 1, 0.9)
                    prefix = "[+] "

                display_text = (prefix + clean_line)[:90] 
                
                if bg_color:
                    tw = fitz.Font("helv").text_length(display_text, fontsize=10)
                    page.draw_rect(fitz.Rect(x_pos-2, y_pos-10, x_pos+tw+5, y_pos+4), color=bg_color, fill=bg_color)
                
                page.insert_text(fitz.Point(x_pos, y_pos), display_text, fontname=font_key, fontsize=10, color=color)
                y_pos += line_height
                
                if y_pos > max_y:
                    page = doc.new_page()
                    font_key = self.get_turkish_font(page)
                    y_pos = 50

            # --- UYAP UYUMLULUK VE GÜVENLİK ENTEGRASYONU ---
            # Üretilen fark raporu PDF'inin meta verilerini sıfırlıyor ve derin nesne temizliği uyguluyoruz
            doc.set_metadata({})
            try: doc.set_xml_metadata("")
            except: pass
            
            doc.save(save_path, deflate=True, garbage=4, clean=True)
            doc.close()
            add_history("⚖️", "history_action_generic", ["Karşılaştırma Raporu", os.path.basename(save_path)], save_path)
            
            self.after(0, lambda: ActionDialog(self.winfo_toplevel(), get_text("dialog_success"), get_text("msg_diff_pdf_success"), save_path))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror(get_text("dialog_error"), str(e)))
        finally:
            if hasattr(self, 'progress') and self.progress.winfo_exists():
                self.after(0, self.progress.destroy)