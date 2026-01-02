<script lang="ts">
	import { onMount } from 'svelte';
	import Download from '$lib/components/icons/Download.svelte';
	import Clipboard from '$lib/components/icons/Clipboard.svelte';
	import Document from '$lib/components/icons/Document.svelte';
	import ChevronDown from '$lib/components/icons/ChevronDown.svelte';
	import ChevronUp from '$lib/components/icons/ChevronUp.svelte';

	interface BlogSection {
		id: string;
		type: 'export' | 'copy' | 'status';
		title: string;
		expanded: boolean;
	}

	let sections: BlogSection[] = [
		{ id: 'export', type: 'export', title: 'Export', expanded: true },
		{ id: 'copy', type: 'copy', title: 'Copy', expanded: true },
		{ id: 'status', type: 'status', title: 'Status', expanded: true }
	];

	let blogContent = {
		title: 'Brex vs Ramp: 5 Key Differences in Credit Limits and Spend Control for 2025',
		paragraphs: [
			{
				id: 'p1',
				content:
					'Business credit cards have become essential tools for startups and growing companies seeking efficient spend management. Modern corporate cards offer advanced controls, real-time monitoring, and seamless integration with accounting systems. Understanding corporate card controls helps businesses mitigate fraud risk, ensure compliance, and optimize cash flow. As spend management evolves, features like automated expense categorization and policy enforcement are becoming standard.',
				selected: true,
				links: [{ text: 'with company_policies', href: '#' }]
			},
			{
				id: 'p2',
				content:
					'Corporate card controls are security features and restrictions that businesses implement to manage employee spending. These controls include spending limits, merchant category restrictions, and real-time transaction monitoring. By setting up proper controls, companies can monitor employee spending, ensure policy compliance, and reduce the risk of unauthorized transactions.',
				selected: false,
				links: [{ text: 'ensure policy compliance', href: '#' }]
			}
		],
		headings: [
			{ id: 'h1', text: 'Brex vs Ramp: 5 Key Differences in Credit Limits and Spend Control for 2025', level: 1 },
			{ id: 'h2', text: 'Understanding Corporate Card Spend Controls in 2025', level: 2 }
		]
	};

	let blogStatus = 'Draft';

	const toggleSection = (section: BlogSection) => {
		section.expanded = !section.expanded;
		sections = [...sections];
	};

	const handleExport = () => {
		console.log('Export blog');
		// Implement export functionality
	};

	const handleCopy = () => {
		const fullContent = `${blogContent.title}\n\n${blogContent.paragraphs.map((p) => p.content).join('\n\n')}`;
		navigator.clipboard.writeText(fullContent).then(() => {
			console.log('Content copied to clipboard');
		});
	};

	const renderParagraphWithLinks = (paragraph: typeof blogContent.paragraphs[0]) => {
		let content = paragraph.content;
		paragraph.links.forEach((link) => {
			content = content.replace(
				link.text,
				`<a href="${link.href}" class="text-blue-600 dark:text-blue-400 hover:underline">${link.text}</a>`
			);
		});
		return content;
	};
</script>

