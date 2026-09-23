# AI Tester Interview Notes

> A one-read refresher for the complete AITESTER repository and the AI concepts behind it.

## Table of Contents

1. [Project in 60 Seconds](#1-project-in-60-seconds)
2. [Repository Map](#2-repository-map)
3. [AI, ML, Deep Learning, and Generative AI](#3-ai-ml-deep-learning-and-generative-ai)
4. [Large Language Model Fundamentals](#4-large-language-model-fundamentals)
5. [Prompt Engineering](#5-prompt-engineering)
6. [Hallucination Control and Grounding](#6-hallucination-control-and-grounding)
7. [RAG, Fine-Tuning, Tools, and Agents](#7-rag-fine-tuning-tools-and-agents)
8. [AI Evaluation and Testing](#8-ai-evaluation-and-testing)
9. [AI for Software Testing](#9-ai-for-software-testing)
10. [Prompt Library in This Repository](#10-prompt-library-in-this-repository)
11. [Jira AI Test Case Generator](#11-jira-ai-test-case-generator)
12. [Codex Test Plan Skill](#12-codex-test-plan-skill)
    - [n8n Jira Agent Workflows](#12a-n8n-jira-agent-workflows)
13. [Playwright Automation Framework](#13-playwright-automation-framework)
14. [How to Test This AI System](#14-how-to-test-this-ai-system)
15. [Security and Responsible AI](#15-security-and-responsible-ai)
16. [Important Design Decisions and Trade-Offs](#16-important-design-decisions-and-trade-offs)
17. [Interview Questions and Short Answers](#17-interview-questions-and-short-answers)
18. [Quick Commands](#18-quick-commands)
19. [Glossary](#19-glossary)
20. [Five-Minute Final Recall](#20-five-minute-final-recall)

---

## 1. Project in 60 Seconds

AITESTER demonstrates how AI can support a QA/SDET workflow without replacing human judgment.

The repository contains:

- LLM anti-hallucination rules for evidence-based output.
- A structured prompt framework called RICE-POT.
- Reusable prompts for test cases, API testing, regression, and bug analysis.
- A Playwright automation framework created from a detailed AI prompt.
- A Streamlit application that fetches Jira requirements and generates test cases with Ollama or Groq.
- A Codex skill and a Flask B.L.A.S.T. agent that convert Jira tickets into draft test plans and stop for human review.
- n8n chat-agent workflow exports for fetching Jira issues and creating Jira subtasks.

### Interview-ready project pitch

> I built an AI-assisted QA repository that covers the full path from requirements to test artifacts. A user can provide a Jira issue key, the application fetches and normalizes the issue, dynamically loads a test-case template, builds a grounded prompt, and sends it to either a local Ollama model or Groq. I also created reusable prompt patterns, anti-hallucination controls, a human-reviewed test-plan skill, a Flask B.L.A.S.T. agent, n8n Jira agent workflows, and a Playwright framework that demonstrates how generated test ideas can become executable automation. The main design goals are traceability, modularity, provider independence, security, and human approval.

### The central idea

```text
Requirement evidence
       |
       v
Parse and structure context
       |
       v
Grounded prompt + output template
       |
       v
LLM generation
       |
       v
Validation and human review
       |
       v
Test plan, test cases, or automation
```

---

## 2. Repository Map

| Area | What it teaches |
|---|---|
| `chapter_01_LLM_Basics/` | Hallucination prevention, evidence, uncertainty, and self-validation. |
| `chapter_02_Prompt_Engineering/` | RICE-POT, reusable QA prompts, and prompt-to-code automation. |
| `chapter_03_Local_TestCase_Generator/` | A complete Jira + LLM + Streamlit application. |
| `chapter_04_JobKit/` | Resume-tailoring skill and job-search prompt assets. |
| `chapter_05_JobTracker/` | Local-first React job tracker with Kanban, dashboard metrics, import/export, and user guide. |
| `chapter_06_Branding_LinkedIn_Medium/` | LinkedIn and Medium content-generation skill with linting references. |
| `chapter_07_Basics_AI_Agents/` | Flask B.L.A.S.T. test-plan agent using Jira, deterministic gap analysis, and local Ollama. |
| `chapter_08_n8n_Agents/` | n8n chat-agent workflow exports for Jira issue lookup and subtask creation. |
| `.agents/skills/testplan-create/` | Agent instructions, requirement gap analysis, templates, and a human review gate. |
| `.agents/output/` | Example test-plan artifacts generated from Jira story `KAN-1`. |
| `PromptQuickReference.md` | A decision guide for selecting a prompt by QA task. |

### Learning sequence

1. Learn why LLMs hallucinate and how to ground them.
2. Learn to write structured prompts with RICE-POT.
3. Use task-specific QA prompt templates.
4. Understand the Playwright framework produced from a detailed prompt.
5. Study the Jira AI Test Case Generator architecture.
6. Study the Codex skill and B.L.A.S.T. agent with their mandatory human review gates.
7. Compare the code-first agent approach with the n8n visual workflow approach.

---

## 3. AI, ML, Deep Learning, and Generative AI

### Core definitions

| Term | Simple meaning | Example |
|---|---|---|
| Artificial Intelligence | The broad field of making machines perform tasks that normally require human intelligence. | Planning, language understanding, vision. |
| Machine Learning | A subset of AI where systems learn patterns from data. | Spam classification. |
| Deep Learning | A subset of ML using multi-layer neural networks. | Image recognition and modern LLMs. |
| Generative AI | Models that create new content based on learned patterns. | Text, code, images, audio. |
| Large Language Model | A generative model trained on large text corpora to predict and generate token sequences. | Gemma, Llama, GPT-style models. |

### Main learning types

- **Supervised learning:** learns from labeled input-output pairs.
- **Unsupervised learning:** discovers structure in unlabeled data.
- **Self-supervised learning:** creates learning signals from the data itself; next-token prediction is a common LLM example.
- **Reinforcement learning:** learns actions from rewards or penalties.
- **Semi-supervised learning:** combines a small labeled set with a larger unlabeled set.

### Traditional ML versus Generative AI

| Traditional ML | Generative AI |
|---|---|
| Usually predicts a class, score, or value. | Produces new text, code, images, or other content. |
| Output space is often constrained. | Output is open-ended and probabilistic. |
| Accuracy can often be checked against one label. | Quality needs several measures such as correctness, relevance, faithfulness, and format compliance. |
| Examples: fraud score, defect classification. | Examples: test generation, summarization, code generation. |

### Standard AI lifecycle

1. Define the business problem and success criteria.
2. Collect and govern data.
3. Prepare, clean, and label data where needed.
4. Select a model or service.
5. Train, fine-tune, or configure the model.
6. Evaluate against representative data.
7. Deploy with security and observability.
8. Monitor quality, cost, latency, drift, and failures.
9. Improve using reviewed feedback.

---

## 4. Large Language Model Fundamentals

### How an LLM works

An LLM does not retrieve a guaranteed fact from a database by default. It predicts the next likely token from the tokens already in context.

```text
Text -> Tokens -> Token embeddings -> Transformer layers -> Probability distribution -> Next token
```

The process repeats until the response ends or reaches a limit.

### Important concepts

#### Tokens

Tokens are pieces of text processed by a model. A token may be a word, part of a word, punctuation, or code fragment. Token count affects context capacity, latency, and cost.

#### Embeddings

Embeddings are numerical vectors that represent semantic meaning. Similar concepts tend to be closer in vector space. They are commonly used for semantic search and RAG retrieval.

#### Transformer

The transformer is the neural network architecture behind most modern LLMs. Its key mechanism is attention.

#### Self-attention

Self-attention lets each token assign importance to other tokens in the context. This helps the model understand relationships such as which requirement a test result refers to.

Simplified formula:

```text
Attention(Q, K, V) = softmax(QK^T / sqrt(d))V
```

- `Q` means query.
- `K` means key.
- `V` means value.
- The result is a weighted combination of relevant token information.

#### Context window

The context window is the maximum amount of input and output the model can consider in one request. Large Jira tickets, templates, and conversation history consume this space.

#### Parameters

Parameters are learned numerical weights inside the model. More parameters can increase capability, but model quality also depends on training data, architecture, tuning, and inference setup.

### Training stages

| Stage | Purpose |
|---|---|
| Pretraining | Learn language and broad patterns from large datasets, usually through next-token prediction. |
| Supervised fine-tuning | Train on curated instruction-response examples. |
| Preference alignment | Make behavior better match human preferences using methods such as RLHF or DPO. |
| Inference | Use the trained model to generate a response for a new prompt. |

### Important inference settings

| Setting | Effect |
|---|---|
| Temperature | Lower values make output more consistent; higher values increase variation. |
| Top-p | Samples from the smallest token set whose cumulative probability reaches `p`. |
| Max tokens | Limits generated response length. |
| Stop sequence | Ends generation when a defined sequence appears. |
| Seed | Can improve repeatability when the provider supports it, but full determinism is not always guaranteed. |

For test-case generation, low temperature is usually preferred because consistency and evidence matter more than creativity. This repository uses `temperature: 0.2` for Groq.

### Why LLM output is nondeterministic

- Generation samples from token probabilities.
- Model/provider versions may change.
- Prompt order and wording can affect attention.
- Retrieved context can change.
- Even small input differences may alter later tokens.

Therefore, AI testing should validate ranges, rules, schemas, and quality dimensions rather than relying only on exact text matching.

---

## 5. Prompt Engineering

Prompt engineering is the design of instructions and context that guide a model toward useful, constrained, and testable output.

### Anatomy of a strong prompt

- **Role:** who the model should act as.
- **Task:** the exact objective.
- **Context:** source information required to do the task.
- **Constraints:** what the model must and must not do.
- **Examples:** demonstrations of the expected pattern.
- **Output format:** table, JSON schema, Markdown, code, and so on.
- **Quality check:** instructions to verify completeness and grounding.

### RICE-POT framework

The repository uses RICE-POT:

| Letter | Meaning | Question answered |
|---|---|---|
| R | Role | Who should the model act as? |
| I | Instructions | What exactly must it do? |
| C | Context | What background and source material does it need? |
| E | Example | What does good input/output look like? |
| P | Parameters | What technical and business limits apply? |
| O | Output | What exact structure must be returned? |
| T | Tone | How should the response sound? |

### Prompting techniques

| Technique | Meaning | QA example |
|---|---|---|
| Zero-shot | Give instructions without an example. | Generate negative tests from this story. |
| One-shot | Provide one example. | Show one correctly formatted test case. |
| Few-shot | Provide several examples. | Demonstrate P0, P1, and P2 scenarios. |
| Role prompting | Assign relevant expertise. | Act as a senior API test engineer. |
| Context grounding | Supply authoritative source material. | Include Jira description and acceptance criteria. |
| Structured output | Demand a schema or template. | Return a Markdown table with fixed columns. |
| Decomposition | Split a complex task into stages. | Extract facts, identify gaps, then draft tests. |
| Constraint prompting | State explicit boundaries. | Do not invent undocumented status codes. |

### Good prompt pattern from this project

```text
ROLE:
You are a Senior QA Engineer.

TASK:
Generate test cases from the Jira requirements.

REQUIREMENTS:
<normalized Jira content>

TEMPLATE:
<template loaded from disk>

CONSTRAINTS:
- Use only supplied requirements.
- Do not invent behavior.
- State "Not specified" for missing information.
- Cover supported positive and negative paths.
- Follow the template exactly.
```

### Prompt design best practices

- Put authoritative context close to the task.
- Separate instructions, evidence, and examples with clear headings or delimiters.
- Define what to do when information is absent.
- Ask for machine-validated output such as JSON when another system consumes it.
- Keep prompts concise for smaller local models.
- Version prompts like code and evaluate changes against a fixed dataset.
- Treat user and retrieved text as untrusted data, not system instructions.
- Do not ask a model for hidden chain-of-thought. Request concise reasons, evidence, or a decision summary instead.

### Common prompt failures

- Vague task or undefined audience.
- Conflicting instructions.
- Too much irrelevant context.
- Missing output schema.
- Examples that conflict with requirements.
- Asking for exact facts without supplying a source.
- Assuming the model will identify missing information automatically.
- Evaluating one successful response and assuming the prompt is reliable.

---

## 6. Hallucination Control and Grounding

A hallucination is output that sounds plausible but is unsupported, incorrect, or fabricated.

### Why hallucinations happen

- The model predicts likely language rather than checking truth automatically.
- Required facts are missing from the context.
- The prompt rewards completeness more than honesty about uncertainty.
- Conflicting or noisy context confuses the model.
- The model relies on patterns learned during training.
- High sampling randomness increases variation.

### Repository anti-hallucination workflow

1. Extract verifiable facts.
2. List missing or unknown information.
3. Generate only from verified facts.
4. Self-check for unsupported statements and contradictions.

Required output sections are:

- Verified Facts
- Missing / Unknown Information
- Generated Output
- Self-Validation Check

### Practical controls

- Ground the response in PRDs, API documentation, Jira, logs, screenshots, and test data.
- Require traceability from each scenario to a source or identified gap.
- Use explicit uncertainty labels such as `Not specified`.
- Lower temperature for factual QA tasks.
- Retrieve only relevant context.
- Validate output structure programmatically.
- Verify critical facts with deterministic tools or APIs.
- Add a human review gate for release-impacting artifacts.
- Monitor unsupported-claim and format-failure rates.

### Grounded does not automatically mean correct

The source itself can be incomplete, outdated, or contradictory. A good QA assistant must surface those gaps instead of silently treating all supplied text as true and complete.

---

## 7. RAG, Fine-Tuning, Tools, and Agents

### Comparison

| Approach | Best use | Knowledge freshness | Main limitation |
|---|---|---|---|
| Prompting | Define a task and behavior quickly. | Only what is in the prompt/model. | Limited context and reliability. |
| RAG | Answer from changing private documents. | High if retrieval source is current. | Retrieval quality controls answer quality. |
| Fine-tuning | Teach stable style, format, or specialized behavior. | Static until retrained. | Requires quality data and evaluation. |
| Tool use | Perform deterministic actions or fetch live data. | As fresh as the tool response. | Tool permissions and failures must be managed. |
| Agent workflow | Plan and use multiple tools across steps. | Depends on tools and context. | More complexity, cost, and failure modes. |

### Retrieval-Augmented Generation (RAG)

RAG retrieves relevant chunks from an external knowledge source and inserts them into the model context.

```text
Documents -> Chunk -> Embed -> Vector index
                              |
Question -> Embed -> Retrieve relevant chunks -> Prompt LLM -> Answer with evidence
```

Key RAG choices:

- Chunk size and overlap.
- Embedding model.
- Vector database/index.
- Metadata filtering.
- Number of chunks (`top-k`).
- Reranking.
- Citation and faithfulness checks.

RAG is useful when requirements, product documentation, or policies change often.

### Fine-tuning

Fine-tuning changes model weights using a curated dataset. It is useful for stable output behavior, domain language, or repeated task patterns. It is usually not the right tool for frequently changing Jira facts.

Important repository clarification: `source/finetuned_Prompt.md` is a refined prompt specification. This repository does not train or fine-tune an LLM's weights.

### Tools and function calling

Tools let a model request deterministic operations such as:

- Fetch a Jira issue.
- Search documentation.
- Run tests.
- Read a template.
- Save an approved artifact.

Tool results should be validated before they are added to context. The model should receive the minimum permissions needed.

### AI agents

An agent combines a model with instructions, tools, state, and a loop that decides what to do next.

```text
Goal -> Observe -> Decide -> Use tool -> Observe result -> Continue or stop
```

A production agent needs:

- Clear scope and stopping conditions.
- Tool schemas and permission boundaries.
- Retry, timeout, and error policies.
- State or memory management.
- Audit logs and traceability.
- Human approval before sensitive or irreversible actions.

The repository's `testplan-create` skill is an agent workflow because it defines when to activate, what sources to fetch, how to analyze them, which template to use, and where to stop for review.

---

## 8. AI Evaluation and Testing

AI quality is multi-dimensional. One metric is not enough.

### Evaluation dimensions

| Dimension | Question |
|---|---|
| Correctness | Is the output factually and logically correct? |
| Faithfulness | Is every claim supported by supplied evidence? |
| Relevance | Does it answer the requested task? |
| Completeness | Does it cover all required items? |
| Format compliance | Does it match the requested schema/template? |
| Consistency | Is quality stable across repeated runs? |
| Safety | Does it avoid harmful or restricted output? |
| Privacy | Does it avoid exposing sensitive data? |
| Latency | Does it respond within the target time? |
| Cost | Is token/provider usage acceptable? |

### Evaluation methods

- **Deterministic checks:** JSON schema, required headings, valid priorities, unique test IDs.
- **Golden dataset:** representative inputs with reviewed expected properties.
- **Human review:** experts score usefulness, correctness, and missed risk.
- **Semantic similarity:** measures meaning similarity, but does not prove factual correctness.
- **LLM-as-judge:** scalable rubric-based scoring, but judge bias and inconsistency must be calibrated.
- **A/B evaluation:** compare two prompts/models using the same test set.
- **Online monitoring:** observe production feedback, failures, latency, and cost.

### Common classification metrics

```text
Precision = TP / (TP + FP)
Recall    = TP / (TP + FN)
F1        = 2 * Precision * Recall / (Precision + Recall)
Accuracy  = Correct predictions / All predictions
```

- Precision matters when false positives are expensive.
- Recall matters when missing a real issue is expensive.
- F1 balances precision and recall.
- Accuracy can mislead on imbalanced datasets.

### Evaluation plan for generated test cases

1. Build a dataset of Jira stories across feature types and requirement quality levels.
2. Have QA reviewers define expected coverage and known gaps.
3. Run each prompt/model multiple times.
4. Check format and traceability automatically.
5. Score correctness, unsupported assumptions, coverage, duplication, and usefulness.
6. Compare local and cloud providers on quality, latency, privacy, and cost.
7. Regression-test every prompt, template, parser, or model change.

### Useful project metrics

- Jira key extraction success rate.
- Jira fetch success/error rate.
- Template-compliance rate.
- Unsupported-claim rate.
- Requirement-to-test traceability coverage.
- Duplicate test-case rate.
- Human acceptance/edit rate.
- P50/P95 generation latency.
- Provider fallback rate.
- Cost per generated artifact.

---

## 9. AI for Software Testing

### Strong use cases

- Convert requirements into draft test scenarios.
- Identify missing acceptance criteria and edge cases.
- Generate test data ideas.
- Draft API, UI, negative, boundary, and regression tests.
- Summarize logs and failure evidence.
- Convert rough notes into structured bug reports.
- Classify defects using a defined rubric.
- Suggest automation skeletons.
- Prioritize regression scope from change and risk information.

### What must remain under human control

- Requirement interpretation and business correctness.
- Approval of assumptions.
- Security and compliance decisions.
- Final test-plan sign-off.
- Whether generated coverage is sufficient for release.
- Validation that automation assertions test the intended behavior.

### Core test design techniques

| Technique | Purpose | Example |
|---|---|---|
| Equivalence partitioning | Group inputs expected to behave similarly. | Valid and invalid email classes. |
| Boundary value analysis | Test edges around allowed limits. | `min-1`, `min`, `max`, `max+1`. |
| Decision table | Cover combinations of conditions and outcomes. | Role, account state, and authentication method. |
| State transition testing | Verify behavior between states. | Logged out -> authenticating -> logged in -> locked. |
| Pairwise testing | Reduce combinations while covering interacting pairs. | Browser, device, language, and user role. |
| Error guessing | Use experience to target likely failures. | Whitespace, duplicate submission, stale session. |
| Risk-based testing | Prioritize by probability and impact. | Authentication receives P0 coverage. |

### Traceability

Every generated scenario should map to one of:

- An explicit requirement or acceptance criterion.
- A design attachment or API contract.
- A clearly labeled gap/question.
- A stated non-functional standard approved for the project.

This prevents a long test list from creating a false impression of coverage.

---

## 10. Prompt Library in This Repository

### Basic test prompts

| Prompt | Use it for |
|---|---|
| Basic Test Case Generation | Fast functional test cases from a story or requirement. |
| PRD to Test Cases | Broad functional, negative, boundary, and edge coverage. |
| API Test Case Generation | Endpoint-specific cases using documented methods and status codes. |
| Negative Test Cases Only | Invalid input, missing data, and failure paths. |
| Regression Test Suite | Release-focused end-to-end regression planning. |

### API testing prompts

| Prompt | Main focus |
|---|---|
| REST API Test Suite | Full endpoint coverage. |
| API Validation Tests | Required fields, types, formats, nulls, and boundaries. |
| API Authentication Tests | Missing, invalid, expired, or insufficient authorization. |
| API Contract Testing | Response schema, required fields, types, and nullability. |
| API Performance Scenarios | Baseline, load, stress, spike, and endurance. |
| API Error Handling | 4xx/5xx behavior, malformed input, timeout, and dependency failure. |

### Bug prompts

| Prompt | Main focus |
|---|---|
| Bug Report from Evidence | Build a report only from logs, screenshots, and observed facts. |
| Bug Classification | Assign severity and priority with justification. |
| Bug Analysis | Separate facts, hypotheses, missing evidence, and next checks. |
| Convert Notes to Bug Report | Turn informal notes into a consistent defect format. |

The [Prompt Quick Reference](./PromptQuickReference.md) is the fastest way to choose among these templates.

---

## 11. Jira AI Test Case Generator

Location: [`chapter_03_Local_TestCase_Generator/jira-ai-testcase-generator/`](./chapter_03_Local_TestCase_Generator/jira-ai-testcase-generator/)

### Purpose

The Streamlit application accepts a natural-language request such as:

```text
Create test cases for PROJ-123
```

It extracts the issue key, fetches Jira, converts the issue to clean context, loads an output template, invokes an LLM, and displays the result.

### Architecture

```text
app.py
  |
  +-- extract Jira key with regex
  +-- jira_service.fetch_issue()
  +-- jira_parser.parse_issue()
  +-- template_loader.load_template()
  +-- prompt_builder.build_test_case_prompt()
  +-- llm_service.generate_response()
          |
          +-- ollama_service.generate()
          +-- groq_service.generate()
  |
  +-- render result or a user-safe error
```

### Responsibilities by file

| File | Responsibility |
|---|---|
| `app.py` | Streamlit UI and end-to-end orchestration. |
| `pages/settings.py` | Configuration form and connection tests. |
| `services/jira_service.py` | Jira REST API communication. |
| `services/ollama_service.py` | Local Ollama model communication. |
| `services/groq_service.py` | Groq chat-completion communication. |
| `services/llm_service.py` | Provider selection and fallback. |
| `utils/config_manager.py` | Load/save local configuration and mask secrets. |
| `utils/jira_parser.py` | Normalize Jira fields and Atlassian Document Format. |
| `utils/template_loader.py` | Read the output template on every request. |
| `utils/prompt_builder.py` | Combine role, requirements, template, and constraints. |
| `templates/test_case_template.md` | Source of truth for generated structure. |

### End-to-end flow

1. User enters a request in Streamlit.
2. Regex extracts the first valid-looking Jira issue key.
3. Configuration is loaded from local environment settings.
4. Jira issue JSON is fetched through Jira REST API v3.
5. The parser handles missing fields and converts ADF description nodes to text.
6. Acceptance criteria come from a configured custom field or a recognized description section.
7. Missing information is represented as `Not specified`.
8. The test-case template is loaded dynamically from disk.
9. A grounded prompt is assembled.
10. The provider layer calls Ollama or Groq.
11. If Ollama is unavailable and Groq is configured, the service can fall back to Groq.
12. Streamlit displays the provider used and the generated Markdown.

### Jira key extraction

The app uses a regular expression shaped like:

```regex
\b([A-Z][A-Z0-9]{1,9}-\d{1,6})\b
```

It accepts keys such as `ABC-123` and rejects ordinary text without the project-number pattern.

### Jira parsing

Jira Cloud descriptions may use Atlassian Document Format (ADF), which is nested JSON. The parser recursively walks the ADF tree and collects text nodes. It also tolerates plain strings and missing optional fields.

This is important because an integration should not assume every Jira project has identical field configuration.

### Provider abstraction

`llm_service.py` hides provider-specific details from the UI and prompt builder.

Benefits:

- The application logic is not coupled to one model vendor.
- A provider can be replaced without changing Jira parsing.
- Fallback behavior is centralized.
- Provider-specific errors become safe application errors.

### Ollama versus Groq

| Ollama | Groq |
|---|---|
| Runs a model locally. | Calls a hosted cloud API. |
| Better privacy and no per-request vendor dependency. | Usually faster on supported hosted models. |
| Limited by local CPU/GPU and memory. | Requires network access and an API key. |
| Model installation and service health are local responsibilities. | Usage limits, provider availability, and cost apply. |

### Why the template is external

- QA can change output format without changing Python code.
- It creates separation between business format and application logic.
- Reloading per request makes template updates immediately effective.
- The same pipeline can support different clients or test types with different templates.

### Current strengths

- Modular service and utility layers.
- Local-first inference with cloud fallback.
- Dynamic output template.
- Missing-field tolerance.
- User-safe service errors and timeouts.
- Secret masking in the settings UI.
- Low temperature for stable QA output.

### Production improvements to discuss in an interview

- Add unit, integration, and end-to-end tests.
- Validate generated output against a schema instead of trusting Markdown alone.
- Persist generation history and reviewed versions.
- Add requirement-to-test traceability IDs.
- Add retries with exponential backoff for transient failures.
- Use structured logging, request IDs, and metrics.
- Add token/context size controls for large Jira issues.
- Sanitize Jira content against prompt injection.
- Add explicit user confirmation before sending private Jira data to a cloud provider.
- Use a secret manager rather than writing production secrets to a local file.
- Cache safe, stable lookups while preventing stale ticket data.
- Add model and prompt version information to every artifact.

---

## 12. Codex Test Plan Skill

Location: [`.agents/skills/testplan-create/`](./.agents/skills/testplan-create/)

### Skill versus normal prompt

A prompt handles one model request. A skill packages a repeatable workflow with activation rules, required references, tools, guardrails, output shape, and stopping conditions.

### Workflow

1. Detect a Jira-based test-planning request.
2. Fetch the ticket and relevant attachments.
3. Capture description, acceptance criteria, components, links, and release context.
4. Score the requirement using the gap-analysis checklist.
5. Convert every ambiguous or missing item into a question.
6. Fill the standard test-plan template.
7. Prioritize scenarios as P0, P1, or P2.
8. Stop at the Human Review Gate.

### Requirement gap categories

- Functional behavior and testable acceptance criteria.
- Negative paths, boundaries, empty states, and workflows.
- Data, environments, dependencies, and preconditions.
- Performance, security, accessibility, localization, and observability.
- Regression impact, compatibility, migration, and rollback.
- Clear wording, consistent terms, and matching designs.

### Why the human review gate matters

- AI cannot approve business assumptions.
- Missing acceptance criteria are findings, not permission to invent behavior.
- Test priority depends on business impact and risk.
- A named owner must accept scope and residual risk.
- Review creates accountability and an audit point.

### KAN-1 example

The generated example covers a VWO/Wingify login page. It uses the Jira description and design attachment, identifies missing acceptance criteria and non-functional details, creates prioritized scenarios, and remains marked as draft pending human approval.

VWO is a digital experience optimization platform used for A/B testing, feature experimentation, behavior analytics, personalization, and user feedback.

---

## 12A. n8n Jira Agent Workflows

Location: [`chapter_08_n8n_Agents/`](./chapter_08_n8n_Agents/)

Chapter 8 shows a visual low-code version of Jira agent automation using n8n workflow exports.

| Workflow | Main nodes | Purpose |
|---|---|---|
| `JiraTicket Fetching.json` | Chat Trigger, AI Agent, OpenAI Chat Model, Simple Memory, Jira Tool | Lets a user ask for a Jira ticket in chat; the agent extracts the issue key and uses the Jira tool to fetch the issue. |
| `Create JiraTicket.json` | Chat Trigger, AI Agent, OpenAI Chat Model, Simple Memory, Jira Tool | Lets a user describe a subtask; the agent fills summary, description, and parent issue key, then creates a Jira subtask. |

### Why it matters

- It demonstrates a low-code agent pattern beside the code-first Streamlit, Flask, and Codex-skill approaches.
- It makes tool wiring visible: trigger, model, memory, and Jira action are separate workflow nodes.
- It is useful for demos and internal workflow prototypes where n8n is already used.

### Safety note

The fetch workflow is read-oriented. The create workflow is write-capable, so it should use least-privilege Jira credentials, a sandbox project during testing, and human review of AI-filled Jira fields before use on real delivery work.

---

## 13. Playwright Automation Framework

Location: [`chapter_02_Prompt_Engineering/OrangePlaywrightFramework/`](./chapter_02_Prompt_Engineering/OrangePlaywrightFramework/)

### Why it belongs in an AI repository

The framework demonstrates prompt-to-code engineering. A detailed RICE-POT prompt defined architecture, mandatory constraints, test examples, artifacts, parallelism, and a release gate. The generated implementation then had to be run and verified like any other software.

AI-generated code is a draft, not proof of correctness.

### Architecture

```text
Tests
  |
  v
Base fixture and common helpers
  |
  v
Page Objects
  |
  v
Central XPath selectors
  |
  v
OrangeHRM UI

Each test also produces logs, a PASS/FAIL screenshot, traces on failure,
and a custom HTML report with a 99% pass-rate gate.
```

### Page Object Model (POM)

POM separates test intent from page interaction details:

- `Tests/` describe behavior and assertions.
- `Pages/` expose reusable actions.
- `Selectors/` centralize locators.
- `Base/baseTest.js` owns setup, teardown, and common helpers.

Benefits include reuse, readability, easier maintenance, and reduced locator duplication.

### Custom fixture

The extended Playwright fixture runs for every test:

1. Initialize logging and the screenshot run folder.
2. Open the configured base URL.
3. Wait for the login form.
4. Expose common actions to the test.
5. Capture a PASS or FAIL screenshot during teardown.
6. Log failure details where available.

### Execution behavior

| Mode | Workers | Retries | Use |
|---|---:|---:|---|
| Headless | 4 | 2 | Fast parallel execution. |
| Headed | 1 | 0 | Visible debugging with less noise. |

### Test coverage in the repository

- Valid login reaches the dashboard.
- Invalid login displays an error.
- Admin user search returns results.
- PIM employee search returns results.

### Artifacts

- Timestamped logs.
- Timestamped PASS/FAIL screenshots.
- Playwright trace retained on failure.
- JSON test results.
- Custom HTML summary report.
- Automatic cleanup that retains the latest five runs.

### Release gate

```text
Pass rate = passed tests / total tests * 100
```

The custom reporter marks the run `APPROVED` at or above 99%; otherwise it marks it `NOT APPROVED`.

Important interview nuance: a pass-rate threshold alone is not sufficient for release. A robust gate should also consider blocked tests, flaky retries, unresolved critical defects, required P0 coverage, environment health, and risk acceptance.

### Automation improvements to discuss

- Prefer user-facing Playwright locators where project rules allow; XPath-only was a prompt requirement, not a universal best practice.
- Avoid logging usernames or other identity data.
- Use worker-safe artifact state for parallel execution.
- Replace fixed demo test data with isolated, controlled test accounts.
- Validate search results, not only that row count is greater than zero.
- Add API-assisted test setup and cleanup.
- Track retry/flaky-test status separately from clean passes.

---

## 14. How to Test This AI System

### Unit tests

- Jira key regex accepts valid keys and rejects invalid forms.
- ADF parser handles text, nested content, missing description, and malformed structures.
- Acceptance criteria extraction recognizes supported headings.
- Template loader reports missing or unreadable files.
- Prompt builder includes the ticket, template, and constraints exactly once.
- Configuration masks secrets and preserves existing secret values when fields are blank.
- Provider selection chooses the configured provider.

### Integration tests

- Jira client handles 200, 401/403, 404, 429, 5xx, timeout, and connection failure.
- Ollama client handles missing model, unavailable service, malformed JSON, and empty output.
- Groq client handles authentication, rate limit, unavailable model, malformed JSON, and empty output.
- Fallback occurs only under the intended conditions.
- Realistic ADF Jira responses become correct normalized context.

### End-to-end tests

- User enters a valid Jira request and receives template-compliant test cases.
- Missing Jira key shows a helpful message.
- Missing configuration does not crash the app.
- Provider used is shown accurately.
- Settings persist non-secret values and keep masked secrets private.
- A missing template produces a recoverable error.

### AI-output tests

- No requirement is invented.
- Missing data is labeled `Not specified`.
- Required columns are present.
- Test IDs are unique.
- Priorities use allowed values.
- Positive and supported negative paths are covered.
- Expected results are observable and testable.
- Duplicate or contradictory scenarios stay below an agreed threshold.
- Every test maps to a requirement or explicit gap.

### Prompt-injection tests

Put malicious instructions inside a Jira description, for example an instruction to ignore the template or reveal configuration. Verify that the system treats the Jira content as evidence only and continues to follow the trusted application instructions.

### Non-functional tests

- Latency for small, medium, and large tickets.
- Concurrent users and provider rate limits.
- Maximum context behavior.
- Memory/CPU use for local models.
- Accessibility of Streamlit controls.
- Browser compatibility.
- Recovery after provider or network interruption.
- Log redaction and data retention.

---

## 15. Security and Responsible AI

### Main risks

| Risk | Example | Control |
|---|---|---|
| Secret exposure | Token appears in code, logs, UI, or Git. | Environment variables, masking, secret manager, scanning. |
| Prompt injection | Jira text asks the model to ignore rules. | Separate trusted instructions from untrusted content and validate output. |
| Data leakage | Private Jira text is sent to an external model. | Consent, data classification, local model, minimization, provider policy. |
| Excessive permissions | Agent can access more Jira data than needed. | Least-privilege service account and scoped tools. |
| Unsafe write action | n8n create workflow writes an incorrect Jira subtask. | Sandbox first, least-privilege credentials, and human review of AI-filled fields. |
| Hallucination | Model invents an acceptance criterion. | Grounding, traceability, automated checks, human review. |
| Bias | Generated coverage ignores some users or accessibility needs. | Diverse test set, bias review, explicit accessibility criteria. |
| Unsafe automation | Generated code changes systems unexpectedly. | Sandbox, review, restricted credentials, approval gates. |

### Security checklist

- Never commit real secrets in `.env`, examples, source, logs, or documents.
- Use placeholders in sample configuration.
- Rotate any secret that may have been exposed.
- Use HTTPS and certificate validation.
- Apply least privilege to Jira and provider access.
- Set request timeouts and bounded retries.
- Avoid returning raw provider errors to users.
- Redact sensitive fields from logs and traces.
- Treat n8n exported credentials as environment-specific; reconnect your own Jira/OpenAI credentials after import and never publish real credential IDs as secrets.
- Keep write-capable workflows disabled until their Jira project, issue type, parent issue handling, and approval rules are verified.
- Define retention and deletion rules for prompts and responses.
- Record model, prompt, source, and review versions for auditability.

### Responsible AI principles

- **Fairness:** check performance across relevant user groups.
- **Privacy:** minimize and protect personal or confidential data.
- **Transparency:** disclose AI involvement and known limitations.
- **Accountability:** keep a human owner for final decisions.
- **Reliability:** test normal, edge, and failure conditions.
- **Safety:** constrain harmful output and risky tool actions.
- **Explainability:** provide evidence and concise reasons where needed.

---

## 16. Important Design Decisions and Trade-Offs

### Why use a local model?

Local inference improves privacy, offline availability, and cost predictability. The trade-offs are hardware usage, setup, slower inference, and potentially lower output quality than a larger hosted model.

### Why keep Groq fallback?

Fallback improves availability and may reduce latency. The trade-offs are network dependency, external data processing, API limits, and secret management.

### Why use Streamlit?

Streamlit provides a fast Python UI for prototypes and internal tools. It reduces frontend work, but offers less control than a dedicated frontend/backend architecture for large production systems.

### Why normalize Jira before prompting?

Raw Jira JSON is noisy and inconsistent. Normalization reduces tokens, isolates useful fields, makes missing values explicit, and gives the LLM a stable input structure.

### Why use an external template?

It separates code from output policy. QA teams can update columns and formatting without changing model integration code.

### Why use low temperature?

QA artifacts require consistency and traceability. Creativity is less valuable than repeatable compliance, so a low temperature is appropriate.

### Why require human review?

Requirements are often ambiguous, and an LLM cannot own business risk. Human review confirms assumptions, scope, priorities, and release impact.

### Why not use RAG here?

The current use case fetches one known Jira ticket directly, so deterministic API retrieval is simpler. RAG becomes useful when the answer must combine many tickets, product documents, policies, and historical defects.

### Why not fine-tune first?

Prompting and templates are cheaper and easier to change. Fine-tuning should follow only after enough reviewed examples show a stable behavior gap that prompting or RAG cannot solve.

### Why add n8n workflows?

n8n shows the same agent idea as a visual workflow: chat trigger, model, memory, and Jira tool. The trade-off is fast workflow assembly versus less custom control than a dedicated app, especially for validation, tests, versioning, and approval gates.

---

## 17. Interview Questions and Short Answers

### 1. What problem does this project solve?

It reduces the manual effort of converting Jira requirements into structured QA artifacts while preserving grounding, traceability, and human approval.

### 2. How do you prevent the model from inventing requirements?

I provide only authoritative Jira context, explicitly forbid unsupported assumptions, represent missing data as `Not specified`, require traceability, use low randomness, validate the output, and keep a human review gate.

### 3. Why is prompt engineering important?

LLMs are sensitive to context and instruction quality. A structured prompt defines the role, task, evidence, constraints, and output format, which improves consistency and makes the behavior testable.

### 4. Explain RICE-POT.

It stands for Role, Instructions, Context, Example, Parameters, Output, and Tone. It is a checklist for turning an unclear request into a complete prompt specification.

### 5. What is the difference between RAG and fine-tuning?

RAG supplies current external knowledge at inference time. Fine-tuning changes model weights to teach stable behavior or patterns. Use RAG for changing facts and fine-tuning for repeated behavior that prompting cannot reliably produce.

### 6. Is this project using RAG?

No. It directly fetches one Jira issue and places normalized content in the prompt. That is tool-based grounding, not vector retrieval.

### 7. Is `finetuned_Prompt.md` model fine-tuning?

No. It is a refined prompt document. No model weights are trained in this repository.

### 8. Why use Ollama?

Ollama runs the model locally, which supports privacy and local development. The trade-off is dependence on local compute and model availability.

### 9. Why add a provider abstraction?

It decouples business logic from a specific LLM API, centralizes fallback and errors, and makes adding or replacing providers easier.

### 10. How does fallback work?

The provider service tries the configured provider. When local Ollama is selected but unavailable, it can use Groq if Groq is configured. Production fallback should also respect data-sharing policy and user consent.

### 11. How are missing Jira fields handled?

The parser safely defaults optional values, supports ADF and plain text, and marks absent information as `Not specified` instead of failing or inventing content.

### 12. Why load the template dynamically?

The output contract can change independently of code, and updates take effect on the next request without restarting the application.

### 13. How would you evaluate generated test cases?

I would use a reviewed golden dataset and score correctness, grounding, coverage, duplication, format compliance, traceability, latency, and human acceptance. Deterministic checks should be automated; subjective quality should use calibrated reviewers.

### 14. Why is exact string matching weak for LLM testing?

Different wording can be equally correct. I validate required facts, forbidden claims, structure, semantic properties, and rubric scores instead of requiring one exact response.

### 15. What is prompt injection?

It is untrusted content that tries to override trusted model instructions. In this project, a Jira description could contain such text, so it must be clearly delimited as data and the output must be validated.

### 16. How would you secure the application?

Use a secret manager, least-privilege Jira access, HTTPS, safe errors, redacted logs, prompt-injection controls, data minimization, dependency scanning, retention rules, and explicit approval before cloud processing.

### 17. What does temperature do?

It changes sampling randomness. Lower temperature gives more stable output, which is preferred for test artifacts; higher temperature may help brainstorming but increases variation.

### 18. What is a context window?

It is the token budget available for the prompt and generated answer. Large tickets and templates may require filtering, summarization, or chunking.

### 19. What makes an AI agent different from a chatbot?

An agent can choose and use tools across multiple steps, maintain state, inspect results, and stop according to workflow rules. A basic chatbot mainly produces a direct response.

### 20. Why is the test plan never automatically final?

AI cannot confirm business intent or accept risk. The draft surfaces gaps, while a human owner approves assumptions, scope, and priorities.

### 20A. How are the n8n workflows different from the Flask agent?

The Flask agent is a custom coded pipeline with deterministic normalization, gap analysis, artifact rendering, and a review gate. The n8n workflows are visual chat agents that wire together model, memory, and Jira tool nodes for quick issue lookup or subtask creation.

### 21. How does the Playwright framework relate to AI?

It was specified through a structured RICE-POT prompt and demonstrates that generated code still needs architectural review, execution, assertions, and maintenance.

### 22. What is POM and why use it?

Page Object Model separates test intent from page selectors and actions. It reduces duplication and localizes UI maintenance.

### 23. Are retries always good?

No. Retries can reduce noise from transient failures but can hide flaky tests. Reports should distinguish a clean pass from a pass after retry.

### 24. Is a 99% pass rate enough for release?

No. Release decisions should also consider critical failures, blocked tests, P0 coverage, flakiness, defect severity, environment health, and accepted residual risk.

### 25. What would you build next?

I would add automated tests, structured output validation, prompt/model versioning, generation history, evaluation datasets, observability, prompt-injection defenses, and approval-aware cloud fallback.

---

## 18. Quick Commands

### Run the Jira AI Test Case Generator

```bash
cd chapter_03_Local_TestCase_Generator/jira-ai-testcase-generator
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Default local Streamlit address:

```text
http://localhost:8501
```

### Check Ollama

```bash
ollama list
curl http://localhost:11434/api/tags
```

### Run the Playwright framework

```bash
cd chapter_02_Prompt_Engineering/OrangePlaywrightFramework
npm install
npx playwright install chromium
npm test
```

### Useful Playwright commands

```bash
npm test -- --headed
npm test -- Tests/base/loginUsingInvalidCredential.js
npm test -- Tests/admin/
npm test -- --debug
npm run test:report
```

### Import n8n Jira agent workflows

Import these files from the n8n UI, then reconnect your own OpenAI and Jira credentials:

```text
chapter_08_n8n_Agents/JiraTicket Fetching.json
chapter_08_n8n_Agents/Create JiraTicket.json
```

Keep the create workflow disabled until it has been tested against a sandbox Jira project.

### Configuration names to remember

Jira/LLM application:

- `JIRA_BASE_URL`
- `JIRA_EMAIL`
- `JIRA_API_TOKEN`
- `OLLAMA_BASE_URL`
- `OLLAMA_MODEL`
- `GROQ_API_KEY`
- `GROQ_MODEL`
- `AI_PROVIDER`
- `ACCEPTANCE_CRITERIA_FIELD_ID`

Playwright framework:

- `BASE_URL`
- `VALID_USERNAME`
- `VALID_PASSWORD`
- `INVALID_USERNAME`
- `INVALID_PASSWORD`
- `PASS_RATE_THRESHOLD`

n8n workflows:

- OpenAI chat model credentials
- Jira Software Cloud credentials
- Jira project ID
- Jira issue type ID
- Jira assignee account ID
- Parent issue key

Never place real secret values in notes, source control, examples, screenshots, or logs.

---

## 19. Glossary

| Term | Meaning |
|---|---|
| ADF | Atlassian Document Format, Jira's structured JSON document format. |
| Agent | An AI workflow that can decide steps and use tools. |
| API | A contract that allows software systems to communicate. |
| Chunking | Splitting documents into smaller retrievable units. |
| Context | Information supplied to the model for the current request. |
| Embedding | A vector representation of semantic meaning. |
| Few-shot | Prompting with several examples. |
| Grounding | Restricting output to authoritative evidence. |
| Hallucination | Plausible-sounding but unsupported or false output. |
| Inference | Running a trained model to generate a result. |
| LLM | Large Language Model. |
| MCP | A protocol for exposing tools and context to AI clients. |
| Model drift | Quality change caused by changing data, behavior, or environment. |
| n8n | A low-code workflow automation tool used here for chat-based Jira agent workflows. |
| PII | Personally identifiable information. |
| POM | Page Object Model for UI test automation. |
| Prompt injection | Untrusted text attempting to override trusted instructions. |
| RAG | Retrieval-Augmented Generation. |
| Regression evaluation | Re-running a fixed evaluation set after a change. |
| RLHF | Reinforcement Learning from Human Feedback. |
| Self-attention | Transformer mechanism for weighting relationships among tokens. |
| Temperature | Sampling control for output randomness. |
| Token | A model's unit of text processing. |
| Vector database | A system optimized for similarity search over embeddings. |
| Zero-shot | Prompting without examples. |

---

## 20. Five-Minute Final Recall

### AI fundamentals

- LLMs generate tokens probabilistically; they do not guarantee truth.
- Transformers use self-attention to connect information across context.
- Lower temperature improves consistency for QA artifacts.
- Context windows limit how much source material can be processed at once.

### Prompting

- RICE-POT means Role, Instructions, Context, Example, Parameters, Output, Tone.
- Strong prompts contain evidence, explicit constraints, missing-data behavior, and an output contract.
- Grounding plus validation is stronger than prompting alone.

### Architecture

- Streamlit handles UI.
- Jira REST API supplies live requirement data.
- The parser normalizes Jira and handles ADF/missing fields.
- The template is loaded dynamically.
- The provider layer selects Ollama or Groq.
- Ollama is local-first; Groq is the optional cloud provider/fallback.
- n8n provides importable visual workflows for Jira issue lookup and Jira subtask creation.

### Quality and safety

- Evaluate correctness, faithfulness, coverage, format, consistency, latency, cost, and safety.
- Treat Jira text as untrusted input because of prompt injection.
- Keep secrets out of Git, output, logs, and prompts.
- Treat write-capable agent workflows as risky until scoped, reviewed, and tested in a sandbox.
- Keep humans responsible for scope, assumptions, and approval.

### QA connection

- AI drafts test artifacts and exposes gaps; QA verifies and approves them.
- Generated tests need requirement traceability.
- Generated automation must be reviewed and executed.
- A pass percentage alone does not decide release readiness.

### Final one-line answer

> This repository applies grounded generative AI to QA by combining structured prompts, deterministic Jira retrieval, modular LLM providers, reusable templates, automated validation opportunities, and mandatory human review.
