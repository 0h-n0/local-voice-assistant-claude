"use client";

import { useEffect, useState } from "react";
import { getHealth } from "@/lib/api";
import type { HealthResponse } from "@/types";

export default function Home() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchHealth() {
      try {
        const response = await getHealth();
        setHealth(response);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch health");
        setHealth(null);
      } finally {
        setLoading(false);
      }
    }

    fetchHealth();
  }, []);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-zinc-50 p-8 font-sans dark:bg-black">
      <main className="flex w-full max-w-md flex-col items-center gap-8 rounded-lg bg-white p-8 shadow-lg dark:bg-zinc-900">
        <h1 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">
          Local Voice Assistant
        </h1>

        <div className="w-full rounded-md border border-zinc-200 p-4 dark:border-zinc-700">
          <h2 className="mb-2 text-lg font-semibold text-zinc-700 dark:text-zinc-300">
            Backend Health Status
          </h2>

          {loading && (
            <p className="text-zinc-500 dark:text-zinc-400">
              Checking backend health...
            </p>
          )}

          {error && (
            <div className="rounded-md bg-red-50 p-3 dark:bg-red-900/20">
              <p className="text-sm text-red-700 dark:text-red-400">
                Error: {error}
              </p>
              <p className="mt-1 text-xs text-red-500 dark:text-red-500">
                Make sure the backend is running on port 8000
              </p>
            </div>
          )}

          {health && (
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <span
                  className={`h-3 w-3 rounded-full ${
                    health.status === "healthy"
                      ? "bg-green-500"
                      : "bg-red-500"
                  }`}
                />
                <span className="font-medium capitalize text-zinc-700 dark:text-zinc-300">
                  {health.status}
                </span>
              </div>
              <p className="text-sm text-zinc-600 dark:text-zinc-400">
                Version: {health.version}
              </p>
              <p className="text-sm text-zinc-600 dark:text-zinc-400">
                Last checked: {new Date(health.timestamp).toLocaleString()}
              </p>
            </div>
          )}
        </div>

        <p className="text-center text-sm text-zinc-500 dark:text-zinc-400">
          Frontend running on port 3000
          <br />
          Backend expected on port 8000
        </p>
      </main>
    </div>
  );
}
