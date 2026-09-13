import { ArrowDownRight, ArrowUpRight, Check, GitBranch, X } from "lucide-react";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { lazy, Suspense, useEffect, useMemo, useState } from "react";

const SpaceScene = lazy(() => import("./SpaceScene"));

type Range = { minimum: number; median: number; maximum: number };
type Evidence = {
  generated_by_commit: string;
  quantity_legend: string[];
  headline: { physical_inference_gate: string; falsification_suite: string; falsification_passed: number; falsification_directional_total: number; null_false_positive_rate: number; conditional_science_gate: string };
  missions: Array<{ id: string; name: string; region: string; detector: string; status: string; summary: string }>;
  hst_epochs: Array<{ year: number; parallel_fraction_mean: number }>;
  environment_years: Array<{ year: number; particle_fluence_sum: number | null; quantity: string }>;
  forecast_scores: Record<string, { rmse: number; nlpd: number }>;
  historical_primary: { gate: string; rmse: number; nlpd: number };
  science_bias: { quantity: string; result_class: string; scenario_count: number; paired_responses: number; metrics: Record<string, Range>; claim_boundary: Record<string, string> };
  falsification_tests: Array<{ id: string; name: string; status: string }>;
  provenance: Record<string, string>;
};

const nav = [["01", "Field", "environment"], ["02", "Instruments", "detector"], ["03", "Time", "timeline"], ["04", "Impact", "impact"], ["05", "Verdict", "evidence"]];

const instrumentSpecs = {
  hst: {
    kicker: "ACS/WFC · focal plane",
    facts: [["Array", "2 × SITe CCD"], ["Active pixels", "4096 × 2048 / CCD"], ["Pixel pitch", "15 × 15 µm"], ["Sampling", "≈ 0.05″ / pixel"], ["Field", "202″ × 202″"], ["Readout", "4 amplifier quadrants"]],
    note: "The rendered chip gap is exaggerated for legibility; the physical separation is equivalent to approximately 50 pixels.",
    source: "STScI ACS Instrument Handbook",
    url: "https://hst-docs.stsci.edu/acsihb/chapter-4-detector-performance/4-2-the-ccds",
  },
  gaia: {
    kicker: "Gaia · scanning focal plane",
    facts: [["Array", "106 CCD / 938 Mpix"], ["Structure", "7 rows × 17 strips"], ["CCD format", "4500 × 1966 pixels"], ["Pixel pitch", "10 × 30 µm · AL × AC"], ["Sampling", "58.9 × 176.8 mas"], ["TDI", "982.8 µs / line"]],
    note: "Functional allocation is reproduced: 14 SM, 62 AF, 14 BP/RP, 12 RVS and four metrology CCDs. The transit animation follows the published along-scan direction.",
    source: "Gaia Collaboration, A&A 595 A1",
    url: "https://doi.org/10.1051/0004-6361/201629272",
  },
  euclid: {
    kicker: "Euclid VIS · detector plane",
    facts: [["Array", "6 × 6 CCD273-84"], ["CCD format", "4096 × 4132 pixels"], ["Pixel pitch", "12 × 12 µm"], ["Sampling", "0.1″ / pixel"], ["Field", "0.57 deg² / 609 Mpix"], ["Readout", "4 nodes / CCD · 144 total"]],
    note: "Every device is shown with four quadrants and corner readout nodes. Inter-device gaps are exaggerated so the mosaic remains readable.",
    source: "Euclid Collaboration, VIS instrument",
    url: "https://doi.org/10.1051/0004-6361/202450996",
  },
} as const;

function Tag({ children, tone = "neutral" }: { children: React.ReactNode; tone?: string }) {
  return <span className={`tag tag-${tone}`}>{children}</span>;
}

