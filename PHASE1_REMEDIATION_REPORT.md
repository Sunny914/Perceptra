# Phase 1 remediation report

Date: 2026-10-27. Branch `main`, commit `bdb18bd` (unchanged). Remote `origin` = `https://github.com/Sunny914/Perceptra.git`. No commit, push, force-push, history rewrite, deployment, or cloud API call was made. `AUDIT_REPORT.md` and `deployment_plan.md` were not modified.

## A. Executive summary

The working tree no longer contains the hardcoded bearer token or the live AWS resource identifiers. Neon and Upstash are optional, with explicit local fallbacks. Dependencies install from `pyproject.toml` plus a generated `uv.lock` on Python 3.12. Unit tests were executed: 35 passed.

The repository is not yet safe to treat as a cleaned public history. Commit `bdb18bd` is already on GitHub and still contains the token, the AWS identifiers, and 45 third-party PDFs. Those blobs stay public until you approve a history rewrite and GitHub drops the old commit. The API key has not been rotated. Conversation memory is no longer shared by default, but a shared `RAG_API_KEY` plus a known `thread_id` is still enough to continue someone else's thread.

The application is reproducible for unit tests and local import on Python 3.12. A live RAG query was not run. Docker image build was not run.

## B. Security findings

### S1 — Hardcoded bearer token — Critical

Evidence: `scripts/locustfile.py` in commit `bdb18bd` (working-tree lines previously 5, 11, and 35). The value is shaped like an application `RAG_API_KEY` (`rag-` prefix, long random suffix), not a documented placeholder. It is the same string in the docstring and the default argument. No other tracked worktree file contains it. `git grep` on `bdb18bd` finds only that file.

Change: the load test now reads `RAG_API_KEY` from the environment and raises `RuntimeError` if it is missing. The former API hostname was removed from the comments. `scripts/create_aws_secrets.py` no longer prints a generated key; it writes `scripts/rag_api_key.local`, which is gitignored.

Validation: `git grep` of the token prefix finds nothing in the working tree and still finds `bdb18bd:scripts/locustfile.py`. Locust itself was not executed (`locust` is the optional `load` extra and was not installed).

Remaining risk: the token is still in the pushed commit. Removing it from the file does not revoke it. Rotate it in `.env`, AWS Secrets Manager, and any client that used it. Rotation was not performed.

### S2 — Third-party PDFs — High (redistribution)

Evidence: 45 tracked files matching `DATA/noisy_data/*.pdf`. `DATA/noisy_data/README.txt` says the synthetic noise set is txt/html/docx/pptx. The PDFs are separately named academic papers, books, manuals, and slides. No license file grants redistribution. They are not imported by tests or by API startup. Ingestion will index them only if you point the CLI at `DATA/`.

Classification:

| Set | Classification |
|---|---|
| `DATA/noisy_data/*.pdf` (45 files) | Permission unverified. Not legally cleared. Unsuitable to keep in a public repo without a license review. |
| `DATA/noisy_data/*.{txt,html,docx,pptx}` plus `README.txt` | Described in-repo as generated synthetic noise. Still your confirmation, not a legal opinion. |
| `DATA/true_data/` | Kubernetes documentation copies. Upstream Kubernetes docs are commonly CC BY 4.0; this repo has no attribution notice. Permission needs your confirmation. |

Change: none. Deletion and history removal are waiting for approval. `.gitignore` now ignores new `DATA/noisy_data/*.pdf` files. Gitignore does not untrack the 45 files already committed.

### S3 — Shared conversation default — High for a multi-user deployment

Evidence: `app/main.py` previously defaulted `thread_id` to `default_user`. Checkpoints are keyed only by that string (`app/agents/graph.py`). `RAG_API_KEY` is one shared bearer token (`app/main.py` `verify_api_key`). It is not a user id.

Change: the default is gone. A missing `thread_id` becomes a new UUID and is returned on the response. `thread_id` must match `^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$`. `q` must be 1–4000 characters. The README states the shared-key limitation.

Validation: `tests/test_async_query.py` covers the omitted id, an invalid id (422), and an empty question (422).

Remaining risk: this is not per-user isolation. Anyone who holds `RAG_API_KEY` and knows a `thread_id` can read and continue that thread. Fixing that needs a real user identity, which this app does not have. Do not describe the current auth as per-user.

### S4 — AWS account and resource identifiers — Medium

