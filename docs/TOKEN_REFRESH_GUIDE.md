# SmartThings OAuth Token Refresh Guide

## Overview

Starting December 30, 2024, SmartThings changed how Personal Access Tokens (PATs) work:
- **New PATs**: Expire after 24 hours
- **Existing PATs**: Continue to work indefinitely (grandfathered in)

This integration now supports **automatic token refresh** using OAuth 2.0, so your tokens never expire!

## How It Works

### OAuth 2.0 Token Refresh Flow

1. **User provides a refresh token** during setup
2. **Integration stores both access and refresh tokens**
3. **Before each API call**, the integration checks token expiry
4. **If token is about to expire** (within 5 minutes), it automatically refreshes using the refresh token
5. **New access token is obtained** without user intervention
6. **Tokens are securely stored** in Home Assistant config

### Benefits

✅ **No more 24-hour token expiration**
✅ **Automatic refresh - fire and forget**
✅ **Works with both OAuth and PAT tokens**
✅ **Backward compatible with existing PAT setups**

## Setup Instructions

### Option 1: Using OAuth Refresh Token (Recommended)

1. **Generate a refresh token** at: https://account.smartthings.com/oauth/authorize
   - This gives you a long-lived refresh token that can generate new access tokens

2. **In Home Assistant**:
   - Go to: Settings → Devices & Services → Create Integration → Samsung Remote
   - Choose: SmartThings API
   - Paste your **refresh token** when prompted
   - Select your TV device

3. **Done!** The token will automatically refresh before expiring

### Option 2: Using Existing PAT (Legacy)

If you have an existing PAT that still works:

1. **Go to**: https://account.smartthings.com/tokens
2. **Copy your existing PAT**
3. **In Home Assistant**:
   - Paste the PAT during setup
   - Integration will treat it as a refresh token

⚠️ **Note**: Newly generated PATs only work for 24 hours. Use OAuth refresh tokens instead.

## Troubleshooting

### "Invalid Token" Error

**If you see this after setup:**

1. Check your token is correct at: https://account.smartthings.com/tokens
2. Ensure your internet connection is stable
3. Verify your TV is still in your SmartThings account
4. Try regenerating a new token

### Token Keeps Expiring

**This should NOT happen with refresh tokens.** If it does:

1. Check Home Assistant logs: Settings → System → Logs
2. Look for messages like: "SmartThings OAuth token refreshed"
3. If refresh is failing, your refresh token may have been revoked
4. Generate a new token and update in: Integration Settings → Options

### I Only Have Old PATs

1. You can still use old PATs - they work indefinitely
2. When you need to generate a new token:
   - Use OAuth instead of regular PAT
   - Get a refresh token from: https://account.smartthings.com/oauth/authorize

## Technical Details

### Token Expiry Handling

- **Access tokens**: Expire after 24 hours
- **Refresh tokens**: No fixed expiry (indefinite)
- **Integration check**: Tokens checked 5 minutes before expiry
- **Automatic refresh**: Happens transparently before API calls

### Token Storage

Tokens are stored in your Home Assistant configuration:
- Secure and encrypted by Home Assistant
- Only used for API calls to SmartThings
- Never shared with external services

### Rate Limits

SmartThings has rate limits on token refresh:
- **Per token**: 100 refreshes per day (more than enough)
- **Per user**: 1000 refreshes per day
- Integration only refreshes when needed, not on every call

## FAQ

**Q: Will my old PAT still work?**
A: Yes! Existing PATs are grandfathered in and work indefinitely.

**Q: Do I need to do anything?**
A: No! The integration automatically handles token refresh. Just set it up once.

**Q: What if the refresh fails?**
A: The integration will log an error. You can generate a new token and update it in Settings.

**Q: Can I use the same token for multiple Home Assistant instances?**
A: Yes, but each instance will refresh the token independently. Keep your tokens secure.

**Q: How often does the token refresh?**
A: Only when needed - typically once per day if you actively use the remote.

## More Information

- SmartThings OAuth Documentation: https://developer.smartthings.com/docs/connected-services/oauth-integrations/
- SmartThings API Documentation: https://developer.smartthings.com/docs/
- Home Assistant Integration: https://github.com/Qlimuli/samsung-tv-remote-HA
