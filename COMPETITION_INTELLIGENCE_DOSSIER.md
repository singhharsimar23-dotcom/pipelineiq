# ARC-AGI-3 & PIPELINEIQ: MASTER RESEARCH & COMPETITION INTELLIGENCE DOSSIER
**Compiled for:** PipelineIQ Research & ARC Prize 2026 Submission Track  
**Timestamp:** 2026-08-17  
**Scope:** Full multi-tier intelligence synthesis (Tiers 1, 2, and 3) for NotebookLM & Academic Paper Source Integration.

---

## TABLE OF CONTENTS
1. [Tier 1 — Direct Competition Intelligence](#tier-1--direct-competition-intelligence)
   - 1.1 Kaggle Public Leaderboard & Percentile Dynamics
   - 1.2 Top 20 Public Notebooks: Exhaustive Taxonomy & Score Analysis
   - 1.3 Kaggle Community Failure Modes & The 80-Action Cap Ceiling
   - 1.4 ARC-AGI-3 Official Starter Kit & Architecture Specification
2. [Tier 2 — Structural & Theoretical Foundations](#tier-2--structural--theoretical-foundations)
   - 2.1 Chollet (2019) *"On the Measure of Intelligence"*: Core Priors & ARC Taxonomy
   - 2.2 ARC Prize 2024 & 2025 Winning Solutions Post-Mortem (the ARChitects, MindsAI, Icecuber)
   - 2.3 Ellis et al. (2021) *DreamCoder*: Program Synthesis, MDL Compression, and Visual Search Limits
   - 2.4 LLM Autoregressive Failure Modes in Interactive Grid Worlds
3. [Tier 3 — Engine Internals & Adjacent Signal](#tier-3--engine-internals--adjacent-signal)
   - 3.1 `arcengine` & `arc_agi` Internals Deconstruction
   - 3.2 Discrete State Scoring Mathematics & Quadratic Weighting Proof
   - 3.3 Connected Component Topologies & Discrete Invariant Solving

---

# TIER 1 — DIRECT COMPETITION INTELLIGENCE

### 1.1 Kaggle Public Leaderboard & Percentile Dynamics
- **Competition Target:** ARC Prize 2026 (ARC-AGI-3 Interactive Track).
- **Evaluation Harness:** 25 hidden evaluation environments served over a private sidecar API gateway (`http://gateway:8001/api/games`) during competition rerun with `KAGGLE_IS_COMPETITION_RERUN=1`.
- **Leaderboard Score Distribution (August 2026 Snapshot):**
  - **Median (50th Percentile):** `0.00% – 0.10%`. Over 70% of public submissions score 0.05% due to execution timeouts, uncaught runtime exceptions in multi-threaded `Swarm`, or false dispatch collisions.
  - **Top 10% Public Benchmark (Duck / Goose Baseline):** `1.70% – 1.85%`. Achieved by unguided novelty search (Stochastic Goose) or un-finetuned 27B LLM prompting (Duck Qwen-3.8).
  - **PipelineIQ V15 Benchmark:** **`9.8508%`**. Achieved via exact topological systems identification, GF(2)/GF(3) matrix solving, and atomic thread-safe dispatch.

---

### 1.2 Top 20 Public Notebooks: Exhaustive Taxonomy & Score Analysis

| # | Notebook Reference | Author / Team | Approach / Paradigm | Public Score | Key Failure Mode / Bottleneck |
|:---:|:---|:---|:---|:---:|:---|
| 1 | `foysalemonshanto/arc3-duck-v12-with-qwen-3-8-27b` | Foysal / TAAF | Qwen 3.8 27B-FP8 LLM via local vLLM on RTX 6000 | **1.70%** | High step latency (2s/step), 64x64 coordinate hallucination, GPU quota burn. |
| 2 | `jakobbrggen/taaf-model-20260815-q38-p1` | Jakob Brüggen (Tufa Labs) | Base TAAF execution harness with Qwen-27B | **1.70%** | Solves only trivial 1-step tasks; cannot invert algebraic/matrix puzzles. |
| 3 | `inversion/arc3-sample-submission-stochastic-goose` | Dries Smit (Tufa Labs) | 4-layer CNN predicting frame novelty ($\Delta \text{frame} \neq 0$) | **1.85%** | Maximizes any pixel perturbation; wanders aimlessly once novelty plateaus. |
| 4 | `thtennant/arc3-duck-v19` | Teddy Tennant | TAAF Duck with extended system prompts | **1.70%** | Prompt bloat slows inference down without improving spatial reasoning. |
| 5 | `tanakaai24/arc3-qwen3-6-duck-lb117-safety-v1` | Tanaka Ai24 | Qwen 3.6 Duck with heuristic action masking | **1.17%** | Strict masking prevents exploration on branching maze paths. |
| 6 | `lucifer19/arc3-blackcat-evolution-c03` | Krizsó Gergely | Genetic / Evolutionary macro action search | **1.05%** | High sample complexity; hits action budget before converging on multi-level puzzles. |
| 7 | `sahsanali/arc-2026-invariant-search-program-synthesis-en` | S. Ahsan Ali | Symbolic Invariant Search & Program Synthesis | **2.10%** | Search space explodes without strong domain-specific topological pruning. |
| 8 | `nekkon/the-80-action-cap-ceilings-you-at-8-7` | Luka Duvanov | Starter kit configuration analysis | N/A (EDA) | Proves default 80-action limit prevents multi-level solutions. |
| 9 | `iamjasonfeng/sandwich` | Jason Feng | Hybrid CNN + Heuristic fallback | **1.45%** | Loose dispatch triggers false positives on maze corridors. |
| 10 | `pengyipeng1/arc3-pagi-001-public-reference` | Pengyi Peng | Primitive Action Generation & Invariance | **1.20%** | Handcrafted rules fail to generalize to transformed game instances. |
| 11 | `lucifer19/pannonia-arc3-agentic-anchor` | Krizsó Gergely | Replay anchor with heuristic search | **0.95%** | Inflexible replay triggers game over when level origins shift. |
| 12 | `juliancamilovilla/arc-agi3-duck-ctx` | Julian Camilo Villa | Context-window augmentation on TAAF | **1.70%** | LLM attention degradation over multi-step frame sequences. |
| 13 | `datlq1202/latent-ltx` | Dat Le Quoc | Latent transition autoencoder | **0.85%** | Low reconstruction fidelity on small 1x1 interactive sprites. |
| 14 | `kunaldesale2408/duck-harness-fast-eval` | Kunal Desale | C++ accelerated TAAF wrapper | **1.70%** | Harness speedup does not fix underlying model reasoning errors. |
| 15 | `iseesmth/duck-harness-prolong-public-eval` | auxentr | Extended step budget TAAF | **1.75%** | Diminishing returns after 100 actions on random LLM exploration. |
| 16 | `gktrkakman/taaf-duck-sub-20260805-share` | Göktürk | TAAF baseline fork | **1.70%** | Standard LLM baseline ceiling. |
| 17 | `hussensehs/trace` | hussen_sehs | Frame-by-frame diff tracer | **0.60%** | Passive observation without active goal formulation. |
| 18 | `valentinorayisabell/arc3-goose-moe-v0` | valentino ray isabell | Mixture-of-Experts action prediction | **1.80%** | Gating network collapses to single dominant action head. |
| 19 | `datlq122/caption-qwen` | Đạt Lê | Grid-to-Text captioning pipeline | **1.10%** | Text descriptions lose fine-grained spatial adjacency coordinates. |
| 20 | `denizmucur/arc-agi-3-group-1` | Deniz Mucur | Grouped grid partition search | **0.90%** | Rigid grid splits break non-aligned connected components. |

---

### 1.3 Kaggle Community Failure Modes & The 80-Action Cap Ceiling
1. **The 80-Action Cap Ceiling (Luka Duvanov's Discovery):**
   - In the starter kit default `Agent` class, `MAX_ACTIONS = 80`.
   - On multi-level games (e.g. `ft09` requiring 75 actions across 6 levels, or `vc33` requiring 140+ actions across 4 levels), an agent with `MAX_ACTIONS = 80` is forcefully terminated at Level 3.
   - **PipelineIQ Resolution:** Set `MAX_ACTIONS: int = 200` per instance, allowing full multi-level completion while respecting the 9-hour total execution budget.
2. **The Swarm Concurrency Trap:**
   - Starter kit `Swarm.main()` evaluates all 25 games concurrently using Python `threading.Thread`.
   - Because `GameAction.ACTION6` in `arcengine` is an Enum member singleton, concurrent threads mutate `ACTION6.action_data` in place.
   - **PipelineIQ Resolution:** Implemented atomic `_ACTION_LOCK = threading.Lock()` wrapping `choose_action()` $\to$ `take_action()`.

---

### 1.4 ARC-AGI-3 Starter Kit & Architecture Specification
- **Repository Structure:** `ARC-AGI-3-Agents` contains:
  - `agents/agent.py`: Base abstract class defining `choose_action(frames, latest_frame)`, `take_action()`, and `main()`.
  - `agents/swarm.py`: Orchestrates multi-agent parallel execution over `GAMES` list retrieved from `/api/games`.
  - `arcengine/`: Defines `FrameData`, `GameAction` (ACTION1–ACTION7, RESET), `GameState` (NOT_PLAYED, NOT_FINISHED, WIN, GAME_OVER), and discrete grid operations.
- **Sidecar Network Contract:** Notebook communicates with `http://gateway:8001/` via standard HTTP REST endpoints:
  - `GET /api/games` $\to$ Returns list of active competition game IDs.
  - `POST /scorecards` $\to$ Opens new evaluation session.
  - `POST /step` $\to$ Submits action and receives next `FrameData`.

---

# TIER 2 — STRUCTURAL & THEORETICAL FOUNDATIONS

### 2.1 François Chollet (2019) *"On the Measure of Intelligence"*: Core Priors & ARC Taxonomy
Chollet defined intelligence as **generalization difficulty normalized by prior knowledge**:
$$\text{Intelligence} = \frac{\text{Skill Target}}{\text{Experience} \times \text{Priors}}$$

ARC tasks are explicitly engineered to resist memorization and pure deep learning curve fitting by grounding problems in **Core Knowledge Priors**:
1. **Objectness & Cohesion:**
   - Pixels of uniform color form distinct, bounded objects that maintain identity across time.
   - Objects can move, rotate, translate, and occlude without disappearing.
2. **Goal-Directedness & Agency:**
   - Certain objects act as agents (e.g., player avatar) that navigate toward targets, avoid barriers, or interact with environmental affordances.
3. **Geometry & Topology:**
   - Relationships such as containment (inside/outside), connectivity (paths, mazes), adjacency, symmetries ($D_4$ group: reflections, 90° rotations), and scaling.
4. **Numbers & Counting:**
   - Small integer arithmetic ($1 \le N \le 10$), sorting by size/area, frequency ordering, parity checks (even/odd).

---

### 2.2 ARC Prize 2024 & 2025 Winning Solutions Post-Mortem

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                          Evolution of ARC Winning Architectures                        │
└───────────────────────────────────┬────────────────────────────────────────────────────┘
                                    │
       ┌────────────────────────────┼────────────────────────────┐
       ▼                            ▼                            ▼
┌──────────────┐             ┌──────────────┐             ┌──────────────┐
│   Icecuber   │             │ theARChitects│             │   MindsAI    │
│  (2020/2024) │             │ (2024 Winner)│             │ (2024/2025)  │
├──────────────┤             ├──────────────┤             ├──────────────┤
│ • Pure C++   │             │ • Fine-Tuned │             │ • Test-Time  │
│   Symbolic   │             │   Diffusion/ │             │   Training   │
│   DSL Search │             │   Transformers│            │   (TTT)      │
│ • Fast DFS   │             │ • AIRV Vote  │             │ • Dynamic LoRA│
│ • Zero LLM   │             │ • Synthetic  │             │ • Search/Ref │
└──────────────┘             └──────────────┘             └──────────────┘
```

1. **the ARChitects (1st Place ARC Prize 2024 — 53.5% Score):**
   - **Authors:** Daniel Franzen & Jan Disselhoff.
   - **Core Innovation (AIRV):** *Augment, Inference, Reverse augmentation, and Vote*.
   - Evaluated inputs across all 8 dihedral transformations ($D_4$), ran ensemble inference, un-transformed predictions back to canonical space, and performed majority voting to eliminate stochastic errors.
2. **MindsAI & Tufa Labs (Highest 2024 Evaluation Score — 55.5% Score):**
   - **Core Innovation:** *Test-Time Training (TTT)*.
   - Fine-tuned transformer weights directly on the test task demonstration pairs at test time, adapting model activations to the specific visual geometry of the unseen task.
3. **Icecuber (2020 Winner / 2024 Hybrid Anchor):**
   - **Core Innovation:** Pure, lightweight, deterministic C++ domain-specific language (DSL) program search.
   - Top 2024/2025 teams ran Icecuber's symbolic search in parallel with neural models because symbolic search solves combinatorial/topological tasks instantly with zero compute overhead.

---

### 2.3 Ellis et al. (2021) *DreamCoder*: Program Synthesis & MDL Compression

DreamCoder models learning as program synthesis with **Minimum Description Length (MDL)** compression via a "Wake-Sleep" algorithm:
$$\mathcal{L}(\mathcal{D}, \mathcal{G}) = \text{bits}(\mathcal{G}) + \sum_{x \in \mathcal{D}} \min_{p \in \mathcal{G}, p \vdash x} \text{bits}(p)$$

- **Wake Phase:** Agent searches for programs $p$ that solve tasks $x$ using its current grammar $\mathcal{G}$.
- **Sleep Phase (Abstraction):** Compresses discovered programs into reusable macro-primitives, adding them to $\mathcal{G}$ if and only if:
  $$\Delta \text{MDL} = \text{bits}(\mathcal{G}_{\text{old}}) - \text{bits}(\mathcal{G}_{\text{new}}) > 0$$
- **Why DreamCoder Failed on Visual Grid ARC:**
  - Standard DreamCoder searched raw lambda-calculus syntax trees without visual geometric awareness.
  - The branching factor in 2D space ($64 \times 64 = 4096$) is catastrophic without **topological connected-component segmentation** to prune the search space prior to synthesis.

---

### 2.4 Why Autoregressive LLMs Hit a Wall on Interactive ARC-AGI-3
1. **No Test-Time Inversion:** Next-token prediction generates actions autoregressively based on training priors, but cannot invert discrete linear systems ($M \cdot x = b \pmod 2$ in toggle puzzles).
2. **Spatial Quantization Loss:** Converting a 64x64 grid to text tokens loses spatial locality (a pixel at $(y, x)$ is hundreds of tokens away from $(y+1, x)$).
3. **Inability to Backtrack Efficiently:** LLMs lack native state graph memory to maintain visited states, leading to cycles and infinite loops in maze environments.

---

# TIER 3 — ENGINE INTERNALS & ADJACENT SIGNAL

### 3.1 `arcengine` & ARC-AGI-3 Game Engine Internals
- **Grid Representation:** All game frames are represented as 2D integer grids of shape $64 \times 64$, where values $0 \le c \le 15$ map to 16 distinct RGB palette colors.
- **Available Actions:**
  - `ACTION1` (Up / Move north)
  - `ACTION2` (Down / Move south)
  - `ACTION3` (Left / Move west)
  - `ACTION4` (Right / Move east)
  - `ACTION5` (Interact / Action key)
  - `ACTION6` (Click / Complex action with parameters `{"x": int, "y": int}`)
  - `ACTION7` (Auxiliary / Secondary action)
  - `RESET` (Full environment level reset)
- **State Lifecycle:** `NOT_PLAYED` $\to$ `NOT_FINISHED` $\to$ (`WIN` | `GAME_OVER`).

---

### 3.2 Discrete State Scoring Mathematics & Quadratic Weighting Proof

The official ARC-AGI-3 scorecard computes evaluation metrics via the following strict formulas:

#### 1. Per-Level Efficiency Score ($S_i$):
For each completed level $i$, the efficiency score is calculated relative to the human baseline $B_i$ and the actions taken $A_i$:
$$S_i = \min\left(115.0, \left(\frac{B_i}{A_i}\right)^2 \times 100\right)$$

#### 2. Weighted Environment Score ($E_j$):
Levels are linearly weighted by their depth $w_i = i$. For an environment with $N$ total levels where $k$ levels are cleared:
$$E_j = \left( \frac{\sum_{i=1}^k i \cdot S_i}{\sum_{i=1}^N i} \right) \times \left( \frac{k}{N} \right)_{\text{cap}}$$

#### 3. Aggregate Competition Leaderboard Score ($L$):
The final score across all $M = 25$ competition environments:
$$L = \frac{1}{25} \sum_{j=1}^{25} E_j$$

* **Mathematical Proof of ft09 Contribution:**
  - $N=6$ levels. Baselines: $[43, 12, 23, 28, 65, 37]$.
  - Agent actions: $[4, 7, 14, 16, 21, 13]$.
  - Ratio $(B_i/A_i)^2 > 1.15 \implies S_i = 100.0\%$ for all $i \in \{1 \dots 6\}$.
  - $E_{\text{ft09}} = \frac{\sum_{i=1}^6 i \cdot 100}{\sum_{i=1}^6 i} = 100.0\%$.
  - Isolated leaderboard contribution: $\frac{100.0\%}{25} = \mathbf{4.0000\%}$.

---

### 3.3 Connected Component Topologies & Discrete Invariant Solving

PipelineIQ replaces unguided search with **exact topological systems identification**:

1. **Toggle Matrix Solving (Linear Systems over $\mathbb{F}_2$ / $\mathbb{F}_3$):**
   - Extract centroid toggles $C = \{c_1, \dots, c_n\}$.
   - Construct adjacency toggle matrix $A \in \{0, 1\}^{n \times n}$.
   - Solve linear equation $A \cdot x = b \pmod 2$ using Gaussian Elimination over finite fields to find minimal click sequence in $\mathcal{O}(n^3)$ time.
2. **Valve & Flow Graph Routing:**
   - Detect static valve coordinates and obstacle masks via contour bounds.
   - Run Breadth-First Search (BFS) / Dijkstra with potential field gradients to route flow lines without trial-and-error.
3. **Dihedral Symmetry Orbit Reductions ($D_4$):**
   - When a level solution is discovered, project the macro sequence across the 8 transformations of the dihedral group $D_4 = \{I, R_{90}, R_{180}, R_{270}, H, V, D_1, D_2\}$ to solve mirrored levels instantaneously in 0 exploratory steps.

---

## 4. SUMMARY OF STRATEGIC IMPLICATIONS

1. **LLMs are structurally bottlenecked at ~1.8%** due to action latency and 64x64 coordinate hallucinations.
2. **Deep learning without symbolic/topological grounding cannot solve combinatorial level progression** (e.g. `ft09` or `vc33`).
3. **PipelineIQ's exact mathematical identification and thread-safe execution achieve 9.85%**, outperforming all public baselines by over **5.3x**.
4. The remaining 14 fallback games represent the next expansion frontier using program synthesis and discrete invariant search.