Evidence: commit `bdb18bd` contains `scripts/aws_deploy_state.sh` and `scripts/aws_secret_arns.sh`. The ARN file embeds a 12-digit account id. These are infrastructure identifiers, not AWS access keys. No AWS secret key or session token was found.

Change: tracked copies are placeholders (`REPLACE_ME` / `REGION` / `ACCOUNT`). The previous contents were copied to gitignored `scripts/aws_deploy_state.local.sh` and `scripts/aws_secret_arns.local.sh` on this machine so the values were not thrown away. `destroy_aws_deployment.sh` refuses to run when `VPC_ID` is still `REPLACE_ME`. `create_aws_secrets.py` and `render_task_defs.py` prefer the `.local.sh` files.

Validation: `git grep` of the account id finds nothing in the tracked worktree and still finds both scripts in `bdb18bd`. No AWS CLI command was run.

Remaining risk: the identifiers remain in the pushed commit until history is rewritten.

### S5 — Other request-safety items addressed

| Item | Change | Remaining |
|---|---|---|
| `/graph` echoed exception text | Returns a fixed error string and logs the exception | Low |
| Eval clients skipped auth | `evals/pipeline.py` and `evals/guardrails_eval.py` send `Authorization` when `RAG_API_KEY` is set, and use `BACKEND_URL` | Eval console is still a local tool. Do not publish it without auth. |
| Query length | `q` max 4000 | History sent to the model is still unbounded |
| Prompt injection | No change | NeMo input rails are example-based. They are not comprehensive injection protection. |
| CORS | No middleware | Unchanged |
| `/ready` calls a paid LLM | No change this phase | Still true. Cost risk if the endpoint is public. |

## C. Git and remote safety

- Branch: `main`. HEAD: `bdb18bd`. Tracking: `origin/main`. Working tree is dirty only with this phase's edits plus the pre-existing untracked `AUDIT_REPORT.md`.
- The credential remains in `bdb18bd`, which is on the remote. History cleanup is still required.
- 45 PDFs remain tracked in the worktree and in that commit.
- AWS identifiers remain in that commit. They are not in the tracked worktree. Gitignored local copies exist on this machine.
- No destructive Git command was run.

Commands that need your approval before anyone runs them:

```powershell
# 1. Rotate RAG_API_KEY first (dashboard / .env / Secrets Manager). History rewrite does not rotate it.

# 2. Only if you also want the PDFs out of the new tree:
git rm --cached -- "DATA/noisy_data/*.pdf"

# 3. New root commit from the current tree (single-commit history).
git checkout --orphan cleaned
git add -A
git status
git commit -m "Replace initial history with a secret-free tree."

# 4. Force-push. This rewrites main on GitHub.
git push --force origin cleaned:main
```

Implications: anyone who cloned the repo must reclone or reset. GitHub can keep the old commit reachable by SHA until it is garbage-collected and, for a public repo, until GitHub support purges cached views. Force-push does not rotate the API key. Do not run step 4 until step 1 is done.

## D. Dependency reproducibility

- Supported Python: 3.12 in CI, Docker (`python:3.12-slim-bookworm`), and the local `.venv`. `requires-python` is `>=3.11,<3.13` because `torch==2.5.1` has no 3.13 wheel. The machine's global Python 3.13 was not modified. uv downloaded CPython 3.12.15 into its own store and created `.venv`.
- Source of truth: `pyproject.toml` locked by `uv.lock` (4,722 lines, generated by `uv lock`, exit 0). `requirements.txt` is now a pointer to `uv sync --frozen --extra dev`.
- `pdfplumber==0.11.7` was added because `app/ingestion/loaders/pdf.py` imports it.
- Office parsing no longer imports `unstructured` (that package was not in `pyproject.toml`). `app/ingestion/loaders/office.py` uses `python-docx` and `python-pptx`, which were already declared. Table-aware unstructured extraction is no longer used.
- Dev extra is pytest, pytest-asyncio, and ruff. RAGAS, deepeval, nest-asyncio, and pandas are the `evals` extra. Locust is the `load` extra. CI installs only `--extra dev`.
- Clean install: `uv sync --frozen --extra dev --python 3.12` exited 0.
- Docker build: NOT RUN. The Dockerfile still installs from `pyproject.toml`; only the base image moved from 3.11 to 3.12.

## E. Test results

