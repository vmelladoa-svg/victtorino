"use client";

import { useStore } from "@/lib/store-context";

export function InstallTermsLink({ children }: { children: React.ReactNode }) {
  const { openInstallTerms } = useStore();
  return (
    <button type="button" className="foot-linkbtn" onClick={openInstallTerms}>
      {children}
    </button>
  );
}
