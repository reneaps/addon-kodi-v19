#####################################################################
# -*- coding: utf-8 -*-
#####################################################################
# Addon : MidiaFlixHD
# By AddonBrasil - 11/12/2015
# Atualizado (1.1.1) - 13/07/2020
# Atualizado (1.1.2) - 29/08/2020
# Atualizado (2.0.0) - 22/07/2021
# Atualizado (2.0.1) - 22/09/2021
# Atualizado (2.0.2) - 12/04/2022
# Atualizado (2.0.3) - 02/05/2022
#####################################################################

import urllib, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon, os, time, base64
import json
import urlresolver
import requests
import inputstreamhelper

from bs4            import BeautifulSoup
from resources.lib  import jsunpack
from time           import time

version   = '2.0.3'
addon_id  = 'plugin.video.midiaflixhd'
selfAddon = xbmcaddon.Addon(id=addon_id)

addonfolder = selfAddon.getAddonInfo('path')
artfolder   = addonfolder + '/resources/media/'
fanart      = addonfolder + '/fanart.png'
base        = 'https://midiaflix.net/'
USERAGENT   = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0"

############################################################################################################

def menuPrincipal():
        addDir('Categorias'                 , base + ''                     ,   10, artfolder + 'categorias.png')
        addDir('Lançamentos'                , base + 'filmes/'              ,   20, artfolder + 'filmes.png')
        addDir('Seriados'                   , base + 'series/'              ,   25, artfolder + 'series.png')
        addDir('Pesquisa Series'            , '--'                          ,   30, artfolder + 'pesquisa.png')
        addDir('Pesquisa Filmes'            , '--'                          ,   35, artfolder + 'pesquisa.png')
        addDir('Configurações'              , base                          ,  999, artfolder + 'config.png', 1, False)

        setViewMenu()

def getCategorias(url):
        link = openURL(url)
        soup = BeautifulSoup(link, 'html.parser')
        conteudo   = soup("ul",{"class":"sub-menu"})
        categorias = conteudo[0]("li")

        totC = len(categorias)

        for categoria in categorias:
                titC = categoria.a.text
                urlC = categoria.a["href"]
                urlC = 'http:%s' % urlC if urlC.startswith("//") else urlC
                urlC = base + urlC if urlC.startswith("categoria") else urlC
                imgC = artfolder + limpa(titC) + '.png'
                addDir(titC,urlC,20,imgC)

        setViewMenu()

def getFilmes(url):
        xbmc.log('[plugin.video.midiaflixhd] L61 ' + str(url), xbmc.LOGINFO)
        link = openURL(url)
        soup = BeautifulSoup(link, 'html.parser')
        try:
            conteudo = soup('div', attrs={'class':'animation-2 items full'})
            filmes = conteudo[0]('article')
        except:
            pass
        try:
            conteudo = soup('div', attrs={'class':'items full'})
            filmes = conteudo[0]('article')
        except:
            pass
        try:
            conteudo = soup('div', attrs={'class':'items featured'})
            filmes = conteudo[0]('article')
        except:
            pass
        i = 0
        totF = len(filmes)

        for filme in filmes:
                urlF = filme.select('.poster')[0].a['href']
                imgF = filme.select('.poster')[0].img['data-src']
                titF = filme.select('.poster')[0].img['alt']
                try:
                    texto = dtinfo[i]('div', {'class':'texto'})
                    pltF = texto[0].text #sinopse(urlF)
                except:
                    pltF = ""
                    pass
                i = i + 1
                addDirF(titF, urlF, 100, imgF, False, totF, pltF)

        try :
                proxima = re.findall('<link rel="next" href="(.*?)"\s*/>', link)[0]
                addDir('Próxima Página >>', proxima, 20, artfolder + 'proxima.png')
        except :
                pass

        setViewFilmes()

def getSeries(url):
        xbmc.log('[plugin.video.midiaflixhd] L99 ' + str(url), xbmc.LOGINFO)
        link = openURL(url)
        soup = BeautifulSoup(link, 'html.parser')
        try:
            conteudo = soup('div', attrs={'class':'animation-2 items full'})
            filmes = conteudo[0]('article')
        except:
            pass
        try:
            conteudo = soup('div', attrs={'class':'items full'})
            filmes = conteudo[0]('article')
        except:
            pass
        try:
            conteudo = soup('div', attrs={'class':'items featured'})
            filmes = conteudo[0]('article')
        except:
            pass
        i = 0
        totF = len(filmes)

        for filme in filmes:
                urlF = filme.select('.poster')[0].a['href']
                imgF = filme.select('.poster')[0].img['data-src']
                titF = filme.select('.poster')[0].img['alt']
                try:
                    texto = dtinfo[i]('div', {'class':'texto'})
                    pltF = texto[0].text #sinopse(urlF)
                except:
                    pltF = ""
                    pass
                i = i + 1
                addDirF(titF, urlF, 26, imgF, True, totF, pltF)

        try :
                proxima = re.findall('<link rel="next" href="(.*?)"', link)[0]
                addDir('Próxima Página >>', proxima, 25, artfolder + 'proxima.png')
        except :
                pass

        #xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')
        setViewFilmes()

