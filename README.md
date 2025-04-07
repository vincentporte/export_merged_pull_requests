# Export Merged Pull Requests

A Python script to export merged pull requests assigned to a user within a specified time period.

## Setup

1. Copy `.env.example` to `.env` and populate it with the required values.
2. Initialize the virtual environment by running `uv sync`.

## Quick Start

1. Run the following command to collect merged pull requests for the first quarter of 2025:
```bash
   uv run python scripts/collect_PR.py --start-date 2025-01-01 --end-date 2025-03-31
```
2. The exported pull requests will be available in the data directory.

## Legacy Usage

1. Activate the virtual environment: 
```bash
source .venv/bin/activate
```
2. Execute the script: 
```bash
python scripts/collect_PR.py --start-date 2025-01-01 --end-date 2025-03-31
```
3. Retrieve the exported PRs from the `data` directory.

## test
Run the test suite in virtual env with:
```bash
pytest tests/
```
## License
This project is licensed under GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.


## Next Steps
- Add CI/CD pipeline for automated testing and deployment.
- Enhance tests to cover more cases.
