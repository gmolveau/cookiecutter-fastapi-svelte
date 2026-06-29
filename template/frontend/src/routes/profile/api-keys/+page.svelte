<script lang="ts">
	import { onMount } from 'svelte';
	import { createApiKey, deleteApiKey, listApiKeys } from '$lib/api/api-keys';
	import * as m from '$lib/paraglide/messages';
	import { getLocale } from '$lib/paraglide/runtime';
	import type { ApiKey, ApiKeyCreated } from '$lib/types';

	let keys = $state<ApiKey[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	let showCreateForm = $state(false);
	let newKeyName = $state('');
	let newKeyExpiresAt = $state('');
	let creating = $state(false);
	let createError = $state<string | null>(null);

	let revealedKey = $state<ApiKeyCreated | null>(null);
	let copied = $state(false);

	const ONE_YEAR_MS = 365 * 24 * 60 * 60 * 1000;
	const maxExpiryDate = new Date(Date.now() + ONE_YEAR_MS).toISOString().slice(0, 10);

	onMount(loadKeys);

	async function loadKeys() {
		loading = true;
		error = null;
		try {
			keys = await listApiKeys();
		} catch {
			error = m.api_keys_load_error();
		} finally {
			loading = false;
		}
	}

	async function handleCreate(event: SubmitEvent) {
		event.preventDefault();
		creating = true;
		createError = null;
		try {
			const expiresAt = newKeyExpiresAt ? `${newKeyExpiresAt}T00:00:00` : null;
			revealedKey = await createApiKey(newKeyName, expiresAt);
			newKeyName = '';
			newKeyExpiresAt = '';
			showCreateForm = false;
			await loadKeys();
		} catch (err) {
			createError = err instanceof Error ? err.message : m.api_keys_create_error();
		} finally {
			creating = false;
		}
	}

	async function handleRevoke(key: ApiKey) {
		if (!confirm(m.api_keys_revoke_confirm({ name: key.name }))) return;
		try {
			await deleteApiKey(key.id);
			await loadKeys();
		} catch {
			error = m.api_keys_revoke_error();
		}
	}

	async function copyKey() {
		if (!revealedKey) return;
		await navigator.clipboard.writeText(revealedKey.key);
		copied = true;
	}

	function closeReveal() {
		revealedKey = null;
		copied = false;
	}

	function isExpired(key: ApiKey): boolean {
		return key.expires_at !== null && new Date(key.expires_at) <= new Date();
	}

	function formatDate(value: string | null): string {
		if (!value) return '—';
		return new Date(value).toLocaleDateString(getLocale());
	}
</script>

<div>
	<div class="mb-6 flex items-center justify-between">
		<h1 class="text-2xl font-semibold text-gray-800">{m.profile_nav_api_keys()}</h1>
		<button
			onclick={() => (showCreateForm = !showCreateForm)}
			class="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
		>
			{m.api_keys_new()}
		</button>
	</div>

	<p class="mb-6 text-sm text-gray-500">
		{m.api_keys_description()}
	</p>

	{#if showCreateForm}
		<form
			onsubmit={handleCreate}
			class="mb-6 rounded-lg border border-gray-200 bg-white p-6 shadow-sm"
		>
			<div class="mb-4">
				<label for="key-name" class="mb-1 block text-sm font-medium text-gray-700"
					>{m.api_keys_name_label()}</label
				>
				<input
					id="key-name"
					type="text"
					required
					maxlength="255"
					bind:value={newKeyName}
					placeholder={m.api_keys_name_placeholder()}
					class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:ring-indigo-500 focus:outline-none"
				/>
			</div>
			<div class="mb-4">
				<label for="key-expiry" class="mb-1 block text-sm font-medium text-gray-700">
					{m.api_keys_expiry_label()}
				</label>
				<input
					id="key-expiry"
					type="date"
					bind:value={newKeyExpiresAt}
					max={maxExpiryDate}
					class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:ring-indigo-500 focus:outline-none"
				/>
				<p class="mt-1 text-xs text-gray-400">{m.api_keys_expiry_hint()}</p>
			</div>
			{#if createError}
				<p class="mb-4 text-sm text-red-600">{createError}</p>
			{/if}
			<div class="flex gap-2">
				<button
					type="submit"
					disabled={creating}
					class="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
				>
					{creating ? m.api_keys_creating() : m.api_keys_create()}
				</button>
				<button
					type="button"
					onclick={() => (showCreateForm = false)}
					class="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
				>
					{m.api_keys_cancel()}
				</button>
			</div>
		</form>
	{/if}

	{#if loading}
		<p class="text-sm text-gray-400">{m.common_loading()}</p>
	{:else if error}
		<p class="text-sm text-red-600">{error}</p>
	{:else if keys.length === 0}
		<p class="text-sm text-gray-500">{m.api_keys_empty()}</p>
	{:else}
		<div class="overflow-x-auto rounded-lg border border-gray-200 bg-white shadow-sm">
			<table class="w-full text-left text-sm">
				<thead class="border-b border-gray-200 text-xs tracking-wide text-gray-500 uppercase">
					<tr>
						<th class="px-4 py-3 font-medium">{m.api_keys_table_name()}</th>
						<th class="px-4 py-3 font-medium">{m.api_keys_table_key()}</th>
						<th class="px-4 py-3 font-medium">{m.api_keys_table_created()}</th>
						<th class="px-4 py-3 font-medium">{m.api_keys_table_expires()}</th>
						<th class="px-4 py-3 font-medium">{m.api_keys_table_last_used()}</th>
						<th class="px-4 py-3"><span class="sr-only">{m.api_keys_table_actions()}</span></th>
					</tr>
				</thead>
				<tbody class="divide-y divide-gray-100">
					{#each keys as key (key.id)}
						<tr>
							<td class="px-4 py-3 text-gray-900">{key.name}</td>
							<td class="px-4 py-3 font-mono text-xs text-gray-500">••••••••••••••••••••</td>
							<td class="px-4 py-3 text-gray-500">{formatDate(key.created_at)}</td>
							<td class="px-4 py-3 text-gray-500">
								{#if key.expires_at}
									{formatDate(key.expires_at)}
									{#if isExpired(key)}
										<span
											class="ml-1 rounded bg-red-100 px-1.5 py-0.5 text-xs font-medium text-red-700"
										>
											{m.api_keys_table_expired()}
										</span>
									{/if}
								{:else}
									{m.api_keys_no_expiry()}
								{/if}
							</td>
							<td class="px-4 py-3 text-gray-500">{formatDate(key.last_used_at)}</td>
							<td class="px-4 py-3 text-right">
								<button
									onclick={() => handleRevoke(key)}
									class="text-sm font-medium text-red-600 hover:text-red-700"
								>
									{m.api_keys_revoke()}
								</button>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>

{#if revealedKey}
	<div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
		<div class="w-full max-w-lg rounded-lg bg-white p-6 shadow-xl">
			<h2 class="mb-2 text-lg font-semibold text-gray-800">{m.api_keys_reveal_title()}</h2>
			<p class="mb-4 text-sm text-gray-600">
				{m.api_keys_reveal_description()}
			</p>
			<div class="mb-4 flex items-center gap-2">
				<code class="flex-1 overflow-x-auto rounded-md bg-gray-100 px-3 py-2 text-sm break-all">
					{revealedKey.key}
				</code>
				<button
					onclick={copyKey}
					class="shrink-0 rounded-md border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
				>
					{copied ? m.api_keys_copied() : m.api_keys_copy()}
				</button>
			</div>
			<div class="flex justify-end">
				<button
					onclick={closeReveal}
					class="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
				>
					{m.api_keys_close()}
				</button>
			</div>
		</div>
	</div>
{/if}
