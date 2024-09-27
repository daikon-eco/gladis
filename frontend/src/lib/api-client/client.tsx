export type SearchResult = {
  id: string;
  title: string;
  category: string;
  value: string;
  functionalUnit: string;
  mainPerformance: string;
  url: string;
};

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
    health?: unknown;
    comfort?: unknown;
    documents?: { id: string; name: string; link: string }[];
  };
};
type APIClient = {
  search: (query: string) => Promise<SearchResult[]>;
  getEPD: (id: string) => Promise<EPD>;
};

const localClient: APIClient = {
  search: async (query: string) => {
    await new Promise((r) => setTimeout(r, 100));

    if (!query) {
      return [];
    }

    return [
      {
        id: '1',
        title: 'IKO enertherm ALU NF 132mm R = 6.0 m2.K/W (v.1.1)',
        category: 'Isolants',
        functionalUnit:
          '1 m² de panneau de mousse polyuréthane rigide parementé, d’épaisseur 132 mm et de résistance thermique de 6.00 m².K/W',
        mainPerformance: 'Résistance thermique : 6 m2.K/W',
        url: 'https://www.base-inies.fr/iniesV4/dist/infos-produit',
        value: '1.34e+1 kg CO2 eq.',
      },
      {
        id: '2',
        title: 'IKO enertherm ALU 50 ; 160 mm ; R = 7.25 m2.K/W (v.1.1)',
        category: 'Isolants',
        functionalUnit:
          '1 m² de panneau de mousse polyuréthane rigide parementé, d’épaisseur 160 mm et de résistance thermique de 7.25 m².K/W',
        mainPerformance: 'Résistance thermique : 7.25 m2.K/W',
        url: 'https://www.base-inies.fr/iniesV4/dist/infos-produit/29641',
        value: '1.59e+1 kg CO2 eq.',
      },
    ];
  },

  // @ts-expect-error not implemented yet
  getEPD: async (id: string) => {
    return Promise.resolve({
      id,
      name,
    });
  },
};

export { localClient };
