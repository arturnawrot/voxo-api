import types
from unittest.mock import patch

import pytest

from voxo_api.services.abstract_service import AbstractService
from voxo_api.service_factory import ServiceFactory


# --- Helpers ---

def _make_concrete_service(name: str) -> type:
    return type(name, (AbstractService,), {
        "get_credentials_class": lambda self: None,
        "get_method": lambda self: "GET",
        "get_url_path": lambda self: "/test",
        "get_response_type": lambda self: dict,
    })


def _build_module(name: str, classes: list[type]) -> types.ModuleType:
    mod = types.ModuleType(name)
    for cls in classes:
        setattr(mod, cls.__name__, cls)
    mod.AbstractService = AbstractService
    return mod


def _with_modules(**modules):
    """Context manager that temporarily injects modules into sys.modules."""
    return patch.dict("sys.modules", modules)


# --- Tests ---

class TestServiceFactoryInit:

    @patch("os.path.isdir", return_value=True)
    @patch("voxo_api.service_factory.os.listdir")
    def test_loads_single_service(self, mock_listdir, _mock_isdir):
        FakeService = _make_concrete_service("FakeService")
        mod = _build_module("voxo_api.services.v1.fake", [FakeService])

        mock_listdir.side_effect = [["v1"], ["fake"], []]

        with _with_modules(**{"voxo_api.services.v1.fake": mod}):
            factory = ServiceFactory()

        assert factory.get_version_services("v1")["FakeService"] is FakeService

    @patch("os.path.isdir", return_value=True)
    @patch("voxo_api.service_factory.os.listdir")
    def test_loads_multiple_services_from_multiple_directories(self, mock_listdir, _mock_isdir):
        ServiceA = _make_concrete_service("ServiceA")
        ServiceB = _make_concrete_service("ServiceB")

        mod_a = _build_module("voxo_api.services.v1.a", [ServiceA])
        mod_b = _build_module("voxo_api.services.v1.b", [ServiceB])

        mock_listdir.side_effect = [["v1"], ["a", "b"], [], []]

        with _with_modules(**{"voxo_api.services.v1.a": mod_a, "voxo_api.services.v1.b": mod_b}):
            factory = ServiceFactory()

        assert factory.get_version_services("v1")["ServiceA"] is ServiceA
        assert factory.get_version_services("v1")["ServiceB"] is ServiceB

    @patch("os.path.isdir", return_value=True)
    @patch("voxo_api.service_factory.os.listdir")
    def test_loads_multiple_services_from_single_package(self, mock_listdir, _mock_isdir):
        ServiceX = _make_concrete_service("ServiceX")
        ServiceY = _make_concrete_service("ServiceY")

        mod = _build_module("voxo_api.services.v1.multi", [ServiceX, ServiceY])

        mock_listdir.side_effect = [["v1"], ["multi"], []]

        with _with_modules(**{"voxo_api.services.v1.multi": mod}):
            factory = ServiceFactory()

        assert factory.get_version_services("v1")["ServiceX"] is ServiceX
        assert factory.get_version_services("v1")["ServiceY"] is ServiceY

    @patch("os.path.isdir", return_value=True)
    @patch("voxo_api.service_factory.os.listdir")
    def test_loads_services_from_multiple_versions(self, mock_listdir, _mock_isdir):
        ServiceA = _make_concrete_service("ServiceA")
        ServiceB = _make_concrete_service("ServiceB")

        mod_v1 = _build_module("voxo_api.services.v1.a", [ServiceA])
        mod_v2 = _build_module("voxo_api.services.v2.b", [ServiceB])

        mock_listdir.side_effect = [["v1", "v2"], ["a"], [], ["b"], []]

        with _with_modules(**{"voxo_api.services.v1.a": mod_v1, "voxo_api.services.v2.b": mod_v2}):
            factory = ServiceFactory()

        assert factory.get_version_services("v1")["ServiceA"] is ServiceA
        assert factory.get_version_services("v2")["ServiceB"] is ServiceB


class TestSkipsNonServiceEntries:

    @patch("voxo_api.service_factory.os.listdir")
    def test_skips_dunder_directories(self, mock_listdir):
        mock_listdir.return_value = ["__init__", "__pycache__"]

        factory = ServiceFactory()
        assert factory._services == {}

    @patch("os.path.isdir", return_value=False)
    @patch("voxo_api.service_factory.os.listdir")
    def test_skips_non_directory_entries(self, mock_listdir, _mock_isdir):
        mock_listdir.return_value = ["README.md", "data.json", "notes.txt"]

        factory = ServiceFactory()
        assert factory._services == {}

    @patch("voxo_api.service_factory.os.listdir")
    def test_skips_underscore_prefixed_directories(self, mock_listdir):
        mock_listdir.return_value = ["_helpers", "_internal"]

        factory = ServiceFactory()
        assert factory._services == {}


