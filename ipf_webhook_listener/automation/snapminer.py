#!/usr/bin/python3
import logging

import httpx
from ipfabric import IPFClient

logger = logging.getLogger()


class MineSnapshot(IPFClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def universal_load(self):
        return {'pagination': {'limit': 1, 'start': 0}, "snapshot": self.snapshot_id, "columns": ["id"]}

    def __str__(self):
        return f"To mine data from snapshot_id: {self.snapshot_id}"

    def unipost(self, endpoint, payload=None, count=True):
        payload = payload or self.universal_load
        post_request = self.post(endpoint, json=payload)
        try:
            post_request.raise_for_status()
            return post_request.json()['_meta']['count'] if count else post_request.json()
        except httpx.HTTPError:
            logger.warning(f'API POST Error - Unable to POST data from endpoint: {endpoint}')
            return None

    def mine_base_data(self):
        # TODO: These were not referenced:
        """
            'e_wcontrollers': '/tables/wireless/controllers',
            'e_waps': '/tables/wireless/access-points',
            'e_wclients': '/tables/wireless/clients',
            'e_rules': '/reports?snapshot=' + self.snapshot_id,
        """
        l_active_int, l_edge_int = self.universal_load, self.universal_load
        l_active_int.update({"columns": ['l2'], "filters": {"l2": ["like", "up"]}})
        l_edge_int.update({"columns": ['edge'], "filters": {"edge": ["eq", "true"]}})

        full_details = {
            'System Hostname': self.get('/os/hostname').json()['hostname'].split('\n')[0],
            'System Version': self.os_version,
            'Snapshots available': len([s for s in self.snapshots if '$' not in s]),
            'Snapshot ID:': self.snapshot_id,
            'Number of devices': self.unipost('/tables/inventory/devices'),
            'Number of hosts': self.unipost('/tables/addressing/hosts'),
            'Number of interfaces': self.unipost('/tables/inventory/interfaces'),
            'Number of active ints': self.unipost('/tables/inventory/interfaces', l_active_int),
            'Number of edge ints': self.unipost('/tables/interfaces/switchports', l_edge_int),
            'Detected Port-Channels': self.unipost('/tables/interfaces/port-channel/member-status'),
            'Detected unique VLAN IDs': self.unipost('/tables/vlan/network-summary'),
            'Detected unique VRF names': self.unipost('/tables/vrf/summary'),
            'Number of IPSec Tunnels': self.unipost('/tables/security/ipsec/tunnels'),
            'Number of IPSec Gateways': self.unipost('/tables/security/ipsec/gateways'),
            'Routing protocols': self.get_routing_protocols(),
        }
        return full_details

    def get_routing_protocols(self):
        route_endpoints = {
            "bgp": '/tables/networks/summary/protocols/bgp',
            "ospf": '/tables/networks/summary/protocols/ospf',
            "ospfv3": '/tables/networks/summary/protocols/ospfv3',
            "isis": '/tables/networks/summary/protocols/isis',
            # "rip" : '/tables/networks/summary/protocols/rip',  # TODO RIP, EIGRP, Others?
        }
        output = [proto.upper() for proto, endpoint in route_endpoints.items() if self.unipost(endpoint) > 0]
        return output

    def mine_vendors(self):
        vendors_payload = {
            "snapshot": self.snapshot_id,
            "columns": ["id", "vendor", "familiesCount", "platformsCount", "modelsCount", "devicesCount"]
        }
        return self.unipost('/tables/inventory/summary/vendors', vendors_payload, count=False)['data']

    def mine_management(self):
        # TODO: 'e_mirror': '/tables/management/port-mirroring'  Do we want this?
        data = {
            'AAA Servers (server - count [share])': self.get_servers('/tables/security/aaa/servers', 'ip'),
            'NTP Servers (server - count [share])': self.get_servers('/tables/management/ntp/sources', 'source'),
            'SNMP Trap Hosts (server - count [share])': self.get_servers('tables/management/snmp/trap-hosts',
                                                                         'dstHost'),
            'Syslog Servers (server - count [share])': self.get_servers('/tables/management/logging/remote', 'host'),
            'Netflow Collectors (collector - count [share])': self.get_servers(
                '/tables/management/flow/netflow/collectors', 'collector'),
            'sFlow Collectors (collector - count [share])': self.get_servers('/tables/management/flow/sflow/collectors',
                                                                             'collector'),
            'Telnet enabled devices total': self.unipost('/tables/security/enabled-telnet')
        }
        return data

    def get_servers(self, data_endpoint, column):
        data = [i[column] for i in self.fetch_all(data_endpoint, columns=[column])]
        total = len(data)
        servers = dict()
        for i in data:
            servers[i] = servers.get(i, 0) + 1
        servers.pop(None, None)

        item_list = [[i, s, '[' + str(round(i / total * 100, 4)) + '%' + ']'] for s, i in servers.items()]
        item_strings = [l[1] + ' - ' + str(l[0]) + ' ' + l[2] + ', ' for l in sorted(item_list, reverse=True)]
        return ' '.join(item_strings)[:-2]

    def mine_intent_rules(self):
        self.intent.load_intent(snapshot_id=self.snapshot_id)
        intent_rules = {group: dict() for group in self.intent.group_by_name}
        for item in self.intent.intent_checks:
            groups = [g.name for g in item.groups]
            item_result = {'description': item.descriptions.general or ''}
            for c, n in dict(green=0, blue=10, amber=20, red=30).items():
                result = getattr(item.result.checks, c)
                if result is not None:
                    item_result[n] = dict(value=result, description=getattr(item.descriptions.checks, c) or '')

            for grp in groups:
                intent_rules[grp].update({item.name: item_result})
        return intent_rules
