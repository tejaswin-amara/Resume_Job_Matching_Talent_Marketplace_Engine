import React from "react";

export interface ShinyTextProps extends React.HTMLAttributes<HTMLSpanElement> {
  text?: string;
  disabled?: boolean;
  speed?: number;
  className?: string;
  children?: React.ReactNode;
}

export const ShinyText: React.FC<ShinyTextProps> = ({
  text,
  disabled = false,
  speed = 5,
  className = "",
  children,
  ...props
}) => {
  const content = text ?? children;
  return (
    <span
      className={`text-gray-100 bg-clip-text inline-block ${
        disabled ? "" : "animate-shine"
      } ${className}`}
      style={{
        backgroundImage:
          "linear-gradient(120deg, rgba(255, 255, 255, 0.4) 30%, rgba(255, 255, 255, 1) 50%, rgba(255, 255, 255, 0.4) 70%)",
        backgroundSize: "200% 100%",
        WebkitBackgroundClip: "text",
        animationDuration: `${speed}s`,
      }}
      {...props}
    >
      {content}
    </span>
  );
};
