import type { Metadata } from 'next';
import localFont from 'next/font/local';
import './globals.css';
import { NextIntlClientProvider, useTranslations } from 'next-intl';
import { getLocale, getMessages } from 'next-intl/server';
import { ThemeProvider as NextThemesProvider } from 'next-themes';
import { TailwindIndicator } from '@/components/tailwind-indicator';
import { Background } from '@/components/background';
import { Footer } from '@/components/footer';

const geistSans = localFont({
  src: '../../public/fonts/GeistVF.woff',
  variable: '--font-geist-sans',
  weight: '100 900',
});
const geistMono = localFont({
  src: '../../public/fonts/GeistMonoVF.woff',
  variable: '--font-geist-mono',
  weight: '100 900',
});

const TITLE = 'Gladis';
const DESCRIPTION = 'The universal EPD search engine';
// This should be enhanced when we want to share the website
export const metadata: Metadata = {
  title: { template: `%s | ${TITLE}`, default: TITLE },
  description: DESCRIPTION,
  openGraph: {
    title: TITLE,
    description: DESCRIPTION,
    type: 'website',
  },
  twitter: { title: TITLE, description: DESCRIPTION },
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const locale = await getLocale();

  // Load messages for the current locale, for now provides all translations, easier to get started
  const messages = await getMessages({ locale });

  return (
    <html lang={locale}>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <NextThemesProvider attribute="class" defaultTheme="light" enableSystem>
          <NextIntlClientProvider messages={messages}>
            <Background>
              <MainLayout>{children}</MainLayout>
            </Background>
          </NextIntlClientProvider>
          <TailwindIndicator />
        </NextThemesProvider>
      </body>
    </html>
  );
}

function MainLayout({ children }: { children: React.ReactNode }) {
  const t = useTranslations();
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-8 p-4 md:p-8">
      <header className="sticky top-3 flex w-full max-w-4xl flex-col items-center rounded-full border border-border font-geist font-bold backdrop-blur-lg">
        {t('heroic_dirty_shrike_thrive')}{' '}
        <div className="font-sans text-sm font-thin">
          {t('happy_stout_crow_fry')}
        </div>
      </header>
      <div className="w-full max-w-4xl flex-1">{children}</div>
      <Footer className="w-full max-w-4xl" />
    </main>
  );
}
