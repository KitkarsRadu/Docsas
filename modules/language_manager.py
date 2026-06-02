class LanguageManager:
    def __init__(self):
        self.current_lang = "TR"  # Varsayılan dil
        
        # --- TÜM UYGULAMANIN DİL SÖZLÜĞÜ ---
        self.texts = {
            # --- ANA EKRAN (main.py) ---
            "menu_title": {"TR": "İşlem Menüsü", "EN": "Action Menu"},
            "btn_pdf": {"TR": "PDF İşlemleri", "EN": "PDF Operations"},
            "btn_word": {"TR": "Word / Excel / PPT", "EN": "Word / Excel / PPT"},
            "btn_img": {"TR": "Resim İşlemleri", "EN": "Image Operations"},
            "btn_pdf_tools": {"TR": "PDF Araçları", "EN": "PDF Tools"},
            "btn_about": {"TR": "Hakkımızda", "EN": "About"},
            "welcome": {"TR": "Lütfen soldaki menüden yapmak istediğiniz işlemi seçin.", "EN": "Please select an operation from the left menu."},
            "about_title": {"TR": "Hakkında", "EN": "About"},

            # --- ORTAK DİYALOGLAR VE MESAJ KUTULARI ---
            "dialog_ok": {"TR": "Tamam", "EN": "OK"},
            "dialog_open": {"TR": "Aç", "EN": "Open"},
            "dialog_success": {"TR": "Başarılı", "EN": "Success"},
            "dialog_error": {"TR": "Hata", "EN": "Error"},
            "dialog_warning": {"TR": "Uyarı", "EN": "Warning"},
            "dialog_info": {"TR": "Bilgi", "EN": "Info"},
            "progress_wait": {"TR": "Lütfen Bekleyin", "EN": "Please Wait"},
            "progress_processing": {"TR": "İşlem yapılıyor, lütfen bekleyin...", "EN": "Processing, please wait..."},

            # --- PDF İŞLEMLERİ SAYFASI ---
            "tab_merge": {"TR": "PDF Birleştir / Düzenle", "EN": "Merge / Edit PDF"},
            "tab_split": {"TR": "PDF Ayır / Sayfa Çıkart", "EN": "Split PDF / Extract Pages"},
            "btn_add": {"TR": "+ Ekle", "EN": "+ Add"},
            "btn_add_blank": {"TR": "+ Boş Sayfa", "EN": "+ Blank Page"},
            "btn_del_selected": {"TR": "🗑 Seçili Sil", "EN": "🗑 Delete Selected"},
            "btn_rot_selected": {"TR": "⟳ Seçili Döndür", "EN": "⟳ Rotate Selected"},
            "btn_clear": {"TR": "Temizle", "EN": "Clear"},
            "btn_select": {"TR": "+ Seç", "EN": "+ Select"},
            "btn_merge_save": {"TR": "Birleştir ve Kaydet", "EN": "Merge and Save"},
            "btn_extract_pages": {"TR": "Sayfaları Çıkart", "EN": "Extract Pages"},
            "lbl_page_settings": {"TR": "Sayfa Ayarları", "EN": "Page Settings"},
            "lbl_merge_info": {"TR": "Ekrandaki sıralama baz alınarak\nTEK BİR PDF oluşturulur.", "EN": "A SINGLE PDF will be created\nbased on the screen order."},
            "lbl_scaling": {"TR": "Sayfa Ölçekleme", "EN": "Page Scaling"},
            "lbl_crop": {"TR": "Canlı Kenar Kırpma", "EN": "Live Edge Cropping"},
            "lbl_export": {"TR": "Dışa Aktar", "EN": "Export"},
            "lbl_split_info": {"TR": "ÖNEMLİ BİLGİ:\nEkranda önizlemesi gözüken\nsayfaların HER BİRİ, seçilen\nklasöre AYRI AYRI birer PDF\ndosyası olarak kaydedilecektir.", "EN": "IMPORTANT:\nEACH page previewed on the\nscreen will be saved as a\nSEPARATE PDF file in the\nselected folder."},
            "opt_original": {"TR": "Orijinal Boyut", "EN": "Original Size"},
            "opt_fit_v": {"TR": "A4 Dikey Sığdır", "EN": "Fit A4 Portrait"},
            "opt_fit_h": {"TR": "A4 Yatay Sığdır", "EN": "Fit A4 Landscape"},
            "opt_none": {"TR": "Yok", "EN": "None"},
            "lbl_blank_page": {"TR": "BOŞ SAYFA", "EN": "BLANK PAGE"},
            "lbl_pwd_solved": {"TR": "🔓 Şifre Çözüldü", "EN": "🔓 Password Solved"},
            "chk_select": {"TR": "Seç", "EN": "Select"},
            "msg_add_pdfs": {"TR": "Lütfen birleştirilecek PDF'leri ekleyin!", "EN": "Please add PDFs to merge!"},
            "msg_select_pdf": {"TR": "Lütfen önce PDF seçin!", "EN": "Please select a PDF first!"},
            "msg_saving_pdf": {"TR": "PDF Kaydediliyor...", "EN": "Saving PDF..."},
            "msg_merged_success": {"TR": "PDF'ler seçtiğiniz ayarlarla TEK BİR DOSYA olarak birleştirildi!", "EN": "PDFs successfully merged into a SINGLE FILE!"},
            "msg_extracting": {"TR": "Sayfalar Çıkartılıyor...", "EN": "Extracting Pages..."},
            "msg_extracted_success": {"TR": "Ekranda gördüğünüz tüm sayfalar klasöre AYRI AYRI çıkartıldı!", "EN": "All previewed pages extracted SEPARATELY to the folder!"},
            "msg_select_to_delete": {"TR": "Lütfen silmek için önce sayfaları tikleyerek seçin.", "EN": "Please tick pages to delete first."},
            "msg_select_to_rotate": {"TR": "Lütfen döndürmek için önce sayfaları tikleyerek seçin.", "EN": "Please tick pages to rotate first."},
            "msg_rotating": {"TR": "Seçili sayfalar döndürülüyor...", "EN": "Rotating selected pages..."},
            "msg_reading_pdfs": {"TR": "PDF'ler Okunuyor...", "EN": "Reading PDFs..."},
            "msg_pwd_file": {"TR": "Şifreli Dosya", "EN": "Encrypted File"},
            "msg_pwd_prompt": {"TR": "'{}' şifreli. Lütfen şifreyi girin:", "EN": "'{}' is encrypted. Enter password:"},
            "msg_pwd_wrong": {"TR": "'{}' için yanlış şifre girildi!", "EN": "Wrong password entered for '{}'!"},
            "msg_load_err": {"TR": "Dosya yüklenemedi:\n{}", "EN": "Failed to load file:\n{}"},
            "msg_updating_previews": {"TR": "Önizlemeler Güncelleniyor...", "EN": "Updating Previews..."},
            "msg_process_err": {"TR": "İşlem sırasında hata oluştu:\n{}", "EN": "An error occurred during process:\n{}"},
            "fd_select_pdf": {"TR": "PDF Seçin", "EN": "Select PDF"},
            "fd_save_merged": {"TR": "Birleştirilmiş PDF Adını Seçin", "EN": "Choose Merged PDF Name"},
            "fd_save_folder": {"TR": "Sayfaların Kaydedileceği Klasörü Seçin", "EN": "Select Target Folder"},

            # --- OFİS İŞLEMLERİ SAYFASI ---
            "tab_to_pdf": {"TR": "Diğer Formatları PDF'ye Çevir", "EN": "Other Formats to PDF"},
            "tab_from_pdf": {"TR": "PDF'yi Diğer Formatlara Çevir", "EN": "PDF to Other Formats"},
            "btn_add_file": {"TR": "+ Dosya Ekle", "EN": "+ Add File"},
            "btn_select_pdf": {"TR": "+ PDF Seç", "EN": "+ Select PDF"},
            "lbl_save_settings": {"TR": "Kaydetme Ayarları", "EN": "Save Settings"},
            "btn_save_as_pdf": {"TR": "PDF Olarak Kaydet", "EN": "Save as PDF"},
            "lbl_target_format": {"TR": "Hedef Format", "EN": "Target Format"},
            "btn_convert_selected": {"TR": "Seçilenleri Dönüştür", "EN": "Convert Selected"},
            "lbl_hybrid_tech": {
                "TR": "        HİBRİT DÖNÜŞTÜRME TEKNOLOJİSİ        \nSisteminizde Microsoft Office yüklü ise en yüksek\nhassasiyet için orijinal Office motoru kullanılır.\nEğer Office yüklü değilse, dönüştürme işlemleri\nyerleşik yedek motorumuzla kesintisiz sürdürülür.\nBu akıllı sistem her koşulda çalışmanızı sağlar.",
                "EN": "        HYBRID CONVERSION TECHNOLOGY        \nIf Microsoft Office is installed, the original\nOffice engine is used for highest precision.\nIf not installed, conversion continues seamlessly\nwith our built-in fallback engine.\nThis smart system works under all conditions."
            },
            "fmt_word": {"TR": "Word (.docx)", "EN": "Word (.docx)"},
            "fmt_excel": {"TR": "Excel (.xlsx)", "EN": "Excel (.xlsx)"},
            "fmt_html": {"TR": "HTML (.html)", "EN": "HTML (.html)"},
            "fmt_txt": {"TR": "Metin (.txt)", "EN": "Text (.txt)"},
            "fmt_json": {"TR": "JSON (.json)", "EN": "JSON (.json)"},
            "fmt_pdfa": {"TR": "PDF/A Uyumu", "EN": "PDF/A Compliance"},
            "msg_read_text_err": {"TR": "Metin okunamadı.", "EN": "Text could not be read."},
            "msg_word_not_found": {"TR": "Microsoft Word bulunamadı. Lütfen Word yükleyin veya PDF formatını kullanın.", "EN": "Microsoft Word not found. Please install Word or use PDF format."},
            "fd_select_office": {"TR": "Dosya Seç", "EN": "Select File"},
            "fd_office_files": {"TR": "Ofis Dosyaları", "EN": "Office Files"},
            "msg_reading_files": {"TR": "Dosyalar Okunuyor...", "EN": "Reading Files..."},
            "msg_file_read_err": {"TR": "Dosya okuma hatası:\n{}", "EN": "File read error:\n{}"},
            "msg_add_files_to_convert": {"TR": "Lütfen dönüştürülecek dosyaları ekleyin!", "EN": "Please add files to convert!"},
            "fd_save_pdf_name": {"TR": "Kaydedilecek PDF Adını Seçin", "EN": "Select PDF Name to Save"},
            "msg_converting_to_pdf": {"TR": "Dosyalar PDF'ye çevriliyor...", "EN": "Converting files to PDF..."},
            "msg_pdf_saved_success": {"TR": "Tüm sayfalar ayarlara uygun şekilde PDF belgesi olarak kaydedildi!", "EN": "All pages saved as a PDF document according to settings!"},
            "msg_add_pdfs_to_convert": {"TR": "Lütfen dönüştürülecek PDF'leri ekleyin!", "EN": "Please add PDFs to convert!"},
            "fd_save_file_name": {"TR": "Dosya Adını Seçin", "EN": "Select File Name"},
            "msg_converting_to_fmt": {"TR": "{} formatına çevriliyor...", "EN": "Converting to {} format..."},
            "msg_files_converted_success": {"TR": "Dosyalar başarıyla {} formatına çevrildi!", "EN": "Files successfully converted to {} format!"},
            "msg_table_page": {"TR": "--- Sayfa {} Tablosu ---", "EN": "--- Page {} Table ---"},
            "msg_text_page": {"TR": "--- Sayfa {} Düz Metin ---", "EN": "--- Page {} Plain Text ---"},
            "msg_conversion_err": {"TR": "Dönüşüm hatası:\n{}", "EN": "Conversion error:\n{}"},

            # --- RESİM İŞLEMLERİ SAYFASI ---
            "tab_img_to_pdf": {"TR": "Resimleri PDF'ye Çevir", "EN": "Images to PDF"},
            "tab_pdf_to_img": {"TR": "PDF'yi Resimlere Çevir", "EN": "PDF to Images"},
            "btn_add_img": {"TR": "+ Resim Ekle", "EN": "+ Add Image"},
            "lbl_pdf_settings": {"TR": "PDF Ayarları", "EN": "PDF Settings"},
            "lbl_page_orientation": {"TR": "Sayfa Yönü", "EN": "Page Orientation"},
            "opt_portrait": {"TR": "Dikey", "EN": "Portrait"},
            "opt_landscape": {"TR": "Yatay", "EN": "Landscape"},
            "lbl_page_size": {"TR": "Sayfa Boyutu", "EN": "Page Size"},
            "opt_a4": {"TR": "A4 (297x210 mm)", "EN": "A4 (297x210 mm)"},
            "lbl_margin": {"TR": "Kenar Boşluğu", "EN": "Margin"},
            "opt_small": {"TR": "Küçük", "EN": "Small"},
            "opt_large": {"TR": "Büyük", "EN": "Large"},
            "btn_convert_to_pdf": {"TR": "PDF'ye Çevir", "EN": "Convert to PDF"},
            "lbl_export_info": {"TR": "Ekrandaki sayfaları klasöre\nPNG olarak kaydeder.", "EN": "Saves previewed pages to\nfolder as PNG files."},
            "btn_extract_images": {"TR": "Resimleri Çıkart", "EN": "Extract Images"},
            
            "fd_select_images": {"TR": "Resimleri Seçin", "EN": "Select Images"},
            "msg_add_images_to_convert": {"TR": "Lütfen dönüştürülecek resimleri ekleyin!", "EN": "Please add images to convert!"},
            "msg_converting_img_to_pdf": {"TR": "Resimler PDF'ye çevriliyor...", "EN": "Converting images to PDF..."},
            "msg_pdf_created_success": {"TR": "PDF tüm ayarlara uygun olarak oluşturuldu!", "EN": "PDF created successfully with all settings!"},
            "fd_save_img_folder": {"TR": "Resimlerin Kaydedileceği Klasörü Seçin", "EN": "Select Folder to Save Images"},
            "msg_extracting_pdf_to_img": {"TR": "PDF sayfaları resimlere çıkartılıyor...", "EN": "Extracting PDF pages to images..."},
            "msg_extracted_img_success": {"TR": "Seçili sayfalar klasöre resim olarak çıkartıldı!", "EN": "Selected pages extracted to folder as images!"},
            "msg_select_img_to_delete": {"TR": "Lütfen silmek için önce resimleri/sayfaları tikleyerek seçin.", "EN": "Please tick images/pages to delete first."},
            "msg_select_img_to_rotate": {"TR": "Lütfen döndürmek için önce resimleri/sayfaları tikleyerek seçin.", "EN": "Please tick images/pages to rotate first."},


            # --- PDF ARAÇLARI SAYFASI ---
            "tab_pdf_tools_main": {"TR": "PDF Sıkıştır / Şifrele / Çöz", "EN": "Compress / Encrypt / Unlock PDF"},
            "btn_cancel": {"TR": "İptal", "EN": "Cancel"},
            "btn_confirm": {"TR": "Onayla", "EN": "Confirm"},
            "lbl_action_select": {"TR": "İşlem Seçimi", "EN": "Select Action"},
            "opt_compress": {"TR": "Sıkıştır", "EN": "Compress"},
            "opt_encrypt": {"TR": "Şifrele", "EN": "Encrypt"},
            "opt_compress_encrypt": {"TR": "Hem Sıkıştır Hem Şifrele", "EN": "Compress & Encrypt"},
            "opt_unlock": {"TR": "Şifre Kaldır (Unlock)", "EN": "Unlock Password"},
            "lbl_compress_power": {"TR": "Sıkıştırma Gücü", "EN": "Compression Level"},
            "opt_light": {"TR": "Hafif", "EN": "Light"},
            "opt_standard": {"TR": "Standart", "EN": "Standard"},
            "opt_maximum": {"TR": "Maksimum", "EN": "Maximum"},
            "lbl_pwd_ops": {"TR": "Şifre İşlemleri", "EN": "Password Operations"},
            "ph_password": {"TR": "Şifre...", "EN": "Password..."},
            "lbl_pwd_again": {"TR": "Şifreyi Tekrar Girin", "EN": "Enter Password Again"},
            "ph_pwd_again": {"TR": "Tekrar...", "EN": "Again..."},
            "ph_pwd_current": {"TR": "Mevcut Şifreyi Girin...", "EN": "Enter Current Password..."},
            "btn_start_process": {"TR": "İşlemi Başlat", "EN": "Start Process"},
            
            "warn_compress": {
                "TR": "⚠️ SIKIŞTIRMA:\nGereksiz veriler temizlenir.\nDosya kalitesi korunur ancak\nboyut önemli ölçüde düşer.", 
                "EN": "⚠️ COMPRESSION:\nUnnecessary data is cleared.\nFile quality is preserved but\nsize is significantly reduced."
            },
            "warn_encrypt": {
                "TR": "⚠️ ŞİFRELEME:\nAES-256 standardı kullanılır.\nŞifre unutulursa belge\nbir daha asla açılamaz!", 
                "EN": "⚠️ ENCRYPTION:\nAES-256 standard is used.\nIf password is lost, document\ncan never be opened again!"
            },
            "warn_unlock": {
                "TR": "⚠️ ŞİFRE KALDIRMA:\nŞifreli bir dosyanın şifresini\nbiliyorsanız, buraya girerek\nşifresiz halini kaydedebilirsiniz.", 
                "EN": "⚠️ UNLOCK PASSWORD:\nIf you know the password of an\nencrypted file, enter it here to\nsave an unencrypted version."
            },
            
            "msg_analyzing": {"TR": "Dosyalar Analiz Ediliyor...", "EN": "Analyzing Files..."},
            "msg_pwd_prompt_2": {"TR": "'{}' şifreli bir dosyadır.\nLütfen erişim şifresini girin:", "EN": "'{}' is an encrypted file.\nPlease enter the access password:"},
            "msg_err_no_pwd": {"TR": "Lütfen bir şifre girin!", "EN": "Please enter a password!"},
            "msg_err_pwd_mismatch": {"TR": "Şifreler uyuşmuyor!", "EN": "Passwords do not match!"},
            "msg_warn_no_file": {"TR": "Dosya ekleyin!", "EN": "Please add a file!"},
            "fd_save_new_pdf": {"TR": "Yeni PDF İsmini Belirleyin", "EN": "Set New PDF Name"},
            "msg_process_success": {"TR": "İşlem başarıyla tamamlandı!", "EN": "Process completed successfully!"},

            # --- GELİŞMİŞ DÜZENLEME SAYFASI ---
            "btn_advanced": {"TR": "Gelişmiş Düzenleme", "EN": "Advanced Editing"},
            "tab_watermark": {"TR": "Filigran", "EN": "Watermark"},
            "tab_signature": {"TR": "İmza / Kaşe", "EN": "Signature / Stamp"},
            "tab_page_num": {"TR": "Sayfa Numarası", "EN": "Page Number"},
            "tab_metadata": {"TR": "Künye Temizle", "EN": "Metadata Cleaner"},
            "lbl_select_pdf_adv": {"TR": "+ Düzenlenecek PDF'i Seç", "EN": "+ Select PDF to Edit"},
            "msg_adv_info": {"TR": "        Düzenleme yapmak için sol üstten bir PDF seçin.", "EN": "Select a PDF from top-left to start editing."},
            "lbl_metadata_info": {"TR": "Belgenin arka planındaki yazar, oluşturulma tarihi,\nprogram bilgisi gibi gizli takip verilerini tamamen siler.\nBu işlem, belgeyi üçüncü şahıslara göndermeden\nönce dijital gizliliğinizi korur.", "EN": "Completely removes hidden tracking data like author,\ncreation date, and software info from the background.\nThis protects your digital privacy before sending\nthe document to third parties."},
            "btn_clean_metadata": {"TR": "Künyeyi Temizle ve Kaydet", "EN": "Clean Metadata & Save"},
            "msg_metadata_cleaned": {"TR": "Belgenin künyesi (gizli veriler) tamamen temizlendi ve kaydedildi!", "EN": "Document metadata (hidden data) successfully cleaned and saved!"},

            # YENİ EKLENEN KISIMLAR
            "btn_prev_page": {"TR": "< Önceki", "EN": "< Prev"},
            "btn_next_page": {"TR": "Sonraki >", "EN": "Next >"},
            "lbl_page_indicator": {"TR": "Sayfa {} / {}", "EN": "Page {} / {}"},
            "btn_zoom_in": {"TR": "🔍 Yakınlaştır", "EN": "🔍 Zoom In"},
            "btn_zoom_out": {"TR": "🔍 Uzaklaştır", "EN": "🔍 Zoom Out"},
            "btn_fit": {"TR": "Ekrana Sığdır", "EN": "Fit Screen"},
            "btn_apply_and_save": {"TR": "Tümünü Uygula ve Kaydet", "EN": "Apply All & Save"},
            "chk_clean_meta": {"TR": "Belge Künyesini (Gizli Verileri) Temizle", "EN": "Clean Document Metadata (Hidden Data)"},
            "msg_saved_unified": {"TR": "Seçilen tüm özellikler uygulandı ve belge başarıyla kaydedildi!", "EN": "All selected features applied and document saved successfully!"},

            # --- GELİŞMİŞ DÜZENLEME (ÖNİZLEME BUTONLARI) ---
            "btn_prev_page": {"TR": "< Önceki", "EN": "< Prev"},
            "btn_next_page": {"TR": "Sonraki >", "EN": "Next >"},
            "lbl_page_indicator": {"TR": "Sayfa {} / {}", "EN": "Page {} / {}"},

            # --- GELİŞMİŞ DÜZENLEME: FİLİGRAN ---
            "chk_enable_wm": {"TR": "Filigranı Etkinleştir", "EN": "Enable Watermark"},
            "lbl_wm_text": {"TR": "Filigran Metni", "EN": "Watermark Text"},
            "ph_wm_text": {"TR": "Örn: GİZLİ, TASLAK...", "EN": "E.g.: CONFIDENTIAL, DRAFT..."},
            
            # --- GELİŞMİŞ DÜZENLEME: İMZA VE KAŞE ---
            "chk_enable_sig": {"TR": "İmza / Kaşeyi Etkinleştir", "EN": "Enable Signature / Stamp"},
            "btn_select_sig": {"TR": "Görsel Seç", "EN": "Select Image"},
            "msg_no_sig_selected": {"TR": "Görsel Seçilmedi", "EN": "No Image Selected"},
            "lbl_sig_pages": {"TR": "Uygulanacak Sayfalar", "EN": "Pages to Apply"},
            "opt_all_pages": {"TR": "Tüm Sayfalar", "EN": "All Pages"},
            "opt_first_page": {"TR": "Sadece İlk Sayfa", "EN": "First Page Only"},
            "opt_last_page": {"TR": "Sadece Son Sayfa", "EN": "Last Page Only"},
            "lbl_sig_pos": {"TR": "Konum", "EN": "Position"},
            "opt_bottom_right": {"TR": "Sağ Alt", "EN": "Bottom Right"},
            "opt_bottom_left": {"TR": "Sol Alt", "EN": "Bottom Left"},
            "opt_top_right": {"TR": "Sağ Üst", "EN": "Top Right"},
            "opt_top_left": {"TR": "Sol Üst", "EN": "Top Left"},
            "lbl_sig_scale": {"TR": "Boyut (Ölçek)", "EN": "Size (Scale)"},
            
            # --- GELİŞMİŞ DÜZENLEME: SAYFA NUMARASI ---
            "chk_enable_pn": {"TR": "Sayfa Numarasını Etkinleştir", "EN": "Enable Page Numbers"},
            "lbl_pn_start": {"TR": "Başlangıç Sayısı", "EN": "Starting Number"},
            "lbl_pn_format": {"TR": "Format (Örn: Sayfa {0})", "EN": "Format (E.g.: Page {0})"},
            "opt_bottom_center": {"TR": "Alt Orta", "EN": "Bottom Center"},
            "opt_top_center": {"TR": "Üst Orta", "EN": "Top Center"},

            # --- GELİŞMİŞ DÜZENLEME V2 EKLENTİLERİ ---
            "chk_wm_behind": {"TR": "Metnin Arkasına Yerleştir (Tarama PDF'lerde görünmeyebilir)", "EN": "Place Behind Text (May not show on scanned PDFs)"},
            "lbl_wm_rot": {"TR": "Döndürme (Derece)", "EN": "Rotation (Degrees)"},
            "lbl_wm_size": {"TR": "Metin Boyutu", "EN": "Text Size"},
            "lbl_wm_opacity": {"TR": "Saydamlık", "EN": "Opacity"},
            
            "lbl_sig_pages_custom": {"TR": "Uygulanacak Sayfalar (Örn: 1, 3, 5-8)", "EN": "Pages to Apply (E.g.: 1, 3, 5-8)"},
            "lbl_sig_x": {"TR": "Yatay Konum (X Eksen)", "EN": "Horizontal Pos (X Axis)"},
            "lbl_sig_y": {"TR": "Dikey Konum (Y Eksen)", "EN": "Vertical Pos (Y Axis)"},
            
            "lbl_pn_template": {"TR": "Hazır Şablonlar", "EN": "Ready Templates"},
            "lbl_pn_pages": {"TR": "Sayfa Aralığı (Örn: 1-10 veya Tümüne: *)", "EN": "Page Range (E.g.: 1-10 or All: *)"},
            "opt_pn_t1": {"TR": "Sadece Numara (1)", "EN": "Number Only (1)"},
            "opt_pn_t2": {"TR": "1 / 10", "EN": "1 / 10"},
            "opt_pn_t3": {"TR": "1 - 10", "EN": "1 - 10"},
            "opt_pn_t4": {"TR": "Sayfa 1", "EN": "Page 1"},
            "opt_pn_t5": {"TR": "Sayfa 1 / 10", "EN": "Page 1 / 10"},
            "opt_pn_t6": {"TR": "EK-1", "EN": "APPENDIX-1"},
            "opt_pn_t7": {"TR": "[ 1 ]", "EN": "[ 1 ]"},

            # --- GELİŞMİŞ DÜZENLEME V3 EKLENTİLERİ ---
            "chk_all_pages": {"TR": "Tüm Sayfalara Uygula", "EN": "Apply to All Pages"},
            "lbl_custom_pages": {"TR": "Özel Sayfalar (Örn: 1, 3, 5-8)", "EN": "Custom Pages (E.g.: 1, 3, 5-8)"},
            "lbl_font_style": {"TR": "Yazı Stili", "EN": "Font Style"},
            "opt_normal": {"TR": "Normal", "EN": "Normal"},
            "opt_bold": {"TR": "Kalın", "EN": "Bold"},
            "opt_italic": {"TR": "İtalik", "EN": "Italic"},
            "opt_bold_italic": {"TR": "Kalın İtalik", "EN": "Bold Italic"},
            
            "lbl_preset_pos": {"TR": "Hızlı Konum Şablonu", "EN": "Quick Position Preset"},
            "opt_pos_tl": {"TR": "Üst Sol", "EN": "Top Left"},
            "opt_pos_tc": {"TR": "Üst Orta", "EN": "Top Center"},
            "opt_pos_tr": {"TR": "Üst Sağ", "EN": "Top Right"},
            "opt_pos_ml": {"TR": "Orta Sol", "EN": "Middle Left"},
            "opt_pos_mc": {"TR": "Tam Orta", "EN": "Center"},
            "opt_pos_mr": {"TR": "Orta Sağ", "EN": "Middle Right"},
            "opt_pos_bl": {"TR": "Alt Sol", "EN": "Bottom Left"},
            "opt_pos_bc": {"TR": "Alt Orta", "EN": "Bottom Center"},
            "opt_pos_br": {"TR": "Alt Sağ", "EN": "Bottom Right"},


            # --- GELİŞMİŞ DÜZENLEME V4 EKLENTİLERİ ---
            "lbl_wm_pos_preset": {"TR": "Hızlı Konum Şablonu", "EN": "Quick Position Preset"},
            "opt_wm_mc": {"TR": "Orta Merkez", "EN": "Center Middle"},
            "opt_wm_bc": {"TR": "Orta Alt", "EN": "Bottom Center"},
            "opt_wm_tc": {"TR": "Orta Üst", "EN": "Top Center"},
            "opt_wm_lv": {"TR": "Sol Dikey", "EN": "Left Vertical"},
            "opt_wm_rv": {"TR": "Sağ Dikey", "EN": "Right Vertical"},
            "opt_wm_cv": {"TR": "Orta Dikey", "EN": "Center Vertical"},
            "lbl_pos_x": {"TR": "Yatay Konum (X Eksen)", "EN": "Horizontal Pos (X Axis)"},
            "lbl_pos_y": {"TR": "Dikey Konum (Y Eksen)", "EN": "Vertical Pos (Y Axis)"},
            
            "lbl_pn_multi_rule": {"TR": "Çoklu Kural Girişi (Gelişmiş)", "EN": "Multiple Rule Entry (Advanced)"},
            "msg_pn_multi_info": {"TR": "Farklı sayfalara farklı yazılar eklemek için kullanın.\nFormat: SayfaAralığı = Metin\nÖrn:\n1-3 = EK-1\n4-10 = EK-2\n(Boş bırakırsanız üstteki tekli ayar geçerli olur)", "EN": "Use to add different texts to different page ranges.\nFormat: PageRange = Text\nE.g.:\n1-3 = APPX-1\n4-10 = APPX-2\n(If left empty, single setting above applies)"},

            # --- GELİŞMİŞ DÜZENLEME V5 (RENKLİ FİLİGRAN VE ŞABLONLAR) ---
            "lbl_wm_preset_text": {"TR": "Hazır Metin Şablonu", "EN": "Ready Text Preset"},
            "lbl_wm_color": {"TR": "Metin Rengi", "EN": "Text Color"},
            "opt_color_gray": {"TR": "Gri", "EN": "Gray"},
            "opt_color_red": {"TR": "Kırmızı", "EN": "Red"},
            "opt_color_blue": {"TR": "Mavi", "EN": "Blue"},
            "opt_color_black": {"TR": "Siyah", "EN": "Black"},
            
            "wm_t1": {"TR": "GİZLİ", "EN": "CONFIDENTIAL"},
            "wm_t2": {"TR": "TASLAK", "EN": "DRAFT"},
            "wm_t3": {"TR": "SURETTİR", "EN": "COPY"},
            "wm_t4": {"TR": "ASLI GİBİDİR", "EN": "TRUE COPY"},
            "wm_t5": {"TR": "İPTAL", "EN": "VOID"},
            "wm_t6": {"TR": "KİŞİYE ÖZEL", "EN": "PERSONAL"},
            "wm_t7": {"TR": "ÖRNEKTİR", "EN": "SAMPLE"},

            # --- GELİŞMİŞ DÜZENLEME V6 (İMZA SAYDAMLIK VE DİL DÜZELTMESİ) ---
            "opt_custom_text": {"TR": "Özel Metin...", "EN": "Custom Text..."},
            "chk_sig_behind": {"TR": "İmza/Kaşeyi Metnin Arkasına Yerleştir", "EN": "Place Signature Behind Text"},
            "lbl_sig_opacity": {"TR": "İmza Saydamlığı", "EN": "Signature Opacity"},

            # --- GELİŞMİŞ DÜZENLEME V7 (KÜNYE GÖRÜNTÜLEYİCİ) ---
            "lbl_current_metadata": {"TR": "Dosyadaki Mevcut Gizli Bilgiler (Künye)", "EN": "Existing Metadata in File"},
            "msg_meta_empty": {"TR": "Künye bilgisi bulunamadı veya temizlenmiş.", "EN": "No metadata found or it's already cleaned."},
            "meta_author": {"TR": "Yazar: ", "EN": "Author: "},
            "meta_creator": {"TR": "Oluşturan: ", "EN": "Creator: "},
            "meta_producer": {"TR": "Araç: ", "EN": "Producer: "},
            "meta_date": {"TR": "Oluşturulma: ", "EN": "Created: "},

            # --- PDF KARŞILAŞTIRMA SAYFASI ---
            "btn_compare": {"TR": "PDF Karşılaştırma", "EN": "PDF Compare"},
            "tab_compare_title": {"TR": "Akıllı PDF Karşılaştırma", "EN": "Smart PDF Comparison"},
            "lbl_orig_pdf": {"TR": "1. Orijinal PDF (Eski Sürüm)", "EN": "1. Original PDF (Old Version)"},
            "lbl_mod_pdf": {"TR": "2. Değiştirilmiş PDF (Yeni Sürüm)", "EN": "2. Modified PDF (New Version)"},
            "btn_select_file": {"TR": "Dosya Seç", "EN": "Select File"},
            "msg_waiting_file": {"TR": "Bekleniyor...", "EN": "Waiting..."},
            "btn_diff_html": {"TR": "🌐 Tarayıcıda Yan Yana Karşılaştır (HTML)", "EN": "🌐 Compare Side-by-Side in Browser (HTML)"},
            "btn_diff_pdf": {"TR": "📄 Değişiklik Raporu Oluştur (PDF)", "EN": "📄 Generate Diff Report (PDF)"},
            "msg_select_both": {"TR": "Lütfen karşılaştırılacak iki PDF dosyasını da seçin!", "EN": "Please select both PDF files to compare!"},
            "msg_diff_reading": {"TR": "Metinler Çıkartılıyor ve Karşılaştırılıyor...", "EN": "Extracting and Comparing Texts..."},
            "msg_diff_html_success": {"TR": "HTML raporu oluşturuldu ve tarayıcıda açıldı!", "EN": "HTML report generated and opened in browser!"},
            "msg_diff_pdf_success": {"TR": "Karşılaştırma PDF raporu başarıyla kaydedildi!", "EN": "Comparison PDF report saved successfully!"},

            # --- PDF KARŞILAŞTIRMA V2 EKLENTİLERİ ---
            "btn_diff_visual": {"TR": "🖍️ Doğrudan PDF Üzerinde İşaretle", "EN": "🖍️ Visual Highlight on PDF"},
            "msg_diff_visual_success": {"TR": "Orijinal PDF'te silinenler kırmızıyla, yeni PDF'te eklenenler yeşille işaretlendi!\n(Kaydedilen klasör açılıyor)", "EN": "Original PDF marked with red for deletions, new PDF marked with green for additions!\n(Opening saved folder)"},

            # --- HAKKINDA SAYFASI (VİTRİN) ---
            "about_company": {"TR": "Kitkars-Radu", "EN": "Kitkars-Radu"},
            "about_mission": {"TR": "Hukuk, eğitim ve eğlenceyi dijital dünyayla buluşturan\nyazılım çözümleri.", "EN": "Software solutions bringing law, education,\nand entertainment to the digital world."},
            "lbl_security_title": {"TR": "🛡️ %100 Güvenli ve Çevrimdışı", "EN": "🛡️ 100% Secure & Offline"},
            "lbl_security_desc": {"TR": "Gizliliğiniz bizim için en üst sıradadır. Bu uygulama tamamen çevrimdışı çalışır.\nBelgeleriniz asla hiçbir sunucuya yüklenmez, cihazınızdan dışarı çıkmaz ve işlenmez.", "EN": "Your privacy is our priority. This application works completely offline.\nYour documents are never uploaded to any server or leave your device."},
            "lbl_our_apps": {"TR": "Mobil Uygulamalarımız (Google Play)", "EN": "Our Mobile Apps (Google Play)"},
            "desc_deutsch": {"TR": "Almanca öğrenmeyi kolaylaştıran modern ve interaktif eğitim uygulaması.", "EN": "Modern and interactive education app making German learning easy."},
            "desc_radu": {"TR": "Strateji ve macera dolu, heyecan verici bir oyun deneyimi.", "EN": "An exciting gaming experience full of strategy and adventure."},
            "btn_visit_googleplay": {"TR": "Google Play'de Gör", "EN": "View on Google Play"},
            "lbl_visit_blog": {"TR": "Güncel duyurular ve yeni projelerimiz için blog sayfamızı ziyaret edin:", "EN": "Visit our blog for latest announcements and new projects:"},
            "btn_go_blog": {"TR": "Kitkars-Radu Blog'u Ziyaret Et", "EN": "Visit Kitkars-Radu Blog"},
            "footer_text": {"TR": "© 2026 Kitkars-Radu. Tüm Hakları Saklıdır. v1.0.0 Pro", "EN": "© 2026 Kitkars-Radu. All Rights Reserved. v1.0.0 Pro"},

            # --- HAKKINDA SAYFASI V2 (İLETİŞİM VE GİZLİLİK) ---
            "btn_contact": {"TR": "✉️ Bize Ulaşın (Öneri & Şikayet)", "EN": "✉️ Contact Us (Feedback)"},
            "btn_privacy": {"TR": "📜 Kullanım Şartları ve Gizlilik", "EN": "📜 Terms of Use & Privacy"},
            "privacy_title": {"TR": "Kullanım Şartları ve Gizlilik Bilgilendirmesi", "EN": "Terms of Use & Privacy Policy"},
            "privacy_text": {"TR": "1. ÇEVRİMDIŞI ÇALIŞMA PRENSİBİ\nBu uygulama gizliliğinizi en üst düzeyde korumak amacıyla %100 çevrimdışı (offline) çalışacak şekilde tasarlanmıştır. Uygulamaya yüklediğiniz belgeler, PDF'ler veya görseller hiçbir şekilde harici bir sunucuya, buluta veya üçüncü şahıslara aktarılmaz.\n\n2. VERİ GÜVENLİĞİ\nTüm sıkıştırma, şifreleme, filigran ekleme ve karşılaştırma işlemleri yalnızca kendi bilgisayarınızın işlemcisi (CPU) ve belleği (RAM) üzerinde lokal olarak gerçekleştirilir.\n\n3. KULLANIM HAKLARI\nBu yazılım Kitkars-Radu Mobile Studios tarafından geliştirilmiştir. Uygulamanın kaynak kodlarının kopyalanması, tersine mühendislik yapılması veya izinsiz ticari amaçla satılması yasaktır.\n\n4. İLETİŞİM\nHer türlü dilek, şikayet ve geliştirme önerileriniz için radugames58@gmail.com adresi üzerinden bizimle iletişime geçebilirsiniz.\n\nBu uygulamayı kullanarak yukarıdaki şartları ve yerel işlem prensibini kabul etmiş sayılırsınız.", 
                             "EN": "1. OFFLINE OPERATION PRINCIPLE\nThis application is designed to work 100% offline to protect your privacy. Documents you upload are never transferred to any external server or cloud.\n\n2. DATA SECURITY\nAll processing occurs locally on your computer's CPU and RAM.\n\n3. USAGE RIGHTS\nDeveloped by Kitkars-Radu Mobile Studios. Reverse engineering or unauthorized commercial distribution is prohibited.\n\n4. CONTACT\nFor feedback and support, contact us at radugames58@gmail.com.\n\nBy using this application, you agree to these terms."},

            # --- HAKKINDA SAYFASI V3 (SÜRÜM VE FOTOĞRAFLI KARTLAR) ---
            "lbl_version": {"TR": "Mevcut Sürüm: v1.0.0 Pro", "EN": "Current Version: v1.0.0 Pro"},
            "btn_check_update": {"TR": "🔄 Yeni Sürüm Kontrol Et", "EN": "🔄 Check for Updates"},
            "lbl_update_info": {"TR": "Yeni özellikler ve güncellemeler için web sitemizi ziyaret edin.", "EN": "Visit our website for new features and updates."},

            # --- PDF GÜVENLİK VE KVKK (REDACTION) ---
            "btn_kvkk": {"TR": "PDF Güvenlik & KVKK", "EN": "PDF Security & GDPR"},
            "tab_kvkk_title": {"TR": "Geri Döndürülemez Metin Karartma", "EN": "Irreversible Text Redaction"},
            "lbl_kvkk_info_title": {"TR": "🛡️ Bu Sistem Nasıl Çalışır?", "EN": "🛡️ How This System Works?"},
            "lbl_kvkk_info_desc": {"TR": "Bu modül, PDF içindeki hassas verileri (T.C. No, İsim, IBAN vb.) nükleer seviyede yok eder. Üstüne siyah bant çekmekle kalmaz, metnin altındaki dijital veriyi de tamamen siler. Böylece karartılan alan kopyalanamaz veya geri döndürülemez. %100 çevrimdışı çalışır.", 
                                   "EN": "This module wipes sensitive data (ID No, Name, IBAN etc.) at a nuclear level. It doesn't just draw a black box; it completely deletes the underlying digital text data. Redacted areas cannot be copied or reversed. Works 100% offline."},
            "lbl_redact_text": {"TR": "Karartılacak Kelimeler veya Numaralar (Virgül ile ayırın):", "EN": "Words or Numbers to Redact (Separate with commas):"},
            "ph_redact_text": {"TR": "Örn: 12345678901, Ahmet Yılmaz, TR0000...", "EN": "Ex: 12345678901, John Doe, IBAN..."},
            "btn_apply_redaction": {"TR": "🕵️ Seçili Metinleri Kalıcı Olarak Sil", "EN": "🕵️ Permanently Delete Selected Texts"},
            "msg_redact_success": {"TR": "Belirlenen metinler başarıyla ve kalıcı olarak karartıldı!", "EN": "Specified texts have been successfully and permanently redacted!"},
            "msg_redact_warn_no_text": {"TR": "Lütfen karartılacak en az bir kelime girin!", "EN": "Please enter at least one word to redact!"},

            # --- PDF GÜVENLİK V2 ---
            "lbl_redact_color": {"TR": "Karartma Bant Rengi:", "EN": "Redaction Box Color:"},
            "opt_color_black": {"TR": "Siyah", "EN": "Black"},
            "opt_color_white": {"TR": "Beyaz (Gizli)", "EN": "White (Hidden)"},

            # --- PDF GÜVENLİK V3 (GÖRSELDEKİ TÜM ÖZELLİKLER) ---
            "tab_kvkk_guide": {"TR": "Redaction Guide", "EN": "Redaction Guide"},
            "msg_redact_guide": {"TR": "Bu modül, PDF içindeki hassas verileri T.C. No, İsim, IBAN vb. kalıcı olarak silmek için tasarlanmıştır.\nKarartılan alanlar kopyalanamaz veya geri döndürülemez. Tüm işlemler cihazınızda yapılır.", 
                                 "EN": "This module is designed to permanently delete sensitive data such as ID No, Name, IBAN etc.\nRedacted areas cannot be copied or reversed. All processes are done on your device."},
            "lbl_redact_type": {"TR": "Redaction Type", "EN": "Redaction Type"},
            "opt_redact_words": {"TR": "Belli Kelimeler/Numaralar", "EN": "Specific Words/Numbers"},
            "opt_redact_regex": {"TR": "Kalıplar (RegEx)", "EN": "Patterns (RegEx)"},
            "lbl_redact_style": {"TR": "Karartma Türü", "EN": "Redaction Style"},
            "lbl_bant_color": {"TR": "Bant Rengi", "EN": "Box Color"},
            "lbl_placeholder": {"TR": "Yer Tutucu Metin", "EN": "Placeholder Text"},
            "btn_apply_save_redact": {"TR": "Tümünü Karart ve Kaydet", "EN": "Redact All and Save"},
            "opt_color_gray": {"TR": "Gri", "EN": "Gray"},
            "btn_zoom_in_text": {"TR": "Yakınlaştır", "EN": "Zoom In"},
            "btn_zoom_out_text": {"TR": "Uzaklaştır", "EN": "Zoom Out"},
            "lbl_help_regex": {"TR": "Yardım mı lazım?", "EN": "Help with Patterns"},

            # --- PDF GÜVENLİK V3 (TAMAMLANMIŞ VE DÜZELTİLMİŞ SÜRÜM) ---
            "btn_kvkk": {"TR": "PDF Güvenlik & KVKK", "EN": "PDF Security & GDPR"},
            "tab_kvkk_title": {"TR": "Geri Döndürülemez Metin Karartma", "EN": "Irreversible Text Redaction"},
            "tab_kvkk_guide": {"TR": "Karartma Rehberi", "EN": "Redaction Guide"},
            "msg_redact_guide": {"TR": "Bu modül, PDF içindeki hassas verileri kalıcı olarak silmek için tasarlanmıştır.\nKarartılan alanlar kopyalanamaz veya geri döndürülemez. Tüm işlemler cihazınızda yapılır.", 
                                 "EN": "This module is designed to permanently delete sensitive data.\nRedacted areas cannot be copied or reversed. All processes are done locally on your device."},
            "lbl_redact_type": {"TR": "Karartma Modu", "EN": "Redaction Mode"},
            "opt_redact_words": {"TR": "Belli Kelimeler/Numaralar", "EN": "Specific Words/Numbers"},
            "opt_redact_regex": {"TR": "Otomatik Kalıplar (RegEx)", "EN": "Auto Patterns (RegEx)"},
            "lbl_redact_style": {"TR": "Karartma Görünümü", "EN": "Redaction Style"},
            "lbl_bant_color": {"TR": "Bant Rengi", "EN": "Box Color"},
            "opt_color_black": {"TR": "Siyah", "EN": "Black"},
            "opt_color_white": {"TR": "Beyaz (Şeffaf)", "EN": "White (Hidden)"},
            "opt_color_gray": {"TR": "Gri", "EN": "Gray"},
            "opt_color_red": {"TR": "Kırmızı", "EN": "Red"},
            "opt_color_blue": {"TR": "Mavi", "EN": "Blue"},
            "lbl_placeholder": {"TR": "Yeni Yazı (Opsiyonel)", "EN": "Replacement Text (Optional)"},
            "ph_hidden_data": {"TR": "[GİZLİ VERİ]", "EN": "[REDACTED]"},
            "btn_apply_save_redact": {"TR": "Tümünü Karart ve Kaydet", "EN": "Redact All and Save"},
            "btn_zoom_in_text": {"TR": "Yakınlaştır", "EN": "Zoom In"},
            "btn_zoom_out_text": {"TR": "Uzaklaştır", "EN": "Zoom Out"},
            "lbl_help_regex": {"TR": "Yardım mı lazım? Kalıpları gör.", "EN": "Need help? View Patterns."},
            "regex_title": {"TR": "Regex (Kalıp) Kullanım Rehberi", "EN": "Regex (Pattern) Guide"},
            "regex_desc": {"TR": "Regex, belirli bir kurala uyan tüm verileri otomatik bulup silmenizi sağlar. Karartılacak metin kutusuna aşağıdaki kodları kopyalayıp yapıştırabilirsiniz:\n\n• T.C. Kimlik No: \\b[0-9]{11}\\b\n• E-Posta Adresi: [a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}\n• Telefon Numarası: \\b0?[5][0-9]{2}\\s?[0-9]{3}\\s?[0-9]{2}\\s?[0-9]{2}\\b\n• IBAN: \\bTR[0-9]{24}\\b\n• Sadece Rakamlar (Tüm Sayılar): \\b\\d+\\b", 
                           "EN": "Regex allows you to automatically find and delete all data matching a specific rule. You can copy and paste the following codes into the text box:\n\n• ID Number (11 digits): \\b[0-9]{11}\\b\n• E-Mail Address: [a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}\n• Phone Number: \\b0?[5][0-9]{2}\\s?[0-9]{3}\\s?[0-9]{2}\\s?[0-9]{2}\\b\n• IBAN: \\b[A-Z]{2}[0-9]{24}\\b\n• All Numbers: \\b\\d+\\b"},
            "ph_page_ranges": {"TR": "Örn: 1, 3, 5-10", "EN": "Ex: 1, 3, 5-10"},

            # --- PDF GÜVENLİK V4 (METİN STİLLERİ VE ÇOKLU REGEX) ---
            "opt_color_transparent": {"TR": "Şeffaf (Arkaplan Yok)", "EN": "Transparent (No Bg)"},
            "lbl_text_color": {"TR": "Yazı Rengi", "EN": "Text Color"},
            "lbl_text_size": {"TR": "Punto", "EN": "Size"},
            "lbl_text_style": {"TR": "Stil", "EN": "Style"},
            "lbl_text_align": {"TR": "Hizalama", "EN": "Align"},
            "opt_align_left": {"TR": "Sol", "EN": "Left"},
            "opt_align_center": {"TR": "Orta", "EN": "Center"},
            "opt_align_right": {"TR": "Sağ", "EN": "Right"},
            "chk_wipe_data": {"TR": "Alttaki Orijinal Dijital Veriyi Sil (KVKK)", "EN": "Wipe Original Digital Data (GDPR)"},

            # --- PDF GÜVENLİK V5 (DÜZELTMELER) ---
            "opt_txt_black": {"TR": "Siyah", "EN": "Black"},
            "opt_txt_white": {"TR": "Beyaz", "EN": "White"},
            "opt_txt_red": {"TR": "Kırmızı", "EN": "Red"},
            "opt_txt_blue": {"TR": "Mavi", "EN": "Blue"},

            # --- PDF GÜVENLİK V6 (BAĞIMSIZ METİN VE FONT AYARLARI) ---
            "opt_redact_free_text": {"TR": "Bağımsız Metin Ekle", "EN": "Add Independent Text"},
            "lbl_font_family": {"TR": "Yazı Tipi (Font)", "EN": "Font Family"},
            "lbl_x_axis": {"TR": "X Ekseni (Yatay Konum)", "EN": "X Axis (Horizontal)"},
            "lbl_y_axis": {"TR": "Y Ekseni (Dikey Konum)", "EN": "Y Axis (Vertical)"},

            # --- PDF GÜVENLİK V7 (BİRLEŞİK ARAYÜZ) ---
            "lbl_redact_section": {"TR": "1. Karartma (Sansür) Ayarları", "EN": "1. Redaction Settings"},
            "lbl_free_text_section": {"TR": "2. Bağımsız Metin (Filigran)", "EN": "2. Free Text (Watermark)"},
            "lbl_shared_text_style": {"TR": "3. Ortak Yazı Ayarları", "EN": "3. Shared Text Styles"},
            "lbl_free_text_input": {"TR": "Eklenecek Bağımsız Metin", "EN": "Independent Text to Add"},

            # --- AKILLI ORGANİZASYON (BÖLME & İÇİNDEKİLER) ---
            "btn_org": {"TR": "Akıllı Organizasyon", "EN": "Smart Organization"},
            "tab_split_size": {"TR": "Boyuta Göre Böl (UYAP)", "EN": "Split by Size"},
            "tab_bookmark_merge": {"TR": "İçindekilerli Birleştir", "EN": "Merge with Bookmarks"},
            "lbl_max_mb": {"TR": "Maksimum Boyut Sınırı (MB):", "EN": "Max Size Limit (MB):"},
            "msg_split_info": {"TR": "Bu araç, seçtiğiniz İLK dosyayı belirlediğiniz MB sınırını aşmayacak şekilde otomatik parçalara ayırır. UYAP vb. sistemler için idealdir.", 
                               "EN": "This tool automatically splits the FIRST selected file so it doesn't exceed the MB limit. Ideal for size-restricted portals."},
            "msg_bookmark_info": {"TR": "Eklediğiniz tüm dosyalar birleştirilir ve sol tarafa dosya adlarından oluşan tıklanabilir bir 'İçindekiler' (Bookmark) menüsü eklenir.", 
                                  "EN": "All added files are merged, and a clickable 'Bookmarks' menu (created from filenames) is added to the left pane."},
            "msg_split_success": {"TR": "PDF dosyası belirlenen boyuta göre başarıyla parçalara ayrıldı!", "EN": "The PDF file was successfully split into parts according to the size!"},
            "lbl_files_to_process": {"TR": "İşlem Bekleyen Dosyalar", "EN": "Files to Process"},

            # --- AKILLI ORGANİZASYON GÜNCELLEMELERİ ---
            "lbl_merge_comp": {"TR": "Birleştirme ve Sıkıştırma (Boyut Küçültme):", "EN": "Merge Compression Level:"},
            "opt_comp_1": {"TR": "Hafif (Hızlı)", "EN": "Light (Fast)"},
            "opt_comp_2": {"TR": "Standart (Önerilen)", "EN": "Standard (Recommended)"},
            "opt_comp_3": {"TR": "Maksimum (Yavaş ama en küçük)", "EN": "Maximum (Smallest size)"},

            # --- OCR (OPTİK KARAKTER TANIMA) ---
            "btn_ocr": {"TR": "OCR (Metin Okuma)", "EN": "OCR (Text Recognition)"},
            "tab_ocr_title": {"TR": "Akıllı OCR Motoru", "EN": "Smart OCR Engine"},
            "msg_ocr_info": {"TR": "Bu modül resim formatındaki (taranmış) belgeleri okur. 'Aranabilir PDF' ile belgeyi kopyalanabilir hale getirebilir veya 'Bölgesel Okuma' ile evrakın sadece belirli bir koordinatındaki metni çıkarabilirsiniz.", "EN": "This module reads scanned documents. Make it a 'Searchable PDF' or extract text from specific coordinates."},
            "lbl_ocr_mode": {"TR": "OCR Çalışma Modu", "EN": "OCR Mode"},
            "opt_ocr_pdf": {"TR": "Tüm Sayfayı Aranabilir PDF Yap", "EN": "Make Full Page Searchable PDF"},
            "opt_ocr_region": {"TR": "Bölgesel Metin Çıkar (Koordinatlı)", "EN": "Regional Text Extraction"},
            "lbl_ocr_lang": {"TR": "Okuma Dili", "EN": "Recognition Language"},
            "opt_lang_tr": {"TR": "Türkçe", "EN": "Turkish"},
            "opt_lang_en": {"TR": "İngilizce", "EN": "English"},
            "opt_lang_de": {"TR": "Almanca", "EN": "German"},
            "lbl_region_w": {"TR": "Genişlik Kapsamı (W)", "EN": "Width Scope (W)"},
            "lbl_region_h": {"TR": "Yükseklik Kapsamı (H)", "EN": "Height Scope (H)"},
            "btn_start_ocr": {"TR": "OCR İşlemini Başlat", "EN": "Start OCR Process"},
            "msg_tesseract_error": {"TR": "Tesseract OCR motoru bulunamadı! Lütfen Windows için Tesseract'ı kurun.", "EN": "Tesseract OCR engine not found! Please install Tesseract for Windows."},
            "lbl_extracted_text": {"TR": "Çıkarılan Metin Sonucu", "EN": "Extracted Text Result"},

            "btn_delete_item": {"TR": "Sil", "EN": "Delete"},
            "lbl_page_short": {"TR": "Sayfa", "EN": "Pages"},

            # --- KARŞILAMA EKRANI VE NAVİGASYON ---
            "btn_home": {"TR": "Ana Sayfa", "EN": "Home"},
            "welcome_subtitle": {"TR": "Tüm PDF ve Belge ihtiyaçlarınız için profesyonel çözüm merkezi.", "EN": "Professional solution center for all your PDF and document needs."},
            "quick_access_title": {"TR": "Hızlı Erişim", "EN": "Quick Access"},
            "edit_slot": {"TR": "Slotu Düzenle", "EN": "Edit Slot"},

            # --- ANA SAYFA GEÇMİŞ (HISTORY) VE SLOTLAR ---
            "history_action_kvkk": {"TR": "'{0}' dosyasına karartma uygulandı ➔ '{1}'", "EN": "Redaction applied to '{0}' ➔ '{1}'"},
            "history_action_merge": {"TR": "{0} adet dosya birleştirildi ➔ '{1}'", "EN": "{0} files merged ➔ '{1}'"},
            "history_action_convert": {"TR": "'{0}', {1} formatına dönüştürüldü ➔ '{2}'", "EN": "'{0}' converted to {1} ➔ '{2}'"},
            "btn_open_file": {"TR": "Dosyayı Aç", "EN": "Open File"},
            "lbl_history_title": {"TR": "🕒 Son Yapılan İşlemler (Geçmiş)", "EN": "🕒 Recent Actions (History)"},
            "lbl_slot_choose": {"TR": "Bu yuvaya (slota) atamak istediğiniz aracı seçin:", "EN": "Select the tool you want to assign to this slot:"},

            "msg_empty_history": {"TR": "Henüz kaydedilmiş bir işlem geçmişi bulunmuyor.", "EN": "No action history found yet."},
            "history_action_kvkk": {"TR": "'{0}' dosyasına karartma uygulandı ➔ '{1}'", "EN": "Redaction applied to '{0}' ➔ '{1}'"},
            "history_action_merge": {"TR": "{0} adet dosya birleştirildi ➔ '{1}'", "EN": "{0} files merged ➔ '{1}'"},
            "history_action_convert": {"TR": "'{0}' dosyası dönüştürüldü ➔ '{1}'", "EN": "'{0}' converted ➔ '{1}'"},
            "history_action_advanced": {"TR": "'{0}' üzerinde gelişmiş düzenleme yapıldı ➔ '{1}'", "EN": "Advanced editing on '{0}' ➔ '{1}'"},
            "history_action_ocr": {"TR": "'{0}' dosyasına metin okuma (OCR) yapıldı ➔ '{1}'", "EN": "OCR performed on '{0}' ➔ '{1}'"},
            "history_action_generic": {"TR": "'{0}' dosyası işlendi ➔ '{1}'", "EN": "Processed '{0}' ➔ '{1}'"},
            "btn_open_file": {"TR": "Aç", "EN": "Open"},
            "msg_shortcut_info": {"TR": "💡 Kısayolu değiştirmek için butonun üzerine sağ tıklayın.", "EN": "💡 Right-click on a button to change the shortcut."},


            # --- DRAG & DROP DİYALOG ---
            "msg_dnd_dialog_title": {"TR": "Dosyalar Yakalandı", "EN": "Files Captured"},
            "msg_dnd_question": {"TR": "Bu dosyalarla hangi işlemi yapmak istiyorsunuz?", "EN": "What action do you want to perform with these files?"},
            "lbl_dropped_files": {"TR": "Sürüklenen Dosyalar:", "EN": "Dropped Files:"},

            # --- TEMA SİSTEMİ ---
            "theme_dark": {"TR": "Karanlık Mod", "EN": "Dark Mode"},
            "theme_light": {"TR": "Aydınlık Mod", "EN": "Light Mode"},

            # --- FORM & OTOMASYON ---
            "btn_form": {"TR": "Form & Otomasyon", "EN": "Form & Automation"},
            "tab_form_title": {"TR": "Toplu PDF Form Doldurucu", "EN": "Batch PDF Form Filler"},
            "msg_form_info": {"TR": "İnteraktif bir PDF şablonu ve veri içeren bir Excel dosyası seçerek yüzlerce belgeyi saniyeler içinde otomatik doldurun.", "EN": "Select an interactive PDF template and an Excel file to automatically fill hundreds of documents in seconds."},
            "lbl_template_pdf": {"TR": "1. Şablon PDF (Doldurulacak Form)", "EN": "1. Template PDF (Form to Fill)"},
            "lbl_excel_data": {"TR": "2. Veri Kaynağı (Excel Dosyası)", "EN": "2. Data Source (Excel File)"},
            "msg_waiting_excel": {"TR": "Henüz Excel seçilmedi.", "EN": "No Excel selected yet."},
            "lbl_output_settings": {"TR": "3. Çıktı Ayarları", "EN": "3. Output Settings"},
            "lbl_name_format": {"TR": "Dosya İsimlendirme Şablonu", "EN": "File Naming Format"},
            "ph_name_format": {"TR": "Örn: Sozlesme_{Ad Soyad}.pdf", "EN": "e.g., Contract_{Name}.pdf"},
            "btn_start_form": {"TR": "Otomatik Doldurmayı Başlat", "EN": "Start Auto-Fill"},
            "msg_form_success": {"TR": "Tüm formlar başarıyla dolduruldu ve kaydedildi!", "EN": "All forms successfully filled and saved!"},
            "msg_form_reading": {"TR": "Veriler Okunuyor ve Formlar Dolduruluyor...", "EN": "Reading Data and Filling Forms..."},

            # --- FORM & OTOMASYON EKLERİ ---
            "btn_test_files": {"TR": "🧪 Test Dosyası Üret", "EN": "🧪 Generate Test Files"},
            "msg_test_success": {"TR": "Örnek PDF Şablonu ve Excel dosyası masaüstüne başarıyla oluşturuldu!\n\nBu dosyaları seçerek sistemi test edebilirsiniz.", "EN": "Sample PDF Template and Excel file successfully created on your desktop!"},
            "lbl_preview_form": {"TR": "Canlı Form Önizlemesi (Excel'in 1. Satırı)", "EN": "Live Form Preview (Excel Row 1)"},

            # --- FORM & OTOMASYON EKLERİ ---
            "btn_test_files": {"TR": "📁 Hazır Şablonları Üret", "EN": "📁 Generate Templates"},
            "msg_test_success": {"TR": "Avukat, İK ve Vatandaşlar için 3 farklı hazır PDF Şablonu ve Excel dosyası masaüstüne başarıyla oluşturuldu!\n\nBu dosyaları seçerek sistemi test edebilirsiniz.", "EN": "3 different ready-to-use PDF templates and Excel files successfully created on your desktop!"},
            "lbl_preview_form": {"TR": "Canlı Form Önizlemesi", "EN": "Live Form Preview"},
            "lbl_record_indicator": {"TR": "Kayıt: {0} / {1}", "EN": "Record: {0} / {1}"},

            # --- FORM & OTOMASYON EKLERİ ---
            "btn_test_files": {"TR": "📁 Hazır Şablonları Üret", "EN": "📁 Generate Templates"},
            "msg_test_success": {"TR": "Örnek şablonlar başarıyla yüklendi.", "EN": "Sample templates successfully loaded."},
            "lbl_preview_form": {"TR": "Canlı Form Önizlemesi", "EN": "Live Form Preview"},
            "lbl_record_indicator": {"TR": "Kayıt: {0} / {1}", "EN": "Record: {0} / {1}"},
            "lbl_smart_form": {"TR": "Dinamik Form (Manuel Doldurma)", "EN": "Smart Form (Manual Fill)"},
            "lbl_ready_templates": {"TR": "Hazır Şablon Seç", "EN": "Select Ready Template"},
            "opt_tmpl_none": {"TR": "Şablon Seçin...", "EN": "Select Template..."},
            "opt_tmpl_ik": {"TR": "1. İK - Detaylı Maaş Bordrosu", "EN": "1. HR - Salary Payslip"},
            "opt_tmpl_hukuk": {"TR": "2. Hukuk - İhtarname", "EN": "2. Legal - Notice"},
            "opt_tmpl_dilekce": {"TR": "3. Resmi Kurum - Genel Dilekçe", "EN": "3. Official - General Petition"},
            "msg_manual_save_success": {"TR": "Belge başarıyla dolduruldu ve kaydedildi!", "EN": "Document successfully filled and saved!"},
            "btn_save_manual": {"TR": "Tekli Belgeyi Kaydet", "EN": "Save Single Document"},

            # --- FORM KULLANIM KILAVUZU ---
            "lbl_guide_title": {"TR": "💡 Nasıl Kullanılır?", "EN": "💡 How to Use?"},
            "msg_guide_text": {
                "TR": "1. ADIM: Doldurulabilir boş form alanları içeren 'Şablon PDF' dosyanızı yükleyin.\n\n2. ADIM: İlgili verileri içeren Excel dosyanızı yükleyin (Sütun başlıkları PDF içindeki alan isimleriyle aynı olmalıdır).\n\nSONUÇ: İki dosyayı da seçtiğiniz an ekranın solunda canlı önizleme başlar. Kayıtlar arasında gezinebilir ve 'Otomatik Doldurmayı Başlat' diyerek yüzlerce dosyayı saniyeler içinde üretebilirsiniz.", 
                "EN": "STEP 1: Load your 'Template PDF' file containing fillable form fields.\n\nSTEP 2: Load your Excel file containing the data (Column headers must match the PDF field names).\n\nRESULT: As soon as both files are selected, live preview starts on the left. You can navigate through records and click 'Start Auto-Fill' to generate hundreds of files in seconds."
            },

            # --- FORM & İSİMLENDİRME EKLERİ ---
            "lbl_dynamic_tags": {"TR": "Dinamik Etiketler (İsme Eklemek İçin Tıklayın):", "EN": "Dynamic Tags (Click to Add to Name):"},
            "msg_illegal_chars": {"TR": "Dosya isminde geçersiz karakterler temizlendi.", "EN": "Illegal characters in filename were cleaned."},

            # --- FORM KULLANIM KILAVUZU ---
            "lbl_guide_title": {"TR": "💡 Nasıl Kullanılır?", "EN": "💡 How to Use?"},
            "msg_guide_text": {
                "TR": "1. ADIM: Doldurulabilir form alanları içeren 'Şablon PDF' dosyanızı yükleyin.\n\n2. ADIM: İlgili verileri içeren Excel dosyanızı yükleyin.\n\n3. ADIM (Akıllı İsimlendirme): Excel yüklendiğinde alt kısımda beliren yeşil etiketlere (örn: + Ad_Soyad) tıklayarak çıktı dosyalarının isim şablonunu belirleyin (Örn: Belge_{Ad_Soyad}.pdf).\n\nSONUÇ: 'Otomatik Doldurmayı Başlat' diyerek yüzlerce PDF'i saniyeler içinde kişiye özel isimlerle üretebilirsiniz.", 
                "EN": "STEP 1: Load your 'Template PDF' file.\n\nSTEP 2: Load your Excel data file.\n\nSTEP 3 (Smart Naming): Click the green tags that appear after loading Excel to define the output filename template (e.g., File_{Name}.pdf).\n\nRESULT: View the live preview on the left and click 'Start Auto-Fill' to generate hundreds of dynamically named files in seconds."
            },
            "lbl_dynamic_tags": {"TR": "Dinamik Etiketler (İsme Eklemek İçin Tıklayın):", "EN": "Dynamic Tags (Click to Add to Name):"},

            # --- MAKRO, BATES VE KAŞE ---
            "btn_macro": {"TR": "Makro & Gelişmiş Kaşe", "EN": "Macro & Advanced Stamp"},
            "tab_macro_tasks": {"TR": "Zincirleme İşlemler", "EN": "Chain Tasks"},
            "tab_bates": {"TR": "Bates Numaralandırma", "EN": "Bates Numbering"},
            "tab_stamp": {"TR": "Mühür & Kaşe", "EN": "Stamp & Seal"},
            "chk_macro_kvkk": {"TR": "Otomatik T.C. Kimlik ve IBAN Karartma (KVKK)", "EN": "Auto-Redact SSN & IBAN"},
            "chk_macro_compress": {"TR": "UYAP Uyumlu Sıkıştırma (Optimizasyon)", "EN": "Court-Compliant Compression"},
            "lbl_bates_prefix": {"TR": "Ön Ek (Örn: EK-)", "EN": "Prefix (e.g., APP-)"},
            "lbl_bates_zeros": {"TR": "Sıfır Dolgusu (Hane)", "EN": "Zero Padding (Digits)"},
            "lbl_stamp_preset": {"TR": "Hazır Mühür Şablonları", "EN": "Ready Stamp Templates"},
            "opt_stamp_none": {"TR": "Mühür Yok", "EN": "No Stamp"},
            "opt_stamp_asli": {"TR": "ASLI GİBİDİR (Mavi)", "EN": "TRUE COPY (Blue)"},
            "opt_stamp_gizli": {"TR": "GİZLİ (Kırmızı)", "EN": "CONFIDENTIAL (Red)"},
            "opt_stamp_onay": {"TR": "ONAYLANDI (Yeşil)", "EN": "APPROVED (Green)"},
            "opt_stamp_custom": {"TR": "Özel Görsel Yükle", "EN": "Upload Custom Image"},

            # --- GELİŞMİŞ MAKRO & BATES ---
            "btn_guide_modal": {"TR": "💡 Nasıl Kullanılır? (Kılavuz)", "EN": "💡 How to Use? (Guide)"},
            "chk_auto_preview": {"TR": "⚡ Değişiklikleri Anında Önizle", "EN": "⚡ Live Auto-Preview"},
            "tab_kvkk_sec": {"TR": "KVKK & Güvenlik", "EN": "Redact & Security"},
            "lbl_redact_custom": {"TR": "Özel Metin Karart:", "EN": "Custom Redact Text:"},
            "lbl_redact_color": {"TR": "Karartma Rengi:", "EN": "Redaction Color:"},
            "opt_transparent": {"TR": "Şeffaf (Sadece Sil)", "EN": "Transparent (Delete Only)"},
            "lbl_macro_pages": {"TR": "Uygulanacak Sayfalar (Örn: Tümü veya 1-3,5):", "EN": "Target Pages (e.g., All or 1-3,5):"},
            "lbl_bates_repeat": {"TR": "Numarayı Tekrar Et (Sayfa):", "EN": "Repeat Number (Per Pages):"},
            "lbl_bates_style": {"TR": "Yazı Tipi & Stil:", "EN": "Font & Style:"},
            "lbl_position": {"TR": "Konum:", "EN": "Position:"},
            "lbl_encryption": {"TR": "PDF Şifreleme (Boş=Şifresiz):", "EN": "Encrypt PDF (Empty=No):"},
            "lbl_compression_lvl": {"TR": "UYAP Sıkıştırma (DPI):", "EN": "UYAP Compression (DPI):"},

            # --- GELİŞMİŞ MAKRO & GÜVENLİK ---
            "lbl_pw_1": {"TR": "Şifre Belirle:", "EN": "Set Password:"},
            "lbl_pw_2": {"TR": "Şifre (Tekrar):", "EN": "Password (Repeat):"},
            "lbl_bates_custom_group": {"TR": "Özel Gruplama (Örn: 1-3=EK-1, 4-9=EK-2):", "EN": "Custom Group (e.g. 1-3=APP-1, 4-9=APP-2):"},

            # --- GELİŞMİŞ MAKRO & GÜVENLİK (i18n Tamamlama) ---
            "lbl_kvkk_regex_title": {"TR": "Otomatik Karartma (Regex):", "EN": "Auto Redact (Regex):"},
            "chk_kvkk_tc": {"TR": "11 Haneli (T.C.)", "EN": "11-Digit (TR ID)"},
            "chk_kvkk_id": {"TR": "Genel Kimlik No (ID)", "EN": "Generic ID No"},
            "chk_kvkk_passport": {"TR": "Pasaport No", "EN": "Passport No"},
            "chk_kvkk_iban": {"TR": "IBAN", "EN": "IBAN"},
            "chk_kvkk_phone": {"TR": "Telefon No", "EN": "Phone No"},
            "chk_kvkk_nums": {"TR": "Tüm Rakamlar", "EN": "All Numbers"},
            "opt_comp_none": {"TR": "Sıkıştırma Yok", "EN": "No Compression"},
            "opt_comp_mid": {"TR": "Orta Kalite (150 DPI)", "EN": "Medium Quality (150 DPI)"},
            "opt_comp_max": {"TR": "Maksimum Sıkıştırma (72 DPI)", "EN": "Max Compression (72 DPI)"},
            "lbl_bates_enable": {"TR": "Bates Numaralandırmayı Aktifleştir", "EN": "Enable Bates Numbering"},
            "lbl_bates_start_no": {"TR": "Başlangıç No:", "EN": "Start No:"},
            "opt_bates_z0": {"TR": "Dolgu Yok (1)", "EN": "No Padding (1)"},
            "opt_bates_z2": {"TR": "2 Hane (01)", "EN": "2 Digits (01)"},
            "opt_bates_z3": {"TR": "3 Hane (001)", "EN": "3 Digits (001)"},
            "opt_bates_z4": {"TR": "4 Hane (0001)", "EN": "4 Digits (0001)"},
            "lbl_stamp_title": {"TR": "Hazır veya Özel Mühür Seçimi:", "EN": "Ready or Custom Stamp Selection:"},
            "lbl_stamp_scale": {"TR": "Boyutlandırma (Ölçek):", "EN": "Scaling (Size):"},
            "btn_upload_img": {"TR": "Görsel Seç (.png/.jpg)", "EN": "Select Image (.png/.jpg)"},
            "opt_pos_tl": {"TR": "Sol Üst", "EN": "Top Left"},
            "opt_pos_tc": {"TR": "Orta Üst", "EN": "Top Center"},
            "opt_pos_tr": {"TR": "Sağ Üst", "EN": "Top Right"},
            "opt_pos_ml": {"TR": "Sol Orta", "EN": "Middle Left"},
            "opt_pos_center": {"TR": "Merkez", "EN": "Center"},
            "opt_pos_mr": {"TR": "Sağ Orta", "EN": "Middle Right"},
            "opt_pos_bl": {"TR": "Sol Alt", "EN": "Bottom Left"},
            "opt_pos_bc": {"TR": "Orta Alt", "EN": "Bottom Center"},
            "opt_pos_br": {"TR": "Sağ Alt", "EN": "Bottom Right"},
            "opt_pos_custom": {"TR": "Özel (X,Y)", "EN": "Custom (X,Y)"},
            "lbl_x_pct": {"TR": "X (%):", "EN": "X (%):"},
            "lbl_y_pct": {"TR": "Y (%):", "EN": "Y (%):"},
            "msg_macro_success": {"TR": "Zincirleme makro işlemleri başarıyla tamamlandı!", "EN": "Macro chain operations completed successfully!"},
            "btn_open_file_direct": {"TR": "Dosyayı Aç", "EN": "Open File"},
            "guide_macro_title": {"TR": "ZİNCİRLEME OTOMASYON REHBERİ", "EN": "CHAIN AUTOMATION GUIDE"},
            "guide_macro_text": {
                "TR": "📌 KVKK & GÜVENLİK:\n- T.C. Kimlik, Uluslararası ID, Pasaport, IBAN, Telefon veya serbest yazdığınız bir metni otomatik bulur ve siler.\n- UYAP sıkıştırması belge çözünürlüğünü düşürerek MB boyutunu azaltır.\n\n📌 BATES NUMARALANDIRMA:\n- 'Özel Gruplama' kutusuna '1-3=EK-1, 4-9=EK-2' yazarsanız normal saymayı iptal edip sayfalara özel grup atar.\n\n📌 X, Y KOORDİNAT SİSTEMİ:\n- Konumu 'Özel (X,Y)' seçtiğinizde beliren çubuğu (slider) sağa sola çekerek numarayı veya kaşeyi milimetrik yerleştirebilirsiniz. (0=Tam Sol/Üst, 100=Tam Sağ/Alt)",
                "EN": "📌 SECURITY & REDACTION:\n- Automatically finds and redacts SSN, Generic ID, Passport, IBAN, Phone or custom text.\n- Compression reduces DPI to shrink file size (MB).\n\n📌 BATES NUMBERING:\n- If you write '1-3=APP-1, 4-9=APP-2' in 'Custom Grouping', it applies specific prefixes to those pages.\n\n📌 X,Y COORDINATES:\n- When 'Custom (X,Y)' is selected, you can use the sliders to place stamps/numbers with millimeter precision. (0=Top/Left, 100=Bottom/Right)"
            },

            # --- PDF OLUŞTURUCU (STUDIO) ---
            "btn_create_pdf": {"TR": "PDF Oluştur", "EN": "Create PDF "},
            "lbl_studio_tools": {"TR": "🛠️ Araç Kutusu", "EN": "🛠️ Toolbox"},
            "btn_add_text": {"TR": "📝 Metin Kutusu Ekle", "EN": "📝 Add Text Box"},
            "btn_add_rect": {"TR": "🟥 Dikdörtgen / Kare", "EN": "🟥 Rectangle / Square"},
            "btn_add_circle": {"TR": "⭕ Çember / Daire", "EN": "⭕ Circle / Oval"},
            "btn_add_triangle": {"TR": "🔺 Üçgen", "EN": "🔺 Triangle"},
            "btn_add_checkbox": {"TR": "☑️ Onay Kutusu (Form)", "EN": "☑️ Checkbox (Form)"},
            "lbl_properties": {"TR": "⚙️ Nesne Özellikleri", "EN": "⚙️ Object Properties"},
            "lbl_item_text": {"TR": "İçerik:", "EN": "Content:"},
            "lbl_item_size": {"TR": "Büyüklük:", "EN": "Size:"},
            "lbl_item_color": {"TR": "Renk:", "EN": "Color:"},
            "btn_save_pdf": {"TR": "💾 PDF Olarak Kaydet", "EN": "💾 Save as PDF"},
            "lbl_templates": {"TR": "Hazır Şablonlar:", "EN": "Templates:"},
            "opt_blank_a4": {"TR": "Boş A4 Kağıdı", "EN": "Blank A4 Paper"},
            "opt_template_dilekce": {"TR": "Dilekçe Şablonu", "EN": "Petition Template"},
            "opt_template_ik": {"TR": "İşe Alım Kartı (İK)", "EN": "Recruitment Card (HR)"},
            "msg_saved_studio": {"TR": "Tasarımınız başarıyla PDF olarak üretildi!", "EN": "Your design was successfully generated as a PDF!"},

            # --- PDF STÜDYO (V10 EKLENTİLERİ) ---
            "btn_create_pdf": {"TR": "PDF Oluştur", "EN": "Create PDF"},
            "lbl_studio_tools": {"TR": "🛠️ Araç Kutusu", "EN": "🛠️ Toolbox"},
            "btn_add_text": {"TR": "📝 Metin (Paragraf)", "EN": "📝 Text (Paragraph)"},
            "btn_add_rect": {"TR": "🟥 Dikdörtgen", "EN": "🟥 Rectangle"},
            "btn_add_circle": {"TR": "⭕ Daire / Oval", "EN": "⭕ Circle / Oval"},
            "btn_add_triangle": {"TR": "🔺 Üçgen", "EN": "🔺 Triangle"},
            "btn_add_table": {"TR": "▦ Tablo Ekle", "EN": "▦ Add Table"},
            "btn_add_image": {"TR": "🖼️ Görsel / Logo", "EN": "🖼️ Image / Logo"},
            "btn_add_checkbox": {"TR": "☑️ Onay Kutusu", "EN": "☑️ Checkbox"},
            "lbl_bg_color": {"TR": "Kağıt Arka Planı:", "EN": "Paper Background:"},
            "lbl_properties": {"TR": "⚙️ Nesne Özellikleri", "EN": "⚙️ Object Properties"},
            "lbl_item_text": {"TR": "İçerik (Alt satır için Enter):", "EN": "Content (Enter for newline):"},
            "lbl_item_size": {"TR": "Büyüklük / Genişlik:", "EN": "Size / Width:"},
            "lbl_item_color": {"TR": "Dış Renk:", "EN": "Outline Color:"},
            "lbl_item_fill": {"TR": "İç Dolgu:", "EN": "Fill Color:"},
            "lbl_font_style": {"TR": "Yazı Tipi & Stili:", "EN": "Font & Style:"},
            "btn_save_pdf": {"TR": "💾 PDF Olarak Üret", "EN": "💾 Generate PDF"},
            "msg_saved_studio": {"TR": "Tasarımınız başarıyla PDF olarak üretildi!", "EN": "Your design was successfully generated as a PDF!"},
            "btn_guide_studio": {"TR": "💡 Kılavuz", "EN": "💡 Guide"},
            "msg_guide_studio": {
                "TR": "📌 HİZALAMA: Nesneyi sayfanın ortasına sürüklediğinizde kırmızı kılavuz çizgisi belirir.\n📌 KONTROLLER: Nesneleri klavyeden 'Delete' tuşu ile silebilirsiniz.\n📌 GERİ/İLERİ: Hatalı işlemleri Ctrl+Z (Geri) ve Ctrl+Y (İleri) ile düzeltebilirsiniz.\n📌 TABLOLAR: Tablo eklerken Satır ve Sütun sayısını belirleyebilirsiniz.",
                "EN": "📌 ALIGNMENT: A red snap-line appears when you drag items to the center.\n📌 CONTROLS: Use the 'Delete' key to remove selected items.\n📌 UNDO/REDO: Use Ctrl+Z (Undo) and Ctrl+Y (Redo) to fix mistakes.\n📌 TABLES: Specify Row and Column counts when adding a table."
            },

            # --- PDF STÜDYO (V11 EKLENTİLERİ) ---
            "btn_create_pdf": {"TR": "PDF Oluştur", "EN": "Create PDF"},
            "lbl_studio_tools": {"TR": "🛠️ Araç Kutusu", "EN": "🛠️ Toolbox"},
            "btn_add_text": {"TR": "📝 Metin (Paragraf)", "EN": "📝 Text (Paragraph)"},
            "btn_add_rect": {"TR": "🟥 Dikdörtgen", "EN": "🟥 Rectangle"},
            "btn_add_circle": {"TR": "⭕ Daire / Oval", "EN": "⭕ Circle / Oval"},
            "btn_add_triangle": {"TR": "🔺 Üçgen", "EN": "🔺 Triangle"},
            "btn_add_table": {"TR": "▦ Tablo Ekle", "EN": "▦ Add Table"},
            "btn_add_image": {"TR": "🖼️ Görsel / Logo", "EN": "🖼️ Image / Logo"},
            "btn_add_checkbox": {"TR": "☑️ Onay Kutusu", "EN": "☑️ Checkbox"},
            "btn_add_whiteout": {"TR": "🩹 Tipeks / Düzeltici", "EN": "🩹 Whiteout / Eraser"},
            "lbl_bg_color": {"TR": "Kağıt Arka Planı:", "EN": "Paper Background:"},
            "btn_custom_color": {"TR": "🎨 Özel Renk Seç", "EN": "🎨 Custom Color"},
            "lbl_properties": {"TR": "⚙️ Nesne Özellikleri", "EN": "⚙️ Object Properties"},
            "lbl_item_text": {"TR": "İçerik (Alt satır için Enter):", "EN": "Content (Enter for newline):"},
            "lbl_item_size": {"TR": "Büyüklük / Genişlik:", "EN": "Size / Width:"},
            "lbl_item_color": {"TR": "Dış Renk:", "EN": "Outline Color:"},
            "lbl_item_fill": {"TR": "İç Dolgu:", "EN": "Fill Color:"},
            "lbl_font_style": {"TR": "Yazı Tipi & Stili:", "EN": "Font & Style:"},
            "btn_save_pdf": {"TR": "💾 PDF Olarak Üret", "EN": "💾 Generate PDF"},
            "btn_import_pdf": {"TR": "📄 PDF İçe Aktar", "EN": "📄 Import PDF"},
            "msg_saved_studio": {"TR": "Tasarımınız başarıyla PDF olarak üretildi!", "EN": "Your design was successfully generated as a PDF!"},
            "btn_guide_studio": {"TR": "💡 Kılavuz", "EN": "💡 Guide"},
            "msg_guide_studio": {
                "TR": "📌 AMACIMIZ: Bu modül bir Word programı değildir. Kendi interaktif formlarınızı (mutabakat, İK formları), görsel delil panolarınızı veya tamamen özelleştirilmiş PDF tasarımlarınızı oluşturmanız için tasarlanmıştır.\n\n📌 SAYFALAR: Birden fazla sayfa ekleyebilir, dışarıdan PDF yükleyerek (arka plan olarak) üzerinde değişiklik yapabilirsiniz.\n\n📌 TİPEKS: İstemediğiniz alanları silmek için Araç Kutusu'ndaki 'Tipeks'i kullanarak o bölgeyi beyaz bir bantla kapatabilirsiniz.\n\n📌 KATMANLAR: Sağ paneldeki okları (Yukarı/Aşağı) kullanarak nesneleri birbirinin üstüne veya altına alabilirsiniz.",
                "EN": "📌 PURPOSE: This is not a Word clone. It is a visual studio for creating interactive forms, evidence boards, or custom PDFs.\n\n📌 PAGES & IMPORT: Add multiple pages or import an existing PDF to act as the background layer for editing.\n\n📌 WHITEOUT: Use the 'Whiteout' tool to hide unwanted areas or text on imported PDFs.\n\n📌 LAYERS: Use the Up/Down arrows in the properties panel to bring items forward or send them backward."
            },
            "btn_bring_forward": {"TR": "🔼 Öne Getir", "EN": "🔼 Bring Forward"},
            "btn_send_backward": {"TR": "🔽 Arkaya Gönder", "EN": "🔽 Send Backward"},

            # --- PDF STÜDYO (V12 EKLENTİLERİ) ---
            "btn_add_square": {"TR": "🟦 Kare", "EN": "🟦 Square"},
            "btn_new_page": {"TR": "+ Yeni Sayfa", "EN": "+ New Page"},
            "lbl_page_counter": {"TR": "Sayfa {0} / {1}", "EN": "Page {0} / {1}"},
            "msg_select_object": {"TR": "Tuvalden bir nesne seçin.", "EN": "Select an object from the canvas."},
            "btn_undo": {"TR": "↩ Geri", "EN": "↩ Undo"},
            "btn_redo": {"TR": "↪ İleri", "EN": "↪ Redo"},
            "lbl_layers": {"TR": "📑 Katmanlar (Nesneler)", "EN": "📑 Layers (Objects)"},
            "lbl_item_width": {"TR": "Genişlik:", "EN": "Width:"},
            "lbl_item_height": {"TR": "Yükseklik:", "EN": "Height:"},
            "btn_open_file_direct": {"TR": "Dosyayı Aç", "EN": "Open File"},

            # --- PDF STÜDYO (V13 EKLENTİLERİ) ---
            "btn_add_line": {"TR": "➖ Çizgi", "EN": "➖ Line"},
            "btn_del_page": {"TR": "🗑️ Sayfayı Sil", "EN": "🗑️ Delete Page"},
            "item_text": {"TR": "Metin", "EN": "Text"},
            "item_rect": {"TR": "Dikdörtgen", "EN": "Rectangle"},
            "item_square": {"TR": "Kare", "EN": "Square"},
            "item_circle": {"TR": "Daire", "EN": "Circle"},
            "item_triangle": {"TR": "Üçgen", "EN": "Triangle"},
            "item_table": {"TR": "Tablo", "EN": "Table"},
            "item_image": {"TR": "Görsel", "EN": "Image"},
            "item_checkbox": {"TR": "Onay Kutusu", "EN": "Checkbox"},
            "item_whiteout": {"TR": "Tipeks", "EN": "Whiteout"},
            "item_line": {"TR": "Çizgi", "EN": "Line"},
            "btn_del_item": {"TR": "🗑️ Nesneyi Sil", "EN": "🗑️ Delete Item"},
            "opt_underline": {"TR": "Altı Çizgili (U)", "EN": "Underline (U)"},
            "opt_strike": {"TR": "Üstü Çizgili (S)", "EN": "Strikethrough (S)"},

            # --- PDF STÜDYO (V14 EKLENTİLERİ - İKONSUZ) ---
            "btn_add_text": {"TR": "Metin (Paragraf)", "EN": "Text (Paragraph)"},
            "btn_add_rect": {"TR": "Dikdörtgen", "EN": "Rectangle"},
            "btn_add_square": {"TR": "Kare", "EN": "Square"},
            "btn_add_circle": {"TR": "Daire / Oval", "EN": "Circle / Oval"},
            "btn_add_triangle": {"TR": "Üçgen", "EN": "Triangle"},
            "btn_add_line": {"TR": "Çizgi", "EN": "Line"},
            "btn_add_table": {"TR": "Tablo Ekle", "EN": "Add Table"},
            "btn_add_image": {"TR": "Görsel / Logo", "EN": "Image / Logo"},
            "btn_add_checkbox": {"TR": "Onay Kutusu", "EN": "Checkbox"},
            "btn_add_whiteout": {"TR": "Tipeks / Düzeltici", "EN": "Whiteout / Eraser"},
            "btn_del_page": {"TR": "Sayfayı Sil", "EN": "Delete Page"},
            "item_text": {"TR": "Metin", "EN": "Text"},
            "item_rect": {"TR": "Dikdörtgen", "EN": "Rectangle"},
            "item_square": {"TR": "Kare", "EN": "Square"},
            "item_circle": {"TR": "Daire", "EN": "Circle"},
            "item_triangle": {"TR": "Üçgen", "EN": "Triangle"},
            "item_table": {"TR": "Tablo", "EN": "Table"},
            "item_image": {"TR": "Görsel", "EN": "Image"},
            "item_checkbox": {"TR": "Onay Kutusu", "EN": "Checkbox"},
            "item_whiteout": {"TR": "Tipeks", "EN": "Whiteout"},
            "item_line": {"TR": "Çizgi", "EN": "Line"},
            "btn_del_item": {"TR": "Nesneyi Sil", "EN": "Delete Item"},

            # --- PDF STÜDYO (V15 - SON RÖTUŞLAR) ---
            "btn_change_out_color": {"TR": "Dış Rengi Değiştir", "EN": "Change Outline Color"},
            "btn_change_in_color": {"TR": "İç Rengi Değiştir", "EN": "Change Fill Color"},
            "btn_make_transp": {"TR": "Şeffaf Yap", "EN": "Make Transparent"},

            "msg_cannot_delete_last_page": {"TR": "Son sayfayı silemezsiniz!", "EN": "You cannot delete the last page!"},

            # --- HAKKINDA (ABOUT) SAYFASI ---
            "about_mission": {"TR": "Modern ve Güvenli Kurumsal Çözümler", "EN": "Modern and Secure Corporate Solutions"},
            "lbl_version": {"TR": "Docsas v1.0", "EN": "Docsas v1.0"},
            "lbl_update_info": {"TR": "Sürümünüz güncel. En iyi güvenlik yamalarına sahipsiniz.", "EN": "Your version is up to date. You have the latest security patches."},
            "btn_check_update": {"TR": "Güncellemeleri Denetle", "EN": "Check for Updates"},
            "update_dialog_title": {"TR": "Yeni Sürüm Mevcut", "EN": "Update Available"},
            "update_dialog_msg": {
                "TR": "Docsas için yeni bir güncelleme bulundu!\n\nMevcut Sürümünüz: v{}\nEn Son Sürüm: v{}\n\nYeni sürümü indirmek için indirme sayfasına gitmek ister misiniz?", 
                "EN": "A new version of Docsas is available!\n\nYour Version: v{}\nLatest Version: v{}\n\nWould you like to go to the download page?"
            },
            "update_latest_title": {"TR": "Sistem Güncel", "EN": "Up to Date"},
            "update_latest_msg": {
                "TR": "Docsas yazılımınız zaten en son sürümde (v{}).\nEk bir güncelleme yapmanıza gerek yoktur.", 
                "EN": "Your Docsas software is already up to date (v{}).\nNo action required."
            },
            "update_error_title": {"TR": "Bağlantı Hatası", "EN": "Connection Error"},
            "update_error_msg": {
                "TR": "Güncelleme sunucusuna erişilemedi.\nŞu anda çevrimdışı (offline) moddasınız veya internet bağlantınız yok.", 
                "EN": "Could not reach the update server.\nYou are currently offline or have no internet connection."
            },
            "lbl_security_title": {"TR": "%100 Yerel Veri Güvenliği (Çevrimdışı)", "EN": "100% Local Data Security (Offline)"},
            "lbl_security_desc": {"TR": "Bu yazılım hiçbir verinizi internete, sunuculara veya yapay zeka bulutlarına yüklemez. Tüm belgeleriniz sadece sizin cihazınızda işlenir. Tam bir kapalı devre sistemdir.", "EN": "This software never uploads your data to the internet, servers, or AI clouds. All documents are processed solely on your device. It is a completely closed-loop system."},
            "desc_radu": {"TR": "Google Play'deki efsanevi strateji ve kart oyunumuz! Rakiplerinizi yenin ve liderlik tablosuna tırmanın.", "EN": "Our legendary strategy and card game on Google Play! Defeat your opponents and climb the leaderboard."},
            "desc_deutsch": {"TR": "Almanca öğrenmenin en eğlenceli ve interaktif yolu. Kelime hafızanızı test edin ve kendinizi geliştirin.", "EN": "The most fun and interactive way to learn German. Test your vocabulary and improve yourself."},
            "btn_visit_googleplay": {"TR": "Google Play'de İncele", "EN": "Visit on Google Play"},
            "btn_contact": {"TR": "✉️ Geliştiriciyle İletişim", "EN": "✉️ Contact Developer"},
            "btn_web_site": {"TR": "🌐 Resmi Web Sitemiz", "EN": "🌐 Official Website"},
            "btn_privacy": {"TR": "📄 Gizlilik Politikası", "EN": "📄 Privacy Policy"},
            "footer_text": {"TR": "Docsas © 2026. Tüm Hakları Saklıdır.", "EN": "Docsas © 2026. All Rights Reserved."},
            "privacy_title": {"TR": "Gizlilik Politikası ve Kullanım Şartları", "EN": "Privacy Policy & Terms of Use"},
            "privacy_text": {"TR": "1. Veri Güvenliği: Docsas, hiçbir kullanıcının kişisel belgesini veya girdiği veriyi uzak bir sunucuya göndermez.\n\n2. Çevrimdışı Kullanım: Program tamamen offline çalışacak şekilde tasarlanmıştır.\n\n3. Kullanım Hakları: Bu program Kitkars-Radu Mobile Studios tarafından geliştirilmiştir...", "EN": "1. Data Security: Docsas does not transmit any user's personal documents or entered data to a remote server.\n\n2. Offline Usage: The program is designed to work completely offline.\n\n3. Usage Rights: This software is developed by Kitkars-Radu Mobile Studios..."},



            # --- GELİŞMİŞ PDF İŞLEMLERİ YENİ EKLENENLER ---
            "btn_sel_odd": {"TR": "Tekleri Seç", "EN": "Select Odd"},
            "btn_sel_even": {"TR": "Çiftleri Seç", "EN": "Select Even"},
            "btn_grayscale": {"TR": "Siyah-Beyaz Yap", "EN": "Make Grayscale"},
            "lbl_paper_size": {"TR": "Hedef Kağıt Formatı", "EN": "Target Paper Size"},
            "opt_paper_orig": {"TR": "Orijinal Boyut", "EN": "Original Size"},
            "lbl_alignment": {"TR": "Hizalama (Sayfa İçi)", "EN": "Page Alignment"},
            "opt_align_center": {"TR": "Tam Merkeze", "EN": "Center"},
            "opt_align_topleft": {"TR": "Sol Üste (Zımba Payı)", "EN": "Top-Left"},
            "chk_auto_crop": {"TR": "Akıllı Kırpma (Boşlukları Sil)", "EN": "Auto-Crop (Remove Whitespace)"},
            "lbl_modal_settings": {"TR": "Sayfaya Özel Ayarlar", "EN": "Per-Page Settings"},
            "chk_page_gray": {"TR": "Bu sayfayı Siyah-Beyaz yap", "EN": "Make this page Grayscale"},

            # --- GELİŞMİŞ PDF İŞLEMLERİ (KIRPMA VE KAĞIT) ---
            "btn_sel_odd": {"TR": "Tekleri Seç", "EN": "Select Odd"},
            "btn_sel_even": {"TR": "Çiftleri Seç", "EN": "Select Even"},
            "btn_grayscale": {"TR": "Siyah-Beyaz Yap", "EN": "Make Grayscale"},
            "lbl_paper_size": {"TR": "Hedef Kağıt Formatı", "EN": "Target Paper Size"},
            "opt_paper_orig": {"TR": "Orijinal Boyut", "EN": "Original Size"},
            "lbl_alignment": {"TR": "Hizalama (Sayfa İçi)", "EN": "Page Alignment"},
            "opt_align_center": {"TR": "Tam Merkeze", "EN": "Center"},
            "opt_align_topleft": {"TR": "Sol Üste (Zımba Payı)", "EN": "Top-Left"},
            "chk_auto_crop": {"TR": "Akıllı Kırpma (Boşlukları Sil)", "EN": "Auto-Crop (Remove Whitespace)"},
            "lbl_modal_settings": {"TR": "Sayfaya Özel Ayarlar", "EN": "Per-Page Settings"},
            "chk_page_gray": {"TR": "Bu sayfayı Siyah-Beyaz yap", "EN": "Make this page Grayscale"},
            "crop_editor_title": {"TR": "Görsel Kırpma Editörü / Crop Editor", "EN": "Visual Crop Editor"},
            "crop_editor_inst": {"TR": "Kenarlardaki yeşil çizgileri sürükleyerek kırpma alanını belirleyin:", "EN": "Drag the green borders to define the crop area:"},
            "btn_crop_apply": {"TR": "Seçilen Alanı Kırp", "EN": "Crop Selected Area"},
            "btn_reset": {"TR": "Sıfırla", "EN": "Reset"},

            "btn_desel_odd": {"TR": "Tekleri Bırak", "EN": "Deselect Odd"},
            "btn_desel_even": {"TR": "Çiftleri Bırak", "EN": "Deselect Even"},

            # --- PDF İŞLEMLERİ: KIRPMA VE OPTİMİZASYON ---
            "btn_desel_odd": {"TR": "Tekleri Bırak", "EN": "Deselect Odd"},
            "btn_desel_even": {"TR": "Çiftleri Bırak", "EN": "Deselect Even"},
            "crop_mode_title": {"TR": "Kırpma Modu:", "EN": "Crop Mode:"},
            "opt_mode_shrink": {"TR": "Alanı Kes (Sayfayı Küçült)", "EN": "Cut Area (Shrink Page)"},
            "opt_mode_mask": {"TR": "Dışını Boya (Sayfa Boyutu Korunur)", "EN": "Mask Outside (Keep Page Size)"},
            "opt_mask_white": {"TR": "Beyaz ile Kapat", "EN": "Mask with White"},
            "opt_mask_black": {"TR": "Siyah ile Kapat", "EN": "Mask with Black"},

            # --- PDF İŞLEMLERİ (KIRPMA GÜNCELLEMESİ) ---
            "btn_zoom_in_text": {"TR": "Yakınlaştır", "EN": "Zoom In"},
            "btn_zoom_out_text": {"TR": "Uzaklaştır", "EN": "Zoom Out"},
            "btn_fit": {"TR": "Merkezle", "EN": "Fit"},

            # --- PDF İŞLEMLERİ (KENAR BOŞLUĞU) ---
            "lbl_margin": {"TR": "Kenar Boşluğu (%)", "EN": "Margin Padding (%)"},

            # --- PDF İŞLEMLERİ (HIZLANDIRMA GÜNCELLEMESİ) ---
            "msg_select_to_gray": {"TR": "Lütfen Siyah-Beyaz yapılacak sayfaları seçin.", "EN": "Please select pages to make grayscale."},
            "lbl_margin": {"TR": "Kenar Boşluğu (Margin)", "EN": "Margin Padding"},

            "msg_layout_info": {
                "TR": "💡 İpucu: Word çıktılarında yazılar sığmazsa Word'den Kenar Boşluklarını 'Dar' yapın. HTML çıktıları tarayıcıda otomatik A4 boyutunda ortalanır.",
                "EN": "💡 Tip: If text overflows in Word, set Page Margins to 'Narrow'. HTML outputs are automatically centered in A4 format."
            },

            "privacy_title": {"TR": "KULLANIM ŞARTLARI VE GİZLİLİK SÖZLEŞMESİ", "EN": "TERMS OF USE AND PRIVACY POLICY"},
            "privacy_text": {
                "TR": "KITKARS-RADU MOBILE STUDIOS\nDOCSAS KULLANIM ŞARTLARI VE GİZLİLİK SÖZLEŞMESİ\n\n1. TARAFLAR VE SÖZLEŞMENİN KONUSU\nİşbu Kullanım Şartları ve Gizlilik Sözleşmesi (“Sözleşme”), Docsas uygulamasını (“Uygulama”) kullanan gerçek veya tüzel kişi (“Kullanıcı”) ile uygulamanın tüm fikri ve ticari haklarına sahip olan Kitkars-Radu Mobile Studios (“Şirket”) arasında akdedilmiştir. Bu sözleşme; uygulamanın kullanım koşullarını, veri güvenliği prensiplerini, tarafların hak ve yükümlülüklerini, fikri mülkiyet haklarını ve sorumluluk sınırlarını düzenlemektedir. Kullanıcı, uygulamayı indirerek, yükleyerek, erişim sağlayarak veya kullanarak işbu sözleşmenin tüm hükümlerini okuduğunu, anladığını ve kabul ettiğini beyan eder.\n\n2. ÇEVRİMDIŞI ÇALIŞMA PRENSİBİ\nDocsas, kullanıcı gizliliğini esas alan tamamen çevrimdışı (offline) bir mimari ile geliştirilmiştir. Uygulama kapsamında yüklenen PDF, Word, Excel, görsel veya diğer tüm belgeler yalnızca kullanıcının kendi cihazında işlenir. Belgeler hiçbir şekilde harici sunuculara, bulut sistemlerine, üçüncü taraf veri merkezlerine veya uzak depolama hizmetlerine aktarılmaz. Uygulama; internet bağlantısına ihtiyaç duymaksızın belge düzenleme, sıkıştırma, dönüştürme, OCR, filigran ekleme, şifreleme ve benzeri işlemleri doğrudan cihaz üzerinde gerçekleştirir. Şirket, kullanıcı belgelerine erişim sağlamaz, belgeleri görüntülemez, analiz etmez, depolamaz veya üçüncü taraflarla paylaşmaz.\n\n3. VERİ GÜVENLİĞİ VE YEREL VERİ İŞLEME\nDocsas içerisinde gerçekleştirilen tüm işlemler yalnızca kullanıcının cihazındaki yerel donanım kaynakları kullanılarak gerçekleştirilir. Belgeler uygulama sunucularına gönderilmediği için kullanıcı verileri üzerinde merkezi bir depolama veya uzaktan erişim mekanizması bulunmamaktadır. OCR işlemleri, PDF düzenleme süreçleri, belge birleştirme, sıkıştırma, parola koruması, filigran ekleme ve diğer tüm teknik işlemler cihazın işlemci (CPU), bellek (RAM) ve yerel depolama kaynakları üzerinde yürütülmektedir. Kullanıcı, cihaz güvenliğinin sağlanması, güçlü parola kullanımı, antivirüs yazılımlarının güncel tutulması, işletim sistemi güncellemelerinin yapılması ve önemli belgelerin düzenli olarak yedeklenmesi konularında bizzat sorumlu olduğunu kabul eder.\n\n4. GİZLİLİK POLİTİKASI\nDocsas, kullanıcı gizliliğini temel prensip olarak benimsemektedir. Uygulama, kullanıcıların belge içeriklerini toplamaz, saklamaz, analiz etmez veya reklam amaçlı işlemez. Bununla birlikte, uygulamanın kararlılığını artırmak ve teknik hataları tespit etmek amacıyla uygulama mağazaları veya işletim sistemi sağlayıcıları tarafından anonim teknik veriler (cihaz modeli, işletim sistemi sürümü, uygulama çökme raporları vb.) toplanabilir.\n\n5. KULLANICI YÜKÜMLÜLÜKLERİ\nKullanıcı, uygulamayı yürürlükte bulunan ulusal ve uluslararası mevzuata uygun şekilde kullanacağını kabul eder. Kullanıcı tarafından işlenen tüm belge, içerik ve dosyaların hukuki sorumluluğu tamamen kullanıcıya aittir. Kullanıcı; telif hakkı ihlali oluşturan, hukuka aykırı, zararlı, kişisel verilerin korunmasına aykırı veya üçüncü kişilerin haklarını ihlal eden içeriklerin işlenmesinden doğabilecek tüm sonuçlardan münhasıran sorumludur.\n\n6. FİKRİ MÜLKİYET HAKLARI\nDocsas uygulamasının tüm yazılım bileşenleri, kullanıcı arayüzleri, tasarımları, logoları, algoritmaları, kaynak kodları ve diğer tüm dijital unsurları Kitkars-Radu Mobile Studios’un münhasır mülkiyetindedir. Kullanıcı; uygulamayı izinsiz şekilde çoğaltamaz, dağıtamaz, kiralayamaz, alt lisans veremez, tersine mühendislik işlemlerine tabi tutamaz veya kaynak kodunu çözümlemeye yönelik girişimlerde bulunamaz.\n\n7. SORUMLULUĞUN SINIRLANDIRILMASI\nDocsas uygulaması mevcut haliyle (“as is”) sunulmaktadır. Şirket, uygulamanın kesintisiz veya hatasız çalışacağını garanti etmez. Veri kayıpları, donanımsal arızalar, kullanıcı hataları veya teknik müdahaleler sonucunda oluşabilecek zararlardan Şirket sorumlu tutulamaz. Kullanıcı, kritik belgelerin yedeklenmesinin kendi yükümlülüğü olduğunu kabul eder.\n\n8. ÜÇÜNCÜ TARAF HİZMETLER\nİlerleyen dönemlerde üçüncü taraf servisler sunulması halinde gerekli bilgilendirmeler ayrıca yapılacaktır.\n\n9. SÖZLEŞME DEĞİŞİKLİKLERİ\nŞirket, işbu sözleşme hükümlerini önceden bildirimde bulunmaksızın güncelleme hakkını saklı tutar.\n\n10. UYGULANACAK HUKUK VE YETKİ\nİşbu sözleşme Türkiye Cumhuriyeti hukukuna tabidir. Uyuşmazlıklarda Kayseri Mahkemeleri yetkilidir.\n\n11. İLETİŞİM\nE-posta: radugames58@gmail.com\n\n12. YÜRÜRLÜK\nKullanıcı, uygulamayı indirerek, kurarak veya kullanarak bu hükümleri tamamen kabul etmiş sayılır.",
                "EN": "KITKARS-RADU MOBILE STUDIOS\nDOCSAS TERMS OF USE AND PRIVACY POLICY\n\n1. PARTIES AND SUBJECT OF THE AGREEMENT\nThis Terms of Use and Privacy Agreement (“Agreement”) is concluded between the person (“User”) using the Docsas application and Kitkars-Radu Mobile Studios (“Company”), which holds all intellectual and commercial rights to the application. The User, by downloading or using the application, accepts all provisions of this Agreement.\n\n2. OFFLINE OPERATION PRINCIPLE\nDocsas is developed with a 100% offline architecture to prioritize user privacy. All uploaded documents are processed only on the user's device. Documents are never transmitted to external servers, cloud systems, or third-party data centers. All operations are performed locally.\n\n3. DATA SECURITY AND LOCAL PROCESSING\nAll operations are performed using the device's local hardware resources (CPU/RAM). The User is personally responsible for device security and backing up important documents.\n\n4. PRIVACY POLICY\nDocsas does not collect, store, or analyze document content. Anonymous technical data (device model, OS version, crash reports) may be collected by platform providers to improve application stability.\n\n5. USER OBLIGATIONS\nThe User commits to using the application in accordance with applicable laws. Legal responsibility for all processed content lies entirely with the User.\n\n6. INTELLECTUAL PROPERTY RIGHTS\nAll software components, designs, and source codes are the property of Kitkars-Radu Mobile Studios. Reverse engineering or unauthorized distribution is prohibited.\n\n7. LIMITATION OF LIABILITY\nThe application is provided 'as is'. The Company is not responsible for data loss, hardware malfunctions, or legal liabilities arising from illegal content processed by the User.\n\n8. THIRD-PARTY SERVICES\nUsers will be notified separately if any third-party services are introduced.\n\n9. CONTRACT MODIFICATIONS\nThe Company reserves the right to update this agreement without prior notice.\n\n10. GOVERNING LAW AND JURISDICTION\nThis agreement is subject to the laws of the Republic of Turkey. Kayseri Courts have jurisdiction over any disputes.\n\n11. CONTACT\nEmail: radugames58@gmail.com\n\n12. EFFECTIVENESS\nBy downloading, installing, or using the application, the User is deemed to have fully accepted these Terms."
            },

            



        }

    def set_language(self, lang_code):
        self.current_lang = lang_code

    def get(self, key):
        # Kelime sözlükte bulunamazsa çökmesin diye anahtarın kendisini gösterir
        return self.texts.get(key, {}).get(self.current_lang, key)

# Tüm sayfalardan erişebilmek için global bir nesne yaratıyoruz
lang_manager = LanguageManager()

def get_text(key):
    return lang_manager.get(key)