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
        mod = _build_module("voxo_api.services.fake", [FakeService])

        mock_listdir.return_value = ["fake"]

        with _with_modules(**{"voxo_api.services.fake": mod}):
            factory = ServiceFactory()

        assert factory.get_service_class("FakeService") is FakeService

    @patch("os.path.isdir", return_value=True)
    @patch("voxo_api.service_factory.os.listdir")
    def test_loads_multiple_services_from_multiple_directories(self, mock_listdir, _mock_isdir):
        ServiceA = _make_concrete_service("ServiceA")
        ServiceB = _make_concrete_service("ServiceB")

        mod_a = _build_module("voxo_api.services.a", [ServiceA])
        mod_b = _build_module("voxo_api.services.b", [ServiceB])

        mock_listdir.return_value = ["a", "b"]

        with _with_modules(**{"voxo_api.services.a": mod_a, "voxo_api.services.b": mod_b}):
            factory = ServiceFactory()

        assert factory.get_service_class("ServiceA") is ServiceA
        assert factory.get_service_class("ServiceB") is ServiceB

    @patch("os.path.isdir", return_value=True)
    @patch("voxo_api.service_factory.os.listdir")
    def test_loads_multiple_services_from_single_package(self, mock_listdir, _mock_isdir):
        ServiceX = _make_concrete_service("ServiceX")
        ServiceY = _make_concrete_service("ServiceY")

        mod = _build_module("voxo_api.services.multi", [ServiceX, ServiceY])

        mock_listdir.return_value = ["multi"]

        with _with_modules(**{"voxo_api.services.multi": mod}):
            factory = ServiceFactory()

        assert factory.get_service_class("ServiceX") is ServiceX
        assert factory.get_service_class("ServiceY") is ServiceY


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
        mod = _build_module("voxo_api.services.base", [])
        mock_listdir.return_value = ["base"]

        with _with_modules(**{"voxo_api.services.base": mod}):
            factory = ServiceFactory()

        assert "AbstractService" not in factory._services

    @patch("os.path.isdir", return_value=True)
    @patch("voxo_api.service_factory.os.listdir")
    def test_skips_plain_classes(self, mock_listdir, _mock_isdir):
        class NotAService:
            pass

        mod = _build_module("voxo_api.services.misc", [NotAService])
        mock_listdir.return_value = ["misc"]

        with _with_modules(**{"voxo_api.services.misc": mod}):
            factory = ServiceFactory()

        assert "NotAService" not in factory._services


class TestGetServiceClass:

    @patch("os.path.isdir", return_value=True)
    @patch("voxo_api.service_factory.os.listdir")
    def test_returns_correct_class(self, mock_listdir, _mock_isdir):
        MyService = _make_concrete_service("MyService")
        mod = _build_module("voxo_api.services.my", [MyService])

        mock_listdir.return_value = ["my"]

        with _with_modules(**{"voxo_api.services.my": mod}):
            factory = ServiceFactory()

        assert factory.get_service_class("MyService") is MyService

    @patch("voxo_api.service_factory.os.listdir")
    def test_raises_lookup_error_for_unknown_service(self, mock_listdir):
        mock_listdir.return_value = []

        factory = ServiceFactory()
        with pytest.raises(LookupError, match="Service 'DoesNotExist' not found"):
            factory.get_service_class("DoesNotExist")

    @patch("os.path.isdir", return_value=True)
    @patch("voxo_api.service_factory.os.listdir")
    def test_name_is_case_sensitive(self, mock_listdir, _mock_isdir):
        MyService = _make_concrete_service("MyService")
        mod = _build_module("voxo_api.services.my", [MyService])

        mock_listdir.return_value = ["my"]

        with _with_modules(**{"voxo_api.services.my": mod}):
            factory = ServiceFactory()

        with pytest.raises(LookupError):
            factory.get_service_class("myservice")
        with pytest.raises(LookupError):
            factory.get_service_class("MYSERVICE")


class TestCachingBehavior:

    @patch("os.path.isdir", return_value=True)
    @patch("voxo_api.service_factory.os.listdir")
    def test_does_not_rescan_on_get(self, mock_listdir, _mock_isdir):
        ServiceA = _make_concrete_service("ServiceA")
        mod = _build_module("voxo_api.services.a", [ServiceA])

        mock_listdir.return_value = ["a"]

        with _with_modules(**{"voxo_api.services.a": mod}):
            factory = ServiceFactory()

        mock_listdir.reset_mock()

        factory.get_service_class("ServiceA")
        factory.get_service_class("ServiceA")
        factory.get_service_class("ServiceA")

        mock_listdir.assert_not_called()

    @patch("os.path.isdir", return_value=False)
    @patch("voxo_api.service_factory.os.listdir")
    def test_scans_exactly_once_on_init(self, mock_listdir, _mock_isdir):
        mock_listdir.return_value = ["a", "b"]

        ServiceFactory()

        mock_listdir.assert_called_once()


class TestLastServiceWinsOnNameCollision:

    @patch("os.path.isdir", return_value=True)
    @patch("voxo_api.service_factory.os.listdir")
    def test_duplicate_name_across_directories_last_wins(self, mock_listdir, _mock_isdir):
        """If two packages define a service with the same class name, the last one scanned wins."""
        ServiceDup1 = _make_concrete_service("Dup")
        ServiceDup2 = _make_concrete_service("Dup")

        mod_a = _build_module("voxo_api.services.a", [ServiceDup1])
        mod_b = _build_module("voxo_api.services.b", [ServiceDup2])

        mock_listdir.return_value = ["a", "b"]

        with _with_modules(**{"voxo_api.services.a": mod_a, "voxo_api.services.b": mod_b}):
            factory = ServiceFactory()

        result = factory.get_service_class("Dup")
        assert result is ServiceDup2


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
        from voxo_api.services.call_blocking import CallBlocking
        assert factory.get_service_class("CallBlocking") is CallBlocking

    def test_raises_for_nonexistent_service(self):
        factory = ServiceFactory()
        with pytest.raises(LookupError):
            factory.get_service_class("NonExistentService")
