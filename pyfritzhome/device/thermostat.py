# -*- coding: utf-8 -*-

from __future__ import print_function

import logging
from .fritzhomedevicefeatures import FritzhomeDeviceFeatures
from .base import FritzhomeBaseDevice

_LOGGER = logging.getLogger(__name__)


class FritzhomeThermostatDevice(FritzhomeBaseDevice):
    """The Fritzhome Device class."""

    actual_temperature = None
    target_temperature = None
    eco_temperature = None
    comfort_temperature = None
    battery_level = None
    window_open = None
    summer_active = None
    holiday_active = None
    lock = None
    device_lock = None
    error_code = None
    battery_low = None

    def _update_from_node(self, node):
        super()._update_from_node(node)

        if self.present is False:
            return

        if self.has_thermostat:
            hkr_element = node.find("hkr")

            try:
                self.actual_temperature = self.get_temp_from_node(hkr_element, "tist")
            except ValueError:
                pass

            self.target_temperature = self.get_temp_from_node(hkr_element, "tsoll")
            self.eco_temperature = self.get_temp_from_node(hkr_element, "absenk")
            self.comfort_temperature = self.get_temp_from_node(hkr_element, "komfort")

            # optional value
            try:
                self.device_lock = self.get_node_value_as_int_as_bool(
                    hkr_element, "devicelock"
                )
                self.lock = self.get_node_value_as_int_as_bool(hkr_element, "lock")
                self.error_code = self.get_node_value_as_int(hkr_element, "errorcode")
                self.battery_low = self.get_node_value_as_int_as_bool(
                    hkr_element, "batterylow"
                )
                self.battery_level = int(
                    self.get_node_value_as_int(hkr_element, "battery")
                )
                self.window_open = self.get_node_value_as_int_as_bool(
                    hkr_element, "windowopenactiv"
                )
                self.summer_active = self.get_node_value_as_int_as_bool(
                    hkr_element, "summeractive"
                )
                self.holiday_active = self.get_node_value_as_int_as_bool(
                    hkr_element, "holidayactive"
                )
            except Exception:
                pass

    @property
    def has_thermostat(self):
        """Check if the device has thermostat function."""
        return self._has_feature(FritzhomeDeviceFeatures.THERMOSTAT)

    def get_temperature(self):
        """Get the device temperature value."""
        return self._fritz.get_temperature(self.ain)

    def get_target_temperature(self):
        """Get the thermostate target temperature."""
        return self._fritz.get_target_temperature(self.ain)

    def set_target_temperature(self, temperature):
        """Set the thermostate target temperature."""
        return self._fritz.set_target_temperature(self.ain, temperature)

    def get_comfort_temperature(self):
        """Get the thermostate comfort temperature."""
        return self._fritz.get_comfort_temperature(self.ain)

    def get_eco_temperature(self):
        """Get the thermostate eco temperature."""
        return self._fritz.get_eco_temperature(self.ain)

    def get_hkr_state(self):
        """Get the thermostate state."""
        self.update()
        try:
            return {
                126.5: "off",
                127.0: "on",
                self.eco_temperature: "eco",
                self.comfort_temperature: "comfort",
            }[self.target_temperature]
        except KeyError:
            return "manual"

    def set_hkr_state(self, state):
        """Set the state of the thermostat.

        Possible values for state are: 'on', 'off', 'comfort', 'eco'.
        """
        try:
            value = {
                "off": 0,
                "on": 100,
                "eco": self.eco_temperature,
                "comfort": self.comfort_temperature,
            }[state]
        except KeyError:
            return

        self.set_target_temperature(value)
