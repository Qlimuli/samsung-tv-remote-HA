# SmartThings OAuth 2.0 Setup Guide

## 🎯 Warum OAuth 2.0?

- ✅ **Tokens laufen NIE ab** - Automatische Erneuerung
- ✅ **Keine manuelle Wartung** - Komplett automatisch
- ✅ **Sicher** - Industry-Standard OAuth 2.0
- ✅ **Stabil** - Keine täglichen Token-Updates mehr

---

## 📋 Voraussetzungen

- Home Assistant mit externer URL (für OAuth Callback)
- SmartThings Developer Account
- Samsung TV in SmartThings App verbunden

---

## 🚀 Schritt 1: SmartThings Developer Account

1. Gehe zu: https://smartthings.developer.samsung.com/
2. Melde dich mit deinem Samsung Account an
3. Akzeptiere die Developer Terms of Service

---

## 🛠️ Schritt 2: Projekt erstellen

1. Gehe zu: https://smartthings.developer.samsung.com/workspace/projects
2. Klicke auf **"New Project"**
3. **Project Name**: `Home Assistant Integration`
4. **Project Type**: Wähle **"Automation"**
5. Klicke **"Create Project"**

---

## 🔌 Schritt 3: App registrieren

1. Im Projekt, klicke auf **"Register App"**
2. **App Type**: Wähle **"Webhook Endpoint"**
3. **App Name**: `Home Assistant Samsung Remote`
4. **Description**: `OAuth integration for Samsung TV control`
5. **Target URL**: 
   ```
   https://your-home-assistant-url.com/api/webhook/smartthings
   ```
   ⚠️ Ersetze `your-home-assistant-url.com` mit deiner echten URL!

6. **Scopes** - Wähle BEIDE:
   - ☑️ `r:devices:*` (Read all devices)
   - ☑️ `x:devices:*` (Execute all devices)

7. Klicke **"Register App"**

---

## 🔑 Schritt 4: OAuth Client erstellen

1. Gehe zur **"OAuth Settings"** Tab
2. Klicke **"Add OAuth Client"**
3. **Redirect URI**:
   ```
   https://your-home-assistant-url.com/auth/external/callback
   ```
   ⚠️ Verwende deine echte Home Assistant externe URL!

4. Klicke **"Generate OAuth Client"**
5. **WICHTIG:** Kopiere sofort:
   - ✅ **Client ID** (sichtbar)
   - ✅ **Client Secret** (nur einmal sichtbar!)

⚠️ **Client Secret wird nur EINMAL angezeigt!** Speichere es sicher!

---

## 🏠 Schritt 5: Home Assistant Integration

1. Gehe zu: **Einstellungen** → **Geräte & Dienste**
2. Klicke **"+ Integration hinzufügen"**
3. Suche nach **"Samsung Remote"**
4. Wähle **"SmartThings API"**
5. Wähle **"OAuth 2.0 (Empfohlen)"**
6. Trage ein:
   - **Client ID**: (aus Schritt 4)
   - **Client Secret**: (aus Schritt 4)
7. Du wirst zu SmartThings weitergeleitet
8. **Authorisiere** die App
9. Du wirst zurück zu Home Assistant geleitet
10. Wähle deinen **Samsung TV** aus der Liste
11. **Fertig!** 🎉

---

## ✅ Token Status überprüfen

Nach dem Setup solltest du in den Logs sehen:

```
✅ Token refreshed successfully
Initialized with OAuth 2.0 (auto-refresh enabled)
```

---

## 🔄 Wie funktioniert Auto-Refresh?

1. **Access Token** läuft nach 24 Stunden ab
2. **5 Minuten** vor Ablauf: Automatischer Refresh
3. **Neuer Access Token** wird abgerufen
4. **Refresh Token** wird aktualisiert (falls rotiert)
5. **Tokens gespeichert** in Home Assistant Config
6. **Komplett transparent** - Du merkst nichts!

---

## 🆘 Troubleshooting

### "External URL required"

**Problem:** Home Assistant hat keine externe URL konfiguriert.

**Lösung:**
1. Gehe zu: **Einstellungen** → **System** → **Netzwerk**
2. Setze **"External URL"**: 
   ```
   https://deine-domain.com:8123
   ```
   oder verwende DuckDNS, Nabu Casa, etc.

### "Redirect URI mismatch"

**Problem:** Die Redirect URI in SmartThings stimmt nicht überein.

**Lösung:**
1. Gehe zu SmartThings Developer Console
2. Prüfe **OAuth Settings** → **Redirect URI**
3. Stelle sicher, es ist EXAKT:
   ```
   https://your-exact-url.com/auth/external/callback
   ```

### "Invalid client credentials"

**Problem:** Client ID oder Client Secret falsch eingegeben.

**Lösung:**
1. Prüfe auf Leerzeichen am Anfang/Ende
2. Client Secret wurde nur EINMAL angezeigt
3. Falls verloren: Generiere neuen OAuth Client

### "Token refresh failed"

**Problem:** Refresh Token ist ungültig oder widerrufen.

**Lösung:**
1. Lösche die Integration in Home Assistant
2. Widerrufe die App in SmartThings:
   - https://account.smartthings.com/tokens
3. Erstelle neue OAuth Credentials
4. Richte Integration neu ein

---

## 🔐 Sicherheit

### Client Secret schützen

- ❌ **Nie in Git committen**
- ❌ **Nie öffentlich teilen**
- ❌ **Nicht in Screenshots zeigen**
- ✅ **Nur in Home Assistant Config**
- ✅ **Backup verschlüsseln**

### OAuth Tokens widerrufen

Falls kompromittiert:

1. Gehe zu: https://account.smartthings.com/tokens
2. Finde deine App
3. Klicke **"Revoke"**
4. Erstelle neue Credentials
5. Richte Integration neu ein

---

## 📊 Vergleich: OAuth vs PAT

| Feature | OAuth 2.0 | PAT (neu) | PAT (alt) |
|---------|-----------|-----------|-----------|
| Setup-Aufwand | Hoch | Niedrig | Niedrig |
| Token-Erneuerung | ✅ Automatisch | ❌ Manuell (täglich) | ✅ Nie nötig |
| Läuft ab nach | ♾️ Nie | 24 Stunden | ♾️ Nie |
| Empfohlen | ✅ Ja | ❌ Nein | ✅ Ja (falls vorhanden) |

---

## 🎓 Weiterführende Links

- SmartThings Developer Console: https://smartthings.developer.samsung.com/
- SmartThings API Docs: https://developer.smartthings.com/docs/
- Home Assistant External URL: https://www.home-assistant.io/integrations/http/#external_url
- Integration Repository: https://github.com/Qlimuli/samsung-tv-remote-HA

---

## 💬 Support

Probleme mit dem Setup?

1. **Prüfe Logs**: Einstellungen → System → Logs
2. **GitHub Issue**: https://github.com/Qlimuli/samsung-tv-remote-HA/issues
3. **Home Assistant Community**: https://community.home-assistant.io/

---

## ✨ Fertig!

Nach dem Setup:
- Tokens erneuern sich automatisch
- Keine Wartung mehr nötig
- TV-Steuerung funktioniert immer
- Entspannt zurücklehnen! 🎬🍿