<div class="h-full w-full overflow-hidden bg-gray-50 dark:bg-gray-900 flex">
	<!-- Left Panel - Blog Actions -->
	<div class="w-80 flex flex-col border-r border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
		<div class="p-6 border-b border-gray-200 dark:border-gray-700">
			<h1 class="text-xl font-bold text-gray-900 dark:text-white mb-2">Blog Actions</h1>
			<p class="text-sm text-gray-600 dark:text-gray-400">
				Export, copy, or publish your blog content.
			</p>
		</div>

		<div class="flex-1 overflow-y-auto p-4 space-y-4">
			<!-- Export Section -->
			{#each sections as section (section.id)}
				{#if section.type === 'export'}
					<div class="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
						<button
							class="w-full flex items-center justify-between p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition"
							on:click={() => toggleSection(section)}
						>
							<span class="text-sm font-semibold text-gray-900 dark:text-white">{section.title}</span>
							{#if section.expanded}
								<ChevronUp className="size-4 text-gray-500" />
							{:else}
								<ChevronDown className="size-4 text-gray-500" />
							{/if}
						</button>
						{#if section.expanded}
							<div class="px-4 pb-4">
								<button
									class="w-full flex items-center gap-2 px-4 py-2.5 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition text-sm font-medium text-gray-900 dark:text-white"
									on:click={handleExport}
								>
									<Download className="size-4" />
									Export Blog
								</button>
							</div>
						{/if}
					</div>
				{/if}

				{#if section.type === 'copy'}
					<div class="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
						<button
							class="w-full flex items-center justify-between p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition"
							on:click={() => toggleSection(section)}
						>
							<span class="text-sm font-semibold text-gray-900 dark:text-white">{section.title}</span>
							{#if section.expanded}
								<ChevronUp className="size-4 text-gray-500" />
							{:else}
								<ChevronDown className="size-4 text-gray-500" />
							{/if}
						</button>
						{#if section.expanded}
							<div class="px-4 pb-4">
								<button
									class="w-full flex items-center gap-2 px-4 py-2.5 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition text-sm font-medium text-gray-900 dark:text-white"
									on:click={handleCopy}
								>
									<Clipboard className="size-4" />
									Copy Content
								</button>
							</div>
						{/if}
					</div>
				{/if}

				{#if section.type === 'status'}
					<div class="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
						<button
							class="w-full flex items-center justify-between p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition"
							on:click={() => toggleSection(section)}
						>
							<span class="text-sm font-semibold text-gray-900 dark:text-white">{section.title}</span>
							{#if section.expanded}
								<ChevronUp className="size-4 text-gray-500" />
							{:else}
								<ChevronDown className="size-4 text-gray-500" />
							{/if}
						</button>
						{#if section.expanded}
							<div class="px-4 pb-4">
								<button
									class="w-full flex items-center gap-2 px-4 py-2.5 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition text-sm font-medium text-gray-900 dark:text-white"
								>
									<Document className="size-4" />
									{blogStatus}
								</button>
							</div>
						{/if}
					</div>
				{/if}
			{/each}
		</div>
	</div>

	<!-- Right Panel - Blog Content Preview -->
	<div class="flex-1 flex flex-col bg-white dark:bg-gray-800 overflow-hidden">
		<div class="flex-1 overflow-y-auto p-12">
			<div class="max-w-4xl mx-auto">
				<!-- H1 Heading -->
				<div class="flex items-start gap-4 mb-6">
					<span class="text-xs text-gray-400 dark:text-gray-500 font-mono shrink-0 mt-2">h1</span>
					<h1 class="text-4xl font-bold text-gray-900 dark:text-white leading-tight">
						{blogContent.headings[0].text}
					</h1>
				</div>

				<!-- First Paragraph (Selected) -->
				<div class="flex items-start gap-4 mb-6">
					<span class="text-xs text-gray-400 dark:text-gray-500 font-mono shrink-0 mt-2">p</span>
					<div
						class="flex-1 p-4 border-2 border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-900/20 rounded-lg"
					>
						<p class="text-base text-gray-700 dark:text-gray-300 leading-relaxed">
							{@html renderParagraphWithLinks(blogContent.paragraphs[0])}
						</p>
					</div>
				</div>

				<!-- H2 Heading -->
				<div class="flex items-start gap-4 mb-6">
					<span class="text-xs text-gray-400 dark:text-gray-500 font-mono shrink-0 mt-2">h2</span>
					<h2 class="text-2xl font-bold text-gray-900 dark:text-white leading-tight">
						{blogContent.headings[1].text}
					</h2>
				</div>

				<!-- Second Paragraph -->
				<div class="flex items-start gap-4 mb-6">
					<span class="text-xs text-gray-400 dark:text-gray-500 font-mono shrink-0 mt-2">p</span>
					<div class="flex-1">
						<p class="text-base text-gray-700 dark:text-gray-300 leading-relaxed">
							{@html renderParagraphWithLinks(blogContent.paragraphs[1])}
						</p>
					</div>
				</div>
			</div>
		</div>
	</div>
</div>
