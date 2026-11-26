export interface DonutPart { label: string; value: number; pct?: number; color: string }

export function DonutSvg({ parts, centro }: { parts: DonutPart[]; centro?: React.ReactNode }) {
  const total = parts.reduce((s, p) => s + p.value, 0);
  const R = 58, C = 2 * Math.PI * R;
  const gap = parts.filter((p) => p.value > 0).length > 1 ? 3 : 0;
  const visibles = parts.filter((p) => p.value > 0);
  // Cada segmento arranca donde termina el anterior
  const offsets = visibles.map((_, i) => visibles.slice(0, i).reduce((s, p) => s + (p.value / total) * C, 0));
  return (
    <div className="donut-wrap">
      <svg viewBox="0 0 140 140" role="img" aria-label="Composición de la cartera">
        <circle r={R} cx="70" cy="70" fill="none" stroke="var(--card2)" strokeWidth="14" />
        {visibles.map((p, i) => {
          const len = (p.value / total) * C;
          return (
            <circle key={p.label} r={R} cx="70" cy="70" fill="none" stroke={p.color} strokeWidth="14" strokeLinecap="butt"
              strokeDasharray={`${Math.max(len - gap, 0.5).toFixed(2)} ${(C - len + gap).toFixed(2)}`}
              strokeDashoffset={(-offsets[i]).toFixed(2)} transform="rotate(-90 70 70)" />
          );
        })}
      </svg>
      {centro && <div className="donut-center">{centro}</div>}
    </div>
  );
}

export function Legend({ parts }: { parts: DonutPart[] }) {
  const total = parts.reduce((s, p) => s + p.value, 0);
  return (
    <div className="legend">
      {parts.filter((p) => p.value > 0).map((p) => (
        <div key={p.label}>
          <span><span className="sw" style={{ background: p.color }} />{p.label}</span>
          <b>{(p.pct != null ? p.pct : (p.value / total) * 100).toFixed(1).replace(".", ",")}%</b>
        </div>
      ))}
    </div>
  );
}

export function Donut({ parts }: { parts: DonutPart[] }) {
  const total = parts.reduce((s, p) => s + p.value, 0);
  if (total <= 0) return <div className="empty">Sin tenencias todavía.</div>;
  return <div className="alloc"><DonutSvg parts={parts} /><Legend parts={parts} /></div>;
}

