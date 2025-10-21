"""
Unit tests for IoT Hardware Automation system
"""

import pytest
from src.models import Node, Endpoint, HardwareType, VersionArtifact
from src.augury_api import AuguryAPI


@pytest.fixture
def endpoint_factory():
    """Factory fixture for creating endpoints with different parameters"""
    def _create_endpoint(hw_type, serial_suffix="001", battery=3000, uuid_suffix="TEST001"):
        return Endpoint(
            f"{hw_type.value}_{serial_suffix}", 
            battery, 
            hw_type, 
            f"{hw_type.value}_{uuid_suffix}", 
            "1.0"
        )
    return _create_endpoint


@pytest.fixture
def node_factory():
    """Factory fixture for creating nodes with different parameters"""
    def _create_node(hw_type, uuid_suffix="TEST001", version="33", endpoints=None):
        if endpoints is None:
            endpoints = [
                Endpoint(f"{hw_type.value}_001", 3000, hw_type, f"{hw_type.value}_{uuid_suffix}", "1.0")
            ]
        return Node(f"{hw_type.value}_{uuid_suffix}", hw_type, version, endpoints)
    return _create_node


@pytest.fixture
def sample_endpoint(endpoint_factory):
    """Fixture for creating a sample endpoint"""
    return endpoint_factory(HardwareType.EP1)


@pytest.fixture
def sample_node(node_factory):
    """Fixture for creating a sample node"""
    return node_factory(HardwareType.AHN2)


@pytest.fixture
def api():
    """Fixture for creating AuguryAPI instance"""
    return AuguryAPI()


class TestEndpoint:
    """Test cases for Endpoint class"""
    
    def test_endpoint_creation(self, endpoint_factory):
        """Test endpoint creation with valid data"""
        endpoint = endpoint_factory(HardwareType.EP1)
        assert endpoint.serial_number == "EP1_001"
        assert endpoint.battery == 3000
        assert endpoint.hardware_type == HardwareType.EP1
        assert endpoint.version == "1.0"
    
    @pytest.mark.parametrize("hardware_type,expected_threshold", [
        (HardwareType.EP1, 2500),
        (HardwareType.EP2, 2500),
        (HardwareType.CANARY, 3600),
    ])
    def test_battery_threshold(self, endpoint_factory, hardware_type, expected_threshold):
        """Test battery thresholds for different hardware types"""
        endpoint = endpoint_factory(hardware_type)
        assert endpoint.battery_threshold == expected_threshold
    
    @pytest.mark.parametrize("backlog,battery,expected", [
        (5, 3000, False),    # backlog > 0
        (0, 2000, False),   # battery below threshold
        (0, 3000, True),    # valid conditions
    ])
    def test_can_update_conditions(self, endpoint_factory, backlog, battery, expected):
        """Test can_update under different conditions"""
        endpoint = endpoint_factory(HardwareType.EP1, battery=battery)
        endpoint.backlog = backlog
        assert endpoint.can_update == expected


class TestNode:
    """Test cases for Node class"""
    
    def test_node_creation(self, node_factory):
        """Test node creation with valid data"""
        node = node_factory(HardwareType.AHN2)
        assert node.uuid == "AHN2_TEST001"
        assert node.hardware_type == HardwareType.AHN2
        assert node.version == "33"
        assert len(node.endpoints) == 1
    
    def test_ota_channel_format(self, node_factory):
        """Test OTA channel format"""
        node = node_factory(HardwareType.AHN2)
        assert node.ota_channel == "OTA_AHN2_TEST001"
    
    @pytest.mark.parametrize("hardware_type,expected_endpoint", [
        (HardwareType.AHN2, "buildroot_api.azure"),
        (HardwareType.CASSIA, "buildroot_api.azure"),
        (HardwareType.MOXA, "moxa_api.azure"),
    ])
    def test_api_endpoints(self, node_factory, hardware_type, expected_endpoint):
        """Test API endpoints for different hardware types"""
        node = node_factory(hardware_type)
        assert node.api_endpoint == expected_endpoint
    
    def test_get_endpoint_by_serial(self, node_factory):
        """Test getting endpoint by serial number"""
        node = node_factory(HardwareType.AHN2)
        endpoint = node.get_endpoint_by_serial("AHN2_001")
        assert endpoint is not None
        assert endpoint.serial_number == "AHN2_001"
        
        endpoint = node.get_endpoint_by_serial("EP3_001")
        assert endpoint is None
    
    @pytest.mark.parametrize("version,expected_result", [
        ("34", True),
        ("abc", False),
        ("32", False),  # lower version
    ])
    def test_update_version(self, node_factory, version, expected_result):
        """Test version updates with different inputs"""
        node = node_factory(HardwareType.AHN2)
        original_version = node.version
        result = node.update_version(version)
        assert result == expected_result
        
        if expected_result:
            assert node.version == version
        else:
            assert node.version == original_version


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