function Detector({ mission }: { mission: string }) {
  if (mission === "euclid") return <div className="detector-art euclid-art" aria-label="Euclid VIS focal plane with 36 four-quadrant CCD273-84 detectors">
    <div className="diagram-axis axis-y">6 DEVICES / CROSS-SCAN</div><div className="diagram-axis axis-x">6 DEVICES / ALONG-SCAN</div>
    <div className="euclid-mosaic">{Array.from({ length: 36 }, (_, i) => <div className={`euclid-ccd ${i === 14 ? "active-ccd" : ""}`} key={i}><span className="q q1"/><span className="q q2"/><span className="q q3"/><span className="q q4"/><i className="node n1"/><i className="node n2"/><i className="node n3"/><i className="node n4"/><b>{String(i + 1).padStart(2, "0")}</b></div>)}</div>
    <div className="euclid-callout"><b>CCD 15 / QUADRANT READOUT</b><span>4 corner nodes operate synchronously</span></div>
  </div>;

  if (mission === "gaia") {
    const columns = ["AUX", "SM1", "SM2", "AF1", "AF2", "AF3", "AF4", "AF5", "AF6", "AF7", "AF8", "AF9", "BP", "RP", "RVS1", "RVS2", "RVS3"];
    const cell = (column: string, row: number) => {
      if (column === "AUX") return ({ 0: "wfs", 2: "bam", 4: "bam" } as Record<number, string>)[row] ?? "empty";
      if (column.startsWith("SM")) return "sm";
      if (column === "AF9" && row === 3) return "wfs";
      if (column.startsWith("AF")) return "af";
      if (column === "BP") return "bp";
      if (column === "RP") return "rp";
      if (column.startsWith("RVS")) return row <= 3 ? "rvs" : "empty";
      return "empty";
    };
    return <div className="detector-art gaia-art" aria-label="Gaia focal plane functional layout with seven rows and 17 strips">
      <div className="gaia-labels">{columns.map(label => <span key={label}>{label}</span>)}</div>
      <div className="gaia-accurate">{Array.from({ length: 7 }, (_, row) => columns.map(column => <span key={`${column}-${row}`} className={cell(column, row)} title={`${column} · row ${7 - row}`}><i>{7 - row}</i></span>))}<div className="gaia-transit"><i/>STAR TRANSIT / ALONG-SCAN</div></div>
      <div className="gaia-legend"><span className="sm">SM · 14</span><span className="af">AF · 62</span><span className="bp">BP · 7</span><span className="rp">RP · 7</span><span className="rvs">RVS · 12</span><span className="wfs">METROLOGY · 4</span></div>
    </div>;
  }

  return <div className="detector-art hst-art" aria-label="HST ACS WFC two-chip, four-amplifier focal-plane layout">
    <div className="hst-scale"><span>4096 ACTIVE PIXELS</span><i/><span>15 µm PITCH</span></div>
    <div className="hst-accurate">
      <div className="hst-chip wfc1"><span className="amp amp-a">A</span><span className="amp amp-b">B</span><div className="chip-half"><b>WFC1 / A</b><i>2048 × 2048</i></div><div className="chip-half"><b>WFC1 / B</b><i>2048 × 2048</i></div><div className="serial-register top"/><i className="charge c1"/><i className="charge c2"/></div>
      <div className="chip-gap"><span>≈ 50 PIXEL-EQUIVALENT GAP</span></div>
      <div className="hst-chip wfc2"><span className="amp amp-c">C</span><span className="amp amp-d">D</span><div className="serial-register bottom"/><div className="chip-half"><b>WFC2 / C</b><i>2048 × 2048</i></div><div className="chip-half"><b>WFC2 / D</b><i>2048 × 2048</i></div><i className="charge c3"/><i className="charge c4"/></div>
    </div>
    <div className="transfer-key"><span><i className="parallel-arrow"/>Parallel transfer</span><span><i className="serial-arrow"/>Serial register → amplifier</span></div>
  </div>;
}

function Trend({ rows }: { rows: Evidence["hst_epochs"] }) {
  const width = 900, height = 310, left = 72, right = 34, top = 42, bottom = 54;
  const values = rows.map(r => r.parallel_fraction_mean);
  const min = Math.min(...values) * .94, max = Math.max(...values) * 1.03;
  const points = rows.map((row, index) => ({ ...row, x: left + index / (rows.length - 1) * (width - left - right), y: top + (max - row.parallel_fraction_mean) / (max - min) * (height - top - bottom) }));
  const polyline = points.map(p => `${p.x},${p.y}`).join(" ");
  const area = `${left},${height - bottom} ${polyline} ${width - right},${height - bottom}`;
  return <figure className="chart-wrap">
    <div className="chart-caption"><span>ACS/WFC PARALLEL TRAIL FRACTION</span><strong>2003—2024</strong></div>
    <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-labelledby="trend-title trend-desc">
      <title id="trend-title">Observed Hubble parallel trailing measurement by epoch</title><desc id="trend-desc">The replicated detector observable rises overall from 2003 through 2024.</desc>
      <defs><linearGradient id="trend-area" x1="0" y1="0" x2="0" y2="1"><stop stopColor="#f05a2a" stopOpacity=".24"/><stop offset="1" stopColor="#f05a2a" stopOpacity="0"/></linearGradient></defs>
      {[0, .25, .5, .75, 1].map(t => <line key={t} x1={left} y1={top + t * (height - top - bottom)} x2={width - right} y2={top + t * (height - top - bottom)} className="grid-line" />)}
      <polygon points={area} className="trend-area" /><polyline points={polyline} className="trend-line" />
      {points.map((p, i) => <g key={p.year}><line x1={p.x} y1={p.y} x2={p.x} y2={height - bottom} className="point-stem"/><circle cx={p.x} cy={p.y} r={i === points.length - 1 ? 7 : 5} className="trend-point"/><text x={p.x} y={height - 21} textAnchor="middle" className="year-label">{p.year}</text>{(i === 0 || i === points.length - 1) && <text x={p.x} y={p.y - 15} textAnchor={i ? "end" : "start"} className="value-label">{p.parallel_fraction_mean.toFixed(4)}</text>}</g>)}
    </svg>
  </figure>;
}

