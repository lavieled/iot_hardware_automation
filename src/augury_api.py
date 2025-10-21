"""
AuguryAPI - Fake API for IoT Hardware Automation
Implements the required API methods for the system
"""

from typing import Dict, List, Optional
from src.models import Node, Endpoint, HardwareType, VersionArtifact


class AuguryAPI:
    """Fake API for IoT system operations"""
    
    def __init__(self):
        """Initialize the API with sample data"""
        self._nodes = self._create_sample_nodes()
        self._ota_channels = {}  # ota_channel -> list of version artifacts
        self._retry_count = 0
        self._max_retries = 3
    
    def _create_sample_nodes(self) -> Dict[str, Node]:
        """Create sample nodes with endpoints"""
        nodes = {}
        
        # Create AHN2 node
        ahn2_endpoints = [
            Endpoint("EP1_001", 3000, HardwareType.EP1, "AHN2_TBCDB1045001", "1.0"),
            Endpoint("EP2_001", 2800, HardwareType.EP2, "AHN2_TBCDB1045001", "1.0"),
            Endpoint("Canary_001", 3800, HardwareType.CANARY, "AHN2_TBCDB1045001", "1.0")
        ]
        nodes["AHN2_TBCDB1045001"] = Node("AHN2_TBCDB1045001", HardwareType.AHN2, "33", ahn2_endpoints)
        
        # Create Cassia node
        cassia_endpoints = [
            Endpoint("EP1_002", 2600, HardwareType.EP1, "Cassia_TBCDB1045002", "1.0"),
            Endpoint("EP2_002", 2400, HardwareType.EP2, "Cassia_TBCDB1045002", "1.0"),
            Endpoint("Canary_002", 3700, HardwareType.CANARY, "Cassia_TBCDB1045002", "1.0")
        ]
        nodes["Cassia_TBCDB1045002"] = Node("Cassia_TBCDB1045002", HardwareType.CASSIA, "33", cassia_endpoints)
        
        # Create Moxa node
        moxa_endpoints = [
            Endpoint("EP1_003", 2900, HardwareType.EP1, "MOXA_TBCDB1045003", "1.0"),
            Endpoint("EP2_003", 2700, HardwareType.EP2, "MOXA_TBCDB1045003", "1.0"),
            Endpoint("Canary_003", 3900, HardwareType.CANARY, "MOXA_TBCDB1045003", "1.0")
        ]
        nodes["MOXA_TBCDB1045003"] = Node("MOXA_TBCDB1045003", HardwareType.MOXA, "33", moxa_endpoints)
        
        return nodes
    
    def api_get_endpoint_by_serial(self, serial_number: str) -> Dict:
        """Get endpoint information by serial number"""
        for node in self._nodes.values():
            endpoint = node.get_endpoint_by_serial(serial_number)
            if endpoint:
                return {
                    "serial_number": endpoint.serial_number,
                    "battery": endpoint.battery,
                    "hardware_type": endpoint.hardware_type.value,
                    "uuid": endpoint.uuid,
                    "version": endpoint.version,
                    "backlog": endpoint.backlog
                }
        return {}
    
    def api_get_node_by_uuid(self, uuid: str) -> Dict:
        """Get node information by UUID"""
        node = self._nodes.get(uuid)
        if node:
            return {
                "uuid": node.uuid,
                "ota_channel": node.ota_channel,
                "version": node.version,
                "endpoints": [
                    {
                        "serial_number": ep.serial_number,
                        "battery": ep.battery,
                        "hardware_type": ep.hardware_type.value,
                        "uuid": ep.uuid,
                        "version": ep.version,
                        "backlog": ep.backlog
                    }
                    for ep in node.endpoints
                ]
            }
        return {}
    
    def api_post_version_to_ota_channel(self, ota_channel: str, version_artifact: str) -> int:
        """Add new version to OTA channel"""
        try:
            if ota_channel not in self._ota_channels:
                self._ota_channels[ota_channel] = []
            
            # Validate artifact format
            if not self._is_valid_artifact(version_artifact):
                return 400
            
            self._ota_channels[ota_channel].append(version_artifact)
            return 200
        except Exception:
            return 400
    
    def api_clear_ota_channel(self, ota_channel: str, version_artifact: str) -> int:
        """Clear an artifact from the OTA channel"""
        try:
            if ota_channel in self._ota_channels:
                if version_artifact in self._ota_channels[ota_channel]:
                    self._ota_channels[ota_channel].remove(version_artifact)
                    return 200
            return 400
        except Exception:
            return 400
    
    def _is_valid_artifact(self, artifact: str) -> bool:
        """Validate artifact format"""
        try:
            if not artifact.endswith('.swu'):
                return False
            parts = artifact.split('_')
            if len(parts) != 2:
                return False
            version_part = parts[1].replace('.swu', '')
            int(version_part)  # Check if version is number
            return True
        except (ValueError, IndexError):
            return False
    
    def simulate_ota_update(self, uuid: str, target_version: str) -> bool:
        """Simulate OTA update process with retries"""
        node = self._nodes.get(uuid)
        if not node:
            return False
        
        # Check if version exists in OTA channel
        ota_channel = node.ota_channel
        if ota_channel not in self._ota_channels:
            return False
        
        # Find matching artifact
        target_artifact = None
        for artifact in self._ota_channels[ota_channel]:
            if artifact.endswith(f"_{target_version}.swu"):
                target_artifact = artifact
                break
        
        if not target_artifact:
            return False
        
        # Simulate retry logic
        self._retry_count = 0
        while self._retry_count < self._max_retries:
            self._retry_count += 1
            # Simulate update process
            if self._perform_update(node, target_version):
                return True
        
        return False
    
    def _perform_update(self, node: Node, version: str) -> bool:
        """Perform the actual update"""
        try:
            # Validate version compatibility
            if not self._is_version_compatible(node, version):
                return False
            
            # Update node version
            node.version = version
            return True
        except Exception:
            return False
    
    def _is_version_compatible(self, node: Node, version: str) -> bool:
        """Check if version is compatible with node hardware type"""
        try:
            version_num = int(version)
            current_version = int(node.version)
            
            # Version should be newer than current
            if version_num <= current_version:
                return False
            
            # Check for a matching artifact for this hardware type
            ota_channel = node.ota_channel
            if ota_channel not in self._ota_channels:
                return False
            
            # Find matching artifact for this hardware type
            expected_prefix = f"{node.hardware_type.value.lower()}_{version}.swu"
            matching_artifact = None
            for artifact in self._ota_channels[ota_channel]:
                if artifact == expected_prefix:
                    matching_artifact = artifact
                    break
            
            # no matching artifact found, incompatible
            if not matching_artifact:
                return False
            
            return True
        except ValueError:
            return False
    
    def simulate_endpoint_dfu(self, serial_number: str, target_version: str) -> bool:
        """Simulate endpoint DFU process"""
        for node in self._nodes.values():
            endpoint = node.get_endpoint_by_serial(serial_number)
            if endpoint:
                # Check if endpoint can update
                if not endpoint.can_update:
                    return False
                
                # Perform update
                endpoint.version = target_version
                return True
        
        return False
    
    def set_endpoint_backlog(self, serial_number: str, backlog: int) -> bool:
        """Set endpoint backlog"""
        for node in self._nodes.values():
            endpoint = node.get_endpoint_by_serial(serial_number)
            if endpoint:
                endpoint.backlog = backlog
                return True
        return False
    
    def set_endpoint_battery(self, serial_number: str, battery: int) -> bool:
        """Set endpoint battery level"""
        for node in self._nodes.values():
            endpoint = node.get_endpoint_by_serial(serial_number)
            if endpoint:
                endpoint.battery = battery
                return True
        return False
    
    def get_ota_channel_versions(self, ota_channel: str) -> List[str]:
        """Get all versions in OTA channel"""
        return self._ota_channels.get(ota_channel, [])
    
    def reset_retry_count(self):
        """Reset retry count for testing"""
        self._retry_count = 0
