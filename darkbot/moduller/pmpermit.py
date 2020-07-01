# Copyright (C) 2020 TeamDerUntergang.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

""" Kimin size özel mesaj gönderebileceğini kontrol altına almanızı sağlayan UserBot modülüdür. """

from telethon.tl.functions.contacts import BlockRequest, UnblockRequest
from telethon.tl.functions.messages import ReportSpamRequest
from telethon.tl.types import User
from sqlalchemy.exc import IntegrityError

from darkbot import (COUNT_PM, CMD_HELP, BOTLOG, BOTLOG_CHATID,
                     PM_AUTO_BAN, LASTMSG, LOGS, PM_UNAPPROVED)
from darkbot.events import darkify

# ========================= CONSTANTS ============================
DEF_UNAPPROVED_MSG = PM_UNAPPROVED or ("`Hey! Ben @quitarist in tasarladıgı bir yönetim botuyum.\n\n`"
                  "`Korkma Beni Kullanan kişi sana birazdan cevap verir.`"
                  "`Sahibimin aktif olmasını bekle lütfen.` \n\n "
                  "`Bildiğim kadarıyla o kafayı yemiş insanlara PM izni vermiyor.`")
# =================================================================
@darkify(incoming=True, disable_edited=True)
async def permitpm(event):
    UNAPPROVED_MSG = DEF_UNAPPROVED_MSG
    if 'PM_USER_MSG' in globals() and PM_USER_MSG:
        UNAPPROVED_MSG = PM_USER_MSG
    """ İzniniz olmadan size PM gönderenleri yasaklamak içindir. \
        Yazmaya devam eden kullanıcıları engeller. """
    if PM_AUTO_BAN:
        self_user = await event.client.get_me()
        if event.is_private and event.chat_id != 777000 and event.chat_id != self_user.id and not (
                await event.get_sender()).bot:
            try:
                from darkbot.moduller.sql_helper.pm_permit_sql import is_approved
                from darkbot.moduller.sql_helper.globals import gvarstatus
            except:
                return
            apprv = is_approved(event.chat_id)
            notifsoff = gvarstatus("NOTIF_OFF")

            # Bu bölüm basitçe akıl sağlığı kontrolüdür.
            # Eğer mesaj daha önceden onaylanmamış olarak gönderildiyse
            # flood yapmayı önlemek için unapprove mesajı göndermeyi durdurur.
            if not apprv and event.text != UNAPPROVED_MSG:
                if event.chat_id in LASTMSG:
                    prevmsg = LASTMSG[event.chat_id]
                    # Eğer önceden gönderilmiş mesaj farklıysa unapprove mesajı tekrardan gönderilir.
                    if event.text != prevmsg:
                        async for message in event.client.iter_messages(
                                event.chat_id,
                                from_user='me',
                                search=UNAPPROVED_MSG):
                            await message.delete()
                        await event.reply(UNAPPROVED_MSG)
                    LASTMSG.update({event.chat_id: event.text})
                else:
                    await event.reply(UNAPPROVED_MSG)
                    LASTMSG.update({event.chat_id: event.text})

                if notifsoff:
                    await event.client.send_read_acknowledge(event.chat_id)
                if event.chat_id not in COUNT_PM:
                    COUNT_PM.update({event.chat_id: 1})
                else:
                    COUNT_PM[event.chat_id] = COUNT_PM[event.chat_id] + 1

                if COUNT_PM[event.chat_id] > 4:
                    await event.respond(
                        "`Sen benim sahibimin PM'ini spamlıyorsun, bu benim hoşuma gitmiyor.`\n"
                        "`Şu an ENGELLENDIN ve SPAM olarak bildirildin, ileride değişiklik olmadığı sürece..`"
                    )

                    try:
                        del COUNT_PM[event.chat_id]
                        del LASTMSG[event.chat_id]
                    except KeyError:
                        if BOTLOG:
                            await event.client.send_message(
                                BOTLOG_CHATID,
                                "PM sayacı kafayı yemiş gibi, botu lütfen yeniden başlatın.",
                            )
                        LOGS.info(
                            "PM sayacı kafayı yemiş gibi, botu lütfen yeniden başlatın.")
                        return

                    await event.client(BlockRequest(event.chat_id))
                    await event.client(ReportSpamRequest(peer=event.chat_id))

                    if BOTLOG:
                        name = await event.client.get_entity(event.chat_id)
                        name0 = str(name.first_name)
                        await event.client.send_message(
                            BOTLOG_CHATID,
                            "[" + name0 + "](tg://user?id=" +
                            str(event.chat_id) + ")" +
                            " kişisi sadece bir hayal kırıklığı idi. PM'ni meşgul ettiği için engellendi.",
                        )

