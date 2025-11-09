# Samsung TV Dashboard Remote Konfiguration

Dieses Dokument enthält verschiedene Dashboard-Layouts für deine Samsung TV Fernbedienung in Home Assistant.

## 🎮 Variante 1: Kompakte Fernbedienung (Empfohlen)

Diese Variante zeigt die wichtigsten Funktionen in einem kompakten Layout.

```yaml
type: vertical-stack
cards:
  # Header mit Power und Home
  - type: grid
    square: false
    columns: 3
    cards:
      - type: button
        entity: button.samsung_tv_power
        name: Ein/Aus
        show_state: false
        
      - type: button
        entity: button.samsung_tv_home
        name: Home
        show_state: false
        
      - type: button
        entity: button.samsung_tv_menu
        name: Menü
        show_state: false

  # Navigation (D-Pad)
  - type: grid
    square: true
    columns: 3
    cards:
      - type: button
        show_icon: false
        show_name: false
        tap_action:
          action: none
          
      - type: button
        entity: button.samsung_tv_up
        show_name: false
        
      - type: button
        show_icon: false
        show_name: false
        tap_action:
          action: none
          
      - type: button
        entity: button.samsung_tv_left
        show_name: false
        
      - type: button
        entity: button.samsung_tv_enter
        name: OK
        icon: mdi:circle
        
      - type: button
        entity: button.samsung_tv_right
        show_name: false
        
      - type: button
        show_icon: false
        show_name: false
        tap_action:
          action: none
          
      - type: button
        entity: button.samsung_tv_down
        show_name: false
        
      - type: button
        entity: button.samsung_tv_back
        show_name: false

  # Lautstärke & Kanäle
  - type: grid
    square: false
    columns: 3
    cards:
      - type: button
        entity: button.samsung_tv_volume_up
        name: Vol +
        
      - type: button
        entity: button.samsung_tv_mute
        name: Stumm
        
      - type: button
        entity: button.samsung_tv_channel_up
        name: CH +
        
      - type: button
        entity: button.samsung_tv_volume_down
        name: Vol -
        
      - type: button
        entity: button.samsung_tv_previous_channel
        name: Zurück
        icon: mdi:history
        
      - type: button
        entity: button.samsung_tv_channel_down
        name: CH -

  # Playback Controls
  - type: grid
    square: false
    columns: 4
    cards:
      - type: button
        entity: button.samsung_tv_rewind
        show_name: false
        
      - type: button
        entity: button.samsung_tv_play
        show_name: false
        
      - type: button
        entity: button.samsung_tv_pause
        show_name: false
        
      - type: button
        entity: button.samsung_tv_fast_forward
        show_name: false
```

---

## 🎯 Variante 2: Vollständige Fernbedienung

Diese Variante enthält ALLE verfügbaren Funktionen.

