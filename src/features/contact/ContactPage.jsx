import phoneImage from "./assets/phone.webp";
import megaphoneImage from "./assets/megaphone.webp";
import linkedinImage from "./assets/linkedin.png";
import telegramImage from "./assets/telegram.png";
import instagramImage from "./assets/instagram.png";
import xImage from "./assets/x.png";
import enamadImage from "./assets/enamad.webp";
import "./ContactPage.css";

const linkedinUrl = "https://www.linkedin.com/company/shahabfintech";
const enamadUrl = "https://trustseal.enamad.ir/?id=8316058&Code=YCgntg1cyA41RMpSVRpI0XieeveRCHnk";
const socialNetworks = [
  { label: "لینکدین", image: linkedinImage, iconClass: "linkedin", href: linkedinUrl },
  { label: "تلگرام", image: telegramImage, iconClass: "telegram" },
  { label: "اینستاگرام", image: instagramImage, iconClass: "instagram" },
  { label: "ایکس", image: xImage, iconClass: "x" },
];

function ContactDetails() {
  return (
    <section className="sh-contact-card sh-contact-details" aria-label="اطلاعات تماس">
      <img className="sh-contact-illustration" src={phoneImage} width="1536" height="1024" alt="" />
      <dl>
        <div><dt>تلفن <span>(کلیک کنید)</span></dt><dd><a href="tel:09371410602" dir="ltr">۰۹۳۷۱۴۱۰۶۰۲</a></dd></div>
        <div><dt>روزهای پاسخگویی</dt><dd>از شنبه تا چهارشنبه</dd></div>
        <div><dt>ساعات پاسخگویی</dt><dd>۹ تا ۲۰</dd></div>
      </dl>
    </section>
  );
}

function SocialNetworks() {
  return (
    <section className="sh-contact-card sh-contact-social" aria-label="شبکه‌های اجتماعی">
      <img className="sh-contact-illustration" src={megaphoneImage} width="1536" height="1024" alt="" />
      <ul>
        {socialNetworks.map(({ label, image, iconClass, href }) => (
          <li key={label}>
            {href ? (
              <a className="sh-contact-network" href={href} target="_blank" rel="noopener noreferrer">
                <span>{label}</span><img className={`sh-contact-network-icon sh-contact-network-icon--${iconClass}`} src={image} alt="" width="40" height="40" />
              </a>
            ) : (
              <button className="sh-contact-network" type="button" disabled aria-label={`${label}؛ صفحه هنوز ایجاد نشده است`}>
                <span>{label}</span><img className={`sh-contact-network-icon sh-contact-network-icon--${iconClass}`} src={image} alt="" width="40" height="40" />
              </button>
            )}
          </li>
        ))}
      </ul>
    </section>
  );
}

/** Static public contact information; shares the existing account header/navigation. */
export default function ContactPage({ header }) {
  return (
    <main className="sh-contact-page" dir="rtl" aria-label="تماس با ما">
      <div className="sh-contact-content">
        {header}
        <ContactDetails />
        <SocialNetworks />
        <a className="sh-contact-enamad" href={enamadUrl} target="_blank" rel="noopener" referrerPolicy="origin" aria-label="استعلام نماد اعتماد الکترونیکی شهاب">
          <img src={enamadImage} width="1254" height="1254" alt="نماد اعتماد الکترونیکی" />
        </a>
      </div>
    </main>
  );
}
