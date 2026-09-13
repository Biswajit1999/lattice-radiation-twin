import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { Pause, Play, RotateCcw } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { AdditiveBlending, BackSide } from "three";
import type { Group, Mesh, Points } from "three";

const HOME: [number, number, number] = [0, 1.2, 10.4];

function CameraKeys({ reset }: { reset: number }) {
  const { camera } = useThree();
  useEffect(() => { camera.position.set(...HOME); camera.lookAt(0, 0, 0); }, [camera, reset]);
  useEffect(() => {
    const move = (event: KeyboardEvent) => {
      if (!["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "+", "-", "r", "R", "0"].includes(event.key)) return;
      const target = event.target as HTMLElement;
      if (["INPUT", "TEXTAREA", "SELECT"].includes(target.tagName)) return;
      event.preventDefault();
      if (["r", "R", "0"].includes(event.key)) camera.position.set(...HOME);
      if (event.key === "ArrowLeft") camera.position.x -= .35;
      if (event.key === "ArrowRight") camera.position.x += .35;
      if (event.key === "ArrowUp") camera.position.y += .35;
      if (event.key === "ArrowDown") camera.position.y -= .35;
      if (event.key === "+") camera.position.z = Math.max(6, camera.position.z - .5);
      if (event.key === "-") camera.position.z = Math.min(14, camera.position.z + .5);
      camera.lookAt(0, 0, 0);
    };
    window.addEventListener("keydown", move);
    return () => window.removeEventListener("keydown", move);
  }, [camera]);
  return null;
}

function Stars() {
  const ref = useRef<Points>(null);
  const positions = useMemo(() => {
    const data = new Float32Array(420 * 3);
    let seed = 7919;
    const random = () => ((seed = seed * 16807 % 2147483647) - 1) / 2147483646;
    for (let i = 0; i < data.length; i += 3) {
      data[i] = (random() - .5) * 19;
      data[i + 1] = (random() - .5) * 10;
      data[i + 2] = -1 - random() * 8;
    }
    return data;
  }, []);
  useFrame((_, delta) => { if (ref.current) ref.current.rotation.z += delta * .001; });
  return <points ref={ref}><bufferGeometry><bufferAttribute attach="attributes-position" args={[positions, 3]} /></bufferGeometry><pointsMaterial color="#d8e2dd" size={.021} transparent opacity={.72} /></points>;
}

function ParticleFlow({ active }: { active: boolean }) {
  const ref = useRef<Group>(null);
  const particles = useMemo(() => Array.from({ length: 33 }, (_, i) => ({
    x: -2.95 + (i % 11) * .68, y: -.64 + Math.floor(i / 11) * .62,
    z: -.32 + (i % 3) * .17, speed: .2 + (i % 5) * .024, phase: i * .67,
  })), []);
  useFrame((state, delta) => {
    if (!active || !ref.current) return;
    ref.current.children.forEach((item, i) => {
      item.position.x += delta * particles[i].speed;
      item.position.y = particles[i].y + Math.sin(state.clock.elapsedTime * .75 + particles[i].phase) * .05;
      if (item.position.x > 4.6) item.position.x = -2.95;
    });
  });
  return <group ref={ref}>{particles.map((p, i) => <mesh key={i} position={[p.x, p.y, p.z]}><sphereGeometry args={[i % 5 ? .012 : .025, 8, 8]} /><meshBasicMaterial color={i % 5 ? "#ec6a36" : "#ffd38b"} transparent opacity={.7} /></mesh>)}</group>;
}

function Sun({ active }: { active: boolean }) {
  const ring = useRef<Mesh>(null);
  useFrame((_, delta) => { if (active && ring.current) ring.current.rotation.z += delta * .025; });
  return <group position={[-3.78, .02, 0]}>
    <pointLight color="#ffb968" intensity={22} distance={8} decay={2} />
    <mesh><sphereGeometry args={[.8, 64, 64]} /><meshBasicMaterial color="#f2a13b" /></mesh>
    <mesh scale={1.08}><sphereGeometry args={[.8, 48, 48]} /><meshBasicMaterial color="#ffd18b" transparent opacity={.27} blending={AdditiveBlending} depthWrite={false} /></mesh>
    <mesh ref={ring} scale={1.36}><ringGeometry args={[.65, .84, 96]} /><meshBasicMaterial color="#f0a545" transparent opacity={.13} blending={AdditiveBlending} depthWrite={false} /></mesh>
    <mesh scale={1.75}><sphereGeometry args={[.8, 32, 32]} /><meshBasicMaterial color="#e57a2f" transparent opacity={.045} blending={AdditiveBlending} depthWrite={false} side={BackSide} /></mesh>
  </group>;
}

function Hubble({ active }: { active: boolean }) {
  const ref = useRef<Group>(null);
  useFrame((state) => {
    if (!ref.current) return;
    const a = active ? state.clock.elapsedTime * .22 : .65;
    ref.current.position.set(Math.cos(a) * .94, Math.sin(a) * .48, .22 + Math.sin(a) * .12);
    ref.current.rotation.z = a;
  });
  return <group ref={ref} scale={.58}>
    <mesh rotation={[0, 0, Math.PI / 2]}><cylinderGeometry args={[.12, .15, .56, 18]} /><meshStandardMaterial color="#dfe4df" metalness={.8} roughness={.24} /></mesh>
    <mesh position={[.29, 0, 0]} rotation={[0, Math.PI / 2, 0]}><cylinderGeometry args={[.105, .105, .06, 18]} /><meshStandardMaterial color="#17252b" /></mesh>
    {[-.31, .31].map(y => <group key={y} position={[0, y, 0]}><mesh><boxGeometry args={[.54, .2, .025]} /><meshStandardMaterial color="#1c4663" metalness={.45} /></mesh>{[-.18, 0, .18].map(x => <mesh key={x} position={[x, 0, .016]}><boxGeometry args={[.008, .19, .008]} /><meshBasicMaterial color="#75a9b6" /></mesh>)}</group>)}
  </group>;
}

function Earth({ active }: { active: boolean }) {
  const ref = useRef<Group>(null);
  useFrame((_, delta) => { if (active && ref.current) ref.current.rotation.y += delta * .06; });
  return <group position={[.12, 0, 0]}>
    <group ref={ref} rotation={[.12, 0, -.2]}>
      <mesh><sphereGeometry args={[.54, 64, 64]} /><meshStandardMaterial color="#176f91" roughness={.78} /></mesh>
      <mesh position={[-.15, .1, .5]} rotation={[.2, -.2, -.35]} scale={[.19, .3, .035]}><sphereGeometry args={[1, 18, 18]} /><meshStandardMaterial color="#859a66" roughness={.95} /></mesh>
      <mesh position={[.21, -.16, .47]} rotation={[0, 0, .8]} scale={[.22, .12, .03]}><sphereGeometry args={[1, 18, 18]} /><meshStandardMaterial color="#99a96e" roughness={.95} /></mesh>
      <mesh scale={1.06}><sphereGeometry args={[.54, 48, 48]} /><meshBasicMaterial color="#8fe4ef" transparent opacity={.14} blending={AdditiveBlending} depthWrite={false} /></mesh>
    </group>
    <mesh rotation={[1.1, .15, .1]}><torusGeometry args={[.86, .008, 8, 128]} /><meshBasicMaterial color="#91cbd4" transparent opacity={.54} /></mesh>
    {[.78, .94, 1.1].map((r, i) => <mesh key={r} rotation={[Math.PI / 2, 0, 0]} scale={[1.55, 1, 1]}><torusGeometry args={[r, .006, 6, 96]} /><meshBasicMaterial color="#60a8b4" transparent opacity={.13 - i * .025} /></mesh>)}
    <Hubble active={active} />
  </group>;
}

function Gaia() {
  return <group position={[-.2, .44, .1]} rotation={[.1, 0, -.12]}>
    <mesh rotation={[Math.PI / 2, 0, 0]}><cylinderGeometry args={[.31, .31, .035, 10]} /><meshStandardMaterial color="#d2a45c" metalness={.72} roughness={.34} /></mesh>
    <mesh position={[0, .17, 0]}><cylinderGeometry args={[.09, .15, .28, 12]} /><meshStandardMaterial color="#d9e0dc" metalness={.74} roughness={.24} /></mesh>
    {[-1, 1].map(side => <mesh key={side} position={[side * .1, .31, 0]} rotation={[0, 0, side * .35]}><boxGeometry args={[.085, .24, .075]} /><meshStandardMaterial color="#6e9ca4" metalness={.5} /></mesh>)}
  </group>;
}

function Euclid() {
  return <group position={[.38, -.48, -.02]} rotation={[0, -.2, .1]}>
    <mesh><boxGeometry args={[.3, .35, .28]} /><meshStandardMaterial color="#d9ded9" metalness={.72} roughness={.28} /></mesh>
    <mesh position={[0, .23, .08]} rotation={[Math.PI / 2, 0, 0]}><cylinderGeometry args={[.13, .1, .12, 24]} /><meshStandardMaterial color="#202b2d" /></mesh>
    <mesh position={[.35, 0, 0]}><boxGeometry args={[.4, .29, .025]} /><meshStandardMaterial color="#25546d" metalness={.45} /></mesh>
    {[-.09, 0, .09].map(y => <mesh key={y} position={[.35, y, .016]}><boxGeometry args={[.38, .008, .008]} /><meshBasicMaterial color="#72a6b2" /></mesh>)}
  </group>;
}

function L2({ active }: { active: boolean }) {
  const ref = useRef<Group>(null);
  useFrame((_, delta) => { if (active && ref.current) ref.current.rotation.z += delta * .06; });
  return <group position={[3.34, 0, 0]}>
    <group ref={ref}><mesh scale={[1, .62, 1]}><ringGeometry args={[.74, .752, 128]} /><meshBasicMaterial color="#ed6a35" transparent opacity={.62} /></mesh><mesh scale={[1.23, .76, 1]}><ringGeometry args={[.74, .752, 128]} /><meshBasicMaterial color="#80b7c0" transparent opacity={.23} /></mesh></group>
    <mesh><sphereGeometry args={[.05, 16, 16]} /><meshBasicMaterial color="#ffb45e" /></mesh>
    <Gaia /><Euclid />
  </group>;
}

function Scene({ active, reset }: { active: boolean; reset: number }) {
  return <><fog attach="fog" args={["#060907", 8, 19]} /><ambientLight intensity={.48} color="#a9c0bd" /><directionalLight position={[-4, 3, 5]} intensity={2.7} color="#ffd1a0" /><Stars /><ParticleFlow active={active} /><Sun active={active} /><Earth active={active} /><L2 active={active} /><CameraKeys reset={reset} /></>;
}

function hasWebGl() {
  try { const canvas = document.createElement("canvas"); return Boolean(canvas.getContext("webgl2") || canvas.getContext("webgl")); } catch { return false; }
}

export default function SpaceScene({ reduceMotion }: { reduceMotion: boolean }) {
  const [running, setRunning] = useState(true);
  const [reset, setReset] = useState(0);
  const available = hasWebGl();
  const active = running && !reduceMotion;
  return <div className="space-stage">
    {available ? <Canvas camera={{ position: HOME, fov: 42, near: .1, far: 40 }} dpr={[1, 1.6]} gl={{ antialias: true, alpha: false, powerPreference: "high-performance" }} role="img" aria-label="Schematic of solar particle flow, Earth and Hubble in low Earth orbit, and Gaia and Euclid around Sun–Earth L2"><Scene active={active} reset={reset} /></Canvas> : <div className="webgl-fallback" role="img" aria-label="Text alternative for the space environment"><span>Sun · particle source</span><i /><span>Earth · HST</span><i /><span>L2 · Gaia · Euclid</span></div>}
    <div className="scene-hud" aria-hidden="true"><span>FIELD PLATE / 01</span><span>SCHEMATIC · NOT TO SCALE</span></div>
    <div className="scene-label label-sun"><b>01</b><span>SUN<small>PARTICLE SOURCE</small></span></div>
    <div className="scene-label label-earth"><b>02</b><span>EARTH + HST<small>LOW EARTH ORBIT</small></span></div>
    <div className="scene-label label-l2"><b>03</b><span>SUN–EARTH L2<small>GAIA · EUCLID</small></span></div>
    <div className="particle-key" aria-hidden="true"><i /> Solar particle direction</div>
    {available && <div className="scene-controls">{!reduceMotion && <button type="button" onClick={() => setRunning(v => !v)}>{active ? <Pause aria-hidden="true" size={14} /> : <Play aria-hidden="true" size={14} />}{active ? "Pause" : "Play"}</button>}<button type="button" onClick={() => setReset(v => v + 1)}><RotateCcw aria-hidden="true" size={14} />Reset view</button></div>}
    <p className="stage-note">ARROWS pan · +/− zoom · R reset</p>
  </div>;
}
