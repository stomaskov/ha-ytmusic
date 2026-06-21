export function formatTime(sec: number | null | undefined): string {
  if (sec == null || !isFinite(sec) || sec < 0) return "0:00";
  const s = Math.floor(sec);
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const ss = String(s % 60).padStart(2, "0");
  return h > 0 ? `${h}:${String(m).padStart(2, "0")}:${ss}` : `${m}:${ss}`;
}

export function joinArtists(a: string | string[] | undefined): string {
  if (!a) return "";
  return Array.isArray(a) ? a.filter(Boolean).join(", ") : a;
}
