from canwest import CanwestBaseChannel

class HistoryTV(CanwestBaseChannel):
    short_name = 'history'
    long_name = 'History TV'
    PID = 'IX_AH1EK64oFyEbbwbGHX2Y_2A_ca8pk'
    swf_url = 'http://www.history.ca/video/cwp/swf/flvPlayer.swf'

    def get_categories_json(self, arg):
        url = CanwestBaseChannel.get_categories_json(self, arg) + '&query=CustomText|PlayerTag|z/History%20Player%20-%20Video%20Center'  # urlencode
        logging.debug('get_categories_json: %s' % url)
        return url
