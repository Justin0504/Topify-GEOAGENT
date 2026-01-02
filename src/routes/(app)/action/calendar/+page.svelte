<script lang="ts">
	import { onMount } from 'svelte';
	import * as XLSX from 'xlsx';
	import ChevronDown from '$lib/components/icons/ChevronDown.svelte';
	import ChevronUp from '$lib/components/icons/ChevronUp.svelte';
	import CheckCircle from '$lib/components/icons/CheckCircle.svelte';
	import Calendar from '$lib/components/icons/Calendar.svelte';
	import DocumentArrowUp from '$lib/components/icons/DocumentArrowUp.svelte';
	import GarbageBin from '$lib/components/icons/GarbageBin.svelte';
	import Spinner from '$lib/components/common/Spinner.svelte';
	import dayjs from '$lib/dayjs';

	interface Article {
		id: string;
		title: string;
		completed: boolean;
	}

	interface DayData {
		date: Date;
		expanded: boolean;
		articles: Article[];
	}

	// Generate calendar for the next 30 days
	let calendarDays: DayData[] = [];
	let fileInput: HTMLInputElement;
	let importing = false;
	let importError = '';
	let importSuccess = false;
	let clearSuccess = false;
	let clearing = false;

	onMount(() => {
		initializeCalendar();
		// Check for pending import data
		checkAndImportFromStorage();
		
		// Listen for custom event when import data is ready
		const handleImportReady = (e: CustomEvent) => {
			try {
				const importData = e.detail;
				localStorage.removeItem('calendar_pending_import');
				importFromJsonData(importData);
			} catch (error) {
				console.error('Failed to import from custom event:', error);
			}
		};
		
		// Listen for storage events (when data is saved from another tab/window)
		const handleStorageChange = (e: StorageEvent) => {
			if (e.key === 'calendar_pending_import' && e.newValue) {
				try {
					const importData = JSON.parse(e.newValue);
					localStorage.removeItem('calendar_pending_import');
					importFromJsonData(importData);
				} catch (error) {
					console.error('Failed to import from storage event:', error);
				}
			}
		};
		
		window.addEventListener('calendar-import-ready', handleImportReady as EventListener);
		window.addEventListener('storage', handleStorageChange);
		
		// Also check periodically for new import data (for same-tab updates)
		const checkInterval = setInterval(() => {
			checkAndImportFromStorage();
		}, 2000); // Check every 2 seconds
		
		return () => {
			window.removeEventListener('calendar-import-ready', handleImportReady as EventListener);
			window.removeEventListener('storage', handleStorageChange);
			clearInterval(checkInterval);
		};
	});

	const initializeCalendar = () => {
		// Try to load from localStorage first
		try {
			const savedData = localStorage.getItem('calendar_data');
			if (savedData) {
				const parsed = JSON.parse(savedData);
				// Convert date strings back to Date objects
				calendarDays = parsed.map((day: any) => ({
					...day,
					date: new Date(day.date)
				}));
				console.log('📂 [Calendar] 从 localStorage 恢复日历数据', calendarDays.length, '天');
				return;
			}
		} catch (error) {
			console.error('Failed to load calendar data from localStorage:', error);
		}

		// Fallback to default sample data
		const today = new Date();
		const days: DayData[] = [];

		// Sample data - in production, fetch from API
		const sampleArticles: Record<number, Article[]> = {
			0: [
				{ id: '1', title: 'Top 10 Business Credit Cards for Startups in 2025', completed: true },
				{ id: '2', title: 'Understanding Corporate Card Spend Controls', completed: true }
			],
			2: [
				{ id: '3', title: 'Best Expense Management Tools for SMEs', completed: false },
				{ id: '4', title: 'How to Optimize Cash Flow with Corporate Cards', completed: false }
			],
			5: [
				{ id: '5', title: 'Comparing Brex vs Ramp: Which is Better?', completed: true }
			],
			7: [
				{ id: '6', title: 'The Future of Business Expense Tracking', completed: false },
				{ id: '7', title: 'Compliance and Security in Corporate Cards', completed: false }
			],
			14: [
				{ id: '8', title: 'Guide to Business Credit Card Rewards', completed: false }
			]
		};

		for (let i = 0; i < 30; i++) {
			const date = new Date(today);
			date.setDate(today.getDate() + i);
			days.push({
				date,
				expanded: i === 0, // Expand today by default
				articles: sampleArticles[i] || []
			});
		}

		calendarDays = days;
		saveCalendarToStorage();
	};

	// Save calendar data to localStorage
	const saveCalendarToStorage = () => {
		try {
			const dataToSave = calendarDays.map((day) => ({
				...day,
				date: day.date.toISOString() // Convert Date to string for JSON serialization
			}));
			localStorage.setItem('calendar_data', JSON.stringify(dataToSave));
		} catch (error) {
			console.error('Failed to save calendar data to localStorage:', error);
		}
	};

	const toggleDay = (day: DayData) => {
		day.expanded = !day.expanded;
		calendarDays = [...calendarDays];
		saveCalendarToStorage();
	};

	const formatDate = (date: Date): string => {
		return dayjs(date).format('MMMM D, YYYY');
	};

	const formatDayOfWeek = (date: Date): string => {
		return dayjs(date).format('dddd');
	};

	const isToday = (date: Date): boolean => {
		const today = new Date();
		return (
			date.getDate() === today.getDate() &&
			date.getMonth() === today.getMonth() &&
			date.getFullYear() === today.getFullYear()
		);
	};

	const handleFileSelect = async (event: Event) => {
		const target = event.target as HTMLInputElement;
		const file = target.files?.[0];

		if (!file) return;

		// Check if file is Excel
		const isExcel =
			file.name.endsWith('.xlsx') ||
			file.name.endsWith('.xls') ||
			file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
			file.type === 'application/vnd.ms-excel';

		if (!isExcel) {
			importError = 'Please select an Excel file (.xlsx or .xls)';
			setTimeout(() => {
				importError = '';
			}, 5000);
			return;
		}

		await importFromExcel(file);
	};

	const importFromExcel = async (file: File) => {
		importing = true;
		importError = '';
		importSuccess = false;

		try {
			const arrayBuffer = await file.arrayBuffer();
			const workbook = XLSX.read(arrayBuffer, { type: 'array' });

			// Find the "内容发布计划" sheet (main worksheet) or use first sheet
			let worksheet = workbook.Sheets['内容发布计划'];
			if (!worksheet) {
				// Fallback: use first sheet if "内容发布计划" not found
				const firstSheetName = workbook.SheetNames[0];
				worksheet = workbook.Sheets[firstSheetName];
			}

			if (!worksheet) {
				throw new Error('Unable to find worksheet');
			}

			// Convert sheet to JSON
			const data = XLSX.utils.sheet_to_json(worksheet, { header: 1, defval: '' });

			if (data.length < 2) {
				throw new Error('Excel file is empty or format is incorrect');
			}

			// Parse header row (assuming first row is headers)
			const headers = data[0] as string[];
			const dateColIndex = headers.findIndex((h) =>
				['发布日期', '日期', 'Date', 'Publish Date'].includes(String(h))
			);
			const titleColIndex = headers.findIndex((h) =>
				['文章标题', '标题', 'Title', 'Article Title'].includes(String(h))
			);
			const statusColIndex = headers.findIndex((h) =>
				['状态', 'Status', '完成状态'].includes(String(h))
			);
			const idColIndex = headers.findIndex((h) =>
				['编号', 'ID', '编号', 'Article ID'].includes(String(h))
			);

			if (dateColIndex === -1 || titleColIndex === -1) {
				throw new Error('Excel file is missing required columns: Publish Date and Article Title');
			}

			// Parse articles from rows
			const articlesByDate: Map<string, Article[]> = new Map();
			let articleCount = 0;

			for (let i = 1; i < data.length; i++) {
				const row = data[i] as any[];
				const dateStr = row[dateColIndex];
				const title = row[titleColIndex];
				const status = statusColIndex >= 0 ? row[statusColIndex] : '';
				const id = idColIndex >= 0 ? row[idColIndex] : `imported-${i}`;

				// Skip empty rows
				if (!dateStr || !title) continue;

				// Parse date
				let publishDate: Date;
				if (typeof dateStr === 'number') {
					// Excel serial date number (days since 1900-01-01)
					// Excel's epoch is 1899-12-30, but JavaScript Date uses 1970-01-01
					const excelEpoch = new Date(1899, 11, 30); // December 30, 1899
					publishDate = new Date(excelEpoch.getTime() + dateStr * 86400000);
				} else if (dateStr instanceof Date) {
					publishDate = dateStr;
				} else {
					// String date, try parsing
					const parsed = dayjs(dateStr.toString());
					if (!parsed.isValid()) {
						console.warn(`Unable to parse date: ${dateStr}, skipping row`);
						continue;
					}
					publishDate = parsed.toDate();
				}

				// Determine completion status
				const completed =
					statusColIndex >= 0 &&
					(['已完成', '完成', 'Completed', 'Done', '已发布', 'Published'].includes(
						String(status).trim()
					) ||
						String(status).includes('完成'));

				const article: Article = {
					id: String(id) || `article-${articleCount++}`,
					title: String(title).trim(),
					completed
				};

				// Group by date (YYYY-MM-DD)
				const dateKey = dayjs(publishDate).format('YYYY-MM-DD');
				if (!articlesByDate.has(dateKey)) {
					articlesByDate.set(dateKey, []);
				}
				articlesByDate.get(dateKey)!.push(article);
			}

			// Update calendar days - Replace existing data instead of merging
			const today = new Date();
			const updatedDays: DayData[] = [];

			for (let i = 0; i < 30; i++) {
				const date = new Date(today);
				date.setDate(today.getDate() + i);
				const dateKey = dayjs(date).format('YYYY-MM-DD');
				const importedArticles = articlesByDate.get(dateKey) || [];

				// Find existing day or create new one
				const existingDay = calendarDays.find(
					(d) => dayjs(d.date).format('YYYY-MM-DD') === dateKey
				);

				// Replace with imported articles (overwrite instead of merge)
				updatedDays.push({
					date,
					expanded: existingDay?.expanded ?? i === 0,
					articles: importedArticles
				});
			}

			calendarDays = updatedDays;
			saveCalendarToStorage(); // Save after Excel import
			importSuccess = true;
			const totalArticles = Array.from(articlesByDate.values()).reduce(
				(sum, articles) => sum + articles.length,
				0
			);

			setTimeout(() => {
				importSuccess = false;
			}, 5000);
		} catch (error) {
			console.error('Failed to import Excel file:', error);
			importError = error instanceof Error ? error.message : 'Import failed, please check file format';
			setTimeout(() => {
				importError = '';
			}, 8000);
		} finally {
			importing = false;
			// Reset file input
			if (fileInput) {
				fileInput.value = '';
			}
		}
	};

	const triggerFileInput = () => {
		fileInput?.click();
	};

	// Check localStorage for pending import data
	const checkAndImportFromStorage = () => {
		try {
			const storedData = localStorage.getItem('calendar_pending_import');
			if (storedData) {
				const importData = JSON.parse(storedData);
				console.log('📥 [Calendar] 从 localStorage 读取到导入数据', importData);
				// Clear the read data
				localStorage.removeItem('calendar_pending_import');
				// Auto import
				importFromJsonData(importData);
			} else {
				console.log('📭 [Calendar] localStorage 中没有待导入的数据');
			}
		} catch (error) {
			console.error('Failed to check localStorage data:', error);
		}
	};

	// Import from JSON data
	const importFromJsonData = (data: any) => {
		if (!data || !data.articles || !Array.isArray(data.articles)) {
			return;
		}

		importing = true;
		importError = '';
		importSuccess = false;

		try {
			const articlesByDate: Map<string, Article[]> = new Map();

			for (const article of data.articles) {
				if (!article.publish_date || !article.title) continue;

				// Parse date
				const publishDate = dayjs(article.publish_date);
				if (!publishDate.isValid()) {
					console.warn(`Unable to parse date: ${article.publish_date}, skipping article`);
					continue;
				}

				const articleData: Article = {
					id: article.id || `article-${Date.now()}-${Math.random()}`,
					title: String(article.title).trim(),
					completed: article.completed || false
				};

				// Group by date
				const dateKey = publishDate.format('YYYY-MM-DD');
				if (!articlesByDate.has(dateKey)) {
					articlesByDate.set(dateKey, []);
				}
				articlesByDate.get(dateKey)!.push(articleData);
			}

			// Update calendar - Replace existing data instead of merging
			const today = new Date();
			const updatedDays: DayData[] = [];

			for (let i = 0; i < 30; i++) {
				const date = new Date(today);
				date.setDate(today.getDate() + i);
				const dateKey = dayjs(date).format('YYYY-MM-DD');
				const importedArticles = articlesByDate.get(dateKey) || [];

				// Find existing day or create new one
				const existingDay = calendarDays.find(
					(d) => dayjs(d.date).format('YYYY-MM-DD') === dateKey
				);

				// Replace with imported articles (overwrite instead of merge)
				updatedDays.push({
					date,
					expanded: existingDay?.expanded ?? i === 0,
					articles: importedArticles
				});
			}

			calendarDays = updatedDays;
			saveCalendarToStorage(); // Save after import
			importSuccess = true;
			const totalArticles = Array.from(articlesByDate.values()).reduce(
				(sum, articles) => sum + articles.length,
				0
			);

			setTimeout(() => {
				importSuccess = false;
			}, 5000);
		} catch (error) {
			console.error('Failed to import from JSON:', error);
			importError = error instanceof Error ? error.message : 'Import failed';
			setTimeout(() => {
				importError = '';
			}, 8000);
		} finally {
			importing = false;
		}
	};

	// Clear all calendar data
	const clearCalendar = () => {
		if (!confirm('Are you sure you want to clear all calendar data? This action cannot be undone.')) {
			return;
		}

		clearing = true;
		
		// Initialize empty calendar
		const today = new Date();
		const emptyDays: DayData[] = [];

		for (let i = 0; i < 30; i++) {
			const date = new Date(today);
			date.setDate(today.getDate() + i);
			emptyDays.push({
				date,
				expanded: i === 0,
				articles: []
			});
		}

		calendarDays = emptyDays;
		saveCalendarToStorage(); // Save after clearing
		clearSuccess = true;
		clearing = false;
		
		setTimeout(() => {
			clearSuccess = false;
		}, 3000);
	};
