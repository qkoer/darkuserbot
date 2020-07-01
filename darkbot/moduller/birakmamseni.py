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
# Credits @Adem68

from requests import post
from fake_useragent import UserAgent
from darkbot import CMD_HELP
from darkbot.events import darkify

@darkify(pattern="^.b[ıi]rakmamseni$", outgoing=True)
async def birakmamseni(event):
    ua = UserAgent()
    url = 'https://birakmamseni.org/'
    path = 'api/counter'

    headers = {
        'User-Agent': '{}'.format(ua.random),
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': '{}'.format(url),
        'X-Requested-With': 'XMLHttpRequest',
    }

    try:
        response = post(url=url + path, headers=headers)
        count = response.json()['counter'].lstrip('0')
    except:
        await event.edit("`Bir hata oluştu.`")
        return

    sonuc = ("**⚫⚪ Bırakmam Seni Kampanyası Verileri ⚫⚪**\n\n" +
             "Şu an itibarıyla **BIRAKMAM SENİ** kampanyası kapsamında " +
             f"`{count}` 🖤🤍 adet destekte bulunuldu.\n" +
             f"\nHaydi sen de hemen **BÜYÜK BEŞİKTAŞ’IMIZA** 🦅 destek ol !\n" +
             f"\n[https://birakmamseni.org](https://birakmamseni.org/)\n" +
             f"`\n=============================\n`" +
             f"`SMS, Havale/Eft ve Posta Çeki kanalları ile gelen destekler periyodik olarak sayaca eklenmektedir.`\n" +
             f"`=============================`")

    await event.edit(sonuc)

CMD_HELP.update({
    "birakmamseni":
    ".birakmamseni \
    \nKullanım: Beşiktaş'ın Bırakmam Seni kampanyasına yapılan destek sayısını göstermektedir."
})
