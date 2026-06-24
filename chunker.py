"""
Java Codebase Chunker
---------------------
Reads a Java Spring Boot Maven project and converts each .java file
into a structured input chunk, writing one subfolder per chunk under
the specified output directory.

Configure the two paths below before running:
    CODEBASE_PATH  — root folder of the unzipped Maven project
    OUTPUT_PATH    — folder where chunk subfolders will be created

Output structure:
    OUTPUT_PATH/
        C001/
            input.txt
        C002/
            input.txt
        ...
"""

import os
import re
from pathlib import Path


# ---------------------------------------------------------------------------
# *** CONFIGURE PATHS HERE ***
# ---------------------------------------------------------------------------

CODEBASE_PATH = r"C:\Projects\Java_SLM\java_code_bases\policy-underwriting-service"
OUTPUT_PATH   = r"C:\Projects\Java_SLM\training_data"

# ---------------------------------------------------------------------------
# Layer detection
# ---------------------------------------------------------------------------

# Package-segment → LAYER (checked against every segment of the package path)
PACKAGE_LAYER_MAP = {
    "controller":     "Controller",
    "controllers":    "Controller",
    "service":        "Service",
    "services":       "Service",
    "repository":     "Repository",
    "repositories":   "Repository",
    "repo":           "Repository",
    "entity":         "Entity",
    "entities":       "Entity",
    "model":          "Entity",
    "models":         "Entity",
    "dto":            "DTO",
    "dtos":           "DTO",
    "request":        "DTO",
    "response":       "DTO",
    "mapper":         "Mapper",
    "mappers":        "Mapper",
    "exception":      "ExceptionHandler",
    "exceptions":     "ExceptionHandler",
    "advice":         "ExceptionHandler",
    "config":         "Config",
    "configuration":  "Config",
    "configs":        "Config",
    "publisher":      "EventPublisher",
    "publishers":     "EventPublisher",
    "listener":       "EventListener",
    "listeners":      "EventListener",
    "event":          "EventPublisher",   # refined by annotation below
    "events":         "EventPublisher",
    "scheduler":      "Scheduler",
    "schedulers":     "Scheduler",
    "scheduled":      "Scheduler",
    "filter":         "Filter",
    "filters":        "Filter",
    "interceptor":    "Filter",
    "interceptors":   "Filter",
    "util":           "Util",
    "utils":          "Util",
    "helper":         "Util",
    "helpers":        "Util",
    "common":         "Util",
}

# Annotation → LAYER override (takes priority over package-segment match)
ANNOTATION_LAYER_MAP = [
    (re.compile(r'@RestController\b'),        "Controller"),
    (re.compile(r'@Controller\b'),            "Controller"),
    (re.compile(r'@Service\b'),               "Service"),
    (re.compile(r'@Repository\b'),            "Repository"),
    (re.compile(r'@Entity\b'),                "Entity"),
    (re.compile(r'@MappedSuperclass\b'),      "Entity"),
    (re.compile(r'@Mapper\b'),                "Mapper"),
    (re.compile(r'@ControllerAdvice\b'),      "ExceptionHandler"),
    (re.compile(r'@RestControllerAdvice\b'),  "ExceptionHandler"),
    (re.compile(r'@Configuration\b'),         "Config"),
    (re.compile(r'@ConfigurationProperties'), "Config"),
    (re.compile(r'@KafkaListener\b'),         "EventListener"),
    (re.compile(r'@RabbitListener\b'),        "EventListener"),
    (re.compile(r'@SqsListener\b'),           "EventListener"),
    (re.compile(r'@EventListener\b'),         "EventListener"),
    (re.compile(r'@Scheduled\b'),             "Scheduler"),
]

VALID_LAYERS = {
    "Controller", "Service", "Repository", "Entity", "DTO",
    "Mapper", "ExceptionHandler", "Config", "EventPublisher",
    "EventListener", "Scheduler", "Filter", "Util",
}


