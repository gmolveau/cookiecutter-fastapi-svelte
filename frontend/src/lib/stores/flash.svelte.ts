function createFlashStore() {
	let message = $state<string | null>(null);

	return {
		get message() {
			return message;
		},
		set(msg: string) {
			message = msg;
		},
		clear() {
			message = null;
		}
	};
}

export const flash = createFlashStore();
