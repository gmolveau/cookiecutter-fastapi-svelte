<script lang="ts">
	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import * as m from '$lib/paraglide/messages';

	let { children } = $props();

	const navLinks: { path: string; label: () => string }[] = [
		{ path: '/profile', label: m.profile_nav_general },
		{ path: '/profile/api-keys', label: m.profile_nav_api_keys }
	];
</script>

<div class="flex gap-8">
	<aside class="w-48 shrink-0">
		<nav class="flex flex-col gap-1">
			{#each navLinks as link (link.path)}
				{@const href = resolve(link.path as Parameters<typeof resolve>[0])}
				{@const active = page.url.pathname === href}
				<a
					{href}
					class="rounded-md px-3 py-2 text-sm font-medium transition-colors
						{active
						? 'bg-indigo-100 text-indigo-700 dark:bg-indigo-500/20 dark:text-indigo-300'
						: 'text-gray-500 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-100'}"
				>
					{link.label()}
				</a>
			{/each}
		</nav>
	</aside>
	<div class="min-w-0 flex-1">
		{@render children()}
	</div>
</div>
