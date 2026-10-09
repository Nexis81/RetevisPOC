#!/usr/bin/env python3
"""
Script to retrieve TalkGroup group members from Retivis POC API

This script demonstrates multiple approaches to get group members:
1. Via the Group/getGroupMembers endpoint (if available)
2. Via group detail endpoint
3. Via monitor list (shows monitored groups)
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, Optional, List
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from api_client.client import RetivisPOCClient
from api_client.exceptions import AuthenticationError, ConnectionError, ValidationError


def get_group_members_via_api(
    client: RetivisPOCClient, group_id: str, method: str = "auto"
) -> Optional[Dict[str, Any]]:
    """
    Retrieve group members using various API endpoints.

    Args:
        client: Authenticated API client
        group_id: Group ID to query
        method: Which method to try ('auto', 'members', 'detail', 'all')

    Returns:
        Response data or None if all methods fail
    """
    results = {}

    # Method 1: Try Group/getGroupMembers endpoint
    if method in ["auto", "members", "all"]:
        print(f"\n[Method 1] Trying Group/getGroupMembers endpoint...")
        try:
            url = f"{client.api_url}/tyt_web/Api/Group/getGroupMembers"
            params = {"gid": group_id}
            headers = client.session.headers.copy()
            
            response = client.session.get(
                url,
                params=params,
                timeout=client.timeout,
                verify=client.verify_ssl,
            )
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    results["members_endpoint"] = data
                    print(f"  ✓ Success! Got response with {len(json.dumps(data))} chars")
                    if method == "members":
                        return data
                except ValueError as e:
                    print(f"  ✗ Failed to parse JSON: {e}")
            else:
                print(f"  ✗ Endpoint returned {response.status_code}")
        except Exception as e:
            print(f"  ✗ Error: {e}")

    # Method 2: Try Index/groupDetail endpoint
    if method in ["auto", "detail", "all"]:
        print(f"\n[Method 2] Trying Index/groupDetail endpoint...")
        try:
            url = f"{client.api_url}/tyt_web/Api/Index/groupDetail"
            params = {"gid": group_id}
            
            response = client.session.get(
                url,
                params=params,
                timeout=client.timeout,
                verify=client.verify_ssl,
            )
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    results["detail_endpoint"] = data
                    print(f"  ✓ Success! Got group details")
                    if method == "detail":
                        return data
                except ValueError as e:
                    print(f"  ✗ Failed to parse JSON: {e}")
            else:
                print(f"  ✗ Endpoint returned {response.status_code}")
        except Exception as e:
            print(f"  ✗ Error: {e}")

    # Method 3: Try Group/groupMembers endpoint (alternative naming)
    if method in ["auto", "members", "all"]:
        print(f"\n[Method 3] Trying Group/groupMembers endpoint...")
        try:
            url = f"{client.api_url}/tyt_web/Api/Group/groupMembers"
            params = {"gid": group_id}
            
            response = client.session.get(
                url,
                params=params,
                timeout=client.timeout,
                verify=client.verify_ssl,
            )
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    results["groupMembers_endpoint"] = data
                    print(f"  ✓ Success! Got response")
                    if method == "members":
                        return data
                except ValueError as e:
                    print(f"  ✗ Failed to parse JSON: {e}")
            else:
                print(f"  ✗ Endpoint returned {response.status_code}")
        except Exception as e:
            print(f"  ✗ Error: {e}")

    # Method 4: Try Device/groupMembers endpoint
    if method in ["auto", "members", "all"]:
        print(f"\n[Method 4] Trying Device/groupMembers endpoint...")
        try:
            url = f"{client.api_url}/tyt_web/Api/Device/groupMembers"
            params = {"gid": group_id}
            
            response = client.session.get(
                url,
                params=params,
                timeout=client.timeout,
                verify=client.verify_ssl,
            )
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    results["device_members"] = data
                    print(f"  ✓ Success! Got response")
                    if method == "members":
                        return data
                except ValueError as e:
                    print(f"  ✗ Failed to parse JSON: {e}")
            else:
                print(f"  ✗ Endpoint returned {response.status_code}")
        except Exception as e:
            print(f"  ✗ Error: {e}")

    if method == "all" and results:
        return results
    elif results:
        # Return the first successful result
        return list(results.values())[0]
    
    return None


def list_all_groups(client: RetivisPOCClient) -> List[Dict[str, Any]]:
    """List all available groups."""
    print("\n" + "="*60)
    print("LISTING ALL GROUPS")
    print("="*60)
    
    try:
        response = client.get_groups(page=1, limit=100)
        
        if response.get("status") == 100:
            groups = response.get("data", [])
            print(f"\nFound {len(groups)} group(s):")
            for i, group in enumerate(groups, 1):
                print(f"  {i}. {group.get('gname', 'Unknown')} (ID: {group.get('gid', 'N/A')})")
            return groups
        else:
            print(f"Error: {response.get('msg', 'Unknown error')}")
            return []
    except Exception as e:
        print(f"Error listing groups: {e}")
        return []


def get_group_members(
    account: str,
    password: str,
    group_id: Optional[str] = None,
    group_name: Optional[str] = None,
    api_url: Optional[str] = None,
    list_all: bool = False,
    method: str = "auto",
    use_prehashed: bool = False,
) -> None:
    """
    Main function to get group members.

    SECURITY WARNING: This API uses header-based MD5 authentication with NO session tokens.
    MD5 is cryptographically broken and should not be used for new systems.
    Only use this script for authorized testing/development.

    Args:
        account: API Account ID (e.g., 'YOUR_API_ACCOUNT', NOT device account like 'YOUR_ACCOUNT_ID')
        password: API Password - can be plaintext (will be MD5 hashed) or pre-hashed MD5
        group_id: Group ID to query
        group_name: Group name to query (will search for it)
        api_url: API base URL
        list_all: Whether to list all groups first
        method: Which API method to try
        use_prehashed: If True, password is already MD5 hashed
    """
    api_url = api_url or os.getenv("RETIVIS_API_URL", "https://www.retevispoc.com")

    print(f"Retivis POC - Get Group Members Script")
    print(f"API URL: {api_url}")
    print(f"API Account: {account} (NOT device account)")
    print("\n⚠️  SECURITY WARNING:")
    print("   This API uses MD5 header-based authentication (cryptographically broken)")
    print("   Credentials are sent with EVERY request in plaintext headers (over HTTPS only)")

    # Initialize client and authenticate
    try:
        with RetivisPOCClient(
            api_url=api_url,
            account=account,
            password=password,
            verify_ssl=True,
            use_prehashed=use_prehashed,
        ) as client:
            print("\nAuthenticating...")
            if client.login():
                print("✓ Authentication successful!")
            else:
                print("✗ Authentication failed!")
                sys.exit(1)

            # List all groups if requested
            if list_all:
                groups = list_all_groups(client)
                if not group_id and not group_name:
                    # Ask user to select a group
                    if groups:
                        print("\n" + "-"*60)
                        try:
                            choice = input("Enter group number to fetch members (or press Enter to skip): ").strip()
                            if choice.isdigit() and 1 <= int(choice) <= len(groups):
                                group_id = groups[int(choice) - 1]["gid"]
                                print(f"Selected group: {groups[int(choice) - 1]['gname']}")
                        except (ValueError, KeyboardInterrupt):
                            print("Skipping group member fetch")
                            return

            # If group_name provided, search for it
            if group_name and not group_id:
                print(f"\nSearching for group: {group_name}")
                groups = list_all_groups(client)
                for group in groups:
                    if group_name.lower() in group.get("gname", "").lower():
                        group_id = group["gid"]
                        print(f"Found: {group['gname']} (ID: {group_id})")
                        break
                if not group_id:
                    print(f"Group '{group_name}' not found!")
                    sys.exit(1)

            # Get group members
            if group_id:
                print("\n" + "="*60)
                print(f"FETCHING MEMBERS FOR GROUP ID: {group_id}")
                print("="*60)

                result = get_group_members_via_api(client, group_id, method=method)

                if result:
                    print("\n" + "="*60)
                    print("RESULT:")
                    print("="*60)
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                    
                    # Try to extract member list if present
                    if isinstance(result, dict):
                        if "data" in result and isinstance(result["data"], list):
                            print(f"\n✓ Found {len(result['data'])} member(s):")
                            for member in result["data"]:
                                if isinstance(member, dict):
                                    print(f"  - {member}")
                                else:
                                    print(f"  - {member}")
                else:
                    print("\n✗ No valid response received from any endpoint")
                    print("\nNote: The Group/getGroupMembers endpoint may not be available on this API.")
                    print("Available endpoints that work:")
                    print("  - Index/monitorList: Get user's monitored groups")
                    print("  - Index/groupList: List all groups")
                    print("  - Index/groupDetail: Get group details (may include members)")
            else:
                print("No group specified. Use --group-id or --group-name to specify a group.")

    except AuthenticationError as e:
        print(f"✗ Authentication error: {e}")
        sys.exit(1)
    except ConnectionError as e:
        print(f"✗ Connection error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Parse arguments and run the script."""
    parser = argparse.ArgumentParser(
        description="Get TalkGroup group members from Retivis POC API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all groups interactively
  python get_group_members.py -a YOUR_API_ACCOUNT -p your_api_password --list-all

  # Get members for TalkGroup group (with plaintext password)
  python get_group_members.py -a YOUR_API_ACCOUNT -p your_api_password --group-id GROUP_ID

  # Get members for TalkGroup group (with prehashed MD5 password)
  python get_group_members.py -a YOUR_API_ACCOUNT -p YOUR_MD5_HASH_HERE --group-id GROUP_ID --prehashed

  # Search for group by name
  python get_group_members.py -a YOUR_API_ACCOUNT -p your_api_password --group-name "TalkGroup"

  # Try all available methods
  python get_group_members.py -a YOUR_API_ACCOUNT -p your_api_password --group-id GROUP_ID --method all

NOTE: Account should be your API account (e.g., 'YOUR_API_ACCOUNT'), NOT the device account (e.g., 'YOUR_ACCOUNT_ID')
        """,
    )

    parser.add_argument(
        "-a",
        "--account",
        required=True,
        help="API Account ID (e.g., 'YOUR_API_ACCOUNT', NOT device account)",
    )
    parser.add_argument(
        "-p",
        "--password",
        required=True,
        help="API Password (MD5 hashed or plaintext, or set RETIVIS_PASSWORD env var)",
    )
    parser.add_argument(
        "--api-url",
        help="API base URL (default: https://www.retevispoc.com)",
    )
    parser.add_argument(
        "--group-id",
        help="Group ID to fetch members for",
    )
    parser.add_argument(
        "--group-name",
        help="Group name to search for and fetch members",
    )
    parser.add_argument(
        "--list-all",
        action="store_true",
        help="List all available groups",
    )
    parser.add_argument(
        "-m",
        "--method",
        choices=["auto", "members", "detail", "all"],
        default="auto",
        help="Which API endpoint method to try (default: auto)",
    )
    parser.add_argument(
        "--prehashed",
        action="store_true",
        help="Indicate that the password is already MD5 hashed",
    )

    args = parser.parse_args()

    get_group_members(
        account=args.account,
        password=args.password,
        group_id=args.group_id,
        group_name=args.group_name,
        api_url=args.api_url,
        list_all=args.list_all,
        method=args.method,
        use_prehashed=args.prehashed,
    )


if __name__ == "__main__":
    main()




