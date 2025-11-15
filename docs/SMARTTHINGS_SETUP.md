# SmartThings Setup Guide

## Getting Your Personal Access Token (Non-Expiring)

SmartThings Personal Access Tokens do **NOT expire by default**. Follow these steps to create a permanent token:

1. Go to https://account.smartthings.com/tokens
2. Click "Generate new token"
3. Name it: "Samsung Remote - Home Assistant"
4. Select these scopes:
   - `devices:read` - To list and get device info
   - `devices:execute` - To send commands
5. Click "Generate"
6. **Copy the token immediately** - It won't be shown again
7. Keep it safe - treat it like a password

## Important: Token Validity

- **Personal Access Tokens do NOT expire** - Your token will remain valid indefinitely
- If you see "Token Invalid" errors after 24 hours, it's likely:
  1. Your SmartThings account was compromised - regenerate a new token
  2. The TV was removed from your SmartThings account
  3. Network connectivity issue - check your internet connection
  4. SmartThings API server temporarily down - wait and retry

## Troubleshooting

### Token shows "Unauthorized" after setup
- Check if your internet connection is stable
- Verify TV is still connected to SmartThings app
- Try to send a command from the SmartThings mobile app first
- If still failing, regenerate a new token at https://account.smartthings.com/tokens

### TV doesn't appear in device list
- Open SmartThings mobile app
- Verify TV is listed there and online
- Try disconnecting and reconnecting TV in SmartThings app
- Restart Home Assistant to refresh device list

### Commands not working
- Verify TV is powered on
- Try sending command from SmartThings app first (to verify TV connectivity)
- Check TV brand/model supports remote control via SmartThings
- View Home Assistant logs for detailed error messages

### "Token Invalid" errors appearing periodically
- This indicates a connectivity or authentication issue, not token expiration
- Check your home network internet connectivity
- Verify SmartThings server status at https://status.smartthings.com/
- Regenerate a fresh token if errors persist

## Revoking Access

To revoke Home Assistant's access:
1. Go to https://account.smartthings.com/tokens
2. Find "Samsung Remote - Home Assistant" token
3. Click the delete icon
4. Confirm deletion
5. Home Assistant integration will stop working until new token added

## Multiple Tokens

You can create multiple tokens for different purposes:
- One for Home Assistant
- One for backup/different installation
- One for testing

Each token is independent and can be revoked separately.
