import { Activity, Database, GitCommit, ShieldAlert } from "lucide-react";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { lazy, Suspense, useEffect, useMemo, useState } from "react";

const SpaceScene = lazy(() => import("./SpaceScene"));

type Range = { minimum: number; median: number; maximum: number };
type Evidence = {
  generated_by_commit: string;
  quantity_legend: string[];
  headline: {
    physical_inference_gate: string;
    falsification_suite: string;
    falsification_passed: number;
    falsification_directional_total: number;
    null_false_positive_rate: number;
    conditional_science_gate: string;
  };
  missions: Array<{ id: string; name: string; region: string; detector: string; status: string; summary: string }>;
  hst_epochs: Array<{ year: number; parallel_fraction_mean: number }>;
  environment_years: Array<{ year: number; particle_fluence_sum: number | null; quantity: string }>;
  forecast_scores: Record<string, { rmse: number; nlpd: number }>;
  historical_primary: { gate: string; rmse: number; nlpd: number };
  science_bias: { quantity: string; result_class: string; scenario_count: number; paired_responses: number; metrics: Record<string, Range>; claim_boundary: Record<string, string> };
  falsification_tests: Array<{ id: string; name: string; status: string }>;
  provenance: Record<string, string>;
};

const nav = ["environment", "detector", "timeline", "impact", "evidence"];

function Tag({ children, tone = "neutral" }: { children: React.ReactNode; tone?: string }) {
  return <span className={`tag tag-${tone}`}>{children}</span>;
}

function Trend({ rows }: { rows: Evidence["hst_epochs"] }) {
  const width = 760, height = 240, pad = 28;
  const values = rows.map((row) => row.parallel_fraction_mean);
  const min = Math.min(...values), max = Math.max(...values);
  const points = rows.map((row, index) => {
    const x = pad + (index / (rows.length - 1)) * (width - pad * 2);
    const y = height - pad - ((row.parallel_fraction_mean - min) / (max - min)) * (height - pad * 2);
    return { ...row, x, y };
  });
  return (
    <div className="chart-wrap">
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-labelledby="trend-title trend-desc">
        <title id="trend-title">Observed HST parallel trailing measurement by epoch</title>
        <desc id="trend-desc">The replicated detector observable rises overall from 2003 through 2024.</desc>
        <line x1={pad} y1={height - pad} x2={width - pad} y2={height - pad} className="axis" />
        <polyline points={points.map((point) => `${point.x},${point.y}`).join(" ")} className="trend-line" />
        {points.map((point) => <circle key={point.year} cx={point.x} cy={point.y} r="5" className="trend-point" />)}
        {points.filter((_, index) => index % 2 === 0 || index === points.length - 1).map((point) => (
          <text key={point.year} x={point.x} y={height - 7} textAnchor="middle">{point.year}</text>
        ))}
      </svg>
    </div>
  );
}

function Detector({ mission }: { mission: string }) {
  if (mission === "euclid") return <div className="ccd-grid" aria-label="Schematic 6 by 6 Euclid VIS CCD mosaic">{Array.from({ length: 36 }, (_, index) => <span key={index} />)}</div>;
  if (mission === "gaia") return <div className="gaia-plane" aria-label="Schematic Gaia focal plane">{Array.from({ length: 21 }, (_, index) => <span key={index} />)}</div>;
  return <div className="hst-plane" aria-label="Schematic two chip HST ACS WFC detector"><span>WFC1</span><span>WFC2</span></div>;
}

function ImpactVisual({ mode }: { mode: string }) {
  return (
    <svg className="impact-visual" viewBox="0 0 580 260" role="img" aria-label={`${mode} simulated galaxy image`}>
      <defs><radialGradient id="galaxy"><stop offset="0" stopColor="#ecf6f8"/><stop offset="0.3" stopColor="#71bdd1" stopOpacity=".85"/><stop offset="1" stopColor="#183643" stopOpacity="0"/></radialGradient></defs>
      <rect width="580" height="260" fill="#071018" />
      <ellipse cx="270" cy="120" rx="62" ry="38" transform="rotate(24 270 120)" fill="url(#galaxy)" />
      {mode === "damaged" && Array.from({ length: 7 }, (_, index) => <ellipse key={index} cx="270" cy={139 + index * 11} rx={38 - index * 3} ry="10" fill="#71bdd1" opacity={0.18 - index * .018} />)}
      {mode === "corrected" && <text x="290" y="222" textAnchor="middle" className="svg-warning">Correction unavailable: no validated mission CTI state</text>}
    </svg>
  );
}

