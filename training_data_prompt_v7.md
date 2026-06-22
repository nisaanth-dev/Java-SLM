# Prompt: Generate 20 Training Samples (Java Spring Boot → Narrative)

You are a senior enterprise Java architect and technical writer. Your task is to **fabricate a realistic, enterprise-level Java Spring Boot microservice application**, divide its code into **20 interdependent code chunks**, and produce a **strict structured narrative** for each chunk. The result is a training dataset of 20 samples for a small language model that converts code chunks into narratives.

---

## 1. The Synthetic Application

- Invent **one coherent enterprise-grade Spring Boot microservice application** (e.g., an order management, claims processing, loan origination, or payments domain — pick one and stay consistent across all 20 samples).
- The code must look like real production enterprise code:
  - Layered architecture: `@RestController` → `@Service` → `@Repository`
  - DTOs, entities, mappers, validators
  - Constructor injection, `@Transactional` boundaries
  - Exception handling (`try/catch/finally`, custom exceptions, `@ControllerAdvice`)
  - Calls to external services (`RestTemplate`/`WebClient`/Feign), and at least one event publish (e.g., Kafka template) somewhere in the app
  - Realistic business logic: validation rules, conditional branching, loops over collections, status transitions, calculations
- Use realistic naming. No `foo`/`bar`, no toy examples, no placeholder comments like `// business logic here`.
- The application must be **internally consistent**: a method called in chunk C004 must actually exist in the chunk where it is defined; IDs, class names, and signatures must agree across all 20 chunks.
- The application must contain **all of the following component types** — every one must appear at least once across the 20 chunks:
  - `@RestController` classes (endpoint handlers, request/response mapping)
  - `@Service` classes (business logic, transaction management)
  - `@Repository` interfaces or classes (Spring Data JPA, custom JPQL/native queries)
  - `@Entity` classes (JPA entities with field annotations, relationships, lifecycle hooks)
  - DTO classes (request DTOs, response DTOs, with Bean Validation annotations)
  - Mapper classes or interfaces (MapStruct or manual entity↔DTO conversion)
  - Custom exception classes and a `@ControllerAdvice` global exception handler
  - `@Configuration` classes (bean definitions: RestTemplate/WebClient, Kafka, datasource, security, etc.)
  - An event publisher and a corresponding `@EventListener` or `@KafkaListener` class
  - At least one `@Scheduled` task or background job class
  - A filter, interceptor, or request-scoped utility/helper class
- Package structure must encode architectural layer per the convention `com.<company>.<application>.<layer>` (e.g., `....controller`, `....service`, `....repository`, `....entity`, `....dto`, `....mapper`, `....exception`, `....config`, `....event`, `....scheduler`, `....filter`, `....util`). All in-application import statements must follow this convention, so that a class's layer is derivable from its fully-qualified name alone.

## 2. Chunking Rules

Divide the application's code into **exactly 20 chunks**, `C001` through `C020`. The chunks are **not independent** — together they form the application's call graph. (In this version the call-graph relationships live only in the code itself; they are not recorded as separate metadata.)

### 2.1 Chunk size