```yaml
type: vertical-stack
cards:
  # Power & Hauptmenü
  - type: grid
    square: false
    columns: 4
    cards:
      - type: button
        entity: button.samsung_tv_power
        name: Power
        
      - type: button
        entity: button.samsung_tv_poweroff
        name: Aus
        
      - type: button
        entity: button.samsung_tv_home
        name: Home
        
      - type: button
        entity: button.samsung_tv_menu
        name: Menü

  # Navigation
  - type: grid
    square: true
    columns: 3
    cards:
      - type: button
        show_icon: false
        show_name: false
        tap_action:
          action: none
          
      - type: button
        entity: button.samsung_tv_up
        show_name: false
        
      - type: button
        show_icon: false
        show_name: false
        tap_action:
          action: none
          
      - type: button
        entity: button.samsung_tv_left
        show_name: false
        
      - type: button
        entity: button.samsung_tv_enter
        name: OK
        icon: mdi:circle
        
      - type: button
        entity: button.samsung_tv_right
        show_name: false
        
      - type: button
        show_icon: false
        show_name: false
        tap_action:
          action: none
          
      - type: button
        entity: button.samsung_tv_down
        show_name: false
        
      - type: button
        entity: button.samsung_tv_back
        show_name: false

  # Lautstärke & Kanäle
  - type: grid
    square: false
    columns: 4
    cards:
      - type: button
        entity: button.samsung_tv_volume_up
        name: Vol +
        
      - type: button
        entity: button.samsung_tv_mute
        name: Stumm
        
      - type: button
        entity: button.samsung_tv_channel_up
        name: CH +
        
      - type: button
        entity: button.samsung_tv_info
        name: Info
        
      - type: button
        entity: button.samsung_tv_volume_down
        name: Vol -
        
      - type: button
        entity: button.samsung_tv_previous_channel
        icon: mdi:history
        show_name: false
        
      - type: button
        entity: button.samsung_tv_channel_down
        name: CH -
        
      - type: button
        entity: button.samsung_tv_exit
        name: Exit

  # Playback
  - type: grid
    square: false
    columns: 5
    cards:
      - type: button
        entity: button.samsung_tv_rewind
        show_name: false
        
      - type: button
        entity: button.samsung_tv_play
        show_name: false
        
      - type: button
        entity: button.samsung_tv_pause
        show_name: false
        
      - type: button
        entity: button.samsung_tv_stop
        show_name: false
        
      - type: button
        entity: button.samsung_tv_fast_forward
        show_name: false

  # HDMI & Quellen
  - type: grid
    square: false
    columns: 5
    cards:
      - type: button
        entity: button.samsung_tv_source
        name: Quelle
        
      - type: button
        entity: button.samsung_tv_hdmi1
        name: HDMI 1
        
      - type: button
        entity: button.samsung_tv_hdmi2
        name: HDMI 2
        
      - type: button
        entity: button.samsung_tv_hdmi3
        name: HDMI 3
        
      - type: button
        entity: button.samsung_tv_hdmi4
        name: HDMI 4

  # Programmführer & Einstellungen
  - type: grid
    square: false
    columns: 4
    cards:
      - type: button
        entity: button.samsung_tv_guide
        name: Guide
        
      - type: button
        entity: button.samsung_tv_channel_list
        name: Kanalliste
        
      - type: button
        entity: button.samsung_tv_tools
        name: Extras
        
      - type: button
        entity: button.samsung_tv_settings
        name: Einstellungen

  # Bild & Ton
  - type: grid
    square: false
    columns: 2
    cards:
      - type: button
        entity: button.samsung_tv_picture_mode
        name: Bildmodus
        
      - type: button
        entity: button.samsung_tv_sound_mode
        name: Tonmodus

  # Farbtasten
  - type: grid
    square: false
    columns: 4
    cards:
      - type: button
        entity: button.samsung_tv_red
        name: Rot
        
      - type: button
        entity: button.samsung_tv_green
        name: Grün
        
      - type: button
        entity: button.samsung_tv_yellow
        name: Gelb
        
      - type: button
        entity: button.samsung_tv_blue
        name: Blau

  # Zifferntasten
  - type: grid
    square: true
    columns: 3
    cards:
      - type: button
        entity: button.samsung_tv_number_1
        name: "1"
        
      - type: button
        entity: button.samsung_tv_number_2
        name: "2"
        
      - type: button
        entity: button.samsung_tv_number_3
        name: "3"
        
      - type: button
        entity: button.samsung_tv_number_4
        name: "4"
        
      - type: button
        entity: button.samsung_tv_number_5
        name: "5"
        
      - type: button
        entity: button.samsung_tv_number_6
        name: "6"
        
      - type: button
        entity: button.samsung_tv_number_7
        name: "7"
        
      - type: button
        entity: button.samsung_tv_number_8
        name: "8"
        
      - type: button
        entity: button.samsung_tv_number_9
        name: "9"
        
      - type: button
        show_icon: false
        show_name: false
        tap_action:
          action: none
          
      - type: button
        entity: button.samsung_tv_number_0
        name: "0"
        
      - type: button
        show_icon: false
        show_name: false
        tap_action:
          action: none
```

---

## 🎨 Variante 3: Moderne Kachel-Ansicht

Diese Variante nutzt moderne Tile-Cards für ein sauberes Design.