</script>

<div class="h-full w-full overflow-auto bg-gray-50 dark:bg-gray-900">
	<div class="max-w-4xl mx-auto px-6 py-8">
		<!-- Header -->
		<div class="mb-8">
			<div class="flex items-center justify-between mb-2">
				<div class="flex items-center gap-3">
					<Calendar className="size-6 text-gray-700 dark:text-gray-300" />
					<h1 class="text-3xl font-bold text-gray-900 dark:text-white">Calendar</h1>
				</div>
				<div class="flex items-center gap-2">
					<button
						on:click={clearCalendar}
						disabled={clearing || importing}
						class="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-lg transition text-sm font-medium"
					>
						{#if clearing}
							<Spinner className="size-4" />
							<span>Clearing...</span>
						{:else}
							<GarbageBin className="size-5" />
							<span>Clear All</span>
						{/if}
					</button>
					<button
						on:click={triggerFileInput}
						disabled={importing || clearing}
						class="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-lg transition text-sm font-medium"
					>
						{#if importing}
							<Spinner className="size-4" />
							<span>Importing...</span>
						{:else}
							<DocumentArrowUp className="size-5" />
							<span>Import Excel</span>
						{/if}
					</button>
				</div>
			</div>
			<p class="text-sm text-gray-600 dark:text-gray-400">
				Manage your content publishing schedule
			</p>

			<!-- Hidden file input -->
			<input
				bind:this={fileInput}
				type="file"
				accept=".xlsx,.xls,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel"
				class="hidden"
				on:change={handleFileSelect}
			/>

			<!-- Import Status Messages -->
			{#if importError}
				<div
					class="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400 text-sm"
				>
					❌ {importError}
				</div>
			{/if}

			{#if importSuccess}
				<div
					class="mt-4 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg text-green-700 dark:text-green-400 text-sm"
				>
					✅ Excel file imported successfully! Calendar has been updated with new schedule.
				</div>
			{/if}

			{#if clearSuccess}
				<div
					class="mt-4 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg text-green-700 dark:text-green-400 text-sm"
				>
					✅ Calendar cleared successfully! All schedule data has been removed.
				</div>
			{/if}
		</div>

		<!-- Calendar Days -->
		<div class="space-y-2">
			{#each calendarDays as day (day.date.getTime())}
				<div
					class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden {isToday(day.date)
						? 'ring-2 ring-blue-500'
						: ''}"
				>
					<!-- Day Header -->
					<button
						class="w-full flex items-center justify-between p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition"
						on:click={() => toggleDay(day)}
					>
						<div class="flex items-center gap-4 flex-1">
							<div class="text-left min-w-[120px]">
								<div
									class="text-sm font-medium {isToday(day.date)
										? 'text-blue-600 dark:text-blue-400'
										: 'text-gray-600 dark:text-gray-400'}"
								>
									{formatDayOfWeek(day.date)}
								</div>
								<div
									class="text-lg font-semibold {isToday(day.date)
										? 'text-blue-600 dark:text-blue-400'
										: 'text-gray-900 dark:text-white'}"
								>
									{formatDate(day.date)}
								</div>
							</div>
							<div class="flex-1">
								{#if day.articles.length > 0}
									<span class="text-sm text-gray-500 dark:text-gray-400">
										{day.articles.length} article{day.articles.length > 1 ? 's' : ''}
									</span>
								{:else}
									<span class="text-sm text-gray-400 dark:text-gray-500">No articles</span>
								{/if}
							</div>
						</div>
						<div class="flex items-center gap-3">
							{#if day.expanded}
								<ChevronUp className="size-5 text-gray-400" />
							{:else}
								<ChevronDown className="size-5 text-gray-400" />
							{/if}
						</div>
					</button>

					<!-- Articles List -->
					{#if day.expanded && day.articles.length > 0}
						<div class="border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-850">
							<div class="p-4 space-y-3">
								{#each day.articles as article (article.id)}
									<div
										class="flex items-center justify-between gap-4 p-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-300 dark:hover:border-blue-700 transition cursor-pointer"
									>
										<div class="flex-1 min-w-0">
											<h3
												class="text-sm font-medium truncate {article.completed
													? 'line-through text-gray-500 dark:text-gray-400'
													: 'text-gray-900 dark:text-white'}"
											>
												{article.title}
											</h3>
										</div>
										<div class="shrink-0 flex items-center">
											{#if article.completed}
												<CheckCircle className="size-5 text-green-500" />
											{:else}
												<div class="size-5 rounded-full border-2 border-gray-300 dark:border-gray-600 flex items-center justify-center">
													<div class="size-2.5 rounded-full bg-transparent"></div>
												</div>
											{/if}
										</div>
									</div>
								{/each}
							</div>
						</div>
					{/if}
				</div>
			{/each}
		</div>
	</div>
</div>
