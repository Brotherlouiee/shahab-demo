import { useEffect, useRef, useState } from "react";
import LoanDetailsScreen from "./features/loan-details/LoanDetailsScreen.jsx";
import LoanResultsScreen from "./features/recommendation/ui/LoanResultsScreen.jsx";
import LoanComparisonCard from "./features/recommendation/ui/LoanComparisonCard.jsx";
import { fetchLoanDetails } from "./features/loan-details/loanDetailsApi.js";
import BankIdentity from "./features/loan-details/BankIdentity.jsx";
import LoanPercent from "./features/loan-details/LoanPercent.jsx";
import { fetchRecommendationResult } from "./features/recommendation/presentation/recommendationResultClient.mjs";
import {
  getCanonicalQuestionIdForRoute,
  getPrototypeQuestionIndexForCanonicalQuestionId,
  getQuestionnaireRouteForPrototypeQuestionIndex,
} from "./features/questionnaire/questionnaireRouteMap.mjs";
import { getCanonicalQuestionForPrototypeIndex } from "./features/questionnaire/canonicalQuestionnaire.mjs";
import {
  saveQuestionnaireAnswer,
  startQuestionnaireSession,
} from "./features/questionnaire/questionnaireSessionClient.mjs";
import logoUrl from "../assets/shahab-logo.png";
import folderIconUrl from "../assets/folder.svg";
import healthIconUrl from "../assets/health.svg";
import profileIconUrl from "../assets/profile.svg";
import sendIconUrl from "../assets/send.svg";
import sidebarLeftIconUrl from "../assets/sidebar-left.svg";
import addCircleIconUrl from "../assets/add-circle.svg";

const bankLogoModules = import.meta.glob("../assets/iranian-bank-logos/*.{png,svg}", {
  eager: true,
  import: "default",
  query: "?url",
});
const analysisLogoUrls = [...new Set(
  Object.entries(bankLogoModules)
    .sort(([firstPath], [secondPath]) => firstPath.localeCompare(secondPath))
    .map(([, logoPath]) => logoPath)
)];

const amounts = [
  "تا ۵۰ میلیون",
  "۵۰ تا ۲۵۰ میلیون",
  "۲۵۰ میلیون تا ۱ میلیارد",
  "۱ تا ۵ میلیارد",
  "۵ تا ۱۰ میلیارد",
  "بیش از ۱۰ میلیارد تومان",
];

const cards = [
  { kind: "image", src: "https://images.unsplash.com/photo-1556761175-5973dc0f32e7?w=900&q=80", name: "سارا احمدی | کافه آرتا", desc: "با تأمین مالی سریع، شعبه دوم را افتتاح کرد" },
  { kind: "stat-dark", value: "+۱۹هزار", label: "امتیاز ۵ ستاره" },
  { kind: "stat-lime", value: "+۵۲۰هزار", label: "کسب‌وکار کوچک تأمین مالی شده", icon: "shield" },
  { kind: "image", src: "https://images.unsplash.com/photo-1542744173-8e7e53415bb0?w=900&q=80", name: "رضا کریمی | باشگاه ورزشی", desc: "وام ۵۰۰ میلیون تومانی برای تجهیز سالن" },
  { kind: "quote", text: "«وقتی زمان دریافت وام رسید، ظرف دو روز پول به حسابم واریز شد.»", name: "محمدرضا شریفی", role: "کارگاه خانوادگی هفت برادران" },
  { kind: "stat-cream", value: "+۱۵", label: "سال تجربه در صنعت" },
];

const features = [
  {
    title: "درخواست در ۱۵ دقیقه",
    desc: "فقط با چند کلیک، اطلاعات کسب‌وکارتان را وارد کنید و پیشنهاد دریافت کنید.",
  },
  {
    title: "مقایسه چندین وام‌دهنده",
    desc: "از بین ده‌ها بانک و مؤسسه مالی، بهترین گزینه را با شفاف‌ترین شرایط انتخاب کنید.",
  },
  {
    title: "بدون کارمزد پنهان",
    desc: "همه هزینه‌ها از ابتدا مشخص است. هیچ غافلگیری در پایان مسیر وجود ندارد.",
  },
  {
    title: "پشتیبانی متخصص",
    desc: "تیم مشاوران ما در هر مرحله از انتخاب وام تا دریافت وجه، در کنار شماست.",
  },
];

function Icon({ name }) {
  if (name === "star") return <span className="hp-icon hp-star">★</span>;
  if (name === "check") return <span className="hp-check">✓</span>;
  if (name === "arrow") return <span className="hp-arrow">←</span>;
  if (name === "shield") return <span className="hp-line-icon">♢</span>;
  if (name === "trend") return <span className="hp-line-icon">↗</span>;
  return <span className="hp-line-icon">○</span>;
}

function BrandMark({ footer = false, onClick }) {
  return (
    <a
      className={`hp-brand ${footer ? "hp-brand-footer" : ""}`}
      href="/"
      onClick={onClick}
    >
      <img src={logoUrl} alt="شهاب" />
      <span>
        <strong>شهاب</strong>
        <small>(شبکه همرسانی اعتبار بر خط)</small>
      </span>
    </a>
  );
}

const jobOptions = [
  { value: "employee", label: "کارمند (شرکت یا اداره)" },
  { value: "manager", label: "مدیر (واحد یا شرکت)" },
  { value: "entrepreneur", label: "کارآفرین / صاحب کسب‌وکار" },
  { value: "merchant", label: "کاسب / بازاری (فروشنده یا تاجر)" },
  { value: "freelancer", label: "فریلنسر / خوداشتغال" },
  { value: "teacher", label: "معلم / مدرس" },
  { value: "professional", label: "متخصص حرفه‌ای (پزشک، وکیل، مهندس)" },
  { value: "technical-worker", label: "کارگر / نیروی فنی (تکنسین یا تعمیرکار)" },
  { value: "driver", label: "راننده / حمل‌ونقل" },
  { value: "farmer", label: "کشاورز / دامدار" },
  { value: "homemaker", label: "خانه‌دار" },
  { value: "student", label: "دانشجو / محصل" },
  { value: "retired", label: "بازنشسته" },
  { value: "unemployed", label: "در حال حاضر بدون شغل" },
  { value: "other", label: "سایر" },
];

const incomeOptions = [
  { value: "up-to-22", label: "تا ۲۲ میلیون تومان" },
  { value: "22-to-50", label: "۲۲ تا ۵۰ میلیون تومان" },
  { value: "50-to-80", label: "۵۰ تا ۸۰ میلیون تومان" },
  { value: "80-to-120", label: "۸۰ تا ۱۲۰ میلیون تومان" },
  { value: "120-to-160", label: "۱۲۰ تا ۱۶۰ میلیون تومان" },
  { value: "160-to-250", label: "۱۶۰ تا ۲۵۰ میلیون تومان" },
  { value: "250-to-500", label: "۲۵۰ میلیون تا ۵۰۰ میلیون تومان" },
  { value: "500-to-1000", label: "۵۰۰ تا ۱ میلیارد تومان" },
  { value: "over-1000", label: "بیش از ۱ میلیارد تومان" },
];

const analysisLogoNames = [
  "بانک ملت",
  "بانک ملی",
  "بانک صادرات",
  "بانک تجارت",
  "بانک سپه",
  "بانک آینده",
  "بانک شهر",
  "بانک سامان",
  "بانک اقتصاد",
  "بانک دی",
  "بانک پاسارگاد",
  "بانک پارسیان",
  "بانک رفاه",
  "بانک سینا",
  "بانک رسالت",
  "بانک قرض الحسنه",
  "بانک گردشگری",
  "بانک کشاورزی",
  "بانک توسعه",
  "بانک کارآفرین",
  "بانک سرمایه",
  "بانک خاورمیانه",
  "بانک حکمت",
  "بانک صنعت",
  "بانک مسکن",
  "بانک ایران زمین",
  "بانک مهر",
  "بلو بانک",
];

const analysisLogoPositions = [
  [10, 5], [43, 5], [79, 6],
  [25, 14], [61, 14], [94, 16],
  [8, 24], [39, 24], [73, 25], [94, 31],
  [7, 40], [94, 42],
  [7, 56], [94, 58],
  [7, 70], [94, 71],
  [12, 80], [38, 79], [64, 80], [89, 79],
  [9, 91], [31, 94], [55, 91], [77, 94],
  [94, 91],
];

// The first two prototype screens precede the ten canonical behavioural
// questions.  Personal information therefore follows S13 at index 12; using
// index 11 would silently redirect the immutable /question/12 route.
const questionnaireQuestionCount = 13;
const personalInfoQuestionIndex = 12;

function getQuestionnaireRouteState(pathname) {
  if (pathname === "/analysis") {
    return {
      questionIndex: personalInfoQuestionIndex,
      isOtpVerificationStep: true,
      isAnalyzingLoans: true,
      loanResultView: "",
    };
  }

  if (pathname === "/loan-results") {
    return {
      questionIndex: personalInfoQuestionIndex,
      isOtpVerificationStep: true,
      isAnalyzingLoans: false,
      loanResultView: "results",
    };
  }

  if (pathname === "/loan-details") {
    return {
      questionIndex: personalInfoQuestionIndex,
      isOtpVerificationStep: true,
      isAnalyzingLoans: false,
      loanResultView: "details",
    };
  }

  if (pathname === "/loan-request") {
    return {
      questionIndex: personalInfoQuestionIndex,
      isOtpVerificationStep: true,
      isAnalyzingLoans: false,
      loanResultView: "request",
    };
  }

  if (pathname === "/compare-loans") {
    return {
      questionIndex: personalInfoQuestionIndex,
      isOtpVerificationStep: true,
      isAnalyzingLoans: false,
      loanResultView: "compare",
    };
  }

  if (pathname === "/compare-result") {
    return {
      questionIndex: personalInfoQuestionIndex,
      isOtpVerificationStep: true,
      isAnalyzingLoans: false,
      loanResultView: "compare-result",
    };
  }

  if (pathname === "/ai-analysis") {
    return {
      questionIndex: personalInfoQuestionIndex,
      isOtpVerificationStep: true,
      isAnalyzingLoans: false,
      loanResultView: "ai-analysis",
    };
  }

  if (pathname === "/verify-code") {
    return {
      questionIndex: personalInfoQuestionIndex,
      isOtpVerificationStep: true,
      isAnalyzingLoans: false,
      loanResultView: "",
    };
  }

  if (pathname === "/personal-info") {
    return {
      questionIndex: personalInfoQuestionIndex,
      isOtpVerificationStep: false,
      isAnalyzingLoans: false,
      loanResultView: "",
    };
  }

  const canonicalQuestionId = getCanonicalQuestionIdForRoute(pathname);
  const prototypeQuestionIndex = canonicalQuestionId
    ? getPrototypeQuestionIndexForCanonicalQuestionId(canonicalQuestionId)
    : null;
  if (prototypeQuestionIndex !== null) {
    return {
      questionIndex: prototypeQuestionIndex,
      isOtpVerificationStep: false,
      isAnalyzingLoans: false,
      loanResultView: "",
    };
  }

  const questionMatch = pathname.match(/^\/question\/(\d+)$/);
  if (questionMatch) {
    const questionNumber = Number(questionMatch[1]);
    const questionIndex = Math.min(
      Math.max(questionNumber - 1, 0),
      questionnaireQuestionCount - 1,
    );

    return {
      questionIndex,
      isOtpVerificationStep: false,
      isAnalyzingLoans: false,
      loanResultView: "",
    };
  }

  return {
    questionIndex: 0,
    isOtpVerificationStep: false,
    isAnalyzingLoans: false,
    loanResultView: "",
  };
}

function getLoanIdFromLocation() {
  if (typeof window === "undefined") return "";
  return new URLSearchParams(window.location.search).get("loanId")?.trim() || "";
}

function getInitialViewFromPath(pathname) {
  if (
    pathname.startsWith("/question/") ||
    pathname === "/personal-info" ||
    pathname === "/verify-code" ||
    pathname === "/analysis" ||
    pathname === "/loan-results" ||
    pathname === "/loan-details" ||
    pathname === "/loan-request" ||
    pathname === "/compare-loans" ||
    pathname === "/compare-result" ||
    pathname === "/ai-analysis"
  ) {
    return "questionnaire";
  }

  if (pathname === "/login" || pathname === "/login/otp") return "login";

  return "home";
}

function replaceRoute(pathname) {
  if (typeof window === "undefined") return;
  if (window.location.pathname === pathname) return;
  window.history.pushState(null, "", pathname);
}

const personalInfoCacheKeys = {
  firstName: "shahab.personalInfo.firstName",
  lastName: "shahab.personalInfo.lastName",
  phone: "shahab.personalInfo.phone",
};
const accountProfileCacheKey = "shahab.accountProfile";

function getCachedPersonalInfoValue(field) {
  if (typeof window === "undefined") return "";

  try {
    return window.localStorage.getItem(personalInfoCacheKeys[field]) || "";
  } catch {
    return "";
  }
}

function setCachedPersonalInfoValue(field, value) {
  if (typeof window === "undefined" || !personalInfoCacheKeys[field]) return;

  try {
    if (value) {
      window.localStorage.setItem(personalInfoCacheKeys[field], value);
    }
  } catch {
    // Ignore storage failures so the form remains usable in private/restricted modes.
  }
}

function getCachedAccountProfile() {
  if (typeof window === "undefined") return null;

  try {
    const cachedProfile = window.localStorage.getItem(accountProfileCacheKey);
    return cachedProfile ? JSON.parse(cachedProfile) : null;
  } catch {
    return null;
  }
}

function setCachedAccountProfile(profile) {
  if (typeof window === "undefined") return;

  try {
    window.localStorage.setItem(accountProfileCacheKey, JSON.stringify(profile));
  } catch {
    // Ignore storage failures so creating the local account does not block the flow.
  }
}

