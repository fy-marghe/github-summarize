import { getAllRepos, getRepoData } from "@/lib/data";

export default async function Home() {
  const repoList = await getAllRepos();
  const repoDataPromises = repoList.slice(0, 4).map(r => getRepoData(r.owner, r.repo));
  const trendingRepos = (await Promise.all(repoDataPromises)).filter(Boolean);

  return (
    <div className="space-y-12 py-12 flex flex-col items-center justify-center text-center">
      <div className="space-y-4 max-w-2xl">
        <h1 className="text-5xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-gray-900 to-gray-500 dark:from-white dark:to-gray-500">
          Understand any GitHub repository in minutes.
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400">
          AI-generated explanations, architecture overviews, and comparisons to help you find the right code faster.
        </p>
      </div>

      <div className="flex gap-4">
        <a href="/topic" className="px-6 py-3 bg-black dark:bg-white text-white dark:text-black font-semibold rounded-lg hover:opacity-90 transition-opacity">
          Explore Topics
        </a>
        <a href="/language" className="px-6 py-3 border border-gray-200 dark:border-gray-800 font-semibold rounded-lg hover:bg-gray-50 dark:hover:bg-gray-900 transition-colors">
          Browse Languages
        </a>
      </div>

      <div className="w-full max-w-4xl text-left border-t border-gray-200 dark:border-gray-800 pt-12 mt-12">
        <h2 className="text-2xl font-bold mb-6">Trending Repositories</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {trendingRepos.map((r, idx) => (
            <a key={idx} href={`/repo/${r.repo_metadata?.owner}/${r.repo_metadata?.name}`} className="block p-6 rounded-xl border border-gray-200 dark:border-gray-800 hover:border-blue-500 transition-colors group">
              <h3 className="font-bold text-lg group-hover:text-blue-500 transition-colors">{r.id}</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-2 line-clamp-2">
                {r.repo_metadata?.description}
              </p>
            </a>
          ))}
        </div>
      </div>
    </div>
  );
}
