#####################################################################
# -*- coding: utf-8 -*-
#####################################################################
# Addon : FilmestorrentBrasil
# By AddonBrasil - 08/08/2020
# Atualizado (2.1.0) - 02/12/2023
# Atualizado (2.1.1) - 17/12/2023
# Atualizado (2.1.2) - 25/12/2023
# Atualizado (2.1.3) - 28/12/2023
# Atualizado (2.1.4) - 03/01/2024
# Atualizado (2.1.5) - 04/01/2024
# Atualizado (2.1.6) - 05/01/2024
# Atualizado (2.1.7) - 09/01/2024
# Atualizado (2.1.8) - 09/01/2024
# Atualizado (2.1.9) - 22/01/2024
#####################################################################

import urllib, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon, os, sys, time, base64
import json
#import urlresolver
import requests
import subprocess
import platform

from bs4                import BeautifulSoup
from resources.lib      import jsunpack

addon_id  = 'plugin.video.filmestorrentbrasil'
selfAddon = xbmcaddon.Addon(id=addon_id)
addon = xbmcaddon.Addon()
_handle = int(sys.argv[1])
full_version_info = xbmc.getInfoLabel('System.BuildVersion')
baseversion = full_version_info.split(".")
installed_version = int(baseversion[0])

addonfolder = selfAddon.getAddonInfo('path')
version     = selfAddon.getAddonInfo('version')
artfolder   = addonfolder + '/resources/media/'
fanart      = addonfolder + '/fanart.png'
base        = 'https://brtorrenthd.org'

############################################################################################################

def menuPrincipal():
        addDir('Categorias'                 , base                          ,   10, artfolder + 'categorias.png')
        addDir('Lançamentos'                , base + '/filmes-utorrent/'    ,   20, artfolder + 'new.png')
        addDir('Seriados'                   , base + '/download-series-hd/' ,   25, artfolder + 'series.png')
        addDir('Pesquisa Series'            , '--'                          ,   30, artfolder + 'pesquisa.png')
        addDir('Pesquisa Filmes'            , '--'                          ,   35, artfolder + 'pesquisa.png')
        #addDir('Configurações'              , base                          ,  999, artfolder + 'config.png', 1, False)

        setViewMenu()

def getCategorias(url):
        link = openURL(url)
        soup = BeautifulSoup(link, 'html.parser')
        conteudo = soup('div', {'class':'row'})
        categorias = conteudo[0]('li')

        totC = len(categorias)

        for categoria in categorias:
            if not 'Menu' in str(categoria):
                if not '//brtorrent' in str(categoria):
                    titC = categoria.a.text
                    urlC = categoria.a["href"]
                    urlC = 'http:%s' % urlC if urlC.startswith("//") else urlC
                    urlC = base + urlC if urlC.startswith("/") else urlC
                    imgC = artfolder + limpa(titC) + '.png'
                    addDir(titC,urlC,20,imgC)

        setViewMenu()

def getFilmes(name,url,iconimage):
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='movies')
        xbmc.log('[plugin.video.filmestorrentbrasil] L76 - ' + str(url), xbmc.LOGINFO)
        link = openURL(url)
        soup = BeautifulSoup(link, "html.parser")
        conteudo = soup("div", {"class":"container"})
        filmes = conteudo[1]("div", {"class":"post"})

        totF = len(filmes)

        for filme in filmes:
            titF = ""
            try:
                titF = filme('a')[1].text
                titF = str(titF).replace('Downloads','').replace('Nacional','').replace('Torrent','').replace('\n','').replace('\t','')
                imgF = re.findall('<div class="img" style="background-image:url\((.*?)\);"></div>', str(filme.a.div))[0]
                urlF = filme('a')[0]['href']
                pltF = ""
                addDirF(titF, urlF, 100, imgF, False, totF)
            except:
                pass

        try :
                proxima = re.findall(r'<a aria-label=".*?" class="nextpostslink" href="(.*?)" rel="next">.*?</a>', str(soup))[0]
                #proxima = re.findall(r'<a aria-label=".*?" class="nextpostslink" href="(.*?)" rel="next">.*?</a>', str(soup))[0]
                proxima = base + proxima if proxima.startswith("/") else proxima
                addDir('Próxima Página >>', proxima, 20, artfolder + 'proxima.png')
        except :
                pass

