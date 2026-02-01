<script lang="ts">
    import { createEventDispatcher } from "svelte";

    const dispatch = createEventDispatcher<{
        send: { message: string };
    }>();

    let inputValue = $state("");
    let inputRef: HTMLTextAreaElement;
    let isComposing = $state(false);

    function handleSubmit() {
        const trimmed = inputValue.trim();
        if (!trimmed) return;

        dispatch("send", { message: trimmed });
        inputValue = "";

        // Reset textarea height
        if (inputRef) {
            inputRef.style.height = "auto";
        }
    }

    function handleKeydown(e: KeyboardEvent) {
        // Don't submit during IME composition
        if (isComposing) return;

        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    }

    function autoResize(e: Event) {
        const target = e.target as HTMLTextAreaElement;
        target.style.height = "auto";
        target.style.height = Math.min(target.scrollHeight, 150) + "px";
    }
</script>

<form
    class="input-bar"
    onsubmit={(e) => {
        e.preventDefault();
        handleSubmit();
    }}
>
    <div class="input-container">
        <textarea
            bind:this={inputRef}
            bind:value={inputValue}
            onkeydown={handleKeydown}
            oninput={autoResize}
            oncompositionstart={() => (isComposing = true)}
            oncompositionend={() => (isComposing = false)}
            placeholder="Escribe un mensaje..."
            rows="1"
        ></textarea>

        <button
            type="submit"
            class="send-btn"
            disabled={!inputValue.trim()}
            aria-label="Enviar mensaje"
        >
            <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
            >
                <path d="m22 2-7 20-4-9-9-4Z" />
                <path d="M22 2 11 13" />
            </svg>
        </button>
    </div>
</form>

<style>
    .input-bar {
        padding: 0.75rem 1rem;
        padding-bottom: max(0.75rem, env(safe-area-inset-bottom));
        background: var(--bg-secondary);
        border-top: 1px solid var(--border);
    }

    .input-container {
        display: flex;
        align-items: flex-end;
        gap: 0.5rem;
        background: var(--bg-tertiary);
        border-radius: 1.5rem;
        padding: 0.5rem 0.75rem;
    }

    textarea {
        flex: 1;
        background: transparent;
        border: none;
        outline: none;
        color: var(--text-primary);
        font-size: 1rem;
        font-family: inherit;
        resize: none;
        max-height: 150px;
        line-height: 1.5;
        padding: 0.25rem 0;
    }

    textarea::placeholder {
        color: var(--text-secondary);
    }

    .send-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 36px;
        height: 36px;
        min-height: 36px;
        border-radius: 50%;
        border: none;
        background: var(--accent);
        color: white;
        cursor: pointer;
        transition:
            background 0.2s,
            opacity 0.2s,
            transform 0.1s;
        flex-shrink: 0;
    }

    .send-btn:hover:not(:disabled) {
        background: var(--accent-hover);
    }

    .send-btn:active:not(:disabled) {
        transform: scale(0.95);
    }

    .send-btn:disabled {
        opacity: 0.4;
        cursor: not-allowed;
    }
</style>
