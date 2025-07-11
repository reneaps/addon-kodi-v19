#####################################################################
# -*- coding: utf-8 -*-
#####################################################################
# Addon : FilmestorrentBrasil
# By AddonBrasil - 08/08/2020
# Atualizado (2.1.1) - 17/12/2023
# Atualizado (2.1.2) - 25/12/2023
# Atualizado (2.1.3) - 28/12/2023
# Atualizado (2.1.4) - 03/01/2024
# Atualizado (2.1.5) - 04/01/2024
# Atualizado (2.1.6) - 05/01/2024
# Atualizado (2.1.7) - 09/01/2024
# Atualizado (2.1.8) - 09/01/2024
# Atualizado (2.1.9) - 22/01/2024
# Atualizado (2.2.0) - 26/01/2024
# Atualizado (2.2.1) - 09/02/2024
# Atualizado (2.2.2) - 08/04/2024
# Atualizado (2.2.3) - 11/10/2024
# Atualizado (3.0.0) - 08/11/2024 > mudou site
# Atualizado (3.0.1) - 11/11/2024
# Atualizado (3.0.2) - 12/11/2024
# Atualizado (3.0.3) - 17/11/2024
# Atualizado (3.0.4) - 18/11/2024
# Atualizado (3.0.5) - 26/11/2024
# Atualizado (3.0.6) - 01/07/2025
# Atualizado (3.0.7) - 02/07/2025
# Atualizado (3.0.8) - 02=6/07/2025
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
base        = 'https://www.starckfilmes.com.br'

############################################################################################################

def menuPrincipal():
        addDir('Categorias'                 , base                          ,   10, artfolder + 'categorias.png')
        addDir('Lançamentos'                , base + '/?type=filme'         ,   20, artfolder + 'new.png')
        addDir('Seriados'                   , base + '/?type=série'         ,   25, artfolder + 'series.png')
        addDir('Pesquisa Series'            , '--'                          ,   30, artfolder + 'pesquisa.png')
        addDir('Pesquisa Filmes'            , '--'                          ,   35, artfolder + 'pesquisa.png')
        #addDir('Configurações'              , base                          ,  999, artfolder + 'config.png', 1, False)

        setViewMenu()

def getCategorias(url):
        link = openURL(url)
        soup = BeautifulSoup(link, 'html.parser')
        #conteudo = soup('div',{'class':'elementor-widget-container'})
        conteudo = soup('nav')
        categorias = conteudo[0]('li')

        totC = len(categorias)

        for categoria in categorias:
                titC = categoria.a.text
                urlC = categoria.a["href"]
                urlC = 'http:%s' % urlC if urlC.startswith("//") else urlC
                urlC = base + urlC if urlC.startswith("/") else urlC
                imgC = artfolder + limpa(titC) + '.png'
                addDir(titC,urlC,20,imgC)

        setViewMenu()

def getFilmes(name,url,iconimage):
        xbmc.log('[plugin.video.filmestorrentbrasil] L86 - ' + str(url), xbmc.LOGINFO)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='movies')
        link = openURL(url)
        soup = BeautifulSoup(link, "html.parser")
        conteudo = soup('div',{'class':'home post-catalog'})
        filmes = conteudo[0]('div',{'class':'item'})

        totF = len(filmes)

        for filme in filmes:
            titF = ""
            try:
                urlF = filme('a')[0]['href']
                titF = filme('a')[1].text
                #xbmc.log('[plugin.video.filmestorrentbrasil] L100- ' + str(titF), xbmc.LOGINFO)
                imgF = filme('div',{'class':'post-image-sub'})[0].get('data-bk')
                urlF = base + urlF if urlF.startswith("/") else urlF
                pltF = titF
                addDirF(titF, urlF, 100, imgF, False, totF)
            except:
                pass

        try :
                proxima = re.findall(r'<div class="prev-active"><a href="(.*?)">.*?</a></div>', str(soup))
                if len(proxima) > 1:
                    proxima = proxima[1]
                else:
                    proxima = proxima[0]
                proxima = base + proxima if proxima.startswith("/") else proxima
                addDir('Próxima Página >>', proxima, 20, artfolder + 'proxima.png')
        except :
                pass

        setViewFilmes()

