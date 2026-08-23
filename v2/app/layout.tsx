import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Student OS",
  description: "A calmer operating system for modern schools.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
