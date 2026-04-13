import sys

def patch_file():
    file_path = "packages/core/src/core/geminiChat.ts"
    with open(file_path, "r") as f:
        content = f.read()

    new_content = content.replace(
        """for await (const chunk of stream) {
              isConnectionPhase = false;
              yield { type: StreamEventType.CHUNK, value: chunk };
            }""",
        """isConnectionPhase = false;
            for await (const chunk of stream) {
              yield { type: StreamEventType.CHUNK, value: chunk };
            }"""
    )

    with open(file_path, "w") as f:
        f.write(new_content)

if __name__ == "__main__":
    patch_file()
