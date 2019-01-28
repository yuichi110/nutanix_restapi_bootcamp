'''
Nutanix REST API Bootcamp.

Lesson03.
Handling JSON.
'''

import json

JSON_TEXT = '''
{"id":"00057f79-32a5-87e1-0000-0000000135e5::79333","uuid":"00057f79-32a5-87e1-0000-0000000135e5","clusterIncarnationId":1547533401032673,"clusterUuid":"00057f79-32a5-87e1-0000-0000000135e5","name":"Training-02","clusterExternalIPAddress":"10.149.161.41","clusterExternalDataServicesIPAddress":null,"timezone":"Asia/Tokyo","supportVerbosityType":"BASIC_COREDUMP","operationMode":"Normal","storageType":"mixed","clusterFunctions":["NDFS"],"numNodes":4,"blockSerials":["15SM60370074"],"version":"5.5.2","fullVersion":"el7.3-release-euphrates-5.5.2-stable-6a19e52b0fc2293b18cf00c5cbc4f675145f1a6a","targetVersion":"5.5.2","externalSubnet":"10.149.160.0/255.255.252.0","internalSubnet":"192.168.5.0/255.255.255.128","nccVersion":"ncc-3.5.1","enableLockDown":false,"enablePasswordRemoteLoginToCluster":true,"fingerprintContentCachePercentage":100,"ssdPinningPercentageLimit":25,"enableShadowClones":true,"globalNfsWhiteList":[],"nameServers":["8.8.8.8"],"ntpServers":["ntp.nict.jp"],"serviceCenters":[],"httpProxies":[],"rackableUnits":[{"id":25,"rackableUnitUuid":"d0740b90-2885-47f4-ab36-4cf163276f9e","model":"UseLayout","modelName":"NX-3060-G4","location":null,"serial":"15SM60370074","positions":["1","2","3","4"],"nodes":[6,7,8,13433],"nodeUuids":["50e41f34-2304-4636-aa57-f2e653e2c310","e528b902-2f74-412c-bdf9-7fdc3ecd085e","59c9561d-13c3-49a2-94d4-5261b521dfa6","0c633e50-4a16-4a9e-982d-f376a59387d1"]}],"publicKeys":[],"smtpServer":null,"hypervisorTypes":["kKvm"],"clusterRedundancyState":{"currentRedundancyFactor":2,"desiredRedundancyFactor":2,"redundancyStatus":{"kCassandraPrepareDone":true,"kZookeeperPrepareDone":true}},"multicluster":false,"cloudcluster":false,"hasSelfEncryptingDrive":false,"isUpgradeInProgress":false,"securityComplianceConfig":{"schedule":"DAILY","enableAide":false,"enableCore":false,"enableHighStrengthPassword":false,"enableBanner":false,"enableSNMPv3Only":false},"hypervisorSecurityComplianceConfig":{"schedule":"DAILY","enableAide":false,"enableCore":false,"enableHighStrengthPassword":false,"enableBanner":false},"hypervisorLldpConfig":{"enableLldpTx":false},"clusterArch":"X86_64","isSspEnabled":false,"iscsiConfig":null,"domain":null,"nosClusterAndHostsDomainJoined":false,"allHypervNodesInFailoverCluster":false,"credential":null,"stats":{"hypervisor_avg_io_latency_usecs":"0","num_read_iops":"0","hypervisor_write_io_bandwidth_kBps":"0","timespan_usecs":"30000000","controller_num_read_iops":"0","read_io_ppm":"0","controller_num_iops":"0","total_read_io_time_usecs":"-1","controller_total_read_io_time_usecs":"0","replication_transmitted_bandwidth_kBps":"0","hypervisor_num_io":"0","controller_total_transformed_usage_bytes":"-1","hypervisor_cpu_usage_ppm":"38620","controller_num_write_io":"0","avg_read_io_latency_usecs":"-1","content_cache_logical_ssd_usage_bytes":"0","controller_total_io_time_usecs":"0","controller_total_read_io_size_kbytes":"0","controller_num_seq_io":"-1","controller_read_io_ppm":"0","content_cache_num_lookups":"0","controller_total_io_size_kbytes":"0","content_cache_hit_ppm":"0","controller_num_io":"0","hypervisor_avg_read_io_latency_usecs":"0","content_cache_num_dedup_ref_count_pph":"100","num_write_iops":"0","controller_num_random_io":"-1","num_iops":"0","replication_received_bandwidth_kBps":"0","hypervisor_num_read_io":"0","hypervisor_total_read_io_time_usecs":"0","controller_avg_io_latency_usecs":"0","hypervisor_hyperv_cpu_usage_ppm":"-1","num_io":"0","controller_num_read_io":"0","hypervisor_num_write_io":"0","controller_seq_io_ppm":"-1","controller_read_io_bandwidth_kBps":"0","controller_io_bandwidth_kBps":"0","hypervisor_hyperv_memory_usage_ppm":"-1","hypervisor_timespan_usecs":"30000000","hypervisor_num_write_iops":"0","replication_num_transmitted_bytes":"0","total_read_io_size_kbytes":"0","hypervisor_total_io_size_kbytes":"0","avg_io_latency_usecs":"0","hypervisor_num_read_iops":"0","content_cache_saved_ssd_usage_bytes":"0","controller_write_io_bandwidth_kBps":"0","controller_write_io_ppm":"0","hypervisor_avg_write_io_latency_usecs":"0","hypervisor_total_read_io_size_kbytes":"0","read_io_bandwidth_kBps":"0","hypervisor_esx_memory_usage_ppm":"-1","hypervisor_memory_usage_ppm":"83984","hypervisor_num_iops":"0","hypervisor_io_bandwidth_kBps":"0","controller_num_write_iops":"0","total_io_time_usecs":"0","hypervisor_kvm_cpu_usage_ppm":"38620","content_cache_physical_ssd_usage_bytes":"0","controller_random_io_ppm":"-1","controller_avg_read_io_size_kbytes":"0","total_transformed_usage_bytes":"-1","avg_write_io_latency_usecs":"-1","num_read_io":"0","write_io_bandwidth_kBps":"0","hypervisor_read_io_bandwidth_kBps":"0","random_io_ppm":"-1","content_cache_num_hits":"0","total_untransformed_usage_bytes":"-1","hypervisor_total_io_time_usecs":"0","num_random_io":"-1","hypervisor_kvm_memory_usage_ppm":"83984","controller_avg_write_io_size_kbytes":"0","controller_avg_read_io_latency_usecs":"0","num_write_io":"0","hypervisor_esx_cpu_usage_ppm":"-1","total_io_size_kbytes":"0","io_bandwidth_kBps":"0","content_cache_physical_memory_usage_bytes":"79648","replication_num_received_bytes":"0","controller_timespan_usecs":"20000000","num_seq_io":"-1","content_cache_saved_memory_usage_bytes":"0","seq_io_ppm":"-1","write_io_ppm":"0","controller_avg_write_io_latency_usecs":"0","content_cache_logical_memory_usage_bytes":"79648"},"usageStats":{"data_reduction.overall.saving_ratio_ppm":"28509064","storage.reserved_free_bytes":"0","storage_tier.das-sata.usage_bytes":"0","data_reduction.compression.saved_bytes":"1072726016","data_reduction.saving_ratio_ppm":"1290781","data_reduction.erasure_coding.post_reduction_bytes":"3689119744","storage_tier.ssd.pinned_usage_bytes":"0","storage.reserved_usage_bytes":"0","data_reduction.erasure_coding.saving_ratio_ppm":"1000000","data_reduction.thin_provision.saved_bytes":"40170553344","storage_tier.das-sata.capacity_bytes":"28886593143110","storage_tier.das-sata.free_bytes":"28886593143110","storage.usage_bytes":"3689152512","data_reduction.erasure_coding.saved_bytes":"0","data_reduction.compression.pre_reduction_bytes":"4761845760","storage_tier.das-sata.pinned_bytes":"0","storage_tier.das-sata.pinned_usage_bytes":"0","data_reduction.pre_reduction_bytes":"4761845760","storage_tier.ssd.capacity_bytes":"3632235249662","data_reduction.clone.saved_bytes":"60240953344","storage_tier.ssd.free_bytes":"3628546097150","data_reduction.dedup.pre_reduction_bytes":"4732739584","data_reduction.erasure_coding.pre_reduction_bytes":"3689119744","storage.capacity_bytes":"32518828392772","data_reduction.dedup.post_reduction_bytes":"4732739584","data_reduction.clone.saving_ratio_ppm":"13728558","storage.logical_usage_bytes":"5551161344","data_reduction.saved_bytes":"1072726016","storage.free_bytes":"32515139240260","storage_tier.ssd.usage_bytes":"3689152512","data_reduction.compression.post_reduction_bytes":"3689119744","data_reduction.post_reduction_bytes":"3689119744","data_reduction.dedup.saved_bytes":"0","data_reduction.overall.saved_bytes":"101484232704","data_reduction.thin_provision.saving_ratio_ppm":"15454416","data_reduction.compression.saving_ratio_ppm":"1290781","data_reduction.dedup.saving_ratio_ppm":"1000000","storage_tier.ssd.pinned_bytes":"0","storage.reserved_capacity_bytes":"0"},"enforceRackableUnitAwarePlacement":false,"disableDegradedNodeMonitoring":false,"commonCriteriaMode":false,"enableOnDiskDedup":false,"managementServers":null}
'''

