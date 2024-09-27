export type SearchResult = { id: string; title: string; description: string };

export type EPD = {
  id: string;
  name: string;
  info: {
    declrationType: 'individual';
    organism: {
      name: string;
      adress: {
        line1: string;
        line2: string;
        postcode: string;
        city: string;
        country: string;
      };
      websiteUrl: string;
      contact: {
        fullname: string;
        phoneNumber: string;
        email: string;
      };
      category: string[];
      associatedRef: string[];
      updatedAt: Date;
      verifiedAt: Date;
      verifier: {
        id: string;
        fullname: string;
      };
      iniesRegistrationNumber: string;
      iniesRegisteredAt: Date;
      databaseUsed: 'ecoinvent' | 'GaBi';
      version: string;
      endOfValidityAt: Date;
      producedIn: 'outside_europe';
    };
    fonctionalUnit: {
      description: string;
      perfUnit: 'mm';
      quantity: {
        size: number;
        unit: 'm2';
      };
      designLife: {
        number: number;
        unit: 'years';
      };
      unincludedFeatures: string;
      fallRateAtConstruction: number;
      maintenanceFrequency: {
        number: number;
        unit: 'years';
      };
      contentDeclaration: string;
      transportDistances: {
        a4: number;
        c2recycledWaste: number;
        c2wasteForEnergy: number;
        c2wasteDisposedOd: number;
      };
      products: {
        name: string;
        value: {
          number: number;
          unit: 'kg';
        };
        type: 'Emballage' | 'Produit déclaré' | 'Produit complémentaire';
      }[];
    };
    indicators?: {
      norm: string;
      environmentalImpacts: {
        headers: string[];
        rows: string[]; // length should be headers.length +1
      };
    };
    health?: any;
    comfort?: any;
    documents?: { id: string; name: string; link: string }[];
  };
};
type APIClient = {
  search: (query: string) => Promise<SearchResult[]>;
  getEPD: (id: string) => Promise<EPD>;
};

const localClient: APIClient = {
  search: async (query: string) => {
    await new Promise((r) => setTimeout(r, 1000));

    if (!query) {
      return [];
    }

    return [
      { id: '1', title: 'Résultat 1', description: 'Description du résultat 1' },
      { id: '2', title: 'Résultat 2', description: 'Description du résultat 2' },
    ];
  },

  getEPD: async (id: string) => {
    return Promise.resolve({
      id,
      name,
    });
  },
};

export { localClient };
