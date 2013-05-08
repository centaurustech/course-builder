# Copyright 2013 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Functional tests for Course Builder."""

__author__ = 'John Orr (jorr@google.com)'

import os.path
import random
import time
from selenium import webdriver
from tests import suite
import pageobjects


class BaseIntegrationTest(suite.TestBase):
    """Base class for all integration tests."""

    TAGS = [suite.TestBase.REQUIRES_INTEGRATION_SERVER]

    LOGIN = 'test'

    def setUp(self):  # pylint: disable-msg=g-bad-name
        self.driver = webdriver.Chrome()

    def tearDown(self):  # pylint: disable-msg=g-bad-name
        time.sleep(1)  # avoid broken sockets on the server
        self.driver.quit()

    def load_root_page(self):
        return pageobjects.RootPage(self).load(
            suite.TestBase.INTEGRATION_SERVER_BASE_URL)

    def load_dashboard(self, name):
        return pageobjects.DashboardPage(self).load(
            suite.TestBase.INTEGRATION_SERVER_BASE_URL, name)

    def get_uid(self):
        """Generate a unique id string."""
        uid = ''
        for i in range(10):  # pylint: disable-msg=unused-variable
            j = random.randint(0, 61)
            if j < 26:
                uid += chr(65 + j)  # ascii capital letters
            elif j < 52:
                uid += chr(97 + j - 26)  # ascii lower case letters
            else:
                uid += chr(48 + j - 52)  # ascii digits
        return uid

    def create_new_course(self):
        """Create a new course with a unique name, using the admin tools."""
        uid = self.get_uid()
        name = 'ns_%s' % uid
        title = 'Test Course (%s)' % uid

        self.load_root_page(
        ).click_login(
        ).login(
            self.LOGIN, admin=True
        ).click_admin(
        ).click_add_course(
        ).set_fields(
            name=name, title=title, email='a@bb.com'
        ).click_save(
            link_text='Add New Course', status_message='Added.'
        ).click_close()

        return (name, title)


class SampleCourseTests(BaseIntegrationTest):
    """Integration tests on the sample course installed with Course Builder."""

    def test_admin_can_add_announcement(self):
        uid = self.get_uid()
        login = 'test-%s' % uid
        name = 'A Student (%s)' % uid
        title = 'Test announcement (%s)' % uid

        self.load_root_page(
        ).click_login(
        ).login(
            login, admin=True
        ).click_register(
        ).enroll(
            name
        ).verify_enrollment(
        ).click_course(
        ).click_announcements(
        ).click_add_new(
        ).enter_fields(
            title=title, date='2013/03/01',
            body='The new announcement'
        ).click_save(
        ).click_close(
        ).verify_announcement(
            title=title + ' (Draft)', date='2013-03-01',
            body='The new announcement')

    def test_admin_can_change_admin_user_emails(self):
        uid = self.get_uid()
        login = 'test-%s' % uid
        email = 'new-admin-%s@foo.com' % uid

        self.load_root_page(
        ).click_login(
        ).login(
            login, admin=True
        ).click_admin(
        ).click_settings(
        ).click_override_admin_user_emails(
        ).set_value(
            email
        ).set_status(
            'Active'
        ).click_save(
        ).click_close(
        ).verify_admin_user_emails_contains(email)


class AdminTests(BaseIntegrationTest):
    """Tests for the administrator interface."""

    LOGIN = 'test'

    def test_default_course_is_read_only(self):
        self.load_root_page(
        ).click_login(
        ).login(
            self.LOGIN, admin=True
        ).click_dashboard(
        ).verify_read_only_course()

    def test_create_new_course(self):
        self.create_new_course()

    def test_add_unit(self):
        name = self.create_new_course()[0]

        self.load_dashboard(
            name
        ).verify_not_publicly_available(
        ).click_add_unit(
        ).set_title(
            'Test Unit 1'
        ).set_status(
            'Public'
        ).click_save(
        ).click_close(
        ).verify_course_outline_contains_unit('Unit 1 - Test Unit 1')

    def test_cancel_add_with_no_changes_should_not_need_confirm(self):
        """Test entering editors and clicking close without making changes."""

        name = self.create_new_course()[0]

        # Test Import
        self.load_dashboard(name).click_import(
        ).click_close(
        ).verify_not_publicly_available()  # confirm that we're on the dashboard

        # Test Add Assessment
        self.load_dashboard(name).click_add_assessment(
        ).click_close(
        ).verify_not_publicly_available()  # confirm that we're on the dashboard

        # Test Add Link
        self.load_dashboard(name).click_add_link(
        ).click_close(
        ).verify_not_publicly_available()  # confirm that we're on the dashboard

        # Test Add Unit
        self.load_dashboard(name).click_add_unit(
        ).click_close(
        ).verify_not_publicly_available()  # confirm that we're on the dashboard

        # Test Add Lesson
        self.load_dashboard(name).click_add_lesson(
        ).click_close(
        ).verify_not_publicly_available()  # confirm that we're on the dashboard

        # Test Organize Units and Lessons
        self.load_dashboard(name).click_organize(
        ).click_close(
        ).verify_not_publicly_available()  # confirm that we're on the dashboard

    def test_upload_and_delete_image(self):
        """Admin should be able to upload an image and then delete it."""
        image_file = os.path.join(
            os.path.dirname(__file__), 'assets', 'img', 'test.png')

        name = self.create_new_course()[0]

        self.load_dashboard(
            name
        ).click_assets(
        ).click_upload(
        ).select_file(
            image_file
        ).click_upload_and_expect_saved(
        ).verify_image_file_by_name(
            'assets/img/test.png'
        ).click_edit_image(
            'assets/img/test.png'
        ).click_delete(
        ).confirm_delete(
        ).verify_no_image_file_by_name('assets/img/test.png')

    def test_add_and_edit_custom_tags(self):
        name = self.create_new_course()[0]
        self.load_dashboard(
            name
        ).click_add_unit(
        ).set_title(
            'First Unit'
        ).click_save(
        ).click_close(
        ).click_add_lesson(
        ).click_rich_text(
        ).set_rte_text(
            'Let\'s watch a video:\n'
        ).click_rte_add_custom_tag(
        ).set_rte_lightbox_field(
            'input[name=videoid]', '123'
        ).click_rte_save(
        ).doubleclick_rte_element(
            'gcb-youtube > img'
        ).ensure_rte_lightbox_field_has_value(
            'input[name=videoid]', '123'
        ).set_rte_lightbox_field(
            'input[name=videoid]', '321'
        ).click_rte_save(
        ).click_plain_text(
        ).ensure_objectives_textarea_contains(
            '<gcb-youtube videoid="321"></gcb-youtube>')

