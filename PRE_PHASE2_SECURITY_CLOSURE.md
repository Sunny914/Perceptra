# Pre-Phase-2 security closure

Verified 2026-10-27 against the working tree. No files were deleted, untracked, committed, pushed, or rewritten. `PHASE1_REMEDIATION_REPORT.md` and `AUDIT_REPORT.md` were not modified. Local `scripts/*.local.sh` backups were not opened or changed.

Credential remediation is **BLOCKED**. History cleanup is **not done**. The public GitHub history is **not safe**.

## 1. Current Git state

| Item | Verified value |
|---|---|
| Root | This repository |
| Branch | `main` |
| Commit | `bdb18bd` — "Initial commit: Perceptra agentic RAG and document intelligence." |
| History | One commit only |
| Remote | `origin` `https://github.com/Sunny914/Perceptra.git` (fetch and push) |
| Tracking | `main...origin/main`, no ahead/behind |
| Staged index | Empty. `git diff --cached --name-only` printed nothing |
| Untracked | `AUDIT_REPORT.md`, `PHASE1_REMEDIATION_REPORT.md`, this file |

The committed tree on `origin/main` is still `bdb18bd`. Phase 1 edits exist only as unstaged working-tree changes. An empty index does not mean the published commit is clean.

## 2. Credential status

The exposed value is the application bearer token `RAG_API_KEY`. `app/main.py` `verify_api_key` compares the `Authorization: Bearer` header with `settings.API_KEY`, which is loaded from `RAG_API_KEY`. It is not `OPENAI_API_KEY` and not `PORTKEY_API_KEY`.

Repository evidence does not support calling it a placeholder. In `bdb18bd` it appears as a long `rag-` prefixed default in `scripts/locustfile.py` (docstring and code). The working-tree file no longer contains that value or the old `elb.amazonaws.com` hostname. It reads `RAG_API_KEY` from the environment and raises if the variable is missing.

`git grep` of the token prefix:

- Working tree: no match.
- History: `bdb18bd:scripts/locustfile.py` only.

Whether that exact value is still accepted depends on wherever `RAG_API_KEY` was configured (local `.env`, AWS Secrets Manager, a running API). This check did not call any service and did not use the value. Rotation is **required** and **not confirmed**. Status: **BLOCKED**.

### Rotation you need to do

1. Generate a new random string locally. Do not reuse the committed value and do not paste it into Git.
2. Put the new value only in `.env` as `RAG_API_KEY`.
3. If Secrets Manager still has the secret whose name was `rag/rag-api-key`, replace its value with the new string (`aws secretsmanager put-secret-value`). Do not run the destroy script.
4. Update any Streamlit or Locust environment that still has the old value.
5. After that, tell me rotation is done. Until then this item stays BLOCKED.

Deleting the line and rewriting history do not revoke the key.

## 3. Historical exposure inventory

One commit, `bdb18bd`, is on `origin/main`.

| What | Where in `bdb18bd` | Working tree now |
|---|---|---|
| Bearer token | `scripts/locustfile.py` | Removed. Env var required. |
| Former API hostname | `scripts/locustfile.py`, `scripts/aws_deploy_state.sh` | Removed from tracked files. |
| AWS account id and resource ids | `scripts/aws_deploy_state.sh`, `scripts/aws_secret_arns.sh` | Tracked files are `REPLACE_ME` / `REGION` / `ACCOUNT` placeholders. |
| 45 third-party PDFs | `DATA/noisy_data/*.pdf` | Still tracked. About 90.6 MB. |
| Extracted PDF text | 4 files under `processed_data/noisy/*.pdf.json` | Still tracked. |
| `default_user` thread default | `app/main.py` | Gone from `app/main.py`. The string remains only in `tests/test_async_query.py` as an assertion that the API must not use it. |

No other tracked file in the working tree matched the token prefix or the account id. Notebooks were not found in that search. This is not a claim that every possible secret pattern was exhaustively proven absent from binary PDFs.

Rewriting `main` means anyone who cloned the repo must reclone or reset. GitHub can keep `bdb18bd` reachable by SHA until it is garbage-collected and, for a public repo, until GitHub support purges cached views. Force-push was not run.

## 4. PDF inventory

None of these files are imported by unit tests. `tests/` has no `DATA/` references. The ingestion CLI will read them only if you point it at `DATA/` or `DATA/noisy_data/`. The API does not load them at startup. The golden eval set is built from the Kubernetes `DATA/true_data` material, not from these PDFs.

