from canwest import CanwestBaseChannel

class GlobalTV(CanwestBaseChannel):
    short_name = 'global'
    long_name = 'Global TV'
    PID = 'W_qa_mi18Zxv8T8yFwmc8FIOolo_tp_g'
    swf_url = 'http://www.globaltv.com/widgets/ThePlatformContentBrowser/swf/flvPlayer.swf swfvfy=true'
    #swf_url = 'http://www.globaltv.com/video/swf/flvPlayer.swf'

    def get_categories_json(self, arg=None):
        url = CanwestBaseChannel.get_categories_json(self, arg) + \
            '&query=CustomText|PlayerTag|z/Global%20Video%20Centre'  # urlencode
        logging.debug('get_categories_json: %s' % url)
        return url

    def get_releases_json(self, arg='0'):
        url = '%s' % CanwestBaseChannel.get_releases_json(self, arg)
        logging.debug('get_releases_json: %s' % url)
        return url
