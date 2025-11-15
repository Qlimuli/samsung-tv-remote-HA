# OAuth Token Refresh - Technical Guide

## Overview

This integration implements OAuth 2.0 token refresh to ensure your SmartThings connection never expires. With proper setup, you configure it once and tokens renew automatically forever.

## The Problem

SmartThings changed their token policy in December 2024:
- **Old PAT tokens**: Continue working indefinitely (grandfathered in)
- **New PAT tokens**: Expire after 24 hours
- **Solution**: Use OAuth 2.0 refresh tokens for automatic renewal

## How It Works

### Token Architecture

\`\`\`
┌─────────────────────┐
│ Initial Setup       │
├─────────────────────┤
│ Access Token (24h)  │
│ Refresh Token (∞)   │
└─────────────────────┘
           │
           ▼
┌─────────────────────┐
│ Stored Securely in  │
│ Home Assistant      │
└─────────────────────┘
           │
           ▼
   Every API Call
┌─────────────────────┐
│ Check Token Expiry  │
├─────────────────────┤
│ >5 min? Use it      │
│ <5 min? Refresh it  │
└─────────────────────┘
           │
           ▼
   ┌────────────────┐
   │ New Access     │
   │ Token (24h)    │
   └────────────────┘
\`\`\`

### Refresh Mechanism

1. **Configuration Phase**:
   - User provides Access Token and Refresh Token
   - Both stored securely in Home Assistant config
   - Token expiry time recorded

2. **Before Each Request**:
   - Check how long until token expires
   - If more than 5 minutes: use current token
   - If less than 5 minutes: refresh immediately

3. **Token Refresh Process**:
   - Use Refresh Token to request new Access Token
   - SmartThings API returns: `{access_token, expires_in, (refresh_token)}`
   - Store new Access Token and expiry time
   - Optionally update Refresh Token (if rotated)

4. **Automatic Updates**:
   - New tokens automatically saved to config
   - Survives Home Assistant restarts
   - Works even if TV is offline (token just renews)

## Configuration

### During Setup

When you first configure the integration:

1. **Access Token** (Required):
   \`\`\`
   Enter your SmartThings OAuth access token
   (used for API authentication)
   \`\`\`

2. **Refresh Token** (Required):
   \`\`\`
   Enter your SmartThings OAuth refresh token
   (used for automatic renewal)
   \`\`\`

Both are required for automatic refresh to work.

### Updating Tokens

If you need to update tokens later:

1. Go to: **Settings → Devices & Services**
2. Find your Samsung Remote integration
3. Click **Options** (gear icon)
4. Update **Access Token** and/or **Refresh Token**
5. Click **Submit**

Tokens are masked for security (showing only last 8 characters).

## Technical Implementation

### Refresh Function

The integration uses the OAuth 2.0 Refresh Token Grant:

\`\`\`python
POST https://auth-global.smartthings.com/oauth/token

Parameters:
  grant_type: "refresh_token"
  refresh_token: "<your_refresh_token>"
  client_id: "homeassistant-samsung-remote"

Response:
{
  "access_token": "new_token_here",
  "expires_in": 86400,  # 24 hours in seconds
  "token_type": "Bearer",
  "refresh_token": "new_or_same_refresh_token"
}
\`\`\`

### Refresh Timing

- **Check interval**: Before every API call
- **Renewal threshold**: 5 minutes before expiry
- **Frequency**: Usually once per day if actively used
- **Overhead**: Minimal (just a timestamp check)

### Storage

Tokens stored in Home Assistant config entry:

\`\`\`python
{
  "device_id": "device-123",
  "api_method": "smartthings",
  "smartthings_access_token": "access_token_here",
  "smartthings_refresh_token": "refresh_token_here",
  "smartthings_token_expires": 1734567890  # Unix timestamp
}
\`\`\`

Encrypted by Home Assistant's storage system.

## Troubleshooting

### Refresh Failing: "No refresh token available"

**Cause**: Setup without refresh token
**Solution**: Update integration to add refresh token:
1. Settings → Devices & Services → Samsung Remote → Options
2. Add your **Refresh Token**
3. Click Submit

### Logs Show: "Failed to refresh token: 401"

**Cause**: Refresh token is invalid or revoked
**Solution**:
1. Check refresh token at: https://account.smartthings.com/tokens
2. If revoked, generate a new token
3. Update in Home Assistant settings

### "Token validated successfully but refresh failed"

**Cause**: Access token valid, but refresh token issue
**Solution**:
1. Verify refresh token still exists in SmartThings account
2. Try refreshing in SmartThings account settings
3. Generate fresh tokens if needed

### Tokens Keep Failing After 24 Hours

**Should NOT happen** - This indicates an error in the refresh flow:

1. **Check logs**:
   \`\`\`
   Settings → System → Logs
   Search: "samsung_remote" or "token"
   \`\`\`

2. **Look for patterns**:
   - "Failed to refresh token" = Refresh token issue
   - "401 Unauthorized" = Both tokens invalid
   - "Connection timeout" = Network issue

3. **Manual refresh if needed**:
   \`\`\`yaml
   service: samsung_remote.refresh_oauth_token
   data:
     entry_id: "your_entry_id"
   \`\`\`

### "Invalid token" but logs show successful refresh

**Cause**: Tokens refreshed but not saved to config
**Solution**:
1. Restart Home Assistant
2. Check if tokens persisted
3. If not, update integration with fresh tokens

## Best Practices

### Token Security

1. **Never share tokens** - Treat like passwords
2. **Store securely** - Home Assistant handles encryption
3. **Revoke when done** - If moving to new setup
4. **Rotate periodically** - Good security practice (once per month)

### Monitoring

Enable debug logging to monitor token refresh:

\`\`\`yaml
# configuration.yaml
logger:
  logs:
    custom_components.samsung_remote: debug
\`\`\`

### Backup Strategy

1. **Store refresh token** somewhere safe
2. **Note original access token** for comparison
3. **If Home Assistant fails**: Can quickly restore with stored tokens
4. **Document** the token setup date

## Rate Limits

SmartThings limits token refresh operations:
- Per token: 100 refreshes per day
- Per user: 1000 refreshes per day
- Integration: Only refreshes when needed (efficient)

You'll never hit these limits with normal usage.

## FAQ

**Q: Do I need to manually refresh tokens?**
A: No! The integration does it automatically.

**Q: Will refresh tokens expire?**
A: No! Refresh tokens are indefinite.

**Q: What if I have multiple Home Assistant instances?**
A: Each can use same token. They'll refresh independently.

**Q: Can I see when token was last refreshed?**
A: Enable debug logs to see refresh messages.

**Q: What happens if internet goes down?**
A: Token refresh is skipped (only works online anyway).

**Q: Can I use same token for multiple integrations?**
A: Yes, but each instance refreshes independently.

## Migration from PAT to OAuth

If you have an old PAT that still works:

1. **Keep using it** - Grandfathered PATs work indefinitely
2. **When regenerating**:
   - Get new OAuth tokens instead
   - Update in Home Assistant settings
   - You're now using automatic refresh

3. **No downtime** - Can switch tokens anytime

## Advanced: Manual Token Refresh

For debugging or forced refresh:

\`\`\`yaml
service: samsung_remote.refresh_oauth_token
data:
  entry_id: "a1b2c3d4e5f6g7h8"
\`\`\`

Check logs to verify:
\`\`\`
SmartThings OAuth token refreshed successfully
\`\`\`

## Support

- **Issue**: https://github.com/Qlimuli/samsung-tv-remote-HA/issues
- **Documentation**: docs/SMARTTHINGS_SETUP.md
- **API Docs**: https://developer.smartthings.com/docs/
