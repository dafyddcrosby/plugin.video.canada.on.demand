from canwest import *

class Showcase(CanwestBaseChannel):
    short_name = 'showcase'
    long_name = 'Showcase'
    PID = 'sx9rVurvXUY4nOXBoB2_AdD1BionOoPy'
    swf_url = 'http://www.showcase.ca/video/swf/flvPlayer.swf  swfvfy=true'
    root_depth = 2

    def get_categories_json(self, arg):
        url = CanwestBaseChannel.get_categories_json(self, arg) + '&query=CustomText|PlayerTag|z/Showcase%20Video%20Centre'  # urlencode
        logging.debug('get_categories_json: %s' % url)
        return url
