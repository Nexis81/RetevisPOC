#!/usr/bin/env python3
"""
Get group members from Retivis POC API

Solution: The API doesn't have a direct "group members" endpoint.
Instead, we fetch ALL devices using Index/deviceList and filter by group ID (curgid field).
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


def get_group_members(
    client: RetivisPOCClient, group_id: str, detailed: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Get all devices that belong to a specific group.
    
    Works by fetching all devices and filtering by curgid (current group ID).
    
    Args:
        client: Authenticated API client
        group_id: Group ID to filter by
        detailed: If True, return full device details; if False, return minimal info
    
    Returns:
        Dictionary with member list and metadata
    """
    if not client.authenticated:
        client.login()
    
    print(f"\nFetching all devices from Index/deviceList...")
    
    url = f"{client.api_url}/tyt_web/Api/Index/deviceList"
    
    try:
        response = client.session.get(
            url,
            timeout=client.timeout,
            verify=client.verify_ssl,
        )
        
        if response.status_code != 200:
            print(f"  Error: API returned status {response.status_code}")
            return None
        
        all_devices_data = response.json()
        
        if not isinstance(all_devices_data, dict) or 'data' not in all_devices_data:
            print(f"  Error: Invalid API response format")
            return None
        
        all_devices = all_devices_data.get('data', [])
        print(f"  Got {len(all_devices)} total devices")
        
        # Filter devices by group ID (curgid field)
        group_members = [d for d in all_devices if d.get('curgid') == group_id]
        
        print(f"  Found {len(group_members)} device(s) in group {group_id}")
        
        # Prepare response
        result = {
            "status": all_devices_data.get('status'),
            "group_id": group_id,
            "group_name": None,
            "member_count": len(group_members),
            "members": group_members if detailed else []
        }
        
        # Try to find the group name
        if group_members and not detailed:
            # Get group name from first member
            group_name = group_members[0].get('gname')
            if group_name:
                result['group_name'] = group_name
        elif group_members:
            result['group_name'] = group_members[0].get('gname')
        
        return result
        
    except Exception as e:
        print(f"  Error: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Get group members from Retivis POC API"
    )
    parser.add_argument('-a', '--account', required=True, help='API account')
    parser.add_argument('-p', '--password', required=True, help='API password (MD5 hash)')
    parser.add_argument('--prehashed', action='store_true', help='Password is already MD5 hashed')
    parser.add_argument('--api-url', default='https://www.retevispoc.com', help='API base URL')
    parser.add_argument('--group-id', help='Group ID to query')
    parser.add_argument('--group-name', help='Group name to query (looks it up by name)')
    parser.add_argument('--list-groups', action='store_true', help='List all available groups')
    parser.add_argument('-m', '--members', choices=['minimal', 'full', 'keys'], default='full',
                       help='Output format for members (minimal=names only, full=all fields, keys=field names)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("Retivis POC - Get Group Members")
    print("=" * 70)
    print(f"API URL: {args.api_url}")
    print(f"Account: {args.account}")
    print()
    
    # Create client
    try:
        client = RetivisPOCClient(
            api_url=args.api_url,
            account=args.account,
            password=args.password,
            use_prehashed=args.prehashed
        )
        
        print("Authenticating...")
        client.login()
        print("Authentication successful!\n")
        
    except AuthenticationError as e:
        print(f"Error: Authentication failed: {e}")
        sys.exit(1)
    except ConnectionError as e:
        print(f"Error: Connection error: {e}")
        sys.exit(1)
    
    # List all groups if requested
    if args.list_groups:
        print("=" * 70)
        print("AVAILABLE GROUPS")
        print("=" * 70)
        
        url = f"{client.api_url}/tyt_web/Api/Group/groupList"
        response = client.session.get(url, timeout=client.timeout, verify=client.verify_ssl)
        
        if response.status_code == 200:
            groups_data = response.json()
            groups = groups_data.get('data', [])
            
            print(f"\nFound {len(groups)} group(s):\n")
            for group in groups:
                print(f"  - {group.get('gname'):20} (ID: {group.get('gid')})")
                print(f"    Created: {group.get('createtime')}")
                print(f"    Type: {group.get('type')}, Active: {'Yes' if group.get('switch') == '1' else 'No'}")
                print()
        else:
            print(f"Error listing groups: {response.status_code}")
        
        return
    
    # Get group members
    if not args.group_id and not args.group_name:
        # Ask user to specify a group
        print("Error: Please specify --group-id or --group-name or use --list-groups")
        print("\nExample:")
        print("  python get_group_members_working.py -a YOUR_API_ACCOUNT -p PASSWORD --group-id GROUP_ID")
        parser.print_help()
        sys.exit(1)
    
    # If group name provided, look up the ID
    if args.group_name and not args.group_id:
        print(f"Looking up group ID for name: {args.group_name}")
        url = f"{client.api_url}/tyt_web/Api/Group/groupList"
        response = client.session.get(url, timeout=client.timeout, verify=client.verify_ssl)
        
        if response.status_code == 200:
            groups_data = response.json()
            groups = groups_data.get('data', [])
            
            for group in groups:
                if group.get('gname').lower() == args.group_name.lower():
                    args.group_id = group.get('gid')
                    print(f"  Found: {args.group_name} (ID: {args.group_id})\n")
                    break
            
            if not args.group_id:
                print(f"  Error: Group '{args.group_name}' not found")
                sys.exit(1)
    
    # Fetch members
    result = get_group_members(client, args.group_id, detailed=True)
    
    if not result:
        print("\nError: Failed to retrieve group members")
        sys.exit(1)
    
    # Display results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    group_name = result.get('group_name', 'Unknown')
    member_count = result.get('member_count', 0)
    
    print(f"\nGroup: {group_name} (ID: {args.group_id})")
    print(f"Members: {member_count}")
    
    members = result.get('members', [])
    
    if member_count == 0:
        print("  (No members in this group)")
    else:
        print()
        if args.members == 'keys':
            # Show field names available
            if members:
                print("Available fields for each member:")
                for key in sorted(members[0].keys()):
                    print(f"  - {key}")
        else:
            # Show member details
            for i, member in enumerate(members, 1):
                print(f"  {i}. {member.get('username', 'Unknown')} (account: {member.get('account')})")
                
                if args.members == 'full':
                    print(f"     User ID: {member.get('uid')}")
                    print(f"     Account: {member.get('account')}")
                    print(f"     Level: {member.get('level')}")
                    print(f"     Created: {member.get('createtime')}")
                    print(f"     Valid Until: {member.get('validtime')}")
                    print(f"     Online: {'Yes' if member.get('online') == '1' else 'No'}")
                    print(f"     Last Online: {member.get('lasttime')}")
                    
                    if member.get('friendData'):
                        print(f"     Contacts: {len(member['friendData'])} friend(s)")
                        for friend in member['friendData']:
                            print(f"       - {friend.get('username')} ({friend.get('account')})")
                    
                    if member.get('function'):
                        print(f"     Functions: {', '.join(member['function'])}")
                    print()
    
    # Output as JSON if requested
    if args.json:
        print("\n" + "=" * 70)
        print("JSON OUTPUT")
        print("=" * 70)
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()




