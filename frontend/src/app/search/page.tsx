'use client';
import { FormEvent, useState } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

type Result = { id: string; title: string; description: string };
const mockResults: Result[] = [
  { id: '1', title: 'Résultat 1', description: 'Description du résultat 1' },
  { id: '2', title: 'Résultat 2', description: 'Description du résultat 2' },
];

export default function SearchApp() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([] as Result[]);

  const handleSearch = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    // TODO: implement API search
    await new Promise((r) => setTimeout(r, 1000));
    setResults(mockResults);
  };

  return (
    <div className="container mx-auto p-4 max-w-2xl">
      <Card>
        <CardHeader>
          <CardTitle>Recherche en langage naturel</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSearch} className="flex space-x-2">
            <Input
              type="text"
              placeholder="Entrez votre recherche..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="flex-grow"
            />
            <Button type="submit">Rechercher</Button>
          </form>
        </CardContent>
      </Card>

      {results.length > 0 && (
        <Card className="mt-4">
          <CardHeader>
            <CardTitle>Résultats</CardTitle>
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
