import React from "react";

export interface AnimatedProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value: number;
  max?: number;
  className?: string;
  indicatorClassName?: string;
}

export const AnimatedProgress: React.FC<AnimatedProgressProps> = ({
  value,
  max = 100,
  className = "",
  indicatorClassName = "bg-blue-600",
  ...props
}) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  return (
    <div
      className={`relative h-2 w-full overflow-hidden rounded-full bg-gray-800 ${className}`}
      {...props}
    >
      <div
        className={`h-full rounded-full transition-all duration-700 ease-out shadow-sm ${indicatorClassName}`}
        style={{ width: `${percentage}%` }}
      />
    </div>
  );
};

export { AnimatedProgress as ProgressBar };
export type { AnimatedProgressProps as ProgressBarProps };
