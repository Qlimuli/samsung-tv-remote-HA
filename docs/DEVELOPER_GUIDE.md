# Developer Guide - Samsung Remote Integration

## Architecture Overview

### Component Structure

\`\`\`
custom_components/samsung_remote/
├── __init__.py          # Integration setup and entry point
├── config_flow.py       # UI configuration flow
├── remote.py            # Remote entity implementation
├── const.py             # Constants and key mappings
├── api/
│   ├── smartthings.py   # SmartThings API client
│   └── tizen_local.py   # Local Tizen API client
└── translations/        # i18n strings
\`\`\`

### Data Flow

1. **Config Flow**: User adds integration → Chooses API method → Authenticates → Selects device
2. **Setup**: `async_setup_entry` creates RemoteEntity with appropriate API client
3. **Command**: User calls `remote.send_command` → RemoteEntity sends to API client → Device executes

## API Clients

### SmartThings API

- **Authentication**: Personal Access Token (PAT)
- **Discovery**: Fetches device list via REST API
- **Commands**: Sends via `/devices/{id}/commands` endpoint
- **Retry**: Implements exponential backoff on rate limits

\`\`\`python
from custom_components.samsung_remote.api.smartthings import SmartThingsAPI

api = SmartThingsAPI(hass, token)
devices = await api.get_devices()
await api.send_command(device_id, "POWER")
\`\`\`

### Tizen Local API

- **Authentication**: Optional PSK (Pre-Shared Key)
- **Discovery**: Validates connection to TV IP
- **Commands**: Sends via local socket/websocket
- **Fallback**: Used when SmartThings not available

\`\`\`python
from custom_components.samsung_remote.api.tizen_local import TizenLocalAPI

api = TizenLocalAPI("192.168.1.100", psk="key")
await api.validate_connection()
await api.send_command("POWER")
\`\`\`

## Key Mapping

Samsung TV commands are mapped in `const.py`:

\`\`\`python
SAMSUNG_KEY_MAP = {
    "POWER": "KEY_POWER",
    "VOLUME_UP": "KEY_VOLUME_UP",
    # ... more mappings
}
\`\`\`

To add new commands:
1. Find the Tizen key code from Samsung documentation
2. Add to `SAMSUNG_KEY_MAP` in `const.py`
3. Add to `SUPPORTED_COMMANDS`
4. Update translations

## Testing

### Running Tests

\`\`\`bash
pytest tests/ --cov=custom_components/samsung_remote
\`\`\`

### Test Structure

- `tests/conftest.py` - Shared fixtures (mock APIs)
- `tests/test_config_flow.py` - Config flow tests
- `tests/test_remote_entity.py` - Remote entity tests
- `tests/test_smartthings_api.py` - SmartThings API tests
- `tests/test_tizen_api.py` - Tizen API tests

### Adding Tests

1. Create test file in `tests/`
2. Use `mock_smartthings_api` or `mock_tizen_api` fixtures
3. Mock external calls with `AsyncMock` and `patch`
4. Run: `pytest tests/test_*.py`

## Configuration

### Config Entry Data Structure

\`\`\`python
{
    "device_id": "smartthings-device-id or ip-address",
    "device_name": "User-friendly device name",
    "api_method": "smartthings" or "tizen_local",
    "smartthings_token": "PAT (if using SmartThings)",
    "local_ip": "IP address (if using local Tizen)",
    "local_psk": "Optional PSK (if using local Tizen)",
}
\`\`\`

## Internationalization

Translations stored in `custom_components/samsung_remote/translations/`:

- `en.json` - English
- `de.json` - German

Add new language:
1. Create `xx.json` in translations folder
2. Copy structure from `en.json`
3. Translate all strings

## Logging

Enable debug logging to troubleshoot:

\`\`\`yaml
logger:
  logs:
    custom_components.samsung_remote: debug
\`\`\`

## Common Issues

### Token Validation Fails
- Check token still exists at https://account.smartthings.com/tokens
- Regenerate if needed
- Ensure scopes: `devices:read`, `devices:execute`

### No Devices Found
- TV must be in SmartThings account
- TV must be online
- Check SmartThings app shows TV

### Local Connection Fails
- Verify TV IP address
- Check TV on same network
- Verify "Remote Management" enabled on TV
- Check firewall port 8001

## Future Enhancements

- [ ] Support for more Tizen key codes
- [ ] Unified app/channel launching
- [ ] TV state polling (power status, volume)
- [ ] Multi-TV support with virtual remotes
- [ ] Custom button mappings per user
- [ ] Long-press support for scancode inputs

## Release Process

1. Update version in `manifest.json`
2. Update `CHANGELOG.md`
3. Commit: `git commit -m "Release v1.x.x"`
4. Tag: `git tag -a v1.x.x -m "Release v1.x.x"`
5. Push: `git push origin main --tags`
6. GitHub Actions automatically creates release
