# Samsung TV Command-Kompatibilität

## Übersicht

Die Samsung Remote Integration unterstützt zwei API-Methoden:
1. **SmartThings API** (Cloud-basiert)
2. **Tizen Local API** (Lokales Netzwerk)

⚠️ **Wichtig:** Die SmartThings API unterstützt nur eine **begrenzte Anzahl an Commands**!

---

## ✅ Mit SmartThings API unterstützte Commands

Diese Commands funktionieren mit **beiden** API-Methoden (SmartThings + Tizen Local):

### Navigation
- `UP` - Hoch
- `DOWN` - Runter
- `LEFT` - Links
- `RIGHT` - Rechts
- `OK` - Bestätigen (wird als ENTER im Button angezeigt)
- `BACK` - Zurück

### Menü
- `HOME` - Home
- `MENU` - Menü
- `EXIT` - Beenden

### Lautstärke
- `MUTE` - Stumm schalten

### Wiedergabe
- `PLAY` - Abspielen
- `PAUSE` - Pause
- `STOP` - Stopp
- `REWIND` - Zurückspulen
- `FF` - Vorspulen
- `PLAY_BACK` - Wiedergabe zurück

### Quellen
- `SOURCE` - Quellenwahl

---

## ⚠️ Nur mit Tizen Local API

Diese Commands funktionieren **NUR** wenn du die **Tizen Local API** verwendest:

### Power
- `POWER` - Ein/Aus
- `POWEROFF` - Ausschalten

### Lautstärke
- `VOLUP` - Lautstärke +
- `VOLDOWN` - Lautstärke -

### Kanäle
- `CHUP` - Kanal +
- `CHDOWN` - Kanal -
- `PRECH` - Vorheriger Kanal

### HDMI
- `HDMI` - HDMI
- `HDMI1` - HDMI 1
- `HDMI2` - HDMI 2
- `HDMI3` - HDMI 3
- `HDMI4` - HDMI 4

### Guide & Info
- `GUIDE` - Programmführer
- `CH_LIST` - Kanalliste
- `TOOLS` - Extras
- `INFO` - Info

### Farbtasten
- `RED` - Rote Taste
- `GREEN` - Grüne Taste
- `YELLOW` - Gelbe Taste
- `BLUE` - Blaue Taste

### Nummern
- `NUM0` bis `NUM9` - Ziffern 0-9

### Zusätzlich
- `PICTURE_MODE` - Bildmodus
- `SOUND_MODE` - Tonmodus
- `SETTINGS` - Einstellungen
- `SLEEP` - Sleep Timer
- `ASPECT` - Seitenverhältnis
- `CAPTION` - Untertitel
- `E_MANUAL` - Elektronisches Handbuch
- `SEARCH` - Suche
- `REC` - Aufnahme

---

## 🔧 Welche API-Methode verwende ich?

Du kannst in Home Assistant nachschauen:

1. Gehe zu **Einstellungen** → **Geräte & Dienste**
2. Klicke auf **Samsung Remote**
3. Klicke auf dein TV-Gerät
4. Unter "Diagnostik" siehst du `api_method`:
   - `smartthings` = Du verwendest SmartThings API (begrenzte Commands)
   - `tizen_local` = Du verwendest Tizen Local API (alle Commands)

---

## 💡 Empfehlung

### Verwende SmartThings wenn:
- ✅ Du keine lokale Netzwerkverbindung zum TV hast
- ✅ Du den TV über das Internet steuern willst
- ✅ Die grundlegenden Commands (Navigation, Play/Pause) ausreichen

### Verwende Tizen Local wenn:
- ✅ Du alle Commands brauchst (Lautstärke, Kanal, HDMI, etc.)
- ✅ Dein TV im gleichen Netzwerk ist
- ✅ Du schnellere Reaktionszeiten willst (keine Cloud)

---

## 🐛 Fehlermeldung bei nicht unterstützten Commands

Wenn du SmartThings verwendest und einen nicht unterstützten Command sendest, erscheint:

\`\`\`
WARNING: Command 'VOLUP' is not supported by SmartThings API. 
This command only works with Tizen Local API.
Supported SmartThings commands: BACK, DOWN, EXIT, FF, HOME, LEFT, MENU, MUTE, OK, PAUSE, PLAY, PLAY_BACK, REWIND, RIGHT, SOURCE, STOP, UP
\`\`\`

**Lösung:** Wechsle zur Tizen Local API oder verwende nur die unterstützten Commands.

---

## 🔄 API-Methode wechseln

Um von SmartThings zu Tizen Local (oder umgekehrt) zu wechseln:

1. **Einstellungen** → **Geräte & Dienste**
2. Klicke auf **Samsung Remote**
3. Lösche die bestehende Integration
4. Füge die Integration neu hinzu
5. Wähle die gewünschte API-Methode

**Hinweis:** Deine Dashboard-Konfiguration bleibt erhalten, da die Entity-IDs gleich bleiben.

---

## 📊 Vergleichstabelle

| Feature | SmartThings API | Tizen Local API |
|---------|----------------|-----------------|
| Navigation (D-Pad) | ✅ | ✅ |
| Play/Pause | ✅ | ✅ |
| Home/Menu | ✅ | ✅ |
| Mute | ✅ | ✅ |
| Lautstärke +/- | ❌ | ✅ |
| Kanal +/- | ❌ | ✅ |
| HDMI-Auswahl | ❌ | ✅ |
| Zifferntasten | ❌ | ✅ |
| Farbtasten | ❌ | ✅ |
| Power On/Off | ❌ | ✅ |
| Internet-Steuerung | ✅ | ❌ |
| Lokales Netzwerk | ❌ | ✅ |

---

## 🆘 Häufige Probleme

### "Command ENTER not found" / Error 422

**Problem:** SmartThings API kennt kein "ENTER" Command.

**Lösung:** Wird automatisch zu "OK" übersetzt (bereits behoben in v1.1.0+)

### Lautstärke/Kanal-Buttons funktionieren nicht

**Problem:** Du verwendest SmartThings API, diese Commands sind nicht verfügbar.

**Lösung:** 
- Option 1: Wechsle zu Tizen Local API
- Option 2: Nutze nur die in der Remote Entity verfügbaren Lautstärke-Services von Home Assistant

### Alle Buttons zeigen "nicht verfügbar"

**Problem:** TV ist aus oder nicht erreichbar.

**Lösung:**
- Prüfe ob TV eingeschaltet ist
- Prüfe Netzwerkverbindung
- Bei SmartThings: Prüfe Internet-Verbindung
