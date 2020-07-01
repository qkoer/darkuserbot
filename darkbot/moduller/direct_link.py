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

""" Çeşitli siteler için doğrudan bağlantı oluşturan UserBot modülü """

import re
import json
import requests
import urllib.parse

from os import popen, path, mkdir, chmod
from random import choice
from bs4 import BeautifulSoup
from humanize import naturalsize

from darkbot import CMD_HELP
from darkbot.events import extract_args, darkify
from asyncio import run as arun

async def load_bins():
    # CloudMail.ru ve MEGA.nz ayarlama
    if not path.exists('bin'):
        mkdir('bin')

    binaries = {
        "https://raw.githubusercontent.com/NaytSeyd/megadown/master/megadown":
        "bin/megadown",
        "https://raw.githubusercontent.com/NaytSeyd/cmrudl.py/master/cmrudl.py":
        "bin/cmrudl"
    }

    for binary, pth in binaries.items():
        with open(pth, 'wb') as load:
            load.write(requests.get(binary).content)
        chmod(pth, 0o755)

arun(load_bins())

@darkify(outgoing=True, pattern=r"^.direct")
async def direct_link_generator(request):
    """ doğrudan bağlantı oluşturma """
    await request.edit("`İşleniyor...`")
    textx = await request.get_reply_message()
    message = extract_args(request)
    if message:
        pass
    elif textx:
        message = textx.text
    else:
        await request.edit("`Kullanım: .direct <link>`")
        return
    reply = ''
    links = re.findall(r'\bhttps?://.*\.\S+', message)
    if not links:
        reply = "`Link bulunamadı!`"
        await request.edit(reply)
    for link in links:
        if 'drive.google.com' in link:
            reply += gdrive(link)
        elif 'zippyshare.com' in link:
            reply += zippy_share(link)
        elif 'mega.' in link:
            reply += mega_dl(link)            
        elif 'yadi.sk' in link:
            reply += yandex_disk(link)
        elif 'cloud.mail.ru' in link:
            reply += cm_ru(link)
        elif 'mediafire.com' in link:
            reply += mediafire(link)
        elif 'sourceforge.net' in link:
            reply += sourceforge(link)
        elif 'osdn.net' in link:
            reply += osdn(link)
        elif 'github.com' in link:
            reply += github(link)
        elif 'androidfilehost.com' in link:
            reply += androidfilehost(link)
        else:
            reply += re.findall(r"\bhttps?://(.*?[^/]+)",
                                link)[0] + 'desteklenmiyor'
    await request.edit(reply)

def gdrive(url: str) -> str:
    """ gdrive doğrudan bağlantı oluşturma """
    drive = 'https://drive.google.com'
    try:
        link = re.findall(r'\bhttps?://drive\.google\.com\S+', url)[0]
    except IndexError:
        reply = "`Google Drive linki bulunamadı`\n"
        return reply
    file_id = ''
    reply = ''
    if link.find("view") != -1:
        file_id = link.split('/')[-2]
    elif link.find("open?id=") != -1:
        file_id = link.split("open?id=")[1].strip()
    elif link.find("uc?id=") != -1:
        file_id = link.split("uc?id=")[1].strip()
    url = f'{drive}/uc?export=download&id={file_id}'
    download = requests.get(url, stream=True, allow_redirects=False)
    cookies = download.cookies
    try:
        # Küçük dosya boyutu durumunda, Google doğrudan indirir
        dl_url = download.headers["location"]
        if 'accounts.google.com' in dl_url:  # Gizli dosya
            reply += '`Link herkese açık değil!`\n'
            return reply
        name = 'Doğrudan İndirme Linki'
    except KeyError:
        page = BeautifulSoup(download.content, 'html.parser')
        export = drive + page.find('a', {'id': 'uc-download-link'}).get('href')
        name = page.find('span', {'class': 'uc-name-size'}).text
        response = requests.get(export,
                                stream=True,
                                allow_redirects=False,
                                cookies=cookies)
        dl_url = response.headers['location']
        if 'accounts.google.com' in dl_url:
            reply += 'Link herkese açık değil!'
            return reply
    reply += f'[{name}]({dl_url})\n'
    return reply