```yaml
type: vertical-stack
cards:
  # Status & Power
  - type: tile
    entity: remote.samsung_tv_remote
    name: Samsung TV
    icon: mdi:television
    features:
      - type: button
        entity: button.samsung_tv_power
        icon: mdi:power
        
  # Quick Actions
  - type: grid
    square: false
    columns: 4
    cards:
      - type: tile
        entity: button.samsung_tv_home
        show_entity_picture: false
        vertical: true
        
      - type: tile
        entity: button.samsung_tv_menu
        vertical: true
        
      - type: tile
        entity: button.samsung_tv_back
        vertical: true
        
      - type: tile
        entity: button.samsung_tv_exit
        vertical: true

  # Navigation
  - type: grid
    title: Navigation
    square: true
    columns: 3
    cards:
      - type: button
        show_icon: false
        tap_action:
          action: none
          
      - type: tile
        entity: button.samsung_tv_up
        vertical: true
        
      - type: button
        show_icon: false
        tap_action:
          action: none
          
      - type: tile
        entity: button.samsung_tv_left
        vertical: true
        
      - type: tile
        entity: button.samsung_tv_enter
        icon: mdi:checkbox-blank-circle
        vertical: true
        
      - type: tile
        entity: button.samsung_tv_right
        vertical: true
        
      - type: button
        show_icon: false
        tap_action:
          action: none
          
      - type: tile
        entity: button.samsung_tv_down
        vertical: true
        
      - type: button
        show_icon: false
        tap_action:
          action: none

  # Lautstärke
  - type: grid
    title: Lautstärke & Kanäle
    square: false
    columns: 3
    cards:
      - type: tile
        entity: button.samsung_tv_volume_up
        vertical: true
        
      - type: tile
        entity: button.samsung_tv_mute
        vertical: true
        
      - type: tile
        entity: button.samsung_tv_channel_up
        vertical: true
        
      - type: tile
        entity: button.samsung_tv_volume_down
        vertical: true
        
      - type: tile
        entity: button.samsung_tv_previous_channel
        vertical: true
        
      - type: tile
        entity: button.samsung_tv_channel_down
        vertical: true

  # Playback
  - type: grid
    title: Wiedergabe
    square: false
    columns: 5
    cards:
      - type: tile
        entity: button.samsung_tv_rewind
        vertical: true
        
      - type: tile
        entity: button.samsung_tv_play
        vertical: true
        
      - type: tile
        entity: button.samsung_tv_pause
        vertical: true
        
      - type: tile
        entity: button.samsung_tv_stop
        vertical: true
        
      - type: tile
        entity: button.samsung_tv_fast_forward
        vertical: true
```

---

## 📱 Installation

### Schritt 1: Entity-Namen anpassen

Ersetze in den YAML-Konfigurationen:
- `samsung_tv` mit dem Namen deines TV-Geräts aus der Integration
- Beispiel: Wenn dein TV "Wohnzimmer TV" heißt, wird aus `button.samsung_tv_power` → `button.wohnzimmer_tv_power`

### Schritt 2: Dashboard hinzufügen

1. Gehe zu **Einstellungen** → **Dashboards**
2. Öffne dein Dashboard oder erstelle ein neues
3. Klicke **Bearbeiten** (Stift-Symbol oben rechts)
4. Klicke **Karte hinzufügen** (+ Symbol unten rechts)
5. Scrolle runter zu **Manuell** und klicke darauf
6. Kopiere eine der YAML-Konfigurationen oben
7. Füge sie in den Editor ein
8. Klicke **Speichern**

### Schritt 3: Dashboard speichern

Klicke oben rechts auf **Fertig**

---

## 🎯 Tipps

### Entity-Namen herausfinden

Gehe zu **Einstellungen** → **Geräte & Dienste** → **Integrationen** → **Samsung Remote**

Klicke auf dein TV-Gerät, dort siehst du alle verfügbaren Button-Entities.

### Anpassungen

**Farben ändern:**
```yaml
- type: button
  entity: button.samsung_tv_red
  icon_color: red
```

**Größe ändern:**
```yaml
- type: grid
  columns: 5  # Mehr Spalten = kleinere Buttons
```

**Titel hinzufügen:**
```yaml
- type: grid
  title: Lautstärke
  columns: 3
```

---

## 🚀 Erweiterte Optionen

### Conditional Card (nur zeigen wenn TV an ist)

```yaml
type: conditional
conditions:
  - entity: remote.samsung_tv_remote
    state: "on"
card:
  # Hier eine der Remote-Konfigurationen von oben einfügen
```

### Mit Custom Card (Universal Remote Card via HACS)

Falls du HACS installiert hast:

1. HACS öffnen
2. Frontend → Suche "Universal Remote Card"
3. Installieren

Dann kannst du verwenden:
```yaml
type: custom:universal-remote-card
remote_id: remote.samsung_tv_remote
rows:
  - - power
  - - back
    - home
    - menu
  - - touchpad
  - - volume_down
    - volume_mute
    - volume_up
```

---

## ❓ Fehlerbehebung

**Buttons werden nicht angezeigt:**
- Prüfe, ob die Integration korrekt geladen ist
- Stelle sicher, dass die Entity-Namen korrekt sind
- Neustart von Home Assistant kann helfen

**Buttons funktionieren nicht:**
- Teste erst die Buttons einzeln unter **Entwicklerwerkzeuge** → **Dienste**
- Prüfe die Home Assistant Logs auf Fehler
- Stelle sicher, dass dein TV eingeschaltet und im Netzwerk erreichbar ist
