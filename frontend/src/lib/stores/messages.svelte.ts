import type { Message } from '$lib/components/chat/MessageBubble.svelte';

// Simple ID generator
function generateId(): string {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

// Messages state using Svelte 5 runes
let messages = $state<Message[]>([]);

export function getMessages(): Message[] {
    return messages;
}

export function addUserMessage(content: string): Message {
    const message: Message = {
        id: generateId(),
        role: 'user',
        content,
        timestamp: new Date()
    };
    messages.push(message);
    return message;
}

export function addAssistantMessage(): Message {
    const message: Message = {
        id: generateId(),
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        isStreaming: true
    };
    messages.push(message);
    return message;
}

export function appendToMessage(id: string, token: string): void {
    const index = messages.findIndex(m => m.id === id);
    if (index !== -1) {
        messages[index].content += token;
    }
}

export function finishStreaming(id: string): void {
    const index = messages.findIndex(m => m.id === id);
    if (index !== -1) {
        messages[index].isStreaming = false;
    }
}

export function clearMessages(): void {
    messages = [];
}
