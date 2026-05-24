<script lang="ts">
	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import { loginUrl } from '$lib/api/auth';
	import { auth } from '$lib/stores/auth.svelte';

	const navLinks: { path: string; label: string }[] = [{ path: '/admin', label: 'Admin' }];
</script>

<header class="border-b bg-white shadow-sm">
	<div class="mx-auto grid max-w-6xl grid-cols-3 items-center px-4 py-3">
		<div class="flex items-baseline gap-2">
			<a href={resolve('/')} class="text-xl font-bold tracking-tight text-indigo-700">My App</a>
			<span class="text-xs text-gray-400">{__APP_VERSION__}</span>
		</div>

		<nav class="flex items-center justify-center gap-1">
			{#each navLinks as link (link.path)}
				{@const href = resolve(link.path as Parameters<typeof resolve>[0])}
				{@const active = page.url.pathname === href}
				<a
					{href}
					class="rounded-md px-3 py-1.5 text-sm font-medium transition-colors
						{active ? 'bg-indigo-100 text-indigo-700' : 'text-gray-500 hover:bg-gray-100 hover:text-gray-900'}"
				>
					{link.label}
				</a>
			{/each}
		</nav>

		<div class="flex items-center justify-end gap-4">
			{#if auth.user}
				<span class="text-sm text-gray-700">{auth.user.name}</span>
			{:else if auth.user === null}
				<!-- eslint-disable-next-line svelte/no-navigation-without-resolve -->
				<a href={loginUrl('/')} class="text-sm text-indigo-600 hover:text-indigo-800">Login</a>
			{/if}
		</div>
	</div>
</header>
