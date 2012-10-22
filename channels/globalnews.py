from canwest import CanwestBaseChannel

class GlobalNews(CanwestBaseChannel):
    short_name = 'globalnews'
    long_name = 'Global News'
    PID = 'M3FYkz1jcJIVtzmoB4e_ZQfqBdpZSFNM'
    local_channels = [
        ('Global News', 'z/Global%20News%20Player%20-%20Main'),
        ('Global National', 'z/Global%20Player%20-%20The%20National%20VC'),
        ('BC', 'z/Global%20BC%20Player%20-%20Video%20Center'),
        ('Calgary', 'z/Global%20CGY%20Player%20-%20Video%20Center'),
        ('Edmonton', 'z/Global%20EDM%20Player%20-%20Video%20Center'),
        ('Lethbridge', 'z/Global%20LTH%20Player%20-%20Video%20Center'),
        ('Maritimes', 'z/Global%20MAR%20Player%20-%20Video%20Center'),
        ('Montreal', 'z/Global%20QC%20Player%20-%20Video%20Center'),
        ('Regina', 'z/Global%20REG%20Player%20-%20Video%20Center'),
        ('Saskatoon', 'z/Global%20SAS%20Player%20-%20Video%20Center'),
        ('Toronto', 'z/Global%20ON%20Player%20-%20Video%20Center'),
        ('Winnipeg', 'z/Global%20WIN%20Player%20-%20Video%20Center'),
    ]

    def get_cache_key(self):
        return "%s-%s" % (self.short_name, self.args.get('local_channel', ''))

    def action_browse(self):
        self.PlayerTag = dict(self.local_channels)[self.args['local_channel']]

        if self.args['entry_id'] is None:
            return CanwestBaseChannel.action_root(self)
        return CanwestBaseChannel.action_browse(self)

    def action_root(self):
        for channel, ptag in self.local_channels:
            self.plugin.add_list_item({
                'Title': channel,
                'action': 'browse',
                'channel': self.short_name,
                'entry_id': None,
                'local_channel': channel
            })
        self.plugin.end_list()

    def get_categories_json(self, arg):
        return CanwestBaseChannel.get_categories_json(self, arg) + '&query=CustomText|PlayerTag|' + self.PlayerTag
