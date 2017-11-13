from kivy import Logger


class AbstractTracker(object):
    def _get_tracker(self):
        raise NotImplementedError()

    def send_screen(self, screen):
        Logger.info('Tracking: Sending screen for %s' % screen.name)

    def clear_screen(self):
        Logger.info('Tracking: Cleared screen')

    def send_event(self, category, action, label=None, value=None):
        Logger.info(
            'Tracking: event sent - %s-%s-%s-%s' % (
                category, action, label, int(value) if value is not None else value)
        )

    def send_to_server(self):
        Logger.info('Tracking: sending data from local storage')
