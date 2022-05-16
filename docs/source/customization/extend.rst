
******************************
Build your own cli application
******************************

.. contents:: Table of Contents

Extend lcli object
==================

Simple example
--------------

.. code:: python

    # Build your own cli application
    import os
    from lcli.app import App

    class YourOwnApp(App):
        pass

    def main():
        try:
            project_root_path = os.path.realpath(os.path.dirname(__file__))
            app = YourOwnApp(app_path=project_root_path)
            app.run()
        except Exception as error:
            # process errors


    if __name__ == '__main__':
        main()


.. raw:: html
   :file: _static/analytics.html
