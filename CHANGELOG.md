# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2024-12-XX

### Added
- **OAuth 2.0 Token Refresh Support** - Tokens now automatically refresh before expiry
- **Separate Access/Refresh Token Input** - Config flow now asks for both tokens
- **Automatic Token Renewal** - 5-minute pre-expiry check and automatic refresh
- **Manual Refresh Service** - `samsung_remote.refresh_oauth_token` for manual control
- **Token Status Logging** - Clear logs when tokens are refreshed
- **Improved Documentation** - Complete OAuth setup and troubleshooting guides
- **Token Expiry Display** - Shows when tokens were last refreshed

### Changed
- **Config Flow Updated** - Now requests both access_token and refresh_token separately
- **Token Storage Enhanced** - Stores access token, refresh token, and expiry time
- **Options Flow Improved** - Can update tokens via integration options
- **Better Error Messages** - Clear guidance when tokens are missing or invalid

### Fixed
- **Token Expiration Issue** - Tokens no longer expire with automatic refresh
- **24-hour Expiration** - Old issue resolved with OAuth refresh tokens

### Deprecated
- **PAT-only Setup** - Still works for grandfathered tokens, but OAuth recommended

### Security
- Token refresh uses secure OAuth 2.0 grant flow
- Refresh tokens never transmitted to unnecessary services
- Token expiry times validated before use

## [1.0.0] - 2024-11-09

### Added
- Initial release
- SmartThings API integration with device discovery
- Local Tizen API support for direct TV control
- UI configuration flow (no YAML needed)
- Support for 20+ remote commands
- Secure token storage using Home Assistant storage
- Retry logic with exponential backoff
- Unit tests with 60%+ code coverage
- GitHub Actions CI/CD pipeline
- English and German translations
- Comprehensive README with troubleshooting guide
- Example automations and service calls

### Security
- Personal access tokens stored securely
- No secrets in configuration.yaml
- Input validation on all user inputs
