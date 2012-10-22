from theplatform import *


class CanwestBaseChannel(ThePlatformBaseChannel):
    is_abstract = True
    base_url = 'http://feeds.theplatform.com/ps/JSON/PortalService/2.2/'
    PID = None
    root_depth = 1

    def get_categories_json(self, arg=None):
        return ThePlatformBaseChannel.get_categories_json(self)  # + '&query=ParentIDs|%s'%arg

    def get_releases_json(self, arg='0'):
        return ThePlatformBaseChannel.get_releases_json(self) + '&query=CategoryIDs|%s' % (self.args['entry_id'],)

    def children_with_releases(self, categorylist, cat):

        if cat['fullTitle'] == '':
            prefix = ''
        else:
            prefix = cat['fullTitle'] + "/"

        children = [c for c in categorylist
                    if c['depth'] == cat['depth'] + 1
                    and c['fullTitle'].startswith(prefix)
                    and (c['hasReleases'] or self.children_with_releases(categorylist, c))]
        return children

    def get_child_categories(self, categorylist, parent_id):

        show_empty = self.plugin.get_setting('show_empty_cat') == 'true'
        if parent_id is None:
            if self.root_depth > 0:
                cat = [c for c in categorylist if c[
                    'depth'] == self.root_depth - 1][0]
            else:
                cat = {'depth': -1, 'fullTitle': ''}
        else:
            logging.debug("ParentID: %s [%s]" % (parent_id, type(parent_id)))
            cat = [c for c in categorylist if c['ID'] == int(parent_id)][0]

        if cat['fullTitle'] == '':
            prefix = ''
        else:
            prefix = cat['fullTitle'] + "/"

        if show_empty:
            categories = [c for c in categorylist if c['depth'] == cat['depth'] + 1
                          and c['fullTitle'].startswith(prefix)]

        else:
            categories = self.children_with_releases(categorylist, cat)

        return categories

    #override ThePlatFormbase so ?querystring isn't included in playpath
    # this could be temp-only, actually. paypath doesn't seem to care about
    # extra parameters
    def action_play(self):
        parse = URLParser(swf_url=self.swf_url, playpath_qs=False)
        self.plugin.set_stream_url(parse(self.args['clip_url']))
