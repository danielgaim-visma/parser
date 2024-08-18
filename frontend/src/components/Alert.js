import React from 'react';

export const Alert = ({ children, variant = 'default' }) => {
  const bgColor = variant === 'destructive' ? 'bg-red-100' : 'bg-blue-100';
  return <div className={`p-4 rounded-md ${bgColor}`}>{children}</div>;
};

export const AlertTitle = ({ children }) => (
  <h5 className="font-bold mb-2">{children}</h5>
);

export const AlertDescription = ({ children }) => (
  <p>{children}</p>
);