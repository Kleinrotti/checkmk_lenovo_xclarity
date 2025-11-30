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
)


def parse_lenovo_xclarity_disks(string_table):
    return string_table


_map_health_state = {
    "Normal": State.OK
}


def check_lenovo_xclarity_disks(item, section):
    entry = next(i for i in section if i[1] == item)
    (
        Index,
        Name,
        Status
    ) = entry
    yield Result(state=_map_health_state.get(Status, State.CRIT), summary=f"State: {Status}")


snmp_section_lenovo_xclarity_disks_setup = SimpleSNMPSection(
    name="lenovo_xclarity_disks",
    parse_function=parse_lenovo_xclarity_disks,
    detect=contains(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.19046.11.1"),
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.19046.11.1.1.12.2.1",
        oids=[
            '1',  # diskIndex
            '2',  # diskFruName
            '3',  # diskHealthStatus
        ]
    )
)


def discover_lenovo_xclarity_disks(section):
    for line in section:
        yield Service(item=line[1])


check_plugin_lenovo_xclarity_disks_setup = CheckPlugin(
    name="lenovo_xclarity_disks",
    sections=["lenovo_xclarity_disks"],
    service_name="Disk %s",
    discovery_function=discover_lenovo_xclarity_disks,
    check_function=check_lenovo_xclarity_disks,
)
