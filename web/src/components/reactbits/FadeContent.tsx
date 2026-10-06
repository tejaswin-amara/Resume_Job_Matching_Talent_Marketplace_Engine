"use client";

import React, { useEffect, useState } from "react";

export interface FadeContentProps {
  children: React.ReactNode;
  blur?: boolean;
  duration?: number;
  delay?: number;
  className?: string;
}

export const FadeContent: React.FC<FadeContentProps> = ({
  children,
  blur = true,
  duration = 800,
  delay = 0,
  className = "",
}) => {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setVisible(true), delay);
    return () => clearTimeout(timer);
  }, [delay]);

  return (
    <div
      className={className}
      style={{
        opacity: visible ? 1 : 0,
        filter: blur ? (visible ? "blur(0px)" : "blur(10px)") : "none",
        transition: `opacity ${duration}ms cubic-bezier(0.16, 1, 0.3, 1), filter ${duration}ms cubic-bezier(0.16, 1, 0.3, 1)`,
      }}
    >
      {children}
    </div>
  );
};
