from theplatform import *

try:
    from pyamf import remoting
    has_pyamf = True
except ImportError:
    has_pyamf = False

try:
    from sqlite3 import dbapi2 as sqlite

except:
    from pysqlite2 import dbapi2 as sqlite


class CTVBaseChannel(BaseChannel):
    status = STATUS_GOOD
    is_abstract = True
    root_url = 'VideoLibraryWithFrame.aspx'
    default_action = 'root'

    def action_root(self):
        url = self.base_url + self.root_url
        soup = BeautifulSoup(
            self.plugin.fetch(url, max_age=self.cache_timeout))
        ul = soup.find('div', {'id': 'Level1'}).find('ul')
        for li in ul.findAll('li'):
            data = {}
            data.update(self.args)
            data['Title'] = decode_htmlentities(li.a['title'])
            data['action'] = 'browse_show'
            data['show_id'] = li.a['id']
            self.plugin.add_list_item(data)
        self.plugin.end_list()

    def action_browse(self):
        """
        DEPRECATED Bookmarks Shouldn't Use this..
        need to find a way to update user's bookmarks

        """
        rurl = self.args.get('remote_url', 'None')
        if rurl == 'None' or rurl is None:
            return self.action_root()

        logging.debug("RURL: %s" % (rurl.__class__,))
        show_id = re.findall(r"\&ShowID=(\d+)", rurl)
        if show_id:
            self.args['show_id'] = show_id[0]
            return self.action_browse_show()

        season_id = re.findall(r"\&SeasonID=(\d+)", rurl)
        if season_id:
            self.args['season_id'] = season_id[0]
            return self.action_browse_season()

        episode_id = re.findall(r"&EpisodeID=(\d+)", rurl)
        if episode_id:
            self.args['episode_id'] = eposode_id[0]
            return self.action_browse_episode()

    def action_browse_season(self):
        url = "http://esi.ctv.ca/datafeed/pubsetservice.aspx?sid=" + \
            self.args['season_id']
        page = self.plugin.fetch(url, max_age=self.cache_timeout).read()
        soup = BeautifulStoneSoup(page)
        for ep in soup.overdrive.gateway.contents:
            if not ep.playlist.contents:
                continue
            data = {}
            data.update(self.args)
            data['Title'] = ep.meta.headline.contents[0].strip()
            data['Plot'] = ep.meta.subhead.contents[0].strip()
            m, d, y = ep['pubdate'].split("/")
            data['Date'] = "%s.%s.%s" % (d, m, y)
            try:
                data['Thumb'] = ep.meta.image.contents[0].strip()
            except:
                pass

            data['videocount'] = ep['videocount']
            vc = int(ep['videocount'])
            if vc == 1:
                action = 'play_episode'
            elif vc <= int(self.plugin.get_setting('max_playlist_size')) \
                and self.plugin.get_setting("make_playlists") == "true":
                action = 'play_episode'
            else:
                action = 'browse_episode'
            data['action'] = action
            data['episode_id'] = ep['id']
            self.plugin.add_list_item(data, is_folder=vc != 1)
        self.plugin.end_list('episodes', [xbmcplugin.
            SORT_METHOD_DATE, xbmcplugin.SORT_METHOD_LABEL])

    def action_play_episode(self):
        import xbmc
        vidcount = self.args.get('videocount')
        if vidcount:
            vidcount = int(vidcount)

        if vidcount and vidcount == 1:
            data = list(self.iter_clip_list())[0]
            logging.debug(data)
            url = self.clipid_to_stream_url(data['clip_id'])
            return self.plugin.set_stream_url(url, data)
        else:
            playlist = xbmc.PlayList(1)
            playlist.clear()
            for clipdata in self.iter_clip_list():
                url = self.plugin.get_url(clipdata)
                li = self.plugin.add_list_item(
                    clipdata, is_folder=False, return_only=True)
                ok = playlist.add(url, li)
                logging.debug(
                    "CLIPDATA: %s, %s, %s, %s" % (clipdata, url, li, ok))

            time.sleep(1)
            logging.debug("CLIPDATA: %s" % (playlist,))
            xbmc.Player().play(playlist)
            xbmc.executebuiltin('XBMC.ActivateWindow(fullscreenvideo)')
            self.plugin.end_list()

    def iter_clip_list(self):
        url = "http://esi.ctv.ca/datafeed/content.aspx?cid=" + \
            self.args['episode_id']
        soup = BeautifulStoneSoup(
            self.plugin.fetch(url, max_age=self.cache_timeout))

        plot = soup.find('content').meta.subhead.contents[0].strip()

        for el in soup.find('playlist').findAll('element'):
            data = {}
            data.update(self.args)
            data['action'] = 'play_clip'
            data['Title'] = el.title.contents[0].strip()
            data['Plot'] = plot
            data['clip_id'] = el['id']
            yield data

    def action_browse_episode(self):
        logging.debug("ID: %s" % (self.args['episode_id'],))
        for data in self.iter_clip_list():
            self.plugin.add_list_item(data, is_folder=False)
        self.plugin.end_list()

    def action_browse_show(self):
        url = self.base_url + 'VideoLibraryContents.aspx?GetChildOnly=true&PanelID=2&ShowID=%s' % (self.args['show_id'],)
        soup = BeautifulSoup(
            self.plugin.fetch(url, max_age=self.cache_timeout))
        div = soup.find('div', {'id': re.compile('^Level\d$')})
        levelclass = [c for c in re.split(r"\s+", div['class'])
            if c.startswith("Level")][0]
        levelclass = int(levelclass[5:])
        if levelclass == 4:
            # Sites like TSN Always return level4 after the top level
            for li in soup.findAll('li'):
                a = li.find('dl', {"class": "Item"}).dt.a
                data = {}
                data.update(self.args)
                data.update(parse_bad_json(a['onclick'][45:-16]))
                data['action'] = 'play_clip'
                data['clip_id'] = data['ClipId']
                self.plugin.add_list_item(data, is_folder=False)
            self.plugin.end_list()

        else:
            for li in soup.find('ul').findAll('li'):
                a = li.find('a')
                is_folder = True
                data = {}
                data.update(self.args)
                if "Interface.GetChildPanel('Season'" in a['onclick']:
                    data['action'] = 'browse_season'
                    data['season_id'] = a['id']
                elif "Interface.GetChildPanel('Episode'" in a['onclick']:
                    data['action'] = 'browse_episode'
                    if self.plugin.get_setting("make_playlists") == "true":
                        data['action'] = 'play_episode'
                    data['episode_id'] = a['id'][8:]
                data['Title'] = decode_htmlentities(a['title'])
                self.plugin.add_list_item(data)
            self.plugin.end_list()

    def clipid_to_stream_url(self, clipid):
        rurl = "http://cls.ctvdigital.net/cliplookup.aspx?id=%s" % (clipid)
        parse = URLParser(swf_url=self.swf_url)
        url = parse(
            self.plugin.fetch(rurl).read().strip()[17:].split("'", 1)[0])
        return url

    def action_play_clip(self):
        url = self.clipid_to_stream_url(self.args['clip_id'])
        logging.debug("Playing Stream: %s" % (url,))
        self.plugin.set_stream_url(url)


