import { env } from '$env/dynamic/public';

export const API_URL = env.PUBLIC_API_URL;

export async function apiFetch(path: string, init: RequestInit = {}): Promise<Response> {
	const res = await fetch(`${API_URL}${path}`, { ...init, credentials: 'include' });
	return res;
}
