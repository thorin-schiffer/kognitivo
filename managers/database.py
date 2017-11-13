from collections import defaultdict
import os
from datetime import datetime, timedelta
from kivy import Logger


class DatabaseManager(object):
    def __init__(self):
        import settings
        self._connection = None
        self.path = None
        self.from_date = datetime.now() - timedelta(days=settings.ACTIVITY_SHOW_STATS_PERIOD)

    def get_database_path(self):
        import settings
        return settings.DATABASE_PATH

    def connect(self):
        self.path = self.get_database_path()
        import sqlite3
        self._connection = sqlite3.connect(self.path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
                                           timeout=1)
        self._connection.row_factory = sqlite3.Row
        cursor = self._connection.cursor()

        create_tables_query = '''
        CREATE TABLE IF NOT EXISTS steps (
            id INTEGER NOT NULL,
            "key" VARCHAR NOT NULL,
            families VARCHAR NOT NULL,
            duration FLOAT,
            efficiency FLOAT NOT NULL,
            weekday INTEGER NOT NULL,
            hour INTEGER NOT NULL,
            created DATETIME NOT NULL,
            PRIMARY KEY (id)
        )
        '''
        cursor.execute(create_tables_query)
        self._connection.commit()

        if not os.path.exists(self.path):
            Logger.info("Database: create database on %s" % self.path)
        else:
            Logger.info("Database: found database at %s" % self.path)
        cursor.close()

    @property
    def connection(self):
        if not self._connection:
            self.connect()
        return self._connection

    def task_efficiencies(self, family=None):
        cursor = self.connection.cursor()

        query = '''
        SELECT steps."key", avg(steps.efficiency) AS "efficiency"
        FROM steps
        WHERE steps.created > ?
        '''

        if family is not None:
            query += '''
            AND (steps.families LIKE '%%' || ? || '%%')
            GROUP BY steps."key"
            '''
            cursor.execute(query, (self.from_date, family))
        else:
            query += '''
            GROUP BY steps."key"
            '''
            cursor.execute(query, (self.from_date,))

        result = dict(cursor.fetchall())
        cursor.close()
        return result

    def add_stat(self, key, duration, efficiency, created=None):
        cursor = self.connection.cursor()

        query = '''
        INSERT INTO steps ("key", families, duration, efficiency, weekday, hour, created) VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        import settings
        families = settings.TASKS[key]['families']
        created = created or datetime.now()
        weekday = created.weekday()
        hour = created.hour
        cursor.execute(query, (key, families, duration, efficiency, weekday, hour, created))
        self.connection.commit()
        cursor.close()

    def all_stat(self):
        cursor = self.connection.cursor()
        query = '''
        SELECT *
        FROM steps
        '''
        result = cursor.execute(query).fetchall()
        cursor.close()
        return result

    def day_task_efficiency(self, family=None):
        cursor = self.connection.cursor()
        query = '''
        SELECT weekday, key, avg(steps.efficiency) AS efficiency
        FROM steps
        WHERE steps.created > ?
        '''

        if family is not None:
            query += '''
            AND (steps.families LIKE '%%' || ? || '%%')
            GROUP BY weekday, steps."key"
            '''
            cursor.execute(query, (self.from_date, family))
        else:
            query += '''
            GROUP BY weekday, steps."key"
            '''
            cursor.execute(query, (self.from_date,))
        data = cursor.fetchall()
        result = defaultdict(dict)
        for weekday, key, value in data:
            result[weekday][key] = value
        return result

    def hour_task_efficiency(self, family=None):
        cursor = self.connection.cursor()
        query = '''
        SELECT hour, key, avg(steps.efficiency) AS efficiency
        FROM steps
        WHERE steps.created > ?
        '''

        if family is not None:
            query += '''
            AND (steps.families LIKE '%%' || ? || '%%')
            GROUP BY hour, steps."key"
            '''
            cursor.execute(query, (self.from_date, family))
        else:
            query += '''
            GROUP BY hour, steps."key"
            '''
            cursor.execute(query, (self.from_date,))
        data = cursor.fetchall()
        result = defaultdict(dict)
        for weekday, key, value in data:
            result[weekday][key] = value
        cursor.close()
        return result

    def task_counts(self, family=None):
        cursor = self.connection.cursor()

        query = '''
        SELECT key, count(steps.id) AS count
        FROM steps
        WHERE steps.created > ?
        '''

        if family is not None:
            query += '''
            AND (steps.families LIKE '%%' || ? || '%%')
            GROUP BY key
            '''
            cursor.execute(query, (self.from_date, family))
        else:
            query += '''
            GROUP BY key
            '''
            cursor.execute(query, (self.from_date,))

        result = dict(cursor.fetchall())
        cursor.close()
        return result

    def total_count(self):
        cursor = self.connection.cursor()

        query = '''
        SELECT count(steps.id) AS count
        FROM steps
        '''

        cursor.execute(query)

        result = cursor.fetchone()[0]
        cursor.close()
        return result

    def _get_percents(self, group, family):
        import settings
        if group == 'day':
            group_task_efficiencies = self.day_task_efficiency(family)
        elif group == 'hour':
            group_task_efficiencies = self.hour_task_efficiency(family)
        else:
            raise RuntimeError("Not known group type for percents %s" % group)
        task_efficiencies = self.task_efficiencies(family)
        task_counts = self.task_counts(family)
        group_percentages = defaultdict(list)

        for group_value in group_task_efficiencies:
            for task in group_task_efficiencies[group_value]:
                if task_counts[task] == 1:
                    # if there is the only one task of this type, use efficiency as percent
                    # because there is no information about the normal efficiency for this task key
                    # and we can't calculate the relative percent
                    group_percentages[group_value].append(
                        settings.LOW_DATA_EFFICIENCY_SCALE * group_task_efficiencies[group_value][task])
                else:
                    group_percentages[group_value].append(
                        group_task_efficiencies[group_value][task] / task_efficiencies[task])
        result = {value: sum(scaled_efficiency) / float(len(scaled_efficiency)) for value, scaled_efficiency in
                  group_percentages.items()}
        return result

    def day_percents(self, family=None):
        return self._get_percents('day', family)

    def hour_percents(self, family=None):
        return self._get_percents('hour', family)

    def task_efficiency_for_weekday(self, key, weekday):
        cursor = self.connection.cursor()

        query = '''
        SELECT avg(steps.efficiency) AS avg_1
        FROM steps
        WHERE steps."key" = ? AND weekday = ?
        '''
        cursor.execute(query, (key, weekday))
        result = cursor.fetchone()[0]

        cursor.close()
        return result

    def task_efficiency_for_hour(self, key, hour):
        cursor = self.connection.cursor()

        query = '''
        SELECT avg(steps.efficiency) AS avg_1
        FROM steps
        WHERE steps."key" = ? AND hour = ?
        '''
        cursor.execute(query, (key, hour))
        result = cursor.fetchone()[0]

        cursor.close()
        return result

    def task_efficiency_for_interval(self, key, from_datetime, to_datetime):
        cursor = self.connection.cursor()

        query = '''
        SELECT avg(steps.efficiency) AS avg_1
        FROM steps
        WHERE steps."key" = ? AND created >= ? AND created <= ?
        '''
        cursor.execute(query, (key, from_datetime, to_datetime))
        result = cursor.fetchone()[0]

        cursor.close()
        return result

    def total_time(self):

        cursor = self.connection.cursor()
        query = '''
        SELECT steps.created AS steps_created
        FROM steps ORDER BY steps.created %s
        LIMIT 1
        '''
        cursor.execute(query % "DESC")

        from_date = cursor.fetchone()

        cursor.execute(query % "")

        to_date = cursor.fetchone()

        if from_date and to_date:
            from_date = datetime.strptime(from_date[0], "%Y-%m-%d %H:%M:%S.%f")
            to_date = datetime.strptime(to_date[0], "%Y-%m-%d %H:%M:%S.%f")
            result = from_date - to_date
        else:
            result = timedelta(0)

        cursor.close()
        return result

    def recent_percents(self, family=None):
        task_efficiencies = self.task_efficiencies(family)
        cursor = self.connection.cursor()
        query = '''
        SELECT strftime('%Y-%m-%d', created) AS step_date, key, avg(efficiency)
        FROM steps
        WHERE created > ?
        '''
        from datetime import datetime, timedelta
        from_data = datetime.now() - timedelta(days=13)
        if family:
            query += '''
            AND (steps.families LIKE '%%' || ? || '%%')
            GROUP BY step_date, key
            '''
            recent_data = cursor.execute(query, (from_data, family)).fetchall()
        else:
            query += '''
            GROUP BY step_date, key
            '''
            recent_data = cursor.execute(query, (from_data,)).fetchall()

        result = defaultdict(list)
        for date, task, efficiency in recent_data:
            result[datetime.strptime(date, "%Y-%m-%d").date()].append(efficiency / task_efficiencies[task])
        cursor.close()
        return {value: sum(scaled_efficiency) / float(len(scaled_efficiency)) for value, scaled_efficiency in
                result.items()}


database_manager = DatabaseManager()
