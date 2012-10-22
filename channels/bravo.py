from ctv import CTVBaseChannel

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
