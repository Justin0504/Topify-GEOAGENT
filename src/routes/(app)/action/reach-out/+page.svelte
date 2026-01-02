<script lang="ts">
	import { onMount } from 'svelte';
	import Search from '$lib/components/icons/Search.svelte';
	import GlobeAlt from '$lib/components/icons/GlobeAlt.svelte';
	import Link from '$lib/components/icons/Link.svelte';
	import Spinner from '$lib/components/common/Spinner.svelte';

	interface Contact {
		id: string;
		logo: string;
		domain: string;
		email: string;
		name: string;
		citations: number;
	}

	interface EmailData {
		referencedArticle: string;
		referencedArticleUrl: string;
		recipient: string;
		subjectLine: string;
		emailBody: string;
	}

	let searchQuery = '';
	let selectedContact: Contact | null = null;
	let processing = true;
	let totalSources = 100;
	let processedSources = 51;
	let contactsFound = 9;

	let contacts: Contact[] = [
		{
			id: '1',
			logo: 'P',
			domain: 'payhawk.com',
			email: 'trish.toovey@payhawk.com',
			name: 'Trish Toovey',
			citations: 48
		},
		{
			id: '2',
			logo: 'R',
			domain: 'ramp.com',
			email: 'amercieca@ramp.com',
			name: 'Ali Mercieca',
			citations: 26
		},
		{
			id: '3',
			logo: 'N',
			domain: 'navan.com',
			email: 'libbyzay@gmail.com',
			name: 'Libby Zay, Palma Colón',
			citations: 26
		},
		{
			id: '4',
			logo: 'N',
			domain: 'navan.com',
			email: 'ezay@navan.com',
			name: 'Libby Zay, Palma Colón',
			citations: 26
		},
		{
			id: '5',
			logo: 'T',
			domain: 'tech.co',
			email: 'contact@tech.co',
			name: 'Tech Co',
			citations: 22
		}
	];

	let emailData: EmailData = {
		referencedArticle: 'Best Business Expense Tracking Apps and Tools of 2025',
		referencedArticleUrl: '#',
		recipient: '',
		subjectLine: '',
		emailBody: ''
	};

	const selectContact = (contact: Contact) => {
		selectedContact = contact;
		emailData.recipient = contact.email;
		emailData.subjectLine = `Quick question about your article on ${emailData.referencedArticle}`;
		emailData.emailBody = `Hey ${contact.name.split(',')[0].split(' ')[0]}!

I'm Emily, Growth at Brex. Loved your blog and how it talks about the top expense tracking apps for 2025, especially highlighting ${contact.domain.split('.')[0]} as the best overall choice and providing a great comparison to other tools. I would love to schedule some time with you soon to discuss if you can feature us on your blog post or maybe collaborate on one together!

Best,`;
		emailData = { ...emailData };
	};

	const getLogoColor = (logo: string): string => {
		const colors: Record<string, string> = {
			P: 'bg-green-500',
			R: 'bg-yellow-400',
			N: 'bg-black',
			T: 'bg-blue-500'
		};
		return colors[logo] || 'bg-gray-400';
	};

	const getLogoTextColor = (logo: string): string => {
		return logo === 'N' ? 'text-white' : 'text-white';
	};

	// Simulate processing
	onMount(() => {
		setTimeout(() => {
			processing = false;
		}, 2000);
	});
</script>

