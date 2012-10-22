import time
import cgi
import datetime
import simplejson
from channel import BaseChannel, ChannelException, ChannelMetaClass, STATUS_BAD, STATUS_GOOD, STATUS_UGLY
from utils import *
import httplib
import xbmcplugin
import xbmc

try:
    from pyamf import remoting
    has_pyamf = True
except ImportError:
    has_pyamf = False


class BrightcoveBaseChannel(BaseChannel):

    """
    None of this works. All videos stop playing after 1 minute.

    """
    is_abstract = True

    def get_swf_url(self):
        conn = httplib.HTTPConnection('c.brightcove.com')
        qsdata = dict(width=640, height=480, flashID=self.flash_experience_id,
                      bgcolor="#000000", playerID=self.player_id, publisherID=self.publisher_id,
                      isSlim='true', wmode='opaque', optimizedContentLoad='true', autoStart='', debuggerID='')
        qsdata['@videoPlayer'] = self.video_id
        logging.debug("SWFURL: %s" % (urllib.urlencode(qsdata),))
        conn.request("GET", "/services/viewer/federated_f9?&" +
                     urllib.urlencode(qsdata))
        resp = conn.getresponse()
        location = resp.getheader('location')
        base = location.split("?", 1)[0]
        location = base.replace(
            "BrightcoveBootloader.swf", "connection/ExternalConnection_2.swf")
        self.swf_url = location

    def get_clip_info(self, player_id, video_id):
        conn = httplib.HTTPConnection("c.brightcove.com")
        envelope = self.build_amf_request(player_id, video_id)
        conn.request("POST", "/services/amfgateway", str(remoting.
                                                         encode(envelope).read()), {'content-type': 'application/x-amf'})
        response = conn.getresponse().read()
        response = remoting.decode(
            response).bodies[0][1].body[0]['data']['videoDTO']
        logging.debug(response)
        return response

    def choose_rendition(self, renditions):
        maxrate = int(self.plugin.get_setting("max_bitrate")) * 1024
        rends = [r for r in renditions if r['encodingRate'] < maxrate]
        if not rends:
            rends = renditions
        rends.sort(key=lambda r: r['encodingRate'])
        return rends[-1]

    def build_amf_request_body(self, player_id, video_id):
        return [
            player_id,
            {
                'optimizeFeaturedContent': 1,
                'featuredLineupFetchInfo': {
                    'fetchLevelEnum': 4,
                    'contentType': u'VideoLineup',
                    'childLimit': 100
                },
                'lineupRefId': None,
                'videoId': video_id,
                'videoRefId': None,
                'lineupId': None,
                'fetchInfos': [
                    {'fetchLevelEnum': 1,
                        'contentType': u'VideoLineup', 'childLimit': 100},
                    {'grandchildLimit': 100, 'fetchLevelEnum': 3,
                        'contentType': u'VideoLineupList', 'childLimit': 100}
                ]
            }
        ]

    def build_amf_request(self, player_id, video_id):
        env = remoting.Envelope(amfVersion=0)
        env.bodies.append(
            (
                "/2",
                remoting.Request(
                    target="com.brightcove.templating.TemplatingFacade.getContentForTemplateInstance",
                    body=self.build_amf_request_body(player_id, video_id),
                    envelope=env
                )
            )
        )
        return env

    def find_ids(self, url):
        soup = BeautifulSoup(
            self.plugin.fetch(url, max_age=self.cache_timeout))
        self.flash_experience_id = soup.find("object")['id']
        try:
            player_id = int(soup.find("object").find("param", {
                "name": "playerID"})['value'])
        except:
            player_id = None

        try:
            video_id = int(soup.find(
                'object').find("param", {"name": "@videoPlayer"})['value'])
        except:
            video_id = None

        return player_id, video_id
