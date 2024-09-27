'use client';

import { FormEvent, useState } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { useTranslations } from 'next-intl';
import { useAPIClient } from '@/lib/api-client/context';
import { SearchResult } from '@/lib/api-client/client';
import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { Link } from '@/components/ui/link';

export default function SearchApp() {
  const client = useAPIClient();
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const [results, setResults] = useState([] as SearchResult[]);
  const t = useTranslations();
  const handleSearch = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    setIsLoading(true);
    const results = await client.search(query);
    setResults(results);
    setIsLoading(false);
  };

  return (
    <div
      // NOTE: we set min-h-[60vh] to center the content on the page, for whatever reason I can't manage to center it without assigin an height
      className={cn('flex min-h-[60vh] w-full flex-col', {
        'justify-center': results.length === 0,
      })}
    >
      <Card className="">
        <CardHeader>
          <CardTitle>{t('upper_gray_squirrel_cry')}</CardTitle>
          <CardDescription>{t('these_flat_stork_sprout')}</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSearch} className="flex space-x-2">
            <Input
              type="text"
              placeholder={t('fuzzy_this_jay_clasp')}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="flex-grow"
            />
            <Button type="submit" disabled={isLoading}>
              {t('clean_keen_robin_embrace')}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Accordion type="multiple">
        {results.map((result) => (
          <AccordionItem value={result.id}>
            <Card className="mt-4">
              <AccordionTrigger>
                <CardHeader className="flex flex-row items-center gap-4">
                  <CardTitle className="w-3/5 truncate hover:underline">
                    {result.title}
                  </CardTitle>
                  <Badge variant="default" className="size-fit">
                    {result.category}
                  </Badge>
                  <span className="text-muted-foregound">{result.value}</span>
                </CardHeader>
              </AccordionTrigger>
              <AccordionContent>
                <CardContent>
                  <span className="font-semibold">
                    Unité fonctionnelle (U.F.):{' '}
                  </span>{' '}
                  {result.functionalUnit}
                  <br />
                  <br />
                  <span className="font-semibold">
                    Performance principale de l'UF (U.F.):{' '}
                  </span>{' '}
                  {result.mainPerformance}
                  <br />
                  <br />
                  <Link label="Lien" href={result.url} />
                </CardContent>
              </AccordionContent>
            </Card>
          </AccordionItem>
        ))}
      </Accordion>
    </div>
  );
}
