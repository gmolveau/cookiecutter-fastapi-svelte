import { API_URL, apiFetch } from '$lib/api/client';

import { env } from '$env/dynamic/public';

export const BASE_URL = env.PUBLIC_BASE_URL;

export interface User {
	name: string;
	role: string | null;
}

export async function getMe(): Promise<User | null> {
	if (!document.cookie.split(';').some((c) => c.trim().startsWith('has_session='))) return null;
	try {
		const res = await apiFetch('/auth/me');
		if (!res.ok) return null;
		return await res.json();
	} catch {
		return null;
	}
}

export function loginUrl(path = '/'): string {
	return `${API_URL}/auth/login?next=${encodeURIComponent(BASE_URL + path)}`;
}

export async function logout(): Promise<void> {
	await apiFetch('/auth/logout', { method: 'GET' });
}
