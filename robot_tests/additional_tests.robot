*** Settings ***
Documentation    Additional IoT Hardware Automation Test Scenarios
Library          Collections
Library          String
Library          BuiltIn

*** Variables ***
${AHN2_UUID}         AHN2_TBCDB1045001
${CASSIA_UUID}       Cassia_TBCDB1045002
${MOXA_UUID}         MOXA_TBCDB1045003

*** Test Cases ***
API Endpoint Validation Test
    [Documentation]    Test API endpoint validation for different node types
    [Tags]    api    validation
    
    ${api}=    Evaluate    __import__('src.augury_api', fromlist=['AuguryAPI']).AuguryAPI()
    
    # Test AHN2 API endpoint
    ${ahn2_info}=    Evaluate    $api.api_get_node_by_uuid('${AHN2_UUID}')
    Should Not Be Empty    ${ahn2_info}
    Should Be Equal    ${ahn2_info['uuid']}    ${AHN2_UUID}
    
    # Test Cassia API endpoint
    ${cassia_info}=    Evaluate    $api.api_get_node_by_uuid('${CASSIA_UUID}')
    Should Not Be Empty    ${cassia_info}
    Should Be Equal    ${cassia_info['uuid']}    ${CASSIA_UUID}
    
    # Test Moxa API endpoint
    ${moxa_info}=    Evaluate    $api.api_get_node_by_uuid('${MOXA_UUID}')
    Should Not Be Empty    ${moxa_info}
    Should Be Equal    ${moxa_info['uuid']}    ${MOXA_UUID}

OTA Channel Management Test
    [Documentation]    Test OTA channel management operations
    [Tags]    ota    channel_management
    
    ${api}=    Evaluate    __import__('src.augury_api', fromlist=['AuguryAPI']).AuguryAPI()
    ${ota_channel}=    Set Variable    OTA_${AHN2_UUID}
    
    # Clear channel initially
    ${clear_result}=    Evaluate    $api.api_clear_ota_channel('${ota_channel}', 'ahn2_34.swu')
    Should Be Equal    ${clear_result}    ${400}  # Should fail if not present
    
    # Add version to channel
    ${add_result}=    Evaluate    $api.api_post_version_to_ota_channel('${ota_channel}', 'ahn2_34.swu')
    Should Be Equal    ${add_result}    ${200}
    
    # Verify version is in channel
    ${versions}=    Evaluate    $api.get_ota_channel_versions('${ota_channel}')
    Should Contain    ${versions}    ahn2_34.swu
    
    # Clear version from channel
    ${clear_result}=    Evaluate    $api.api_clear_ota_channel('${ota_channel}', 'ahn2_34.swu')
    Should Be Equal    ${clear_result}    ${200}
    
    # Verify version is removed
    ${versions}=    Evaluate    $api.get_ota_channel_versions('${ota_channel}')
    Should Not Contain    ${versions}    ahn2_34.swu

Battery Threshold Test
    [Documentation]    Test battery threshold constraints for different endpoint types
    [Tags]    battery    threshold    constraints
    
    ${api}=    Evaluate    __import__('src.augury_api', fromlist=['AuguryAPI']).AuguryAPI()
    
    # Test EP1 threshold (2500mA)
    ${battery_set}=    Evaluate    $api.set_endpoint_battery('EP1_001', 2400)  # Below threshold
    Should Be True    ${battery_set}
    
    ${endpoint_info}=    Evaluate    $api.api_get_endpoint_by_serial('EP1_001')
    Should Be Equal    ${endpoint_info['battery']}    ${2400}
    
    # Test EP2 threshold (2500mA)
    ${battery_set}=    Evaluate    $api.set_endpoint_battery('EP2_001', 2600)  # Above threshold
    Should Be True    ${battery_set}
    
    # Test Canary threshold (3600mA)
    ${battery_set}=    Evaluate    $api.set_endpoint_battery('Canary_001', 3500)  # Below threshold
    Should Be True    ${battery_set}
    
    ${endpoint_info}=    Evaluate    $api.api_get_endpoint_by_serial('Canary_001')
    Should Be Equal    ${endpoint_info['battery']}    ${3500}

Version Artifact Format Test
    [Documentation]    Test version artifact format validation
    [Tags]    validation    artifact_format
    
    ${api}=    Evaluate    __import__('src.augury_api', fromlist=['AuguryAPI']).AuguryAPI()
    ${ota_channel}=    Set Variable    OTA_${AHN2_UUID}
    
    # Test valid artifact formats
    ${valid_artifacts}=    Create List    ahn2_34.swu    cassia_35.swu    moxa_36.swu
    
    FOR    ${artifact}    IN    @{valid_artifacts}
        ${result}=    Evaluate    $api.api_post_version_to_ota_channel('${ota_channel}', '${artifact}')
        Should Be Equal    ${result}    ${200}
    END
    
    # Test invalid artifact formats
    ${invalid_artifacts}=    Create List    invalid.swu    ahn2.swu    ahn2_abc.swu    ahn2_34.txt
    
    FOR    ${artifact}    IN    @{invalid_artifacts}
        ${result}=    Evaluate    $api.api_post_version_to_ota_channel('${ota_channel}', '${artifact}')
        Should Be Equal    ${result}    ${400}
    END

*** Keywords ***
Verify Endpoint Battery Threshold
    [Arguments]    ${serial}    ${expected_threshold}
    ${api}=    Evaluate    __import__('src.augury_api', fromlist=['AuguryAPI']).AuguryAPI()
    ${endpoint_info}=    Evaluate    $api.api_get_endpoint_by_serial('${serial}')
    ${actual_threshold}=    Set Variable    ${endpoint_info['battery_threshold']}
    Should Be Equal    ${actual_threshold}    ${expected_threshold}