const persianNamePattern = /^[\u0621-\u064A\u067E\u0686\u0698\u06AF\u06A9\u06CC\s‌]+$/;
const persianNameError = "فقط حروف فارسی مجاز هستند";
const phoneDigitPattern = /^[0-9۰-۹٠-٩]$/;
const persianDigits = ["۰", "۱", "۲", "۳", "۴", "۵", "۶", "۷", "۸", "۹"];

function hasInvalidPersianNameCharacter(value) {
  return Array.from(value).some((character) => !persianNamePattern.test(character));
}

function sanitizePersianName(value) {
  return Array.from(value).reduce((result, character) => {
    if (Array.from(result).length >= 12) return result;
    if (!persianNamePattern.test(character)) return result;
    const letters = Array.from(result);
    if (letters.at(-1) === character && letters.at(-2) === character) return result;
    return `${result}${character}`;
  }, "");
}

function sanitizePhoneDigits(value) {
  return Array.from(value)
    .filter((character) => phoneDigitPattern.test(character))
    .map((character) => {
      if (character >= "0" && character <= "9") return persianDigits[Number(character)];
      const arabicDigitIndex = "٠١٢٣٤٥٦٧٨٩".indexOf(character);
      return arabicDigitIndex >= 0 ? persianDigits[arabicDigitIndex] : character;
    })
    .reduce((result, digit) => {
      const digits = Array.from(result);
      const hasFourRepeatedDigits =
        digits.at(-1) === digit &&
        digits.at(-2) === digit &&
        digits.at(-3) === digit &&
        digits.at(-4) === digit;
      return hasFourRepeatedDigits ? result : `${result}${digit}`;
    }, "")
    .slice(0, 9);
}

function sanitizeOtpDigits(value) {
  return Array.from(value)
    .filter((character) => phoneDigitPattern.test(character))
    .map((character) => {
      if (character >= "0" && character <= "9") return persianDigits[Number(character)];
      const arabicDigitIndex = "٠١٢٣٤٥٦٧٨٩".indexOf(character);
      return arabicDigitIndex >= 0 ? persianDigits[arabicDigitIndex] : character;
    });
}

function Nav({ onLogin, onBack, onMenu, onHome, isLoginView = false }) {
  return (
    <header className="hp-nav">
      <div className="hp-nav-inner">
        <div className="hp-nav-right">
          <button className="hp-menu-button" type="button" aria-label="menu" onClick={onMenu}>
            <span></span>
            <span></span>
            <span></span>
          </button>
          <BrandMark onClick={onHome} />
        </div>
        <div className="hp-nav-left">
          {isLoginView ? (
            <button className="hp-back-button" type="button" onClick={onBack} aria-label="بازگشت">
              <svg viewBox="0 0 24 24" focusable="false">
                <path d="M20.4 12H5" />
                <path d="m12 19-7-7 7-7" />
              </svg>
            </button>
          ) : (
            <button className="hp-login-link" type="button" onClick={onLogin}>ورود</button>
          )}
          <a href="#">پشتیبانی</a>
          <a href="#">درباره ما</a>
        </div>
      </div>
    </header>
  );
}

function SidebarIcon({ name }) {
  const icons = {
    profile: (
      <>
        <path d="M12.12 12.78a.963.963 0 0 0-.24 0 3.27 3.27 0 0 1-3.16-3.27c0-1.81 1.46-3.28 3.28-3.28a3.276 3.276 0 0 1 .12 6.55ZM18.74 19.38A9.934 9.934 0 0 1 12 22c-2.6 0-4.96-.99-6.74-2.62.1-.94.7-1.86 1.77-2.58 2.74-1.82 7.22-1.82 9.94 0 1.07.72 1.67 1.64 1.77 2.58Z" />
        <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10Z" />
      </>
    ),
    requests: (
      <>
        <path d="M21 8v10c0 3-1.79 4-4 4H7c-2.21 0-4-1-4-4V8" />
        <path d="M1 5v2c0 1.1.53 2 2 2h18c1.47 0 2-.9 2-2V5c0-1.1-.53-2-2-2H3C1.53 3 1 3.9 1 5Z" />
        <path d="M10.18 13h3.64" />
      </>
    ),
    invest: (
      <>
        <path d="M8.672 14.33c0 1.29.99 2.33 2.22 2.33h2.51c1.07 0 1.94-.91 1.94-2.03 0-1.22-.53-1.65-1.32-1.93l-4.03-1.4c-.79-.28-1.32-.71-1.32-1.93 0-1.12.87-2.03 1.94-2.03h2.51c1.23 0 2.22 1.04 2.22 2.33M12 6v12" />
        <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10Z" />
      </>
    ),
    shop: (
      <>
        <path d="M3.01 11.22v4.49C3.01 20.2 4.81 22 9.3 22h5.39c4.49 0 6.29-1.8 6.29-6.29v-4.49" />
        <path d="M12 12c1.83 0 3.18-1.49 3-3.32L14.34 2H9.67L9 8.68C8.82 10.51 10.17 12 12 12Z" />
        <path d="M18.31 12c2.02 0 3.5-1.64 3.3-3.65l-.28-2.75C20.97 3 19.97 2 17.35 2H14.3l.7 7.01c.17 1.65 1.66 2.99 3.31 2.99ZM5.64 12c1.65 0 3.14-1.34 3.3-2.99l.22-2.21.48-4.8H6.59C3.97 2 2.97 3 2.61 5.6l-.27 2.75C2.14 10.36 3.62 12 5.64 12ZM12 17c-1.67 0-2.5.83-2.5 2.5V22h5v-2.5c0-1.67-.83-2.5-2.5-2.5Z" />
      </>
    ),
    credit: (
      <>
        <path d="M2 12.61h17" />
        <path d="M19 10.28v7.15c-.03 2.85-.81 3.57-3.78 3.57H5.78C2.76 21 2 20.25 2 17.27v-6.99c0-2.7.63-3.57 3-3.71.24-.01.5-.02.78-.02h9.44c3.02 0 3.78.75 3.78 3.73Z" />
        <path d="M22 6.73v6.99c0 2.7-.63 3.57-3 3.71v-7.15c0-2.98-.76-3.73-3.78-3.73H5.78c-.28 0-.54.01-.78.02C5.03 3.72 5.81 3 8.78 3h9.44C21.24 3 22 3.75 22 6.73Z" />
        <path d="M5.25 17.81h1.72M9.11 17.81h3.44" />
      </>
    ),
    wallet: (
      <>
        <path d="M13 11.15H7M2 11.15V6.53c0-2.04 1.65-3.69 3.69-3.69h5.62c2.04 0 3.69 1.27 3.69 3.31" />
        <path d="M17.48 12.2c-.5.48-.74 1.22-.54 1.98.25.93 1.17 1.52 2.13 1.52H20v1.45c0 2.21-1.79 4-4 4H6c-2.21 0-4-1.79-4-4v-7c0-2.21 1.79-4 4-4h10c2.2 0 4 1.8 4 4v1.45h-1.08c-.56 0-1.07.22-1.44.6Z" />
        <path d="M22 12.62v2.06c0 .56-.46 1.02-1.03 1.02h-1.93c-1.08 0-2.07-.79-2.16-1.87-.06-.63.18-1.22.6-1.63.37-.38.88-.6 1.44-.6h2.05c.57 0 1.03.46 1.03 1.02Z" />
      </>
    ),
    reports: (
      <>
        <path d="M2 22h20" />
        <path d="M9.75 4v18h4.5V4c0-1.1-.45-2-1.8-2h-.9c-1.35 0-1.8.9-1.8 2ZM3 10v12h4V10c0-1.1-.4-2-1.6-2h-.8C3.4 8 3 8.9 3 10ZM17 15v7h4v-7c0-1.1-.4-2-1.6-2h-.8c-1.2 0-1.6.9-1.6 2Z" />
      </>
    ),
    ai: (
      <>
        <path d="M15.59 12.26a5.13 5.13 0 1 0 0-10.26 5.13 5.13 0 0 0 0 10.26ZM6.36 19.44a3.08 3.08 0 1 0 0-6.16 3.08 3.08 0 0 0 0 6.16ZM16.62 22a2.56 2.56 0 1 0 0-5.12 2.56 2.56 0 0 0 0 5.12Z" />
      </>
    ),
    about: (
      <>
        <path d="M18 7.16a.605.605 0 0 0-.19 0 2.573 2.573 0 0 1-2.48-2.58c0-1.43 1.15-2.58 2.58-2.58a2.58 2.58 0 0 1 2.58 2.58A2.589 2.589 0 0 1 18 7.16ZM16.97 14.44c1.37.23 2.88-.01 3.94-.72 1.41-.94 1.41-2.48 0-3.42-1.07-.71-2.6-.95-3.97-.71M5.97 7.16c.06-.01.13-.01.19 0a2.573 2.573 0 0 0 2.48-2.58C8.64 3.15 7.49 2 6.06 2a2.58 2.58 0 0 0-2.58 2.58c.01 1.4 1.11 2.53 2.49 2.58ZM7 14.44c-1.37.23-2.88-.01-3.94-.72-1.41-.94-1.41-2.48 0-3.42 1.07-.71 2.6-.95 3.97-.71M12 14.63a.605.605 0 0 0-.19 0 2.573 2.573 0 0 1-2.48-2.58c0-1.43 1.15-2.58 2.58-2.58a2.58 2.58 0 0 1 2.58 2.58c-.01 1.4-1.11 2.54-2.49 2.58ZM9.09 17.78c-1.41.94-1.41 2.48 0 3.42 1.6 1.07 4.22 1.07 5.82 0 1.41-.94 1.41-2.48 0-3.42-1.59-1.06-4.22-1.06-5.82 0Z" />
      </>
    ),
    logout: (
      <>
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10" />
        <path d="M13 11l8.2-8.2M22 6.83V2h-4.83" />
      </>
    ),
  };

  return (
    <svg className="hp-sidebar-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      {icons[name]}
    </svg>
  );
}

function UserSidebar({ isOpen, onClose, userName }) {
  const [activeItem, setActiveItem] = useState("");
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
  const items = [
    ["profile", "پروفایل کاربر"],
    ["requests", "درخواست‌های ثبت شده"],
    ["invest", "فرصت‌های سرمایه‌گذاری"],
    ["shop", "خرید و فروش امتیاز وام"],
    ["credit", "استخر اعتباری"],
    ["wallet", "کیف پول"],
    ["reports", "گزارشات"],
    ["ai", "تحلیل با هوش مصنوعی"],
    ["about", "درباره ما"],
  ];

  return (
    <div className={`hp-sidebar-layer ${isOpen ? "is-open" : ""}`} aria-hidden={!isOpen}>
      <button className="hp-sidebar-backdrop" type="button" aria-label="بستن منو" onClick={onClose}></button>
      <aside className="hp-user-sidebar" aria-label="منوی کاربر">
        <strong className="hp-sidebar-name">{userName || "محمد حسن کیوند"}</strong>
        <nav className="hp-sidebar-menu">
          {items.map(([icon, label]) => (
            <a
              className={activeItem === icon ? "is-active" : ""}
              href="#"
              key={label}
              onClick={(event) => {
                event.preventDefault();
                setActiveItem(icon);
              }}
            >
              <SidebarIcon name={icon} />
              <span>{label}</span>
            </a>
          ))}
          <a
            className={`hp-sidebar-logout ${activeItem === "logout" ? "is-active" : ""}`}
            href="#"
            onClick={(event) => {
              event.preventDefault();
              setShowLogoutConfirm(true);
            }}
          >
            <SidebarIcon name="logout" />
            <span>خروج از حساب کاربری</span>
          </a>
        </nav>
        <p className="hp-sidebar-support">
          جهت دریافت مشاوره با شماره تلفن
          <br />
          <a href="tel:02135647">۰۲۱-۳۵۶۴۷</a>
          {" "}
          تماس حاصل نمایید.
        </p>
        {showLogoutConfirm ? (
          <div className="hp-logout-confirm" role="dialog" aria-modal="true">
            <div className="hp-logout-warning" aria-hidden="true">
              <svg viewBox="0 0 24 24" focusable="false">
                <path d="M12 9v5M12 21.41H5.94c-3.47 0-4.92-2.48-3.24-5.51l3.12-5.62L8.76 5c1.78-3.21 4.7-3.21 6.48 0l2.94 5.29 3.12 5.62c1.68 3.03.22 5.51-3.24 5.51H12v-.01Z" />
                <path d="M11.995 17h.009" />
              </svg>
            </div>
            <p>آیا از خروج از حساب کاربری‌تان مطمئن هستید؟</p>
            <div>
              <button
                className="hp-logout-no"
                type="button"
                onClick={() => setShowLogoutConfirm(false)}
              >
                خیر
              </button>
              <button
                className="hp-logout-yes"
                type="button"
                onClick={() => {
                  setShowLogoutConfirm(false);
                  setActiveItem("logout");
                }}
              >
                بله
              </button>
            </div>
          </div>
        ) : null}
      </aside>
      {showLogoutConfirm ? (
        <div className="hp-logout-confirm hp-logout-confirm-floating" role="dialog" aria-modal="true">
          <div className="hp-logout-warning" aria-hidden="true">
            <svg viewBox="0 0 24 24" focusable="false">
              <path d="M12 9v5M12 21.41H5.94c-3.47 0-4.92-2.48-3.24-5.51l3.12-5.62L8.76 5c1.78-3.21 4.7-3.21 6.48 0l2.94 5.29 3.12 5.62c1.68 3.03.22 5.51-3.24 5.51H12v-.01Z" />
              <path d="M11.995 17h.009" />
            </svg>
          </div>
          <p>آیا از خروج از حساب کاربری‌تان مطمئن هستید؟</p>
          <div>
            <button
              className="hp-logout-no"
              type="button"
              onClick={() => setShowLogoutConfirm(false)}
            >
              خیر
            </button>
            <button
              className="hp-logout-yes"
              type="button"
              onClick={() => {
                setShowLogoutConfirm(false);
                setActiveItem("logout");
              }}
            >
              بله
            </button>
          </div>
        </div>
      ) : null}
    </div>
  );
}

