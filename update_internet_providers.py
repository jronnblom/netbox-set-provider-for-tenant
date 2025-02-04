import os
import json
import socket
import argparse
from dotenv import load_dotenv
import pynetbox

def load_config():
    """Load configuration from JSON file."""
    with open('config.json', 'r') as f:
        return json.load(f)

def get_fqdn_from_ip(ip_address):
    """Perform reverse DNS lookup."""
    try:
        fqdn = socket.gethostbyaddr(ip_address)[0]
        return fqdn.lower()
    except (socket.herror, socket.gaierror):
        return None

def determine_provider(fqdn, providers):
    """Determine internet provider based on FQDN."""
    if not fqdn:
        return "unknown"
    
    for domain in providers.keys():
        if domain in fqdn:
            return domain
    return "unknown"

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action='store_true', help='Run in test mode without updating Netbox')
    parser.add_argument('--verbose', action='store_true', help='Show detailed progress')
    args = parser.parse_args()

    # Load environment variables and configuration
    load_dotenv()
    config = load_config()
    
    # Initialize Netbox connection
    nb = pynetbox.api(
        url=os.getenv('NETBOX_URL'),
        token=os.getenv('NETBOX_API_KEY')
    )

    # Get all tenants from specified groups
    tenants = nb.tenancy.tenants.filter(
        tenant_group=config['tenant_groups']
    )

    found_sites = False
    for tenant in list(tenants):
        if args.verbose:
            print(f"\nTenant: {tenant.name}")
        
        # Get sites for each tenant
        sites = nb.dcim.sites.filter(tenant_id=tenant.id)
        
        for site in list(sites):
            found_sites = True
            if args.verbose:
                print(f"\n  Site: {site.name}")
            
            # Get devices with specified roles
            devices = list(nb.dcim.devices.filter(
                site_id=site.id,
                role=config['device_roles']
            ))

            if not devices:
                if args.verbose:
                    print(f"    No matching devices found")
                continue

            # Get the first device's primary IP
            device = devices[0]
            if not device.primary_ip:
                if args.verbose:
                    print(f"    No primary IP found for device {device.name}")
                continue

            ip_address = str(device.primary_ip).split('/')[0]
            fqdn = get_fqdn_from_ip(ip_address)
            provider = determine_provider(fqdn, config['internet_providers'])

            if args.verbose:
                print(f"    Device: {device.name}")
                print(f"    IP: {ip_address}")
                print(f"    FQDN: {fqdn or 'Not found'}")
                print(f"    Provider: {config['internet_providers'][provider]}")

            if args.test:
                if not args.verbose:
                    print(f"\nSite: {site.name}")
                    print(f"Provider: {config['internet_providers'][provider]}")
                    print("---")
            else:
                # Update the site's internet_provider custom field
                site.custom_fields['internet_provider'] = provider
                site.save()
                if args.verbose:
                    print(f"    Updated internet provider to: {provider}")

    if not found_sites:
        print("\nNo sites found for the specified tenant groups")

if __name__ == "__main__":
    main() 