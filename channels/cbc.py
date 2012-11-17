from theplatform import *

class CBCChannel(ThePlatformBaseChannel):
    PID = "_DyE_l_gC9yXF9BvDQ4XNfcCVLS4PQij"
    base_url = 'http://cbc.feeds.theplatform.com/ps/JSON/PortalService/2.2/'
    custom_fields = ['Account', 'AudioVideo', 'BylineCredit', 'CBCPersonalities', 'Characters', 'ClipType',
                     'EpisodeNumber', 'Event', 'Genre', 'LiveOnDemand', 'Organizations', 'People', 'Producers', 'Region',
                     'Segment', 'Show', 'SeasonNumber', 'Sport', 'SubEvent']
    status = STATUS_UGLY
    short_name = 'cbc'
    long_name = 'CBC'
    category_cache_timeout = 0  # can't cache for CBC, need to drill-down each time

    #this holds an initial value for CBC only to get the top-level categories;
    #it is overwritten in action_root
    in_root = False
    category_json = '&query=ParentIDs|'

    def get_categories_json(self, arg):
        logging.debug('get_categories_json arg=%s, categ_json=%s' %
                      (arg, self.category_json))
        url = ThePlatformBaseChannel.get_categories_json(self) + \
            '&customField=GroupLevel&customField=GroupOrder&customField=IsDynamicPlaylist'

        # Add other custom fields
        for cf in self.custom_fields:
            url += '&customField=' + cf

        if arg or self.in_root:
            url += self.category_json
        if arg:
            url += arg
        return url

    #arg is CBC's customfield array from getReleases query
    def get_releases_json(self, arg):
        url = ThePlatformBaseChannel.get_releases_json(self)
        logging.warn("RELURL: %s" % (url,))

        # this code is copied from CBCVideoFunctions.js on CBC's web site
        if arg['IsDynamicPlaylist'] and arg['IsDynamicPlaylist'].lower() != 'false':
            for cf in self.custom_fields:
                if cf in arg and arg[cf] != '(not specified)' and (cf != 'Genre' or arg[cf] != 'Other'):
                    url += '&query=ContentCustomText|%s|%s' % (
                        cf, urlquoteval(arg[cf]))
        else:
            url += '&query=CategoryIds|%s' % urlquoteval(arg['entry_id'])

        logging.debug('get_releases_json: %s' % url)
        return url

    def get_child_categories(self, categorylist, parent_id):
        if parent_id is None:
            categories = [c for c in categorylist
                          #if c['depth'] == 1 or c['depth'] == 0
                          if c['depth'] == 0
                          and (
                              self.plugin.get_setting('show_empty_cat') == True
                              or (c['hasReleases'] or c['hasChildren'])
                          )]
        else:
            #do nothing with parent_id in CBC's case
            categories = categorylist
        return categories

    def action_root(self):
        logging.debug('CBCChannel::action_root')

        #all CBC sections = ['Shows,Sports,News,Kids,Radio']
        self.category_json = ''
        self.in_root = True  # just for annoying old CBC
        self.category_json = '&query=FullTitles|Shows,Sports,News,Radio'
        categories = self.get_categories(None)

        for cat in categories:
            cat.update({'Title': 'CBC %s' % cat['Title']})
            self.plugin.add_list_item(cat)
        self.plugin.end_list()

        #restore ParentIDs query for sub-categories
        self.category_json = '&query=ParentIDs|'
        self.in_root = False
        logging.debug('setting categ_json=%s' % self.category_json)

