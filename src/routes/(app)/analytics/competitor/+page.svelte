<script lang="ts">
	import { onMount } from 'svelte';
	import Plus from '$lib/components/icons/Plus.svelte';
	import XMark from '$lib/components/icons/XMark.svelte';
	import GlobeAlt from '$lib/components/icons/GlobeAlt.svelte';
	import Document from '$lib/components/icons/Document.svelte';

	interface Competitor {
		id: string;
		name: string;
		website: string;
		logo: string; // Logo text or emoji
		logoColor?: string;
	}

	const MAX_COMPETITORS = 20;

	let competitorName = '';
	let competitorWebsite = '';
	let competitors: Competitor[] = [
		{
			id: '1',
			name: 'Ahrefs',
			website: 'ahrefs.com',
			logo: 'A',
			logoColor: 'bg-blue-500'
		},
		{
			id: '2',
			name: 'Moz Pro',
			website: 'moz.com',
			logo: 'M',
			logoColor: 'bg-gray-600'
		},
		{
			id: '3',
			name: 'SE Ranking',
			website: 'seranking.com',
			logo: 'SE',
			logoColor: 'bg-blue-600'
		},
		{
			id: '4',
			name: 'Serpstat',
			website: 'serpstat.com',
			logo: 'S',
			logoColor: 'bg-blue-700'
		},
		{
			id: '5',
			name: 'SpyFu',
			website: 'spyfu.com',
			logo: 'SF',
			logoColor: 'bg-black'
		},
		{
			id: '6',
			name: 'Similarweb',
			website: 'similarweb.com',
			logo: 'SW',
			logoColor: 'bg-black'
		},
		{
			id: '7',
			name: 'Mangools',
			website: 'mangools.com',
			logo: 'M',
			logoColor: 'bg-orange-500'
		},
		{
			id: '8',
			name: 'BrightLocal',
			website: 'brightlocal.com',
			logo: 'BL',
			logoColor: 'bg-green-500'
		},
		{
			id: '9',
			name: 'Ubersuggest',
			website: 'neilpatel.com/ubersuggest',
			logo: 'U',
			logoColor: 'bg-purple-500'
		},
		{
			id: '10',
			name: 'SEO PowerSuite',
			website: 'seopowersuite.com',
			logo: 'SEO',
			logoColor: 'bg-gradient-to-br from-green-400 via-orange-400 to-blue-500'
		}
	];

	const addCompetitor = () => {
		if (!competitorName.trim()) {
			return;
		}

		if (competitors.length >= MAX_COMPETITORS) {
			alert(`You can only track up to ${MAX_COMPETITORS} competitors.`);
			return;
		}

		const newCompetitor: Competitor = {
			id: Date.now().toString(),
			name: competitorName.trim(),
			website: competitorWebsite.trim() || '',
			logo: competitorName.trim().charAt(0).toUpperCase(),
			logoColor: 'bg-gray-500'
		};

		competitors = [...competitors, newCompetitor];
		competitorName = '';
		competitorWebsite = '';
	};

	const removeCompetitor = (id: string) => {
		competitors = competitors.filter((c) => c.id !== id);
	};

	const getLogoText = (name: string): string => {
		const words = name.split(' ');
		if (words.length >= 2) {
			return (words[0].charAt(0) + words[1].charAt(0)).toUpperCase();
		}
		return name.substring(0, 2).toUpperCase();
	};
</script>

<div class="h-full w-full overflow-auto bg-gray-50 dark:bg-gray-900">
	<div class="max-w-6xl mx-auto px-6 py-12">
		<!-- Header -->
		<div class="text-center mb-12">
			<h1 class="text-4xl font-bold text-gray-900 dark:text-white mb-3">Add Your Competitors</h1>
			<p class="text-lg text-gray-600 dark:text-gray-400">
				Track up to {MAX_COMPETITORS} competitors to monitor your relative AI visibility
			</p>
		</div>

		<!-- Add New Competitor Section -->
		<div class="mb-12">
			<h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Add New Competitor</h2>
			<div class="flex items-start gap-4">
				<div class="flex-1 flex gap-3">
					<!-- Competitor Name Input -->
					<div class="flex-1 relative">
						<div class="absolute left-3 top-1/2 transform -translate-y-1/2">
							<Document className="size-5 text-gray-400" />
						</div>
						<input
							type="text"
							bind:value={competitorName}
							placeholder="Competitor name"
							class="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
							on:keydown={(e) => {
								if (e.key === 'Enter') {
									addCompetitor();
								}
							}}
						/>
					</div>

					<!-- Website Input -->
					<div class="flex-1 relative">
						<div class="absolute left-3 top-1/2 transform -translate-y-1/2">
							<GlobeAlt className="size-5 text-gray-400" />
						</div>
						<input
							type="text"
							bind:value={competitorWebsite}
							placeholder="www.example.com (optional)"
							class="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
							on:keydown={(e) => {
								if (e.key === 'Enter') {
									addCompetitor();
								}
							}}
						/>
					</div>
				</div>

				<!-- Add Button -->
				<div class="flex flex-col items-end gap-2">
					<div class="text-xs text-gray-500 dark:text-gray-400">
						{competitors.length}/{MAX_COMPETITORS}
					</div>
					<button
						class="px-6 py-3 bg-black dark:bg-white text-white dark:text-black rounded-lg hover:bg-gray-800 dark:hover:bg-gray-100 transition flex items-center gap-2 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
						on:click={addCompetitor}
						disabled={competitors.length >= MAX_COMPETITORS || !competitorName.trim()}
					>
						<Plus className="size-5" />
					</button>
				</div>
			</div>
		</div>

		<!-- Competitors Grid -->
		{#if competitors.length > 0}
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
				{#each competitors as competitor (competitor.id)}
					<div
						class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 flex items-center gap-3 hover:shadow-md transition relative group"
					>
						<!-- Logo -->
						<div
							class="w-12 h-12 rounded-lg {competitor.logoColor} flex items-center justify-center shrink-0 text-white font-bold text-sm"
						>
							{competitor.logo.length <= 2 ? competitor.logo : getLogoText(competitor.name)}
						</div>

						<!-- Competitor Info -->
						<div class="flex-1 min-w-0">
							<h3 class="text-base font-semibold text-gray-900 dark:text-white truncate">
								{competitor.name}
							</h3>
							{#if competitor.website}
								<p class="text-sm text-gray-500 dark:text-gray-400 truncate mt-0.5">
									{competitor.website}
								</p>
							{:else}
								<p class="text-sm text-gray-400 dark:text-gray-500 italic mt-0.5">No website</p>
							{/if}
						</div>

						<!-- Remove Button -->
						<button
							class="opacity-0 group-hover:opacity-100 transition p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg shrink-0"
							on:click={() => removeCompetitor(competitor.id)}
							aria-label="Remove competitor"
						>
							<XMark className="size-5 text-gray-500 dark:text-gray-400" />
						</button>
					</div>
				{/each}
			</div>
		{:else}
			<div class="text-center py-12">
				<p class="text-gray-500 dark:text-gray-400">No competitors added yet. Add your first competitor above.</p>
			</div>
		{/if}
	</div>
</div>