def getSeries(url):
        xbmc.log('[plugin.video.filmestorrentbrasil] L122 - ' + str(url), xbmc.LOGINFO)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')
        link = openURL(url)
        soup = BeautifulSoup(link, "html.parser")
        conteudo = soup('div', {'class':'home post-catalog'})
        filmes = conteudo[0]('div', {'class':'item'})

        totF = len(filmes)

        for filme in filmes:
                urlF = filme('a')[0]['href']
                titF = filme('a')[1].text.encode('utf-8')
                imgF = filme('div',{'class':'post-image-sub'})[0].get('data-bk')
                urlF = base + urlF if urlF.startswith("/") else urlF
                pltF = titF
                addDirF(titF, urlF, 27, imgF, True, totF)

        try :
                proxima = re.findall(r'<div class="prev-active"><a href="(.*?)">.*?</a></div>', str(soup))
                if len(proxima) > 1:
                    proxima = proxima[1]
                else:
                    proxima = proxima[0]
                proxima = base + proxima if proxima.startswith("/") else proxima
                addDir('Próxima Página >>', proxima, 25, artfolder + 'proxima.png')
        except :
                pass

        #setViewFilmes()

def getTemporadas(name,url,iconimage):
        xbmc.log('[plugin.video.filmestorrentbrasil] L153 - ' + str(url), xbmc.LOGINFO)
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
                    addDir(titF, urlF, 27, iconimage, True, totF)
                except:
                    pass
                i = i + 1

        xbmcplugin.setContent(_handle, content='seasons')

def getEpisodios(name, url, iconimage):
        xbmc.log('[plugin.video.filmestorren tbrasil] L173 - ' + str(url), xbmc.LOGINFO)
        xbmcplugin.setContent(_handle, content='episodes')
        link = openURL(url)
        soup = BeautifulSoup(link, 'html.parser')
        conteudo = soup("div", {"class":"container"})
        filmes = conteudo[1]("div", {"class":"post-buttons"})
        links = filmes[0]('a')
        ''''
        for i in conteudo:
                if 'catalog' in str(i):
                        links = i('a')
        #links = soup('p')
        #if 'buttons-content' in str(links) : links = soup('div',{'class':'buttons-content'})
        '''
        totF = len(links)
        imgF = iconimage
        try:
            imgF = links[1].img['src']
        except:
            pass

        for link in links:
            if 'campanha' in str(link):
                #if titF: titF = 'Epis'
                u = link.a['href']
                fxID = u.split('?id=')[-1]
                urlF = base64.b64decode(fxID).decode('utf-8')
                urlF = base + urlF if urlF.startswith("/") else urlF
                titF = name.split("emporada")[0] + " | " + str(titF)
                addDirF(titF, urlF, 110, imgF, False, totF)
            elif '91A89222EFDC' in str(link):
                #if titF: titF = 'Epis'
                #u = link.a['href']
                u = link['href']
                fxID = u[::-1]
                urlF = base64.b64decode(fxID) #.decode('utf-8')
                urlF = urllib.parse.unquote(urlF)
                urlF = base + urlF if urlF.startswith("/") else urlF
                titF = urlF.split('&')[1]
                titF = titF.replace('dn=','')
                titF = urllib.parse.unquote(titF)
                addDirF(titF, urlF, 110, imgF, False, totF)
            elif 'magnet' in str(link):
                urlF = link['href']
                urlF = base + urlF if urlF.startswith("/") else urlF
                titF = urlF.split('&')[1]
                titF = titF.replace('dn=','')
                titF = urllib.parse.unquote(titF)
                titF = urllib.parse.unquote(titF)
                #addDirF(name+"|"+titF, urlF, 110, imgF, False, totF)
                addDirF(titF, urlF, 110, imgF, False, totF)

