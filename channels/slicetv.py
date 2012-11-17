from canwest import *

class SliceTV(CanwestBaseChannel):
    short_name = 'slice'
    long_name = 'Slice TV'
    PID = 'EJZUqE_dB8XeUUgiJBDE37WER48uEQCY'
    #swf_url = 'http://www.slice.ca/includes/cwp/swf/flvPlayer.swf'

    def get_categories_json(self, arg):
        url = CanwestBaseChannel.get_categories_json(self, arg) + '&query=CustomText|PlayerTag|z/Slice%20Player%20-%20New%20Video%20Center'  # urlencode
        logging.debug('get_categories_json: %s' % url)
        return url
