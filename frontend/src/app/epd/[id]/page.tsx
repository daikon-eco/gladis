'use client';
import { FormEvent, useState } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useTranslations } from 'next-intl';
import { useAPIClient } from '@/lib/api-client/context';
import { SearchResult } from '@/lib/api-client/client';

export default function SearchApp(params) {
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
    <div className="container mx-auto p-4 max-w-2xl">
      <Card>
        <CardHeader>
          <CardTitle>{t('upper_gray_squirrel_cry')}</CardTitle>
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

      {results.length > 0 && (
        <Card className="mt-4">
          <CardHeader>
            <CardTitle>{t('zippy_mellow_pelican_delight')}</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {results.map((result) => (
                <li key={result.id} className="border-b pb-2">
                  <h3 className="font-semibold">{result.title}</h3>
                  <p className="text-sm text-gray-600">{result.description}</p>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