| Command | Result | Class |
|---|---|---|
| `uv lock` | exit 0 | PASS |
| `uv sync --frozen --extra dev --python 3.12` | exit 0, CPython 3.12.15 | PASS |
| `uv run ruff check app tests evals` | All checks passed | PASS |
| `uv run ruff format --check app tests evals` | 46 files already formatted | PASS |
| `uv run pytest tests/` with dummy env vars | 35 passed, 27 warnings, 40.43s | PASS |
| Live `/query`, ingestion, RAGAS, Locust | not run (would call paid APIs or need the load extra) | NOT RUN |
| `docker build` | not run (large torch image; not required to prove the unit tests) | NOT RUN |

Dummy env used for pytest: `JINA_API_KEY`, `OPENAI_API_KEY`, `PORTKEY_API_KEY`, `PORTKEY_PRIMARY_CONFIG_ID`, `QDRANT_URL`, `NEON_DB_URL`, `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN`, `LOGFIRE_IGNORE_NO_CONFIG`. No live network assertion was made. Passing tests do not prove retrieval quality.

Warnings are pre-existing library and FastAPI `on_event` deprecations, not failures.

## F. Changed files

Modified:

| File | Why |
|---|---|
| `scripts/locustfile.py` | Remove hardcoded credential and hostname. Require `RAG_API_KEY`. |
| `scripts/aws_deploy_state.sh`, `scripts/aws_secret_arns.sh` | Replace live IDs with placeholders. |
| `scripts/destroy_aws_deployment.sh` | Prefer `.local.sh`. Refuse placeholder IDs. |
| `scripts/create_aws_secrets.py` | Write ARNs and any generated API key to gitignored local files. |
| `scripts/render_task_defs.py` | Read `.local.sh` when it exists. |
| `app/main.py` | Drop `default_user`. Validate `thread_id` and `q`. Return `thread_id`. Generic `/graph` error. |
| `app/config.py` | Neon and Upstash optional. Blank optional env values become unset. |
| `app/agents/graph.py` | MemorySaver when Neon is unset, with an explicit warning. |
| `app/services/health/connection_checker.py` | Report unconfigured Postgres and Redis instead of crashing. |
| `app/ingestion/loaders/office.py` | Parse docx/pptx with declared libraries. |
| `evals/pipeline.py`, `evals/guardrails_eval.py` | `BACKEND_URL` and bearer header. |
| `pyproject.toml` | Python `<3.13`, pdfplumber, split extras. |
| `uv.lock` | Regenerated by uv. |
| `requirements.txt`, `requirements-prod.txt` | Point at pyproject / mirror the pdfplumber pin. |
| `.github/workflows/ci.yml` | `uv sync --frozen --extra dev` on Python 3.12. |
| `Dockerfile` | Base image 3.12. |
| `.gitignore` | Env variants, keys, caches, generated data, local AWS state, new noisy PDFs. |
| `.env.example` | Optional Neon/Upstash called out. Placeholders only. |
| `README.md`, `local_testing.md` | Install, Python version, optional services, `--wipe`, thread-id limitation. |
| `tests/test_async_query.py`, `tests/test_connection_checker.py` | Cover the new validation and unconfigured fallbacks. |

Added: this report.

Not added to Git (gitignored, kept on disk): `scripts/aws_deploy_state.local.sh`, `scripts/aws_secret_arns.local.sh`, `.venv/`.

Untouched on purpose: `AUDIT_REPORT.md`, `deployment_plan.md`, `aws.md`, application graph logic beyond the fallback, datasets, notebooks, `ui/`.

Deleted: none.

## G. Remaining blockers

- P0: Rotate the exposed `RAG_API_KEY`. Not done.
- P0: Rewrite and force-push history so the token, AWS IDs, and (if you approve) the PDFs leave GitHub. Not done. Needs your approval.
- P0: Decide the 45 PDFs. They are still in the tree and in history.
- P1: Shared API key does not isolate threads. Needs a real identity model before any multi-user claim.
- P1: `/ready` still makes a live LLM call. Public exposure can spend money.
- P2: Docker build not executed after the base-image change.
- P3: `processed_data/` is still tracked even though new output is gitignored. Untracking it is a separate `git rm --cached` decision.
- P3: FastAPI `on_event` deprecation. Not a functional failure.

## H. Next phase (not started)

Portfolio naming in code, README rewrite, citations, abstain-on-empty-context, screenshots, license, and deployment. Do not start that until you ask for Phase 2.
