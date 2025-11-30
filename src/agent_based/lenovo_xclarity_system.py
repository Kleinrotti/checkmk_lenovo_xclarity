#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) 2025 Kleinrotti

# This is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# ails.  You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

from cmk.agent_based.v2 import (
    Service,
    SNMPTree,
    Metric,
    CheckPlugin,
    contains,
    State,
    Result,
    SNMPSection
)

_map_health = {
    "255": (State.OK, "Normal"),
    "0": (State.CRIT, "Non recoverable"),
    "2": (State.CRIT, "Critical"),
    "4": (State.WARN, "Warning")
}

_power_mapping = {
    "0": "Powered off",
    "1": "Sleep S3",
    "255": "Powered on"
}


def parse_lenovo_xclarity_system(string_table):
    return string_table


def check_lenovo_xclarity_system(section):
    (
        Status,
    ) = section[0][0]
    (
        PowerStatus,
        PowerOnHours,
        RestartCount,
    ) = section[1][0]
    state = _map_health.get(Status, (State.UNKNOWN, "Unknown"))
    yield Metric("hours_operation", float(PowerOnHours))
    yield Result(state=state[0], summary=f"Power: {_power_mapping.get(PowerStatus, "Unknown")}, Health: {state[1]}, Power on hours: {PowerOnHours}", details=f"Restarts: {RestartCount}")


snmp_section_lenovo_xclarity_system_setup = SNMPSection(
    name="lenovo_xclarity_system",
    parse_function=parse_lenovo_xclarity_system,
    detect=contains(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.19046.11.1"),
    fetch=[
        SNMPTree(
            base=".1.3.6.1.4.1.19046.11.1.1.4",
            oids=[
                '1.0',  # systemHealthStat
            ]
        ),
        SNMPTree(
            base=".1.3.6.1.4.1.19046.11.1.5.1",
            oids=[
                '1.0',  # currentSysPowerStatus
                '2.0',  # powerOnHours
                '3.0',  # restartCount
            ]
        )
    ]
)


def discover_lenovo_xclarity_system(section):
    yield Service()


check_plugin_lenovo_xclarity_system_setup = CheckPlugin(
    name="lenovo_xclarity_system",
    sections=["lenovo_xclarity_system"],
    service_name="System",
    discovery_function=discover_lenovo_xclarity_system,
    check_function=check_lenovo_xclarity_system,
)
