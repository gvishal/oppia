# Copyright 2016 The Oppia Authors. All Rights Reserved.
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

"""Performance tests for the library page."""

from core.tests.performance_tests import base
from core.tests.performance_tests import test_config


class LibraryPagePerformanceTest(base.TestBase):
    """Performance tests for the library page."""
    PAGE_KEY = test_config.LIBRARY_PAGE_KEY

    def setUp(self):
        super(LibraryPagePerformanceTest, self).setUp()

        page_config = test_config.TEST_DATA[self.PAGE_KEY]
        self._set_test_limits(page_config)

        self._load_page_to_cache_server_resources()

    def test_page_size_under_specified_limit(self):
        self._test_total_page_size()

    def test_page_size_under_specified_limit_for_cached_session(self):
        self._test_total_page_size_for_cached_session()

    def test_page_loads_under_specified_limit(self):
        self._test_page_load_time()

    def test_page_loads_under_specified_limit_cached_session(self):
        self._test_page_load_time_for_cached_session()