def pesquisa():
        keyb = xbmc.Keyboard('', 'Pesquisar Filmes')
        keyb.doModal()

        if (keyb.isConfirmed()):
                texto    = keyb.getText()
                pesquisa = urllib.parse.quote(texto)
                url      = base + '?s=%s' % str(pesquisa)

                xbmc.log('[plugin.video.filmestorrentbrasil] L234 - ' + str(url), xbmc.LOGINFO)
                hosts = []
                temp = []
                link = openURL(url)
                soup = BeautifulSoup(link, "html.parser")
                conteudo = soup('div',{'class':'home post-catalog'})
                filmes = conteudo[0]('div',{'class':'item'})

                totF = len(filmes)

                for filme in filmes:
                        titF = ""
                        try:
                            urlF = filme('a')[0]['href']
                            titF = filme('a')[1].text
                            imgF = filme('div',{'class':'post-image-sub'})[0].get('data-bk')
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
            xbmc.log('[plugin.video.filmestorrentbrasil] L263 - ' + str(url2), xbmc.LOGINFO)
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
        xbmc.log('[plugin.video.filmestorrentbrasil] L278 - ' + str(url), xbmc.LOGINFO)
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('FilmestorrentBrasil', 'Obtendo Fontes para ' + name + ' Por favor aguarde...')
        mensagemprogresso.update(0)

        titsT = []
        idsT = []
        sub = None

        link = openURL(url)
        soup = BeautifulSoup(link, "html.parser")
        conteudo = soup("div",{"class":"container"})
        buttons = conteudo[1]("div",{"class":"buttons-content"})
        links=[]
        for i in buttons:
                if '91A89222EFDC' in str(i):
                    links.append(i)
                elif 'magnet' in str(i):
                    links.append(i)

        n = 1

        for link in links:
            if 'campanha' in str(link) :
                urlF = link.a['href']
                print(urlF)
                idS = urlF.split('id=')[-1]
                urlVideo = base64.b64decode(idS)
                titS = "Server_" + str(n)
                n = n + 1
                titsT.append(titS)
                idsT.append(urlVideo)
            elif '91A89222EFDC' in str(link):
                #if titF: titF = 'Epis'
                u = link.a['href']
                fxID = u[::-1]
                urlVideo = base64.b64decode(fxID)
                urlVideo = urllib.parse.unquote(urlVideo)
                xbmc.log('[plugin.video.filmestorrentbrasil] L317 - ' + str(urlVideo[0]), xbmc.LOGINFO)
                titS = "Server_" + str(n)
                n = n + 1
                titsT.append(titS)
                idsT.append(urlVideo)
            if 'magnet' in str(link):
                urlF = link.a['href']
                urlVideo = urlF
                if '&dn=' in str(urlF) :
                    titF = urlF.split('&dn=')[1].split('&tr=')[0]
                    titF = urllib.parse.unquote(titF)
                    titS = titF[0:50]
                else:
                    titS = link.text.replace('\n','') #"Server_" +str(n)
                n = n + 1
                titsT.append(titS)
                idsT.append(urlVideo)

        if not titsT : return

        index = xbmcgui.Dialog().select('Selecione uma das opcoes :', titsT)

        if index == -1 : return

        i = int(index)
        urlVideo = idsT[i]

        xbmc.log('[plugin.video.filmestorrentbrasil] L344 - ' + str(urlVideo), xbmc.LOGINFO)

        mensagemprogresso.update(50, 'Resolvendo fonte para ' + name + ' Por favor aguarde...')

        if 'magnet' in str(urlVideo) :
                #urlVideo = urllib.parse.unquote(urlVideo)
                if "&amp;" in str(urlVideo) : urlVideo = urlVideo.replace("&amp;","&")
                url2Play = 'plugin://plugin.video.elementum/play?uri={0}'.format(urlVideo)
                #xbmc.executebuiltin('RunPlugin(%s)' % url2Play)
                #return
                OK = False

        if OK :
            try:
                url2Play = urlresolver.resolve(urlVideo)
            except:
                dialog = xbmcgui.Dialog()
                dialog.ok(" Erro:", " Video removido! ")
                url2Play = []
                pass

        xbmc.log('[plugin.video.filmestorrentbrasil] L365 - ' + str(url2Play), xbmc.LOGINFO)

        if not url2Play : return

        if sub is None:
            legendas = '-'
        else:
            legendas = sub

        mensagemprogresso.update(75, 'Abrindo Sinal para ' +name+' Por favor aguarde...')

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
                #listitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
                #listitem.setMimeType('application/dash+xml')
                listitem.setContentLookup(False)
                playlist.add(url2Play,listitem)
        else:
                listitem = xbmcgui.ListItem(name, path=url2Play)
                if int(installed_version) > 18:
                        info_tag = listitem.getVideoInfoTag()
                        info_tag.setMediaType('video')
                        info_tag.setTitle(name.split("|")[0])
                        listitem.setArt({'icon': iconimage, 'thumb': iconimage })
                        playlist.add(url2Play,listitem)
                else:
                        listitem.setProperty('fanart_image', fanart)
                        listitem.setInfo(type = "Video", infoLabels = {"title": name})
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

        return OK

def player_series(name,url,iconimage):
        xbmc.log('[plugin.video.filmestorrentbrasil] L431 - ' + str(url), xbmc.LOGINFO)
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

        xbmc.log('[plugin.video.filmestorrentbrasil] L449 - ' + str(url2Play), xbmc.LOGINFO)

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
                listitem = xbmcgui.ListItem(name, path=url2Play)
                if int(installed_version) > 18:
                        info_tag = listitem.getVideoInfoTag()
                        info_tag.setMediaType('video')
                        info_tag.setTitle(name) #.split("|")[0])
                        listitem.setArt({'icon': iconimage, 'thumb': iconimage })
                        listitem.setProperty('IsPlayable', 'true')
                        listitem.setContentLookup(False)
                        playlist.add(url2Play,listitem)
                else:
                        listitem.setProperty('fanart_image', fanart)
                        listitem.setInfo(type = "Video", infoLabels = {"title": name})
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

        return OK

