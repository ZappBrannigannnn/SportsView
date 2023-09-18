import xbmcaddon
from window_manager import WindowManager

class MyAddon(xbmcaddon.Addon):
    def __init__(self):
        xbmcaddon.Addon.__init__(self)
        self.window_manager = WindowManager()

    def defaultrun(self):
        print("Running MyAddon")
        # Run the landing page window
        self.window_manager.show_landing_page()

#initialize instance of MyAddon as addon 
addon = MyAddon()

addon.defaultrun()

sdfsdfdsfsdfds