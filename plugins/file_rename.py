from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from pyrogram.enums import MessageMediaType
from pyrogram.errors import FloodWait

from asyncio import sleep
import os
import time

from helper.utils import progress_for_pyrogram, convert, humanbytes
from helper.database import db

# Assuming the necessary imports for metadata extraction and processing are already present

@Client.on_message(filters.private & (filters.document | filters.audio | filters.video))
async def rename_start(client, message):
    file = getattr(message, message.media.value)
    filename = file.file_name  
    if file.file_size > 2000 * 1024 * 1024:
        return await message.reply_text("Sorry, this bot doesn't support uploading files bigger than 2GB.")

    try:
        await message.reply_text(
            text=f"**__Please enter the new filename and format.__**\n\n**Old Filename:** `{filename}`",
            reply_to_message_id=message.message_id,
            reply_markup=ForceReply(True)
        )       
        await sleep(30)
    except FloodWait as e:
        await sleep(e.value)
        await message.reply_text(
            text=f"**__Please enter the new filename and format.__**\n\n**Old Filename:** `{filename}`",
            reply_to_message_id=message.message_id,
            reply_markup=ForceReply(True)
        )
    except:
        pass


@Client.on_message(filters.private & filters.reply)
async def refunc(client, message):
    reply_message = message.reply_to_message
    if (reply_message.reply_markup) and isinstance(reply_message.reply_markup, ForceReply):
        text = message.text.split(".")
        if len(text) != 2:
            return await message.reply_text("Please enter the filename and format separated by a dot (e.g., newfile.mp4).")

        new_name, format = text
        await message.delete() 
        msg = await client.get_messages(message.chat.id, reply_message.message_id)
        file = msg.reply_to_message
        media = getattr(file, file.media.value)
        await reply_message.delete()

        button = [[InlineKeyboardButton("📁 Document", callback_data="upload_document")]]
        if file.media in [MessageMediaType.VIDEO, MessageMediaType.DOCUMENT]:
            button.append([InlineKeyboardButton("🎥 Video", callback_data="upload_video")])
        elif file.media == MessageMediaType.AUDIO:
            button.append([InlineKeyboardButton("🎵 Audio", callback_data="upload_audio")])
        await message.reply(
            text=f"**Select the output file type**\n**• File Name:** `{new_name}`\n**• Format:** `{format}`",
            reply_to_message_id=file.message_id,
            reply_markup=InlineKeyboardMarkup(button)
        )


@Client.on_callback_query(filters.regex("upload"))
async def doc(bot, update):    
    new_name = update.message.text
    new_filename = new_name.split("Filename: ")[1].split("\n")[0]
    file_path = f"downloads/{new_filename}"
    file = update.message.reply_to_message

    ms = await update.message.edit("Trying to download...")
    try:
        path = await bot.download_media(message=file, file_name=file_path, progress=progress_for_pyrogram, progress_args=("Download started...", ms, time.time()))                    
    except Exception as e:
        return await ms.edit(str(e))

    duration = 0
    try:
        metadata = extractMetadata(createParser(file_path))
        if metadata.has("duration"):
           duration = metadata.get('duration').seconds
    except:
        pass

    ph_path = None
    media = getattr(file, file.media.value)
    c_caption = await db.get_caption(update.message.chat.id)
    c_thumb = await db.get_thumbnail(update.message.chat.id)

    if c_caption:
        try:
            caption = c_caption.format(filename=new_filename, filesize=humanbytes(media.file_size), duration=convert(duration))
        except Exception as e:
            return await ms.edit(f"Your caption has an error. Exception: {e}")             
    else:
        caption = f"**{new_filename}**"

    if (media.thumbs or c_thumb):
        if c_thumb:
            ph_path = await bot.download_media(c_thumb) 
        else:
            ph_path = await bot.download_media(media.thumbs[0].file_id)
        Image.open(ph_path).convert("RGB").save(ph_path)
        img = Image.open(ph_path)
        img.resize((320, 320))
        img.save(ph_path, "JPEG")

    await ms.edit("Trying to upload...")
    type = update.data.split("_")[1]
    try:
        if type == "document":
            await bot.send_document(
                update.message.chat.id,
                document=file_path,
                thumb=ph_path, 
                caption=caption, 
                progress=progress_for_pyrogram,
                progress_args=("Upload started...", ms, time.time()))
        elif type == "video": 
            await bot.send_video(
                update.message.chat.id,
                video=file_path,
                caption=caption,
                thumb=ph_path,
                duration=duration,
                progress=progress_for_pyrogram,
                progress_args=("Upload started...", ms, time.time()))
        elif type == "audio": 
            await bot.send_audio(
                update.message.chat.id,
                audio=file_path,
                caption=caption,
                thumb=ph_path,
                duration=duration,
                progress=progress_for_pyrogram,
                progress_args=("Upload started...", ms, time.time()))
    except Exception as e:          
        os.remove(file_path)
        if ph_path:
            os.remove(ph_path)
        return await ms.edit(f"Error: {e}")

    await ms.delete() 
    os.remove(file_path) 
    if ph_path: os.remove(ph_path)
