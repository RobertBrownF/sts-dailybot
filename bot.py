import json
import urllib.request
import urllib.error

# ВСТАВЬТЕ ВАШУ ССЫЛКУ МЕЖДУ КАВЫЧКАМИ НИЖЕ:
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1563585917363552417/tMoxLqmxT_b85qBDFF2uzlCt0oa-by-NyRIsHIW-GR8slgKiDeZPmmHSaY5c63wkYkTH"

def get_runs():
    url = "https://spire-codex.com"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Ошибка получения данных с API Spire Codex: {e}")
        return []

def parse_dailies():
    runs = get_runs()
    main_data = None
    beta_data = None

    for run in runs:
        if not isinstance(run, dict):
            continue
            
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
        if not mods:
            return "Стандартные"
        return ", ".join(str(m) for m in mods)

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
        print("В логах Spire Codex пока нет свежих ежедневных забегов.")
        return

    jsondata = json.dumps(payload).encode('utf-8')
    
    req = urllib.request.Request(
        DISCORD_WEBHOOK_URL,
        data=jsondata,
        headers={
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0'
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            print(f"Ответ от Discord получен. Статус: {res.getcode()}")
            print("Сообщение успешно доставлено в чат!")
    except urllib.error.HTTPError as e:
        print(f"Discord отклонил запрос. Код ошибки: {e.code}")
        print(f"Ответ сервера Дискорд: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"Непредвиденная ошибка при отправке: {e}")

if __name__ == "__main__":
    main_branch, beta_branch = parse_dailies()
    send_to_discord(main_branch, beta_branch)
