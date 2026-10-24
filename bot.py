import json
import urllib.request
import urllib.error
import re
import os

# Робот автоматически возьмет ссылку из секретных настроек GitHub
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")

TRANSLATE_CHARS = {
    "IRONCLAD": "👤 Латоносец (Ironclad)",
    "SILENT": "👤 Безмолвная (Silent)",
    "DEFECT": "👤 Дефект (Defect)",
    "WATCHER": "👤 Созерцающая (Watcher)",
    "NECOBINDER": "💀 Призывательница (Necobinder)",
    "REGENT": "⏳ Наследник (Regent)"
}

def get_daily_from_web(is_beta=False):
    url = "https://spire-codex.com"
    if is_beta:
        url += "&channel=beta"
    else:
        url += "&channel=stable"
        
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8')
            
            char_match = re.search(r'"character_chosen"\s*:\s*"([^"]+)"', html)
            seed_match = re.search(r'"seed"\s*:\s*"?(-?\d+)"?', html)
            mods_match = re.search(r'"modifiers"\s*:\s*(\[[^\]]*\])', html)
            
            if char_match and seed_match:
                raw_char = char_match.group(1)
                seed = seed_match.group(1)
                
                modifiers = []
                if mods_match:
                    try:
                        modifiers = json.loads(mods_match.group(1))
                    except:
                        pass
                
                return {
                    "character": TRANSLATE_CHARS.get(raw_char, raw_char),
                    "seed": seed,
                    "modifiers": modifiers
                }
    except Exception as e:
        print(f"[ЛОГ] Не удалось прочитать страницу (Beta={is_beta}): {e}")
    return None

def send_to_discord():
    if not DISCORD_WEBHOOK_URL:
        print("[КРИТИЧЕСКАЯ ОШИБКА] Ссылка DISCORD_WEBHOOK не найдена в Секретах GitHub!")
        return

    print("[СТАРТ] Чтение страниц Spire Codex...")
    main = get_daily_from_web(is_beta=False)
    beta = get_daily_from_web(is_beta=True)

    def format_mods(mods):
        if not mods:
            return "Стандартные модификаторы"
        return ", ".join(str(m).replace('_', ' ') for m in mods)

    payload = {"embeds": []}

    if main:
        print(f"[УСПЕХ] Найдена основная ветка. Сид: {main['seed']}")
        payload["embeds"].append({
            "title": "⚔️ Slay the Spire 2: Дейлик (Основная ветка)",
            "color": 3066993,
            "fields": [
                {"name": "Класс персонажа", "value": str(main["character"]), "inline": True},
                {"name": "🌱 Сид (Seed)", "value": f"`{main['seed']}`", "inline": True},
                {"name": "✨ Модификаторы дня", "value": format_mods(main["modifiers"]), "inline": False}
            ]
        })

    if beta:
        print(f"[УСПЕХ] Найдена БЕТА-ветка. Сид: {beta['seed']}")
        payload["embeds"].append({
            "title": "🧪 Slay the Spire 2: Дейлик (БЕТА-ветка)",
            "color": 10181046,
            "fields": [
                {"name": "Класс персонажа", "value": str(beta["character"]), "inline": True},
                {"name": "🌱 Сид (Seed)", "value": f"`{beta['seed']}`", "inline": True},
                {"name": "✨ Модификаторы дня", "value": format_mods(beta["modifiers"]), "inline": False}
            ]
        })

    if not payload["embeds"]:
        print("[ОТМЕНА] Не удалось собрать данные со страницы сайта.")
        return

    jsondata = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        DISCORD_WEBHOOK_URL,
        data=jsondata,
        headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            print(f"[ДИСКОРД] Пакет успешно доставлен! Код: {res.getcode()}")
    except Exception as e:
        print(f"[ДИСКОРД ОШИБКА] {e}")

if __name__ == "__main__":
    send_to_discord()
