import os
import types
from unittest.mock import patch, MagicMock

import pytest

from voxo.services.abstract_service import AbstractService
from voxo.service_factory import ServiceFactory


# --- Helpers ---

def _make_concrete_service(name: str) -> type:
    """Create a minimal concrete subclass of AbstractService with the given name."""
    return type(name, (AbstractService,), {
        "get_credentials_class": lambda self: None,
        "get_method": lambda self: "GET",
        "get_url_path": lambda self: "/test",
        "get_response_type": lambda self: dict,
    })


def _fake_listdir(filenames: list[str]):
    """Return a patched os.listdir that returns the given filenames."""
    def listdir(path):
        return filenames
    return listdir


def _fake_import_module(modules: dict[str, types.ModuleType]):
    """Return a patched importlib.import_module that looks up from a dict."""
    def import_module(name):
        if name in modules:
            return modules[name]
        raise ModuleNotFoundError(f"No module named '{name}'")
    return import_module


def _build_module(name: str, classes: list[type]) -> types.ModuleType:
    """Build a fake module containing the given classes."""
    mod = types.ModuleType(name)
    for cls in classes:
        setattr(mod, cls.__name__, cls)
    # AbstractService must be importable for issubclass checks during inspect
    mod.AbstractService = AbstractService
    return mod


# --- Tests ---

class TestServiceFactoryInit:

    @patch("voxo.service_factory.importlib.import_module")
    @patch("voxo.service_factory.os.listdir")
    def test_loads_single_service(self, mock_listdir, mock_import):
        FakeService = _make_concrete_service("FakeService")
        mod = _build_module("voxo.services.fake", [FakeService])

        mock_listdir.return_value = ["fake.py"]
        mock_import.side_effect = _fake_import_module({"voxo.services.fake": mod})

        factory = ServiceFactory()
        assert factory.get_service_class("FakeService") is FakeService

    @patch("voxo.service_factory.importlib.import_module")
    @patch("voxo.service_factory.os.listdir")
    def test_loads_multiple_services_from_multiple_files(self, mock_listdir, mock_import):
        ServiceA = _make_concrete_service("ServiceA")
        ServiceB = _make_concrete_service("ServiceB")

        mod_a = _build_module("voxo.services.a", [ServiceA])
        mod_b = _build_module("voxo.services.b", [ServiceB])

        mock_listdir.return_value = ["a.py", "b.py"]
        mock_import.side_effect = _fake_import_module({
            "voxo.services.a": mod_a,
            "voxo.services.b": mod_b,
        })

        factory = ServiceFactory()
        assert factory.get_service_class("ServiceA") is ServiceA
        assert factory.get_service_class("ServiceB") is ServiceB

    @patch("voxo.service_factory.importlib.import_module")
    @patch("voxo.service_factory.os.listdir")
    def test_loads_multiple_services_from_single_file(self, mock_listdir, mock_import):
        ServiceX = _make_concrete_service("ServiceX")
        ServiceY = _make_concrete_service("ServiceY")

        mod = _build_module("voxo.services.multi", [ServiceX, ServiceY])

        mock_listdir.return_value = ["multi.py"]
        mock_import.side_effect = _fake_import_module({"voxo.services.multi": mod})

        factory = ServiceFactory()
        assert factory.get_service_class("ServiceX") is ServiceX
        assert factory.get_service_class("ServiceY") is ServiceY


class TestSkipsNonServiceFiles:

    @patch("voxo.service_factory.importlib.import_module")
    @patch("voxo.service_factory.os.listdir")
    def test_skips_dunder_files(self, mock_listdir, mock_import):
        mock_listdir.return_value = ["__init__.py", "__pycache__"]
        mock_import.side_effect = AssertionError("should not be called")

        factory = ServiceFactory()
        assert factory._services == {}

    @patch("voxo.service_factory.importlib.import_module")
    @patch("voxo.service_factory.os.listdir")
    def test_skips_non_python_files(self, mock_listdir, mock_import):
        mock_listdir.return_value = ["README.md", "data.json", "notes.txt"]
        mock_import.side_effect = AssertionError("should not be called")

        factory = ServiceFactory()
        assert factory._services == {}

    @patch("voxo.service_factory.importlib.import_module")
    @patch("voxo.service_factory.os.listdir")
    def test_skips_underscore_prefixed_files(self, mock_listdir, mock_import):
        mock_listdir.return_value = ["_helpers.py", "_internal.py"]
        mock_import.side_effect = AssertionError("should not be called")

        factory = ServiceFactory()
        assert factory._services == {}


class TestSkipsNonServiceClasses:

    @patch("voxo.service_factory.importlib.import_module")
    @patch("voxo.service_factory.os.listdir")
    def test_skips_abstract_service_itself(self, mock_listdir, mock_import):
        mod = _build_module("voxo.services.base", [])
        # Module only has AbstractService from _build_module

        mock_listdir.return_value = ["base.py"]
        mock_import.side_effect = _fake_import_module({"voxo.services.base": mod})

        factory = ServiceFactory()
        assert "AbstractService" not in factory._services

    @patch("voxo.service_factory.importlib.import_module")
    @patch("voxo.service_factory.os.listdir")
    def test_skips_plain_classes(self, mock_listdir, mock_import):
        class NotAService:
            pass

        mod = _build_module("voxo.services.misc", [NotAService])

        mock_listdir.return_value = ["misc.py"]
        mock_import.side_effect = _fake_import_module({"voxo.services.misc": mod})

        factory = ServiceFactory()
        assert "NotAService" not in factory._services


