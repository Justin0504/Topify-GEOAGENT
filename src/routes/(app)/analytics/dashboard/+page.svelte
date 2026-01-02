<script lang="ts">
	import { onMount } from 'svelte';
	import { theme } from '$lib/stores';
	import GlobeAlt from '$lib/components/icons/GlobeAlt.svelte';
	import Calendar from '$lib/components/icons/Calendar.svelte';
	import Hashtag from '$lib/components/icons/Hashtag.svelte';
	import ChevronDown from '$lib/components/icons/ChevronDown.svelte';

	// Sample data - replace with actual API data
	let brandVisibility = 51.8;
	let citationShare = 12.0;
	let brandRanking = 1;
	let closestCompetitor = 'Netlify';
	let competitorMentions = 150;
	let totalPrompts = 1806;
	let totalCitations = 330;
	let totalCitationsMax = 2825;

	// Competitor data
	let competitors = [
		{ name: 'Vercel (You)', visibility: 51.8, rank: 1 },
		{ name: 'Netlify', visibility: 36.9, rank: 2 },
		{ name: 'AWS Amplify', visibility: 21.7, rank: 3 },
		{ name: 'Render', visibility: 21.4, rank: 4 },
		{ name: 'Heroku', visibility: 17.3, rank: 5 },
		{ name: 'Cloudflare Pages', visibility: 14.9, rank: 6 }
	];

	// Top sources data
	let topSources = [
		{ name: 'Wikipedia', domain: 'en.wikipedia.org', citations: 1690 },
		{ name: 'Medium', domain: 'medium.com', citations: 1153 },
		{ name: 'Aws', domain: 'aws.amazon.com', citations: 1115 },
		{ name: 'Cloud', domain: 'cloud.google.com', citations: 908 }
	];

	// Chart data (simplified - you can use a charting library for real charts)
	let chartDates = ['Oct 31', 'Nov 01', 'Nov 02', 'Nov 03', 'Nov 04', 'Nov 05', 'Nov 06'];
	let competitorVisibilityData = [
		[48.2, 49.1, 50.7, 50.9, 51.2, 51.5, 51.8],
		[35.1, 36.2, 37.0, 36.8, 36.9, 36.7, 36.9],
		[20.5, 21.2, 21.9, 21.6, 21.8, 21.7, 21.7]
	];

	$: isDark = $theme.includes('dark') || ($theme === 'system' && typeof window !== 'undefined' && window.matchMedia('(prefers-color-scheme: dark)').matches);
</script>