function ImpactVisual({ mode }: { mode: string }) {
  const stars = useMemo(() => Array.from({ length: 42 }, (_, i) => ({ x: (i * 83) % 720 + 10, y: (i * 47) % 330 + 10, r: i % 7 === 0 ? 1.5 : .7, o: .25 + (i % 5) * .12 })), []);
  return <svg className="impact-visual" viewBox="0 0 760 360" role="img" aria-label={`${mode} conditional simulated galaxy image`}>
    <defs><radialGradient id="galaxy"><stop offset="0" stopColor="#fff8e8"/><stop offset=".18" stopColor="#ffc786" stopOpacity=".98"/><stop offset=".46" stopColor="#bc87b2" stopOpacity=".64"/><stop offset="1" stopColor="#191c2a" stopOpacity="0"/></radialGradient><filter id="soft"><feGaussianBlur stdDeviation="8"/></filter><linearGradient id="trail" x1="0" y1="0" x2="0" y2="1"><stop stopColor="#f09a70" stopOpacity=".38"/><stop offset="1" stopColor="#f09a70" stopOpacity="0"/></linearGradient></defs>
    <rect width="760" height="360" fill="#090b10" />{stars.map((s, i) => <circle key={i} cx={s.x} cy={s.y} r={s.r} fill="#f4ead6" opacity={s.o}/>) }
    <g transform="translate(380 168) rotate(-24)"><ellipse rx="108" ry="59" fill="url(#galaxy)" filter="url(#soft)"/><ellipse rx="72" ry="28" fill="url(#galaxy)"/><ellipse rx="24" ry="9" fill="#fff9e8" opacity=".86"/></g>
    {mode === "damaged" && <g>{Array.from({ length: 12 }, (_, i) => <rect key={i} x={322 + i * 9} y={190 + i * 5} width={82 - i * 4} height="9" rx="5" fill="url(#trail)" opacity={.8 - i * .045}/>)}</g>}
    <g className="reticle"><line x1="380" y1="70" x2="380" y2="115"/><line x1="380" y1="221" x2="380" y2="266"/><line x1="260" y1="168" x2="320" y2="168"/><line x1="440" y1="168" x2="500" y2="168"/><circle cx="380" cy="168" r="74"/></g>
    <text x="24" y="31" className="plate-label">CONDITIONAL RESPONSE / {mode.toUpperCase()}</text><text x="736" y="334" textAnchor="end" className="plate-label">FIELD 07 · SCALE 0.1″</text>
    {mode === "corrected" && <g><rect x="118" y="286" width="524" height="42" className="warning-box"/><text x="380" y="312" textAnchor="middle" className="svg-warning">NO VALIDATED MISSION CTI STATE · CORRECTION WITHHELD</text></g>}
  </svg>;
}

