from canwest import CanwestBaseChannel

class diyNet(CanwestBaseChannel):
    short_name = 'diynet'
    long_name = 'The DIY Network'
    PID = 'FgLJftQA35gBSx3kKPM46ZVvhP6JxTYt'
    #swf_url = 'http://www.diy.ca/Includes/cwp/swf/flvPlayer.swf'

    def get_categories_json(self, arg):
        url = CanwestBaseChannel.get_categories_json(self, arg) + '&query=CustomText|PlayerTag|z/DIY%20Network%20-%20Video%20Centre'  # urlencode
        logging.debug('get_categories_json: %s' % url)
        return url
