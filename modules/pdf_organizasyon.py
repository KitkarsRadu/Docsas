import customtkinter as ctk
from tkinter import filedialog, messagebox
import fitz  
import os
import io
import threading
from modules.pdf_araclari import PasswordDialog, ProgressWindow, ActionDialog
from modules.language_manager import get_text

class AkilliOrganizasyonSayfasi(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        
        self.file_list = []
        
        # Sekme isimlerini hafızada tutuyoruz ki diller arası geçişte hata vermesin
        self.tab_split_name = get_text("tab_split_size")
        self.tab_merge_name = get_text("tab_bookmark_merge")
        
        self.setup_ui()
        self.update_language()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=3) 
        self.grid_columnconfigure(1, weight=1, minsize=400) 
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # --- SOL TARAF: DOSYA YÖNETİM ALANI ---
        # ==========================================
        left_frame = ctk.CTkFrame(self, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        top_bar = ctk.CTkFrame(left_frame, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 10))
        
        self.btn_add_file = ctk.CTkButton(top_bar, text=get_text("btn_add_file"), font=ctk.CTkFont(weight="bold"), 
                      fg_color="#1565C0", hover_color="#0D47A1", command=self.add_files)
        self.btn_add_file.pack(side="left", padx=5)
        
        self.btn_clear_files = ctk.CTkButton(top_bar, text=get_text("btn_clear"), width=80, fg_color="transparent", 
                      border_width=1, border_color=("gray60", "gray40"), text_color=("black", "white"), 
                      hover_color=("gray85", "gray25"), command=self.clear_files)
        self.btn_clear_files.pack(side="left", padx=5)

        self.lbl_files_to_process = ctk.CTkLabel(left_frame, text=get_text("lbl_files_to_process"), font=ctk.CTkFont(size=14, weight="bold"))
        self.lbl_files_to_process.pack(anchor="w", padx=5, pady=5)
        
        self.listbox_frame = ctk.CTkScrollableFrame(left_frame, fg_color=("gray90", "gray15"), corner_radius=10)
        self.listbox_frame.pack(fill="both", expand=True)

        # ==========================================
        # --- SAĞ TARAF: ARAÇ SEKMELERİ ---
        # ==========================================
        right_frame = ctk.CTkFrame(self, width=400)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.tabview = ctk.CTkTabview(right_frame)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=(10, 5))

        self.tab_split = self.tabview.add(self.tab_split_name)
        self.tab_merge = self.tabview.add(self.tab_merge_name)

        # --- 1. BOYUTA GÖRE BÖL (UYAP) SEKMESİ ---
        info_box1 = ctk.CTkFrame(self.tab_split, fg_color=("#E8F5E9", "#1B5E20"), corner_radius=8)
        info_box1.pack(fill="x", padx=10, pady=15)
        
        self.lbl_split_info = ctk.CTkLabel(info_box1, text="ℹ️ " + get_text("msg_split_info"), text_color=("#2E7D32", "#A5D6A7"), font=ctk.CTkFont(size=11), justify="left", wraplength=320)
        self.lbl_split_info.pack(padx=10, pady=10)

        self.lbl_max_mb = ctk.CTkLabel(self.tab_split, text=get_text("lbl_max_mb"), font=ctk.CTkFont(weight="bold"))
        self.lbl_max_mb.pack(anchor="w", padx=15, pady=(10, 5))
        self.var_mb_limit = ctk.DoubleVar(value=9.5)
        
        mb_frame = ctk.CTkFrame(self.tab_split, fg_color="transparent")
        mb_frame.pack(fill="x", padx=15, pady=5)
        self.slider_mb = ctk.CTkSlider(mb_frame, from_=1.0, to=50.0, number_of_steps=490, variable=self.var_mb_limit, command=self._sync_mb_slider)
        self.slider_mb.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.ent_mb = ctk.CTkEntry(mb_frame, width=60, height=25)
        self.ent_mb.pack(side="right")
        self.ent_mb.insert(0, "9.5")
        self.ent_mb.bind("<KeyRelease>", self._sync_mb_entry)

        self.btn_start_split = ctk.CTkButton(self.tab_split, text=get_text("tab_split_size"), font=ctk.CTkFont(size=16, weight="bold"), height=55, fg_color="#F57C00", hover_color="#E65100", command=self.start_split_process)
        self.btn_start_split.pack(side="bottom", fill="x", padx=15, pady=20)


        # --- 2. İÇİNDEKİLERLİ BİRLEŞTİR VE SIKIŞTIR SEKMESİ ---
        info_box2 = ctk.CTkFrame(self.tab_merge, fg_color=("#FFF3E0", "#E65100"), corner_radius=8)
        info_box2.pack(fill="x", padx=10, pady=15)
        
        self.lbl_merge_info = ctk.CTkLabel(info_box2, text="ℹ️ " + get_text("msg_bookmark_info"), text_color=("#E65100", "#FFCC80"), font=ctk.CTkFont(size=11), justify="left", wraplength=320)
        self.lbl_merge_info.pack(padx=10, pady=10)

        self.lbl_merge_comp = ctk.CTkLabel(self.tab_merge, text=get_text("lbl_merge_comp"), font=ctk.CTkFont(weight="bold"))
        self.lbl_merge_comp.pack(anchor="w", padx=15, pady=(10, 5))
        self.var_merge_comp = ctk.StringVar(value=get_text("opt_comp_2"))
        opts_comp = [get_text("opt_comp_1"), get_text("opt_comp_2"), get_text("opt_comp_3")]
        
        self.opt_merge_comp = ctk.CTkOptionMenu(self.tab_merge, values=opts_comp, variable=self.var_merge_comp)
        self.opt_merge_comp.pack(fill="x", padx=15, pady=5)

        self.btn_start_merge = ctk.CTkButton(self.tab_merge, text=get_text("tab_bookmark_merge"), font=ctk.CTkFont(size=16, weight="bold"), height=55, fg_color="#2E7D32", hover_color="#1B5E20", command=self.start_merge_process)
        self.btn_start_merge.pack(side="bottom", fill="x", padx=15, pady=20)


    # ==========================================
    # --- ANLIK ÇEVİRİ MOTORU (SIFIR KASMA) ---
    # ==========================================
    def update_language(self):
        # 1. Sekme İsimlerini Güncelle (Hata yakalama ile korunmuştur)
        try:
            self.tabview._segmented_button._buttons_dict[self.tab_split_name].configure(text=get_text("tab_split_size"))
            self.tabview._segmented_button._buttons_dict[self.tab_merge_name].configure(text=get_text("tab_bookmark_merge"))
        except: pass

        # 2. Sol Menü Buton ve Başlıkları
        if hasattr(self, 'btn_add_file'): self.btn_add_file.configure(text=get_text("btn_add_file"))
        if hasattr(self, 'btn_clear_files'): self.btn_clear_files.configure(text=get_text("btn_clear"))
        if hasattr(self, 'lbl_files_to_process'): self.lbl_files_to_process.configure(text=get_text("lbl_files_to_process"))

        # 3. Bölme Sekmesi Bilgileri
        if hasattr(self, 'lbl_split_info'): self.lbl_split_info.configure(text="ℹ️ " + get_text("msg_split_info"))
        if hasattr(self, 'lbl_max_mb'): self.lbl_max_mb.configure(text=get_text("lbl_max_mb"))
        if hasattr(self, 'btn_start_split'): self.btn_start_split.configure(text=get_text("tab_split_size"))

        # 4. Birleştirme Sekmesi Bilgileri
        if hasattr(self, 'lbl_merge_info'): self.lbl_merge_info.configure(text="ℹ️ " + get_text("msg_bookmark_info"))
        if hasattr(self, 'lbl_merge_comp'): self.lbl_merge_comp.configure(text=get_text("lbl_merge_comp"))
        if hasattr(self, 'btn_start_merge'): self.btn_start_merge.configure(text=get_text("tab_bookmark_merge"))

        # 5. Sıkıştırma Seviyesi Eşleştiricisi (Diller arası geçişte ayarı sıfırlamaz)
        if hasattr(self, 'opt_merge_comp'):
            old_vals_tr = ["Hafif", "Standart", "Maksimum"]
            old_vals_en = ["Light", "Standard", "Maximum"]
            curr = self.var_merge_comp.get()
            idx = 1 # Varsayılan: Standart
            if curr in old_vals_tr: idx = old_vals_tr.index(curr)
            elif curr in old_vals_en: idx = old_vals_en.index(curr)
            
            opts_comp = [get_text("opt_comp_1"), get_text("opt_comp_2"), get_text("opt_comp_3")]
            self.opt_merge_comp.configure(values=opts_comp)
            self.var_merge_comp.set(opts_comp[idx])

        # 6. Listelenen dosyaların "Sayfa" ve "Sil" yazılarını güncellemek için listeyi baştan çiz
        self.update_listbox()


    # ==========================================
    # --- UI SENKRONİZASYON VE LİSTE İŞLEMLERİ ---
    # ==========================================
    def _sync_mb_slider(self, val):
        self.ent_mb.delete(0, "end")
        self.ent_mb.insert(0, f"{float(val):.1f}")

    def _sync_mb_entry(self, event):
        try:
            val = float(self.ent_mb.get())
            if 1.0 <= val <= 500.0: self.var_mb_limit.set(val)
        except ValueError: pass
    
    # --- SÜRÜKLE BIRAK KARŞILAMA MOTORU ---
    def add_dropped_files(self, files):
        pdf_files = [f for f in files if f.lower().endswith('.pdf')]
        if pdf_files:
            self.progress = ProgressWindow(self.winfo_toplevel(), get_text("msg_analyzing"))
            # Animasyonun donmaması için 200ms gecikmeli thread başlatıyoruz
            self.after(200, lambda: threading.Thread(target=self._thread_add_files, args=(pdf_files,), daemon=True).start())

    def add_files(self):
        files = filedialog.askopenfilenames(filetypes=[("PDF", "*.pdf")])
        if not files: return
        
        self.progress = ProgressWindow(self.winfo_toplevel(), get_text("msg_analyzing"))
        self.after(200, lambda: threading.Thread(target=self._thread_add_files, args=(files,), daemon=True).start())

    def _thread_add_files(self, files):
        try:
            for f in files:
                doc = fitz.open(f)
                pwd = ""
                if doc.is_encrypted:
                    self.after(0, lambda: self.progress.withdraw())
                    dialog = PasswordDialog(self.winfo_toplevel(), get_text("dialog_warning"), f"'{os.path.basename(f)}' şifreli. Şifreyi girin:")
                    user_pass = dialog.get_result()
                    self.after(0, lambda: self.progress.deiconify())
                    
                    if user_pass and doc.authenticate(user_pass): pwd = user_pass
                    else: doc.close(); continue
                
                size_mb = os.path.getsize(f) / (1024 * 1024)
                pages = len(doc)
                doc.close()
                
                self.file_list.append({'path': f, 'name': os.path.basename(f), 'size': size_mb, 'pages': pages, 'pwd': pwd})
            
            self.after(0, self.update_listbox)
        except Exception as e: self.after(0, lambda: messagebox.showerror(get_text("dialog_error"), str(e)))
        finally:
            if hasattr(self, 'progress') and self.progress.winfo_exists(): self.after(0, self.progress.destroy)

    def update_listbox(self):
        for w in self.listbox_frame.winfo_children(): w.destroy()
        
        for idx, f_data in enumerate(self.file_list):
            row = ctk.CTkFrame(self.listbox_frame, fg_color=("white", "gray20"), corner_radius=5)
            row.pack(fill="x", padx=5, pady=2)
            
            # "Sayfa" kelimesi dile göre dinamik hale getirildi
            page_txt = get_text("lbl_page_short")
            lbl_name = ctk.CTkLabel(row, text=f"{idx+1}. {f_data['name']} ({f_data['pages']} {page_txt} - {f_data['size']:.1f} MB)", font=ctk.CTkFont(weight="bold", size=12))
            lbl_name.pack(side="left", padx=10, pady=10)
            
            # "Sil" butonu dile göre dinamik hale getirildi
            btn_del = ctk.CTkButton(row, text=get_text("btn_delete_item"), width=50, fg_color="#E53935", hover_color="#B71C1C", command=lambda i=idx: self.remove_item(i))
            btn_del.pack(side="right", padx=10)

    def remove_item(self, index):
        self.file_list.pop(index)
        self.update_listbox()

    def clear_files(self):
        self.file_list.clear()
        self.update_listbox()


    # ==========================================
    # --- MOTOR 1: İÇİNDEKİLERLİ VE SIKIŞTIRMALI BİRLEŞTİRME ---
    # ==========================================
    def start_merge_process(self):
        if len(self.file_list) < 2:
            messagebox.showwarning(get_text("dialog_warning"), "Birleştirme için en az 2 dosya seçmelisiniz!")
            return
            
        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], initialfile="Birlesik_Icindekilerli_Belge.pdf")
        if not save_path: return
        
        comp_level = self.var_merge_comp.get()
        self.progress = ProgressWindow(self.winfo_toplevel(), "İçindekiler Oluşturulup Birleştiriliyor...")
        self.after(200, lambda: threading.Thread(target=self._thread_merge_files, args=(save_path, comp_level), daemon=True).start())

    def _thread_merge_files(self, save_path, comp_level):
        try:
            final_doc = fitz.open()
            toc = [] 
            current_page = 1
            
            for f_data in self.file_list:
                # Çoklu dosya birleştirilirken yüklenme kutusunun donmasını engelle
                if hasattr(self, 'progress') and self.progress.winfo_exists():
                    self.progress.update()

                doc = fitz.open(f_data['path'])
                if doc.is_encrypted: doc.authenticate(f_data['pwd'])
                
                final_doc.insert_pdf(doc)
                
                clean_title = f_data['name'].replace(".pdf", "")
                toc.append([1, clean_title, current_page])
                
                current_page += len(doc)
                doc.close()
            
            final_doc.set_toc(toc)
            
            # --- UYAP UYUMLULUK VE GÜVENLİK ENTEGRASYONU ---
            # 1. Birleştirilen dökümanların içindeki eski form etkileşimlerini metne düzleştiriyoruz
            try:
                for page in final_doc:
                    page.flatten_widgets()
            except: pass

            # 2. Yerel bilgisayar adını ve dosya yollarını temizlemek için meta verileri sıfırlıyoruz
            final_doc.set_metadata({})
            try: final_doc.set_xml_metadata("")
            except: pass

            # SIKIŞTIRMA SEVİYESİNE GÖRE KAYIT AYARLARI
            save_args = {"deflate": True}
            if comp_level == get_text("opt_comp_3"): # Maksimum
                save_args["garbage"] = 4
                save_args["clean"] = True
            elif comp_level == get_text("opt_comp_2"): # Standart
                save_args["garbage"] = 4  # UYAP XREF yapısı için temizlik seviyesi 4'e yükseltildi
                save_args["clean"] = True
            else: # Hafif
                save_args["garbage"] = 4  # Boyut kaygısı olmasa da yapısal temizlik için 4 yapıldı
                save_args["clean"] = True
                
            final_doc.save(save_path, **save_args)
            final_doc.close()

            from modules.history_manager import add_history
            add_history("🗂️", "history_action_merge", [len(self.file_list), os.path.basename(save_path)], save_path)
            
            self.after(0, lambda: ActionDialog(self.winfo_toplevel(), get_text("dialog_success"), get_text("msg_process_success"), save_path))
        except Exception as e: self.after(0, lambda: messagebox.showerror(get_text("dialog_error"), str(e)))
        finally:
            if hasattr(self, 'progress') and self.progress.winfo_exists(): self.after(0, self.progress.destroy)


    # ==========================================
    # --- MOTOR 2: BOYUTA GÖRE AKILLI BÖLME ---
    # ==========================================
    def start_split_process(self):
        if not self.file_list:
            messagebox.showwarning(get_text("dialog_warning"), get_text("msg_warn_no_file"))
            return
            
        target_file = self.file_list[0]
        max_mb = float(self.ent_mb.get())
        
        if target_file['size'] <= max_mb:
            messagebox.showinfo("Bilgi", "Seçilen dosya zaten belirlediğiniz MB sınırından küçük. Bölmeye gerek yok.")
            return
            
        save_dir = filedialog.askdirectory(title="Bölünen Parçaların Kaydedileceği Klasörü Seçin")
        if not save_dir: return
        
        base_name = target_file['name'].replace('.pdf', '')
        
        self.progress = ProgressWindow(self.winfo_toplevel(), f"{target_file['name']} Tartılarak Bölünüyor...")
        self.after(200, lambda: threading.Thread(target=self._thread_split_file, args=(target_file, max_mb, save_dir, base_name), daemon=True).start())

    def _thread_split_file(self, target_file, max_mb, save_dir, base_name):
        try:
            max_bytes = max_mb * 1024 * 1024
            src_doc = fitz.open(target_file['path'])
            if src_doc.is_encrypted: src_doc.authenticate(target_file['pwd'])
            
            out_doc = fitz.open()
            part_num = 1
            
            for i in range(len(src_doc)):
                # Her sayfa analiz edilip bölünürken arayüzü zorla tazeleyerek donmayı kırın
                if hasattr(self, 'progress') and self.progress.winfo_exists():
                    self.progress.update()

                out_doc.insert_pdf(src_doc, from_page=i, to_page=i)
                
                buf = io.BytesIO()
                out_doc.save(buf, garbage=3, deflate=True)
                current_size = buf.getbuffer().nbytes
                buf.close()
                
                if current_size > max_bytes and len(out_doc) > 1:
                    out_doc.delete_page(-1)
                    
                    part_path = os.path.join(save_dir, f"{base_name}_Part_{part_num}.pdf")
                    
                    # --- UYAP UYUMLULUK ENTEGRASYONU ---
                    try:
                        for page in out_doc: page.flatten_widgets()
                    except: pass
                    out_doc.set_metadata({})
                    try: out_doc.set_xml_metadata("")
                    except: pass

                    out_doc.save(part_path, garbage=4, clean=True, deflate=True)
                    out_doc.close()
                    
                    part_num += 1
                    
                    out_doc = fitz.open()
                    out_doc.insert_pdf(src_doc, from_page=i, to_page=i)
            
            if len(out_doc) > 0:
                part_path = os.path.join(save_dir, f"{base_name}_Part_{part_num}.pdf")
                
                # --- UYAP UYUMLULUK ENTEGRASYONU ---
                try:
                    for page in out_doc: page.flatten_widgets()
                except: pass
                out_doc.set_metadata({})
                try: out_doc.set_xml_metadata("")
                except: pass

                out_doc.save(part_path, garbage=4, clean=True, deflate=True)
            
            out_doc.close()
            src_doc.close()
            
            self.after(0, lambda: ActionDialog(self.winfo_toplevel(), get_text("dialog_success"), get_text("msg_split_success"), save_dir))
        except Exception as e: self.after(0, lambda: messagebox.showerror(get_text("dialog_error"), str(e)))
        finally:
            if hasattr(self, 'progress') and self.progress.winfo_exists(): self.after(0, self.progress.destroy)