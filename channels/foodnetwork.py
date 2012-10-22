from canwest import CanwestBaseChannel

class FoodNetwork(CanwestBaseChannel):
    short_name = 'foodnet'
    long_name = 'The Food Network'
    PID = '6yC6lGVHaVA8oWSm1F9PaIYc9tOTzDqY'
    # swf_url =
    # 'http://webdata.globaltv.com/global/canwestPlayer/swf/4.1/flvPlayer.swf'

    def get_categories_json(self, arg):
        url = CanwestBaseChannel.get_categories_json(self, arg) + '&query=CustomText|PlayerTag|z/FOODNET%20Player%20-%20Video%20Centre'  # urlencode
        logging.debug('get_categories_json: %s' % url)
        return url