def getSeries(url):
        xbmc.log('[plugin.video.filmestorrentbrasil] L105- ' + str(url), xbmc.LOGINFO)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='season')
        link = openURL(url)
        soup = BeautifulSoup(link, "html.parser")
        conteudo = soup("div", {"class":"container"})
        filmes = conteudo[1]("div", {"class":"post"})

        totF = len(filmes)

        for filme in filmes:
            titF = ""
            try:
                titF = filme('a')[1].text
                titF = str(titF).replace('Downloads','').replace('Nacional','').replace('Torrent','').replace('\n','').replace('\t','')
                imgF = re.findall('<div class="img" style="background-image:url\((.*?)\);"></div>', str(filme.a.div))[0]
                imgF = 'http:%s' % imgF if imgF.startswith("//") else imgF
                urlF = filme('a')[0]['href']
                urlF = base + urlF if urlF.startswith("/") else urlF
                pltF = titF
                addDirF(titF, urlF, 27, imgF, True, totF)
            except:
                pass

        try :
                proxima = re.findall(r'<a aria-label=".*?" class="nextpostslink" href="(.*?)" rel="next">.*?</a>', str(soup))[0]
                proxima = base + proxima if proxima.startswith("/") else proxima
                addDir('Próxima Página >>', proxima, 25, artfolder + 'proxima.png')
        except :
                pass

        #setViewFilmes()

def getTemporadas(name,url,iconimage):
        xbmc.log('[plugin.video.filmestorrentbrasil] L138 - ' + str(url), xbmc.LOGINFO)
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
                    addDir(titF, urlF, 27, iconimage, totF, True)
                except:
                    pass
                i = i + 1

        xbmcplugin.setContent(_handle, content='seasons')

def getEpisodios(name, url, iconimage):
        xbmc.log('[plugin.video.filmestorren tbrasil] L158 - ' + str(url), xbmc.LOGINFO)
        xbmcplugin.setContent(_handle, content='episodes')
        link = openURL(url)
        soup = BeautifulSoup(link, 'html.parser')
        links = soup('p')
        totF = len(links)
        imgF = iconimage
        '''
        try:
            imgF = links[0].img['src']
        except:
            pass
        '''

        for link in links:
            if 'tulo Traduzido:' in str(link):
                titF = link.br.text
            elif 'tulo Original:' in str(link):
                titF = link.br.text
            elif 'emporada' in str(link):
                if 'strong' in str(link):
                    titF = link.strong.text
                if 'b' in str(link):
                    titF = link.text
                if 'img' in str(link):
                    titF = link.img['alt']
                if 'COMPLETA' in str(link):
                    titF = link.a.text
            elif 'Epis' in str(link).upper():
                if '<strong>' in str(link) : titF = link.strong.text
                if '<b>' in str(link) : titF = link.text
                if '<a' in str(link) : titF = link.text
            elif 'WEB' in str(link).upper():
                if '<strong>' in str(link) : titF = link.strong.text
                if '<b>' in str(link) : titF = link.text
                if '<a' in str(link) : titF = link.text
            if 'campanha' in str(link):
                #if titF: titF = 'Epis'
                u = link.a['href']
                fxID = u.split('?id=')[-1]
                urlF = base64.b64decode(fxID).decode('utf-8')
                urlF = base + urlF if urlF.startswith("/") else urlF
                titF = name.split("emporada")[0] + " | " + str(titF)
                addDir(titF, urlF, 110, imgF, totF, False)
            elif 'magnet' in str(link):
                urlF = link.a['href']
                urlF = base + urlF if urlF.startswith("/") else urlF
                titF = str(link.text) #str(titF) + name.split("emporada")[0] + " | " + str(titF)
                xbmc.log('[plugin.video.filmestorrentbrasil] L206 - ' + str(urlF), xbmc.LOGINFO)
                addDir(name+"| "+titF, urlF, 110, imgF, totF, False)