def zippy_share(url: str) -> str:
    """ ZippyShare doğrudan link oluşturma
    https://github.com/LameLemon/ziggy taban alınmıştır """
    reply = ''
    dl_url = ''
    try:
        link = re.findall(r'\bhttps?://.*zippyshare\.com\S+', url)[0]
    except IndexError:
        reply = "`ZippyShare linki bulunamadı`\n"
        return reply
    session = requests.Session()
    base_url = re.search('http.+.com', link).group()
    response = session.get(link)
    page_soup = BeautifulSoup(response.content, 'html.parser')
    scripts = page_soup.find_all("script", {"type": "text/javascript"})
    for script in scripts:
        if "getElementById('dlbutton')" in script.text:
            url_raw = re.search(r'= (?P<url>\".+\" \+ (?P<math>\(.+\)) .+);',
                                script.text).group('url')
            math = re.search(r'= (?P<url>\".+\" \+ (?P<math>\(.+\)) .+);',
                             script.text).group('math')
            dl_url = url_raw.replace(math, '"' + str(eval(math)) + '"')
            break
    dl_url = base_url + eval(dl_url)
    name = urllib.parse.unquote(dl_url.split('/')[-1])
    reply += f'[{name}]({dl_url})\n'
    return reply

def yandex_disk(url: str) -> str:
    """ Yandex.Disk doğrudan link oluşturma
    https://github.com/wldhx/yadisk-direct taban alınmıştır """
    reply = ''
    try:
        link = re.findall(r'\bhttps?://.*yadi\.sk\S+', url)[0]
    except IndexError:
        reply = "`Yandex.Disk linki bulunamadı`\n"
        return reply
    api = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={}'
    try:
        dl_url = requests.get(api.format(link)).json()['href']
        name = dl_url.split('filename=')[1].split('&disposition')[0]
        reply += f'[{name}]({dl_url})\n'
    except KeyError:
        reply += '`Hata: Dosya bulunamadı / İndirme limiti aşılmıştır`\n'
        return reply
    return reply

def mega_dl(url: str) -> str:
    """ MEGA.nz direct doğrudan link oluşturma
    https://github.com/tonikelope/megadown taban alınmıştır """
    reply = ''
    try:
        link = re.findall(r'\bhttps?://.*mega.*\.nz\S+', url)[0]
    except IndexError:
        reply = "`MEGA.nz linki bulunamadı`\n"
        return reply
    command = f'bin/megadown -q -m {link}'
    result = popen(command).read()
    try:
        data = json.loads(result)
    except json.JSONDecodeError:
        reply += "`Hata: link çıkarılamıyor`\n"
        return reply
    dl_url = data['url']
    name = data['file_name']
    size = naturalsize(int(data['file_size']))
    reply += f'[{name} ({size})]({dl_url})\n'
    return reply

def cm_ru(url: str) -> str:
    """ cloud.mail.ru doğrudan link oluşturma
    https://github.com/JrMasterModelBuilder/cmrudl.py taban alınmıştır """
    reply = ''
    try:
        link = re.findall(r'\bhttps?://.*cloud\.mail\.ru\S+', url)[0]
    except IndexError:
        reply = "`cloud.mail.ru linki bulunamadı`\n"
        return reply
    command = f'bin/cmrudl -s {link}'
    result = popen(command).read()
    result = result.splitlines()[-1]
    try:
        data = json.loads(result)
    except json.decoder.JSONDecodeError:
        reply += "`Hata: link çıkarılamıyor`\n"
        return reply
    dl_url = data['download']
    name = data['file_name']
    size = naturalsize(int(data['file_size']))
    reply += f'[{name} ({size})]({dl_url})\n'
    return reply

def mediafire(url: str) -> str:
    """ MediaFire doğrudan link oluşturma """
    try:
        link = re.findall(r'\bhttps?://.*mediafire\.com\S+', url)[0]
    except IndexError:
        reply = "`MediaFire linki bulunamadı`\n"
        return reply
    reply = ''
    page = BeautifulSoup(requests.get(link).content, 'html.parser')
    info = page.find('a', {'aria-label': 'Download file'})
    dl_url = info.get('href')
    size = re.findall(r'\(.*\)', info.text)[0]
    name = page.find('div', {'class': 'filename'}).text
    reply += f'[{name} {size}]({dl_url})\n'
    return reply

def sourceforge(url: str) -> str:
    """ SourceForge doğrudan link oluşturma """
    try:
        link = re.findall(r'\bhttps?://.*sourceforge\.net\S+', url)[0]
    except IndexError:
        reply = "`SourceForge linki bulunamadı`\n"
        return reply
    file_path = re.findall(r'files(.*)/download', link)[0]
    reply = f"Mirrors for __{file_path.split('/')[-1]}__\n"
    project = re.findall(r'projects?/(.*?)/files', link)[0]
    mirrors = f'https://sourceforge.net/settings/mirror_choices?' \
        f'projectname={project}&filename={file_path}'
    page = BeautifulSoup(requests.get(mirrors).content, 'html.parser')
    info = page.find('ul', {'id': 'mirrorList'}).findAll('li')
    for mirror in info[1:]:
        name = re.findall(r'\((.*)\)', mirror.text.strip())[0]
        dl_url = f'https://{mirror["id"]}.dl.sourceforge.net/project/{project}/{file_path}'
        reply += f'[{name}]({dl_url}) '
    return reply

