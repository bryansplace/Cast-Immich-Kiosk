"""
Immich Kiosk Cast Controller — Flask version.
A simple mobile-friendly web interface for casting any URL (typically an
Immich Kiosk slideshow URL) to a Chromecast device via CATT.
"""

import os
import re
import subprocess
from """
Immich Kiosk Cast Controller — Flask version.
A simple mobile-friendly web interface for casting any URL (typically an
Immich Kiosk slideshow URL) to a Chromecast device via CATT.
"""

import os
import re
import signal
import subprocess
import sys
from flask import Flask, make_response, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

ENV_PATH = os.path.join(os.path.dirname(__file__), "data", ".env")

DEFAULTS = {
    "KIOSK_URL":   "http://192.168.1.223:3000",
    "CAST_DEVICE": "Salon",
}

COOKIE_LAST_URL = "last_cast_url"


# ── Signal handling ────────────────────────────────────────────────────────────

def handle_sigterm(*args):
    """Exit cleanly on SIGTERM so Docker does not resort to SIGKILL."""
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_sigterm)


# ── .env helpers ───────────────────────────────────────────────────────────────

def read_env() -> dict:
    """Read the .env file and return only recognised keys."""
    values = {}
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key = key.strip()
                if key in DEFAULTS:
                    values[key] = val.strip()
    return values


def write_env(values: dict) -> None:
    """Write recognised keys to the .env file."""
    os.makedirs(os.path.dirname(ENV_PATH), exist_ok=True)
    merged = read_env()
    merged.update({k: v for k, v in values.items() if k in DEFAULTS})
    with open(ENV_PATH, "w") as f:
        for key, val in merged.items():
            f.write(f"{key}={val}\n")


def get_config() -> dict:
    """Config precedence: built-in defaults < .env file < environment variables."""
    cfg = dict(DEFAULTS)
    cfg.update(read_env())
    for key in DEFAULTS:
        if key in os.environ:
            cfg[key] = os.environ[key]
    return cfg


# ── CATT helpers ───────────────────────────────────────────────────────────────

def catt_scan() -> tuple[list[str], str]:
    """Run `catt scan` and return (device_names, error_message)."""
    try:
        result = subprocess.run(
            ["catt", "scan"],
            capture_output=True, text=True, timeout=20,
        )
        if result.returncode != 0:
            return [], f"catt exited {result.returncode}: {result.stderr.strip() or result.stdout.strip()}"
        devices = []
        for line in result.stdout.splitlines():
            match = re.match(r"^\S+\s*-\s*(.+?)\s*-\s*.+$", line.strip())
            if match:
                devices.append(match.group(1).strip())
        if not devices:
            return [], f"No devices parsed. Raw output: {result.stdout!r}"
        return devices, ""
    except subprocess.TimeoutExpired:
        return [], "catt scan timed out after 20s"
    except FileNotFoundError:
        return [], "catt command not found in container"
    except Exception as e:
        return [], f"Unexpected error: {e!r}"


def catt_cast(device: str, url: str) -> str:
    try:
        result = subprocess.run(
            ["catt", "-d", device, "cast_site", url],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            return f"✅ Casting to {device}"
        return f"⚠ CATT error: {result.stderr.strip() or result.stdout.strip()}"
    except subprocess.TimeoutExpired:
        return "⚠ CATT command timed out."
    except FileNotFoundError:
        return "⚠ catt not found in container."
    except Exception as e:
        return f"⚠ Unexpected error: {e}"


def catt_stop(device: str) -> str:
    try:
        result = subprocess.run(
            ["catt", "-d", device, "stop"],
            capture_output=True, text=True, timeout=20,
        )
        if result.returncode == 0:
            return f"⏹ Stopped {device}"
        return f"⚠ CATT error: {result.stderr.strip() or result.stdout.strip()}"
    except Exception as e:
        return f"⚠ Unexpected error: {e}"


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    cfg = get_config()
    last_url = request.cookies.get(COOKIE_LAST_URL, "")
    return render_template("home.html", cfg=cfg, last_selection=last_url)


@app.route("/settings", methods=["GET", "POST"])
def settings():
    cfg = get_config()
    if request.method == "POST":
        kiosk_url   = request.form["kiosk_url"].strip()
        cast_device = request.form.get("cast_device", "").strip() or cfg["CAST_DEVICE"]
        write_env({
            "KIOSK_URL":   kiosk_url,
            "CAST_DEVICE": cast_device,
        })
        return redirect(url_for("home"))
    return render_template("settings.html", cfg=cfg)


@app.route("/api/device/scan", methods=["POST"])
def api_device_scan():
    devices, error = catt_scan()
    return jsonify({"devices": devices, "error": error})


@app.route("/api/cast", methods=["POST"])
def api_cast():
    cfg  = get_config()
    data = request.json or {}
    url  = (data.get("url") or "").strip()
    if not url:
        return jsonify({"message": "⚠ No URL provided."}), 400
    message = catt_cast(cfg["CAST_DEVICE"], url)
    resp = make_response(jsonify({"message": message}))
    resp.set_cookie(COOKIE_LAST_URL, url, max_age=60 * 60 * 24 * 365, samesite="Lax")
    return resp


@app.route("/api/stop", methods=["POST"])
def api_stop():
    cfg = get_config()
    return jsonify({"message": catt_stop(cfg["CAST_DEVICE"])})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=False) import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

