# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import time
from gaiatest import GaiaTestCase


class TestContacts(GaiaTestCase):

    _loading_overlay = ('id', 'loading-overlay')

    _contacts_items_locator = ("css selector", "li.contact-item")
    _settings_button_locator = ("id", "settings-button")
    _settings_close_button_locator = ("id", "settings-close")
    _check_fb_span_locator = ("id", "span-check-fb")
    
    _facebook_import_iframe_locator = ('css selector', 'iframe[src="fb_import.html"]')
    
    _iframe_selector = ("css selector", "iframe")
    
    _facebook_login_url = "m.facebook.com/login.php"
    
    _facebook_login_name_locator = ("css selector", "div#u_0_0 input")
    _facebook_login_pw_locator = ("css selector", "div#u_0_1 input")
    _facebook_login_button_locator = ("css selector", "button[name=login]")
    
    _facebook_friends_check_items_locator = ("css selector", "li.block-item")
    _facebook_friends_check_items_name_locator = ("css selector", "li.block-item p")
    _facebook_friends_check_items_inputs_locator = ("css selector", "li.block-item label input")
    _facebook_friends_import_button_locator = ("id", "import-action")
    
    _facebook_contacts_remove_button_locator = ("css selector", "form#confirmation-message menu button.danger")
    
    
    def setUp(self):
        GaiaTestCase.setUp(self)
        # enable wifi
        self.data_layer.enable_wifi()
        self.data_layer.connect_to_wifi(self.testvars['wifi'])
        
        # launch the Contacts app
        self.app = self.apps.launch('Contacts')
        self.wait_for_element_not_displayed(*self._loading_overlay)

    def create_contact_locator(self, contact):
        return ('xpath', "//li[@class='contact-item']/a[p[contains(@data-search, '%s')]]" % contact)
    
    def create_contact_text_locator(self, contact):
        return ('xpath', "//li[@class='contact-item']/a/p[contains(@data-search, '%s')]" % contact)

    def test_import_contacts_from_facebook(self):
        
        self.wait_for_element_displayed(*self._settings_button_locator)
        
        pre_contact_items = self.marionette.find_elements(*self._contacts_items_locator)
        pre_contact_items_number = len(pre_contact_items)
        
        contact_settings_button = self.marionette.find_element(*self._settings_button_locator)
        self.marionette.tap(contact_settings_button)
        
        self.wait_for_element_displayed(*self._check_fb_span_locator)
        settings_check_fb = self.marionette.find_element(*self._check_fb_span_locator)
        self.marionette.tap(settings_check_fb)
        
        self.marionette.switch_to_frame()
        # time issue, need to wait device connect to fb...
        time.sleep(10)
        browser_frames = self.marionette.find_elements(*self._iframe_selector)
        
        for browser_frame in browser_frames:
            if self._facebook_login_url in browser_frame.get_attribute("data-url"):
                self.marionette.switch_to_frame(browser_frame)
                break
                
        self.wait_for_element_displayed(*self._facebook_login_name_locator)
        fb_name = self.marionette.find_element(*self._facebook_login_name_locator)
        fb_pw = self.marionette.find_element(*self._facebook_login_pw_locator)
        fb_login = self.marionette.find_element(*self._facebook_login_button_locator)
        fb_name.send_keys(self.testvars['facebook']['username'])
        fb_pw.send_keys(self.testvars['facebook']['password'])
        self.marionette.tap(fb_login);
        # do it as soon as possible, or self.marionette.switch_to_frame() will throw exception...
        self.marionette.switch_to_frame();
        
        # time issue, need to wait device connect to fb...
        time.sleep(10)
        self.marionette.switch_to_frame(self.app.frame)
        self.marionette.switch_to_frame(self.marionette.find_element(*self._facebook_import_iframe_locator))
        
        # select one fb friend        
        facebook_friends_check_items = self.marionette.find_elements(*self._facebook_friends_check_items_locator)
        facebook_friends_check_items_inputs = self.marionette.find_elements(*self._facebook_friends_check_items_inputs_locator)
        
        contact_name = ""
        if len(facebook_friends_check_items) > 0 :
            facebook_friends_check_items[0].text
            self.marionette.tap(facebook_friends_check_items[0])
            contact_name_item =self.marionette.find_element(*self._facebook_friends_check_items_name_locator)
            contact_name = contact_name_item.text
            facebook_friends_import_button = self.marionette.find_element(*self._facebook_friends_import_button_locator)
            self.marionette.tap(facebook_friends_import_button)
            self.marionette.switch_to_frame()
            self.marionette.switch_to_frame(self.app.frame)
            # time issue, need to wait device connect to fb...
            time.sleep(10)
        
        self.wait_for_element_displayed(*self._settings_button_locator)
        contact_item = self.marionette.find_element(*self.create_contact_text_locator(contact_name))
        
        post_contact_items = self.marionette.find_elements(*self._contacts_items_locator)
        post_contact_items_number = len(post_contact_items)
        
        self.assertTrue( contact_item.text == contact_name )
        self.assertTrue( (pre_contact_items_number+1) == post_contact_items_number )
        
    
    def test_remove_contacts_from_facebook(self):
        
        self.wait_for_element_displayed(*self._settings_button_locator)
        
        pre_contact_items = self.marionette.find_elements(*self._contacts_items_locator)
        pre_contact_items_number = len(pre_contact_items)

        contact_settings_button = self.marionette.find_element(*self._settings_button_locator)
        self.marionette.tap(contact_settings_button)
        
        self.wait_for_element_displayed(*self._check_fb_span_locator)
        settings_check_fb = self.marionette.find_element(*self._check_fb_span_locator)
        self.marionette.tap(settings_check_fb)
        
        self.wait_for_element_displayed(*self._facebook_contacts_remove_button_locator)
        facebook_contacts_remove_button = self.marionette.find_element(*self._facebook_contacts_remove_button_locator)
        self.marionette.tap(facebook_contacts_remove_button)
        
        self.wait_for_element_displayed(*self._settings_close_button_locator)
        settings_close_button = self.marionette.find_element(*self._settings_close_button_locator)
        self.marionette.tap(settings_close_button)

        post_contact_items = self.marionette.find_elements(*self._contacts_items_locator)
        post_contact_items_number = len(post_contact_items)

        # There is no contact-item when running gaiatest now.
        if pre_contact_items_number > 0:
            self.assertTrue( pre_contact_items_number == (post_contact_items_number+1) )
        else:
            self.assertTrue((pre_contact_items_number == 0) and (post_contact_items_number == 0))
    