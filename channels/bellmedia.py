from theplatform import *
from channel import STATUS_GOOD
import xbmc

class BellMediaBaseChannel(BaseChannel):
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