No license file in the repo covers them. Filename provenance is a published paper, book, manual, or slide deck. Status for every row: **permission unverified**, and **not suitable for the public repository** until you supply a license. None are "permission verified."

| Bytes | Path |
|---:|---|
| 1516903 | `DATA/noisy_data/100G Networking Technology Overview - Slides - Toronto (August 2016).pdf` |
| 1164143 | `DATA/noisy_data/2018 CppCon Unwinding the Stack - Exploring how C++ Exceptions work on Windows - James McNellis.pdf` |
| 459589 | `DATA/noisy_data/37 Million Compilations - Investigating Novice Programming Mistakes in Large-Scale Student Data (fp1187-altadmri).pdf` |
| 199550 | `DATA/noisy_data/5-Level Paging and 5-Level EPT - Intel - Revision 1.0 (December, 2016).pdf` |
| 187398 | `DATA/noisy_data/5-Level Paging and 5-Level EPT - Intel - Revision 1.1 (May, 2017).pdf` |
| 108608 | `DATA/noisy_data/A Block-sorting Lossless Data Compression Algorithm - May 10th, 1994 (SRC-RR-124).pdf` |
| 6358127 | `DATA/noisy_data/A Brief Introduction to Neural Networks (neuronalenetze-en-zeta2-2col-dkrieselcom).pdf` |
| 358744 | `DATA/noisy_data/A Brief Introduction to the Standard Annotation Language (SAL) - 2006.pdf` |
| 207314 | `DATA/noisy_data/A Brief Tutorial on Database Queries, Data Mining, and OLAP (hamel-197-manuscript-final).pdf` |
| 325479 | `DATA/noisy_data/A Case Study in Optimizing HTM-Enabled Dynamic Data Structures - Patricia Tries (2015).pdf` |
| 2346760 | `DATA/noisy_data/A Catalogue of Optimizing Transformations (1971-allen-catalog).pdf` |
| 211355 | `DATA/noisy_data/A Comparison of Programming Languages in Economics (16-Jun-2014).pdf` |
| 156844 | `DATA/noisy_data/A Comparison of Software and Hardware Techniques for x86 Virtualization - Oct 2015 (asplos235_adams).pdf` |
| 23669057 | `DATA/noisy_data/A Forensic Analysis of CSG 11 Encounter with an Anomalous Aerial Vehicle.pdf` |
| 85503 | `DATA/noisy_data/A Framework for Building Extensible C++ Class Libraries - 1993.pdf` |
| 2336905 | `DATA/noisy_data/A GPU-friendly Skiplist Algorith - 2014 (GPUSkiplist).pdf` |
| 568047 | `DATA/noisy_data/A History of Modern 64-bit Computing - Feb 2007 (CSEP590A).pdf` |
| 1858017 | `DATA/noisy_data/A Journey in Creating an Operating System Kernel - The 539Kernel Book (Nov 2022).pdf` |
| 822345 | `DATA/noisy_data/A Little Journey Inside Windows Memory.pdf` |
| 927704 | `DATA/noisy_data/A Locality-Sensitive Hash for Real Vectors (10.1.1.215.7690).pdf` |
| 934238 | `DATA/noisy_data/A Lock-Free Wait-Free Hash Table - Slides (070221_LockFreeHash).pdf` |
| 740232 | `DATA/noisy_data/A Look at Intel's Dataplane Development Kit (2014).pdf` |
| 208991 | `DATA/noisy_data/A Malloc Tutorial (Feb 16, 2009).pdf` |
| 374609 | `DATA/noisy_data/A Mathematical Theory of Communication (1948).pdf` |
| 400277 | `DATA/noisy_data/A Mathematician's Lament - Paul Lockhart.pdf` |
| 331643 | `DATA/noisy_data/A Method for the Construction of Minimum-Redundancy Codes - Huffman (1952).pdf` |
| 517898 | `DATA/noisy_data/A NUMA API for Linux - Novell (2005).pdf` |
| 216415 | `DATA/noisy_data/A Nanopass Framework for Compiler Education.pdf` |
| 140095 | `DATA/noisy_data/A Neural Probabilistic Language Model (bengio03a).pdf` |
| 275148 | `DATA/noisy_data/A New Algorithm for Data Compression (1994).pdf` |
| 507664 | `DATA/noisy_data/A Novel Hybrid Quicksort Algorithm Vectorized using AVX-512 on Intel Skylake (1704.08579).pdf` |
| 138811 | `DATA/noisy_data/A Parallel Page Cache- IOPS and Caching for Multicore Systems.pdf` |
| 11985208 | `DATA/noisy_data/A Pattern Language - Alexander.pdf` |
| 551215 | `DATA/noisy_data/A PlusCal User's Manual - C-Syntax Version 1.8 (31 Aug 2018).pdf` |
| 297323 | `DATA/noisy_data/A Practical Guide to Support Vector Classification.pdf` |
| 213497 | `DATA/noisy_data/A Practical Minimal Perfect Hashing Method (2005).pdf` |
| 12640318 | `DATA/noisy_data/A Primer on Memory Consistency and Cache Coherence (10.1.1.225.9278).pdf` |
| 4877958 | `DATA/noisy_data/A Primer on Memory Consistency and Cache Coherence - 2nd Edition.pdf` |
| 6226320 | `DATA/noisy_data/A Probabilistic Theory of Deep Learning (1504.00641v1).pdf` |
| 408023 | `DATA/noisy_data/A Proposal for Hardware Assisted Arithmetic Overflow Detection - 2010 - Slides (Mihocka-Troeger-CGO-WISH-2010_final).pdf` |
| 286284 | `DATA/noisy_data/A Proposal for Hardware Assisted Arithmetic Overflow Detection for Array and Bitfield Operations (LazyOverflowDetect_Final).pdf` |
| 204106 | `DATA/noisy_data/A Quick Guide To LaTeX.pdf` |
| 1462855 | `DATA/noisy_data/A Relational Model of Data for Large Shared Data Banks - E.F. Codd (1970).pdf` |
| 6465724 | `DATA/noisy_data/A Theoretical Framework for Back-Propagation (2001).pdf` |
| 776282 | `DATA/noisy_data/A Tool for the Symbolic Execution of Linux Binaries - PySymemu (Slides).pdf` |

