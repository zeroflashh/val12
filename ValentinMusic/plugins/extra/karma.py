"""
Karma Module — Upvote/downvote users, track karma scores.
Ported from WilliamButcherBot (MIT License) by TheHamkerCat.
"""
import re

from pyrogram import filters

from ValentinMusic import app
from ValentinMusic.core.mongo import mongodb

karmadb = mongodb.karma
karma_toggle_db = mongodb.karma_toggle

regex_upvote = r"^(\++|\+1|thx|tnx|tq|ty|thankyou|thank you|thanx|thanks|pro|cool|good|agree|👍|\++ .+)$"
regex_downvote = r"^(-+|-1|not cool|disagree|worst|bad|👎|-+ .+)$"


# ─── DB Functions ─────────────────────────────────────────
async def get_karma(chat_id, user_id):
    data = await karmadb.find_one({"chat_id": chat_id, "user_id": user_id})
    return data.get("karma", 0) if data else 0


async def update_karma(chat_id, user_id, karma):
    await karmadb.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": {"karma": karma}},
        upsert=True,
    )


async def get_all_karma(chat_id):
    results = {}
    async for doc in karmadb.find({"chat_id": chat_id}):
        results[doc["user_id"]] = doc.get("karma", 0)
    return results


async def is_karma_on(chat_id):
    data = await karma_toggle_db.find_one({"chat_id": chat_id})
    if data:
        return data.get("enabled", True)
    return True


async def karma_on(chat_id):
    await karma_toggle_db.update_one(
        {"chat_id": chat_id}, {"$set": {"enabled": True}}, upsert=True
    )


async def karma_off(chat_id):
    await karma_toggle_db.update_one(
        {"chat_id": chat_id}, {"$set": {"enabled": False}}, upsert=True
    )


# ─── Handlers ─────────────────────────────────────────────
@app.on_message(
    filters.text
    & filters.group
    & filters.incoming
    & filters.reply
    & filters.regex(regex_upvote, re.IGNORECASE)
    & ~filters.via_bot
    & ~filters.bot,
    group=5,
)
async def upvote(_, message):
    if not await is_karma_on(message.chat.id):
        return
    if not message.reply_to_message.from_user:
        return
    if not message.from_user:
        return
    if message.reply_to_message.from_user.id == message.from_user.id:
        return

    chat_id = message.chat.id
    user_id = message.reply_to_message.from_user.id
    user_mention = message.reply_to_message.from_user.mention
    current = await get_karma(chat_id, user_id)
    karma = current + 1
    await update_karma(chat_id, user_id, karma)
    await message.reply_text(
        f"⬆️ <b>Karma of {user_mention} increased!</b>\n"
        f"<b>Total Points:</b> <code>{karma}</code>"
    )


@app.on_message(
    filters.text
    & filters.group
    & filters.incoming
    & filters.reply
    & filters.regex(regex_downvote, re.IGNORECASE)
    & ~filters.via_bot
    & ~filters.bot,
    group=6,
)
async def downvote(_, message):
    if not await is_karma_on(message.chat.id):
        return
    if not message.reply_to_message.from_user:
        return
    if not message.from_user:
        return
    if message.reply_to_message.from_user.id == message.from_user.id:
        return

    chat_id = message.chat.id
    user_id = message.reply_to_message.from_user.id
    user_mention = message.reply_to_message.from_user.mention
    current = await get_karma(chat_id, user_id)
    karma = current - 1
    await update_karma(chat_id, user_id, karma)
    await message.reply_text(
        f"⬇️ <b>Karma of {user_mention} decreased!</b>\n"
        f"<b>Total Points:</b> <code>{karma}</code>"
    )


@app.on_message(filters.command("karma") & filters.group)
async def command_karma(_, message):
    chat_id = message.chat.id

    if not message.reply_to_message:
        m = await message.reply_text("📊 <b>Analyzing Karma...</b>")
        karma_data = await get_all_karma(chat_id)
        if not karma_data:
            return await m.edit("No karma data for this chat yet.")

        sorted_karma = sorted(karma_data.items(), key=lambda x: x[1], reverse=True)[:10]

        text = "<b>╔══════════════════╗\n║   🏆 𝗞𝗔𝗥𝗠𝗔 𝗕𝗢𝗔𝗥𝗗\n╠══════════════════╣</b>\n"
        rank = 1
        for user_id, points in sorted_karma:
            try:
                user = await app.get_users(user_id)
                name = user.first_name[:15]
            except Exception:
                name = f"User {user_id}"
            medal = ["🥇", "🥈", "🥉"][rank - 1] if rank <= 3 else f"#{rank}"
            text += f"<b>║ {medal}</b> {name} — <code>{points}</code>\n"
            rank += 1
        text += "<b>╚══════════════════╝</b>"
        await m.edit(text)
    else:
        if not message.reply_to_message.from_user:
            return await message.reply("Anonymous users have no karma.")
        user_id = message.reply_to_message.from_user.id
        karma = await get_karma(chat_id, user_id)
        await message.reply_text(f"<b>Total Points:</b> <code>{karma}</code>")


@app.on_message(filters.command("karma_toggle") & ~filters.private)
async def karma_toggle_cmd(_, message):
    usage = "<b>Usage:</b>\n/karma_toggle [enable|disable]"
    if len(message.command) != 2:
        return await message.reply_text(usage)
    state = message.text.split(None, 1)[1].strip().lower()
    if state == "enable":
        await karma_on(message.chat.id)
        await message.reply_text("✅ <b>Karma system enabled for this chat.</b>")
    elif state == "disable":
        await karma_off(message.chat.id)
        await message.reply_text("❌ <b>Karma system disabled for this chat.</b>")
    else:
        await message.reply_text(usage)
