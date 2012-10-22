from ctv import CTVBaseChannel

class Space(CTVBaseChannel):
    short_name = 'space'
    long_name = "Space"
    base_url = "http://watch.spacecast.com/AJAX/"
    swf_url = "http://watch.spacecast.com/Flash/player.swf?themeURL=http://watch.spacecast.com/themes/Space/player/theme.aspx"
