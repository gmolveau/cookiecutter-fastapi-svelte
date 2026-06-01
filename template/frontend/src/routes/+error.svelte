<script lang="ts">
	import { page } from '$app/state';
</script>

<div class="text-center">
	<p class="text-6xl font-bold text-indigo-200">{page.status}</p>
	<h1 class="mt-4 text-2xl font-bold text-gray-900">
		{page.status === 404 ? 'Page introuvable' : 'Une erreur est survenue'}
	</h1>
	<p class="mt-3 text-gray-500">
		{page.status === 404
			? "Cette page n'existe pas ou a été déplacée."
			: 'Une erreur inattendue s\'est produite. Veuillez réessayer plus tard.'}
	</p>

	<div class="mt-8">
		<a
			href="/"
			class="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
		>
			Retour à l'accueil
		</a>
	</div>
</div>
