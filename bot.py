import logging
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)
from config import BOT_TOKEN, ADMIN_ID
from database import db
from game import MafiaGame

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Active games per chat
games: dict[int, MafiaGame] = {}

# ─────────────────────────────────────────
# ADMIN COMMANDS
# ─────────────────────────────────────────

async def cmd_users(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    count = db.user_count()
    await update.message.reply_text(f"👥 Jami foydalanuvchilar: <b>{count}</b>", parse_mode="HTML")

async def cmd_xabar(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not ctx.args:
        await update.message.reply_text("❗ Foydalanish: /xabar <matn>")
        return
    text = " ".join(ctx.args)
    users = db.all_users()
    sent, failed = 0, 0
    msg = await update.message.reply_text(f"📤 Xabar yuborilmoqda {len(users)} ta foydalanuvchiga...")
    for uid in users:
        try:
            await ctx.bot.send_message(uid, f"📢 <b>Admin xabari:</b>\n\n{text}", parse_mode="HTML")
            sent += 1
        except Exception:
            failed += 1
    await msg.edit_text(f"✅ Yuborildi: <b>{sent}</b>\n❌ Muvaffaqiyatsiz: <b>{failed}</b>", parse_mode="HTML")

async def cmd_admin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    text = (
        "🛠 <b>Admin Paneli</b>\n\n"
        "/users — Foydalanuvchilar soni\n"
        "/xabar &lt;matn&gt; — Hammaga xabar yuborish\n"
    )
    await update.message.reply_text(text, parse_mode="HTML")

# ─────────────────────────────────────────
# BOT COMMANDS
# ─────────────────────────────────────────

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user.id)
    await update.message.reply_text(
        f"👋 Salom, <b>{user.first_name}</b>!\n\n"
        "🎭 <b>Mafia Bot</b>ga xush kelibsiz!\n\n"
        "Guruhga qo'shing va o'yinni boshlang:\n"
        "• /yangioyun — Yangi o'yin boshlash\n"
        "• /qoshilish — O'yinga qo'shilish\n"
        "• /boshlash — O'yinni ishga tushirish\n"
        "• /toxtash — O'yinni bekor qilish\n"
        "• /yordam — Yordam\n\n"
        "🔞 Minimum 5 o'yinchi talab etiladi!",
        parse_mode="HTML"
    )

async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 <b>Yordam</b>\n\n"
        "<b>Buyruqlar:</b>\n"
        "/yangioyun — Yangi o'yin yaratish\n"
        "/qoshilish — O'yinga qo'shilish\n"
        "/boshlash — O'yinni boshlash (admin)\n"
        "/toxtash — O'yinni bekor qilish\n"
        "/oyinchilar — O'yinchilar ro'yxati\n\n"
        "<b>Rollar:</b>\n"
        "🔴 Mafia — Tungi ovozda fuqarolarni o'ldiradi\n"
        "⚫ Don — Mafia boshlig'i, Detektiv tekshira olmaydi\n"
        "🟡 Detektiv — Tungi tekshirish o'tkazadi\n"
        "🟢 Shifokor — Tungi birini davolaydi\n"
        "🟠 Sheriff — Mafiachini o'ldira oladi\n"
        "💜 Fahisha — Tungi birini band qiladi\n"
        "🔵 Jurnalist — Fuqaroning rolini aniqlaydi\n"
        "🩸 Maniak — Yolg'iz o'ldiradi\n"
        "👼 Farishta — Bir marta o'limdan qutqaradi\n"
        "💣 Portlovchi — O'lsa bir qo'shnisini ham o'ldiradi\n"
        "🃏 Joker — Har kecha rol o'zgartiradi\n"
        "🕵️ Agent — Ikkita tekshirish o'tkazadi\n"
        "🧙 Sehrgar — Ovozni bloklaydi\n"
        "⚔️ Qahramon — Mafiachini kunduz o'ldiradi\n"
        "👤 Fuqaro — Oddiy fuqaro\n",
        parse_mode="HTML"
    )

