# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from gaiatest import GaiaTestCase


class TestContacts(GaiaTestCase):

    # settings section
    _loading_overlay_locator = ('id', 'loading-overlay')
    _contacts_items_locator = ('css selector', 'li.contact-item')
    _settings_button_locator = ('id', 'settings-button')
    _settings_close_button_locator = ('id', 'settings-close')
    _check_fb_span_locator = ('id', 'span-check-fb')

    # facebook section
    _facebook_login_iframe_locator = ('css selector', 'iframe[data-url*="m.facebook.com/login.php"]', 60)
    _facebook_import_iframe_locator = ('css selector', 'iframe[src="fb_import.html"]', 300)
    _facebook_login_name_locator = ('css selector', 'div#u_0_0 input')
    _facebook_login_password_locator = ('css selector', 'div#u_0_1 input')
    _facebook_login_button_locator = ('css selector', 'button[name=login]')
    _facebook_friends_check_items_locator = ('css selector', 'li.block-item')
    _facebook_friends_check_items_name_locator = ('css selector', 'li.block-item p')
    _facebook_friends_check_items_inputs_locator = ('css selector', 'li.block-item label input')
    _facebook_friends_import_button_locator = ('id', 'import-action')
    _facebook_contacts_remove_button_locator = ('css selector', 'form#confirmation-message menu button.danger')

    def setUp(self):
        GaiaTestCase.setUp(self)
        # this test should have facebook information
        facebook_credential = self.testvars.get('facebook')
        self.assertTrue(facebook_credential and facebook_credential.get('username'), "No facebook username setting in testvars.")
        self.assertTrue(facebook_credential and facebook_credential.get('password'), "No facebook password setting in testvars.")

        # enable wifi
        self.data_layer.enable_wifi()
        self.data_layer.connect_to_wifi(self.testvars['wifi'])

        # launch the Contacts app
        self.app = self.apps.launch('Contacts')
        self.wait_for_element_not_displayed(*self._loading_overlay_locator)

    def create_contact_locator(self, contact):
        return ('css selector', ".contact-item p[data-search^='%s']" % contact)

    def test_import_contacts_from_facebook(self):
        """ Import contacts from facebook

        https://github.com/mozilla/gaia-ui-tests/issues/344

        """
        self.wait_for_element_displayed(*self._settings_button_locator)

        # get the contact items' number before import facebook contacts
        pre_import_contact_items = self.marionette.find_elements(*self._contacts_items_locator)
        pre_import_contact_items_number = len(pre_import_contact_items)

        # navigate to settings page
        contact_settings_button = self.marionette.find_element(*self._settings_button_locator)
        self.marionette.tap(contact_settings_button)
        # turn on facebook import switch
        self.wait_for_element_displayed(*self._check_fb_span_locator)
        settings_check_fb = self.marionette.find_element(*self._check_fb_span_locator)
        self.marionette.tap(settings_check_fb)

        # switch to facebook login frame
        self.marionette.switch_to_frame()
        facebook_login_iframe = self.wait_for_element_present(*self._facebook_login_iframe_locator)
        self.marionette.switch_to_frame(facebook_login_iframe)

        # login to facebook, due to the permission-allow page only display once, skip this step here
        self.wait_for_element_displayed(*self._facebook_login_name_locator)
        fb_name = self.marionette.find_element(*self._facebook_login_name_locator)
        fb_password = self.marionette.find_element(*self._facebook_login_password_locator)
        fb_login = self.marionette.find_element(*self._facebook_login_button_locator)
        fb_name.send_keys(self.testvars['facebook']['username'])
        fb_password.send_keys(self.testvars['facebook']['password'])
        self.marionette.tap(fb_login)
        # do it as soon as possible, or self.marionette.switch_to_frame() will throw exception...
        self.marionette.switch_to_frame()
        self.marionette.switch_to_frame(self.app.frame)

        # switch to facebook import page to select the friends
        facebook_import_iframe = self.wait_for_element_present(*self._facebook_import_iframe_locator)
        self.marionette.switch_to_frame(facebook_import_iframe)
        # select one friend (first) from facebook
        self.wait_for_element_displayed(*self._facebook_friends_check_items_locator)
        facebook_friends_check_items = self.marionette.find_elements(*self._facebook_friends_check_items_locator)
        facebook_friends_check_items_inputs = self.marionette.find_elements(*self._facebook_friends_check_items_inputs_locator)
        # Assume that there will be more than 0 friends in facebook account
        self.assertTrue(len(facebook_friends_check_items) > 0, 'Expect more than 0 friends in facebook account.')
        self.marionette.tap(facebook_friends_check_items[0])
        contact_name_item = self.marionette.find_element(*self._facebook_friends_check_items_name_locator)
        contact_name = contact_name_item.text
        facebook_friends_import_button = self.marionette.find_element(*self._facebook_friends_import_button_locator)
        self.marionette.tap(facebook_friends_import_button)

        # switch to contacts app
        self.marionette.switch_to_frame()
        self.marionette.switch_to_frame(self.app.frame)
        self.wait_for_element_displayed(*self.create_contact_locator(contact_name))
        contact_item = self.marionette.find_element(*self.create_contact_locator(contact_name))

        # get the contact items' number after import facebook contacts
        post_import_contact_items = self.marionette.find_elements(*self._contacts_items_locator)
        post_import_contact_items_number = len(post_import_contact_items)

        # the amount of contact items should increase
        self.assertEqual((pre_import_contact_items_number + 1), post_import_contact_items_number, 'The amount of contacts should increase.')
        # the name of contact should be the same as facebook's
        self.assertEqual(contact_item.text, contact_name, 'The name of contact should be the same as facebook.')

        # prepare to remove facebook contacts
        self.wait_for_element_displayed(*self._settings_button_locator)

        # get the contact items' number before remove facebook contacts
        pre_remove_contact_items = self.marionette.find_elements(*self._contacts_items_locator)
        pre_remove_contact_items_number = len(pre_remove_contact_items)

        # navigate to settings page
        contact_settings_button = self.marionette.find_element(*self._settings_button_locator)
        self.marionette.tap(contact_settings_button)
        # turn on facebook import switch
        self.wait_for_element_displayed(*self._check_fb_span_locator)
        settings_check_fb = self.marionette.find_element(*self._check_fb_span_locator)
        self.marionette.tap(settings_check_fb)

        # tap button to remove the connection between contacts and facebook
        self.wait_for_element_displayed(*self._facebook_contacts_remove_button_locator)
        facebook_contacts_remove_button = self.marionette.find_element(*self._facebook_contacts_remove_button_locator)
        self.marionette.tap(facebook_contacts_remove_button)

        # go to contacts main page from settings page
        self.wait_for_element_displayed(*self._settings_close_button_locator)
        settings_close_button = self.marionette.find_element(*self._settings_close_button_locator)
        self.marionette.tap(settings_close_button)

        # get the contact items' number after remove facebook contacts
        post_remove_contact_items = self.marionette.find_elements(*self._contacts_items_locator)
        post_remove_contact_items_number = len(post_remove_contact_items)

        # the amount of contact items should decrease
        self.assertEqual(pre_remove_contact_items_number, (post_remove_contact_items_number + 1), 'The amount of contacts should decrease.')
