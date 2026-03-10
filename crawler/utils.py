import os
import json
import config


def ensure_folders():
    """Создает необходимые папки"""
    for folder in [config.HTML_DIR, config.IMG_DIR]:
        os.makedirs(folder, exist_ok=True)


def load_state():
    """Загружает состояние из JSON"""
    if os.path.exists(config.STATE_FILE):
        try:
            with open(config.STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: pass
    return {"pages": {}, "images": {}}


def save_state(state):
    """Сохраняет текущее состояние"""
    with open(config.STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=4, ensure_ascii=False)