- Each chunk contains **2 to 6 logically related methods or declarations** from one component (e.g., a service class's operations and its private helpers, or an entity class with its field declarations and lifecycle methods).
- Target **300–350 lines of Java code** per chunk (excluding metadata). Never fewer than 250, never more than 400.
- A chunk must be a **logically complete unit** — one cohesive piece of one component. Never cut a method, class declaration, or annotation block in half across chunks.
- For structural components (entities, DTOs, config classes) that may not have many methods, fill the line budget with the full class including all field declarations, annotations, constructors, getters/setters, and any lifecycle or utility methods.
- When a chunk includes the top of a source file, its `import` statements are part of the code as written and must be handled per §3.3's import-handling rule.

### 2.2 Chunk format (INPUT of each sample)

Every chunk MUST follow this exact structure:

```text
CHUNK_ID: CXXX
APPLICATION: <application name>
SERVICE: <microservice name>
FILE: fNN (<package-qualified class name>)
LAYER: <Controller | Service | Repository | Entity | DTO | Mapper | ExceptionHandler | Config | EventPublisher | EventListener | Scheduler | Filter | Util>
ENTRY_POINT: <yes/no — yes only if this chunk contains an externally triggered entry such as a REST endpoint or message listener>

=== CODE ===
<method 1 signature and full body>
<method 2 signature and full body>
<... up to 4 methods>
```

### 2.3 File notation

- `fNN` = file number (e.g., `f01`, `f02`). Assign each class a file number and keep it stable across all chunks.

## 3. Output Spec for Each Sample (STRICT)

### 3.0 Why Completeness Is Non-Negotiable

The narrative produced here is not a summary for a developer. It is the **sole input** to a downstream codebase reverse engineering pipeline that reconstructs a full functional specification document from narratives alone — without access to the original source code. Every piece of information present in the code must be captured in the narrative with zero loss. If a line of code is not reflected somewhere in the narrative, that information is permanently lost from the functional spec. Treat the narrative as a lossless encoding of the chunk's behavior and structure in plain language, complete enough that a business analyst, auditor, or modernization engineer can understand what the chunk does, why it exists, how it behaves under all conditions, and what it produces — without reading the Java.

### 3.1 Output Structure (Order Is Mandatory)

Each sample's `output` field contains, in this exact order:

1. **Business Details section** (STRICT YAML) — Section 3.7
2. **Technical Narrative** — produced under Execution-Trace Mode (3.4) or Structural-Walkthrough Mode (3.5), depending on the chunk's `LAYER`
3. **Supporting Elements section** — included only if Stage 2 of 3.4.1 finds elements not reached by the primary flow. Titled exactly: `Supporting Elements in This Chunk`. Omit entirely if nothing qualifies.

### 3.2 Narrative Mode Is Determined by Chunk LAYER

- **Execution-Trace Mode** applies to: `Controller`, `Service`, `Repository`, `EventPublisher`, `EventListener`, `Scheduler`, `Filter`, and any `Mapper` or `ExceptionHandler` chunk that contains conditional or branching logic.
- **Structural-Walkthrough Mode** applies to: `Entity`, `DTO`, `Config`, and any `Mapper` or `ExceptionHandler` chunk that is purely declarative (field declarations, annotations, simple delegation — no branching).

Do not state which mode was used in the output — it is determined by the rules that follow, applied silently.

### 3.3 Mandatory Java Construct Coverage Checklist

Every construct below, if present anywhere in the chunk's code, must be explicitly identified and narrated. None may be collapsed into a generic statement.

- **Class-level declarations:** Every field, constant, and injected dependency declared at the top of a class — name, type, and business purpose.
- **Method signatures:** Method name, access modifier, return type, and every parameter — named and described exactly as declared, as a business input.
- **Local declarations:** Every local variable, collection, and object declared in a method body — name, type, and what business data it holds.
- **if / else if / else chains:** Every branch — both true and false paths — described individually. Never merge branches.
- **switch / switch expressions:** Every case described individually, including `default`.
- **Loops (`for`, enhanced-for, `while`, `do-while`):** What business entity is iterated, what happens per iteration, and what terminates the loop.
- **Stream operations / lambdas:** What data set is processed, what filter/map/reduce is applied, and what business result is produced. Treat as a loop for narration purposes.
- **try / catch / finally:** See 3.4.3.
- **Method calls — internal:** Calls to other methods in the same chunk — business purpose of the call and what it returns. Fully narrated (3.4.1).
- **Method calls — cross-chunk or external:** See 3.4.4.
- **Backend procedure / data access calls:** For repository methods, native queries, or `CallableStatement`-style calls — the exact query/procedure name or derived method name, every parameter passed, and every value returned.
- **Object construction (`new`):** What business entity is created, what it's initialized with, and what it represents.
- **JSON construction/parsing:** What business structure is read or built, which fields are extracted/populated, and what the result represents.
- **HTTP / REST client calls:** The endpoint in business terms, what is sent, what response is expected, and how each handled response code is treated.
- **return statements:** Exactly what value/result is returned and what it signifies to the caller.
- **throw statements:** The exact exception type, the business condition that triggered it, and the resulting business outcome.
- **Null checks and defensive guards:** What field is checked, what counts as valid vs. absent, and what happens in each case.
- **String manipulation / data transformation:** For every trimmed, parsed, converted, or formatted value — what it represented before, the transformation applied, and what it means after.
- **Constants and hardcoded literals:** Every literal used in a condition or assignment (e.g., `"ACTIVE"`, `30`, `"E_INV_002"`) — state the business policy or threshold it represents.
- **Import statements (if present in this chunk):** For each import of an in-application class, state the imported class's name, its architectural layer/module (derived from its package path per the established convention), and what role that dependency plays in this chunk (e.g., "the repository layer dependency used for order persistence"). For imports of external libraries/frameworks (Spring, Lombok, Jackson, etc.), state what capability each import provides to this class (e.g., "provides the annotation marking this class as a JPA entity"). Imports serving the same purpose may be grouped in one statement rather than narrated individually — but every distinct imported class or framework feature actually used in the chunk must be named at least once. **If this chunk does not include an imports block** (because it doesn't begin at the top of its file), omit this entirely — do not fabricate imports that aren't in the input.
- **Class-level generated-behavior annotations** (e.g., Lombok's `@RequiredArgsConstructor`, `@Data`, `@Getter`/`@Setter`, or similar code-generation annotations): state once, at the class-level description, exactly what is generated (e.g., which fields the generated constructor accepts, in what order) with full specificity. Do not restate this when later describing the individual fields it covers — at that point, simply note that the field is supplied via the generated constructor, without re-explaining what the annotation does.

### 3.4 Execution-Trace Mode Rules

#### 3.4.0 Establish Once, Reference After

The narrative is one continuous, end-to-end account of the chunk — not a series of independently-complete paragraphs. When a fact, mechanism, or annotation's meaning is fully explained once (e.g., in the imports discussion or at its first occurrence), every later point where it recurs must **reference** that established meaning briefly rather than re-explain it.

A later reference is brief if it states only what is *new* at that point (a specific value, path, field, or business condition) and does not restate the general mechanism, definition, or framework behavior already covered.

**Test before writing any explanatory sentence:** "Has this exact mechanism/meaning already been fully stated earlier in this narrative, with no new information at this occurrence?" If yes, do not restate it — name the element and move on. If the occurrence carries new information (a different value, path, condition, or outcome), state only that new information, omitting the general mechanism already covered.

This rule applies most directly to: annotations whose meaning is constant across all uses (e.g., Lombok-generated constructors, class-level stereotype annotations), and any phrase that would otherwise be repeated verbatim or near-verbatim at multiple points in the narrative.

#### 3.4.1 Two-Stage Walk: Primary Flow + Supporting Elements

**Stage 1 — Primary Flow.** Identify the chunk's primary method: for `ENTRY_POINT: yes` chunks, this is the REST endpoint or listener method; for other chunks, it is the primary public method that represents the chunk's main business operation (the method other parts of the application call into). Narrate this method's execution step by step, following every call to another method **within the same chunk** recursively — fully explain the called method before returning to the caller (3.4.2). For calls leaving the chunk, apply 3.4.4.

**Stage 2 — Supporting Elements.** After Stage 1, identify any method, field, or constant in the chunk not reached by the primary flow (e.g., a helper used only by a second public method, an overload, a constant used only in a branch not exercised by the primary trace's framing). Narrate each fully under the `Supporting Elements in This Chunk` section (3.1). If everything in the chunk is reached by Stage 1, omit this section.

#### 3.4.2 Explicit Return and Continuation

After fully explaining a called method (internal call), the narrative must explicitly state that control returns to the point immediately following the call, then continue narrating from that exact point.

Do not state "control proceeds to the next statement" after ordinary sequential statements where this is the only possible continuation — this is the default and need not be narrated. State it only where the alternative is genuinely possible (e.g., after a branch, loop, or returning call) and its absence would be ambiguous.

#### 3.4.3 Exception Handling (Expanded)

Every `try / catch / finally` block must be analyzed in full:

- For each `catch` block (specific type or general `Exception`): state what business condition causes this exception to be raised, what the catch block does in response (log, re-throw, return an error response, set a status, roll back, release a resource), and what the resulting business outcome is (process aborts, caller receives an error, processing continues with a default, record is skipped, resource is freed).
- The `finally` block: state what always executes regardless of outcome, and what business significance that has (e.g., a connection is always closed, an audit entry is always written).

#### 3.4.4 Cross-Chunk and External Call Handling (CRITICAL)

When the code calls a method that belongs to **another component (defined in a different chunk)** or to an **external dependency** (another service or system):

- Describe only what is visible from the calling code itself: the method/endpoint name, the arguments passed and their business meaning, and what the return value is assigned to or how it is used afterward.
- State explicitly that control transfers out to that called operation and that its result returns to this point. (No chunk identifier is referenced — none is available from the code alone.)
- Do **NOT** narrate the internal logic, branches, exception handling, or implementation of the target — even if that logic is known from generating the other chunks in this dataset. The detailed behavior of the called component belongs in its own chunk's narrative.
- If the calling code's `try/catch` anticipates specific exception types from this call, describe those per 3.4.3 — that much IS visible from the calling chunk.

This rule does not apply to internal calls (3.4.1/3.4.2) to methods defined within the chunk, which must be fully narrated.

#### 3.4.5 Anti-Compression Mandate

The following must NEVER be compressed, paraphrased, or omitted:

- Every specific literal value used in a condition (e.g., `"ACTIVE"`, `"Y"`, `0`, `30`, `"status_2"`, `true`)
- Every distinct `if`/`else if`/`else` branch — each is a separate business outcome
- Every loop iteration and its termination condition
- Every exception handler — each is a separate business response
- Every method call in the execution chain — each is a distinct business step
- Every null check — each is a distinct validation decision
- Every return statement — each is a distinct business outcome
- Every line from the chunk's code must be covered completely

**Violation test:** if a reader cannot reconstruct the original `if` condition — the condition itself, the true path, and the false path — from the narrative alone, the narrative has compressed too much.

#### 3.4.6 No Summarization (Example)

- **Incorrect:** "The method validates the request and returns an error if invalid."
- **Correct:** "An if statement checks whether the local variable `customerStatus` is not null and is not equal to the empty string after trimming. If this condition is false — meaning `customerStatus` is null or blank — the method immediately constructs a response object, sets its `status` field to the literal value `"REJECTED"` and its `message` field to the value of the `validationErrorMessage` variable, and returns this response to the caller, terminating further processing in this method. If the condition is true, execution continues to the next statement."

#### 3.4.7 Data Lineage Traceability

For every derived, calculated, or transformed value, trace its full origin: every assignment, transformation, parsing, or lookup from source to final value.

**Example:** "The variable `branchCode` is initially declared as `null`. It is subsequently populated by the return value of the internal call to `resolveBranchForCustomer(customerId)`, which receives the customer identifier as its sole input. This return value is assigned directly to `branchCode`, which is thereafter used as the branch parameter in the call to `saveOrderRecord` later in this method."

#### 3.4.8 Absence Handling

Explicitly state when any of the following are absent or minimal for an operation that would normally have them:

- Exception handling for a particular operation
- Null or empty checks before use of a value
- Logging or audit trail
- Transaction management (no `@Transactional`, commit, or rollback)
- Input validation before delegation to another layer

### 3.5 Structural-Walkthrough Mode Rules

For `Entity`, `DTO`, `Config`, and purely declarative `Mapper`/`ExceptionHandler` chunks:

- **Fields, in declaration order:** for each field, state its name, type, every annotation present (e.g., `@Column`, `@NotNull`, `@Size`, `@JsonProperty`) and what runtime behavior or constraint that annotation enforces, and what business data the field represents.
- **Relationships:** for `@OneToMany`, `@ManyToOne`, `@OneToOne`, `@ManyToMany` — state the related entity, the cardinality in business terms, and the fetch/cascade behavior if specified.
- **Constructors:** for each constructor, state what it initializes and from what inputs.
- **Methods (getters/setters/mapping/conversion logic):** narrate each individually. If any method contains conditional logic (e.g., a mapper with an `if` for a default value), apply Execution-Trace rules (3.4) to that logic.
- **Class-level annotations** (e.g., `@Entity`, `@Table`, `@ConfigurationProperties`, `@Bean`-producing methods in `@Configuration` classes): state what each means at runtime — what table/resource it maps to, what bean it produces and how it is wired.

### 3.6 Verbatim Naming

All variable names, parameter names, method names, class names, constant names, literal values, exception type names, JSON key names, annotation names, and endpoint paths must be stated exactly as they appear in the chunk's code. Do not rename or paraphrase identifiers in the technical narrative.

### 3.7 Business Details Section (STRICT YAML)

#### 3.7.1 Business Rule Purity Mandate

A business rule describes a real-world policy, constraint, or decision the organization enforces, expressed entirely in business language.

A business rule **MUST NOT** contain: variable, parameter, method, or class names, or any Java identifier; technical terms such as exception, null check, try-catch, throw, method call, flag, loop, stream, JSON, query, HTTP call, REST, or procedure; any reference to how the rule is implemented in code.

A business rule **MUST**: describe a real-world condition in plain business language (e.g., "customer identity", "order status", "account balance"); state the business outcome or policy consequence (e.g., "the order is rejected", "a notification is sent", "the record is placed on hold"); be understandable to a business stakeholder with no technical background.

**Business Rule Test** — before writing any rule, apply this test: *"Could a business manager, with no knowledge of Java, read this rule and immediately understand the business policy it describes?"* If no, rewrite until the answer is yes. If a rule genuinely cannot be expressed without technical terms, write instead: `"Not expressible as a pure business rule from available input — requires business context to complete."`

#### 3.7.2 Output Format

```yaml
business_functional_name: |
  Exactly one name, three to six words, Title Case, capturing the entire
  business behavior of this chunk as a single process label.
  Must contain no variable names, method names, or technical terms.
  Must be specific enough to distinguish this chunk from others.
  Example: "Customer Identity Verification And Registration"
  Example: "Order Status Transition And Notification"
  Example: "Branch Transaction Validation And Posting"

core_business_functionality: |
  Exactly two sentences describing business capability.
  Must be business-focused (NO technical explanation).

business_function: |
  Each line = one business function, one sentence, independently readable.
  No technical terms. No paragraphs. One new function per line.

business_functions_list:
  - Each item MUST be exactly 2 to 3 words.
  - Format: Verb + Business Noun
  - No articles ("a", "the", "an")
  - No technical verbs: never use Fetch, Query, Execute, Throw, Call,
    Return, Parse, Serialize, Instantiate, Invoke, Post, Get, Put
  - One distinct business action per entry
  - Example: "Validate Identity"
  - Example: "Reject Submission"
  - Example: "Notify Branch"

business_rules:
  - rule_id: "CXXX_BR1"
    rule: "Business rule written in plain business language. Must pass the Business Rule Test."
    condition: "Business condition only (no technical terms)"
    action: "Business outcome only"
    occurrence: "Same as rule_id"
    source_chunks: ["CXXX"]

  - rule_id: "CXXX_BR2"
    rule: "Another business rule"
    condition: "Condition in business language"
    action: "Outcome in business language"
    occurrence: "Same as rule_id"
    source_chunks: ["CXXX"]
```

> **Note on `occurrence`:** in this dataset every chunk is generated and narrated independently (no consolidation pass), so `occurrence` is always identical to `rule_id`. The field is retained for forward-compatibility in case a later consolidation/functional-spec pass over multiple chunks' business rules is introduced.

### 3.8 General Rules

- Do NOT summarize.
- Do NOT skip any logic.
- Do NOT merge conditions.
- Use exact variable, method, class, and constant names from the chunk's code (3.6).
- Output must fully depend on the chunk's actual content — no template/generic output.

## 4. Final Sample Format (MANDATORY)

Each of the 20 samples MUST be a JSON object in exactly this structure:

```json
{
  "sample_id": 1,
  "chunk_id": "C001",
  "input": "<the full chunk exactly as defined in section 2.2, as a single string>",
  "output": "<Business Details YAML + Full Execution Narrative, as a single string>"
}
```

Emit all 20 samples as a JSON array. Escape the strings properly so the array is valid, parseable JSON.

## 5. Coverage Requirements Across the 20 Samples

The 20 chunks together must cover ALL of the following. Every row is mandatory.

### 5A. Component Type Coverage (structural — what kind of component the chunk is)

| # | Component Type | Minimum chunks |
|---|---|---|
| 1 | `@RestController` — REST endpoint handlers | 2 |
| 2 | `@Service` — Business logic classes | 4 |
| 3 | `@Repository` — Data access (Spring Data JPA or JDBC) | 2 |
| 4 | `@Entity` — JPA entity with field annotations, relationships, lifecycle hooks | 2 |
| 5 | DTO classes — Request/response objects with Bean Validation annotations | 2 |
| 6 | Mapper — Entity↔DTO conversion (MapStruct or manual) | 1 |
| 7 | Custom exceptions + `@ControllerAdvice` global handler | 1 |
| 8 | `@Configuration` — Bean definitions (RestTemplate/WebClient, Kafka, datasource, etc.) | 1 |
| 9 | Event publisher + `@EventListener` or `@KafkaListener` | 1 |
| 10 | `@Scheduled` task or background job | 1 |
| 11 | Filter, interceptor, or request-scoped utility/helper | 1 |

### 5B. Behavioral Construct Coverage (what the code does inside the chunk)

| # | Construct / Pattern | Minimum occurrences |
|---|---|---|
| 1 | REST controller endpoints (GET/POST/PUT) | 3 chunks |
| 2 | Service-layer business logic with branching (`if/else`, `switch`) | 5 chunks |
| 3 | Loops over collections (`for`, enhanced-for, streams treated as loops) | 4 chunks |
| 4 | `try/catch/finally` with custom exceptions | 3 chunks |
| 5 | `@Transactional` method with rollback-relevant logic | 2 chunks |
| 6 | Repository/data access (Spring Data JPA or JDBC template) | 3 chunks |
| 7 | External HTTP call (RestTemplate/WebClient/Feign) with error handling | 2 chunks |
| 8 | Event publishing (e.g., Kafka) | 1 chunk |
| 9 | Validation logic (Bean Validation or manual) | 2 chunks |
| 10 | Status/state transition logic | 2 chunks |

A single chunk may satisfy multiple rows in both tables. Distribute constructs naturally — do not force them into a chunk where they would not logically belong.

## 6. Quality Gates (Self-Check Before Emitting)

Before producing the final answer, verify ALL of the following:

1. Exactly 20 samples; chunk IDs C001–C020 each used exactly once.
2. Every method referenced in a narrative exists in the named chunk with the same name and signature.
3. No business-language field (names, functions, rules) contains a class name, method name, variable name, annotation, or framework term.
4. Every narrative walks all branches, loops, exception paths, and returns present in the code — nothing summarized or skipped.
5. Every annotation with runtime significance is described in the narrative.
6. Every field, constructor, thrown exception, and null check present in the code is reflected in the narrative.
7. No vague summary verbs ("handles", "processes", "manages") used in place of concrete description.
8. The JSON array parses.

If any check fails, fix the sample before emitting. Emit ONLY the final JSON array — no commentary before or after.


## 7. Self-Review Section (Mandatory Output — Per Sample)
 
Every sample's `output` field must include a **Self-Review** section after the Technical Narrative (and after Supporting Elements if present). This section is always written, regardless of whether issues were found.
 
### Format
 
```
---
**Self-Review**
 
**Rules followed:**
<A plain prose paragraph stating which key rules were applied and how — e.g., which narrative mode was used, whether the establish-once principle was applied, whether absence handling was noted, whether all constructs in the checklist were covered.>
 
**Gaps or uncertainties identified:**
<A plain prose paragraph honestly reflecting on anything that may have been missed, compressed, approximated, or handled with less than full confidence. This includes: any construct from §3.3 that was present in the code but may not have been fully narrated; any branch, loop, or exception path that may have been partially described; any business rule that was difficult to express without technical terms; any annotation whose runtime behavior was described with uncertainty; any place where the establish-once rule may have been violated. If nothing is flagged, state: "No gaps or uncertainties identified in this sample.">
 
**Duplication check:**
<A plain prose paragraph identifying any explanation, phrase, or mechanism that was repeated more than once in this narrative. For each repetition found, state what was repeated and where. If no repetition was found, state: "No duplication detected in this sample.">
```
 
### Rules for the Self-Review section
 
- It is always present — never omitted, even on a sample the model considers fully correct.
- It is written after the narrative is complete — the model reviews what it actually produced, not what it intended to produce.
- It must be honest: if the model is uncertain whether a construct was fully covered, it flags it even if it made a best effort.
- It must not simply repeat the rules back as confirmation — it must reflect on the actual content of this specific sample's narrative.
- The three sub-sections (Rules followed, Gaps or uncertainties, Duplication check) are always present and always labeled exactly as shown.
 