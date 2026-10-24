import json
import urllib.request
import urllib.error

# ВСТАВЬ СВОЮ ССЫЛКУ МЕЖДУ КАВЫЧКАМИ НИЖЕ:
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1563585917363552417/tMoxLqmxT_b85qBDFF2uzlCt0oa-by-NyRIsHIW-GR8slgKiDeZPmmHSaY5c63wkYkTH"

def get_daily_data(is_beta=False):
    """
    Запрашивает данные из официальной таблицы лидеров Daily Climb.
    Для беты добавляет параметр ?channel=beta, как требует API Spire Codex.
    """
    base_url = "https://spire-codex.com"
    if is_beta:
        base_url += "&channel=beta"
        
    try:
        req = urllib.request.Request(base_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            # API возвращает список. Проверяем, что он пришел и в нем есть хотя бы один забег
            if isinstance(data, list) and len(data) > 0:
                run = data[0]
                return {
                    "character": run.get("character_chosen", "Неизвестно"),
                    "seed": run.get("seed", "Неизвестно"),
                    "modifiers": run.get("modifiers", [])
                }
    except Exception as e:
        print(f"Ошибка при запросе к Spire Codex (Beta={is_beta}): {e}")
    return None

def send_to_discord():
    # Собираем данные отдельно для Main и отдельно для Beta ветки
    main = get_daily_data(is_beta=False)
    beta = get_daily_data(is_beta=True)

    def format_mods(mods):
        if not mods:
            return "Стандартные"
        return ", ".join(str(m) for m in mods)

    payload = {"embeds": []}

    # Оформляем карточку для основной ветки (Main)
    if main:
        payload["embeds"].append({
            "title": "⚔️ Slay the Spire 2: Дейлик (Основная ветка)",
            "color": 3066993,  # Зеленый цвет
            "fields": [
                {"name": "👤 Персонаж", "value": str(main["character"]), "inline": True},
                {"name": "🌱 Сид (Seed)", "value": f"`{main['seed']}`", "inline": True},
                {"name": "✨ Модификаторы", "value": format_mods(main["modifiers"]), "inline": False}
            ]
        })

    # Оформляем карточку для бета-ветки (Beta)
    if beta:
        payload["embeds"].append({
            "title": "🧪 Slay the Spire 2: Дейлик (БЕТА-ветка)",
            "color": 10181046,  # Фиолетовый цвет
            "fields": [
                {"name": "👤 Персонаж", "value": str(beta["character"]), "inline": True},
                {"name": "🌱 Сид (Seed)", "value": f"`{beta['seed']}`", "inline": True},
                {"name": "✨ Модификаторы", "value": format_mods(beta["modifiers"]), "inline": False}
            ]
        })

    # Если база данных по каким-то причинам вернула пустоту по обеим веткам
    if not payload["embeds"]:
        print("База данных Spire Codex вернула пустой ответ. Нечего отправлять.")
        return

    # Кодируем наш готовый пакет данных в байты
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
            print(f"Данные ушли. Дискорд принял пакет с кодом: {res.getcode()}")
    except urllib.error.HTTPError as e:
        print(f"Дискорд отклонил пакет. Код ошибки: {e.code}")
        print(f"Причина отказа от Discord: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"Критическая ошибка сети при отправке: {e}")

if __name__ == "__main__":
    send_to_discord()
