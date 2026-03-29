import importlib
import inspect
import os
from voxo_api.services.abstract_service import AbstractService


class ServiceFactory:

    def __init__(self) -> None:
        self._services: dict[str, type] = {}
        self._load_services()

    def _load_services(self) -> None:
        services_dir = os.path.join(os.path.dirname(__file__), 'services')

        for entry in os.listdir(services_dir):
            entry_path = os.path.join(services_dir, entry)
            if os.path.isdir(entry_path) and not entry.startswith('_'):
                module_name = f'voxo_api.services.{entry}'
                module = importlib.import_module(module_name)
                for _, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, AbstractService) and obj is not AbstractService:
                        self._services[obj.__name__] = obj

    def get_service_class(self, service_name: str) -> type:
        try:
            return self._services[service_name]
        except KeyError:
            raise LookupError(f"Service '{service_name}' not found")
