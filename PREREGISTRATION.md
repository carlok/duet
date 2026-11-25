# Preregistration

Each section is committed before its run starts. Changes after the start are listed under "Deviations".

## X10: stage c under a cap, with the search beside it (written 25 Nov 2026, 06:03 UTC, before X10 starts)

Exploratory and descriptive. X9 left 156 stage-c tasks and showed two gaps (deviation 11). Both are fixed:
`--cap-c` and the drain rule (`f9a774e`), and `--max-c` (`3e7394b`); see REPORT, "The stage-c cap and the drain rule".
The user chose an 8-hour night run with the search beside stage c over a full drain, which would take about 33 hours.

**What stage c has done so far** (`notes/stagec_history.py`, output `notes/stagec_history.out`):
- Since T4 it settled about 7 of the 96 claims it ran on (7.3%), all by Vampire FMB, and proved none. Since X5, when FMB
  entered stage c, the figure is 7 of 52 (13.5%). The mean is 37.7 minutes per theory over all runs.
- The 156 tasks hold 221 unknown claims: 6 tasks have none left, 85 have one, 59 two and 6 three. Their priorities run
  from 12.8 to 25.0, and none is a candidate or in N1.
- So the run is not expected to change a candidate. It measures stage c under a cap, and it continues the search.

**Design.**
- **Data directory:** `x10`, a fork of X9's state, made this morning so that the smoke runs could copy it. x9 has not
  changed since.
  - `soup.t4_setup --dir x10`, then its corpus is replaced by a copy of X9's (16,826 files);
  - X9's `queue/stage2c` (156), `queue/pending` (1) and `queue/seen` (18,333) are copied in;
  - so are the 156 stage-b results that the stage-c tasks read, and nothing else from `results/`;
  - `soup.known build --out /data/x10`: 51 known entries, 1,651 candidate entries, 62,038 seen-before keys.
- **Arm and verifier:** arm `fusion4`, verifier V7, as in X9.
- **Processes:** 6 searchers kept alive (`--min-searchers 6`) and 4 verifiers.
  - `--max-c 2 --cap-c 2`: two stage-c tasks whenever the lane has work, never more. v0 prefers stage c, one more
    verifier joins it there, and the other two work on stages a and b.
  - The verifier floor is then 3, so the rebalancer can move one verifier to search if pending runs dry.
  - The pending lane is capped at 1,500 (the default `--qmax`).
- **Memory:** `--recycle-mb 700`, `--mem-stop-mb 1000`. MemAvailable is now logged every tick.
- **Budget and seeds:** 28,800 s (8 h); seeds from 1401.

**Run:**
1. Compare `date -u` with `podman machine ssh date -u`, and keep the Mac awake for the whole budget (the app's
   keep-awake).
2. `podman run -d --name soup-x10 -v "$PWD/work:/data" -e SOUP_DATA=/data/x10 -e SOUP_VERIFIER=V7 soup python3 -m
   soup.stream.supervisor --arm fusion4 --searchers 6 --verifiers 4 --min-searchers 6 --max-c 2 --cap-c 2 --seed0 1401
   --budget 28800 --recycle-mb 700 --mem-stop-mb 1000 --run x10`.

**Done before this entry, disclosed.**
- **Code:**
  - `--cap-c`, the drain rule and the fresh-heartbeat check (`f9a774e`);
  - `--max-c` and the MemAvailable log (`3e7394b`);
  - 101 tests pass.
- **Smoke runs** on copies of the fork, deleted afterwards (`notes/capsmoke.py`):
  - `capsmoke`: 5 verifiers, no searcher, cap 2 (REPORT).
  - 6 searchers, 5 verifiers, `--max-c 3 --cap-c 3` (`notes/x10smoke_cap3.out`): the memory rule fired after 217 s
    (860 MB). The three stage-c tasks started together, and their long E runs grew at the same time. That was the first
    design, dropped.
  - 6 searchers, 4 verifiers, `--max-c 2 --cap-c 2` (`notes/x10smoke_cap2.out`): ran its 900 s.
    - MemAvailable fell to 2,516 MB while both E runs grew, then stayed near 5.6 GB.
    - 22 theories were verified, about 44 per stage-a/b verifier-hour.
    - 426,187 evaluations were made, 0.28M per searcher-hour at a steady rate. X8 + x8b made about 0.72M; X9's corpus is
      about twice X8's.
    - The pending lane reached 1,500 in 4 minutes.
  - Nothing else was read.

**Predictions** (descriptive):
- **U1, the cap:** no tick in `logs/stats.jsonl` has more than 2 workers in stage c, and the run reaches its budget
  without the memory rule.
- **U2, stage-c throughput:** at least 12 of the 150 copied tasks with open claims get through stage c. Two slots over
  8 h at 40 minutes would be 24; under load X8 took 71 minutes.
- **U3, stage-c yield:** stage c settles at least 5% of the claims it runs on, and proves at most one. Since T4 it has
  settled 7.3% and proved none.
- **U4, the search:** level 0 rises by at least 10M, to at least 125.1M. The smoke rate gives about 13M for 48
  searcher-hours. Restated in the amendment below.
- **U5, verification beside stage c:** at least 400 new theories get through stages a and b (the smoke rate gives about
  700).

**Amendment (written 25 Nov 2026, 08:02 UTC, before X10 starts).**
- **Code since this entry:** the column cache in `Corpus.has` (`74a07ff`; REPORT, "Why the searchers slowed down"). It
  changes the searchers' speed only: on 3,000 replayed proposals their outputs are byte-identical. X10 runs with it.
- **A second smoke run** with X10's exact command, 900 s on a fresh copy of the fork, deleted afterwards
  (`notes/smoke_rate.py` and `notes/capsmoke.py`, output `notes/x10smoke_cache.out`):
  - 0.60M evaluations per searcher-hour, against 0.28M in the cap-2 smoke, measured the same way (from the first tick
    with evaluations to the last live tick);
  - stage c peaked at 2 tasks, and MemAvailable fell to 2,133 MB at 333 s (the cap-2 smoke: 2,516 MB);
  - only 7 theories got through stages a and b (the cap-2 smoke: 22). One of the two stage-a/b verifiers spent 850 s on
    one theory in stage b, and two parameter screens took about 170 s each with E unknown.
- **U4, restated:** level 0 rises by at least 22M, to at least 137.1M. The new rate gives about 29M for 48
  searcher-hours, and the threshold keeps the old margin (10M of 13M). The rate will fall as the corpus grows.
- **U5 is kept at 400.** The two smokes give 14 and 44 theories per stage-a/b verifier-hour, so 220 to 700 over the
  run: U5 is less likely to hold than when it was written.
- Nothing else changes.

**After the run:**
- X9's post-run pipeline with x10 added (`taxonomy.RUNS`, `funnel.DIRS`, `known.RUN_DIRS`): the split per candidate,
  dedupe, N1, F1, the funnel, the linear sweep and a REPORT section.
- The 156 copied results are reported apart, since their stages a and b ran in x8, x8b or x9.

**Caveats.**
- **Double counting:** level 1 and F1 count the copied results under both x9 and x10, as with the 65 in X9. The distinct
  count is reported.
- **Wall time under load:** E's limits are CPU time, but those of FMB, Mace4 and the linear screen are wall time, and
  10 processes on 11 cores slow them down.
- **The lane is ordered by priority:** the highest-priority tasks will be done and most of the rest will not.
- **A sleeping Mac:** if it sleeps, the VM freezes and the budget runs on a frozen clock (24 Nov). That would be a
  deviation.

## X9: verifier V7 drains X8's queue (written 24 Nov 2026, 22:27 UTC, before X9 starts)

Exploratory and descriptive. X8 + x8b were search-heavy (8 searchers, 3 verifiers), and verification was the bottleneck:
444 verified in 9 hours, with 1,256 theories and 65 stage-c tasks left in the queue (REPORT, "X8 + x8b"). The user chose
a run that works through that queue with a faster verifier, starting tonight.

**Verifier V7** (`soup/verify.py`) = V6 plus two changes, both measured on X8 + x8b:
- **No z3 after an E proof** (`z3_after_e=False`). Since V2 a claim's difficulty is E's proof length; the z3 run on a
  claim E had proved only kept the z3 effort comparable with old runs. On X8 + x8b z3 hit its cap on 113 of 269
  E-proved claims, and the 86 theories with such a claim took 4.2 of stage b's 11.3 hours. Scores do not change.
- **Linear models** (`soup.linear`) for each claim E neither proves nor saturates:
  - in stage b, after E's small run and before FMB, on rings up to 32 elements and affine models up to 9, 60 s;
  - in stage c, before FMB and Mace4, on the full range (rings up to 64, affine up to 16), 600 s;
  - a model counts only after `check_offline.check_finite` accepts it, and it goes into the corpus;
  - the post-run sweep refuted 14 of X8's 116 open claims this way, all linear, on 8 to 17 elements.

