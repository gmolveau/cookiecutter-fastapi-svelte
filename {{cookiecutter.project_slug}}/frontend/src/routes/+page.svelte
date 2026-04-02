<script lang="ts">
	import AppHeader from '$lib/components/AppHeader.svelte';
	import { auth } from '$lib/stores/auth.svelte';
</script>

<div class="min-h-screen bg-gray-50">
	<AppHeader />

	<main class="mx-auto max-w-4xl px-4 py-12">
		<div class="text-center">
			<h1 class="text-4xl font-bold text-gray-900">My App</h1>
			<p class="mt-3 text-lg text-gray-500">Welcome. Edit this page to get started.</p>

			<div class="mt-8 flex justify-center gap-4">
				<a
					href="/items"
					class="rounded-md bg-indigo-600 px-6 py-3 text-sm font-semibold text-white shadow hover:bg-indigo-500"
				>
					Browse items
				</a>
				{#if auth.user}
					<a
						href="/items/new"
						class="rounded-md bg-white px-6 py-3 text-sm font-semibold text-gray-900 shadow ring-1 ring-gray-300 hover:bg-gray-50"
					>
						Create item
					</a>
				{/if}
			</div>
		</div>
	</main>
</div>
