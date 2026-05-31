import random

ROLES = {
    "Mafia": {
        "emoji": "🔴",
        "team": "mafia",
        "desc": "Mafia a'zosi. Tun vaqtida jamoangiz bilan fuqarolarni o'ldirasiz. Kunduz o'zingizni yashiring!"
    },
    "Don": {
        "emoji": "⚫",
        "team": "mafia",
        "desc": "Mafia Don. Boshlig'siz. Detektiv sizni oddiy fuqaro deb ko'radi. Tun vaqtida jamoangiz bilan o'ldirasiz."
    },
    "Detektiv": {
        "emoji": "🟡",
        "team": "town",
        "desc": "Har tun bir o'yinchini tekshirasiz. Agar u Mafia bo'lsa, xabar olasiz. Don sizni aldaydi."
    },
    "Shifokor": {
        "emoji": "🟢",
        "team": "town",
        "desc": "Har tun bir o'yinchini davolaysiz. Agar o'sha kishi o'ldirilsa, u tirik qoladi. O'zingizni ham davolay olasiz."
    },
    "Sheriff": {
        "emoji": "🟠",
        "team": "town",
        "desc": "Tun vaqtida bir o'yinchini otasiz. Agar u Mafia bo'lsa — o'ladi. Agar fuqaro bo'lsa — o'zingiz o'lasiz!"
    },
    "Fahisha": {
        "emoji": "💜",
        "team": "town",
        "desc": "Tun vaqtida bir o'yinchini band qilasiz. U o'sha tun hech qanday harakat qila olmaydi."
    },
    "Jurnalist": {
        "emoji": "🔵",
        "team": "town",
        "desc": "Har tun bir o'yinchining aniq rolini bilib olasiz. Bu ma'lumotni faqat siz bilasiz."
    },
    "Maniak": {
        "emoji": "🩸",
        "team": "neutral",
        "desc": "Yolg'iz o'ynaysiz! Tun vaqtida biror o'yinchini o'ldirasiz. G'alaba uchun HAMMA o'lishi kerak."
    },
    "Farishta": {
        "emoji": "👼",
        "team": "town",
        "desc": "Bitta marta o'limdan qaytasiz! Siz o'ldirilsangiz, bir marta tirilasiz. Bu sirni hech kim bilmaydi."
    },
    "Portlovchi": {
        "emoji": "💣",
        "team": "town",
        "desc": "Kunduz ovoz bilan o'ldirilsangiz — yoningizda tasodifiy bir kishi ham o'ladi! Mafiani qo'rqiting."
    },
    "Joker": {
        "emoji": "🃏",
        "team": "neutral",
        "desc": "Har tun sizning rolingiz o'zgarib turadi. Kim bo'lishingizni bilmaysiz! Omadingizga ishoning."
    },
    "Agent": {
        "emoji": "🕵️",
        "team": "town",
        "desc": "Tun vaqtida ikkita o'yinchini tekshirasiz. Detektivdan kuchliroq, lekin e'tiborli bo'ling."
    },
    "Sehrgar": {
        "emoji": "🧙",
        "team": "town",
        "desc": "Tun vaqtida bir o'yinchining ovozini bloklaysiz. U ertangi kunda gapira olmaydi. (Sim-imitatsiya)"
    },
    "Qahramon": {
        "emoji": "⚔️",
        "team": "town",
        "desc": "Bir marta tun vaqtida bir o'yinchiga hujum qilasiz. Agar u Mafia bo'lsa — o'ladi. Fuqaro bo'lsa — siz o'lasiz."
    },
    "Fuqaro": {
        "emoji": "👤",
        "team": "town",
        "desc": "Oddiy fuqaro. Maxsus kuchingiz yo'q, lekin kunduz ovoz berib Mafiachini aniqlay olasiz!"
    },
}

def get_role_distribution(player_count: int) -> list:
    """Smart role distribution based on player count"""
    if player_count == 5:
        return ["Mafia", "Detektiv", "Shifokor", "Fuqaro", "Fuqaro"]
    elif player_count == 6:
        return ["Mafia", "Don", "Detektiv", "Shifokor", "Fuqaro", "Fuqaro"]
    elif player_count == 7:
        return ["Mafia", "Don", "Detektiv", "Shifokor", "Sheriff", "Fuqaro", "Fuqaro"]
    elif player_count == 8:
        return ["Mafia", "Don", "Detektiv", "Shifokor", "Sheriff", "Fahisha", "Fuqaro", "Fuqaro"]
    elif player_count == 9:
        return ["Mafia", "Don", "Mafia", "Detektiv", "Shifokor", "Sheriff", "Fahisha", "Fuqaro", "Fuqaro"]
    elif player_count == 10:
        return ["Mafia", "Don", "Mafia", "Detektiv", "Shifokor", "Sheriff", "Fahisha", "Jurnalist", "Fuqaro", "Fuqaro"]
    elif player_count == 11:
        return ["Mafia", "Don", "Mafia", "Detektiv", "Shifokor", "Sheriff", "Fahisha", "Jurnalist", "Maniak", "Fuqaro", "Fuqaro"]
    elif player_count == 12:
        return ["Mafia", "Don", "Mafia", "Detektiv", "Shifokor", "Sheriff", "Fahisha", "Jurnalist", "Maniak", "Farishta", "Fuqaro", "Fuqaro"]
    elif player_count == 13:
        return ["Mafia", "Don", "Mafia", "Mafia", "Detektiv", "Shifokor", "Sheriff", "Fahisha", "Jurnalist", "Maniak", "Farishta", "Portlovchi", "Fuqaro"]
    elif player_count == 14:
        return ["Mafia", "Don", "Mafia", "Mafia", "Detektiv", "Shifokor", "Sheriff", "Fahisha", "Jurnalist", "Maniak", "Farishta", "Portlovchi", "Agent", "Fuqaro"]
    else:  # 15+
        return ["Mafia", "Don", "Mafia", "Mafia", "Detektiv", "Shifokor", "Sheriff", "Fahisha",
                "Jurnalist", "Maniak", "Farishta", "Portlovchi", "Agent", "Sehrgar", "Qahramon"]


