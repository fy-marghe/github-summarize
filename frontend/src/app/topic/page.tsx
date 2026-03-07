import { Metadata } from "next";

import { getAllTopics, getTopicData } from "@/lib/data";

export const metadata: Metadata = {
  title: "Topics",
  description: "Explore GitHub repositories by topic. Find the best tools for your next project.",
};

export default async function TopicsIndex() {
  const topicList = await getAllTopics();
  
  // Fetch detailed data for each topic to display nicely
  const topicsData = await Promise.all(
    topicList.map(t => getTopicData(t.topic))
  );

  return (
    <div className="space-y-6">
      <h1 className="text-4xl font-extrabold tracking-tight">Explore Topics</h1>
      <p className="text-lg text-gray-600 dark:text-gray-400">
        Browse curated lists of GitHub repositories grouped by functionality and ecosystem.
      </p>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {topicsData.filter(Boolean).map((t, idx) => (
          <a key={idx} href={`/topic/${t.slug}`} className="block p-6 rounded-xl border border-gray-200 dark:border-gray-800 hover:border-blue-500 transition-colors group">
            <h2 className="font-bold text-xl mb-2 group-hover:text-blue-500 transition-colors">{t.name}</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-2">{t.description}</p>
          </a>
        ))}
      </div>
    </div>
  );
}
