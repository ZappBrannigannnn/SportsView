# IMPORTS
# region
import xbmcgui
import xbmc
import xbmcaddon
from allleagues.allleaguesbuttons import AllLeaguesButtons
# endregion

# AllLeaguesWindow class
# region
class AllLeaguesWindow(xbmcgui.WindowXML):
    def __init__(self, *args, **kwargs):
        self.sportname = kwargs.get('sportname')

        # Initialize the window and other stuff
        super(AllLeaguesWindow, self).__init__(*args, **kwargs)

        # Pass the required arguments to AllLeaguesButtons
        cwd = xbmcaddon.Addon().getAddonInfo('path')
        self.allleagues_buttons = AllLeaguesButtons('allleagues.xml', cwd, 'default', '1080i', sportname=self.sportname)
        self.allleagues_buttons.set_parent_window(self)  # Set the parent_window attribute
# endregion

# onInit method
# region
    def onInit(self):
        print("AllLeaguesWindow - onInit")

        # Call the method to check if the file exists
     #   self.allleagues_buttons.file_exists()

        # Call the visible_buttons_info method after moving focus
      #  self.allleagues_buttons.visible_buttons()
# endregion

# onAction method
# region
    def onAction(self, action):
        if action == xbmcgui.ACTION_MOVE_LEFT:
            # Call the method in AllLeaguesButtons to move the focus left
            self.allleagues_buttons.moveFocus(-1, 0)
        elif action == xbmcgui.ACTION_MOVE_RIGHT:
            # Call the method in AllLeaguesButtons to move the focus right
            self.allleagues_buttons.moveFocus(1, 0)
        elif action == xbmcgui.ACTION_MOVE_UP:
            # Call the method in AllLeaguesButtons to move the focus up
            self.allleagues_buttons.moveFocus(0, -1)
        elif action == xbmcgui.ACTION_MOVE_DOWN:
            # Call the method in AllLeaguesButtons to move the focus down
            self.allleagues_buttons.moveFocus(0, 1)
        elif action == xbmcgui.ACTION_NAV_BACK:
            self.close()
# endregion
