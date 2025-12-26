"use client";

import { useState } from "react";
import { ChatArea } from "@/components/chat/ChatArea";
import { Sidebar } from "@/components/sidebar/Sidebar";

export default function Home() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  return (
    <div className="flex h-screen bg-zinc-50 dark:bg-black">
      {/* Mobile overlay */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 z-20 bg-black/50 md:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={`fixed z-30 h-full md:relative md:z-0 ${
          isSidebarOpen ? "" : "hidden md:block"
        }`}
      >
        <Sidebar
          isOpen={isSidebarOpen}
          onClose={() => setIsSidebarOpen(false)}
        />
      </div>

      {/* Main Chat Area */}
      <main className="flex flex-1 flex-col">
        {/* Mobile header with menu button */}
        <div className="flex items-center border-b border-zinc-200 p-2 dark:border-zinc-700 md:hidden">
          <button
            type="button"
            onClick={() => setIsSidebarOpen(true)}
            className="rounded p-2 text-zinc-500 hover:bg-zinc-100 dark:hover:bg-zinc-800"
            aria-label="メニューを開く"
          >
            <MenuIcon className="h-5 w-5" />
          </button>
          <span className="ml-2 font-medium text-zinc-900 dark:text-zinc-100">
            ボイスチャット
          </span>
        </div>

        <div className="flex-1">
          <ChatArea />
        </div>
      </main>
    </div>
  );
}

function MenuIcon({ className = "" }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M4 6h16M4 12h16M4 18h16"
      />
    </svg>
  );
}
