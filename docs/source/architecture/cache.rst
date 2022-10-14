
*******************
Cache
*******************

Configuration cache
===================

For performance reason the configuration tree used by flex console needs to be cached as this is rarely change once put in place.

Because each working directories has each commands tree generated, the cache needs to be build for the closest non empty configuration group available in the configuration precedence list (CWD) -> (USR) -> (SYS).

The cache is stored by default in the (USR) level. with the following structure, with fallback from the last to the top.

User configuration locations (USR)
----------------------------------

.. code:: console

    - $HOME/cache/flex-cli/sys
    - $HOME/cache/flex-cli/usr/$USER
    - $HOME/cache/flex-cli/$CWD

Current working directory (CWD)
-------------------------------

Additionally the (CWD) cache location from home directory could be redirected to the current working directory itself.

.. code:: yaml

    # $CWD/config/.flex-cli
    # or $CWD/.flex-cli
    local_cache: True

With this configuration the current working directory configuration cache will be redirected from ``$HOME/cache/flex-cli/$CWD`` to local directory as well.

.. code:: console

    $CWD/.flex-cli/cache

