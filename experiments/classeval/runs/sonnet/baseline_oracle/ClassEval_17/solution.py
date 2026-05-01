from datetime import datetime, timedelta

class CalendarUtil:
    """
    This is a class as CalendarUtil that provides functionalities to manage calendar events, schedule appointments, and perform conflict checks.
    """

    def __init__(self):
        self.events = []

    def add_event(self, event):
        self.events.append(event)

    def remove_event(self, event):
        if event in self.events:
            self.events.remove(event)

    def get_events(self, date):
        return [e for e in self.events if e['date'].date() == date.date()]

    def is_available(self, start_time, end_time):
        for event in self.events:
            if start_time < event['end_time'] and end_time > event['start_time']:
                return False
        return True

    def get_available_slots(self, date):
        day_start = datetime(date.year, date.month, date.day, 0, 0)
        slots = []
        for hour in range(24):
            slot_start = day_start + timedelta(hours=hour)
            slot_end = slot_start + timedelta(hours=1)
            if self.is_available(slot_start, slot_end):
                slots.append((slot_start, slot_end))
        return slots

    def get_upcoming_events(self, num_events):
        if not self.events:
            return []
        sorted_events = sorted(self.events, key=lambda e: e['start_time'])
        earliest = sorted_events[0]['start_time']
        upcoming = [e for e in sorted_events if e['start_time'] > earliest]
        return upcoming[:num_events]