# Retivis POC API Scripts

Simple Python scripts for fetching chat groups and group members from the Retivis POC API.

## Scripts

### `get_chat_groups.py`
Fetch all chat groups available to your account.

```bash
python get_chat_groups.py -a YOUR_API_ACCOUNT -p YOUR_MD5_HASH
```

### `get_group_members.py`
Fetch members (devices) for a specific group.

```bash
python get_group_members.py -a YOUR_API_ACCOUNT -p YOUR_MD5_HASH --group-id GROUP_ID
```

### `get_group_members_working.py`
Enhanced version with additional output formats and filtering options.

```bash
python get_group_members_working.py -a YOUR_API_ACCOUNT -p YOUR_MD5_HASH --group-id GROUP_ID
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure with environment variables (recommended):
```bash
cp .env.example .env
# Edit .env with your API credentials
```

3. Run scripts:
```bash
python get_chat_groups.py
python get_group_members.py --group-id GROUP_ID
```

## Options

- `-a, --account` - API account name
- `-p, --password` - MD5 hashed password
- `--prehashed` - Password is already MD5 hashed
- `--group-id` - Fetch members for specific group
- `--group-name` - Fetch members by group name
- `--format` - Output format (table, minimal, json)

## Environment Variables

Set credentials in `.env`:
```
RETIVIS_ACCOUNT=YOUR_API_ACCOUNT
RETIVIS_PASSWORD=YOUR_MD5_HASH
```



