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
    get_value_store,
    State,
    Result
)

from cmk.plugins.lib.temperature import check_temperature


def parse_lenovo_xclarity_temperatures(string_table):
    for i, row in enumerate(string_table):
        for j, cell in enumerate(row):
            if cell == 'N/A':
                string_table[i][j] = None
            if cell.endswith(" Temp"):
                string_table[i][j] = cell[:-5]
    return string_table


_map_health_state = {
    "Normal": State.OK
}


def check_lenovo_xclarity_temperatures(item, params, section):
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
    temp = float(Reading)
    if UpperNonCritical and UpperCritical:
        levels: tuple[float | None, float | None] = (
            float(UpperNonCritical),
            float(UpperCritical),
        )
    else:
        levels = None, None
    if LowerNonCritical and LowerCritical:
        lower_levels: tuple[float | None, float | None] = (
            float(LowerNonCritical),
            float(LowerCritical),
        )
    else:
        lower_levels = None, None
    yield Result(state=_map_health_state.get(Status, State.CRIT), summary=f"State: {Status}")
    yield from check_temperature(
        reading=temp,
        params=params,
        unique_name="lenovo_xclarity_temp_%s" % item,
        value_store=get_value_store(),
        dev_levels=levels,
        dev_levels_lower=lower_levels,
        dev_status=0,
        dev_status_name=Status
    )


snmp_section_lenovo_xclarity_temperatures_setup = SimpleSNMPSection(
    name="lenovo_xclarity_temperatures",
    parse_function=parse_lenovo_xclarity_temperatures,
    detect=contains(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.19046.11.1"),
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.19046.11.1.1.1.2.1",
        oids=[
            '1',  # tempIndex
            '2',  # tempDescr
            '3',  # tempReading
            '6',  # tempCritLimitHigh
            '7',  # tempNonCritLimitHigh (used was warning)
            '9',  # tempCritLimitLow
            '10',  # tempNonCritLimitLow (used as warning)
            '11',  # tempHealthStatus
        ]
    )
)


def discover_lenovo_xclarity_temperatures(section):
    for line in section:
        yield Service(item=line[1])


check_plugin_lenovo_xclarity_temperatures_setup = CheckPlugin(
    name="lenovo_xclarity_temperatures",
    sections=["lenovo_xclarity_temperatures"],
    service_name="Temperature %s",
    discovery_function=discover_lenovo_xclarity_temperatures,
    check_function=check_lenovo_xclarity_temperatures,
    check_default_parameters={},
    check_ruleset_name="temperature",
)