def getTemporadas(name,url,iconimage):
        xbmc.log('[plugin.video.midiaflixhd] L130 ' + str(url), xbmc.LOGINFO)
        html = openURL(url)
        soup = BeautifulSoup(html, 'html.parser')
        conteudo = soup('div', {'id':'seasons'})
        seasons = conteudo[0]('div', {'class': 'se-c'})
        totF = len(seasons)
        imgF = ''
        urlF = url
        i = 1
        while i <= totF:
                titF = str(i) + "ª Temporada"
                try:
                    addDirF(titF, urlF, 27, iconimage, True, totF)
                except:
                    pass
                i = i + 1

        xbmcplugin.setContent(handle=int(sys.argv[1]), content='seasons')

def getEpisodios(name, url):
        xbmc.log('[plugin.video.midiaflixhd] L150 ' + str(url), xbmc.LOGINFO)
        n = name.replace('ª Temporada', '')
        n = int(n)
        n = (n-1)
        temp = []
        episodios = []

        link = openURL(url)
        soup = BeautifulSoup(link, 'html.parser')
        conteudo = soup('div', {'class':'se-c'})
        episodes = conteudo[n]('ul', {'class':'episodios'})
        itens = episodes[0]('li')

        totF = len(itens)

        for i in itens:
            urlF = i.a['href']
            #if not url in urlF : urlF = base + urlF
            imgF = i.img['src']
            imgF = imgF.replace('w154', 'w300')
            imgF = 'http:%s' % imgF if imgF.startswith("//") else imgF
            imgF = base + imgF if imgF.startswith("/wp-content") else imgF
            xbmc.log('[plugin.video.midiaflixhd] L172 - ' + str(imgF), xbmc.LOGINFO)
            titA = i(class_='numerando')[0].text.replace('-','x')
            titB = i(class_='episodiotitle')[0].a.text
            titF = titA + ' - ' + titB
            addDirF(titF, urlF, 110, imgF, False, totF)

        xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')

def pesquisa():
        keyb = xbmc.Keyboard('', 'Pesquisar Filmes')
        keyb.doModal()

        if (keyb.isConfirmed()):
                texto    = keyb.getText()
                pesquisa = urllib.parse.quote(texto)
                url      = base + '?s=%s' % str(pesquisa)

                hosts = []
                link = openURL(url)
                soup = BeautifulSoup(link, 'html.parser')
                try:
                    conteudo = soup('div', attrs={'class':'animation-2 items full'})
                    filmes = conteudo[0]('article')
                except:
                    pass
                try:
                    conteudo = soup('div', attrs={'class':'items full'})
                    filmes = conteudo[0]('article')
                except:
                    pass
                try:
                    conteudo = soup('div', attrs={'class':'items featured'})
                    filmes = conteudo[0]('article')
                except:
                    pass
                try:
                    conteudo = soup('div', attrs={'class':'search-page'})
                    filmes = conteudo[0]('article')
                except:
                    pass
                totF = len(filmes)
                for filme in filmes:
                        titF = filme.img["alt"]
                        urlF = filme.a["href"]
                        urlF = base + urlF if urlF.startswith("/filmes") else urlF
                        urlF = base + urlF if urlF.startswith("filmes") else urlF
                        urlF = base + urlF if urlF.startswith("/series") else urlF
                        urlF = base + urlF if urlF.startswith("series") else urlF
                        urlF = base + "filmes/" + urlF if urlF.startswith("assistir") else urlF
                        imgF = filme.img["src"]
                        imgF = imgF.replace('w92', 'w400')
                        imgF = 'http:%s' % imgF if imgF.startswith("//") else imgF
                        imgF = base + imgF if imgF.startswith("/wp-content") else imgF
                        imgF = base + imgF if imgF.startswith("wp-content") else imgF
                        temp = [urlF, titF, imgF]
                        hosts.append(temp)

                a = []
                for url, titulo, img in hosts:
                    temp = [url, titulo, img]
                    a.append(temp);

                return a

def doPesquisaSeries():
        a = pesquisa()
        total = len(a)
        for url2, titulo, img in a:
            addDir(titulo, url2, 26, img, False, total)

        xbmcplugin.setContent(handle=int(sys.argv[1]), content='seasons')

def doPesquisaFilmes():
        a = pesquisa()
        total = len(a)
        for url2, titulo, img in a:
            addDir(titulo, url2, 100, img, False, total)
            
        setViewFilmes()

