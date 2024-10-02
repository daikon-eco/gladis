'use client';

import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

export default function SearchApp() {
  const variants = [
    'default',
    'destructive',
    'ghost',
    'link',
    'outline',
    'secondary',
  ] as const;

  const size = ['sm', 'default', 'lg', 'icon'] as const;

  return (
    <div
      // NOTE: we set min-h-[60vh] to center the content on the page, for whatever reason I can't manage to center it without assigin an height
      className={cn('flex min-h-[60vh] w-full flex-col')}
    >
      <div className="flex flex-col gap-2">
        <h1 className="text-lg">Button</h1>
        <div className="flex gap-2">
          {variants.map((variant) => (
            <Button key={variant} variant={variant} disabled={false}>
              {capitalize(variant)}
            </Button>
          ))}
        </div>
        <div className="flex gap-2">
          {variants.map((variant) => (
            <Button key={variant} variant={variant} disabled={true}>
              {capitalize(variant)}
            </Button>
          ))}
        </div>
        <div className="flex gap-2">
          {size.map((size) => (
            <Button key={size} size={size}>
              {capitalize(size)}
            </Button>
          ))}
        </div>
      </div>
    </div>
  );
}

function capitalize(s: string) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}
