import json
import os
from datetime import datetime

APP_DATA_DIR = os.path.join(os.getenv("APPDATA"), "Docsas")

if not os.path.exists(APP_DATA_DIR):
    os.makedirs(APP_DATA_DIR)

HISTORY_FILE = os.path.join(APP_DATA_DIR, "gecmis.json")

def add_history(icon, action_key, params, file_path):
    history = get_history()
    now = datetime.now().strftime("%d.%m.%Y, %H:%M")
    entry = {
        "icon": icon,
        "action": action_key,
        "params": params,
        "time": now,
        "path": file_path
    }
    history.insert(0, entry) 
    
    if len(history) > 30: # Limit 30'a çıkarıldı
        history = history[:30]
    
    save_history(history)

def remove_history_item(index): # Yeni silme fonksiyonu
    history = get_history()
    if 0 <= index < len(history):
        history.pop(index)
        save_history(history)

def save_history(history):
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print("History save error:", e)

def get_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print("History read error:", e)
        return []