def player(name,url,iconimage):
        xbmc.log('[plugin.video.midiaflixhd] L233 - ' + str(url), xbmc.LOGINFO)
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('MidiaFlixHD', 'Obtendo Fontes para ' + name + ' Por favor aguarde...')
        mensagemprogresso.update(0)

        titsT = []
        idsT = []
        sub = None

        link = openURL(url)
        soup = BeautifulSoup(link, 'html.parser')

        dooplay = re.findall(r'<li id=[\'"]player-option-1[\'"] class=[\'"]dooplay_player_option[\'"] data-type=[\'"](.+?)[\'"] data-post=[\'"](.+?)[\'"] data-nume=[\'"](.+?)[\'"]>', link)

        for dtype, dpost, dnume in dooplay:
                print(dtype, dpost, dnume)
        try:
            p = soup('p', limit=5)[0]
            plot = p.text.replace('kk-star-ratings','')
        except:
            plot = 'Sem Sinopse'
            pass
        try:
                headers = {'Referer': url,
                        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        'Host': 'www.midiaflixhd.net',
                        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
                }
                urlF = 'https://www.midiaflixhd.net/wp-admin/admin-ajax.php'
                xbmc.log('[plugin.video.midiaflixhd] L279 - ' + str(dooplay), xbmc.LOGINFO)
                data = urllib.urlencode({'action': 'doo_player_ajax', 'post': dpost, 'nume': dnume, 'type': dtype})
                r = requests.post(url=urlF, data=data, headers=headers)
                html = r.content
                xbmc.log('[plugin.video.midiaflixhd] L283 - ' + str(html), xbmc.LOGINFO)
        except:
            pass

        try:
            soup = BeautifulSoup(link, 'html.parser')
            urlF = soup.iframe['src']
        except:
            pass

        try:
            urlF = soup.a['href']
            fxID = urlF.split('l=')[1]
            urlF = base64.b64decode(fxID)
            xbmc.log('[plugin.video.midiaflixhd] L297 - ' + str(urlF), xbmc.LOGINFO)
        except:
            pass

        try:
            b = json.loads(html)
            urlF = str(b['embed_url'])
            #urlVideo = urlF
        except:
            pass

        try:
            soup = BeautifulSoup(link, 'html.parser')
            conteudo = soup.select('.source-box')
            #print(link)
            for i in conteudo:
                if 'auth' in str(i) :
                    uri = i.a['href']
                    uri = uri.split('auth=')[-1]
                    urlF = base64.b64decode(uri)
                    b = json.loads(urlF)
                    urlF = b['url']
                    print(urlF)
        except:
            pass
            
        xbmc.log('[plugin.video.midiaflixhd] L323 - ' + str(urlF), xbmc.LOGINFO)
        urlVideo = urlF
        mensagemprogresso.update(50, 'Resolvendo fonte para ' + name +' Por favor aguarde...')

        if 'video.php' in urlVideo :
                html = openURL(urlVideo)
                soup = BeautifulSoup(html, 'html.parser')
                urlF = soup.iframe["src"]
                urlVideo = urlF
                xbmc.log('[plugin.video.midiaflixhd] L338 - ' + str(urlVideo), xbmc.LOGINFO)

        elif 'embed.mystream.to' in urlVideo:
                html = openURL(urlVideo)
                soup = BeautifulSoup(html, 'html.parser')
                urlF = soup.source["src"]
                url2Play = urlF
                xbmc.log('[plugin.video.midiaflixhd] L345 - ' + str(urlVideo), xbmc.LOGINFO)
                OK = False

        elif 'playercdn.net' in urlVideo:
                html = openURL(urlVideo)
                soup = BeautifulSoup(html, 'html.parser')
                urlF = soup.source["src"]
                url2Play = urlF
                xbmc.log('[plugin.video.midiaflixhd] L353 - ' + str(urlVideo), xbmc.LOGINFO)
                OK = False

        elif 'play.midiaflixhd.com' in urlVideo:
                html = openURL(urlVideo)
                soup = BeautifulSoup(html, 'html.parser')
                #xbmc.log('[plugin.video.midiaflixhd] L360 - ' + str(html), xbmc.LOGINFO)
                match = re.findall(r'\("SvplayerID",{\r\n\t\t\t\t\t\t\tidS: "(.*?)"\r\n\t\t\t\t\t\t}\);', html)
                for x in match:
                    idsT.append(x)
                match = re.findall('\t<button id="Servidores" class="button-xlarge pure-button" svid=".+?">(.+?)</button>\r', html)
                for x in match:
                    titsT.append(x)

                if not titsT : return

                index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

                if index == -1 : return

                i = int(index)
                idS = idsT[i]

                headers = {'Referer': url,
                           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                           'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                           'Host': 'play.midiaflixhd.com',
                           'Connection': 'keep-alive',
                           'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
                }
                urlF ='https://play.midiaflixhd.com/CallPlayer'
                data = urllib.parse.urlencode({'id': idS})
                r = requests.post(url=urlF, data=data, headers=headers)
                html = r.text
                _html = str(html)
                _html = bytes.fromhex(_html).decode('utf-8')
                xbmc.log('[plugin.video.midiaflixhd] L390 - ' + str(html), xbmc.LOGINFO)
                b = json.loads(_html)
                try:
                        urlF = b['url']
                        urlVideo = urlF
                except:
                        c = b['video'][0]
                        urlF = c['file']
                        url2Play = urlF
                        OK = False
                        pass

                xbmc.log('[plugin.video.midiaflixhd] L402 - ' + str(urlVideo), xbmc.LOGINFO)

                if 'letsupload.co' in urlVideo:
                        nowID = urlVideo.split("=")[1]
                        urlVideo = "https://letsupload.co/plugins/mediaplayer/site/_embed.php?u=%s" % nowID
                        r = requests.get(urlVideo)
                        url2Play = re.findall(r'file: "(.+?)",', r.text)[0]
                        OK = False
                        
                if 'redecine' in urlVideo:
                        nowID = urlVideo.split("url=")[1]
                        url2Play = nowID
                        OK = False
                        
                elif 'embed.mystream.to' in urlVideo:
                        html = openURL(urlVideo)
                        e = re.findall('<meta name="twitter:image" content="(.+?)">', html)[0]
                        url2Play = e.replace('/img', '').replace('jpg','mp4')
                        xbmc.log('[plugin.video.midiaflixhd] L415 - ' + str(url2Play), xbmc.LOGINFO)
                        OK = False

                elif 'megafilmeshd50' in urlVideo:
                        link = openURL(urlVideo)
                        soup = BeautifulSoup(link, 'html.parser')
                        filme = soup('video')
                        url2Play = filme[0].source['src']
                        xbmc.log('[plugin.video.midiaflixhd] L423 - ' + str(url2Play), xbmc.LOGINFO)
                        OK = False

                elif 'evoload' in urlVideo:
                        code = urlVideo.split('e/')[-1]
                        urlC = 'https://csrv.evosrv.com/captcha?m412548'
                        captcha = openURL(urlC)
                        urlF = 'https://evoload.io/SecurePlayer'
                        data = {"code":code,"token":"ok","csrv_token":captcha,"pass":"7dczpuzsmak","reff":""}
                        headers = {
                                "referrer": urlVideo,
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
                                "Accept": "application/json, text/plain, */*",
                                "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3",
                                "Content-Type": "application/json;charset=utf-8",
                                "X-XSRF-TOKEN": ""
                            }
                        link = requests.post(url=urlF, data=json.dumps(data), headers=headers)
                        r = json.loads(link.text).get('stream')
                        urlF = r.get('backup') if r.get('backup') else r.get('src')
                        url2Play = urlF
                        xbmc.log('[plugin.video.midiaflixhd] L444 - ' + str(url2Play), xbmc.LOGINFO)
                        OK = False

                elif 'gofilmes.me' in urlVideo:
                        headers = {
                                'Referer': urlVideo,
                                'authority': 'gofilmes.me',
                                'Upgrade-Insecure-Requests': '1',
                                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
                        }
                        r = requests.get(url=urlVideo, headers=headers)
                        e = re.findall('var \$data = JSON.parse\(\'(.*?)\'\);', r.text)
                        if len(e) > 0 :
                            b = json.loads(e[0])
                            xbmc.log('[plugin.video.midiaflixhd] L458 - ' + str(b['g']), xbmc.LOGINFO)
                            f = b['g']
                        else:
                            e = re.findall('sources:\s*\[\{[\'"]file[\'"]:[\'"](.+?)[\'"], type:[\'"]mp4[\'"], default:[\'"]true[\'"]\}\],', r.text)
                        if len(e) == 0 :
                            xbmc.log('[plugin.video.midiaflixhd] L463 - ' + str(r.text), xbmc.LOGINFO)
                            f = re.findall(r'<source src="(.*?)" size="720" />', r.text)
                            url2Play = f[0]
                        else:
                            url2Play = f #+ '%7C' + urllib.urlencode(headers)
                        OK = False

                elif '4toshare' in urlVideo :
                        r = requests.get(urlVideo)
                        e = re.findall('{src:\s*"(.+?)", type: "(.+?)", res:\s*.+?, label: "(.+?)"}', r.text)
                        headers = {
                                'Referer': urlVideo,
                                'Host': 's2.4toshare.com',
                                'Upgrade-Insecure-Requests': '1',
                                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
            }
                        url2Play = e[0][0] + '%7C' + urllib.urlencode(headers)
                        OK = False

                elif 'video.php' in urlVideo :
                        fxID = urlVideo.split('u=')[1]
                        urlVideo = base64.b64decode(fxID)
                        xbmc.log('[plugin.video.midiaflixhd] L485 - ' + str(urlVideo), xbmc.LOGINFO)
                        OK = True

                elif 'actelecup.com' in urlVideo :
                        xbmc.log('[plugin.video.midiaflixhd] L489 - ' + str(urlVideo), xbmc.LOGINFO)
                        urlVideo = moonwalk.get_playlist(urlVideo)
                        urlVideo = urlVideo[0]
                        qual = []
                        for i in urlVideo:
                                qual.append(str(i))
                        index = xbmcgui.Dialog().select('Selecione uma das qualidades suportadas :', qual)
                        if index == -1 : return
                        i = int(qual[index])
                        url2Play = urlVideo[i]
                        OK = False

                elif 'uauplayer' in urlVideo :
                        html = openURL(urlVideo)
                        xbmc.log('[plugin.video.midiaflixhd] L538 - ' + str(html), xbmc.LOGINFO)
                        urlF = re.findall('sources\:\s*\[{"file"\:"([^"]+)",', html)[0]
                        xbmc.log('[plugin.video.midiaflixhd] L540 - ' + str(urlF), xbmc.LOGINFO)
                        headers = {'Referer': urlVideo,
                                   'Accept': '*/*',
                                   'Content-Type': 'application/vnd.apple.mpegurl',
                                   'authority': 'cdn1.lordplayer.club',
                                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
                        }
                        r = requests.get(url=urlF, headers=headers)
                        
                        host = urlF.split('/video.m3u8')[0]
                        xbmc.log('[plugin.video.midiaflixhd] L548 - ' + str(r.text), xbmc.LOGINFO)
                        titsT = re.findall('RESOLUTION=(.*?)\n.+', r.text)
                        idsT = re.findall('RESOLUTION=.*?\n(.*?).m3u8', r.text)
                        xbmc.log('[plugin.video.midiaflixhd] L553 - ' + str(idsT), xbmc.LOGINFO)

                        if not titsT : return

                        index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

                        if index == -1 : return
                        
                        headers = {
                                 'accept': '*/*',
                                 'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7,so;q=0.6,ca;q=0.5,bg;q=0.4,de;q=0.3,it;q=0.2,fr;q=0.1,es;q=0.1',
                                 'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
                                 'sec-ch-ua-mobile': '?0',
                                 'sec-ch-ua-platform': '"Windows"',
                                 'sec-fetch-dest': 'empty',
                                 'sec-fetch-mode': 'cors',
                                 'sec-fetch-site': 'cross-site',
                                 'Referer': 'https://uauplayer.com/',
                                 'Referrer-Policy': 'strict-origin-when-cross-origin'
                                 }
                        urlVideo = host + '/' + idsT[index] + '.m3u8' + '|' + urllib.parse.urlencode(headers)
                        url2Play = urlVideo
                        OK = False

                elif 'mrdhan.com' in urlVideo or 'vfilmesonline' in urlVideo :
                        pu = urllib.parse.urlparse(urlVideo)
                        p = r'(?://|\.)((mrdhan|vfilmesonline)\.(com|net))/(?:f|e|v)/(.+)'
                        match = re.search(p, urlVideo)
                        ul = match.group()
                        fxID = ul.split('/v/')[-1]
                        urlF = pu.scheme + '://' + pu.netloc + '/api/source/%s' % fxID
                        headers = {
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
                                "Accept": "*/*",
                                "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3",
                                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                                "X-Requested-With": "XMLHttpRequest",
                                "Alt-Used": "mrdhan.com"
                            }
                        payload = "r=&d=mrdhan.com"
                        r = requests.post(url=urlF, data=payload)
                        js = json.loads(r.text)
                        links = js['data']
                        qual = []
                        for link in links:
                            qual.append(link['label'])
                        index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', qual)
                        if index == -1 : return
                        i = int(index)
                        url2Play = links[i]['file']
                        OK = False

                elif 'megafilmeshd50' in urlVideo:
                        link = openURL(urlVideo)
                        soup = BeautifulSoup(link, 'html.parser')
                        filme = soup('video')
                        url2Play = filme[0].source['src']
                        xbmc.log('[plugin.video.midiaflixhd] L534 - ' + str(url2Play), xbmc.LOGINFO)
                        OK = False

                elif 'filmesmp4' in url or 'pandafiles' in urlVideo :
                        if 'pandafiles' in urlVideo :
                                u = re.findall('https://pandafiles.com/embed-(.*?).html', urlVideo)[0]
                                urlF = 'https://filmesmp4.com/03/?dub=%s' % u
                                print('1 ->',urlF)
                        if 'filmesmp4' in urlVideo :
                                u = urlVideo.split('=')[-1]
                                urlF = 'https://filmesmp4.com/03/?dub=%s' % u
                                print('2 -> ',urlF)
                        link = openURL(urlF)
                        try:
                                soup = BeautifulSoup(link, 'html.parser')
                                urlF = soup.iframe['src']
                                url2Play = urlF
                                print(url2Play)
                        except:
                                pass
                        try:
                                soup = BeautifulSoup(link, 'html.parser')
                                urlF = soup.iframe['src']
                                link = openURL(urlF)
                                soup = BeautifulSoup(link, 'html.parser')
                                video = soup.body('source')
                                urlV = video[0]['src']
                                url2Play = urlV
                                print(url2Play)
                        except:
                                pass
                        OK = False

        if OK :
            try:
                url2Play = urlresolver.resolve(urlVideo)
            except:
                dialog = xbmcgui.Dialog()
                dialog.ok(" Erro:", " Video removido! ")
                url2Play = []
                pass

        xbmc.log('[plugin.video.midiaflixhd] L576 - ' + str(url2Play), xbmc.LOGINFO)

        if not url2Play : return

        legendas = '-'

        mensagemprogresso.update(75, 'Abrindo Sinal para ' + name +' Por favor aguarde...')

        playlist = xbmc.PlayList(1)
        playlist.clear()

        if "m3u8" in url2Play:
                PROTOCOL = 'hls'
                DRM = 'com.widevine.alpha'
                LICENSE_URL = 'https://widevine-proxy.appspot.com/proxy'
                listitem = xbmcgui.ListItem(name, path=url2Play)
                listitem.setArt({"thumb": iconimage, "icon": iconimage})
                is_helper = inputstreamhelper.Helper(PROTOCOL, drm=DRM)
                listitem.setProperty('IsPlayable', 'true')
                listitem.setMimeType('application/x-mpegURL')
                listitem.setProperty('inputstream',is_helper.inputstream_addon)
                listitem.setProperty('inputstream.adaptive.manifest_type', PROTOCOL)
                listitem.setProperty('inputstream.adaptive.stream_headers', 'User-Agent=' + USERAGENT)
                listitem.setProperty('inputstream.adaptive.play_timeshift_buffer', 'true')
                listitem.setProperty('inputstream.adaptive.manifest_update_parameter', 'full')
                listitem.setProperty('inputstream.adaptive.license_type', DRM)
                listitem.setProperty('inputstream.adaptive.license_key', LICENSE_URL + '||B{SSM}|')
                listitem.setContentLookup(False)
                #listitem.setInfo('video', { 'genre': genre })
                playlist.add(url2Play,listitem)
        else:
                listitem = xbmcgui.ListItem(name, path=url2Play)
                listitem.setArt({"thumb": iconimage, "icon": iconimage})
                listitem.setProperty('IsPlayable', 'true')
                listitem.setMimeType('video/mp4')
                #listitem.setInfo('video', { 'genre': genre })
                playlist.add(url2Play,listitem)

        xbmcPlayer = xbmc.Player()

        while xbmcPlayer.play(playlist) :
            xbmc.sleep(20000)
            if not xbmcPlayer.isPlaying():
                xbmcPlayer.stop()

        mensagemprogresso.update(100)
        mensagemprogresso.close()

        if legendas != '-':
            if 'timedtext' in legendas:
                    import os.path
                    sfile = os.path.join(xbmc.translatePath("special://temp"),'sub.srt')
                    sfile_xml = os.path.join(xbmc.translatePath("special://temp"),'sub.xml')#timedtext
                    sub_file_xml = open(sfile_xml,'w')
                    sub_file_xml.write(requests.get(legendas).text)
                    xmltosrt.main(sfile_xml)
                    xbmcPlayer.setSubtitles(sfile)
            else:
                xbmcPlayer.setSubtitles(legendas)

