"""
Unit tests for IoT Hardware Automation system
"""

import pytest
from src.models import Node, Endpoint, HardwareType, VersionArtifact
from src.augury_api import AuguryAPI


class TestEndpoint:
    """Test cases for Endpoint class"""
    
    def test_endpoint_creation(self):
        """Test endpoint creation with valid data"""
        endpoint = Endpoint("EP1_001", 3000, HardwareType.EP1, "AHN2_TBCDB1045001", "1.0")
        assert endpoint.serial_number == "EP1_001"
        assert endpoint.battery == 3000
        assert endpoint.hardware_type == HardwareType.EP1
        assert endpoint.version == "1.0"
    
    def test_battery_threshold_ep1(self):
        """Test battery threshold for EP1"""
        endpoint = Endpoint("EP1_001", 3000, HardwareType.EP1, "AHN2_TBCDB1045001", "1.0")
        assert endpoint.battery_threshold == 2500
    
    def test_battery_threshold_ep2(self):
        """Test battery threshold for EP2"""
        endpoint = Endpoint("EP2_001", 3000, HardwareType.EP2, "AHN2_TBCDB1045001", "1.0")
        assert endpoint.battery_threshold == 2500
    
    def test_battery_threshold_canary(self):
        """Test battery threshold for Canary"""
        endpoint = Endpoint("Canary_001", 3000, HardwareType.CANARY, "AHN2_TBCDB1045001", "1.0")
        assert endpoint.battery_threshold == 3600
    
    def test_can_update_with_backlog(self):
        """Test can_update when backlog > 0"""
        endpoint = Endpoint("EP1_001", 3000, HardwareType.EP1, "AHN2_TBCDB1045001", "1.0")
        endpoint.backlog = 5
        assert not endpoint.can_update
    
    def test_can_update_with_low_battery(self):
        """Test can_update when battery below threshold"""
        endpoint = Endpoint("EP1_001", 2000, HardwareType.EP1, "AHN2_TBCDB1045001", "1.0")
        assert not endpoint.can_update
    
    def test_can_update_valid(self):
        """Test can_update when conditions are met"""
        endpoint = Endpoint("EP1_001", 3000, HardwareType.EP1, "AHN2_TBCDB1045001", "1.0")
        endpoint.backlog = 0
        assert endpoint.can_update


class TestNode:
    """Test cases for Node class"""
    
    def test_node_creation(self):
        """Test node creation with valid data"""
        endpoints = [
            Endpoint("EP1_001", 3000, HardwareType.EP1, "AHN2_TBCDB1045001", "1.0")
        ]
        node = Node("AHN2_TBCDB1045001", HardwareType.AHN2, "33", endpoints)
        assert node.uuid == "AHN2_TBCDB1045001"
        assert node.hardware_type == HardwareType.AHN2
        assert node.version == "33"
        assert len(node.endpoints) == 1
    
    def test_ota_channel_format(self):
        """Test OTA channel format"""
        endpoints = []
        node = Node("AHN2_TBCDB1045001", HardwareType.AHN2, "33", endpoints)
        assert node.ota_channel == "OTA_AHN2_TBCDB1045001"
    
    def test_api_endpoint_ahn2(self):
        """Test API endpoint for AHN2"""
        endpoints = []
        node = Node("AHN2_TBCDB1045001", HardwareType.AHN2, "33", endpoints)
        assert node.api_endpoint == "buildroot_api.azure"
    
    def test_api_endpoint_cassia(self):
        """Test API endpoint for Cassia"""
        endpoints = []
        node = Node("Cassia_TBCDB1045002", HardwareType.CASSIA, "33", endpoints)
        assert node.api_endpoint == "buildroot_api.azure"
    
    def test_api_endpoint_moxa(self):
        """Test API endpoint for Moxa"""
        endpoints = []
        node = Node("MOXA_TBCDB1045003", HardwareType.MOXA, "33", endpoints)
        assert node.api_endpoint == "moxa_api.azure"
    
    def test_get_endpoint_by_serial(self):
        """Test getting endpoint by serial number"""
        endpoints = [
            Endpoint("EP1_001", 3000, HardwareType.EP1, "AHN2_TBCDB1045001", "1.0"),
            Endpoint("EP2_001", 2800, HardwareType.EP2, "AHN2_TBCDB1045001", "1.0")
        ]
        node = Node("AHN2_TBCDB1045001", HardwareType.AHN2, "33", endpoints)
        
        endpoint = node.get_endpoint_by_serial("EP1_001")
        assert endpoint is not None
        assert endpoint.serial_number == "EP1_001"
        
        endpoint = node.get_endpoint_by_serial("EP3_001")
        assert endpoint is None
    
    def test_update_version_valid(self):
        """Test valid version update"""
        endpoints = []
        node = Node("AHN2_TBCDB1045001", HardwareType.AHN2, "33", endpoints)
        result = node.update_version("34")
        assert result is True
        assert node.version == "34"
    
    def test_update_version_invalid(self):
        """Test invalid version update"""
        endpoints = []
        node = Node("AHN2_TBCDB1045001", HardwareType.AHN2, "33", endpoints)
        result = node.update_version("abc")
        assert result is False
        assert node.version == "33"  # Should remain unchanged


