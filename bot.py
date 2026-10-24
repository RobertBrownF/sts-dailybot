import json
import urllib.request
import urllib.error
import os
from datetime import datetime

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")

class STS2Random:
    def __init__(self, seed):
        self.seed = (seed ^ 0x5DEECE66D) & ((1 << 48) - 1)
    
    def next_int(self, n):
        self.seed = (self.seed * 0x5DEECE66D + 0xB) & ((1 << 48) - 1)
        bits = self.seed >> 17
        if (n & -n) == n:
            return int((n * bits) >> 31)
        bits = bits % n
        return int(bits)

def generate_daily_math(date_str, is_beta=False):
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        base_seed = date_obj.year * 10000 + date_obj.month * 100 + date_obj.day
        
        if is_beta:
            base_seed += 987654321
            
        rng = STS2Random(base_seed)
        
        # ИСПРАВЛЕНО: Строго 5 персонажей, доступных в Slay the Spire 2 (без Созерцательницы)
        characters = [
            " Ironclad (Бронированный)", 
            " Silent (Скрытная)", 
            " Defect (Дефект)", 
            " Regent (Регент)",
            "💀 Necobinder (Некробиндер)"
        ]
            
        char_index = rng.next_int(len(characters))
        chosen_char = characters[char_index]
        
        game_seed = (rng.next_int(1000000) * 123456789) - 456789123
        
        # Пул базовых модификаторов Slay the Spire 2
        all_mods = ["One Punch", "Uncertainty", "Lethality", "Draft", "Midas", "Insanity", "Specialized", "Terminal"]
        chosen_mods = []
        available_mods = all_mods.copy()
        
        for _ in range(3):
            if available_mods:
                idx = rng.next_int(len(available_mods))
                chosen_mods.append(available_mods.pop(idx))
                
        return {
            "character": chosen_char,
            "seed": game_seed,
            "modifiers": chosen_mods
        }
    except Exception as e:
        print(f"[ОШИБКА РАСЧЕТА]: {e}")
        return None

def send_to_discord():
    print("[СТАРТ] Автономный расчет дейлика под ростер StS2...")
    today = datetime.utcnow().strftime("%Y-%m-%d")
    
    main = generate_daily_math(today, is_beta=False)
    beta = generate_daily_math(today, is_beta=True)

    payload = {"embeds": []}

    if main:
        payload["embeds"].append({
            "title": f"⚔️ Slay the Spire 2: Дейлик на {today} (Основная ветка)",
            "color": 3066993,
            "fields": [
                {"name": "Класс персонажа", "value": str(main["character"]), "inline": True},
                {"name": "🌱 Сид (Seed)", "value": f"`{main['seed']}`", "inline": True},
                {"name": "✨ Модификаторы дня", "value": ", ".join(main["modifiers"]), "inline": False}
            ]
        })

    if beta:
        payload["embeds"].append({
            "title": f"🧪 Slay the Spire 2: Дейлик на {today} (БЕТА-ветка)",
            "color": 10181046,
            "fields": [
                {"name": "Класс персонажа", "value": str(beta["character"]), "inline": True},
                {"name": "🌱 Сид (Seed)", "value": f"`{beta['seed']}`", "inline": True},
                {"name": "✨ Модификаторы дня", "value": ", ".join(beta["modifiers"]), "inline": False}
            ]
        })

    if not DISCORD_WEBHOOK_URL:
        print("[ОШИБКА] Вебхук Дискорда пустой!")
        return

    jsondata = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        DISCORD_WEBHOOK_URL,
        data=jsondata,
        headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            print(f"[УСПЕХ] Доставлено в Discord! Код: {res.getcode()}")
    except Exception as e:
        print(f"[ОШИБКА ОТПРАВКИ]: {e}")

if __name__ == "__main__":
    send_to_discord()
