# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Approximate runtime per 100 iterations: 10 minutes

from gaiatest import GaiaStressTest

import os
import datetime
import time


class TestStressAddEvent(GaiaStressTest):

    _add_event_button_locator = ('xpath', "//a[@href='/event/add/']")
    _event_title_input_locator = ('xpath', "//input[@data-l10n-id='event-title']")
    _event_location_input_locator = ('xpath', "//input[@data-l10n-id='event-location']")
    _event_start_time_input_locator = ('xpath', "//input[@data-l10n-id='event-start-time']")
    _event_end_time_input_locator = ('xpath', "//input[@data-l10n-id='event-end-time']")
    _save_event_button_locator = ('css selector', 'button.save')

    _event_start_date_input_locator = ('xpath', "//input[@data-l10n-id='event-start-date']")
    _event_end_date_input_locator = ('xpath', "//input[@data-l10n-id='event-end-date']")

    def setUp(self):
        GaiaStressTest.setUp(self)

        # Set name of stress test method to be repeated
        self.test_method = self.add_event

        # Setting the system time to a hardcoded datetime to avoid timezone issues
        # Jan. 1, 2013, according to http://www.epochconverter.com/
        _seconds_since_epoch = 1357043430
        self.today = datetime.datetime.utcfromtimestamp(_seconds_since_epoch)

        # set the system date to an expected date, and timezone to UTC
        self.data_layer.set_time(_seconds_since_epoch * 1000)
        self.data_layer.set_setting('time.timezone', 'Atlantic/Reykjavik')

        # Starting event
        self.next_event_date = self.today

        # launch the Calendar app
        self.app = self.apps.launch('calendar')

    def test_stress_add_event(self):
        self.drive()

    def add_event(self, count):
        # Add a calendar event on the next day and verify
        # Borrowed some code from test_add_calendar.py
        event_title = "Event %d of %d" % (count, self.iterations)
        event_location = "Event Location %s" % str(time.time())
        event_start_date = self.next_event_date.strftime("%Y-%m-%d")
        event_end_date = self.next_event_date.strftime("%Y-%m-%d")
        event_start_time = "01:00:00"
        event_end_time = "02:00:00"
        this_event_time_slot_locator = (
            'css selector',
            '#event-list section.hour-1 span.display-hour')
        month_view_time_slot_all_events_locator = (
            'css selector',
            '#event-list section.hour-1 div.events')

        # wait for the add event button to appear
        self.wait_for_element_displayed(*self._add_event_button_locator)

        # click the add event button
        add_event_button = self.marionette.find_element(*self._add_event_button_locator)
        self.marionette.tap(add_event_button)
        self.wait_for_element_displayed(*self._event_title_input_locator)

        # create a new event
        self.marionette.find_element(*self._event_title_input_locator).send_keys(event_title)
        time.sleep(1)
        self.marionette.find_element(*self._event_location_input_locator).send_keys(event_location)
        time.sleep(1)
        self.marionette.find_element(*self._event_start_date_input_locator).clear()
        self.marionette.find_element(*self._event_start_date_input_locator).send_keys(event_start_date)
        time.sleep(1)
        self.marionette.find_element(*self._event_end_date_input_locator).clear()
        self.marionette.find_element(*self._event_end_date_input_locator).send_keys(event_end_date)
        time.sleep(1)
        self.marionette.find_element(*self._event_start_time_input_locator).clear()
        self.marionette.find_element(*self._event_start_time_input_locator).send_keys(event_start_time)
        time.sleep(1)
        self.marionette.find_element(*self._event_end_time_input_locator).clear()
        self.marionette.find_element(*self._event_end_time_input_locator).send_keys(event_end_time)
        time.sleep(1)
        save_event_button = self.marionette.find_element(*self._save_event_button_locator)
        self.marionette.tap(save_event_button)

        # wait for the default calendar display
        self.wait_for_element_displayed(*this_event_time_slot_locator)

        # assert that the event is displayed as expected
        time.sleep(1)
        self.assertTrue(self.marionette.find_element(*this_event_time_slot_locator).is_displayed(),
                        "Expected the time slot for the event to be present.")
        displayed_events = self.marionette.find_element(*month_view_time_slot_all_events_locator).text
        self.assertIn(event_title, displayed_events)
        self.assertIn(event_location, displayed_events)

        # Increment for the next event
        self.next_event_date += datetime.timedelta(days=1)

        # sleep between reps
        time.sleep(3)