class CTVNews(CTVBaseChannel):
    base_url = 'http://www.ctvnews.ca/video'
    short_name = 'ctvnews'
    long_name = 'CTV News'
    default_action = 'browse'

    def action_browse(self):
        if not self.args['remote_url']:
            self.args['remote_url'] = self.base_url
        soup = BeautifulSoup(self.plugin.fetch(self.args[
            'remote_url'], max_age=self.cache_timeout))

        for category in soup.findAll('dt', {'class': 'videoPlaylistCategories'}):
            data = {}
            data.update(self.args)
            data.update({
                'action': 'browse_category',
                'Title': category.a.contents[0],
                'entry_id': None,
                'category_id': category['id'],
                'page_num': 1
            })
            self.plugin.add_list_item(data)
        self.plugin.end_list()

    def action_browse_category(self):
        soup = BeautifulSoup(self.plugin.fetch("%s/%s?ot=example.AjaxPageLayout.ot&maxItemsPerPage=12&pageNum=%s" % (self.args['remote_url'], self.args["category_id"], self.args['page_num']),
                        max_age=self.cache_timeout))
        #print soup
        for clip in soup.findAll('article', {'class': 'videoPackageThumb'}):
            #print clip
            thumb = None
            if 'src' in clip.img:
                thumb = clip.img['src']
            tagline = clip.h3.string
            #title = clip.find('p',{'class':'videoPlaylistDescription'}).string

            script = clip.findNextSibling()
            scripts = []
            while script:
                if script.name != 'script':
                    break
                scripts.append(script)
                script = script.findNextSibling()

            if len(scripts) > 2:
                script = scripts[0]
                txt = script.string.strip()
                if txt.find('playlistMap[') >= 0:
                    match = re.search(
                        "playlistMap\['([0-9.]*)'\] = new Array()", txt)
                    playlist_id = match.group(1)
                    data = {}
                    data.update(self.args)
                    data.update({
                        'action': 'browse_playlist',
                        'Title': tagline,
                        'entry_id': None,
                        'Thumb': thumb,
                        'playlist_id': playlist_id,
                    })
                    self.plugin.add_list_item(data)
            else:
                for script in scripts:
                    txt = script.string.strip()
                    if txt.find('clip.id') >= 0:
                        match = re.search('.*clip[.]id = ([0-9]*).*clip[.]title = escape\("(.*)"\).*clip[.]description = escape\("(.*)"\).*', txt, re.DOTALL)
                        clipId = match.group(1)
                        title = match.group(2).strip()
                        plot = match.group(3).strip()

                        #print thumb
                        data = {}
                        data.update(self.args)
                        data.update({
                            'Title': title,
                            'action': 'play_clip',
                            'remote_url': clipId,
                            'clip_id': clipId,
                            'Thumb': thumb,
                            'tagline': tagline,
                            'plot': plot,
                            'genre': 'News'
                        })
                        self.plugin.add_list_item(data, is_folder=False)

        nextPager = soup.find("span", {"class": "videoPaginationNext"})
        if nextPager and nextPager.find('a'):
            data = {}
            data.update(self.args)
            data.update({
                'Title': ">>> Next Page",
                'page_num': int(self.args["page_num"]) + 1
            })
        self.plugin.add_list_item(data)

        self.plugin.end_list()

    def action_browse_playlist(self):
        soup = BeautifulSoup(self.plugin.fetch("%s/%s?ot=example.AjaxPageLayout.ot&maxItemsPerPage=12&pageNum=%s" % (self.args['remote_url'], self.args["playlist_id"], self.args['page_num']),
                        max_age=self.cache_timeout))
        for clip in soup.findAll('article', {'class': 'videoClipThumb'}):
            #print clip
            thumb = clip.img['src']
            tagline = clip.h3.a.string
            clipId = clip['id']
            plot = clip.p.string.strip()
            data = {}
            data.update(self.args)
            data.update({
                'Title': tagline,
                'action': 'play_clip',
                'remote_url': clipId,
                'clip_id': clipId,
                'Thumb': thumb,
                'tagline': tagline,
                'plot': plot,
                'genre': 'News'
            })
            self.plugin.add_list_item(data, is_folder=False)
        self.plugin.end_list()


