"use client";

import React from "react";

export interface StarBorderProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  as?: React.ElementType;
  className?: string;
  color?: string;
  speed?: string;
  children?: React.ReactNode;
}

export const StarBorder: React.FC<StarBorderProps> = ({
  as: Component = "button",
  className = "",
  color = "#3b82f6",
  speed = "6s",
  children,
  disabled,
  ...props
}) => {
  return (
    <Component
      disabled={disabled}
      className={`relative inline-block py-[1px] px-[1px] overflow-hidden rounded-xl transition-all duration-200 ${
        disabled
          ? "opacity-50 cursor-not-allowed"
          : "hover:scale-[1.02] active:scale-[0.98] cursor-pointer"
      } ${className}`}
      {...props}
    >
      <div
        className="absolute w-[300%] h-[50%] opacity-70 bottom-[-11px] right-[-250%] rounded-full animate-star-movement-bottom z-0 pointer-events-none"
        style={{
          background: `radial-gradient(circle, ${color}, transparent 25%)`,
          animationDuration: speed,
        }}
      />
      <div
        className="absolute w-[300%] h-[50%] opacity-70 top-[-10px] left-[-250%] rounded-full animate-star-movement-top z-0 pointer-events-none"
        style={{
          background: `radial-gradient(circle, ${color}, transparent 25%)`,
          animationDuration: speed,
        }}
      />
      <div className="relative z-10 bg-gray-900 border border-gray-800 text-gray-100 py-2 px-4 rounded-xl font-medium text-sm flex items-center justify-center">
        {children}
      </div>
    </Component>
  );
};
