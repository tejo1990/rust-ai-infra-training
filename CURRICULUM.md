# 4-Week Deliberate Practice Curriculum (Rust Systems × Python AI Infra)

* **가용 시간**: 주당 20시간 × 4주 (총 80시간)
* **핵심 전제**: 로컬 CPU 100% 재현 가능 (CUDA 커널·멀티GPU NCCL 버그 배제 → 환경 마찰 최소화)

---

## 1. Shadow PR 최적 오픈소스 레포 3곳 (직교 3계층)

| 순번 | 레포 & 필수 스코프 | 단련 근육 | 로컬 CPU 실행/검증 명령 |
| :--- | :--- | :--- | :--- |
| **1** | **`tokio-rs/tokio`**<br>(`M-sync`, `M-rt`, `M-time`) | Rust 저수준 동시성, `Acquire`/`Release` 메모리 오더링, `Pin`, `Waker` 경합, Cancellation Safety, `unsafe` 불변식 | `cargo test`<br>`RUSTFLAGS="--cfg loom" cargo test`<br>`cargo +nightly miri test` |
| **2** | **`vllm-project/vllm`**<br>(**`vllm/v1/core/` · `vllm/v1/engine/` 한정**) | Python AI 추론 제어 평면: V1 토큰 예산 스케줄러, Continuous Batching, Chunked Prefill, 선점(Preemption), 논리 KV 블록 할당/프리픽스 캐시 | `VLLM_TARGET_DEVICE=cpu pytest tests/v1/core/test_scheduler.py` |
| **3** | **`sgl-project/sglang`**<br>(**`sgl-router/` · `sgl-model-gateway/` · Rust RadixCache 한정**) | Rust ↔ Python AI 서빙 브리지: Intrusive LRU Radix Tree, 캐시 인식 L7/PD 라우팅, 락 경합, PyO3 FFI, Python Reference Parity Oracle | `cd sgl-router && cargo test`<br>(또는 `cd sgl-model-gateway && cargo test`) |

> **대체 옵션**: LLM 서빙보다 파일시스템 경합·네트워크 스트리밍·패키지 리졸버 비중을 높이고 싶다면 3번을 **`astral-sh/uv`**로 교체.

---

## 2. 좋은 훈련용 PR 선별 필터 (변경 20~300줄 + 테스트 포함 + 댓글 ≥ 5)

### A. 웹 검색 쿼리
```text
# Tokio (M-sync 또는 M-rt를 하나씩 번갈아 추가)
repo:tokio-rs/tokio is:pr is:merged label:C-bug label:A-tokio comments:>=5 (loom OR miri OR race OR deadlock OR cancel OR ordering) -label:C-docs

# vLLM V1 (CPU 제어 평면 한정)
repo:vllm-project/vllm is:pr is:merged comments:>=5 ("v1/core" OR "scheduler" OR "kv_cache" OR "prefix_cache") (fix OR bug OR race OR leak OR preempt OR evict) -cuda -rocm -tpu

# SGLang (Rust 라우터/게이트웨이 및 RadixCache)
repo:sgl-project/sglang is:pr is:merged comments:>=4 ("sgl-router" OR "sgl-model-gateway" OR "radix" OR "rust") (fix OR race OR deadlock OR leak OR evict OR lock)
```

### B. 스포일러 차단 자동 추출기 (`scripts/pick_shadow_pr.py`)
`gh` CLI가 없어도 Python 표준 라이브러리만으로 PR 번호·변경 라인 수·부모 커밋(`merge_sha~1`)·연결된 이슈 URL만 추출합니다(정답 `diff` 및 변경 파일명 비노출).

```bash
python scripts/pick_shadow_pr.py --preset tokio --limit 10
python scripts/pick_shadow_pr.py --preset vllm --limit 10
python scripts/pick_shadow_pr.py --preset sglang --limit 10
```

---

## 3. 병행 밑바닥 재구현 과제: `Mini-PagedRadix`

Rust 코어 + PyO3 바인딩 기반 **"KV 캐시 Radix 프리픽스 트리 + 연속 배치 토큰 스케줄러" & 결정론적 카오스 하네스**.

