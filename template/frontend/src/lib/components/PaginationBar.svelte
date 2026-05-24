<script lang="ts">
	interface Props {
		page: number;
		totalPages: number;
		ongotoPage: (p: number) => void;
	}

	let { page, totalPages, ongotoPage }: Props = $props();

	const pageWindow = $derived((): (number | '…')[] => {
		if (totalPages <= 7) return Array.from({ length: totalPages }, (_, i) => i);
		const pages: (number | '…')[] = [];
		const addPage = (i: number) => {
			if (pages.at(-1) !== i) pages.push(i);
		};
		addPage(0);
		if (page > 3) pages.push('…');
		for (let i = Math.max(1, page - 2); i <= Math.min(totalPages - 2, page + 2); i++) addPage(i);
		if (page < totalPages - 4) pages.push('…');
		addPage(totalPages - 1);
		return pages;
	});
</script>

{#if totalPages > 1}
	<div class="mt-8 flex flex-wrap items-center justify-center gap-1">
		<button
			onclick={() => ongotoPage(page - 1)}
			disabled={page === 0}
			class="rounded border border-gray-300 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-50 disabled:opacity-40"
		>
			← Prev
		</button>

		{#each pageWindow() as p, i (i)}
			{#if p === '…'}
				<span class="px-1 text-sm text-gray-400">…</span>
			{:else}
				<button
					onclick={() => ongotoPage(p)}
					class="rounded border px-3 py-1.5 text-sm {p === page
						? 'border-indigo-500 bg-indigo-600 text-white'
						: 'border-gray-300 text-gray-600 hover:bg-gray-50'}"
				>
					{p + 1}
				</button>
			{/if}
		{/each}

		<button
			onclick={() => ongotoPage(page + 1)}
			disabled={page >= totalPages - 1}
			class="rounded border border-gray-300 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-50 disabled:opacity-40"
		>
			Next →
		</button>
	</div>
{/if}
