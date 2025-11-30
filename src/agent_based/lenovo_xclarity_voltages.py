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
    check_levels,
    State,
    Result
)


def parse_lenovo_xclarity_voltages(string_table):
    for i, row in enumerate(string_table):
        for j, cell in enumerate(row):
            if cell == 'N/A':
                string_table[i][j] = None
    return string_table


_map_health_state = {
    "Normal": State.OK
}


def check_lenovo_xclarity_voltages(item, params, section):
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
    if params.get("levels") is not None:
        levels = ("fixed", params.get("levels"))
    elif UpperNonCritical and UpperCritical:
        levels: tuple[str, tuple[float | None, float | None]] = ("fixed", (
                                                                 float(
                                                                     UpperNonCritical),
                                                                 float(
                                                                     UpperCritical))
                                                                 )
    else:
        levels = None
    if params.get("levels_lower") is not None:
        lower_levels = ("fixed", params.get("levels_lower"))
    elif LowerNonCritical and LowerCritical:
        lower_levels: tuple[str, tuple[float | None, float | None]] = ("fixed", (
                                                                       float(
                                                                           LowerNonCritical),
                                                                       float(
                                                                           LowerCritical))
                                                                       )
    else:
        lower_levels = None
    yield Result(state=_map_health_state.get(Status, State.CRIT), summary=f"State: {Status}")
    yield from check_levels(
        value=temp,
        metric_name="voltage",
        levels_upper=levels,
        levels_lower=lower_levels,
        render_func=lambda v: "%.1fV" % v
    )


snmp_section_lenovo_xclarity_voltages_setup = SimpleSNMPSection(
    name="lenovo_xclarity_voltages",
    parse_function=parse_lenovo_xclarity_voltages,
    detect=contains(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.19046.11.1"),
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.19046.11.1.1.2.2.1",
        oids=[
            '1',  # voltIndex
            '2',  # voltDescr
            '3',  # voltReading
            '6',  # voltCritLimitHigh
            '7',  # voltNonCritLimitHigh (used was warning)
            '9',  # voltCritLimitLow
            '10',  # voltNonCritLimitLow (used as warning)
            '11',  # voltHealthStatus
        ]
    )
)


def discover_lenovo_xclarity_voltages(section):
    for line in section:
        yield Service(item=line[1])


check_plugin_lenovo_xclarity_voltages_setup = CheckPlugin(
    name="lenovo_xclarity_voltages",
    sections=["lenovo_xclarity_voltages"],
    service_name="Voltage %s",
    discovery_function=discover_lenovo_xclarity_voltages,
    check_function=check_lenovo_xclarity_voltages,
    check_ruleset_name="voltage",
    check_default_parameters={}
)
