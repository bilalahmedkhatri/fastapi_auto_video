"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

const Slider = React.forwardRef(({ 
  className, 
  value = [0],
  min = 0,
  max = 100,
  step = 1,
  onValueChange,
  disabled,
  orientation = "horizontal",
  ...props 
}, ref) => {
  const [internalValue, setInternalValue] = React.useState(value)
  const sliderRef = React.useRef(null)
  const isDragging = React.useRef(false)
  
  React.useEffect(() => {
    setInternalValue(value)
  }, [value])
  
  const getValue = (clientX, clientY) => {
    if (!sliderRef.current) return internalValue[0]
    
    const rect = sliderRef.current.getBoundingClientRect()
    let percentage
    
    if (orientation === "horizontal") {
      percentage = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width))
    } else {
      percentage = Math.max(0, Math.min(1, 1 - (clientY - rect.top) / rect.height))
    }
    
    const rawValue = min + percentage * (max - min)
    return Math.round(rawValue / step) * step
  }
  
  const handleMouseDown = (e) => {
    if (disabled) return
    
    isDragging.current = true
    const newValue = getValue(e.clientX, e.clientY)
    const newValueArray = [newValue]
    
    setInternalValue(newValueArray)
    onValueChange?.(newValueArray)
    
    e.preventDefault()
  }
  
  const handleMouseMove = (e) => {
    if (!isDragging.current || disabled) return
    
    const newValue = getValue(e.clientX, e.clientY)
    const newValueArray = [newValue]
    
    setInternalValue(newValueArray)
    onValueChange?.(newValueArray)
  }
  
  const handleMouseUp = () => {
    isDragging.current = false
  }
  
  React.useEffect(() => {
    if (isDragging.current) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
      
      return () => {
        document.removeEventListener('mousemove', handleMouseMove)
        document.removeEventListener('mouseup', handleMouseUp)
      }
    }
  }, [isDragging.current, disabled, min, max, step])
  
  const percentage = ((internalValue[0] - min) / (max - min)) * 100
  
  return (
    <div
      ref={ref}
      className={cn(
        "relative flex w-full touch-none select-none items-center",
        orientation === "vertical" && "h-full w-4 flex-col",
        className
      )}
      {...props}
    >
      <div
        ref={sliderRef}
        className={cn(
          "relative grow overflow-hidden rounded-full bg-gray-200",
          orientation === "horizontal" ? "h-2 w-full" : "h-full w-2",
          disabled && "opacity-50 cursor-not-allowed"
        )}
        onMouseDown={handleMouseDown}
      >
        <div
          className={cn(
            "absolute bg-blue-600 rounded-full",
            orientation === "horizontal" ? "h-full" : "w-full"
          )}
          style={{
            [orientation === "horizontal" ? "width" : "height"]: `${percentage}%`,
            [orientation === "horizontal" ? "left" : "bottom"]: 0,
          }}
        />
        <div
          className={cn(
            "absolute h-5 w-5 rounded-full border-2 border-blue-600 bg-white shadow transition-colors hover:bg-gray-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 disabled:pointer-events-none",
            disabled && "border-gray-400"
          )}
          style={{
            [orientation === "horizontal" ? "left" : "bottom"]: `calc(${percentage}% - 10px)`,
            [orientation === "horizontal" ? "top" : "left"]: "50%",
            transform: orientation === "horizontal" ? "translateY(-50%)" : "translateX(-50%)",
          }}
        />
      </div>
    </div>
  )
})
Slider.displayName = "Slider"

export { Slider }
