# Netbox Internet Provider Updater

This script automatically updates the internet provider information for sites in Netbox based on DNS reverse lookup of device IP addresses.

## Prerequisites

- Python 3.6 or higher
- Access to a Netbox instance
- Required Python packages:
  ```bash
  pip install pynetbox python-dotenv
  ```

## Configuration

1. Copy the environment file template and fill in your Netbox credentials:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` with your actual Netbox URL and API key.

2. Review and modify `config.json` if needed:
   - `tenant_groups`: List of tenant groups to process
   - `device_roles`: Device roles to look for at each site
   - `internet_providers`: Mapping of domain names to provider labels

## Installation

1. Create and activate a virtual environment:
   ```bash
   # On Windows
   python -m venv .venv
   .\.venv\Scripts\activate

   # On Linux/Mac
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Test Mode
To run the script in test mode (no changes to Netbox):
```bash
python update_internet_providers.py --test
```

### Production Mode
To update the internet provider information in Netbox:
```bash
python update_internet_providers.py
```

This will display the site names and their detected internet providers.

## How it Works

1. The script gets all tenants that belong to the configured tenant groups
2. For each tenant's sites, it looks for devices with the specified roles
3. It performs a reverse DNS lookup on the device's primary IP
4. Based on the FQDN, it determines the internet provider
5. Updates the site's `internet_provider` custom field in Netbox

## Configuration Files

- `.env`: Contains Netbox credentials (not version controlled)
- `config.json`: Contains tenant groups, device roles, and provider mappings

## Running and testing

```bash
python update_internet_providers.py --test
```
# Test mode with verbose output
python update_internet_providers.py --test --verbose

# Test mode with minimal output
python update_internet_providers.py --test

# Production mode with verbose output
python update_internet_providers.py --verbose

# Production mode with minimal output
python update_internet_providers.py