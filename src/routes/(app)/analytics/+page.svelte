<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
</script>

<svelte:head>
	<title>Analytics • Topify.AI</title>
</svelte:head>

<div class="flex flex-col w-full h-screen max-h-[100dvh]">
	<div class="flex-1 overflow-y-auto p-6">
		<div class="max-w-7xl mx-auto">
			<h1 class="text-3xl font-bold mb-6 dark:text-white">Analytics</h1>
			
			<div class="bg-white dark:bg-gray-850 rounded-lg p-6 shadow-sm">
				<p class="text-gray-700 dark:text-gray-300">
					Analytics 板块内容。你可以在这里添加数据分析功能。
				</p>
			</div>
		</div>
	</div>
</div>

