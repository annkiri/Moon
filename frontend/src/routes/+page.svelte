<script lang="ts">
	import ChatContainer from '$lib/components/chat/ChatContainer.svelte';
	import InputBar from '$lib/components/chat/InputBar.svelte';
	import {
		getMessages,
		addUserMessage,
		addAssistantMessage,
		appendToMessage,
		finishStreaming
	} from '$lib/stores/messages.svelte';
	import { streamChat } from '$lib/api/client';

	let messages = $derived(getMessages());
	let isLoading = $state(false);

	async function handleSend(event: CustomEvent<{ message: string }>) {
		const { message } = event.detail;
		
		// Add user message
		addUserMessage(message);
		
		// Add placeholder for assistant response
		const assistantMessage = addAssistantMessage();
		isLoading = true;

		// Stream response from API
		await streamChat(
			message,
			(token) => {
				appendToMessage(assistantMessage.id, token);
			},
			() => {
				finishStreaming(assistantMessage.id);
				isLoading = false;
			},
			(error) => {
				console.error('Chat error:', error);
				appendToMessage(assistantMessage.id, 'Error: No se pudo conectar con el servidor.');
				finishStreaming(assistantMessage.id);
				isLoading = false;
			}
		);
	}
</script>

<main class="chat-page">
	<header class="chat-header">
		<h1>Moon AI</h1>
	</header>
	
	<ChatContainer {messages} />
	
	<InputBar on:send={handleSend} />
</main>

<style>
	.chat-page {
		display: flex;
		flex-direction: column;
		height: 100%;
		width: 100%;
		max-width: 768px;
		margin: 0 auto;
	}
	
	.chat-header {
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 0.75rem 1rem;
		padding-top: max(0.75rem, env(safe-area-inset-top));
		background: var(--bg-secondary);
		border-bottom: 1px solid var(--border);
		position: sticky;
		top: 0;
		z-index: 10;
	}
	
	.chat-header h1 {
		margin: 0;
		font-size: 1.125rem;
		font-weight: 600;
		color: var(--text-primary);
	}
</style>
