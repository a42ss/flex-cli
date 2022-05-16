************
Installation
************

Install the package (or add it to your ``requirements.txt`` file):

.. code:: console

    # From source
    $ invoke install

    # or
    # install in user space
    $ ./install -u

    #install it globally
    $ ./install

    # From repository
    $ pip install lcli

    # or simply install it using python in root of the repository
    $ python -m pip install -r requirements.txt
    $ python -m pip install . --user

.. note::
    Note that form this point on there are two options to use lcli

    * Configure the build in cli to support your custom cli commands, and expose better API for the existing commands. See :doc:`configuring`
    * Build your own cli application by extending python package as in example bellow

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