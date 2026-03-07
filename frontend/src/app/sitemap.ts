import { MetadataRoute } from 'next'
import { getAllRepos, getAllTopics, getAllLanguages } from '@/lib/data'

export const dynamic = 'force-static'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://github-seo.example.com'

  const routes = ['', '/topic', '/language'].map((route) => ({
    url: `${baseUrl}${route}`,
    lastModified: new Date(),
    changeFrequency: 'daily' as const,
    priority: 1,
  }))

  const repos = await getAllRepos()
  const repoRoutes = repos.map((repo) => ({
    url: `${baseUrl}/repo/${repo.owner}/${repo.repo}`,
    lastModified: new Date(),
    changeFrequency: 'weekly' as const,
    priority: 0.8,
  }))

  const topics = await getAllTopics()
  const topicRoutes = topics.map((t) => ({
    url: `${baseUrl}/topic/${t.topic}`,
    lastModified: new Date(),
    changeFrequency: 'weekly' as const,
    priority: 0.9,
  }))

  const languages = await getAllLanguages()
  const languageRoutes = languages.map((l) => ({
    url: `${baseUrl}/language/${l.language}`,
    lastModified: new Date(),
    changeFrequency: 'weekly' as const,
    priority: 0.9,
  }))

  return [...routes, ...repoRoutes, ...topicRoutes, ...languageRoutes]
}