class MafiaGame:
    def __init__(self, chat_id: int, creator_id: int):
        self.chat_id = chat_id
        self.creator_id = creator_id
        self.players: dict = {}  # uid -> {name, role, alive, role_emoji, role_desc, ...}
        self.active = False
        self.phase = "lobby"
        self.day = 1
        self.votes: dict = {}
        self.night_actions: dict = {}

    def add_player(self, uid: int, name: str) -> str:
        if uid in self.players:
            return "already"
        self.players[uid] = {
            "name": name,
            "role": None,
            "role_emoji": "👤",
            "role_desc": "",
            "alive": True,
            "angel_used": False,
            "silenced": False,
        }
        return "added"

    def assign_roles(self):
        pids = list(self.players.keys())
        role_list = get_role_distribution(len(pids))
        # Pad with Fuqaro if more players than roles
        while len(role_list) < len(pids):
            role_list.append("Fuqaro")
        role_list = role_list[:len(pids)]
        random.shuffle(role_list)
        for pid, role in zip(pids, role_list):
            r = ROLES[role]
            self.players[pid]["role"] = role
            self.players[pid]["role_emoji"] = r["emoji"]
            self.players[pid]["role_desc"] = r["desc"]
            self.players[pid]["team"] = r["team"]

    def process_night(self) -> dict:
        results = {"killed": [], "healed": [], "messages": []}
        heal_target = None
        blocked = set()
        kill_target = None
        sheriff_kill = None
        maniac_kill = None
        hero_kill = None

        # Process blocks first (Fahisha)
        for uid, action in self.night_actions.items():
            if action["action"] == "block":
                blocked.add(action["target"])

        for uid, action in self.night_actions.items():
            if uid in blocked:
                continue
            act = action["action"]
            target = action["target"]

            if act == "kill":
                kill_target = target
            elif act == "heal":
                heal_target = target
            elif act == "shoot":
                # Sheriff shoots
                t_role = self.players[target].get("role", "")
                if t_role in ["Mafia", "Don"]:
                    sheriff_kill = target
                else:
                    # Sheriff dies instead
                    sheriff_kill = uid
                    results["messages"].append(f"🟠 Sheriff masum birini otdi va o'zi o'ldi!")
            elif act == "check":
                t_role = self.players[target].get("role", "")
                is_mafia = t_role in ["Mafia"]  # Don returns innocent
                results["messages"].append(
                    f"🟡 Detektiv: {self.players[target]['name']} — {'🔴 MAFIAchi!' if is_mafia else '✅ Fuqaro'}"
                )
                # Send privately — we store for now, handle in bot
            elif act == "expose":
                t_role = self.players[target].get("role", "")
                t_emoji = self.players[target].get("role_emoji", "")
                results["messages"].append(
                    f"🔵 Jurnalist: {self.players[target]['name']} — {t_emoji} {t_role}"
                )
            elif act == "maniac":
                maniac_kill = target
            elif act == "hero":
                t_role = self.players[target].get("role", "")
                if t_role in ["Mafia", "Don"]:
                    hero_kill = target
                else:
                    hero_kill = uid  # Hero dies
                    results["messages"].append(f"⚔️ Qahramon masum birini urdi va o'zi o'ldi!")

            # Joker role change
            if self.players[uid].get("role") == "Joker":
                available = [r for r in ROLES if r not in ["Don", "Mafia", "Joker"]]
                new_role = random.choice(available)
                self.players[uid]["role"] = new_role
                self.players[uid]["role_emoji"] = ROLES[new_role]["emoji"]

        # Apply kills
        to_kill = set()
        if kill_target is not None:
            to_kill.add(kill_target)
        if sheriff_kill is not None:
            to_kill.add(sheriff_kill)
        if maniac_kill is not None:
            to_kill.add(maniac_kill)
        if hero_kill is not None:
            to_kill.add(hero_kill)

        for victim in list(to_kill):
            p = self.players[victim]
            # Farishta (angel) - one-time save
            if p["role"] == "Farishta" and not p["angel_used"]:
                p["angel_used"] = True
                results["messages"].append(f"👼 {p['name']} farishtasi uni o'limdan qutqardi!")
                to_kill.discard(victim)
                continue
            # Shifokor heal
            if victim == heal_target:
                results["healed"].append(victim)
                to_kill.discard(victim)
                continue

        for victim in to_kill:
            self.players[victim]["alive"] = False
            results["killed"].append(victim)

        return results

    def check_winner(self) -> str | None:
        alive = {pid: p for pid, p in self.players.items() if p["alive"]}
        mafia_alive = [p for p in alive.values() if p.get("team") == "mafia"]
        town_alive = [p for p in alive.values() if p.get("team") == "town"]
        maniac_alive = [p for p in alive.values() if p.get("role") == "Maniak"]

        if not alive:
            return "draw"

        # Maniac wins if alone
        if len(alive) == 1 and maniac_alive:
            return "maniac"

        # Mafia wins if >= town (no maniac)
        if len(mafia_alive) >= len(town_alive) and not maniac_alive:
            return "mafia"

        # Town wins if no mafia and no maniac
        if not mafia_alive and not maniac_alive:
            return "town"

        # Maniac wins if only mafia left with them (not town)
        if not town_alive and maniac_alive and not mafia_alive:
            return "maniac"

        return None
