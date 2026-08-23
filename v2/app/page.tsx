import { ArrowRight, BarChart3, CheckCircle2, GraduationCap, ShieldCheck } from "lucide-react";

const principles = [
  { icon: GraduationCap, title: "One school workspace", text: "Attendance, academics and communication in one calm place." },
  { icon: ShieldCheck, title: "Role-aware by default", text: "Every screen is shaped around what the user actually needs." },
  { icon: BarChart3, title: "Useful data", text: "Turn everyday school activity into clear, actionable signals." },
];

export default function Home() {
  return (
    <main className="min-h-screen px-6 py-8 sm:px-10 lg:px-16">
      <div className="mx-auto max-w-6xl">
        <nav className="flex items-center justify-between border-b border-black/8 pb-6">
          <div className="flex items-center gap-2.5 font-semibold tracking-tight">
            <div className="grid size-8 place-items-center rounded-lg bg-[var(--foreground)] text-white">
              <GraduationCap size={17} />
            </div>
            Student OS
          </div>
          <span className="text-sm text-[var(--muted)]">v2 · foundation</span>
        </nav>

        <section className="grid gap-12 py-20 lg:grid-cols-[1.2fr_.8fr] lg:items-end lg:py-28">
          <div>
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-black/8 bg-white px-3 py-1.5 text-xs font-medium text-[var(--muted)] shadow-sm">
              <CheckCircle2 size={14} /> Built around real school workflows
            </div>
            <h1 className="max-w-3xl text-5xl font-semibold leading-[1.02] tracking-[-0.045em] sm:text-6xl lg:text-7xl">
              School operations, without the chaos.
            </h1>
            <p className="mt-7 max-w-2xl text-lg leading-8 text-[var(--muted)] sm:text-xl">
              Student OS is being rebuilt from the ground up as a fast, focused workspace for administrators, teachers and students.
            </p>
            <div className="mt-9 flex flex-wrap gap-3">
              <button className="inline-flex items-center gap-2 rounded-xl bg-[var(--foreground)] px-5 py-3 text-sm font-medium text-white transition hover:opacity-90">
                Explore the foundation <ArrowRight size={16} />
              </button>
              <button className="rounded-xl border border-black/10 bg-white px-5 py-3 text-sm font-medium transition hover:bg-black/[.03]">
                View product principles
              </button>
            </div>
          </div>

          <div className="rounded-3xl border border-black/8 bg-white p-6 shadow-[0_24px_70px_rgba(0,0,0,.07)]">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--muted)]">First workflow</p>
            <div className="mt-6 space-y-3">
              {["Admin creates a class", "Teacher joins the class", "Students are enrolled", "Teacher marks attendance", "Student sees attendance"].map((item, index) => (
                <div key={item} className="flex items-center gap-3 rounded-xl border border-black/7 px-4 py-3">
                  <span className="grid size-7 shrink-0 place-items-center rounded-full bg-black/[.04] text-xs font-semibold">{index + 1}</span>
                  <span className="text-sm font-medium">{item}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="grid gap-4 border-t border-black/8 py-10 md:grid-cols-3">
          {principles.map(({ icon: Icon, title, text }) => (
            <div key={title} className="rounded-2xl border border-black/7 bg-white p-6">
              <Icon size={19} />
              <h2 className="mt-5 font-semibold tracking-tight">{title}</h2>
              <p className="mt-2 text-sm leading-6 text-[var(--muted)]">{text}</p>
            </div>
          ))}
        </section>
      </div>
    </main>
  );
}