class CTVLocalNews(CTVNews):
    short_name = 'ctvlocal'
    long_name = 'CTV Local News'
    default_action = 'root'

    local_channels = [
        ('Atlantic', 'http://atlantic.ctvnews.ca/video'),
        ('British Columbia', 'http://bc.ctvnews.ca/video'),
        ('Calgary', 'http://calgary.ctvnews.ca/video'),
        ('Edmonton', 'http://edmonton.ctvnews.ca/video'),
        ('Kitchener', 'http://kitchener.ctvnews.ca/video'),
        ('Montreal', 'http://montreal.ctvnews.ca/video'),
        ('Northern Ontario', 'http://northernontario.ctvnews.ca/video'),
        ('Ottawa', 'http://ottawa.ctvnews.ca/video'),
        ('Regina', 'http://regina.ctvnews.ca/video'),
        ('Saskatoon', 'http://saskatoon.ctvnews.ca/video'),
        ('Toronto', 'http://toronto.ctvnews.ca/video'),
        ('Winnipeg', 'http://winnipeg.ctvnews.ca/video'),
    ]

    def action_root(self):
        for channel, domain in self.local_channels:
            self.plugin.add_list_item({
                'Title': channel,
                'action': 'browse',
                'channel': self.short_name,
                'entry_id': None,
                'local_channel': channel,
                'remote_url': domain,

                'Thumb': self.args['Thumb'],
            })
        self.plugin.end_list()


