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

""" Userid, chatid ve log komutlarını içeren UserBot modülü """

from asyncio import sleep

from darkbot.moduller.admin import get_user_from_event
from darkbot import CMD_HELP, BOTLOG, BOTLOG_CHATID, bot
from darkbot.events import extract_args, darkify

@darkify(outgoing=True, pattern="^.id")
async def useridgetter(target):
    """ .id komutu belirlenen kullanıcının ID numarasını verir """
    message = await target.get_reply_message()
    if message:
        if not message.forward:
            user_id = message.sender.id
            if message.sender.username:
                name = "@" + message.sender.username
            else:
                name = "**" + message.sender.first_name + "**"
        else:
            user_id = message.forward.sender.id
            if message.forward.sender.username:
                name = "@" + message.forward.sender.username
            else:
                name = "*" + message.forward.sender.first_name + "*"
        await target.edit("**Kullanıcı Adı:** {} \n**Kullanıcı ID:** `{}`".format(
            name, user_id))
    else:
        await target.edit("`Bir mesajı alıntılamalısın.`")

@darkify(outgoing=True, pattern="^.link")
async def permalink(mention):
    """ .link komutu belirlenen kullanıcının profil bağlantısını metin ile ulaşılabilir hale getirir """
    user, custom = await get_user_from_event(mention)
    if not user:
        return
    if custom:
        await mention.edit(f"[{custom}](tg://user?id={user.id})")
    else:
        tag = user.first_name.replace("\u2060",
                                      "") if user.first_name else user.username
        await mention.edit(f"[{tag}](tg://user?id={user.id})")

@darkify(outgoing=True, pattern="^.chatid")
async def chatidgetter(chat):
    """ .chatid komutu belirlenen grubun ID numarasını verir """
    await chat.edit("Grup ID: `" + str(chat.chat_id) + "`")

@darkify(outgoing=True, pattern=r"^.log")
async def log(log_text):
    """ .log komutu seçilen mesajı günlük grubuna gönderir """
    args = extract_args(log_text)
    if BOTLOG:
        if log_text.reply_to_msg_id:
            reply_msg = await log_text.get_reply_message()
            await reply_msg.forward_to(BOTLOG_CHATID)
        elif len(args) > 1:
            user = f"#LOG / Grup ID: {log_text.chat_id}\n\n"
            textx = user + args
            await bot.send_message(BOTLOG_CHATID, textx)
        else:
            await log_text.edit("`Bununla ne yapmam gerekiyor ?`")
            return
        await log_text.edit("`Günlüğe Kaydedildi`")
    else:
        await log_text.edit("`Bu özellik etkin olması için günlük alma açık olmalıdır!`")
    await sleep(2)
    await log_text.delete()

@darkify(outgoing=True, pattern="^.kickme")
async def kickme(leave):
    """ .kickme komutu gruptan çıkmaya yarar """
    await leave.edit("Güle Güle ben gidiyorum 🤠")
    await leave.client.kick_participant(leave.chat_id, 'me')

@darkify(outgoing=True, pattern="^.unmutechat")
async def unmute_chat(unm_e):
    """ .unmutechat komutu susturulmuş grubun sesini açar """
    try:
        from darkbot.moduller.sql_helper.keep_read_sql import unkread
    except AttributeError:
        await unm_e.edit('`SQL dışı modda çalışıyor!`')
        return
    unkread(str(unm_e.chat_id))
    await unm_e.edit("```Sohbetin sesi açıldı```")
    await sleep(2)
    await unm_e.delete()

@darkify(outgoing=True, pattern="^.mutechat")
async def mute_chat(mute_e):
    """ .mutechat komutu grubu susturur """
    try:
        from darkbot.moduller.sql_helper.keep_read_sql import kread
    except AttributeError:
        await mute_e.edit("`SQL dışı modda çalışıyor!`")
        return
    await mute_e.edit(str(mute_e.chat_id))
    kread(str(mute_e.chat_id))
    await mute_e.edit("`Sohbet susturuldu!`")
    await sleep(2)
    await mute_e.delete()
    if BOTLOG:
        await mute_e.client.send_message(
            BOTLOG_CHATID,
            str(mute_e.chat_id) + " susturuldu.")

@darkify(incoming=True, disable_errors=True)
async def keep_read(message):
    """ Mute mantığı. """
    try:
        from darkbot.moduller.sql_helper.keep_read_sql import is_kread
    except AttributeError:
        return
    kread = is_kread()
    if kread:
        for i in kread:
            if i.groupid == str(message.chat_id):
                await message.client.send_read_acknowledge(message.chat_id)

# Regex-Ninja modülü için teşekkürler @Kandnub
regexNinja = False

@darkify(outgoing=True, pattern="^s/")
async def sedNinja(event):
    """Regex-ninja modülü için, s/ ile başlayan otomatik silme komutu"""
    if regexNinja:
        await sleep(.5)
        await event.delete()

@darkify(outgoing=True, pattern="^.regexninja")
async def sedNinjaToggle(event):
    """ Regex ninja modülünü etkinleştirir veya devre dışı bırakır. """
    global regexNinja
    args = extract_args(event)
    if len(args) < 1 or args not in ['on','off']:
        await event.edit("`Regexbot ninja modu konusunda ne yapacağımı bilmiyorum.`")
    else:
        if args == "on":
            regexNinja = True
            await event.edit("`Regexbot için ninja modu etkinleştirdi.`")
            await sleep(1)
            await event.delete()
        elif args == "off":
            regexNinja = False
            await event.edit("`Regexbot için ninja modu devre dışı bırakıldı.`")
            await sleep(1)
            await event.delete()

CMD_HELP.update({
    "chat":
    ".chatid\
\nKullanım: Belirlenen grubun ID numarasını verir\
\n\n.id\
\nKullanım: Belirlenen kullanıcının ID numarasını verir.\
\n\n.log\
\nKullanım: Yanıtlanan mesajı günlük grubuna gönderir.\
\n\n.kickme\
\nKullanım: Belirlenen gruptan ayrılmanızı sağlar.\
\n\n.unmutechat\
\nKullanım: Susturulmuş bir sohbetin sesini açar.\
\n\n.mutechat\
\nKullanım: Belirlenen grubu susturur.\
\n\n.link <kullanıcı adı/kullanıcı id> : <isteğe bağlı metin> (veya) herhangi birinin mesajına .link ile yanıt vererek <isteğe bağlı metin>\
\nKullanım: İsteğe bağlı özel metin ile kullanıcının profiline kalıcı bir bağlantı oluşturun.\
\n\n.regexninja on/off\
\nKullanım: Küresel olarak regex ninja modülünü etkinleştirir / devre dışı bırakır.\
\nRegex ninja modülü regex bot tarfından tetiklenen mesajları silmek için yardımcı olur."
})
