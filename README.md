# IoT Hardware Automation System

This project implements a small testable IoT system in Python with end-to-end tests in Robot Framework. The system simulates an IoT environment with 3 Nodes (gateways) and 3 Endpoints (sensors) for hardware automation testing.

## System Overview

### Hardware Components
- **Nodes (Gateways)**: AHN2, Cassia, Moxa
- **Endpoints (Sensors)**: EP1, EP2, Canary_A

### Key Features
- OTA (Over The Air) updates for Nodes
- DFU (Device Firmware Update) for Endpoints
- Battery threshold management
- Backlog-based update constraints
- Fake API (AuguryAPI) for system operations

## Project Structure

```
iot_hardware_automation/
├── .gitignore             # Git ignore file
├── src/
│   ├── __init__.py
│   ├── models.py          # Domain models (Node, Endpoint, etc.)
│   └── augury_api.py      # Fake API implementation
├── tests/
│   └── test_models.py     # Unit tests
├── robot_tests/
│   ├── iot_automation_tests.robot  # Main test scenarios
│   └── additional_tests.robot      # Additional test cases
├── requirements.txt       # Python dependencies
├── demo.py               # System demonstration
├── run_tests.py          # Test runner script
└── README.md             # This file
```

## System Specifications

### Node UUID Format
- Format: `<hardware_type>_string`
- Example: `MOXA_TBCDB1045001`

### Battery Thresholds
- EP1 and EP2: 2500mA
- Canary: 3600mA

### Version Artifacts
- Format: `<hardware_type>_version_string.swu`
- Example: `moxa_33.swu`

### API Endpoints
- AHN2 and Cassia: `buildroot_api.azure`
- Moxa: `moxa_api.azure`

### OTA Channel Format
- Format: `OTA_<uuid>`
- Example: `OTA_AHN2_TBCDB1045001`

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Required Libraries & Frameworks

This project uses the following Python libraries and frameworks:

#### **Core Testing Frameworks**
- **pytest (7.4.3)**: Python unit testing framework
  - Used for: Unit tests in `tests/test_models.py`
  - Command: `python -m pytest tests/ -v`

- **pytest-cov (4.1.0)**: Coverage plugin for pytest
  - Used for: Code coverage reporting

- **Robot Framework (6.1.1)**: Generic open source automation framework
  - Used for: End-to-end integration tests
  - Command: `python -m robot robot_tests/`

#### **Built-in Python Libraries Used**
- **dataclasses**: For clean data structure definitions (Node, Endpoint classes)
- **enum**: For type-safe hardware type definitions (HardwareType enum)
- **typing**: For type hints and annotations throughout the codebase
- **subprocess**: For running external commands in test runner
- **os, sys**: For file system operations and system interactions

#### **Robot Framework Libraries Used**
- **BuiltIn**: Robot Framework's standard library for common operations
- **Collections**: For list and dictionary operations in tests
- **String**: For string manipulation in test cases

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd iot_hardware_automation
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**
   ```bash
   python -m pytest tests/ -v
   ```

## Quick Start

Run the demo to see the system in action:
```bash
python demo.py
```

Run all tests:
```bash
python run_tests.py
```

## Running Tests

### Unit Tests
Run the Python unit tests:
```bash
python -m pytest tests/ -v
```

### Robot Framework Tests
Run the Robot Framework test suites:

**Main test scenarios:**
```bash
python -m robot robot_tests/iot_automation_tests.robot
```

**Additional test cases:**
```bash
python -m robot robot_tests/additional_tests.robot
```

**All tests:**
```bash
python -m robot robot_tests/
```

### Test Output
Robot Framework will generate:
- Console output with test results
- `log.html` - Detailed test execution log
- `report.html` - Test execution report
- `output.xml` - Machine-readable test results

## Test Scenarios

### 1. OTA Happy Flow
- **Purpose**: Test successful OTA update from version 33 to 34
- **Steps**:
  1. Initialize Node with version 33
  2. Upload new version (34) to OTA channel
  3. Simulate OTA update with retries
  4. Verify Node version is updated

### 2. Endpoint DFU with Backlog
- **Purpose**: Test endpoint updates with backlog and battery constraints
- **Steps**:
  1. Set endpoint with pending samples (backlog > 0)
  2. Verify endpoint cannot update with backlog
  3. Clear backlog
  4. Verify endpoint can update
  5. Test battery threshold constraints

### 3. Bad Firmware OTA
- **Purpose**: Test OTA with incompatible firmware
- **Steps**:
  1. Upload incompatible version (wrong hardware type)
  2. Attempt OTA update
  3. Verify update fails and version remains unchanged
  4. Test invalid artifact format validation

## Additional Test Scenarios

The `additional_tests.robot` file contains extended test coverage beyond the required scenarios:

### 4. API Endpoint Validation Test
- **Purpose**: Test API endpoint validation for different node types
- **Steps**:
  1. Test AHN2 API endpoint validation
  2. Test Cassia API endpoint validation  
  3. Test Moxa API endpoint validation
  4. Verify correct UUIDs and node information

### 5. OTA Channel Management Test
- **Purpose**: Test OTA channel management operations
- **Steps**:
  1. Clear non-existent version (should fail)
  2. Add version to OTA channel
  3. Verify version is in channel
  4. Clear version from channel
  5. Verify version is removed

### 6. Battery Threshold Test
- **Purpose**: Test battery threshold constraints for different endpoint types
- **Steps**:
  1. Test EP1 threshold (2500mA) with below-threshold battery
  2. Test EP2 threshold (2500mA) with above-threshold battery
  3. Test Canary threshold (3600mA) with below-threshold battery
  4. Verify battery levels are correctly set and retrieved

### 7. Version Artifact Format Test
- **Purpose**: Test version artifact format validation
- **Steps**:
  1. Test valid artifact formats (ahn2_34.swu, cassia_35.swu, moxa_36.swu)
  2. Test invalid artifact formats (invalid.swu, ahn2.swu, ahn2_abc.swu)
  3. Verify proper validation and error handling

## API Reference

### AuguryAPI Methods

#### `api_get_endpoint_by_serial(serial_number: str) -> dict`
Returns endpoint information by serial number.

**Parameters:**
- `serial_number`: Endpoint serial number

**Returns:**
- Dictionary with endpoint details (serial_number, battery, hardware_type, uuid, version, backlog)

#### `api_get_node_by_uuid(uuid: str) -> dict`
Returns node information by UUID.

**Parameters:**
- `uuid`: Node UUID

**Returns:**
- Dictionary with node details (uuid, ota_channel, version, endpoints)

#### `api_post_version_to_ota_channel(ota_channel: str, version_artifact: str) -> int`
Adds new version to OTA channel.

**Parameters:**
- `ota_channel`: OTA channel name
- `version_artifact`: Version artifact name

**Returns:**
- 200 (success) or 400 (fail)

#### `api_clear_ota_channel(ota_channel: str, version_artifact: str) -> int`
Clears an artifact from the OTA channel.

**Parameters:**
- `ota_channel`: OTA channel name
- `version_artifact`: Version artifact name

**Returns:**
- 200 (success) or 400 (fail)


### Error Handling
- Failure handling in API methods
- Validation of input parameters
- Return codes for success/failure

### Testing Strategy
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete user scenarios
- **Robot Framework**: Business-readable test scenarios




