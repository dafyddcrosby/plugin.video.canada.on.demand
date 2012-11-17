from bellmedia import *

class ComedyNetwork(BellMediaBaseChannel):
    status = STATUS_UGLY
    short_name = 'comedynetwork'
    long_name = 'The Comedy Network'

    base_url = 'http://watch.thecomedynetwork.ca/AJAX/'
    swf_url = 'http://watch.thecomedynetwork.ca/Flash/player.swf?themeURL=http://watch.thecomedynetwork.ca/themes/Comedy/player/theme.aspx'
