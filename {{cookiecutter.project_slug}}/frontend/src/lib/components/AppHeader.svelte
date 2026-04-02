<script lang="ts">
	import { resolve } from '$app/paths';
	import { loginUrl } from '$lib/api/auth';
	import { auth } from '$lib/stores/auth.svelte';
</script>

<header class="border-b bg-white shadow-sm">
	<div class="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
		<div class="flex items-baseline gap-2">
			<a href={resolve('/')} class="text-xl font-bold tracking-tight text-indigo-700">My App</a>
			<span class="text-xs text-gray-400">{__APP_VERSION__}</span>
		</div>
		<nav class="flex items-center gap-4">
			<a href={resolve('/items')} class="text-sm text-gray-600 hover:text-indigo-600">Items</a>
			{#if auth.user}
				<span class="text-sm text-gray-700">{auth.user.name}</span>
			{:else if auth.user === null}
				<!-- eslint-disable-next-line svelte/no-navigation-without-resolve -->
				<a href={loginUrl('/')} class="text-sm text-indigo-600 hover:text-indigo-800">Login</a>
			{/if}
		</nav>
	</div>
</header>
