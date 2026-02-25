"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";
import { useSWRConfig } from "swr";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

const links = [
  { href: "/", label: "Dashboard" },
  { href: "/history", label: "History" },
  { href: "/top", label: "Top" },
  { href: "/playlists", label: "Playlists" },
  { href: "/decades", label: "Decades" },
];

export default function Navbar() {
  const pathname = usePathname();
  const [syncing, setSyncing] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const { mutate } = useSWRConfig();

  async function handleSync() {
    setSyncing(true);
    try {
      const res = await fetch(`${API_BASE}/pipeline/run?playlists=true`, { method: "POST" });
      if (!res.ok) {
        const data = await res.json();
        toast.error(`Sync failed: ${data.detail || res.statusText}`);
        setSyncing(false);
        return;
      }
      toast.info("Syncing your Spotify data...");
      // Poll pipeline status
      const poll = setInterval(async () => {
        try {
          const statusRes = await fetch(`${API_BASE}/pipeline/status`);
          const status = await statusRes.json();
          if (!status.running) {
            clearInterval(poll);
            setSyncing(false);
            if (status.error) {
              toast.error(`Sync error: ${status.error}`);
            } else {
              toast.success("Sync complete!");
              // Revalidate all SWR caches
              mutate(() => true, undefined, { revalidate: true });
            }
          }
        } catch {
          clearInterval(poll);
          setSyncing(false);
        }
      }, 2000);
    } catch (err) {
      toast.error(`Sync failed: ${err}`);
      setSyncing(false);
    }
  }

  return (
    <nav className="bg-zinc-900 border-b border-zinc-800" role="navigation" aria-label="Main navigation">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link href="/" className="text-xl font-bold text-green-500">
            Spoti Stats
          </Link>

          {/* Mobile hamburger */}
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="sm:hidden p-2 rounded-md text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors"
            aria-label="Toggle menu"
            aria-expanded={menuOpen}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {menuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>

          {/* Desktop nav */}
          <div className="hidden sm:flex items-center space-x-2">
            {links.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                aria-current={pathname === link.href ? "page" : undefined}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  pathname === link.href
                    ? "bg-zinc-800 text-white"
                    : "text-zinc-400 hover:text-white hover:bg-zinc-800"
                }`}
              >
                {link.label}
              </Link>
            ))}
            <button
              onClick={handleSync}
              disabled={syncing}
              aria-busy={syncing}
              className="ml-2 bg-green-600 hover:bg-green-500 disabled:bg-green-800 disabled:cursor-not-allowed text-white text-sm font-semibold px-4 py-2 rounded-lg transition-colors"
            >
              {syncing ? "Syncing..." : "Sync Data"}
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {menuOpen && (
          <div className="sm:hidden pb-4 space-y-2">
            {links.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setMenuOpen(false)}
                aria-current={pathname === link.href ? "page" : undefined}
                className={`block px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  pathname === link.href
                    ? "bg-zinc-800 text-white"
                    : "text-zinc-400 hover:text-white hover:bg-zinc-800"
                }`}
              >
                {link.label}
              </Link>
            ))}
            <button
              onClick={() => { setMenuOpen(false); handleSync(); }}
              disabled={syncing}
              className="w-full bg-green-600 hover:bg-green-500 disabled:bg-green-800 text-white text-sm font-semibold px-4 py-2 rounded-lg transition-colors"
            >
              {syncing ? "Syncing..." : "Sync Data"}
            </button>
          </div>
        )}
      </div>
    </nav>
  );
}