async def cmd_new_game(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if update.effective_chat.type == "private":
        await update.message.reply_text("❗ Bu buyruq faqat guruhda ishlaydi!")
        return
    if chat_id in games and games[chat_id].active:
        await update.message.reply_text("⚠️ Guruhda allaqachon o'yin ketmoqda!")
        return
    games[chat_id] = MafiaGame(chat_id, update.effective_user.id)
    db.add_user(update.effective_user.id)
    games[chat_id].add_player(update.effective_user.id, update.effective_user.first_name)
    kb = [[InlineKeyboardButton("✅ Qo'shilish", callback_data="join")]]
    await update.message.reply_text(
        "🎭 <b>Yangi Mafia o'yini boshlandi!</b>\n\n"
        f"👤 O'yinchilar: <b>1</b>\n"
        "⏳ Minimum 5 o'yinchi kerak\n\n"
        "Qo'shilish uchun tugmani bosing! 👇",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="HTML"
    )

async def cmd_join(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    db.add_user(user.id)
    if chat_id not in games:
        await update.message.reply_text("❗ Hali o'yin yo'q. /yangioyun bilan boshlang!")
        return
    game = games[chat_id]
    if game.active:
        await update.message.reply_text("❗ O'yin allaqachon boshlangan!")
        return
    result = game.add_player(user.id, user.first_name)
    if result == "already":
        await update.message.reply_text(f"⚠️ {user.first_name}, siz allaqachon ro'yxatdasiz!")
    elif result == "added":
        count = len(game.players)
        kb = [[InlineKeyboardButton("✅ Qo'shilish", callback_data="join")]]
        await update.message.reply_text(
            f"✅ <b>{user.first_name}</b> qo'shildi!\n"
            f"👥 O'yinchilar: <b>{count}</b>/15",
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode="HTML"
        )

async def cmd_start_game(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if chat_id not in games:
        await update.message.reply_text("❗ Avval /yangioyun buyrug'ini yuboring!")
        return
    game = games[chat_id]
    if user.id != game.creator_id and user.id != ADMIN_ID:
        await update.message.reply_text("❗ Faqat o'yin yaratuvchisi boshlashi mumkin!")
        return
    if len(game.players) < 5:
        await update.message.reply_text(f"❗ Kamida 5 o'yinchi kerak! Hozir: {len(game.players)}")
        return
    await update.message.reply_text("🎰 Rollar taqsimlanmoqda...")
    game.assign_roles()
    game.active = True
    # Send roles privately
    for pid, pdata in game.players.items():
        role = pdata["role"]
        emoji = pdata["role_emoji"]
        desc = pdata["role_desc"]
        try:
            await ctx.bot.send_message(
                pid,
                f"🎭 <b>Sizning rolingiz:</b>\n\n{emoji} <b>{role}</b>\n\n{desc}",
                parse_mode="HTML"
            )
        except Exception:
            pass
    player_list = "\n".join([f"• {p['name']}" for p in game.players.values()])
    await update.message.reply_text(
        f"🌙 <b>O'yin boshlandi!</b>\n\n"
        f"👥 <b>O'yinchilar ({len(game.players)}):</b>\n{player_list}\n\n"
        "Har bir o'yinchi shaxsiy xabarida o'z rolini ko'rdi!\n\n"
        "🌅 <b>1-kun boshlandi.</b> Muhokama qiling!",
        parse_mode="HTML"
    )
    await asyncio.sleep(2)
    await start_day_phase(update, ctx, chat_id)

async def cmd_stop(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if chat_id not in games:
        await update.message.reply_text("❗ Hozir o'yin yo'q!")
        return
    game = games[chat_id]
    if user.id != game.creator_id and user.id != ADMIN_ID:
        await update.message.reply_text("❗ Faqat o'yin yaratuvchisi to'xtatishi mumkin!")
        return
    del games[chat_id]
    await update.message.reply_text("🛑 O'yin bekor qilindi!")

async def cmd_players(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in games:
        await update.message.reply_text("❗ Hozir o'yin yo'q!")
        return
    game = games[chat_id]
    alive = [p for p in game.players.values() if p["alive"]]
    dead = [p for p in game.players.values() if not p["alive"]]
    text = "👥 <b>O'yinchilar:</b>\n\n"
    text += "💚 <b>Tirik:</b>\n" + "\n".join([f"• {p['name']}" for p in alive]) + "\n"
    if dead:
        text += "\n💀 <b>O'lgan:</b>\n" + "\n".join([f"• {p['name']} ({p['role_emoji']} {p['role']})" for p in dead])
    await update.message.reply_text(text, parse_mode="HTML")

# ─────────────────────────────────────────
# GAME PHASES
# ─────────────────────────────────────────

async def start_day_phase(update: Update, ctx: ContextTypes.DEFAULT_TYPE, chat_id: int):
    game = games.get(chat_id)
    if not game:
        return
    game.phase = "day"
    game.votes = {}
    alive = [p for p in game.players.values() if p["alive"]]
    buttons = []
    for pid, p in game.players.items():
        if p["alive"]:
            buttons.append([InlineKeyboardButton(f"🗳 {p['name']}", callback_data=f"vote_{pid}")])
    buttons.append([InlineKeyboardButton("⏭ Ovozni o'tkazib yuborish", callback_data="skip_vote")])
    await ctx.bot.send_message(
        chat_id,
        f"☀️ <b>{game.day}-kun.</b> Mafiachi kim ekanini aniqlang!\n\n"
        f"👥 Tiriklar: {len(alive)} kishi\n"
        "📢 Muhokama qilib, ovoz bering! Kim mafiachi?",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="HTML"
    )

async def start_night_phase(chat_id: int, ctx: ContextTypes.DEFAULT_TYPE):
    game = games.get(chat_id)
    if not game:
        return
    game.phase = "night"
    game.night_actions = {}
    await ctx.bot.send_message(
        chat_id,
        "🌙 <b>Tun boshlandi.</b>\n\nHamma uxladi... Mafia uyg'oq!",
        parse_mode="HTML"
    )
    # Notify each special role privately
    for pid, p in game.players.items():
        if not p["alive"]:
            continue
        role = p["role"]
        alive_others = [(oid, op) for oid, op in game.players.items() if op["alive"] and oid != pid]
        if not alive_others:
            continue

        if role in ["Mafia", "Don"]:
            buttons = [[InlineKeyboardButton(f"🔫 {op['name']}", callback_data=f"night_kill_{oid}")]
                       for oid, op in alive_others if game.players[oid].get("role") not in ["Mafia", "Don"]]
            if buttons:
                try:
                    await ctx.bot.send_message(pid,
                        "🔴 <b>Mafia vaqti!</b> Kimni o'ldirasiz?",
                        reply_markup=InlineKeyboardMarkup(buttons), parse_mode="HTML")
                except Exception:
                    pass

        elif role == "Detektiv":
            buttons = [[InlineKeyboardButton(f"🔍 {op['name']}", callback_data=f"night_check_{oid}")]
                       for oid, op in alive_others]
            try:
                await ctx.bot.send_message(pid,
                    "🟡 <b>Detektiv vaqti!</b> Kimni tekshirasiz?",
                    reply_markup=InlineKeyboardMarkup(buttons), parse_mode="HTML")
            except Exception:
                pass

        elif role == "Shifokor":
            buttons = [[InlineKeyboardButton(f"💉 {op['name']}", callback_data=f"night_heal_{oid}")]
                       for oid, op in game.players.items() if op["alive"]]
            try:
                await ctx.bot.send_message(pid,
                    "🟢 <b>Shifokor vaqti!</b> Kimni davolaysiz?",
                    reply_markup=InlineKeyboardMarkup(buttons), parse_mode="HTML")
            except Exception:
                pass

        elif role == "Sheriff":
            buttons = [[InlineKeyboardButton(f"🔫 {op['name']}", callback_data=f"night_shoot_{oid}")]
                       for oid, op in alive_others]
            try:
                await ctx.bot.send_message(pid,
                    "🟠 <b>Sheriff vaqti!</b> Kimni otasiz?",
                    reply_markup=InlineKeyboardMarkup(buttons), parse_mode="HTML")
            except Exception:
                pass

        elif role == "Fahisha":
            buttons = [[InlineKeyboardButton(f"💋 {op['name']}", callback_data=f"night_block_{oid}")]
                       for oid, op in alive_others]
            try:
                await ctx.bot.send_message(pid,
                    "💜 <b>Fahisha vaqti!</b> Kimni band qilasiz?",
                    reply_markup=InlineKeyboardMarkup(buttons), parse_mode="HTML")
            except Exception:
                pass

        elif role == "Jurnalist":
            buttons = [[InlineKeyboardButton(f"📰 {op['name']}", callback_data=f"night_expose_{oid}")]
                       for oid, op in alive_others]
            try:
                await ctx.bot.send_message(pid,
                    "🔵 <b>Jurnalist vaqti!</b> Kimni oshkor qilasiz?",
                    reply_markup=InlineKeyboardMarkup(buttons), parse_mode="HTML")
            except Exception:
                pass

        elif role == "Agent":
            buttons = [[InlineKeyboardButton(f"🕵️ {op['name']}", callback_data=f"night_agent_{oid}")]
                       for oid, op in alive_others]
            try:
                await ctx.bot.send_message(pid,
                    "🕵️ <b>Agent vaqti!</b> Kimni kuzatasiz?",
                    reply_markup=InlineKeyboardMarkup(buttons), parse_mode="HTML")
            except Exception:
                pass

        elif role == "Sehrgar":
            buttons = [[InlineKeyboardButton(f"🧙 {op['name']}", callback_data=f"night_silence_{oid}")]
                       for oid, op in alive_others]
            try:
                await ctx.bot.send_message(pid,
                    "🧙 <b>Sehrgar vaqti!</b> Kimni jimlatasiz?",
                    reply_markup=InlineKeyboardMarkup(buttons), parse_mode="HTML")
            except Exception:
                pass

        elif role == "Maniak":
            buttons = [[InlineKeyboardButton(f"🩸 {op['name']}", callback_data=f"night_maniac_{oid}")]
                       for oid, op in alive_others]
            try:
                await ctx.bot.send_message(pid,
                    "🩸 <b>Maniak vaqti!</b> Qurbonni tanlang:",
                    reply_markup=InlineKeyboardMarkup(buttons), parse_mode="HTML")
            except Exception:
                pass

        elif role == "Qahramon":
            buttons = [[InlineKeyboardButton(f"⚔️ {op['name']}", callback_data=f"night_hero_{oid}")]
                       for oid, op in alive_others]
            try:
                await ctx.bot.send_message(pid,
                    "⚔️ <b>Qahramon vaqti!</b> Kimga hujum qilasiz?",
                    reply_markup=InlineKeyboardMarkup(buttons), parse_mode="HTML")
            except Exception:
                pass

    # Auto-resolve night after 60s
    await asyncio.sleep(60)
    if games.get(chat_id) and games[chat_id].phase == "night":
        await resolve_night(chat_id, ctx)

async def resolve_night(chat_id: int, ctx: ContextTypes.DEFAULT_TYPE):
    game = games.get(chat_id)
    if not game or game.phase != "night":
        return
    game.phase = "resolving"
    results = game.process_night()
    text = "🌅 <b>Tun tugadi!</b>\n\n"
    if results["killed"]:
        for pid in results["killed"]:
            name = game.players[pid]["name"]
            role = game.players[pid]["role"]
            emoji = game.players[pid]["role_emoji"]
            text += f"💀 <b>{name}</b> o'ldirildi! Rol: {emoji} {role}\n"
    else:
        text += "😮 Bu tun hech kim o'lmadi!\n"
    if results["healed"]:
        text += f"\n💉 Shifokor birini davoladi!\n"
    if results.get("messages"):
        for msg in results["messages"]:
            text += f"\n{msg}"
    await ctx.bot.send_message(chat_id, text, parse_mode="HTML")
    winner = game.check_winner()
    if winner:
        await announce_winner(chat_id, ctx, winner)
        return
    game.day += 1
    await asyncio.sleep(3)
    await start_day_phase(None, ctx, chat_id)

async def announce_winner(chat_id: int, ctx: ContextTypes.DEFAULT_TYPE, winner: str):
    game = games.get(chat_id)
    if not game:
        return
    if winner == "town":
        msg = "🎉 <b>FUQAROLAR G'ALABA QILDI!</b>\n\nMafia yo'q qilindi!"
    elif winner == "mafia":
        msg = "🔴 <b>MAFIA G'ALABA QILDI!</b>\n\nQorong'ulik hukm surdi..."
    elif winner == "maniac":
        msg = "🩸 <b>MANIAK G'ALABA QILDI!</b>\n\nHamma o'ldirildi!"
    else:
        msg = "🤝 <b>Durrang!</b>"
    roles_reveal = "\n".join([
        f"{'💀' if not p['alive'] else '✅'} {p['name']} — {p['role_emoji']} {p['role']}"
        for p in game.players.values()
    ])
    await ctx.bot.send_message(
        chat_id,
        f"{msg}\n\n<b>Barcha rollar:</b>\n{roles_reveal}",
        parse_mode="HTML"
    )
    del games[chat_id]

# ─────────────────────────────────────────
# CALLBACK HANDLER
# ─────────────────────────────────────────

async def callback_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user = query.from_user
    chat_id = query.message.chat_id
    db.add_user(user.id)

    # Join game via button
    if data == "join":
        if chat_id not in games:
            await query.answer("O'yin topilmadi!", show_alert=True)
            return
        game = games[chat_id]
        if game.active:
            await query.answer("O'yin boshlangan!", show_alert=True)
            return
        result = game.add_player(user.id, user.first_name)
        if result == "already":
            await query.answer("Siz allaqachon ro'yxatdasiz!", show_alert=True)
        else:
            count = len(game.players)
            kb = [[InlineKeyboardButton("✅ Qo'shilish", callback_data="join")]]
            await query.message.edit_text(
                f"🎭 <b>Mafia o'yini - Ro'yxatga olish</b>\n\n"
                f"👥 O'yinchilar ({count}):\n" +
                "\n".join([f"• {p['name']}" for p in game.players.values()]) +
                "\n\n⏳ Minimum 5 o'yinchi kerak\nQo'shilish uchun tugmani bosing! 👇",
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode="HTML"
            )

    # Day voting
    elif data.startswith("vote_"):
        target_id = int(data.split("_")[1])
        if chat_id not in games:
            return
        game = games[chat_id]
        if game.phase != "day":
            await query.answer("Hozir ovoz berish vaqti emas!", show_alert=True)
            return
        if user.id not in game.players or not game.players[user.id]["alive"]:
            await query.answer("Siz o'yinda yo'qsiz!", show_alert=True)
            return
        if user.id in game.votes:
            await query.answer("Siz allaqachon ovoz berdingiz!", show_alert=True)
            return
        game.votes[user.id] = target_id
        voter_name = game.players[user.id]["name"]
        target_name = game.players[target_id]["name"]
        alive_count = sum(1 for p in game.players.values() if p["alive"])
        await ctx.bot.send_message(chat_id,
            f"🗳 <b>{voter_name}</b> → <b>{target_name}</b>ga ovoz berdi "
            f"({len(game.votes)}/{alive_count})",
            parse_mode="HTML")
        # Check if all voted
        if len(game.votes) >= alive_count:
            await process_day_vote(chat_id, ctx)

    elif data == "skip_vote":
        if chat_id not in games:
            return
        game = games[chat_id]
        if game.phase != "day":
            return
        if user.id not in game.players or not game.players[user.id]["alive"]:
            await query.answer("Siz o'yinda yo'qsiz!", show_alert=True)
            return
        if user.id in game.votes:
            await query.answer("Allaqachon ovoz berdingiz!", show_alert=True)
            return
        game.votes[user.id] = None
        alive_count = sum(1 for p in game.players.values() if p["alive"])
        await ctx.bot.send_message(chat_id,
            f"⏭ <b>{game.players[user.id]['name']}</b> ovozni o'tkazib yubordi. ({len(game.votes)}/{alive_count})",
            parse_mode="HTML")
        if len(game.votes) >= alive_count:
            await process_day_vote(chat_id, ctx)

    # Night actions
    elif data.startswith("night_"):
        parts = data.split("_")
        action = parts[1]
        target_id = int(parts[2])
        if chat_id not in games:
            return
        game = games[chat_id]
        if game.phase != "night":
            await query.answer("Tun emas!", show_alert=True)
            return
        if user.id not in game.players or not game.players[user.id]["alive"]:
            await query.answer("Siz o'yinda yo'qsiz!", show_alert=True)
            return
        if user.id in game.night_actions:
            await query.answer("Siz allaqachon harakat qildingiz!", show_alert=True)
            return
        game.night_actions[user.id] = {"action": action, "target": target_id}
        target_name = game.players[target_id]["name"]
        await query.edit_message_text(f"✅ Tanlov qabul qilindi: <b>{target_name}</b>", parse_mode="HTML")
        # Check if all special roles acted
        special_roles = ["Mafia", "Don", "Detektiv", "Shifokor", "Sheriff",
                        "Fahisha", "Jurnalist", "Agent", "Sehrgar", "Maniak", "Qahramon"]
        actors_needed = [pid for pid, p in game.players.items()
                        if p["alive"] and p["role"] in special_roles]
        if all(pid in game.night_actions for pid in actors_needed):
            await resolve_night(chat_id, ctx)

async def process_day_vote(chat_id: int, ctx: ContextTypes.DEFAULT_TYPE):
    game = games.get(chat_id)
    if not game:
        return
    game.phase = "voting"
    # Count votes
    vote_count = {}
    for voter, target in game.votes.items():
        if target is None:
            continue
        vote_count[target] = vote_count.get(target, 0) + 1
    if not vote_count:
        await ctx.bot.send_message(chat_id, "🤷 Hech kim ovoz bermadi! Tun boshlandi.", parse_mode="HTML")
    else:
        max_votes = max(vote_count.values())
        candidates = [pid for pid, v in vote_count.items() if v == max_votes]
        eliminated = random.choice(candidates)
        game.players[eliminated]["alive"] = False
        name = game.players[eliminated]["name"]
        role = game.players[eliminated]["role"]
        emoji = game.players[eliminated]["role_emoji"]
        # Portlovchi - kills neighbor
        extra = ""
        if role == "Portlovchi":
            alive_list = [pid for pid, p in game.players.items() if p["alive"]]
            if alive_list:
                victim = random.choice(alive_list)
                game.players[victim]["alive"] = False
                extra = f"\n💣 <b>Portlovchi!</b> {game.players[victim]['name']} ham o'ldi!"
        result_text = "📊 <b>Ovoz natijalari:</b>\n"
        for pid, cnt in sorted(vote_count.items(), key=lambda x: -x[1]):
            result_text += f"• {game.players[pid]['name']}: {cnt} ovoz\n"
        await ctx.bot.send_message(chat_id,
            f"{result_text}\n☠️ <b>{name}</b> o'ldirildi! Rol: {emoji} {role}{extra}",
            parse_mode="HTML")
        winner = game.check_winner()
        if winner:
            await announce_winner(chat_id, ctx, winner)
            return
    await asyncio.sleep(3)
    await start_night_phase(chat_id, ctx)

# ─────────────────────────────────────────
# TRACK NEW USERS
# ─────────────────────────────────────────

async def track_user(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user:
        db.add_user(update.effective_user.id)

# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    # Admin
    app.add_handler(CommandHandler("admin", cmd_admin))
    app.add_handler(CommandHandler("users", cmd_users))
    app.add_handler(CommandHandler("xabar", cmd_xabar))
    # Game
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("yordam", cmd_help))
    app.add_handler(CommandHandler("yangioyun", cmd_new_game))
    app.add_handler(CommandHandler("qoshilish", cmd_join))
    app.add_handler(CommandHandler("boshlash", cmd_start_game))
    app.add_handler(CommandHandler("toxtash", cmd_stop))
    app.add_handler(CommandHandler("oyinchilar", cmd_players))
    # Callbacks
    app.add_handler(CallbackQueryHandler(callback_handler))
    # Track users
    app.add_handler(MessageHandler(filters.ALL, track_user))
    print("🤖 Mafia bot ishga tushdi!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
