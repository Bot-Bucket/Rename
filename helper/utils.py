import math
import time
from datetime import datetime
from pytz import timezone
from config import Config, Txt
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

async def progress_for_pyrogram(current, total, ud_type, message, start_time):
    now = time.monotonic()
    diff = now - start_time

    if round(diff % 5.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time_str = format_time(elapsed_time)
        estimated_total_time_str = format_time(estimated_total_time)

        progress = ''.join(["⬢" for _ in range(math.floor(percentage / 5))]) + \
                   ''.join(["⬡" for _ in range(20 - math.floor(percentage / 5))])

        try:
            await message.edit(
                text=f"{ud_type}\n\n{progress}{Txt.PROGRESS_BAR.format( 
                        round(percentage, 2),
                        humanbytes(current),
                        humanbytes(total),
                        humanbytes(speed),
                        estimated_total_time_str if estimated_total_time_str else '0 s'
                    )}",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✖️ 𝙲𝙰𝙽𝙲𝙴𝙻 ✖️", callback_data="close")]])
            )
        except Exception as e:
            print(f"Error editing message: {e}")

def humanbytes(size):
    if not size:
        return ""

    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}

    while size > power:
        size /= power
        n += 1

    return str(round(size, 2)) + " " + Dic_powerN[n] + 'ʙ'

def format_time(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    time_components = []
    if days:
        time_components.append(f"{days}ᴅ")
    if hours:
        time_components.append(f"{hours}ʜ")
    if minutes:
        time_components.append(f"{minutes}ᴍ")
    if seconds:
        time_components.append(f"{seconds}ꜱ")
    if milliseconds:
        time_components.append(f"{milliseconds}ᴍꜱ")

    return ", ".join(time_components)

def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return "%d:%02d:%02d" % (hour, minutes, seconds)

async def send_log(bot, user):
    if Config.LOG_CHANNEL is not None:
        curr = datetime.now(timezone("Asia/Kolkata"))
        date = curr.strftime('%d %B, %Y')
        time = curr.strftime('%I:%M:%S %p')
        await bot.send_message(
            Config.LOG_CHANNEL,
            f"**-- New User Started The Bot --**\n\nUser: {user.mention}\nID: `{user.id}`\nUsername: @{user.username}\n\nDate: {date}\nTime: {time}\n\nBy: {bot.mention}"
        )
