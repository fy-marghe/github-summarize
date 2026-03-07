import { getTopicData, getAllTopics } from "@/lib/data";
import { notFound } from "next/navigation";
import { Metadata } from "next";

export async function generateStaticParams() {
  const topics = await getAllTopics();
  return topics.map((t) => ({
    topic: t.topic,
  }));
}

export async function generateMetadata(
  // @ts-expect-error Types issue with params Promise in Next.js 15
  { params }: { params: Promise<{ topic: string }> }
): Promise<Metadata> {
  const resolvedParams = await params;
  const data = await getTopicData(resolvedParams.topic);
  if (!data) return {};
  
  return {
    title: data.seo_metadata?.title || data.name,
    description: data.seo_metadata?.description || data.description,
    alternates: {
      canonical: data.canonical_path,
    },
    robots: {
      index: true,
      follow: true,
    }
  };
}

export default async function TopicPage(
  // @ts-expect-error Types issue with params Promise in Next.js 15
  { params }: { params: Promise<{ topic: string }> }
) {
  const resolvedParams = await params;
  const data = await getTopicData(resolvedParams.topic);

  if (!data) {
    notFound();
  }

  return (
    <article className="max-w-4xl mx-auto space-y-12">
      <header className="space-y-6 pb-8 border-b border-gray-200 dark:border-gray-800 text-center">
        <h1 className="text-4xl font-extrabold tracking-tight">
          {data.name}
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
          {data.description}
        </p>
      </header>

      <section className="space-y-4">
        <h2 className="text-2xl font-bold">Introduction</h2>
        <div className="prose dark:prose-invert max-w-none text-gray-600 dark:text-gray-300">
          {data.content.intro}
        </div>
      </section>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <section className="space-y-4">
          <h2 className="text-2xl font-bold">Who is this for?</h2>
          <div className="bg-gray-50 dark:bg-gray-900/50 p-6 rounded-xl border border-gray-100 dark:border-gray-800 text-gray-600 dark:text-gray-300">
            {data.content.who_this_topic_is_for}
          </div>
        </section>

        <section className="space-y-4">
          <h2 className="text-2xl font-bold">Common Architecture</h2>
          <div className="bg-gray-50 dark:bg-gray-900/50 p-6 rounded-xl border border-gray-100 dark:border-gray-800 text-gray-600 dark:text-gray-300">
            {data.content.common_architecture}
          </div>
        </section>
      </div>

      <section className="space-y-4">
        <h2 className="text-2xl font-bold">Pros and Cons</h2>
        <div className="prose dark:prose-invert max-w-none text-gray-600 dark:text-gray-300">
          {data.content.pros_cons}
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-2xl font-bold">Learning Resources</h2>
        <ul className="list-disc pl-5 space-y-2 text-gray-600 dark:text-gray-300">
          {data.content.learning_resources.map((res: string, i: number) => (
            <li key={i}>{res}</li>
          ))}
        </ul>
      </section>

      <section className="space-y-6 pt-8 border-t border-gray-200 dark:border-gray-800">
        <h2 className="text-2xl font-bold">Top Repositories for {data.name}</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data.top_repos.map((repoSlug: string, idx: number) => {
            const [owner, repo] = repoSlug.split('--');
            return (
              <a key={idx} href={`/repo/${owner}/${repo}`} className="block p-4 rounded-xl border border-gray-200 dark:border-gray-800 hover:border-blue-500 transition-colors group">
                <h3 className="font-bold text-lg group-hover:text-blue-500 transition-colors">{owner} / {repo}</h3>
                <span className="text-blue-500 text-sm mt-2 inline-block">Read Analysis →</span>
              </a>
            );
          })}
        </div>
      </section>

      <section className="space-y-4 pt-8 border-t border-gray-200 dark:border-gray-800">
        <h2 className="text-xl font-bold">Related Topics</h2>
        <div className="flex flex-wrap gap-2">
          {data.related_topics.map((topic: string, idx: number) => (
            <a key={idx} href={`/topic/${topic}`} className="px-3 py-1.5 bg-gray-100 dark:bg-gray-800 text-sm font-medium rounded-lg hover:opacity-80 transition-opacity">
              {topic}
            </a>
          ))}
        </div>
      </section>

    </article>
  );
}
