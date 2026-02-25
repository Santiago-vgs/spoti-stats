#!/usr/bin/env python3
"""Interactive setup script for Spoti Stats backend."""

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BACKEND_DIR / ".env"


def main():
    print("=== Spoti Stats Setup ===\n")

    if ENV_FILE.exists():
        overwrite = input(f"{ENV_FILE} already exists. Overwrite? [y/N] ").strip().lower()
        if overwrite != "y":
            print("Setup cancelled.")
            sys.exit(0)

    client_id = input("Spotify Client ID: ").strip()
    if not client_id:
        print("Error: Client ID cannot be empty.")
        sys.exit(1)

    client_secret = input("Spotify Client Secret: ").strip()
    if not client_secret:
        print("Error: Client Secret cannot be empty.")
        sys.exit(1)

    env_content = (
        f"SPOTIPY_CLIENT_ID={client_id}\n"
        f"SPOTIPY_CLIENT_SECRET={client_secret}\n"
        f"SPOTIPY_REDIRECT_URI=http://127.0.0.1:8000/callback\n"
        f"DATABASE_URL=sqlite:///data/spoti_stats.db\n"
    )

    ENV_FILE.write_text(env_content)
    print(f"\nWrote {ENV_FILE}")
    print("\n--- IMPORTANT ---")
    print("Add this Redirect URI in your Spotify Developer App settings:")
    print("  http://127.0.0.1:8000/callback")
    print("\nSetup complete! Start the API server with: python scripts/run_api.py")


if __name__ == "__main__":
    main()
