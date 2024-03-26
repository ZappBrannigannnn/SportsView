# imports
import xbmcaddon
import base64

# API KEY
# region
# Your encryption key (keep it secret)
encryption_key = b'ZappBSportsVAPI6'

# Encrypted API key from settings.xml
addon = xbmcaddon.Addon()
encrypted_api_key = addon.getSetting('setting2')

apikey = base64.b64decode(encrypted_api_key).decode('utf-8')

#API_URL = 
# endregion

class AllLeaguesButtons:
    def __init__(self, *args, **kwargs):
        self.sportname = str(kwargs.get('sportname'))
        print("allleaguesbuttons.py sportname", self.sportname)

    def set_parent_window(self, parent_window):
        self.parent_window = parent_window


