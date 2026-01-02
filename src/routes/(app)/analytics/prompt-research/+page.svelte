<script lang="ts">
	import { onMount } from 'svelte';
	import ChevronDown from '$lib/components/icons/ChevronDown.svelte';
	import ChevronUp from '$lib/components/icons/ChevronUp.svelte';
	import Link from '$lib/components/icons/Link.svelte';
	import Plus from '$lib/components/icons/Plus.svelte';
	import dayjs from '$lib/dayjs';
	import relativeTime from 'dayjs/plugin/relativeTime';
	
	dayjs.extend(relativeTime);

	// Sample data structure
	interface Prompt {
		id: string;
		topic: string;
		avgVisibility: number;
		visibilityTrend: 'up' | 'down';
		topPerformers: string[];
		location: string;
		locationCode: string;
		region: string;
		created: number;
		status: 'prompt-ran' | 'pending' | 'failed';
	}

	interface PromptGroup {
		id: string;
		name: string;
		prompts: Prompt[];
		avgVisibility: number;
		visibilityTrend: 'up' | 'down';
		topPerformers: string[];
		locationCount: number;
		region: string;
		created: number;
		statusLink?: string;
		expanded: boolean;
	}

	let promptGroups: PromptGroup[] = [
		{
			id: '1',
			name: 'Business Credit Cards',
			prompts: [
				{
					id: '1-1',
					topic: 'business credit card providers with expense management tools',
					avgVisibility: 0,
					visibilityTrend: 'down',
					topPerformers: ['Z'],
					location: 'US',
					locationCode: 'US',
					region: 'Connecticut',
					created: Date.now() - 9 * 24 * 60 * 60 * 1000,
					status: 'prompt-ran'
				},
				{
					id: '1-2',
					topic: 'best business credit cards for startups and SMEs',
					avgVisibility: 5,
					visibilityTrend: 'down',
					topPerformers: ['Z'],
					location: 'JP',
					locationCode: 'JP',
					region: 'Tokyo',
					created: Date.now() - 8 * 24 * 60 * 60 * 1000,
					status: 'prompt-ran'
				},
				{
					id: '1-3',
					topic: 'corporate credit card comparison features rewards limits',
					avgVisibility: 0,
					visibilityTrend: 'down',
					topPerformers: ['Z'],
					location: 'US',
					locationCode: 'US',
					region: 'New York',
					created: Date.now() - 7 * 24 * 60 * 60 * 1000,
					status: 'prompt-ran'
				},
				{
					id: '1-4',
					topic: 'top recommended business credit cards for SMEs and expense tracking',
					avgVisibility: 38,
					visibilityTrend: 'down',
					topPerformers: ['Z', 'XO'],
					location: 'IN',
					locationCode: 'IN',
					region: 'Bangalore',
					created: Date.now() - 6 * 24 * 60 * 60 * 1000,
					status: 'prompt-ran'
				},
				{
					id: '1-5',
					topic: 'best business credit cards for startups',
					avgVisibility: 73,
					visibilityTrend: 'up',
					topPerformers: ['Z'],
					location: 'US',
					locationCode: 'US',
					region: 'New York',
					created: Date.now() - 5 * 24 * 60 * 60 * 1000,
					status: 'prompt-ran'
				},
				{
					id: '1-6',
					topic: 'compare corporate credit cards with expense management features',
					avgVisibility: 79,
					visibilityTrend: 'up',
					topPerformers: ['Z'],
					location: 'UK',
					locationCode: 'GB',
					region: 'London',
					created: Date.now() - 4 * 24 * 60 * 60 * 1000,
					status: 'prompt-ran'
				},
				{
					id: '1-7',
					topic: 'business credit cards with highest reward rates and cashback',
					avgVisibility: 7,
					visibilityTrend: 'down',
					topPerformers: ['Z'],
					location: 'US',
					locationCode: 'US',
					region: 'New York',
					created: Date.now() - 3 * 24 * 60 * 60 * 1000,
					status: 'prompt-ran'
				},
				{
					id: '1-8',
					topic: 'most reliable corporate cards for businesses with good customer service',
					avgVisibility: 37,
					visibilityTrend: 'down',
					topPerformers: ['Z'],
					location: 'UK',
					locationCode: 'GB',
					region: 'Manchester',
					created: Date.now() - 2 * 24 * 60 * 60 * 1000,
					status: 'prompt-ran'
				}
			],
			avgVisibility: 30,
			visibilityTrend: 'down',
			topPerformers: ['Z'],
			locationCount: 4,
			region: 'Multiple',
			created: Date.now() - 9 * 24 * 60 * 60 * 1000,
			statusLink: '#',
			expanded: true
		}
	];

	const toggleGroup = (group: PromptGroup) => {
		group.expanded = !group.expanded;
		promptGroups = [...promptGroups];
	};

	const getFlagEmoji = (code: string): string => {
		const flags: Record<string, string> = {
			US: '🇺🇸',
			JP: '🇯🇵',
			IN: '🇮🇳',
			GB: '🇬🇧',
			UK: '🇬🇧'
		};
		return flags[code] || '🌍';
	};

	const getPerformerIcon = (performer: string): string => {
		// Return a simple text representation or use actual icons
		return performer;
	};