@darkify(disable_edited=True, outgoing=True)
async def auto_accept(event):
    """ İlk mesajı atan sizseniz otomatik olarak onaylanır. """
    UNAPPROVED_MSG = DEF_UNAPPROVED_MSG
    if 'PM_USER_MSG' in globals() and PM_USER_MSG:
        UNAPPROVED_MSG = PM_USER_MSG
    if not PM_AUTO_BAN:
        return
    self_user = await event.client.get_me()
    if event.is_private and event.chat_id != 777000 and event.chat_id != self_user.id and not (
            await event.get_sender()).bot:
        try:
            from darkbot.moduller.sql_helper.pm_permit_sql import approve, is_approved
        except:
            return

        chat = await event.get_chat()
        if isinstance(chat, User):
            if is_approved(event.chat_id) or chat.bot:
                return
            async for message in event.client.iter_messages(event.chat_id,
                                                            reverse=True,
                                                            limit=1):
                if message.message is not UNAPPROVED_MSG and message.from_id == self_user.id:
                    try:
                        approve(event.chat_id)
                    except IntegrityError:
                        return

                if is_approved(event.chat_id) and BOTLOG:
                    await event.client.send_message(
                        BOTLOG_CHATID,
                        "#OTOMATIK-ONAYLANDI\n" + "Kullanıcı: " +
                        f"[{chat.first_name}](tg://user?id={chat.id})",
                    )

@darkify(outgoing=True, pattern="^.notifoff$")
async def notifoff(noff_event):
    """ .notifoff komutu onaylanmamış kişilerden gelen PM lerden bildirim almamanızı sağlar. """
    try:
        from darkbot.moduller.sql_helper.globals import addgvar
    except:
        await noff_event.edit("`Bot Non-SQL modunda çalışıyor!!`")
        return
    addgvar("NOTIF_OFF", True)
    await noff_event.edit("`PM izni olmayan kullanıcıların bildirimleri sessize alındı!`")

@darkify(outgoing=True, pattern="^.notifon$")
async def notifon(non_event):
    """ .notifon komutu onaylanmamış kişilerden gelen PM lerden bildirim almanızı sağlar. """
    try:
        from darkbot.moduller.sql_helper.globals import delgvar
    except:
        await non_event.edit("`Bot Non-SQL modunda çalışıyor!!`")
        return
    delgvar("NOTIF_OFF")
    await non_event.edit("`PM izni olmayan kullanıcıarın bildirim göndermesine izin verildi!`")

@darkify(outgoing=True, pattern="^.approve$")
async def approvepm(apprvpm):
    UNAPPROVED_MSG = DEF_UNAPPROVED_MSG
    if 'PM_USER_MSG' in globals() and PM_USER_MSG:
        UNAPPROVED_MSG = PM_USER_MSG
    """ .approve komutu herhangi birine PM atabilme izni verir. """
    try:
        from darkbot.moduller.sql_helper.pm_permit_sql import approve
    except:
        await apprvpm.edit("`Bot Non-SQL modunda çalışıyor!!`")
        return

    if apprvpm.reply_to_msg_id:
        reply = await apprvpm.get_reply_message()
        replied_user = await apprvpm.client.get_entity(reply.from_id)
        aname = replied_user.id
        name0 = str(replied_user.first_name)
        uid = replied_user.id

    else:
        aname = await apprvpm.client.get_entity(apprvpm.chat_id)
        if not isinstance(aname, User):
            await apprvpm.edit("`Şu an bir PM'de değilsin ve birinin mesajını alıntılamadın.`")
            return
        name0 = aname.first_name 
        uid = apprvpm.chat_id

    try:
        approve(uid)
    except IntegrityError:
        await apprvpm.edit("`Kullanıcı halihazırda PM gönderebiliyor olmalıdır.`")
        return

    await apprvpm.edit(f"[{name0}](tg://user?id={uid}) `kişisi PM gönderebilir!`")

    async for message in apprvpm.client.iter_messages(apprvpm.chat_id,
                                                      from_user='me',
                                                      search=UNAPPROVED_MSG):
        await message.delete()

    if BOTLOG:
        await apprvpm.client.send_message(
            BOTLOG_CHATID,
            "#ONAYLANDI\n" + "Kullanıcı: " + f"[{name0}](tg://user?id={uid})",
        )

