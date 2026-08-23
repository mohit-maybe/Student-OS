import Link from "next/link";
import { ArrowRight, BarChart3, CheckCircle2, GraduationCap, ShieldCheck } from "lucide-react";

const principles = [
  { icon: GraduationCap, title: "One school workspace", text: "Attendance, academics and communication in one calm place." },
  { icon: ShieldCheck, title: "Role-aware by default", text: "Every screen is shaped around what the user actually needs." },
  { icon: BarChart3, title: "Useful data", text: "Turn everyday school activity into clear, actionable signals." },
];

const workflow = ["Admin creates a class", "Teacher joins the class", "Students are enrolled", "Teacher marks attendance", "Student sees attendance"];

export default function Home() {
  return (
    <main className="min-h-screen overflow-hidden px-5 py-6 sm:px-8 lg:px-12">
      <div className="mx-auto max-w-6xl">
        <nav className="animate-fade-up flex items-center justify-between border-b border-[var(--border)] pb-5">
          <div className="flex items-center gap-2.5 font-semibold tracking-[-.02em]">
            <div className="grid size-9 place-items-center rounded-xl bg-[var(--foreground)] text-white shadow-sm"><GraduationCap size={18} /></div>
            Student OS
          </div>
          <div className="flex items-center gap-3 text-sm text-[var(--muted)]">
            <span className="hidden sm:inline">v2 · foundation</span>
            <Link href="/login" className="rounded-lg px-3 py-2 font-medium text-[var(--foreground)] transition hover:bg-white">Sign in</Link>
          </div>
        </nav>

        <section className="grid gap-14 py-20 lg:grid-cols-[1.12fr_.88fr] lg:items-center lg:py-28">
          <div>
            <div className="animate-fade-up stagger-1 mb-7 inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-white px-3.5 py-2 text-xs font-semibold text-[var(--muted)] shadow-sm">
              <CheckCircle2 size={14} className="text-[var(--success)]" /> Built around real school workflows
            </div>
            <h1 className="animate-fade-up stagger-2 max-w-3xl text-5xl font-semibold leading-[.98] tracking-[-.055em] sm:text-6xl lg:text-[76px]">
              School operations, <span className="text-[var(--accent)]">without the chaos.</span>
            </h1>
            <p className="animate-fade-up stagger-3 mt-7 max-w-2xl text-lg leading-8 text-[var(--muted)] sm:text-xl">
              A focused workspace for administrators, teachers and students — designed to make the everyday school workflow feel simple.
            </p>
            <div className="animate-fade-up stagger-4 mt-9 flex flex-wrap items-center gap-3">
              <Link href="/login" className="group inline-flex items-center gap-2 rounded-xl bg-[var(--foreground)] px-5 py-3.5 text-sm font-semibold text-white shadow-[0_8px_24px_rgba(17,24,39,.14)] transition duration-300 hover:-translate-y-0.5 hover:shadow-[0_12px_30px_rgba(17,24,39,.18)]">
                Enter Student OS <ArrowRight size={16} className="transition-transform group-hover:translate-x-1" />
              </Link>
              <a href="#principles" className="rounded-xl border border-[var(--border)] bg-white px-5 py-3.5 text-sm font-semibold transition duration-300 hover:-translate-y-0.5 hover:border-slate-300">See how it works</a>
            </div>
            <div className="mt-12 text-[var(--foreground)]">
              <span className="text-sm text-[var(--muted)]">Built with intention, one workflow at a time.</span><br />
              <span className="handwritten mt-2 text-4xl text-[var(--accent)]">Make school feel simpler.</span>
            </div>
          </div>

          <div className="animate-float-in rounded-[28px] border border-[var(--border)] bg-white/90 p-5 shadow-[0_30px_90px_rgba(15,23,42,.09)] backdrop-blur">
            <div className="flex items-center justify-between px-2 py-1">
              <div><p className="text-xs font-semibold uppercase tracking-[.16em] text-[var(--muted)]">First workflow</p><p className="mt-1 text-sm font-semibold">From setup to attendance</p></div>
              <span className="rounded-full bg-[var(--accent-soft)] px-2.5 py-1 text-[11px] font-semibold text-[var(--accent)]">v2</span>
            </div>
            <div className="mt-5 space-y-2.5">
              {workflow.map((item, index) => (
                <div key={item} className="group flex items-center gap-3 rounded-2xl border border-transparent bg-[#f8f9fb] px-4 py-3.5 transition duration-300 hover:border-[var(--border)] hover:bg-white hover:shadow-sm">
                  <span className="grid size-8 shrink-0 place-items-center rounded-full bg-white text-xs font-bold text-[var(--muted)] shadow-sm">{index + 1}</span>
                  <span className="text-sm font-semibold">{item}</span>
                  <ArrowRight size={14} className="ml-auto text-slate-300 transition-transform group-hover:translate-x-0.5" />
                </div>
              ))}
            </div>
          </div>
        </section>

        <section id="principles" className="grid gap-4 border-t border-[var(--border)] py-12 md:grid-cols-3">
          {principles.map(({ icon: Icon, title, text }) => (
            <div key={title} className="animate-float-in rounded-2xl border border-[var(--border)] bg-white p-6 transition duration-300 hover:-translate-y-1 hover:shadow-[0_16px_45px_rgba(15,23,42,.06)]">
              <div className="grid size-9 place-items-center rounded-xl bg-[var(--accent-soft)] text-[var(--accent)]"><Icon size={18} /></div>
              <h2 className="mt-5 font-semibold tracking-[-.02em]">{title}</h2>
              <p className="mt-2 text-sm leading-6 text-[var(--muted)]">{text}</p>
            </div>
          ))}
        </section>
      </div>
    </main>
  );
}
