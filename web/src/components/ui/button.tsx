import * as React from "react";
import { clsx, type ClassValue } from "clsx";

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost";
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", ...props }, ref) => {
    const baseStyles = "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 h-10 px-4 py-2";
    
    const variants = {
      primary: "bg-blue-600 text-white hover:bg-blue-700",
      secondary: "bg-gray-800 text-gray-100 hover:bg-gray-700",
      outline: "border border-gray-700 bg-transparent hover:bg-gray-800 text-gray-100",
      ghost: "hover:bg-gray-800 hover:text-gray-100 text-gray-300",
    };

    return (
      <button
        ref={ref}
        className={cn(baseStyles, variants[variant], className)}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";
