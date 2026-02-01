<script lang="ts">
	export interface Message {
		id: string;
		role: 'user' | 'assistant';
		content: string;
		timestamp: Date;
		isStreaming?: boolean;
	}
	
	let { message }: { message: Message } = $props();
	
	const isUser = $derived(message.role === 'user');
</script>

<div class="message-wrapper" class:user={isUser} class:assistant={!isUser}>
	<div class="bubble">
		{#if message.isStreaming && !message.content}
			<span class="typing-indicator">
				<span class="dot"></span>
				<span class="dot"></span>
				<span class="dot"></span>
			</span>
		{:else}
			<p>{message.content}</p>
		{/if}
	</div>
</div>

<style>
	.message-wrapper {
		display: flex;
		padding: 0.5rem 1rem;
		width: 100%;
	}
	
	.message-wrapper.user {
		justify-content: flex-end;
	}
	
	.message-wrapper.assistant {
		justify-content: flex-start;
	}
	
	.bubble {
		max-width: 85%;
		padding: 0.75rem 1rem;
		border-radius: 1.25rem;
		word-wrap: break-word;
		line-height: 1.5;
	}
	
	.user .bubble {
		background: var(--accent);
		color: white;
		border-bottom-right-radius: 0.25rem;
	}
	
	.assistant .bubble {
		background: var(--bg-tertiary);
		color: var(--text-primary);
		border-bottom-left-radius: 0.25rem;
	}
	
	.bubble p {
		margin: 0;
		font-size: 0.9375rem;
	}
	
	/* Typing indicator */
	.typing-indicator {
		display: flex;
		gap: 0.25rem;
		padding: 0.25rem 0;
	}
	
	.dot {
		width: 8px;
		height: 8px;
		background: var(--text-secondary);
		border-radius: 50%;
		animation: bounce 1.4s infinite ease-in-out both;
	}
	
	.dot:nth-child(1) { animation-delay: -0.32s; }
	.dot:nth-child(2) { animation-delay: -0.16s; }
	.dot:nth-child(3) { animation-delay: 0s; }
	
	@keyframes bounce {
		0%, 80%, 100% {
			transform: scale(0);
			opacity: 0.5;
		}
		40% {
			transform: scale(1);
			opacity: 1;
		}
	}
</style>
