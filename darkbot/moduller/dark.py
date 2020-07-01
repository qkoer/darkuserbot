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

""" UserBot yardım komutu """

from darkbot import CMD_HELP
from darkbot.events import extract_args, darkify

@darkify(outgoing=True, pattern="^.dark")
async def dark(event):
    """ .dark komutu için """
    args = extract_args(event).lower()
    if args:
        if args in CMD_HELP:
            await event.edit(str(CMD_HELP[args]))
        else:
            await event.edit("Lütfen bir dark modülü adı belirtin.")
    else:
        await event.edit("Lütfen hangi dark modülü için yardım istediğinizi belirtin !!\
            \nKullanım: .dark <modül adı>")
        string = "**[dark UserBot](https://telegram.dog/karanliksohbet) Yüklü Modüller:**\n↓  ↓  ↓  ↓\n"
        for i in CMD_HELP:
            string += "🔸 - `" + str(i)
            string += "` \n"
        await event.reply(string)
