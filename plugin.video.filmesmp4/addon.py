#####################################################################
# -*- coding: utf-8 -*-
#####################################################################
# Addon : FilmesMP4
# By AddonBrasil - 11/12/2015
# Atualizado (1.0.0) - 20/08/2021
# Atualizado (1.0.1) - 21/09/2021
#####################################################################

import urllib, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon, os, time, base64
import json
import urlresolver
import requests

from bs4            import BeautifulSoup
from resources.lib  import jsunpack
from time           import time

version   = '1.0.1'
addon_id  = 'plugin.video.filmesmp4'
selfAddon = xbmcaddon.Addon(id=addon_id)

addonfolder = selfAddon.getAddonInfo('path')
artfolder   = addonfolder + '/resources/media/'
fanart      = addonfolder + '/fanart.png'
base        = 'https://filmesmp4.com/'

############################################################################################################

def menuPrincipal():
        addDir('Categorias'       , base + ''                           ,   10, artfolder + 'categorias.png')
        addDir('Lançamentos'      , base + 'category/lancamentos/'      ,   20, artfolder + 'filmes.png')
        addDir('Seriados'         , base + 'category/series/'           ,   25, artfolder + 'series.png')
        addDir('Pesquisa Series'  , '--'                                ,   30, artfolder + 'pesquisa.png')
        addDir('Pesquisa Filmes'  , '--'                                ,   35, artfolder + 'pesquisa.png')
        addDir('Configurações'    , base                                ,  999, artfolder + 'config.png', 1, False)

        setViewMenu()

def getCategorias(url):
        link = openURL(url)
        soup = BeautifulSoup(link, 'html.parser')
        conteudo = soup('nav', {'class':'menu'})
        categorias = conteudo[0]('li')

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
        xbmc.log('[plugin.video.filmesmp4] L74 ' + str(url), xbmc.LOGINFO)
        link = openURL(url)
        soup = BeautifulSoup(link, 'html.parser')
        conteudo = soup("div", {"class":"listagem"})
        filmes = conteudo[0]("div", {"class":"item"})

        totF = len(filmes)

        for databox in filmes:
                imgF = databox.img['src']
                titF = databox.a['title'] #.encode('utf-8')
                urlF = databox.a['href']
                pltF = ""
                addDirF(titF, urlF, 100, imgF, False, totF, pltF)

        try :
                proxima = re.findall('<link rel="next" href="(.*?)"\s*/>', link)[0]
                addDir('Próxima Página >>', proxima, 20, artfolder + 'proxima.png')
        except :
                pass

        setViewFilmes()

def getSeries(url):
        xbmc.log('[plugin.video.filmesmp4] L91 ' + str(url), xbmc.LOGINFO)
        link = openURL(url)
        soup = BeautifulSoup(link, 'html.parser')
        conteudo = soup("div", {"class":"listagem"})
        filmes = conteudo[0]("div", {"class":"item"})

        totF = len(filmes)

        for databox in filmes:
                imgF = databox.img['src']
                titF = databox.a['title'] #.encode('utf-8')
                urlF = databox.a['href']
                pltF = ""
                addDirF(titF, urlF, 27, imgF, True, totF, pltF)

        try :
                proxima = re.findall('<link rel="next" href="(.*?)"', link)[0]
                addDir('Próxima Página >>', proxima, 25, artfolder + 'proxima.png')
        except :
                pass

        #xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')
        setViewFilmes()

def getTemporadas(name,url,iconimage):
        xbmc.log('[plugin.video.filmesmp4] L155 ' + str(url), xbmc.LOGINFO)
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