export default function App() {
  const [data, setData] = useState<Evidence | null>(null);
  const [error, setError] = useState("");
  const [mission, setMission] = useState("euclid");
  const [impact, setImpact] = useState("clean");
  const reduceMotion = useReducedMotion() ?? false;
  useEffect(() => {
    fetch(`${import.meta.env.BASE_URL}data/evidence.json`)
      .then((response) => { if (!response.ok) throw new Error(`${response.status}`); return response.json(); })
      .then(setData)
      .catch(() => setError("Evidence JSON could not be loaded. Rebuild it with scripts/export_web_data.py."));
  }, []);
  const selectedMission = useMemo(() => data?.missions.find((item) => item.id === mission), [data, mission]);
  if (error) return <main className="load-state"><h1>LATTICE</h1><p>{error}</p></main>;
  if (!data) return <main className="load-state" aria-live="polite"><p>Loading versioned evidence…</p></main>;
  return (
    <>
      <header className="site-header">
        <a className="wordmark" href="#top" aria-label="LATTICE home">LATTICE <span>β</span></a>
        <nav aria-label="Primary navigation">{nav.map((item) => <a key={item} href={`#${item}`}>{item}</a>)}</nav>
        <a className="repository-link" href="https://github.com/Biswajit1999/lattice-radiation-twin">Repository</a>
      </header>
      <main id="main">
        <section className="hero" id="top">
          <div className="hero-copy">
            <p className="eyebrow">Cross-mission CCD radiation inference · research build</p>
            <h1>A detector twin that keeps failed hypotheses visible.</h1>
            <p className="lede">LATTICE connects observed HST detector change, space-environment proxies, constrained Gaia evidence and conditional Euclid simulations—without turning correlation into radiation attribution.</p>
            <div className="hero-actions"><a className="button primary" href="#evidence">Inspect evidence</a><a className="button" href="#environment">Explore schematic</a></div>
          </div>
          <aside className="gate-panel" aria-label="Current scientific gate status">
            <div><ShieldAlert aria-hidden="true"/><span>Physical inference</span><strong>{data.headline.physical_inference_gate}</strong></div>
            <div><Activity aria-hidden="true"/><span>Falsification suite</span><strong>{data.headline.falsification_passed}/{data.headline.falsification_directional_total} pass</strong></div>
            <div><Database aria-hidden="true"/><span>Conditional image response</span><strong>{data.headline.conditional_science_gate}</strong></div>
            <p>Null false-positive rate <b>{(data.headline.null_false_positive_rate * 100).toFixed(0)}%</b> · frozen maximum 10%</p>
          </aside>
        </section>

        <section id="environment" className="section split">
          <div><p className="eyebrow">A · Space environment</p><h2>Three missions, two radiation regions</h2><p className="section-intro">Positions are schematic. HST occupies low Earth orbit; Gaia and Euclid operate around Sun–Earth L2. Particle transport is not reconstructed.</p><Suspense fallback={<div className="space-stage load-state">Loading 3D schematic…</div>}><SpaceScene reduceMotion={reduceMotion} /></Suspense></div>
          <div className="mission-list">{data.missions.map((item) => <article key={item.id}><div><Tag tone={item.status.toLowerCase()}>{item.status}</Tag><span>{item.region}</span></div><h3>{item.name}</h3><p>{item.summary}</p><small>{item.detector}</small></article>)}</div>
        </section>

        <section id="detector" className="section detector-section">
          <p className="eyebrow">B · Detector twin</p><div className="section-heading"><div><h2>Architecture stays mission specific</h2><p className="section-intro">Selectable layouts communicate detector geometry. They do not imply shared CTI amplitude.</p></div><div className="segmented" role="group" aria-label="Select instrument">{data.missions.map((item) => <button key={item.id} type="button" aria-pressed={mission === item.id} onClick={() => setMission(item.id)}>{item.name.split(" ")[0]}</button>)}</div></div>
          <AnimatePresence mode="wait"><motion.div key={mission} className="detector-view" initial={reduceMotion ? false : { opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}><Detector mission={mission}/><div><Tag tone={selectedMission?.status.toLowerCase()}>{selectedMission?.status}</Tag><h3>{selectedMission?.name}</h3><p>{selectedMission?.summary}</p><dl><dt>Detector</dt><dd>{selectedMission?.detector}</dd><dt>Environment</dt><dd>{selectedMission?.region}</dd></dl></div></motion.div></AnimatePresence>
        </section>

        <section id="timeline" className="section">
          <p className="eyebrow">C · Time machine</p><div className="section-heading"><div><h2>Observed detector evolution, with limits</h2><p className="section-intro">Eight historical anchors summarize 32 replication measurements. Environment series are observed through early 2020 and proxy based after the archive transition.</p></div><Tag tone="observed">OBSERVED</Tag></div>
          <Trend rows={data.hst_epochs}/><details><summary>Accessible epoch table</summary><table><thead><tr><th>Year</th><th>Mean parallel trail fraction</th></tr></thead><tbody>{data.hst_epochs.map((row) => <tr key={row.year}><td>{row.year}</td><td>{row.parallel_fraction_mean.toFixed(5)}</td></tr>)}</tbody></table></details>
        </section>

        <section id="impact" className="section impact-section">
          <p className="eyebrow">D · Science impact</p><div className="section-heading"><div><h2>Controlled image response</h2><p className="section-intro">Fixed-template statistics pass for 432 conditional Euclid scenarios. Captured fractions are sensitivity settings, not measured mission state.</p></div><Tag tone="simulated">SIMULATED</Tag></div>
          <div className="segmented" role="group" aria-label="Select image state">{["clean", "damaged", "corrected"].map((item) => <button key={item} type="button" aria-pressed={impact === item} onClick={() => setImpact(item)}>{item}</button>)}</div><AnimatePresence mode="wait"><motion.div key={impact} initial={reduceMotion ? false : { opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}><ImpactVisual mode={impact}/></motion.div></AnimatePresence>
          <div className="metric-strip"><div><span>Median centroid response</span><strong>{data.science_bias.metrics.centroid_y_mas.median.toFixed(3)} mas</strong></div><div><span>Weighted flux response</span><strong>{data.science_bias.metrics.flux_fraction.median.toExponential(2)}</strong></div><div><span>Paired responses</span><strong>{data.science_bias.paired_responses}/32</strong></div></div>
        </section>

        <section id="evidence" className="section evidence-section">
          <p className="eyebrow">E · Evidence</p><div className="section-heading"><div><h2>The failed suite is the main result</h2><p className="section-intro">Calendar time remains the stronger practical baseline. Five controls pass; six attribution and calibration checks fail.</p></div><Tag tone="fail">FAIL</Tag></div>
          <div className="evidence-grid"><div className="test-table"><table><thead><tr><th>Test</th><th>Status</th></tr></thead><tbody>{data.falsification_tests.map((test) => <tr key={test.id}><td>{test.name.replace(`${test.id}_`, "").replaceAll("_", " ")}</td><td><Tag tone={test.status.toLowerCase()}>{test.status}</Tag></td></tr>)}</tbody></table></div><aside className="provenance"><GitCommit aria-hidden="true"/><h3>Provenance panel</h3><p>Generated from commit</p><code>{data.generated_by_commit}</code><dl>{Object.entries(data.provenance).map(([name, hash]) => <div key={name}><dt>{name.replaceAll("_", " ")}</dt><dd title={hash}>{hash.slice(0, 12)}…</dd></div>)}</dl></aside></div>
        </section>
      </main>
      <footer><div><span className="wordmark">LATTICE</span><p>Latent Astronomical Trap Tracking & Inference across Cosmic Environments</p></div><div><p>Author · Biswajit Jana</p><p>Every number is linked to a versioned result.</p></div></footer>
    </>
  );
}