function toPersianDigits(value) {
  return String(value).replace(/\d/g, (digit) => "۰۱۲۳۴۵۶۷۸۹"[Number(digit)]);
}

function formatOtpCountdown(seconds) {
  const minutes = Math.floor(seconds / 60);
  const rest = seconds % 60;
  return toPersianDigits(`${String(minutes).padStart(2, "0")}:${String(rest).padStart(2, "0")}`);
}

function LoginScreen({ loginStep, setLoginStep }) {
  const [phone, setPhone] = useState("");
  const [otp, setOtp] = useState(Array(6).fill(""));
  const [remainingSeconds, setRemainingSeconds] = useState(120);

  useEffect(() => {
    if (loginStep !== "otp" || remainingSeconds <= 0) return undefined;

    const timer = window.setTimeout(() => {
      setRemainingSeconds((current) => Math.max(current - 1, 0));
    }, 1000);

    return () => window.clearTimeout(timer);
  }, [loginStep, remainingSeconds]);

  function handlePhoneChange(event) {
    setPhone(event.target.value.replace(/\D/g, "").slice(0, 9));
  }

  function handlePhoneKeyDown(event) {
    const allowedKeys = [
      "Backspace",
      "Delete",
      "ArrowLeft",
      "ArrowRight",
      "Tab",
      "Home",
      "End",
    ];

    if (allowedKeys.includes(event.key) || event.ctrlKey || event.metaKey) return;
    if (!/^\d$/.test(event.key)) event.preventDefault();
  }

  function handlePhoneSubmit(event) {
    event.preventDefault();
    if (phone.length !== 9) return;

    setLoginStep("otp");
    setOtp(Array(6).fill(""));
    setRemainingSeconds(120);
  }

  function handleOtpChange(index, event) {
    const digit = event.target.value.replace(/\D/g, "").slice(-1);
    const nextOtp = [...otp];
    nextOtp[index] = digit;
    setOtp(nextOtp);

    if (digit) {
      event.target.nextElementSibling?.focus();
    }
  }

  function handleOtpKeyDown(index, event) {
    const allowedKeys = [
      "Backspace",
      "Delete",
      "ArrowLeft",
      "ArrowRight",
      "Tab",
      "Home",
      "End",
    ];

    if (event.key === "Backspace" && !otp[index]) {
      event.target.previousElementSibling?.focus();
      return;
    }

    if (allowedKeys.includes(event.key) || event.ctrlKey || event.metaKey) return;
    if (!/^\d$/.test(event.key)) event.preventDefault();
  }

  function handleOtpPaste(event) {
    event.preventDefault();
    const pastedDigits = event.clipboardData.getData("text").replace(/\D/g, "").slice(0, 6);
    if (!pastedDigits) return;

    const nextOtp = Array(6).fill("");
    pastedDigits.split("").forEach((digit, index) => {
      nextOtp[index] = digit;
    });
    setOtp(nextOtp);
  }

  function handleResendCode() {
    if (remainingSeconds > 0) return;

    setOtp(Array(6).fill(""));
    setRemainingSeconds(120);
  }

  function handleChangePhone() {
    setLoginStep("phone");
    setOtp(Array(6).fill(""));
    setRemainingSeconds(120);
  }

  if (loginStep === "otp") {
    return (
      <main className="hp-login-page hp-otp-page">
        <form className="hp-otp-form" onSubmit={(event) => event.preventDefault()}>
          <label>کد یکبار مصرف</label>
          <div className="hp-otp-row" dir="ltr">
            {otp.map((digit, index) => (
              <input
                key={index}
                type="tel"
                inputMode="numeric"
                pattern="[0-9]*"
                maxLength={1}
                value={digit}
                onChange={(event) => handleOtpChange(index, event)}
                onKeyDown={(event) => handleOtpKeyDown(index, event)}
                onPaste={handleOtpPaste}
                aria-label={`رقم ${index + 1} کد یکبار مصرف`}
              />
            ))}
          </div>
          <div className="hp-otp-actions">
            <button className="hp-change-phone" type="button" onClick={handleChangePhone}>
              تغییر شماره تلفن
            </button>
            <button
              className="hp-resend-code"
              type="button"
              disabled={remainingSeconds > 0}
              onClick={handleResendCode}
            >
              ارسال مجدد
              {remainingSeconds > 0 ? ` (${formatOtpCountdown(remainingSeconds)})` : ""}
            </button>
          </div>
        </form>
      </main>
    );
  }

  return (
    <main className="hp-login-page">
      <form className="hp-login-form" onSubmit={handlePhoneSubmit}>
        <label htmlFor="login-phone">شماره تلفن همراه</label>
        <div className="hp-phone-row">
          <span>۰۹</span>
          <input
            id="login-phone"
            type="tel"
            inputMode="numeric"
            pattern="[0-9]*"
            maxLength={9}
            value={phone}
            onChange={handlePhoneChange}
            onKeyDown={handlePhoneKeyDown}
            aria-label="شماره تلفن همراه"
          />
        </div>
        <button type="submit" disabled={phone.length !== 9}>ارسال کد یکبار مصرف</button>
      </form>
    </main>
  );
}

function QuestionnaireHeader({ onBack, onMenu, onHome }) {
  return (
    <header className="hp-questionnaire-header">
      <button className="hp-questionnaire-icon-button" type="button" onClick={onBack} aria-label="بازگشت">
        <svg viewBox="0 0 24 24" focusable="false">
          <path d="M20 12H5" />
          <path d="m12 19-7-7 7-7" />
        </svg>
      </button>
      <a className="hp-questionnaire-brand" href="/" onClick={onHome}>
        <img src={logoUrl} alt="شهاب" />
        <span>
          <strong>شهاب</strong>
          <small>(شبکه هم‌رسانی اعتبار برخط)</small>
        </span>
      </a>
      <button className="hp-questionnaire-menu" type="button" onClick={onMenu} aria-label="منو">
        <span />
        <span />
        <span />
      </button>
    </header>
  );
}

function allRecommendationItems(result) {
  if (!result) return [];
  const items = [
    ...result.rankedRecommendations,
    ...result.lowCompatibilityRecommendations,
    ...result.needsReview,
  ];
  return items.filter((item, index) => items.findIndex((candidate) => candidate.loanId === item.loanId) === index);
}

function LoanCompareScreen({ result, onBack, onMenu, onHome, onCompareSubmit, mode = "request", initialSelectedPlanIds = [] }) {
  const [selectedPlans, setSelectedPlans] = useState(() => Object.fromEntries(initialSelectedPlanIds.map((planId) => [planId, true])));
  const selectedPlanIds = Object.entries(selectedPlans)
    .filter(([, isSelected]) => isSelected)
    .map(([planId]) => planId);
  const selectedCount = selectedPlanIds.length;
  const isCompareMode = mode === "compare";
  const visiblePlans = allRecommendationItems(result);

  if (!result) {
    return <main className="hp-questionnaire-page" dir="rtl"><QuestionnaireHeader onBack={onBack} onMenu={onMenu} onHome={onHome} /><p className="hp-recommendation-result-state">برای ادامه، ابتدا پرسشنامه را در همین تب کامل کنید و نتیجهٔ معتبر دریافت کنید.</p></main>;
  }

  return (
    <main className={`hp-questionnaire-page hp-loan-compare-page ${isCompareMode ? "is-simple-compare" : ""} ${selectedCount > 0 ? "has-bottom-bar" : ""}`} dir="rtl">
      <QuestionnaireHeader onBack={onBack} onMenu={onMenu} onHome={onHome} />
      <div className="hp-compare-warning">
        <span>!</span>
        <p>{isCompareMode ? "حداکثر ۱۰ وام واقعی را برای مقایسه انتخاب کنید." : "روش اقدام رسمی فقط پس از تأیید provider نمایش داده می‌شود."}</p>
      </div>
      {!isCompareMode ? (
        <div className="hp-compare-info">
          <span>!</span>
          <p>در دادهٔ serving فعلی، روش اقدام یا provider رسمی ثبت نشده است؛ این صفحه پرداخت یا ثبت موفقیت را شبیه‌سازی نمی‌کند.</p>
        </div>
      ) : null}
      <section className="hp-compare-list">
        {visiblePlans.map((recommendation) => (
          <LoanComparisonCard
            key={recommendation.loanId}
            recommendation={recommendation}
            selected={Boolean(selectedPlans[recommendation.loanId])}
            onToggle={() => setSelectedPlans((current) => ({
              ...current,
              [recommendation.loanId]: current[recommendation.loanId] ? false : selectedCount < 10,
            }))}
          />
        ))}
      </section>
      {isCompareMode && selectedCount > 0 ? (
        <div className="hp-simple-compare-bottom-bar">
          <button className="hp-simple-compare-submit" type="button" onClick={() => onCompareSubmit?.(selectedPlanIds)}>مقایسه کن ({toPersianDigits(selectedCount)} وام)</button>
        </div>
      ) : selectedCount > 0 ? (
        <div className="hp-compare-bottom-bar">
          <div>
            <span>برای «{toPersianDigits(selectedCount)}» وام انتخاب‌شده، روش اقدام تأییدشده‌ای موجود نیست.</span>
          </div>
          <button type="button" disabled>ثبت یا پرداخت در دسترس نیست</button>
        </div>
      ) : (
        null
      )}
    </main>
  );
}

const comparisonMetrics = [
  {
    id: "amount",
    label: "مبلغ وام",
    title: "حداکثر مبلغ وام",
    value: (detail) => formatApprovedMoney(detail.maxAmountTomans),
  },
  {
    id: "interest",
    label: "نرخ بهره",
    title: "نرخ بهره اعلامی",
    value: (detail) => formatApprovedPercent(detail.interestRatePercent),
  },
  {
    id: "repayment",
    label: "بازپرداخت",
    title: "حداکثر زمان بازپرداخت",
    value: (detail) => detail.maxRepaymentMonths == null ? "اعلام نشده" : `${Number(detail.maxRepaymentMonths).toLocaleString("fa-IR").replaceAll("٬", "/")} ماه`,
  },
  {
    id: "installment",
    label: "مبلغ قسط",
    title: "مبلغ هر قسط",
    value: (detail) => formatApprovedMoney(detail.monthlyInstallmentTomans),
  },
  {
    id: "guarantee",
    label: "ضمانت",
    title: "نوع ضمانت",
    value: (detail) => detail.guaranteeType || "اعلام نشده",
  },
];

function formatApprovedMoney(value) {
  return value == null ? "اعلام نشده" : `${Number(value).toLocaleString("fa-IR").replaceAll("٬", "/")} تومان`;
}

function formatApprovedPercent(value) {
  return <LoanPercent value={value} />;
}

function LoanComparisonResultCard({ detail, metric }) {
  return (
    <article className="hp-compare-result-card">
      <BankIdentity lenderName={detail.lenderName} />
      <strong title={detail.loanName} aria-label={detail.loanName}>{detail.loanName}</strong>
      <p>
        <span>{metric.title}</span>
        <b>{metric.value(detail)}</b>
      </p>
    </article>
  );
}

function LoanComparisonResultScreen({ result, onBack, onMenu, onHome, onAiAnalysis, selectedPlanIds }) {
  const [activeMetricIndex, setActiveMetricIndex] = useState(0);
  const [detailState, setDetailState] = useState({ status: "loading", details: [] });
  const tabsRef = useRef(null);
  const tabDragStartXRef = useRef(null);
  const tabDragStartScrollLeftRef = useRef(0);
  const activeMetric = comparisonMetrics[activeMetricIndex];

  useEffect(() => {
    if (!result || selectedPlanIds.length < 2) {
      setDetailState({ status: "empty", details: [] });
      return undefined;
    }
    const controller = new AbortController();
    setDetailState({ status: "loading", details: [] });
    Promise.all(selectedPlanIds.map((loanId) => fetchLoanDetails(loanId, { signal: controller.signal })))
      .then((details) => setDetailState({ status: "ready", details: details.filter(Boolean) }))
      .catch((error) => { if (error.name !== "AbortError") setDetailState({ status: "error", details: [] }); });
    return () => controller.abort();
  }, [result, selectedPlanIds]);

  if (!result) {
    return <main className="hp-questionnaire-page" dir="rtl"><QuestionnaireHeader onBack={onBack} onMenu={onMenu} onHome={onHome} /><p className="hp-recommendation-result-state">نتیجهٔ معتبر این پرسشنامه در دسترس نیست.</p></main>;
  }

  useEffect(() => {
    const activeTab = tabsRef.current?.querySelector(`[data-tab-index="${activeMetricIndex}"]`);
    activeTab?.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "nearest" });
  }, [activeMetricIndex]);

  function handleTabsPointerDown(event) {
    tabDragStartXRef.current = event.clientX;
    tabDragStartScrollLeftRef.current = tabsRef.current?.scrollLeft || 0;
    event.currentTarget.setPointerCapture?.(event.pointerId);
  }

  function handleTabsPointerMove(event) {
    if (tabDragStartXRef.current === null || !tabsRef.current) return;

    const deltaX = event.clientX - tabDragStartXRef.current;
    tabsRef.current.scrollLeft = tabDragStartScrollLeftRef.current - deltaX;
  }

  function handleTabsPointerUp(event) {
    if (tabDragStartXRef.current === null) return;

    const deltaX = event.clientX - tabDragStartXRef.current;
    tabDragStartXRef.current = null;

    if (Math.abs(deltaX) < 28) return;

    setActiveMetricIndex((current) => {
      if (deltaX < 0) return Math.min(current + 1, comparisonMetrics.length - 1);
      return Math.max(current - 1, 0);
    });
  }

  return (
    <main className="hp-questionnaire-page hp-compare-result-page" dir="rtl">
      <QuestionnaireHeader onBack={onBack} onMenu={onMenu} onHome={onHome} />

      <nav
        ref={tabsRef}
        className="hp-compare-result-tabs"
        aria-label="مقایسه وام"
        onPointerDown={handleTabsPointerDown}
        onPointerMove={handleTabsPointerMove}
        onPointerUp={handleTabsPointerUp}
        onPointerCancel={() => {
          tabDragStartXRef.current = null;
        }}
      >
        {comparisonMetrics.map((metric, index) => (
          <button
            className={index === activeMetricIndex ? "is-active" : ""}
            type="button"
            data-tab-index={index}
            onClick={() => setActiveMetricIndex(index)}
            key={metric.id}
          >
            {metric.label}
          </button>
        ))}
      </nav>

      <section className="hp-compare-result-list">
        {detailState.status === "loading" ? <p className="hp-recommendation-result-state">در حال دریافت جزئیات وام‌ها…</p> : null}
        {detailState.status === "empty" ? <p className="hp-recommendation-result-state">برای مقایسه دست‌کم دو وام را انتخاب کنید.</p> : null}
        {detailState.status === "error" ? <p className="hp-recommendation-result-state">دریافت جزئیات مقایسه در حال حاضر ممکن نیست.</p> : null}
        {detailState.status === "ready" ? detailState.details.map((detail) => <LoanComparisonResultCard key={detail.loanId} detail={detail} metric={activeMetric} />) : null}
      </section>

      <div className="hp-compare-result-bottom-bar">
        <button type="button" onClick={() => onAiAnalysis(selectedPlanIds[0] || "")}>توضیح نتیجه</button>
      </div>
    </main>
  );
}

