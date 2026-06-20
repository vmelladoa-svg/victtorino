"use client";

import { useStore } from "@/lib/store-context";
import { Icon, ICONS } from "./Icon";

export function Toast() {
  const { toast } = useStore();
  if (!toast) return null;
  return (
    <div className="toast">
      <Icon d={ICONS.check} size={16} /> {toast}
    </div>
  );
}