def player_series(name,url,iconimage):
        xbmc.log('[plugin.video.midiaflixhd] L630 - ' + str(url), xbmc.LOGINFO)
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('MidiaFlixHD', 'Obtendo Fontes para ' + name + ' Por favor aguarde...')
        mensagemprogresso.update(0)

        titsT = []
        idsT = []
        links = []
        hosts = []
        sub = None

        link = openURL(url)
        soup = BeautifulSoup(link, 'html.parser')
        dados = soup('li',{'id':'player-option-1'})
        t = soup.select('.item')
        title = t[1].a['title']
        xbmc.log('[plugin.video.midiaflixhd] L647 - ' + str(title), xbmc.LOGINFO)
        if not dados :
                dialog = xbmcgui.Dialog()
                dialog.ok(name, " ainda não liberado, aguarde... ")
                return

        dooplay = []
        dtype = dados[0]['data-type']
        dpost = dados[0]['data-post']
        dnume = dados[0]['data-nume']
        dooplay = re.findall(r'<li id=[\'"]player-option-.+?[\'"] class=[\'"]dooplay_player_option.+?[\'"] data-type=[\'"](.+?)[\'"] data-post=[\'"](.+?)[\'"] data-nume=[\'"](.+?)[\'"]>', link)
        xbmc.log('[plugin.video.midiaflixhd] L658 - ' + str(dooplay), xbmc.LOGINFO)
        for dtype, dpost, dnume in dooplay:
            print(dtype, dpost, dnume)

        try:
            headers = {'Referer': url,
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'Host': 'www.midiaflixhd.net',
                    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
            }
            urlF = 'https://www.midiaflixhd.net/wp-admin/admin-ajax.php'
            data = urllib.urlencode({'action': 'doo_player_ajax', 'post': dpost, 'nume': dnume, 'type': dtype})
            xbmc.log('[plugin.video.midiaflixhd] L670 - ' + str(data), xbmc.LOGINFO)
            r = requests.post(url=urlF, data=data, headers=headers)
            html = r.content
            soup = BeautifulSoup(html, 'html.parser')
        except:
            pass

        try:
            urlF = soup.iframe['src']
            xbmc.log('[plugin.video.midiaflixhd] L679 - ' + str(urlF), xbmc.LOGINFO)
        except:
            pass

        try:
            urlF = soup.a['href']
            fxID = urlF.split('l=')[1]
            urlF = base64.b64decode(fxID)
            xbmc.log('[plugin.video.midiaflixhd] L687 - ' + str(urlF), xbmc.LOGINFO)
        except:
            pass

        try:
            soup = BeautifulSoup(link, 'html.parser')
            conteudo = soup.select('.source-box')
            xbmc.log('[plugin.video.midiaflixhd] L694 - ' + str(conteudo), xbmc.LOGINFO)
            #print(link)
            for i in conteudo:
                    if 'auth' in str(i) :
                            uri = i.a['href']
                            uri = uri.split('auth=')[-1]
                            urlF = base64.b64decode(uri)
                            b = json.loads(urlF)
                            urlF = b['url']
                            idsT.append(urlF)
                            if '/dub' in urlF : titsT.append("Dublado")
                            if '/leg' in urlF : titsT.append("Legendado")
                            print(urlF)

            if not titsT : return

            index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

            if index == -1 : return

            i = int(index)
            urlF = idsT[i]
            idsT = []
            titsT = []
        except:
                pass

        urlVideo = urlF

        xbmc.log('[plugin.video.midiaflixhd] L723 - ' + str(urlVideo), xbmc.LOGINFO)

        if 'play.midiaflixhd.com' in urlVideo:
                html = requests.get(urlVideo).text
                match = re.findall('idS="(.+?)"', html)
                for x in match:
                    idsT.append(x)

                idS = idsT[0]

                headers = {'Referer': url,
                           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                           'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                           'Host': 'play.midiaflixhd.com',
                           'Connection': 'keep-alive',
                           'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
                }
                urlF ='https://play.midiaflixhd.com/CallEpi'
                data = urllib.parse.urlencode({'idS': idS})
                r = requests.post(url=urlF, data=data, headers=headers)
                #xbmc.log('[plugin.video.midiaflixhd] L743 - ' + str(data), xbmc.LOGINFO)

                #xbmc.log('[plugin.video.midiaflixhd] L745 - ' + str(r.text), xbmc.LOGINFO)

                html = r.text
                _html = str(html)
                _html = bytes.fromhex(_html).decode('utf-8')
                b = json.loads(_html)
                if 'video' in str(b) :
                    c = b['video']
                    urlF = c[0]['file']
                    if 'subtitle' in str(b) : sub = b['subtitle']
                else:
                    urlF = b['url']
                xbmc.log('[plugin.video.midiaflixhd] L757 - ' + str(sub), xbmc.LOGINFO)
                headers = {'referer': urlVideo,
                            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'}
                r = requests.get(url=urlF,allow_redirects=False,headers=headers)
                if r.status_code >= 300 and r.status_code <= 399:
                    #Sucesso
                    urlF = r.headers['Location']
                else :
                    #Erros
                    return

                r = requests.get(url=urlF,allow_redirects=False,headers=headers)
                if r.status_code >= 300 and r.status_code <= 399:
                    #Sucesso
                    urlF = r.headers['Location']
                else :
                    #Erros
                    return

                urlVideo = urlF

                xbmc.log('[plugin.video.midiaflixhd] L778 - ' + str(urlVideo), xbmc.LOGINFO)

                if 'letsupload.co' in urlVideo:
                        nowID = urlVideo.split("=")[1]
                        urlVideo = "https://letsupload.co/plugins/mediaplayer/site/_embed.php?u=%s" % nowID
                        r = requests.get(urlVideo)
                        url2Play = re.findall(r'file: "(.+?)",', r.text)[0]
                        OK = False

                elif 'videok7.online' in urlVideo :
                        url2Play = urlVideo
                        OK = False

                elif 'saborcaseiro' in urlVideo :
                        url2Play = urlVideo
                        OK = False

                elif 'apiblogger.xyz' in urlVideo :
                        headers = {'Referer': urlF2,
                                   'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
                        }
                        url2Play = urlVideo + "|" + urllib.urlencode(headers)
                        OK = False

                elif 'googlevideo.com' in urlVideo :
                        url2Play = urlVideo
                        OK = False

                elif 'video.php' in urlVideo :
                        fxID = urlVideo.split('=')[1]
                        urlVideo = base64.b64decode(fxID)
                        xbmc.log('[plugin.video.midiaflixhd] L809 - ' + str(urlVideo), xbmc.LOGINFO)
                        OK = True

                        if 'alfastream.cc' in urlVideo:
                                if 'actelecup.com' in urlVideo:
                                        xbmc.log('[plugin.video.midiaflixhd] L814 - ' + str(urlVideo), xbmc.LOGINFO)
                                        urlVideo = moonwalk.get_playlist(urlVideo)
                                        urlVideo = urlVideo[0]
                                        qual = []
                                        for i in urlVideo:
                                                qual.append(str(i))
                                        index = xbmcgui.Dialog().select('Selecione uma das qualidades suportadas :', qual)
                                        if index == -1 : return
                                        i = int(qual[index])
                                        url2Play = urlVideo[i]
                                        OK = False

        xbmc.log('[plugin.video.midiaflixhd] L826 ' + str(urlVideo), xbmc.LOGINFO)

        mensagemprogresso.update(50, 'Resolvendo fonte para ' + name + ' Por favor aguarde...')

        if OK : url2Play = urlresolver.resolve(urlVideo)

        if not url2Play : return

        if sub is None:
            legendas = '-'
        else:
            legendas = sub

        mensagemprogresso.update(75, 'Abrindo Sinal para ' + name + ' Por favor aguarde...')

        playlist = xbmc.PlayList(1)
        playlist.clear()

        if "m3u8" in url2Play:
                #ip = addon.getSetting("inputstream")
                listitem = xbmcgui.ListItem(name, path=url2Play)
                listitem.setArt({"thumb": iconimage, "icon": iconimage})
                listitem.setProperty('IsPlayable', 'true')
                listitem.setMimeType('application/x-mpegURL')
                listitem.setProperty('inputstream','inputstream.hls')
                #listitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
                #listitem.setMimeType('application/dash+xml')
                listitem.setContentLookup(False)
                playlist.add(url2Play,listitem)
        else:
                listitem = xbmcgui.ListItem(path=url2Play)
                listitem.setArt({"thumb": iconimage, "icon": iconimage})
                listitem.setProperty('IsPlayable', 'true')
                listitem.setMimeType('video/mp4')
                listitem.setInfo('video', { 'title': title, 'genre': name})
                playlist.add(url2Play,listitem)

        xbmcPlayer = xbmc.Player()

        while xbmcPlayer.play(playlist) :
            xbmc.sleep(20000)
            if not xbmcPlayer.isPlaying():
                xbmcPlayer.stop()

        mensagemprogresso.update(100)
        mensagemprogresso.close()

        if legendas != '-':
            if 'timedtext' in legendas:
                    import os.path
                    sfile = os.path.join(xbmc.translatePath("special://temp"),'sub.srt')
                    sfile_xml = os.path.join(xbmc.translatePath("special://temp"),'sub.xml')#timedtext
                    sub_file_xml = open(sfile_xml,'w')
                    sub_file_xml.write(requests.get(legendas).text)
                    xmltosrt.main(sfile_xml)
                    xbmcPlayer.setSubtitles(sfile)
            else:
                xbmcPlayer.setSubtitles(legendas)

        return OK

############################################################################################################

def openConfig():
        selfAddon.openSettings()
        setViewMenu()
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

def openConfigEI():
        eiID  = 'script.extendedinfo'
        eiAD  = xbmcaddon.Addon(id=eiID)

        eiAD.openSettings()
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

def openURL(url):
        headers= {'Referer': url,
                'content-type': 'text/html; charset=UTF-8',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36'
        }
        link = requests.get(url=url,headers=headers).text
        return link

def postURL(url):
        headers = {'Referer': base,
                   'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                   'Host': 'www.midiaflixhd.net',
                   'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
        }

        req = requests.post(url,headers)
        link=resp.content
        return link

def addDir(name, url, mode, iconimage, total=1, pasta=True):
        u = sys.argv[0]+"?url="+urllib.parse.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.parse.quote_plus(name)+"&iconimage="+urllib.parse.quote_plus(iconimage)

        ok = True

        liz = xbmcgui.ListItem(name)
        liz.setProperty('fanart_image', fanart)
        liz.setInfo(type = "Video", infoLabels = {"title": name})
        liz.setArt({ 'icon': iconimage, 'thumb': iconimage })

        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=pasta, totalItems=total)

        return ok