function LoanAiAnalysisScreen({ onBack, result, loanId }) {
  const selectedRecommendation = allRecommendationItems(result).find((item) => item.loanId === loanId);
  const explanation = selectedRecommendation?.compatibilityReason
    || selectedRecommendation?.rankingExcludedReasons?.join("، ")
    || "برای این نتیجه توضیح تأییدشده‌ای موجود نیست.";
  return (
    <main className="hp-ai-analysis-page" dir="rtl">
      <div className="hp-ai-analysis-credit">اعتبار شما در هر ۲ ساعت ۱۰ پرامپت است.</div>
      <header className="hp-ai-analysis-header">
        <button className="hp-ai-analysis-back" type="button" onClick={onBack} aria-label="بازگشت">
          <svg viewBox="0 0 24 24" focusable="false">
            <path d="M20 12H5" />
            <path d="m12 19-7-7 7-7" />
          </svg>
        </button>
        <button className="hp-ai-analysis-panel-button" type="button" aria-label="پنل">
          <img src={sidebarLeftIconUrl} alt="" />
        </button>
      </header>

      <section className="hp-ai-analysis-message">
        <p>
          {explanation}
          <br />
          provider خارجی فعال نیست؛ تحلیل ساختگی نمایش داده نمی‌شود.
        </p>
      </section>

      <form className="hp-ai-analysis-input" onSubmit={(event) => event.preventDefault()}>
        <button type="button" aria-label="افزودن" disabled>
          <img src={addCircleIconUrl} alt="" />
        </button>
        <input type="text" placeholder="تحلیل هوش مصنوعی هنوز فعال نیست" disabled />
        <button type="submit" aria-label="ارسال" disabled>
          <img src={sendIconUrl} alt="" />
        </button>
      </form>
    </main>
  );
}

