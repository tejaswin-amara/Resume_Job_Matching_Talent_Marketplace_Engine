"use client";

import React, { useRef, useEffect } from "react";

export interface SquaresProps {
  direction?: "diagonal" | "up" | "right" | "down" | "left";
  speed?: number;
  borderColor?: string;
  squareSize?: number;
  hoverFillColor?: string;
  className?: string;
}

export const Squares: React.FC<SquaresProps> = ({
  direction = "diagonal",
  speed = 0.5,
  borderColor = "rgba(255, 255, 255, 0.05)",
  squareSize = 40,
  hoverFillColor = "rgba(59, 130, 246, 0.12)",
  className = "",
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const hoveredSquareRef = useRef<{ x: number; y: number } | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animationFrameId: number;
    const gridOffset = { x: 0, y: 0 };

    const resizeCanvas = () => {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
    };
    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);

    const handleMouseMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;
      const col = Math.floor((mouseX - (gridOffset.x % squareSize)) / squareSize);
      const row = Math.floor((mouseY - (gridOffset.y % squareSize)) / squareSize);
      hoveredSquareRef.current = { x: col, y: row };
    };

    const handleMouseLeave = () => {
      hoveredSquareRef.current = null;
    };

    canvas.addEventListener("mousemove", handleMouseMove);
    canvas.addEventListener("mouseleave", handleMouseLeave);

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const numCols = Math.ceil(canvas.width / squareSize) + 2;
      const numRows = Math.ceil(canvas.height / squareSize) + 2;

      const offsetX = gridOffset.x % squareSize;
      const offsetY = gridOffset.y % squareSize;

      // Draw hovered square highlight
      if (hoveredSquareRef.current && hoverFillColor) {
        ctx.fillStyle = hoverFillColor;
        const hx = hoveredSquareRef.current.x * squareSize + offsetX;
        const hy = hoveredSquareRef.current.y * squareSize + offsetY;
        ctx.fillRect(hx, hy, squareSize, squareSize);
      }

      ctx.strokeStyle = borderColor;
      ctx.lineWidth = 1;

      for (let col = -1; col < numCols; col++) {
        for (let row = -1; row < numRows; row++) {
          const x = col * squareSize + offsetX;
          const y = row * squareSize + offsetY;
          ctx.strokeRect(x, y, squareSize, squareSize);
        }
      }

      switch (direction) {
        case "diagonal":
          gridOffset.x = (gridOffset.x + speed) % squareSize;
          gridOffset.y = (gridOffset.y + speed) % squareSize;
          break;
        case "up":
          gridOffset.y = (gridOffset.y - speed) % squareSize;
          break;
        case "down":
          gridOffset.y = (gridOffset.y + speed) % squareSize;
          break;
        case "left":
          gridOffset.x = (gridOffset.x - speed) % squareSize;
          break;
        case "right":
          gridOffset.x = (gridOffset.x + speed) % squareSize;
          break;
      }

      animationFrameId = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      window.removeEventListener("resize", resizeCanvas);
      canvas.removeEventListener("mousemove", handleMouseMove);
      canvas.removeEventListener("mouseleave", handleMouseLeave);
      cancelAnimationFrame(animationFrameId);
    };
  }, [direction, speed, borderColor, squareSize, hoverFillColor]);

  return <canvas ref={canvasRef} className={`w-full h-full ${className}`} />;
};
