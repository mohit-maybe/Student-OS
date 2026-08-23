import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Student OS — School operations, simplified",
  description: "A focused operating system for administrators, teachers and students.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