def pesquisa():
        keyb = xbmc.Keyboard('', 'Pesquisar Filmes')
        keyb.doModal()

        if (keyb.isConfirmed()):
                texto    = keyb.getText()
                pesquisa = urllib.parse.quote(texto)
                url      = base + '?s=%s' % str(pesquisa)

                xbmc.log('[plugin.video.filmestorrentbrasil] L218 - ' + str(url), xbmc.LOGINFO)
                hosts = []
                temp = []
                link = openURL(url)
                soup = BeautifulSoup(link, 'html.parser')
                conteudo = soup('div',{'class':'container'})
                filmes = conteudo[1]("div", {"class":"post"})

                totF = len(filmes)

                for filme in filmes:
                        try:
                                titF = filme('div', attrs={'class':'title'})[0].text #.encode('utf-8')
                                titF = str(titF).replace('Downloads','').replace('Nacional','').replace('Torrent','').replace('\n','').replace('\t','')
                                imgF = re.findall('<div class="img" style="(.*?)."></div>', str(link))[0]
                                imgF = imgF.replace('background-image:url(','').replace(')','')
                                imgF = 'http:%s' % imgF if imgF.startswith("//") else imgF
                                urlF = filme('div', attrs={'class':'title'})[0].a['href']
                                urlF = base + urlF if urlF.startswith("/") else urlF
                                temp = [urlF, titF, imgF]
                                hosts.append(temp)
                        except:
                                pass

                return hosts

def doPesquisaSeries():
        a = pesquisa()
        if a is None : return
        total = len(a)
        for url2, titulo, img in a:
            xbmc.log('[plugin.video.filmestorrentbrasil] L249 - ' + str(url2), xbmc.LOGINFO)
            addDirF(titulo, url2, 27, img, True, total)

        xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')

def doPesquisaFilmes():
        a = pesquisa()
        if a is None : return
        total = len(a)
        for url2, titulo, img in a:
            addDirF(titulo, url2, 100, img, False, total)

        setViewFilmes()