############################################################################################################

def openConfig():
        selfAddon.openSettings()
        setViewMenu()
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

def openURL(url):
        os = ""
        user_agent = "User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0"
        upgrade_requests = "Upgrade-Insecure-Requests: 1"

        if hasattr(sys, 'getandroidapilevel'):
            os = "Android"
        else:
            os = platform.system()

        if os == '2Windows' :
            result = subprocess.check_output(["curl", "--compressed", "-H", user_agent, "-H", upgrade_requests, url], shell=True)
            return result
        elif os == "2Android" :
            result = subprocess.run(["curl", "-H", user_agent, "-H", upgrade_requests, url], capture_output=True,text=True,encoding='UTF-8').stdout
            return result
        else:
            headers= {
                    "Upgrade-Insecure-Requests": "1",
                    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0"
                     }
            link = requests.get(url=url, headers=headers).content
            return link

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

        liz = xbmcgui.ListItem(name)

        if int(installed_version) > 18:
                info_tag = liz.getVideoInfoTag()
                info_tag.setMediaType('video')
                info_tag.setTitle(name) #.split("|")[0])
                liz.setArt({'icon': iconimage, 'thumb': iconimage })
                #liz.setProperty('IsPlayable', 'false')
        else:
                liz.setProperty('fanart_image', fanart)
                liz.setInfo(type = "Video", infoLabels = {"title": name})
                liz.setArt({'icon': iconimage, 'thumb': iconimage })

        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=pasta, totalItems=total)

        return ok

def addDirF(name,url,mode,iconimage,pasta=False,total=1) :
        u  = sys.argv[0]+"?url="+urllib.parse.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.parse.quote_plus(name)+"&iconimage="+urllib.parse.quote_plus(iconimage)

        ok = True

        liz = xbmcgui.ListItem(name)

        if int(installed_version) > 18:
                info_tag = liz.getVideoInfoTag()
                info_tag.setMediaType('video')
                if "|" in str(name) : info_tag.setTitle(name.split("|")[0])
                liz.setArt({'icon': iconimage, 'thumb': iconimage, 'fanart':iconimage  })
                #liz.setProperty('IsPlayable', 'true')
        else:
                liz.setProperty('fanart_image', fanart)
                liz.setInfo(type = "Video", infoLabels = {"title": name})
                liz.setArt({ 'icon': iconimage, 'thumb': iconimage})

        cmItems = []

        cmItems.append(('[COLOR gold]Informações do Filme[/COLOR]', 'RunPlugin(%s?url=%s&mode=98'%(sys.argv[0], url)))
        cmItems.append(('[COLOR red]Assistir Trailer[/COLOR]', 'RunPlugin(%s?name=%s&url=%s&iconimage=%s&mode=99)' % (sys.argv[0], urllib.parse.quote(name), url, urllib.parse.quote(iconimage))))
        cmItems.append(('[COLOR red]Assistir[/COLOR]', 'RunPlugin(%s?name=%s&url=%s&iconimage=%s&mode=100)' % (sys.argv[0], urllib.parse.quote(name), url, urllib.parse.quote(iconimage))))

        liz.addContextMenuItems(cmItems, replaceItems=False)

        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=pasta, totalItems=total)

        return ok

def getInfo(url):
        link = openURL(url)
        titO = re.findall('<meta property="og:title" content="(.*?)" />', link)[0]

        xbmc.executebuiltin('RunScript(script.extendedinfo,info=extendedinfo, name=%s)' % titO)

def playTrailer(name, url,iconimage):
        link = openURL(url)
        ytID = re.findall(r'data-youtube-link=https:\/\/www.youtube.com\/embed\/(.*?)></div>',link)[0]
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('FilmestorrentBrasil', 'Obtendo Fontes para ' + name + ' Por favor aguarde...')
        mensagemprogresso.update(0)

        mensagemprogresso.update(100, 'Resolvendo fonte para ' + name+ ' Por favor aguarde...')
        mensagemprogresso.close()
        xbmc.log('[plugin.video.filmestorrentbrasil] L631 - ' + str(name), xbmc.LOGINFO)

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
        xbmcplugin.setContent(int(sys.argv[1]), 'episodes')

        opcao = selfAddon.getSetting('menuVisu')
        opcao = '0'

        if   opcao == '0': xbmc.executebuiltin("Container.SetViewMode(54)")
        elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51)")
        elif opcao == '2': xbmc.executebuiltin("Container.SetViewMode(500)")

def setViewFilmes() :
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')

        opcao = selfAddon.getSetting('filmesVisu')
        opcao = '2'

        #xbmc.log('[plugin.video.filmestorrentbrasil] L661 - ' + str(opcao), xbmc.LOGINFO)

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
