import { goto } from '$app/navigation';
import { resolve } from '$app/paths';
import { env } from '$env/dynamic/public';
import { flash } from '$lib/stores/flash.svelte';

export const API_URL = env.PUBLIC_API_URL;

export async function apiFetch(path: string, init: RequestInit = {}): Promise<Response> {
	const res = await fetch(`${API_URL}${path}`, { ...init, credentials: 'include' });
	if (res.status === 401) {
		flash.set('Your session has expired. Please log in again.');
		goto(resolve('/'));
	}
	return res;
}
