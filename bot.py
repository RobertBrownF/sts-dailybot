import json
import urllib.request
import urllib.error

# ВСТАВЬТЕ ВАШУ ССЫЛКУ МЕЖДУ КАВЫЧКАМИ НИЖЕ:
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1563585917363552417/tMoxLqmxT_b85qBDFF2uzlCt0oa-by-NyRIsHIW-GR8slgKiDeZPmmHSaY5c63wkYkTH"

def extract_run_details(raw_data):
    """Безопасно извлекает первый элемент из ответа API, как бы он ни был упакован"""
    run = None
    if isinstance(raw_data, list) and len(raw_data) > 0:
        run = raw_data[0]
    elif isinstance(raw_data, dict):
        # Если API упаковал список в объект типа {"items": [...]} или {"entries": [...]}
        for key in ["items", "entries", "runs", "leaderboard"]:
            if key in raw_data and isinstance(raw_data[key], list) and len(raw_data[key]) > 0:
                run = raw_data[key][0]
                break
        if not run and len(raw_data) > 0:
            # На крайний случай берем первый попавшийся элемент словаря, если там структура записей
            first_val = next(iter(raw_data.values()))
            if isinstance(first_val, list) and len(first_val) > 0:
                run = first_val[0]
                
    if run and isinstance(run, dict):
        return {
            "character": run.get("character_chosen", run.get("character", "Неизвестно")),
            "seed": run.get("seed", "Неизвестно"),
            "modifiers": run.get("modifiers", [])
        }
    return None

def get_daily_data(is_beta=False):
    base_url = "https://spire-codex.com"
    if is_beta:
        base_url += "&channel=beta"
        
    try:
        req = urllib.request.Request(base_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            body = response.read().decode('utf-8')
            print(f"[API Стриминг] Ответ сервера (Beta={is_beta}): {body[:300]}...") # Логируем ответ для отладки
            data = json.loads(body)
            return extract_run_details(data)
    except Exception as e:
        print(f"Ошибка при запросе к Spire Codex (Beta={is_beta}): {e}")
    return None

def send_to_discord():
    main = get_daily_data(is_beta=False)
    beta = get_daily_data(is_beta=True)

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
        print("Критическая ошибка: Обе ветки вернули пустоту. Проверьте логи сервера выше!")
        return

    jsondata = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        DISCORD_WEBHOOK_URL,
        data=jsondata,
        headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            print(f"Успешно доставили пакет в Discord! Код ответа сервера: {res.getcode()}")
    except urllib.error.HTTPError as e:
        print(f"Дискорд отклонил пакет. Код ошибки: {e.code}")
        print(f"Ответ Дискорда: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"Ошибка отправки: {e}")

if __name__ == "__main__":
    send_to_discord()
