import { Metadata } from "next";

import { getAllLanguages, getLanguageData } from "@/lib/data";

export const metadata: Metadata = {
  title: "Languages",
  description: "Explore GitHub repositories by primary programming language.",
};

export default async function LanguagesIndex() {
  const langList = await getAllLanguages();
  
  const langsData = await Promise.all(
    langList.map(l => getLanguageData(l.language))
  );

  return (
    <div className="space-y-6">
      <h1 className="text-4xl font-extrabold tracking-tight">Browse by Language</h1>
      <p className="text-lg text-gray-600 dark:text-gray-400">
        Discover the most popular and useful repositories across different programming languages.
      </p>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {langsData.filter(Boolean).map((l, idx) => (
          <a key={idx} href={`/language/${l.slug}`} className="block p-6 rounded-xl border border-gray-200 dark:border-gray-800 hover:border-blue-500 transition-colors group">
            <h2 className="font-bold text-xl mb-2 group-hover:text-blue-500 transition-colors">{l.name}</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-2">{l.content?.intro}</p>
          </a>
        ))}
      </div>
    </div>
  );
}
