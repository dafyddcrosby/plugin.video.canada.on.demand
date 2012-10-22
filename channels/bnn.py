from ctv import CTVBaseChannel

class BNN(CTVBaseChannel):
    base_url = 'http://watch.bnn.ca/AJAX/'
    long_name = 'Business News Network'
    short_name = 'bnn'
    swf_url = 'http://watch.bnn.ca/news/Flash/player.swf?themeURL=http://watch.bnn.ca/themes/BusinessNews/player/theme.aspx'
