#!/usr/bin/env python3
"""
Azure AI Foundry Project Resource Explorer

DESCRIPTION:
    This script connects to Azure AI Foundry projects and provides comprehensive
    resource exploration capabilities. It can list and analyze various Azure
    resources including Cognitive Services accounts, deployments, models, and
    other project-related resources.

FEATURES:
    - List all Azure resources in a resource group
    - Focus on Cognitive Services accounts with detailed information
    - Show AI model deployments and versions
    - Display project summaries and statistics
    - Support for both service principal and default Azure authentication
    - Debug mode for detailed troubleshooting

DEPENDENCIES:
    Required Python packages (install with pip):
        pip install azure-identity>=1.15.0
        pip install azure-mgmt-resource>=23.0.0
        pip install azure-mgmt-cognitiveservices>=13.5.0
        pip install python-dotenv>=1.0.0

PREREQUISITES:
    1. Azure subscription with AI Foundry project
    2. Service principal with appropriate permissions:
       - Cognitive Services Contributor
       - Reader role on resource group
    3. Environment configuration (.env file)

ENVIRONMENT CONFIGURATION:
    Create a .env file in the same directory with:
        AZURE_SUBSCRIPTION_ID=your-subscription-id
        AZURE_RESOURCE_GROUP=your-resource-group-name
        AZURE_PROJECT_NAME=your-project-name
        AZURE_ENDPOINT=https://your-endpoint.cognitiveservices.azure.com/
        AZURE_CLIENT_ID=your-service-principal-client-id
        AZURE_CLIENT_SECRET=your-service-principal-secret
        AZURE_TENANT_ID=your-azure-tenant-id

USAGE EXAMPLES:
    # Show project summary (default behavior)
    python foundryResourceExplorer.py
    
    # List all resources in the resource group
    python foundryResourceExplorer.py --list-resources
    
    # Focus on cognitive services with detailed info
    python foundryResourceExplorer.py --cognitive
    
    # Enable debug output for troubleshooting
    python foundryResourceExplorer.py --debug
    
    # Combine options
    python foundryResourceExplorer.py --cognitive --debug
    python foundryResourceExplorer.py --list-resources --debug

AUTHENTICATION:
    The script uses Azure service principal authentication by default.
    If service principal credentials are not available, it falls back
    to DefaultAzureCredential (Azure CLI, managed identity, etc.).

PERMISSIONS REQUIRED:
    - Microsoft.CognitiveServices/accounts/read
    - Microsoft.CognitiveServices/accounts/deployments/read
    - Microsoft.Resources/subscriptions/resourceGroups/resources/read

TROUBLESHOOTING:
    - Use --debug flag for detailed error information
    - Verify .env file exists and contains correct values
    - Check Azure permissions for the service principal
    - Ensure network connectivity to Azure endpoints

AUTHOR: Azure AI Foundry Resource Explorer
VERSION: 1.0.0
"""

from __future__ import annotations

import os
import sys
import argparse
from typing import Optional, Dict, List

# Script metadata
__version__ = "1.0.0"
__author__ = "Azure AI Foundry Resource Explorer"
__description__ = "Azure AI Foundry Project Resource Explorer and Management Tool"

# Required package versions
REQUIRED_PACKAGES = {
    "azure-identity": ">=1.15.0",
    "azure-mgmt-resource": ">=23.0.0", 
    "azure-mgmt-cognitiveservices": ">=13.5.0",
    "python-dotenv": ">=1.0.0"
}

def check_dependencies():
    """Check if all required packages are installed with correct versions."""
    missing_packages = []
    
    try:
        import azure.identity
        import azure.mgmt.resource
        import azure.mgmt.cognitiveservices
        # python-dotenv is optional, handled in load_environment()
    except ImportError as e:
        missing_packages.append(str(e))
    
    if missing_packages:
        print("❌ Missing required packages:")
        for pkg in missing_packages:
            print(f"   - {pkg}")
        print("\n📦 Install required packages:")
        print("   pip install azure-identity>=1.15.0")
        print("   pip install azure-mgmt-resource>=23.0.0")
        print("   pip install azure-mgmt-cognitiveservices>=13.5.0") 
        print("   pip install python-dotenv>=1.0.0")
        print("\n   Or install all at once:")
        print("   pip install azure-identity azure-mgmt-resource azure-mgmt-cognitiveservices python-dotenv")
        sys.exit(1)

