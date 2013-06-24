# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from gaiatest import GaiaTestCase
from gaiatest.mocks.mock_contact import MockContact

from gaiatest.apps.contacts.app import Contacts

from progressbar import *


class CreateMockContacts(GaiaTestCase):

    def setUp(self):
        GaiaTestCase.setUp(self)

    def test_create_mock_contacts(self):
        amount = 500
        z_width = 3

        print 'Total amount:', amount
        pbar = ProgressBar().start()
        for i in range(amount):
            # Seed the contact with the remote phone number so we don't call random people
            self.contact = MockContact(givenName=str(i).zfill(z_width), familyName='test', name=str(i).zfill(z_width)+' test')
            self.data_layer.insert_contact(self.contact)
            pbar.update(int((i*100)/amount))

        contacts = Contacts(self.marionette)
        contacts.launch()

    def tearDown(self):
        GaiaTestCase.tearDown(self)
