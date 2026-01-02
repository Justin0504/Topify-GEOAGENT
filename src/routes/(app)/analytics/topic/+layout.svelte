<script lang="ts">
	import { getContext } from 'svelte';
	import { WEBUI_NAME } from '$lib/stores';

	const i18n = getContext('i18n');
</script>

<svelte:head>
	<title>
		Topic • {$WEBUI_NAME}
	</title>
</svelte:head>

<slot />

