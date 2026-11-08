# Desk presence: bring-up

An ESP32 and an HLK-LD2410C mmWave radar under the desk report whether someone is in the chair. Config: `esphome/desk-presence.yaml`. The device works alone (ESPHome native API plus a web page) and Home Assistant can adopt it later without a reflash.

## Parts (prices are guesses)

| Part | Guess |
|---|---|
| ESP32 dev board (ESP32-WROOM, 30 or 38 pin) | $8 |
| HLK-LD2410C module | $5 |
| LD2410 breakout board, or a 1.27 mm to 2.54 mm cable | $3 |
| Dupont jumper wires, micro-USB or USB-C cable, 5 V supply | $5 |
| Mounting tape or a small box | $2 |

The LD2410C's header is 1.27 mm pitch, not the 2.54 mm of a breadboard. Buy the breakout or a 1.27 to 2.54 mm cable, or you cannot plug it into jumper wires.

## Wiring

| LD2410C | ESP32 |
|---|---|
| 5V | 5V (VIN) |
| GND | GND |
| TX | GPIO16 (UART2 RX) |
| RX | GPIO17 (UART2 TX) |

TX and RX cross. The module takes 5 V power and its serial lines are 3.3 V. Mount it under the desk aimed at the seat, about 1 m away, with nothing moving in its view (a fan, a curtain).

## Secrets and flashing

Secrets live encrypted in `esphome/secrets.sops.yaml` (placeholders for wifi and OTA; a real random API key). Edit with `sops esphome/secrets.sops.yaml` (needs your age key where sops finds it) and fill in the real wifi values.

```bash
sops -d esphome/secrets.sops.yaml > esphome/secrets.yaml   # gitignored
pipx install esphome
esphome run esphome/desk-presence.yaml     # first flash over USB
rm esphome/secrets.yaml                    # when done
```

Later flashes go over the air. Quick look: http://desk-presence.local/ (it is plain HTTP on the LAN with no login).

## Tuning (no reflash)

Every setting is an entity on the web page, and later in Home Assistant.

1. Set **Distance Resolution** to `0.2m`. Gates are then 0.2 m wide (gate 5 ends at 1.2 m); at the default 0.75 m, gates are too coarse for a 1 m range.
2. Set **Max Move Distance Gate** and **Max Still Distance Gate** to `5` (the minimum allowed is 2). Anything beyond the seat is ignored.
3. Watch **Moving Energy**, **Still Energy** and **Detection Distance** while seated, then while away. Switch on **Engineering Mode** for per-gate energies.
4. Set each gate's **Move Threshold** and **Still Threshold** (0 to 100) just under the seated energy and above the empty-chair noise. Raise thresholds to cut false presence; lower them if a still sitter drops out.
5. **Timeout** is how many seconds presence stays on after the radar loses the target. Keep it short (the default is 5 s), since the stay-on time you measure below includes it.

The HLKRadarTool phone app (iOS and Android) can tune the same parameters over Bluetooth and shows live gate energies. The app and ESPHome write the same settings, so change one at a time. Bluetooth on the module is on by default.

## Test protocol

Write down the numbers.

1. **Sit still, 10 min.** Read, type little, do not move. Presence must stay on the whole time. Any drop means the still thresholds are too high or the range too short.
2. **Leave and time it.** Stand up and walk out of view; start a stopwatch. Record seconds until **Presence** goes off. Repeat 5 times.
3. **Stand next to the desk, not sitting,** for 2 min. Presence should stay off. If it goes on, lower the max gate or raise thresholds.

The measured "stays present after leaving" time decides whether a seat pressure sensor is added. If presence lingers too long after leaving (and tuning cannot fix it), the sitting-end time will be wrong by that much, and a pressure sensor is the fix. If it clears within a few seconds, skip the extra hardware.
