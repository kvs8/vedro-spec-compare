import argparse

from .coverage import coverage


def command() -> None:
    parser = argparse.ArgumentParser(description='vedro-spec-compare commands')
    subparsers = parser.add_subparsers(help='Available commands', required=True)

    coverage_parser = subparsers.add_parser('coverage', help='Generate coverage report')
    coverage_parser.add_argument('golden_spec_path', type=str, help='Path to the golden OpenAPI spec')
    coverage_parser.add_argument('testing_spec_path', type=str, help='Path to the testing OpenAPI spec')
    coverage_parser.add_argument(
        '--report-path', type=str, help='The path of the coverage report', default='coverage.html'
    )
    coverage_parser.set_defaults(func=coverage)

    args = parser.parse_args()
    args.func(args)
