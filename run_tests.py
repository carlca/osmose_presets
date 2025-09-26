#!/usr/bin/env python3
"""
Test runner script for the Osmose Presets Refactoring project.

This script provides various options for running tests with different levels of detail.
"""

import subprocess
import sys
import argparse
from pathlib import Path

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")

def run_command(cmd, description):
    """Run a command and display its output."""
    print(f"{Colors.OKCYAN}Running: {Colors.ENDC}{description}")
    print(f"{Colors.OKBLUE}Command: {Colors.ENDC}{cmd}\n")
    
    result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
    
    if result.returncode == 0:
        print(f"\n{Colors.OKGREEN}✓ Tests passed!{Colors.ENDC}")
    else:
        print(f"\n{Colors.FAIL}✗ Some tests failed!{Colors.ENDC}")
    
    return result.returncode

def main():
    parser = argparse.ArgumentParser(description='Run tests for Osmose Presets Refactoring')
    parser.add_argument('mode', nargs='?', default='standard',
                       choices=['standard', 'verbose', 'coverage', 'integration', 
                               'search', 'filters', 'quick', 'full', 'failed'],
                       help='Test mode to run')
    parser.add_argument('--html', action='store_true',
                       help='Generate HTML coverage report')
    parser.add_argument('--file', type=str,
                       help='Run tests for a specific file')
    parser.add_argument('--class', type=str, dest='test_class',
                       help='Run tests for a specific test class')
    parser.add_argument('--test', type=str,
                       help='Run a specific test')
    
    args = parser.parse_args()
    
    # Base test directory
    test_dir = "tests"
    
    # Define test commands for different modes
    commands = {
        'standard': {
            'cmd': f"python3 -m pytest {test_dir}/test_preset_model.py -v",
            'desc': "Standard test run with moderate verbosity"
        },
        'verbose': {
            'cmd': f"python3 -m pytest {test_dir}/test_preset_model.py -vvs --tb=short",
            'desc': "Verbose test run showing all details and print statements"
        },
        'coverage': {
            'cmd': f"python3 -m pytest {test_dir}/test_preset_model.py --cov=src/data --cov-report=term-missing",
            'desc': "Test run with code coverage report"
        },
        'integration': {
            'cmd': f"python3 -m pytest {test_dir}/test_preset_integration.py -vvs",
            'desc': "Integration tests with real data"
        },
        'search': {
            'cmd': f"python3 -m pytest {test_dir}/test_preset_model.py::TestPresetSearch -vvs",
            'desc': "Search functionality tests only"
        },
        'filters': {
            'cmd': f"python3 -m pytest {test_dir}/test_preset_model.py::TestPresetFilters -vvs",
            'desc': "Filter functionality tests only"
        },
        'quick': {
            'cmd': f"python3 -m pytest {test_dir}/test_preset_model.py -q",
            'desc': "Quick test run with minimal output"
        },
        'full': {
            'cmd': f"python3 -m pytest {test_dir}/ -vvs --tb=short",
            'desc': "Run all tests with full verbosity"
        },
        'failed': {
            'cmd': f"python3 -m pytest {test_dir}/ --lf -vv",
            'desc': "Run only previously failed tests"
        }
    }
    
    # Handle custom test selection
    if args.file:
        cmd = f"python3 -m pytest {args.file} -vvs"
        desc = f"Running tests for {args.file}"
    elif args.test_class:
        cmd = f"python3 -m pytest {test_dir}/test_preset_model.py::{args.test_class} -vvs"
        desc = f"Running test class {args.test_class}"
    elif args.test:
        cmd = f"python3 -m pytest {test_dir}/ -k {args.test} -vvs"
        desc = f"Running tests matching '{args.test}'"
    else:
        mode_info = commands.get(args.mode)
        if not mode_info:
            print(f"{Colors.FAIL}Invalid mode: {args.mode}{Colors.ENDC}")
            return 1
        cmd = mode_info['cmd']
        desc = mode_info['desc']
    
    # Add HTML coverage option
    if args.html and 'cov' in cmd:
        cmd += " --cov-report=html"
        desc += " (with HTML report)"
    
    print_header("Osmose Presets Refactoring - Test Runner")
    
    # Run the selected test command
    exit_code = run_command(cmd, desc)
    
    # If HTML coverage was generated, show the path
    if args.html and 'cov' in cmd and exit_code == 0:
        print(f"\n{Colors.OKGREEN}HTML coverage report generated at: htmlcov/index.html{Colors.ENDC}")
        print(f"Open with: {Colors.OKBLUE}open htmlcov/index.html{Colors.ENDC}")
    
    # Show available modes at the end
    if args.mode == 'standard':
        print(f"\n{Colors.OKCYAN}Other available test modes:{Colors.ENDC}")
        for mode, info in commands.items():
            if mode != 'standard':
                print(f"  {Colors.OKBLUE}{mode:12}{Colors.ENDC} - {info['desc']}")
        print(f"\n{Colors.OKCYAN}Run with:{Colors.ENDC} {Colors.OKBLUE}python3 run_tests.py <mode>{Colors.ENDC}")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())