# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import textwrap
import time

from gaiatest import GaiaTestCase
from marionette import MarionetteTestOptions
from marionette import MarionetteTestRunner
from marionette.runtests import cli


class GaiaTestOptions(MarionetteTestOptions):

    def __init__(self, **kwargs):
        MarionetteTestOptions.__init__(self, **kwargs)
        group = self.add_option_group('gaiatest')
        group.add_option('--restart',
                         action='store_true',
                         dest='restart',
                         default=False,
                         help='restart target instance between tests')
        group.add_option('--skip-all-warning',
                         action='store_true',
                         dest='skip_all_warning',
                         default=False,
                         help='skip all warning messages. https://developer.mozilla.org/en-US/docs/Gaia_Test_Runner#Risks')


class GaiaTestRunner(MarionetteTestRunner):

    def __init__(self, **kwargs):
        skip_all_warning = kwargs.pop('skip_all_warning', False)

        MarionetteTestRunner.__init__(self, **kwargs)

        width = 80
        if (not self.testvars.get('acknowledged_risks') is True) and (not skip_all_warning is True):
            url = 'https://developer.mozilla.org/en-US/docs/Gaia_Test_Runner#Risks'
            heading = 'Acknowledge risks'
            message = 'These tests are destructive and will remove data from the target Firefox OS instance as well ' \
                      'as using services that may incur costs! Before you can run these tests you must follow the ' \
                      'steps to indicate you have acknowledged the risks detailed at the following address:'
            print '\n' + '*' * 5 + ' %s ' % heading.upper() + '*' * (width - len(heading) - 7)
            print '\n'.join(textwrap.wrap(message, width))
            print url
            print '*' * width + '\n'
            exit()
        if (not self.testvars.get('skip_warning') is True) and (not skip_all_warning is True):
            delay = 30
            heading = 'Warning'
            message = 'You are about to run destructive tests against a Firefox OS instance. These tests ' \
                      'will restore the target to a clean state, meaning any personal data such as contacts, ' \
                      'messages, photos, videos, music, etc. will be removed. The tests may also attempt to ' \
                      'initiate outgoing calls, or connect to services such as cellular data, wifi, gps, ' \
                      'bluetooth, etc.'
            try:
                print '\n' + '*' * 5 + ' %s ' % heading.upper() + '*' * (width - len(heading) - 7)
                print '\n'.join(textwrap.wrap(message, width))
                print '*' * width + '\n'
                print 'To abort the test run hit Ctrl+C on your keyboard.'
                print 'The test run will continue in %d seconds.' % delay
                time.sleep(delay)
            except KeyboardInterrupt:
                print '\nTest run aborted by user.'
                exit()
            print 'Continuing with test run...\n'

    def register_handlers(self):
        self.test_handlers.extend([GaiaTestCase])


def main():
    cli(runner_class=GaiaTestRunner, parser_class=GaiaTestOptions)


if __name__ == "__main__":
    main()