def detect_layer(java_path: Path, source_code: str) -> str:
    """
    Determine the architectural LAYER of a Java file.
    Priority order:
      1. Annotation-based detection (most reliable)
      2. Package-segment detection (from directory path)
      3. Fallback: Util
    """
    # 1. Annotation-based (scan the source text)
    for pattern, layer in ANNOTATION_LAYER_MAP:
        if pattern.search(source_code):
            # Special case: @EventListener can appear inside a publisher too;
            # if the class also publishes events, prefer EventPublisher.
            # We resolve this by checking both and deferring to the first match.
            return layer

    # 2. Package-segment from directory path
    # Convert path separators to lowercase segments for matching
    path_str = str(java_path).lower().replace("\\", "/")
    segments = path_str.split("/")
    for segment in reversed(segments):          # innermost package first
        if segment in PACKAGE_LAYER_MAP:
            return PACKAGE_LAYER_MAP[segment]

    # 3. Fallback
    return "Util"


# ---------------------------------------------------------------------------
# Entry point detection
# ---------------------------------------------------------------------------

# Patterns that indicate an externally triggered entry point
ENTRY_POINT_PATTERNS = [
    re.compile(r'@(Get|Post|Put|Delete|Patch)Mapping\b'),   # Spring MVC
    re.compile(r'@RequestMapping\b'),                        # Spring MVC (method level)
    re.compile(r'@KafkaListener\b'),                         # Kafka
    re.compile(r'@RabbitListener\b'),                        # RabbitMQ
    re.compile(r'@SqsListener\b'),                           # AWS SQS
    re.compile(r'@EventListener\b'),                         # Spring events
    re.compile(r'@MessageMapping\b'),                        # WebSocket STOMP
    re.compile(r'@JmsListener\b'),                           # JMS
    re.compile(r'@StreamListener\b'),                        # Spring Cloud Stream (legacy)
    re.compile(r'@InboundChannelAdapter\b'),                 # Spring Integration
    re.compile(r'@Scheduled\b'),                             # Scheduled tasks
]


def detect_entry_point(source_code: str) -> str:
    """Return 'yes' if the file contains any externally triggered entry point."""
    for pattern in ENTRY_POINT_PATTERNS:
        if pattern.search(source_code):
            return "yes"
    return "no"


# ---------------------------------------------------------------------------
# Package and class name extraction
# ---------------------------------------------------------------------------

PACKAGE_RE = re.compile(r'^\s*package\s+([\w.]+)\s*;', re.MULTILINE)
CLASS_RE    = re.compile(
    r'^\s*(?:public\s+|protected\s+|private\s+|abstract\s+|final\s+)*'
    r'(?:class|interface|enum|record|@interface)\s+(\w+)',
    re.MULTILINE
)


def extract_package(source_code: str) -> str:
    m = PACKAGE_RE.search(source_code)
    return m.group(1) if m else ""


def extract_class_name(source_code: str) -> str:
    m = CLASS_RE.search(source_code)
    return m.group(1) if m else "Unknown"


def fully_qualified_name(source_code: str) -> str:
    pkg  = extract_package(source_code)
    cls  = extract_class_name(source_code)
    return f"{pkg}.{cls}" if pkg else cls


# ---------------------------------------------------------------------------
# Project summary parsing
# ---------------------------------------------------------------------------

