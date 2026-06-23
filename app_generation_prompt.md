# Prompt: Generate Synthetic Enterprise Java Spring Boot Application

You are a senior enterprise Java architect. Your task is to generate a **complete, realistic, enterprise-grade Java Spring Boot microservice application** as a fully structured Maven project. This codebase will be used as synthetic training data for a machine learning research project — so it must look and behave exactly like real production code, not a tutorial or demo.

---

## 1. Domain and Application

Choose **one application** from the **Banking, Finance, or Insurance** domain. The exact service is your choice — examples include but are not limited to: loan origination, trade settlement, claims processing, payment gateway, policy underwriting, account management, fraud detection, or portfolio valuation. Pick whichever domain you can make most realistic and complete.

State your chosen domain and application name at the very top of your response before any code, in this format:

```
DOMAIN: <Banking | Finance | Insurance>
APPLICATION: <Application name, e.g., "Meridian Loan Origination Platform">
SERVICE: <Microservice name, e.g., "loan-origination-service">
BASE_PACKAGE: com.<company>.<service> (e.g., com.meridianbank.loanorigination)
```

---

## 2. Technology Stack (Fixed — Do Not Deviate)

- **Java 17** — use Java 17 language features where appropriate (records are allowed for DTOs if desired, sealed classes, pattern matching, text blocks)
- **Spring Boot 3.2.x** — use `jakarta.*` namespace throughout (NOT `javax.*`)
- **Spring Data JPA** with Hibernate
- **Spring Web** (REST controllers)
- **Spring Kafka** for event publishing and listening
- **Spring Security** (basic configuration)
- **Spring Scheduling** (`@Scheduled`)
- **Lombok** — `@Getter`, `@Setter`, `@Builder`, `@RequiredArgsConstructor`, `@NoArgsConstructor`, `@AllArgsConstructor`, `@Slf4j` where appropriate
- **MapStruct 1.5.x** for entity↔DTO mapping
- **Bean Validation** (`jakarta.validation.*`) on DTOs
- **OpenFeign** (Spring Cloud OpenFeign) for external HTTP client calls
- **PostgreSQL** as the assumed database (use PostgreSQL-compatible SQL in any native queries)
- **Maven** as the build tool

---

## 3. Project Structure (Standard Maven Layout)

Generate the complete project in standard Maven layout:

```
<service-name>/
├── pom.xml
├── src/
│   └── main/
│       ├── java/
│       │   └── com/<company>/<service>/
│       │       ├── <ServiceNameApplication>.java
│       │       ├── controller/
│       │       ├── service/
│       │       ├── repository/
│       │       ├── entity/
│       │       ├── dto/
│       │       │   ├── request/
│       │       │   └── response/
│       │       ├── mapper/
│       │       ├── exception/
│       │       ├── config/
│       │       ├── event/
│       │       │   ├── publisher/
│       │       │   └── listener/
│       │       ├── scheduler/
│       │       ├── filter/
│       │       └── util/
│       └── resources/
│           ├── application.yml
│           └── db/
│               └── migration/ (optional Flyway scripts if relevant)
```

All in-application import statements must follow the package convention above, so that a class's architectural layer is derivable from its fully-qualified class name alone.

---

## 4. File Size Constraint (CRITICAL)

- Generate **between 40 and 60 Java source files** (excluding `pom.xml`, `application.yml`, and migration scripts).
- **No Java source file may exceed 350 lines** — this is a hard upper limit.
  - If a class would naturally exceed 350 lines (e.g., a large service with many methods), split it into two or more classes with distinct, cohesive responsibilities (e.g., `LoanValidationService` and `LoanProcessingService`) so each file stays within the 350 line ceiling.
  - Files that are naturally short (e.g., a simple enum, a small utility class) may be as short as they need to be — there is no minimum line requirement.
  - Count every line toward the total: package declaration, imports, blank lines, Javadoc, annotations, field declarations, method bodies — everything counts.

---

## 5. Required Component Types

Every one of the following component types must appear at least once in the codebase. The minimum file counts below are floors, not targets — generate as many as the application realistically needs:

| Component Type | Minimum files | Package |
|---|---|---|
| `@RestController` classes | 3 | `controller` |
| `@Service` classes | 6 | `service` |
| `@Repository` interfaces | 4 | `repository` |
| `@Entity` classes | 6 | `entity` |
| DTO request classes | 4 | `dto/request` |
| DTO response classes | 4 | `dto/response` |
| `@Mapper` interfaces (MapStruct) | 3 | `mapper` |
| Custom exception classes | 3 | `exception` |
| `@ControllerAdvice` global handler | 1 | `exception` |
| `@Configuration` classes | 3 | `config` |
| Event publisher classes | 2 | `event/publisher` |
| `@KafkaListener` event listener classes | 2 | `event/listener` |
| `@Scheduled` task classes | 1 | `scheduler` |
| Filter or interceptor classes | 1 | `filter` |
| Utility/helper classes | 2 | `util` |
| Feign client interfaces | 2 | `config` or `service` |

---

## 6. Code Quality Requirements

### 6.1 Must Look Like Real Production Code

