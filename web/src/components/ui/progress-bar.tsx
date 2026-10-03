import * as React from "react";
import { clsx, type ClassValue } from "clsx";

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

interface ProgressBarProps {
  value: number;
  max?: number;
  className?: string;
  indicatorClassName?: string;
}

export function ProgressBar({ value, max = 100, className, indicatorClassName }: ProgressBarProps) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
  
  return (
    <div className={cn("relative h-2 w-full overflow-hidden rounded-full bg-gray-800", className)}>
      <div 
        className={cn("h-full w-full flex-1 bg-blue-600 transition-all", indicatorClassName)} 
        style={{ transform: `translateX(-${100 - percentage}%)` }} 
      />
    </div>
  );
}
