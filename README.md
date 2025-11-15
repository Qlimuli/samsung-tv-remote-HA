# Samsung Remote - Home Assistant Integration

A HACS-compatible Home Assistant custom integration for controlling Samsung Smart TVs via remote commands.

## Features

- **SmartThings API Support** (Recommended) - Cloud-based control via SmartThings with OAuth token auto-refresh
- **Local Tizen Support** (Fallback) - Direct control over local network
- **UI Configuration Flow** - No YAML configuration needed
- **Standard remote.send_command Service** - Compatible with automations and voice assistants
- **Secure Token Storage** - OAuth refresh tokens with automatic renewal
- **40+ Remote Commands** - POWER, NAVIGATION, PLAYBACK, and more
- **Multi-language Support** - English and German translations
- **Automatic Token Refresh** - OAuth tokens automatically renewed before expiry
<img width="307" height="828" alt="image" src="https://github.com/user-attachments/assets/fa374cb6-fc02-4bae-af7f-750e74eb93a3" />
<img width="537" height="750" alt="image" src="https://github.com/user-attachments/assets/56fc977b-1bd8-416f-8b77-15496c83c5c4" />


## Installation

### Via HACS (Recommended)

1. Open HACS in Home Assistant
2. Click "Integrations" 
3. Click the "+" button and search for "Samsung Remote"
4. Click "Install"
5. Restart Home Assistant

### Manual Installation

1. Clone this repository to your `custom_components` folder:
   \`\`\`bash
   git clone https://github.com/Qlimuli/samsung-tv-remote-HA.git \
     ~/.homeassistant/custom_components/samsung_remote
   \`\`\`
2. Restart Home Assistant

## Setup

### SmartThings Method (Recommended)

The integration now supports **OAuth 2.0 with automatic token refresh**. This means tokens never expire!

#### Option A: New Setup (OAuth - Recommended)

1. In Home Assistant, go to Settings > Devices & Services > Create Integration
2. Search for "Samsung Remote"
3. Select "SmartThings API" as connection method
4. You'll be asked for:
   - **Access Token**: Your current OAuth access token
   - **Refresh Token**: Your OAuth refresh token for automatic renewal
5. Select your Samsung TV from the list
6. Done! Tokens will auto-refresh every 24 hours

#### Option B: Existing PAT Token (Legacy)

If you have an existing Personal Access Token that still works:

1. Go to https://account.smartthings.com/tokens
2. Copy your PAT token
3. In Home Assistant setup, paste it as both access token and leave refresh token empty
4. **Note**: New PATs expire after 24 hours - upgrade to OAuth tokens for automatic renewal

See **docs/SMARTTHINGS_SETUP.md** for detailed instructions on obtaining OAuth tokens.

### Local Tizen Method

1. Find your TV's IP address (Settings > Network > Status)
2. In Home Assistant, go to Settings > Devices & Services > Create Integration
3. Search for "Samsung Remote"
4. Select "Local Tizen" as connection method
5. Enter your TV's IP address
6. Done!

## Usage

### Basic Remote Control

\`\`\`yaml
service: remote.send_command
target:
  entity_id: remote.samsung_tv_livingroom
data:
  command:
    - "POWER"
\`\`\`

### Multiple Commands

\`\`\`yaml
service: remote.send_command
target:
  entity_id: remote.samsung_tv_livingroom
data:
  command:
    - "POWER"
    - "HOME"
\`\`\`

### In Automations

\`\`\`yaml
automation:
  - alias: "Turn on TV when arriving home"
    trigger:
      platform: state
      entity_id: person.your_name
      to: "home"
    action:
      service: remote.send_command
      target:
        entity_id: remote.samsung_tv_livingroom
      data:
        command:
          - "POWER"
\`\`\`

## Supported Commands

**SmartThings API** (Limited set):
- **Navigation**: UP, DOWN, LEFT, RIGHT, OK, BACK, HOME, MENU, EXIT
- **Volume**: MUTE
- **Playback**: PLAY, PAUSE, STOP, REWIND, FF, PLAY_BACK
- **Source**: SOURCE

**Local Tizen API** (Full set - 40+ commands):
- All SmartThings commands plus:
- **Power**: POWER, POWEROFF
- **Volume**: VOLUME_UP, VOLUME_DOWN
- **Channel**: CHANNEL_UP, CHANNEL_DOWN, PRECH
- **HDMI**: HDMI, HDMI1-4
- **Numpad**: 0-9
- **Color Buttons**: RED, GREEN, YELLOW, BLUE
- **Special**: GUIDE, CH_LIST, TOOLS, INFO, PICTURE_MODE, SOUND_MODE, SLEEP, ASPECT, CAPTION, SETTINGS, E_MANUAL, SEARCH, REC

## Token Refresh

### Automatic Token Refresh

With OAuth tokens, the integration automatically:
1. Checks token expiry before each API call
2. Refreshes tokens 5 minutes before expiry
3. Updates stored tokens securely
4. **You never need to do anything!**

### Manual Token Refresh

If needed, you can manually refresh tokens:

\`\`\`yaml
service: samsung_remote.refresh_oauth_token
data:
  entry_id: "your_config_entry_id"
\`\`\`

See **docs/TOKEN_REFRESH_GUIDE.md** for detailed technical information.

## Troubleshooting

### "Invalid SmartThings token"
- Verify your OAuth tokens are still active
- Tokens are automatically refreshed - this usually means a connectivity issue
- Check your home internet connection
- Verify TV is still in your SmartThings account

### "No Samsung TVs found"
- Verify TV is added to your SmartThings account
- Check TV is online and connected to network
- Log in to SmartThings app and verify TV appears there

### "Connection failed" (Local Tizen)
- Verify TV IP address is correct
- Ensure TV is on and connected to network
- Check firewall isn't blocking port 8001
- Try enabling "Remote Management" on TV settings

### Token keeps expiring (SmartThings)
- This should NOT happen with OAuth refresh tokens
- Check logs: Settings > System > Logs
- If still failing, regenerate new tokens
- See docs/TOKEN_REFRESH_GUIDE.md for troubleshooting

## License

MIT - See LICENSE file

## Support

For issues and feature requests, visit: https://github.com/Qlimuli/samsung-tv-remote-HA/issues
