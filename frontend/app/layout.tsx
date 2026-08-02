import type { Metadata } from "next";

import Providers from "./providers";
import "./globals.css";

export const metadata: Metadata = {
  title: "موتوشاب",
  description: "پلتفرم ارتباطات و فرآیندهای سازمانی",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fa" dir="rtl">
      <head>
        {/* Apply the persisted theme before paint to avoid a flash. */}
        <script
          dangerouslySetInnerHTML={{
            __html: `try{var d=localStorage.getItem('ms-dark');if(d==='1'||(d===null&&matchMedia('(prefers-color-scheme:dark)').matches))document.documentElement.classList.add('dark');var f=localStorage.getItem('ms-font');if(f)document.documentElement.setAttribute('data-font',f);var ac=localStorage.getItem('ms-accent');if(ac)document.documentElement.setAttribute('data-accent',ac);}catch(e){}`,
          }}
        />
      </head>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
