type Cta = { href: string; label: string; primary?: boolean }

// Empty-state rico e consistente: titulo + orientacao + proximo passo.
// Usa a classe .empty (centralizada, com marca ✦ via CSS).
export function EmptyState({ title, hint, ctas }: { title: string; hint?: string; ctas?: Cta[] }) {
  return (
    <div className="empty">
      <strong style={{ color: '#fff4e7', fontSize: '1rem' }}>{title}</strong>
      {hint ? <span className="muted small" style={{ maxWidth: '54ch' }}>{hint}</span> : null}
      {ctas && ctas.length ? (
        <div style={{ display: 'flex', gap: 8, marginTop: 8, flexWrap: 'wrap', justifyContent: 'center' }}>
          {ctas.map((c) => (
            <a key={c.href} className={c.primary ? 'primaryLink' : 'secondaryLink'} href={c.href}>{c.label}</a>
          ))}
        </div>
      ) : null}
    </div>
  )
}