class TestAuguryAPI:
    """Test cases for AuguryAPI class"""
    
    def test_api_initialization(self):
        """Test API initialization"""
        api = AuguryAPI()
        assert len(api._nodes) == 3
        assert "AHN2_TBCDB1045001" in api._nodes
        assert "Cassia_TBCDB1045002" in api._nodes
        assert "MOXA_TBCDB1045003" in api._nodes
    
    def test_get_endpoint_by_serial(self):
        """Test getting endpoint by serial number"""
        api = AuguryAPI()
        result = api.api_get_endpoint_by_serial("EP1_001")
        assert result["serial_number"] == "EP1_001"
        assert result["hardware_type"] == "EP1"
    
    def test_get_endpoint_by_serial_not_found(self):
        """Test getting non-existent endpoint"""
        api = AuguryAPI()
        result = api.api_get_endpoint_by_serial("EP999_001")
        assert result == {}
    
    def test_get_node_by_uuid(self):
        """Test getting node by UUID"""
        api = AuguryAPI()
        result = api.api_get_node_by_uuid("AHN2_TBCDB1045001")
        assert result["uuid"] == "AHN2_TBCDB1045001"
        assert result["version"] == "33"
        assert len(result["endpoints"]) == 3
    
    def test_get_node_by_uuid_not_found(self):
        """Test getting non-existent node"""
        api = AuguryAPI()
        result = api.api_get_node_by_uuid("NONEXISTENT_UUID")
        assert result == {}
    
    def test_post_version_to_ota_channel_valid(self):
        """Test posting valid version to OTA channel"""
        api = AuguryAPI()
        result = api.api_post_version_to_ota_channel("OTA_AHN2_TBCDB1045001", "ahn2_34.swu")
        assert result == 200
    
    def test_post_version_to_ota_channel_invalid(self):
        """Test posting invalid version to OTA channel"""
        api = AuguryAPI()
        result = api.api_post_version_to_ota_channel("OTA_AHN2_TBCDB1045001", "invalid_format.swu")
        assert result == 400
    
    def test_clear_ota_channel(self):
        """Test clearing OTA channel"""
        api = AuguryAPI()
        ota_channel = "OTA_AHN2_TBCDB1045001"
        
        # Add version first
        api.api_post_version_to_ota_channel(ota_channel, "ahn2_34.swu")
        
        # Clear version
        result = api.api_clear_ota_channel(ota_channel, "ahn2_34.swu")
        assert result == 200
        
        # Verify version is removed
        versions = api.get_ota_channel_versions(ota_channel)
        assert "ahn2_34.swu" not in versions
    
    def test_simulate_ota_update_success(self):
        """Test successful OTA update"""
        api = AuguryAPI()
        ota_channel = "OTA_AHN2_TBCDB1045001"
        
        # Add version to channel
        api.api_post_version_to_ota_channel(ota_channel, "ahn2_34.swu")
        
        # Simulate update
        result = api.simulate_ota_update("AHN2_TBCDB1045001", "34")
        assert result is True
        
        # Verify version updated
        node_info = api.api_get_node_by_uuid("AHN2_TBCDB1045001")
        assert node_info["version"] == "34"
    
    def test_simulate_endpoint_dfu_success(self):
        """Test successful endpoint DFU"""
        api = AuguryAPI()
        
        # Set backlog to 0 and battery above threshold
        api.set_endpoint_backlog("EP1_001", 0)
        api.set_endpoint_battery("EP1_001", 3000)
        
        # Simulate DFU
        result = api.simulate_endpoint_dfu("EP1_001", "2.0")
        assert result is True
        
        # Verify version updated
        endpoint_info = api.api_get_endpoint_by_serial("EP1_001")
        assert endpoint_info["version"] == "2.0"
    
    def test_simulate_endpoint_dfu_with_backlog(self):
        """Test endpoint DFU with backlog"""
        api = AuguryAPI()
        
        # Set backlog > 0
        api.set_endpoint_backlog("EP1_001", 5)
        
        # Simulate DFU (should fail)
        result = api.simulate_endpoint_dfu("EP1_001", "2.0")
        assert result is False
    
    def test_simulate_endpoint_dfu_low_battery(self):
        """Test endpoint DFU with low battery"""
        api = AuguryAPI()
        
        # Set battery below threshold
        api.set_endpoint_battery("EP1_001", 2000)
        api.set_endpoint_backlog("EP1_001", 0)
        
        # Simulate DFU (should fail)
        result = api.simulate_endpoint_dfu("EP1_001", "2.0")
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__])
