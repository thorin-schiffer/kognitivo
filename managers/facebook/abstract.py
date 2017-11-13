from kivy import Logger


class AbstractFacebookManager(object):
    def initialize(self):
        Logger.info("Facebook: initialize...")

    def activate(self):
        Logger.info("Facebook: activation...")

    def deactivate(self):
        Logger.info("Facebook: deactivation")
