# Home Assistant: basics

Home Assistant (HA) is not running yet. This page records what to buy and where the official steps are. Follow the official pages; they change.

## Hardware

- HA OS 17.0 dropped 32-bit armv7 targets. A **Raspberry Pi 2 is out**, with no 64-bit option. Pi 3 owners must use the 64-bit image. ([17.0 release notes](https://github.com/home-assistant/operating-system/releases/tag/17.0), [deprecation blog post](https://home-assistant.io/blog/2025/05/22/deprecating-core-and-supervised-installation-methods-and-32-bit-systems/))
- A **Pi 3** runs only the 64-bit image, and with 1 GB RAM it is tight. The official Raspberry Pi page asks for a Pi 4 or 5 with at least 2 GB.
- **Recommended:** a Raspberry Pi 4 or 5, or a small x86-64 box (a used mini PC), or Home Assistant Green.
- **Why not a VM on Windows:** HA wants direct control of the zigbee and z-wave USB sticks. Passing a USB device through to a VM is fragile (resets, re-enumeration), and the host must stay on. A dedicated box avoids this.

## Install

HA OS is the recommended type for your own hardware.

- Overview: https://www.home-assistant.io/installation/
- Raspberry Pi: https://www.home-assistant.io/installation/raspberrypi
- Generic x86-64: https://www.home-assistant.io/installation/generic-x86-64
- VMs (not for zigbee/z-wave sticks): https://www.home-assistant.io/installation/windows

## Adopt the ESPHome desk sensor

No reflash is needed; the device already runs the native API with encryption.

1. In HA, install the ESPHome Device Builder add-on if you want to manage devices there (optional; the files in this repo still build with the CLI).
2. Open Settings > Devices & services. HA discovers `desk-presence` automatically; click Add on the discovered card. If it does not appear, add the ESPHome integration by hand and enter host `desk-presence.local`.
3. When asked for the encryption key, paste `api_encryption_key` from the decrypted `esphome/secrets.yaml` (`sops -d esphome/secrets.sops.yaml`).
4. The entities (Presence, distances, thresholds, gates) appear under the device.
