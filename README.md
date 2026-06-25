# immich-kiosk-cast

A lightweight web app that lets you cast [Immich Kiosk](https://github.com/damongolding/immich-kiosk) slideshows — or in fact any URL — to a Chromecast device on your LAN, without needing HTTPS or a public DNS record.

## Background

[Immich](https://immich.app/) is a self-hosted photo and video library. Its built-in Chromecast support requires a publicly accessible HTTPS instance with a DNS record, which is overkill for home use.

This project uses [CATT (Cast All The Things)](https://github.com/skorokithakis/catt) to cast over the local LAN directly. Point your phone's browser at the web interface address, build and paste your Kiosk URL for what to display, and cast.

## How it works

The app provides a home screen:

- **Start** — casts the URL in the textbox to the configured Chromecast device and saves it for next time.
- **Stop** — stops whatever is currently casting.
- **Settings** — configure the Kiosk URL and cast device name. Settings are saved to `config.env` on the host and persist across restarts and updates.
- **URL to cast**
Paste the URL to be cast into the textbox. Pasting http://<IMMICH KIOSK>:3000 would cast the default Immich Kiosk display. To be more selective, use the button below 
- **Build new URL** — opens the Kiosk URL builder in a new tab. Select people, albums, transitions, and other options. At the bottom of the selection list, Kiosk builds a URL.  Copy it, go back to Home screen, and paste. 

Note: Any valid URL can be cast, not just Kiosk URLs — YouTube, for example, should work too.  



## Prerequisites

- A running [Immich Kiosk](https://github.com/damongolding/immich-kiosk) instance, with `enable_url_builder: true` in its config.
- A Chromecast-compatible device on the same LAN
- Docker and Docker Compose

This project does not deploy or manage Immich or Immich Kiosk. Both must be running before you set this up.

---

## Setting up Immich Kiosk (if not already running)

If you don't have Immich Kiosk, the full installation instructions are at [docs.immichkiosk.app](https://docs.immichkiosk.app/installation/). 

It is a powerful program with many options. Below, I give a quick installation guide to get up and running using a standalone docker compose file.

You will need an [Immich API key](https://api.immich.app/getting-started) for Kiosk to access Immich. You can allow all permissions or include only [those required](https://docs.immichkiosk.app/installation/#api-key-permissions)

Make project folder to hold `docker-compose.yaml` and `config.yaml`

```
mkdir ./immich-kiosk
cd ./immich-kiosk
mkdir ./config
```

Create `docker-compose.yaml`:
```
services:
  immich-kiosk:
    image: ghcr.io/damongolding/immich-kiosk:latest
    container_name: immich-kiosk
    tty: true
    environment:
      TZ: "Europe/Paris"
    ports:
      - 3000:3000
    volumes:
      - ./config:/config
    restart: always
    healthcheck:
      test: ["CMD", "/kiosk", "--healthcheck"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
```


Create `./config/config.yaml`


The following is a suggestion to copy and paste to get started. 
The only required items are:
immich_api_key: "????"
immich_url: ""http://192.168.X.XXX:2283"
enable_url_builder: true

Later, you can customise further ( Clock, texts, etc. ) using Immich Kiosk documentation.

 
```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/damongolding/immich-kiosk/main/config.schema.json

## Required
immich_api_key: ""
immich_url: ""

## Kiosk behaviour
duration: 60
disable_screensaver: true
optimize_images: true
use_gpu: false

## Asset sources
show_archived: false

## UI
disable_ui: true
background_blur: false
layout: splitview

## Transitions
transition: cross-fade
cross_fade_transition_duration: 1

## Image display
image_fit: none
image_effect: none
use_original_image: false

## Video
show_videos: false
live_photos: false
live_photo_loop_delay: 0
show_animated_gifs: false

## Fixed options (cannot be changed via URL params)
kiosk:
  port: 3000
  behind_proxy: false
  disable_url_queries: false
  disable_config_endpoint: false
  enable_url_builder: true   # IMPORTANT — required by immich-kiosk-cast
  watch_config: false
  fetched_assets_size: 1000
  http_timeout: 20
  password: ""
  cache: true
  prefetch: true
  asset_weighting: true
```

Run `docker-compose up -d` and point browser to `<KIOSK HOST>:3000 to check it is working

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

> **Note:** The container has to run with `network_mode: host` so CATT can discover Chromecast devices on the LAN.

### 2. Create an empty config file

```sh
touch config.env
```

The app will write to this file as you configure it via the Settings page. No pre-configuration is needed.

### 3. Start the container

```sh
docker compose up -d
```

### 4. Open the UI

```
http://<host-ip>:7860
```

Go to **Settings** and enter your Kiosk URL and Chromecast device name. To find your device name, tap 'Scan for devices'

Go back to home screen and tap **Start**, the default Kiosk display (probably everything) should be cast to the device.

To create a URL which displays what you want, tap 'Build new URL'.
This takes you to the Immich Kiosk URL builder where you are given lots of choices ( eg Album) to create a URL that Kiosk uses to create the display.


Have fun.....


## Compatibility

This project was developed and tested against:

| Component | Version |
|---|---|
| Immich | v2.7.3 |
| Immich Kiosk | v0.38.1 |
| CATT | 0.13.1 |
| Flask | 3.1.3 |

Both Immich and Immich Kiosk are under active development. If a future release breaks something, check their respective changelogs for API or configuration changes.