# Load environment variables
def load_environment():
    """Load environment variables from .env file if available."""
    try:
        from dotenv import load_dotenv
        base = os.path.dirname(__file__)
        env_files = [
            os.getenv('ENV_FILE'),
            os.path.join(base, '.env'),
            os.path.join(base, 'env')
        ]
        
        for env_file in env_files:
            if env_file and os.path.isfile(env_file):
                if load_dotenv(env_file):
                    print(f"✅ Loaded environment from: {env_file}")
                    break
        else:
            print("⚠️  No .env file found. Using system environment variables.")
            
    except ImportError:
        print("⚠️  python-dotenv not installed. Using system environment variables only.")
    except Exception as e:
        print(f"⚠️  Error loading environment: {e}")

# Check dependencies first
check_dependencies()

# Load environment
load_environment()

# Azure SDK imports with version checking
try:
    from azure.identity import DefaultAzureCredential, ClientSecretCredential
    from azure.mgmt.resource import ResourceManagementClient
    from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
    
    # Verify we can import core classes (basic validation)
    assert DefaultAzureCredential
    assert ClientSecretCredential  
    assert ResourceManagementClient
    assert CognitiveServicesManagementClient
    
except ImportError as e:
    print(f"❌ Azure SDK import error: {e}")
    print("\n📦 Install required Azure SDK packages:")
    print("   pip install azure-identity azure-mgmt-resource azure-mgmt-cognitiveservices")
    sys.exit(1)
except Exception as e:
    print(f"❌ Azure SDK validation error: {e}")
    sys.exit(1)

# Required environment variables for Azure authentication
REQUIRED_ENV_VARS = {
    "AZURE_SUBSCRIPTION_ID": "Azure subscription ID where resources are located",
    "AZURE_RESOURCE_GROUP": "Resource group name containing the AI Foundry project",
    "AZURE_CLIENT_ID": "Service principal application (client) ID", 
    "AZURE_CLIENT_SECRET": "Service principal client secret",
    "AZURE_TENANT_ID": "Azure tenant ID"
}

# Optional environment variables
OPTIONAL_ENV_VARS = {
    "AZURE_PROJECT_NAME": "AI Foundry project name",
    "AZURE_ENDPOINT": "AI Foundry project endpoint URL"
}

def ensure_env():
    """Validate required environment variables are present."""
    missing = []
    
    # Check required variables
    for var, description in REQUIRED_ENV_VARS.items():
        if not os.getenv(var):
            missing.append(f"{var} ({description})")
    
    if missing:
        print("❌ Missing required environment variables:")
        for var in missing:
            print(f"   - {var}")
        print("\n📋 Create a .env file with these variables:")
        print("   AZURE_SUBSCRIPTION_ID=your-subscription-id")
        print("   AZURE_RESOURCE_GROUP=your-resource-group-name") 
        print("   AZURE_CLIENT_ID=your-service-principal-client-id")
        print("   AZURE_CLIENT_SECRET=your-service-principal-secret")
        print("   AZURE_TENANT_ID=your-azure-tenant-id")
        print("\n📖 See script documentation for detailed setup instructions.")
        sys.exit(1)
    
    # Show optional variables status
    optional_found = []
    optional_missing = []
    for var, description in OPTIONAL_ENV_VARS.items():
        if os.getenv(var):
            optional_found.append(var)
        else:
            optional_missing.append(f"{var} ({description})")
    
    if optional_found:
        print(f"✅ Optional variables loaded: {', '.join(optional_found)}")
    if optional_missing:
        print(f"⚠️  Optional variables not set: {len(optional_missing)} variables")

def create_credential(debug: bool = False):
    """Create Azure credential for authentication."""
    # Try service principal first
    client_id = os.getenv('AZURE_CLIENT_ID')
    client_secret = os.getenv('AZURE_CLIENT_SECRET')
    tenant_id = os.getenv('AZURE_TENANT_ID')
    
    if all([client_id, client_secret, tenant_id]):
        if debug:
            print("🔐 Using service principal authentication")
        
        return ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
    else:
        if debug:
            print("🔐 Using default Azure credential")
        
        return DefaultAzureCredential()

