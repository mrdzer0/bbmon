#!/usr/bin/env python3
"""
Test runner for bb-monitor
Runs all unit tests and generates coverage report
"""

import sys
import unittest
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_all_tests(verbosity=2):
    """Run all unit tests"""
    print("=" * 70)
    print("BB-Monitor Unit Test Suite")
    print("=" * 70)
    print()

    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')

    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)

    print()
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print()

    if result.wasSuccessful():
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


def run_specific_test(test_name, verbosity=2):
    """Run a specific test module or test case"""
    print(f"Running test: {test_name}")
    print()

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(test_name)

    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


def run_with_coverage():
    """Run tests with coverage report"""
    try:
        import coverage
    except ImportError:
        print("Coverage package not installed. Install with: pip install coverage")
        print("Running tests without coverage...")
        return run_all_tests()

    print("Running tests with coverage...")
    print()

    # Start coverage
    cov = coverage.Coverage(source=['monitor', 'modules'])
    cov.start()

    # Run tests
    result = run_all_tests(verbosity=1)

    # Stop coverage
    cov.stop()
    cov.save()

    print()
    print("=" * 70)
    print("Coverage Report")
    print("=" * 70)
    cov.report()

    # Generate HTML report
    html_dir = 'htmlcov'
    cov.html_report(directory=html_dir)
    print()
    print(f"HTML coverage report generated in: {html_dir}/index.html")

    return result


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='BB-Monitor Test Runner')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output')
    parser.add_argument('-c', '--coverage', action='store_true',
                        help='Run with coverage report')
    parser.add_argument('-t', '--test', type=str,
                        help='Run specific test (e.g., tests.test_monitor.TestBBMonitor.test_init)')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Quiet output')

    args = parser.parse_args()

    # Determine verbosity
    if args.quiet:
        verbosity = 0
    elif args.verbose:
        verbosity = 2
    else:
        verbosity = 1

    # Run tests
    if args.coverage:
        exit_code = run_with_coverage()
    elif args.test:
        exit_code = run_specific_test(args.test, verbosity)
    else:
        exit_code = run_all_tests(verbosity)

    sys.exit(exit_code)
