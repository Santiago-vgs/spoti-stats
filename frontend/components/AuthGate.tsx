"use client";

import { useAuth } from "@/lib/useAuth";
import SignIn from "@/components/ui/SignIn";
import Navbar from "@/components/ui/Navbar";

export default function AuthGate({ children }: { children: React.ReactNode }) {
  const { authenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-zinc-950">
        <div className="flex items-center gap-3">
          <div className="h-5 w-5 animate-spin rounded-full border-2 border-green-500 border-t-transparent" />
          <span className="text-zinc-400 text-lg">Loading...</span>
        </div>
      </div>
    );
  }

  if (!authenticated) {
    return <SignIn />;
  }

  return (
    <>
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:p-4 focus:bg-green-600 focus:text-white"
      >
        Skip to content
      </a>
      <Navbar />
      <main id="main-content" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </>
  );
}