<div class="h-full w-full overflow-hidden bg-gray-50 dark:bg-gray-900 flex">
	<!-- Left Panel - Contact Search and Results -->
	<div class="flex-1 flex flex-col border-r border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
		<!-- Search Bar -->
		<div class="p-4 border-b border-gray-200 dark:border-gray-700">
			<div class="relative">
				<Search className="absolute left-3 top-1/2 transform -translate-y-1/2 size-5 text-gray-400" />
				<input
					type="text"
					bind:value={searchQuery}
					placeholder="Search emails, authors, or companies..."
					class="w-full pl-10 pr-4 py-2.5 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
				/>
			</div>
		</div>

		<!-- Processing Status -->
		{#if processing}
			<div class="p-4 border-b border-gray-200 dark:border-gray-700">
				<div class="flex items-center gap-3">
					<Spinner className="size-5 text-blue-500" />
					<div class="flex-1">
						<div class="text-sm font-medium text-gray-900 dark:text-white">
							Finding contacts from your sources...
						</div>
						<div class="text-xs text-gray-500 dark:text-gray-400 mt-1">
							Processing {totalSources} sources • {processedSources} processed • {contactsFound} contacts found
						</div>
					</div>
				</div>
			</div>
		{/if}

		<!-- Contact List -->
		<div class="flex-1 overflow-y-auto p-4 space-y-3">
			{#each contacts as contact (contact.id)}
				<div
					class="p-4 border border-gray-200 dark:border-gray-700 rounded-lg cursor-pointer hover:border-blue-500 dark:hover:border-blue-500 hover:shadow-md transition {selectedContact?.id === contact.id
						? 'border-blue-500 dark:border-blue-500 bg-blue-50 dark:bg-blue-900/20'
						: 'bg-white dark:bg-gray-800'}"
					on:click={() => selectContact(contact)}
				>
					<div class="flex items-start gap-4">
						<!-- Logo -->
						<div
							class="w-12 h-12 rounded-lg {getLogoColor(contact.logo)} flex items-center justify-center shrink-0 {getLogoTextColor(contact.logo)} font-bold text-lg"
						>
							{contact.logo}
						</div>

						<!-- Contact Info -->
						<div class="flex-1 min-w-0">
							<div class="text-sm font-medium text-gray-900 dark:text-white truncate">
								{contact.domain}
							</div>
							<div class="text-sm text-gray-600 dark:text-gray-400 mt-1 truncate">
								{contact.email}
							</div>
							<div class="text-sm text-gray-900 dark:text-white font-medium mt-1">
								{contact.name}
							</div>
							<div class="text-xs text-gray-500 dark:text-gray-400 mt-1">
								{contact.citations} citations
							</div>
						</div>
					</div>
				</div>
			{/each}
		</div>
	</div>

	<!-- Right Panel - Email Composition -->
	<div class="w-[500px] flex flex-col bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700">
		<div class="flex-1 overflow-y-auto p-6 space-y-6">
			<!-- Referenced Article -->
			<div>
				<div class="flex items-center gap-2 mb-3">
					<GlobeAlt className="size-4 text-gray-600 dark:text-gray-400" />
					<label class="text-sm font-medium text-gray-700 dark:text-gray-300">Referenced Article</label>
				</div>
				<a
					href={emailData.referencedArticleUrl}
					target="_blank"
					rel="noopener noreferrer"
					class="inline-flex items-center gap-1.5 text-blue-600 dark:text-blue-400 hover:underline text-sm"
				>
					{emailData.referencedArticle}
					<Link className="size-3" />
				</a>
			</div>

			<!-- Recipient -->
			<div>
				<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
					Recipient
				</label>
				<input
					type="email"
					bind:value={emailData.recipient}
					placeholder="Enter email address"
					class="w-full px-4 py-2.5 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
				/>
			</div>

			<!-- Subject Line -->
			<div>
				<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
					Subject Line
				</label>
				<input
					type="text"
					bind:value={emailData.subjectLine}
					placeholder="Enter subject line"
					class="w-full px-4 py-2.5 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
				/>
			</div>

			<!-- Email Body -->
			<div class="flex-1">
				<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
					Email Body
				</label>
				<textarea
					bind:value={emailData.emailBody}
					placeholder="Enter email body"
					rows="12"
					class="w-full px-4 py-3 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none font-mono text-sm"
				></textarea>
			</div>
		</div>

		<!-- Action Buttons -->
		<div class="border-t border-gray-200 dark:border-gray-700 p-4 flex gap-3">
			<button
				class="flex-1 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition"
			>
				Send Email
			</button>
			<button
				class="px-4 py-2.5 border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 font-medium rounded-lg transition"
			>
				Save Draft
			</button>
		</div>
	</div>
</div>
