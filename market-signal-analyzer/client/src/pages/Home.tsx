import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { trpc } from "@/lib/trpc";
import { startLogin } from "@/const";
import {
  Activity, ArrowDownRight, ArrowUpRight, BarChart3, Bot, BrainCircuit, ChevronRight,
  CircleAlert, CircleCheck, CircleDotDashed, Clock3, Database, FileText, Globe2,
  Layers3, LineChart, Loader2, Menu, Newspaper, Radar, RefreshCw, ShieldCheck,
  SlidersHorizontal, Sparkles, WalletCards, X,
} from "lucide-react";
import { useMemo, useState } from "react";
import {
  Area, AreaChart, Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import { toast } from "sonner";

const heroAsset = "/manus-storage/market-signal-global-network_b4b79bc2.png";

const navItems = [
  { label: "Signal desk", icon: Radar, href: "#signal-desk" },
  { label: "Source ledger", icon: Newspaper, href: "#sources" },
  { label: "Paper book", icon: WalletCards, href: "#paper-book" },
  { label: "Methodology", icon: ShieldCheck, href: "#methodology" },
];

const priceData = [
  { t: "09:30", price: 48, sentiment: 51, volume: 38 }, { t: "10:20", price: 51, sentiment: 49, volume: 52 },
  { t: "11:10", price: 49, sentiment: 54, volume: 43 }, { t: "12:00", price: 56, sentiment: 58, volume: 68 },
  { t: "12:50", price: 54, sentiment: 60, volume: 57 }, { t: "13:40", price: 61, sentiment: 64, volume: 74 },
  { t: "14:30", price: 59, sentiment: 62, volume: 63 }, { t: "15:20", price: 65, sentiment: 67, volume: 81 },
];

const sectorData = [
  { sector: "Compute", score: 74, tone: "positive" }, { sector: "Energy", score: 62, tone: "mixed" },
  { sector: "Payments", score: 57, tone: "mixed" }, { sector: "Crypto", score: 69, tone: "positive" },
  { sector: "Rates", score: 43, tone: "negative" },
];

const illustrationSignals = [
  { symbol: "NOVA", type: "Equity", direction: "Upside", confidence: 68, note: "Supply-chain relief remains a hypothesis until primary releases corroborate it.", color: "lime" },
  { symbol: "BTC", type: "Crypto", direction: "Watch", confidence: 56, note: "Liquidity narrative is mixed; price context is not connected.", color: "amber" },
  { symbol: "ARCC", type: "Equity", direction: "Downside", confidence: 52, note: "Risk is flagged from an illustrative scenario, not a live recommendation.", color: "rose" },
];

type RetrievedStory = {
  providerItemId: string; canonicalUrl: string; title: string; summary: string; publisher: string; language?: string | null;
  publishedAt?: Date | string | null; acquiredAt: Date | string; imageUrl?: string | null;
};

function StatusDot({ status }: { status: string }) {
  const tone = status === "connected" ? "bg-[#d9fb63] shadow-[0_0_10px_#d9fb63]" : status === "attention" ? "bg-[#ffbf69]" : status === "paper_only" ? "bg-[#8da4ff]" : "bg-[#9a9e91]";
  return <span className={cn("mt-1.5 h-2 w-2 shrink-0 rounded-full", tone)} />;
}

function Metric({ label, value, delta, positive }: { label: string; value: string; delta: string; positive?: boolean }) {
  return <article className="min-w-[148px] border-l border-white/10 px-4 first:border-l-0 first:pl-0">
    <p className="mono text-[10px] uppercase tracking-[.17em] text-white/42">{label}</p>
    <div className="mt-1 flex items-end gap-2"><strong className="text-xl font-extrabold tracking-tight text-white">{value}</strong><span className={cn("mb-0.5 flex items-center text-[11px] font-bold", positive ? "text-[#d9fb63]" : "text-[#ff7a7a]")}>{positive ? <ArrowUpRight className="mr-0.5 h-3 w-3" /> : <ArrowDownRight className="mr-0.5 h-3 w-3" />}{delta}</span></div>
  </article>;
}

export default function Home() {
  const { isAuthenticated } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [topic, setTopic] = useState("markets OR stocks OR crypto");
  const [selectedStory, setSelectedStory] = useState<RetrievedStory | null>(null);
  const [chartPoint, setChartPoint] = useState(0);
  const utils = trpc.useUtils();
  const status = trpc.market.connectionStatus.useQuery();
  const portfolio = trpc.market.paperPortfolio.useQuery();
  const newsQuery = trpc.market.refreshGlobalNews.useQuery({ query: topic }, { enabled: false, retry: false });
  const retainedNews = trpc.market.retainedNews.useQuery(undefined, { enabled: isAuthenticated });
  const retainNews = trpc.market.retainGlobalNews.useMutation({
    onSuccess: result => {
      void utils.market.retainedNews.invalidate();
      toast.success(`${result.retained} sources retained`, { description: result.airtable.status === "synced" ? `${result.airtable.synced} records synchronized to Airtable.` : "Airtable is not configured, so this batch remains in the application database." });
    },
    onError: error => toast.error("Sign in to retain source evidence", { description: error.message }),
  });
  const analyze = trpc.market.analyzeEvidence.useMutation({
    onSuccess: response => toast.success("Evidence hypothesis generated", { description: `Cutoff: ${new Date(response.informationCutoffAt).toLocaleTimeString()}` }),
    onError: error => toast.error("Analysis needs a signed-in research session", { description: error.message }),
  });

  const stories = useMemo(() => (newsQuery.data?.items ?? []) as RetrievedStory[], [newsQuery.data]);
  const latestAnalysis = analyze.data?.analysis as { assetSymbols: string[]; catalyst: string; direction: string; sentiment: string; confidence: number; hypothesis: string; uncertainty: string; evidenceExcerpt: string } | undefined;
  const activeChartPoint = priceData[chartPoint];

  async function refreshNews() {
    const result = await newsQuery.refetch();
    if (result.data?.mode === "retrieved") toast.success(`${result.data.items.length} provenance-linked stories retrieved`);
    else toast.error("Global discovery is temporarily unavailable", { description: result.data?.error ?? "Try again shortly." });
  }

  function retainSourceBatch() {
    if (!isAuthenticated) {
      toast.message("Sign in to retain the source batch", { description: "Retention and external sync are authenticated server-side actions." });
      return;
    }
    retainNews.mutate({ query: topic });
  }

  function analyzeStory(story: RetrievedStory) {
    setSelectedStory(story);
    if (!isAuthenticated) { toast.message("Sign in to run private evidence analysis", { description: "The underlying model is server-side and keeps credentials out of the browser." }); return; }
    analyze.mutate({ title: story.title, publisher: story.publisher, canonicalUrl: story.canonicalUrl, summary: story.summary, publishedAt: story.publishedAt ? new Date(story.publishedAt) : undefined });
  }

  return (
    <div className="min-h-screen overflow-x-hidden bg-[#070807] text-[#f4f5ec]">
      <div className="noise-layer" />
      <header className="sticky top-0 z-40 border-b border-white/10 bg-[#070807]/88 backdrop-blur-xl">
        <div className="mx-auto flex h-[70px] max-w-[1580px] items-center justify-between px-5 lg:px-8">
          <a href="#signal-desk" className="group flex items-center gap-3" aria-label="MarketSignal OS home">
            <span className="relative grid h-8 w-8 place-items-center overflow-hidden rounded-full border border-[#d9fb63]/70 bg-[#d9fb63] text-[#10120d]"><Activity className="h-4 w-4" /><i className="signal-pulse absolute inset-1 rounded-full border border-[#10120d]/50" /></span>
            <span><strong className="block text-[13px] font-extrabold uppercase tracking-[.12em]">MarketSignal</strong><span className="mono block text-[9px] tracking-[.18em] text-white/42">INTELLIGENCE OS / 01</span></span>
          </a>
          <nav className="hidden items-center gap-1 lg:flex" aria-label="Workspace navigation">
            {navItems.map(item => <a key={item.label} href={item.href} className="flex items-center gap-2 rounded-full px-4 py-2 text-xs font-bold text-white/55 transition hover:bg-white/5 hover:text-white"><item.icon className="h-3.5 w-3.5" />{item.label}</a>)}
          </nav>
          <div className="flex items-center gap-2">
            <span className="mono hidden text-[10px] text-white/45 sm:block"><span className="mr-1.5 inline-block h-1.5 w-1.5 rounded-full bg-[#d9fb63]" />PAPER MODE</span>
            {!isAuthenticated && <Button size="sm" onClick={startLogin} className="hidden h-9 rounded-full bg-[#d9fb63] px-4 text-xs font-extrabold text-[#10120d] hover:bg-[#ecff9c] sm:inline-flex">Sign in</Button>}
            <Button variant="ghost" size="icon" onClick={() => setMobileMenuOpen(value => !value)} className="h-9 w-9 rounded-full border border-white/10 lg:hidden" aria-label="Toggle menu">{mobileMenuOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}</Button>
          </div>
        </div>
        {mobileMenuOpen && <nav className="border-t border-white/10 bg-[#0d0e0d] px-5 py-3 lg:hidden">{navItems.map(item => <a onClick={() => setMobileMenuOpen(false)} key={item.label} href={item.href} className="flex items-center gap-3 rounded-lg px-2 py-3 text-sm font-bold text-white/75"><item.icon className="h-4 w-4 text-[#d9fb63]" />{item.label}</a>)}</nav>}
      </header>

      <main className="mx-auto max-w-[1580px] px-5 pb-16 pt-5 lg:px-8">
        <section id="signal-desk" className="grid-backdrop relative isolate overflow-hidden rounded-[1.6rem] border border-white/10 bg-[#0e100e] px-5 py-6 sm:px-8 sm:py-10 lg:min-h-[420px]">
          <img src={heroAsset} alt="Abstract world data network" className="slow-drift pointer-events-none absolute inset-0 h-full w-full object-cover object-right opacity-55 mix-blend-screen" />
          <div className="pointer-events-none absolute inset-0 bg-gradient-to-r from-[#0e100e] via-[#0e100e]/88 to-[#0e100e]/15" />
          <div className="relative max-w-3xl">
            <div className="mb-6 flex items-center gap-2"><span className="h-px w-8 bg-[#d9fb63]" /><span className="mono text-[10px] uppercase tracking-[.2em] text-[#d9fb63]">OPEN RESEARCH DESK / UTC</span></div>
            <h1 className="max-w-2xl text-4xl font-extrabold leading-[.96] tracking-[-.065em] text-white sm:text-5xl lg:text-7xl">News becomes <span className="serif font-bold italic text-[#d9fb63]">context.</span><br />Not a promise.</h1>
            <p className="type-cursor mt-6 max-w-xl text-sm leading-6 text-white/60 sm:text-[15px]">Trace sources, inspect uncertainty, timestamp hypotheses, and evaluate paper trades only after the market has had time to respond.</p>
            <div className="mt-8 flex flex-wrap gap-3"><Button onClick={refreshNews} disabled={newsQuery.isFetching} className="h-11 rounded-full bg-[#d9fb63] px-5 text-xs font-extrabold text-[#10120d] hover:bg-[#ecff9c]">{newsQuery.isFetching ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <RefreshCw className="mr-2 h-4 w-4" />}Refresh global discovery</Button><a href="#methodology" className="inline-flex h-11 items-center rounded-full border border-white/15 px-5 text-xs font-extrabold text-white/75 transition hover:bg-white/5">Read safeguards<ChevronRight className="ml-1 h-4 w-4" /></a></div>
          </div>
          <div className="relative mt-10 grid grid-cols-2 gap-3 sm:grid-cols-4 lg:absolute lg:bottom-8 lg:right-8 lg:mt-0"><Metric label="Source coverage" value="Global" delta="GDELT" positive /><Metric label="Mode" value="Paper" delta="No live route" positive /><Metric label="Cutoff" value="UTC" delta="Locked" positive /><Metric label="Forecasts" value="Uncertain" delta="Required" /></div>
        </section>

        <section className="mt-5 grid gap-5 xl:grid-cols-[1.55fr_.82fr]">
          <div className="rounded-[1.35rem] border border-white/10 bg-[#101210] p-5 sm:p-6">
            <div className="flex flex-wrap items-start justify-between gap-4"><div><p className="mono text-[10px] uppercase tracking-[.18em] text-white/38">Daily signal temperature</p><h2 className="mt-1 text-xl font-extrabold tracking-[-.045em]">Context movement, not a price forecast</h2></div><span className="rounded-full border border-[#d9fb63]/25 bg-[#d9fb63]/10 px-3 py-1 mono text-[10px] text-[#d9fb63]">ILLUSTRATIVE SIMULATION</span></div>
            <div className="mt-5 h-[238px] w-full" role="img" aria-label="Illustrative context index and sentiment chart; use the chart controls below to read each data point"><ResponsiveContainer width="100%" height="100%"><AreaChart data={priceData} margin={{ top: 12, right: 2, left: -24, bottom: 0 }}><defs><linearGradient id="signalArea" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#d9fb63" stopOpacity={.34} /><stop offset="100%" stopColor="#d9fb63" stopOpacity={0} /></linearGradient></defs><CartesianGrid stroke="#ffffff" strokeOpacity={.07} vertical={false} /><XAxis dataKey="t" axisLine={false} tickLine={false} tick={{ fill: "#7d8278", fontSize: 10, fontFamily: "DM Mono" }} /><YAxis axisLine={false} tickLine={false} tick={{ fill: "#7d8278", fontSize: 10, fontFamily: "DM Mono" }} /><Tooltip cursor={{ stroke: "#d9fb63", strokeOpacity: .28 }} contentStyle={{ background: "#151715", border: "1px solid #30352d", borderRadius: "10px", fontSize: "11px" }} /><Area type="monotone" dataKey="price" stroke="#d9fb63" strokeWidth={2.2} fill="url(#signalArea)" name="Context index" /><Area type="monotone" dataKey="sentiment" stroke="#8da4ff" strokeWidth={1.2} strokeDasharray="5 5" fill="transparent" name="Sentiment" /></AreaChart></ResponsiveContainer></div>
            <div className="mt-3 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-white/10 bg-black/20 px-3 py-2" aria-label="Accessible chart navigation"><div className="flex items-center gap-1"><Button type="button" variant="ghost" size="sm" onClick={() => setChartPoint(point => Math.max(0, point - 1))} disabled={chartPoint === 0} className="h-7 px-2 text-xs text-white/70">Previous</Button><Button type="button" variant="ghost" size="sm" onClick={() => setChartPoint(point => Math.min(priceData.length - 1, point + 1))} disabled={chartPoint === priceData.length - 1} className="h-7 px-2 text-xs text-white/70">Next</Button></div><p aria-live="polite" className="mono text-[10px] text-white/52">{activeChartPoint.t} · context {activeChartPoint.price} · sentiment {activeChartPoint.sentiment} · volume {activeChartPoint.volume}</p></div>
            <div className="mt-4 grid grid-cols-[auto_1fr] items-center gap-3 border-t border-white/10 pt-3"><p className="mono text-[9px] uppercase tracking-[.15em] text-white/36">Relative volume</p><div className="h-[52px] min-w-0"><ResponsiveContainer width="100%" height="100%"><BarChart data={priceData}><Bar dataKey="volume" radius={[3, 3, 0, 0]} fill="#8da4ff" fillOpacity={.72} /></BarChart></ResponsiveContainer></div></div>
            <p className="mt-3 border-t border-white/10 pt-3 text-xs leading-5 text-white/42"><CircleAlert className="mr-1.5 inline h-3.5 w-3.5 text-[#ffbf69]" />Values above are a layout-only simulation. No connected price feed is being represented as live market data.</p>
          </div>

          <aside className="rounded-[1.35rem] border border-white/10 bg-[#101210] p-5 sm:p-6"><div className="flex items-center justify-between"><div><p className="mono text-[10px] uppercase tracking-[.18em] text-white/38">Market regime</p><h2 className="mt-1 text-xl font-extrabold tracking-[-.045em]">Balanced risk posture</h2></div><div className="grid h-11 w-11 place-items-center rounded-full border border-[#d9fb63]/30 bg-[#d9fb63]/10"><Radar className="h-5 w-5 text-[#d9fb63]" /></div></div><p className="mt-4 text-sm leading-6 text-white/57">The dashboard keeps uncertain or contradictory evidence visible instead of collapsing it into a single trade command.</p><div className="mt-6 space-y-4">{[{ label: "Macro / rates", value: "Mixed", pct: 46 }, { label: "Risk appetite", value: "Constructive", pct: 64 }, { label: "Cross-asset agreement", value: "Partial", pct: 52 }].map(row => <div key={row.label}><div className="mb-2 flex justify-between text-xs"><span className="font-bold text-white/72">{row.label}</span><span className="mono text-white/42">{row.value}</span></div><div className="h-1.5 overflow-hidden rounded-full bg-white/8"><div className="h-full rounded-full bg-[#d9fb63]" style={{ width: `${row.pct}%`, opacity: row.pct < 55 ? .54 : .9 }} /></div></div>)}</div></aside>
        </section>

        <section className="mt-5 grid gap-5 lg:grid-cols-[.96fr_1.54fr]">
          <article className="rounded-[1.35rem] border border-white/10 bg-[#101210] p-5 sm:p-6"><div className="flex items-start justify-between gap-3"><div><p className="mono text-[10px] uppercase tracking-[.18em] text-white/38">Sector impact</p><h2 className="mt-1 text-xl font-extrabold tracking-[-.045em]">Evidence-weighted attention</h2></div><BarChart3 className="h-5 w-5 text-white/35" /></div><div className="mt-4 h-[244px]"><ResponsiveContainer width="100%" height="100%"><BarChart layout="vertical" data={sectorData} margin={{ left: -10, right: 13 }}><XAxis type="number" domain={[0, 100]} hide /><YAxis type="category" dataKey="sector" width={74} axisLine={false} tickLine={false} tick={{ fill: "#afb2a8", fontSize: 11, fontWeight: 700 }} /><Tooltip cursor={{ fill: "rgba(217,251,99,.05)" }} contentStyle={{ background: "#151715", border: "1px solid #30352d", borderRadius: "10px", fontSize: "11px" }} /><Bar dataKey="score" radius={[0, 9, 9, 0]} fill="#d9fb63" /></BarChart></ResponsiveContainer></div><p className="mt-2 text-xs leading-5 text-white/42">Attention score reflects the illustrative dashboard state; it is not a valuation or expected-return metric.</p></article>
          <article className="rounded-[1.35rem] border border-white/10 bg-[#101210] p-5 sm:p-6"><div className="flex flex-wrap items-start justify-between gap-3"><div><p className="mono text-[10px] uppercase tracking-[.18em] text-white/38">Trend board</p><h2 className="mt-1 text-xl font-extrabold tracking-[-.045em]">Questions worth monitoring</h2></div><span className="flex items-center gap-1.5 text-[11px] font-bold text-white/45"><CircleDotDashed className="h-3.5 w-3.5 text-[#d9fb63]" />Hypotheses, not calls</span></div><div className="mt-5 grid gap-3 sm:grid-cols-3">{illustrationSignals.map(signal => <div key={signal.symbol} className="group rounded-2xl border border-white/10 bg-white/[.025] p-4 transition hover:border-white/20 hover:bg-white/[.045]"><div className="flex items-start justify-between"><div><span className="mono text-[10px] text-white/40">{signal.type}</span><h3 className="mt-1 text-2xl font-extrabold tracking-[-.06em]">{signal.symbol}</h3></div><span className={cn("mt-1 h-2 w-2 rounded-full", signal.color === "lime" ? "bg-[#d9fb63]" : signal.color === "amber" ? "bg-[#ffbf69]" : "bg-[#ff7a7a]")} /></div><p className="mt-5 text-xs font-bold text-white/72">{signal.direction} <span className="mono font-normal text-white/35">/ {signal.confidence}% context confidence</span></p><p className="mt-2 text-[11px] leading-5 text-white/43">{signal.note}</p></div>)}</div></article>
        </section>

        <section id="sources" className="mt-5 rounded-[1.35rem] border border-white/10 bg-[#101210] p-5 sm:p-6"><div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end"><div><div className="flex items-center gap-2"><Newspaper className="h-4 w-4 text-[#d9fb63]" /><p className="mono text-[10px] uppercase tracking-[.18em] text-white/38">Source ledger</p></div><h2 className="mt-2 text-2xl font-extrabold tracking-[-.05em]">Inspect the evidence before the hypothesis.</h2><p className="mt-2 max-w-2xl text-sm leading-6 text-white/48">Fetch globally scoped discovery results, retain original publisher links and acquisition timestamps, then run a private, structured analysis only on selected evidence.</p></div><div className="flex w-full max-w-md gap-2"><Input value={topic} onChange={event => setTopic(event.target.value)} aria-label="Global news search topic" className="h-10 border-white/10 bg-black/25 text-xs text-white placeholder:text-white/30" placeholder="Search topic" /><Button variant="outline" onClick={refreshNews} disabled={newsQuery.isFetching} className="h-10 shrink-0 border-white/15 bg-white/[.03] text-xs text-white hover:bg-white/10 hover:text-white">{newsQuery.isFetching ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}</Button></div></div>
          {newsQuery.isFetching && <div className="mt-6 flex items-center gap-3 rounded-xl border border-white/10 bg-black/20 px-4 py-4 text-sm text-white/55"><Loader2 className="h-4 w-4 animate-spin text-[#d9fb63]" />Retrieving and normalizing public global-news context…</div>}
          {newsQuery.data?.mode === "unavailable" && <div className="mt-6 rounded-xl border border-[#ffbf69]/25 bg-[#ffbf69]/[.06] p-4 text-sm text-[#ffdfad]"><CircleAlert className="mr-2 inline h-4 w-4" />{newsQuery.data.error}</div>}
          {!newsQuery.isFetching && stories.length === 0 && <div className="mt-6 grid min-h-[160px] place-items-center rounded-2xl border border-dashed border-white/15 bg-black/20 px-5 text-center"><div><Globe2 className="mx-auto h-6 w-6 text-white/27" /><p className="mt-3 text-sm font-bold text-white/65">No retained stories in this session yet.</p><p className="mt-1 text-xs leading-5 text-white/38">Start a public discovery refresh; the application will show the original publisher path and retrieved time for each available result.</p></div></div>}
          {stories.length > 0 && <><div className="mt-5 flex flex-wrap items-center justify-between gap-3"><p className="mono text-[10px] text-white/38">{stories.length} normalized items in the current review batch</p><Button variant="outline" size="sm" onClick={retainSourceBatch} disabled={retainNews.isPending} className="h-8 border-[#d9fb63]/35 bg-[#d9fb63]/[.05] text-[11px] text-[#d9fb63] hover:bg-[#d9fb63]/10 hover:text-[#edffae]">{retainNews.isPending ? <Loader2 className="mr-1.5 h-3 w-3 animate-spin" /> : <Database className="mr-1.5 h-3 w-3" />}Retain source batch</Button></div><div className="mt-3 overflow-hidden rounded-2xl border border-white/10"><div className="hidden grid-cols-[1.1fr_1.8fr_.65fr_.75fr] gap-4 border-b border-white/10 px-4 py-3 mono text-[9px] uppercase tracking-[.16em] text-white/35 sm:grid"><span>Publisher</span><span>Evidence</span><span>Language</span><span>Action</span></div>{stories.slice(0, 8).map((story, index) => <div key={`${story.providerItemId}-${index}`} className="grid gap-3 border-b border-white/[.07] px-4 py-4 last:border-0 sm:grid-cols-[1.1fr_1.8fr_.65fr_.75fr] sm:items-center sm:gap-4"><div><p className="text-xs font-extrabold text-white/80">{story.publisher}</p><p className="mono mt-1 text-[10px] text-white/35">{story.publishedAt ? new Date(story.publishedAt).toLocaleString() : "time unavailable"}</p></div><a href={story.canonicalUrl} target="_blank" rel="noreferrer" className="group min-w-0"><p className="line-clamp-2 text-sm font-bold leading-5 text-white/74 transition group-hover:text-[#d9fb63]">{story.title}</p><p className="mono mt-1 text-[10px] text-white/33">Original source ↗</p></a><span className="mono text-[10px] text-white/45">{story.language ?? "—"}</span><Button variant="outline" size="sm" onClick={() => analyzeStory(story)} disabled={analyze.isPending} className="h-8 border-white/15 bg-transparent text-[11px] text-white/72 hover:bg-white/10 hover:text-white">{analyze.isPending && selectedStory?.canonicalUrl === story.canonicalUrl ? <Loader2 className="mr-1.5 h-3 w-3 animate-spin" /> : <BrainCircuit className="mr-1.5 h-3 w-3" />}Analyze</Button></div>)}</div></>}
          {isAuthenticated && <div className="mt-5 rounded-xl border border-dashed border-white/15 bg-black/20 p-4"><div className="flex items-center justify-between gap-4"><div><p className="mono text-[9px] uppercase tracking-[.16em] text-white/35">Persisted history</p><p className="mt-1 text-xs text-white/54">{retainedNews.data?.note ?? "Loading retained evidence records…"}</p></div><span className="mono text-[10px] text-[#d9fb63]">{retainedNews.data?.items.length ?? 0} retained</span></div>{retainedNews.data?.items.slice(0, 3).map(item => <a key={item.id} href={item.canonicalUrl} target="_blank" rel="noreferrer" className="mt-3 block border-t border-white/[.08] pt-3 text-xs font-bold text-white/70 hover:text-[#d9fb63]"><span className="mr-2 mono text-[9px] text-white/35">{item.publisher ?? "Publisher unavailable"}</span>{item.title}</a>)}</div>}
          {latestAnalysis && <div className="mt-5 rounded-2xl border border-[#d9fb63]/25 bg-[#d9fb63]/[.055] p-5"><div className="flex flex-wrap items-center justify-between gap-3"><span className="flex items-center gap-2 text-xs font-extrabold text-[#d9fb63]"><Sparkles className="h-4 w-4" />Structured evidence hypothesis</span><span className="mono text-[10px] text-white/45">{latestAnalysis.assetSymbols.join(", ") || "No verified symbol"} / {latestAnalysis.confidence}%</span></div><p className="mt-4 text-sm font-bold leading-6 text-white/85">{latestAnalysis.hypothesis}</p><div className="mt-4 grid gap-3 border-t border-white/10 pt-4 sm:grid-cols-2"><div><p className="mono text-[9px] uppercase tracking-[.15em] text-white/35">Evidence anchor</p><p className="mt-1 text-xs leading-5 text-white/58">{latestAnalysis.evidenceExcerpt}</p></div><div><p className="mono text-[9px] uppercase tracking-[.15em] text-white/35">Uncertainty / falsifier</p><p className="mt-1 text-xs leading-5 text-white/58">{latestAnalysis.uncertainty}</p></div></div></div>}
        </section>

        <section id="paper-book" className="mt-5 grid gap-5 xl:grid-cols-[1.45fr_.95fr]"><article className="rounded-[1.35rem] border border-white/10 bg-[#101210] p-5 sm:p-6"><div className="flex flex-wrap items-start justify-between gap-4"><div><div className="flex items-center gap-2"><WalletCards className="h-4 w-4 text-[#8da4ff]" /><p className="mono text-[10px] uppercase tracking-[.18em] text-white/38">Paper book</p></div><h2 className="mt-2 text-2xl font-extrabold tracking-[-.05em]">Simulation ledger</h2></div><span className="rounded-full border border-[#8da4ff]/30 bg-[#8da4ff]/10 px-3 py-1 mono text-[10px] text-[#b8c5ff]">NO EXECUTION ROUTE</span></div><div className="mt-6 grid gap-3 sm:grid-cols-3"><div className="rounded-xl bg-black/25 p-4"><p className="mono text-[10px] text-white/38">VIRTUAL EQUITY</p><p className="mt-2 text-2xl font-extrabold tracking-[-.06em]">${portfolio.data?.equity.toLocaleString() ?? "—"}</p><p className="mt-1 text-xs font-bold text-[#d9fb63]">+{portfolio.data?.returnPct ?? "—"}% simulated</p></div><div className="rounded-xl bg-black/25 p-4"><p className="mono text-[10px] text-white/38">VIRTUAL CASH</p><p className="mt-2 text-2xl font-extrabold tracking-[-.06em]">${portfolio.data?.virtualCash.toLocaleString() ?? "—"}</p><p className="mt-1 text-xs text-white/42">Starting allocation</p></div><div className="rounded-xl bg-black/25 p-4"><p className="mono text-[10px] text-white/38">WIN / LOSS</p><p className="mt-2 text-2xl font-extrabold tracking-[-.06em]">{portfolio.data ? `${portfolio.data.winLoss.wins} / ${portfolio.data.winLoss.losses}` : "—"}</p><p className="mt-1 text-xs text-white/42">Reported, not optimized</p></div></div><div className="mt-5 overflow-hidden rounded-xl border border-white/10"><div className="grid grid-cols-[1fr_.6fr_.6fr_.75fr] gap-2 border-b border-white/10 px-4 py-3 mono text-[9px] uppercase tracking-[.15em] text-white/35"><span>Position</span><span>Average</span><span>Mark</span><span>P&L</span></div>{portfolio.data?.positions.map(position => <div key={position.symbol} className="grid grid-cols-[1fr_.6fr_.6fr_.75fr] gap-2 px-4 py-4 text-xs"><div><strong>{position.symbol}</strong><span className="ml-2 mono text-[9px] text-white/35">{position.assetClass}</span></div><span className="mono text-white/58">${position.averagePrice.toLocaleString()}</span><span className="mono text-white/58">${position.markPrice.toLocaleString()}</span><span className={cn("mono font-bold", position.pnl >= 0 ? "text-[#d9fb63]" : "text-[#ff8b8b]")}>{position.pnl >= 0 ? "+" : ""}${position.pnl.toFixed(2)}</span></div>)}</div><p className="mt-4 text-xs leading-5 text-white/41">{portfolio.data?.label}</p></article>
          <aside id="methodology" className="rounded-[1.35rem] border border-white/10 bg-[#d9fb63] p-5 text-[#10120d] sm:p-6"><ShieldCheck className="h-6 w-6" /><p className="mono mt-5 text-[10px] font-bold uppercase tracking-[.18em] text-[#10120d]/62">Evaluation guardrail</p><h2 className="mt-2 text-2xl font-extrabold leading-none tracking-[-.06em]">Every signal is held to a point-in-time standard.</h2><div className="mt-6 space-y-4">{[["01", "Evidence cutoff", "Sources and observations are frozen before evaluation."], ["02", "Market window", "Paper-trade outcomes are only observed after the cutoff."], ["03", "Traceable result", "Win/loss and attribution show their methodology, not a promise."]].map(([number, title, copy]) => <div key={number} className="flex gap-3 border-t border-[#10120d]/15 pt-3"><span className="mono text-[10px] font-bold text-[#10120d]/55">{number}</span><div><p className="text-xs font-extrabold">{title}</p><p className="mt-1 text-xs leading-5 text-[#10120d]/62">{copy}</p></div></div>)}</div><a href="#sources" className="mt-7 inline-flex items-center text-xs font-extrabold underline decoration-[#10120d]/35 underline-offset-4">Inspect source ledger <ChevronRight className="ml-1 h-3.5 w-3.5" /></a></aside>
        </section>

        <section className="mt-5 grid gap-5 lg:grid-cols-2"><article className="rounded-[1.35rem] border border-white/10 bg-[#101210] p-5 sm:p-6"><div className="flex items-center gap-2"><SlidersHorizontal className="h-4 w-4 text-white/55" /><p className="mono text-[10px] uppercase tracking-[.18em] text-white/38">Provider settings</p></div><h2 className="mt-2 text-xl font-extrabold tracking-[-.045em]">Connection status, not hidden credentials.</h2><div className="mt-5 space-y-3">{Object.entries(status.data ?? {}).map(([key, value]) => <div key={key} className="flex gap-3 rounded-xl border border-white/10 bg-black/20 p-3"><StatusDot status={value.status} /><div><p className="text-xs font-extrabold capitalize">{key.replace(/([A-Z])/g, " $1")}</p><p className="mt-1 text-xs leading-5 text-white/44">{value.detail}</p></div></div>)}</div></article><article className="relative overflow-hidden rounded-[1.35rem] border border-white/10 bg-[#101210] p-5 sm:p-6"><div className="absolute right-4 top-4 opacity-20"><Database className="h-20 w-20" /></div><div className="relative"><div className="flex items-center gap-2"><Database className="h-4 w-4 text-[#ffbf69]" /><p className="mono text-[10px] uppercase tracking-[.18em] text-white/38">Airtable sync boundary</p></div><h2 className="mt-2 max-w-sm text-xl font-extrabold tracking-[-.045em]">Retain sources without making a spreadsheet your truth engine.</h2><p className="mt-3 max-w-md text-sm leading-6 text-white/48">When authorization is restored, retained records can sync with source fingerprints, timestamps, canonical URLs, and connection audit status. Credentials are never written into the dashboard code.</p><div className="mt-5 flex items-center gap-2 text-xs font-bold text-[#ffdfad]"><CircleAlert className="h-4 w-4" />Authorization needs reconnection</div></div></article></section>

        <footer className="flex flex-col gap-3 px-1 pb-2 pt-10 text-xs leading-5 text-white/37 sm:flex-row sm:items-center sm:justify-between"><p>MarketSignal OS is an evidence workspace and paper-trading simulator. It does not provide personalized investment advice, guarantee predictions, or place real-money orders.</p><p className="mono shrink-0 text-[10px]">UTC · PROVENANCE FIRST · v0.1</p></footer>
      </main>
    </div>
  );
}
