import json
import urllib.request

# ВСТАВЬ СВОЮ ССЫЛКУ МЕЖДУ КАВЫЧКАМИ НИЖЕ:
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1563585917363552417/tMoxLqmxT_b85qBDFF2uzlCt0oa-by-NyRIsHIW-GR8slgKiDeZPmmHSaY5c63wkYkTH"

def get_runs():
    url = "https://spire-codex.com"
    try:
        # Устанавливаем жесткий тайм-аут 10 секунд, чтобы скрипт никогда не зависал
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Ошибка получения данных с API: {e}")
        return []

def parse_dailies():
    runs = get_runs()
    main_data = None
    beta_data = None

    for run in runs:
        if run.get("game_mode") == "daily" or run.get("is_daily") is True:
            version = run.get("version", "")
            
            run_info = {
                "character": run.get("character_chosen", "Неизвестно"),
                "seed": run.get("seed", "Неизвестно"),
                "modifiers": run.get("modifiers", [])
            }
            
            if "Beta" in version and not beta_data:
                beta_data = run_info
            elif "Beta" not in version and not main_data:
                main_data = run_info
                
        if main_data and beta_data:
            break

    return main_data, beta_data

def send_to_discord(main, beta):
    def format_mods(mods):
        return ", ".join(mods) if mods else "Стандартные"

    payload = {"embeds": []}

    if main:
        payload["embeds"].append({
            "title": "⚔️ Slay the Spire 2: Дейлик (Основная ветка)",
            "color": 3066993,
            "fields": [
                {"name": "👤 Персонаж", "value": str(main["character"]), "inline": True},
                {"name": "🌱 Сид (Seed)", "value": f"`{main['seed']}`", "inline": True},
                {"name": "✨ Модификаторы", "value": format_mods(main["modifiers"]), "inline": False}
            ]
        })

    if beta:
        payload["embeds"].append({
            "title": "🧪 Slay the Spire 2: Дейлик (БЕТА-ветка)",
            "color": 10181046,
            "fields": [
                {"name": "👤 Персонаж", "value": str(beta["character"]), "inline": True},
                {"name": "🌱 Сид (Seed)", "value": f"`{beta['seed']}`", "inline": True},
                {"name": "✨ Модификаторы", "value": format_mods(beta["modifiers"]), "inline": False}
            ]
        })

    if not payload["embeds"]:
        print("В базе Spire Codex пока нет сегодняшних дейликов.")
        return

    req = urllib.request.Request(
        DISCORD_WEBHOOK_URL,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
    )
    try:
        # Просто отправляем данные без лишних запутанных проверок кодов ответов
        with urllib.request.urlopen(req, timeout=10) as res:
            print("Скрипт успешно отработал!")
    except Exception as e:
        print(f"Ошибка отправки в Discord: {e}")

if __name__ == "__main__":
    main_branch, beta_branch = parse_dailies()
    send_to_discord(main_branch, beta_branch)
