# Training Progress Tracker

* **Current Stage**: Week 1 — Setup Complete / Ready for Shadow PR #1
* **Weekly Budget**: 20h (`Shadow PR 8h` + `Mini-PagedRadix 9h` + `Triage/Review 3h`)

---

## Week 1 — Rust Memory Model & Arena Core
- [ ] **Shadow PR #1 (`tokio` `M-sync`/`M-time`)**: PR `#___` | Parent: `___` | Postmortem: `notes/w1_tokio_pr1.md`
- [ ] **Shadow PR #2 (`tokio` `M-sync`/`M-time`)**: PR `#___` | Parent: `___` | Postmortem: `notes/w1_tokio_pr2.md`
- [ ] **`Mini-PagedRadix` Core**: Slab/Arena Intrusive LRU Radix Tree + Paged Block Allocator + `allocated + cached + free == TOTAL_BLOCKS`
- [ ] **Public Triage (No PR)**: 방치 Open 이슈 2건 분석 및 로컬 재현 시도
- [ ] **Week 1 Gate**: `cargo +nightly miri test` UB 0건 + 랜덤 분할/축출 블록 누수 0건

## Week 2 — Scheduler State Machine & Differential Fuzzing
- [ ] **Shadow PR #3 (`vllm` `vllm/v1/core/` CPU)**: PR `#___` | Parent: `___` | Postmortem: `notes/w2_vllm_pr1.md`
- [ ] **Shadow PR #4 (`vllm` `vllm/v1/core/` CPU)**: PR `#___` | Parent: `___` | Postmortem: `notes/w2_vllm_pr2.md`
- [ ] **`Mini-PagedRadix` Scheduler + Oracle**: Continuous Batching + Chunked Prefill + Preemption + Python Reference Oracle 50k-step Differential Fuzzing
- [ ] **Public Triage (No PR)**: Open 이슈 1건에 MRE 또는 `git bisect` 원인 커밋 댓글 작성
- [ ] **Week 2 Gate**: 50,000스텝 차등 퍼징 불일치 0건 + OOM 포화 시 Livelock 0건

## Week 3 — Rust↔Python FFI Boundary & Chaos Injection
- [ ] **Shadow PR #5 (`sglang` Rust router/Radix)**: PR `#___` | Parent: `___` | Postmortem: `notes/w3_sglang_pr1.md`
- [ ] **Shadow PR #6 (`sglang` Rust router/Radix)**: PR `#___` | Parent: `___` | Postmortem: `notes/w3_sglang_pr2.md`
- [ ] **`Mini-PagedRadix` FFI + Router + Chaos**: PyO3(GIL 해제) + Tokio 캐시 인식 라우터 + 중도 취소 30%·워커 크래시 카오스 주입
- [ ] **Public Review**: Open PR 2건 로컬 리뷰 작성 → 실제 메인테이너 리뷰와 대조
- [ ] **Week 3 Gate**: 1,000 동시 요청 + 취소/크래시 10분 부하 시 누수·데드락 0

## Week 4 — High-Difficulty Integration & First Live Sparring
- [ ] **Shadow PR #7 (`tokio` `M-rt` + `Loom`)**: PR `#___` | Parent: `___` | Postmortem: `notes/w4_tokio_loom.md`
- [ ] **`Mini-PagedRadix` Profiling & ADR**: Python vs Rust+PyO3 `flamegraph`/`py-spy` 계측, FFI 배치 최적화, ADR 작성
- [ ] **Live Sparring**: 사전 합의된 이슈 있으면 첫 실전 PR 1건 (없으면 억지 PR 금지, MRE 1건 추가)
- [ ] **Week 4 Gate**: "내 패치 vs 메인테이너 패치 설계 차이 TOP 5" 오답노트 완성 (`notes/top5_design_gaps.md`)

---

## Session Handoff Log (PC 전환 시 1줄 기록)

| Date (KST) | Machine | Completed | Next Action |
| :--- | :--- | :--- | :--- |
| 2026-11-24 | PC-1 (Windows + WSL2 Ubuntu-24.04) | 커리큘럼·핸드오프·규칙·스크립트 초기 패키징 | 새 PC에서 `HANDOFF.md` 복붙 → Week 1 `tokio` Shadow PR #1 시작 |
