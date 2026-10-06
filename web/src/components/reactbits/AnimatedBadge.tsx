import React from "react";

export interface AnimatedBadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "success" | "danger" | "outline";
  children: React.ReactNode;
  className?: string;
}

export const AnimatedBadge: React.FC<AnimatedBadgeProps> = ({
  children,
  variant = "default",
  className = "",
  ...props
}) => {
  const variants = {
    default: "border-gray-700 bg-gray-800 text-gray-100",
    success:
      "border-green-800 bg-green-900/50 text-green-400 shadow-[0_0_8px_rgba(34,197,94,0.15)]",
    danger:
      "border-red-800 bg-red-900/50 text-red-400 shadow-[0_0_8px_rgba(239,68,68,0.15)]",
    outline: "border-gray-700 bg-transparent text-gray-100",
  };

  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-all duration-200 hover:scale-105 ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </span>
  );
};

export { AnimatedBadge as Badge };
export type { AnimatedBadgeProps as BadgeProps };
