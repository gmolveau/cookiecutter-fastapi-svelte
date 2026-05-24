<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	import AppHeader from '$lib/components/AppHeader.svelte';
	import { auth } from '$lib/stores/auth.svelte';
	import { flash } from '$lib/stores/flash.svelte';
	import { onMount } from 'svelte';

	let { children } = $props();

	onMount(() => auth.init());
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>

<div class="flex min-h-screen flex-col bg-gray-50">
	<AppHeader />
	{#if flash.message}
		<div
			class="border-b border-yellow-200 bg-yellow-50 px-4 py-3 text-center text-sm text-yellow-800"
		>
			{flash.message}
			<button onclick={() => flash.clear()} class="ml-3 font-medium underline">Dismiss</button>
		</div>
	{/if}
	<main class="mx-auto w-full max-w-4xl flex-1 px-4 py-12">
		{@render children()}
	</main>
</div>
