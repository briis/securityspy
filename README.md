# SecuritySpy for Home Assistant

This is a Home Assistant Integration for [Ben Softwares](https://www.bensoftware.com) SecuritySpy Surveillance system.

Basically what this does, is integrating the Camera feeds from SecuritySpy in to Home Assistant, adds switches to adjust recording settings and adds Binary Motion Sensors to show if motion has occured.

**Note**: There is a know bug in the Python library *urllib3* which might show a Warning like the below in the Event Log:

`Failed to parse headers (url=http://192.168.x.x:8000/++eventStream?version=3&format=multipart&auth=ABCDEFGHIJKLMN): [StartBoundaryNotFoundDefect(), MultipartInvariantViolationDefect()], unparsed data: ''`

This warning can be ignored, and the Integration will still work as expected.

## Prerequisites

Before you install this Integration you need to ensure that the following settings are applied in SecuritySpy:

1. **Enable the Web Server** Open SecuritySpy on your Mac. Select *Preferences* from the SecuritySpy Menu and click the *Web* icon on the Top Left. Make sure that *HTTP enabled on Port* is selected and note the Port number as you need this later. Default is port 8000, but you are free to select another port if you want to. Currently SSL is not supported, so it does not have to be selected, but you can do, if you want to use this with external access.

2. **Add a Web Server User** You must add a user with either *Administrator* privileges or at least *Get Live Video and Images* and *Arm and Disarm, set schedules* privileges.

![Web Server Setup](https://github.com/briis/securityspy/blob/master/support_files/secspy_webserver_sm.png) ![User Setup](https://github.com/briis/securityspy/blob/master/support_files/secspy_users_sm.png) 

**Note** This Integration is only guaranteed to work on version 5.2.2 and greater of SecuritySpy. The integration is using some features from the AI implementation in V5 and some additions to the Event Stream that were introduced in V5.2.2.

## Manual Installation

To add SecuritySpy to your installation, create this folder structure in your /config directory:

`custom_components/securityspy`.
Then, drop the following files into that folder:

```yaml
__init__.py
manifest.json
binary_sensor.py
camera.py
switch.py
securityspy_server.py
services.yaml
```

## HACS Installation

This Integration is not part of the default HACS store yet. You can add is a Customer Integration in HACS by adding `https://github.com/briis/securityspy` to HACS under settings.

## Configuration

Start by configuring the core platform. No matter which of the entities you activate, this has to be configured. The core platform by itself does nothing else than establish a link to the *SecuritySpy NVR*, so by activating this you will not see any entities being created in Home Assistant.

Edit your *configuration.yaml* file and add the *unifiprotect* component to the file:

```yaml
# Example configuration.yaml entry
securityspy:
  host: <Internal ip address of your SecuritySpy Server>
  port: <Port Number>
  username: <your SecuritySpy username>
  password: <Your SecuritySpy Password>
```

**host**:  
(string)(Required) Type the IP address of your *SecuritySpy Server*. Example: `192.168.1.10`  

**port**:
(int)(required) Type the Port number you setup under the *Prerequisites* section.

**username**:  
(string)(Required) The username you setup under the *Prerequisites* section.  

**password**  
(string)(Required) The password you setup under the *Prerequisites* section.  

**This program is under development. The code in here might work. Once this message is removed, the code should be finished.**