### 필수 구현 요건 (외부 자료구조·스케줄러 크레이트 금지)
1. **Rust Arena/Slab Intrusive LRU Radix Tree**: `Rc`/`RefCell` 금지. `Vec<Node>` + 인덱스 핸들 + Free-list로 노드 분할(Split)·병합(Merge)·축출(Evict) 불변식 구현.
2. **Paged KV Block Allocator & Preemption 상태 머신**: 고정 물리 블록 풀, Reference Counting, Copy-on-Write 분기, OOM 시 우선순위 선점(Preemption) 및 재투입.
3. **Python Reference Oracle + 50,000스텝 차등 퍼징(Differential Fuzzing)**: Python 150줄 순수 정답 모델(Oracle)과 Rust 코어에 동일한 랜덤 요청·취소·OOM 시퀀스 5만 스텝을 동시 주입해 100% 상태 일치 검증.
4. **PyO3 FFI 경계 + Tokio 멀티워커 캐시 인식 라우터**: GIL 해제(`py.allow_threads` / `py.detach`) 구간 분리, Tokio 기반 모의 워커(비선형 지연 + 랜덤 크래시) 앞단 Prefix-Match 라우팅.
5. **강제 카오스 장애 주입(Fault Injection)**:
   * 매 스텝 불변식 assert: `allocated_blocks + cached_blocks + free_blocks == TOTAL_BLOCKS`
   * 중도 취소(`Cancellation`) 30% + 워커 크래시 + 블록 풀 100% 포화 상태에서 데드락·Livelock·블록 누수·UB 0 달성.

---

## 4. 주당 20시간 × 4주 루틴

**고정 배분**: `Shadow PR 8h (2건 × 4h)` + `Mini-PagedRadix 9h` + `공개 트리아지·리뷰·회고 3h` = **20h/주**

| 주차 | 트랙 1: Shadow PR (8h) | 트랙 2: `Mini-PagedRadix` (9h) | 트랙 3: 공개 트리아지/리뷰 (3h) | 주간 통과 게이트 |
| :--- | :--- | :--- | :--- | :--- |
| **1주차** | `tokio` (`M-sync`/`M-time`) PR **2건** 역추적 | Rust Arena Radix Tree + Paged Block Allocator + 블록 보존 불변식 | 방치된 Open 이슈 2건 분석 및 로컬 재현 시도 | `cargo +nightly miri test` UB 0 + 블록 누수 0 |
| **2주차** | `vllm` (`vllm/v1/core/` CPU) PR **2건** 역추적 | Continuous Batching + Chunked Prefill + Preemption + **Python Oracle 5만 스텝 차등 퍼징** | 재현 성공한 Open 이슈 1건에 **MRE 또는 `git bisect` 결과 댓글**(PR 금지) | 50,000스텝 차등 퍼징 불일치 0 + Livelock 0 |
| **3주차** | `sglang` (Rust 라우터/Radix) PR **2건** 역추적 | **PyO3(GIL 해제)** + Tokio 캐시 인식 라우터 + **중도 취소 30%·워커 크래시 카오스 테스트** | 활발한 Open PR 2건 로컬 리뷰 작성 후 실제 메인테이너 리뷰와 대조 | 1,000 동시 요청 + 취소/크래시 10분 부하 시 누수·데드락 0 |
| **4주차** | *(6h)* `tokio` (`M-rt` + `Loom`) 고난도 PR **1건** 심화 | *(8h)* Python vs Rust+PyO3 **`flamegraph`/`py-spy` 프로파일링**, FFI 배치 최적화, ADR 작성 | *(6h)* 메인테이너와 사전 합의된 이슈 있으면 **첫 실전 PR 1건** (없으면 MRE 1건 추가) | "내 패치 vs 메인테이너 패치 설계 차이 TOP 5" 오답노트 완성 |

---

## 5. 훈련 효과 0 방지 3대 금지 규칙 (Anti-Illusion Rules)

1. **AI 코드 작성 OFF, 적대적 리뷰어 ON**: 패치·재구현 코드는 직접 작성. AI는 반례 생성·적대적 시니어 리뷰·API 조회로만 사용.
2. **90분 타임박스**: Shadow PR에서 90분간 원인을 못 찾으면 정답 구현 diff 대신 **테스트 파일 diff만 먼저 열어** 실패 시나리오 힌트를 얻고 재도전.
3. **리뷰 쓰레드 강제 대조**: 테스트 통과 후 반드시 원본 PR 리뷰 댓글을 읽고 **"내 패치가 업스트림에서 반려됐을 이유 3줄"**을 `notes/`에 기록해야 1회 완료 인정.
