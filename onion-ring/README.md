# Onion Ring Nest

Research branch based on [Cody Kociemba's NoLongerEvil](https://github.com/codykociemba/NoLongerEvil-Thermostat), preserving upstream history and attribution. This is a firmware-patch/installer fork, **not** a replacement implementation of Google's proprietary thermostat application.

## What differs

- Installer identity: Onion Ring Nest, version `1.0.1-onion-ring.1`.
- Self-hosting is selected by default; the existing upstream hosted choice remains explicit.
- Installer no longer has an automatic upstream GitHub publishing destination.
- `profile.json` records the upstream commit, research status and SHA-256 of every bundled image.
- `build-plan.py` requires an explicit RFC1918 IPv4 endpoint and generation, omits root access/backplate simulation, and emits a build command without executing anything.

The **bundled device images are still unmodified upstream images**. Installer branding/defaults do not make those images an Onion Ring kernel. They retain upstream boot/provisioning behavior, including the initial hosted endpoint. Do not flash these expecting a cloud-free first boot. A local-endpoint kernel must be built and verified separately first.

```sh
python3 onion-ring/build-plan.py --api-url http://192.168.1.50:8000 --generation gen2
```

No host addresses, device identities, Wi-Fi secrets, credentials or private home settings belong in this repository. Build in a disposable checkout/copy: upstream `build.sh` removes bundled images when rebuilding. Outputs and build logs stay outside this checkout.

## Source boundaries and licensing

The installer `package.json` declares MIT. Its `omapLoaderUsb.ts` explicitly identifies GPLv2-derived code; that exception must be preserved. The repository has **no top-level license covering the new firmware builder/device-side scripts**, and bundled binary/source obligations have not been fully established. Do not apply a blanket MIT license to this tree or publish modified device images until that scope is clarified. GitHub permits viewing/forking public repositories; that is not a blanket modification/distribution grant. See [GitHub's licensing guidance](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository).

The separately [forked server](https://github.com/rheaney/onion-ring-nest-server) has a full MIT license. New original `onion-ring/` files alone use `onion-ring/LICENSE`; it does not relicense any upstream component.

## Architecture and qualification

Keep this fork narrow: device endpoint/provisioning/identity at the firmware boundary; Nest cloud-protocol compatibility in the local server; automation policy in an existing single-writer HVAC controller, not the server or an LLM. MQTT must not introduce a second thermostat writer. Application controls should use generic device status/command capabilities, not a thermostat-specific mini-app.

Original physical controls, schedules and safety behavior are expected to remain because the original thermostat application is retained, but source here cannot prove those proprietary behaviors. Qualify a spare device's ring, schedule, safety limits, power/battery behavior, server-down/Wi-Fi-down operation, reconnection and recovery before any installed-HVAC use. Confirm its exact display model first. No device is enrolled or flashed by this branch.

Customization seams include endpoint and CA/provisioning in `firmware/builder/build.sh`; boot logo in `firmware/builder/deps/logo_nest_clut224.ppm`; on-device configuration and API updater in `firmware/builder/deps/`; installer in `firmware/installer/`. Rich thermostat UI/HVAC algorithms are **not** present as modifiable source.

Before release, review fixed SSH credentials, credential-bearing settings logs, serial-based key retrieval, whole CA-bundle replacement, and the destructive MD5-only CGI updater. Do not deploy their defaults as a trusted local management/update plane.

## Updates

Keep `upstream` pointing at Cody's repository and `origin` at the Onion Ring fork. Preserve `main` as the upstream baseline and put our delta on `onion-ring`. For each upstream update: fetch, inspect the diff, merge the chosen commit into the development branch, update the provenance manifest and re-run installer/kernel/bench qualification. No automatic `latest` device updates and no new binary releases at this research stage.

## Initial build qualification — 2026-10-12

Installer TypeScript/Vite production build passes. Upstream Docker builder also compiled a local-endpoint ARM Linux 2.6.37 kernel successfully. U-Boot image header/payload CRCs, exact length and the local test endpoint inside the decompressed kernel were independently verified. Optional root access was not requested. This is source/build qualification, not a flashed or bench-qualified thermostat. No modified firmware binary is published, and bundled installer images remain unchanged upstream prebuilts.

Direct on-device MQTT is an assessed alternative, not implemented: retain the original thermostat application, translate its protocol locally and use MQTT off-device. Wi-Fi sleep/wake and battery behavior remain the main feasibility gate. Do not replace the local HVAC safety loop with broker-dependent logic.
