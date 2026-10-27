import ContactPage from "./features/contact/ContactPage.jsx";
import contactIconUrl from "../assets/call-calling.svg";
import AboutPage from "./features/about/AboutPage.jsx";
import { readAccountProfileCache, writeAccountProfileCache, readPersonalInfoCache, writePersonalInfoCache, synchronizeAccountTabs, readRecommendationCache, writeRecommendationCache } from "./features/account/accountBrowserState.mjs";
import { accountAccessEpoch, displayProfilePhone, hasProfileAccess, logoutProfile, normalizeProfilePhone, persistPersonalInfo, persistProfile, readOwnProfile, readPersonalInfoProfile, requestProfileCode, restoreAccountAccess, verifyProfileCode } from "./features/account/profileClient.mjs";
import { useEffect, useMemo, useRef, useState } from "react";
import { readSavedLoans, refreshSavedLoans } from "./features/account/savedLoans.mjs";
import { isSavedLoanDetailsPath, savedLoanDetailsPath } from "./features/account/savedLoansPresentation.mjs";
import LoanDetailsScreen from "./features/loan-details/LoanDetailsScreen.jsx";
import LoanResultsScreen from "./features/recommendation/ui/LoanResultsScreen.jsx";
import { fetchHistoricalRecommendation, fetchRecommendationHistory, hideRecommendationHistory } from "./features/recommendation/presentation/recommendationHistoryClient.mjs";
import historyIconUrl from "../assets/book-saved.svg";
import closeCircleIconUrl from "../assets/close-circle.svg";
import dangerIconUrl from "../assets/danger.svg";
import LoanComparisonCard from "./features/recommendation/ui/LoanComparisonCard.jsx";
import { fetchLoanDetails } from "./features/loan-details/loanDetailsApi.js";
import BankIdentity from "./features/loan-details/BankIdentity.jsx";
import LoanPercent from "./features/loan-details/LoanPercent.jsx";
import { toPersianDigits } from "./features/loan-details/toPersianDigits.mjs";
import DeferredPageSkeleton from "./shared/DeferredPageSkeleton.jsx";
import { fetchRecommendationResult } from "./features/recommendation/presentation/recommendationResultClient.mjs";
import {
  getCanonicalQuestionIdForRoute,
  getPrototypeQuestionIndexForCanonicalQuestionId,
  guardQuestionnaireRoute,
  getQuestionnaireRouteForPrototypeQuestionIndex,
  getQuestionnaireStepIdForPrototypeQuestionIndex,
  getPrototypeQuestionIndexForQuestionnaireStepId,
} from "./features/questionnaire/questionnaireRouteMap.mjs";
import { getCanonicalQuestionForPrototypeIndex } from "./features/questionnaire/canonicalQuestionnaire.mjs";
import {
  QuestionnaireSessionApiError,
  readQuestionnaireSession,
  readCurrentQuestionnaireSession,
  saveQuestionnaireAnswer,
  saveQuestionnaireFlowAnswer,
  startQuestionnaireSession,
} from "./features/questionnaire/questionnaireSessionClient.mjs";
import logoUrl from "../assets/shahab-logo.svg";
import folderIconUrl from "../assets/folder.svg";
import healthIconUrl from "../assets/health.svg";
import profileIconUrl from "../assets/profile.svg";
import sendIconUrl from "../assets/send.svg";
import sidebarLeftIconUrl from "../assets/sidebar-left.svg";
import addCircleIconUrl from "../assets/add-circle.svg";

// These images belong only to the five-second analysis screen. Loading them
// eagerly delayed every route, including results and loan details.
const bankLogoModules = import.meta.glob("../assets/iranian-bank-logos/*.{png,svg}", {
  import: "default",
  query: "?url",
});
let analysisLogoPromise;
function loadAnalysisLogos() {
  analysisLogoPromise ??= Promise.all(
    Object.entries(bankLogoModules)
      .sort(([firstPath], [secondPath]) => firstPath.localeCompare(secondPath))
      .map(([, loadLogo]) => loadLogo()),
  ).then((urls) => [...new Set(urls)]).catch(() => {
    analysisLogoPromise = undefined;
    return [];
  });
  return analysisLogoPromise;
}

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

function getCanonicalQuestionIdsFromPrototypeAnswers(answerByIndex = {}) {
  return Object.keys(answerByIndex)
    .map((index) => getCanonicalQuestionForPrototypeIndex(Number(index))?.questionId)
    .filter(Boolean);
}

function getFlowStepIdsFromPrototypeAnswers(answerByIndex = {}) {
  return Object.keys(answerByIndex)
    .map(Number)
    .map((index) => getQuestionnaireStepIdForPrototypeQuestionIndex(index))
    .filter((stepId) => stepId === "loan_type" || stepId === "entity_type");
}

function getGuardedQuestionnaireRouteState(pathname, answeredQuestionIds = [], answeredFlowStepIds = []) {
  const guardedPathname = guardQuestionnaireRoute(pathname, answeredQuestionIds, answeredFlowStepIds);
  return { ...getQuestionnaireRouteState(guardedPathname), pathname: guardedPathname };
}

function getLoanIdFromLocation() {
  if (typeof window === "undefined") return "";
  return new URLSearchParams(window.location.search).get("loanId")?.trim() || "";
}

/**
 * The active recommendation is kept only in the browser's current history
 * entry. This permits a detail-page refresh followed by Back without putting
 * questionnaire answers or the opaque session ID in a URL or web storage.
 */
function getActiveRecommendationHistoryState() {
  if (typeof window === "undefined") return null;
  const value = window.history.state?.shahabRecommendation;
  const sessionId = typeof value?.sessionId === "string" ? value.sessionId : null;
  const historyId = typeof value?.historyId === "string" ? value.historyId : getHistoryIdFromLocation();
  if (!sessionId && !historyId) return null;
  return {
    sessionId,
    historyId: historyId || null,
    selectedComparisonPlanIds: Array.isArray(value?.selectedComparisonPlanIds)
      ? value.selectedComparisonPlanIds.filter((id) => typeof id === "string").slice(0, 10)
      : [],
    result: sessionId ? readRecommendationCache(sessionId) : null,
  };
}

function replaceActiveRecommendationHistoryState(sessionId, result, selectedComparisonPlanIds) {
  if (typeof window === "undefined") return;
  if (sessionId) writeRecommendationCache(sessionId, result);
  const active = getActiveRecommendationHistoryState();
  const historyId = result?.historyId || active?.historyId || null;
  if (!sessionId && !historyId) return;
  window.history.replaceState(
    {
      ...(window.history.state || {}),
      shahabRecommendation: {
        ...(sessionId ? { sessionId } : {}),
        ...(historyId ? { historyId } : {}),
        ...((selectedComparisonPlanIds || active?.selectedComparisonPlanIds || []).length
          ? { selectedComparisonPlanIds: selectedComparisonPlanIds || active.selectedComparisonPlanIds }
          : {}),
      },
    },
    "",
    window.location.pathname + window.location.search,
  );
}

function withRecommendationHistory(pathname, historyId) {
  if (!historyId) return pathname;
  const [path, query = ""] = pathname.split("?");
  const params = new URLSearchParams(query);
  params.set("historyId", historyId);
  return `${path}?${params.toString()}`;
}

function clearActiveRecommendationHistoryState() {
  if (typeof window === "undefined" || !window.history.state?.shahabRecommendation) return;
  const { shahabRecommendation: _discarded, ...nextState } = window.history.state;
  window.history.replaceState(nextState, "", window.location.pathname + window.location.search);
}

