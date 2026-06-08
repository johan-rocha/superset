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

import pytest

from superset.utils import version as version_utils


@pytest.mark.parametrize(
    "branch, sha, expected_label",
    [
        ("feature/version-label", "abcdef1234567890", "feature/version-label@abcdef12"),
        (None, "abcdef1234567890", "@abcdef12"),
        ("feature/version-label", None, "feature/version-label"),
        (None, None, ""),
    ],
)
def test_get_dev_env_label_formats_branch_and_sha(
    monkeypatch: pytest.MonkeyPatch,
    branch: str | None,
    sha: str | None,
    expected_label: str,
) -> None:
    for env_var in ("GITHUB_HEAD_REF", "GITHUB_REF_NAME", "GITHUB_SHA"):
        monkeypatch.delenv(env_var, raising=False)

    monkeypatch.setattr(version_utils, "_get_local_branch", lambda: branch)
    monkeypatch.setattr(version_utils, "_get_local_sha", lambda: sha)

    assert version_utils.get_dev_env_label() == expected_label


def test_get_dev_env_label_prefers_github_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GITHUB_HEAD_REF", "pull-request-branch")
    monkeypatch.setenv("GITHUB_REF_NAME", "fallback-branch")
    monkeypatch.setenv("GITHUB_SHA", "1234567890abcdef")
    monkeypatch.setattr(version_utils, "_get_local_branch", lambda: "local-branch")
    monkeypatch.setattr(version_utils, "_get_local_sha", lambda: "local-sha")

    assert version_utils.get_dev_env_label() == "pull-request-branch@12345678"
