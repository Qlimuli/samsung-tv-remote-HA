# Samsung Remote - Home Assistant Integration

A HACS-compatible Home Assistant custom integration for controlling Samsung Smart TVs via remote commands.

## Features

- **SmartThings API Support** (Recommended) - Cloud-based control via SmartThings
- **Local Tizen Support** (Fallback) - Direct control over local network
- **UI Configuration Flow** - No YAML configuration needed
- **Standard remote.send_command Service** - Compatible with automations and voice assistants
- **Secure Token Storage** - Personal access tokens stored securely
- **20+ Remote Commands** - POWER, VOLUME, CHANNEL, NUMPAD, and more
- **Multi-language Support** - English and German translations

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

1. Go to https://account.smartthings.com/tokens
2. Generate a new Personal Access Token with the following scopes:
   - `devices:read`
   - `devices:execute`
3. In Home Assistant, go to Settings > Devices & Services > Create Integration
4. Search for "Samsung Remote"
5. Select "SmartThings API" as connection method
6. Paste your token
7. Select your Samsung TV from the list
8. Done!

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

- **Power**: POWER
- **Volume**: VOLUME_UP, VOLUME_DOWN
- **Channel**: CHANNEL_UP, CHANNEL_DOWN
- **Navigation**: UP, DOWN, LEFT, RIGHT, ENTER, BACK, HOME
- **Numpad**: 0-9
- **Playback**: PLAY, PAUSE, STOP, REWIND, FAST_FORWARD
- **Color Buttons**: RED, GREEN, YELLOW, BLUE
- **Special**: SOURCE, GUIDE, INFO, MENU, EXIT

## Troubleshooting

### "Invalid SmartThings token"
- Verify the token is still active at https://account.smartthings.com/tokens
- Regenerate a new token if needed
- Ensure token has `devices:read` and `devices:execute` scopes

### "No Samsung TVs found"
- Verify TV is added to your SmartThings account
- Check TV is online and connected to network
- Log in to SmartThings app and verify TV appears there

### "Connection failed" (Local Tizen)
- Verify TV IP address is correct
- Ensure TV is on and connected to network
- Check firewall isn't blocking port 8001
- Try enabling "Remote Management" on TV settings

### Commands not working
- Verify remote entity exists in Home Assistant
- Check logs for error messages: Settings > System > Logs
- Try command via Developer Tools > Services

## License

MIT - See LICENSE file

## Support

For issues and feature requests, visit: https://github.com/Qlimuli/samsung-tv-remote-HA/issues

## Changelog

### 1.0.0 - Initial Release
- SmartThings API integration
- Local Tizen fallback
- UI config flow
- 20+ remote commands
- Multi-language support