def getEpisodios(name, url ,iconimage):
        xbmc.log('[plugin.video.filmesmp4] L175 ' + str(url), xbmc.LOGINFO)
        link = openURL(url)
        soup = BeautifulSoup(link, 'html.parser')
        conteudo = soup('div', {'class':'content clearfix'})
        links = conteudo[0]('p')
        imgF = links[0].img['src']
        idsT = []
        idsU = []
        
        tepis = links[7]    #titulo episodio
        for i in tepis:
            if 'EPIS' in i : 
                titF = i
                idsT.append(titF)
                
        lepis = links[7]('a') #link episodio
        for i in lepis:
            if 'filmesmp4' in i['href']:
                urlF = i['href']
                idsU.append(urlF)
                
        totF = len(idsT)

        for i in range(0, totF):
            urlF = idsU[i]
            titF = idsT[i]
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
                filmes = soup.findAll('div', {'class':'image'})
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
        xbmc.log('[plugin.video.filmesmp4] L210 - ' + str(url), xbmc.LOGINFO)
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('FilmesMP4', 'Obtendo Fontes para ' + name + ' Por favor aguarde...')
        mensagemprogresso.update(0)

        titsT = []
        idsT = []

        link = openURL(url)
        soup = BeautifulSoup(link, 'html.parser')
        conteudo = soup.select(".botoes-post")
        links = conteudo[0]('a')

        for i in links:
            if '' != i['href'] : 
                urlF = i['href']
                xbmc.log('[plugin.video.filmesmp4] L226 - ' + str(urlF), xbmc.LOGINFO)

        urlVideo = urlF

        xbmc.log('[plugin.video.filmesmp4] L231 - ' + str(urlVideo), xbmc.LOGINFO)

        mensagemprogresso.update(50, 'Resolvendo fonte para ' + name +' Por favor aguarde...')

        if 'filmesmp4' in urlVideo or 'pandafiles' in urlVideo :
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

        xbmc.log('[plugin.video.filmesmp4] L274 - ' + str(url2Play), xbmc.LOGINFO)

        if not url2Play : return

        legendas = '-'

        mensagemprogresso.update(75, 'Abrindo Sinal para ' + name +' Por favor aguarde...')

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
                listitem = xbmcgui.ListItem(name, path=url2Play)
                listitem.setArt({"thumb": iconimage, "icon": iconimage})
                listitem.setProperty('IsPlayable', 'true')
                listitem.setMimeType('video/mp4')
                playlist.add(url2Play,listitem)

        xbmcPlayer = xbmc.Player()

        while xbmcPlayer.play(playlist) :
            xbmc.sleep(20000)
            if not xbmcPlayer.isPlaying():
                xbmc.stop()

        mensagemprogresso.update(100)
        mensagemprogresso.close()

        if legendas != '-':
            if 'timedtext' in legendas:
                    import os.path
                    sfile = os.path.join(xbmc.translatePath("special://temp"),'sub.srt')
                    sfile_xml = os.path.join(xbmc.translatePath("special://temp"),'sub.xml')#timedtext
                    sub_file_xml = open(sfile_xml,'w')
                    sub_file_xml.write(urllib2.urlopen(legendas).read())
                    sub_file_xml.close()
                    xmltosrt.main(sfile_xml)
                    xbmcPlayer.setSubtitles(sfile)
            else:
                xbmcPlayer.setSubtitles(legendas)