class TestGetServiceClass:

    @patch("voxo.service_factory.importlib.import_module")
    @patch("voxo.service_factory.os.listdir")
    def test_returns_correct_class(self, mock_listdir, mock_import):
        MyService = _make_concrete_service("MyService")
        mod = _build_module("voxo.services.my", [MyService])

        mock_listdir.return_value = ["my.py"]
        mock_import.side_effect = _fake_import_module({"voxo.services.my": mod})

        factory = ServiceFactory()
        assert factory.get_service_class("MyService") is MyService

    @patch("voxo.service_factory.importlib.import_module")
    @patch("voxo.service_factory.os.listdir")
    def test_raises_lookup_error_for_unknown_service(self, mock_listdir, mock_import):
        mock_listdir.return_value = []

        factory = ServiceFactory()
        with pytest.raises(LookupError, match="Service 'DoesNotExist' not found"):
            factory.get_service_class("DoesNotExist")

    @patch("voxo.service_factory.importlib.import_module")
    @patch("voxo.service_factory.os.listdir")
    def test_name_is_case_sensitive(self, mock_listdir, mock_import):
        MyService = _make_concrete_service("MyService")
        mod = _build_module("voxo.services.my", [MyService])

        mock_listdir.return_value = ["my.py"]
        mock_import.side_effect = _fake_import_module({"voxo.services.my": mod})

        factory = ServiceFactory()
        with pytest.raises(LookupError):
            factory.get_service_class("myservice")
        with pytest.raises(LookupError):
            factory.get_service_class("MYSERVICE")


class TestCachingBehavior:

    @patch("voxo.service_factory.importlib.import_module")
    @patch("voxo.service_factory.os.listdir")
    def test_does_not_rescan_on_get(self, mock_listdir, mock_import):
        ServiceA = _make_concrete_service("ServiceA")
        mod = _build_module("voxo.services.a", [ServiceA])

        mock_listdir.return_value = ["a.py"]
        mock_import.side_effect = _fake_import_module({"voxo.services.a": mod})

        factory = ServiceFactory()

        # Reset mocks after init
        mock_listdir.reset_mock()
        mock_import.reset_mock()

        # Multiple lookups should not trigger rescan
        factory.get_service_class("ServiceA")
        factory.get_service_class("ServiceA")
        factory.get_service_class("ServiceA")

        mock_listdir.assert_not_called()
        mock_import.assert_not_called()

    @patch("voxo.service_factory.importlib.import_module")
    @patch("voxo.service_factory.os.listdir")
    def test_scans_exactly_once_on_init(self, mock_listdir, mock_import):
        mock_listdir.return_value = ["a.py", "b.py"]
        mock_import.return_value = types.ModuleType("empty")

        ServiceFactory()

        mock_listdir.assert_called_once()


class TestLastServiceWinsOnNameCollision:

    @patch("voxo.service_factory.importlib.import_module")
    @patch("voxo.service_factory.os.listdir")
    def test_duplicate_name_across_files_last_wins(self, mock_listdir, mock_import):
        """If two files define a service with the same class name, the last one scanned wins."""
        ServiceDup1 = _make_concrete_service("Dup")
        ServiceDup2 = _make_concrete_service("Dup")

        mod_a = _build_module("voxo.services.a", [ServiceDup1])
        mod_b = _build_module("voxo.services.b", [ServiceDup2])

        # os.listdir order determines scan order
        mock_listdir.return_value = ["a.py", "b.py"]
        mock_import.side_effect = _fake_import_module({
            "voxo.services.a": mod_a,
            "voxo.services.b": mod_b,
        })

        factory = ServiceFactory()
        result = factory.get_service_class("Dup")
        # Last file scanned (b.py) should win
        assert result is ServiceDup2


class TestEmptyServicesDir:

    @patch("voxo.service_factory.importlib.import_module")
    @patch("voxo.service_factory.os.listdir")
    def test_empty_directory(self, mock_listdir, mock_import):
        mock_listdir.return_value = []

        factory = ServiceFactory()
        assert factory._services == {}

    @patch("voxo.service_factory.importlib.import_module")
    @patch("voxo.service_factory.os.listdir")
    def test_only_non_service_files(self, mock_listdir, mock_import):
        mock_listdir.return_value = ["__init__.py", "README.md", "_utils.py"]

        factory = ServiceFactory()
        assert factory._services == {}


class TestIntegration:
    """Test against the real services directory without mocks."""

    def test_discovers_call_blocking_service(self):
        factory = ServiceFactory()
        from voxo.services.call_blocking import CallBlocking
        assert factory.get_service_class("CallBlocking") is CallBlocking

    def test_raises_for_nonexistent_service(self):
        factory = ServiceFactory()
        with pytest.raises(LookupError):
            factory.get_service_class("NonExistentService")
