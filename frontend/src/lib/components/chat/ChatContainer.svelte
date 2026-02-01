<script lang="ts">
	import MessageBubble from './MessageBubble.svelte';
	import type { Message } from './MessageBubble.svelte';
	
	let { messages }: { messages: Message[] } = $props();
	
	let containerRef: HTMLDivElement;
	
	// Auto-scroll to bottom when new messages arrive
	$effect(() => {
		if (messages.length && containerRef) {
			requestAnimationFrame(() => {
				containerRef.scrollTo({
					top: containerRef.scrollHeight,
					behavior: 'smooth'
				});
			});
		}
	});
</script>

<div class="chat-container" bind:this={containerRef}>
	{#if messages.length === 0}
		<div class="empty-state">
			<div class="moon-icon">🌙</div>
			<h2>Hola, soy Moon</h2>
			<p>Tu asistente personal con memoria</p>
		</div>
	{:else}
		<div class="messages">
			{#each messages as message (message.id)}
				<MessageBubble {message} />
			{/each}
		</div>
	{/if}
</div>

<style>
	.chat-container {
		flex: 1;
		overflow-y: auto;
		overflow-x: hidden;
		-webkit-overflow-scrolling: touch;
		scroll-behavior: smooth;
	}
	
	.messages {
		display: flex;
		flex-direction: column;
		padding: 1rem 0;
		min-height: 100%;
	}
	
	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 100%;
		padding: 2rem;
		text-align: center;
		color: var(--text-secondary);
	}
	
	.moon-icon {
		font-size: 4rem;
		margin-bottom: 1rem;
		animation: float 3s ease-in-out infinite;
	}
	
	.empty-state h2 {
		margin: 0 0 0.5rem;
		font-size: 1.5rem;
		font-weight: 600;
		color: var(--text-primary);
	}
	
	.empty-state p {
		margin: 0;
		font-size: 1rem;
	}
	
	@keyframes float {
		0%, 100% {
			transform: translateY(0);
		}
		50% {
			transform: translateY(-10px);
		}
	}
</style>
