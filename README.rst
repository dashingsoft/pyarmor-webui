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

1.4.1
~~~~~
* Change install_requires to `pyarmor~=7.6.0` because it doesn't work with Pyarmor 8.0+

1.4.0
~~~~~
* Add new option `--mix-str`

1.3.3
~~~~~
* Fix typos

1.3.2
~~~~~
* Add advanced mode 5

1.3.1
~~~~~
* Add restrict mode 101, 102, 103, 104, 105

1.2.9
~~~~~
* Add new platforms: darwin.aarch64.3, android.armv7, android.x86_64, android.x86

1.2.8
~~~~~
* In register dialog, it also supports to register a code.

1.2.7
~~~~~
* Fix bug (#3): mode `pack all to one file with outer license` failed.

1.2.6
~~~~~
* Add restrict mode 5
* For Windows disable quick edit in CMD, as it can freeze the application

1.2.5
~~~~~
* Fix issue: the relative path in extra pack options may not work

1.2.4
~~~~~
* Fix issue: the icon with absolute path could not be found in Windows
* Fix select Src issue in Windows

1.2.3
~~~~~
* Add new platform catalog `VM Protection` with 2 platforms:
  - windows.x86_64.25
  - windows.x86.25
* Rename platform `alpine.*` to `musl.*`
* Add new platforms:
  - musl.mips32
  - linux.mips64
  - linux.mips64el

1.2.2
~~~~~
* In mode tab, `Advanced Mode` support 2 extra values:
  - 3, enable vm mode and advanced mode
  - 4, enable vm mode and super mode
* When registering PyArmor, if there is a file `pyarmor-regfile-1.zip` is in the
  current path, need not select any file, just click register directly

1.2.1
~~~~~
* Fix Windows issue: there is no drive list when selecting source path from `/`

1.2
~~~
* In mode tab, `Obfuscate Code Object` support 3 values:
  - 0, no obfuscate functions in module
  - 1, obfuscate each function by quick algorithm
  - 2, obfuscate each function by complex algorithm

1.1
~~~
* In mode tab, `Advanced Mode` support 3 values:
  - 0, disable advanced mode
  - 1, enable advanced mode
  - 2, enable super mode

1.0
~~~
* Add 2 plugins `on`, `assert_armored` in the plugin selection list
* Fix python 2.7 failed issue: `TypeError: super() takes at least 1 argument (0 given)`
* Add chinese language only for UI

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