export default function App() {
  const [data, setData] = useState<Evidence | null>(null), [error, setError] = useState("");
  const [mission, setMission] = useState("euclid"), [impact, setImpact] = useState("clean");
  const reduceMotion = useReducedMotion() ?? false;
  useEffect(() => { fetch(`${import.meta.env.BASE_URL}data/evidence.json`).then(r => { if (!r.ok) throw new Error(`${r.status}`); return r.json(); }).then(setData).catch(() => setError("Evidence JSON could not be loaded. Rebuild it with scripts/export_web_data.py.")); }, []);
  const selected = useMemo(() => data?.missions.find(item => item.id === mission), [data, mission]);
  const selectedSpec = instrumentSpecs[mission as keyof typeof instrumentSpecs];
  if (error) return <main className="load-state"><h1>LATTICE</h1><p>{error}</p></main>;
  if (!data) return <main className="load-state" aria-live="polite"><p>Opening evidence dossier…</p></main>;

  return <>
    <a className="skip-link" href="#main">Skip to research</a>
    <header className="site-header">
      <a className="wordmark" href="#top" aria-label="LATTICE home"><b>L</b><span>LATTICE</span></a>
      <nav aria-label="Research sections">{nav.map(([n, label, id]) => <a key={id} href={`#${id}`}><small>{n}</small>{label}</a>)}</nav>
      <a className="repository-link" href="https://github.com/Biswajit1999/lattice-radiation-twin"><GitBranch aria-hidden="true" size={15}/>Source</a>
    </header>

    <main id="main">
      <section className="hero" id="top">
        <div className="hero-index"><span>RESEARCH DOSSIER</span><b>01—25</b><small>FINAL BOUNDED RELEASE</small></div>
        <motion.div className="hero-copy" initial={reduceMotion ? false : { opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: .65 }}>
          <p className="eyebrow">Astronomical detector research / HST · Gaia · Euclid</p>
          <h1>Radiation leaves a trace.<em>Causation leaves a harder one.</em></h1>
          <p className="lede">LATTICE follows detector damage across missions, then tests whether the space environment actually explains it. The answer is preserved even when it fails.</p>
          <a className="text-link" href="#evidence">Read the verdict <ArrowDownRight aria-hidden="true" /></a>
        </motion.div>
        <aside className="verdict-card" aria-label="Current scientific verdict">
          <div className="verdict-top"><span>ATTRIBUTION GATE</span><b>NOT ESTABLISHED</b></div>
          <strong>{data.headline.falsification_passed}<i>/</i>{data.headline.falsification_directional_total}</strong>
          <p>directional falsification tests passed</p>
          <div className="verdict-rule" />
          <dl><div><dt>Physical inference</dt><dd>{data.headline.physical_inference_gate}</dd></div><div><dt>Image response</dt><dd>{data.headline.conditional_science_gate}</dd></div><div><dt>Null false-positive</dt><dd>{(data.headline.null_false_positive_rate * 100).toFixed(0)}%</dd></div></dl>
        </aside>
        <div className="hero-ledger"><div><b>48</b><span>HST exposures</span></div><div><b>432</b><span>conditional scenarios</span></div><div><b>11</b><span>falsification tests</span></div><div><b>3</b><span>mission architectures</span></div></div>
      </section>

      <section id="environment" className="section field-section">
        <div className="section-number">01</div><div className="section-copy"><p className="eyebrow">The field</p><h2>One stellar source.<br/><em>Two detector environments.</em></h2><p className="section-intro">Hubble crosses low Earth orbit. Gaia and Euclid occupy halo orbits around Sun–Earth L2. The plate communicates mission geometry; positions and particle paths remain schematic.</p></div>
        <div className="scene-shell"><Suspense fallback={<div className="space-stage load-state">Assembling field plate…</div>}><SpaceScene reduceMotion={reduceMotion}/></Suspense></div>
        <div className="mission-register">{data.missions.map((item, i) => <article key={item.id}><span className="register-index">0{i + 1}</span><div><Tag tone={item.status.toLowerCase()}>{item.status}</Tag><small>{item.region}</small></div><h3>{item.name}</h3><p>{item.summary}</p><footer>{item.detector}</footer></article>)}</div>
      </section>

      <section id="detector" className="dark-section detector-section"><div className="dark-inner">
        <div className="section-number">02</div><div className="section-copy"><p className="eyebrow">Instrument anatomy</p><h2>Geometry changes.<br/><em>The physics cannot be copied.</em></h2><p className="section-intro">Each mission keeps its own focal-plane architecture. Selection changes the instrument record, not the evidence class.</p></div>
        <div className="instrument-tabs" role="group" aria-label="Select instrument">{data.missions.map((item, i) => <button key={item.id} type="button" aria-pressed={mission === item.id} onClick={() => setMission(item.id)}><span>0{i + 1}</span>{item.name.split(" ")[0]}</button>)}</div>
        <AnimatePresence mode="wait"><motion.div key={mission} className="detector-view" initial={reduceMotion ? false : { opacity: 0, x: 24 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -14 }} transition={{ duration: .3 }}><Detector mission={mission}/><div className="instrument-record"><span>ACTIVE RECORD / {mission.toUpperCase()}</span><Tag tone={selected?.status.toLowerCase()}>{selected?.status}</Tag><h3>{selected?.name}</h3><p>{selected?.summary}</p><div className="spec-kicker">{selectedSpec.kicker}</div><dl className="spec-list">{selectedSpec.facts.map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl><p className="geometry-note">{selectedSpec.note}</p><a className="source-link" href={selectedSpec.url}>Primary specification <ArrowUpRight aria-hidden="true" size={14}/><span>{selectedSpec.source}</span></a></div></motion.div></AnimatePresence>
      </div></section>

      <section id="timeline" className="section timeline-section">
        <div className="section-number">03</div><div className="section-copy"><p className="eyebrow">Observed time</p><h2>Twenty-one years,<br/><em>eight historical anchors.</em></h2><p className="section-intro">Thirty-two replication measurements show the HST detector observable rising overall. Environment records become proxy-based after the archive transition.</p></div>
        <div className="timeline-note"><Tag tone="observed">OBSERVED</Tag><p>Trend is descriptive.<br/>Causal attribution failed.</p></div>
        <Trend rows={data.hst_epochs}/>
        <details><summary>Open numerical epoch table <ArrowDownRight aria-hidden="true" size={16}/></summary><table><thead><tr><th>Year</th><th>Mean parallel trail fraction</th></tr></thead><tbody>{data.hst_epochs.map(row => <tr key={row.year}><td>{row.year}</td><td>{row.parallel_fraction_mean.toFixed(5)}</td></tr>)}</tbody></table></details>
      </section>

      <section id="impact" className="section impact-section">
        <div className="section-number">04</div><div className="section-copy"><p className="eyebrow">Conditional consequence</p><h2>What damage could do<br/><em>to a measured galaxy.</em></h2><p className="section-intro">Fixed-template statistics pass across 432 Euclid scenarios. These are sensitivity experiments, not measurements of Euclid’s current detector state.</p></div>
        <div className="impact-switch" role="group" aria-label="Select simulated image state">{["clean", "damaged", "corrected"].map((item, i) => <button key={item} type="button" aria-pressed={impact === item} onClick={() => setImpact(item)}><span>0{i + 1}</span>{item}</button>)}</div>
        <div className="impact-frame"><AnimatePresence mode="wait"><motion.div key={impact} initial={reduceMotion ? false : { opacity: 0, scale: .99 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }}><ImpactVisual mode={impact}/></motion.div></AnimatePresence></div>
        <div className="metric-strip"><div><span>Centroid response / median</span><strong>{data.science_bias.metrics.centroid_y_mas.median.toFixed(3)}<small>mas</small></strong></div><div><span>Weighted flux / median</span><strong>{data.science_bias.metrics.flux_fraction.median.toExponential(2)}</strong></div><div><span>Finite paired responses</span><strong>{data.science_bias.paired_responses}<small>/ 32</small></strong></div></div>
      </section>

      <section id="evidence" className="verdict-section"><div className="verdict-inner">
        <div className="section-number">05</div><div className="section-copy"><p className="eyebrow">The verdict</p><h2>The failed suite<br/><em>is the main result.</em></h2><p className="section-intro">Calendar time remains the stronger practical baseline. Five controls pass; six attribution and calibration checks fail.</p></div>
        <div className="verdict-score"><strong>{data.headline.falsification_passed}</strong><span>of {data.headline.falsification_directional_total}<br/>tests passed</span></div>
        <div className="evidence-list">{data.falsification_tests.map((test, i) => <div key={test.id} className={test.status.toLowerCase()}><span>{String(i + 1).padStart(2, "0")}</span>{test.status === "PASS" ? <Check aria-hidden="true"/> : <X aria-hidden="true"/>}<p>{test.name.replace(`${test.id}_`, "").replaceAll("_", " ")}</p><b>{test.status}</b></div>)}</div>
        <aside className="provenance"><div><p>PROVENANCE / FINAL RELEASE</p><code>{data.generated_by_commit}</code></div><a href="https://github.com/Biswajit1999/lattice-radiation-twin">Inspect repository <ArrowUpRight aria-hidden="true"/></a><dl>{Object.entries(data.provenance).map(([name, hash]) => <div key={name}><dt>{name.replaceAll("_", " ")}</dt><dd title={hash}>{hash.slice(0, 12)}…</dd></div>)}</dl></aside>
      </div></section>
    </main>
    <footer className="site-footer"><div className="footer-mark"><b>L</b><span>LATTICE<small>Latent Astronomical Trap Tracking & Inference<br/>across Cosmic Environments</small></span></div><div><p>Research and authorship</p><strong>Biswajit Jana</strong></div><div><p>Release principle</p><strong>Every claim remains traceable.</strong></div><a href="#top">Return to index <ArrowUpRight aria-hidden="true" size={16}/></a></footer>
  </>;
}