def parse_project_summary(codebase_root: Path) -> dict:
    """
    Read PROJECT_SUMMARY.txt from the codebase root.
    Returns a dict with APPLICATION and SERVICE keys (and others).
    Falls back to empty strings if the file is missing.
    """
    summary = {
        "APPLICATION": "",
        "SERVICE":     "",
        "DOMAIN":      "",
        "BASE_PACKAGE": "",
    }

    summary_path = codebase_root / "PROJECT_SUMMARY.txt"
    if not summary_path.exists():
        print(f"[WARN] PROJECT_SUMMARY.txt not found at {summary_path}. "
              f"APPLICATION and SERVICE fields will be empty.")
        return summary

    with open(summary_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            for key in summary:
                if line.startswith(f"{key}:"):
                    summary[key] = line[len(key) + 1:].strip()

    return summary


# ---------------------------------------------------------------------------
# Java file discovery
# ---------------------------------------------------------------------------

def collect_java_files(codebase_root: Path) -> list[Path]:
    """
    Recursively collect all .java files under codebase_root,
    sorted alphabetically by full path for deterministic ordering.
    Ignores test directories (src/test).
    """
    java_files = []
    for path in sorted(codebase_root.rglob("*.java")):
        # Skip test sources
        parts = path.parts
        if "test" in parts or "Test" in parts:
            continue
        java_files.append(path)
    return java_files


# ---------------------------------------------------------------------------
# Chunk format assembly
# ---------------------------------------------------------------------------

CHUNK_TEMPLATE = """\
CHUNK_ID: {chunk_id}
APPLICATION: {application}
SERVICE: {service}
FILE: {file_id} ({fqn})
LAYER: {layer}
ENTRY_POINT: {entry_point}

=== CODE ===
{code}"""


def format_chunk_id(n: int) -> str:
    return f"C{n:03d}"


def format_file_id(n: int) -> str:
    return f"f{n:02d}"


def build_chunk(
    chunk_number: int,
    file_number:  int,
    java_path:    Path,
    source_code:  str,
    application:  str,
    service:      str,
) -> str:
    return CHUNK_TEMPLATE.format(
        chunk_id    = format_chunk_id(chunk_number),
        application = application,
        service     = service,
        file_id     = format_file_id(file_number),
        fqn         = fully_qualified_name(source_code),
        layer       = detect_layer(java_path, source_code),
        entry_point = detect_entry_point(source_code),
        code        = source_code.rstrip(),
    )


# ---------------------------------------------------------------------------
# Output writing
# ---------------------------------------------------------------------------

def write_chunk(output_root: Path, chunk_id: str, content: str) -> None:
    chunk_dir = output_root / chunk_id
    chunk_dir.mkdir(parents=True, exist_ok=True)
    input_file = chunk_dir / "input.txt"
    with open(input_file, "w", encoding="utf-8") as f:
        f.write(content)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    codebase_root = Path(CODEBASE_PATH).resolve()
    output_root   = Path(OUTPUT_PATH).resolve()

    if not codebase_root.exists():
        print(f"[ERROR] Codebase path does not exist: {codebase_root}")
        return

    print(f"[INFO] Codebase root : {codebase_root}")
    print(f"[INFO] Output root   : {output_root}")

    # Parse project summary for APPLICATION and SERVICE
    summary     = parse_project_summary(codebase_root)
    application = summary["APPLICATION"]
    service     = summary["SERVICE"]

    if not application:
        print("[WARN] APPLICATION not found in PROJECT_SUMMARY.txt — field will be blank.")
    if not service:
        print("[WARN] SERVICE not found in PROJECT_SUMMARY.txt — field will be blank.")

    # Collect java files
    java_files = collect_java_files(codebase_root)
    if not java_files:
        print("[ERROR] No .java files found under the codebase path.")
        return

    print(f"[INFO] Found {len(java_files)} Java source file(s).")
    output_root.mkdir(parents=True, exist_ok=True)

    # Process each file
    layer_counts = {}
    for idx, java_path in enumerate(java_files, start=1):
        source_code = java_path.read_text(encoding="utf-8")
        chunk_id    = format_chunk_id(idx)
        file_id     = format_file_id(idx)
        layer       = detect_layer(java_path, source_code)
        entry_point = detect_entry_point(source_code)
        fqn         = fully_qualified_name(source_code)
        line_count  = len(source_code.splitlines())

        chunk_content = build_chunk(
            chunk_number = idx,
            file_number  = idx,
            java_path    = java_path,
            source_code  = source_code,
            application  = application,
            service      = service,
        )

        write_chunk(output_root, chunk_id, chunk_content)

        layer_counts[layer] = layer_counts.get(layer, 0) + 1

        print(
            f"[INFO] {chunk_id} | {file_id} | {layer:<16} | "
            f"ENTRY={entry_point} | {line_count:>4} lines | {fqn}"
        )

    # Summary
    print(f"\n[DONE] {len(java_files)} chunk(s) written to {output_root}")
    print("\n[SUMMARY] Layer distribution:")
    for layer, count in sorted(layer_counts.items()):
        print(f"          {layer:<20} {count} file(s)")


if __name__ == "__main__":
    main()