</script>

<div class="h-full w-full overflow-auto bg-gray-50 dark:bg-gray-900">
	<div class="max-w-[1400px] mx-auto px-6 py-6">
		<!-- Top Bar with Model Selector -->
		<div class="mb-6">
			<select
				class="px-4 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm font-medium cursor-pointer hover:border-gray-300 dark:hover:border-gray-600 transition"
			>
				<option value="chatgpt">ChatGPT</option>
				<option value="claude">Claude</option>
				<option value="gemini">Gemini</option>
			</select>
		</div>

		<!-- Table Container -->
		<div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
			<div class="overflow-x-auto">
				<table class="w-full">
					<thead>
						<tr class="border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-850">
							<th class="text-left py-3 px-4 text-xs font-semibold text-gray-600 dark:text-gray-400">Topic</th>
							<th class="text-left py-3 px-4 text-xs font-semibold text-gray-600 dark:text-gray-400">Prompts</th>
							<th class="text-left py-3 px-4 text-xs font-semibold text-gray-600 dark:text-gray-400">Avg Visibility</th>
							<th class="text-left py-3 px-4 text-xs font-semibold text-gray-600 dark:text-gray-400">Top Performers</th>
							<th class="text-left py-3 px-4 text-xs font-semibold text-gray-600 dark:text-gray-400">Location</th>
							<th class="text-left py-3 px-4 text-xs font-semibold text-gray-600 dark:text-gray-400">Region</th>
							<th class="text-left py-3 px-4 text-xs font-semibold text-gray-600 dark:text-gray-400">Created</th>
							<th class="text-left py-3 px-4 text-xs font-semibold text-gray-600 dark:text-gray-400">Status</th>
						</tr>
					</thead>
					<tbody>
						{#each promptGroups as group (group.id)}
							<!-- Group Header Row -->
							<tr
								class="border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-850 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer transition"
								on:click={() => toggleGroup(group)}
							>
								<td class="py-3 px-4">
									<div class="flex items-center gap-2">
										{#if group.expanded}
											<ChevronDown className="size-4 text-gray-500" />
										{:else}
											<ChevronUp className="size-4 text-gray-500" />
										{/if}
										<span class="text-sm font-medium text-gray-900 dark:text-white">{group.name}</span>
									</div>
								</td>
								<td class="py-3 px-4 text-sm text-gray-900 dark:text-white">{group.prompts.length}</td>
								<td class="py-3 px-4">
									<div class="flex items-center gap-1">
										<span class="text-sm font-medium text-gray-900 dark:text-white">{group.avgVisibility}%</span>
										{#if group.visibilityTrend === 'up'}
											<svg class="size-3 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
												<path stroke-linecap="round" stroke-linejoin="round" d="M4.5 15.75l7.5-7.5 7.5 7.5" />
											</svg>
										{:else}
											<svg class="size-3 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
												<path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
											</svg>
										{/if}
									</div>
								</td>
								<td class="py-3 px-4">
									<div class="flex items-center gap-1">
										{#each group.topPerformers as performer}
											<div class="w-6 h-6 rounded-full bg-yellow-400 flex items-center justify-center text-xs font-bold text-gray-800">
												{getPerformerIcon(performer)}
											</div>
										{/each}
									</div>
								</td>
								<td class="py-3 px-4 text-sm text-gray-900 dark:text-white">{group.locationCount} locations</td>
								<td class="py-3 px-4 text-sm text-gray-900 dark:text-white">{group.region}</td>
								<td class="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">{dayjs(group.created).fromNow()}</td>
								<td class="py-3 px-4">
									{#if group.statusLink}
										<a
											href={group.statusLink}
											class="inline-flex items-center gap-1 text-sm text-blue-600 dark:text-blue-400 hover:underline"
											on:click|stopPropagation
										>
											See
											<Link className="size-3" />
										</a>
									{/if}
								</td>
							</tr>

							<!-- Child Rows -->
							{#if group.expanded}
								{#each group.prompts as prompt (prompt.id)}
									<tr
										class="border-b border-gray-100 dark:border-gray-700/50 hover:bg-gray-50 dark:hover:bg-gray-700/30 transition"
									>
										<td class="py-3 px-4 pl-12">
											<span class="text-sm text-gray-700 dark:text-gray-300">{prompt.topic}</span>
										</td>
										<td class="py-3 px-4"></td>
										<td class="py-3 px-4">
											<div class="flex items-center gap-1">
												<span class="text-sm font-medium text-gray-900 dark:text-white">{prompt.avgVisibility}%</span>
												{#if prompt.visibilityTrend === 'up'}
													<svg class="size-3 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
														<path stroke-linecap="round" stroke-linejoin="round" d="M4.5 15.75l7.5-7.5 7.5 7.5" />
													</svg>
												{:else}
													<svg class="size-3 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
														<path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
													</svg>
												{/if}
											</div>
										</td>
										<td class="py-3 px-4">
											<div class="flex items-center gap-1">
												{#each prompt.topPerformers as performer}
													<div class="w-6 h-6 rounded-full {performer === 'Z' ? 'bg-yellow-400' : 'bg-black'} flex items-center justify-center text-xs font-bold {performer === 'Z' ? 'text-gray-800' : 'text-white'}">
														{getPerformerIcon(performer)}
													</div>
												{/each}
											</div>
										</td>
										<td class="py-3 px-4">
											<div class="flex items-center gap-1.5">
												<span class="text-lg">{getFlagEmoji(prompt.locationCode)}</span>
												<span class="text-sm text-gray-900 dark:text-white">{prompt.location}</span>
											</div>
										</td>
										<td class="py-3 px-4 text-sm text-gray-900 dark:text-white">{prompt.region}</td>
										<td class="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">{dayjs(prompt.created).fromNow()}</td>
										<td class="py-3 px-4">
											{#if prompt.status === 'prompt-ran'}
												<button
													class="px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-xs font-medium rounded-lg"
												>
													Prompt Ran
												</button>
											{:else if prompt.status === 'pending'}
												<button
													class="px-3 py-1 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 text-xs font-medium rounded-lg"
												>
													Pending
												</button>
											{:else}
												<button
													class="px-3 py-1 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 text-xs font-medium rounded-lg"
												>
													Failed
												</button>
											{/if}
										</td>
									</tr>
								{/each}
							{/if}
						{/each}
					</tbody>
				</table>
			</div>

			<!-- Add Prompt Button -->
			<div class="border-t border-gray-200 dark:border-gray-700 px-4 py-4">
				<button
					class="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition"
				>
					<Plus className="size-4" />
					Add prompt
				</button>
			</div>
		</div>
	</div>
</div>
