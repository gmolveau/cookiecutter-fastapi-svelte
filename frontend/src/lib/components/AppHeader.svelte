<script lang="ts">
	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import { loginUrl } from '$lib/api/auth';
	import * as m from '$lib/paraglide/messages';
	import { auth } from '$lib/stores/auth.svelte';

	const adminHref = resolve('/admin' as Parameters<typeof resolve>[0]);
	const adminActive = $derived(page.url.pathname === adminHref);
</script>

<header class="border-b bg-white shadow-sm dark:border-gray-700 dark:bg-gray-800">
	<div class="mx-auto grid max-w-6xl grid-cols-3 items-center px-4 py-3">
		<div class="flex items-baseline gap-2">
			<a
				href={resolve('/')}
				class="text-xl font-bold tracking-tight text-indigo-700 dark:text-indigo-400">MyApp</a
			>
			<span class="text-xs text-gray-400 dark:text-gray-500">{__APP_VERSION__}</span>
		</div>

		<nav class="flex items-center justify-center gap-1">
			<a
				href={adminHref}
				class="rounded-md px-3 py-1.5 text-sm font-medium transition-colors
					{adminActive
					? 'bg-indigo-100 text-indigo-700 dark:bg-indigo-500/20 dark:text-indigo-300'
					: 'text-gray-500 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-100'}"
			>
				{m.nav_admin()}
			</a>
		</nav>

		<div class="flex items-center justify-end gap-4">
			{#if auth.user}
				<a
					href={resolve('/profile')}
					class="text-sm text-gray-700 hover:text-indigo-700 dark:text-gray-300 dark:hover:text-indigo-400"
				>
					{auth.user.name}
				</a>
			{:else if auth.user === null}
				<!-- eslint-disable svelte/no-navigation-without-resolve -->
				<a
					href={loginUrl('/')}
					class="text-sm text-indigo-600 hover:text-indigo-800 dark:text-indigo-400 dark:hover:text-indigo-300"
					>{m.nav_login()}</a
				>
				<!-- eslint-enable svelte/no-navigation-without-resolve -->
			{/if}
		</div>
	</div>
</header>
