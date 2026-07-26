<script lang="ts">
	import * as m from '$lib/paraglide/messages';
	import { getLocale, locales, setLocale } from '$lib/paraglide/runtime';

	const labels: Record<string, string> = {
		en: 'English',
		fr: 'Français'
	};

	let current = $derived(getLocale());
</script>

<div
	role="group"
	aria-label={m.profile_language()}
	class="inline-flex gap-1 rounded-md border border-gray-200 bg-gray-50 p-1 dark:border-gray-700 dark:bg-gray-800"
>
	{#each locales as locale (locale)}
		{@const active = locale === current}
		<button
			type="button"
			onclick={() => setLocale(locale)}
			aria-pressed={active}
			class="rounded px-3 py-1 text-sm font-medium transition-colors
				{active
				? 'bg-indigo-100 text-indigo-700 dark:bg-indigo-500/20 dark:text-indigo-300'
				: 'text-gray-500 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-100'}"
		>
			{labels[locale] ?? locale.toUpperCase()}
		</button>
	{/each}
</div>
