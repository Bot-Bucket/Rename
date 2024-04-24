from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup, ForceReply)
from thumb_&_cap.py import get_thumbnail, get_caption

@Client.on_message(filters.private & filters.reply)
async def refunc(client, message):
    if (message.reply_to_message.reply_markup) and isinstance(message.reply_to_message.reply_markup, ForceReply):
        new_name = message.text
        await message.delete()
        media = await client.get_messages(message.chat.id, message.reply_to_message.id)
        file = media.reply_to_message.document or media.reply_to_message.video
        filename = file.file_name
        mime = file.mime_type.split("/")[0]
        mg_id = media.reply_to_message.message_id
        try:
            out = new_name.split(".")
            out_filename = new_name
            await message.reply_to_message.delete()
            # Constructing inline keyboard based on file type
            if mime == "video":
                markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton("📁 Document", callback_data="doc")],
                    [InlineKeyboardButton("🎥 Rename to video", callback_data="vid")]
                ])
            else:
                markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton("📁 Rename to document", callback_data="doc")],
                    [InlineKeyboardButton("🎥 Rename to video", callback_data="vid")]
                ])
            # Generating custom thumbnail and caption
            thumb_url = get_thumbnail(file)
            caption_text = get_caption(out_filename)
            await client.send_document(
                chat_id=message.chat.id,
                document=file.file_id,
                caption=caption_text,
                reply_markup=markup,
                thumb=thumb_url
            )

        except Exception as e:
            print(e)
            await message.reply_to_message.delete()
            await message.reply_text("**Error:** No extension found in the new file name.", reply_to_message_id=mg_id)