def list_all_resources(debug: bool = False) -> Dict[str, List]:
    """List all resources in the resource group."""
    try:
        subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
        resource_group = os.getenv('AZURE_RESOURCE_GROUP')
        
        if debug:
            print(f"📋 Listing resources in subscription {subscription_id}, resource group {resource_group}")
        
        credential = create_credential(debug)
        resource_client = ResourceManagementClient(credential, subscription_id)
        
        # Get all resources in the resource group
        resources = list(resource_client.resources.list_by_resource_group(resource_group))
        
        # Organize resources by type
        resource_types = {}
        for resource in resources:
            resource_type = resource.type
            if resource_type not in resource_types:
                resource_types[resource_type] = []
            
            resource_info = {
                'name': resource.name,
                'location': resource.location,
                'kind': getattr(resource, 'kind', None),
                'sku': getattr(resource, 'sku', None),
                'tags': resource.tags or {}
            }
            resource_types[resource_type].append(resource_info)
        
        print(f"\n✅ Found {len(resources)} resources in resource group '{resource_group}':")
        print(f"📊 Resource types: {len(resource_types)}")
        
        for resource_type, resources_list in resource_types.items():
            print(f"\n🔸 {resource_type} ({len(resources_list)} resources):")
            for i, resource in enumerate(resources_list, 1):
                print(f"  {i}. {resource['name']}")
                if debug:
                    print(f"     Location: {resource['location']}")
                    if resource['kind']:
                        print(f"     Kind: {resource['kind']}")
                    if resource['sku']:
                        print(f"     SKU: {resource['sku']}")
                    if resource['tags']:
                        print(f"     Tags: {resource['tags']}")
                    print()
        
        return resource_types
        
    except Exception as e:
        print(f"❌ Error listing resources: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        return {}

def list_cognitive_services(debug: bool = False) -> List:
    """List cognitive services accounts with detailed information."""
    subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
    resource_group = os.getenv('AZURE_RESOURCE_GROUP')
    
    if debug:
        print(f"🧠 Listing cognitive services in {resource_group}")
    
    credential = create_credential(debug)
    cognitive_client = CognitiveServicesManagementClient(credential, subscription_id)
    
    # List cognitive services accounts
    accounts = list(cognitive_client.accounts.list_by_resource_group(resource_group))
    
    print(f"\n🧠 Cognitive Services Accounts ({len(accounts)} found):")
    
    for i, account in enumerate(accounts, 1):
        print(f"\n  {i}. {account.name}")
        print(f"     Kind: {account.kind}")
        print(f"     SKU: {account.sku.name if account.sku else 'Unknown'}")
        print(f"     Location: {account.location}")
        print(f"     Endpoint: {account.properties.endpoint if account.properties else 'N/A'}")
        
        if debug:
            print(f"     Provisioning State: {account.properties.provisioning_state if account.properties else 'Unknown'}")
            if account.properties and hasattr(account.properties, 'custom_sub_domain_name'):
                print(f"     Custom Domain: {account.properties.custom_sub_domain_name}")
            if account.tags:
                print(f"     Tags: {account.tags}")
        
        # Try to list deployments if possible
        if debug:
            print("     🚀 Checking deployments...")
        try:
            deployments = list(cognitive_client.deployments.list(resource_group, account.name))
            if deployments:
                print(f"     📦 Deployments ({len(deployments)}):")
                for j, deployment in enumerate(deployments, 1):
                    print(f"       {j}. {deployment.name}")
                    if debug and deployment.properties:
                        model = deployment.properties.model
                        print(f"          Model: {model.name if model else 'Unknown'}")
                        print(f"          Version: {model.version if model else 'Unknown'}")
            else:
                print("     📦 No deployments found")
        except Exception as e:
            if debug:
                print(f"     ⚠️  Could not list deployments: {e}")
    
    return accounts

def show_project_summary(debug: bool = False):
    """Show a summary of the AI Foundry project."""
    project_name = os.getenv('AZURE_PROJECT_NAME')
    resource_group = os.getenv('AZURE_RESOURCE_GROUP')
    subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
    endpoint = os.getenv('AZURE_ENDPOINT')
    
    print(f"\n🏗️  Azure AI Foundry Project Summary")
    print(f"   Project Name: {project_name or 'Not specified'}")
    print(f"   Resource Group: {resource_group}")
    print(f"   Subscription: {subscription_id}")
    print(f"   Endpoint: {endpoint or 'Not specified'}")
    print(f"   Configuration Source: .env file")

def show_help():
    """Display comprehensive help information."""
    print(f"""
🚀 Azure AI Foundry Project Resource Explorer v{__version__}

DESCRIPTION:
    Explore and analyze Azure AI Foundry project resources including
    Cognitive Services accounts, deployments, models, and other resources.

USAGE:
    python {os.path.basename(__file__)} [OPTIONS]

OPTIONS:
    --help              Show this help message
    --debug             Enable verbose debug output
    --list-resources    List all resources in the resource group
    --cognitive         Focus on cognitive services accounts
    --summary           Show project summary (default if no other options)

EXAMPLES:
    {os.path.basename(__file__)}                    # Show project summary
    {os.path.basename(__file__)} --cognitive        # List cognitive services
    {os.path.basename(__file__)} --list-resources   # List all resources
    {os.path.basename(__file__)} --cognitive --debug # Cognitive services with debug

SETUP:
    1. Install dependencies:
       pip install azure-identity azure-mgmt-resource azure-mgmt-cognitiveservices python-dotenv

    2. Create .env file:
       AZURE_SUBSCRIPTION_ID=your-subscription-id
       AZURE_RESOURCE_GROUP=your-resource-group-name
       AZURE_CLIENT_ID=your-service-principal-client-id
       AZURE_CLIENT_SECRET=your-service-principal-secret
       AZURE_TENANT_ID=your-azure-tenant-id

    3. Ensure service principal has permissions:
       - Cognitive Services Contributor
       - Reader role on resource group

For more information, see the script documentation.
""")

def main():
    parser = argparse.ArgumentParser(
        description="Azure AI Foundry Project Resource Explorer",
        add_help=False  # We'll handle help ourselves
    )
    parser.add_argument('--help', action='store_true', help='Show help message')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--list-resources', action='store_true', help='List all project resources')
    parser.add_argument('--cognitive', action='store_true', help='Focus on cognitive services')
    parser.add_argument('--summary', action='store_true', help='Show project summary')
    
    args = parser.parse_args()
    
    # Handle help
    if args.help:
        show_help()
        return
    
    if args.debug:
        print(f"🚀 Starting Azure AI Foundry Project Resource Explorer v{__version__}")
        print(f"📁 Working directory: {os.getcwd()}")
        print(f"🐍 Python version: {sys.version}")
    
    # Validate environment
    ensure_env()
    
    # Show project summary
    if args.summary or not any([args.list_resources, args.cognitive]):
        show_project_summary(debug=args.debug)
    
    # List all resources
    if args.list_resources or not any([args.cognitive, args.summary]):
        resource_types = list_all_resources(debug=args.debug)
        
        # Show quick stats
        if resource_types:
            print(f"\n📈 Quick Stats:")
            for resource_type, resources in resource_types.items():
                short_type = resource_type.split('/')[-1]  # Get just the resource type name
                print(f"   {short_type}: {len(resources)}")
    
    # Focus on cognitive services
    if args.cognitive:
        accounts = list_cognitive_services(debug=args.debug)
        
        if accounts:
            print(f"\n🎯 Cognitive Services Focus:")
            ai_foundry_accounts = [acc for acc in accounts if 'foundry' in acc.name.lower() or 'ai' in acc.kind.lower()]
            if ai_foundry_accounts:
                print(f"   🤖 AI/Foundry accounts: {len(ai_foundry_accounts)}")
                for acc in ai_foundry_accounts:
                    print(f"      • {acc.name} ({acc.kind})")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Operation cancelled by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Unexpected error occurred:")
        print(f"   Error: {e}")
        print(f"   Type: {type(e).__name__}")
        print(f"\n🔧 Troubleshooting tips:")
        print(f"   - Run with --debug for more details")
        print(f"   - Check your .env file configuration")
        print(f"   - Verify Azure permissions")
        print(f"   - Ensure network connectivity to Azure")
        print(f"   - Use --help for usage information")
        sys.exit(1)
