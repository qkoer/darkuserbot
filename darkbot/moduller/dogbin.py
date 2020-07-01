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

""" Dogbin ile etkileşim için komutlar içeren UserBot modülü(https://del.dog)"""

import asyncio
import os

from requests import get, post, exceptions

from darkbot import BOTLOG, BOTLOG_CHATID, CMD_HELP, LOGS, TEMP_DOWNLOAD_DIRECTORY
from darkbot.events import extract_args, darkify

DOGBIN_URL = "https://del.dog/"

@darkify(outgoing=True, pattern=r"^.paste")
async def paste(pstl):
    """ .paste komutu metni doğrudan dogbine yapıştırır """
    dogbin_final_url = ""
    match = extract_args(pstl)
    reply_id = pstl.reply_to_msg_id

    if not match and not reply_id:
        await pstl.edit("`Elon Musk boşluğu yapıştıramayacağımı söyledi.`")
        return

    if match:
        message = match
    elif reply_id:
        message = (await pstl.get_reply_message())
        if message.media:
            downloaded_file_name = await pstl.client.download_media(
                message,
                TEMP_DOWNLOAD_DIRECTORY,
            )
            m_list = None
            with open(downloaded_file_name, "rb") as fd:
                m_list = fd.readlines()
            message = ""
            for m in m_list:
                message += m.decode("UTF-8") + "\r"
            os.remove(downloaded_file_name)
        else:
            message = message.message

    # Dogbin
    await pstl.edit("`Metin yapıştırılıyor . . .`")
    resp = post(DOGBIN_URL + "documents", data=message.encode('utf-8'))

    if resp.status_code == 200:
        response = resp.json()
        key = response['key']
        dogbin_final_url = DOGBIN_URL + key

        if response['isUrl']:
            reply_text = ("`Başarıyla yapıştırıldı!`\n\n"
                          f"`Kısaltılmış URL:` {dogbin_final_url}\n\n"
                          "`Orijinal (kısaltılmamış) URL`\n"
                          f"`Dogbin URL`: {DOGBIN_URL}v/{key}\n")
        else:
            reply_text = ("`Pasted successfully!`\n\n"
                          f"`Dogbin URL`: {dogbin_final_url}")
    else:
        reply_text = ("`Dogbine ulaşılamadı`")

    await pstl.edit(reply_text)
    if BOTLOG:
        await pstl.client.send_message(
            BOTLOG_CHATID,
            f"Dogbine metin yapıştırma başarıyla yürütüldü",
        )

@darkify(outgoing=True, pattern="^.getpaste")
async def get_dogbin_content(dog_url):
    """ .getpaste komutu dogbin url içeriğini aktarır """
    textx = await dog_url.get_reply_message()
    message = extract_args(dog_url)
    await dog_url.edit("`Dogbin içeriği alınıyor...`")

    if textx:
        message = str(textx.message)

    format_normal = f'{DOGBIN_URL}'
    format_view = f'{DOGBIN_URL}v/'

    if message.startswith(format_view):
        message = message[len(format_view):]
    elif message.startswith(format_normal):
        message = message[len(format_normal):]
    elif message.startswith("del.dog/"):
        message = message[len("del.dog/"):]
    else:
        await dog_url.edit("`Bu bir dogbin URL'si mi?`")
        return

    resp = get(f'{DOGBIN_URL}raw/{message}')

    try:
        resp.raise_for_status()
    except exceptions.HTTPError as HTTPErr:
        await dog_url.edit(
            "İstek başarısız bir durum kodu döndürdü.\n\n" + str(HTTPErr))
        return
    except exceptions.Timeout as TimeoutErr:
        await dog_url.edit("İstek zaman aşımına uğradı." + str(TimeoutErr))
        return
    except exceptions.TooManyRedirects as RedirectsErr:
        await dog_url.edit(
            "İstek, yapılandırılmış en fazla yönlendirme sayısını aştı." +
            str(RedirectsErr))
        return

    reply_text = "`Dogbin URL içeriği başarıyla getirildi!`\n\n`İçerik:` " + resp.text

    await dog_url.edit(reply_text)
    if BOTLOG:
        await dog_url.client.send_message(
            BOTLOG_CHATID,
            "Dogbin içerik aktarma başarıyla yürütüldü",
        )

CMD_HELP.update({
    "dogbin":
    ".paste <metin/yanıtlama>\
\nKullanım: Dogbin kullanarak yapıştırılmış veya kısaltılmış url oluşturma (https://del.dog/)\
\n\n.getpaste\
\nKullanım: Dogbin url içeriğini metne aktarır (https://del.dog/)"
})
