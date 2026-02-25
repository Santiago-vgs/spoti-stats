"use client";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export default function SignIn() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-zinc-950 relative overflow-hidden">
      {/* Gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-green-950/40 via-zinc-950 to-zinc-950" />
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-green-500/10 rounded-full blur-3xl" />
      <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-green-600/5 rounded-full blur-3xl" />

      <div className="relative bg-zinc-900/80 backdrop-blur border border-zinc-800 rounded-2xl p-10 max-w-sm w-full text-center space-y-6 shadow-2xl shadow-black/50">
        <div className="space-y-2">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-green-600/20 mb-2">
            <svg className="w-8 h-8 text-green-500" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.477 2 2 6.477 2 12s4.477 10 10 10 10-4.477 10-10S17.523 2 12 2zm4.586 14.424a.622.622 0 01-.857.207c-2.348-1.435-5.304-1.76-8.785-.964a.622.622 0 11-.277-1.215c3.809-.87 7.076-.496 9.712 1.115a.623.623 0 01.207.857zm1.224-2.719a.78.78 0 01-1.072.257c-2.687-1.652-6.785-2.131-9.965-1.166a.78.78 0 01-.973-.519.781.781 0 01.52-.972c3.632-1.102 8.147-.568 11.234 1.328a.78.78 0 01.256 1.072zm.105-2.835C14.692 8.95 9.375 8.775 6.297 9.71a.936.936 0 11-.543-1.791c3.532-1.072 9.404-.865 13.115 1.338a.936.936 0 01-.954 1.613z"/>
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-white">Spoti Stats</h1>
          <p className="text-zinc-400 text-sm">
            Connect your Spotify account to view your listening analytics.
          </p>
        </div>
        <a
          href={`${API_BASE}/auth/login`}
          className="inline-block w-full bg-green-600 hover:bg-green-500 active:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg transition-all hover:shadow-lg hover:shadow-green-600/20"
        >
          Sign in with Spotify
        </a>
        <p className="text-zinc-500 text-xs">
          We only read your listening history — nothing is modified.
        </p>
      </div>
    </div>
  );
}