function getInitialViewFromPath(pathname) {
  if (pathname === "/contact") return "contact";
  if (pathname.startsWith("/recommendation-history/")) return "history-result";
  if (pathname === "/loan-details" && new URLSearchParams(window.location.search).get("from") === "history") return "history-detail";
  if (["/profile", "/saved-loans", "/about", "/recommendation-history"].includes(pathname)) return pathname.slice(1).replace("-loans", "").replace("recommendation-history", "history");
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

function getHistoryIdFromLocation() {
  const queryHistoryId = new URLSearchParams(window.location.search).get("historyId");
  const match = window.location.pathname.match(/^\/recommendation-history\/([^/]+)$/);
  return match ? decodeURIComponent(match[1]) : queryHistoryId || "";
}

function replaceRoute(pathname) {
  if (typeof window === "undefined") return;
  if (window.location.pathname === pathname) return;
  // Carry only the current browser-history entry forward; this preserves the
  // active, opaque recommendation navigation through a detail-page refresh.
  window.history.pushState(window.history.state, "", pathname);
}

const personalInfoCacheKeys = { firstName: "firstName", lastName: "lastName", phone: "phone", income: "income", job: "job" };
function getCachedPersonalInfoValue(field) { return readPersonalInfoCache(field); }
function setCachedPersonalInfoValue(field, value) { writePersonalInfoCache(field, value); }
function getCachedAccountProfile() { return readAccountProfileCache(); }
function setCachedAccountProfile(profile) { writeAccountProfileCache(profile); }

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
  const normalized = Array.from(value)
    .filter((character) => phoneDigitPattern.test(character))
    .map((character) => {
      if (character >= "0" && character <= "9") return persianDigits[Number(character)];
      const arabicDigitIndex = "٠١٢٣٤٥٦٧٨٩".indexOf(character);
      return arabicDigitIndex >= 0 ? persianDigits[arabicDigitIndex] : character;
    })
    .join("");
  const suffix = normalized.length === 11 && normalized.startsWith("۰۹") ? normalized.slice(2) : normalized;
  return Array.from(suffix).reduce((result, digit) => {
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

function Nav({ onBack, onMenu, onHome, isLoginView = false }) {
  return (
    <header className="hp-nav"><div className="hp-nav-inner"><div className="hp-nav-right">
      <button className="hp-menu-button" type="button" aria-label="menu" onClick={onMenu}><span></span><span></span><span></span></button>
      <BrandMark onClick={onHome} />
    </div><div className="hp-nav-left">
      {isLoginView ? <button className="hp-back-button" type="button" onClick={onBack} aria-label="بازگشت"><svg viewBox="0 0 24 24" focusable="false"><path d="M20.4 12H5" /><path d="m12 19-7-7 7-7" /></svg></button> : null}
    </div></div></header>
  );
}

function SidebarIcon({ name }) {
  if (name === "contact") return <img className="hp-sidebar-icon" src={contactIconUrl} alt="" aria-hidden="true" />;
  if (name === "history") return <img className="hp-sidebar-icon" src={historyIconUrl} alt="" aria-hidden="true" />;
  if (name === "login") return <svg className="hp-sidebar-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M13 3h5a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-5" /><path d="m10 17 5-5-5-5M15 12H3" /></svg>;
  if (name === "saved") return <svg className="hp-sidebar-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 3h12a2 2 0 0 1 2 2v16l-8-4-8 4V5a2 2 0 0 1 2-2Z" /><path d="M12 7v6M9 10h6" /></svg>;
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

function UserSidebar({ isOpen, onClose, onLogin, onLogout, onNavigate, userName, isAuthenticated = false }) {
  const [activeItem, setActiveItem] = useState("");
  const [isLogoutConfirmationOpen, setIsLogoutConfirmationOpen] = useState(false);
  const items = isAuthenticated
    ? [["profile", "پروفایل کاربر"], ["requests", "سوابق درخواست وام"], ["history", "سوابق وام‌های توصیه شده"], ["saved", "وام‌های نشان شده"], ["contact", "تماس با ما"], ["about", "درباره ما"]]
    : [["login", "ورود کاربر"], ["contact", "تماس با ما"], ["about", "درباره ما"]];
  function selectItem(icon) { setActiveItem(icon); onClose(); if (icon === "login") onLogin(); else onNavigate?.(icon); }
  function confirmLogout() {
    setIsLogoutConfirmationOpen(false);
    onClose();
    onLogout();
  }
  return (
    <div className={"hp-sidebar-layer " + (isOpen ? "is-open" : "")} aria-hidden={!isOpen}>
      <button className="hp-sidebar-backdrop" type="button" aria-label="بستن منو" onClick={onClose}></button>
      <aside className="hp-user-sidebar" aria-label="منوی کاربر">
        {isAuthenticated ? <strong className="hp-sidebar-name">{userName}</strong> : null}
        <nav className="hp-sidebar-menu">
          {items.map(([icon, label]) => <button className={activeItem === icon ? "is-active" : ""} type="button" key={label} onClick={() => selectItem(icon)}><SidebarIcon name={icon} /><span>{label}</span></button>)}
          {isAuthenticated ? <button className="hp-sidebar-logout" type="button" onClick={() => setIsLogoutConfirmationOpen(true)}><SidebarIcon name="logout" /><span>خروج از حساب کاربری</span></button> : null}
        </nav>
      </aside>
      {isLogoutConfirmationOpen ? <div className="hp-logout-confirm-backdrop" role="presentation"><section className="hp-logout-confirm-dialog" role="alertdialog" aria-modal="true" aria-labelledby="logout-confirm-title"><img src={dangerIconUrl} alt="" /><strong id="logout-confirm-title">آیا از خروج از حساب کاربری‌تان مطمئن هستید؟</strong><div><button type="button" onClick={() => setIsLogoutConfirmationOpen(false)}>خیر</button><button type="button" onClick={confirmLogout}>بله</button></div></section></div> : null}
    </div>
  );
}

function formatOtpCountdown(seconds) {
  const minutes = Math.floor(seconds / 60);
  const rest = seconds % 60;
  return toPersianDigits(`${String(minutes).padStart(2, "0")}:${String(rest).padStart(2, "0")}`);
}

function LoginScreen({ loginStep, setLoginStep, onAuthenticated }) {
  const [phone, setPhone] = useState("");
  const [otp, setOtp] = useState(Array(6).fill(""));
  const [remainingSeconds, setRemainingSeconds] = useState(120);
  const [challengeId, setChallengeId] = useState("");
  const [loginError, setLoginError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (loginStep !== "otp" || remainingSeconds <= 0) return undefined;

    const timer = window.setTimeout(() => {
      setRemainingSeconds((current) => Math.max(current - 1, 0));
    }, 1000);

    return () => window.clearTimeout(timer);
  }, [loginStep, remainingSeconds]);

  function handlePhoneChange(event) {
    setPhone(sanitizePhoneDigits(event.target.value));
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
    if (!phoneDigitPattern.test(event.key)) event.preventDefault();
  }

  async function handlePhoneSubmit(event) {
    event.preventDefault();
    if (phone.length !== 9 || isSubmitting) return;
    setIsSubmitting(true); setLoginError("");
    try { const challenge = await requestProfileCode(phone); setChallengeId(challenge.challengeId); }
    catch (error) { setLoginError(error.message); return; }
    finally { setIsSubmitting(false); }
    setLoginStep("otp");
    setOtp(Array(6).fill(""));
    setRemainingSeconds(120);
  }

  function handleOtpChange(index, event) {
    const digit = sanitizeOtpDigits(event.target.value).slice(-1).join("");
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
    if (!phoneDigitPattern.test(event.key)) event.preventDefault();
  }

  function handleOtpPaste(event) {
    event.preventDefault();
    const pastedDigits = sanitizeOtpDigits(event.clipboardData.getData("text")).slice(0, 6).join("");
    if (!pastedDigits) return;

    const nextOtp = Array(6).fill("");
    pastedDigits.split("").forEach((digit, index) => {
      nextOtp[index] = digit;
    });
    setOtp(nextOtp);
  }

  async function handleResendCode() {
    if (remainingSeconds > 0 || isSubmitting) return;
    setIsSubmitting(true); setLoginError("");
    try { const challenge = await requestProfileCode(phone); setChallengeId(challenge.challengeId); }
    catch (error) { setLoginError(error.message); return; }
    finally { setIsSubmitting(false); }

    setOtp(Array(6).fill(""));
    setRemainingSeconds(120);
  }

  function handleChangePhone() {
    setLoginStep("phone");
    setOtp(Array(6).fill(""));
    setRemainingSeconds(120);
  }

  async function handleOtpSubmit(event) {
    event.preventDefault();
    if (otp.join("").length !== 6 || isSubmitting) return;
    setIsSubmitting(true); setLoginError("");
    try {
      if (!hasProfileAccess(phone)) await verifyProfileCode(challengeId, otp.join(""));
      const stored = await readOwnProfile();
      onAuthenticated(stored || { firstName: "", lastName: "", phone });
    } catch (error) { setLoginError(error.message); }
    finally { setIsSubmitting(false); }
  }

  if (loginStep === "otp") {
    return (
      <main className="hp-login-page hp-otp-page">
        <form className="hp-otp-form" onSubmit={handleOtpSubmit}>
          {loginError ? <p role="alert">{loginError}</p> : null}
          <label>کد یکبار مصرف</label>
          <div className="hp-otp-row" dir="ltr">
            {otp.map((digit, index) => (
              <input
                key={index}
                type="tel"
                inputMode="numeric"
                pattern="[0-9۰-۹٠-٩]*"
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
          <button className="hp-login-verify" type="submit" disabled={otp.join("").length !== 6 || isSubmitting}>ورود به حساب</button>
        </form>
      </main>
    );
  }

  return (
    <main className="hp-login-page">
      <form className="hp-login-form" onSubmit={handlePhoneSubmit}>
        {loginError ? <p role="alert">{loginError}</p> : null}
        <label htmlFor="login-phone">شماره تلفن همراه</label>
        <div className="hp-phone-row">
          <span>۰۹</span>
          <input
            id="login-phone"
            type="tel"
            inputMode="numeric"
            pattern="[0-9۰-۹٠-٩]*"
            maxLength={9}
            value={phone}
            onChange={handlePhoneChange}
            onKeyDown={handlePhoneKeyDown}
            aria-label="شماره تلفن همراه"
          />
        </div>
        <button type="submit" disabled={phone.length !== 9 || isSubmitting}>ارسال کد یکبار مصرف</button>
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

function AccountHeader({ onBack, onHome, onMenu }) {
  return <header className="hp-account-header"><button className="hp-questionnaire-icon-button" type="button" onClick={onBack} aria-label="بازگشت"><svg viewBox="0 0 24 24" focusable="false"><path d="M20 12H5" /><path d="m12 19-7-7 7-7" /></svg></button><a className="hp-questionnaire-brand" href="/" onClick={onHome}><img src={logoUrl} alt="شهاب" /><span><strong>شهاب</strong><small>(شبکه همرسانی اعتبار برخط)</small></span></a>{onMenu ? <button className="hp-questionnaire-icon-button" type="button" onClick={onMenu} aria-label="menu"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18" /></svg></button> : null}</header>;
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

function LoanCompareScreen({ result, status = "ready", onBack, onMenu, onHome, onCompareSubmit, onDetails, mode = "request", initialSelectedPlanIds = [] }) {
  const [selectedPlans, setSelectedPlans] = useState(() => Object.fromEntries(initialSelectedPlanIds.map((planId) => [planId, true])));
  const selectedPlanIds = Object.entries(selectedPlans)
    .filter(([, isSelected]) => isSelected)
    .map(([planId]) => planId);
  const selectedCount = selectedPlanIds.length;
  const isCompareMode = mode === "compare";
  const visiblePlans = useMemo(() => allRecommendationItems(result).slice().sort((first, second) => {
    const firstScore = typeof first.compatibilityScore === "number" ? first.compatibilityScore : -1;
    const secondScore = typeof second.compatibilityScore === "number" ? second.compatibilityScore : -1;
    return secondScore - firstScore || first.loanId.localeCompare(second.loanId);
  }), [result]);

  if (!result) {
    const isRestoring = status === "idle" || status === "loading";
    return <main className="hp-questionnaire-page" dir="rtl" aria-busy={isRestoring}><QuestionnaireHeader onBack={onBack} onMenu={onMenu} onHome={onHome} />{isRestoring ? <DeferredPageSkeleton active variant="cards" /> : <p className="hp-recommendation-result-state">برای ادامه، ابتدا پرسشنامه را در همین تب کامل کنید و نتیجهٔ معتبر دریافت کنید.</p>}</main>;
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
            onDetails={onDetails}
            onToggle={() => setSelectedPlans((current) => ({
              ...current,
              [recommendation.loanId]: current[recommendation.loanId] ? false : selectedCount < 10,
            }))}
          />
        ))}
      </section>
      {isCompareMode && selectedCount > 0 ? (
        <div className="hp-simple-compare-bottom-bar">
          <button className="hp-simple-compare-submit" type="button" disabled={selectedCount < 2} onClick={() => onCompareSubmit?.(selectedPlanIds)}>مقایسه کن ({toPersianDigits(selectedCount)} وام)</button>
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

function LoanComparisonResultCard({ detail, metric, onDetails }) {
  return (
    <article className="hp-compare-result-card" role="link" tabIndex={0} onClick={() => onDetails?.(detail.loanId)} onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); onDetails?.(detail.loanId); } }}>
      <BankIdentity lenderName={detail.lenderName} />
      <strong title={toPersianDigits(detail.loanName)} aria-label={toPersianDigits(detail.loanName)}>{toPersianDigits(detail.loanName)}</strong>
      <p>
        <span>{metric.title}</span>
        <b>{metric.value(detail)}</b>
      </p>
    </article>
  );
}

function LoanComparisonResultScreen({ result, status = "ready", onBack, onMenu, onHome, onDetails, selectedPlanIds }) {
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

  useEffect(() => {
    const activeTab = tabsRef.current?.querySelector(`[data-tab-index="${activeMetricIndex}"]`);
    activeTab?.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "nearest" });
  }, [activeMetricIndex]);

  if (!result) {
    const isRestoring = status === "idle" || status === "loading";
    return <main className="hp-questionnaire-page" dir="rtl" aria-busy={isRestoring}><QuestionnaireHeader onBack={onBack} onMenu={onMenu} onHome={onHome} />{isRestoring ? <DeferredPageSkeleton active variant="cards" /> : <p className="hp-recommendation-result-state">نتیجهٔ معتبر این پرسشنامه در دسترس نیست.</p>}</main>;
  }

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
        <DeferredPageSkeleton active={detailState.status === "loading"} variant="cards" />
        {detailState.status === "empty" ? <p className="hp-recommendation-result-state">برای مقایسه دست‌کم دو وام را انتخاب کنید.</p> : null}
        {detailState.status === "error" ? <p className="hp-recommendation-result-state">دریافت جزئیات مقایسه در حال حاضر ممکن نیست.</p> : null}
        {detailState.status === "ready" ? detailState.details.map((detail) => <LoanComparisonResultCard key={detail.loanId} detail={detail} metric={activeMetric} onDetails={onDetails} />) : null}
      </section>

      <div className="hp-compare-result-bottom-bar">
        <button type="button" disabled>تحلیل با هوش مصنوعی</button>
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

function QuestionnaireScreen({ onBack, onMenu, onAccountCreated, onHome, onSavedLoans, onHistoricalBack }) {
  const initialRequestedPath = window.location.pathname;
  const initialRecommendationHistory = getActiveRecommendationHistoryState();
  const initialSessionId = initialRecommendationHistory?.sessionId || "";
  const isInitialQuestionnaireRoute = /^\/question\/\d+$/.test(initialRequestedPath);
  const initialRouteState = isInitialQuestionnaireRoute && !initialSessionId
    ? getGuardedQuestionnaireRouteState(initialRequestedPath, [])
    : getQuestionnaireRouteState(initialRequestedPath);
  const [currentQuestion, setCurrentQuestion] = useState(initialRouteState.questionIndex);
  const [answers, setAnswers] = useState({});
  const answersRef = useRef(answers);
  answersRef.current = answers;
  const initialRouteSessionIdRef = useRef(initialSessionId);
  const initialRouteRestoredRef = useRef(false);
  const [isRestoringQuestionnaireRoute, setIsRestoringQuestionnaireRoute] = useState(
    isInitialQuestionnaireRoute,
  );
  // Kept only in this React instance: canonical answers and the opaque session
  // identifier are deliberately absent from URLs and browser storage.
  const [questionnaireSessionId, setQuestionnaireSessionId] = useState(() => initialRecommendationHistory?.sessionId || "");
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
    income: getCachedPersonalInfoValue("income"),
    job: getCachedPersonalInfoValue("job"),
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
  const [selectedComparisonPlanIds, setSelectedComparisonPlanIds] = useState(() => initialRecommendationHistory?.selectedComparisonPlanIds || []);
  // One in-flight request is sufficient for one anonymous questionnaire session.
  // The guard prevents a rerender from issuing a duplicate recommendation request.
  const recommendationRequestRef = useRef(false);
  const [analysisLogoUrls, setAnalysisLogoUrls] = useState([]);
  const [recommendationResult, setRecommendationResult] = useState(() => initialRecommendationHistory?.result || null);
  const [recommendationStatus, setRecommendationStatus] = useState(() => initialRecommendationHistory?.result ? "ready" : "idle");
  const [selectedAnalysisLoanId, setSelectedAnalysisLoanId] = useState("");
  const [isAnalysisSpinnerRunning, setIsAnalysisSpinnerRunning] = useState(false);
  const [analysisCountdown, setAnalysisCountdown] = useState(5);
  const [loanOtp, setLoanOtp] = useState(Array(6).fill(""));
  const [loanOtpSeconds, setLoanOtpSeconds] = useState(120);
  const [loanOtpError, setLoanOtpError] = useState("");
  const [profileChallengeId, setProfileChallengeId] = useState("");
  const [isSavingProfile, setIsSavingProfile] = useState(false);
  const [isCheckingPersonalAccess, setIsCheckingPersonalAccess] = useState(true);
  const [personalAccountPhone, setPersonalAccountPhone] = useState("");
  const personalDraftFields = useRef(new Set());
  const profileSubmitRef = useRef(false);
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
          label: "به عنوان یک «شخص» نیازمند اعتبار هستم.",
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
  const usesContentHeightQuestionCard = ["Q3", "S8"].includes(canonicalQuestion?.questionId);
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
  const canProceed = !isRestoringQuestionnaireRoute && !isSavingProfile && (!isPersonalInfoQuestion || !isCheckingPersonalAccess) && (isOtpQuestion
    ? loanOtpValue.length === 6
    : isPersonalInfoQuestion
      ? Boolean(isPersonalInfoComplete)
      : Boolean(selectedOption) && !isSavingQuestionnaireAnswer);
  const nextQuestionButtonText = isOtpQuestion
    ? "تایید و جستجوی وام"
    : isPersonalInfoQuestion
      ? "تایید"
      : "پاسخ به سوال بعد";
  const previousQuestionButtonText = isPersonalStageQuestion
    ? "بازگشت به مرحله قبل"
    : "بازگشت به سوال قبل";
  const historyId = getHistoryIdFromLocation()
    || (!initialRecommendationHistory?.sessionId ? initialRecommendationHistory?.historyId : null)
    || null;
  const routeBasePath = isAnalyzingLoans
    ? "/analysis"
    : loanResultView === "results"
      ? "/loan-results"
      : loanResultView === "details"
      ? (isSavedLoanDetailsPath(window.location.search)
        ? savedLoanDetailsPath(selectedLoanId)
        : `/loan-details?loanId=${encodeURIComponent(selectedLoanId)}`)
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
  const routePath = withRecommendationHistory(routeBasePath, historyId);
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
    if (!isPersonalInfoQuestion || isAnalyzingLoans || loanResultView) return undefined;
    let active = true;
    setIsCheckingPersonalAccess(true);
    readPersonalInfoProfile().then((profile) => {
      if (!active) return;
      setPersonalAccountPhone(profile?.phone || "");
      if (!profile) return;
      const fields = { firstName: profile.firstName || "", lastName: profile.lastName || "",
        income: profile.income || "", job: profile.job || "", phone: displayProfilePhone(profile.phone).slice(2) };
      setPersonalInfo((current) => Object.fromEntries(Object.entries(fields).map(([key, value]) =>
        [key, personalDraftFields.current.has(key) ? current[key] : value])));
    }).catch((error) => {
      if (active) setQuestionnaireSessionError(error.message);
    }).finally(() => { if (active) setIsCheckingPersonalAccess(false); });
    return () => { active = false; };
  }, [isPersonalInfoQuestion, isAnalyzingLoans, loanResultView]);

  useEffect(() => {
    replaceActiveRecommendationHistoryState(questionnaireSessionId, recommendationResult, selectedComparisonPlanIds);
  }, [questionnaireSessionId, recommendationResult, routePath, selectedComparisonPlanIds]);

  useEffect(() => {
    if (!isInitialQuestionnaireRoute || initialSessionId) return undefined;
    let active = true;
    readCurrentQuestionnaireSession().then((session) => {
      if (!active) return;
      if (session?.sessionId) {
        initialRouteSessionIdRef.current = session.sessionId;
        const restored = { ...answersRef.current };
        for (const [questionId, answerId] of Object.entries(session.answers || {})) {
          const questionIndex = getPrototypeQuestionIndexForCanonicalQuestionId(questionId);
          if (questionIndex !== null && !restored[questionIndex]) restored[questionIndex] = answerId;
        }
        for (const [stepId, answerId] of Object.entries(session.flowAnswers || {})) {
          const questionIndex = getPrototypeQuestionIndexForQuestionnaireStepId(stepId);
          if (questionIndex !== null && !restored[questionIndex]) restored[questionIndex] = answerId;
        }
        answersRef.current = restored;
        setAnswers(restored);
        initialRouteRestoredRef.current = true;
        const routeState = getGuardedQuestionnaireRouteState(
          initialRequestedPath,
          Object.keys(session.answers || {}),
          Object.keys(session.flowAnswers || {}),
        );
        setCurrentQuestion(routeState.questionIndex);
        setIsOtpVerificationStep(routeState.isOtpVerificationStep);
        setIsAnalyzingLoans(routeState.isAnalyzingLoans);
        setLoanResultView(routeState.loanResultView);
        if (routeState.pathname !== window.location.pathname) {
          window.history.replaceState(window.history.state, "", routeState.pathname);
        }
        setQuestionnaireSessionId(session.sessionId);
        setIsRestoringQuestionnaireRoute(false);
        return;
      }
      initialRouteRestoredRef.current = true;
      const routeState = getGuardedQuestionnaireRouteState(initialRequestedPath, []);
      setCurrentQuestion(routeState.questionIndex);
      setIsOtpVerificationStep(routeState.isOtpVerificationStep);
      setIsAnalyzingLoans(routeState.isAnalyzingLoans);
      setLoanResultView(routeState.loanResultView);
      if (routeState.pathname !== window.location.pathname) {
        window.history.replaceState(window.history.state, "", routeState.pathname);
      }
      setIsRestoringQuestionnaireRoute(false);
    }).catch(() => {
      if (!active) return;
      initialRouteRestoredRef.current = true;
      const routeState = getGuardedQuestionnaireRouteState(initialRequestedPath, []);
      setCurrentQuestion(routeState.questionIndex);
      setIsOtpVerificationStep(routeState.isOtpVerificationStep);
      setIsAnalyzingLoans(routeState.isAnalyzingLoans);
      setLoanResultView(routeState.loanResultView);
      if (routeState.pathname !== window.location.pathname) {
        window.history.replaceState(window.history.state, "", routeState.pathname);
      }
      setIsRestoringQuestionnaireRoute(false);
      setQuestionnaireSessionError("بازیابی نشست پرسشنامه ممکن نشد. اتصال را بررسی و صفحه را دوباره بارگذاری کنید.");
    });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (!questionnaireSessionId) return undefined;
    let active = true;
    readQuestionnaireSession(questionnaireSessionId).then((session) => {
      if (!active) return;
      const savedAnswers = session.answers || {};
      const restored = { ...answersRef.current };
      for (const [questionId, answerId] of Object.entries(savedAnswers)) {
        const questionIndex = getPrototypeQuestionIndexForCanonicalQuestionId(questionId);
        if (questionIndex !== null && !restored[questionIndex]) restored[questionIndex] = answerId;
      }
      const savedFlowAnswers = session.flowAnswers || {};
      for (const [stepId, answerId] of Object.entries(savedFlowAnswers)) {
        const questionIndex = getPrototypeQuestionIndexForQuestionnaireStepId(stepId);
        if (questionIndex !== null && !restored[questionIndex]) restored[questionIndex] = answerId;
      }
      answersRef.current = restored;
      setAnswers(restored);

      if (questionnaireSessionId === initialRouteSessionIdRef.current
        && isInitialQuestionnaireRoute
        && !initialRouteRestoredRef.current) {
        initialRouteRestoredRef.current = true;
        const routeState = getGuardedQuestionnaireRouteState(
          initialRequestedPath,
          Object.keys(savedAnswers),
          Object.keys(savedFlowAnswers),
        );
        setCurrentQuestion(routeState.questionIndex);
        setIsOtpVerificationStep(routeState.isOtpVerificationStep);
        setIsAnalyzingLoans(routeState.isAnalyzingLoans);
        setLoanResultView(routeState.loanResultView);
        setIsRestoringQuestionnaireRoute(false);
      }
    }).catch((error) => {
      if (!active) return;
      setQuestionnaireSessionError(error.status === 410
        ? "مهلت پرسشنامه تمام شده است. پرسشنامه را دوباره تکمیل کنید."
        : "بازیابی پاسخ‌های ثبت‌شده از نشست پرسشنامه در حال حاضر ممکن نشد.");

      if (questionnaireSessionId === initialRouteSessionIdRef.current
        && isInitialQuestionnaireRoute
        && !initialRouteRestoredRef.current) {
        initialRouteRestoredRef.current = true;
        const routeState = getGuardedQuestionnaireRouteState(initialRequestedPath, []);
        setCurrentQuestion(routeState.questionIndex);
        setIsOtpVerificationStep(routeState.isOtpVerificationStep);
        setIsAnalyzingLoans(routeState.isAnalyzingLoans);
        setLoanResultView(routeState.loanResultView);
        if (routeState.pathname !== window.location.pathname) {
          window.history.replaceState(window.history.state, "", routeState.pathname);
        }
        setIsRestoringQuestionnaireRoute(false);
      }
    });
    return () => { active = false; };
  }, [questionnaireSessionId]);

  useEffect(() => {
    if (isInitialQuestionnaireRoute) return;
    const routeState = getGuardedQuestionnaireRouteState(
      window.location.pathname,
      getCanonicalQuestionIdsFromPrototypeAnswers(answersRef.current),
      getFlowStepIdsFromPrototypeAnswers(answersRef.current),
    );
    setCurrentQuestion(routeState.questionIndex);
    setIsOtpVerificationStep(routeState.isOtpVerificationStep);
    setIsAnalyzingLoans(routeState.isAnalyzingLoans);
    setLoanResultView(routeState.loanResultView);
    if (routeState.pathname !== window.location.pathname) {
      window.history.replaceState(window.history.state, "", routeState.pathname);
    }
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
      const routeState = getGuardedQuestionnaireRouteState(
        window.location.pathname,
        getCanonicalQuestionIdsFromPrototypeAnswers(answersRef.current),
        getFlowStepIdsFromPrototypeAnswers(answersRef.current),
      );
      setCurrentQuestion(routeState.questionIndex);
      setIsOtpVerificationStep(routeState.isOtpVerificationStep);
      setIsAnalyzingLoans(routeState.isAnalyzingLoans);
      setLoanResultView(routeState.loanResultView);
      if (routeState.pathname !== window.location.pathname) {
        window.history.replaceState(window.history.state, "", routeState.pathname);
      }
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
    // Start the real server request during the existing five-second spinner.
    // It still remains a server-owned recommendation and no artificial extra
    // wait is added after the countdown.
    const resultBackedViews = ["results", "details", "request", "compare", "compare-result", "ai-analysis"];
    if ((!isAnalyzingLoans && !resultBackedViews.includes(loanResultView)) || recommendationResult || recommendationStatus !== "idle") return;
    const activeHistory = getActiveRecommendationHistoryState();
    if (!questionnaireSessionId && !activeHistory?.historyId) {
      setRecommendationStatus("sessionMissing");
      return;
    }
    loadRecommendationResult();
  }, [isAnalyzingLoans, loanResultView, questionnaireSessionId, recommendationResult, recommendationStatus, historyId]);

  useEffect(() => {
    if (!isAnalyzingLoans) return undefined;
    let cancelled = false;
    loadAnalysisLogos().then((urls) => {
      if (!cancelled) setAnalysisLogoUrls(urls);
    });
    return () => { cancelled = true; };
  }, [isAnalyzingLoans]);

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

  async function persistQuestionnaireAnswer() {
    const flowStepId = getQuestionnaireStepIdForPrototypeQuestionIndex(currentQuestion);
    if (!canonicalQuestion && !["loan_type", "entity_type"].includes(flowStepId)) return true;

    setIsSavingQuestionnaireAnswer(true);
    setQuestionnaireSessionError("");
    try {
      let sessionId = questionnaireSessionId;
      if (!sessionId) {
        const session = await startQuestionnaireSession();
        sessionId = session.sessionId;
        setQuestionnaireSessionId(sessionId);
        // The next screen becomes refreshable as soon as its route is shown.
        // Persist the opaque capability on this history entry synchronously,
        // before awaiting the answer write and navigating to that screen.
        replaceActiveRecommendationHistoryState(
          sessionId,
          recommendationResult,
          selectedComparisonPlanIds,
        );
      }
      if (canonicalQuestion) {
        await saveQuestionnaireAnswer(sessionId, canonicalQuestion.questionId, selectedOption);
      } else {
        await saveQuestionnaireFlowAnswer(sessionId, flowStepId, selectedOption);
      }
      return true;
    } catch (error) {
      if (error instanceof QuestionnaireSessionApiError && error.status === 410) {
        setAnswers({});
        setQuestionnaireSessionError("مهلت پرسشنامه تمام شده است. پرسشنامه را دوباره تکمیل کنید.");
        return false;
      }
      setQuestionnaireSessionError(
        "ذخیره پاسخ انجام نشد. لطفاً اتصال را بررسی کنید و دوباره تلاش کنید.",
      );
      return false;
    } finally {
      setIsSavingQuestionnaireAnswer(false);
    }
  }

  async function loadRecommendationResult() {
    if (recommendationRequestRef.current) return;
    const activeHistory = getActiveRecommendationHistoryState();
    const activeHistoryId = activeHistory?.historyId || historyId;
    if (!questionnaireSessionId && !activeHistoryId) {
      setRecommendationStatus("sessionMissing");
      return;
    }
    recommendationRequestRef.current = true;
    setRecommendationStatus("loading");
    try {
      const result = activeHistoryId
        ? await fetchHistoricalRecommendation(activeHistoryId)
        : await fetchRecommendationResult(questionnaireSessionId);
      setRecommendationResult(result);
      setRecommendationStatus("ready");
    } catch {
      // Retry is deliberately user-triggered; an effect must not loop after a
      // transient failure and keep the page in a permanently busy state.
      setRecommendationStatus("error");
    } finally {
      recommendationRequestRef.current = false;
    }
  }

  async function savePersonalProfileAndAnalyze(profile) {
    const stored = await persistPersonalInfo(profile);
    const accountProfile = stored;
    Object.entries(accountProfile).forEach(([field, value]) => {
      if (field in personalInfoCacheKeys) setCachedPersonalInfoValue(field, value);
    });
    setCachedAccountProfile(accountProfile);
    onAccountCreated(accountProfile);
    setLoanResultView("");
    setIsAnalyzingLoans(true);
    setIsAnalysisSpinnerRunning(true);
    setAnalysisCountdown(5);
    setLoanOtpError("");
  }

  async function handleNextQuestion() {
    if (!canProceed) return;
    if (!(await persistQuestionnaireAnswer())) return;
    if (isPersonalInfoQuestion) {
      if (profileSubmitRef.current) return;
      profileSubmitRef.current = true;
      setIsSavingProfile(true);
      setQuestionnaireSessionError("");
      try {
        const profile = await readPersonalInfoProfile();
        setPersonalAccountPhone(profile?.phone || "");
        if (profile && normalizeProfilePhone(personalInfo.phone) === profile.phone) {
          // An expired account cookie cannot authorize questionnaire reads.
          // Reestablish account access first, then validate the original raw TTL.
          if (questionnaireSessionId) await readQuestionnaireSession(questionnaireSessionId);
          await savePersonalProfileAndAnalyze({ ...personalInfo, phone: profile.phone });
          return;
        }
        const challenge = await requestProfileCode(personalInfo.phone);
        setProfileChallengeId(challenge.challengeId);
        setIsOtpVerificationStep(true);
        setLoanOtp(Array(6).fill(""));
        setLoanOtpSeconds(120);
        setLoanOtpError("");
      } catch (error) {
        if (error instanceof QuestionnaireSessionApiError && error.status === 410) {
          setAnswers({});
          setQuestionnaireSessionError("مهلت پرسشنامه تمام شده است. پرسشنامه را دوباره تکمیل کنید.");
        } else {
          if (error.status === 401) setPersonalAccountPhone("");
          setQuestionnaireSessionError(error.message);
        }
      } finally { setIsSavingProfile(false); profileSubmitRef.current = false; }
      return;
    }
    if (isOtpQuestion) {
      setIsSavingProfile(true);
      setLoanOtpError("");
      try {
        // Verification and persistence must both succeed before the analysis route opens.
        // A storage retry reuses the verified capability, not a consumed OTP challenge.
        if (!hasProfileAccess(personalInfo.phone)) await verifyProfileCode(profileChallengeId, loanOtpValue);
        if (questionnaireSessionId) await readQuestionnaireSession(questionnaireSessionId);
        await savePersonalProfileAndAnalyze(personalInfo);
      } catch (error) { setLoanOtpError(error.message); }
      finally { setIsSavingProfile(false); }
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
    if (isRestoringQuestionnaireRoute || isSavingQuestionnaireAnswer) return;

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

    if (loanResultView === "compare") {
      // Leaving selection for results intentionally starts the next compare
      // visit with no choices; returning from compare-result is handled above.
      setSelectedComparisonPlanIds([]);
      setLoanResultView("results");
      return;
    }

    if (loanResultView === "details" && isSavedLoanDetailsPath(window.location.search)) {
      onSavedLoans();
      return;
    }

    if (loanResultView === "details" || loanResultView === "request") {
      setLoanResultView("results");
      return;
    }

    if (loanResultView === "results" && historyId) {
      onHistoricalBack?.(historyId);
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
    replaceActiveRecommendationHistoryState(questionnaireSessionId, recommendationResult, selectedPlanIds);
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
    clearActiveRecommendationHistoryState();
    setQuestionnaireSessionId("");
    setAnswers({});
    setQuestionnaireSessionError("");
    setRecommendationResult(null);
    setRecommendationStatus("idle");
    setSelectedComparisonPlanIds([]);
    setLoanResultView("");
    setIsOtpVerificationStep(false);
    setIsAnalyzingLoans(false);
    setCurrentQuestion(0);
  }

  function handlePersonalInfoChange(field, value) {
    personalDraftFields.current.add(field);
    setPersonalInfo((current) => ({
      ...current,
      [field]: value,
    }));
    if (field === "income" || field === "job") {
      setCachedPersonalInfoValue(field, value);
      setCachedPersonalInfo((current) => ({ ...current, [field]: value }));
    }
  }

  function handlePersianNameChange(field, value) {
    personalDraftFields.current.add(field);
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
    if (isCheckingPersonalAccess) return;
    const sanitizedValue = sanitizePhoneDigits(value);
    handlePersonalInfoChange("phone", sanitizedValue);
    // A pending phone switch must not replace the current account's display cache.
    // The verified profile updates that cache only after successful persistence.
    if (personalAccountPhone) return;
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

  async function handleLoanOtpResend() {
    setIsSavingProfile(true);
    try {
      const challenge = await requestProfileCode(personalInfo.phone);
      setProfileChallengeId(challenge.challengeId);
    } catch (error) { setLoanOtpError(error.message); return; }
    finally { setIsSavingProfile(false); }
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
        onAiAnalysis={handleLoanAiAnalysisOpen}
      />
    );
  }

  if (loanResultView === "request") {
    return (
      <LoanCompareScreen
        result={recommendationResult}
        status={recommendationStatus}
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
        status={recommendationStatus}
        onBack={handleLoanResultBack}
        onMenu={onMenu}
        onHome={onHome}
        onCompareSubmit={handleLoanCompareSubmit}
        onDetails={handleLoanDetailsOpen}
        mode="compare"
        initialSelectedPlanIds={selectedComparisonPlanIds}
      />
    );
  }

  if (loanResultView === "compare-result") {
    return (
      <LoanComparisonResultScreen
        result={recommendationResult}
        status={recommendationStatus}
        onBack={handleLoanResultBack}
        onMenu={onMenu}
        onHome={onHome}
        onAiAnalysis={handleLoanAiAnalysisOpen}
        onDetails={handleLoanDetailsOpen}
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
    <main className="hp-questionnaire-page" dir="rtl" aria-busy={isRestoringQuestionnaireRoute || isSavingQuestionnaireAnswer || isSavingProfile}>
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
        <DeferredPageSkeleton active={isRestoringQuestionnaireRoute || isSavingQuestionnaireAnswer || isSavingProfile} variant="questionnaire" />
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
                  readOnly={isCheckingPersonalAccess}
                  onFocus={() => setFocusedPersonalInfoField("phone")}
                  onBlur={() => window.setTimeout(() => setFocusedPersonalInfoField(""), 120)}
                  onBeforeInput={(event) => {
                    const input = event.currentTarget;
                    const start = input.selectionStart ?? personalInfo.phone.length;
                    const end = input.selectionEnd ?? start;
                    const remaining = `${personalInfo.phone.slice(0, start)}${personalInfo.phone.slice(end)}`;
                    const proposed = `${personalInfo.phone.slice(0, start)}${event.data || ""}${personalInfo.phone.slice(end)}`;
                    if (
                      event.data &&
                      (!Array.from(event.data).every((character) => phoneDigitPattern.test(character)) ||
                        sanitizePhoneDigits(proposed).length === remaining.length)
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
              {!personalAccountPhone && !isCheckingPersonalAccess && focusedPersonalInfoField === "phone" && cachedPersonalInfo.phone && cachedPersonalInfo.phone !== personalInfo.phone ? (
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
                  <option value="up-to-22">تا ۲۲ میلیون تومان</option>
                  <option value="22-to-50">۲۲ تا ۵۰ میلیون تومان</option>
                  <option value="50-to-80">۵۰ تا ۸۰ میلیون تومان</option>
                  <option value="80-to-120">۸۰ تا ۱۲۰ میلیون تومان</option>
                  <option value="120-to-160">۱۲۰ تا ۱۶۰ میلیون تومان</option>
                  <option value="over-160">بیش از ۱۶۰ میلیون تومان</option>
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
              className={`hp-question-card ${currentQuestion === 1 ? "is-compact" : ""} ${isStagedQuestion ? "is-staged" : ""} ${usesContentHeightQuestionCard ? "uses-content-height" : ""}`}
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
              disabled={isRestoringQuestionnaireRoute || isSavingQuestionnaireAnswer}
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
      <img src={card.src} alt={card.name} loading="lazy" decoding="async" />
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

function ProfileDropdown({ label, value, options, onChange }) {
  const [isOpen, setIsOpen] = useState(false);
  const selectedLabel = options.find((option) => option.value === value)?.label || "";
  return <label><span>{label}</span><span className="hp-personal-select"><span className={"hp-personal-dropdown " + (isOpen ? "is-open" : "")} onBlur={(event) => { if (!event.currentTarget.contains(event.relatedTarget)) setIsOpen(false); }}><button className="hp-personal-dropdown-trigger" type="button" aria-haspopup="listbox" aria-expanded={isOpen} onClick={() => setIsOpen((current) => !current)}><span>{selectedLabel}</span></button>{isOpen ? <span className="hp-personal-dropdown-menu" role="listbox">{options.map((option) => <button className={"hp-personal-dropdown-option " + (value === option.value ? "is-selected" : "")} type="button" role="option" aria-selected={value === option.value} key={option.value} onClick={() => { onChange(option.value); setIsOpen(false); }}>{option.label}</button>)}</span> : null}</span></span></label>;
}
const genderOptions = [{ value: "female", label: "زن" }, { value: "male", label: "مرد" }];
function displayPersianPhone(phone) { return displayProfilePhone(phone); }
function AccountPage({ profile, onSave, onBack }) {
  const [draft, setDraft] = useState(() => ({ ...profile, income: profile.income || "", job: profile.job || "", gender: profile.gender || "", avatar: profile.avatar || "" }));
  const [profileError, setProfileError] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [saveSucceeded, setSaveSucceeded] = useState(false);
  const edited = useRef(false);
  const update = (field, value) => { edited.current = true; setSaveSucceeded(false); setDraft((current) => ({ ...current, [field]: value })); };
  async function submitProfile(event) {
    event.preventDefault();
    if (isSaving) return;
    setIsSaving(true); setProfileError(""); setSaveSucceeded(false);
    try { const stored = await persistProfile(draft); onSave(stored); setSaveSucceeded(true); }
    catch (error) { setProfileError(error.message); }
    finally { setIsSaving(false); }
  }
  useEffect(() => {
    if (!profile.phone) return undefined;
    let isCurrent = true;
    readOwnProfile()
      .then((stored) => {
        if (isCurrent && stored && !edited.current) setDraft((current) => ({ ...current, ...stored, phone: profile.phone }));
      })
      .catch((error) => { if (isCurrent) setProfileError(error.message); });
    return () => { isCurrent = false; };
  }, [profile.phone]);
  function selectAvatar(event) { const file = event.target.files?.[0]; if (!file) return; if (file.size > 100 * 1024) { window.alert("حجم عکس پروفایل باید حداکثر ۱۰۰ کیلوبایت باشد."); event.target.value = ""; return; } const reader = new FileReader(); reader.onload = () => update("avatar", reader.result); reader.readAsDataURL(file); }
  return <main className="hp-account-page" dir="rtl"><AccountHeader onBack={onBack} onHome={onBack} /><label className="hp-avatar-upload">{draft.avatar ? <img src={draft.avatar} alt="عکس پروفایل" /> : <img src="/ui-icons/user-add.svg" alt="" />}<input type="file" accept="image/*" onChange={selectAvatar} /></label><form className="hp-account-profile-form" onSubmit={submitProfile}><label><span>شماره تلفن همراه</span><input value={displayPersianPhone(draft.phone)} disabled /></label><label><span>نام</span><input value={draft.firstName || ""} onChange={(event) => update("firstName", sanitizePersianName(event.target.value))} /></label><label><span>نام خانوادگی</span><input value={draft.lastName || ""} onChange={(event) => update("lastName", sanitizePersianName(event.target.value))} /></label><ProfileDropdown label="میزان درآمد ماهانه" value={draft.income} options={incomeOptions} onChange={(value) => update("income", value)} /><ProfileDropdown label="شغل" value={draft.job} options={jobOptions} onChange={(value) => update("job", value)} /><ProfileDropdown label="جنسیت" value={draft.gender} options={genderOptions} onChange={(value) => update("gender", value)} /><button type="submit" className="hp-account-save" disabled={isSaving}>ذخیره تغییرات</button>{profileError ? <p role="alert">{profileError}</p> : null}{saveSucceeded ? <p role="status">تغییرات ذخیره شد.</p> : null}</form></main>;
}

function SavedLoansPage({ onBack, onDetails }) {
  const [loans, setLoans] = useState(readSavedLoans);
  const [status, setStatus] = useState("loading");
  const load = () => {
    setStatus("loading");
    refreshSavedLoans().then((value) => { setLoans(value); setStatus("ready"); }).catch(() => setStatus("error"));
  };
  useEffect(() => {
    let active = true;
    const sync = () => { if (active) setLoans(readSavedLoans()); };
    const refresh = () => { if (active) load(); };
    refresh(); window.addEventListener("shahab:saved-loans", sync); window.addEventListener("focus", refresh);
    return () => { active = false; window.removeEventListener("shahab:saved-loans", sync); window.removeEventListener("focus", refresh); };
  }, []);
  return <LoanResultsScreen result={null} status={status} onRetry={load} header={<AccountHeader onBack={onBack} onHome={onBack} />} onDetails={onDetails} savedItems={loans} showActions={false} />;
}

function RecommendationHistoryPage({ onBack, onOpen, onUnauthorized, state, setState }) {
  const [pendingHideId, setPendingHideId] = useState(null);
  const [isHiding, setIsHiding] = useState(false);
  const load = (cursor = null, append = false) => {
    setState((current) => ({ ...current, status: "loading" }));
    fetchRecommendationHistory({ cursor }).then((value) => setState((current) => ({
      status: "ready",
      items: append ? [...new Map([...current.items, ...(value.items || [])].map((item) => [item.historyId, item])).values()] : (value.items || []),
      nextCursor: value.nextCursor ?? null,
    }))).catch((error) => {
      if (error?.status === 401) { onUnauthorized?.(); return; }
      setState((current) => ({ ...current, status: "error" }));
    });
  };
  useEffect(() => { load(); }, []);
  async function confirmHide() {
    if (!pendingHideId || isHiding) return;
    setIsHiding(true);
    try {
      await hideRecommendationHistory(pendingHideId);
      setState((current) => ({ ...current, items: current.items.filter((item) => item.historyId !== pendingHideId) }));
      setPendingHideId(null);
    } finally { setIsHiding(false); }
  }
  return <main className="hp-account-page hp-recommendation-history-page" dir="rtl"><AccountHeader onBack={onBack} onHome={onBack} />
    {state.status === "loading" ? <DeferredPageSkeleton active variant="cards" /> : null}
    {state.status === "error" ? <div className="hp-recommendation-result-state" role="alert"><p>دریافت سوابق در حال حاضر ممکن نیست.</p><button type="button" onClick={() => load()}>تلاش مجدد</button></div> : null}
    {state.status === "ready" && !state.items.length ? <div className="hp-saved-loans-empty-state" role="status"><img src="/saved-loans-empty.png" alt="" width="1230" height="1278" decoding="async" fetchPriority="high" /></div> : null}
    {state.status === "ready" ? <section className="hp-recommendation-history-list">{state.items.map((item) => <article className="hp-recommendation-history-card" key={item.historyId}><button type="button" className="hp-history-card-open" onClick={() => onOpen(item.historyId)}><span className="hp-history-card-top"><strong>مشاهده نتایج</strong></span><span className="hp-history-card-row"><b>تعداد وام توصیه شده</b><em>{toPersianDigits(item.rankedCount)}</em></span><span className="hp-history-card-row"><b>تاریخ</b><em>{new Date(item.createdAt).toLocaleDateString("fa-IR", { timeZone: "Asia/Tehran" })}</em></span><span className="hp-history-card-row"><b>ساعت</b><em>{new Date(item.createdAt).toLocaleTimeString("fa-IR", { timeZone: "Asia/Tehran", hour: "2-digit", minute: "2-digit" })}</em></span></button><button className="hp-history-hide" type="button" aria-label="حذف سابقه" onClick={() => setPendingHideId(item.historyId)}><img src={closeCircleIconUrl} alt="" /></button></article>)}{state.nextCursor !== null ? <button type="button" className="hp-history-load-more" onClick={() => load(state.nextCursor, true)}>نمایش بیشتر</button> : null}</section> : null}
    {pendingHideId ? <div className="hp-history-confirm-backdrop" role="presentation"><section className="hp-history-confirm" role="alertdialog" aria-modal="true" aria-labelledby="history-confirm-title"><img src={dangerIconUrl} alt="" /><strong id="history-confirm-title">آیا از حذف کارت مطمئن هستید؟</strong><div><button type="button" disabled={isHiding} onClick={() => setPendingHideId(null)}>خیر</button><button type="button" disabled={isHiding} onClick={confirmHide}>بله</button></div></section></div> : null}
  </main>;
}

export default function HomePage() {
  const [currentView, setCurrentView] = useState(() => getInitialViewFromPath(window.location.pathname));
  const [loginStep, setLoginStep] = useState(() => (window.location.pathname === "/login/otp" ? "otp" : "phone"));
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [accountProfile, setAccountProfile] = useState(() => getCachedAccountProfile());
  const [historyResult, setHistoryResult] = useState(null);
  const [pendingHistoryPath, setPendingHistoryPath] = useState("");
  const [historyListState, setHistoryListState] = useState({ status: "loading", items: [], nextCursor: null });
  const [historyOrigin, setHistoryOrigin] = useState(null);
  const knownAccountEpoch = useRef(accountAccessEpoch());
  useEffect(() => {
    const clear = () => {
      setAccountProfile(null); setHistoryResult(null); setPendingHistoryPath("");
      setHistoryListState({ status: "loading", items: [], nextCursor: null }); setHistoryOrigin(null);
      setIsSidebarOpen(false); setLoginStep("phone");
      window.history.replaceState(window.history.state, "", "/"); setCurrentView("home");
    };
    const changed = () => {
      const hadAccount = knownAccountEpoch.current > 0;
      knownAccountEpoch.current = accountAccessEpoch();
      setAccountProfile(null); setHistoryResult(null);
      setHistoryListState({ status: "loading", items: [], nextCursor: null });
      if (hadAccount && /^\/(profile|saved-loans|recommendation-history)(\/|$)/.test(window.location.pathname)) {
        window.history.replaceState(window.history.state, "", "/"); setCurrentView("home");
      }
      // Populate only a still-empty current generation; a later successful form
      // save must not be overwritten by this earlier bootstrap profile read.
      Promise.resolve().then(() => readOwnProfile()).then(profile => {
        if (profile) setAccountProfile(current => { if (current) return current; setCachedAccountProfile(profile); return profile; });
      }).catch(() => {});
    };
    window.addEventListener("shahab:account-changed", changed);
    window.addEventListener("shahab:account-cleared", clear);
    const stopTabs = synchronizeAccountTabs();
    return () => { window.removeEventListener("shahab:account-changed", changed); window.removeEventListener("shahab:account-cleared", clear); stopTabs(); };
  }, []);
  useEffect(() => { let active = true; restoreAccountAccess().then((phone) => { if (!phone || !active) return; readOwnProfile().then((profile) => { if (profile && active) { setAccountProfile(profile); setCachedAccountProfile(profile); } }).catch(() => {}); }); return () => { active = false; }; }, []);
  useEffect(() => {
    if (currentView !== "history-result" || historyResult) return;
    const historyId = getHistoryIdFromLocation();
    if (!historyId) return;
    fetchHistoricalRecommendation(historyId).then(setHistoryResult).catch((error) => {
      if (error?.status === 401) {
        setPendingHistoryPath(window.location.pathname + window.location.search);
        setLoginStep("phone");
        setCurrentView("login");
        replaceRoute("/login");
        return;
      }
      setHistoryResult(false);
    });
  }, [currentView, historyResult]);
  const sidebarUserName = accountProfile
    ? `${accountProfile.firstName || ""} ${accountProfile.lastName || ""}`.trim() || "کاربر"
    : "";
  const hasValidAccountAccess = Boolean(accountProfile?.phone && hasProfileAccess(accountProfile.phone));

  useEffect(() => {
    if (!isSidebarOpen || !accountProfile?.phone || !hasProfileAccess(accountProfile.phone)) return undefined;
    let active = true;
    readOwnProfile().then((stored) => {
      if (active && stored) { setAccountProfile(stored); setCachedAccountProfile(stored); }
    }).catch(() => {});
    return () => { active = false; };
  }, [isSidebarOpen, accountProfile?.phone]);

  useEffect(() => {
    if (!isSidebarOpen) return undefined;

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    return () => {
      document.body.style.overflow = previousOverflow;
    };
  }, [isSidebarOpen]);

  useEffect(() => {
    if (currentView === "questionnaire" || currentView === "history-result" || currentView === "history-detail") return;

    const accountRoute = { profile: "/profile", saved: "/saved-loans", history: "/recommendation-history", about: "/about", contact: "/contact" };
    replaceRoute(currentView === "login" ? (loginStep === "otp" ? "/login/otp" : "/login") : (accountRoute[currentView] || "/"));
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

  function handleLoginAuthenticated(profile) {
    setCachedAccountProfile(profile);
    setAccountProfile(profile);
    if (pendingHistoryPath) {
      const destination = pendingHistoryPath;
      setPendingHistoryPath("");
      setHistoryResult(null);
      replaceRoute(destination);
      setCurrentView(getInitialViewFromPath(new URL(destination, window.location.origin).pathname));
    } else {
      setCurrentView("home");
    }
    setLoginStep("phone");
  }

  function handleLogout() {
    // Failed revoke stays pending, preventing cookie restoration on refresh.
    void logoutProfile().catch(() => window.alert("خروج در سرور تأیید نشد. اتصال را بررسی کنید و دوباره تلاش کنید."));
  }

  function handleSidebarNavigate(destination) {
    const routes = { profile: "/profile", saved: "/saved-loans", history: "/recommendation-history", about: "/about", contact: "/contact" };
    const views = { profile: "profile", saved: "saved", history: "history", about: "about", contact: "contact" };
    if (!routes[destination]) return;
    if (destination === "history") setHistoryOrigin({ view: currentView, path: window.location.pathname + window.location.search });
    setIsSidebarOpen(false);
    replaceRoute(routes[destination]);
    setCurrentView(views[destination]);
  }

  function handleSavedLoanDetails(loanId) {
    replaceRoute(savedLoanDetailsPath(loanId));
    setCurrentView("questionnaire");
  }

  function handleSavedLoansOpen() {
    replaceRoute("/saved-loans");
    setCurrentView("saved");
  }

  function handleQuestionnaireOpen() {
    clearActiveRecommendationHistoryState();
    setQuestionnaireSessionId("");
    setAnswers({});
    setQuestionnaireSessionError("");
    setRecommendationResult(null);
    setRecommendationStatus("idle");
    setSelectedComparisonPlanIds([]);
    setLoanResultView("");
    setIsOtpVerificationStep(false);
    setIsAnalyzingLoans(false);
    setCurrentQuestion(0);
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

    if (currentView === "questionnaire") setCurrentView("home");
  }

  if (currentView === "profile") return <AccountPage profile={{ ...(accountProfile || {}), firstName: getCachedPersonalInfoValue("firstName") || accountProfile?.firstName || "", lastName: getCachedPersonalInfoValue("lastName") || accountProfile?.lastName || "", phone: getCachedPersonalInfoValue("phone") || accountProfile?.phone || "", income: getCachedPersonalInfoValue("income") || accountProfile?.income || "", job: getCachedPersonalInfoValue("job") || accountProfile?.job || "" }} onSave={(profile) => { ["firstName", "lastName", "phone", "income", "job"].forEach((field) => setCachedPersonalInfoValue(field, profile[field] || "")); setCachedAccountProfile(profile); setAccountProfile(profile); }} onBack={handleHomeOpen} />;
  if (currentView === "contact") return <><UserSidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} onLogin={handleLoginOpen} onLogout={handleLogout} onNavigate={handleSidebarNavigate} userName={sidebarUserName} isAuthenticated={hasValidAccountAccess} /><ContactPage header={<AccountHeader onBack={handleHomeOpen} onHome={handleHomeOpen} onMenu={() => setIsSidebarOpen(true)} />} /></>;
  if (currentView === "about") return <AboutPage onBack={handleHomeOpen} AccountHeader={AccountHeader} />;
  if (currentView === "saved") return <SavedLoansPage onBack={handleHomeOpen} onDetails={handleSavedLoanDetails} />;
  if (currentView === "history") return <><UserSidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} onLogin={handleLoginOpen} onLogout={handleLogout} onNavigate={handleSidebarNavigate} userName={sidebarUserName} isAuthenticated={hasValidAccountAccess} /><RecommendationHistoryPage state={historyListState} setState={setHistoryListState} onBack={() => { const origin = historyOrigin; replaceRoute(origin?.path || "/"); setCurrentView(origin?.view || "home"); setIsSidebarOpen(Boolean(origin)); }} onUnauthorized={() => { setPendingHistoryPath("/recommendation-history"); setLoginStep("phone"); setCurrentView("login"); replaceRoute("/login"); }} onOpen={(historyId) => { fetchHistoricalRecommendation(historyId).then((result) => { setHistoryResult(result); setCurrentView("history-result"); replaceRoute(`/recommendation-history/${encodeURIComponent(historyId)}`); }).catch(() => setHistoryResult(false)); }} /></>;
  if (currentView === "history-result") {
    if (historyResult === false) return <main className="hp-questionnaire-page" dir="rtl"><QuestionnaireHeader onBack={() => { replaceRoute("/recommendation-history"); setCurrentView("history"); }} onMenu={() => setIsSidebarOpen(true)} onHome={handleHomeOpen} /><p className="hp-recommendation-result-state">نتیجهٔ تاریخی در دسترس نیست.</p></main>;
    if (!historyResult) return <main className="hp-questionnaire-page" dir="rtl"><QuestionnaireHeader onBack={() => { replaceRoute("/recommendation-history"); setCurrentView("history"); }} onMenu={() => setIsSidebarOpen(true)} onHome={handleHomeOpen} /><DeferredPageSkeleton active variant="cards" /></main>;
    return <><UserSidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} onLogin={handleLoginOpen} onLogout={handleLogout} onNavigate={handleSidebarNavigate} userName={sidebarUserName} isAuthenticated={hasValidAccountAccess} /><LoanResultsScreen result={historyResult} status="ready" header={<QuestionnaireHeader onBack={() => { replaceRoute("/recommendation-history"); setHistoryResult(null); setCurrentView("history"); }} onMenu={() => setIsSidebarOpen(true)} onHome={handleHomeOpen} />} onDetails={(loanId) => { const historyId = getHistoryIdFromLocation(); replaceRoute(`/loan-details?loanId=${encodeURIComponent(loanId)}&from=history&historyId=${encodeURIComponent(historyId)}`); setCurrentView("history-detail"); }} onCompare={(result) => { const historyId = result.historyId || getHistoryIdFromLocation(); if (!historyId) return; window.history.replaceState({ ...(window.history.state || {}), shahabRecommendation: { historyId, selectedComparisonPlanIds: [] } }, "", window.location.pathname + window.location.search); replaceRoute(withRecommendationHistory("/compare-loans", historyId)); setCurrentView("questionnaire"); }} /></>;
  }
  if (currentView === "history-detail") {
    const historyId = new URLSearchParams(window.location.search).get("historyId") || "";
    return <LoanDetailsScreen loanId={getLoanIdFromLocation()} header={<AccountHeader onBack={() => { replaceRoute(`/recommendation-history/${encodeURIComponent(historyId)}`); setHistoryResult(null); setCurrentView("history-result"); }} onHome={handleHomeOpen} />} />;
  }

  if (currentView === "questionnaire") {
    return (
      <div className="hp-page hp-questionnaire-shell" dir="rtl">
        <UserSidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} onLogin={handleLoginOpen} onLogout={handleLogout} onNavigate={handleSidebarNavigate} userName={sidebarUserName} isAuthenticated={hasValidAccountAccess} />
        <QuestionnaireScreen
          onBack={handleBack}
          onMenu={() => setIsSidebarOpen(true)}
          onAccountCreated={handleAccountCreated}
          onHome={handleHomeOpen}
          onSavedLoans={handleSavedLoansOpen}
          onHistoricalBack={(historyId) => { replaceRoute(`/recommendation-history/${encodeURIComponent(historyId)}`); setCurrentView("history-result"); }}
        />
      </div>
    );
  }

  return (
    <div className="hp-page" dir="rtl">
      <Nav
        isLoginView={currentView === "login"}
        onBack={handleBack}
        onMenu={() => setIsSidebarOpen(true)}
        onHome={handleHomeOpen}
      />
      <UserSidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} onLogin={handleLoginOpen} onLogout={handleLogout} onNavigate={handleSidebarNavigate} userName={sidebarUserName} isAuthenticated={hasValidAccountAccess} />
      {currentView === "login" ? (
        <LoginScreen loginStep={loginStep} setLoginStep={setLoginStep} onAuthenticated={handleLoginAuthenticated} />
      ) : (
        <main>
          <Hero onStartQuestionnaire={handleQuestionnaireOpen} />
        </main>
      )}
    </div>
  );
}
