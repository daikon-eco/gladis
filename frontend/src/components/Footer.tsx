import Link from 'next/link';
import { cn } from '@/lib/utils';
import { ThemeToggle } from './theme-toggle';
import Image from 'next/image';

import { Icons } from './icons';
import { Shell } from './shell';

interface Props {
  className?: string;
}

export function Footer({ className }: Props) {
  return (
    <footer className={cn('w-full', className)}>
      <Shell className="flex gap-6 justify-between items-center">
        <Brand className="max-w-[25%]" />
        <div className="flex gap-2">
          <FooterLink href="https://daikon.eco/" label="About" external />
          <FooterLink href="/legal/terms" label="Terms" />
          <FooterLink href="/legal/privacy" label="Privacy" />
        </div>
        <ThemeToggle />
      </Shell>
    </footer>
  );
}

function FooterLink({ href, label, external = false }: { href: string; label: string; external?: boolean }) {
  const isExternal = external || href.startsWith('http');

  const externalProps = isExternal
    ? {
        target: '_blank',
        rel: 'noreferrer',
      }
    : {};

  return (
    <Link
      className="inline-flex w-fit items-center text-muted-foreground underline underline-offset-4 hover:text-foreground hover:no-underline text-sm"
      href={href}
      {...externalProps}
    >
      {label}
      {isExternal ? <Icons.arrowUpRight className="ml-1 h-4 w-4 flex-shrink-0" /> : null}
    </Link>
  );
}

function Brand({ className }: { className?: string }) {
  return (
    <div className={className}>
      <Link href="/" className="flex items-center gap-2 font-geist font-semibold max-w-28">
        <Image
          src="/images/daikon_white.png"
          alt="Gladis"
          width={32}
          height={32}
          className="rounded-full border border-border bg-transparent"
        />
        Gladis
      </Link>
      <p className="mt-2 max-w-md font-light text-muted-foreground text-sm">
        EPD Search Engine, <span className="underline decoration-dotted underline-offset-2">easily</span>
      </p>
    </div>
  );
}