ENV_PATH = os.path.join(os.path.dirname(__file__), "data", ".env")

DEFAULTS = {
    "KIOSK_URL":      "http://192.168.1.223:3000",
    "CAST_DEVICE":    "Salon",
    "LAST_SELECTION": "",
}


# ── .env helpers ───────────────────────────────────────────────────────────────

def read_env() -> dict:
    """Read the .env file into a dict, falling back to defaults for missing keys."""
    values = dict(DEFAULTS)
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                values[key.strip()] = val.strip()
    return values


def write_env(values: dict) -> None:
    """Merge the given values into the .env file and rewrite it."""
    os.makedirs(os.path.dirname(ENV_PATH), exist_ok=True)
    merged = read_env()
    merged.update(values)
    with open(ENV_PATH, "w") as f:
        for key, val in merged.items():
            f.write(f"{key}={val}\n")


def get_config() -> dict:
    """Config precedence: .env file > process environment > built-in defaults."""
    cfg = dict(DEFAULTS)
    for key in DEFAULTS:
        if key in os.environ:
            cfg[key] = os.environ[key]
    cfg.update(read_env())
    return cfg


# ── CATT helpers ───────────────────────────────────────────────────────────────

def catt_scan() -> tuple[list[str], str]:
    """Run `catt scan` and return (device_names, error_message)."""
    try:
        result = subprocess.run(
            ["catt", "scan"],
            capture_output=True, text=True, timeout=20,
        )
        if result.returncode != 0:
            return [], f"catt exited {result.returncode}: {result.stderr.strip() or result.stdout.strip()}"
        devices = []
        for line in result.stdout.splitlines():
            match = re.match(r"^\S+\s*-\s*(.+?)\s*-\s*.+$", line.strip())
            if match:
                devices.append(match.group(1).strip())
        if not devices:
            return [], f"No devices parsed. Raw output: {result.stdout!r}"
        return devices, ""
    except subprocess.TimeoutExpired:
        return [], "catt scan timed out after 20s"
    except FileNotFoundError:
        return [], "catt command not found in container"
    except Exception as e:
        return [], f"Unexpected error: {e!r}"


def catt_cast(device: str, url: str) -> str:
    try:
        result = subprocess.run(
            ["catt", "-d", device, "cast_site", url],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            return f"✅ Casting to {device}"
        return f"⚠ CATT error: {result.stderr.strip() or result.stdout.strip()}"
    except subprocess.TimeoutExpired:
        return "⚠ CATT command timed out."
    except FileNotFoundError:
        return "⚠ catt not found in container."
    except Exception as e:
        return f"⚠ Unexpected error: {e}"


def catt_stop(device: str) -> str:
    try:
        result = subprocess.run(
            ["catt", "-d", device, "stop"],
            capture_output=True, text=True, timeout=20,
        )
        if result.returncode == 0:
            return f"⏹ Stopped {device}"
        return f"⚠ CATT error: {result.stderr.strip() or result.stdout.strip()}"
    except Exception as e:
        return f"⚠ Unexpected error: {e}"


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    cfg = get_config()
    return render_template("home.html", cfg=cfg, last_selection=cfg["LAST_SELECTION"])


@app.route("/settings", methods=["GET", "POST"])
def settings():
    cfg = get_config()
    if request.method == "POST":
        kiosk_url   = request.form["kiosk_url"].strip()
        cast_device = request.form.get("cast_device", "").strip() or cfg["CAST_DEVICE"]
        write_env({
            "KIOSK_URL":   kiosk_url,
            "CAST_DEVICE": cast_device,
        })
        return redirect(url_for("home"))
    return render_template("settings.html", cfg=cfg)


@app.route("/api/device/scan", methods=["POST"])
def api_device_scan():
    devices, error = catt_scan()
    return jsonify({"devices": devices, "error": error})


@app.route("/api/cast", methods=["POST"])
def api_cast():
    cfg  = get_config()
    data = request.json or {}
    url  = (data.get("url") or "").strip()
    if not url:
        return jsonify({"message": "⚠ No URL provided."}), 400
    message = catt_cast(cfg["CAST_DEVICE"], url)
    write_env({"LAST_SELECTION": url})
    return jsonify({"message": message})


@app.route("/api/stop", methods=["POST"])
def api_stop():
    cfg = get_config()
    return jsonify({"message": catt_stop(cfg["CAST_DEVICE"])})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=False)
