# vedro-spec-compare

[![PyPI](https://img.shields.io/pypi/v/vedro-spec-compare.svg?style=flat-square)](https://pypi.org/project/vedro-spec-compare/)
[![Python Version](https://img.shields.io/pypi/pyversions/vedro-spec-compare.svg?style=flat-square)](https://pypi.org/project/vedro-spec-compare/)

# Description

`vedro-spec-compare` is a tool to compare two OpenAPI specs and generate reports


# Installation

```bash
pip3 install vedro-spec-compare
```


# Usage

## Help

```bash
vsc --help
```
```
usage: vsc [-h] {coverage,discrepancy} ...

vedro-spec-compare commands

positional arguments:
  {coverage,discrepancy}
                        Available commands
    coverage            Generate coverage report
    discrepancy         Generate discrepancy report

options:
  -h, --help            show this help message and exit
```


## Coverage

```bash
vsc coverage --help
```
```
usage: vsc coverage [-h] [--report-path REPORT_PATH] golden_spec_path testing_spec_path

positional arguments:
  golden_spec_path      Path to the golden OpenAPI spec
  testing_spec_path     Path to the testing OpenAPI spec

options:
  -h, --help            show this help message and exit
  --report-path REPORT_PATH
                        The path of the coverage report
```

### Examples

#### From yml files
```bash
vsc coverage golden_spec.yml testing_spec.yml
```
```bash
google-chrome coverage.html 
```

#### From json files
```bash
vsc coverage golden_spec.json testing_spec.json
```
```bash
google-chrome coverage.html 
```

#### With report path
```bash
vsc coverage golden_spec.yml testing_spec.yml --report-path coverage_report.html
```
```bash
google-chrome coverage_report.html 
```

#### From urls
```bash
vsc coverage https://golden/openapi.yaml https://testing/openapi.yaml
```
```bash
google-chrome coverage.html 
```


## Discrepancy

```bash
vsc discrepancy --help
```
```
usage: vsc discrepancy [-h] [--report-path REPORT_PATH] golden_spec_path testing_spec_path

positional arguments:
  golden_spec_path      Path to the golden OpenAPI spec
  testing_spec_path     Path to the testing OpenAPI spec

options:
  -h, --help            show this help message and exit
  --report-path REPORT_PATH
                        The path of the discrepancy report
```

### Examples

#### From yml files
```bash
vsc discrepancy golden_spec.yml testing_spec.yml
```
```bash
google-chrome discrepancy.html 
```

#### From json files
```bash
vsc discrepancy golden_spec.json testing_spec.json
```
```bash
google-chrome discrepancy.html 
```

#### With report path
```bash
vsc discrepancy golden_spec.yml testing_spec.yml --report-path coverage_report.html
```
```bash
google-chrome discrepancy.html 
```

#### From urls
```bash
vsc discrepancy https://golden/openapi.yaml https://testing/openapi.yaml
```
```bash
google-chrome discrepancy.html 
```