def player(name,url,iconimage):
        xbmc.log('[plugin.video.filmestorrentbrasil] L264 - ' + str(url), xbmc.LOGINFO)
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('FilmestorrentBrasil', 'Obtendo Fontes para ' + name + ' Por favor aguarde...')
        mensagemprogresso.update(0)

        titsT = []
        idsT = []
        sub = None

        link = openURL(url)
        soup = BeautifulSoup(link, "html.parser")
        conteudo = soup('div', attrs={'class':'container'})
        #links = conteudo[8]('p')
        for i in conteudo:
                if 'magnet' in str(i):
                        links = i('a')

        n = 1

        for link in links:
            if 'campanha' in str(link) :
                urlF = link.a['href']
                print(urlF)
                idS = urlF.split('id=')[-1]
                urlVideo = base64.b64decode(idS).decode('utf-8')
                titS = "Server_" + str(n)
                n = n + 1
                titsT.append(titS)
                idsT.append(urlVideo)
            if 'magnet' in str(link):
                urlF = link['href']
                urlVideo = urlF
                titS = "Option_" +str(n)
                n = n + 1
                titsT.append(titS)
                idsT.append(urlVideo)

        if not titsT : return

        index = xbmcgui.Dialog().select('Selecione uma das opcoes :', titsT)

        if index == -1 : return

        i = int(index)
        urlVideo = idsT[i]

        xbmc.log('[plugin.video.filmestorrentbrasil] L311 - ' + str(urlVideo), xbmc.LOGINFO)

        mensagemprogresso.update(50, 'Resolvendo fonte para ' + name + ' Por favor aguarde...')

        if 'magnet' in urlVideo :
                if "&amp;" in str(urlVideo) : urlVideo = urlVideo.replace("&amp;","&")
                url2Play = 'plugin://plugin.video.elementum/play?doresume=false&uri=' + urlVideo
                OK = False

        if OK :
            try:
                url2Play = urlresolver.resolve(urlVideo)
            except:
                dialog = xbmcgui.Dialog()
                dialog.ok(" Erro:", " Video removido! ")
                url2Play = []
                pass

        xbmc.log('[plugin.video.filmestorrentbrasil] L329 - ' + str(url2Play), xbmc.LOGINFO)

        if not url2Play : return

        if sub is None:
            legendas = '-'
        else:
            legendas = sub

        mensagemprogresso.update(75, 'Abrindo Sinal para ' +name+ ' Por favor aguarde...')

        playlist = xbmc.PlayList(1)
        playlist.clear()

        if "m3u8" in url2Play:
                #ip = addon.getSetting("inputstream")
                listitem = xbmcgui.ListItem(name, path=url2Play)
                listitem.setArt({"thumb": iconimage, "icon": iconimage})
                listitem.setArt({"Poster": iconimage})
                listitem.setProperty('IsPlayable', 'true')
                listitem.setMimeType('application/x-mpegURL')
                listitem.setProperty('inputstream','inputstream.hls')
                listitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
                listitem.setMimeType('application/dash+xml')
                listitem.setContentLookup(False)
                playlist.add(url2Play,listitem)
        else:
                listitem = xbmcgui.ListItem(label=name, path=url2Play)
                if int(installed_version) > 18:
                        info_tag = listitem.getVideoInfoTag()
                        info_tag.setMediaType('video')
                        info_tag.setTitle(name.split("|")[0])
                        listitem.setArt({'icon': iconimage, 'thumb': iconimage })
                        listitem.setProperty('IsPlayable', '')
                        playlist.add(url2Play,listitem)
                else:
                        listitem.setProperty('fanart_image', fanart)
                        listitem.setInfo(type = "Video", infoLabels = {"title": name})
                        listitem.setArt({'icon': iconimage, 'thumb': iconimage })
                        playlist.add(url2Play,listitem)

        xbmc.log('[plugin.video.filmestorrentbrasil] L370 - ' + str(playlist), xbmc.LOGINFO)

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
                    sub_file_xml.write(urllib.parse.urlopen(legendas).read())
                    sub_file_xml.close()
                    xmltosrt.main(sfile_xml)
                    xbmcPlayer.setSubtitles(sfile)
            else:
                xbmcPlayer.setSubtitles(legendas)

        del legendas
        del url2Play
        del urlVideo
        del xbmcPlayer

        return OK

