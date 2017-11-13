import os
import settings
import pytest
from managers.database import database_manager
from datetime import datetime, timedelta


@pytest.fixture
def data():
    database_manager.add_stat('numbers_calculation', 10, 1.0)
    database_manager.add_stat('numbers_calculation', 10, 2.0)
    database_manager.add_stat('numbers_calculation', 10, 3.0)

    database_manager.add_stat('color_sequence', 10, 3.0)
    database_manager.add_stat('color_sequence', 10, 4.0)
    database_manager.add_stat('color_sequence', 10, 5.0)


def test_initialize():
    assert database_manager._connection is None
    assert database_manager.connection
    assert database_manager.path == os.path.join(settings.PROJECT_DIR, settings.DATABASE_NAME)


def test_average_task_efficiency(data):
    result = database_manager.task_efficiencies()
    assert result['numbers_calculation'] == (1. + 2. + 3.) / 3
    result = database_manager.task_efficiencies(family=settings.MEMORY_FAMILY)
    assert not 'number_calculation' in result
    assert 'color_sequence' in result
    assert result['color_sequence'] == (3. + 4. + 5.) / 3


def test_all(data):
    result = database_manager.all_stat()
    assert len(result) == 6


@pytest.fixture
def data_day():
    n = datetime.now()

    monday = n.replace(2015, 7, 20)
    tuesday = n.replace(2015, 7, 21)
    database_manager.add_stat('numbers_calculation', 10, 1.0, created=monday)
    database_manager.add_stat('numbers_calculation', 10, 2.0, created=monday)
    database_manager.add_stat('numbers_calculation', 10, 3.0, created=tuesday)
    database_manager.add_stat('numbers_calculation', 10, 4.0, created=tuesday)

    database_manager.add_stat('color_sequence', 10, 3.0, created=monday)
    database_manager.add_stat('color_sequence', 10, 4.0, created=monday)
    database_manager.add_stat('color_sequence', 10, 5.0, created=tuesday)
    database_manager.add_stat('color_sequence', 10, 6.0, created=tuesday)


def test_day_task_efficiency(data_day):
    start = datetime(2015, 7, 20, hour=20)
    database_manager.from_date = start - timedelta(days=10)
    result = database_manager.day_task_efficiency()
    assert result[0]['numbers_calculation'] == (1.0 + 2.0) / 2
    assert result[1]['numbers_calculation'] == (3.0 + 4.0) / 2
    assert result[0]['color_sequence'] == (3.0 + 4.0) / 2
    assert result[1]['color_sequence'] == (5.0 + 6.0) / 2

    result = database_manager.day_task_efficiency(family=settings.MEMORY_FAMILY)
    assert 'numbers_calculation' not in result[0]
    assert 'numbers_calculation' not in result[1]
    assert result[0]['color_sequence'] == (3.0 + 4.0) / 2
    assert result[1]['color_sequence'] == (5.0 + 6.0) / 2


@pytest.fixture
def data_hour(mock):
    start = datetime(2015, 7, 20, hour=20)
    one_hour_later = datetime(2015, 7, 20, hour=21)
    database_manager.from_date = start - timedelta(days=10)

    database_manager.add_stat('numbers_calculation', 10, 1.0, created=start)
    database_manager.add_stat('numbers_calculation', 10, 2.0, created=start)
    database_manager.add_stat('numbers_calculation', 10, 3.0, created=one_hour_later)
    database_manager.add_stat('numbers_calculation', 10, 4.0, created=one_hour_later)

    database_manager.add_stat('color_sequence', 10, 3.0, created=start)
    database_manager.add_stat('color_sequence', 10, 4.0, created=start)
    database_manager.add_stat('color_sequence', 10, 5.0, created=one_hour_later)
    database_manager.add_stat('color_sequence', 10, 6.0, created=one_hour_later)


