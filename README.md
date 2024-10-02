# vedro-spec-compare

# Description

`vedro-spec-compare` is a tool to compare two OpenAPI specs and generate a coverage report

# Installation

```bash
pip3 install vedro-spec-compare
```


# Usage

## Help
```bash
vsc -h
```
```
usage: vsc [-h] {coverage} ...

vedro-spec-compare commands

positional arguments:
  {coverage}  Available commands
    coverage  Generate coverage report

options:
  -h, --help  show this help message and exit
```

## Coverage
```bash
vsc coverage -h
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

#### With report path
```bash
vsc coverage golden_spec.yml testing_spec.yml --report-path coverage_report.yml
```
```bash
google-chrome coverage_report.html 
```

#### From urls
```bash
vsc coverage https://raw.githubusercontent.com/OAI/OpenAPI-Specification/main/examples/v3.0/petstore.yaml https://raw.githubusercontent.com/OAI/OpenAPI-Specification/main/examples/v3.0/petstore-expanded.yaml
```
```bash
google-chrome coverage.html 
```