def player_series(name,url,iconimage):
        xbmc.log('[plugin.video.filmesmp4] L511 - ' + str(url), xbmc.LOGINFO)
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('FilmesMP4', 'Obtendo Fontes para ' + name + ' Por favor aguarde...')
        mensagemprogresso.update(0)

        titsT = []
        idsT = []
        links = []
        hosts = []

        link = openURL(url)
        soup = BeautifulSoup(link, 'html.parser')
        dados = soup('li',{'id':'player-option-1'})
        xbmc.log('[plugin.video.filmesmp4] L526 - ' + str(dados), xbmc.LOGINFO)
        if not dados :
                dialog = xbmcgui.Dialog()
                dialog.ok(name, " ainda não liberado, aguarde... ")
                return

        dooplay = []
        dtype = dados[0]['data-type']
        dpost = dados[0]['data-post']
        dnume = dados[0]['data-nume']
        dooplay = re.findall(r'<li id=[\'"]player-option-1[\'"] class=[\'"]dooplay_player_option.+?[\'"] data-type=[\'"](.+?)[\'"] data-post=[\'"](.+?)[\'"] data-nume=[\'"](.+?)[\'"]>', link)

        for dtype, dpost, dnume in dooplay:
            print(dtype, dpost, dnume)

        try:
            headers = {'Referer': url,
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'Host': 'www.filmesmp4.net',
                    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
            }
            urlF = 'https://www.filmesmp4.net/wp-admin/admin-ajax.php'
            data = urllib.urlencode({'action': 'doo_player_ajax', 'post': dpost, 'nume': dnume, 'type': dtype})
            xbmc.log('[plugin.video.filmesmp4] L547 - ' + str(data), xbmc.LOGINFO)
            r = requests.post(url=urlF, data=data, headers=headers)
            html = r.content
            soup = BeautifulSoup(html, 'html.parser')
        except:
            pass

        try:
            urlF = soup.iframe['src']
            xbmc.log('[plugin.video.filmesmp4] L553 - ' + str(urlF), xbmc.LOGINFO)
        except:
            pass

        try:
            urlF = soup.a['href']
            fxID = urlF.split('l=')[1]
            urlF = base64.b64decode(fxID)
            xbmc.log('[plugin.video.filmesmp4] L558 - ' + str(urlF), xbmc.LOGINFO)
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

        urlVideo = urlF

        xbmc.log('[plugin.video.filmesmp4] L622 - ' + str(urlVideo), xbmc.LOGINFO)

        if 'play.filmesmp4.com' in urlVideo:
                html = requests.get(urlVideo).text
                match = re.findall('idS="(.+?)"', html)
                for x in match:
                    idsT.append(x)
                match = re.findall('<button class="btn btn-l.+?" idS=".+?" id="btn-(.+?)"><i id="icon-.+?" class="glyphicon glyphicon-play-circle"></i> Others</button>', html)
                for x in match:
                        if x =='0' : titsT.append("Dublado")
                        if x =='1' : titsT.append("Legendado")

                if not titsT : return

                index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

                if index == -1 : return

                i = int(index)
                idS = idsT[i]

                headers = {'Referer': url,
                           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                           'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                           'Host': 'play.filmesmp4.com',
                           'Connection': 'keep-alive',
                           'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
                }
                urlF ='https://play.filmesmp4.com/CallEpi'
                data = urllib.parse.urlencode({'idS': idS})
                r = requests.post(url=urlF, data=data, headers=headers)
                xbmc.log('[plugin.video.filmesmp4] L591 - ' + str(data), xbmc.LOGINFO)

                xbmc.log('[plugin.video.filmesmp4] L593 - ' + str(r.text), xbmc.LOGINFO)

                html = r.text
                _html = str(html)
                _html = bytes.fromhex(_html).decode('utf-8')
                b = json.loads(_html)
                c = b['video']
                urlF = c[0]['file']
                headers = {'referer': urlVideo,
                            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'}
                r = requests.get(url=urlF,allow_redirects=False,headers=headers)
                urlF = r.headers['Location']
                r = requests.get(url=urlF,allow_redirects=False,headers=headers)
                urlF = r.headers['Location']
                urlVideo = urlF

                xbmc.log('[plugin.video.filmesmp4] L602 - ' + str(urlVideo), xbmc.LOGINFO)

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
                        xbmc.log('[plugin.video.filmesmp4] L629 - ' + str(urlVideo), xbmc.LOGINFO)
                        OK = True

                        if 'alfastream.cc' in urlVideo:
                                if 'actelecup.com' in urlVideo:
                                        xbmc.log('[plugin.video.filmesmp4] L634 - ' + str(urlVideo), xbmc.LOGINFO)
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

        xbmc.log('[plugin.video.filmesmp4] L646 ' + str(urlVideo), xbmc.LOGINFO)

        mensagemprogresso.update(50, 'Resolvendo fonte para ' + name + ' Por favor aguarde...')

        if OK : url2Play = urlresolver.resolve(urlVideo)

        if not url2Play : return

        legendas = '-'

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
                listitem = xbmcgui.ListItem(name, path=url2Play)
                listitem.setArt({"thumb": iconimage, "icon": iconimage})
                listitem.setProperty('IsPlayable', 'true')
                listitem.setMimeType('video/mp4')
                playlist.add(url2Play,listitem)

        xbmcPlayer = xbmc.Player()

        while xbmcPlayer.play(playlist) :
            xbmc.sleep(20000)
            if not xbmcPlayer.isPlaying():
                xbmc.stop()

        mensagemprogresso.update(100)
        mensagemprogresso.close()

        if legendas != '-':
            if 'timedtext' in legendas:
                    import os.path
                    sfile = os.path.join(xbmc.translatePath("special://temp"),'sub.srt')
                    sfile_xml = os.path.join(xbmc.translatePath("special://temp"),'sub.xml')#timedtext
                    sub_file_xml = open(sfile_xml,'w')
                    sub_file_xml.write(urllib2.urlopen(legendas).read())
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
                   'Host': 'www.filmesmp4.net',
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
        cmItems.append(('[COLOR red]Assistir Trailer[/COLOR]', 'RunPlugin(%s?name=%s&url=%s&iconimage=%s&mode=99)'%(sys.argv[0], urllib.parse.quote(name), url, urllib.parse.quote(iconimage))))

        liz.addContextMenuItems(cmItems, replaceItems=False)

        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=pasta, totalItems=total)

        return ok

def getInfo(url):
        link = openURL(url)
        titO = re.findall('<meta property="og:title" content="(.*?)" />', link)[0]

        xbmc.executebuiltin('XBMC.RunScript(script.extendedinfo,info=extendedinfo, name=%s)' % titO)

def playTrailer(name, url,iconimage):
        link = openURL(url)
        ytID = re.findall('<iframe title="Trailer" width=".*?" height=".*?" src="https://www.youtube.com/embed/(.*?)" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>', link)[0]
        #ytID = '' #SytID.replace('?','')
        xbmc.log('[plugin.video.filmesmp4] L637 - ' + str(ytID), xbmc.LOGINFO)
        if ytID == '' : 
            dialog = xbmcgui.Dialog()
            dialog.ok(" Desculpe:", " Trailer não disponivel! ")
            return ''
        xbmc.executebuiltin('RunPlugin("plugin://plugin.video.youtube/play/?video_id=%s")' % ytID)
        #xbmc.executebuiltin('XBMC.RunPlugin("plugin://script.extendedinfo/?info=youtubevideo&&id=%s")' % ytID)

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