def osdn(url: str) -> str:
    """ OSDN doğrudan link oluşturma """
    osdn_link = 'https://osdn.net'
    try:
        link = re.findall(r'\bhttps?://.*osdn\.net\S+', url)[0]
    except IndexError:
        reply = "`OSDN linki bulunamadı`\n"
        return reply
    page = BeautifulSoup(
        requests.get(link, allow_redirects=True).content, 'html.parser')
    info = page.find('a', {'class': 'mirror_link'})
    link = urllib.parse.unquote(osdn_link + info['href'])
    reply = f"Mirrors for __{link.split('/')[-1]}__\n"
    mirrors = page.find('form', {'id': 'mirror-select-form'}).findAll('tr')
    for data in mirrors[1:]:
        mirror = data.find('input')['value']
        name = re.findall(r'\((.*)\)', data.findAll('td')[-1].text.strip())[0]
        dl_url = re.sub(r'm=(.*)&f', f'm={mirror}&f', link)
        reply += f'[{name}]({dl_url}) '
    return reply

def github(url: str) -> str:
    """ GitHub doğrudan link oluşturma """
    try:
        link = re.findall(r'\bhttps?://.*github\.com.*releases\S+', url)[0]
    except IndexError:
        reply = "`GitHub linki bulunamadı`\n"
        return reply
    reply = ''
    dl_url = ''
    download = requests.get(url, stream=True, allow_redirects=False)
    try:
        dl_url = download.headers["location"]
    except KeyError:
        reply += "`Hata: Link çıkarılamıyor`\n"
    name = link.split('/')[-1]
    reply += f'[{name}]({dl_url}) '
    return reply

def androidfilehost(url: str) -> str:
    """ AFH doğrudan link oluşturma """
    try:
        link = re.findall(r'\bhttps?://.*androidfilehost.*fid.*\S+', url)[0]
    except IndexError:
        reply = "`AFH linki bulanamadı`\n"
        return reply
    fid = re.findall(r'\?fid=(.*)', link)[0]
    session = requests.Session()
    user_agent = useragent()
    headers = {'user-agent': user_agent}
    res = session.get(link, headers=headers, allow_redirects=True)
    headers = {
        'origin': 'https://androidfilehost.com',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'user-agent': user_agent,
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'x-mod-sbb-ctype': 'xhr',
        'accept': '*/*',
        'referer': f'https://androidfilehost.com/?fid={fid}',
        'authority': 'androidfilehost.com',
        'x-requested-with': 'XMLHttpRequest',
    }
    data = {
        'submit': 'submit',
        'action': 'getdownloadmirrors',
        'fid': f'{fid}'
    }
    mirrors = None
    reply = ''
    error = "`Hata: link için farklı mirror bulunamadı`\n"
    try:
        req = session.post(
            'https://androidfilehost.com/libs/otf/mirrors.otf.php',
            headers=headers,
            data=data,
            cookies=res.cookies)
        mirrors = req.json()['MIRRORS']
    except (json.decoder.JSONDecodeError, TypeError):
        reply += error
    if not mirrors:
        reply += error
        return reply
    for item in mirrors:
        name = item['name']
        dl_url = item['url']
        reply += f'[{name}]({dl_url}) '
    return reply

def useragent():
    """
    useragent rastgele ayarlayıcı
    """
    useragents = BeautifulSoup(
        requests.get(
            'https://developers.whatismybrowser.com/'
            'useragents/explore/operating_system_name/android/').content,
        'html.parser').findAll('td', {'class': 'useragent'})
    user_agent = choice(useragents)
    return user_agent.text

CMD_HELP.update({
    "direct":
    ".direct <link>\n"
    "Kullanım: Bir bağlantıyı yanıtlayın veya doğrudan indirme bağlantısı\n"
    "oluşturmak için bir URL yapıştırın\n\n"
    "Desteklenen URL'lerin listesi:\n"
    "`Google Drive - Cloud Mail - Yandex.Disk - AFH - "
    "ZippyShare - MEGA.nz - MediaFire - SourceForge - OSDN - GitHub`"
})
