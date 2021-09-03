# Changelog for SecuritySpy Home Assistant Integration

## Version 1.0.7

Release date: Sepetember 3rd, 2021

* `FIX`: Issue #24.
* `CHANGED`: Ben from Bensoftware made a change I asked for, so it is now possible to optimize the Binary Motion Sensor, so that we don't need to wait for a file to be written. The sensor now turns on and off much faster, and we don't need specific Capture settings. It requires minimum V5.3.4b3 of SecuritySpy for this work.

## Version 1.0.4

Release date: May 6th, 2021

* `FIX`: If SecuritySpy had only 1 camera attached, the Integration would fail during setup. Issue #21
* `ADDED`: The CLASSIFY event is now also added to the Event Stream, so that this, in combination with the TRIGGER_M event, will ensure we record if a Human or Vehicle is detected. Requires that the `Motion Capture AI Trigger` threshold is set to a value larger than 0 on the *Triggers* Settings tab. See the [README.md](https://github.com/briis/securityspy#capture-image-when-person-is-detected) file for an example of how to make an automation based on this.


## Version 1.0.3

Release date: May 4th, 2021

* `CHANGE`: Modified several files to ensure compatability with 2021.5.x releases
* `CHANGE`: Added **iot_class** to `manifest.json` as per Home Assistant 2021.5 requirements.

## Version 1.0.2

Release date: April 10th, 2021

* `FIXED`: Issues #13 and #14 are fixed with this release. Specific Cameras and switches went off and on, without any actions by the user
* `CHANGE`: Removed all code that would refresh sensors as per a specific timeinterval. All changes are now purely push based.

## Version 1.0.1

Release date: April 9th, 2021

* `ADDED`: If you don't need Audio in the Live Stream, you can remove most of the latency in the stream, by not using the rtsp feed from the Camera. In order to do that, there is now an option in the Config Flow, to *Disable RTSP*. If this box is marked the stream will not use RTSP for streaming - and Audio will not work. If you already have configured the Integration, go to the *Integrations* page, and click OPTIONS on the SecuritySpy widget, then you will have the possibility to change this setting.
* `FIXED`: If there were no Schedule Presets defined on the SecuritySpy Server, the Integration would not install. Fixing issue #16
* `FIXED`: If authentication failed during setup or startup of the Integration it did not return the proper boolean, and did not close the session properly.

## Version 0.9.0 Beta-1

Release date: March 25th, 2021

This is a complete rewrite of the SecuritySpy Integration and the underlying Python IO Library that communicates with SecuritySpy. It is now fully working system, with basic functionality for a Video Surveillance integration.

**If you have already installed the previous version, please de-install it before you install this release.**

* `ADDED`: New push model, that removes the need for polling the SecuritySpy server every 2 seconds. Now data are pushed to HA, whenever a change occur.
* `ADDED`: Binary Motion Sensor, that shows if motion occurs or not. Please note, this will only be activated if the camera is set to record continuosly or on motion. If the AI features are activated in SecuritySpy, there will be an attribute called `event_object` that tells you if a Human or a Vehicle has been detected.
* Also this module is a complete rewrite, so it needs extensive testing. Please report any issues in the Issues log on Github.

As stated above, this is a rudimentary implementation, so if there are features you need, please also open an Issue on Github.