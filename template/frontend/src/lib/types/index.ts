export interface User {
	id: number;
	name: string;
	email: string;
}

export interface Item {
	id: number;
	name: string;
	description: string;
	created_at: string;
}

export interface ApiKey {
	id: number;
	name: string;
	key_prefix: string;
	created_at: string;
	expires_at: string | null;
	last_used_at: string | null;
}

export interface ApiKeyCreated extends ApiKey {
	key: string;
}