function QuestionnaireScreen({ onBack, onMenu, onAccountCreated, onHome }) {
  const initialRouteState = getQuestionnaireRouteState(window.location.pathname);
  const [currentQuestion, setCurrentQuestion] = useState(initialRouteState.questionIndex);
  const [answers, setAnswers] = useState({});
  // Kept only in this React instance: canonical answers and the opaque session
  // identifier are deliberately absent from URLs and browser storage.
  const [questionnaireSessionId, setQuestionnaireSessionId] = useState("");
  const [questionnaireSessionError, setQuestionnaireSessionError] = useState("");
  const [isSavingQuestionnaireAnswer, setIsSavingQuestionnaireAnswer] = useState(false);
  const [personalInfo, setPersonalInfo] = useState({
    firstName: "",
    lastName: "",
    phone: "",
    income: "",
    job: "",
  });
  const [cachedPersonalInfo, setCachedPersonalInfo] = useState(() => ({
    firstName: getCachedPersonalInfoValue("firstName"),
    lastName: getCachedPersonalInfoValue("lastName"),
    phone: getCachedPersonalInfoValue("phone"),
  }));
  const [focusedPersonalInfoField, setFocusedPersonalInfoField] = useState("");
  const [personalInfoErrors, setPersonalInfoErrors] = useState({
    firstName: "",
    lastName: "",
  });
  const [isOtpVerificationStep, setIsOtpVerificationStep] = useState(initialRouteState.isOtpVerificationStep);
  const [isAnalyzingLoans, setIsAnalyzingLoans] = useState(initialRouteState.isAnalyzingLoans);
  const [loanResultView, setLoanResultView] = useState(initialRouteState.loanResultView);
  const [selectedLoanId, setSelectedLoanId] = useState(getLoanIdFromLocation);
  const [selectedComparisonPlanIds, setSelectedComparisonPlanIds] = useState([]);
  const [recommendationResult, setRecommendationResult] = useState(null);
  const [recommendationStatus, setRecommendationStatus] = useState("idle");
  const [selectedAnalysisLoanId, setSelectedAnalysisLoanId] = useState("");
  const [isAnalysisSpinnerRunning, setIsAnalysisSpinnerRunning] = useState(false);
  const [analysisCountdown, setAnalysisCountdown] = useState(5);
  const [loanOtp, setLoanOtp] = useState(Array(6).fill(""));
  const [loanOtpSeconds, setLoanOtpSeconds] = useState(120);
  const [loanOtpError, setLoanOtpError] = useState("");
  const [isIncomeDropdownOpen, setIsIncomeDropdownOpen] = useState(false);
  const [isJobDropdownOpen, setIsJobDropdownOpen] = useState(false);
  const [stageOffset, setStageOffset] = useState(0);
  const [stageOffsets, setStageOffsets] = useState([0, 176, 276]);
  const loanOtpRefs = useRef([]);
  const stageItemRefs = useRef([]);
  const didSkipInitialRouteSyncRef = useRef(false);
  const stageDragRef = useRef({
    isDragging: false,
    startX: 0,
    startOffset: 0,
    lastOffset: 0,
  });
  const questions = [
    {
      title: "۱-مایل به دریافت چه نوع وامی هستید؟",
      warning:
        "وام «شهاب» وامی کوتاه مدت و فوری است که توسط سرمایه‌گذاران خصوصی اعم از افراد و سازمان‌ها تامین می‌شود.",
      options: [
        {
          id: "shahab",
          label: "وام «شهاب» تا سقف ۳۰۰/۰۰۰/۰۰۰ تومان",
        },
        {
          id: "bank",
          label: "وام «بانکی» تا سقف ۳/۰۰۰/۰۰۰/۰۰۰ تومان",
        },
      ],
    },
    {
      title: "۲-شخص حقیقی هستید یا شخص حقوقی؟",
      options: [
        {
          id: "business",
          label: "به عنوان یک «کسب و کار» نیازمند اعتبار هستم.",
        },
        {
          id: "person",
          label: "به عنوان یک «شخصی» نیازمند اعتبار هستم.",
        },
      ],
    },
    {
      title:
        "۱-پولی که از این وام یا اعتبار به دست می‌آورید را دقیقاً در چه راهی مصرف می‌کنید؟",
      stageIndex: 0,
      stepIndex: 0,
      options: [
        {
          id: "work-equipment",
          label:
            "مستقیماً برای کار، تولید یا خرید تجهیزاتی که درآمدم را بیشتر می‌کند سرمایه‌گذاری می‌کنم.",
        },
        {
          id: "assets",
          label:
            "برای حفظ ارزش پولم در برابر تورم، دارایی‌هایی مثل طلا، ارز یا سهام می‌خرم.",
        },
        {
          id: "essentials",
          label:
            "برای خرید کالاهای اساسی و ضروری زندگی هزینه می‌کنم.(مثل لوازم خانگی یا تعمیرات مهم)",
        },
        {
          id: "lifestyle",
          label:
            "برای ارتقای سطح زندگی و خریدهای غیرضروری خرج می‌کنم.(مثل سفر، گوشی جدید یا لوازم لوکس)",
        },
        {
          id: "debt",
          label:
            "فقط برای پرداخت بدهی‌های قبلی یا پاس کردن چک‌های برگشتی از آن استفاده می‌کنم.",
        },
      ],
    },
    {
      title:
        "۲-اگر دریافت این وام لغو شود و نتوانید آن را بگیرید، برای رفع نیازتان چه می‌کنید؟",
      stageIndex: 0,
      stepIndex: 1,
      options: [
        {
          id: "urgent-loan",
          label:
            "به هر قیمتی شده پول را جور می‌کنم چون نیازم فوری است.(حتی با قرض گرفتن از بازار آزاد با سود بسیار بالا)",
        },
        {
          id: "sell-assets",
          label:
            "فوراً بخشی از دارایی‌های باارزشم (مثل طلا یا ماشین) را می‌فروشم تا کارم راه بیفتد.",
        },
        {
          id: "cheaper-option",
          label:
            "سعی می‌کنم یک کالا یا خدمات ارزان‌تر پیدا کنم تا با بودجه فعلی‌ام همخوانی داشته باشد.",
        },
        {
          id: "delay-purchase",
          label:
            "خرید را چند ماه عقب می‌اندازم تا خودم کم‌کم پولش را پس‌انداز کنم.",
        },
        {
          id: "cancel-action",
          label:
            "کلاً از این خرید یا اقدام منصرف می‌شوم، چون اصلاً عجله‌ای ندارم و ضروری نیست.",
        },
      ],
    },
    {
      title:
        "۳-در انتخاب یک وام، کدام حالت برای شما در اولویت اول قرار دارد؟",
      stageIndex: 0,
      stepIndex: 2,
      options: [
        {
          id: "lowest-rate",
          label:
            "فقط کمترین سود ممکن برایم مهم است؛\u00a0حاضرم ماه‌ها در نوبت بمانم و چند ضامن ببرم.",
        },
        {
          id: "low-rate-easy-guarantee",
          label:
            "سود پایین مهم‌تر است، اما به شرطی که شرایط ضامن آوردن بیش از حد سخت نباشد.",
        },
        {
          id: "balanced",
          label:
            "تعادل برایم مهم است؛ سودی منطقی با دردسر و زمان انتظار متوسط.",
        },
        {
          id: "speed-ease",
          label:
            "سرعت و راحتی مهم‌تر است؛ حاضرم سود کمی بالاتر بدهم اما درگیر کاغذبازی و ضامن نشوم.",
        },
        {
          id: "instant-no-guarantor",
          label:
            "فقط و فقط دریافت فوری و بدون ضامن برایم مهم است؛ اصلاً به مبلغ سود نهایی فکر نمی‌کنم.",
        },
      ],
    },
    {
      title:
        "۴-بین مبلغ اقساط ماهانه و مدت‌زمان وام، کدام حالت را انتخاب می‌کنید؟",
      stageIndex: 0,
      stepIndex: 3,
      options: [
        {
          id: "short-heavy-installments",
          label:
            "کوتاه‌ترین زمان ممکن با اقساط بسیار سنگین (تا جایی که کل درآمدم درگیر شود) تا سود کمتری بدهم.",
        },
        {
          id: "short-manageable",
          label:
            "زمان کوتاه با اقساط نسبتاً سنگین، فقط به قدری که حداقل پول برای گذران زندگی‌ام باقی بماند.",
        },
        {
          id: "balanced-term",
          label:
            "یک حالت میانه؛ اقساط متوسط در یک زمان استاندارد (مثلاً ۲۴ ماهه).",
        },
        {
          id: "long-light",
          label:
            "زمان طولانی با اقساط سبک، حتی اگر در نهایت مجموع سود پرداختی‌ام بیشتر شود.",
        },
        {
          id: "long-lowest-payment",
          label:
            "طولانی‌ترین زمان ممکن با کمترین قسط ماهانه؛ اصلاً برایم مهم نیست که مجموع سود چقدر زیاد می‌شود.",
        },
      ],
    },
    {
      title:
        "۵-چقدر برایتان مهم است که شرایط پرداخت اقساط قابل تغییر و منعطف باشد؟",
      stageIndex: 0,
      stepIndex: 4,
      options: [
        {
          id: "fully-flexible",
          label:
            "بسیار زیاد؛ درآمدم متغیر است و می‌خواهم مبلغ قسط هر ماه بر اساس توانم در آن ماه تعیین شود.",
        },
        {
          id: "skip-or-delay",
          label:
            "می‌خواهم این حق را داشته باشم که اگر به مشکل خوردم، یکی دو قسط را با جریمه‌ای کم به تعویق بیندازم.",
        },
        {
          id: "date-flexible",
          label:
            "نیازی به تغییر مبلغ ندارم، اما می‌خواهم تاریخ پرداخت در طول ماه شناور باشد (مثلاً بین یکم تا دهم هر ماه).",
        },
        {
          id: "fixed-with-buffer",
          label:
            "تاریخ و مبلغ ثابت را ترجیح می‌دهم، اما با یک فرجه چند روزه برای تأخیرهای احتمالی.",
        },
        {
          id: "strict-fixed",
          label:
            "اصلاً نیازی به تغییر ندارم؛ اقساط ثابت، قطعی و غیرقابل تغییر را ترجیح می‌دهم تا دقیق برنامه‌ریزی کنم.",
        },
      ],
    },
    {
      title:
        "۶-در حال حاضر، چه کسری از درآمد ماهانه شما صرف پرداخت اقساط وام‌های قبلی یا بدهی‌ها می‌شود و این موضوع چه احساسی در شما ایجاد کرده است؟",
      stageIndex: 0,
      stepIndex: 5,
      options: [
        {
          id: "no-debt-pressure",
          label:
            "تقریباً ۰٪؛ هیچ بدهی یا قسط قابل‌توجهی ندارم و از نظر مالی کاملاً احساس آزادی و تسلط می‌کنم.",
        },
        {
          id: "low-debt-calm",
          label:
            "کمتر از ۲۰٪ درآمدم صرف اقساط می‌شود؛ پرداخت‌ها را به راحتی انجام می‌دهم و هیچ فشاری برای تأمین هزینه‌های روزمره احساس نمی‌کنم.",
        },
        {
          id: "medium-debt-careful",
          label:
            "بین ۲۰٪ تا ۴۰٪ درآمدم به اقساط می‌رود؛ پرداخت‌ها را مدیریت می‌کنم اما جای مانور مالی‌ام کم شده و باید مراقب مخارج دیگرم باشم.",
        },
        {
          id: "high-debt-pressure",
          label:
            "بین ۴۰٪ تا ۶۰٪ درآمدم صرف بدهی‌ها می‌شود؛ فشار مالی زیادی حس می‌کنم و گاهی برای رسیدگی به هزینه‌های ضروری زندگی دچار مشکل می‌شوم.",
        },
        {
          id: "severe-debt-pressure",
          label:
            "بیش از ۶۰٪ درآمدم برای اقساط می‌رود؛ به شدت تحت فشارم و گاهی برای پرداخت اقساط قبلی، مجبور می‌شوم وام جدید بگیرم یا پول قرض کنم.",
        },
      ],
    },
    {
      title:
        "۱-تصور کنید کارشناس اعتبارات بانک به شما می‌گوید: «ما طرح‌های تسهیلاتی بسیار متنوعی داریم؛ برخی از این طرح‌ها نیازمند مسدود شدن پول شما در بانک هستند، برخی دیگر فقط به کارکرد روزانه حساب شما نگاه می‌کنند و طرح‌هایی هم داریم که اصلاً نیازی به سپرده‌گذاری ندارند اما شرایط خاص خود را می‌طلبند. کدام‌یک از جملات زیر دقیقاً پاسخ شما به کارشناس بانک است؟»",
      stageIndex: 1,
      stepIndex: 0,
      titleClassName: "is-long",
      options: [
        {
          id: "deposit-long-term",
          label:
            "سرمایه مازاد و آزادی دارم و می‌توانم بخش قابل‌توجهی از آن را برای میان‌مدت یا بلندمدت (بیش از ۳ تا ۶ ماه) در بانک کاملاً مسدود کنم تا بهترین شرایط وام را بگیرم.",
        },
        {
          id: "deposit-short-term",
          label:
            "نقدینگی مازاد دارم، اما صرفاً می‌توانم آن را برای مدت زمان کوتاهی (حداکثر ۱ تا ۳ ماه) مسدود نگه دارم و زودتر به پولم نیاز دارم.",
        },
        {
          id: "daily-balance",
          label:
            "نقدینگی دارم، اما به دلیل نیاز روزمره (مثل سرمایه در گردش کسب‌وکارم) اصلاً امکان مسدودی ندارم و فقط می‌توانم میانگین کارکرد حساب برایتان ایجاد کنم.",
        },
        {
          id: "limited-liquidity",
          label:
            "نقدینگی بسیار محدودی دارم که نهایتاً برای پرداخت هزینه‌های جانبی، تشکیل پرونده یا سپرده‌ای بسیار ناچیز (کمتر از ۱۰٪ مبلغ وام) کفایت می‌کند.",
        },
        {
          id: "no-liquidity",
          label:
            "هیچ نقدینگی اولیه‌ای ندارم؛ هدفم از دریافت این وام دقیقاً تأمین سرمایه از نقطه صفر است و به وامی بدون نیاز به هیچ‌گونه سپرده پیش‌نیاز احتیاج دارم.",
        },
      ],
    },
    {
      title:
        "۲-برای یک سرمایه‌گذاری یا ارتقای کسب‌وکار به مبلغ ۲۰۰ میلیون تومان نیاز دارید. بانک برای تأمین این مبلغ، ۵ سناریوی مالی متفاوت را پیشنهاد می‌دهد. انتخاب شما در این طیف کدام است؟",
      stageIndex: 1,
      stepIndex: 1,
      options: [
        {
          id: "instant-high-cost",
          label:
            "دریافت فوری وام (اقساط: ۱۲ میلیون، مجموع سود: ۸۸ میلیون تومان).",
        },
        {
          id: "one-month-wait",
          label:
            "دریافت وام با ۱ ماه انتظار (اقساط: ۱۱/۵ میلیون، مجموع سود: ۷۶ میلیون تومان).",
        },
        {
          id: "two-month-wait",
          label:
            "دریافت وام با ۲ ماه انتظار (اقساط: ۱۱ میلیون، مجموع سود: ۶۴ میلیون تومان).",
        },
        {
          id: "three-month-wait",
          label:
            "دریافت وام با ۳ ماه انتظار (اقساط: ۱۰ میلیون، مجموع سود: ۴۰ میلیون تومان).",
        },
        {
          id: "cancel-bank-loan",
          label:
            "انصراف از وام بانکی و صبر کردن تا زمان پس‌انداز شخصی کل مبلغ بدون پرداخت هیچ‌گونه سود.",
        },
      ],
    },
    {
      title:
        "۳-برای توسعه کار به ۵۰۰ میلیون تومان سرمایه نیاز دارید. بازار دارای نوسان است، کدام ساختار را با توجه به شدت ریسک آن می‌پذیرید؟",
      stageIndex: 1,
      stepIndex: 2,
      options: [
        {
          id: "high-rate-no-document",
          label: "بازپرداخت ۶۰ ماهه با سود ۳۵٪ بدون وثیقه سنگین",
        },
        {
          id: "salary-deduction",
          label: "بازپرداخت ۴۸ ماهه با سود ۳۰٪ ارائه کسر از حقوق و سفته",
        },
        {
          id: "guarantor-medium-rate",
          label: "بازپرداخت ۳۶ ماهه با سود ۲۵٪ نیازمند دو ضامن معتبر",
        },
        {
          id: "personal-cheque",
          label: "بازپرداخت ۱۲ ماهه با سود ۲۰٪ ارائه چک صیادی شخصی",
        },
        {
          id: "balloon-payment",
          label:
            "تسویه یکجا در پایان سال سوم با سود ۱۵٪ در قبال ترهین وثیقه ملکی",
        },
      ],
    },
    {
      title:
        "۴-برای تأمین مبلغ ۱۰۰ میلیون تومان، دو پیشنهاد تسهیلاتی به شما ارائه شده است: پیشنهاد الف: «نرخ سود ۱۸٪، اما ۲۰٪ از مبلغ وام تا پایان اقساط نزد بانک مسدود می‌شود و ۳٪ هم کارمزد تشکیل پرونده دارد.» پیشنهاد ب: «نرخ سود ۲۴٪، اما هیچ مبلغی مسدود نمی‌شود و کل ۱۰۰ میلیون تومان بدون کارمزد اضافه به شما پرداخت می‌شود.»",
      stageIndex: 1,
      stepIndex: 3,
      titleClassName: "is-long",
      options: [
        {
          id: "compare-total-cost",
          label:
            "از بانک می‌خواهم جدول دقیق بازپرداخت هر دو وام را به من بدهد تا با محاسبه دقیق «نرخ سود مؤثر» و کل پولی که در نهایت به بانک برمی‌گردانم، گزینه ارزان‌تر را پیدا کنم.",
        },
        {
          id: "choose-no-blocked-money",
          label:
            "پیشنهاد دوم (سود ۲۴٪) را انتخاب می‌کنم؛ چون به کل مبلغ ۱۰۰ میلیون تومان نیاز دارم و مسدود شدن بخشی از پول، ارزش وام با سود کمتر را از بین می‌برد.",
        },
        {
          id: "choose-by-installment",
          label:
            "تنها ملاک من توان پرداخت ماهانه است؛ می‌پرسم مبلغ قسط ماهانه کدام وام کمتر است و همان را انتخاب می‌کنم، فارغ از اینکه شرایط مسدودی یا کارمزدشان چگونه باشد.",
        },
        {
          id: "choose-lower-rate",
          label:
            "پیشنهاد اول (سود ۱۸٪) را انتخاب می‌کنم؛ زیرا نرخ سود آن به شکل قابل‌توجهی پایین‌تر است و در نتیجه سود کمتری به بانک پرداخت خواهم کرد.",
        },
        {
          id: "choose-simpler-admin",
          label:
            "خیلی درگیر مقایسه این اعداد نمی‌شوم؛ وامی را انتخاب می‌کنم که زودتر به حسابم واریز شود و ضامن یا دردسرهای اداری کمتری داشته باشد.",
        },
      ],
    },
    {
      type: "personal-info",
      stageIndex: 2,
      stepIndex: 0,
    },
  ];
  const stages = [
    {
      title: "تصمیم‌گیری اعتباری",
      count: 6,
      icon: healthIconUrl,
    },
    {
      title: "ترجیحات مالی",
      count: 4,
      icon: folderIconUrl,
    },
    {
      title: "اطلاعات کاربر",
      count: 4,
      icon: profileIconUrl,
    },
  ];
  const prototypeQuestion = questions[currentQuestion];
  const canonicalQuestion = getCanonicalQuestionForPrototypeIndex(currentQuestion);
  // The legacy index remains layout/navigation glue only. Behavioural wording
  // and answer identifiers always come from the verified canonical artifact.
  const question = canonicalQuestion
    ? {
        ...prototypeQuestion,
        title: canonicalQuestion.prompt,
        options: canonicalQuestion.answerOptions.map((option) => ({
          id: option.answerId,
          label: option.label,
        })),
      }
    : prototypeQuestion;
  const selectedOption = answers[currentQuestion] || "";
  const selectedIncomeLabel = incomeOptions.find((option) => option.value === personalInfo.income)?.label || "";
  const selectedJobLabel = jobOptions.find((option) => option.value === personalInfo.job)?.label || "";
  const isStagedQuestion = currentQuestion >= 2;
  const isPersonalQuestion = currentQuestion === personalInfoQuestionIndex;
  const isPersonalInfoQuestion = isPersonalQuestion && !isOtpVerificationStep;
  const isOtpQuestion = isPersonalQuestion && isOtpVerificationStep;
  const isPersonalStageQuestion = isPersonalQuestion;
  const loanOtpValue = loanOtp.join("");
  const isPersonalInfoComplete =
    personalInfo.firstName.trim() &&
    personalInfo.lastName.trim() &&
    personalInfo.phone.length === 9 &&
    personalInfo.income &&
    personalInfo.job &&
    !personalInfoErrors.firstName &&
    !personalInfoErrors.lastName;
  const canProceed = isOtpQuestion
    ? loanOtpValue.length === 6
    : isPersonalInfoQuestion
      ? Boolean(isPersonalInfoComplete)
      : Boolean(selectedOption) && !isSavingQuestionnaireAnswer;
  const nextQuestionButtonText = isOtpQuestion
    ? "تایید و جستجوی وام"
    : isPersonalInfoQuestion
      ? "تایید"
      : "پاسخ به سوال بعد";
  const previousQuestionButtonText = isPersonalStageQuestion
    ? "بازگشت به مرحله قبل"
    : "بازگشت به سوال قبل";
  const routePath = isAnalyzingLoans
    ? "/analysis"
    : loanResultView === "results"
      ? "/loan-results"
      : loanResultView === "details"
      ? `/loan-details?loanId=${encodeURIComponent(selectedLoanId)}`
        : loanResultView === "request"
          ? "/loan-request"
          : loanResultView === "compare"
            ? "/compare-loans"
            : loanResultView === "compare-result"
              ? "/compare-result"
              : loanResultView === "ai-analysis"
                ? "/ai-analysis"
                : isOtpQuestion
                  ? "/verify-code"
                  : isPersonalInfoQuestion
                    ? "/personal-info"
                    : getQuestionnaireRouteForPrototypeQuestionIndex(currentQuestion)
                      ?? `/question/${currentQuestion + 1}`;
  const maxStageOffset = stageOffsets[stageOffsets.length - 1];
  const stagedQuestionIndexes = questions.reduce((groups, item, index) => {
    if (item.stageIndex === undefined) return groups;
    return {
      ...groups,
      [item.stageIndex]: [...(groups[item.stageIndex] || []), index],
    };
  }, {});
  const completedStageIndexes = stages
    .map((stage, index) => {
      const indexes = stagedQuestionIndexes[index] || [];
      const hasAllStageQuestions = indexes.length >= stage.count;
      const allExistingAnswered = indexes.every((questionIndex) => answers[questionIndex]);
      return hasAllStageQuestions && allExistingAnswered ? index : null;
    })
    .filter((index) => index !== null);
  const workflowActiveStageIndex = stages.findIndex(
    (_, index) => !completedStageIndexes.includes(index),
  );
  const activeStageIndex =
    workflowActiveStageIndex === -1 ? stages.length - 1 : workflowActiveStageIndex;

  useEffect(() => {
    const routeState = getQuestionnaireRouteState(window.location.pathname);
    setCurrentQuestion(routeState.questionIndex);
    setIsOtpVerificationStep(routeState.isOtpVerificationStep);
    setIsAnalyzingLoans(routeState.isAnalyzingLoans);
    setLoanResultView(routeState.loanResultView);
    if (routeState.loanResultView === "details") setSelectedLoanId(getLoanIdFromLocation());
  }, []);

  useEffect(() => {
    if (!didSkipInitialRouteSyncRef.current) {
      didSkipInitialRouteSyncRef.current = true;
      return;
    }

    replaceRoute(routePath);
  }, [routePath]);

  useEffect(() => {
    function handleRouteChange() {
      const routeState = getQuestionnaireRouteState(window.location.pathname);
      setCurrentQuestion(routeState.questionIndex);
      setIsOtpVerificationStep(routeState.isOtpVerificationStep);
      setIsAnalyzingLoans(routeState.isAnalyzingLoans);
      setLoanResultView(routeState.loanResultView);
      if (routeState.loanResultView === "details") setSelectedLoanId(getLoanIdFromLocation());
      setLoanOtpError("");
    }

    window.addEventListener("popstate", handleRouteChange);

    return () => {
      window.removeEventListener("popstate", handleRouteChange);
    };
  }, []);

  useEffect(() => {
    if (!isStagedQuestion) return;
    setStageOffset(stageOffsets[question.stageIndex] || 0);
  }, [isStagedQuestion, question.stageIndex, stageOffsets]);

  useEffect(() => {
    if (!isStagedQuestion) return;

    const visiblePreviousTail = 12;
    const stageGap = 13;
    const measuredOffsets = stages.map((_, index) => {
      if (index === 0) return 0;

      return stageItemRefs.current
        .slice(0, index)
        .reduce((offset, item) => offset + (item?.offsetWidth || 0) + stageGap, 0) - visiblePreviousTail;
    });

    setStageOffsets(measuredOffsets);
  }, [activeStageIndex, completedStageIndexes.length, isStagedQuestion]);

  useEffect(() => {
    if (!isOtpVerificationStep || loanOtpSeconds <= 0) return undefined;

    const timerId = window.setTimeout(() => {
      setLoanOtpSeconds((seconds) => Math.max(seconds - 1, 0));
    }, 1000);

    return () => window.clearTimeout(timerId);
  }, [isOtpVerificationStep, loanOtpSeconds]);

  useEffect(() => {
    if (!isAnalyzingLoans) return undefined;

    setAnalysisCountdown(5);
    setIsAnalysisSpinnerRunning(true);

    const timerId = window.setInterval(() => {
      setAnalysisCountdown((current) => {
        if (current <= 1) {
          window.clearInterval(timerId);
          setIsAnalysisSpinnerRunning(false);
          setIsAnalyzingLoans(false);
          setLoanResultView("results");
          return 0;
        }

        return current - 1;
      });
    }, 1000);

    return () => window.clearInterval(timerId);
  }, [isAnalyzingLoans]);

  useEffect(() => {
    if (loanResultView !== "results" || recommendationResult || recommendationStatus === "loading") return;
    if (!questionnaireSessionId) {
      setRecommendationStatus("sessionMissing");
      return;
    }
    loadRecommendationResult();
  }, [loanResultView, questionnaireSessionId, recommendationResult, recommendationStatus]);

  function getNearestStageIndex(offset) {
    return stageOffsets.reduce((nearestIndex, currentOffset, index) => {
      const nearestDistance = Math.abs(offset - stageOffsets[nearestIndex]);
      const currentDistance = Math.abs(offset - currentOffset);
      return currentDistance < nearestDistance ? index : nearestIndex;
    }, 0);
  }

  function getLastAccessibleQuestionIndex(stageIndex) {
    const indexes = stagedQuestionIndexes[stageIndex] || [];
    if (!indexes.length) return null;
    if (stageIndex < activeStageIndex) return indexes[indexes.length - 1];
    if (stageIndex > activeStageIndex) return null;

    const firstUnansweredIndex = indexes.find((questionIndex) => !answers[questionIndex]);
    return firstUnansweredIndex ?? indexes[indexes.length - 1];
  }

  function goToStage(stageIndex) {
    const targetQuestionIndex = getLastAccessibleQuestionIndex(stageIndex);
    if (targetQuestionIndex === null) {
      setStageOffset(stageOffsets[question.stageIndex] || 0);
      return;
    }

    setCurrentQuestion(targetQuestionIndex);
    setStageOffset(stageOffsets[stageIndex] || 0);
  }

  function getQuestionIndexForStep(stageIndex, stepIndex) {
    return (stagedQuestionIndexes[stageIndex] || []).find(
      (questionIndex) => questions[questionIndex].stepIndex === stepIndex,
    );
  }

  function canGoToStep(stageIndex, stepIndex) {
    const targetQuestionIndex = getQuestionIndexForStep(stageIndex, stepIndex);
    if (targetQuestionIndex === undefined) return false;
    return Boolean(answers[targetQuestionIndex]) || targetQuestionIndex === currentQuestion;
  }

  function handleStepClick(stageIndex, stepIndex) {
    if (!canGoToStep(stageIndex, stepIndex)) return;
    const targetQuestionIndex = getQuestionIndexForStep(stageIndex, stepIndex);
    setCurrentQuestion(targetQuestionIndex);
  }

  async function persistCanonicalQuestionnaireAnswer() {
    if (!canonicalQuestion) return true;

    setIsSavingQuestionnaireAnswer(true);
    setQuestionnaireSessionError("");
    try {
      let sessionId = questionnaireSessionId;
      if (!sessionId) {
        const session = await startQuestionnaireSession();
        sessionId = session.sessionId;
        setQuestionnaireSessionId(sessionId);
      }
      await saveQuestionnaireAnswer(sessionId, canonicalQuestion.questionId, selectedOption);
      return true;
    } catch {
      setQuestionnaireSessionError(
        "ذخیره پاسخ انجام نشد. لطفاً اتصال را بررسی کنید و دوباره تلاش کنید.",
      );
      return false;
    } finally {
      setIsSavingQuestionnaireAnswer(false);
    }
  }

  async function loadRecommendationResult() {
    if (!questionnaireSessionId) {
      setRecommendationStatus("sessionMissing");
      return;
    }
    setRecommendationStatus("loading");
    try {
      const result = await fetchRecommendationResult(questionnaireSessionId);
      setRecommendationResult(result);
      setRecommendationStatus("ready");
    } catch {
      setRecommendationStatus("error");
    }
  }

  async function handleNextQuestion() {
    if (!canProceed) return;
    if (!(await persistCanonicalQuestionnaireAnswer())) return;
    if (isPersonalInfoQuestion) {
      setIsOtpVerificationStep(true);
      setLoanOtp(Array(6).fill(""));
      setLoanOtpSeconds(120);
      setLoanOtpError("");
      return;
    }
    if (isOtpQuestion) {
      // Deliberate local-only prototype flow: no OTP provider is called and no
      // real authentication, application or approval claim is made.
      if (loanOtpValue !== "۱۲۳۴۵۶") {
        setLoanOtpError("کد وارد شده اشتباه است");
        return;
      }
      const accountProfile = {
        firstName: personalInfo.firstName.trim(),
        lastName: personalInfo.lastName.trim(),
        phone: personalInfo.phone,
      };
      setCachedAccountProfile(accountProfile);
      onAccountCreated(accountProfile);
      setLoanResultView("");
      setIsAnalyzingLoans(true);
      setIsAnalysisSpinnerRunning(true);
      setAnalysisCountdown(5);
      setLoanOtpError("");
      return;
    }
    if (canonicalQuestion?.questionId === "S13") {
      // The final canonical answer must lead to the restored local profile
      // and demonstration-OTP screens before recommendations are requested.
      setCurrentQuestion(personalInfoQuestionIndex);
      setIsOtpVerificationStep(false);
      return;
    }
    if (currentQuestion === 1 && selectedOption !== "person") return;
    if (currentQuestion >= questions.length - 1) return;

    setCurrentQuestion((current) => current + 1);
  }

  function handlePreviousQuestion() {
    if (isOtpQuestion) {
      setIsOtpVerificationStep(false);
      setLoanOtpError("");
      return;
    }

    if (currentQuestion === 0) {
      onBack();
      return;
    }

    setCurrentQuestion((current) => current - 1);
  }

  function handleSelectOption(optionId) {
    setAnswers((current) => ({
      ...current,
      [currentQuestion]: optionId,
    }));
  }

  function handleLoanResultBack() {
    if (loanResultView === "ai-analysis") {
      setLoanResultView("compare-result");
      return;
    }

    if (loanResultView === "compare-result") {
      setLoanResultView("compare");
      return;
    }

    if (loanResultView === "details" || loanResultView === "request" || loanResultView === "compare") {
      setLoanResultView("results");
      return;
    }

    setLoanResultView("");
    setIsOtpVerificationStep(false);
    setCurrentQuestion(11);
  }

  function handleLoanDetailsOpen(loanId) {
    setSelectedLoanId(loanId);
    setLoanResultView("details");
  }

  function handleLoanCompareOpen(result = recommendationResult) {
    if (result) setRecommendationResult(result);
    setLoanResultView("compare");
  }

  function handleLoanCompareSubmit(selectedPlanIds) {
    setSelectedComparisonPlanIds(selectedPlanIds);
    setLoanResultView("compare-result");
  }

  function handleLoanAiAnalysisOpen(loanId) {
    setSelectedAnalysisLoanId(loanId);
    setLoanResultView("ai-analysis");
  }

  function handleLoanRequestOpen() {
    // The current recommendation result is already state-owned. This action only
    // changes the route/view; it must not replace that result with an event object.
    setLoanResultView("request");
  }

  function handleStartQuestionnaire() {
    setRecommendationResult(null);
    setRecommendationStatus("idle");
    setLoanResultView("");
    setIsOtpVerificationStep(false);
    setCurrentQuestion(2);
  }

  function handlePersonalInfoChange(field, value) {
    setPersonalInfo((current) => ({
      ...current,
      [field]: value,
    }));
  }

  function handlePersianNameChange(field, value) {
    const sanitizedValue = sanitizePersianName(value);
    const hasInvalidCharacter = hasInvalidPersianNameCharacter(value);

    setPersonalInfo((current) => ({
      ...current,
      [field]: sanitizedValue,
    }));
    setCachedPersonalInfo((current) => ({
      ...current,
      [field]: sanitizedValue || current[field],
    }));
    setCachedPersonalInfoValue(field, sanitizedValue);
    setPersonalInfoErrors((current) => ({
      ...current,
      [field]: hasInvalidCharacter ? persianNameError : "",
    }));
  }

  function handlePhoneChange(value) {
    const sanitizedValue = sanitizePhoneDigits(value);
    handlePersonalInfoChange("phone", sanitizedValue);
    setCachedPersonalInfo((current) => ({
      ...current,
      phone: sanitizedValue || current.phone,
    }));
    setCachedPersonalInfoValue("phone", sanitizedValue);
  }

  function handleCachedPersonalInfoSelect(field) {
    const cachedValue = cachedPersonalInfo[field];
    if (!cachedValue) return;

    if (field === "phone") {
      handlePhoneChange(cachedValue);
    } else {
      handlePersianNameChange(field, cachedValue);
    }

    setFocusedPersonalInfoField("");
  }

  function handleLoanOtpChange(index, value) {
    const digits = sanitizeOtpDigits(value);
    if (!digits.length) {
      setLoanOtp((current) => current.map((digit, digitIndex) => (digitIndex === index ? "" : digit)));
      setLoanOtpError("");
      return;
    }

    setLoanOtp((current) => {
      const nextOtp = [...current];
      digits.slice(0, 6 - index).forEach((digit, offset) => {
        nextOtp[index + offset] = digit;
      });
      return nextOtp;
    });
    setLoanOtpError("");

    const nextFocusIndex = Math.min(index + digits.length, 5);
    window.requestAnimationFrame(() => loanOtpRefs.current[nextFocusIndex]?.focus());
  }

  function handleLoanOtpKeyDown(index, event) {
    if (event.key === "Backspace" && !loanOtp[index] && index > 0) {
      loanOtpRefs.current[index - 1]?.focus();
    }
  }

  function handleLoanOtpPaste(event) {
    event.preventDefault();
    handleLoanOtpChange(0, event.clipboardData.getData("text"));
  }

  function handleLoanOtpResend() {
    setLoanOtp(Array(6).fill(""));
    setLoanOtpSeconds(120);
    setLoanOtpError("");
    loanOtpRefs.current[0]?.focus();
  }

  function handleStageDragStart(event) {
    const clientX = event.clientX ?? event.touches?.[0]?.clientX;
    if (clientX === undefined) return;

    stageDragRef.current = {
      isDragging: true,
      startX: clientX,
      startOffset: stageOffset,
      lastOffset: stageOffset,
    };
  }

  function handleStageDragMove(event) {
    if (!stageDragRef.current.isDragging) return;

    const clientX = event.clientX ?? event.touches?.[0]?.clientX;
    if (clientX === undefined) return;

    const deltaX = clientX - stageDragRef.current.startX;
    const nextOffset = Math.min(
      Math.max(stageDragRef.current.startOffset + deltaX, 0),
      maxStageOffset,
    );
    stageDragRef.current.lastOffset = nextOffset;
    setStageOffset(nextOffset);
  }

  function handleStageDragEnd() {
    if (!stageDragRef.current.isDragging) return;
    stageDragRef.current.isDragging = false;
    goToStage(getNearestStageIndex(stageDragRef.current.lastOffset));
  }

  if (isAnalyzingLoans) {
    return (
      <main className="hp-loan-analysis-page" dir="rtl" aria-busy={isAnalysisSpinnerRunning}>
        <div className="hp-analysis-logo-cloud" aria-hidden="true">
          {analysisLogoUrls.map((logoUrl, index) => {
            const [x, y] = analysisLogoPositions[index] || [50, 50];

            return (
              <img
                src={logoUrl}
                alt=""
                style={{
                  "--logo-x": `${x}%`,
                  "--logo-y": `${y}%`,
                  "--logo-tilt": `${(index % 5) * 3 - 6}deg`,
                }}
                key={`${logoUrl}-${index}`}
              />
            );
          })}
        </div>
        <div className={`hp-analysis-spinner ${isAnalysisSpinnerRunning ? "is-running" : ""}`}>
          <svg className="hp-analysis-spinner-ring" viewBox="0 0 232 232" aria-hidden="true">
            <circle cx="116" cy="116" r="100" />
          </svg>
          <span>{toPersianDigits(analysisCountdown)}</span>
        </div>
        <p>
          سیستم در حال یافتن
          <br />
          مناسب‌ترین وام‌ها با شرایط شماست.
        </p>
      </main>
    );
  }

  if (loanResultView === "results") {
    return (
      <LoanResultsScreen
        result={recommendationResult}
        status={recommendationStatus}
        onRetry={loadRecommendationResult}
        onStartQuestionnaire={handleStartQuestionnaire}
        header={<QuestionnaireHeader onBack={handleLoanResultBack} onMenu={onMenu} onHome={onHome} />}
        onDetails={handleLoanDetailsOpen}
        onCompare={handleLoanCompareOpen}
        onRequest={handleLoanRequestOpen}
      />
    );
  }

  if (loanResultView === "details") {
    return (
      <LoanDetailsScreen
        loanId={selectedLoanId}
        header={<QuestionnaireHeader onBack={handleLoanResultBack} onMenu={onMenu} onHome={onHome} />}
      />
    );
  }

  if (loanResultView === "request") {
    return (
      <LoanCompareScreen
        result={recommendationResult}
        onBack={handleLoanResultBack}
        onMenu={onMenu}
        onHome={onHome}
        mode="request"
      />
    );
  }

  if (loanResultView === "compare") {
    return (
      <LoanCompareScreen
        result={recommendationResult}
        onBack={handleLoanResultBack}
        onMenu={onMenu}
        onHome={onHome}
        onCompareSubmit={handleLoanCompareSubmit}
        mode="compare"
        initialSelectedPlanIds={selectedComparisonPlanIds}
      />
    );
  }

  if (loanResultView === "compare-result") {
    return (
      <LoanComparisonResultScreen
        result={recommendationResult}
        onBack={handleLoanResultBack}
        onMenu={onMenu}
        onHome={onHome}
        onAiAnalysis={handleLoanAiAnalysisOpen}
        selectedPlanIds={selectedComparisonPlanIds}
      />
    );
  }

  if (loanResultView === "ai-analysis") {
    return (
      <LoanAiAnalysisScreen
        onBack={handleLoanResultBack}
        result={recommendationResult}
        loanId={selectedAnalysisLoanId || selectedComparisonPlanIds[0] || ""}
      />
    );
  }

  return (
    <main className="hp-questionnaire-page" dir="rtl">
      <header className="hp-questionnaire-header">
        <button className="hp-questionnaire-icon-button" type="button" onClick={onBack} aria-label="بازگشت">
          <svg viewBox="0 0 24 24" focusable="false">
            <path d="M20 12H5" />
            <path d="m12 19-7-7 7-7" />
          </svg>
        </button>
        <a className="hp-questionnaire-brand" href="/" onClick={onHome}>
          <img src={logoUrl} alt="شهاب" />
          <span>
            <strong>شهاب</strong>
            <small>(شبکه هم‌رسانی اعتبار برخط)</small>
          </span>
        </a>
        <button className="hp-questionnaire-menu" type="button" onClick={onMenu} aria-label="منو">
          <span />
          <span />
          <span />
        </button>
      </header>

      <section className="hp-questionnaire-content">
        {isStagedQuestion ? (
          <div className="hp-stage-board" aria-label="مراحل پرسشنامه">
            <div
              className={`hp-stage-track ${isPersonalStageQuestion ? "is-personal-info" : ""}`}
              style={{ transform: `translateX(${stageOffset}px)` }}
              onPointerDown={handleStageDragStart}
              onPointerMove={handleStageDragMove}
              onPointerUp={handleStageDragEnd}
              onPointerCancel={handleStageDragEnd}
              onPointerLeave={handleStageDragEnd}
            >
              {stages.map((stage, index) => (
                <div
                  className={`hp-stage-item ${completedStageIndexes.includes(index) ? "is-complete" : ""} ${index === activeStageIndex ? "is-active" : ""}`}
                  key={stage.title}
                  ref={(element) => {
                    stageItemRefs.current[index] = element;
                  }}
                >
                  <img className="hp-stage-icon" src={stage.icon} alt="" aria-hidden="true" />
                  <span>{stage.title}</span>
                </div>
              ))}
            </div>
            <div
              className="hp-step-line"
              style={{ "--step-count": isPersonalStageQuestion ? 2 : stages[question.stageIndex].count }}
            >
              {Array.from({ length: isPersonalStageQuestion ? 2 : stages[question.stageIndex].count }).map((_, index) => {
                const isPersonalCurrent = isPersonalStageQuestion && index === (isOtpQuestion ? 1 : 0);
                const isPersonalDone = isPersonalStageQuestion && index === (isOtpQuestion ? 0 : 1);

                return (
                  <button
                    className={`hp-step-dot ${isPersonalStageQuestion ? (isPersonalDone ? "is-done" : "") : (answers[getQuestionIndexForStep(question.stageIndex, index)] && getQuestionIndexForStep(question.stageIndex, index) !== currentQuestion ? "is-done" : "")} ${isPersonalStageQuestion ? (isPersonalCurrent ? "is-current" : "") : (index === question.stepIndex ? "is-current" : "")}`}
                    type="button"
                    disabled={isPersonalStageQuestion || !canGoToStep(question.stageIndex, index)}
                    key={index}
                    onClick={() => !isPersonalStageQuestion && handleStepClick(question.stageIndex, index)}
                  >
                    {toPersianDigits(index + 1)}
                  </button>
                );
              })}
            </div>
          </div>
        ) : null}

        {isOtpQuestion ? (
          <>
          <div className="hp-loan-otp-card">
            <label>کد یکبار مصرف</label>
            <div className="hp-loan-otp-row" dir="ltr">
              {loanOtp.map((digit, index) => (
                <input
                  key={index}
                  ref={(element) => {
                    loanOtpRefs.current[index] = element;
                  }}
                  type="tel"
                  inputMode="numeric"
                  pattern="[0-9۰-۹٠-٩]*"
                  maxLength={1}
                  value={digit}
                  onBeforeInput={(event) => {
                    if (event.data && !Array.from(event.data).every((character) => phoneDigitPattern.test(character))) {
                      event.preventDefault();
                    }
                  }}
                  onChange={(event) => handleLoanOtpChange(index, event.target.value)}
                  onKeyDown={(event) => handleLoanOtpKeyDown(index, event)}
                  onPaste={handleLoanOtpPaste}
                  aria-label={`رقم ${toPersianDigits(index + 1)} کد یکبار مصرف`}
                />
              ))}
            </div>
            <div className="hp-loan-otp-links">
              <button type="button" onClick={() => setIsOtpVerificationStep(false)}>تغییر شماره تلفن</button>
              <button type="button" disabled={loanOtpSeconds > 0} onClick={handleLoanOtpResend}>
                {loanOtpSeconds > 0 ? `(${formatOtpCountdown(loanOtpSeconds)})` : "ارسال مجدد"}
              </button>
            </div>
          </div>
          {loanOtpError ? <p className="hp-loan-otp-error">{loanOtpError}</p> : null}
          </>
        ) : isPersonalInfoQuestion ? (
          <form className="hp-personal-info-form" onSubmit={(event) => event.preventDefault()}>
            <label>
              <span>نام</span>
              <input
                maxLength={12}
                list="hp-first-name-cache"
                autoComplete="given-name"
                value={personalInfo.firstName}
                onFocus={() => setFocusedPersonalInfoField("firstName")}
                onBlur={() => window.setTimeout(() => setFocusedPersonalInfoField(""), 120)}
                onChange={(event) => handlePersianNameChange("firstName", event.target.value)}
              />
              <datalist id="hp-first-name-cache">
                {cachedPersonalInfo.firstName ? <option value={cachedPersonalInfo.firstName} /> : null}
              </datalist>
              {focusedPersonalInfoField === "firstName" && cachedPersonalInfo.firstName && cachedPersonalInfo.firstName !== personalInfo.firstName ? (
                <button className="hp-personal-cache-suggestion" type="button" onMouseDown={(event) => event.preventDefault()} onClick={() => handleCachedPersonalInfoSelect("firstName")}>
                  {cachedPersonalInfo.firstName}
                </button>
              ) : null}
              {personalInfoErrors.firstName ? (
                <small className="hp-personal-field-error">{personalInfoErrors.firstName}</small>
              ) : null}
            </label>
            <label>
              <span>نام خانوادگی</span>
              <input
                maxLength={12}
                list="hp-last-name-cache"
                autoComplete="family-name"
                value={personalInfo.lastName}
                onFocus={() => setFocusedPersonalInfoField("lastName")}
                onBlur={() => window.setTimeout(() => setFocusedPersonalInfoField(""), 120)}
                onChange={(event) => handlePersianNameChange("lastName", event.target.value)}
              />
              <datalist id="hp-last-name-cache">
                {cachedPersonalInfo.lastName ? <option value={cachedPersonalInfo.lastName} /> : null}
              </datalist>
              {focusedPersonalInfoField === "lastName" && cachedPersonalInfo.lastName && cachedPersonalInfo.lastName !== personalInfo.lastName ? (
                <button className="hp-personal-cache-suggestion" type="button" onMouseDown={(event) => event.preventDefault()} onClick={() => handleCachedPersonalInfoSelect("lastName")}>
                  {cachedPersonalInfo.lastName}
                </button>
              ) : null}
              {personalInfoErrors.lastName ? (
                <small className="hp-personal-field-error">{personalInfoErrors.lastName}</small>
              ) : null}
            </label>
            <label>
              <span>شماره تلفن همراه</span>
              <div className="hp-personal-phone">
                <span>۰۹</span>
                <input
                  inputMode="numeric"
                  pattern="[0-9۰-۹٠-٩]*"
                  maxLength={9}
                  list="hp-phone-cache"
                  autoComplete="tel-national"
                  value={personalInfo.phone}
                  onFocus={() => setFocusedPersonalInfoField("phone")}
                  onBlur={() => window.setTimeout(() => setFocusedPersonalInfoField(""), 120)}
                  onBeforeInput={(event) => {
                    if (
                      event.data &&
                      (!Array.from(event.data).every((character) => phoneDigitPattern.test(character)) ||
                        sanitizePhoneDigits(`${personalInfo.phone}${event.data}`).length === personalInfo.phone.length)
                    ) {
                      event.preventDefault();
                    }
                  }}
                  onChange={(event) => handlePhoneChange(event.target.value)}
                />
                <datalist id="hp-phone-cache">
                  {cachedPersonalInfo.phone ? <option value={cachedPersonalInfo.phone} /> : null}
                </datalist>
              </div>
              {focusedPersonalInfoField === "phone" && cachedPersonalInfo.phone && cachedPersonalInfo.phone !== personalInfo.phone ? (
                <button className="hp-personal-cache-suggestion" type="button" onMouseDown={(event) => event.preventDefault()} onClick={() => handleCachedPersonalInfoSelect("phone")}>
                  {cachedPersonalInfo.phone}
                </button>
              ) : null}
            </label>
            <label>
              <span>میزان درآمد</span>
              <span className="hp-personal-select">
                <span
                  className={`hp-personal-dropdown ${isIncomeDropdownOpen ? "is-open" : ""}`}
                  onBlur={(event) => {
                    if (!event.currentTarget.contains(event.relatedTarget)) {
                      setIsIncomeDropdownOpen(false);
                    }
                  }}
                >
                  <button
                    className="hp-personal-dropdown-trigger"
                    type="button"
                    aria-haspopup="listbox"
                    aria-expanded={isIncomeDropdownOpen}
                    onClick={() => setIsIncomeDropdownOpen((current) => !current)}
                  >
                    <span>{selectedIncomeLabel}</span>
                  </button>
                  {isIncomeDropdownOpen ? (
                    <span className="hp-personal-dropdown-menu" role="listbox">
                      {incomeOptions.map((option) => (
                        <button
                          className={`hp-personal-dropdown-option ${personalInfo.income === option.value ? "is-selected" : ""}`}
                          type="button"
                          role="option"
                          aria-selected={personalInfo.income === option.value}
                          key={option.value}
                          onClick={() => {
                            handlePersonalInfoChange("income", option.value);
                            setIsIncomeDropdownOpen(false);
                          }}
                        >
                          {option.label}
                        </button>
                      ))}
                    </span>
                  ) : null}
                </span>
                <select
                  value={personalInfo.income}
                  onChange={(event) => handlePersonalInfoChange("income", event.target.value)}
                >
                  <option value=""></option>
                  <option value="up-to-22">تا 22 میلیون تومان</option>
                  <option value="22-to-50">22 تا 50 میلیون تومان</option>
                  <option value="50-to-80">50 تا 80 میلیون تومان</option>
                  <option value="80-to-120">80 تا 120 میلیون تومان</option>
                  <option value="120-to-160">120 تا 160 میلیون تومان</option>
                  <option value="over-160">بیش از 160 میلیون تومان</option>
                </select>
              </span>
            </label>
            <label>
              <span>شغل</span>
              <span className="hp-personal-select">
                <span
                  className={`hp-personal-dropdown ${isJobDropdownOpen ? "is-open" : ""}`}
                  onBlur={(event) => {
                    if (!event.currentTarget.contains(event.relatedTarget)) {
                      setIsJobDropdownOpen(false);
                    }
                  }}
                >
                  <button
                    className="hp-personal-dropdown-trigger"
                    type="button"
                    aria-haspopup="listbox"
                    aria-expanded={isJobDropdownOpen}
                    onClick={() => setIsJobDropdownOpen((current) => !current)}
                  >
                    <span>{selectedJobLabel}</span>
                  </button>
                  {isJobDropdownOpen ? (
                    <span className="hp-personal-dropdown-menu" role="listbox">
                      {jobOptions.map((option) => (
                        <button
                          className={`hp-personal-dropdown-option ${personalInfo.job === option.value ? "is-selected" : ""}`}
                          type="button"
                          role="option"
                          aria-selected={personalInfo.job === option.value}
                          key={option.value}
                          onClick={() => {
                            handlePersonalInfoChange("job", option.value);
                            setIsJobDropdownOpen(false);
                          }}
                        >
                          {option.label}
                        </button>
                      ))}
                    </span>
                  ) : null}
                </span>
                <select
                  value={personalInfo.job}
                  onChange={(event) => handlePersonalInfoChange("job", event.target.value)}
                >
                  <option value=""></option>
                  <option value="employee">کارمند (کارشناس، کارمند شرکت یا اداره)</option>
                  <option value="manager">مدیر (مدیر شرکت، مدیر واحد، مدیر ارشد)</option>
                  <option value="entrepreneur">کارآفرین / صاحب کسب‌وکار (مؤسس، صاحب شرکت، صاحب استارتاپ)</option>
                  <option value="merchant">کاسب / بازاری (مغازه‌دار، فروشنده، عمده‌فروش، تاجر)</option>
                  <option value="freelancer">فریلنسر / خوداشتغال (مشاور مستقل، طراح، برنامه‌نویس آزاد)</option>
                  <option value="teacher">معلم / مدرس</option>
                  <option value="professional">متخصص حرفه‌ای (پزشک، وکیل، مهندس، حسابدار، روان‌شناس)</option>
                  <option value="technical-worker">کارگر / نیروی فنی (کارگر، تکنسین، تعمیرکار، نیروی فنی ماهر)</option>
                  <option value="driver">راننده / حمل‌ونقل (راننده تاکسی، پیک، راننده کامیون)</option>
                  <option value="farmer">کشاورز / دامدار</option>
                  <option value="homemaker">خانه‌دار</option>
                  <option value="student">دانشجو / محصل</option>
                  <option value="retired">بازنشسته</option>
                  <option value="unemployed">در حال حاضر بدون شغل (جویای کار، فاقد فعالیت شغلی)</option>
                  <option value="other">سایر</option>
                </select>
              </span>
            </label>
          </form>
        ) : (
          <>
            <h1 className={question.titleClassName || ""}>{toPersianDigits(question.title)}</h1>

            <div
              className={`hp-question-card ${currentQuestion === 1 ? "is-compact" : ""} ${isStagedQuestion ? "is-staged" : ""}`}
              role="radiogroup"
              aria-label="نوع وام"
            >
              {question.options.map((option, index) => (
                <div key={option.id}>
                  <button
                    className={`hp-question-option ${selectedOption === option.id ? "is-selected" : ""}`}
                    type="button"
                    role="radio"
                    aria-checked={selectedOption === option.id}
                    onClick={() => handleSelectOption(option.id)}
                  >
                    <span className="hp-option-check" aria-hidden="true" />
                    <span>{toPersianDigits(option.label)}</span>
                  </button>

                  {index === 0 && question.warning ? (
                    <div className="hp-question-warning">
                      <span className="hp-question-warning-icon" aria-hidden="true">!</span>
                      <p>{toPersianDigits(question.warning)}</p>
                    </div>
                  ) : null}
                </div>
              ))}
            </div>
          </>
        )}

        {questionnaireSessionError ? (
          <p className="hp-question-session-error" role="alert">
            {questionnaireSessionError}
          </p>
        ) : null}
        <div className="hp-question-actions">
          <button
            className={`hp-next-question ${isPersonalInfoQuestion ? "is-personal-confirm" : ""} ${isOtpQuestion ? "is-loan-otp-submit" : ""}`}
            type="button"
            disabled={!canProceed}
            onClick={handleNextQuestion}
          >
            {isPersonalInfoQuestion ? "تایید و جستجوی وام" : "پاسخ به سوال بعد"}
          </button>
          {currentQuestion > 0 ? (
            <button
              className={`hp-previous-question ${isPersonalStageQuestion ? "is-personal-stage-back" : ""}`}
              type="button"
              onClick={handlePreviousQuestion}
            >
              {isPersonalInfoQuestion ? "بازگشت به مرحله قبل" : "بازگشت به سوال قبل"}
            </button>
          ) : null}
        </div>
      </section>
    </main>
  );
}

