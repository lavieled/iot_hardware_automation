#!/usr/bin/env python3
"""
Test runner script for IoT Hardware Automation system
"""

import subprocess
import sys
import os


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {description}:")
        print(f"Return code: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False


def main():
    """Main test runner"""
    print("IoT Hardware Automation - Test Runner")
    print("=====================================")
    
    # Check if we're in the right directory
    if not os.path.exists("src") or not os.path.exists("robot_tests"):
        print("Error: Please run this script from the project root directory")
        sys.exit(1)
    
    success = True
    
    # Run unit tests
    if not run_command("python -m pytest tests/ -v", "Unit Tests"):
        success = False
    
    # Run Robot Framework tests
    if not run_command("python -m robot robot_tests/iot_automation_tests.robot", "Robot Framework - Main Tests"):
        success = False
    
    if not run_command("python -m robot robot_tests/additional_tests.robot", "Robot Framework - Additional Tests"):
        success = False
    
    # Summary
    print(f"\n{'='*50}")
    if success:
        print(" All tests completed successfully!")
    else:
        print(" Some tests failed. Check the output above.")
    print(f"{'='*50}")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
