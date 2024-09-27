import NextLink from 'next/link';
import { Icons } from '../icons';

export function Link({
  href,
  label,
  external = false,
}: {
  href: string;
  label: string;
  external?: boolean;
}) {
  const isExternal = external || href.startsWith('http');

  const externalProps = isExternal
    ? {
        target: '_blank',
        rel: 'noreferrer',
      }
    : {};

  return (
    <NextLink
      className="inline-flex w-fit items-center text-sm text-muted-foreground underline underline-offset-4 hover:text-foreground hover:no-underline"
      href={href}
      {...externalProps}
    >
      {label}
      {isExternal ? (
        <Icons.arrowUpRight className="h-4 w-4 flex-shrink-0" />
      ) : null}
    </NextLink>
  );
}
