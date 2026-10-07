import { useEffect, useState } from "react";

/**
 * Product-wide delayed loading placeholder. It prevents a loading message or
 * blank data region from appearing when a real request exceeds 50ms.
 */
export default function DeferredPageSkeleton({ active, variant = "cards" }) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (!active) {
      setVisible(false);
      return undefined;
    }
    const timer = window.setTimeout(() => setVisible(true), 50);
    return () => window.clearTimeout(timer);
  }, [active]);

  if (!visible) return null;

  return (
    <section className={"hp-deferred-skeleton is-" + variant} role="status" aria-label="در حال بارگذاری">
      <span className="hp-skeleton-line hp-skeleton-title" />
      <span className="hp-skeleton-line" />
      <span className="hp-skeleton-line" />
      <span className="hp-skeleton-card" />
    </section>
  );
}
