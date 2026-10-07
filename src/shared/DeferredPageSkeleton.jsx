import { useEffect, useState } from "react";

/**
 * Product-wide delayed loading placeholder. It prevents a loading message or
 * blank data region from appearing when a real request exceeds 50ms. Variants
 * expose only the geometry of the route; they never create loan data or state.
 */
const shapes = {
  cards: (
    <div className="hp-skeleton-cards">
      <span className="hp-skeleton-block hp-skeleton-heading" />
      <span className="hp-skeleton-block hp-skeleton-filter" />
      <span className="hp-skeleton-block hp-skeleton-loan-card" />
      <span className="hp-skeleton-block hp-skeleton-loan-card" />
    </div>
  ),
  detail: (
    <div className="hp-skeleton-detail">
      <span className="hp-skeleton-block hp-skeleton-heading" />
      <span className="hp-skeleton-block hp-skeleton-summary" />
      <span className="hp-skeleton-block hp-skeleton-detail-group" />
      <span className="hp-skeleton-block hp-skeleton-detail-group" />
      <span className="hp-skeleton-block hp-skeleton-bottom-action" />
    </div>
  ),
  questionnaire: (
    <div className="hp-skeleton-questionnaire">
      <span className="hp-skeleton-block hp-skeleton-stage" />
      <span className="hp-skeleton-block hp-skeleton-question-title" />
      <span className="hp-skeleton-block hp-skeleton-option" />
      <span className="hp-skeleton-block hp-skeleton-option" />
      <span className="hp-skeleton-block hp-skeleton-next-action" />
    </div>
  ),
};

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
      {shapes[variant] || shapes.cards}
    </section>
  );
}
