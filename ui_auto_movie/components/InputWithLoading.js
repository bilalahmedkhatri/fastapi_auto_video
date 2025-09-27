'use client';

import React from 'react';

export default function InputWithLoading({
  id,
  name,
  type = 'text',
  value,
  onChange,
  disabled,
  placeholder,
  className = '',
  isLoading = false,
  rows, // For textarea
}) {
  const baseClasses = "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500";
  
  // Combine provided classes with base classes
  const fullClassName = `${baseClasses} ${className} ${isLoading ? 'opacity-70' : ''}`;
  
  // Determine if it's a textarea or input
  const isTextarea = type === 'textarea';
  
  return (
    <div className="relative">
      {isTextarea ? (
        <textarea
          id={id}
          name={name}
          rows={rows || 3}
          className={fullClassName}
          value={value || ''}
          onChange={onChange}
          disabled={disabled || isLoading}
          placeholder={placeholder}
        />
      ) : (
        <input
          id={id}
          name={name}
          type={type}
          className={fullClassName}
          value={value || ''}
          onChange={onChange}
          disabled={disabled || isLoading}
          placeholder={placeholder}
        />
      )}
      
      {isLoading && (
        <div className="absolute right-2 top-1/2 transform -translate-y-1/2">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-indigo-500"></div>
        </div>
      )}
    </div>
  );
}
