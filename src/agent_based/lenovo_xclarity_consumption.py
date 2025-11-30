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
    SimpleSNMPSection,
    CheckPlugin,
    contains,
    State,
    Result,
    Metric
)


def parse_lenovo_xclarity_consumption(string_table):
    return string_table


def check_lenovo_xclarity_consumption(section):
    (
        PowerInUse,
    ) = section[0]
    yield Result(state=State.OK, summary=f"Power: {PowerInUse}W")
    yield Metric("power_usage", int(PowerInUse))


snmp_section_lenovo_xclarity_consumption_setup = SimpleSNMPSection(
    name="lenovo_xclarity_consumption",
    parse_function=parse_lenovo_xclarity_consumption,
    detect=contains(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.19046.11.1"),
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.19046.11.1.1.10",
        oids=[
            '1.10',  # fuelGaugeTotalPowerInUse
        ]
    )
)


def discover_lenovo_xclarity_consumption(section):
    yield Service()


check_plugin_lenovo_xclarity_consumption_setup = CheckPlugin(
    name="lenovo_xclarity_consumption",
    sections=["lenovo_xclarity_consumption"],
    service_name="Power Consumption",
    discovery_function=discover_lenovo_xclarity_consumption,
    check_function=check_lenovo_xclarity_consumption,
)
