import NextLink from 'next/link';
import { cn } from '@/lib/utils';
import { ThemeToggle } from './theme-toggle';
import Image from 'next/image';
import { Link } from './ui/link';
import { Shell } from './shell';
import { useTranslations } from 'next-intl';

interface Props {
  className?: string;
}

export function Footer({ className }: Props) {
  const t = useTranslations();
  return (
    <footer className={cn('w-full', className)}>
      <Shell className="flex items-center justify-between gap-6">
        <Brand className="max-w-[25%]" />
        <div className="flex gap-2">
          <Link
            href="https://daikon.eco/"
            label={t('candid_deft_seahorse_agree')}
            external
          />
          <Link href="/legal/terms" label={t('early_free_goldfish_treat')} />
          <Link href="/legal/privacy" label={t('shy_patchy_niklas_reap')} />
        </div>
        <ThemeToggle />
      </Shell>
    </footer>
  );
}

function Brand({ className }: { className?: string }) {
  const t = useTranslations();
  return (
    <div className={className}>
      <NextLink
        href="/"
        className="flex max-w-28 items-center gap-2 font-geist font-semibold"
      >
        <Image
          src="/images/daikon_white.png"
          alt="Gladis"
          width={32}
          height={32}
          className="rounded-full border border-border bg-transparent"
        />
        Gladis
      </NextLink>
      <p className="mt-2 max-w-md text-sm font-light text-muted-foreground">
        {t('mealy_mealy_mayfly_honor')}{' '}
        <span className="underline decoration-dotted underline-offset-2">
          {t('chunky_nice_oryx_pet')}
        </span>
      </p>
    </div>
  );
}