class TestSkipsNonServiceClasses:

    @patch("os.path.isdir", return_value=True)
    @patch("voxo_api.service_factory.os.listdir")
    def test_skips_abstract_service_itself(self, mock_listdir, _mock_isdir):
        mod = _build_module("voxo_api.services.v1.base", [])
        mock_listdir.side_effect = [["v1"], ["base"], []]

        with _with_modules(**{"voxo_api.services.v1.base": mod}):
            factory = ServiceFactory()

        assert "AbstractService" not in factory._services.get("v1", {})

    @patch("os.path.isdir", return_value=True)
    @patch("voxo_api.service_factory.os.listdir")
    def test_skips_plain_classes(self, mock_listdir, _mock_isdir):
        class NotAService:
            pass

        mod = _build_module("voxo_api.services.v1.misc", [NotAService])
        mock_listdir.side_effect = [["v1"], ["misc"], []]

        with _with_modules(**{"voxo_api.services.v1.misc": mod}):
            factory = ServiceFactory()

        assert "NotAService" not in factory._services.get("v1", {})


class TestGetVersionServices:

    @patch("os.path.isdir", return_value=True)
    @patch("voxo_api.service_factory.os.listdir")
    def test_returns_correct_class(self, mock_listdir, _mock_isdir):
        MyService = _make_concrete_service("MyService")
        mod = _build_module("voxo_api.services.v1.my", [MyService])

        mock_listdir.side_effect = [["v1"], ["my"], []]

        with _with_modules(**{"voxo_api.services.v1.my": mod}):
            factory = ServiceFactory()

        assert factory.get_version_services("v1")["MyService"] is MyService

    @patch("voxo_api.service_factory.os.listdir")
    def test_raises_lookup_error_for_unknown_version(self, mock_listdir):
        mock_listdir.return_value = []

        factory = ServiceFactory()
        with pytest.raises(LookupError, match="Version 'v99' not found"):
            factory.get_version_services("v99")

    @patch("os.path.isdir", return_value=True)
    @patch("voxo_api.service_factory.os.listdir")
    def test_name_is_case_sensitive(self, mock_listdir, _mock_isdir):
        MyService = _make_concrete_service("MyService")
        mod = _build_module("voxo_api.services.v1.my", [MyService])

        mock_listdir.side_effect = [["v1"], ["my"], []]

        with _with_modules(**{"voxo_api.services.v1.my": mod}):
            factory = ServiceFactory()

        services = factory.get_version_services("v1")
        assert "myservice" not in services
        assert "MYSERVICE" not in services


class TestCachingBehavior:

    @patch("os.path.isdir", return_value=True)
    @patch("voxo_api.service_factory.os.listdir")
    def test_does_not_rescan_on_get(self, mock_listdir, _mock_isdir):
        ServiceA = _make_concrete_service("ServiceA")
        mod = _build_module("voxo_api.services.v1.a", [ServiceA])

        mock_listdir.side_effect = [["v1"], ["a"], []]

        with _with_modules(**{"voxo_api.services.v1.a": mod}):
            factory = ServiceFactory()

        mock_listdir.reset_mock()

        factory.get_version_services("v1")
        factory.get_version_services("v1")
        factory.get_version_services("v1")

        mock_listdir.assert_not_called()

    @patch("os.path.isdir", return_value=False)
    @patch("voxo_api.service_factory.os.listdir")
    def test_scans_exactly_once_on_init(self, mock_listdir, _mock_isdir):
        mock_listdir.return_value = ["a", "b"]

        ServiceFactory()

        mock_listdir.assert_called_once()


class TestSameNameAcrossVersions:

    @patch("os.path.isdir", return_value=True)
    @patch("voxo_api.service_factory.os.listdir")
    def test_same_name_in_different_versions_are_independent(self, mock_listdir, _mock_isdir):
        ServiceV1 = _make_concrete_service("MyService")
        ServiceV2 = _make_concrete_service("MyService")

        mod_v1 = _build_module("voxo_api.services.v1.svc", [ServiceV1])
        mod_v2 = _build_module("voxo_api.services.v2.svc", [ServiceV2])

        mock_listdir.side_effect = [["v1", "v2"], ["svc"], [], ["svc"], []]

        with _with_modules(**{"voxo_api.services.v1.svc": mod_v1, "voxo_api.services.v2.svc": mod_v2}):
            factory = ServiceFactory()

        assert factory.get_version_services("v1")["MyService"] is ServiceV1
        assert factory.get_version_services("v2")["MyService"] is ServiceV2


class TestEmptyServicesDir:

    @patch("voxo_api.service_factory.os.listdir")
    def test_empty_directory(self, mock_listdir):
        mock_listdir.return_value = []

        factory = ServiceFactory()
        assert factory._services == {}

    @patch("voxo_api.service_factory.os.listdir")
    def test_only_non_service_entries(self, mock_listdir):
        mock_listdir.return_value = ["__init__", "README.md", "_utils"]

        factory = ServiceFactory()
        assert factory._services == {}


class TestIntegration:
    """Test against the real services directory without mocks."""

    def test_discovers_call_blocking_service(self):
        factory = ServiceFactory()
        from voxo_api.services.v1.call_blocking import CallBlocking
        assert factory.get_version_services("v1")["CallBlocking"] is CallBlocking

    def test_raises_for_nonexistent_version(self):
        factory = ServiceFactory()
        with pytest.raises(LookupError):
            factory.get_version_services("v99")