function Hero({ onStartQuestionnaire }) {
  const [amount, setAmount] = useState("");
  const [isAmountOpen, setIsAmountOpen] = useState(false);
  const [showEligibilityNotice, setShowEligibilityNotice] = useState(false);

  function handleHeroSubmit(event) {
    event.preventDefault();

    if (!amount) {
      setIsAmountOpen(true);
      return;
    }

    setIsAmountOpen(false);
    setShowEligibilityNotice(true);
  }

  return (
    <section className="hp-hero">
      <h1>
        تأمین مالی شما یا کسب و کارتان{" "}
        <br />
        در کمتر از <em>۲۴ ساعت</em>
      </h1>

      {showEligibilityNotice ? (
        <div className="hp-eligibility-message" role="status" aria-live="polite">
          <p>
            برای پیشنهاد بهترین وام‌ها متناسب با شرایط و ترجیحات شما لازم است در ابتدا
            به تعدادی پرسش پاسخ دهید.
          </p>
          <button
            type="button"
            onClick={() => {
              setShowEligibilityNotice(false);
              onStartQuestionnaire();
            }}
          >
            متوجه شدم
          </button>
        </div>
      ) : (
        <>
          <p>
            با یک درخواست، بهترین پیشنهادهای بانک‌ها، نهادهای مالی{" "}
            <br />
            و سرمایه‌گذاران را دریافت و مقایسه کنید.
          </p>

          <form className="hp-hero-form" onSubmit={handleHeroSubmit}>
            <button className="hp-submit" type="submit">بررسی واجد شرایط بودن</button>
            <div
              className={`hp-select-wrap ${isAmountOpen ? "is-open" : ""}`}
              onBlur={() => setIsAmountOpen(false)}
            >
              <button
                className="hp-select-trigger"
                type="button"
                onClick={() => setIsAmountOpen((current) => !current)}
              >
                {amount || "چقدر سرمایه نیاز دارید؟"}
              </button>
              <span>⌄</span>
              {isAmountOpen ? (
                <div className="hp-select-menu">
                  {amounts.map((item) => (
                    <button
                      key={item}
                      type="button"
                      onMouseDown={(event) => event.preventDefault()}
                      onClick={() => {
                        setAmount(item);
                        setIsAmountOpen(false);
                      }}
                    >
                      {item}
                    </button>
                  ))}
                </div>
              ) : null}
            </div>
          </form>
        </>
      )}
    </section>
  );
}