def addDirF(name,url,mode,iconimage,pasta=True,total=1,plot='') :
        u  = sys.argv[0]+"?url="+urllib.parse.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.parse.quote_plus(name)+"&iconimage="+urllib.parse.quote_plus(iconimage)

        ok = True

        liz = xbmcgui.ListItem(name)
        liz.setProperty('fanart_image', fanart)
        liz.setInfo(type = "Video", infoLabels = {"title": name})
        liz.setArt({ 'icon': iconimage, 'thumb': iconimage })

        cmItems = []

        cmItems.append(('[COLOR gold]Informações do Filme[/COLOR]', 'XBMC.RunPlugin(%s?url=%s&mode=98)'%(sys.argv[0], url)))
        cmItems.append(('[COLOR red]Assistir Trailer[/COLOR]', 'XBMC.RunPlugin(%s?name=%s&url=%s&iconimage=%s&mode=99)'%(sys.argv[0], urllib.parse.quote(name), url, urllib.parse.quote(iconimage))))

        liz.addContextMenuItems(cmItems, replaceItems=False)

        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=pasta, totalItems=total)

        return ok

def getInfo(url):
        link = openURL(url)
        titO = re.findall('<meta property="og:title" content="(.*?)" />', link)[0]

        xbmc.executebuiltin('XBMC.RunScript(script.extendedinfo,info=extendedinfo, name=%s)' % titO)

