from ctv import CTVBaseChannel

class Discovery(CTVBaseChannel):
    short_name = 'discovery'
    long_name = 'Discovery'

    base_url = 'http://watch.discoverychannel.ca/AJAX/'
    swf_url = 'http://watch.discoverychannel.ca/Flash/player.swf?themeURL=http://watch.discoverychannel.ca/themes/Discoverynew/player/theme.aspx'
