import os
import sys
import traceback

from .__init__ import EXECUTABLE_NAME


def main(init_params: dict = None):
    cwd = process_working_directory()
    if init_params is None:
        init_params = {}
    try:
        from lcli.app import App

        project_root_path = os.path.realpath(os.path.dirname(__file__))
        app = App(
            app_path=project_root_path,
            executable_name=EXECUTABLE_NAME,
            init_params=init_params,
            cwd=cwd,
        )
        app.logger.info("start")
        app.run()
        app.logger.info("end")
    except ModuleNotFoundError as error:
        print("\n")
        print("Module dependencies are not met: " + str(error))
        print(
            "Please install all requirements defined in requirements.txt of "
            + EXECUTABLE_NAME
            + " before running the application."
        )
        print("\n")

    except Exception as error:
        print("Unexpected error: " + str(error))
        print(traceback.format_exc())
    except KeyboardInterrupt:
        print("\n")
        print("Execution stopped by keyboard interrupt signal.")
        print("\n")


def process_working_directory():
    cwd = os.getcwd()

    found_cwd = False
    to_remove_args = []

    for param in sys.argv:
        if found_cwd:
            to_remove_args.append(param)
            cwd = param
            break
        if param == "--cwd":
            to_remove_args.append(param)
            found_cwd = True

    for flag in to_remove_args:
        sys.argv.remove(flag)

    sys.path.append(cwd)
    return cwd


if __name__ == "__main__":
    main({})