<div class="h-full w-full overflow-auto bg-white dark:bg-gray-900">
	<div class="max-w-7xl mx-auto px-6 py-8">
		<!-- Header with Filters -->
		<div class="flex flex-wrap items-center gap-4 mb-8">
			<div class="flex items-center gap-2 px-4 py-2 border border-gray-200 dark:border-gray-700 rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 transition">
				<GlobeAlt className="size-4 text-gray-600 dark:text-gray-400" />
				<span class="text-sm font-medium text-gray-700 dark:text-gray-300">All Platforms</span>
				<ChevronDown className="size-4 text-gray-600 dark:text-gray-400" />
			</div>
			<div class="flex items-center gap-2 px-4 py-2 border border-gray-200 dark:border-gray-700 rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 transition">
				<Calendar className="size-4 text-gray-600 dark:text-gray-400" />
				<span class="text-sm font-medium text-gray-700 dark:text-gray-300">Last 7 days</span>
				<ChevronDown className="size-4 text-gray-600 dark:text-gray-400" />
			</div>
			<div class="flex items-center gap-2 px-4 py-2 border border-gray-200 dark:border-gray-700 rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 transition">
				<Hashtag className="size-4 text-gray-600 dark:text-gray-400" />
				<span class="text-sm font-medium text-gray-700 dark:text-gray-300">All Topics</span>
				<ChevronDown className="size-4 text-gray-600 dark:text-gray-400" />
			</div>
		</div>

		<!-- Metric Cards -->
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
			<!-- Brand Visibility -->
			<div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-6">
				<div class="text-sm text-gray-600 dark:text-gray-400 mb-2">Brand Visibility</div>
				<div class="text-3xl font-bold text-gray-900 dark:text-white mb-2">{brandVisibility}%</div>
				<div class="text-xs text-gray-500 dark:text-gray-500">Based on {totalPrompts.toLocaleString()} prompts simulated</div>
			</div>

			<!-- Citation Share -->
			<div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-6">
				<div class="text-sm text-gray-600 dark:text-gray-400 mb-2">Citation Share</div>
				<div class="text-3xl font-bold text-gray-900 dark:text-white mb-2">{citationShare}%</div>
				<div class="text-xs text-gray-500 dark:text-gray-500">{totalCitations} of {totalCitationsMax.toLocaleString()} citations</div>
			</div>

			<!-- Brand Ranking -->
			<div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-6">
				<div class="text-sm text-gray-600 dark:text-gray-400 mb-2">Brand Ranking</div>
				<div class="text-3xl font-bold text-gray-900 dark:text-white mb-2">#{brandRanking}</div>
				<div class="text-xs text-gray-500 dark:text-gray-500">Market leader</div>
			</div>

			<!-- Closest Competitor -->
			<div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-6">
				<div class="text-sm text-gray-600 dark:text-gray-400 mb-2">Closest Competitor</div>
				<div class="flex items-center gap-2 mb-2">
					<div class="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center text-xs font-semibold text-gray-700 dark:text-gray-300">
						{closestCompetitor.charAt(0)}
					</div>
					<div class="text-lg font-semibold text-gray-900 dark:text-white">{closestCompetitor}</div>
				</div>
				<div class="text-xs text-gray-500 dark:text-gray-500">{competitorMentions} mentions</div>
			</div>
		</div>

		<!-- Charts and Tables Grid -->
		<div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
			<!-- Competitor Visibility Chart -->
			<div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-6">
				<div class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Competitor Visibility</div>
				<div class="h-64 relative">
					<svg viewBox="0 0 600 200" class="w-full h-full" preserveAspectRatio="none">
						<!-- Grid lines -->
						{#each [0, 25, 50, 75, 100] as value}
							<line
								x1="0"
								y1={200 - (value / 100 * 200)}
								x2="600"
								y2={200 - (value / 100 * 200)}
								stroke="currentColor"
								stroke-width="1"
								class="text-gray-200 dark:text-gray-700"
							/>
						{/each}
						<!-- Vercel line -->
						<polyline
							points={competitorVisibilityData[0].map((val, i) => `${(i / (chartDates.length - 1)) * 600},${200 - (val / 60 * 200)}`).join(' ')}
							fill="none"
							stroke="#3b82f6"
							stroke-width="2"
							class="transition-all"
						/>
						<!-- Netlify line -->
						<polyline
							points={competitorVisibilityData[1].map((val, i) => `${(i / (chartDates.length - 1)) * 600},${200 - (val / 60 * 200)}`).join(' ')}
							fill="none"
							stroke="#10b981"
							stroke-width="2"
							class="transition-all"
						/>
						<!-- AWS Amplify line -->
						<polyline
							points={competitorVisibilityData[2].map((val, i) => `${(i / (chartDates.length - 1)) * 600},${200 - (val / 60 * 200)}`).join(' ')}
							fill="none"
							stroke="#f59e0b"
							stroke-width="2"
							class="transition-all"
						/>
					</svg>
					<!-- X-axis labels -->
					<div class="absolute bottom-0 left-0 right-0 flex justify-between px-2 -mb-6">
						{#each chartDates as date}
							<span class="text-xs text-gray-500 dark:text-gray-400">{date}</span>
						{/each}
					</div>
				</div>
				<div class="flex gap-4 mt-8 text-xs">
					<div class="flex items-center gap-2">
						<div class="w-3 h-3 rounded bg-blue-500"></div>
						<span class="text-gray-600 dark:text-gray-400">Vercel (You)</span>
					</div>
					<div class="flex items-center gap-2">
						<div class="w-3 h-3 rounded bg-green-500"></div>
						<span class="text-gray-600 dark:text-gray-400">Netlify</span>
					</div>
					<div class="flex items-center gap-2">
						<div class="w-3 h-3 rounded bg-amber-500"></div>
						<span class="text-gray-600 dark:text-gray-400">AWS Amplify</span>
					</div>
				</div>
			</div>

			<!-- Citation Share Chart -->
			<div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-6">
				<div class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Citation Share</div>
				<div class="h-64 relative">
					<svg viewBox="0 0 600 200" class="w-full h-full" preserveAspectRatio="none">
						<!-- Grid lines -->
						{#each [0, 5, 10, 15, 20, 25] as value}
							<line
								x1="0"
								y1={200 - (value / 25 * 200)}
								x2="600"
								y2={200 - (value / 25 * 200)}
								stroke="currentColor"
								stroke-width="1"
								class="text-gray-200 dark:text-gray-700"
							/>
						{/each}
						<!-- Citation Share line -->
						<polyline
							points="0,140 100,130 200,125 300,120 400,115 500,110 600,105"
							fill="none"
							stroke="#3b82f6"
							stroke-width="2"
							class="transition-all"
						/>
					</svg>
					<!-- X-axis labels -->
					<div class="absolute bottom-0 left-0 right-0 flex justify-between px-2 -mb-6">
						{#each chartDates as date}
							<span class="text-xs text-gray-500 dark:text-gray-400">{date}</span>
						{/each}
					</div>
				</div>
			</div>
		</div>

		<!-- Tables Grid -->
		<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
			<!-- Competitor Rankings -->
			<div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-6">
				<div class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Competitor Rankings</div>
				<div class="overflow-x-auto">
					<table class="w-full">
						<thead>
							<tr class="border-b border-gray-200 dark:border-gray-700">
								<th class="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">Rank</th>
								<th class="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">Competitor</th>
								<th class="text-right py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">Visibility</th>
							</tr>
						</thead>
						<tbody>
							{#each competitors as competitor}
								<tr class="border-b border-gray-100 dark:border-gray-700/50 hover:bg-gray-50 dark:hover:bg-gray-700/30 transition">
									<td class="py-3 px-4 text-sm text-gray-900 dark:text-white">{competitor.rank}</td>
									<td class="py-3 px-4 text-sm text-gray-900 dark:text-white">{competitor.name}</td>
									<td class="py-3 px-4 text-sm text-right text-gray-900 dark:text-white font-medium">{competitor.visibility}%</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			</div>

			<!-- Top Sources -->
			<div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-6">
				<div class="flex items-center justify-between mb-4">
					<div class="text-lg font-semibold text-gray-900 dark:text-white">Top Sources</div>
					<a href="#" class="text-sm text-blue-600 dark:text-blue-400 hover:underline">View All ></a>
				</div>
				<div class="overflow-x-auto">
					<table class="w-full">
						<thead>
							<tr class="border-b border-gray-200 dark:border-gray-700">
								<th class="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">Source</th>
								<th class="text-right py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">Citations</th>
							</tr>
						</thead>
						<tbody>
							{#each topSources as source}
								<tr class="border-b border-gray-100 dark:border-gray-700/50 hover:bg-gray-50 dark:hover:bg-gray-700/30 transition">
									<td class="py-3 px-4">
										<div class="text-sm font-medium text-gray-900 dark:text-white">{source.name}</div>
										<div class="text-xs text-gray-500 dark:text-gray-400">{source.domain}</div>
									</td>
									<td class="py-3 px-4 text-sm text-right text-gray-900 dark:text-white font-medium">{source.citations.toLocaleString()}</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			</div>
		</div>
	</div>
</div>
