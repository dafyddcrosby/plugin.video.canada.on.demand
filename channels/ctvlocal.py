from ctv import BellMediaBaseChannel

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
