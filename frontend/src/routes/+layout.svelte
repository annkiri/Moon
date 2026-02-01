<script lang="ts">
	import '../app.css';
	
	let { children } = $props();
</script>

<svelte:head>
	<title>Moon AI</title>
	<meta name="description" content="Tu asistente personal con memoria" />
</svelte:head>

<div class="app">
	{@render children()}
</div>

<style>
	.app {
		display: flex;
		flex-direction: column;
		min-height: 100vh;
		min-height: 100dvh; /* Dynamic viewport height for mobile */
		background-color: var(--bg-primary);
	}
</style>
