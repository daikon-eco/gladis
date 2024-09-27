import { createContext, useContext } from 'react';
import { localClient } from './client';

const APIClientContext = createContext(localClient);
APIClientContext.displayName = 'APIClientContext';

const APIClientProvider = APIClientContext.Provider;

const useAPIClient = () => {
  const client = useContext(APIClientContext);
  if (!client) {
    throw new Error('useAPIClient must be used within a APIClientProvider');
  }
  return client;
};

export { APIClientProvider, useAPIClient };