def player_series(name,url,iconimage):
        xbmc.log('[plugin.video.filmestorrentbrasil] L403 - ' + str(url), xbmc.LOGINFO)
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('FilmestorrentBrasil', 'Obtendo Fontes para ' + name + ' Por favor aguarde...')
        mensagemprogresso.update(0)

        sub = None

        urlVideo = url

        mensagemprogresso.update(50, 'Resolvendo fonte para ' + name+ ' Por favor aguarde...')

        if 'magnet' in urlVideo :
                #urlVideo = urllib.parse.unquote(urlVideo)
                if "&amp;" in str(urlVideo) : urlVideo = urlVideo.replace("&amp;","&")
                url2Play = 'plugin://plugin.video.elementum/play?uri={0}'.format(urlVideo)
                OK = False

        xbmc.log('[plugin.video.filmestorrentbrasil] L421 - ' + str(url2Play), xbmc.LOGINFO)

        if OK :
            try:
                url2Play = urlresolver.resolve(urlVideo)
            except:
                dialog = xbmcgui.Dialog()
                dialog.ok(" Erro:", " Video removido! ")
                url2Play = []
                pass

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
                listitem = xbmcgui.ListItem((name.split("|")[0]), path=url2Play)
                listitem.setArt({"thumb": iconimage, "icon": iconimage})
                listitem.setArt({"Poster": iconimage})
                listitem.setProperty('IsPlayable', 'true')
                listitem.setMimeType('application/x-mpegURL')
                listitem.setProperty('inputstream','inputstream.hls')
                listitem.setContentLookup(False)
                playlist.add(url2Play,listitem)
        else:
                listitem = xbmcgui.ListItem(label=name.split("|")[0], label2=name.split("|")[1], path=url2Play)
                if int(installed_version) > 18:
                        info_tag = listitem.getVideoInfoTag()
                        info_tag.setMediaType('episode')
                        info_tag.setTitle(name) #.split("|")[0])
                        listitem.setArt({'icon': iconimage, 'thumb': iconimage })
                        listitem.setPath(path=url2Play)
                        listitem.setProperty('IsPlayable', 'true')
                        playlist.add(url2Play,listitem)
                else:
                        listitem.setProperty('fanart_image', fanart)
                        listitem.setInfo(type = "episode", infoLabels = {"title": name})
                        listitem.setArt({'icon': iconimage, 'thumb': iconimage })
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
                    sub_file_xml.write(urllib.parse.urlopen(legendas).read())
                    sub_file_xml.close()
                    xmltosrt.main(sfile_xml)
                    xbmcPlayer.setSubtitles(sfile)
            else:
                xbmcPlayer.setSubtitles(legendas)

        del legendas
        del url2Play
        del urlVideo
        del xbmcPlayer

        return OK

############################################################################################################

def openConfig():
        selfAddon.openSettings()
        setViewMenu()
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

def openURL(url):
        os = ""
        user_agent = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0"

        if hasattr(sys, 'getandroidapilevel'):
            os = "Android"
        else:
            os = platform.system()

        if os == 'Windows' :
            result = subprocess.check_output(["curl", "-A", user_agent, url], shell=True)
            return result
        elif os == "Android" :
            result = subprocess.run(["curl", "-A", user_agent, url], capture_output=True,text=True,encoding='UTF-8').stdout
            return result
        else:
            headers= {
                    "Upgrade-Insecure-Requests": "1",
                    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0"
                     }
            link = requests.get(url=url, headers=headers)
            return link.text

def postURL(url):
        headers = {'Referer': base,
                   'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                   'Host': 'filmestorrentbrasil.com.br',
                   'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
        }
        response = requests.post(url=url, data='', headers=headers)
        link=response.text
        return link

def addDir(name, url, mode, iconimage, total=1, pasta=True):
        u = sys.argv[0]+"?url="+urllib.parse.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.parse.quote_plus(name)+"&iconimage="+urllib.parse.quote_plus(iconimage)

        ok = True

        liz = xbmcgui.ListItem(label=name)

        if int(installed_version) > 18:
                info_tag = liz.getVideoInfoTag()
                info_tag.setMediaType('video')
                info_tag.setTitle(name) #.split("|")[0])
                liz.setArt({'icon': iconimage, 'thumb': iconimage })
                #liz.setProperty('IsPlayable', 'true')
        else:
                liz.setProperty('fanart_image', fanart)
                liz.setInfo(type = "episode", infoLabels = {"title": name})
                liz.setArt({'icon': iconimage, 'thumb': iconimage })

        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=pasta, totalItems=total)

        del liz
        del u

        return ok

