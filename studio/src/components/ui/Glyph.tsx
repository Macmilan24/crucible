// The Crucible brand glyph — one mark used everywhere (sidebar, chat, empty
// states), always the ember gradient per the design system. The gradient + shape
// are defined once by <GlyphDefs/> at the app root; each <Glyph/> references it.

export function GlyphDefs() {
  return (
    <svg width="0" height="0" className="absolute" aria-hidden="true">
      <defs>
        <linearGradient id="crucible-ember" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#ff4d4d" />
          <stop offset="100%" stopColor="#f9cb28" />
        </linearGradient>
        {/* A crucible: a forge vessel (triangle) refining a molten core (circle). */}
        <g id="crucible-glyph">
          <path d="M12 2L22 19H2L12 2Z" fill="url(#crucible-ember)" />
          <circle cx="12" cy="14" r="3" fill="#ffffff" />
        </g>
      </defs>
    </svg>
  );
}

export function Glyph({ size = 24, className = "" }: { size?: number; className?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" className={className} aria-hidden="true">
      <use href="#crucible-glyph" />
    </svg>
  );
}