@darkify(outgoing=True, pattern="^.disapprove$")
async def disapprovepm(disapprvpm):
    try:
        from darkbot.moduller.sql_helper.pm_permit_sql import dissprove
    except:
        await disapprvpm.edit("`Bot Non-SQL modunda çalışıyor!!`")
        return

    if disapprvpm.reply_to_msg_id:
        reply = await disapprvpm.get_reply_message()
        replied_user = await disapprvpm.client.get_entity(reply.from_id)
        aname = replied_user.id
        name0 = str(replied_user.first_name)
        dissprove(replied_user.id)
    else:
        dissprove(disapprvpm.chat_id)
        aname = await disapprvpm.client.get_entity(disapprvpm.chat_id)
        if not isinstance(aname, User):
            await disapprvpm.edit("`Şu an bir PM'de değilsin ve birinin mesajını alıntılamadın.`")
            return
        name0 = str(aname.first_name)

    await disapprvpm.edit(
        f"[{name0}](tg://user?id={disapprvpm.chat_id}) `kişisinin PM atma izni kaldırıldı.`")

    if BOTLOG:
        await disapprvpm.client.send_message(
            BOTLOG_CHATID,
            f"[{name0}](tg://user?id={disapprvpm.chat_id})"
            " kişisinin PM atma izni kaldırıldı.",
        )

@darkify(outgoing=True, pattern="^.block$")
async def blockpm(block):
    """ .block komutu insanları engellemenizi sağlar. """
    if block.reply_to_msg_id:
        reply = await block.get_reply_message()
        replied_user = await block.client.get_entity(reply.from_id)
        aname = replied_user.id
        name0 = str(replied_user.first_name)
        await block.client(BlockRequest(replied_user.id))
        await block.edit("`Engellendin!`")
        uid = replied_user.id
    else:
        await block.client(BlockRequest(block.chat_id))
        aname = await block.client.get_entity(block.chat_id)
        if not isinstance(aname, User):
            await apprvpm.edit("`Şu an bir PM'de değilsin ve birinin mesajını alıntılamadın.`")
            return
        await block.edit("`Engellendin!`")
        name0 = str(aname.first_name)
        uid = block.chat_id

    try:
        from darkbot.moduller.sql_helper.pm_permit_sql import dissprove
        dissprove(uid)
    except:
        pass

    if BOTLOG:
        await block.client.send_message(
            BOTLOG_CHATID,
            "#ENGELLENDI\n" + "Kullanıcı: " + f"[{name0}](tg://user?id={uid})",
        )

@darkify(outgoing=True, pattern="^.unblock$")
async def unblockpm(unblock):
    """ .unblock komutu insanların size yeniden PM atabilmelerini sağlar. """
    if unblock.reply_to_msg_id:
        reply = await unblock.get_reply_message()
        replied_user = await unblock.client.get_entity(reply.from_id)
        name0 = str(replied_user.first_name)
        await unblock.client(UnblockRequest(replied_user.id))
        await unblock.edit("`Engelin kaldırıldı.`")

    if BOTLOG:
        await unblock.client.send_message(
            BOTLOG_CHATID,
            f"[{name0}](tg://user?id={replied_user.id})"
            " kişisinin engeli kaldırıldı.",
        )

@darkify(outgoing=True, pattern="^.(rem|set)permitmsg")
async def set_permit_msg(msg):
    txt = msg.text.split(' ', 1)
    act = txt[0][1:4]
    global PM_USER_MSG
    if act == 'rem':
        PM_USER_MSG = None
        UNAPPROVED_MSG = DEF_UNAPPROVED_MSG
        await msg.edit(f'`Mesaj sıfırlandı. Artık, ` {UNAPPROVED_MSG}')
    elif len(txt) < 2:
        await msg.edit('`Mesaj belirtmediniz.`')
    else:
        PM_USER_MSG = UNAPPROVED_MSG = txt[1]
        await msg.edit(f'`Mesaj değiştirildi. Artık, ` {UNAPPROVED_MSG}')

CMD_HELP.update({
    "pmpermit":
    "\
\n\n.approve\
\nKullanım: Yanıt verilen kullanıcıya PM atma izni verilir.\
\n\n.disapprove\
\nKullanım: Yanıt verilen kullanıcının PM onayını kaldırır.\
\n\n.setpermitmsg\
\nPM izin mesajınızı (Hey! Bu bir bot. Endişelenme ...) değiştirir.\
\nKullanım: .setpermitmsg <metin>\
\n\n.rempermitmsg\
\nPM izin mesajınızı varsayılana döndürür.\
\n\n.block\
\nKullanım: Bir kullanıcıyı engeller.\
\n\n.unblock\
\nKullanımı: Engellenmiş kullanıcının engelini kaldırır.\
\n\n.notifoff\
\nKullanım: Onaylanmamış özel mesajların bildirimlerini temizler ya da devre dışı bırakır.\
\n\n.notifon\
\nKullanım: Onaylanmamış özel mesajların bildirim göndermesine izin verir."
})
