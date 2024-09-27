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

  // Results should be displayed as a table (for inspi, see table from the guy I contacted on x about synthetic monitoring)

  return (
    <div className="flex flex-col bg-accent-foreground">
      <Card className="">
        <CardHeader>
          <CardTitle>{t('upper_gray_squirrel_cry')}</CardTitle>
          <CardDescription>
            Les données environnementales et sanitaires de référence pour le
            bâtiment
          </CardDescription>
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
      {results.map((result) => (
        <Card className="mt-4" key={result.id}>
          <CardHeader>
            <CardTitle>{result.title}</CardTitle>
          </CardHeader>
        </Card>
      ))}
    </div>
  );
}
