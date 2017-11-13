from datetime import datetime, timedelta
from kivy.utils import get_color_from_hex

from managers.calendar.abstract import AbstractCalendarManager


class DummyCalendarManager(AbstractCalendarManager):
    def get_events(self):
        return [{
            'title': 'Ev/JK/BDog',
            'calendar_id': '1',
            'begin': datetime.now() - timedelta(days=7 - i),
            'all_day': False,
            'end': datetime(2015, 8, 25, 8, 30)
        } for i in range(14)] + [{
            'title': 'Ev/JK/BDog',
            'calendar_id': '1',
            'begin': datetime(2015, 8, 25, 7, 30),
            'all_day': True,
            'end': datetime(2015, 8, 25, 8, 30)
        }]

    def get_calendars(self):
        return {
            '1': {'color': get_color_from_hex('#29527aff'), 'is_visible': True, 'display_name': 'sergey@two-bulls.com',
                  'name': 'sergey@two-bulls.com'},
            '3': {'color': get_color_from_hex('#2952a3ff'), 'is_visible': True,
                  'display_name': 'sergei.cheparev@gmail.com',
                  'name': 'sergei.cheparev@gmail.com'},
            '2': {'color': get_color_from_hex('#8d6f47ff'), 'is_visible': False, 'display_name': 'katja@two-bulls.com',
                  'name': 'katja@two-bulls.com'},
        }
