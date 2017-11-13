from datetime import datetime, timedelta
from kivy import Logger
from kivy.utils import get_color_from_hex

from jnius import autoclass, JavaException

import settings
from managers.calendar.abstract import AbstractCalendarManager

python_activity = autoclass('org.kivy.android.PythonActivity').mActivity
Context = autoclass('android.content.Context')
Uri = autoclass('android.net.Uri')


class AndroidCalendarManager(AbstractCalendarManager):
    MAX_EVENTS = 50

    def get_events(self):

        active_calendar_ids = self.get_active_calendars().keys()

        ContentUris = autoclass('android.content.ContentUris')
        content_builder = Uri.parse("content://com.android.calendar/instances/when").buildUpon()
        dtstart = datetime.now() - timedelta(days=1)
        dtend = datetime.now() + timedelta(days=14)
        ContentUris.appendId(content_builder, int(dtstart.strftime("%s")) * 1000)
        ContentUris.appendId(content_builder, int(dtend.strftime("%s")) * 1000)
        vec = ["calendar_id", "title", "begin", "end", "allDay"]
        selection_clause = "(calendar_id IN (%s))" % (",".join(active_calendar_ids))
        order_clause = "begin ASC"
        contentResolver = python_activity.getContentResolver()
        try:
            cursor = contentResolver.query(content_builder.build(), vec, selection_clause, None, order_clause)
        except JavaException:
            return []
        if not cursor:
            return []
        cursor.moveToFirst()
        result = []
        for i in range(cursor.getCount()):
            begin = datetime.fromtimestamp(int(cursor.getString(2)) / 1000)
            end = datetime.fromtimestamp(int(cursor.getString(3)) / 1000)
            result.append({
                "calendar_id": cursor.getString(0),
                "title": cursor.getString(1),
                "begin": begin,
                "end": end,
                "all_day": cursor.getString(4) == '1',
            })
            cursor.moveToNext()
        Logger.info("Android Calendar: %s entries in calendar found" % len(result))
        return result[-self.MAX_EVENTS:]

    def get_calendars(self):
        if self.calendars:
            return self.calendars
        content = Uri.parse("content://com.android.calendar/calendars")
        contentResolver = python_activity.getContentResolver()
        try:
            cursor = contentResolver.query(content, [
                'name',
                'calendar_displayName',
                'calendar_color',
                'visible',
                '_id',
            ], None, None, None)
        except JavaException:
            return {}
        if not cursor:
            return {}
        cursor.moveToFirst()
        result = {}
        for i in range(cursor.getCount()):
            int_color = cursor.getString(2)
            if int_color:
                hex_color_android = int(cursor.getString(2)) + (1 << 32)
                kivy_color = get_color_from_hex(
                    hex(hex_color_android & 0x00ffffff).replace("L", "ff").replace("0x", "#"))
            else:
                kivy_color = settings.TEXT_COLOR
            result[cursor.getString(4)] = {
                "display_name": cursor.getString(1),
                "color": kivy_color,
                "is_visible": cursor.getString(3) != '0',
                "name": cursor.getString(0)
            }
            cursor.moveToNext()
        self.calendars = result
        return result

    def get_active_calendars(self):
        if not self.active_calendars:
            return self.get_calendars()
        else:
            return {
                id_: d for id_, d in self.get_calendars().items() if
                int(id_) in self.active_calendars and d['is_visible']
            }

    def __init__(self):
        self.calendars = {}
        self.active_calendars = []
