"""Download an Ollama model directly over IPv4 and install it into local Ollama storage."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import httpx

REGISTRY_BASE = "https://registry.ollama.ai/v2/library"


def pull_model(model_name: str = "smollm2:135m") -> None:
    if ":" in model_name:
        repo, tag = model_name.split(":", 1)
    else:
        repo, tag = model_name, "latest"

    models_dir = Path.home() / ".ollama" / "models"
    blobs_dir = models_dir / "blobs"
    manifests_dir = models_dir / "manifests" / "registry.ollama.ai" / "library" / repo
    blobs_dir.mkdir(parents=True, exist_ok=True)
    manifests_dir.mkdir(parents=True, exist_ok=True)

    transport = httpx.HTTPTransport(local_address="0.0.0.0")
    client = httpx.Client(transport=transport, follow_redirects=True, timeout=60.0)

    print(f"Fetching manifest for {repo}:{tag}...")
    manifest_url = f"{REGISTRY_BASE}/{repo}/manifests/{tag}"
    headers = {"Accept": "application/vnd.docker.distribution.manifest.v2+json"}
    resp = client.get(manifest_url, headers=headers)
    if resp.status_code != 200:
        print(f"Error fetching manifest: HTTP {resp.status_code}\n{resp.text}")
        sys.exit(1)

    manifest = resp.json()
    manifest_file = manifests_dir / tag
    manifest_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # Collect all blobs to download (config + layers)
    blobs_to_fetch = []
    if "config" in manifest:
        blobs_to_fetch.append(manifest["config"])
    for layer in manifest.get("layers", []):
        blobs_to_fetch.append(layer)

    total_size = sum(b.get("size", 0) for b in blobs_to_fetch)
    print(f"Total model download size: {total_size / (1024 * 1024):.1f} MB across {len(blobs_to_fetch)} layers")

    for idx, b in enumerate(blobs_to_fetch, start=1):
        digest = b["digest"]  # format: sha256:xxxx
        size = b.get("size", 0)
        blob_filename = digest.replace(":", "-")
        target_path = blobs_dir / blob_filename

        if target_path.exists() and target_path.stat().st_size == size:
            print(f"[{idx}/{len(blobs_to_fetch)}] Layer {digest[:19]}... already exists ({size / (1024 * 1024):.1f} MB)")
            continue

        print(f"[{idx}/{len(blobs_to_fetch)}] Downloading {digest[:19]}... ({size / (1024 * 1024):.2f} MB)")
        blob_url = f"{REGISTRY_BASE}/{repo}/blobs/{digest}"

        temp_path = blobs_dir / f"{blob_filename}.tmp"
        hasher = hashlib.sha256()
        downloaded = 0

        with client.stream("GET", blob_url) as stream:
            if stream.status_code != 200:
                print(f"Error downloading blob {digest}: HTTP {stream.status_code}")
                sys.exit(1)
            with temp_path.open("wb") as out_f:
                for chunk in stream.iter_bytes(chunk_size=1024 * 512):
                    out_f.write(chunk)
                    hasher.update(chunk)
                    downloaded += len(chunk)
                    pct = (downloaded / size * 100) if size > 0 else 100
                    print(f"\r  Downloaded {downloaded / (1024 * 1024):.1f} / {size / (1024 * 1024):.1f} MB ({pct:.1f}%)", end="", flush=True)

        print()
        calc_digest = f"sha256:{hasher.hexdigest()}"
        if calc_digest != digest:
            temp_path.unlink(missing_ok=True)
            print(f"Digest mismatch! Expected {digest}, got {calc_digest}")
            sys.exit(1)

        temp_path.rename(target_path)

    print(f"\nSuccessfully downloaded and registered {model_name} in Ollama storage!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", nargs="?", default="smollm2:135m", help="Model name (e.g. smollm2:135m or qwen2.5:0.5b)")
    args = parser.parse_args()
    pull_model(args.model)