**Design.**
- **Data directory:** `x9`, a fork of X8's state:
  - `soup.t4_setup --dir x9`, then its corpus is replaced by a copy of X8's (7,708 structures);
  - X8's `queue/pending` (1,256), `queue/stage2c` (65) and `queue/seen` (18,333) are copied in;
  - so are the 65 stage-b results that the stage-c tasks read, and nothing else from `results/`;
  - `soup.known build --out /data/x9` then includes X8's candidates and seen keys (62,038).
- **Arm and verifier:** arm `fusion4`, verifier V7.
- **Processes:** 7 verifiers and no searcher at the start.
  - The rebalancer starts searchers only from idle verifiers, as in every run, so the search resumes once the queue
    runs low.
  - The pending lane is capped at 5,000 (`--qmax 5000`), so no copied task is trimmed.
- **Memory:** `--recycle-mb 700`, `--mem-stop-mb 1000`.
- **Budget and seeds:** 28,800 s (8 h); searchers started by the rebalancer get seeds from 1301.

**Run:**
1. the fork (`t4_setup`, copies, `soup.known build`), as above;
2. `podman run -d --name soup-x9 -v "$PWD/work:/data" -e SOUP_DATA=/data/x9 -e SOUP_VERIFIER=V7 soup python3 -m
   soup.stream.supervisor --arm fusion4 --searchers 0 --verifiers 7 --seed0 1301 --budget 28800 --qmax 5000
   --recycle-mb 700 --mem-stop-mb 1000 --run x9`.

**Done before this entry, disclosed.**
- **Code:** V7, with `tests/test_v7.py`; 96 tests pass.
- **Benchmark of stage b** (`notes/v7_bench.py`, output `notes/v7_bench.out`):
  - V6 against V7 on 24 X8 theories with their recorded stage-a output: 12 with a z3-capped E proof, 12 with a hard
    claim, seed 9, from theories whose stage b took at most 600 s.
  - V7 took 600 s against V6's 1,424 (58% less). 5 claims changed outcome, all to a linear refutation: three
    from unknown, two from an FMB refutation. No score changed.
  - A first version searched the full range in stage b: 21% less, with up to 60 s added per hard claim. That is why
    stage b now stops at 32 elements.
- **Smoke runs** on forks of X8's state, 4–6 minutes each, all deleted afterwards:
  - 10 verifiers and 1 searcher: the stage-c tasks were dropped, because their stage-b results had not been copied. Hence
    the results copy above.
  - With the results copied, 10 and 8 verifiers both tripped the memory rule (911 and 966 MB available) once two
    stage-c tasks ran together, with prover processes capped at 2 GB each.
  - 7 verifiers and no searcher (one stage-c task at a time): at least 6.4 GB stayed available; 57 verified in 6
    minutes, and the copied pending lane fell from 1,256 to 1,199.
  - With 1 searcher, about 200 new theories were pushed in 4 minutes, enough to crowd out the copied ones; hence no
    searcher at the start.
  - Nothing else was read.

**Predictions** (descriptive):
- **S1, throughput:** at least 25 theories through stages a and b per verifier-hour, 1.5 times x8b's 16.9 (397 in
  3 × 7.85 h). Verifier-hours are the time integral of the live verifier count in `logs/stats.jsonl`.
- **S2, stage c:** a mean of at most 35 minutes per theory through stage c, half of x8b's 70.6 (8.24 h for 7).
- **S3, the linear screen:** it refutes at least 5% of the claims it runs on in stage b.
- **S4, the queue:** at least 1,000 of the 1,256 copied pending theories get a result.

**After the run:** X7's post-run pipeline with x9 added (`taxonomy.RUNS`, `funnel.DIRS`, `known.RUN_DIRS`), the split per
candidate, dedupe, N1, F1, the funnel and a REPORT section. The 65 copied stage-b results are reported apart: their
stages a and b ran in x8b under V6.

**Caveats.**
- The copied queue is what X8's verifiers had not reached, after trimming by priority. So the comparison with x8b is
  not randomized, and the hardest stage-c tasks may be among the copied ones.
- Seven verifiers load the machine more than three did. E's limits are CPU time, but FMB's and the linear screen's are
  wall time.
- The theories were found by X8's searchers but are verified in x9, so F1 counts them under x9.
- One stage-c task at a time: most of the 65 stage-c tasks will not be reached.

## X8: search-heavy, toward 100M (written 24 Nov 2026, 08:03 UTC, before X8 starts)

Exploratory and descriptive. The user's aim (24 Nov), in their words: 50M is "the dust removed", 100M "the surface
scratched", 200M "digging". They chose a search-heavy run.
- **Level 0:** the corrected funnel count, raw, with distinct beside it: 63,662,919 before X8.
- **Why search-heavy:** in X5–X7 the rebalancer cut 4 searchers to 1 within 30 minutes.

**Design.**
- **Arm and verifier:** arm `fusion4` with verifier V6, as in X7.
- **Library:** the known library and the seen-before keys are rebuilt with `soup.known build --out /data/x8`, so
  they include X7.
- **Processes:** 8 searchers and 3 verifiers. `--min-searchers 8` means the rebalancer never retires a searcher.
  It can still turn an idle verifier into a searcher, keeping at least 2 verifiers.
- **Memory:** verifiers recycle above 700 MB private (`--recycle-mb 700`), and the run stops below 1,000 MB available
  (`--mem-stop-mb 1000`).
- **Budget and seeds:** 32,400 s (9 h), seeds 1201–1208.

**Run:**
1. `python -m soup.t4_setup --dir x8`;
2. `soup.known build --out /data/x8`;
3. `podman run -d --name soup-x8 -v "$PWD/work:/data" -e SOUP_DATA=/data/x8 -e SOUP_VERIFIER=V6 soup python3 -m
   soup.stream.supervisor --arm fusion4 --searchers 8 --verifiers 3 --min-searchers 8 --seed0 1201 --budget 32400
   --recycle-mb 700 --mem-stop-mb 1000 --run x8`.

**Done before this entry, disclosed.**
- `--min-searchers` was added to the supervisor, with a test. 86 tests pass.
- `soup.known` now also reads x4a and X7 for the seen-before keys, which number 43,705 (X7 had 38,701). Before this
  fix, X7's own theories would not have been skipped.
- A 4-minute engineering smoke run (`work/x8smoke`, seeds 1991–1998, deleted afterwards):
  - the 8 searchers stayed alive with no rebalancing;
  - they made 719,100 evaluations (about 10.8M per hour at the start, on the small starting corpus), of which each
    searcher counted about 83% as distinct;
  - 309–356 MB PSS per searcher, and 10.4 GB still available at the end;
  - 15 theories verified. Nothing else was read.

**Predictions** (descriptive):
- **R1:** the raw funnel level 0 passes 100M, so X8 adds at least 36.4M.
- **R2:** distinct evaluations are at least 70% of X8's raw ones (X7: 73.8%).
- **R3:** the parameter screen fires on less than 5% of X8's verified theories (X7: 2.2%).
- **R4:** F1, recomputed with X8, gives X8 at least one new structured family that holds at least 2% of X8's
  verified theories.

**After the run:** X7's post-run pipeline with x8 added (split per candidate, merged into
`check/split_candidates.json`). Then F1 (`soup.taxonomy build --confirm`, `report`), the funnel and a REPORT section.

**Caveats.**
- With 3 verifiers, most pushed theories are never verified. The queue is trimmed to 1,500 by priority, so the
  verified ones are the searchers' best.
- Evaluations get slower as the corpus grows. With fewer verifiers the corpus grows more slowly, which works the
  other way.

## F1: families of verified theories, and emerging patterns (post hoc; written 24 Nov 2026, 07:41 UTC, before it is computed)

Descriptive. The user's request (24 Nov): a statistic of families and their percentages next to the funnel, and the
emerging patterns. Code: `soup/taxonomy.py`. Data: every verified theory (`results/*.json` with laws) in the run
directories of the funnel. x4a's results are left out, as in the funnel. Percentages are per run directory, over all
of its verified theories.

**Primary family**, the first rule that matches, so the shares sum to 100% per run:
1. **Disguise:** stage a screened it (`screened`: split, division or parameter definition; V4 on).
2. **Known:** `check/rediscover.json` relates it to a catalogue entry, under some relabelling, as a fragment,
   subvariety or equivalent, proved by E. The model-only kinds ("subvariety?") do not count. Its key is also known
   if the ledger `notes/rediscovery.md` identifies it. The subtype is the catalogue entry, the first in catalogue
   order.
