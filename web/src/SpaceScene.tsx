import { Canvas, useFrame, useLoader, useThree } from "@react-three/fiber";
import { Pause, Play, RotateCcw } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import {
  AdditiveBlending,
  BackSide,
  DoubleSide,
  Group,
  Mesh,
  Points,
  SRGBColorSpace,
  TextureLoader,
  Vector3,
} from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { DRACOLoader } from "three/examples/jsm/loaders/DRACOLoader.js";

type Focus = "system" | "earth" | "l2";

const CAMERA: Record<Focus, { position: [number, number, number]; target: [number, number, number] }> = {
  system: { position: [0, 1.15, 10.6], target: [0, 0, 0] },
  earth: { position: [0.18, 0.4, 4.25], target: [0.12, 0, 0] },
  l2: { position: [3.35, 0.45, 4.25], target: [3.35, 0, 0] },
};

const asset = (path: string) => `${import.meta.env.BASE_URL}${path}`;

function CameraRig({ focus, reset }: { focus: Focus; reset: number }) {
  const { camera } = useThree();
  const desired = useRef(new Vector3(...CAMERA.system.position));
  const target = useRef(new Vector3(...CAMERA.system.target));

  useEffect(() => {
    desired.current.set(...CAMERA[focus].position);
    target.current.set(...CAMERA[focus].target);
  }, [focus, reset]);

  useEffect(() => {
    const move = (event: KeyboardEvent) => {
      if (!["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "+", "-", "r", "R", "0"].includes(event.key)) return;
      const element = event.target as HTMLElement;
      if (["INPUT", "TEXTAREA", "SELECT", "BUTTON"].includes(element.tagName)) return;
      event.preventDefault();
      if (["r", "R", "0"].includes(event.key)) desired.current.set(...CAMERA[focus].position);
      if (event.key === "ArrowLeft") desired.current.x -= 0.35;
      if (event.key === "ArrowRight") desired.current.x += 0.35;
      if (event.key === "ArrowUp") desired.current.y += 0.35;
      if (event.key === "ArrowDown") desired.current.y -= 0.35;
      if (event.key === "+") desired.current.z = Math.max(3.2, desired.current.z - 0.5);
      if (event.key === "-") desired.current.z = Math.min(14, desired.current.z + 0.5);
    };
    window.addEventListener("keydown", move);
    return () => window.removeEventListener("keydown", move);
  }, [focus]);

  useFrame((_, delta) => {
    const ease = 1 - Math.exp(-delta * 5.5);
    camera.position.lerp(desired.current, ease);
    camera.lookAt(target.current);
  });
  return null;
}

function Stars() {
  const ref = useRef<Points>(null);
  const positions = useMemo(() => {
    const data = new Float32Array(520 * 3);
    let seed = 7919;
    const random = () => ((seed = (seed * 16807) % 2147483647) - 1) / 2147483646;
    for (let i = 0; i < data.length; i += 3) {
      data[i] = (random() - 0.5) * 20;
      data[i + 1] = (random() - 0.5) * 11;
      data[i + 2] = -1 - random() * 8;
    }
    return data;
  }, []);
  useFrame((_, delta) => {
    if (ref.current) ref.current.rotation.z += delta * 0.001;
  });
  return (
    <points ref={ref}>
      <bufferGeometry><bufferAttribute attach="attributes-position" args={[positions, 3]} /></bufferGeometry>
      <pointsMaterial color="#d8e2dd" size={0.018} transparent opacity={0.7} />
    </points>
  );
}

function ParticleFlow({ active }: { active: boolean }) {
  const ref = useRef<Group>(null);
  const particles = useMemo(() => Array.from({ length: 44 }, (_, i) => ({
    x: -3.02 + (i % 11) * 0.72,
    y: -0.85 + Math.floor(i / 11) * 0.56,
    z: -0.42 + (i % 4) * 0.14,
    speed: 0.2 + (i % 5) * 0.026,
    phase: i * 0.67,
  })), []);
  useFrame((state, delta) => {
    if (!active || !ref.current) return;
    ref.current.children.forEach((item, i) => {
      item.position.x += delta * particles[i].speed;
      item.position.y = particles[i].y + Math.sin(state.clock.elapsedTime * 0.75 + particles[i].phase) * 0.05;
      if (item.position.x > 4.65) item.position.x = -3.05;
    });
  });
  return (
    <group ref={ref}>
      {particles.map((particle, i) => (
        <mesh key={i} position={[particle.x, particle.y, particle.z]}>
          <sphereGeometry args={[i % 5 ? 0.01 : 0.024, 8, 8]} />
          <meshBasicMaterial color={i % 5 ? "#ec6a36" : "#ffd38b"} transparent opacity={0.7} />
        </mesh>
      ))}
    </group>
  );
}

function Sun({ active }: { active: boolean }) {
  const shell = useRef<Mesh>(null);
  useFrame((_, delta) => {
    if (active && shell.current) shell.current.rotation.z += delta * 0.02;
  });
  return (
    <group position={[-3.78, 0.02, 0]}>
      <pointLight color="#ffb968" intensity={24} distance={8} decay={2} />
      <mesh><sphereGeometry args={[0.81, 72, 72]} /><meshStandardMaterial color="#e99a35" emissive="#d87920" emissiveIntensity={1.6} roughness={0.9} /></mesh>
      <mesh ref={shell} scale={1.018}><sphereGeometry args={[0.81, 32, 32]} /><meshBasicMaterial color="#ffcd76" wireframe transparent opacity={0.12} /></mesh>
      <mesh scale={1.11}><sphereGeometry args={[0.81, 48, 48]} /><meshBasicMaterial color="#ffd18b" transparent opacity={0.19} blending={AdditiveBlending} depthWrite={false} /></mesh>
      {[1.2, 1.38, 1.62].map((scale, index) => (
        <mesh key={scale} scale={scale} rotation={[0, 0, index * 0.58]}>
          <ringGeometry args={[0.66, 0.69, 96]} />
          <meshBasicMaterial color="#f0a545" transparent opacity={0.1 - index * 0.02} blending={AdditiveBlending} depthWrite={false} />
        </mesh>
      ))}
    </group>
  );
}

function NasaHubble({ active }: { active: boolean }) {
  const orbit = useRef<Group>(null);
  const { scene } = useLoader(GLTFLoader, asset("models/nasa-hubble-a.glb"), (loader) => {
    const draco = new DRACOLoader();
    draco.setDecoderPath(asset("draco/"));
    loader.setDRACOLoader(draco);
  });
  const model = useMemo(() => scene.clone(true), [scene]);
  useFrame((state) => {
    if (!orbit.current) return;
    const angle = active ? state.clock.elapsedTime * 0.2 : 0.7;
    orbit.current.rotation.z = angle;
  });
  return (
    <group ref={orbit} rotation={[1.02, 0.12, 0.7]}>
      <group position={[1.03, 0, 0]} rotation={[0.25, 0.55, -0.1]} scale={0.00145}>
        <primitive object={model} />
      </group>
    </group>
  );
}

function Earth({ active }: { active: boolean }) {
  const ref = useRef<Group>(null);
  const texture = useLoader(TextureLoader, asset("textures/nasa-blue-marble-2015.jpg"));
  const map = useMemo(() => {
    const result = texture.clone();
    result.colorSpace = SRGBColorSpace;
    result.needsUpdate = true;
    return result;
  }, [texture]);
  useFrame((_, delta) => {
    if (active && ref.current) ref.current.rotation.y += delta * 0.055;
  });
  return (
    <group position={[0.12, 0, 0]}>
      <group ref={ref} rotation={[0.12, -0.8, -0.2]}>
        <mesh><sphereGeometry args={[0.55, 72, 72]} /><meshStandardMaterial map={map} roughness={0.78} metalness={0.02} /></mesh>
        <mesh scale={1.035}><sphereGeometry args={[0.55, 64, 64]} /><meshPhongMaterial color="#b5f3ff" transparent opacity={0.09} shininess={80} depthWrite={false} /></mesh>
        <mesh scale={1.085}><sphereGeometry args={[0.55, 48, 48]} /><meshBasicMaterial color="#58cce5" transparent opacity={0.07} blending={AdditiveBlending} depthWrite={false} side={BackSide} /></mesh>
      </group>
      <mesh rotation={[1.02, 0.08, 0.08]}><torusGeometry args={[1.03, 0.006, 8, 160]} /><meshBasicMaterial color="#b5e3e5" transparent opacity={0.52} /></mesh>
      {[0.78, 0.96, 1.15].map((radius, index) => (
        <mesh key={radius} rotation={[Math.PI / 2, 0, 0]} scale={[1.65, 1, 1]}>
          <torusGeometry args={[radius, 0.005, 6, 128]} />
          <meshBasicMaterial color="#60a8b4" transparent opacity={0.12 - index * 0.024} />
        </mesh>
      ))}
      <NasaHubble active={active} />
    </group>
  );
}

function GaiaModel() {
  return (
    <group rotation={[0.18, -0.22, -0.1]}>
      <mesh rotation={[Math.PI / 2, 0, 0]}><cylinderGeometry args={[0.54, 0.54, 0.035, 12]} /><meshStandardMaterial color="#b98a42" metalness={0.72} roughness={0.35} /></mesh>
      {Array.from({ length: 12 }, (_, index) => {
        const angle = (index / 12) * Math.PI * 2;
        return <mesh key={index} rotation={[0, 0, angle]} position={[Math.cos(angle) * 0.29, Math.sin(angle) * 0.29, 0.022]}><boxGeometry args={[0.46, 0.012, 0.009]} /><meshBasicMaterial color="#f0c071" transparent opacity={0.76} /></mesh>;
      })}
      <mesh position={[0, 0.19, 0]}><cylinderGeometry args={[0.18, 0.22, 0.38, 6]} /><meshStandardMaterial color="#d9d8cb" metalness={0.68} roughness={0.3} /></mesh>
      <mesh position={[0, 0.4, 0]}><cylinderGeometry args={[0.15, 0.18, 0.08, 6]} /><meshStandardMaterial color="#75868a" metalness={0.55} /></mesh>
      {[-1, 1].map((side) => <group key={side} position={[side * 0.105, 0.45, 0.04]} rotation={[0.08, 0, side * 0.13]}><mesh><boxGeometry args={[0.16, 0.12, 0.12]} /><meshStandardMaterial color="#c7d2cd" metalness={0.65} roughness={0.28} /></mesh><mesh position={[0, 0, 0.064]}><boxGeometry args={[0.115, 0.065, 0.008]} /><meshBasicMaterial color="#07171b" /></mesh></group>)}
    </group>
  );
}

function EuclidModel() {
  return (
    <group rotation={[0.08, -0.35, 0.08]}>
      <mesh position={[0, -0.13, 0]}><boxGeometry args={[0.48, 0.31, 0.4]} /><meshStandardMaterial color="#c5b28a" metalness={0.42} roughness={0.55} /></mesh>
      <mesh position={[0, 0.18, 0]}><cylinderGeometry args={[0.19, 0.22, 0.42, 24]} /><meshStandardMaterial color="#e1e3dc" metalness={0.7} roughness={0.25} /></mesh>
      <mesh position={[0, 0.405, 0]}><cylinderGeometry args={[0.15, 0.19, 0.055, 32]} /><meshStandardMaterial color="#171e1e" roughness={0.32} /></mesh>
      <mesh position={[0, 0.438, 0]} rotation={[Math.PI / 2, 0, 0]}><circleGeometry args={[0.12, 32]} /><meshStandardMaterial color="#48656b" metalness={0.8} roughness={0.2} side={DoubleSide} /></mesh>
      <mesh position={[0, -0.34, -0.04]} rotation={[Math.PI / 2, 0, 0]}><cylinderGeometry args={[0.42, 0.42, 0.025, 8]} /><meshStandardMaterial color="#142f3d" metalness={0.38} roughness={0.42} /></mesh>
      {[-0.2, 0, 0.2].map((x) => <mesh key={x} position={[x, -0.36, -0.025]}><boxGeometry args={[0.006, 0.7, 0.008]} /><meshBasicMaterial color="#7297a0" /></mesh>)}
      <group position={[0.37, -0.03, 0.12]} rotation={[0.2, 0.2, -0.45]}><mesh><cylinderGeometry args={[0.018, 0.018, 0.28, 8]} /><meshStandardMaterial color="#dbded7" metalness={0.75} /></mesh><mesh position={[0, 0.18, 0]} rotation={[Math.PI / 2, 0, 0]}><coneGeometry args={[0.12, 0.055, 24, 1, true]} /><meshStandardMaterial color="#d8d4c5" metalness={0.7} side={DoubleSide} /></mesh></group>
    </group>
  );
}

function L2Observatories({ active }: { active: boolean }) {
  const gaia = useRef<Group>(null);
  const euclid = useRef<Group>(null);
  const rings = useRef<Group>(null);
  useFrame((state, delta) => {
    if (active && rings.current) rings.current.rotation.z += delta * 0.028;
    if (!active) return;
    const time = state.clock.elapsedTime * 0.14;
    if (gaia.current) gaia.current.position.set(Math.cos(time) * 0.74, 0.24 + Math.sin(time) * 0.32, Math.sin(time) * 0.12);
    if (euclid.current) euclid.current.position.set(Math.cos(time + Math.PI) * 0.9, -0.18 + Math.sin(time + Math.PI) * 0.39, Math.sin(time + Math.PI) * 0.16);
  });
  return (
    <group position={[3.34, 0, 0]}>
      <group ref={rings}><mesh scale={[1, 0.62, 1]}><ringGeometry args={[0.74, 0.75, 160]} /><meshBasicMaterial color="#ed6a35" transparent opacity={0.58} /></mesh><mesh scale={[1.28, 0.79, 1]}><ringGeometry args={[0.74, 0.75, 160]} /><meshBasicMaterial color="#80b7c0" transparent opacity={0.22} /></mesh></group>
      <mesh><sphereGeometry args={[0.045, 16, 16]} /><meshBasicMaterial color="#ffb45e" /></mesh>
      <group ref={gaia} position={[0.72, 0.24, 0.08]} scale={0.66}><GaiaModel /></group>
      <group ref={euclid} position={[-0.86, -0.18, -0.08]} scale={0.69}><EuclidModel /></group>
    </group>
  );
}

function Scene({ active, focus, reset }: { active: boolean; focus: Focus; reset: number }) {
  return <><color attach="background" args={["#040706"]} /><fog attach="fog" args={["#040706", 8, 19]} /><ambientLight intensity={0.62} color="#b9c8c4" /><directionalLight position={[-4, 3, 5]} intensity={3.1} color="#ffd1a0" /><Stars /><ParticleFlow active={active} /><Sun active={active} /><Earth active={active} /><L2Observatories active={active} /><CameraRig focus={focus} reset={reset} /></>;
}

function hasWebGl() {
  try {
    const canvas = document.createElement("canvas");
    return Boolean(canvas.getContext("webgl2") || canvas.getContext("webgl"));
  } catch {
    return false;
  }
}

const focusLabels: Record<Focus, string> = { system: "System", earth: "Earth orbit", l2: "L2 observatories" };

export default function SpaceScene({ reduceMotion }: { reduceMotion: boolean }) {
  const [running, setRunning] = useState(true);
  const [reset, setReset] = useState(0);
  const [focus, setFocus] = useState<Focus>("system");
  const available = hasWebGl();
  const active = running && !reduceMotion;

  return (
    <>
      <div className={`space-stage focus-${focus}`}>
        {available ? <Canvas camera={{ position: CAMERA.system.position, fov: 42, near: 0.1, far: 40 }} dpr={[1, 1.6]} gl={{ antialias: true, alpha: false, preserveDrawingBuffer: true, powerPreference: "high-performance" }} onCreated={({ gl }) => gl.setClearColor("#040706", 1)} role="img" aria-label="Research-informed 3D view of the Sun, Earth with NASA Hubble in low Earth orbit, and ESA Gaia and Euclid around Sun–Earth L2"><Scene active={active} focus={focus} reset={reset} /></Canvas> : <div className="webgl-fallback" role="img" aria-label="Text alternative for the space environment"><span>Sun · particle source</span><i /><span>Earth · HST</span><i /><span>L2 · Gaia · Euclid</span></div>}
        <div className="scene-hud" aria-hidden="true"><span>FIELD PLATE / 01</span><span>MEASURED DISTANCES · OBJECTS ENLARGED</span></div>
        <div className="scene-focus" role="group" aria-label="Select camera view">{(Object.keys(focusLabels) as Focus[]).map((item) => <button key={item} type="button" aria-pressed={focus === item} onClick={() => setFocus(item)}>{focusLabels[item]}</button>)}</div>
        {(focus === "system" || focus === "earth") && <div className="scene-label label-earth"><b>02</b><span>EARTH + HST<small>483 km nominal altitude</small></span></div>}
        {focus === "system" && <div className="scene-label label-sun"><b>01</b><span>SUN<small>G2 V · PARTICLE SOURCE</small></span></div>}
        {(focus === "system" || focus === "l2") && <div className="scene-label label-l2"><b>03</b><span>SUN–EARTH L2<small>GAIA · EUCLID</small></span></div>}
        {focus === "earth" && <div className="model-credit model-credit-hst">NASA 3D ASSET / HST-A <small>13.2 m × 4.2 m</small></div>}
        {focus === "l2" && <div className="l2-specs"><span>GAIA<small>10 m / 12-panel shield</small></span><span>EUCLID<small>4.7 × 3.7 m / 1.2 m telescope</small></span></div>}
        {focus === "system" && <div className="distance-rail" aria-hidden="true"><span className="distance-au">149.6 million km · 1 AU</span><i /><span className="distance-l2">1.5 million km</span></div>}
        <div className="particle-key" aria-hidden="true"><i /> Solar particle direction</div>
        {available && <div className="scene-controls">{!reduceMotion && <button type="button" onClick={() => setRunning((value) => !value)}>{active ? <Pause aria-hidden="true" size={14} /> : <Play aria-hidden="true" size={14} />}{active ? "Pause" : "Play"}</button>}<button type="button" onClick={() => setReset((value) => value + 1)}><RotateCcw aria-hidden="true" size={14} />Reset</button></div>}
        <p className="stage-note">ARROWS pan · +/− zoom · R reset</p>
      </div>
      <div className="field-scale" aria-label="Mission geometry measurements">
        <div><span>01 / baseline</span><strong>149.6 M km</strong><p>Mean Sun–Earth distance / 1 AU</p></div>
        <div><span>02 / low Earth orbit</span><strong>483 km</strong><p>Approximate Hubble altitude</p></div>
        <div><span>03 / deep-space station</span><strong>1.5 M km</strong><p>Earth to Sun–Earth L2</p></div>
        <div className="scale-disclosure"><span>DISPLAY SCALE</span><p>Ordering is physical. Distances are compressed and bodies enlarged for inspection.</p></div>
      </div>
      <p className="field-credit">Geometry sources: <a href="https://science.nasa.gov/mission/hubble/overview/hubble-by-the-numbers/">NASA Hubble</a> · <a href="https://science.nasa.gov/learn/basics-of-space-flight/chapter1-1/">NASA 1 AU</a> · <a href="https://science.nasa.gov/universe/glossary/">NASA L2</a> · <a href="https://www.esa.int/Science_Exploration/Space_Science/Gaia/Gaia_factsheet">ESA Gaia</a> · <a href="https://www.esa.int/Science_Exploration/Space_Science/Euclid_overview">ESA Euclid</a></p>
    </>
  );
}
