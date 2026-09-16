import { useState } from "react";
import logoUrl from "../assets/logo.svg";

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
    className: "is-complete narrow-2",
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

const loanPlans = [
  {
    bank: "بانک ملت",
    title: "طرح نیک وام",
    match: 75,
    amount: "۲۰۰ میلیون تومان",
    rate: "٪۲۵",
    duration: "۱۸ ماه",
  },
  {
    bank: "بانک ملی",
    title: "طرح ۳۰۰ میلیونی",
    match: 75,
    amount: "۲۰۰ میلیون تومان",
    rate: "٪۲۵",
    duration: "۱۸ ماه",
  },
  {
    bank: "بانک اقتصاد نوین",
    title: "طرح خرید مسکن",
    match: 75,
    amount: "۲۰۰ میلیون تومان",
    rate: "٪۲۵",
    duration: "۱۸ ماه",
  },
  {
    bank: "بانک سامان",
    title: "طرح ۲۰۰ میلیونی",
    match: 35,
    amount: "۲۰۰ میلیون تومان",
    rate: "٪۲۵",
    duration: "۱۸ ماه",
  },
  {
    bank: "بانک ملت",
    title: "طرح نیک وام",
    match: 75,
    amount: "۲۰۰ میلیون تومان",
    rate: "٪۲۵",
    duration: "۱۸ ماه",
  },
  {
    bank: "بانک سامان",
    title: "طرح ۳۰۰ میلیونی",
    match: 75,
    amount: "۲۰۰ میلیون تومان",
    rate: "٪۲۵",
    duration: "۱۸ ماه",
  },
  {
    bank: "بانک اقتصاد نوین",
    title: "طرح خرید مسکن",
    match: 75,
    amount: "۲۰۰ میلیون تومان",
    rate: "٪۲۵",
    duration: "۱۸ ماه",
  },
  {
    bank: "بانک سامان",
    title: "طرح ۲۰۰ میلیونی",
    match: 35,
    amount: "۲۰۰ میلیون تومان",
    rate: "٪۲۵",
    duration: "۱۸ ماه",
  },
];

const requirements = [
  "یک ضامن کارمند یا کاسب",
  "یک فقره چک",
  "یک ضامن کارمند یا کاسب",
  "دارای حساب قرض‌الحسنه در نزد شعب این بانک که بین ۱ تا ۱۲ ماه",
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
          <div className="brand-text">شهاب (شبکه همرسانی اعتبار برخط)</div>
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

function SelectBox({ label }) {
  return (
    <button className="select-box" type="button">
      <span className="select-chevron" aria-hidden="true" />
      <span>{label}</span>
    </button>
  );
}

function LoanStat({ label, value, multiline = false }) {
  return (
    <div className={`loan-stat${multiline ? " is-tall" : ""}`}>
      <span className="loan-value">{value}</span>
      <span className="loan-label">{label}</span>
    </div>
  );
}

function LoanCard({ plan }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <article className={`loan-card${isExpanded ? " is-expanded" : ""}`}>
      <div className="loan-card-inner">
        <header className="loan-card-header">
          <div className="loan-logo-space" aria-hidden="true" />
          <span className="loan-bank">«{plan.bank}»</span>
          <strong className="loan-title">{plan.title}</strong>
        </header>

        <div className="loan-separator" />

        <div className="match-row">
          <div className="match-meter">
            <span className="match-percent">٪{plan.match}</span>
            <span className="match-track">
              <span
                className="match-fill"
                style={{ width: `${plan.match}%` }}
              />
            </span>
          </div>
          <span className="match-label">درصد تطابق</span>
        </div>

        <LoanStat label="مبلغ وام" value={plan.amount} />
        <LoanStat label="درصد بهره" value={plan.rate} />
        <LoanStat label="مدت بازپرداخت" value={plan.duration} />
        <LoanStat
          label="مشتریان هدف"
          value={
            <>
              دارندگان دستگاه کارت خوان
              <br />
              سپرده گذاران
            </>
          }
          multiline
        />

        <button
          className="requirements-title"
          type="button"
          aria-expanded={isExpanded}
          onClick={() => setIsExpanded((current) => !current)}
        >
          <span className="tiny-chevron" aria-hidden="true" />
          <span>شرایط و مدارک</span>
        </button>

        {isExpanded ? (
          <ul className="requirements-list">
            {requirements.map((item, index) => (
              <li key={`${item}-${index}`}>{item}</li>
            ))}
          </ul>
        ) : null}
      </div>
    </article>
  );
}

function MainContent() {
  return (
    <section className="content">
      <div className="top-panel">
        <AlertBox />
        <div className="main-divider" />
      </div>

      <div className="loan-area">
        <div className="filters-row">
          <SelectBox label="نام بانک" />
          <SelectBox label="مرتب سازی تطابق بر اساس" />
        </div>

        <div className="loan-grid">
          {loanPlans.map((plan, index) => (
            <LoanCard key={`${plan.bank}-${plan.title}-${index}`} plan={plan} />
          ))}
        </div>
      </div>

      <div className="bottom-action">
        <button className="submit-button" type="button">
          ثبت درخواست وام بانکی
        </button>
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
