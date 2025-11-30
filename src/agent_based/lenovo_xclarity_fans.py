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
    check_levels
)


def parse_lenovo_xclarity_fans(string_table):
    for i, row in enumerate(string_table):
        for j, cell in enumerate(row):
            if cell.endswith(" Tach"):
                string_table[i][j] = cell[:-5]
    return string_table


_map_health_state = {
    "Normal": State.OK
}


def check_lenovo_xclarity_fans(item, params, section):
    entry = next(i for i in section if i[1] == item)
    (
        Index,
        Description,
        Reading,
        UpperCritical,
        UpperNonCritical,
        LowerCritical,
        LowerNonCritical,
        Status
    ) = entry
    if not Reading:
        return
    # unfortunalty the device threshholds are useless because the sensor value is in percent and the min max are absolute RPMs
    levels_low = params.get("levels_lower")
    level_up = params.get("levels")
    # the value comes as string like this: "37% of maximum", so it has to be formatted/cleaned
    speed = float(Reading.split('%')[0].replace(" ", ""))
    yield Result(state=_map_health_state.get(Status, State.CRIT), summary=f"State: {Status}")
    yield from check_levels(
        value=speed,
        metric_name="fan_perc",
        render_func=lambda v: "Speed: %.1f%%" % v,
        levels_lower=("fixed", levels_low) if levels_low else None,
        levels_upper=("fixed", level_up) if level_up else None
    )


snmp_section_lenovo_xclarity_fans_setup = SimpleSNMPSection(
    name="lenovo_xclarity_fans",
    parse_function=parse_lenovo_xclarity_fans,
    detect=contains(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.19046.11.1"),
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.19046.11.1.1.3.2.1",
        oids=[
            '1',  # fanIndex
            '2',  # fanDescr
            '3',  # fanSpeed in percent
            '5',  # fanCritLimitHigh
            '6',  # fanNonCritLimitHigh (used was warning)
            '8',  # fanCritLimitLow
            '9',  # fanNonCritLimitLow (used as warning)
            '10',  # fanHealthStatus
        ]
    )
)


def discover_lenovo_xclarity_fans(section):
    for line in section:
        yield Service(item=line[1])


check_plugin_lenovo_xclarity_fans_setup = CheckPlugin(
    name="lenovo_xclarity_fans",
    sections=["lenovo_xclarity_fans"],
    service_name="%s",
    discovery_function=discover_lenovo_xclarity_fans,
    check_function=check_lenovo_xclarity_fans,
    check_default_parameters={},
    check_ruleset_name="hw_fans_perc",
)
