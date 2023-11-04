# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import periphery
import glob
import time

class PsuControl_ToggleGpioPlugin(octoprint.plugin.StartupPlugin,
                                  octoprint.plugin.RestartNeedingPlugin,
                                  octoprint.plugin.TemplatePlugin,
                                  octoprint.plugin.SettingsPlugin
                                  ):
    def __init__(self):
        super().__init__()
        self._switchGPIOPin = None
        self._availableGPIODevices = self.get_gpio_devs()

    def get_settings_defaults(self):
        return dict(
            gpioDevice='',
            switchGPIOPin=0,
            invertSwitchGPIOPin=False,
            toggleTime=100
        )

    def on_after_startup(self):
        self.configure_gpio()

    def cleanup_gpio(self):
        self._logger.debug("Cleaning up pin {}".format(self._switchGPIOPin.name))
        try:
            self._switchGPIOPin.close()
        except Exception:
            self._logger.exception("Exception while cleaning up pin {}.".format(self._switchGPIOPin.name))
        self._switchGPIOPin = None
    def get_gpio_devs(self):
        return sorted(glob.glob('/dev/gpiochip*'))

    def turn_psu_on(self):
        self._logger.debug("Switching PSU On Using GPIO: {}".format(self._settings.get(["switchGPIOPin"])))
        self.toggle_gpio()

    def turn_psu_off(self):
        self._logger.debug("Switching PSU Off Using GPIO: {}".format(self._settings.get(["switchGPIOPin"])))
        self.toggle_gpio()

    def toggle_gpio(self):
        try:
            self._switchGPIOPin.write(bool(1 ^ self._settings.get_boolean(["invertSwitchGPIOPin"])))
            time.sleep(self._settings.get_int(["toggleTime"])/1000)
            self._switchGPIOPin.write(bool(0 ^ self._settings.get_boolean(["invertSwitchGPIOPin"])))
        except Exception:
            self._logger.exception("Exception while writing GPIO line")
            return

    def configure_gpio(self):
        self._logger.info("Periphery version: {}".format(periphery.version))
        if not self._settings.get_boolean(["invertSwitchGPIOPin"]):
            initial_output = 'low'
        else:
            initial_output = 'high'
        try:
            pin = periphery.GPIO(self._settings.get(["gpioDevice"]), self._settings.get_int(["switchGPIOPin"]), initial_output)
            self._switchGPIOPin = pin
        except Exception:
            self._logger.exception(
                "Exception while setting up GPIO pin {}".format(self._settings.get_int(["switchGPIOPin"]))
            )

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        self.cleanup_gpio()
        self.configure_gpio()

    def on_startup(self, host, port):
        psucontrol_helpers = self._plugin_manager.get_helpers("psucontrol")
        if not psucontrol_helpers or 'register_plugin' not in psucontrol_helpers.keys():
            self._logger.warning("The version of PSUControl that is installed does not support plugin registration.")
            return

        self._logger.debug("Registering plugin with PSUControl")
        psucontrol_helpers['register_plugin'](self)

    ##~~ AssetPlugin mixin

    def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
        return {
            "js": ["js/psucontrol_togglegpio.js"],
            "css": ["css/psucontrol_togglegpio.css"],
            "less": ["less/psucontrol_togglegpio.less"]
        }

    ##~~ Softwareupdate hook

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return {
            "psucontrol_togglegpio": {
                "displayName": "Psucontrol_togglegpio Plugin",
                "displayVersion": self._plugin_version,

                # version check: github repository
                "type": "github_release",
                "user": "irotsoma",
                "repo": "OctoPrint-PSUControl-ToggleGPIO",
                "current": self._plugin_version,

                # update method: pip
                "pip": "https://github.com/irotsoma/OctoPrint-PSUControl-ToggleGPIO/archive/{target_version}.zip",
            }
        }


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "PSUControl_ToggleGPIO Plugin"

# Set the Python version your plugin is compatible with below. Recommended is Python 3 only for all new plugins.
# OctoPrint 1.4.0 - 1.7.x run under both Python 3 and the end-of-life Python 2.
# OctoPrint 1.8.0 onwards only supports Python 3.
__plugin_pythoncompat__ = ">=3,<4"  # Only Python 3


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = PsuControl_ToggleGpioPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
