# Retivis POC API Scripts - Quick Reference

## 🎯 Common Commands

### List all chat groups
```bash
python get_chat_groups.py -a YOUR_API_ACCOUNT -p YOUR_MD5_HASH --prehashed
```

### Get members for a group
```bash
python get_group_members.py -a YOUR_API_ACCOUNT -p YOUR_MD5_HASH --prehashed --group-id GROUP_ID
```

### Enhanced version with more options
```bash
python get_group_members_working.py -a YOUR_API_ACCOUNT -p YOUR_MD5_HASH --prehashed --group-id GROUP_ID
```

---

## Using Environment Variables (Recommended)

Create `.env` file:
```
RETIVIS_ACCOUNT=YOUR_API_ACCOUNT
RETIVIS_PASSWORD=YOUR_MD5_HASH
```

Then run:
```bash
python get_chat_groups.py
python get_group_members.py --group-id GROUP_ID
```

---

## 📁 Available Scripts

| Script | Purpose |
|--------|---------|
| `get_chat_groups.py` | List all available chat groups |
| `get_group_members.py` | Fetch members for a specific group |
| `get_group_members_working.py` | Enhanced version with multiple output formats |

---

## Command Options

### Authentication
- `-a, --account` - API account name
- `-p, --password` - MD5 hashed password
- `--prehashed` - Password is already MD5 hashed

### Selection
- `--group-id GROUP_ID` - Fetch members by group ID
- `--group-name GROUP_NAME` - Fetch members by group name

### Output
- `--format table` - Pretty table format (default)
- `--format minimal` - Minimal output
- `--format json` - JSON format

---

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure credentials (optional):
```bash
cp .env.example .env
# Edit .env with your credentials
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Authentication failed" | Check API account and password hash |
| "Group not found" | Use `get_chat_groups.py` to see available groups |
| "Connection error" | Verify HTTPS access to retevispoc.com |
| "No module named" | Run `pip install -r requirements.txt` |

---

## 📚 Files

- `get_chat_groups.py` - List groups
- `get_group_members.py` - Get members
- `get_group_members_working.py` - Enhanced version
- `src/api_client/` - Reusable API client library
- `.env.example` - Environment variable template
- `README.md` - Full documentation

**Ready to use! 🚀**
