# SmartThings Setup Guide

## Getting Your Personal Access Token

1. Go to https://account.smartthings.com/tokens
2. Click "Generate new token"
3. Name it: "Samsung Remote - Home Assistant"
4. Select these scopes:
   - `devices:read` - To list and get device info
   - `devices:execute` - To send commands
5. Click "Generate"
6. **Copy the token immediately** - It won't be shown again
7. Keep it safe - treat it like a password

## Troubleshooting

### Token shows "Unauthorized"
- Regenerate a new token
- Ensure SmartThings account owns the TV
- Check TV is connected to SmartThings

### TV doesn't appear in device list
- Open SmartThings mobile app
- Verify TV is listed there
- Try disconnecting and reconnecting TV

### Commands not working
- Verify TV is powered on
- Try sending command from SmartThings app first
- Check TV brand/model supports remote control

## Revoking Access

To revoke Home Assistant's access:
1. Go to https://account.smartthings.com/tokens
2. Find "Samsung Remote - Home Assistant" token
3. Click the delete icon
4. Confirm deletion
5. Home Assistant integration will stop working until new token added
