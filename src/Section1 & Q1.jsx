import { useState } from "react";
import logoUrl from "../assets/logo.svg";
import businessLoanUrl from "../assets/business-loan.png";
import personLoanUrl from "../assets/person-loan.png";

const steps = [
  {
    number: "۱",
    title: "ثبت اطلاعات شخصی",
    className: "active-step narrow-1",
    titleClassName: "step-1",
  },
  {
    number: "۲",
    title: "ثبت سوابق مالی",
    className: "is-complete",
    titleClassName: "step-2",
  },
  {
    number: "۳",
    title: "ثبت سوابق مالی",
    className: "is-complete narrow-3",
    titleClassName: "step-3",
  },
  {
    number: "۴",
    title: "مرور و تایید صحت اطلاعات",
    className: "is-complete narrow-4",
    titleClassName: "step-4",
  },
];

function Stepper() {
  return (
    <div className="stepper-container">
      {steps.map((step) => (
        <div key={step.number} className={`step ${step.className}`}>
          <div className="step-icon-wrapper">
            <span className="step-number">{step.number}</span>
          </div>
          <span className={`step-title ${step.titleClassName}`}>
            {step.title}
          </span>
        </div>
      ))}
    </div>
  );
}

function BrandPanel() {
  return (
    <aside className="sidebar">
      <div className="brand-wrap">
        <div className="brand-row">
          <img className="logo-img logo-fallback" src={logoUrl} alt="" />
          <div className="brand-text">
            شهاب (شبکه هم‌رسانی اعتبار برخط)
          </div>
        </div>

        <Stepper />
      </div>

      <div className="support-line" />
      <p className="support-text">
        جهت دریافت مشاوره با شماره تلفن ۳۵۶۴۷-۰۲۱ <br />
        تماس حاصل نمایید.
      </p>
    </aside>
  );
}

function AlertBox() {
  return (
    <div className="alert">
      <div className="alert-inner">
        <button className="alert-button" type="button">
          محاسبه وام شهاب
        </button>
        <div className="alert-message-wrap">
          <div className="alert-icon" aria-hidden="true">
            <span className="alert-mark" />
          </div>
          <p className="alert-text">
            اگر هیچ یک از وام‌های بانکی متناسب با شرایط شما نیست «وام شهاب»
            دلخواه خود را
            <br />
            محاسبه و ثبت درخواست نمایید.
          </p>
        </div>
      </div>
    </div>
  );
}

function LoanCard({ type, title, label, imageUrl, selected, onSelect }) {
  const checkboxId = `${type}-loan-choice`;

  return (
    <article className={`loan-choice-card card-${type}${selected ? " is-selected" : ""}`}>
      <button
        className="loan-choice-button"
        type="button"
        aria-pressed={selected}
        aria-labelledby={`${checkboxId}-label`}
        onClick={onSelect}
      >
        <div className={`loan-image ${type}-image`}>
          <img src={imageUrl} alt={title} />
        </div>
        <div className="image-copy">
          <strong>{title}</strong>
        </div>
        <span className={`label-row ${type}-label-row`}>
          <span className="checkbox" aria-hidden="true">
            <span className="checkbox-tick" />
          </span>
          <span id={`${checkboxId}-label`} className={`card-label ${type}-label`}>
            {label}
          </span>
        </span>
      </button>
    </article>
  );
}

function MainContent() {
  const [selectedType, setSelectedType] = useState(null);

  return (
    <section className="content">
      <div className="figma-main">
        <AlertBox />

        <div className="main-divider" />

        <div className="cards">
          <LoanCard
            type="business"
            title="وام برای کسب‌وکارها"
            label="به عنوان یک کسب و کارم نیازمند اعتبار هستم."
            imageUrl={businessLoanUrl}
            selected={selectedType === "business"}
            onSelect={() =>
              setSelectedType((current) => (current === "business" ? null : "business"))
            }
          />
          <LoanCard
            type="person"
            title="وام برای اشخاص"
            label="به عنوان یک شخص نیازمند اعتبار هستم."
            imageUrl={personLoanUrl}
            selected={selectedType === "person"}
            onSelect={() =>
              setSelectedType((current) => (current === "person" ? null : "person"))
            }
          />
        </div>
      </div>
    </section>
  );
}

export default function App() {
  return (
    <main className="page">
      <BrandPanel />
      <MainContent />
    </main>
  );
}
