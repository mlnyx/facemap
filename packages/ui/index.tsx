import * as React from "react";

export const GlassCard: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="backdrop-blur-xl bg-white/60 rounded-3xl shadow-xl px-8 py-12 flex flex-col items-center">
    {children}
  </div>
);

export const MainButton: React.FC<React.ButtonHTMLAttributes<HTMLButtonElement>> = (props) => (
  <button
    className="rounded-xl bg-black/80 text-white py-4 text-lg font-semibold hover:bg-black/90 transition"
    {...props}
  />
);

export const SubButton: React.FC<React.ButtonHTMLAttributes<HTMLButtonElement>> = (props) => (
  <button
    className="rounded-xl bg-white/80 text-black py-4 text-lg font-semibold border border-gray-300 hover:bg-gray-100 transition"
    {...props}
  />
);
