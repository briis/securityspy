# SecuritySpy for Home Assistant
![GitHub release](https://img.shields.io/github/release/briis/securityspy.svg?style=flat-square) [![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=flat-square)](https://github.com/custom-components/hacs)

This is a Home Assistant Integration for [Ben Softwares](https://www.bensoftware.com) SecuritySpy Surveillance system.

Basically what this does, is integrating the Camera feeds from SecuritySpy in to Home Assistant, adds switches to adjust recording settings and adds Binary Motion Sensors to show if motion has occured.

There is support for the following devices types within Home Assistant:
* Camera
* Sensor
* Switch
* --Binary Sensor

**NOTE**: There is now a working version that will setup the Cameras defined on the SecuritySpy Server, and some switches to to turn on/off the Motion Detection, plus a sensor for each camera showing what Recording Mode the Camera is in.
At present there is NOT a Binary Motion Sensor pr. camera. I am working on this, but it is a bit more tricky.

Please use the *Issues* tab on the repository, to report any errors you may find.

## Prerequisites

Before you install this Integration you need to ensure that the following settings are applied in SecuritySpy:

1. **Enable the Web Server** Open SecuritySpy on your Mac. Select *Preferences* from the SecuritySpy Menu and click the *Web* icon on the Top Left. Make sure that *HTTP enabled on Port* is selected and note the Port number as you need this later. Default is port 8000, but you are free to select another port if you want to. Currently SSL is not supported, so it does not have to be selected, but you can do, if you want to use this with external access.

2. **Add a Web Server User** You must add a user with either *Administrator* privileges or at least *Get Live Video and Images* and *Arm and Disarm, set schedules* privileges. **Note**: This might not be enough, as I have seen some errors, when using a user like that. If you want to be sure that it works for now, give the user *Administrative* rights.

![Web Server Setup](https://github.com/briis/securityspy/blob/master/support_files/secspy_webserver_sm.png) ![User Setup](https://github.com/briis/securityspy/blob/master/support_files/secspy_users_sm.png)

**Note** This Integration is only guaranteed to work on version 5.2.2 and greater of SecuritySpy. The integration is using some features from the AI implementation in V5 and some additions to the Event Stream that were introduced in V5.2.2.

## Installation

### HACS Installation
This Integration is not part of the default HACS store yet. You can add is a Customer Integration in HACS by adding `https://github.com/briis/securityspy` to HACS under settings.

### Manual Installation

To add SecuritySpy to your installation, create this folder structure in your /config directory:

`custom_components/securityspy`.
Then, drop the following files into that folder:

```yaml
__init__.py
manifest.json
config_flow.py
const.py
entity.py
camera.py
switch.py
services.yaml
strings.json
<translations> (Copy the directory and the files within it)
```


## Configuration
To add SecuritySpy to your installation, go to the Integrations page inside the configuration panel and add a Server by providing the IP Address, Port Username and Password for the SecuritySpy Webserver you set up above.

If the Server is found on the network it will be added to your installation. After that, you can add additional Servers if you have more than one in your network.

**You can only add SecuritySpy through the integrations page, not in configuration files.**

**host**:
(string)(Required) Type the IP address of your *SecuritySpy Server*. Example: `192.168.1.10`

**port**:
(int)(required) Type the Port number you setup under the *Prerequisites* section.

**username**:
(string)(Required) The username you setup under the *Prerequisites* section.

**password**
(string)(Required) The password you setup under the *Prerequisites* section.