- Use realistic class names, field names, method names, and variable names reflecting the actual business domain. No `foo`, `bar`, `test`, `sample`, `dummy`, or placeholder names.
- No placeholder comments like `// TODO`, `// business logic here`, `// implement this`, or `// add logic`.
- Every method must have a complete, working body — no empty methods, no stub implementations.
- Business logic must be realistic: proper status transitions, validation rules with real thresholds, calculations with real formulas, collection processing with real filtering/mapping logic.

### 6.2 Layered Architecture and Interdependence

- Strict layered flow: `Controller` → `Service` → `Repository` / `Feign Client`
- Services must call repositories and/or Feign clients — no service that does nothing but delegate.
- Controllers must call services — no controller that contains business logic.
- Entities must have realistic JPA relationships (`@OneToMany`, `@ManyToOne`, `@ManyToMany` where appropriate) with proper `CascadeType`, `FetchType`, and `orphanRemoval` settings.
- At least **3 end-to-end flows** must span Controller → Service → Repository → (optionally) external Feign call or Kafka publish — these flows must be traceable by reading the method calls across files.

### 6.3 Mandatory Constructs Across the Codebase

The full codebase must collectively contain, at minimum:

- `if/else` branching: at least 20 distinct business-decision branches across all service and utility classes
- Loops (`for`, enhanced-for, stream operations): at least 15 distinct loop/stream usages
- `try/catch/finally` blocks: at least 10 distinct exception-handling blocks
- `@Transactional` methods: at least 6, with meaningful rollback conditions
- Custom exceptions thrown: at least 8 distinct throw sites across the codebase
- `@PrePersist` / `@PreUpdate` lifecycle callbacks: at least 3 entities with these
- Null checks and defensive guards: at least 15 distinct null/empty checks
- Status/state transitions: at least 2 entities with a status enum and transition logic in their service

### 6.4 External Integration Points

- At least **2 Feign client interfaces** making calls to named external services (invent realistic external service names, e.g., `credit-bureau-service`, `notification-service`, `identity-verification-service`)
- At least **2 Kafka topics** — one for publishing domain events, one for consuming external events — with realistic topic names and message schemas
- At least **1 `@Scheduled` task** that performs a real background operation (e.g., expiring stale records, sending reminder notifications, recalculating risk scores)

### 6.5 Configuration and Infrastructure

`application.yml` must include:
- Server port and application name
- PostgreSQL datasource configuration (with placeholder values)
- JPA/Hibernate settings (`ddl-auto: validate`, dialect, show-sql)
- Kafka bootstrap servers, producer, and consumer group settings
- Any custom application properties referenced in `@ConfigurationProperties` classes
- Logging levels

`pom.xml` must include all dependencies for the fixed technology stack in Section 2, with correct versions compatible with Spring Boot 3.2.x and Java 17.

---

## 7. Internal Consistency Requirements

- Every class referenced in an import statement must actually be defined somewhere in the codebase.
- Every method called on a service/repository/mapper from a controller or another service must exist in that called class with the exact signature used.
- Every entity relationship must be navigable: if `LoanApplication` has a `@OneToMany` to `LoanDocument`, then `LoanDocument` must have the corresponding `@ManyToOne` back-reference.
- Every enum referenced (e.g., `ApplicationStatus.DRAFT`) must be defined as a Java enum somewhere in the codebase.
- Every custom exception thrown (e.g., `throw new LoanNotFoundException(...)`) must be defined as a class in the `exception` package.
- Kafka topic names used in `@KafkaListener` must match topic names used in the corresponding publisher.
- Feign client method signatures must be consistent with how they are called from service classes.

---

## 8. Output Format

Generate the complete project and deliver it as a **downloadable zip file** named `<service-name>.zip` containing the full Maven project structure. The zip must be self-contained — unzipping it must produce the complete project directory ready for inspection.

Inside the zip, also include a plain text file at the project root named `PROJECT_SUMMARY.txt` in this format:

```
DOMAIN: <domain>
APPLICATION: <application name>
SERVICE: <service name>
BASE_PACKAGE: <base package>
TOTAL_FILES: <count of .java files>
FILES_IN_RANGE: <count of files with 300-350 lines>
FILES_OUT_OF_RANGE: <list any files outside 300-350 lines with their actual counts>
ENTITIES: <comma-separated list of entity class names>
ENUMS: <comma-separated list of enum class names>
KAFKA_TOPICS: <comma-separated list of topic names>
EXTERNAL_SERVICES: <comma-separated list of Feign client target service names>
```

---

## 9. Quality Self-Check (Before Emitting Any Code)

Before generating the first file, mentally plan the full class list, their responsibilities, and their interdependencies. Verify:

1. Every component type in Section 5 is covered at the planned file count.
2. Every end-to-end flow (Section 6.2) is traceable across the planned classes.
3. Every mandatory construct count (Section 6.3) is achievable across the planned classes.
4. No planned file will require more than 350 lines or fewer than 300.
5. All enum types, exception types, and Feign client interfaces referenced anywhere are planned as actual files.

Only begin emitting files after this mental plan is complete.
