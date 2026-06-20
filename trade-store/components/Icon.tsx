export const ICONS: Record<string, string> = {
  cart: "M6 6h15l-1.5 9h-12z|M6 6L5 3H2|M9 21a1 1 0 100-2 1 1 0 000 2z|M18 21a1 1 0 100-2 1 1 0 000 2z",
  search: "M11 19a8 8 0 100-16 8 8 0 000 16z|M21 21l-4.35-4.35",
  truck: "M1 7h14v10H1z|M15 11h4l4 4v2h-8z|M6 19a2 2 0 100-4 2 2 0 000 4z|M18 19a2 2 0 100-4 2 2 0 000 4z",
  shield: "M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z|M9 12l2 2 4-4",
  lock: "M5 11h14v10H5z|M8 11V7a4 4 0 018 0v4",
  chat: "M21 12a8 8 0 01-8 8H4l2-3a8 8 0 1115-5z",
  check: "M20 6L9 17l-5-5",
  drop: "M12 2s6 7 6 12a6 6 0 11-12 0c0-5 6-12 6-12z",
  mirror: "M12 21a7 7 0 007-7c0-5-3-10-7-12-4 2-7 7-7 12a7 7 0 007 7z|M9 9c1-2 2-3 3-4",
  faucet: "M4 12h10a4 4 0 014 4v2h-4v-2H4z|M9 12V7h4|M11 4a2 2 0 100 .01|M20 20c0 1-2 1-2 0 0-1 1-2 1-2s1 1 1 2",
  sink: "M3 12h18l-2 7H5z|M12 12V5a2 2 0 014 0",
  shower: "M4 4h6a4 4 0 014 4v1|M14 12h.01M11 14h.01M17 14h.01M14 17h.01M8 12h.01M20 12h.01",
  wc: "M6 3h8v8H6z|M6 11h12a6 6 0 01-6 6h-2l1 4H8z",
  tools: "M14 7a4 4 0 015 5l-7 7-3-3 7-7z|M5 21l3-3",
  star: "M12 2l3 7h7l-5.5 4.5L18 21l-6-4-6 4 1.5-7.5L2 9h7z",
  arrow: "M5 12h14|M13 6l6 6-6 6",
  box: "M21 8l-9-5-9 5v8l9 5 9-5z|M3 8l9 5 9-5|M12 13v8",
  menu: "M3 6h18|M3 12h18|M3 18h18",
  close: "M6 6l12 12|M18 6L6 18",
  up: "M18 15l-6-6-6 6",
  phone: "M5 4h4l2 5-2.5 1.5a11 11 0 005 5L15 13l5 2v4a2 2 0 01-2 2A16 16 0 013 6a2 2 0 012-2z",
};

export function Heart({ filled = false, size = 20 }: { filled?: boolean; size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill={filled ? "currentColor" : "none"}
      stroke="currentColor"
      strokeWidth={1.8}
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M20.8 4.6a5.5 5.5 0 00-7.8 0L12 5.6l-1-1a5.5 5.5 0 00-7.8 7.8l1 1L12 21l7.8-7.6 1-1a5.5 5.5 0 000-7.8z" />
    </svg>
  );
}

export function Icon({
  d,
  size = 20,
  stroke = 1.8,
}: {
  d: string;
  size?: number;
  stroke?: number;
}) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={stroke}
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      {d.split("|").map((p, i) => (
        <path key={i} d={p} />
      ))}
    </svg>
  );
}