def playTrailer(name, url,iconimage):
        link = openURL(url)
        #ytID = re.findall('<a id="open-trailer" class="btn iconized trailer" data-trailer="https://www.youtube.com/embed/(.*?)rel=0&amp;controls=1&amp;showinfo=0&autoplay=0"><b>Trailler</b> <i class="icon fa fa-play"></i></a>', link)[0]
        ytID = '' #SytID.replace('?','')

        xbmc.executebuiltin('XBMC.RunPlugin("plugin://script.extendedinfo/?info=youtubevideo&&id=%s")' % ytID)

def setViewMenu() :
        xbmcplugin.setContent(int(sys.argv[1]), 'episodes')

        opcao = selfAddon.getSetting('menuVisu')

        if   opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
        elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51)")
        elif opcao == '2': xbmc.executebuiltin("Container.SetViewMode(500)")

def setViewFilmes() :
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')

        opcao = selfAddon.getSetting('filmesVisu')

        if   opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
        elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51)")
        elif opcao == '2': xbmc.executebuiltin("Container.SetViewMode(500)")
        elif opcao == '3': xbmc.executebuiltin("Container.SetViewMode(501)")
        elif opcao == '4': xbmc.executebuiltin("Container.SetViewMode(508)")
        elif opcao == '5': xbmc.executebuiltin("Container.SetViewMode(504)")
        elif opcao == '6': xbmc.executebuiltin("Container.SetViewMode(503)")
        elif opcao == '7': xbmc.executebuiltin("Container.SetViewMode(515)")

