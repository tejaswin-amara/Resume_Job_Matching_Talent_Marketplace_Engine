"use client";

import React, { useEffect, useState } from "react";

export interface CountUpProps extends React.HTMLAttributes<HTMLSpanElement> {
  from?: number;
  to: number;
  duration?: number;
  decimals?: number;
  suffix?: string;
  prefix?: string;
  className?: string;
}

export const CountUp: React.FC<CountUpProps> = ({
  from = 0,
  to,
  duration = 1.2,
  decimals = 0,
  suffix = "",
  prefix = "",
  className = "",
  ...props
}) => {
  const [count, setCount] = useState(from);

  useEffect(() => {
    let startTime: number | null = null;
    let frameId: number;

    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime;
      const progress = Math.min((currentTime - startTime) / (duration * 1000), 1);
      const easeOut = 1 - Math.pow(1 - progress, 3);
      const currentVal = from + (to - from) * easeOut;
      setCount(Number(currentVal.toFixed(decimals)));

      if (progress < 1) {
        frameId = requestAnimationFrame(animate);
      }
    };

    frameId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(frameId);
  }, [from, to, duration, decimals]);

  return (
    <span className={className} {...props}>
      {prefix}
      {count}
      {suffix}
    </span>
  );
};
