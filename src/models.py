"""
IoT Hardware Automation Domain Models
Contains Node, Endpoint, and related classes
"""

from typing import List, Optional
from dataclasses import dataclass
from enum import Enum


class HardwareType(Enum):
    """Hardware types for nodes and endpoints"""
    AHN2 = "AHN2"
    CASSIA = "Cassia"
    MOXA = "Moxa"
    EP1 = "EP1"
    EP2 = "EP2"
    CANARY = "Canary_A"


@dataclass
class Endpoint:
    """Represents an IoT endpoint (sensor)"""
    serial_number: str
    battery: int
    hardware_type: HardwareType
    uuid: str
    version: str
    backlog: int = 0
    
    @property
    def battery_threshold(self) -> int:
        """Returns battery threshold based on hardware type"""
        if self.hardware_type in [HardwareType.EP1, HardwareType.EP2]:
            return 2500
        elif self.hardware_type == HardwareType.CANARY:
            return 3600
        return 2500  # default
    
    @property
    def can_update(self) -> bool:
        """Checks if endpoint can be updated (backlog=0 and battery above threshold)"""
        return self.backlog == 0 and self.battery >= self.battery_threshold


@dataclass
class Node:
    """Represents an IoT node (gateway)"""
    uuid: str
    hardware_type: HardwareType
    version: str
    endpoints: List[Endpoint]
    
    @property
    def ota_channel(self) -> str:
        """Returns OTA channel name for this node"""
        return f"OTA_{self.uuid}"
    
    @property
    def api_endpoint(self) -> str:
        """Returns API endpoint based on hardware type"""
        if self.hardware_type in [HardwareType.AHN2, HardwareType.CASSIA]:
            return "buildroot_api.azure"
        elif self.hardware_type == HardwareType.MOXA:
            return "moxa_api.azure"
        return "default_api.azure"
    
    def get_endpoint_by_serial(self, serial_number: str) -> Optional[Endpoint]:
        """Get endpoint by serial number"""
        for ep in self.endpoints:
            if ep.serial_number == serial_number:
                return ep
        return None
    
    def update_version(self, new_version: str) -> bool:
        """Update node version"""
        try:
            # Validate version format
            if not self._is_valid_version(new_version):
                return False
            self.version = new_version
            return True
        except Exception:
            return False
    
    def _is_valid_version(self, version: str) -> bool:
        """Validate version format"""
        try:
            version_num = int(version)
            return version_num > 0
        except ValueError:
            return False


@dataclass
class VersionArtifact:
    """Represents a version artifact for OTA/DFU"""
    hardware_type: HardwareType
    version: str
    
    @property
    def artifact_name(self) -> str:
        """Returns artifact name in required format"""
        return f"{self.hardware_type.value.lower()}_{self.version}.swu"
