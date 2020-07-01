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

from asyncio import sleep
from pylast import User, WSError, LastFMNetwork, md5
from re import sub
from urllib import parse
from os import environ
from sys import setrecursionlimit

from telethon.errors import AboutTooLongError
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import User as Userbot
from telethon.errors.rpcerrorlist import FloodWaitError

from darkbot import CMD_HELP, BOTLOG, BOTLOG_CHATID, DEFAULT_BIO, BIO_PREFIX, lastfm, LASTFM_USERNAME, bot
from darkbot.events import extract_args, darkify

# =================== CONSTANT ===================
LFM_BIO_ENABLED = "```last.fm'de oynatılan müziği biyografiye ekleme aktif.```"
LFM_BIO_DISABLED = "```last.fm'de oynatılan müziği biyografiye ekleme devre dışı. Biyografi varsayılana çevrildi.```"
LFM_BIO_RUNNING = "```last.fm'de oynatılan müziği biyografiye ekleme halihazırda aktif.```"
LFM_BIO_ERR = "```Bir seçenek belirtilmedi.```"
LFM_LOG_ENABLED = "```last.fm bot logları şu an aktif.```"
LFM_LOG_DISABLED = "```last.fm bot logları devre dışı bırakıldı.```"
LFM_LOG_ERR = "```Bir seçenek belirtilmedi.```"
ERROR_MSG = "```last.fm modulü beklenmedik bir hatadan dolayı durduruldu.```"

ARTIST = 0
SONG = 0
USER_ID = 0

if BIO_PREFIX:
    BIOPREFIX = BIO_PREFIX
else:
    BIOPREFIX = None

LASTFMCHECK = False
RUNNING = False
LastLog = False
# ================================================

@darkify(outgoing=True, pattern="^.lastfm")
async def last_fm(lastFM):
    """ .lastfm komutu last.fm'den verileri çeker. """
    await lastFM.edit("İşleniyor...")
    preview = None
    playing = User(LASTFM_USERNAME, lastfm).get_now_playing()
    username = f"https://www.last.fm/user/{LASTFM_USERNAME}"
    if playing :
        try:
            image = User(LASTFM_USERNAME,
                         lastfm).get_now_playing().get_cover_image()
        except IndexError:
            image = None
            pass
        tags = await gettags(isNowPlaying=True, playing=playing)
        rectrack = parse.quote_plus(f"{playing}")
        rectrack = sub("^", "https://www.youtube.com/results?search_query=",
                       rectrack)
        if image:
            output = f"[‎]({image})[{LASTFM_USERNAME}]({username}) __şu an şunu dinliyor:__\n\n• [{playing}]({rectrack})\n`{tags}`"
            preview = True
        else:
            output = f"[{LASTFM_USERNAME}]({username}) __şu an şunu dinliyor:__\n\n• [{playing}]({rectrack})\n`{tags}`"
    else:
        recent = User(LASTFM_USERNAME, lastfm).get_recent_tracks(limit=3)
        playing = User(LASTFM_USERNAME, lastfm).get_now_playing()
        output = f"[{LASTFM_USERNAME}]({username}) __en son şunu dinledi:__\n\n"
        for i, track in enumerate(recent):
            printable = await artist_and_song(track)
            tags = await gettags(track)
            rectrack = parse.quote_plus(str(printable))
            rectrack = sub("^",
                           "https://www.youtube.com/results?search_query=",
                           rectrack)
            output += f"• [{printable}]({rectrack})\n"
            if tags:
                output += f"`{tags}`\n\n"
    if preview :
        await lastFM.edit(f"{output}", parse_mode='md', link_preview=True)
    else:
        await lastFM.edit(f"{output}", parse_mode='md')


async def gettags(track=None, isNowPlaying=None, playing=None):
    if isNowPlaying:
        tags = playing.get_top_tags()
        arg = playing
        if not tags:
            tags = playing.artist.get_top_tags()
    else:
        tags = track.track.get_top_tags()
        arg = track.track
    if not tags:
        tags = arg.artist.get_top_tags()
    tags = "".join([" #" + t.item.__str__() for t in tags[:5]])
    tags = sub("^ ", "", tags)
    tags = sub(" ", "_", tags)
    tags = sub("_#", " #", tags)
    return tags


async def artist_and_song(track):
    return f"{track.track}"


