import json
import urllib.request
import urllib.error
import re

# ВСТАВЬТЕ ВАШУ ССЫЛКУ МЕЖДУ КАВЫЧКАМИ НИЖЕ:
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1563585917363552417/tMoxLqmxT_b85qBDFF2uzlCt0oa-by-NyRIsHIW-GR8slgKiDeZPmmHSaY5c63wkYkTH"

TRANSLATE_CHARS = {
    "IRONCLAD": "👤 Бронированный (Ironclad)",
    "SILENT": "👤 Скрытная (Silent)",
    "DEFECT": "👤 Дефект (Defect)",
    "WATCHER": "👤 Созерцательница (Watcher)",
    "NECOBINDER": "💀 Некробиндер (Necobinder)",
    "REGENT": "⏳ Регент (Regent)"
}

def get_daily_from_web(is_beta=False):
    # Заходим на живые страницы сайта, где люди смотрят лидерборды
    url = "https://spire-codex.com"
    if is_beta:
        url += "&channel=beta"
    else:
        url += "&channel=stable"
        
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8')
            
            # Находим данные, которые сайт прячет внутри скриптов для отображения таблицы
            # Ищем подстроку с персонажем
            char_match = re.search(r'"character_chosen"\s*:\s*"([^"]+)"', html)
            seed_match = re.search(r'"seed"\s*:\s*"?(-?\d+)"?', html)
            mods_match = re.search(r'"modifiers"\s*:\s*(\[[^\]]*\])', html)
            
            if char_match and seed_match:
                raw_char = char_match.group(1)
                seed = seed_match.group(1)
                
                # Безопасно вытаскиваем массив модификаторов
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
