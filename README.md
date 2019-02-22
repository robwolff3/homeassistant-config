# Home Assistant

My personal implementation of [Home Assistant](https://home-assistant.io) (version: 0.88.0). Configuration last updated 2/22/2019.

## Overview

Here is my home automation project I have been improving since mid 2017. At that time I had switched from Samsung SmartThings and I could not be more happy with my decision. I take a firm minimalism approach to my layout, hence the number of things are essential and concise.

### In-front of Home Assistant

* HA is running on a docker container on a collective docker host I run in my homelab. For z-wave there a Z-stick plugged into the host. When I first started I tried Hassbian and other deployment methods, but wasn't satisfied with the level of control over the access and administration. HA in a Virtual Environment on a Debian Raspberry Pi 3 host is what I ran for awhile until last year when I upgraded my homelab to a single docker host. Docker is defiantly the way to go for easy of use, administration and updating.
* Interested in [Docker](https://www.docker.com/) but never used it before? Checkout my blog post: [Docker In Your HomeLab - Getting Started](https://borked.io/2019/02/13/docker-in-your-homelab.html).
* Connecting to HA externally, I use my own domain through Google Domains with a Dynamic DNS record setup on a sub domain. To solve the internal/external connection problem, I have a Host Override setup on my pfSense router that forwards my HA sub domain to the local IP address of HA when I'm on my local network.
* For connection security and certificate management I use the [linuxserver/letsencrypt](https://hub.docker.com/r/linuxserver/letsencrypt/) Docker container which has Nginx and [Let's Encrypt](https://letsencrypt.org/) packaged together. Nginx to reverse proxies the connections to HA and Let's Encrypt auto-renews to secure my traffic internally and externally.

### High Level Components and Ideas

* Google Assistant Commands - To get around a few limitations like casting Spotify and the mediocre native TTS I am using emulated google assistant SDK on my RaspberryPi. Following a post form [chocomega](https://community.home-assistant.io/u/chocomega) [here](https://community.home-assistant.io/t/community-hass-io-add-on-google-assistant-webserver-broadcast-messages-without-interrupting-music/37274/234) he walks you though setting it up. You can find the config in [configuration.yaml](configuration.yaml), the spotify/playlist selector here [playlist.yaml](packages/playlist.yaml) and broadcast notifications here [things.yaml](packages/things.yaml).
* Dishwasher Status/Notification - [phil1019](https://www.reddit.com/user/phil1019) shared his write up with me about monitoring dumb home devices power consumption to assume their state. I used the dishwasher portion of his setup, it can be found [here](https://philhawthorne.com/making-dumb-dishwashers-and-washing-machines-smart-alerts-when-the-dishes-and-clothes-are-cleaned/).
* Auto hide media devices when not in-use - Before I used a self made method, now lovelace has more native functionality through a [Conditional Card](https://www.home-assistant.io/lovelace/conditional/). I didn't like the clutter of 6 media devices on my main page when they are not playing anything.
* Light Alarm Clock - My bedroom lights slowly turn on, and the radio cast(s) instead of an immediate audible alarm. I used [this example](https://community.home-assistant.io/t/creating-an-alarm-clock-updated/15195) on the community forum by [hokagegano](https://community.home-assistant.io/u/hokagegano).
* Alarm Control - There are a lot of examples of HA Alarm Systems on the community forum, but none of them did exactly what I wanted, so I wrote [this one](packages/security.yaml) myself. The front end modules is the lovelace javascript module [alarm_control_panel-card](https://github.com/ciotlosm/custom-lovelace/tree/master/alarm_control_panel-card).
* [geekofweek](https://github.com/geekofweek/homeassistant) Repository - When I was getting started I pulled a lot of ideas and config examples from [geekoftheweek](https://community.home-assistant.io/u/geekoftheweek). Many thanks to this guy!
* Future Considerations - When I own my own dwelling I will probably monitor, operate, and use sensors from smart deadbolts/doors handles, smart smoke/carbon monoxide detector, smart doorbell, exterior lights, garage door opener, etc from HA.

### Custom Components

* [nadtcp2](https://gitlab.com/mindig.marton/ha-nadtcp) - The [nad](https://www.home-assistant.io/components/media_player.nad/) component doesn't work with the Nad C 338. This is a workaround.

### Lovelace JavaScript Modules

* [Alarm Control Panel Card](https://github.com/ciotlosm/custom-lovelace/tree/master/alarm_control_panel-card)
* [Mini Media Player](https://github.com/kalkih/mini-media-player)
* [Slider Entity Row](https://github.com/thomasloven/lovelace-slider-entity-row)

## Devices

* Docker Host - SSD based
* Aeotec Z-Stick Gen5
* DIY [pfSense](https://www.pfsense.org/) router
* Netgear Orbi (Set in AP mode)
* ZoneMinder

### Z-Wave Devices

* GE Z-Wave Plus In-wall Smart Dimmer Toggle 14295 - 6
* Ecolink Z-wave Plus Motion Detector PIRZWAVE2.5-ECO - 5
* Inovelli Z-Wave Plus Single Channel Smart Outlet
* Inovelli Z-Wave Plus Dual Channel Smart Outlet - 2
* NEO Z-wave Plus MINI Smart Power Plug (monitors power consumption) - 1
* Sensative Z-Wave Plus Strips Guard Contact Sensor (Don't recommend) - 3
* Kwikset 912 Z-Wave SmartCode Electronic Touchpad

### Media and Other Devices

* Hikvision Cameras - 2
* Google Hub
* Chromecast Ultra
* JBL Link 20
* Vizio 4k TV
* Nad C 338
* Roomba 890
* Hue Bridge (Deprecating)
* Hue White A19 - 2
* Hue Dimmer Switch

## Interface

![UI](images/ha1_home.jpg)
![UI](images/ha1_security.jpg)
![UI](images/ha1_override.jpg)
