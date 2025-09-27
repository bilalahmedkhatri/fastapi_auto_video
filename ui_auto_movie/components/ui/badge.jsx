import * as React from "react"
import { cn } from "@/lib/utils"

const badgeVariants = {
  variant: {
    default: "border-transparent bg-blue-600 text-white",
    secondary: "border-transparent bg-gray-200 text-gray-900",
    destructive: "border-transparent bg-red-600 text-white",
    outline: "border-gray-300 text-gray-900",
  },
}

function Badge({ className, variant = "default", ...props }) {
  const variantClasses = badgeVariants.variant[variant] || badgeVariants.variant.default
  
  return (
    <div 
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2",
        variantClasses,
        className
      )} 
      {...props} 
    />
  )
}

export { Badge }
