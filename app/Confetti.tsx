"use client";

import type { RefObject } from "react";
import { useEffect, useRef, useState } from "react";
import "./Confetti.scss";

type Props = {
  targetRef?: RefObject<HTMLDivElement | null>;
  shouldStart?: boolean;
  amount?: number;
};

const gravity = 0.1;

const createParticle = (
  index: number,
  x: number,
  y: number,
  velocityXMultiplier: number,
  color: string
) => {
  const particle = {
    index,
    x,
    y,
    z: 0,
    color,
    weight: Math.random() - 0.4 + 0.75,
    velocity: {
      x: Math.random() * 8 * velocityXMultiplier,
      y: (Math.random() - 0.8) * 6,
      z: (Math.random() - 0.8) * 6,
      rotation: (Math.random() - 0.5) * 120,
    },
    rotation: {
      vector: [Math.random(), Math.random(), Math.random()],
      angle: Math.random() * 300,
    },
    life: 5 + Math.random() * 2,
    element: document.createElement("b"),
    get hasCompleted() {
      return particle.life <= 0;
    },
    update: () => {
      if (particle.life <= 0) return;
      particle.x += particle.velocity.x;
      particle.y += particle.velocity.y;
      particle.z += particle.velocity.z;
      particle.rotation.angle += particle.velocity.rotation;
      particle.element.style.setProperty(
        "transform",
        `translate3d(${particle.x}px, ${particle.y}px, ${
          particle.z
        }px) rotate3d(${particle.rotation.vector.join(",")},${
          particle.rotation.angle
        }deg)`
      );
      particle.life -= 0.01;
      if (particle.hasCompleted) {
        particle.dispose();
      }
      particle.velocity.y += gravity * particle.weight;
      particle.velocity.x *= 0.995;
      particle.velocity.rotation *= 0.995;
      if (particle.life < 0.1)
        particle.element.style.setProperty("opacity", `${particle.life * 10}`);
    },
    dispose: () => {
      particle.life = 0;
      particle.element.parentElement?.removeChild(particle.element);
    },
  };
  particle.element.style.setProperty("background-color", particle.color);
  particle.update();
  return particle;
};

type Particle = ReturnType<typeof createParticle>;

const confettiColors = ["#8D75E6", "#FD975D", "#F486B8", "#5ABE89", "#F0A848"];

type ConfettiOptions = {
  containerRef?: RefObject<HTMLDivElement | null>;
  targetRef?: RefObject<HTMLDivElement | null>;
  onComplete?: () => void;
  amount?: number;
};

function throwConfetti({
  containerRef,
  targetRef,
  onComplete,
  amount,
}: ConfettiOptions) {
  const createFpsScheduler = (maxFps = 60) => {
    const fpsInterval = 1000 / maxFps;
    let then = window.performance.now();
    let elapsed = 0;
    let stopped = false;

    return (callback: () => void) => {
      function animate(now: number) {
        if (stopped) return;

        requestAnimationFrame(animate);
        elapsed = now - then;

        if (elapsed > fpsInterval) {
          then = now - (elapsed % fpsInterval);
          callback();
        }
      }

      requestAnimationFrame(animate);

      return function dispose() {
        stopped = true;
      };
    };
  };

  const particles: Particle[] = [];
  const maxSixtyFpsScheduler = createFpsScheduler(60);
  const disposers: (() => void)[] = [];

  if (!containerRef?.current || (targetRef && !targetRef.current)) {
    return () => {};
  }

  const isScreenWideConfettiEffect = !targetRef;
  const boundingBox = (
    targetRef ?? containerRef
  ).current!.getBoundingClientRect();
  const { top, left, width, height } = boundingBox;
  const totalPieces = Math.floor(amount ?? 60);

  particles.push(
    ...Array(totalPieces)
      .fill(null)
      .map((n, i) => {
        const x =
          left +
          Math.random() * width +
          (Math.random() - 0.5) *
            (isScreenWideConfettiEffect ? window.innerWidth * 0.25 : 20);
        return createParticle(
          i,
          x,
          isScreenWideConfettiEffect
            ? 0 + Math.random() * 20
            : top + Math.random() * height + (Math.random() - 0.5) * 20,
          (i % 2 === 0
            ? Math.random() - 0.5 >= 0
              ? 1
              : -1
            : x > left + width / 2
              ? 1
              : -1) * (isScreenWideConfettiEffect ? -0.5 : 0.5),
          confettiColors[i % 5]
        );
      })
  );

  containerRef.current!.append(...particles.map((p) => p.element));

  const update = () => {
    if (particles.every((p) => p.hasCompleted)) {
      onComplete?.();
      disposers.forEach((d) => d());
      return;
    }
    particles.forEach((p) => p.update());
  };

  disposers.push(maxSixtyFpsScheduler(update));

  return () => {
    disposers.forEach((d) => d());
    particles.forEach((p) => p.dispose());
  };
}

const ConfettiScreen = (props: Props) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [completed, setCompleted] = useState(false);

  useEffect(() => {
    const disposeConfetti = throwConfetti({
      containerRef,
      targetRef: props.targetRef,
      onComplete: () => {
        setCompleted(true);
      },
      amount: props.amount,
    });
    return () => {
      disposeConfetti();
    };
  }, []);

  return !completed ? (
    <div id="global">
      <div className="confetti-screen" ref={containerRef} />
    </div>
  ) : null;
};

export default ConfettiScreen;