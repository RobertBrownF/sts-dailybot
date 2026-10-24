import json
import urllib.request
import urllib.error
import os
from datetime import datetime

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")
API_KEY = os.environ.get("SPIRE_CODEX_API_KEY")

# Словари для правильного перевода и цветов StS2
TRANSLATE_CHARS = {
    "IRONCLAD": "Латоносец (Ironclad)",
    "SILENT": "Безмолвная (Silent)",
    "DEFECT": "Дефект (Defect)",
    "REGENT": "Наследник (Regent)",
    "NECOBINDER": "Призывающая (Necobinder)"
}

CHAR_COLORS = {
    "IRONCLAD": 12002594,   # Красный
    "SILENT": 3066993,      # Зеленый
    "DEFECT": 2259167,      # Синий
    "REGENT": 10181046,     # Фиолетовый
    "NECOBINDER": 7763574   # Серый
}

TRANSLATE_MODS = {
    "Flight": "Полет (Flight)",
    "Nightmares": "Ночные кошмары (Nightmares)",
    "Silent Cards": "Карты Безмолвной (Silent Cards)",
    "One Punch": "Один удар (One Punch)",
    "Lethality": "Летальность (Lethality)",
    "Draft": "Драфт (Draft)",
    "Midas": "Мидас (Midas)",
    "Insanity": "Безумие (Insanity)",
    "Specialized": "Специализация (Specialized)",
    "Terminal": "Терминал (Terminal)",
    "Uncertainty": "Неопределенность (Uncertainty)"
}

def get_daily_from_api(is_beta=False):
    # Прямой официальный эндпоинт базы данных Spire Codex
    url = "https://spire-codex.com"
    if is_beta:
        url += "&channel=beta"
    else:
        url += "&channel=stable"
        
    try:
        req = urllib.request.Request(url)
        # Передаем твой официальный токен авторизации и маскируем под браузер
        req.add_header('X-API-Key', API_KEY)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
        
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if isinstance(data, list) and len(data) > 0:
                for run in data:
                    if run.get("game_mode") == "daily" or run.get("is_daily") is True:
                        raw_char = run.get("character_chosen", "Неизвестно")
                        raw_mods = run.get("modifiers", [])
                        return {
                            "raw_char": raw_char,
                            "character": TRANSLATE_CHARS.get(raw_char, raw_char),
                            "seed": run.get("seed", "Неизвестно"),
                            "modifiers": [TRANSLATE_MODS.get(m, m) for m in raw_mods],
                            "ascension": run.get("ascension_level", "0")
                        }
    except Exception as e:
        print(f"[ЛОГ] Ошибка запроса к API (Beta={is_beta}): {e}")
    return None

def send_to_discord():
    if not API_KEY:
        print("[ОШИБКА] API-ключ SPIRE_CODEX_API_KEY не найден в Секретах GitHub!")
        return
        
    today = datetime.utcnow().strftime("%Y-%m-%d")
    main = get_daily_from_api(is_beta=False)
    beta = get_daily_from_api(is_beta=True)

    payload = {"embeds": []}

    if main:
        char_type = main["raw_char"]
        payload["embeds"].append({
            "title": f"⚔️ Slay the Spire 2: Дейлик на {today} (Основная ветка)",
            "color": CHAR_COLORS.get(char_type, 8421504),
            "fields": [
                {"name": "👤 Персонаж", "value": main["character"], "inline": True},
                {"name": "💀 Возвышение", "value": f"Наследник {main['ascension']}" if str(main['ascension']) != "0" else "0 (Обычная)", "inline": True},
                {"name": "🌱 Сид (Seed)", "value": f"`{main['seed']}`", "inline": True},
                {"name": "✨ Модификаторы дня", "value": ", ".join(main["modifiers"]) if main["modifiers"] else "Стандартные", "inline": False}
            ]
        })

    if beta:
        char_type = beta["raw_char"]
        payload["embeds"].append({
            "title": f"🧪 Slay the Spire 2: Дейлик на {today} (БЕТА-ветка)",
            "color": CHAR_COLORS.get(char_type, 8421504),
            "fields": [
                {"name": "👤 Персонаж", "value": beta["character"], "inline": True},
                {"name": "💀 Возвышение", "value": f"Наследник {beta['ascension']}" if str(beta['ascension']) != "0" else "0 (Обычная)", "inline": True},
                {"name": "🌱 Сид (Seed)", "value": f"`{beta['seed']}`", "inline": True},
                {"name": "✨ Модификаторы дня", "value": ", ".join(beta["modifiers"]) if beta["modifiers"] else "Стандартные", "inline": False}
            ]
        })

    if not payload["embeds"]:
        print("[ОТМЕНА] В базе данных пока нет сегодняшних дейликов.")
        return

    jsondata = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        DISCORD_WEBHOOK_URL,
        data=jsondata,
        headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            print(f"[УСПЕХ] Карточки доставлены! Код: {res.getcode()}")
    except Exception as e:
        print(f"[ОШИБКА ОТПРАВКИ В ДИСКОРД]: {e}")

if __name__ == "__main__":
    send_to_discord()
