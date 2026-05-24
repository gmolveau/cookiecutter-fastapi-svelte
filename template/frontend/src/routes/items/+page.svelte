<script lang="ts">
	import AppHeader from '$lib/components/AppHeader.svelte';
	import { fetchItems } from '$lib/api/items';
	import type { Item } from '$lib/types';

	let items = $state<Item[]>([]);
	let total = $state(0);
	let search = $state('');
	let loading = $state(true);
	let error = $state<string | null>(null);

	async function load(q = '') {
		loading = true;
		error = null;
		try {
			const result = await fetchItems(q || undefined);
			items = result.items;
			total = result.total;
		} catch (e) {
			error = String(e);
		} finally {
			loading = false;
		}
	}

	$effect(() => {
		load();
	});
</script>

<div class="min-h-screen bg-gray-50">
	<AppHeader />

	<main class="mx-auto max-w-4xl px-4 py-6">
		<div class="mb-6 flex items-center justify-between">
			<h2 class="text-2xl font-semibold text-gray-800">Items</h2>
			<span class="text-sm text-gray-500">{total} total</span>
		</div>

		<div class="mb-4">
			<input
				type="search"
				placeholder="Search..."
				bind:value={search}
				onchange={() => load(search)}
				class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
			/>
		</div>

		{#if loading}
			<p class="text-gray-400">Loading…</p>
		{:else if error}
			<p class="text-red-500">{error}</p>
		{:else if items.length === 0}
			<p class="text-gray-400">No items found.</p>
		{:else}
			<ul class="divide-y divide-gray-200 rounded-md bg-white shadow">
				{#each items as item (item.id)}
					<li class="px-4 py-3">
						<p class="font-medium text-gray-900">{item.name}</p>
						{#if item.description}
							<p class="mt-0.5 text-sm text-gray-500">{item.description}</p>
						{/if}
					</li>
				{/each}
			</ul>
		{/if}
	</main>
</div>
