import * as React from "react"
import { cn } from "../../lib/utils"

const badgeVariants = (variant) => {
  const base = "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
  
  const variants = {
    default: "border-transparent bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200",
    secondary: "border-transparent bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100",
    destructive: "border-transparent bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200",
    outline: "border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100"
  }
  
  return cn(base, variants[variant] || variants.default)
}

const Badge = React.forwardRef(({ className, variant = "default", ...props }, ref) => {
  return (
    <div
      ref={ref}
      className={cn(badgeVariants(variant), className)}
      {...props}
    />
  )
})
Badge.displayName = "Badge"

export { Badge, badgeVariants }
