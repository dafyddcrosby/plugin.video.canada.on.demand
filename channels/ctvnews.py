from ctv import BellMediaBaseChannel

class CTVNews(BellMediaBaseChannel):
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
