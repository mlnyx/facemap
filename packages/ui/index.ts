import * as React from "react";

export const GlassCard: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="backdrop-blur-xl bg-white/60 rounded-3xl shadow-xl px-8 py-12 flex flex-col items-center">
    {children}
  </div>
);