def test_hour_task_efficiency(data_hour):
    result = database_manager.hour_task_efficiency()
    assert result[20]['numbers_calculation'] == (1.0 + 2.0) / 2
    assert result[21]['numbers_calculation'] == (3.0 + 4.0) / 2
    assert result[20]['color_sequence'] == (3.0 + 4.0) / 2
    assert result[21]['color_sequence'] == (5.0 + 6.0) / 2

    result = database_manager.hour_task_efficiency(family=settings.MEMORY_FAMILY)
    assert 'numbers_calculation' not in result[20]
    assert 'numbers_calculation' not in result[21]
    assert result[20]['color_sequence'] == (3.0 + 4.0) / 2
    assert result[21]['color_sequence'] == (5.0 + 6.0) / 2


def test_counts(data):
    result = database_manager.task_counts()
    assert result['numbers_calculation'] == 3
    assert result['color_sequence'] == 3

    result = database_manager.task_counts(settings.MEMORY_FAMILY)
    assert 'numbers_calculation' not in result
    assert result['color_sequence'] == 3


def test_day_percents(data_day):
    result = database_manager.day_percents()
    assert abs(result[0] - 0.68) < 0.01
    assert abs(result[1] - 1.31) < 0.01

    result = database_manager.day_percents(settings.MEMORY_FAMILY)
    assert abs(result[0] - 0.78) < 0.01
    assert abs(result[1] - 1.22) < 0.01


def test_hour_percents(data_hour):
    result = database_manager.hour_percents()
    assert abs(result[20] - 0.68) < 0.01
    assert abs(result[21] - 1.31) < 0.01

    result = database_manager.hour_percents(settings.MEMORY_FAMILY)
    assert abs(result[20] - 0.78) < 0.01
    assert abs(result[21] - 1.22) < 0.01


def test_task_average_for_weekday(data_day):
    result = database_manager.task_efficiency_for_weekday('numbers_calculation', 0)
    assert result == 1.5


def test_task_average_for_hour(data_hour):
    result = database_manager.task_efficiency_for_hour('numbers_calculation', 20)
    assert result == 1.5


def test_task_average_for_interval(data_day):
    result = database_manager.task_efficiency_for_interval(
        'numbers_calculation', datetime(2015, 7, 19), datetime(2015, 7, 22)
    )
    assert result == 2.5


def test_total_time(data_day):
    result = database_manager.total_time()
    assert result.days == 1


today = datetime.now()
yesterday = today - timedelta(days=1)
last_week = today - timedelta(days=7)
too_old = today - timedelta(days=21)


@pytest.fixture
def data_progress():
    database_manager.add_stat('numbers_calculation', 10, 1.0, created=today)
    database_manager.add_stat('numbers_calculation', 10, 2.0, created=yesterday)
    database_manager.add_stat('numbers_calculation', 10, 3.0, created=last_week)
    database_manager.add_stat('numbers_calculation', 10, 4.0, created=too_old)

    database_manager.add_stat('color_sequence', 10, 3.0, created=today)
    database_manager.add_stat('color_sequence', 10, 4.0, created=yesterday)
    database_manager.add_stat('color_sequence', 10, 5.0, created=last_week)
    database_manager.add_stat('color_sequence', 10, 6.0, created=too_old)


def test_recent_progress_stat(data_progress):
    result = database_manager.recent_percents()
    assert abs(result[today.date()] - (1. / 2.5 + 3. / 4.5) / 2) < 0.01
    assert abs(result[yesterday.date()] - (2. / 2.5 + 4. / 4.5) / 2) < 0.01
    assert abs(result[last_week.date()] - (3. / 2.5 + 5. / 4.5) / 2) < 0.01
    assert too_old.date() not in result

    result = database_manager.recent_percents(settings.MEMORY_FAMILY)
    assert abs(result[today.date()] - 3. / 4.5) < 0.01
    assert abs(result[yesterday.date()] - 4. / 4.5) < 0.01
    assert abs(result[last_week.date()] - 5. / 4.5) < 0.01
