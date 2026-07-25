import { createContext, useContext, useState, ReactNode } from 'react';

type Language = 'en' | 'mm';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

const translations: Record<Language, Record<string, string>> = {
  en: {
    "app.title": "Warm Hug",
    "nav.donate": "Donate",
    "nav.request": "Request",
    "nav.my_donations": "My Donations",
    "nav.my_requests": "My Requests",
    "nav.browse_donations": "Browse Donations",
    "nav.browse_requests": "Browse Requests",
    "nav.matches": "Matches",
    "nav.volunteer_dashboard": "Volunteer Dashboard",
    "nav.become_volunteer": "Become a Volunteer",
    "nav.admin": "Admin",
    "nav.logout": "Log out",
    "nav.login": "Log in",
    "nav.signup": "Sign up",

    "login.title": "Log in",
    "login.email": "Email",
    "login.password": "Password",
    "login.button": "Log in",
    "login.button.submitting": "Logging in...",
    "login.no_account": "No account?",
    "login.failed": "Login failed",

    "signup.title": "Sign up",
    "signup.full_name": "Full name",
    "signup.email": "Email",
    "signup.password": "Password",
    "signup.phone": "Phone (optional)",
    "signup.button": "Sign up",
    "signup.button.submitting": "Signing up...",
    "signup.has_account": "Already have an account?",
    "signup.failed": "Signup failed",

    "home.hero.title": "Bringing warmth to every community",
    "home.hero.subtitle": "Join our network of donors and volunteers to provide essential goods, food, and care to those in need. Your contribution brings a warm hug to the world.",
    "home.hero.donate_btn": "Donate Now",
    "home.hero.request_btn": "Request Help",
    "home.hero.join_btn": "Join the Community",
    "home.how_it_works": "How it works",
    "home.give.title": "Give with a Warm Hug",
    "home.give.desc": "List items or food you'd like to donate. Our volunteers will pick it up and deliver it securely to the community.",
    "home.req.title": "Request Essentials",
    "home.req.desc": "Communities in need can easily request specific items. We match your request with generous donors nearby.",
    "home.vol.title": "Volunteer Dispatch",
    "home.vol.desc": "Join our dispatch team. Use your vehicle or time to securely transport goods from donors to those who need them most.",
    "home.ready.title": "Ready to make a difference?",
    "home.ready.desc": "Whether you're giving, receiving, or delivering, every action brings a warm hug to those who need it most.",
    "home.ready.btn": "Explore Active Donations"
  },
  mm: {
    "app.title": "အလှူငွေ လှူဒါန်းရန်",
    "nav.donate": "လှူမည်",
    "nav.request": "တောင်းဆိုမည်",
    "nav.my_donations": "ကျွန်ုပ်၏အလှူများ",
    "nav.my_requests": "ကျွန်ုပ်၏တောင်းဆိုမှုများ",
    "nav.browse_donations": "အလှူများကိုရှာဖွေရန်",
    "nav.browse_requests": "တောင်းဆိုမှုများကိုရှာဖွေရန်",
    "nav.matches": "ကိုက်ညီမှုများ",
    "nav.volunteer_dashboard": "စေတနာ့ဝန်ထမ်း ဒက်ရှ်ဘုတ်",
    "nav.become_volunteer": "စေတနာ့ဝန်ထမ်း ဖြစ်လာရန်",
    "nav.admin": "အက်ဒမင်",
    "nav.logout": "ထွက်မည်",
    "nav.login": "အကောင့်ဝင်ရန်",
    "nav.signup": "အကောင့်ဖွင့်ရန်",

    "login.title": "အကောင့်ဝင်ရန်",
    "login.email": "အီးမေးလ်",
    "login.password": "စကားဝှက်",
    "login.button": "အကောင့်ဝင်မည်",
    "login.button.submitting": "ဝင်နေသည်...",
    "login.no_account": "အကောင့်မရှိဘူးလား?",
    "login.failed": "အကောင့်ဝင်ခြင်း မအောင်မြင်ပါ",

    "signup.title": "အကောင့်ဖွင့်ရန်",
    "signup.full_name": "အမည်အပြည့်အစုံ",
    "signup.email": "အီးမေးလ်",
    "signup.password": "စကားဝှက်",
    "signup.phone": "ဖုန်း (မလုပ်မနေရမဟုတ်ပါ)",
    "signup.button": "အကောင့်ဖွင့်မည်",
    "signup.button.submitting": "အကောင့်ဖွင့်နေသည်...",
    "signup.has_account": "အကောင့်ရှိပြီးသားလား?",
    "signup.failed": "အကောင့်ဖွင့်ခြင်း မအောင်မြင်ပါ",

    "home.hero.title": "လူမှုအသိုင်းအဝိုင်းတိုင်းဆီသို့ နွေးထွေးမှုများ ယူဆောင်လာပေးခြင်း",
    "home.hero.subtitle": "အကူအညီလိုအပ်နေသူများအတွက် မရှိမဖြစ်လိုအပ်သော ပစ္စည်းများ၊ အစားအစာနှင့် စောင့်ရှောက်မှုများ ပေးအပ်ရန် ကျွန်ုပ်တို့၏ အလှူရှင်များနှင့် စေတနာ့ဝန်ထမ်းများ ကွန်ရက်တွင် ပါဝင်လိုက်ပါ။ သင့်၏လှူဒါန်းမှုက ကမ္ဘာကြီးအတွက် နွေးထွေးသော ပွေ့ဖက်မှုတစ်ခုကို ယူဆောင်လာပေးပါသည်။",
    "home.hero.donate_btn": "ယခုလှူဒါန်းမည်",
    "home.hero.request_btn": "အကူအညီတောင်းခံမည်",
    "home.hero.join_btn": "အသိုင်းအဝိုင်းသို့ ဝင်ရောက်မည်",
    "home.how_it_works": "မည်သို့အလုပ်လုပ်သနည်း",
    "home.give.title": "နွေးထွေးစွာ လှူဒါန်းပါ",
    "home.give.desc": "သင်လှူဒါန်းလိုသော ပစ္စည်းများ သို့မဟုတ် အစားအစာများကို စာရင်းသွင်းပါ။ ကျွန်ုပ်တို့၏ စေတနာ့ဝန်ထမ်းများက လာရောက်ယူဆောင်ပြီး လိုအပ်သူများထံ လုံခြုံစွာ ပို့ဆောင်ပေးမည်ဖြစ်ပါသည်။",
    "home.req.title": "လိုအပ်သောပစ္စည်းများ တောင်းဆိုရန်",
    "home.req.desc": "အကူအညီလိုအပ်နေသော အသိုင်းအဝိုင်းများသည် လိုအပ်သော ပစ္စည်းများကို အလွယ်တကူ တောင်းဆိုနိုင်ပါသည်။ သင့်တောင်းဆိုမှုကို အနီးအနားရှိ အလှူရှင်များနှင့် ကျွန်ုပ်တို့ ချိတ်ဆက်ပေးပါမည်။",
    "home.vol.title": "စေတနာ့ဝန်ထမ်း ပို့ဆောင်ရေး",
    "home.vol.desc": "ကျွန်ုပ်တို့၏ ပို့ဆောင်ရေးအဖွဲ့တွင် ပါဝင်ပါ။ သင့်ယာဉ် သို့မဟုတ် အချိန်ကို အသုံးပြု၍ အလှူရှင်များထံမှ လိုအပ်သူများထံသို့ ပစ္စည်းများကို လုံခြုံစွာ ပို့ဆောင်ပေးပါ။",
    "home.ready.title": "အပြောင်းအလဲတစ်ခုပြုလုပ်ရန် အဆင်သင့်ဖြစ်ပြီလား?",
    "home.ready.desc": "သင်သည် ပေးကမ်းသူ၊ လက်ခံသူ၊ သို့မဟုတ် ပို့ဆောင်ပေးသူ မည်သူပင်ဖြစ်စေ သင့်လုပ်ရပ်တိုင်းသည် လိုအပ်နေသူများအတွက် နွေးထွေးသော ပွေ့ဖက်မှုတစ်ခု ဖြစ်စေပါသည်။",
    "home.ready.btn": "လှူဒါန်းမှုများကို ရှာဖွေရန်"
  }
};

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const getInitialLang = (): Language => {
    if (typeof document !== 'undefined') {
      const match = document.cookie.match(/googtrans=\/en\/(en|my)/);
      if (match && match[1] === 'my') {
        return 'mm';
      }
    }
    return 'en';
  };

  const [language, setLangState] = useState<Language>(getInitialLang());

  const setLanguage = (lang: Language) => {
    setLangState(lang);
    
    // Setup Google Translate API cookies
    const googleLang = lang === 'mm' ? 'my' : 'en';
    document.cookie = `googtrans=/en/${googleLang}; path=/`;
    document.cookie = `googtrans=/en/${googleLang}; domain=${window.location.hostname}; path=/`;
    
    // Reload page to trigger the API translation
    window.location.reload();
  };

  const t = (key: string) => {
    // When using Google Translate, we return English text so the API can translate it,
    // but we can still return manual translations if they exist.
    // To ensure Google API handles everything including dynamic text smoothly,
    // returning the English string here allows Google to translate the whole DOM equally.
    return translations['en'][key] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}
