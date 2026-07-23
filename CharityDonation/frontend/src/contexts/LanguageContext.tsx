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
    "signup.failed": "Signup failed"
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
    "signup.failed": "အကောင့်ဖွင့်ခြင်း မအောင်မြင်ပါ"
  }
};

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<Language>('en');

  const t = (key: string) => {
    return translations[language][key] || key;
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