def limpa(texto):
        texto = texto.replace('ç','c').replace('ã','a').replace('õ','o')
        texto = texto.replace('â','a').replace('ê','e').replace('ô','o')
        texto = texto.replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u')
        texto = texto.replace(' ','-')
        texto = texto.lower()

        return texto

def sinopse(urlF):
        link = openURL(urlF)
        soup = BeautifulSoup(link, 'html.parser')
        #conteudo = soup("div", {"id": "info"})
        try:
            p = soup('p', limit=5)[0]
            plot = p.text.replace('kk-star-ratings','')
        except:
            plot = 'Sem Sinopse'
            pass
        return plot

############################################################################################################

def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]

        return param

params    = get_params()
url       = None
name      = None
mode      = None
iconimage = None

try    : url=urllib.parse.unquote_plus(params["url"])
except : pass
try    : name=urllib.parse.unquote_plus(params["name"])
except : pass
try    : mode=int(params["mode"])
except : pass
try    : iconimage=urllib.parse.unquote_plus(params["iconimage"])
except : pass

print("Mode: "+str(mode))
print("URL: "+str(url))
print("Name: "+str(name))
print("Iconimage: "+str(iconimage))

###############################################################################################################

if   mode == None : menuPrincipal()
elif mode == 10   : getCategorias(url)
elif mode == 20   : getFilmes(url)
elif mode == 25   : getSeries(url)
elif mode == 26   : getTemporadas(name,url,iconimage)
elif mode == 27   : getEpisodios(name,url)
elif mode == 30   : doPesquisaSeries()
elif mode == 35   : doPesquisaFilmes()
elif mode == 40   : getFavoritos()
elif mode == 41   : addFavoritos(name,url,iconimage)
elif mode == 42   : remFavoritos(name,url,iconimage)
elif mode == 43   : cleanFavoritos()
elif mode == 98   : getInfo(url)
elif mode == 99   : playTrailer(name,url,iconimage)
elif mode == 100  : player(name,url,iconimage)
elif mode == 110  : player_series(name,url,iconimage)
elif mode == 999  : openConfig()

xbmcplugin.endOfDirectory(int(sys.argv[1]))
