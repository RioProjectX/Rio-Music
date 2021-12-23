import asyncio
import importlib
import os
import re

from config import LOG_GROUP_ID
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from rich.console import Console
from rich.table import Table
from youtubesearchpython import VideosSearch

from Yukki import (ASSID, ASSMENTION, ASSNAME, ASSUSERNAME, BOT_ID, BOT_NAME,
                   BOT_USERNAME, SUDOERS, app, db, userbot)
from Yukki.Core.Logger.Log import (startup_delete_last, startup_edit_last,
                                   startup_send_new)
from Yukki.Core.PyTgCalls.Yukki import run
from Yukki.Database import get_active_chats, get_sudoers, remove_active_chat
from Yukki.Inline import private_panel
from Yukki.Plugins import ALL_MODULES
from Yukki.Utilities.inline import paginate_modules

loop = asyncio.get_event_loop()
console = Console()
HELPABLE = {}


async def initiate_bot():
    with console.status(
        "[magenta] Booting up The Rio Music Bot...",
    ) as status:
        console.print("┌ [red]Clearing MongoDB cache...")
        try:
            chats = await get_active_chats()
            for chat in chats:
                chat_id = int(chat["chat_id"])
                await remove_active_chat(chat_id)
        except Exception as e:
            console.print("[red] Error while clearing Mongo DB.")
        console.print("└ [green]MongoDB Cleared Successfully!\n\n")
        ____ = await startup_send_new("Importing All Plugins...")
        status.update(
            status="[bold blue]Scanning for Plugins", spinner="earth"
        )
        await asyncio.sleep(1.7)
        console.print("Found {} Plugins".format(len(ALL_MODULES)) + "\n")
        status.update(
            status="[bold red]Importing Plugins...",
            spinner="bouncingBall",
            spinner_style="yellow",
        )
        await asyncio.sleep(1.2)
        for all_module in ALL_MODULES:
            imported_module = importlib.import_module(
                "Yukki.Plugins." + all_module
            )
            if (
                hasattr(imported_module, "__MODULE__")
                and imported_module.__MODULE__
            ):
                imported_module.__MODULE__ = imported_module.__MODULE__
                if (
                    hasattr(imported_module, "__HELP__")
                    and imported_module.__HELP__
                ):
                    HELPABLE[
                        imported_module.__MODULE__.lower()
                    ] = imported_module
            console.print(
                f">> [bold cyan]Successfully imported: [green]{all_module}.py"
            )
            await asyncio.sleep(0.2)
        console.print("")
        _____ = await startup_edit_last(____, "Finalizing...")
        status.update(
            status="[bold blue]Importation Completed!",
        )
        await asyncio.sleep(2.4)
        await startup_delete_last(_____)
    console.print(
        "[bold green]Congrats!! Rio Music Bot has started successfully!\n"
    )
    try:
        await app.send_message(
            LOG_GROUP_ID,
            "<b>Congrats!! Music Bot has started successfully! Credit Rio Music</b>",
        )
    except Exception as e:
        print(
            "Bot has failed to access the log Channel. Make sure that you have added your bot to your log channel and promoted as admin!"
        )
        console.print(f"\n[red]Stopping Bot")
        return
    a = await app.get_chat_member(LOG_GROUP_ID, BOT_ID)
    if a.status != "administrator":
        print("Promote Bot as Admin in Logger Channel")
        console.print(f"\n[red]Stopping Bot")
        return
    try:
        await userbot.send_message(
            LOG_GROUP_ID,
            "<b>Congrats!! Assistant has started successfully!</b>",
        )
    except Exception as e:
        print(
            "Assistant Account has failed to access the log Channel. Make sure that you have added your bot to your log channel and promoted as admin!"
        )
        console.print(f"\n[red]Stopping Bot")
        return
    try:
        await userbot.join_chat("OfficialYukki")
    except:
        pass
    console.print(f"\n┌[red] Bot Started as {BOT_NAME}!")
    console.print(f"├[green] ID :- {BOT_ID}!")
    console.print(f"├[red] Assistant Started as {ASSNAME}!")
    console.print(f"└[green] ID :- {ASSID}!")
    await run()
    console.print(f"\n[red]Stopping Bot")



@app.on_message(filters.command("start") & filters.private)
async def start_command(_, message):
    if len(message.text.split()) > 1:
        name = (message.text.split(None, 1)[1]).lower()
        if name[0] == "s":
            sudoers = await get_sudoers()
            text = "**__Sudo Users List of Bot:-__**\n\n"
            j = 0
            for count, user_id in enumerate(sudoers, 1):
                try:
                    user = await app.get_users(user_id)
                    user = (
                        user.first_name if not user.mention else user.mention
                    )
                except Exception:
                    continue
                text += f"➤ {user}\n"
                j += 1
            if j == 0:
                await message.reply_text("No Sudo Users")
            else:
                await message.reply_text(text)
        if name == "help":
            text, keyboard = await help_parser(message.from_user.mention)
            await message.delete()
            return await app.send_text(
                message.chat.id,
                text,
                reply_markup=keyboard,
            )
        if name[0] == "i":
            m = await message.reply_text("🔎 Fetching Info!")
            query = (str(name)).replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"
            results = VideosSearch(query, limit=1)
            for result in results.result()["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                channellink = result["channel"]["link"]
                channel = channel = result["channel"]["name"]
                link = result["link"]
                published = result["publishedTime"]
            searched_text = f"""
🔍__**Video Track Information**__

❇️**Judul:** {title}

⏳**Durasi:** {duration} Mins
👀**Views:** `{views}`
⏰**Published Time:** {published}
🎥**Nama Channel:** {channel}
📎**Channel Link:** [Visit From Here]({channellink})
🔗**Video Link:** [Link]({link})

⚡️ __Searched Powered By {BOT_NAME}t__"""
            key = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="🎥 Watch Youtube Video", url=f"{link}"
                        ),
                        InlineKeyboardButton(
                            text="🔄 Close", callback_data="close"
                        ),
                    ],
                ]
            )
            await m.delete()
            return await app.send_photo(
                message.chat.id,
                photo=thumbnail,
                caption=searched_text,
                parse_mode="markdown",
                reply_markup=key,
            )
    out = private_panel()


@app.on_callback_query(filters.regex("shikhar"))
async def shikhar(_, CallbackQuery):
    text, keyboard = await help_parser(CallbackQuery.from_user.mention)
    await CallbackQuery.message.edit(text, reply_markup=keyboard)



if __name__ == "__main__":
    loop.run_until_complete(initiate_bot())
