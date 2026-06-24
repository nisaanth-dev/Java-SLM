"""
Narrative Generation Pipeline — Claude API
===========================================
Reads each chunk from the input folder, injects its content into the
prompt template, calls the Claude API, and writes the narrative to
output.txt in the same chunk subfolder.

Folder structure expected:
    CHUNKS_ROOT/
        C001/
            input.txt
        C002/
            input.txt
        ...

Output written to:
    CHUNKS_ROOT/
        C001/
            input.txt
            output.txt     <-- generated here
        ...
"""

import os
import time
import anthropic
from pathlib import Path
from dotenv import load_dotenv


CHUNKS_ROOT   = r"C:\Projects\Java_SLM\training_data\app1"          # root folder containing chunk subfolders
PROMPT_TEMPLATE_PATH = r"C:\Projects\Java_SLM\prompts\narrative_prompt_v2.md"  # path to the .md prompt file


# Claude models
#----------------------------------
MODEL = "claude-opus-4-8"
#MODEL = "claude-sonnet-4-6"
#MODEL = "claude-haiku-4-5-20251001"

# Generation parameters
MAX_TOKENS = 16384
TEMPERATURE    = 0.2

# Retry settings
MAX_RETRIES    = 3
RETRY_DELAY_S  = 5   # seconds between retries on transient errors


def load_prompt_template(path: str) -> str:
    """Load the prompt .md file and return its content as a string."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def build_prompt(template: str, chunk_text: str) -> str:
    """Replace the {{CODE_CHUNK}} placeholder with the actual chunk content."""
    if "{{CODE_CHUNK}}" not in template:
        raise ValueError("Prompt template does not contain {{CODE_CHUNK}} placeholder.")
    return template.replace("{{CODE_CHUNK}}", chunk_text)


def call_claude(client: anthropic.Anthropic, prompt: str, chunk_id: str) -> str:
    """
    Send the prompt to Claude and return the generated narrative text.
    Retries up to MAX_RETRIES times on transient API errors.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            print(f"\nRESPONSE : {response}")

            # Extract text from the response content blocks
            narrative_parts = [
                block.text
                for block in response.content
                if block.type == "text"
            ]


            if not narrative_parts:
                raise ValueError("API returned a response with no text content blocks.")

            print(f"\nnarrative_parts : {narrative_parts}")
            
            return "\n".join(narrative_parts)

        except anthropic.RateLimitError as e:
            print(f"  [!] Rate limit hit for {chunk_id} (attempt {attempt}/{MAX_RETRIES}). "
                  f"Waiting {RETRY_DELAY_S}s...")
            time.sleep(RETRY_DELAY_S)

        except anthropic.APIStatusError as e:
            print(f"  [!] API error for {chunk_id} (attempt {attempt}/{MAX_RETRIES}): "
                  f"status={e.status_code} — {e.message}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_S)

        except anthropic.APIConnectionError as e:
            print(f"  [!] Connection error for {chunk_id} (attempt {attempt}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_S)

    raise RuntimeError(f"Failed to generate narrative for {chunk_id} after {MAX_RETRIES} attempts.")


def process_chunks(chunks_root: str, prompt_template: str, client: anthropic.Anthropic):
    """
    Walk the chunks root folder, process each subfolder that contains
    an input.txt and is missing an output.txt.
    """
    root = Path(chunks_root)
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"Chunks root folder not found: {chunks_root}")

    # Collect chunk subfolders (sorted for deterministic ordering)
    chunk_dirs = sorted([d for d in root.iterdir() if d.is_dir()])

    if not chunk_dirs:
        print("No subfolders found in the chunks root. Nothing to process.")
        return

    total    = len(chunk_dirs)
    skipped  = 0
    success  = 0
    failed   = 0

    print(f"\nFound {total} chunk subfolder(s) under: {chunks_root}\n")
    print("=" * 60)

    for chunk_dir in chunk_dirs:
        chunk_id   = chunk_dir.name
        input_path = chunk_dir / "input.txt"
        output_path = chunk_dir / "output.txt"

        # Skip if input.txt is missing
        if not input_path.exists():
            print(f"[SKIP] {chunk_id} — input.txt not found.")
            skipped += 1
            continue

        # Skip if output.txt already exists (resume-safe)
        if output_path.exists():
            print(f"[SKIP] {chunk_id} — output.txt already exists. Skipping.")
            skipped += 1
            continue

        print(f"[PROC] {chunk_id} ...", end=" ", flush=True)

        try:
            # Read chunk
            chunk_text = input_path.read_text(encoding="utf-8").strip()
            if not chunk_text:
                print("EMPTY — skipping.")
                skipped += 1
                continue

            # Build full prompt
            full_prompt = build_prompt(prompt_template, chunk_text)

            # Call Claude
            narrative = call_claude(client, full_prompt, chunk_id)

            # Write output
            output_path.write_text(narrative, encoding="utf-8")

            print("DONE")
            success += 1

        except RuntimeError as e:
            print(f"FAILED — {e}")
            failed += 1

        except Exception as e:
            print(f"UNEXPECTED ERROR — {e}")
            failed += 1

    print("=" * 60)
    print(f"\nSummary: {success} generated | {skipped} skipped | {failed} failed")
    print(f"Total chunk folders processed: {total}\n")


def main():
    # Load API key from .env
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY not found. "
            "Add it to a .env file in the same directory as this script."
        )

    # Load prompt template
    print(f"Loading prompt template from: {PROMPT_TEMPLATE_PATH}")
    prompt_template = load_prompt_template(PROMPT_TEMPLATE_PATH)
    print("Prompt template loaded.\n")

    # Initialise Anthropic client
    client = anthropic.Anthropic(api_key=api_key)

    # Run pipeline
    process_chunks(CHUNKS_ROOT, prompt_template, client)


if __name__ == "__main__":
    main()
