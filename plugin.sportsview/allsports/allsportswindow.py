# IMPORTS
# region
import xbmcgui
import xbmc
import xbmcaddon
from allsports.allsportsbuttons import AllSportsButtons
# endregion

# AllSportsWindow class
# region
class AllSportsWindow(xbmcgui.WindowXML):
    def __init__(self, *args, **kwargs):

        # Initialize the window and other stuff
        super(AllSportsWindow, self).__init__(*args, **kwargs)

        # Pass the required arguments to AllSportsButtons
        cwd = xbmcaddon.Addon().getAddonInfo('path')
        self.allsports_buttons = AllSportsButtons('allsports.xml', cwd, 'default', '1080i')
        self.allsports_buttons.set_parent_window(self)  # Set the parent_window attribute
# endregion

# onInit method
# region
    def onInit(self):
        print("AllSportsWindow - onInit")

        # Call the method to check if the file exists
        self.allsports_buttons.file_exists()

        # Call the visible_buttons_info method after moving focus
        self.allsports_buttons.visible_buttons()
# endregion

# onAction method
# region
    def onAction(self, action):
        if action == xbmcgui.ACTION_MOVE_LEFT:
            # Call the method in MySportsButtons to move the focus left
            self.allsports_buttons.moveFocus(-1, 0)
        elif action == xbmcgui.ACTION_MOVE_RIGHT:
            # Call the method in MySportsButtons to move the focus right
            self.allsports_buttons.moveFocus(1, 0)
        elif action == xbmcgui.ACTION_MOVE_UP:
            # Call the method in MySportsButtons to move the focus up
            self.allsports_buttons.moveFocus(0, -1)
        elif action == xbmcgui.ACTION_MOVE_DOWN:
            # Call the method in MySportsButtons to move the focus down
            self.allsports_buttons.moveFocus(0, 1)
        elif action == xbmcgui.ACTION_NAV_BACK:
            self.close()
        elif action == xbmcgui.ACTION_SELECT_ITEM:
            focused_button_id = self.getFocusId()
            focused_sport_name = self.allsports_buttons.get_focused_sport_name()
            print("Currently focused sportclickckckckckckc:", focused_sport_name)
            # Launch My Leagues window
            self.allsports_buttons.onClick(focused_button_id, focused_sport_name)

# endregion
