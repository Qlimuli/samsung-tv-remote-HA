# Samsung TV Dashboard Remote Konfiguration

Dieses Dokument enthält verschiedene Dashboard-Layouts für deine Samsung TV Fernbedienung in Home Assistant.

## 🎮 Variante 1: Kompakte Fernbedienung (Empfohlen)

Diese Variante zeigt die wichtigsten Funktionen in einem kompakten Layout.

\`\`\`yaml
type: vertical-stack
cards:
  - type: custom:mushroom-template-card
    primary: TV {{PLACEHOLDER}}
    secondary: >-
      {{ states('media_player.tv_{{PLACEHOLDER}}') | title }} | Lautstärke:
      {{ states('sensor.tv_{{PLACEHOLDER}}_lautstarke') }}
    icon: mdi:television
    icon_color: |-
      {% if is_state('media_player.tv_{{PLACEHOLDER}}', 'on') %}
        blue
      {% else %}
        grey
      {% endif %}
    tap_action:
      action: toggle
    entity: switch.tv_{{PLACEHOLDER}}
    card_mod:
      style: |
        ha-card {
          background: linear-gradient(135deg, rgba(30,30,45,0.95), rgba(20,20,35,0.95));
          border-radius: 20px;
          border: 1px solid rgba(100,100,120,0.2);
        }
  - type: grid
    columns: 3
    square: false
    cards:
      - type: custom:mushroom-template-card
        icon: mdi:power
        icon_color: red
        tap_action:
          action: call-service
          service: switch.toggle
          target:
            entity_id: switch.tv_{{PLACEHOLDER}}
        card_mod:
          style: |
            ha-card {
              background: rgba(20,20,30,0.6);
              border-radius: 12px;
              height: 55px;
              border: 1px solid rgba(255,50,50,0.3);
            }
      - type: custom:mushroom-template-card
        icon: mdi:home
        icon_color: blue
        tap_action:
          action: call-service
          service: button.press
          target:
            entity_id: button.tv_{{PLACEHOLDER}}_home
        card_mod:
          style: |
            ha-card {
              background: rgba(20,20,30,0.6);
              border-radius: 12px;
              height: 55px;
              border: 1px solid rgba(50,100,255,0.3);
            }
      - type: custom:mushroom-template-card
        icon: mdi:menu
        icon_color: blue
        tap_action:
          action: call-service
          service: button.press
          target:
            entity_id: button.tv_{{PLACEHOLDER}}_menu
        card_mod:
          style: |
            ha-card {
              background: rgba(20,20,30,0.6);
              border-radius: 12px;
              height: 55px;
              border: 1px solid rgba(50,100,255,0.3);
            }
  - type: grid
    columns: 3
    square: false
    cards:
      - type: custom:mushroom-template-card
        icon: mdi:undo
        icon_color: orange
        tap_action:
          action: call-service
          service: button.press
          target:
            entity_id: button.tv_{{PLACEHOLDER}}_zuruck
        card_mod:
          style: |
            ha-card {
              background: rgba(20,20,30,0.6);
              border-radius: 12px;
              height: 55px;
              border: 1px solid rgba(255,150,50,0.3);
            }
      - type: custom:mushroom-template-card
        icon: mdi:chevron-up
        icon_color: cyan
        tap_action:
          action: call-service
          service: button.press
          target:
            entity_id: button.tv_{{PLACEHOLDER}}_hoch
        card_mod:
          style: |
            ha-card {
              background: linear-gradient(135deg, rgba(60,80,100,0.9), rgba(40,60,80,0.9));
              border-radius: 12px;
              height: 55px;
              border: 2px solid rgba(100,200,255,0.6);
              box-shadow: 0 0 15px rgba(100,200,255,0.3), inset 0 0 10px rgba(100,200,255,0.1);
            }
      - type: custom:mushroom-template-card
        icon: mdi:source-branch
        icon_color: purple
        tap_action:
          action: call-service
          service: button.press
          target:
            entity_id: button.tv_{{PLACEHOLDER}}_quelle
        card_mod:
          style: |
            ha-card {
              background: rgba(20,20,30,0.6);
              border-radius: 12px;
              height: 55px;
              border: 1px solid rgba(200,100,255,0.3);
            }
  - type: grid
    columns: 3
    square: false
    cards:
      - type: custom:mushroom-template-card
        icon: mdi:chevron-left
        icon_color: cyan
        tap_action:
          action: call-service
          service: button.press
          target:
            entity_id: button.tv_{{PLACEHOLDER}}_links
        card_mod:
          style: |
            ha-card {
              background: linear-gradient(135deg, rgba(60,80,100,0.9), rgba(40,60,80,0.9));
              border-radius: 12px;
              height: 55px;
              border: 2px solid rgba(100,200,255,0.6);
              box-shadow: 0 0 15px rgba(100,200,255,0.3), inset 0 0 10px rgba(100,200,255,0.1);
            }
      - type: custom:mushroom-template-card
        icon: mdi:checkbox-blank-circle
        icon_color: lime
        tap_action:
          action: call-service
          service: button.press
          target:
            entity_id: button.tv_{{PLACEHOLDER}}_bestatigen
        card_mod:
          style: |
            ha-card {
              background: linear-gradient(135deg, rgba(80,120,80,0.95), rgba(60,100,60,0.95));
              border-radius: 50%;
              height: 55px;
              border: 3px solid rgba(150,255,150,0.8);
              box-shadow: 0 0 20px rgba(150,255,150,0.5), inset 0 0 15px rgba(150,255,150,0.2);
            }
      - type: custom:mushroom-template-card
        icon: mdi:chevron-right
        icon_color: cyan
        tap_action:
          action: call-service
          service: button.press
          target:
            entity_id: button.tv_{{PLACEHOLDER}}_rechts
        card_mod:
          style: |
            ha-card {
              background: linear-gradient(135deg, rgba(60,80,100,0.9), rgba(40,60,80,0.9));
              border-radius: 12px;
              height: 55px;
              border: 2px solid rgba(100,200,255,0.6);
              box-shadow: 0 0 15px rgba(100,200,255,0.3), inset 0 0 10px rgba(100,200,255,0.1);
            }
  - type: grid
    columns: 3
    square: false
    cards:
      - type: custom:mushroom-template-card
        icon: mdi:volume-mute
        icon_color: grey
        tap_action:
          action: call-service
          service: button.press
          target:
            entity_id: button.tv_{{PLACEHOLDER}}_stumm
        card_mod:
          style: |
            ha-card {
              background: rgba(20,20,30,0.6);
              border-radius: 12px;
              height: 55px;
              border: 1px solid rgba(150,150,150,0.3);
            }
      - type: custom:mushroom-template-card
        icon: mdi:chevron-down
        icon_color: cyan
        tap_action:
          action: call-service
          service: button.press
          target:
            entity_id: button.tv_{{PLACEHOLDER}}_runter
        card_mod:
          style: |
            ha-card {
              background: linear-gradient(135deg, rgba(60,80,100,0.9), rgba(40,60,80,0.9));
              border-radius: 12px;
              height: 55px;
              border: 2px solid rgba(100,200,255,0.6);
              box-shadow: 0 0 15px rgba(100,200,255,0.3), inset 0 0 10px rgba(100,200,255,0.1);
            }
      - type: custom:mushroom-template-card
        icon: mdi:exit-to-app
        icon_color: red
        tap_action:
          action: call-service
          service: button.press
          target:
            entity_id: button.tv_{{PLACEHOLDER}}_beenden
        card_mod:
          style: |
            ha-card {
              background: rgba(20,20,30,0.6);
              border-radius: 12px;
              height: 55px;
              border: 1px solid rgba(255,50,50,0.3);
            }
  - type: grid
    columns: 4
    square: false
    cards:
      - type: custom:mushroom-template-card
        icon: mdi:play
        icon_color: green
        tap_action:
          action: call-service
          service: button.press
          target:
            entity_id: button.tv_{{PLACEHOLDER}}_abspielen
        card_mod:
          style: |
            ha-card {
              background: rgba(20,20,30,0.6);
              border-radius: 12px;
              height: 50px;
              border: 1px solid rgba(50,255,50,0.3);
            }
      - type: custom:mushroom-template-card
        icon: mdi:pause
        icon_color: yellow
        tap_action:
          action: call-service
          service: button.press
          target:
            entity_id: button.tv_{{PLACEHOLDER}}_pause
        card_mod:
          style: |
            ha-card {
              background: rgba(20,20,30,0.6);
              border-radius: 12px;
              height: 50px;
              border: 1px solid rgba(255,200,50,0.3);
            }
      - type: custom:mushroom-template-card
        icon: mdi:stop
        icon_color: red
        tap_action:
          action: call-service
          service: button.press
          target:
            entity_id: button.tv_{{PLACEHOLDER}}_stopp
        card_mod:
          style: |
            ha-card {
              background: rgba(20,20,30,0.6);
              border-radius: 12px;
              height: 50px;
              border: 1px solid rgba(255,50,50,0.3);
            }
      - type: custom:mushroom-template-card
        icon: mdi:record
        icon_color: red
        card_mod:
          style: |
            ha-card {
              background: rgba(20,20,30,0.6);
              border-radius: 12px;
              height: 50px;
              border: 1px solid rgba(255,50,50,0.3);
            }
  - type: grid
    columns: 2
    square: false
    cards:
      - type: custom:mushroom-template-card
        icon: mdi:rewind
        icon_color: blue
        tap_action:
          action: call-service
          service: button.press
          target:
            entity_id: button.tv_{{PLACEHOLDER}}_zuruckspulen
        card_mod:
          style: |
            ha-card {
              background: rgba(20,20,30,0.6);
              border-radius: 12px;
              height: 50px;
              border: 1px solid rgba(50,100,255,0.3);
            }
      - type: custom:mushroom-template-card
        icon: mdi:fast-forward
        icon_color: blue
        tap_action:
          action: call-service
          service: button.press
          target:
            entity_id: button.tv_{{PLACEHOLDER}}_vorspulen
        card_mod:
          style: |
            ha-card {
              background: rgba(20,20,30,0.6);
              border-radius: 12px;
              height: 50px;
              border: 1px solid rgba(50,100,255,0.3);
            }
card_mod:
  style: |
    ha-card {
      background: linear-gradient(180deg, rgba(15,15,25,0.98), rgba(25,25,35,0.98));
      border-radius: 20px;
      padding: 8px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    }
\`\`\`

---

## 📱 Installation

### Dashboard hinzufügen

1. Gehe zu **Einstellungen** → **Dashboards**
2. Öffne dein Dashboard oder erstelle ein neues
3. Klicke **Bearbeiten** (Stift-Symbol oben rechts)
4. Klicke **Karte hinzufügen** (+ Symbol unten rechts)
5. Scrolle runter zu **Manuell** und klicke darauf
6. Kopiere eine der YAML-Konfigurationen oben
7. Füge sie in den Editor ein
8. Klicke **Speichern**

---

## 🎯 Tipps

### Entity-Namen herausfinden

Gehe zu **Einstellungen** → **Geräte & Dienste** → **Integrationen** → **Samsung Remote**

Klicke auf dein TV-Gerät, dort siehst du alle verfügbaren Button-Entities.
