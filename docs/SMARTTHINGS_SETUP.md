# SmartThings Setup Guide

## Token Options

### Option 1: OAuth Refresh Token (Recommended)

SmartThings now supports OAuth 2.0 with long-lived refresh tokens. This is the recommended approach.

1. Go to https://account.smartthings.com/oauth/authorize
2. Generate an OAuth refresh token
3. Use this token in Home Assistant - it will **never expire**
4. The integration automatically refreshes the access token before it expires

**Benefits:**
- Tokens never expire
- Automatic refresh - fire and forget
- Better security than PATs
- Full OAuth 2.0 compliance

### Option 2: Personal Access Tokens (PAT)


**Important Update (December 2024):**
- **Existing PATs**: Continue to work indefinitely (grandfathered in)
- **New PATs**: Expire after 24 hours as of December 30, 2024

If you have an existing PAT that still works, you can continue using it. However, SmartThings now recommends using OAuth refresh tokens for new setups.

**To create a Personal Access Token:**

1. Go to https://account.smartthings.com/tokens
2. Click "Generate new token"
3. Name it: "Samsung Remote - Home Assistant"
4. Select these scopes:
   - `r:devices:*` - To list and get device info
   - `x:devices:*` - To send commands
5. Click "Generate"
6. **Copy the token immediately** - It won't be shown again
7. Keep it safe - treat it like a password

## How Token Refresh Works


The integration automatically handles token refresh:

1. Before each API call, it checks if the access token is about to expire
2. If expiry is within 5 minutes, it automatically requests a new access token
3. The refresh token is used to get a new access token
4. This all happens transparently - you don't need to do anything

**Result:** Your connection never drops due to token expiration.

## Troubleshooting

### Token shows "Unauthorized" after setup
- Check if your internet connection is stable
- Verify TV is still connected to SmartThings app
- Try to send a command from the SmartThings mobile app first
- If still failing, regenerate a new token at https://account.smartthings.com/tokens or https://account.smartthings.com/oauth/authorize

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

### Token keeps showing as "Invalid" 

With automatic token refresh enabled, tokens should not expire. If you see "Invalid Token" errors:
- This indicates a connectivity or authentication issue, not token expiration
- Check your home network internet connectivity
- Verify SmartThings server status at https://status.smartthings.com/
- Verify your refresh token is still valid in your SmartThings account
- Regenerate a fresh token if errors persist

## Revoking Access

To revoke Home Assistant's access:
1. Go to https://account.smartthings.com/tokens (for PAT) or https://account.smartthings.com/oauth/authorize (for OAuth)
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

## More Information

- SmartThings OAuth Documentation: https://developer.smartthings.com/docs/connected-services/oauth-integrations/
- SmartThings API Documentation: https://developer.smartthings.com/docs/
- Token Refresh Guide: See `docs/TOKEN_REFRESH_GUIDE.md` for detailed technical information