Total: 45 files, 95,049,526 bytes.

### Other data files

`DATA/noisy_data/README.txt` says the txt/html/docx/pptx files are generated synthetic noise inspired by academic titles. A spot-check of `A Pattern Language - Alexander.txt` is repeated filler sentences, not the book. Those 10 non-PDF files plus the README can stay as the synthetic noise set. That is not a legal clearance of every binary in that list; the README is the in-repo evidence.

`DATA/true_data/` (6 files: Kubernetes job, cron, and autoscaling docs) is what the golden questions use. Upstream Kubernetes documentation is commonly CC BY 4.0. This repo has no `LICENSE` and no attribution notice. Classification: **license identified, redistribution needs attribution before you call it cleared.**

`processed_data/noisy/*.pdf.json` (4 files) are extracted text from the PDFs above. Treat them as the same redistribution risk. `processed_data/` is now gitignored for future files, which does not untrack these.

### Minimal dataset to keep

- `DATA/true_data/` for the demo and the golden set, with a CC BY 4.0 attribution line once you confirm that license.
- The synthetic non-PDF files in `DATA/noisy_data/` for parser and "noise" tests.
- Do not ship the 45 PDFs or the four PDF-derived JSON files.
- Ingest with `python -m app.ingestion.processor DATA/true_data` rather than `DATA --wipe` if the PDFs are still on disk. `--wipe` deletes the Qdrant collection.

## 5. AWS metadata review

Tracked `scripts/aws_deploy_state.sh` and `scripts/aws_secret_arns.sh` contain only placeholders (`REPLACE_ME`, `REGION`, `ACCOUNT`) plus the public region names `us-east-1a` and `us-east-1b`. They do not contain the account id.

Gitignored backups exist and were not modified:

- `scripts/aws_deploy_state.local.sh` (1,269 bytes)
- `scripts/aws_secret_arns.local.sh` (1,242 bytes)

`git check-ignore` matches both via `.gitignore` line `scripts/*.local.sh`. `scripts/rag_api_key.local`, `.env`, and `.venv/` are also ignored. History still contains the real identifiers in `bdb18bd`. They have not been purged.

`destroy_aws_deployment.sh` was not run. It refuses to run while `VPC_ID` is `REPLACE_ME`.

## 6. Files that would be excluded from a cleaned tree

Only after you approve:

- The 45 PDFs listed above (`git rm --cached` leaves them on disk).
- The 4 `processed_data/noisy/*.pdf.json` extracts, same command style.

Not excluded: Phase 1 source edits, `DATA/true_data/`, synthetic noisy non-PDFs, placeholder AWS scripts, `uv.lock`.

Must never be staged: `.env`, `scripts/*.local.sh`, `scripts/rag_api_key.local`, `.venv/`.

`git add -A` is the wrong command here. After `git rm --cached`, a later `git add -A` can re-add a PDF if the ignore rule is wrong, and it would also pick up every untracked report. Use the explicit adds below.

## 7. Commands that need approval

Do not run these until you say so. Step A can happen before rotation. Step C must not happen until you have rotated the key. Nothing below has been run.

```powershell
# A. Untrack the PDFs and the extracted JSON. Files stay on disk.
git rm --cached -- "DATA/noisy_data/*.pdf"
git rm --cached -- processed_data/noisy/100G*.json processed_data/noisy/37*.json processed_data/noisy/5-Level*.json

# B. New root commit that includes the current Phase 1 edits.
git checkout --orphan cleaned
git add -- .env.example .github .gitignore Dockerfile README.md ARCHITECTURE.md TESTING.md local_testing.md aws.md deployment_plan.md pyproject.toml uv.lock requirements.txt requirements-prod.txt
git add -- app evals ui tests scripts notebooks .streamlit
git add -- DATA/true_data DATA/noisy_data/README.txt
git add -- "DATA/noisy_data/*.html" "DATA/noisy_data/*.txt" "DATA/noisy_data/*.docx" "DATA/noisy_data/*.pptx"
git add -- AUDIT_REPORT.md PHASE1_REMEDIATION_REPORT.md PRE_PHASE2_SECURITY_CLOSURE.md
git status
git diff --cached --name-only
# Stop here and review. Confirm no .env, no *.local.sh, no .pdf, no rag_api_key.local.

git commit -m "Publish a secret-free tree for Perceptra."

# C. Only after rotation, and only with a separate explicit yes:
git push --force origin cleaned:main
```

`git checkout --orphan` keeps the current index and working tree. It does not delete files. The force-push replaces `main` on GitHub and drops `bdb18bd` from the branch tip. It does not rotate the key.

## 8. Verification results

| Check | Result | Class |
|---|---|---|
| `git diff --check` | exit 0 | PASS |
| `uv lock --check` | Resolved 280 packages, exit 0 | PASS |
| `uv run ruff check app tests evals` | All checks passed | PASS |
| `uv run ruff format --check app tests evals` | 46 files already formatted | PASS |
| `uv run pytest tests/ -q` | 35 dots, `[100%]`, exit 0 | PASS |
| Live RAGAS, paid APIs, `DATA --wipe`, Docker build, AWS scripts | not run | NOT RUN |
| Credential rotation | not confirmed | BLOCKED |
| History rewrite | not performed | BLOCKED |

Python in the project: `requires-python` is `>=3.11,<3.13`. Dockerfile is `python:3.12-slim-bookworm`. CI uses Python 3.12 and `uv sync --frozen --extra dev`. README tells you to create the venv with Python 3.12. `.venv` is present.

Shared thread default: absent from `app/main.py`. README states that `RAG_API_KEY` is one shared key and does not identify a user.

`.env.example` values are empty or obvious placeholders (`marathon-api`, `anthropic-fallback`, `http://localhost:8000`). No live credential was found in the tracked working tree by the token and account-id searches.

## 9. Remaining blockers

- P0: Rotate `RAG_API_KEY`. BLOCKED on you.
- P0: Approve and then run the history replacement. The token, AWS ids, and PDFs are still in `bdb18bd` on GitHub.
- P0: Approve untracking the 45 PDFs and 4 extracted JSON files.
- P1: Add Kubernetes CC BY attribution before calling `DATA/true_data` cleared. Portfolio phase, not done here.
- P1: Shared API key still does not isolate conversations.

## 10. Recommendation

The working tree is in good shape for a cleanup commit: tests pass, the lockfile matches, placeholders replaced the AWS ids, and the token is gone from the files Git would commit after the explicit `git add` above.

The repository is **not** ready for a public portfolio push and **not** publicly safe. The old key may still work, and GitHub still serves `bdb18bd`. Do not start Phase 2 until rotation is confirmed and you approve the commands in section 7. Force-push stays a separate yes.
