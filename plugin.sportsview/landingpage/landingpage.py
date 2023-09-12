import xbmcgui
import xbmc

class LandingPageWindow(xbmcgui.WindowXML):
    def __init__(self, window_manager, *args, **kwargs):
        xbmcgui.WindowXML.__init__(self, *args, **kwargs)
        self.window_manager = window_manager

    def onInit(self):
        current_window = xbmcgui.getCurrentWindowId()  
        print("CURRENT WINDOW LANDING PAGE", current_window) 
        xbmc.log("LandingPageWindow - onInit")
        allsports_focus = self.getControl(1003)  # Get the label control by its ID
        self.setFocus(allsports_focus)  # Set the focus to the label control

    def onClick(self, controlId):
        from window_manager import WindowManager

        # Create an instance of the WindowManager class
        self.window_manager = WindowManager()

        if controlId == 1001:  # ID of the AllSportsButton control
            # Call the show_all_sports_page method of the WindowManager instance
            self.window_manager.show_all_sports_page()

        elif controlId == 1003: # ID of the Mysports buttons control
            # Call the show_my_sports_page method of the WindowManager instance
            self.window_manager.show_my_sports_page()
