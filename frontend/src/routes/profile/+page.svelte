<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import LanguageSwitcher from '$lib/components/LanguageSwitcher.svelte';
	import ThemeSwitcher from '$lib/components/ThemeSwitcher.svelte';
	import * as m from '$lib/paraglide/messages';
	import { auth } from '$lib/stores/auth.svelte';

	let loggingOut = $state(false);

	async function handleLogout() {
		loggingOut = true;
		await auth.logout();
		goto(resolve('/'));
	}
</script>

<div class="max-w-sm">
	<h1 class="mb-6 text-2xl font-semibold text-gray-800 dark:text-gray-100">{m.profile_title()}</h1>

	{#if auth.user}
		<div
			class="rounded-lg border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800"
		>
			<dl class="space-y-4">
				<div>
					<dt class="text-xs font-medium tracking-wide text-gray-500 uppercase dark:text-gray-400">
						{m.profile_name()}
					</dt>
					<dd class="mt-1 text-sm text-gray-900 dark:text-gray-100">{auth.user.name}</dd>
				</div>
				{#if auth.user.role}
					<div>
						<dt
							class="text-xs font-medium tracking-wide text-gray-500 uppercase dark:text-gray-400"
						>
							{m.profile_role()}
						</dt>
						<dd class="mt-1 text-sm text-gray-900 dark:text-gray-100">{auth.user.role}</dd>
					</div>
				{/if}
				<div>
					<dt class="text-xs font-medium tracking-wide text-gray-500 uppercase dark:text-gray-400">
						{m.profile_language()}
					</dt>
					<dd class="mt-1">
						<LanguageSwitcher />
					</dd>
				</div>
				<div>
					<dt class="text-xs font-medium tracking-wide text-gray-500 uppercase dark:text-gray-400">
						{m.profile_theme()}
					</dt>
					<dd class="mt-1">
						<ThemeSwitcher />
					</dd>
				</div>
			</dl>

			<div class="mt-6 border-t border-gray-100 pt-4 dark:border-gray-700">
				<button
					onclick={handleLogout}
					disabled={loggingOut}
					class="rounded-md bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50"
				>
					{loggingOut ? m.profile_logging_out() : m.profile_logout()}
				</button>
			</div>
		</div>
	{:else if auth.user === null}
		<p class="text-sm text-gray-500 dark:text-gray-400">{m.profile_not_logged_in()}</p>
	{:else}
		<p class="text-sm text-gray-400 dark:text-gray-500">{m.common_loading()}</p>
	{/if}
</div>
