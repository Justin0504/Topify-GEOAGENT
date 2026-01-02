<script lang="ts">
	import { goto } from '$app/navigation';
	import { user } from '$lib/stores';
	import { onMount } from 'svelte';

	onMount(() => {
		// Redirect logic if user is not admin or lacks specific permissions
		if ($user?.role !== 'admin') {
			if ($user?.permissions?.workspace?.models) {
				goto('/workspace/models');
			} else if ($user?.permissions?.workspace?.knowledge) {
				goto('/workspace/knowledge');
			} else if ($user?.permissions?.workspace?.prompts) {
				goto('/workspace/prompts');
			} else if ($user?.permissions?.workspace?.tools) {
				goto('/workspace/tools');
			} else {
				goto('/');
			}
		} else {
			// Default redirect for admin or if no specific workspace permissions
			goto('/workspace/models');
		}
	});
</script>

<div class="flex h-full w-full items-center justify-center text-2xl text-gray-500">
	Topic Page Content (Redirecting...)
</div>

