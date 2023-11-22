# OctoPrint-PSUControl-MomentaryGpio/

A sub-plugin for the PSUControl plugin that allows using bistable relays for power control. It implements
the same mechanisms as PSUControl, so it requires python periphery to be installed, only it pulls the GPIO
up/down only momentarily and then returns it to the default state.

## Setup

Install via the bundled [Plugin Manager](https://docs.octoprint.org/en/master/bundledplugins/pluginmanager.html)
or manually using this URL:

    https://github.com/irotsoma/OctoPrint-PSUControl-MomentaryGpio/archive/master.zip

## Configuration

- Set the PSUControl Switching Method to "Plugin" and select "PSUControl MomentaryGpio Plugin" from the dropdown

- Then in the PSUControl MomentaryGpio Plugin settings screen, set the appropriate GPIO Device, PIN, and pulse time in
milliseconds.

http://plugins.octoprint.org/plugin/psucontrol_momentarygpio/
