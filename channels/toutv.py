from theplatform import *

class TouTV(ThePlatformBaseChannel):
    long_name = 'Tou.TV'
    short_name = 'toutv'
    base_url = 'http://www.tou.tv/repertoire/'
    swf_url = 'http://static.tou.tv/lib/ThePlatform/4.2.9c/swf/flvPlayer.swf'
    default_action = 'root'

    categories = [
            ("animation", "Animation"),
            ("entrevues-varietes", "Entrevues et varietes"),
            ("films-documentaires", "Films et documentaires"),
            ("magazines-affaires-publiques",
                "Magazines et affaires publiques"),
            ("series-teleromans", "Series et teleromans"),
            ("spectacles-evenements", "Spectacles et evenements"),
            ("webteles", u"Webteles"),
    ]

    def action_play_episode(self):
        url = self.args['remote_url']
        soup = BeautifulSoup(
            self.plugin.fetch(url, max_age=self.cache_timeout))
        scripts = soup.findAll('script')

        epinfo_tag = [s for s in scripts if s.contents and s.contents[
            0].strip().startswith("// Get IP address and episode ID")][0]
        self.args['remote_PID'] = re.search(r"episodeId = '([^']+)'",
                                            epinfo_tag.contents[0].strip()).groups()[0]
        return ThePlatformBaseChannel.action_play_episode(self)

    def action_browse_series(self):
        url = self.args['remote_url']
        soup = BeautifulSoup(
            self.plugin.fetch(url, max_age=self.cache_timeout))
        for row in soup.findAll('div', {'class': 'blocepisodeemission'}):

            data = {}
            data.update(self.args)
            images = row.findAll('img')
            if len(images) == 2:
                image = images[1]
            else:
                image = images[0]

            title = decode_htmlentities(
                row.find('a', {'class': 'episode'}).b.contents[0],)[:-1]

            try:
                seasonp = [p for p in row.findAll('p')
                           if 'class' in dict(p.attrs)][0]
                season = seasonp.contents[0].strip()
                title = season + ": " + title
            except:
                pass

            try:
                plotp = [p for p in row.findAll('p')
                         if 'class' not in dict(p.attrs)][0]
                plot = plotp.contents[0].strip()
            except:
                plot = '(failed to fetch plot)'

            data.update({
                'action': 'play_episode',
                'remote_url': 'http://tou.tv' + row.find('a')['href'],
                'Title': title,
                'Thumb': image['src'],
                'Plot': plot
            })
            self.plugin.add_list_item(data, is_folder=False)
        self.plugin.end_list('episodes')

    def action_browse_category(self):
        cat = dict(self.categories)[self.args['category']]
        logging.debug("CAT: %s" % (cat,))
        url = self.base_url + self.args['category'] + "/"
        soup = BeautifulSoup(
            self.plugin.fetch(url, max_age=self.cache_timeout))
        logging.debug(url)
        for a in soup.findAll('a', {'class': re.compile(r'bloc_contenu.*')}):
            data = {}
            data.update(self.args)
            data.update({
                'action': 'browse_series',
                'remote_url': 'http://tou.tv' + a['href'],
                'Title': a.find('h1').contents[0],
            })

            self.plugin.add_list_item(data)
        self.plugin.end_list()

    def action_root(self):

        for cat in self.categories:
            data = {}
            data.update(self.args)
            data.update({
                'channel': 'toutv',
                'action': 'browse_category',
                'category': cat[0],
                'Title': cat[1],
            })

            self.plugin.add_list_item(data)
        self.plugin.end_list()
