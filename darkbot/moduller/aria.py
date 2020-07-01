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

import aria2p

from asyncio import sleep
from os import system
from requests import get

from darkbot import LOGS, CMD_HELP
from darkbot.events import extract_args, darkify

# Gelişmiş indirme hızları için en iyi trackerları çağırır, bunun için K-E-N-W-A-Y'e teşekkürler.
trackers_list = get(
    'https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_best.txt'
).text.replace('\n\n', ',')
trackers = f"[{trackers_list}]"

cmd = f"aria2c \
--enable-rpc \
--rpc-listen-all=false \
--rpc-listen-port 6800 \
--max-connection-per-server=10 \
--rpc-max-request-size=1024M \
--seed-time=0.01 \
--max-upload-limit=5K \
--max-concurrent-downloads=5 \
--min-split-size=10M \
--follow-torrent=mem \
--split=10 \
--bt-tracker={trackers} \
--daemon=true \
--allow-overwrite=true"

aria2_is_running = system(cmd)

aria2 = aria2p.API(aria2p.Client(host="http://localhost", port=6800,
                                 secret=""))

@darkify(outgoing=True, pattern="^.amag")
async def magnet_download(event):
    magnet_uri = extract_args(event)
    # Magnet URI'ı kuyruğa ekler.
    try:
        download = aria2.add_magnet(magnet_uri)
    except Exception as e:
        LOGS.info(str(e))
        await event.edit("Hata:\n`" + str(e) + "`")
        return
    gid = download.gid
    await check_progress_for_dl(gid=gid, event=event, previous=None)
    await sleep(5)
    new_gid = await check_metadata(gid)
    await check_progress_for_dl(gid=new_gid, event=event, previous=None)

@darkify(outgoing=True, pattern="^.ator")
async def torrent_download(event):
    torrent_file_path = extract_args(event)
    # Torrent'i kuyruğa ekler.
    try:
        download = aria2.add_torrent(torrent_file_path,
                                     uris=None,
                                     options=None,
                                     position=None)
    except Exception as e:
        await event.edit(str(e))
        return
    gid = download.gid
    await check_progress_for_dl(gid=gid, event=event, previous=None)

@darkify(outgoing=True, pattern="^.aurl")
async def amagnet_download(event):
    uri = [extract_args(event)]
    try:  # URL'yi kuyruğa ekler.
        download = aria2.add_uris(uri, options=None, position=None)
    except Exception as e:
        LOGS.info(str(e))
        await event.edit("Hata :\n`{}`".format(str(e)))
        return
    gid = download.gid
    await check_progress_for_dl(gid=gid, event=event, previous=None)
    file = aria2.get_download(gid)
    if file.followed_by_ids:
        new_gid = await check_metadata(gid)
        await progress_status(gid=new_gid, event=event, previous=None)

@darkify(outgoing=True, pattern="^.aclear")
async def remove_all(event):
    await event.edit("`Devam eden indirmeler temizleniyor... `")
    try:
        removed = aria2.remove_all(force=True)
        aria2.purge_all()
    except:
        pass
    if not removed:  # Eğer API False olarak dönerse sistem vasıtasıyla kaldırılmaya çalışılır.
        system("aria2p remove-all")
    await event.edit("`Tüm indirilenler başarıyla temizlendi.`")

@darkify(outgoing=True, pattern="^.apause")
async def pause_all(event):
    # Tüm devam eden indirmeleri duraklatır.
    await event.edit("`İndirmeler duraklatılıyor...`")
    aria2.pause_all(force=True)
    await event.edit("`Devam eden indirmeler başarıyla durduruldu.`")

@darkify(outgoing=True, pattern="^.aresume")
async def resume_all(event):
    await event.edit("`İndirmeler devam ettiriliyor...`")
    aria2.resume_all()
    await event.edit("`İndirmeler devam ettirildi.`")
    await sleep(2.5)
    await event.delete()

@darkify(outgoing=True, pattern="^.ashow")
async def show_all(event):
    output = "output.txt"
    downloads = aria2.get_downloads()
    msg = ""
    for download in downloads:
        msg = msg + "Dosya: `" + str(download.name) + "`\nHız: " + str(
            download.download_speed_string()) + "\nİşlem: " + str(
                download.progress_string()) + "\nToplam Boyut: " + str(
                    download.total_length_string()) + "\nDurum: " + str(
                        download.status) + "\nTahmini bitiş:  " + str(
                            download.eta_string()) + "\n\n"
    if len(msg) <= 4096:
        await event.edit("`Devam eden indirmeler: `\n" + msg)
        await sleep(5)
        await event.delete()
    else:
        await event.edit("`Çıktı çok büyük, bu sebepten dolayı dosya olarak gönderiliyor...`")
        with open(output, 'w') as f:
            f.write(msg)
        await sleep(2)
        await event.delete()
        await event.client.send_file(
            event.chat_id,
            output,
            force_document=True,
            supports_streaming=False,
            allow_cache=False,
            reply_to=event.message.id,
        )


async def check_metadata(gid):
    file = aria2.get_download(gid)
    new_gid = file.followed_by_ids[0]
    LOGS.info("GID " + gid + " şu değerden şu değere değiştiriliyor:" + new_gid)
    return new_gid


async def check_progress_for_dl(gid, event, previous):
    complete = None
    while not complete:
        file = aria2.get_download(gid)
        complete = file.is_complete
        try:
            if not complete and not file.error_message:
                msg = f"\nİndirilen dosya: `{file.name}`"
                msg += f"\nHız: {file.download_speed_string()}"
                msg += f"\nİşlem: {file.progress_string()}"
                msg += f"\nToplam Boyut: {file.total_length_string()}"
                msg += f"\nDurum: {file.status}"
                msg += f"\nTahmini bitiş: {file.eta_string()}"
                if msg != previous:
                    await event.edit(msg)
                    msg = previous
            else:
                LOGS.info(str(file.error_message))
                await event.edit(f"`{msg}`")
            await sleep(5)
            await check_progress_for_dl(gid, event, previous)
            file = aria2.get_download(gid)
            complete = file.is_complete
            if complete:
                await event.edit(f"Dosya başarıyla indirdi: `{file.name}`"
                                 )
                return False
        except Exception as e:
            if " not found" in str(e) or "'file'" in str(e):
                await event.edit("İndirme iptal edildi :\n`{}`".format(file.name))
                await sleep(2.5)
                await event.delete()
                return
            elif " depth exceeded" in str(e):
                file.remove(force=True)
                await event.edit(
                    "İndirme otomatik olarak iptal edildi:\n`{}`\nTorrent ya da link ölü."
                    .format(file.name))

CMD_HELP.update({
    "aria":
    ".aurl [URL] (ya da) .amag [Magnet Linki] (ya da) .ator [torrent dosyasının yolu]\
    \nKullanım: Bir dosyayı userbot sunucusuna indirir.\
    \n\n.apause (ya da) .aresume\
    \nKullanım: Devam eden indirmeyi durdurur ya da devam ettirir.\
    \n\n.aclear\
    \nKullanım: İndirme kuyruğunu temizler, devam eden tüm indirmeleri siler.\
    \n\n.ashow\
    \nKullanım: Devam eden indirmelerin durumunu gösterir."
})