3. **No synergy:** no proved emergent law.
4. **Diagonal:** a proved emergent law in one variable (`offdiag.ONEVAR`).
5. **Argument-ignoring:** on the corpus it implies an `offdiag.IGNORE` law (X4's attractor).
6. **Structured:** everything else, labelled by its reduct signature.

A rule for square-ignoring laws (`IGNORE2`) was considered and dropped before this entry: every totally symmetric
quasigroup satisfies x·(x·x) = y·(x·y), so the rule would file classical structure as an attractor.

**Reduct signature.** Eleven properties of one operation, written for ·:
- commutative x·y = y·x; associative; idempotent x·x = x; constant squares x·x = y·y;
- squares are right identities x·(y·y) = x, and left identities (y·y)·x = x;
- left involutive x·(x·y) = y, and right involutive (y·x)·x = y;
- flexible x·(y·x) = (x·y)·x; x·(y·z) = x·y, and its mirror (x·y)·z = y·z.

With the same eleven for ∘, that is 22 laws, a set closed under the 8 relabellings.
- A theory has a property when the law holds in every model of the theory in the union of all runs' corpora.
- The signature lists the properties of · and of ∘. "TSQ" abbreviates commutative and left involutive.
- The family label is the least label over the 8 relabellings, so relabelled twins share a family.
- Evidence: for structured theories, E is asked for each property the corpus gives (10 s, 200,000 processed
  clauses). The confirmation rate is reported, and an unconfirmed property is marked model-implied.

**Emerging patterns.** Runs in time order: root, t4-prior, t4-noprior, x1, …, x7.
- A structured family is **new** in a run if no earlier run has a theory in it.
- It is **emerging** in a run if it has at least 10 theories there and its share there is at least twice its share in
  all earlier runs together.
- The same two flags are applied to proved emergent laws, each taken up to the 8 relabellings.
- **The accumulation curve:** distinct structured families against cumulative verified theories, and at each run's
  end against cumulative level 0. Chao1 (S + f1²/(2 f2), with f1 and f2 the families seen once and twice) estimates
  how many exist in total.

**Predictions:**
- **F1a:** in X7, "structured" is the largest primary family, and in T4 (t4-prior and t4-noprior together) its share
  is under 10%.
- **F1b:** at least 10% of the structured families seen up to X7 are new in X7.

**Caveats.**
- Corpus implication over-approximates real implication, so a signature can be too rich. The E confirmation
  bounds this error.
- A fixed list of 11 properties names only what it lists. Two theories in one family can still differ a lot.
- The "known" rule relies on our catalogue, not on the literature.

## X7: skip what is already known, a night run (written 23 Nov 2026, 19:46 UTC, before X7 starts)

Exploratory and descriptive. The user's instruction (23 Nov): "skip the already known, do not risk to do again the
same", and a new level-0 measurement.

**Design.** Arm `fusion4` is X6's `fusion2` plus three changes (`soup/known.py`, `soup/stream/searcher.py`). The
verifier is V6, as in X6.

1. **Known-library skip.**
   - Built once before the run by `python -m soup.known build --out /data/x7`, from the shared data and the ledger.
   - The library, each entry under all 8 relabellings:
     - 129 known entries: the 13 catalogue entries, which include the 10 named theories, and the 15 candidates
       identified in the ledger;
     - 1,097 entries for the other earlier candidates.
   - A theory is skipped if, on the corpus, it is a fragment or a subvariety of a known entry, or equivalent to an
     earlier candidate.
   - A strengthening of an unidentified candidate is not skipped: it is new ground.
   - The library's corpus view is rebuilt every 30 minutes.
2. **Seen-before skip.** The 38,701 theory keys that earlier runs pushed or verified (`seen_before.json`) are never
   inserted or pushed again.
3. **Distinct level 0.** A one-hash bitmap of 2^27 bits per searcher, estimated by linear counting. The bitmaps are
   saved at the end, so the distinct count across searchers is computed post hoc from their union.

**Unattended safety.** The memory rule, applied by hand in X1, X3 and X6, is now code: `--mem-stop-mb 1000` stops
the run cleanly when MemAvailable falls below 1,000 MB, and the stop is reported in the journal. It is the same
preregistered rule, applied automatically, so a stop is not a deviation. The budget is 28,800 s (8 h), with 4
searchers, 4 verifiers and seeds 1101+.

**Run:** `python -m soup.t4_setup --dir x7`, then `soup.known build --out /data/x7`, then `podman run -d --name
soup-x7 -v "$PWD/work:/data" -e SOUP_DATA=/data/x7 -e SOUP_VERIFIER=V6 soup python3 -m soup.stream.supervisor --arm
fusion4 --searchers 4 --verifiers 4 --seed0 1101 --budget 28800 --mem-stop-mb 1000 --run x7`.

**Done before this entry, disclosed.**
- `tests/test_x7.py` was added, and the whole suite passes (80 tests).
- A 4-minute engineering smoke run (`work/x7smoke`, seeds 1991–1994, deleted afterwards) checked that nothing breaks.
  Per evaluation it skipped about 7% as known, 0.2% as earlier candidates and 0.05% as seen before. Distinct
  evaluations were about 88% of raw. 15 theories were verified, 5 with a positive score. Nothing else was read.

**Predictions** (descriptive):
- **Q1:** post hoc, `soup.relabel` and `soup.rediscover` find no fragment or subvariety of a named or catalogue
  theory among X7's top 20, and `soup.dedupe` finds no top-20 candidate equivalent to an earlier one.
- **Q2:** the union of the searchers' bitmaps counts at least 80% of raw evaluations as distinct.
- **Q3:** X7's top 20 holds at least 10 distinct varieties, and at least 5 are "disconnected" (X6: 17 and 7).
- **Q4:** the parameter screen fires on less than 24% of verified theories (X6: 24%).

**After the run:** X6's post-run pipeline, with x7 added.
- Fragments, statistics, candidates, profile, `soup.hidden` (plain and `--param`), relabel, rank and rediscover.
- Split per candidate, with the results merged into `check/split_candidates.json`.
- Disconnected marks, dedupe, N1, the funnel, and a REPORT section.

**Caveats:**
- The skips rely on the corpus, which over-approximates implication. A skipped theory may not really be a fragment
  or subvariety: the error goes towards skipping too much.
- The library holds only what our checks and the ledger know, not the literature.
## X6: X5 with the parameter-definition screen, a longer run (written 23 Nov 2026, 06:39 UTC, before X6 starts)

Exploratory and descriptive. The user chose the design on 23 Nov: verifier V6, arm `fusion2` as in X5, not `fusion3`.

**The single change from X5.** Verifier V6 = V5 plus a third stage-a screen. If one operation is a term in the other
plus a constant square (`soup.hidden.hidden_param` on the census models, then E for 10 s), the theory scores 0. Post
hoc, the check catches 18 of X5's 20 top candidates and none of the other 138 candidates (REPORT, "The two filters").

Everything else is as in X5:
- arm `fusion2`;
- 4 searchers and 4 verifiers;
- the memory stop rule (available memory below 1 GB, reported), and nothing heavy alongside.

The seeds are 1001+. The budget is **28,800 s (8 h)**, against X5's 9,000 s. The user asked for more cheap
evaluations (level 0), and a longer run also tests whether the search keeps finding new varieties over time. Counts
are therefore not comparable with X5; shares and per-hour rates are.

Setup: `python -m soup.t4_setup --dir x6`. Run: `podman run -d --name soup-x6 -v "$PWD/work:/data" -e
SOUP_DATA=/data/x6 -e SOUP_VERIFIER=V6 soup python3 -m soup.stream.supervisor --arm fusion2 --searchers 4 --verifiers 4
--seed0 1001 --budget 28800 --run x6`.

**Tests before the start.** The whole suite passes (75 tests, including `tests/test_x6_filters.py`). An engineering
smoke run of V6 (4 min, arm `fusion3`, deleted, REPORT) showed no screen errors.

**Predictions** (descriptive, no p-values):
- Q1: post hoc, `soup.hidden --param` catches none of X6's top 20. A hit would mean the screen leaks, for example
  through census models too few for the term search.
- Q2: X6's top 20 holds at least 10 distinct varieties (`soup.dedupe`). X5 had 5, one of them holding 15 candidates.
- Q3: the attractor of X5, x·(x·x) = y·(x·y), stays among the three most frequent proved emergent laws. `fusion2`
  does not filter it.
- Q4: at least 15 of the top 20 have a classical model. The rigid region is dense in affine structures, and V6 removes
  only the translate disguise.

**After the run**, as for X5, with `x6` added to the sources:
1. fragments, statistics, `notes/x5_predictions.py` extended to x6;
2. candidates (`--sources ...,x5,x6`), profile, hidden, relabel, rank, rediscover;
3. `notes/disconnected.py x6 x5`;
4. split per candidate (`soup.split --laws`, 300 s each; the X5 workaround);
5. `soup.hidden --param` on the candidates (Q1);
6. `soup.dedupe` with `x6`, then `soup.novelty` and `soup.funnel`.

The split scan of all non-fragments comes last and only if time allows.

**Caveats:**
- An 8-hour run grows the corpus more than the earlier runs did, so the cheap score drifts more within the run.
- The census can be small. The parameter screen then works on few models, and Q1 checks for exactly that.

## X5: the fusion arm, restricted to rigid theories (written 22 Nov 2026, 21:37 UTC, before X5 starts; the first commit said 21:40, an estimate)

Exploratory and descriptive. The aim is the user's: steer the search away from X4's attractor and toward fusions
that work but are not clearly connected to known structure.

**Why this restriction, measured before writing this.**
- **X4's attractor.** It was off the diagonal but still about squares: `x · (x · y) = x · x` and its kin. Of X4's 565
  scored theories, 483 (85%) prove a claim with a subterm `s · s` or `s ∘ s`.
- **First design, rejected.** It excluded laws with a square subterm (26,980 of 71,369 laws) and was rejected on two
  measurements, neither from a run:
  1. With those laws as background, McKenzie's positive control loses commutativity. With idempotence, a square law
     such as `x · (y · y) = y · x` is commutativity in disguise.
  2. Without them as background, a sample of 150 X4 theories still gains the same attractor in square-free form.
     The most frequent remaining law is `x · (x · y) = x · (x · z)`.
- **What the attractor really is.** A derived operation of order ≤ 2 that ignores an argument. Call a law
  *argument-ignoring* if it reads `t = t'`, where `t'` is `t` with one variable that occurs once renamed to a fresh
  one. Examples are `x · y = x · z`, `x · (x · y) = x · (x · z)` and `x · (x ∘ y) = x · (x ∘ z)`. There are 53 such
  laws (`soup.offdiag.IGNORE`). On X4's final corpus, 519 of its 565 scored theories (92%) imply one. On samples of 300,
  X4 has 28 rigid theories and X3 has 15. Script: `notes/x5_baseline.py`, output
  `notes/x5_baseline.out`.

**The single change from X4.** Arm `fusion2` is arm `fusion` plus one skip.
- Any theory whose corpus-implied laws contain an argument-ignoring law is skipped and counted in the heartbeats
  (`ign_skipped`).
- The corpus over-approximates implication. So a theory that passes really implies no argument-ignoring law: a
  finite model refutes each one.
- What is left are *rigid* theories, in which every derived operation of order ≤ 2 depends on all its arguments, as
  in quasigroups and rings. Absorption, the lattice region, bands and X4's attractor are all excluded.
- Everything else is as in X4: verifier V5, the off-diagonal score, the lattice skip, the pools, 4 searchers and
  4 verifiers, a budget of 9,000 s. Seeds are 801+.
- The stop rule is as in X3 and X4: available memory below 1 GB, reported. Nothing heavy runs alongside.
- Setup: `python -m soup.t4_setup --dir x5`.
- Run: `podman run -d --name soup-x5 -v "$PWD/work:/data" -e SOUP_DATA=/data/x5 -e SOUP_VERIFIER=V5 soup python3 -m
  soup.stream.supervisor --arm fusion2 --searchers 4 --verifiers 4 --seed0 801 --budget 9000 --run x5`.

**Done before this entry, disclosed.** A 4-minute engineering smoke run (`work/x5smoke`, seeds 901–904, deleted
afterwards) checked that the skip does not starve the search. About 4% of evaluations were skipped, and 12 theories
were verified, 7 with a positive score. Nothing else from it was read.

**Tests before the start** (`tests/test_fusion.py`, the whole suite, 71 tests, passes):
- the masks on named laws;
- absorption, McKenzie's basis and an attractor theory each imply an argument-ignoring law on the corpus;
- the left quasigroup with `∘` its left division implies none.

**Predictions** (descriptive; none is a test with a p-value):
- P1: by construction, no X5 theory implies an argument-ignoring law on X5's final corpus. A violation would be a bug.
- P2: the ten most frequent proved emergent laws of X5 share at most 3 with X4's.
- P3: the share of scored theories with a proved claim containing a square is below X4's 85%.
- P4: the classical constructions (affine, group-derived, rings), which are rigid, model more of the top-20
  non-fragments than in X4. The risk is that X5 mostly finds known quasigroup and ring fragments.

**After the run, as X4** (sources plus `x5`):
1. fragments;
2. top 20 into the candidates;
3. profile, `soup.hidden`, `soup.split`, `soup.relabel`;
4. T5a ranking, dossiers, Lean;
5. `soup.rediscover`;
6. `notes/disconnected.py`;
7. `soup.dedupe`, with `x5` in its corpora;
8. `soup.novelty --readme`;
9. the split scan of X5's non-fragments, last.

**Reported next to X4:**
- theories verified per hour;
- the share with a proved off-diagonal law;
- the ten most frequent proved emergent laws;
- fragment share;
- V4 marks;
- skips;
- FMB refutations;
- identification share of the top 20;
- the disconnected marks;
- N1 entries from X5.

**Caveats:**
- The rigid region is where quasigroups, groups and rings live. Rediscovery there is likely, and the catalogue covers
  it less well than the lattice region, so "unidentified" is weaker still.
- The skip depends on the corpus, which grows during the run.
- An empty or near-empty result is possible and gets reported.

## N1: a novelty ranking of the candidates (post hoc; written 22 Nov 2026, 15:40 UTC, before it is computed)

**Why.** The preregistered T5a ranking sorts candidates by the features that separate named theories from random
ones: a convergent presentation, then a duality. It rewards resemblance to the known, which is right for "is this
the kind of structure algebraists name?" and wrong for the user's aim: a fusion that works but is not clearly
connected to anything known. X4's theories have no duality by design, so T5a puts them low whatever they are. N1 is
a second ranking, used *alongside* T5a, not instead of it. The user asked for it (22 Nov, afternoon).

**Status at the time of writing.** X4's candidate checks (profile, hidden, split, relabel) are running. Two of
their log lines were seen in passing: `d82738a2` not definitional, `94d69dd2` not split. No other X4 candidate
check, no R1 result on X4 and no dedupe result has been read.

**Input.** The candidate pool, `work/check/candidates.json`: the top 20 non-fragments by verified score of each run
(`.`, `t4-prior`, `t4-noprior`, `x1`, `x2`, `x3`, `x4`), plus T1 and T2. It runs after the X4 post-run, R1 on X4, and
`soup.dedupe` on the pool.

**Gate.** A candidate enters N1 only if all of these hold:
1. **It works.** Its verification record has at least one proved emergent law, and its profile shows
   non-degenerate models on at least 2 sizes. Candidates with no verification record (T1, T2) are listed apart.
2. **Nothing identifies it.**
   - Not split (`soup.split` True). `None` is allowed but flagged.
   - Not definitional (`soup.hidden`), and no V4 mark.
   - No relation in `soup.relabel`: none of implies, fragment of, equivalent to.
   - No R1 relation to a catalogue entry: none of fragment, subvariety, equivalent. A relation with "?" is allowed
     but flagged.
3. **One per variety.** From each class of `soup.dedupe` (equivalent under the 8 relabellings), only the member with
   the highest verified score enters.

**Order** among those that pass, lexicographic:
1. A proved emergent law that is **off-diagonal**: not a diagonal law, and in `soup.offdiag.offdiag_gain` on the
   corpus of the candidate's own run. Yes first.
2. **No classical model**, as in the X4 entry: no non-degenerate structured probe on 3 or more elements. Yes first.
3. **Not related** to a known structure by a partial identification in the ledger (`notes/rediscovery.md`). These
   are `10c98c4b` (its core is Δ-bijectivity), `3e068fa6` (its finite models are Δ-bijective pairs) and `31d6d970`
   (its associative case is the rectangular skew lattices). Unrelated first. The list is fixed now; later ledger
   rows do not change N1.
   *Clarification (22 Nov 2026, 18:11 UTC, after `soup.dedupe` and before N1 is computed).* A partial
   identification belongs to the variety, so it applies to every member of the candidate's dedupe class. `soup.dedupe`
   puts `2dc27508`, `69dfbd8e` and `31d6d970` in one class (E both ways under rev∘; equal model counts on 3 and 4
   elements). Its representative, `2dc27508` (highest score), therefore carries `31d6d970`'s flag.
4. **More sizes with non-degenerate models**, from the profile spectrum.
5. **Smaller axioms**: the sum of the orders of the laws.
6. **Verified score**, higher first, as the last tie-break. Scores from different verifiers are not comparable, so
   it only breaks ties.

**Outputs.**
- `work/check/novelty_ranking.json`, and the N1 top 20 with every mark.
- `notes/candidates_table.md` (added at the user's request, 15:43 UTC, before computing), in two tables:
  - **known:** every candidate a check identifies, with what it is and which check said so;
  - **not known as far as our checks and searches go:** the N1 list in order, with its marks as the metric.

  Below them: candidates that fail "works", and those with no verification record.
- A live summary in `README.md`, between `<!-- candidates:start -->` and `<!-- candidates:end -->` (`--readme`;
  added at the user's request before computing): the metric, the counts, and the N1 top 10. It is regenerated each
  time `soup.novelty` runs, which is after every run's checks.
- The gate counts: how many fail each condition.
- The overlap of N1's and T5a's top 10.
- The share of each run in N1's top 10. Expectation, not a test: X4 takes a larger share of N1's top 10 than of
  T5a's.

**Follow-up.**
- New N1 top-10 entries get a dossier, a Lean certificate of the smallest model, and a literature check (a web-only
  agent, key claims rechecked by E). Wording: no candidate is called new without a check by someone who knows the
  field.
- Code: `soup/novelty.py`, committed with this entry, before it is run.

**Caveats.**
- N1 is post hoc and descriptive.
- Its gate depends on our checks and catalogue: "unconnected" means unconnected to them.
- Its first key favours X4 by construction, since X4 selected for off-diagonal laws.

## X4: fusion arm, away from the diagonal and the lattice corner (written 22 Nov 2026, 10:40 UTC, during X3, before X4 starts)

Exploratory and descriptive only: no hypothesis is tested. The user's aim (22 Nov, morning): find theories in the
spirit of the "jazz" example, an original jump of the kind a human makes, and look for strategies that find
legitimate, probably unexplored, valid new theories. Two measurements motivate X4:
- **Coverage.** All runs together verified 4,222 theories against 1.8 × 10²⁶ law sets, and the duality prior keeps
  them in the most-studied corner (`notes/coverage.py`, REPORT "Coverage").
- **A diagonal attractor.** Of the 3,596 theories with a positive verified score in T4, X1, X2 and X3 (10:43 UTC,
  X3 running), 3,478 (97%) prove an emergent law in one variable. The ten most frequent proved emergent laws are all
  about squares (`x·x = x∘x`, `x·(x·x) = x·x`, `x·x = x`, ...), and none of the 3,596 proves emergent associativity.
  So the score rewards what a fusion forces on the diagonal. The lattice absorption pair, our reference case, is
  itself such a case. Script: `notes/diagonal.py`, output `notes/diagonal_pre_x4.out`. A first one-off tally at
  10:40 counted only three laws (`x·x = x`, `x∘x = x`, `x·x = x∘x`): 2,495 of 3,574, 70%. That figure was in this entry's
  first commit, `3faeeb9`.

Setup and arm:
- Setup: `python -m soup.t4_setup --dir x4`, own `SOUP_DATA=/data/x4`, as X2 and X3.
- Search: new arm `fusion` (`soup/stream/searcher.py`, `soup/offdiag.py`). It is arm `noprior` (no duality operator,
  no duality bonus) with three changes:
  1. **Off-diagonal gain.** The cheap score counts only laws that T implies on the corpus and that no single law of
     T implies even together with all the one-variable laws T implies. Weights by order: 1, 0.5, 0.25, 0.125 (the
     old weights gave order-4 laws, such as associativity, weight 0). *Changed after a 3-minute first attempt
     (deviation 6):* "one-variable laws" became "diagonal laws", laws in which each side has at most one variable
     (adding x·x = y·y and its kin).
  2. **The lattice corner is skipped.** Theories that hold in the 2-element lattice are not scored. The count of
     skipped theories goes into the heartbeats.
  3. **Tradition-fusion proposals.** In the 25% slot the prior arm uses for duality closure: one law in · alone and
     one in ∘ alone, each drawn from a pool of restrictive one-operation laws with non-degenerate corpus models at
     three or more sizes, plus one random bridge. These are two "traditions" and a bridge between them. The other
     mutations are unchanged.
- Verifier V5 (`soup/verify.py`) = V4, but stage a draws its claims from the off-diagonal emergent laws. So the
  verified score counts only laws the fusion produces without going through the diagonal. The split and division
  screens of V4 stay.
- 4 searchers and 4 verifiers, seeds 701+, budget 9,000 s. The stop rule is as X3: memory below 1 GB, reported, and
  nothing heavy alongside.
- Tests before the start: `tests/test_fusion.py`.
  - Positive control: McKenzie's lattice basis has commutativity of both operations among its off-diagonal emergent
    laws.
  - Negative control: the absorption pair's emergent `x·x = x` does not count.
  - The 2-element lattice holds the lattice laws and not the Δ-bijective core; the pools are one-operation and
    non-empty.

  The whole suite must pass.

After the run, in this order (as X3, with `x4` added to the sources):
1. the fragment check;
2. the top 20 non-fragments join the candidate list;
3. profile, `soup.hidden`, `soup.split`, `soup.relabel` on the new candidates;
4. the T5a ranking, dossiers and Lean certificates for new top-10 entries;
5. `soup.rediscover` on X4;
6. the split scan of X4's non-fragments, last.

Post hoc, and labelled as such: the off-diagonal gain of X3's verified theories, computed on X3's final corpus, as a
baseline for how often off-diagonal synergy occurs without being selected for.

Reported descriptively, X4 next to X3:
- theories verified per hour;
- the share of verified theories with a proved off-diagonal emergent law;
- the ten most frequent proved emergent laws (does a new attractor appear?);
- fragment share;
- V4 marks;
- theories skipped as lattice-valid;
- FMB refutations;
- the share of the top-20 non-fragments that the post hoc checks identify;
- the top 20 that no check identifies.

Each unidentified one gets a literature check (Latin-square, quasigroup, Yang–Baxter/rack/cycle-set, bisemilattice
and ETP sources). None is called new without that check and a check by someone who knows the field. Our web
searches are weak evidence (REPORT, "Coverage").

**Added 22 Nov 2026, 12:54 UTC, before X4 starts: "disconnected" candidates.** The user confirmed the reading of the
jazz example and added a second one: something that works but is not clearly connected to what came before.
Post hoc, on X4's top-20 non-fragments, and on X3's 19 as a baseline, each candidate gets three marks:
- **works:** non-degenerate models at two or more sizes, and at least one proved emergent law (off-diagonal for X4);
- **unconnected:** none of the checks relates it to anything known. That means no fragment, subvariety or equivalence
  to any of the 13 catalogue entries under the 8 relabellings (R1's method), no V4 mark, not split, not definitional
  (`soup.hidden`), and no relation in `soup.relabel`. A relation left unknown by E's budget counts as unknown, not as
  unconnected;
- **no classical model:** no non-degenerate model on 3 or more elements among the structured probe families (affine
  over ℤ/n, 𝔽₄, Klein, ℤ/n with + and ×, S₃, the min/max and Boolean families, M₃, N₅). Random tables, the complete
  set on 2 elements, and the structures found by the search do not count as classical.

Reported:
- the number of candidates with all three marks, X4 against X3;
- the list of those candidates, each with its literature check.

Script: `notes/disconnected.py`, written during the run, before any X4 result is read. "Unconnected" means
unconnected to our checks and catalogue. It is no claim about the literature, which gets its own check.

Caveats:
- Three changes at once: what X4 finds cannot be attributed to one of them.
- X4 scores differently from X3, so scores are not comparable across the two runs. Shares and counts are.
- The pools and the off-diagonal gain depend on the corpus, which grows during the run.
- An empty result (no theory with a proved off-diagonal emergent law) is a possible outcome, and it gets reported.

## X3: an exploratory run with filters for known disguises (written 22 Nov 2026, 06:45 UTC, before X3 starts)

Exploratory and descriptive only: no hypothesis is tested. The night showed that most top candidates are old
structures in disguise: split theories, and one-operation varieties with their division written as ∘. X3 asks
what the search finds when those two disguises score nothing. The user's framing (22 Nov, morning): measuring
rediscovery should help new findings, not replace the search for them.

- Setup: `python -m soup.t4_setup --dir x3`, with its own `SOUP_DATA=/data/x3`, as X2.
- Search: as X2. Arm `prior`, 4 searchers and 4 verifiers, seeds 601+. No change to the search code.
- Verifier V4 (`soup/verify.py`) = V3 plus two screens in stage a, after the census:
  - **Split screen.** `soup.split.screen` looks for a certificate of non-split on 2–4 elements. Without one,
    `soup.split.prove_split` runs (E, 30 s). A proved split sets `split` in the result and gives verified score 0.
  - **Division screen.** `soup.relabel.check` runs against the left and right quasigroup pairs only, under the 8
    relabellings (E, 10 s per law). If T implies one, ∘ is a one-sided division of · (or the reverse): `division`
    is set and the verified score is 0.

  Neither screen uses the R1 catalogue or anything outside the code (rule 6). Tests: `tests/test_v4.py`.
- Budget: 10,200 s from the start, the same as X2. The first version of this entry (commit `534c1af`) said 10,800
  s. It was changed before the start because X2's available memory reached a minimum of 1,026 MB, just above the
  stop rule, with nothing alongside.
- Stop rule: as X2. The budget runs out, or the VM's available memory drops below 1 GB, which gets reported. Nothing
  else heavy runs next to it.
- After the run, in this order:
  1. the fragment check;
  2. the top 20 non-fragments by score join the candidate list (sources `t4-prior,t4-noprior,.,x1,x2,x3`);
  3. profile, `soup.hidden`, `soup.split` and `soup.relabel` on the new candidates;
  4. the T5a ranking of all candidates, dossiers and Lean certificates for new entries in the top 10;
  5. `soup.rediscover` (R1's method) on X3's verified theories;
  6. a split scan of all X3 non-fragments (`soup.split --fragments 1 --jobs 4`), run last.
- Reported descriptively, X3 next to X2:
  - theories verified per hour;
  - fragment share;
  - split and division marks set by V4;
  - claims refuted by FMB;
  - the share of the top-20 non-fragments that the post hoc checks identify as split, division or a catalogue
    entry;
  - the top 20 and where they land in the ranking.
- Caveats: V4 sets split and division theories to score 0, so X3's archive differs from X2's by construction. The
  comparison is descriptive. The corpus at the start is the main `work/corpus` (as X2).

## R1: rediscovery against a fixed catalogue (post hoc; written 22 Nov 2026, 06:45 UTC, before anything is computed)

Post hoc analysis of existing results. The user's framing (22 Nov, morning): rediscovery has value as a process.
It is measured here against a catalogue fixed in advance.

- Catalogue: `soup/catalogue.py`, `KNOWN`, 13 entries, committed with this section:
  - the 10 named theories of T3 (`soup.calib.NAMED`, unchanged);
  - doppelsemigroups (= mutually interassociative semigroups);
  - weakly associative lattices;
  - Δ-bijective pairs, marked `post_hoc`: it was added because candidate `10c98c4b` contains it.

  Sources are in the file. All entries have laws of order ≤ 4. Quasilattices were dropped: their axioms have
  order 5.
- Data: every verified theory with a law list in `.`, `t4-prior`, `t4-noprior`, `x1` and `x2` (and `x3` after it
  runs).
- For each theory T, entry K and relabelling r (`soup.relabel.relabellings`, 8, including the 3 dualities):
  - **fragment**: every law of T holds in r(K) (r(K) ⇒ T), and T has an emergent law;
  - **subvariety**: T ⇒ every law of r(K);
  - **equivalent**: both.

  Method: a model filter first. The corpus models of r(K) (resp. T) must satisfy the law (`Corpus.implied`). Then
  E proves it: 10 s and 500,000 processed clauses per law. Only proofs count, and an E timeout is "unknown".
  Results are cached per (r(K), law) and per (T, r(K)).
- **Primary outcome:** the number of catalogue entries rediscovered at least once (some T equivalent to, or a
  fragment of, some r(K)). Reported out of 13 and out of the 12 entries that are not `post_hoc`, per data
  directory and overall.
- Secondary outcomes:
  - counts of fragment, subvariety and equivalent per entry and per directory;
  - for the top-20 non-fragments of each run, the share identified by any route (split, division, a catalogue
    relation).
- Positive controls: the lattice fragments of `fragments.json` (as written) must reappear, and `10c98c4b` must be a
  subvariety of the Δ-bijective entry.
- Budget: 6 jobs and a 2 h wall cap, with nothing else heavy alongside. Theories not reached are reported.
- Caveats:
  - Post hoc. The catalogue was written by us after seeing the results, with the help of an LLM working outside
    the search, and it covers only structures with axioms of order ≤ 4.
  - Equivalence is up to the 8 relabellings, not up to arbitrary term equivalence. `soup.hidden` and `soup.split`
    cover two other kinds.

## X2: a second exploratory run, as X1 (written 22 Nov 2026, 04:25 UTC, before X2 starts)

Exploratory and descriptive only: no hypothesis is tested. The user asked that, with time left, a fresh batch of
candidates go through the pipeline again. X1 was cut to 1.5 h (deviation 4).

- Setup: `python -m soup.t4_setup --dir x2`, with its own `SOUP_DATA=/data/x2`. Matrix files are linked; the corpus
  is copied from the main `work/corpus` at setup.
- Search and verifier: exactly as X1. Arm `prior`, 4 searchers and 4 verifiers, verifier V3, seeds 501+. No code
  change to the search or the verifier.
- Budget: 10,200 s from the start (until about 07:20 UTC).
- Stop rule: as X1. The budget runs out, or the VM's available memory drops below 1 GB, which gets reported.
  Nothing else heavy runs next to it: no scans, no profiles, no prover batches. Light reads and docs only.
- After the run, in this order:
  1. the fragment check;
  2. the top 20 non-fragments by score join the candidate list (sources `t4-prior,t4-noprior,.,x1,x2`);
  3. profile, `soup.hidden`, `soup.split` and `soup.relabel` on the new candidates;
  4. the T5a ranking of all candidates, dossiers and Lean certificates for new entries in the top 10;
  5. a split scan of all X2 non-fragments (`soup.split --fragments 1 --jobs 4`), run last.
- Reported descriptively:
  - theories verified;
  - fragment share;
  - claims refuted by FMB;
  - split share among non-fragments;
  - the top 20 non-fragments and where they land in the ranking.
- Caveats: the corpus at the start includes neither X1's models nor X1's corpus. Not compared with X1 or T4 by a
  test.

## X1: exploratory run with verifier V3 (written 21 Nov 2026, night, during T4, before X1 starts)

Exploratory and descriptive only: no hypothesis is tested, and nothing from X1 enters T4's analysis.

- Purpose: more verified theories, from the duality-prior search, for the T5a ranking and the dossiers. The user
  asked to use the rest of the night this way.
- Setup: `python -m soup.t4_setup --dir x1`, i.e. its own `SOUP_DATA=/data/x1`. Matrix files are linked, and the
  corpus is copied from the main `work/corpus` at the time of setup.
- Verifier V3 (`soup/verify.py`): V2 plus Vampire finite model building. Stage b runs it for 60 s on every pending
  claim that E's small run neither proves nor saturates, starting from the smallest size stage a left unsearched,
  or 7. Stage c runs it for 600 s before Mace4. A model counts only after `check_offline.check_finite`.
- Search: arm `prior` (the duality closure and score factor as in T4), 4 searchers and 4 verifiers, seeds 401+.
- Budget: from the start until 07:30 UTC, at most 14,400 s. It starts after the T4 analysis, the T5a profile run
  and the T4 profiles.
- Stop rule: the budget runs out. The run is stopped early only if the VM's free memory drops below 1 GB; that would
  be reported.
- Reported descriptively:
  - verified theories;
  - the share that are fragments (`fragments.py`), without comparison to T4;
  - claims refuted by FMB that stage a missed;
  - the top 20 non-fragments by score.

  The top 20 then go through the profile and the T5a ranking, with the others in its candidate list.
- Caveats:
  - The corpus of X1 starts larger than T4's: it includes tonight's S10 model and the sweep's models.
  - Score and selection are as in T4. V3 refutes more claims than V2, so V3 scores are not comparable with T4
    scores.

## T5a: does an algebraist's profile separate named from random theories? (written 21 Nov 2026, night, before the run)

Why: the synergy score does not prefer named theories (T3, H2), so it cannot pick out theories a universal
algebraist would find interesting. Before candidates are ranked by structural features, those features are tested
on the same calibration set.

Theories: the 130 of T3 (`work/calib_t3.json`): 10 named, 120 random, including the 2 whose T3 verification
crashed. The profile needs only the laws.

Profile: `python -m soup.profile --set t3 --jobs 8` (code at the commit of this section), one child process per
theory, 1,800 s limit. Budgets:
- Mace4 enumerates all models of sizes 2–4 (60 s each) and size 5 (120 s), capped at 3,000 models per size.
- Models are counted up to isomorphism.
- Term functions: up to 60 models of sizes 2–4 for ternary terms (size ≤ 5); up to 120 models of sizes 2–5 for
  binary terms (size ≤ 7); 60 s and 20,000 functions per arity.
- E proves each identity of a candidate term in 30 s and 500,000 processed clauses, for at most 3 candidates per
  kind.

Features, all binary:
- **F1 `malcev_term` (primary):** some term of size ≤ 5 is a majority, Mal'cev, Pixley or minority term, and E
  proves every identity of that kind from the axioms.
- **F2 `finite_free2`:** the binary term functions on the models close under both operations. This is a finite
  free algebra on 2 generators of the variety generated by those models.
- **F3 `convergent`:** an E saturation against x = y passes the `soup.confluence` checks, i.e. a convergent
  presentation of a non-trivial theory.
- **F4 `spectrum3`:** non-degenerate models on at least 3 of the sizes 2–5.

Hypotheses and tests:
- H1: named theories have F1 more often than random ones. One-sided Fisher exact test.
- H2–H4: the same for F2, F3 and F4. One-sided Fisher, Holm-corrected over the three.
- A crashed profile is reported and left out of the test for each feature it lacks.

Use in ranking (fixed now, before any T4 or exploratory-run theory is profiled). Candidates are:
- the 20 best non-fragment theories by V2 score from each T4 arm;
- T1 and T2;
- the 20 best non-fragment theories of the earlier runs;
- the 20 best of the exploratory run, if it runs.

The ranking:
1. Exclude fragments of a named theory (`fragments.py`: valid) and theories that E proves equivalent, both ways,
   to a variety on the standard list (semilattices, bands, rectangular bands, left- and right-zero bands,
   lattices, distributive lattices, quasigroups), on either assignment of the two operations.
2. Rank by the number of features with p < 0.05 after Holm that the theory has. Ties are broken by duality, then
   by the number of sizes with non-degenerate models, then by V2 score.
3. If no feature reaches p < 0.05, nothing is ranked. Candidates are listed with their features, and the profile is
   reported as not calibrated.

Every listed theory is a candidate, not a result (rule 4), until a literature check and the equivalence checks are
done.

Seen before this section: the profile code was debugged on 3 of the 10 named theories, without the random ones:
- lattice: F1 (a majority term of size 4, proved), F2 (4 functions), F4;
- absorption pair: F3, F4;
- left quasigroup: F3.

No random theory and no T4 theory had been profiled.

## T4: duality-prior search against a matched control (written 21 Nov 2026, evening, before the run)

- **Arms.** `prior`: the searcher with the duality-closure mutation and the score factor (1 + number of
  dualities). `noprior`: the same searcher without both (same filters: bridge, non-degenerate model,
  definitional theories rejected; same cap of 6 laws). Code as of the commit that adds this section.
- **Isolation.** Each arm has its own data directory (`python -m soup.t4_setup`): matrix files linked, a copy
  of the corpus store as it stands after the stage-c sweep of 21 Nov 2026 (the common start), and its own
  queue, dedup markers, gate, results, journal and corpus growth. Nothing is shared between the arms while
  they run.
- **Verifier V2** (`SOUP_VERIFIER=V2`, `soup/verify.py`), the score change decided before this run:
  - difficulty of a proved claim = E 3.2.5 `--auto` proof steps / 10 (z3 effort still recorded);
  - a claim E did not prove gets 0.1;
  - stage a verifies one claim per order level (at most 4 pending, 12 tried);
  - every E saturation gets a convergence certificate;
  - stage c starts Mace4 at the smallest size stage a left unsearched.
- **Compute.** Both arms run at the same time on the 11-core VM, each under its own supervisor: 2 searchers
  and 3 verifiers at the start. Rebalancing within an arm is allowed; the total stays 5 processes per arm.
  Budget 14,400 s (4 h) per arm. Seeds: prior 201–, noprior 301– (one per searcher started). z3-solver
  5.4.1.0, E 3.2.5, Mace4 2026-8A.
- **H1 (primary).** Among verified theories with positive score, the share that are fragments of at least
  one of the 10 named theories of T3 (`python -m soup.fragments`; a law is valid by an E or z3 proof, invalid
  by a corpus model of the named theory or a certified saturation) is higher in `prior` than in `noprior`.
  One-sided Fisher exact test, α = 0.05; undecided theories are excluded from the test, and the two bounds
  (undecided counted as fragments, as non-fragments) are reported. Pilot (first session, different verifier,
  control without the definitional filter): 64/97 against 6/59.
- **Secondary (descriptive).** The 10 highest-scoring non-fragment theories per arm, deduplicated across arms
  up to the three dualities and up to equivalence (E proves each theory's laws from the other; compared only
  when the model counts on 2–5 elements agree). None is called new without a literature check and a check
  against the Equational Theories Project data where the theory specialises to one operation.
- **Stop rule.** Each arm runs once for its budget, without extension or rerun. Crashed workers are restarted
  by the supervisor and reported. If a supervisor dies, its arm is reported as it stands; a rerun would be a
  deviation, written before it starts.
- **Known limits, reported with the result.** Only queue-top theories get verified (priority by the cheap
  score): any arm difference inherits this selection. The arms' corpora diverge as each verifies its own
  theories; that is part of each arm. E's proof length is an upper bound on proof length: proof minimisation
  shortens ETP proofs several-fold (Kondylidou, Blanchette, Heule, arXiv:2605.21200: 62 to 20 steps, 151 to
  10), so V2 difficulty ranks proofs only roughly. (Added before the run, after the literature check.)
- **Analysis.** `SOUP_DATA=/data/t4-prior python -m soup.fragments`, the same for `t4-noprior`, then
  `python -m soup.t4_report`.

## T3: calibration, named vs random theories (written 21 Nov 2026, before the run)

- **Theories.** 10 named theories of order ≤ 4 (`soup/calib.py`): lattice, skew lattice, dimonoid,
  absorption pair, left quasigroup, right quasigroup (the first session's six), plus bisemilattice,
  right absorption pair, idempotent left quasigroup, idempotent right quasigroup. (Racks and quandles do not
  fit: left self-distributivity has order 5.)
  Random theories: 30 per size k present among the named ones (k = 2, 3, 5, 6: 120 in all), k distinct
  laws uniform over the 71,368 non-trivial laws, kept if ≥ 1 bridge and a non-degenerate base-corpus model.
  Seed 11.
- **Verification.** `verify` stages a+b with E (z3-solver 5.4.1.0, E 3.2.5), on the shared corpus store.
- **H1 (primary).** Named theories have a duality more often than random ones. Test: one-sided Fisher exact
  test on the 2×2 table (named/random × duality yes/no), α = 0.05. The named theories were chosen by people,
  and several were chosen *because* they are symmetric: H1 is a sanity check of the duality prior, not a
  discovery.
- **H2 (descriptive, no test).** On gain, max difficulty (z3), max E proof steps, model richness and score,
  report each named theory's percentile among random theories of the same size. First-session expectation:
  9th–91st percentiles, i.e. these measures do not separate named from random theories.
- **Stop rule.** All 130 theories verified once; no reruns, no exclusions after the fact. A theory whose
  verification crashes is reported as such.
- **Analysis.** `python -m soup.calib_report work/calib_t3.json`.

## Deviations

1. **T3, k = 6 null (21 Nov 2026, before any calibration result existed).** Uniform rejection sampling
   accepted 0 of 267,682 draws at k = 6 (k = 5: 7 of 308,389; k = 3: 1,650 of 434,019; k = 2: 31,473 of
   549,832; 20 s each). The k = 6 random theories are instead drawn model-first: a non-degenerate base
   structure uniformly at random, then 6 distinct laws it satisfies, at least one a bridge. Same filter,
   different weighting; the 6-law comparisons (lattice, skew lattice, bisemilattice) are reported as against
   this null. k = 2, 3, 5 stay uniform. Fisher's test is reported on all random theories and on the uniform
   ones only.
2. **T3, crashed run resumed (21 Nov 2026, evening, after 69 of 130 results existed).** The run stopped
   at 69 results: the kernel of the Podman VM OOM-killed one worker (python, 5.9 GB resident, 12:56 VM time),
   and the broken process pool ended the whole run. Which theories were in flight is not known; none of them
   has a result. The 69 results were looked at before this deviation was written (duality counts: named 8/10,
   random 0/59); nothing below depends on them.
   - Fix: every theory runs in its own child process. z3 is capped at 1.5 GB (as in the stream verifier);
     E and Vampire are capped at 2 GB. A child that dies, or runs longer than 1 h, is recorded as `crashed`.
     6 theories at a time instead of 10.
   - The 61 theories without a result (1 at k = 2, 5 at k = 3, 25 at k = 5, 30 at k = 6) are verified once
     with the same verifier settings (`verify.V1`). The 69 results are kept and not rerun.
   - A theory that crashes is reported as crashed. It counts for H1, since having a duality is syntactic,
     and is left out of the H2 percentiles.
   - Caveats: the 69 ran without memory caps, which can only turn a run that would have used more memory
     into an unknown; the shared corpus has grown since the start (stream runs), so later theories see more
     structures. Both are reported with the results.

3. **T5a, provers killed by the VM's OOM killer (22 Nov 2026, ~01:50 UTC, after the T5a result was seen).**
   - What happened: the T5a profile ran with 8 jobs, alongside the candidate profile (3 jobs) and `t4_report`,
     which ran 10 E processes at once. The kernel log of the Podman VM shows 10 OOM kills between 01:28 and
     01:41 UTC:
     - `soup-t5a`: 3 profile children, reported as crashed, plus 3 E runs;
     - `t4_report`: 3 E runs;
     - the candidate profile: 1 E run.
   - Why it matters: the profile recorded a killed E run as "not proved" or "did not saturate", which is a
     feature value of 0, not a crash. Which theories were affected cannot be told from the output. The
     analysis as run reported F3 (`convergent`) as calibrated (named 6/10, random 13/117, Holm p = 0.0022) and
     F1, F2, F4 as not calibrated. 3 random theories crashed.
   - Fix (commit after this entry): a prover or Mace4 killed by a signal now gives the value *unknown* for the
     feature it feeds. Per the T5a rule for crashed profiles, an unknown value leaves that theory out of that
     feature's test. `t4_report` takes its pool size from `T4R_JOBS` and reports equivalence checks whose E run
     crashed as unknown.
   - Reruns:
     - all 130 T5a theories, with the fixed code and 4 jobs, nothing else heavy running, into
       `check/profile_t3_rerun.json` (`python -m soup.profile --set t3 --name t3_rerun --jobs 4`), analysed with
       `python -m soup.profile --t5a t3_rerun`;
     - the 62 candidates, from scratch with the fixed code (the partial run is kept as
       `check/profile_candidates_asrun.json`);
     - `t4_report` with `T4R_JOBS=3`. Its primary outcome does not use E, so it cannot change.
   - Reported: both T5a analyses, as run and rerun. Fixed now, before the rerun: the ranking uses only the
     features calibrated in **both** (`soup.dossier rank`).
   - The OOM killer also hit T4 once (searcher s302 of noprior, 00:00 UTC). The supervisor restarted it, as
     preregistered; REPORT lists it with the T4 crashes.
4. **X1, stopped by its memory rule (22 Nov 2026, 03:50 UTC, before any X1 result was analysed).** X1 started at
   02:20:41 UTC with a 14,400 s budget. At 03:50:29 UTC the watcher read 170 MB of available memory in the VM, below
   the preregistered 1 GB, and stopped the run (`podman stop -t 30`; the supervisor's last journal line is
   "stopped by signal" at 03:50:43, the container exit code 137). It ran 1 h 30 min of the planned 4 h.
   - Most likely cause: I started two post hoc split scans (`soup.split --fragments`, 1 job each, each loading the
     corpus) about two minutes earlier, alongside X1's 8 workers. Twenty minutes later the VM had 9.2 GB available
     and the kernel log showed no OOM kill in the last 30 min.
   - Not restarted: the stop rule says stop, and a second start would be a run with a different budget and corpus.
   - Reported: X1 as run (1.5 h), with the descriptive outcomes listed above. The top 20 non-fragments go through
     the profile and ranking as planned.
5. **X3, stopped by its memory rule (22 Nov 2026, 11:08 UTC, before any X3 result was analysed).** X3 started at
   08:33:28 UTC with a 10,200 s budget. At 11:08:32 UTC the watcher read 975 MB of available memory, below the
   preregistered 1 GB, and stopped the run (`podman stop -t 30`; journal "stopped by signal" at 11:08:37; exit code 137).
   It ran 9,304 s, 91% of the budget: 970 theories verified.
   - Likely cause: the run's own memory. The supervisor's PSS total rose from 7,087 MB (10:45) to 8,334 MB (11:07). X2,
     with the same worker count, ended at a minimum of 1,026 MB.
   - Nothing of mine ran in the last 23 minutes. Earlier, during the run, two light read-only containers counted
     result files (`notes/coverage.py` at 10:14, `notes/diagonal.py` at 10:43), each finishing in seconds.
   - The VM also hosts four containers of other projects. Together they use about 120 MB.
   - Not restarted. Reported as run, with the post-run steps as planned.
   - For X4: its budget (9,000 s) is below the point where X3 stopped. The stop rule is unchanged.
6. **X4, stopped after 3 minutes and restarted with a widened definition (22 Nov 2026, 12:58 UTC).** The first attempt
   (`work/x4a`, started 12:55:23) verified 19 theories. 18 had a positive score, and none proved a one-variable emergent
   law, as designed. But 10 of the 18 proved x·x = y·y, and most of the rest proved its kin: x·(x·x) = y·y,
   x·(x·x) = x·(y·y) (`notes/diagonal_x4a.out`). These laws have two variables but speak only about squares. The fusion
   forces the square map to be constant instead of the identity: the same diagonal attractor in another form. The
   entry's stated intent is laws "the fusion produces without going through the diagonal", and these go through it.
   - Change: D, the laws a single law may use, is now every diagonal law T implies: each side has at most one variable
     (`soup.offdiag.DIAG`). The consequences of such laws, such as x·(x·x) = x·(y·y), are then covered through
     implied({t} ∪ D).
   - Tests: `tests/test_fusion.py` gains a mask test and a regression test on x4a's top theory `19b5765e`, where
     x·x = y·y is emergent but no longer counts. The positive and negative controls still pass, and so does the whole
     suite (68).
   - Everything else is as preregistered: arm, seeds 701+, budget 9,000 s from the restart, stop rule, post-run steps.
   - Reported: x4a as a separate 3-minute attempt, with its tally. The first form of the attractor is itself an outcome:
     with one-variable laws excluded, the search found the next diagonal loophole within three minutes.
7. **X4 post-run: `soup.split` on the candidates stopped after 17 of 20 (22 Nov 2026, 17:28 UTC).** The step ran from
   about 15:37. For a candidate with no finite certificate, `prove_split` gives E up to 200 attempts of 30 s, so the
   last 3 could have taken about five more hours.
   - Results by then: 14 not split (finite certificate), 3 undecided.
   - The 3 left (`f1f50575`, `33eca86a`, `d82738a2`) passed V4's split screen during the run, like every X4 theory
     with a positive score. N1 flags them "split not run", as its gate already allows.
   - `soup.relabel` then ran on its own. Every other post-run step is unchanged.
8. **X5 post-run: the split check of the candidates was rerun per candidate (23 Nov 2026, about 01:00 UTC).**
   - `soup.split --set candidates` goes through the candidates in file order. Capped at 1,800 s, it stalled on one
     of X4's three unchecked candidates (deviation 7) and checked none of X5's.
   - It was rerun per candidate (`soup.split --laws`, 300 s each, 4 in parallel). Result: 0 split, 1 not split,
     19 undecided (REPORT, X5).
9. **X6 stopped by its memory rule (23 Nov 2026, 12:25 UTC, before any X6 result was analysed beyond the progress
   counts in the journal).**
   - X6 started at 06:40:02 UTC with a budget of 28,800 s.
   - At 12:25 UTC the VM had 702 MB available, below the 1 GB rule. The X6 container held 11.06 GB: the workers'
     PSS was 7.3 GB, and prover child processes are not counted in it.
   - `podman stop -t 120` ended it cleanly at 12:26:33 UTC, after 20,790 s (72% of the budget). The kernel log shows
     no OOM kill.
   - Results by then: 1,460 verified, 645 with a positive score, 4,004,695 cheap evaluations, and 8,055 structures
     added to the corpus.
   - Every post-run step is unchanged. Counts are for the 5.8 hours that ran, and per-hour rates are computed on
     those hours.

10. **X8 stopped by its memory rule after 70 minutes, because of an image rebuild next to it (24 Nov 2026, 10:19 UTC;
    written 10:26 UTC).**
    - X8 started at 09:09:52 UTC with a budget of 32,400 s.
    - At 10:13 UTC a `podman build` was started next to the run, for a reporting-only change (a Chao1 caveat in
      `soup.taxonomy`). This breaks the rule "nothing extra next to a stream run".
    - About an hour earlier, 78 old soup images had been removed to free disk space. `podman rmi` also removed their
      untagged parent images, which were the build cache, so the build compiled the provers from source.
    - At 10:19:29 UTC the VM had 754 MB available, below the 1,000 MB rule. The supervisor stopped the workers, and the
      run ended at 10:19:37 UTC after 4,183 s (13% of the budget). Exit code 0, no OOM kill.
    - Results by then: 49 verified, 33 with a positive score, 8,453,911 cheap evaluations. The queue (1,500 pending,
      3 in stage c) is kept for the next run.
    - **Decision (user, 10:29 UTC):** continue as run `x8b` in the same data directory (`SOUP_DATA=/data/x8`).
      - Settings unchanged, except seeds 1209 onward (X8 used 1201–1208) and the remaining budget, 28,217 s.
      - Nothing else runs beside it, not even a build.
      - R1–R4 are judged over X8 and x8b together, and the report gives each part's counts separately.

11. **X9 stopped by its memory rule after 2 hours, once X8's copied queue was empty (25 Nov 2026, 00:29 UTC; written
    00:38 UTC, after S1–S4 were computed but before anything else).**
    - X9 started at 22:28:27 UTC with a budget of 28,800 s.
    - The pending lane was empty at 00:28:24 UTC. 1,255 of the 1,256 copied theories had a result, and the last one
      was still claimed.
    - With nothing pending, the verifiers took stage-c tasks: six of the seven were in stage c at 00:29:29 UTC. Until
      then two or three had been in stage c at a time, and memory had held.
    - At 00:29:45 UTC the VM had 362 MB available, below the 1,000 MB rule. The supervisor stopped the workers, and the
      run ended at 00:29:58 UTC after 7,291 s (25% of the budget). Exit code 0, and the kernel log shows no OOM kill
      during the run.
    - **The design was wrong on one point.** It said searchers would start once the queue ran low, and none did. The
      rebalancer starts a searcher only in place of an idle verifier, and a verifier with nothing pending takes
      stage-c work instead of going idle. So X9 made no cheap evaluations.
    - Results by then: 1,262 verified, 808 with a positive score, 9,118 structures added to the corpus. The queue
      left (1 pending, 156 in stage c) is kept for the next run.
    - S1–S4 are judged on the 2 hours that ran, and per-hour rates use those hours. Nothing else changes.
    - The VM also holds the user's other containers, idle, with about 0.7 GB between them. They have been running since
      before X9 and its smoke runs.
