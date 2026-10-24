import json
import urllib.request
import urllib.error
import re
import os
import ssl
from datetime import datetime

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")

# Словари для красивого и правильного перевода StS2
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

def get_real_daily_data(is_beta=False):
    # Обходим блокировку DNS Гитхаба: стучимся по IP Cloudflare-сервера сайта
    ip_url = "https://172.67.142"
    if is_beta:
        ip_url += "&channel=beta"
    else:
        ip_url += "&channel=stable"
        
    try:
        req = urllib.request.Request(
            ip_url, 
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'Host': 'spire-codex.com' # Передаем Host, чтобы сервер пустил нас
            }
        )
        # Отключаем проверку имени хоста SSL для работы по IP
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
            html = response.read().decode('utf-8')
            
            # Парсим реальные данные, зашитые в код страницы
            char_match = re.search(r'"character_chosen"\s*:\s*"([^"]+)"', html)
            seed_match = re.search(r'"seed"\s*:\s*"?(-?\d+)"?', html)
            mods_match = re.search(r'"modifiers"\s*:\s*(\[[^\]]*\])', html)
            asc_match = re.search(r'"ascension_level"\s*:\s*(\d+)', html)
            
            if char_match and seed_match:
                raw_char = char_match.group(1)
                
                modifiers = []
                if mods_match:
                    try:
                        modifiers = json.loads(mods_match.group(1))
                    except:
                        pass
                        
                asc_level = asc_match.group(1) if asc_match else "0"
                
                return {
                    "raw_char": raw_char,
                    "character": TRANSLATE_CHARS.get(raw_char, raw_char),
                    "seed": seed_match.group(1),
                    "modifiers": [TRANSLATE_MODS.get(m, m) for m in modifiers],
                    "ascension": asc_level
                }
    except Exception as e:
        print(f"[ЛОГ] Ошибка сбора данных по IP (Beta={is_beta}): {e}")
    return None

def send_to_discord():
    print("[СТАРТ] Сбор живых данных с серверов Spire Codex...")
    today = datetime.utcnow().strftime("%Y-%m-%d")
    main = get_real_daily_data(is_beta=False)
    beta = get_real_daily_data(is_beta=True)

    payload = {"embeds": []}

    if main:
        char_type = main["raw_char"]
        payload["embeds"].append({
            "title": f"⚔️ Slay the Spire 2: Дейлик на {today} (Основная ветка)",
            "color": CHAR_COLORS.get(char_type, 8421504),
            "fields": [
                {"name": "👤 Персонаж", "value": main["character"], "inline": True},
                {"name": "💀 Возвышение", "value": f"Наследник {main['ascension']}" if main['ascension'] != "0" else "0 (Обычная)", "inline": True},
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
                {"name": "💀 Возвышение", "value": f"Наследник {beta['ascension']}" if beta['ascension'] != "0" else "0 (Обычная)", "inline": True},
                {"name": "🌱 Сид (Seed)", "value": f"`{beta['seed']}`", "inline": True},
                {"name": "✨ Модификаторы дня", "value": ", ".join(beta["modifiers"]) if beta["modifiers"] else "Стандартные", "inline": False}
            ]
        })

    if not payload["embeds"]:
        print("[ОТМЕНА] Игровой сервер не отдал данные.")
        return

    if not DISCORD_WEBHOOK_URL:
        print("[ОШИБКА] Переменная DISCORD_WEBHOOK не найдена!")
        return

    jsondata = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        DISCORD_WEBHOOK_URL,
        data=jsondata,
        headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            print(f"[УСПЕХ] Доставлено в Discord! Статус: {res.getcode()}")
    except Exception as e:
        print(f"[ОШИБКА ОТПРАВКИ]: {e}")

if __name__ == "__main__":
    send_to_discord()
