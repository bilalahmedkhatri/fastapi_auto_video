"use client"

import * as React from "react"
import { Check, ChevronDown } from "lucide-react"
import { cn } from "../../lib/utils"

const Select = React.forwardRef(({ children, value, onValueChange, ...props }, ref) => {
  const [isOpen, setIsOpen] = React.useState(false)
  const [selectedValue, setSelectedValue] = React.useState(value || '')
  
  const handleValueChange = (newValue) => {
    setSelectedValue(newValue)
    onValueChange?.(newValue)
    setIsOpen(false)
  }
  
  return (
    <div className="relative" ref={ref} {...props}>
      {React.Children.map(children, child => {
        if (child?.type?.displayName === 'SelectTrigger') {
          return React.cloneElement(child, { 
            onClick: () => setIsOpen(!isOpen),
            isOpen,
            selectedValue 
          })
        }
        if (child?.type?.displayName === 'SelectContent') {
          return React.cloneElement(child, { 
            isOpen,
            onValueChange: handleValueChange,
            selectedValue 
          })
        }
        return child
      })}
    </div>
  )
})
Select.displayName = "Select"

const SelectTrigger = React.forwardRef(({ className, children, onClick, isOpen, selectedValue, ...props }, ref) => (
  <button
    ref={ref}
    className={cn(
      "flex h-10 w-full items-center justify-between rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
      className
    )}
    onClick={onClick}
    type="button"
    {...props}
  >
    {children}
    <ChevronDown className={cn("h-4 w-4 opacity-50 transition-transform", isOpen && "rotate-180")} />
  </button>
))
SelectTrigger.displayName = "SelectTrigger"

const SelectValue = React.forwardRef(({ placeholder, ...props }, ref) => (
  <span ref={ref} className="text-gray-900 dark:text-gray-100" {...props}>
    {props.children || placeholder}
  </span>
))
SelectValue.displayName = "SelectValue"

const SelectContent = React.forwardRef(({ className, children, isOpen, onValueChange, selectedValue, ...props }, ref) => {
  if (!isOpen) return null
  
  return (
    <div
      ref={ref}
      className={cn(
        "absolute z-50 mt-1 max-h-96 min-w-[8rem] w-full overflow-hidden rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 shadow-md",
        className
      )}
      {...props}
    >
      <div className="p-1">
        {React.Children.map(children, child => 
          React.cloneElement(child, { onValueChange, selectedValue })
        )}
      </div>
    </div>
  )
})
SelectContent.displayName = "SelectContent"

const SelectItem = React.forwardRef(({ className, children, value, onValueChange, selectedValue, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "relative flex w-full cursor-pointer select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none hover:bg-gray-100 dark:hover:bg-gray-700 focus:bg-gray-100 dark:focus:bg-gray-700 text-gray-900 dark:text-gray-100",
      selectedValue === value && "bg-blue-50 dark:bg-blue-900 text-blue-900 dark:text-blue-200",
      className
    )}
    onClick={() => onValueChange?.(value)}
    {...props}
  >
    <span className="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">
      {selectedValue === value && <Check className="h-4 w-4" />}
    </span>
    {children}
  </div>
))
SelectItem.displayName = "SelectItem"

export {
  Select,
  SelectTrigger,
  SelectContent,
  SelectItem,
  SelectValue,
}
