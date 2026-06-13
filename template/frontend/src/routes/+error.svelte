<script lang="ts">
	import { resolve } from '$app/paths';
	import { page } from '$app/state';
	import * as m from '$lib/paraglide/messages';
</script>

<div class="text-center">
	<p class="text-6xl font-bold text-indigo-200">{page.status}</p>
	<h1 class="mt-4 text-2xl font-bold text-gray-900">
		{page.status === 404 ? m.error_404_title() : m.error_generic_title()}
	</h1>
	<p class="mt-3 text-gray-500">
		{page.status === 404 ? m.error_404_body() : m.error_generic_body()}
	</p>

	<div class="mt-8">
		<a
			href={resolve('/')}
			class="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
		>
			{m.error_back_home()}
		</a>
	</div>
</div>
