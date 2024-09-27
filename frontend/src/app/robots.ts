import type { MetadataRoute } from 'next';

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: '*',
      allow: '/',
    },
    // TODO: Add sitemap once ready to share
    // sitemap: 'https://www.openstatus.dev/sitemap.xml',
  };
}
