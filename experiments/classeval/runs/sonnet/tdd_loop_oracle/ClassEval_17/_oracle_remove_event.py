import sys, unittest
sys.path.insert(0, '.')
from datetime import datetime, timedelta
from solution import CalendarUtil

class CalendarTestRemoveEvent(unittest.TestCase):
    def test_remove_event(self):
        calendar = CalendarUtil()
        calendar.events = [{'date': datetime(2023, 1, 1, 0, 0), 'start_time': datetime(2023, 1, 1, 0, 0),
                            'end_time': datetime(2023, 1, 1, 1, 0), 'description': 'New Year'}]
        calendar.remove_event({'date': datetime(2023, 1, 1, 0, 0), 'start_time': datetime(2023, 1, 1, 0, 0),
                               'end_time': datetime(2023, 1, 1, 1, 0), 'description': 'New Year'})
        self.assertEqual(calendar.events, [])

    def test_remove_event_2(self):
        calendar = CalendarUtil()
        calendar.events = [{'date': datetime(2023, 1, 1, 0, 0), 'start_time': datetime(2023, 1, 1, 0, 0),
                            'end_time': datetime(2023, 1, 1, 1, 0), 'description': 'New Year'},
                           {'date': datetime(2023, 1, 2, 0, 0), 'start_time': datetime(2023, 1, 2, 0, 0),
                            'end_time': datetime(2023, 1, 2, 1, 0), 'description': 'New Year'}]
        calendar.remove_event({'date': datetime(2023, 1, 1, 0, 0), 'start_time': datetime(2023, 1, 1, 0, 0),
                               'end_time': datetime(2023, 1, 1, 1, 0), 'description': 'New Year'})
        self.assertEqual(calendar.events, [
            {'date': datetime(2023, 1, 2, 0, 0), 'start_time': datetime(2023, 1, 2, 0, 0),
             'end_time': datetime(2023, 1, 2, 1, 0), 'description': 'New Year'}])

    def test_remove_event_3(self):
        calendar = CalendarUtil()
        calendar.events = [{'date': datetime(2023, 1, 1, 0, 0), 'start_time': datetime(2023, 1, 1, 0, 0),
                            'end_time': datetime(2023, 1, 1, 1, 0), 'description': 'New Year'},
                           {'date': datetime(2023, 1, 2, 0, 0), 'start_time': datetime(2023, 1, 2, 0, 0),
                            'end_time': datetime(2023, 1, 2, 1, 0), 'description': 'New Year'}]
        calendar.remove_event({'date': datetime(2023, 1, 2, 0, 0), 'start_time': datetime(2023, 1, 2, 0, 0),
                               'end_time': datetime(2023, 1, 2, 1, 0), 'description': 'New Year'})
        self.assertEqual(calendar.events, [
            {'date': datetime(2023, 1, 1, 0, 0), 'start_time': datetime(2023, 1, 1, 0, 0),
             'end_time': datetime(2023, 1, 1, 1, 0), 'description': 'New Year'}])

    def test_remove_event_4(self):
        calendar = CalendarUtil()
        calendar.events = [{'date': datetime(2023, 1, 1, 0, 0), 'start_time': datetime(2023, 1, 1, 0, 0),
                            'end_time': datetime(2023, 1, 1, 23, 0), 'description': 'New Year'},
                           {'date': datetime(2023, 1, 2, 0, 0), 'start_time': datetime(2023, 1, 2, 0, 0),
                            'end_time': datetime(2023, 1, 2, 1, 0), 'description': 'New Year'}]
        calendar.remove_event({'date': datetime(2023, 1, 2, 0, 0), 'start_time': datetime(2023, 1, 2, 0, 0),
                               'end_time': datetime(2023, 1, 2, 1, 0), 'description': 'New Year'})
        self.assertEqual(calendar.events, [
            {'date': datetime(2023, 1, 1, 0, 0), 'start_time': datetime(2023, 1, 1, 0, 0),
             'end_time': datetime(2023, 1, 1, 23, 0), 'description': 'New Year'}])

    def test_remove_event_5(self):
        calendar = CalendarUtil()
        calendar.events = [{'date': datetime(2023, 1, 1, 0, 0), 'start_time': datetime(2023, 1, 1, 0, 0),
                            'end_time': datetime(2023, 1, 1, 22, 0), 'description': 'New Year'},
                           {'date': datetime(2023, 1, 2, 0, 0), 'start_time': datetime(2023, 1, 2, 0, 0),
                            'end_time': datetime(2023, 1, 2, 1, 0), 'description': 'New Year'}]
        calendar.remove_event({'date': datetime(2023, 1, 2, 0, 0), 'start_time': datetime(2023, 1, 2, 0, 0),
                               'end_time': datetime(2023, 1, 2, 1, 0), 'description': 'New Year'})
        self.assertEqual(calendar.events, [
            {'date': datetime(2023, 1, 1, 0, 0), 'start_time': datetime(2023, 1, 1, 0, 0),
             'end_time': datetime(2023, 1, 1, 22, 0), 'description': 'New Year'}])

    def test_remove_event_6(self):
        calendar = CalendarUtil()
        calendar.events = []
        calendar.remove_event({'date': datetime(2023, 1, 1, 0, 0), 'start_time': datetime(2023, 1, 1, 0, 0),
                               'end_time': datetime(2023, 1, 1, 1, 0), 'description': 'New Year'})
        self.assertEqual(calendar.events, [])

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(CalendarTestRemoveEvent)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
