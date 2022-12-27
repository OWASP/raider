## Release history

### 0.3.3 - beta4 (2022-12-27)
Minor bugfix release.
* Fix crash when JSON doesn't decode
* Exit when (Failure) is returned while running multiple Flows from CLI
* Cookie/Header .from_plugin didn't work after recent changes, this was fixed
* Use RAIDERPATH environment variable

### 0.3.2 - beta3 (2022-12-13)

* Added Print.all Operation to print all HTTP data (request+response)
* Add the option to run quoted hylang code as operation
* Clean cache files and other unnecessary stuff from the final package

### 0.3.1 - beta2 (2022-12-10)

Minor bugfix release. Documentation being updated.


### 0.3.0 - beta1 (2022-12-04)

Besides outdated documentation, Raider is now ready to be considered a
beta quality software. Many things have changed, and many are still
being planned in the near future after the documentation gets
updated. Raider started as a framework focused on testing and
automating authentication processes, however it has evolved and now it
can be used for all kinds of stateful HTTP processes.

Some major things that have changed since last release are:

* Raider now has a CLI interface (not fully complete)
* Graph-like architecture, and there's no need to distinguish between
* authentication Flows and regular Flows
* Logging added everywhere
* New Plugins and Operations
* No more special variables
* Simplified Request definitions
* Fixed many bugs and implemented many smaller features

The documentation is still being worked on, so if you run into issues,
you will have to figure it out from the source code, or wait a little
until we update the documentation.


### 0.2.2 - alpha3 (2021-08-23)

* Split plugins into common, basic, modifiers and parsers.
* Add Combine modifier.
* Add UrlParser plugin.
* Update documentation with new plugin structure.

### 0.2.1 - alpha2 (2021-08-03)

* Improved the fuzzing module.
* Added request templates.
* Added Combine and Empty plugins.
* Fixed many bugs.

### 0.2.0 - alpha1 (2021-08-01)

* Added new operations and plugins.
* Improved existing operations and plugins.
* Implemented sessions, allowing users to save and load authentication data.
* Implemented basic fuzzing.
* Multiple bug fixes.
* Project directory changed from ``~/.config/raider/apps`` to
  ``~/.config/raider/projects``.
* Updated documentation.


### 0.1.3 - prototype (2021-07-20)

* Raider became open source.
* Package published on PyPi.
* Documentation published on readthedocs.
