<script lang="ts">
	import { getContext } from 'svelte';
	import { WEBUI_NAME } from '$lib/stores';
	import { page } from '$app/stores';

	const i18n = getContext('i18n');
</script>

<svelte:head>
	<title>Action • {$WEBUI_NAME}</title>
</svelte:head>

<div class="flex flex-col w-full h-screen max-h-[100dvh]">
	<slot />
</div>

