import * as React from "react";
import { clsx, type ClassValue } from "clsx";

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "success" | "danger" | "outline";
}

function Badge({ className, variant = "default", ...props }: BadgeProps) {
  const variants = {
    default: "border-transparent bg-gray-800 text-gray-100",
    success: "border-transparent bg-green-900/50 text-green-400 border border-green-800",
    danger: "border-transparent bg-red-900/50 text-red-400 border border-red-800",
    outline: "text-gray-100 border border-gray-700",
  };

  return (
    <div className={cn("inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2", variants[variant], className)} {...props} />
  );
}

export { Badge };