function CardView({ card }) {
  if (card.kind === "stat-dark") {
    return (
      <article className="hp-m-card hp-stat-dark">
        <div className="hp-stars">
          {Array.from({ length: 5 }).map((_, index) => (
            <Icon key={index} name="star" />
          ))}
        </div>
        <div>
          <strong>{card.value}</strong>
          <span>{card.label}</span>
        </div>
      </article>
    );
  }

  if (card.kind === "stat-lime") {
    return (
      <article className="hp-m-card hp-stat-lime">
        <Icon name={card.icon} />
        <div>
          <strong>{card.value}</strong>
          <span>{card.label}</span>
        </div>
      </article>
    );
  }

  if (card.kind === "stat-cream") {
    return (
      <article className="hp-m-card hp-stat-cream">
        <span className="hp-line-icon">◷</span>
        <div>
          <strong>{card.value}</strong>
          <span>{card.label}</span>
        </div>
      </article>
    );
  }

  if (card.kind === "quote") {
    return (
      <article className="hp-m-card hp-quote">
        <p>{card.text}</p>
        <div>
          <strong>{card.name}</strong>
          <span>{card.role}</span>
          <a href="#">مطالعه داستان مشتری <Icon name="arrow" /></a>
        </div>
      </article>
    );
  }

  return (
    <article className="hp-m-card hp-image-card">
      <img src={card.src} alt={card.name} />
      <div>
        <strong>{card.name}</strong>
        <span>{card.desc}</span>
        <Icon name="arrow" />
      </div>
    </article>
  );
}