def addDirF(name,url,mode,iconimage,pasta=False,total=1) :
        u  = sys.argv[0]+"?url="+urllib.parse.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.parse.quote_plus(name)+"&iconimage="+urllib.parse.quote_plus(iconimage)

        ok = True

        liz = xbmcgui.ListItem(name)

        if int(installed_version) > 18:
                info_tag = liz.getVideoInfoTag()
                info_tag.setMediaType('video')
                info_tag.setTitle(name.split("|")[0])
                liz.setArt({'icon': iconimage, 'thumb': iconimage })
                #liz.setProperty('IsPlayable', 'true')
        else:
                liz.setProperty('fanart_image', fanart)
                liz.setInfo(type = "Video", infoLabels = {"title": name})
                liz.setArt({'icon': iconimage, 'thumb': iconimage })

        cmItems = []

        cmItems.append(('[COLOR gold]Informações do Filme[/COLOR]', 'RunPlugin(%s?url=%s&mode=98'%(sys.argv[0], url)))
        cmItems.append(('[COLOR red]Assistir Trailer[/COLOR]', 'RunPlugin(%s?name=%s&url=%s&iconimage=%s&mode=99)' % (sys.argv[0], urllib.parse.quote(name), url, urllib.parse.quote(iconimage))))
        cmItems.append(('[COLOR green]Assistir[/COLOR]', 'RunPlugin(%s?name=%s&url=%s&iconimage=%s&mode=100)' % (sys.argv[0], urllib.parse.quote(name), url, urllib.parse.quote(iconimage))))

        #xbmc.log('[plugin.video.filmestorrentbrasil] L589 - ' + str(cmItems), xbmc.LOGINFO)

        liz.addContextMenuItems(cmItems, replaceItems=False)

        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=pasta, totalItems=total)

        del liz
        del u
        del cmItems

        return ok

def getInfo(url):
        link = openURL(url)
        titO = re.findall('<meta property="og:title" content="(.*?)" />', link)[0]

        xbmc.executebuiltin('RunScript(script.extendedinfo,info=extendedinfo, name=%s)' % titO)

def playTrailer(name, url,iconimage):
        link = openURL(url)
        soup = BeautifulSoup(link, "html.parser")
        #xbmc.log('[plugin.video.filmestorrentbrasil] L610 - ' + str(url), xbmc.LOGINFO)
        #ytID = re.findall(r'data-litespeed-src="https:\/\/www.youtube.com\/embed\/(.*?).feature=oembed"', str(link))[0]
        urlF = soup.iframe['src']
        ytID = urlF.split('/')[4]
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('FilmestorrentBrasil', 'Obtendo Fontes para ' + name + ' Por favor aguarde...')
        mensagemprogresso.update(0)

        mensagemprogresso.update(100, 'Resolvendo fonte para ' + name+ ' Por favor aguarde...')
        mensagemprogresso.close()

        if not ytID :
            addon = xbmcaddon.Addon()
            addonname = addon.getAddonInfo('name')
            line1 = str("Trailer não disponível!")
            xbmcgui.Dialog().ok(addonname, line1)
            return

        mensagemprogresso.update(100)
        mensagemprogresso.close()

        xbmc.executebuiltin('RunPlugin(plugin://plugin.video.youtube/play/?video_id=%s)' % ytID)

def setViewMenu() :
        xbmcplugin.setContent(int(sys.argv[1]), 'videos')

        opcao = selfAddon.getSetting('menuVisu')
        opcao = '0'

        if   opcao == '0': xbmc.executebuiltin("Container.SetViewMode(54)")
        elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51)")
        elif opcao == '2': xbmc.executebuiltin("Container.SetViewMode(500)")

def setViewFilmes() :
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')

        opcao = selfAddon.getSetting('filmesVisu')
        opcao = '2'

        #xbmc.log('[plugin.video.filmestorrentbrasil] L649 - ' + str(opcao), xbmc.LOGINFO)

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
        link = unicode(link, 'utf-8', 'ignore')
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
elif mode == 20   : getFilmes(name,url,iconimage)
elif mode == 25   : getSeries(url)
elif mode == 26   : getTemporadas(name,url,iconimage)
elif mode == 27   : getEpisodios(name,url,iconimage)
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
