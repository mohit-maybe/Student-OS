import { BarChart3, BookOpen, CalendarCheck2, GraduationCap, Users } from "lucide-react";
import { createClient } from "@/lib/supabase/server";

const stats = [
  { label: "Attendance", value: "92.4%", change: "+2.1%", icon: CalendarCheck2 },
  { label: "Students", value: "248", change: "12 new", icon: Users },
  { label: "Classes", value: "18", change: "This term", icon: BookOpen },
  { label: "Performance", value: "84.7%", change: "+4.8%", icon: BarChart3 },
];

export default async function DashboardPage() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  const name = user?.user_metadata?.full_name?.split(" ")[0] || "there";

  return (
    <main className="min-h-screen px-5 py-6 sm:px-8 lg:px-10">
      <div className="mx-auto max-w-7xl">
        <header className="flex items-center justify-between border-b border-[var(--border)] pb-5">
          <div className="flex items-center gap-2.5 font-semibold tracking-[-.02em]"><span className="grid size-9 place-items-center rounded-xl bg-[var(--foreground)] text-white"><GraduationCap size={18} /></span>Student OS</div>
          <span className="text-sm text-[var(--muted)]">{user?.email}</span>
        </header>
        <section className="animate-fade-up py-10">
          <p className="text-sm font-semibold text-[var(--accent)]">Tuesday, 23 August</p>
          <h1 className="mt-2 text-4xl font-semibold tracking-[-.045em]">Good morning, {name}.</h1>
          <p className="mt-2 text-[var(--muted)]">Here&apos;s what&apos;s happening across your school today.</p>
        </section>
        <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {stats.map(({ label, value, change, icon: Icon }, index) => <div key={label} className={`animate-float-in stagger-${index + 1} rounded-2xl border border-[var(--border)] bg-white p-5 shadow-sm transition duration-300 hover:-translate-y-1 hover:shadow-md`}><div className="flex items-center justify-between"><span className="text-sm font-medium text-[var(--muted)]">{label}</span><span className="grid size-9 place-items-center rounded-xl bg-[var(--accent-soft)] text-[var(--accent)]"><Icon size={17} /></span></div><p className="mt-6 text-3xl font-semibold tracking-[-.04em]">{value}</p><p className="mt-1 text-xs font-semibold text-[var(--success)]">{change}</p></div>)}
        </section>
        <section className="mt-5 grid gap-5 lg:grid-cols-[1.3fr_.7fr]">
          <div className="rounded-2xl border border-[var(--border)] bg-white p-6"><div className="flex items-center justify-between"><div><p className="text-xs font-semibold uppercase tracking-[.15em] text-[var(--muted)]">Today</p><h2 className="mt-1 text-lg font-semibold">School activity</h2></div><span className="rounded-full bg-[#f2f4f7] px-3 py-1 text-xs font-semibold text-[var(--muted)]">Live</span></div><div className="mt-6 space-y-3">{["Class 12-A · Physics attendance recorded", "Class 11-B · Mathematics marks updated", "12 new student profiles awaiting review"].map((item) => <div key={item} className="rounded-xl bg-[#f8f9fb] px-4 py-3 text-sm font-medium">{item}</div>)}</div></div>
          <div className="rounded-2xl border border-[var(--border)] bg-white p-6"><p className="text-xs font-semibold uppercase tracking-[.15em] text-[var(--muted)]">Foundation</p><h2 className="mt-1 text-lg font-semibold">Your workspace is private</h2><p className="mt-3 text-sm leading-6 text-[var(--muted)]">This dashboard is now protected by Supabase session authentication. School membership and role-based data come next.</p></div>
        </section>
      </div>
    </main>
  );
}
