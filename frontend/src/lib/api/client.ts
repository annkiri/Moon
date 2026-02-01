// API configuration
// Dynamically use same host as frontend, just different port
const API_BASE = typeof window !== 'undefined'
    ? `${window.location.protocol}//${window.location.hostname}:8000`
    : 'http://localhost:8000';

/**
 * Send a message and stream the response
 */
export async function streamChat(
    message: string,
    onToken: (token: string) => void,
    onComplete: () => void,
    onError: (error: Error) => void
): Promise<void> {
    try {
        const response = await fetch(`${API_BASE}/api/chat/stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        if (!reader) {
            throw new Error('No response body');
        }

        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });

            // Parse SSE format: "data: token\n\n"
            const lines = chunk.split('\n');
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const token = line.slice(6);
                    if (token === '[DONE]') {
                        onComplete();
                        return;
                    }
                    onToken(token);
                }
            }
        }

        onComplete();
    } catch (error) {
        onError(error instanceof Error ? error : new Error('Unknown error'));
    }
}

/**
 * Send a simple message (non-streaming)
 */
export async function sendMessage(message: string): Promise<string> {
    const response = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message })
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data.response;
}

/**
 * Health check
 */
export async function healthCheck(): Promise<boolean> {
    try {
        const response = await fetch(`${API_BASE}/api/health`);
        return response.ok;
    } catch {
        return false;
    }
}
