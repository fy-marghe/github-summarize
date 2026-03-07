import { getRepoData, getAllRepos } from "@/lib/data";
import { notFound } from "next/navigation";
import { Metadata } from "next";

export async function generateStaticParams() {
  const repos = await getAllRepos();
  return repos.map((repo) => ({
    owner: repo.owner,
    repo: repo.repo,
  }));
}

export async function generateMetadata(
  // @ts-expect-error Types issue with params Promise in Next.js 15
  { params }: { params: Promise<{ owner: string; repo: string }> }
): Promise<Metadata> {
  const resolvedParams = await params;
  const data = await getRepoData(resolvedParams.owner, resolvedParams.repo);
  if (!data) return {};
  
  return {
    title: data.seo_metadata?.title || `${resolvedParams.owner}/${resolvedParams.repo}`,
    description: data.seo_metadata?.description || data.repo_metadata?.description,
    alternates: {
      canonical: data.canonical_path,
    },
    robots: {
      index: data.indexing?.is_indexable ?? true,
      follow: true,
    }
  };
}

export default async function RepoPage(
  // @ts-expect-error Types issue with params Promise in Next.js 15
  { params }: { params: Promise<{ owner: string; repo: string }> }
) {
  const resolvedParams = await params;
  const data = await getRepoData(resolvedParams.owner, resolvedParams.repo);

  if (!data) {
    notFound();
  }

  return (
    <article className="max-w-4xl mx-auto space-y-12">
      <header className="space-y-6 pb-8 border-b border-gray-200 dark:border-gray-800">
        <div className="flex items-center gap-2 text-sm font-medium text-gray-500">
          <a href="/topic" className="hover:text-black dark:hover:text-white transition-colors">Topic</a>
          <span>›</span>
          <a href={`/topic/${data.primary_topic}`} className="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded hover:opacity-80 transition-opacity">
            {data.primary_topic}
          </a>
        </div>
        <h1 className="text-4xl font-extrabold tracking-tight">
          <a href={`https://github.com/${data.id}`} target="_blank" rel="noopener noreferrer" className="hover:underline">
            {data.id}
          </a>
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400">
          {data.repo_metadata.description}
        </p>
        
        <div className="flex flex-wrap gap-4 text-sm mt-4">
          <span className="flex items-center gap-1">
            <span className="text-yellow-500">★</span> 
            {data.repo_metadata.stars.toLocaleString()} Stars
          </span>
          <span className="flex items-center gap-1">
            <span className="text-gray-400">⑂</span>
            {data.repo_metadata.forks.toLocaleString()} Forks
          </span>
          <a href={`/language/${data.repo_metadata.primary_language.toLowerCase()}`} className="flex items-center gap-1 hover:text-blue-500">
            <span className="text-blue-500">■</span>
            {data.repo_metadata.primary_language}
          </a>
        </div>
      </header>

      <section className="space-y-4">
        <h2 className="text-2xl font-bold">What it does</h2>
        <div className="prose dark:prose-invert max-w-none text-gray-600 dark:text-gray-300 bg-gray-50 dark:bg-gray-900/50 p-6 rounded-xl border border-gray-100 dark:border-gray-800">
          {data.content.what_it_does}
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-2xl font-bold">Key Features</h2>
        <ul className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data.content.key_features.map((feature: string, idx: number) => (
            <li key={idx} className="flex gap-2">
              <span className="text-blue-500">✓</span>
              <span>{feature}</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="space-y-4">
        <h2 className="text-2xl font-bold">Architecture Overview</h2>
        <div className="prose dark:prose-invert max-w-none text-gray-600 dark:text-gray-300 leading-relaxed">
          {data.content.architecture_overview}
        </div>
      </section>
      
      <section className="space-y-4">
        <h2 className="text-2xl font-bold">How to run</h2>
        <pre className="bg-gray-950 text-gray-300 p-4 rounded-xl overflow-x-auto text-sm font-mono border border-gray-800">
          <code>{data.content.how_to_run}</code>
        </pre>
      </section>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 pt-8 border-t border-gray-200 dark:border-gray-800">
        <section className="space-y-4">
          <h2 className="text-xl font-bold">Important Files</h2>
          <ul className="space-y-2">
            {data.content.important_files.map((file: string, idx: number) => (
              <li key={idx} className="flex items-center gap-2 text-sm font-mono bg-gray-50 dark:bg-gray-900 px-3 py-2 rounded-lg border border-gray-100 dark:border-gray-800">
                📄 {file}
              </li>
            ))}
          </ul>
        </section>

        <section className="space-y-4">
          <h2 className="text-xl font-bold">Related Topics</h2>
          <div className="flex flex-wrap gap-2">
            {data.related_topics.map((topic: string, idx: number) => (
              <a key={idx} href={`/topic/${topic}`} className="px-3 py-1.5 bg-gray-100 dark:bg-gray-800 text-sm font-medium rounded-lg hover:opacity-80 transition-opacity">
                {topic}
              </a>
            ))}
          </div>
        </section>
      </div>

    </article>
  );
}
