#!/usr/bin/env python3
"""
Demo script for IoT Hardware Automation system
Shows basic usage of the AuguryAPI
"""

from src.augury_api import AuguryAPI


def main():
    """Demo the IoT Hardware Automation system"""
    print("IoT Hardware Automation System Demo")
    print("===================================")
    
    # Initialize the API
    api = AuguryAPI()
    print("AuguryAPI initialized")
    
    # Show available nodes
    print("\n📡 Available Nodes:")
    for uuid in api._nodes.keys():
        node_info = api.api_get_node_by_uuid(uuid)
        print(f"  - {node_info['uuid']} (Version: {node_info['version']})")
        print(f"    OTA Channel: {node_info['ota_channel']}")
        print(f"    Endpoints: {len(node_info['endpoints'])}")
    
    # Show available endpoints
    print("\n🔌 Available Endpoints:")
    for uuid, node in api._nodes.items():
        for endpoint in node.endpoints:
            endpoint_info = api.api_get_endpoint_by_serial(endpoint.serial_number)
            print(f"  - {endpoint_info['serial_number']} (Battery: {endpoint_info['battery']}mA, Version: {endpoint_info['version']})")
    
    # Demo OTA update
    print("\n🔄 OTA Update Demo:")
    node_uuid = "AHN2_TBCDB1045001"
    ota_channel = f"OTA_{node_uuid}"
    
    # Get current version
    node_info = api.api_get_node_by_uuid(node_uuid)
    print(f"Current version: {node_info['version']}")
    
    # Upload new version
    version_artifact = "ahn2_34.swu"
    result = api.api_post_version_to_ota_channel(ota_channel, version_artifact)
    print(f"Upload result: {result}")
    
    # Simulate OTA update
    update_success = api.simulate_ota_update(node_uuid, "34")
    print(f"OTA update success: {update_success}")
    
    # Verify update
    updated_node_info = api.api_get_node_by_uuid(node_uuid)
    print(f"New version: {updated_node_info['version']}")
    
    # Demo Endpoint DFU
    print("\n🔧 Endpoint DFU Demo:")
    endpoint_serial = "EP1_001"
    
    # Get current endpoint info
    endpoint_info = api.api_get_endpoint_by_serial(endpoint_serial)
    print(f"Endpoint {endpoint_serial}:")
    print(f"  Battery: {endpoint_info['battery']}mA (Threshold: {endpoint_info.get('battery_threshold', 'N/A')}mA)")
    print(f"  Backlog: {endpoint_info['backlog']}")
    print(f"  Version: {endpoint_info['version']}")
    
    # Set backlog to 0 for update
    api.set_endpoint_backlog(endpoint_serial, 0)
    
    # Simulate DFU
    dfu_success = api.simulate_endpoint_dfu(endpoint_serial, "2.0")
    print(f"DFU update success: {dfu_success}")
    
    # Verify update
    updated_endpoint_info = api.api_get_endpoint_by_serial(endpoint_serial)
    print(f"New version: {updated_endpoint_info['version']}")
    
    # Demo error handling
    print("\nError Handling Demo:")
    
    # Try invalid artifact
    invalid_result = api.api_post_version_to_ota_channel(ota_channel, "invalid_format.swu")
    print(f"Invalid artifact upload result: {invalid_result}")
    
    # Try DFU with backlog
    api.set_endpoint_backlog(endpoint_serial, 5)
    dfu_with_backlog = api.simulate_endpoint_dfu(endpoint_serial, "3.0")
    print(f"DFU with backlog result: {dfu_with_backlog}")
    
    print("\nDemo completed successfully!")
    print("\nTo run the full test suite:")
    print("  python run_tests.py")
    print("\nTo run Robot Framework tests:")
    print("  robot robot_tests/")


if __name__ == "__main__":
    main()
