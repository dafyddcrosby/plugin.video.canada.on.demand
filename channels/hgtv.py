from canwest import CanwestBaseChannel

class HGTV(CanwestBaseChannel):
    short_name = 'hgtv'
    long_name = 'HGTV.ca'
    PID = 'HmHUZlCuIXO_ymAAPiwCpTCNZ3iIF1EG'
    #swf_url = 'http://www.hgtv.ca/includes/cwp/swf/flvPlayer.swf'

    def get_categories_json(self, arg):
        url = CanwestBaseChannel.get_categories_json(self, arg) + '&query=CustomText|PlayerTag|z/HGTVNEWVC%20-%20New%20Video%20Center'  # urlencode
        logging.debug('get_categories_json: %s' % url)
        return url