PYTHON_DICT = {'id': '00057f79-32a5-87e1-0000-0000000135e5::79333', 'uuid': '00057f79-32a5-87e1-0000-0000000135e5', 'clusterIncarnationId': 1547533401032673, 'clusterUuid': '00057f79-32a5-87e1-0000-0000000135e5', 'name': 'Training-02', 'clusterExternalIPAddress': '10.149.161.41', 'clusterExternalDataServicesIPAddress': None, 'timezone': 'Asia/Tokyo', 'supportVerbosityType': 'BASIC_COREDUMP', 'operationMode': 'Normal', 'storageType': 'mixed', 'clusterFunctions': ['NDFS'], 'numNodes': 4, 'blockSerials': ['15SM60370074'], 'version': '5.5.2', 'fullVersion': 'el7.3-release-euphrates-5.5.2-stable-6a19e52b0fc2293b18cf00c5cbc4f675145f1a6a', 'targetVersion': '5.5.2', 'externalSubnet': '10.149.160.0/255.255.252.0', 'internalSubnet': '192.168.5.0/255.255.255.128', 'nccVersion': 'ncc-3.5.1', 'enableLockDown': False, 'enablePasswordRemoteLoginToCluster': True, 'fingerprintContentCachePercentage': 100, 'ssdPinningPercentageLimit': 25, 'enableShadowClones': True, 'globalNfsWhiteList': [], 'nameServers': ['8.8.8.8'], 'ntpServers': ['ntp.nict.jp'], 'serviceCenters': [], 'httpProxies': [], 'rackableUnits': [{'id': 25, 'rackableUnitUuid': 'd0740b90-2885-47f4-ab36-4cf163276f9e', 'model': 'UseLayout', 'modelName': 'NX-3060-G4', 'location': None, 'serial': '15SM60370074', 'positions': ['1', '2', '3', '4'], 'nodes': [6, 7, 8, 13433], 'nodeUuids': ['50e41f34-2304-4636-aa57-f2e653e2c310', 'e528b902-2f74-412c-bdf9-7fdc3ecd085e', '59c9561d-13c3-49a2-94d4-5261b521dfa6', '0c633e50-4a16-4a9e-982d-f376a59387d1']}], 'publicKeys': [], 'smtpServer': None, 'hypervisorTypes': ['kKvm'], 'clusterRedundancyState': {'currentRedundancyFactor': 2, 'desiredRedundancyFactor': 2, 'redundancyStatus': {'kCassandraPrepareDone': True, 'kZookeeperPrepareDone': True}}, 'multicluster': False, 'cloudcluster': False, 'hasSelfEncryptingDrive': False, 'isUpgradeInProgress': False, 'securityComplianceConfig': {'schedule': 'DAILY', 'enableAide': False, 'enableCore': False, 'enableHighStrengthPassword': False, 'enableBanner': False, 'enableSNMPv3Only': False}, 'hypervisorSecurityComplianceConfig': {'schedule': 'DAILY', 'enableAide': False, 'enableCore': False, 'enableHighStrengthPassword': False, 'enableBanner': False}, 'hypervisorLldpConfig': {'enableLldpTx': False}, 'clusterArch': 'X86_64', 'isSspEnabled': False, 'iscsiConfig': None, 'domain': None, 'nosClusterAndHostsDomainJoined': False, 'allHypervNodesInFailoverCluster': False, 'credential': None, 'stats': {'hypervisor_avg_io_latency_usecs': '0', 'num_read_iops': '0', 'hypervisor_write_io_bandwidth_kBps': '0', 'timespan_usecs': '30000000', 'controller_num_read_iops': '0', 'read_io_ppm': '0', 'controller_num_iops': '0', 'total_read_io_time_usecs': '-1', 'controller_total_read_io_time_usecs': '0', 'replication_transmitted_bandwidth_kBps': '0', 'hypervisor_num_io': '0', 'controller_total_transformed_usage_bytes': '-1', 'hypervisor_cpu_usage_ppm': '38620', 'controller_num_write_io': '0', 'avg_read_io_latency_usecs': '-1', 'content_cache_logical_ssd_usage_bytes': '0', 'controller_total_io_time_usecs': '0', 'controller_total_read_io_size_kbytes': '0', 'controller_num_seq_io': '-1', 'controller_read_io_ppm': '0', 'content_cache_num_lookups': '0', 'controller_total_io_size_kbytes': '0', 'content_cache_hit_ppm': '0', 'controller_num_io': '0', 'hypervisor_avg_read_io_latency_usecs': '0', 'content_cache_num_dedup_ref_count_pph': '100', 'num_write_iops': '0', 'controller_num_random_io': '-1', 'num_iops': '0', 'replication_received_bandwidth_kBps': '0', 'hypervisor_num_read_io': '0', 'hypervisor_total_read_io_time_usecs': '0', 'controller_avg_io_latency_usecs': '0', 'hypervisor_hyperv_cpu_usage_ppm': '-1', 'num_io': '0', 'controller_num_read_io': '0', 'hypervisor_num_write_io': '0', 'controller_seq_io_ppm': '-1', 'controller_read_io_bandwidth_kBps': '0', 'controller_io_bandwidth_kBps': '0', 'hypervisor_hyperv_memory_usage_ppm': '-1', 'hypervisor_timespan_usecs': '30000000', 'hypervisor_num_write_iops': '0', 'replication_num_transmitted_bytes': '0', 'total_read_io_size_kbytes': '0', 'hypervisor_total_io_size_kbytes': '0', 'avg_io_latency_usecs': '0', 'hypervisor_num_read_iops': '0', 'content_cache_saved_ssd_usage_bytes': '0', 'controller_write_io_bandwidth_kBps': '0', 'controller_write_io_ppm': '0', 'hypervisor_avg_write_io_latency_usecs': '0', 'hypervisor_total_read_io_size_kbytes': '0', 'read_io_bandwidth_kBps': '0', 'hypervisor_esx_memory_usage_ppm': '-1', 'hypervisor_memory_usage_ppm': '83984', 'hypervisor_num_iops': '0', 'hypervisor_io_bandwidth_kBps': '0', 'controller_num_write_iops': '0', 'total_io_time_usecs': '0', 'hypervisor_kvm_cpu_usage_ppm': '38620', 'content_cache_physical_ssd_usage_bytes': '0', 'controller_random_io_ppm': '-1', 'controller_avg_read_io_size_kbytes': '0', 'total_transformed_usage_bytes': '-1', 'avg_write_io_latency_usecs': '-1', 'num_read_io': '0', 'write_io_bandwidth_kBps': '0', 'hypervisor_read_io_bandwidth_kBps': '0', 'random_io_ppm': '-1', 'content_cache_num_hits': '0', 'total_untransformed_usage_bytes': '-1', 'hypervisor_total_io_time_usecs': '0', 'num_random_io': '-1', 'hypervisor_kvm_memory_usage_ppm': '83984', 'controller_avg_write_io_size_kbytes': '0', 'controller_avg_read_io_latency_usecs': '0', 'num_write_io': '0', 'hypervisor_esx_cpu_usage_ppm': '-1', 'total_io_size_kbytes': '0', 'io_bandwidth_kBps': '0', 'content_cache_physical_memory_usage_bytes': '79648', 'replication_num_received_bytes': '0', 'controller_timespan_usecs': '20000000', 'num_seq_io': '-1', 'content_cache_saved_memory_usage_bytes': '0', 'seq_io_ppm': '-1', 'write_io_ppm': '0', 'controller_avg_write_io_latency_usecs': '0', 'content_cache_logical_memory_usage_bytes': '79648'}, 'usageStats': {'data_reduction.overall.saving_ratio_ppm': '28509064', 'storage.reserved_free_bytes': '0', 'storage_tier.das-sata.usage_bytes': '0', 'data_reduction.compression.saved_bytes': '1072726016', 'data_reduction.saving_ratio_ppm': '1290781', 'data_reduction.erasure_coding.post_reduction_bytes': '3689119744', 'storage_tier.ssd.pinned_usage_bytes': '0', 'storage.reserved_usage_bytes': '0', 'data_reduction.erasure_coding.saving_ratio_ppm': '1000000', 'data_reduction.thin_provision.saved_bytes': '40170553344', 'storage_tier.das-sata.capacity_bytes': '28886593143110', 'storage_tier.das-sata.free_bytes': '28886593143110', 'storage.usage_bytes': '3689152512', 'data_reduction.erasure_coding.saved_bytes': '0', 'data_reduction.compression.pre_reduction_bytes': '4761845760', 'storage_tier.das-sata.pinned_bytes': '0', 'storage_tier.das-sata.pinned_usage_bytes': '0', 'data_reduction.pre_reduction_bytes': '4761845760', 'storage_tier.ssd.capacity_bytes': '3632235249662', 'data_reduction.clone.saved_bytes': '60240953344', 'storage_tier.ssd.free_bytes': '3628546097150', 'data_reduction.dedup.pre_reduction_bytes': '4732739584', 'data_reduction.erasure_coding.pre_reduction_bytes': '3689119744', 'storage.capacity_bytes': '32518828392772', 'data_reduction.dedup.post_reduction_bytes': '4732739584', 'data_reduction.clone.saving_ratio_ppm': '13728558', 'storage.logical_usage_bytes': '5551161344', 'data_reduction.saved_bytes': '1072726016', 'storage.free_bytes': '32515139240260', 'storage_tier.ssd.usage_bytes': '3689152512', 'data_reduction.compression.post_reduction_bytes': '3689119744', 'data_reduction.post_reduction_bytes': '3689119744', 'data_reduction.dedup.saved_bytes': '0', 'data_reduction.overall.saved_bytes': '101484232704', 'data_reduction.thin_provision.saving_ratio_ppm': '15454416', 'data_reduction.compression.saving_ratio_ppm': '1290781', 'data_reduction.dedup.saving_ratio_ppm': '1000000', 'storage_tier.ssd.pinned_bytes': '0', 'storage.reserved_capacity_bytes': '0'}, 'enforceRackableUnitAwarePlacement': False, 'disableDegradedNodeMonitoring': False, 'commonCriteriaMode': False, 'enableOnDiskDedup': False, 'managementServers': None}


