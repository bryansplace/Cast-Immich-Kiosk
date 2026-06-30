# immich-kiosk-cast

Use your phone browser to locally cast [Immich Kiosk](https://github.com/damongolding/immich-kiosk) Immich Kiosk — or in fact any URL — to a Chromecast device on your LAN, without needing HTTPS or a public DNS record.

## Background

[Immich](https://immich.app/) is a self-hosted photo and video library. Its built-in Chromecast support requires a publicly accessible HTTPS instance with a DNS record, which is overkill for home use.

This project uses [CATT (Cast All The Things)](https://github.com/skorokithakis/catt) to cast over the local LAN directly. Point your phone's browser at the web interface address, build and paste your Kiosk URL for what to display, and cast.

## How it works

The app provides a home screen:

- **Start** — casts the URL in the textbox to the configured Chromecast device. The URL is saved in a browser cookie and pre-filled next time.
- **Stop** — stops whatever is currently casting.
- **Settings** — configure the Kiosk base URL and cast device name. Settings are saved to `config.env` on the host and persist across restarts and updates.
- **URL to cast** — paste the URL to be cast into the textbox. Pasting `http://<host>:3000` casts the default Immich Kiosk display. To be more selective, use the button below.
- **Build new URL** — opens the Kiosk URL builder in a new tab. Select people, albums, transitions, and other options. At the bottom of the selection list, Kiosk builds a URL. Copy it, go back to the Home screen, and paste.

Note: Any valid URL can be cast, not just Kiosk URLs — YouTube, for example, should work too.

## Prerequisites

- A running [Immich Kiosk](https://github.com/damongolding/immich-kiosk) instance, with `enable_url_builder: true` in its config.
- A Chromecast-compatible device on the same LAN.
- Docker and Docker Compose.

---

## Setting up Immich Kiosk (if not already installed)

If you have Immich Kiosk, skip this section.

Kiosk is a powerful program with many installation options. Below is a  installation guide to quickly get up and running using a standalone Docker-Compose file.

The full installation instructions are at [docs.immichkiosk.app](https://docs.immichkiosk.app/installation/) which can be used to customise the display (eg, display clock, dates etc.)

An [Immich API key](https://immich.app/docs/features/api-keys) is needed for Kiosk to access Immich. You can allow all permissions or include only [those required](https://docs.immichkiosk.app/installation/#api-key-permissions).

Make a project folder to hold `docker-compose.yaml`:

```
mkdir ./immich-kiosk
cd ./immich-kiosk
```

Create `docker-compose.yaml`:

```yaml
services:
  immich-kiosk:
    image: ghcr.io/damongolding/immich-kiosk:latest
    container_name: immich-kiosk
    environment:
      KIOSK_IMMICH_API_KEY: "xxxxxxxxxxxxxxxxxxxxxxx"
      KIOSK_IMMICH_URL: "http://192.168.1.XXX:2283"
      KIOSK_ENABLE_URL_BUILDER: true
    ports:
      - 3000:3000
    restart: always
    healthcheck:
      test: ["CMD", "/kiosk", "--healthcheck"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
```

Run `docker compose up -d` and point your browser to `http://<host-ip>:3000` to confirm it is working.

---

## Setting up immich-kiosk-cast

### 1. Create the compose file

Create a directory and save the following as `docker-compose.yaml`:

```yaml
services:
  immich-kiosk-cast:
    image: ghcr.io/bryansplace/immich-kiosk-cast:latest
    container_name: immich-kiosk-cast
    network_mode: host
    volumes:
      - ./config.env:/app/data/.env
    restart: unless-stopped
```

> **Note:** The container must run with `network_mode: host` so CATT can discover Chromecast devices on the LAN.

### 2. Create an empty config file

```
touch config.env
```

The app writes `KIOSK_URL` and `CAST_DEVICE` to this file as you configure them via the Settings page. No pre-configuration is needed.

### 3. Start the container

```
docker compose up -d
```

### 4. Open the UI

```
http://<host-ip>:7860
```

Go to **Settings** and enter your Kiosk base URL and Chromecast device name. Tap **Scan for devices** if you are unsure of the device name.

Go back to the home screen and tap **Start** — the default Kiosk display will be cast to the device.

To cast a specific album or set of people, tap **Build new URL**. This opens the Immich Kiosk URL builder where you can select albums, people, transitions, and other options to construct a URL. Copy it, return to the Home screen, paste it into the URL field, and tap **Start**.

## Compatibility

This project was developed and tested against:

| Component    | Version |
| ------------ | ------- |
| Immich       | v2.7.3  |
| Immich Kiosk | v0.38.1 |
| CATT         | 0.13.1  |
| Flask        | 3.1.3   |

Both Immich and Immich Kiosk are under active development. If a future release breaks something, check their respective changelogs for API or configuration changes.
