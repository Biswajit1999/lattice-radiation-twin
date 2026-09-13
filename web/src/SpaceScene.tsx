import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { Pause, Play } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import type { Group } from "three";

function CameraKeys() {
  const { camera } = useThree();
  useEffect(() => {
    const move = (event: KeyboardEvent) => {
      if (!["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "+", "-"].includes(event.key)) return;
      const element = event.target as HTMLElement;
      if (["INPUT", "TEXTAREA", "SELECT"].includes(element.tagName)) return;
      event.preventDefault();
      if (event.key === "ArrowLeft") camera.position.x -= 0.35;
      if (event.key === "ArrowRight") camera.position.x += 0.35;
      if (event.key === "ArrowUp") camera.position.y += 0.35;
      if (event.key === "ArrowDown") camera.position.y -= 0.35;
      if (event.key === "+") camera.position.z = Math.max(4, camera.position.z - 0.5);
      if (event.key === "-") camera.position.z = Math.min(12, camera.position.z + 0.5);
      camera.lookAt(0, 0, 0);
    };
    window.addEventListener("keydown", move);
    return () => window.removeEventListener("keydown", move);
  }, [camera]);
  return null;
}

function Schematic({ running }: { running: boolean }) {
  const group = useRef<Group>(null);
  useFrame((_, delta) => {
    if (running && group.current) group.current.rotation.y += delta * 0.055;
  });
  return (
    <group ref={group}>
      <ambientLight intensity={1.5} />
      <directionalLight position={[3, 4, 5]} intensity={2.2} />
      <mesh position={[-3.4, 0, 0]}>
        <sphereGeometry args={[0.68, 32, 32]} />
        <meshStandardMaterial color="#e6a84b" roughness={0.75} />
      </mesh>
      <mesh position={[0, 0, 0]}>
        <sphereGeometry args={[0.48, 32, 32]} />
        <meshStandardMaterial color="#4aa8c8" roughness={0.8} />
      </mesh>
      <mesh position={[0.78, 0.1, 0]}>
        <boxGeometry args={[0.18, 0.12, 0.1]} />
        <meshStandardMaterial color="#e8edf2" />
      </mesh>
      <mesh position={[3.15, 0, 0]}>
        <sphereGeometry args={[0.13, 20, 20]} />
        <meshStandardMaterial color="#cf8f55" />
      </mesh>
      <mesh position={[3.5, 0.36, 0.18]}>
        <boxGeometry args={[0.22, 0.08, 0.32]} />
        <meshStandardMaterial color="#70bfd5" />
      </mesh>
      <mesh position={[3.5, -0.36, -0.18]}>
        <boxGeometry args={[0.22, 0.08, 0.32]} />
        <meshStandardMaterial color="#d8a969" />
      </mesh>
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <ringGeometry args={[0.72, 0.73, 96]} />
        <meshBasicMaterial color="#55707d" transparent opacity={0.65} />
      </mesh>
      <mesh position={[3.15, 0, 0]} rotation={[Math.PI / 2, 0, 0]}>
        <ringGeometry args={[0.42, 0.43, 64]} />
        <meshBasicMaterial color="#55707d" transparent opacity={0.55} />
      </mesh>
      <CameraKeys />
    </group>
  );
}

function webGlAvailable() {
  try {
    const canvas = document.createElement("canvas");
    return Boolean(canvas.getContext("webgl2") || canvas.getContext("webgl"));
  } catch {
    return false;
  }
}

export default function SpaceScene({ reduceMotion }: { reduceMotion: boolean }) {
  const [running, setRunning] = useState(true);
  const available = webGlAvailable();
  const active = running && !reduceMotion;
  return (
    <div className="space-stage">
      {available ? (
        <Canvas
          camera={{ position: [0, 2.3, 8], fov: 44 }}
          role="img"
          aria-label="Schematic Sun, Earth, HST in low Earth orbit, and Gaia and Euclid near Sun–Earth L2"
        >
          <Schematic running={active} />
        </Canvas>
      ) : (
        <div className="webgl-fallback" role="img" aria-label="WebGL schematic unavailable">
          <span>Sun</span><span>Earth · HST</span><span>L2 · Gaia · Euclid</span>
        </div>
      )}
      {available && !reduceMotion && (
        <button className="motion-toggle" type="button" onClick={() => setRunning((value) => !value)}>
          {active ? <Pause aria-hidden="true" size={16} /> : <Play aria-hidden="true" size={16} />}
          {active ? "Pause schematic" : "Play schematic"}
        </button>
      )}
      <p className="stage-note">SCHEMATIC geometry · Arrow keys move camera · +/− zoom</p>
    </div>
  );
}
