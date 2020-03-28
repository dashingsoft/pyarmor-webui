pyarmor-webui
=============

pyarmor-webui is a web-ui for pyarmor. It's a tool to obfuscate python
scripts, bind obfuscated scripts to fixed machine or expire obfuscated
scripts.

Install by `pip`::

  pip install pyarmor-webui

Start it in the default web browser::

  pyarmor-webui

A light-weigh web server will run on default port 9096 to serve the
request of web pages. If this port is used by others, start it with
other port. For example::

  pyarmor-webui -p 9088

Only run the web server, do not open web browser::

  pyarmor-webui -n

For more options::

  pyarmor-webui -h

If it's not installed by `pip`, run `pyarmor-webui` by this way::

  python server.py

Before that make sure `pyarmor` has been installed::

  pip install pyarmor

More Resources
--------------

- `snapshots <https://github.com/dashingsoft/pyarmor-webui/tree/master/snapshots>`_
- `pyarmor <https://github.com/dashingsoft/pyarmor>`_
- `pyarmor-vue <https://github.com/dashingsoft/pyarmor-vue>`_

Change Logs
-----------

0.9
~~~
* Fix python2.7 issue: No module named shelx
* Add new platform: `uclibc.armv7.0`
* In my projects page add a project action `Diagnose` to print debug information
  in case something is wrong with building the project
* In project edit page add 2 buttons: `Build`, `Diagnose`
* In project edit page, the field of `Pack options` now is textarea
* Change default restrict mode to `1`

0.8
~~~
* Fix license option `Extra data` doesn't work issue
