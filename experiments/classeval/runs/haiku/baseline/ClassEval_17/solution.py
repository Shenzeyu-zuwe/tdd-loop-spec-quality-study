from datetime import datetime, timedelta

class CalendarUtil:
    """
    This is a class as CalendarUtil that provides functionalities to manage calendar events, schedule appointments, and perform conflict checks.
    """

    def __init__(self):
        """
        Initialize the calendar with an empty list of events.
        """
        self.events = []

    def add_event(self, event):
        """
        Add an event to the calendar.
        :param event: The event to be added to the calendar,dict.
        """
        self.events.append(event)

    def remove_event(self, event):
        """
        Remove an event from the calendar.
        :param event: The event to be removed from the calendar,dict.
        """
        if event in self.events:
            self.events.remove(event)

    def get_events(self, date):
        """
        Get all events on a given date.
        :param date: The date to get events for,datetime.
        :return: A list of events on the given date,list.
        """
        result = []
        for event in self.events:
            event_date = event['date']
            if event_date.date() == date.date():
                result.append(event)
        return result

    def is_available(self, start_time, end_time):
        """
        Check if the calendar is available for a given time slot.
        :param start_time: The start time of the time slot,datetime.
        :param end_time: The end time of the time slot,datetime.
        :return: True if the calendar is available for the given time slot, False otherwise,bool.
        """
        for event in self.events:
            event_start = event.get('start_time', event['date'])
            event_end = event.get('end_time')
            
            if event_end is None:
                continue
            
            if not (end_time <= event_start or start_time >= event_end):
                return False
        return True

    def get_available_slots(self, date):
        """
        Get all available time slots on a given date.
        :param date: The date to get available time slots for,datetime.
        :return: A list of available time slots on the given date,list.
        """
        events_on_date = self.get_events(date)
        
        sorted_events = sorted(
            events_on_date,
            key=lambda e: e.get('start_time', e['date'])
        )
        
        available_slots = []
        day_start = datetime(date.year, date.month, date.day)
        day_end = day_start + timedelta(days=1)
        
        if not sorted_events:
            available_slots.append((day_start, day_end))
        else:
            first_event_start = sorted_events[0].get('start_time', sorted_events[0]['date'])
            if first_event_start > day_start:
                available_slots.append((day_start, first_event_start))
            
            for i in range(len(sorted_events) - 1):
                current_event_end = sorted_events[i].get('end_time')
                next_event_start = sorted_events[i + 1].get('start_time', sorted_events[i + 1]['date'])
                
                if current_event_end and next_event_start > current_event_end:
                    available_slots.append((current_event_end, next_event_start))
            
            last_event_end = sorted_events[-1].get('end_time')
            if last_event_end and last_event_end < day_end:
                available_slots.append((last_event_end, day_end))
        
        return available_slots

    def get_upcoming_events(self, num_events):
        """
        Get the next n upcoming events from a given date.
        :param date: The date to get upcoming events from,datetime.
        :param n: The number of upcoming events to get,int.
        :return: A list of the next n upcoming events from the given date,list.
        """
        sorted_events = sorted(
            self.events,
            key=lambda e: e.get('start_time', e['date'])
        )
        return sorted_events[:num_events]