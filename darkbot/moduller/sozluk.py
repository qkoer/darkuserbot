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
# Turkish word meaning. Only Turkish. Coded @By_Azade, dark uyarlaması @qulec
#

import requests

from html.parser import HTMLParser
from bs4 import BeautifulSoup

from darkbot.moduller.admin import get_user_from_event
from darkbot import CMD_HELP
from darkbot.events import extract_args, darkify

def searchTureng_tr(word):
    url="https://tureng.com/tr/turkce-ingilizce/"+word
    try:
        answer =  requests.get(url)
    except:
        return "No connection"
    soup = BeautifulSoup(answer.content, 'html.parser')
    trlated='{} Kelimesinin Anlamı/Anlamları:\n\n'.format(word)
    try:
        table = soup.find('table')
        td = table.find_all('td', attrs={'lang':'en'})
        # print(td)
        for val in td[0:5]:
            trlated = '{}👉  {}\n'.format(trlated , val.text )
        return trlated
    except:
        return "Sonuç bulunamadı"

@darkify(outgoing=True, pattern="^.tureng")
async def tureng(event): 
    input_str = extract_args(event)
    result = searchTureng_tr(input_str)
    await event.edit(result)

@darkify(outgoing=True, pattern="^.tdk")
async def tdk(event): 
    if event.fwd_from:
        return
    inp = extract_args(event)
    kelime = "https://sozluk.gov.tr/gts?ara={}".format(inp)
    headers = {"USER-AGENT": "dark"}
    response = requests.get(kelime, headers=headers).json()
    
    try:
        anlam_sayisi = response[0]['anlam_say']
        x = "TDK Sözlük\n\nKelime: **{}**\n".format(inp)
        for anlamlar in range(int(anlam_sayisi)):
            x += "👉{}\n".format(response[0]['anlamlarListe'][anlamlar]['anlam'])
            # print(x)
        await event.edit(x)
    except KeyError:
        await event.edit("`Kelime bulunamadı`")

CMD_HELP.update({
    "sozluk":
    ".tdk <kelime> .\
    \nKullanım: Verdiğiniz kelimeyi TDK Sözlükte arar.\n\n.tureng <kelime> .\
    \nKullanım: Verdiğiniz kelimeyi Tureng Sözlükte arar."
})
