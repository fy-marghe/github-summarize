import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000'),
  title: {
    template: "%s | GitHub SEO",
    default: "GitHub SEO - Understand any GitHub repository in minutes.",
  },
  description: "Understand any GitHub repository in minutes. AI-generated explanations, architectures, and comparisons.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen flex flex-col`}>
        <header className="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-black sticky top-0 z-10">
          <div className="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
            <a href="/" className="font-bold text-xl tracking-tight">GitHub SEO</a>
            <nav className="flex gap-4 text-sm font-medium text-gray-600 dark:text-gray-300">
              <a href="/topic" className="hover:text-black dark:hover:text-white transition-colors">Topics</a>
              <a href="/language" className="hover:text-black dark:hover:text-white transition-colors">Languages</a>
            </nav>
          </div>
        </header>
        <main className="flex-1 max-w-5xl mx-auto w-full px-4 py-8">
          {children}
        </main>
        <footer className="border-t border-gray-200 dark:border-gray-800 py-8 text-center text-sm text-gray-500">
          <p>© {new Date().getFullYear()} GitHub SEO. Built for finding the right code.</p>
        </footer>
      </body>
    </html>
  );
}
