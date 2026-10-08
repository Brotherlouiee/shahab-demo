import { useEffect, useRef, useState } from "react";

import logoUrl from "../../../assets/shahab-logo.png";
import aboutPaymentUrl from "../../../assets/teal-mobile-payment-essentials.webp";
import { toPersianDigits } from "../loan-details/toPersianDigits.mjs";

const maximumProfilePhotoBytes = 100 * 1024;

function AccountHeader({ title, onBack }) {
  return (
    <header className="account-header">
      <button type="button" className="account-back" onClick={onBack} aria-label="بازگشت">←</button>
      <strong>{title}</strong>
      <a className="account-brand" href="/" onClick={(event) => { event.preventDefault(); onBack(); }}>
        <img src={logoUrl} alt="شهاب" />
      </a>
    </header>
  );
}

export function ProfileScreen({ profile, onSave, onBack }) {
  const [draft, setDraft] = useState(profile);
  const [photoUrl, setPhotoUrl] = useState("");
  const [photoError, setPhotoError] = useState("");
  const fileInput = useRef(null);

  useEffect(() => () => { if (photoUrl) URL.revokeObjectURL(photoUrl); }, [photoUrl]);

  function update(field, value) {
    setDraft((current) => ({ ...current, [field]: value }));
  }

  function choosePhoto(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    if (file.size > maximumProfilePhotoBytes) {
      setPhotoError("حجم عکس پروفایل باید حداکثر ۱۰۰ کیلوبایت باشد.");
      event.target.value = "";
      return;
    }
    setPhotoError("");
    setPhotoUrl((current) => {
      if (current) URL.revokeObjectURL(current);
      return URL.createObjectURL(file);
    });
  }

  return (
    <main className="account-page account-profile-page">
      <AccountHeader title="پروفایل کاربر" onBack={onBack} />
      <form className="account-profile-form" onSubmit={(event) => { event.preventDefault(); onSave(draft); }}>
        <button type="button" className="account-photo-picker" onClick={() => fileInput.current?.click()} aria-label="بارگذاری عکس پروفایل">
          {photoUrl ? <img src={photoUrl} alt="عکس پروفایل" /> : <span>＋</span>}
        </button>
        <input ref={fileInput} className="account-file-input" type="file" accept="image/*" onChange={choosePhoto} />
        {photoError ? <p className="account-field-error" role="alert">{photoError}</p> : null}
        <label>شماره تلفن همراه<input value={toPersianDigits(draft.phone || "")} readOnly aria-label="شماره تلفن همراه" /></label>
        <label>نام<input value={draft.firstName || ""} onChange={(event) => update("firstName", event.target.value)} /></label>
        <label>نام خانوادگی<input value={draft.lastName || ""} onChange={(event) => update("lastName", event.target.value)} /></label>
        <label>میزان درآمد ماهانه<input value={draft.income || ""} onChange={(event) => update("income", event.target.value)} /></label>
        <label>شغل<input value={draft.job || ""} onChange={(event) => update("job", event.target.value)} /></label>
        <label>جنسیت
          <select value={draft.gender || ""} onChange={(event) => update("gender", event.target.value)}>
            <option value="">انتخاب کنید</option><option value="female">زن</option><option value="male">مرد</option><option value="other">ترجیح می‌دهم اعلام نکنم</option>
          </select>
        </label>
        <button className="account-primary-button" type="submit">ذخیره تغییرات</button>
      </form>
    </main>
  );
}

export function SavedLoansScreen({ loans, onBack, onDetails }) {
  return (
    <main className="account-page">
      <AccountHeader title="وام‌های نشان شده" onBack={onBack} />
      <section className="account-saved-loans">
        {loans.length ? loans.map((loan) => (
          <button key={loan.loanId} type="button" className="account-saved-loan-card" onClick={() => onDetails(loan.loanId)}>
            <span>{loan.lenderName || loan.bankName || "ارائه‌دهندهٔ وام"}</span>
            <strong>{loan.loanName || loan.name || "جزئیات وام"}</strong>
            <small>مشاهده جزئیات ←</small>
          </button>
        )) : <p className="account-empty-state">هنوز وامی را نشان نکرده‌اید.</p>}
      </section>
    </main>
  );
}

export function AboutScreen({ onBack }) {
  return (
    <main className="account-page account-about-page">
      <AccountHeader title="درباره ما" onBack={onBack} />
      <img className="account-about-image" src={aboutPaymentUrl} alt="پرداخت و مدیریت مالی دیجیتال" />
      <section className="account-about-copy">
        <h1>شهاب؛ همراه شما در انتخاب آگاهانه وام</h1>
        <p>شهاب به شما کمک می‌کند شرایط وام‌های منتشرشده را با نیازها و ترجیحاتتان مقایسه کنید تا بررسی گزینه‌ها ساده‌تر و شفاف‌تر شود.</p>
        <p>نتیجهٔ شهاب پیشنهاد قطعی یا تضمین دریافت وام نیست؛ تصمیم نهایی و تأیید وام با بانک و ارائه‌دهندهٔ تسهیلات است.</p>
      </section>
    </main>
  );
}
