# SmartThings Setup Guide

## Token Setup

### New Setup - OAuth 2.0 (Recommended)

SmartThings now supports OAuth 2.0 with long-lived refresh tokens. This is the best option for automatic token renewal.

#### Step 1: Obtain OAuth Tokens

Unfortunately, the SmartThings OAuth authorize endpoint is currently not publicly available. In the meantime, you can use **existing grandfathered PATs** that continue to work indefinitely.

#### Step 2: Configure in Home Assistant

During integration setup, you'll be asked for:

1. **Access Token** (Required):
   - Your current token for API authentication
   - Expires after 24 hours
   - Automatically renewed using refresh token

2. **Refresh Token** (Required for auto-renewal):
   - Used to obtain new access tokens
   - Does not expire
   - Enables completely automatic token refresh

#### Step 3: Select Your TV

The integration will discover all your SmartThings-connected TVs. Select the one you want to control.

### Legacy Setup - Personal Access Token (PAT)

If you have an existing PAT that still works:

1. Go to https://account.smartthings.com/tokens
2. Copy your existing PAT token
3. During Home Assistant setup:
   - Paste PAT as **Access Token**
   - Leave **Refresh Token** empty
   - The integration will treat it as a permanent token

**Important**: New PATs created after December 30, 2024 expire after 24 hours. Only use old PATs or upgrade to OAuth tokens.

## How Automatic Token Refresh Works

The integration handles everything automatically:

1. **On startup**: Loads access token and refresh token from config
2. **Before each API call**: Checks if token expires within 5 minutes
3. **When renewal needed**: Uses refresh token to get a new access token
4. **Transparently**: All happens in the background - you don't see it
5. **Secure storage**: New tokens are stored in Home Assistant config

**Result**: Your tokens **never expire** and connection never drops!

## Updating Tokens

If you need to update your tokens later:

1. Go to: Settings → Devices & Services
2. Find your Samsung Remote integration
3. Click the three dots → Modify
4. Update **Access Token** and/or **Refresh Token**
5. Click Submit

You'll see masked tokens showing last 8 characters for security.

## Troubleshooting

### "Invalid Token" Error During Setup

This means the token couldn't authenticate with SmartThings API:

1. **Verify token format**:
   - Copy the entire token (no extra spaces)
   - Make sure nothing was cut off

2. **Check token is active**:
   - Go to https://account.smartthings.com/tokens
   - Verify your token is listed there

3. **Verify scopes** (for PAT tokens):
   - Token needs: `r:devices:*` and `x:devices:*`

4. **Regenerate if needed**:
   - Go to https://account.smartthings.com/tokens
   - Delete the old token
   - Create a new one

### "No Samsung TVs found"

Your token is valid, but SmartThings can't find any TVs:

1. **Add TV to SmartThings account**:
   - Open SmartThings mobile app
   - Add your TV (if not already there)
   - Verify TV is powered on and online

2. **Verify in SmartThings app**:
   - Open the SmartThings app
   - You should see your TV in the devices list
   - If not there, it can't be controlled

3. **Refresh in Home Assistant**:
   - Try rediscovering the integration
   - Restart Home Assistant

### Token Shows "Unauthorized" After Setup

This shouldn't happen with refresh tokens, but if it does:

1. **Check internet connection**:
   - Verify your home network has internet
   - SmartThings API requires internet connectivity

2. **Verify TV connectivity**:
   - Check TV is still in your SmartThings account
   - Verify TV is powered on and online

3. **Check logs**:
   - Go to Settings → System → Logs
   - Search for "SmartThings" or "samsung_remote"
   - Look for specific error messages

4. **Regenerate tokens if needed**:
   - Go to https://account.smartthings.com/tokens
   - Delete and recreate your token
   - Update in Home Assistant settings

### Commands Sent But TV Doesn't Respond

1. **Verify via SmartThings app**:
   - Try sending a command from SmartThings mobile app
   - If that works, the TV is reachable

2. **Check command compatibility**:
   - Not all commands work with SmartThings API
   - See supported commands in README

3. **Try Local Tizen instead**:
   - Local Tizen supports more commands
   - Requires TV on same network
   - No token expiration issues

## OAuth Limitations

The SmartThings OAuth authorize endpoint (`https://account.smartthings.com/oauth/authorize`) appears to be not publicly available. We're working on alternatives:

1. **For now**: Use existing grandfathered PAT tokens (work indefinitely)
2. **Future**: We'll provide an alternative OAuth flow when available
3. **Fallback**: Use Local Tizen API (no tokens, LAN-based)

## Revoking Access

To revoke Home Assistant's access to your SmartThings account:

1. Go to: https://account.smartthings.com/tokens
2. Find your token in the list
3. Click the delete/revoke button
4. Confirm deletion
5. Home Assistant integration will stop working until new token added

## Multiple Integrations

You can create multiple tokens for different purposes:
- One for main Home Assistant instance
- One for testing setup
- One for backup instance

Each token is independent and can be revoked separately.

## More Information

- SmartThings API Documentation: https://developer.smartthings.com/docs/
- SmartThings Account: https://account.smartthings.com/
- Token Refresh Guide: See `docs/TOKEN_REFRESH_GUIDE.md`
- GitHub Issues: https://github.com/Qlimuli/samsung-tv-remote-HA/issues
