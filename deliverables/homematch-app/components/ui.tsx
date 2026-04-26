import React from "react";

export function Button({
  children,
  variant = "primary",
  className = "",
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "outline" | "ghost";
}) {
  const base =
    "inline-flex items-center justify-center px-6 py-3 rounded-3xl font-medium transition-all duration-200 text-sm";
  const variants = {
    primary: "bg-slate-900 text-white hover:bg-slate-800 shadow-sm",
    secondary: "bg-brand-700 text-white hover:bg-brand-800 shadow-sm",
    outline:
      "border border-slate-300 text-slate-700 hover:bg-slate-100 bg-white",
    ghost: "text-slate-600 hover:bg-slate-100",
  };
  return (
    <button className={`${base} ${variants[variant]} ${className}`} {...props}>
      {children}
    </button>
  );
}

export function Card({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={`bg-white rounded-4xl shadow-sm border border-slate-100 overflow-hidden ${className}`}
    >
      {children}
    </div>
  );
}

export function Container({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={`max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 ${className}`}>
      {children}
    </div>
  );
}

export function SectionHeading({
  title,
  subtitle,
}: {
  title: string;
  subtitle?: string;
}) {
  return (
    <div className="mb-10 text-center">
      <h2 className="font-serif text-3xl sm:text-4xl text-slate-900 mb-3">
        {title}
      </h2>
      {subtitle && (
        <p className="text-slate-500 text-lg max-w-2xl mx-auto">{subtitle}</p>
      )}
    </div>
  );
}

export function Badge({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <span
      className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-700 ${className}`}
    >
      {children}
    </span>
  );
}

export function Input({
  className = "",
  ...props
}: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={`w-full px-4 py-3 rounded-2xl border border-slate-200 bg-white text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all ${className}`}
      {...props}
    />
  );
}

export function TextArea({
  className = "",
  ...props
}: React.TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      className={`w-full px-4 py-3 rounded-2xl border border-slate-200 bg-white text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all resize-none ${className}`}
      {...props}
    />
  );
}

export function Select({
  className = "",
  children,
  ...props
}: React.SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select
      className={`w-full px-4 py-3 rounded-2xl border border-slate-200 bg-white text-slate-800 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all appearance-none ${className}`}
      {...props}
    >
      {children}
    </select>
  );
}
