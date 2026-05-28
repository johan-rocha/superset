# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from superset.tasks import utils as task_utils
from superset.utils.core import parse_js_uri_path_item, split, user_label
from superset.utils.oauth2 import check_for_oauth2
from superset.utils.screenshots import ScreenshotCachePayload, StatusValues


def test_get_current_user_mcdc_user_presence_decision(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    active_user = SimpleNamespace(username="admin", is_anonymous=False)

    monkeypatch.setattr(task_utils, "g", SimpleNamespace())
    assert task_utils.get_current_user() is None

    monkeypatch.setattr(task_utils, "g", SimpleNamespace(user=None))
    assert task_utils.get_current_user() is None

    monkeypatch.setattr(task_utils, "g", SimpleNamespace(user=active_user))
    assert task_utils.get_current_user() == "admin"


def test_get_current_user_mcdc_anonymous_user_decision(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    active_user = SimpleNamespace(username="admin", is_anonymous=False)
    anonymous_user = SimpleNamespace(username="anonymous", is_anonymous=True)

    monkeypatch.setattr(task_utils, "g", SimpleNamespace(user=active_user))
    assert task_utils.get_current_user() == "admin"

    monkeypatch.setattr(task_utils, "g", SimpleNamespace(user=anonymous_user))
    assert task_utils.get_current_user() is None


def test_parse_js_uri_path_item_mcdc_eval_undefined_decision() -> None:
    assert parse_js_uri_path_item("undefined", eval_undefined=True) is None
    assert parse_js_uri_path_item("undefined", eval_undefined=False) == "undefined"
    assert parse_js_uri_path_item("dashboard", eval_undefined=True) == "dashboard"


def test_parse_js_uri_path_item_mcdc_unquote_decision() -> None:
    assert parse_js_uri_path_item("sales%2Fnorth", unquote=True) == "sales/north"
    assert parse_js_uri_path_item("sales%2Fnorth", unquote=False) == "sales%2Fnorth"
    assert parse_js_uri_path_item(None, unquote=True) is None


def test_user_label_mcdc_full_name_decision() -> None:
    assert (
        user_label(SimpleNamespace(first_name="Ada", last_name="Lovelace"))
        == "Ada Lovelace"
    )
    assert (
        user_label(SimpleNamespace(first_name="Ada", last_name="", username="ada"))
        == "ada"
    )
    assert (
        user_label(SimpleNamespace(first_name="", last_name="Lovelace", username="ada"))
        == "ada"
    )
    assert user_label(None) is None


def test_split_mcdc_delimiter_decision() -> None:
    assert list(split("a,b", delimiter=",")) == ["a", "b"]
    assert list(split("func(a,b),c", delimiter=",")) == ["func(a,b)", "c"]
    assert list(split('"a,b",c', delimiter=",")) == ['"a,b"', "c"]
    assert list(split("abc", delimiter=",")) == ["abc"]


@pytest.mark.parametrize(
    "enabled,needs_oauth2,expected_start",
    [
        (True, True, True),
        (False, True, False),
        (True, False, False),
    ],
)
def test_check_for_oauth2_mcdc_decision(
    enabled: bool,
    needs_oauth2: bool,
    expected_start: bool,
) -> None:
    database = MagicMock()
    database.is_oauth2_enabled.return_value = enabled
    database.db_engine_spec.needs_oauth2.return_value = needs_oauth2

    with pytest.raises(RuntimeError, match="query failed"):
        with check_for_oauth2(database):
            raise RuntimeError("query failed")

    assert database.db_engine_spec.start_oauth2_dance.called is expected_start


def _screenshot_payload(
    status: StatusValues,
    image: bytes | None = b"image",
    error_expired: bool = False,
    computing_stale: bool = False,
) -> ScreenshotCachePayload:
    payload = ScreenshotCachePayload(image=image, status=status)
    payload.status = status
    payload.is_error_cache_ttl_expired = (  # type: ignore[method-assign]
        lambda: error_expired
    )
    payload.is_computing_stale = lambda: computing_stale  # type: ignore[method-assign]
    return payload


def test_screenshot_payload_should_trigger_task_mcdc_decision() -> None:
    baseline = _screenshot_payload(StatusValues.UPDATED, image=b"image")
    assert baseline.should_trigger_task() is False
    assert baseline.should_trigger_task(force=True) is True

    assert _screenshot_payload(StatusValues.PENDING).should_trigger_task() is True
    assert (
        _screenshot_payload(
            StatusValues.ERROR,
            error_expired=True,
        ).should_trigger_task()
        is True
    )
    assert (
        _screenshot_payload(
            StatusValues.ERROR,
            error_expired=False,
        ).should_trigger_task()
        is False
    )
    assert (
        _screenshot_payload(
            StatusValues.COMPUTING,
            computing_stale=True,
        ).should_trigger_task()
        is True
    )
    assert (
        _screenshot_payload(
            StatusValues.COMPUTING,
            computing_stale=False,
        ).should_trigger_task()
        is False
    )
    assert _screenshot_payload(StatusValues.UPDATED, image=None).should_trigger_task()
