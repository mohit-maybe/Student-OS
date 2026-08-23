"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { ArrowRight, GraduationCap, Loader2 } from "lucide-react";
import { createClient } from "@/lib/supabase/client";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    const supabase = createClient();
    const { error: authError } = await supabase.auth.signInWithPassword({ email, password });
    if (authError) {
      setError(authError.message);
      setLoading(false);
      return;
    }
    window.location.href = "/dashboard";
  }

  return (
    <main className="min-h-screen bg-[var(--background)] px-5 py-6">
      <div className="mx-auto flex min-h-[calc(100vh-48px)] max-w-6xl flex-col justify-between">
        <header className="animate-fade-up flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5 font-semibold tracking-[-.02em]">
            <span className="grid size-9 place-items-center rounded-xl bg-[var(--foreground)] text-white"><GraduationCap size={18} /></span>
            Student OS
          </Link>
          <Link href="/" className="text-sm font-medium text-[var(--muted)] transition hover:text-[var(--foreground)]">Back home</Link>
        </header>

        <section className="mx-auto w-full max-w-md py-16">
          <div className="animate-float-in rounded-[28px] border border-[var(--border)] bg-white p-7 shadow-[0_30px_90px_rgba(15,23,42,.08)] sm:p-9">
            <div className="mb-8">
              <p className="text-sm font-semibold text-[var(--accent)]">Welcome back</p>
              <h1 className="mt-2 text-3xl font-semibold tracking-[-.04em]">Sign in to Student OS</h1>
              <p className="mt-2 text-sm leading-6 text-[var(--muted)]">Use your school account to continue.</p>
            </div>
            <form onSubmit={handleSubmit} className="space-y-5">
              <label className="block">
                <span className="mb-2 block text-sm font-semibold">Email</span>
                <input required type="email" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} className="w-full rounded-xl border border-[var(--border)] bg-[#fbfcfd] px-4 py-3 text-sm outline-none transition focus:border-[var(--accent)] focus:bg-white focus:ring-4 focus:ring-indigo-100" placeholder="you@school.edu" />
              </label>
              <label className="block">
                <span className="mb-2 block text-sm font-semibold">Password</span>
                <input required type="password" autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full rounded-xl border border-[var(--border)] bg-[#fbfcfd] px-4 py-3 text-sm outline-none transition focus:border-[var(--accent)] focus:bg-white focus:ring-4 focus:ring-indigo-100" placeholder="••••••••" />
              </label>
              {error && <p role="alert" className="rounded-xl bg-red-50 px-4 py-3 text-sm leading-5 text-red-700">{error}</p>}
              <button disabled={loading} className="group flex w-full items-center justify-center gap-2 rounded-xl bg-[var(--foreground)] px-5 py-3.5 text-sm font-semibold text-white transition duration-300 hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-60">
                {loading ? <Loader2 size={17} className="animate-spin" /> : <>Continue <ArrowRight size={16} className="transition-transform group-hover:translate-x-1" /></>}
              </button>
            </form>
          </div>
          <p className="mt-6 text-center text-xs leading-5 text-[var(--muted)]">Your school administrator manages account access.</p>
        </section>
        <footer className="pb-2 text-center text-xs text-slate-400">Student OS · v2</footer>
      </div>
    </main>
  );
}
