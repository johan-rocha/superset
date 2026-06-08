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

import sys
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any, Iterator


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class _FeatureFlagManager:
    def is_feature_enabled(self, _feature: str) -> bool:
        return False


class _MachineAuthProvider:
    def authenticate_browser_context(self, *args: Any, **_kwargs: Any) -> Any:
        return args[0] if args else None

    def authenticate_webdriver(self, *args: Any, **_kwargs: Any) -> Any:
        return args[0] if args else None


@contextmanager
def _log_context(_name: str) -> Iterator[None]:
    yield


superset_stub = ModuleType("superset")
superset_stub.__file__ = str(PROJECT_ROOT / "superset" / "__init__.py")
superset_stub.__path__ = [str(PROJECT_ROOT / "superset")]
superset_stub.db = SimpleNamespace()
superset_stub.feature_flag_manager = _FeatureFlagManager()
superset_stub.thumbnail_cache = SimpleNamespace(
    get=lambda *_args: None,
    set=lambda *_args: None,
)
sys.modules["superset"] = superset_stub

extensions_stub = ModuleType("superset.extensions")
extensions_stub.event_logger = SimpleNamespace(log_context=_log_context)
extensions_stub.machine_auth_provider_factory = SimpleNamespace(
    instance=_MachineAuthProvider(),
)
sys.modules["superset.extensions"] = extensions_stub

flask_appbuilder_stub = ModuleType("flask_appbuilder")
fab_security_stub = ModuleType("flask_appbuilder.security")
fab_sqla_stub = ModuleType("flask_appbuilder.security.sqla")
fab_models_stub = ModuleType("flask_appbuilder.security.sqla.models")
fab_models_stub.User = type("User", (), {})
sys.modules["flask_appbuilder"] = flask_appbuilder_stub
sys.modules["flask_appbuilder.security"] = fab_security_stub
sys.modules["flask_appbuilder.security.sqla"] = fab_sqla_stub
sys.modules["flask_appbuilder.security.sqla.models"] = fab_models_stub


def _clean(value: str, *_args: Any, **_kwargs: Any) -> str:
    return value


nh3_stub = ModuleType("nh3")
nh3_stub.clean = _clean
sys.modules["nh3"] = nh3_stub

jwt_stub = ModuleType("jwt")
jwt_stub.encode = lambda *_args, **_kwargs: ""
jwt_stub.decode = lambda *_args, **_kwargs: {}
sys.modules["jwt"] = jwt_stub

cryptography_stub = ModuleType("cryptography")
hazmat_stub = ModuleType("cryptography.hazmat")
backends_stub = ModuleType("cryptography.hazmat.backends")
backends_stub.default_backend = lambda: None
x509_stub = ModuleType("cryptography.x509")
x509_stub.Certificate = object
x509_stub.load_pem_x509_certificate = lambda *_args, **_kwargs: None
sys.modules["cryptography"] = cryptography_stub
sys.modules["cryptography.hazmat"] = hazmat_stub
sys.modules["cryptography.hazmat.backends"] = backends_stub
sys.modules["cryptography.x509"] = x509_stub

webdriver_stub = ModuleType("superset.utils.webdriver")
webdriver_stub.PLAYWRIGHT_AVAILABLE = False
webdriver_stub.PLAYWRIGHT_INSTALL_MESSAGE = (
    "Playwright module not loaded in PTOSS tests"
)
webdriver_stub.ChartStandaloneMode = SimpleNamespace(
    HIDE_NAV=SimpleNamespace(value="hide_nav"),
)
webdriver_stub.DashboardStandaloneMode = SimpleNamespace(
    REPORT=SimpleNamespace(value="report"),
)
webdriver_stub.WebDriver = object
webdriver_stub.WebDriverPlaywright = object
webdriver_stub.WebDriverSelenium = object
webdriver_stub.WindowSize = tuple[int, int]
sys.modules["superset.utils.webdriver"] = webdriver_stub
