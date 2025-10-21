*** Settings ***
Documentation    IoT Hardware Automation Test Suite using BuiltIn library
Library          Collections
Library          String
Library          BuiltIn

*** Variables ***
${AHN2_UUID}         AHN2_TBCDB1045001
${CASSIA_UUID}       Cassia_TBCDB1045002
${MOXA_UUID}         MOXA_TBCDB1045003
${EP1_SERIAL}        EP1_001
${EP2_SERIAL}        EP2_001
${CANARY_SERIAL}     Canary_001

*** Test Cases ***
OTA Happy Flow Test
    [Documentation]    Test OTA update flow from version 33 to 34
    [Tags]    ota    happy_flow
    
    # Initialize API using Python code
    ${api}=    Evaluate    __import__('src.augury_api', fromlist=['AuguryAPI']).AuguryAPI()
    
    # Verify initial node version
    ${node_info}=    Evaluate    $api.api_get_node_by_uuid('${AHN2_UUID}')
    Should Be Equal    ${node_info['version']}    33
    
    # Upload new version to OTA channel
    ${ota_channel}=    Set Variable    OTA_${AHN2_UUID}
    ${version_artifact}=    Set Variable    ahn2_34.swu
    ${result}=    Evaluate    $api.api_post_version_to_ota_channel('${ota_channel}', '${version_artifact}')
    Should Be Equal    ${result}    ${200}
    
    # Simulate OTA update with retries
    ${update_success}=    Evaluate    $api.simulate_ota_update('${AHN2_UUID}', '34')
    Should Be True    ${update_success}
    
    # Verify node version is updated
    ${updated_node_info}=    Evaluate    $api.api_get_node_by_uuid('${AHN2_UUID}')
    Should Be Equal    ${updated_node_info['version']}    34

Endpoint DFU with Backlog Test
    [Documentation]    Test endpoint DFU with backlog and battery constraints
    [Tags]    dfu    endpoint    backlog
    
    # Initialize API using Python code
    ${api}=    Evaluate    __import__('src.augury_api', fromlist=['AuguryAPI']).AuguryAPI()
    
    # Set endpoint with pending samples (backlog > 0)
    ${backlog_set}=    Evaluate    $api.set_endpoint_backlog('${EP1_SERIAL}', 5)
    Should Be True    ${backlog_set}
    
    # Verify endpoint cannot update with backlog
    ${endpoint_info}=    Evaluate    $api.api_get_endpoint_by_serial('${EP1_SERIAL}')
    Should Be Equal    ${endpoint_info['backlog']}    ${5}
    
    # Try to update endpoint (should fail due to backlog)
    ${dfu_success}=    Evaluate    $api.simulate_endpoint_dfu('${EP1_SERIAL}', '2.0')
    Should Not Be True    ${dfu_success}
    
    # Clear backlog
    ${backlog_cleared}=    Evaluate    $api.set_endpoint_backlog('${EP1_SERIAL}', 0)
    Should Be True    ${backlog_cleared}
    
    # Now endpoint should be able to update
    ${dfu_success}=    Evaluate    $api.simulate_endpoint_dfu('${EP1_SERIAL}', '2.0')
    Should Be True    ${dfu_success}
    
    # Verify endpoint version is updated
    ${updated_endpoint_info}=    Evaluate    $api.api_get_endpoint_by_serial('${EP1_SERIAL}')
    Should Be Equal    ${updated_endpoint_info['version']}    2.0
    
    # Test battery threshold constraint
    ${battery_set}=    Evaluate    $api.set_endpoint_battery('${EP2_SERIAL}', 2000)
    Should Be True    ${battery_set}
    
    # EP2 has threshold of 2500mA, so update should fail
    ${dfu_success}=    Evaluate    $api.simulate_endpoint_dfu('${EP2_SERIAL}', '2.0')
    Should Not Be True    ${dfu_success}

Bad Firmware OTA Test
    [Documentation]    Test OTA with incompatible firmware version
    [Tags]    ota    bad_firmware    error_handling
    
    # Initialize API using Python code
    ${api}=    Evaluate    __import__('src.augury_api', fromlist=['AuguryAPI']).AuguryAPI()
    
    # Upload incompatible version (wrong hardware type)
    ${ota_channel}=    Set Variable    OTA_${AHN2_UUID}
    ${bad_artifact}=    Set Variable    moxa_34.swu  # Wrong hardware type for AHN2
    ${result}=    Evaluate    $api.api_post_version_to_ota_channel('${ota_channel}', '${bad_artifact}')
    Should Be Equal    ${result}    ${200}  # API accepts it, but update should fail
    
    # Try to update with bad firmware (should fail because it's wrong hardware type)
    ${update_success}=    Evaluate    $api.simulate_ota_update('${AHN2_UUID}', '34')
    Should Not Be True    ${update_success}
    
    # Verify node version remains unchanged
    ${node_info}=    Evaluate    $api.api_get_node_by_uuid('${AHN2_UUID}')
    Should Be Equal    ${node_info['version']}    33  # Should remain at original version
    
    # Test with invalid artifact format
    ${invalid_artifact}=    Set Variable    invalid_format.swu
    ${result}=    Evaluate    $api.api_post_version_to_ota_channel('${ota_channel}', '${invalid_artifact}')
    Should Be Equal    ${result}    ${400}  # Should fail validation

*** Keywords ***
Verify Node Version
    [Arguments]    ${uuid}    ${expected_version}
    ${api}=    Evaluate    __import__('src.augury_api', fromlist=['AuguryAPI']).AuguryAPI()
    ${node_info}=    Evaluate    $api.api_get_node_by_uuid('${uuid}')
    Should Be Equal    ${node_info['version']}    ${expected_version}

Verify Endpoint Version
    [Arguments]    ${serial}    ${expected_version}
    ${api}=    Evaluate    __import__('src.augury_api', fromlist=['AuguryAPI']).AuguryAPI()
    ${endpoint_info}=    Evaluate    $api.api_get_endpoint_by_serial('${serial}')
    Should Be Equal    ${endpoint_info['version']}    ${expected_version}