class Bravo(CTVBaseChannel):
    short_name = 'bravo'
    long_name = 'Bravo!'

    def action_root(self):
        url = 'http://www.bravo.ca/shows'
        soup = BeautifulSoup(
            self.plugin.fetch(url, max_age=self.cache_timeout))
        shows = soup.find('div', 'shows_list').findAll('a', 'link')
        for show in shows:
            show_img = 'http://www.bravo.ca' + show.findPrevious('img')['src']
            show_url = 'http://www.bravo.ca' + show['href']
            # must check url to see if there are any videos
            soup2 = BeautifulSoup(
                self.plugin.fetch(show_url, max_age=self.cache_timeout))
            if not soup2.find('a', 'video_carousel_thumbnail_container'):
                continue
            # there are videos, so add to the list
            self.plugin.add_list_item({
                'Title': show.contents[0],
                'Thumb': show_img,
                'action': 'browse',
                'channel': self.short_name,
                'show_url': show_url
            })
        self.plugin.end_list()

    def action_browse(self):
        soup = BeautifulSoup(self.plugin.fetch(self.args[
            'show_url'], max_age=self.cache_timeout))
        episodes = soup.findAll('a', 'video_carousel_thumbnail_container')
        for ep in episodes:
            ep_img = ep.find('img')['src']
            ep_title = ep.find('span').contents[0]
            ep_id = ep['href'].split('=')[1]
            self.plugin.add_list_item({
                'Title': ep_title,
                'Thumb': ep_img,
                'action': 'browse_episode',
                'channel': self.short_name,
                'episode_id': ep_id
            })
        self.plugin.end_list()


class CTV(CTVBaseChannel):
    short_name = 'ctv'
    long_name = 'CTV'
    base_url = 'http://watch.ctv.ca/AJAX/'
    swf_url = 'http://watch.ctv.ca/Flash/player.swf?themeURL=http://watch.ctv.ca/themes/CTV/player/theme.aspx'


class TSN(CTVBaseChannel):
    short_name = 'tsn'
    long_name = 'The Sports Network'
    base_url = 'http://watch.tsn.ca/AJAX/'
    swf_url = 'http://watch.tsn.ca/Flash/player.swf?themeURL=http://watch.ctv.ca/themes/TSN/player/theme.aspx'


class Discovery(CTVBaseChannel):
    short_name = 'discovery'
    base_url = 'http://watch.discoverychannel.ca/AJAX/'
    long_name = 'Discovery'
    swf_url = 'http://watch.discoverychannel.ca/Flash/player.swf?themeURL=http://watch.discoverychannel.ca/themes/Discoverynew/player/theme.aspx'


class ComedyNetwork(CTVBaseChannel):
    status = STATUS_UGLY
    short_name = 'comedynetwork'
    base_url = 'http://watch.thecomedynetwork.ca/AJAX/'
    long_name = 'The Comedy Network'
    swf_url = 'http://watch.thecomedynetwork.ca/Flash/player.swf?themeURL=http://watch.thecomedynetwork.ca/themes/Comedy/player/theme.aspx'


class Space(CTVBaseChannel):
    short_name = 'space'
    long_name = "Space"
    base_url = "http://watch.spacecast.com/AJAX/"
    swf_url = "http://watch.spacecast.com/Flash/player.swf?themeURL=http://watch.spacecast.com/themes/Space/player/theme.aspx"


class BNN(CTVBaseChannel):
    base_url = 'http://watch.bnn.ca/AJAX/'
    long_name = 'Business News Network'
    short_name = 'bnn'
    swf_url = 'http://watch.bnn.ca/news/Flash/player.swf?themeURL=http://watch.bnn.ca/themes/BusinessNews/player/theme.aspx'


class Fashion(CTVBaseChannel):
    short_name = 'fashion'
    base_url = 'http://watch.fashiontelevision.com/AJAX/'
    long_name = 'Fashion Television'
    swf_url = 'http://watch.fashiontelevision.com/Flash/player.swf?themeURL=http://watch.fashiontelevision.com/themes/FashionTelevision/player/theme.aspx'
