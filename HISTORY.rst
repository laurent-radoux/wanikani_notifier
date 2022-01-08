=======
History
=======

Unreleased
----------

0.6.1 (2022-01-08)
------------------

* Fixed python 3.6 no longer supported

0.6.0 (2022-01-08)
------------------

* Fixed issue where hidden items were not filtered out
* Improved performances by caching all subjects

0.5.2 (2021-12-30)
------------------

* Updated pushsafer dependencies

0.5.1 (2021-10-03)
------------------

* Fixed reviews not filtered against current user level

0.5.0 (2021-08-05)
------------------

* Improved notifications by allowing the sending of URLs and icons
* Added min option to available_assignments_now CLI command
* Time for available now is no longer set to beginning of hour

  * Caused weird timings for lessons

* Fix stop-if-empty option not correctly handled in all cases

0.4.2 (2021-07-28)
------------------

* Fixed lessons not properly retrieved
* Fixed CLI parameters retrieval for notify

0.4.1 (2021-07-28)
------------------

* Fixed missing dependency


0.4.0 (2021-07-28)
------------------

* Added possibility to chain generation of messages to notify multiple things at once (CLI)
* Added support for console and Pushover notifiers
* Added Notifier factory system
* Added total available assignments to the notifiable topics

0.3.0 (2021-07-23)
------------------

* Changed "hours age" parameter to "since" to improve usability in scripts.
* Added notifier abstraction
* Added the possibility to use multiple notifiers

  * Currently, there is only one notifier (pushsafer)

* Changed options name to reflect these changes

0.2.0 (2021-07-21)
------------------

* Changed "after" parameter to "hours ago" to improve usability in scripts.

0.1.0 (2021-07-21)
------------------

* First release on PyPI.
