#!/usr/bin/env python3
"""
Get TalkGroup Group Members - Fixed Script
Uses only WORKING endpoints from the Retivis POC API
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, Optional, List
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from api_client.client import RetivisPOCClient
from api_client.exceptions import AuthenticationError, ConnectionError, ValidationError


def get_TalkGroup_groups(client: RetivisPOCClient) -> Dict[str, Any]:
    """
    Get all TalkGroup groups using the WORKING Group/groupList endpoint.
    
    Returns group details including:
    - gid: Group ID
    - gname: Group name  
    - createtime: Creation time
    - type: Group type
    - switch: Whether group is active
    """
    print("\n" + "="*70)
    print("FETCHING GROUPS (using Group/groupList endpoint)")
    print("="*70)
    
    try:
        url = f"{client.api_url}/tyt_web/Api/Group/groupList"
        params = {"page": "1", "limit": "100"}
        
        response = client.session.get(
            url,
            params=params,
            timeout=client.timeout,
            verify=client.verify_ssl,
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✓ Success! Got {len(data.get('data', []))} group(s)")
                return data
            except ValueError as e:
                print(f"✗ Failed to parse JSON: {e}")
                return None
        else:
            print(f"✗ Endpoint returned {response.status_code}")
            return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def get_monitored_groups(client: RetivisPOCClient, uid: str) -> Dict[str, Any]:
    """
    Get user's monitored groups using the WORKING Index/monitorList endpoint.
    
    Shows which groups the user is monitoring.
    """
    print("\n" + "="*70)
    print("FETCHING MONITORED GROUPS (using Index/monitorList endpoint)")
    print("="*70)
    
    try:
        url = f"{client.api_url}/tyt_web/Api/Index/monitorList"
        params = {"uid": uid}
        
        response = client.session.get(
            url,
            params=params,
            timeout=client.timeout,
            verify=client.verify_ssl,
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✓ Success!")
                return data
            except ValueError as e:
                print(f"✗ Failed to parse JSON: {e}")
                return None
        else:
            print(f"✗ Endpoint returned {response.status_code}")
            return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Get TalkGroup Group Information from Retivis POC API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
IMPORTANT NOTE: The API does NOT have a working endpoint to fetch group members.
This script shows all available group information that can be retrieved.

Working endpoints:
  - Group/groupList: Get all groups with details (gid, gname, createtime, type, switch)
  - Index/monitorList: Get user's monitored groups (groupData with gid, gname, monitored)

NOT working (return 404):
  - Group/getGroupMembers: Would return group members (NOT IMPLEMENTED)
  - Index/groupDetail: Would return group details (NOT IMPLEMENTED)
  - Device/groupMembers: Would return devices in group (NOT IMPLEMENTED)

Examples:
  # Show all groups
  python get_group_members.py -a YOUR_API_ACCOUNT -p your_password

  # Show monitored groups  
  python get_group_members.py -a YOUR_API_ACCOUNT -p your_password -u USER_ID

  # Show TalkGroup group specifically
  python get_group_members.py -a YOUR_API_ACCOUNT -p your_password --group-name "TalkGroup"
        """,
    )

    parser.add_argument(
        "-a",
        "--account",
        required=True,
        help="API Account (e.g., YOUR_API_ACCOUNT)",
    )
    parser.add_argument(
        "-p",
        "--password",
        required=True,
        help="API Password (MD5 hashed or plaintext)",
    )
    parser.add_argument(
        "--prehashed",
        action="store_true",
        help="Password is already MD5 hashed",
    )
    parser.add_argument(
        "-u",
        "--uid",
        help="User ID to get monitored groups (optional)",
    )
    parser.add_argument(
        "--group-name",
        help="Filter by group name",
    )
    parser.add_argument(
        "--api-url",
        default="https://www.retevispoc.com",
        help="API base URL",
    )

    args = parser.parse_args()

    print(f"Retivis POC - Get TalkGroup Groups")
    print(f"API URL: {args.api_url}")
    print(f"API Account: {args.account}\n")

    # Authenticate
    try:
        with RetivisPOCClient(
            api_url=args.api_url,
            account=args.account,
            password=args.password,
            use_prehashed=args.prehashed,
        ) as client:
            print("Authenticating...")
            if not client.login():
                print("✗ Authentication failed!")
                sys.exit(1)
            
            print("✓ Authentication successful!\n")
            
            # Get both sets of group data
            groups_data = get_TalkGroup_groups(client)
            
            # If uid provided, also get monitored groups
            if args.uid:
                monitored_data = get_monitored_groups(client, args.uid)
            else:
                monitored_data = None
            
            # Display results
            print("\n" + "="*70)
            print("RESULTS")
            print("="*70)
            
            if groups_data and groups_data.get("data"):
                groups = groups_data["data"]
                
                # Filter by name if provided
                if args.group_name:
                    groups = [g for g in groups if args.group_name.lower() in g.get("gname", "").lower()]
                
                print(f"\n✓ Found {len(groups)} group(s):\n")
                
                for i, group in enumerate(groups, 1):
                    print(f"  {i}. {group['gname']} (ID: {group['gid']})")
                    print(f"     Created: {group.get('createtime', 'N/A')}")
                    print(f"     Type: {group.get('type', 'N/A')}")
                    print(f"     Active: {'Yes' if group.get('switch') == '1' else 'No'}")
                    
                    # Check if monitored
                    if monitored_data and monitored_data.get("data", {}).get("groupData"):
                        monitored = any(g["gid"] == group["gid"] for g in monitored_data["data"]["groupData"])
                        print(f"     Monitored: {'Yes' if monitored else 'No'}")
                    print()
                
                # Show full JSON
                print("\n" + "="*70)
                print("FULL JSON RESPONSE")
                print("="*70)
                print(json.dumps(groups_data, indent=2, ensure_ascii=False))
                
                if monitored_data:
                    print(f"\n\nMONITORED GROUPS:")
                    print(json.dumps(monitored_data, indent=2, ensure_ascii=False))
            else:
                print("\n✗ No groups found or error fetching groups")
                if groups_data:
                    print(json.dumps(groups_data, indent=2, ensure_ascii=False))
    
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


if __name__ == "__main__":
    main()




