import { apiFetch } from '$lib/api/client';
import type { ApiKey, ApiKeyCreated } from '$lib/types';

export async function listApiKeys(): Promise<ApiKey[]> {
	const res = await apiFetch('/api-keys');
	if (!res.ok) throw new Error('Failed to load API keys');
	const data: { api_keys: ApiKey[] } = await res.json();
	return data.api_keys;
}

export async function createApiKey(name: string, expiresAt: string | null): Promise<ApiKeyCreated> {
	const res = await apiFetch('/api-keys', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ name, expires_at: expiresAt })
	});
	if (!res.ok) {
		const data = await res.json().catch(() => null);
		throw new Error(data?.detail ?? 'Failed to create API key');
	}
	return res.json();
}

export async function deleteApiKey(id: number): Promise<void> {
	const res = await apiFetch(`/api-keys/${id}`, { method: 'DELETE' });
	if (!res.ok) throw new Error('Failed to delete API key');
}
