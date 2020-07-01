# Copyright (C) 2020 TeamDerUntergang.
#
# darkUserBot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# darkUserBot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Prakasaka tarafından portlanmıştır.
#

import io
import os
import requests

from telethon.tl.types import MessageMediaPhoto

from darkbot.events import extract_args, darkify
from darkbot import CMD_HELP, REM_BG_API_KEY, TEMP_DOWNLOAD_DIRECTORY

@darkify(outgoing=True, pattern="^.rbg")
async def kbg(remob):
    """ .rbg komutu ile görüntünün arka planını kaldırın """
    if not REM_BG_API_KEY:
        await remob.edit(
            "`Hata: Remove.BG API key eksik! Lütfen ekleyin.`"
        )
        return
    input_str = extract_args(remob)
    message_id = remob.message.id
    if remob.reply_to_msg_id:
        message_id = remob.reply_to_msg_id
        reply_message = await remob.get_reply_message()
        await remob.edit("`İşleniyor..`")
        try:
            if isinstance(
                    reply_message.media, MessageMediaPhoto
            ) or "image" in reply_message.media.document.mime_type.split('/'):
                downloaded_file_name = await remob.client.download_media(
                    reply_message, TEMP_DOWNLOAD_DIRECTORY)
                await remob.edit("`Bu görüntüden arka plan kaldırılıyor..`")
                output_file_name = await ReTrieveFile(downloaded_file_name)
                os.remove(downloaded_file_name)
            else:
                await remob.edit("`Bunun arka planını nasıl kaldırabilirim ?`"
                                 )
        except Exception as e:
            await remob.edit(str(e))
            return
    elif input_str:
        await remob.edit(
            f"`Çevrimiçi görüntüden arka planı kaldırma`\n{input_str}")
        output_file_name = await ReTrieveURL(input_str)
    else:
        await remob.edit("`Arka planı kaldırmak için bir şeye ihtiyacım var.`")
        return
    contentType = output_file_name.headers.get("content-type")
    if "image" in contentType:
        with io.BytesIO(output_file_name.content) as remove_bg_image:
            remove_bg_image.name = "removed_bg.png"
            await remob.client.send_file(
                remob.chat_id,
                remove_bg_image,
                caption="Remove.bg kullanılarak arka plan kaldırıldı",
                force_document=True,
                reply_to=message_id)
            await remob.delete()
    else:
        await remob.edit("**Hata (Geçersiz API key olduğunu tamhin ediyorum..)**\n`{}`".format(
            output_file_name.content.decode("UTF-8")))


async def ReTrieveFile(input_file_name):
    headers = {
        "X-API-Key": REM_BG_API_KEY,
    }
    files = {
        "image_file": (input_file_name, open(input_file_name, "rb")),
    }
    r = requests.post("https://api.remove.bg/v1.0/removebg",
                      headers=headers,
                      files=files,
                      allow_redirects=True,
                      stream=True)
    return r


async def ReTrieveURL(input_url):
    headers = {
        "X-API-Key": REM_BG_API_KEY,
    }
    data = {"image_url": input_url}
    r = requests.post("https://api.remove.bg/v1.0/removebg",
                      headers=headers,
                      data=data,
                      allow_redirects=True,
                      stream=True)
    return r

CMD_HELP.update({
    "rbg":
    ".rbg <Resim bağlantısı> veya herhangi bir görüntüye cevap verin (Uyarı: çıkartmalar üzerinde çalışmaz.)\
\nKullanım: remove.bg API kullanarak görüntülerin arka planını kaldırır."
})
