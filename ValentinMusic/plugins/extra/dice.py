"""
Dice Module — Roll dice, darts, basketball, bowling, slots, and football.
Ported from WilliamButcherBot (MIT License) by TheHamkerCat.
"""
from pyrogram import filters
from pyrogram.types import Message

from ValentinMusic import app
from ValentinMusic.misc import SUDOERS


@app.on_message(filters.command("dice"))
async def throw_dice(client, message: Message):
    await client.send_dice(message.chat.id, "🎲")



@app.on_message(filters.command("dart"))
async def throw_dart(client, message: Message):
    await client.send_dice(message.chat.id, "🎯")


@app.on_message(filters.command("basketball"))
async def throw_ball(client, message: Message):
    await client.send_dice(message.chat.id, "🏀")


@app.on_message(filters.command("bowling"))
async def throw_bowling(client, message: Message):
    await client.send_dice(message.chat.id, "🎳")


@app.on_message(filters.command("slots"))
async def play_slots(client, message: Message):
    await client.send_dice(message.chat.id, "🎰")


@app.on_message(filters.command("football"))
async def throw_football(client, message: Message):
    await client.send_dice(message.chat.id, "⚽")
