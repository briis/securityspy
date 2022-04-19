# Changelog for SecuritySpy Home Assistant Integration

## Version 1.1.4

Release date: Not Released

- `NEW`: Added an `event_score_human` and `event_score_vehicle` attributes to the binary motion sensor and the detected oject sensor, that shows the percentage probability of the object being detected. The `event_object` will still hold the object that has the highest score of the two, but if you only want to look for a person moving, you can check on the `event_score_human` value. Closing <Issue [#38](https://github.com/briis/securityspy/issues/38)>

## Version 1.1.4-beta.2

Release date: 2022-04-18

- `NEW`: Replaced the `event_score` attribute with two new attributes: `event_score_human` and `event_score_vehicle`. The `event_object` will still hold the object that has the highest score of the two, but if you only want to look for a person moving, you can check on the `event_score_human` value.


## Version 1.1.4-beta.1

Release date: 2022-04-17

- `NEW`: Added an `event_score` attribute to the binary motion sensor and the detected oject sensor, that shows the percentage probability of the object being detected. Currently this will only show one score for either Human or Vehicle, depending on which is highest.


## Version 1.1.3

Release date: 2022-04-07

- `FIXED`: Issue [#37](https://github.com/briis/securityspy/issues/37) Ensures that Switches and Sensors are being loaded correctly after upgrade to 2022.4 of Home Assistant.
- `NEW`: Added a new sensor per Camera called `sensor.CAMERA_NAME_detected_object`. On motion detection this will change the state to either `Human` or `Vehicle` if one of these objects are detected. You can use this sensor to only run automations if a Person or a Car is detected on motion.


## Version 1.1.1

Release date: 2021-12-24

- `NEW`: Added 2 more PTZ Buttons
  - `Zoom In` button. When pressing this button the camera will start to zoom in.
  - `Zoom Out` button. When pressing this button the camera will start to zoom out.


## Version 1.1.0

Release date: 2021-12-22

## This release contains BREAKING CHANGES and you will have to re-define most of your settings in the UI and in automations after installation.

### Upgrade Instructions

Due to the many changes and entities that have been removed and replaced, we recommend the following process to upgrade from an earlier Beta or from an earlier release:

- Upgrade the Integration files, either through HACS (Recommended) or by copying the files manually to your custom_components/securityspy directory.
- Restart Home Assistant
- Remove the SecuritySpy Integration by going to the Integrations page, click the 3 dots in the lower right corner of the SecuritySpy Integration and select Delete
- While still on this page, click the + ADD INTEGRATION button in the lower right corner, search for SecuritySpy, and start the installation, supplying your credentials.

### Changes

* `NEW`: Added a new Binary Sensor for each Camera showing if the Camera is updated. This sensor is event driven, so as soon as SecuritySpy flags it as Offline the sensor will update and vice versa.
* `NEW`: Added configuration url for each camera on the *Devices* page, so that you can go directly from here to the Camera Settings page in SecuritySpy
* `NEW`: Added partial support for PTZ. If a camera has PTZ capabilities, the following buttons will be created:
  * `Left` button. When pressing this button the camera will start a left movement.
  * `Right` button. When pressing this button the camera will start a right movement.
  * `Up` button. When pressing this button the camera will start an upwards movement.
  * `Down` button. When pressing this button the camera will start a downwardst movement.
  * `Stop` button. When pressing this button the camera will stop any movement currently in progress.
  * `Presets` buttons. For each Preset defined in SecuritySpy, a button will be created to activate that preset.

* `CHANGED`: Removed the *online* attribute from the Camera Entity, as this is now replaced with the Binary Online sensor.
* `CHANGED`: All entities have been updated to follow a more up to date coding practice for Home Assistant Integrations.

* `FIXED`: Ensuring the Websocket is properly closed before a restart of the Integration.
* `FIXED`: Deprecation warning about `device_state_attributes` start showing up in Home Assistant 2021.12. This is now corrected and moved to the correct type.

## Version 1.1.0-beta.2

Release date: 2021-12-21

* `FIXED`: Ensuring the Websocket is properly closed before a restart of the Integration.
* `FIXED`: Code clean-up.
* `NEW`: Added a new Binary Sensor for each Camera showing if the Camera is updated. This sensor is event driven, so as soon as SecuritySpy flags it as Offline the sensor will update and vice versa.
* `CHANGED`: All entities have been updated to follow a more up to date coding practice for Home Assistant Integrations.


## Version 1.1.0-beta.1

Release date: 2021-12-20

* `NEW`: Added partial support for PTZ. If a camera has PTZ capabilities, the following buttons will be created:
  * `Left` button. When pressing this button the camera will start a left movement.
  * `Right` button. When pressing this button the camera will start a right movement.
  * `Up` button. When pressing this button the camera will start an upwards movement.
  * `Down` button. When pressing this button the camera will start a downwardst movement.
  * `Stop` button. When pressing this button the camera will stop any movement currently in progress.
  * `Presets` buttons. For each Preset defined in SecuritySpy, a button will be created to activate that preset.


* `FIXED`: Deprecation warning about `device_state_attributes` start showing up in Home Assistant 2021.12. This is now corrected and moved to the correct type.

* `NEW`: Added configuration url for each camera on the *Devices* page, so that you can go directly from here to the Camera Settings page in SecuritySpy

* `NEW`: **Breaking Change** As part of Home Assistant 2021.11 a new Entity Category is introduced. This makes it possible to classify an entity as either `config` or `diagnostic`. A `config` entity is used for entities that can change the configuration of a device and a `diagnostic` entity is used for devices that report status, but does not allow changes. These to entity categories have been applied to selected entities in this Integration.<br>
Entities which have the entity_category set:
  * Are not included in a service call targetting a whole device or area.
  * Are, by default, not exposed to Google Assistant or Alexa. **This might be a Breaking Change**
  * Are shown on a separate card on the device configuration page.
  * Do not show up on the automatically generated Lovelace Dashboards. **This might be a Breaking Change**

## Version 1.0.7

Release date: Sepetember 7th, 2021

* `FIX`: Issue #24. Allow requesting a custom snapshot width and height, to support 2021.9 release
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