function StatsMarquee() {
  return (
    <section className="hp-marquee" aria-label="آمار و نمونه مشتریان">
      <div className="hp-marquee-track">
        {[...cards, ...cards].map((card, index) => (
          <CardView key={`${card.kind}-${index}`} card={card} />
        ))}
      </div>
    </section>
  );
}

function Features() {
  return (
    <section id="process" className="hp-features">
      <div className="hp-section-heading">
        <span>چرا شهاب؟</span>
        <h2>
          ساده‌ترین مسیر برای رشد کسب‌وکار شما.
        </h2>
      </div>

      <div className="hp-feature-grid">
        {features.map((item) => (
          <article key={item.title} className="hp-feature-item">
            <Icon name="check" />
            <div>
              <h3>{item.title}</h3>
              <p>{item.desc}</p>
            </div>
          </article>
        ))}
      </div>

      <div id="start" className="hp-cta">
        <h2>
          آماده‌اید سرمایه‌ای را که نیاز دارید
          <br />
          دریافت کنید؟
        </h2>
        <p>هزاران کسب‌وکار به ما اعتماد کرده‌اند. نوبت شماست.</p>
        <a href="#" className="hp-lime-pill">همین حالا شروع کنید</a>
        <small>² زمان دریافت وجه بسته به نوع وام و وام‌دهنده می‌تواند متفاوت باشد.</small>
      </div>
    </section>
  );
}

function Footer() {
  const columns = [
    { title: "محصولات", links: ["وام سرمایه در گردش", "وام تجهیزات", "خط اعتباری", "تأمین مالی فاکتور"] },
    { title: "شرکت", links: ["درباره ما", "تیم ما", "فرصت‌های شغلی", "تماس با ما"] },
    { title: "منابع", links: ["وبلاگ", "راهنما", "محاسبه‌گر وام", "سؤالات متداول"] },
  ];

  return (
    <footer className="hp-footer">
      <div className="hp-footer-grid">
        <div className="hp-footer-about">
          <BrandMark footer />
          <p>پلتفرم مقایسه و دریافت وام برای کسب‌وکارهای کوچک و متوسط ایرانی.</p>
        </div>

        {columns.map((column) => (
          <nav key={column.title}>
            <h4>{column.title}</h4>
            {column.links.map((link) => (
              <a key={link} href="#">{link}</a>
            ))}
          </nav>
        ))}
      </div>

      <div className="hp-footer-bottom">
        <p>© ۱۴۰۴ شهاب. تمامی حقوق محفوظ است.</p>
        <div>
          <a href="#">حریم خصوصی</a>
          <a href="#">شرایط استفاده</a>
        </div>
      </div>
    </footer>
  );
}

export default function HomePage() {
  const [currentView, setCurrentView] = useState(() => getInitialViewFromPath(window.location.pathname));
  const [loginStep, setLoginStep] = useState(() => (window.location.pathname === "/login/otp" ? "otp" : "phone"));
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [accountProfile, setAccountProfile] = useState(() => getCachedAccountProfile());
  const sidebarUserName = accountProfile
    ? `${accountProfile.firstName} ${accountProfile.lastName}`.trim()
    : "";

  useEffect(() => {
    if (!isSidebarOpen) return undefined;

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    return () => {
      document.body.style.overflow = previousOverflow;
    };
  }, [isSidebarOpen]);

  useEffect(() => {
    if (currentView === "questionnaire") return;

    replaceRoute(currentView === "login" ? (loginStep === "otp" ? "/login/otp" : "/login") : "/");
  }, [currentView, loginStep]);

  useEffect(() => {
    function handleRouteChange() {
      const nextView = getInitialViewFromPath(window.location.pathname);
      setCurrentView(nextView);
      setLoginStep(window.location.pathname === "/login/otp" ? "otp" : "phone");
    }

    window.addEventListener("popstate", handleRouteChange);

    return () => {
      window.removeEventListener("popstate", handleRouteChange);
    };
  }, []);

  function handleLoginOpen() {
    setCurrentView("login");
    setLoginStep("phone");
  }

  function handleAccountCreated(profile) {
    setAccountProfile(profile);
  }

  function handleQuestionnaireOpen() {
    replaceRoute("/question/1");
    setCurrentView("questionnaire");
  }

  function handleHomeOpen(event) {
    event?.preventDefault();
    setIsSidebarOpen(false);
    replaceRoute("/");
    setCurrentView("home");
    setLoginStep("phone");
  }

  function handleBack() {
    if (isSidebarOpen) {
      setIsSidebarOpen(false);
      return;
    }

    if (currentView === "login" && loginStep === "otp") {
      setLoginStep("phone");
      return;
    }

    if (currentView === "login") {
      setCurrentView("home");
      return;
    }

    if (currentView === "questionnaire") {
      setCurrentView("home");
    }
  }

  if (currentView === "questionnaire") {
    return (
      <div className="hp-page hp-questionnaire-shell" dir="rtl">
        <UserSidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} userName={sidebarUserName} />
        <QuestionnaireScreen
          onBack={handleBack}
          onMenu={() => setIsSidebarOpen(true)}
          onAccountCreated={handleAccountCreated}
          onHome={handleHomeOpen}
        />
      </div>
    );
  }

  return (
    <div className="hp-page" dir="rtl">
      <Nav
        isLoginView={currentView === "login"}
        onLogin={handleLoginOpen}
        onBack={handleBack}
        onMenu={() => setIsSidebarOpen(true)}
        onHome={handleHomeOpen}
      />
      <UserSidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} userName={sidebarUserName} />
      {currentView === "login" ? (
        <LoginScreen loginStep={loginStep} setLoginStep={setLoginStep} />
      ) : (
        <>
          <main>
            <Hero onStartQuestionnaire={handleQuestionnaireOpen} />
            <StatsMarquee />
            <Features />
          </main>
          <Footer />
        </>
      )}
    </div>
  );
}