async def get_curr_track(lfmbio):
    global ARTIST
    global SONG
    global LASTFMCHECK
    global RUNNING
    global USER_ID
    oldartist = ""
    oldsong = ""
    while LASTFMCHECK:
        try:
            if USER_ID == 0:
                USER_ID = (await lfmbio.client.get_me()).id
            user_info = await bot(GetFullUserRequest(USER_ID))
            RUNNING = True
            playing = User(LASTFM_USERNAME, lastfm).get_now_playing()
            SONG = playing.get_title()
            ARTIST = playing.get_artist()
            oldsong = environ.get("oldsong", None)
            oldartist = environ.get("oldartist", None)
            if playing  and SONG != oldsong and ARTIST != oldartist:
                environ["oldsong"] = str(SONG)
                environ["oldartist"] = str(ARTIST)
                if BIOPREFIX:
                    lfmbio = f"{BIOPREFIX} 🎧: {ARTIST} - {SONG}"
                else:
                    lfmbio = f"🎧: {ARTIST} - {SONG}"
                try:
                    if BOTLOG and LastLog:
                        await bot.send_message(
                            BOTLOG_CHATID,
                            f"Biyografi şuna çevrildi: \n{lfmbio}")
                    await bot(UpdateProfileRequest(about=lfmbio))
                except AboutTooLongError:
                    short_bio = f"🎧: {SONG}"
                    await bot(UpdateProfileRequest(about=short_bio))
            else:
                if not playing and user_info.about != DEFAULT_BIO:
                    await sleep(6)
                    await bot(UpdateProfileRequest(about=DEFAULT_BIO))
                    if BOTLOG and LastLog:
                        await bot.send_message(
                            BOTLOG_CHATID, f"Biyografi geri şuna çevrildi: \n{DEFAULT_BIO}")
        except AttributeError:
            try:
                if user_info.about != DEFAULT_BIO:
                    await sleep(6)
                    await bot(UpdateProfileRequest(about=DEFAULT_BIO))
                    if BOTLOG and LastLog:
                        await bot.send_message(
                            BOTLOG_CHATID, f"Biyografi geri şuna çevrildi \n{DEFAULT_BIO}")
            except FloodWaitError as err:
                if BOTLOG and LastLog:
                    await bot.send_message(BOTLOG_CHATID,
                                           f"Biyografi değiştirilirken hata oluştu :\n{err}")
        except FloodWaitError as err:
            if BOTLOG and LastLog:
                await bot.send_message(BOTLOG_CHATID,
                                       f"Biyografi değiştirilirken hata oluştu :\n{err}")
        except WSError as err:
            if BOTLOG and LastLog:
                await bot.send_message(BOTLOG_CHATID,
                                       f"Biyografi değiştirilirken hata oluştu: \n{err}")
        await sleep(2)
    RUNNING = False

@darkify(outgoing=True, pattern=r"^.lastbio")
async def lastbio(lfmbio):
    arg = extract_args(lfmbio).lower()
    global LASTFMCHECK
    global RUNNING
    if arg == "on":
        setrecursionlimit(700000)
        if not LASTFMCHECK:
            LASTFMCHECK = True
            environ["errorcheck"] = "0"
            await lfmbio.edit(LFM_BIO_ENABLED)
            await sleep(4)
            await get_curr_track(lfmbio)
        else:
            await lfmbio.edit(LFM_BIO_RUNNING)
    elif arg == "off":
        LASTFMCHECK = False
        RUNNING = False
        await bot(UpdateProfileRequest(about=DEFAULT_BIO))
        await lfmbio.edit(LFM_BIO_DISABLED)
    else:
        await lfmbio.edit(LFM_BIO_ERR)

@darkify(outgoing=True, pattern=r"^.lastlog")
async def lastlog(lstlog):
    arg = extract_args(lstlog).lower()
    global LastLog
    LastLog = False
    if arg == "on":
        LastLog = True
        await lstlog.edit(LFM_LOG_ENABLED)
    elif arg == "off":
        LastLog = False
        await lstlog.edit(LFM_LOG_DISABLED)
    else:
        await lstlog.edit(LFM_LOG_ERR)

CMD_HELP.update({
    'lastfm':
    ".lastfm\
    \nKullanım: Şu anlık oynatılan parça ya da en son oynatılan parça gösterilir.\
    \n\nlastbio: .lastbio <on/off>\
    \nKullanım: last.fm'deki şu an oynatılan parça gösterimi etkinleştirilir/devre dışı bırakılır.\
    \n\nlastlog: .lastlog <on/off>\
    \nKullanım: last.fm biyografi loglamasını etkinleştirir/devre dışı bırakır."
})
