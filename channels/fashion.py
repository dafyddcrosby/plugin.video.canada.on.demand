from ctv import CTVBaseChannel

class Fashion(CTVBaseChannel):
    short_name = 'fashion'
    long_name = 'Fashion Television'

    base_url = 'http://watch.fashiontelevision.com/AJAX/'
    swf_url = 'http://watch.fashiontelevision.com/Flash/player.swf?themeURL=http://watch.fashiontelevision.com/themes/FashionTelevision/player/theme.aspx'
