import importlib
import inspect
import os
from voxo_api.services.abstract_service import AbstractService


class ServiceFactory:

    def __init__(self) -> None:
        self._services: dict[str, dict[str, type]] = {}
        self._load_services()

    def _load_services(self) -> None:
        services_dir = os.path.join(os.path.dirname(__file__), 'services')
        for entry in os.listdir(services_dir):
            if entry.startswith('_'):
                continue
            entry_path = os.path.join(services_dir, entry)
            if not os.path.isdir(entry_path):
                continue
            version_services: dict[str, type] = {}
            self._scan_dir(entry_path, f'voxo_api.services.{entry}', version_services)
            self._services[entry] = version_services

    def _scan_dir(self, directory: str, package: str, services: dict[str, type]) -> None:
        for entry in os.listdir(directory):
            entry_path = os.path.join(directory, entry)
            if not os.path.isdir(entry_path) or entry.startswith('_'):
                continue
            module_name = f'{package}.{entry}'
            module = importlib.import_module(module_name)
            for _, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, AbstractService) and obj is not AbstractService:
                    services[obj.__name__] = obj
            self._scan_dir(entry_path, module_name, services)

    def get_version_services(self, version: str) -> dict[str, type]:
        try:
            return self._services[version]
        except KeyError:
            raise LookupError(f"Version '{version}' not found")
