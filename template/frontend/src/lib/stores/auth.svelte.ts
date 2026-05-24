import { getMe, logout as apiLogout, type User } from '$lib/api/auth';

function createAuthStore() {
	// undefined = not yet fetched, null = not logged in, User = logged in
	let user = $state<User | null | undefined>(undefined);

	return {
		get user() {
			return user;
		},
		async init() {
			if (user !== undefined) return;
			user = await getMe();
		},
		async logout() {
			await apiLogout();
			user = null;
		}
	};
}

export const auth = createAuthStore();
