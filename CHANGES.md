# Changelog for SecuritySpy Home Assistant Integration

## Version 0.9.0 Beta-1

Release date: March 25th, 2021

This is a complete rewrite of the SecuritySpy Integration and the underlying Python IO Library that communicates with SecuritySpy. It is now fully working system, with basic functionality for a Video Surveillance integration.

**If you have already installed the previous version, please de-install it before you install this release.**

* `ADDED`: New push model, that removes the need for polling the SecuritySpy server every 2 seconds. Now data are pushed to HA, whenever a change occur.
* `ADDED`: Binary Motion Sensor, that shows if motion occurs or not. Please note, this will only be activated if the camera is set to record continuosly or on motion. If the AI features are activated in SecuritySpy, there will be an attribute called `event_object` that tells you if a Human or a Vehicle has been detected.
* Also this module is a complete rewrite, so it needs extensive testing. Please report any issues in the Issues log on Github.

As stated above, this is a rudimentary implementation, so if there are features you need, please also open an Issue on Github.