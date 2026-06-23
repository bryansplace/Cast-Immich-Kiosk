# Setup Guide

## Overview

This guide covers the components that make up immich-kiosk-cast, how they fit together, and reference material for building Kiosk URLs.

---

## Components

### Immich

[Immich](https://immich.app/) is a self-hosted photo and video library. It provides the underlying asset storage and the API that Kiosk queries to fetch images for display.

### Immich Kiosk

[Immich Kiosk](https://github.com/damongolding/immich-kiosk) is a lightweight slideshow service that connects to Immich and renders a continuously cycling display of photos in a browser. Its behaviour — which photos to show, transition style, display duration, image fit, and many other options — is controlled entirely through URL query parameters. No runtime changes to its configuration file are needed; a different URL produces a different slideshow.

Kiosk includes a built-in **URL builder** at `/url-builder`. This must be explicitly enabled in its configuration before use:

```yaml
kiosk:
  enable_url_builder: true
```

or via environment variable:

```
KIOSK_ENABLE_URL_BUILDER=true
```

The URL builder provides a web form for selecting people, albums, date ranges, transitions, image fit, and other parameters, and generates the corresponding Kiosk URL. That URL can be copied and pasted into the immich-kiosk-cast home screen for casting.

### CATT (Cast All The Things)

[CATT](https://github.com/skorokithakis/catt) is a command-line tool that instructs a Chromecast-compatible device to open and render a given URL. The command used by this app is:

```
catt -d "Device Name" cast_site "http://..."
```

Where `Device Name` is the device's display name as it appears on the local network, and the URL is the address to cast.

CATT is installed inside the Flask controller container via `pip install catt`. No separate CATT container or host installation is required.

To discover device names on the LAN, run:

```
catt scan
```

This is also accessible from within the app via the **Scan for devices** button on the Settings screen.

#### Why `network_mode: host`

Chromecast device discovery uses mDNS (multicast DNS), which does not cross Docker's default bridge network. The Flask controller container therefore runs with `network_mode: host`, giving CATT direct access to the LAN. With host networking, the app is reachable on port `7860` of the host directly; the `ports:` mapping in the compose file has no effect in this mode.

---

## Building Kiosk URLs

The recommended workflow is:

1. Press **Build new URL** in the app — this opens `/url-builder` on the Kiosk instance in a new browser tab.
2. Configure the slideshow using the URL builder's form controls (people, albums, dates, transitions, etc.).
3. Copy the generated URL from the URL builder.
4. Switch back to the app tab — the URL is pasted into the textbox automatically.
5. Press **Start** to cast.

The URL is saved when Start is pressed, so it will be pre-filled on the next visit.

---

## Kiosk URL parameter reference

Kiosk's full parameter list is documented in the [official Kiosk documentation](https://docs.immichkiosk.app/configuration/url-params/). The URL builder covers most parameters interactively. The following notes cover two parameters that are easily confused when building URLs by hand.

### `filter_date` vs `dates`

These two parameters look similar but serve fundamentally different roles.

**`dates`** is an *asset source*. It defines an independent pool of assets drawn from a specified date range, in the same way that `person` or `album` each define their own pool. Including `dates` adds those assets to the slideshow.

**`filter_date`** is a *restrictor*. It narrows an already-selected pool of assets — from `person`, `album`, `dates`, or the whole library — down to those falling within the given range. It does not add assets; it removes them from whatever has already been selected.

#### Practical consequences

Combining `person=X` with `dates=2023-01-01_to_2023-12-31` produces a **union**: all photos of person X (from any year), plus all photos from 2023 (of any person). The result is likely not what most users intend.

To show only photos of person X *taken* in 2023, use `filter_date` instead:

```
?person=PERSON_ID&filter_date=2023-01-01_to_2023-12-31
```

This selects all photos of person X, then restricts that set to those within the date range.

#### Accepted values

| Parameter | Format | Example |
|---|---|---|
| `filter_date` | Explicit range | `2023-01-01_to_2023-12-31` |
| `filter_date` | Relative keyword | `last-7-days`, `last-30-days`, `last-year`, `today` |
| `dates` | Explicit range only | `2023-01-01_to_2023-12-31` |

---

## Known display limitations (Google Nest Hub Max)

These are hardware constraints, not software issues, and are documented here to avoid repeated investigation.

**Dimness.** The Nest Hub Max panel has a maximum brightness of approximately 300 nits. This cannot be increased via software or Kiosk configuration.

**Upscaling.** CATT renders the cast content at 1280×720. The Nest Hub Max's native panel resolution is 1280×800. The 80-pixel vertical difference results in mild upscaling. Setting `image_fit: none` in the Kiosk configuration avoids additional distortion caused by Kiosk's own image scaling on top of the device upscale.
