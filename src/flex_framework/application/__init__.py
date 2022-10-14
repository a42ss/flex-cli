from ..api.proxy import ProxyInterface, ProxyContainer
from ..logger import Logger, ProfilerLoggerProxy
from ..object_manager import Factory as ObjectManagerFactory, ObjectManager


class ApplicationBootstrap:
    _profiler: Logger | ProxyInterface
    _current_working_dir: str
    _arguments: dict
    _object_manager: ObjectManager

    def __init__(self, object_manager_factory: ObjectManagerFactory, current_working_dir: str, arguments: dict):
        self._object_manager = object_manager_factory.create(arguments)
        self._current_working_dir = current_working_dir
        self._arguments = arguments
        self._profiler = ProxyInterface[ProxyContainer[Logger], Logger](self._object_manager, ProfilerLoggerProxy)

    @staticmethod
    def create(current_working_dir: str, params=None, object_manager_factory: ObjectManagerFactory = None):
        if params is None:
            params = {}
        params["current_working_dir"] = current_working_dir

        if object_manager_factory is None:
            object_manager_factory = ObjectManagerFactory()

        return ApplicationBootstrap(object_manager_factory, current_working_dir, params)

    def create_application(self, instance):
        return self._object_manager.provide(instance)

    def run(self, application):
        self._profiler.info("Start")
        try:
            try:
                try:
                    self.init_error_handler()
                    result = application.launch()
                    result.send_response(lambda: self._profiler.info("Stop"))
                except Exception as exception:
                    application.catch_exception(self, exception)
            except Exception as unhandled_exception:
                application.terminate(unhandled_exception)
        except Exception as unhandled_exception:
            self.terminate(unhandled_exception)

    def init_error_handler(self):
        pass

    def terminate(self, exception: Exception):
        print("Unhandled exception: " + str(exception))
        exit(1)
