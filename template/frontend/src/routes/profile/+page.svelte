<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { auth } from '$lib/stores/auth.svelte';

	let loggingOut = $state(false);

	async function handleLogout() {
		loggingOut = true;
		await auth.logout();
		goto(resolve('/'));
	}
</script>

<div class="mx-auto max-w-sm">
	<h1 class="mb-6 text-2xl font-semibold text-gray-800">Profil</h1>

	{#if auth.user}
		<div class="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
			<dl class="space-y-4">
				<div>
					<dt class="text-xs font-medium tracking-wide text-gray-500 uppercase">Nom</dt>
					<dd class="mt-1 text-sm text-gray-900">{auth.user.name}</dd>
				</div>
				{#if auth.user.role}
					<div>
						<dt class="text-xs font-medium tracking-wide text-gray-500 uppercase">Rôle</dt>
						<dd class="mt-1 text-sm text-gray-900">{auth.user.role}</dd>
					</div>
				{/if}
			</dl>

			<div class="mt-6 border-t border-gray-100 pt-4">
				<button
					onclick={handleLogout}
					disabled={loggingOut}
					class="rounded-md bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50"
				>
					{loggingOut ? 'Déconnexion…' : 'Se déconnecter'}
				</button>
			</div>
		</div>
	{:else if auth.user === null}
		<p class="text-sm text-gray-500">Vous n'êtes pas connecté.</p>
	{:else}
		<p class="text-sm text-gray-400">Chargement…</p>
	{/if}
</div>
