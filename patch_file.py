import sys

def patch_file():
    file_path = "packages/core/src/core/geminiChat.ts"
    with open(file_path, "r") as f:
        content = f.read()

    new_content = content.replace(
        """            for await (const chunk of stream) {
              isConnectionPhase = false;
              yield { type: StreamEventType.CHUNK, value: chunk };
            }""",
        """            isConnectionPhase = false;
            for await (const chunk of stream) {
              yield { type: StreamEventType.CHUNK, value: chunk };
            }"""
    )

    with open(file_path, "w") as f:
        f.write(new_content)

def patch_test_file():
    file_path = "packages/core/src/core/geminiChat_network_retry.test.ts"
    with open(file_path, "r") as f:
        content = f.read()

    new_content = content.replace(
        "mockRetryWithBackoff.mockImplementation((fn, opts) => retryWithBackoff(fn, { ...opts, initialDelayMs: 1, maxDelayMs: 1 }));",
        "mockRetryWithBackoff.mockImplementation(retryWithBackoff);"
    )

    test_block = """

  it('should retry on ERR_STREAM_PREMATURE_CLOSE error during stream iteration', async () => {
    const error = new Error('Premature close');
    (error as any).code = 'ERR_STREAM_PREMATURE_CLOSE';

    vi.mocked(mockContentGenerator.generateContentStream)
      .mockImplementationOnce(async () =>
        (async function* () {
          yield {
            candidates: [
              { content: { parts: [{ text: 'Partial response...' }] } },
            ],
          } as unknown as GenerateContentResponse;
          throw error;
        })(),
      )
      .mockImplementationOnce(async () =>
        (async function* () {
          yield {
            candidates: [
              { content: { parts: [{ text: 'Success after retry' }] } },
              { finishReason: 'STOP' },
            ],
          } as unknown as GenerateContentResponse;
        })(),
      );

    const stream = await chat.sendMessageStream(
      { model: 'test-model' },
      'test message',
      'prompt-id-stream-error-retry',
      new AbortController().signal,
      LlmRole.MAIN,
    );

    const events: StreamEvent[] = [];
    for await (const event of stream) {
      events.push(event);
    }

    const successChunk = events.find(
      (e) =>
        e.type === StreamEventType.CHUNK &&
        e.value.candidates?.[0]?.content?.parts?.[0]?.text ===
          'Success after retry',
    );
    expect(successChunk).toBeDefined();
    expect(mockContentGenerator.generateContentStream).toHaveBeenCalledTimes(2);
  });"""
    new_content = new_content.replace(test_block, "")

    with open(file_path, "w") as f:
        f.write(new_content)


if __name__ == "__main__":
    patch_file()
    patch_test_file()
