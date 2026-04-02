<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	import { auth } from '$lib/stores/auth.svelte';
	import { onMount } from 'svelte';

	let { children } = $props();

	onMount(() => auth.init());
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>
{@render children()}
