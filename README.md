# immich-kiosk-cast

A Flask-based, mobile-friendly web UI for casting [Immich Kiosk](https://github.com/damongolding/immich-kiosk) slideshows — or any URL — to a Chromecast device using [CATT](https://github.com/skorokithakis/catt).

## Prerequisites

- A running [Immich](https://immich.app/) instance
- A running [Immich Kiosk](https://github.com/damongolding/immich-kiosk) instance, with `enable_url_builder: true` set in its configuration
- A Chromecast-compatible device on the same LAN
- Docker and Docker Compose

This project does not manage or deploy Immich or Immich Kiosk. Both must be running independently before setup.

## How it works

The app provides a single home screen:

- **Start** — casts the URL currently in the textbox to the configured Chromecast device and saves it for next time.
- **Stop** — stops whatever is currently casting.
- **Build new URL** — opens the Kiosk URL builder (`/url-builder`) in a new tab. Select people, albums, dates, transitions, and other options visually; copy the resulting URL. When the app tab is refocused, the URL is pasted into the textbox automatically.
- **Settings** — configure the Kiosk URL and cast device.

Any valid URL can be cast, not only Kiosk URLs.

See [`docs/Setup_guide.md`](docs/Setup_guide.md) for background on CATT, the Kiosk URL builder, and Kiosk's `filter_date` vs `dates` parameter distinction.

## Setup

1. Create the data directory and copy the example config:
   ```
   mkdir -p flaskapp/data
   cp .env.example flaskapp/data/.env
   ```

2. Edit `flaskapp/data/.env` and set `KIOSK_URL` and `CAST_DEVICE`.

3. Start the container:
   ```
   docker compose up -d --build
   ```

4. Open the UI at `http://<host>:7860`.

> **Note:** The container runs with `network_mode: host` so CATT can discover Chromecast devices on the LAN. The app is reachable directly on port `7860` of the host.

## Enabling the Kiosk URL builder

The Kiosk URL builder must be explicitly enabled in the Kiosk instance's own configuration. Add the following to the Kiosk `config.yaml`:

```yaml
kiosk:
  enable_url_builder: true
```

Or set the environment variable in the Kiosk container:

```
KIOSK_ENABLE_URL_BUILDER=true
```

Once enabled, the URL builder is available at `http://<kiosk-host>:3000/url-builder`.

## Project structure

```
immich-kiosk-cast/
├── docker-compose.yaml
├── .env.example
├── .gitignore
├── README.md
├── docs/
│   └── Setup_guide.md
└── flaskapp/
    ├── Dockerfile
    ├── app.py
    ├── templates/
    │   ├── base.html
    │   ├── home.html
    │   └── settings.html
    └── data/                 (tracked empty via .gitkeep; .env is gitignored)
        └── .gitkeep
```
