from ctv import CTVBaseChannel

class TSN(CTVBaseChannel):
    short_name = 'tsn'
    long_name = 'The Sports Network'
    base_url = 'http://watch.tsn.ca/AJAX/'
    swf_url = 'http://watch.tsn.ca/Flash/player.swf?themeURL=http://watch.ctv.ca/themes/TSN/player/theme.aspx'
