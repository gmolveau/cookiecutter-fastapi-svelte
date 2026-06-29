const STORAGE_KEY = 'theme';

export type Theme = 'light' | 'dark';

function apply(value: Theme) {
	document.documentElement.classList.toggle('dark', value === 'dark');
}

function createThemeStore() {
	let theme = $state<Theme>('light');

	return {
		get theme() {
			return theme;
		},
		init() {
			theme = localStorage.getItem(STORAGE_KEY) === 'dark' ? 'dark' : 'light';
			apply(theme);
		},
		set(value: Theme) {
			theme = value;
			localStorage.setItem(STORAGE_KEY, value);
			apply(value);
		}
	};
}

export const theme = createThemeStore();
