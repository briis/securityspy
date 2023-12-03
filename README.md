# SecuritySpy for Home Assistant
![GitHub release](https://img.shields.io/github/release/briis/securityspy.svg?style=flat-square) [![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=flat-square)](https://github.com/hacs/integration)

## Overview

This is a Home Assistant Integration for [Ben Software](https://www.bensoftware.com)'s SecuritySpy Surveillance system.

Basically what this does, is integrating the Camera feeds from SecuritySpy in to Home Assistant, adds switches to adjust recording settings and adds Binary Motion Sensors to show if motion has occured. This project uses a *local push model* to get data from the SecuritySpy Server.

There is support for the following devices types within Home Assistant:
* Camera
* Binary Sensor
* Button
* Sensor
* Switch

Please use the *Issues* tab on the repository, to report any errors you may find.

## Prerequisites

Before you install this Integration you need to ensure that the following settings are applied in SecuritySpy:

1. **Enable the Web Server** Open SecuritySpy on your Mac. Select *Preferences* from the SecuritySpy Menu and click the *Web* icon on the Top Left. Make sure that *HTTP enabled on Port* is selected and note the Port number as you need this later. Default is port 8000, but you are free to select another port if you want to. Currently SSL is not supported, so it does not have to be selected, but you can do, if you want to use this with external access.

2. **Add a Web Server User** You must add a user with either *Administrator* privileges or at least *Get Live Video and Images* and *Arm and Disarm, set schedules* privileges. **Note**: This might not be enough, as I have seen some errors, when using a user like that. If you want to be sure that it works for now, give the user *Administrative* rights.

3. This Integration is only guaranteed to work on version 5.3.4 and greater of SecuritySpy.

![Web Server Setup](https://github.com/briis/securityspy/blob/master/support_files/secspy_webserver_sm.png) ![User Setup](https://github.com/briis/securityspy/blob/master/support_files/secspy_users_sm.png)

**Note** As Home Assistant only supports AAC audio format and SecuritySpy only sends audio in µLaw, there is NO AUDIO on the Live Stream. Hopefylly this can be corrected in future updates of either of these programs.

## Installation

### HACS Installation
This Integration is part of the default HACS store. Search for *securityspy* under *Integrations* and install from there. After the installation of the files you must restart Home Assistant, or else you will not be able to add SecuritySpy from the Integration Page.

If you are not familiar with HACS, or haven't installed it, we would recommend to [look through the HACS documentation](https://hacs.xyz/), before continuing. Even though you can install the Integration manually, we recommend using HACS, as you would always be reminded when a new release is published.

**Please note**: All HACS does, is copying the needed files to Home Assistant, and placing them in the right directory. To get the Integration to work, you now need to go through the steps in the *Configuration* section.

### Manual Installation

To add SecuritySpy to your installation, create this folder structure in your /config directory:

`custom_components/securityspy`.
Then, drop the following files into that folder:

```yaml
__init__.py
binary_sensor.py
button.py
camera.py
config_flow.py
const.py
data.py
entity.py
manifest.json
models.py
sensor.py
services.yaml
strings.json
switch.py
<translations> (Copy the directory and the files within it)
```


## Configuration
To add SecuritySpy to your installation, go to the Integrations page inside the configuration panel and add a Server by providing the IP Address, Port Username and Password for the SecuritySpy Webserver you set up above.

If the Server is found on the network it will be added to your installation. After that, you can add additional Servers if you have more than one in your network.

**You can only add SecuritySpy through the integrations page, not in configuration files.**

**host**:
(string)(Required) Type the IP address of your *SecuritySpy Server*. Example: `192.168.1.10`

**port**:
(int)(required) Type the Port number you setup under the *Prerequisites* section. Example: `8000`

**username**:
(string)(Required) The username you setup under the *Prerequisites* section.

**password**
(string)(Required) The password you setup under the *Prerequisites* section.

**disable rtsp stream**
(boolean)(Optional) Mark this box, if you want to diable the RTSP stream - Gives better realtime live streaming.

## Automation Examples

As part of the integration, we provide a couple of blueprints that you can use or extend to automate stuff.

### Motion Notifications

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https://raw.githubusercontent.com/briis/securityspy/master/blueprints/securityspy_push_notification_motion_event.yaml)


Here are examples of different automations that can be used with this integration.

### Capture Image when Person is detected

This automation captures an image, when a Person is detected on the Camera. For the example, the Camera is called `camera.outdoor` so the motion sensor will then be named `binary_sensor.motion_outdoor` It is a very basic example, but it can be used to illustrate the use case. `event_object` can be *human* or *vehicle*.

```yaml
alias: Capture snapshot when person is detected
description: ''
trigger:
  - platform: state
    entity_id: binary_sensor.motion_outdoor
    attribute: event_object
    to: human
condition: []
action:
  - service: camera.snapshot
    target:
      entity_id: camera.outdoor
    data:
      filename: /config/www/camera_outdoor.jpg
mode: single
```

### Download Video Recording when motion is complete

If you want to have a copy of the latest Video recording on your local Home Assistant, then the below is an example on how to do that. Again the Camera is called `camera.outdoor` so the motion sensor will then be named `binary_sensor.motion_outdoor`

```yaml
alias: Download Recording after motion
description: ''
trigger:
  - platform: state
    entity_id: binary_sensor.motion_outdoor
    from: 'on'
    to: 'off'
condition: []
action:
  - service: securityspy.download_latest_motion_recording
    data:
      entity_id: camera.outdoor
      filename: /media/outdoor_latest.m4v
mode: restart
```

## Enable Debug Logging
If logs are needed for debugging or reporting an issue, use the following configuration.yaml:
```yaml
logger:
  default: error
  logs:
    custom_components.securityspy: debug
```