# (1) JSON_TEXT(text data of json) to python dict
python_dict_01 = json.loads(JSON_TEXT)
print('(1) JSON Text -> Python dict')
print(python_dict_01)
print()


# (2) PYTHON_DICT(python dict object) to text data
json_text_02 = json.dumps(PYTHON_DICT)
print('(2) Python dict -> JSON Text')
print(json_text_02)
print()


# (3) PYTHON_DICT(python dict object) to text data with indent formatting
json_text_03 = json.dumps(PYTHON_DICT, indent=2)
print('(3) Python dict -> JSON Text with indenting')
print(json_text_03)
print()


# (4) Get JSON Value
json_text_04 = '''
{
  "id": "00057f79-32a5-87e1-0000-0000000135e5::79333",
  "uuid": "00057f79-32a5-87e1-0000-0000000135e5",
  "clusterIncarnationId": 1547533401032673,
  "clusterUuid": "00057f79-32a5-87e1-0000-0000000135e5",
  "name": "Training-02",
  "clusterExternalIPAddress": "10.149.161.41",
  "clusterExternalDataServicesIPAddress": null,
  "timezone": "Asia/Tokyo",
  "supportVerbosityType": "BASIC_COREDUMP",
  "operationMode": "Normal",
  "storageType": "mixed",
  "clusterRedundancyState": {
    "currentRedundancyFactor": 2,
    "desiredRedundancyFactor": 2,
    "redundancyStatus": {
      "kCassandraPrepareDone": true,
      "kZookeeperPrepareDone": true
    }
  }
}
'''
d = json.loads(json_text_04)
name = d['name']
redundancy_factor = d['clusterRedundancyState']['currentRedundancyFactor']
print('(4) Get JSON Values by choosing keys')
print(name)
print(redundancy_factor)
print()


# (5) list loop
print('(5) List Loop')
a = [1, 2, 3, 4, 5]
for item in a:
  print(item)
print()


# (6) dict loop
print('(6) 3 Type of Dict Loop')
b = {'a':'apple', 'b':'banana', 'c':'candy'}
for key in b:
  print(key)
print()

for value in b.values():
  print(value)
print()

for (key, value) in b.items():
  print('{} : {}'.format(key, value))
print()


# (7) Get JSON Values from inner-list and inner-dict
json_text_07 = '''
{
  "id": "00057f79-32a5-87e1-0000-0000000135e5::79333",
  "uuid": "00057f79-32a5-87e1-0000-0000000135e5",
  "blockSerials": [
    "15SM60370074",
    "15SM60370075",
    "15SM60370076"
  ],
  "clusterRedundancyState": {
    "currentRedundancyFactor": 2,
    "desiredRedundancyFactor": 2
  }
}
'''
d = json.loads(json_text_07)
print('(7-1)')
for block_serial in d['blockSerials']:
  print(block_serial)
print()

print('(7-2)')
for (key, value) in d['clusterRedundancyState'].items():
  print('{} : {}'.format(key, value))
