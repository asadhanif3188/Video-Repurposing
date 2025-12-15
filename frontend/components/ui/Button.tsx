import * as React from "react";
import { cn } from "@/lib/utils";

export interface ButtonProps
    extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: "primary" | "secondary" | "outline" | "ghost";
    size?: "sm" | "md" | "lg";
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant = "primary", size = "md", ...props }, ref) => {
        return (
            <button
                ref={ref}
                className={cn(
                    "inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none",
                    {
                        "bg-zinc-900 text-zinc-50 hover:bg-zinc-900/90":
                            variant === "primary",
                        "bg-zinc-100 text-zinc-900 hover:bg-zinc-100/80":
                            variant === "secondary",
                        "border border-zinc-200 bg-white hover:bg-zinc-100 hover:text-zinc-900":
                            variant === "outline",
                        "hover:bg-zinc-100 hover:text-zinc-900": variant === "ghost",
                        "h-9 px-3 text-sm": size === "sm",
                        "h-10 px-4 py-2": size === "md",
                        "h-11 px-8 rounded-md": size === "lg",
                    },
                    className
                )}
                {...props}
            />
        );
    }
);
Button.displayName = "Button";

export { Button };
