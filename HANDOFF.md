# Cross-PC Conversation Handoff Pack

다른 PC에서 새 Antigravity(또는 LLM) 대화를 열었을 때 **이전 대화의 결론·제약·훈련 규칙을 0% 손실로 복원**하기 위한 문서입니다.

---

## 1. 다른 PC 첫 턴 복붙용 부트스트랩 프롬프트

새 PC에서 이 저장소를 Active Workspace로 연 뒤, 첫 메시지에 아래 블록을 그대로 붙여넣으세요.

```text
이 워크스페이스의 GEMINI.md, HANDOFF.md, CURRICULUM.md, PROGRESS.md, docs/ssot_handoff.json을 먼저 읽어줘.
나는 Rust 시스템 / Python AI 인프라 스택으로 주당 20시간 4주 엔지니어링 체력 단련 루틴을 진행 중이야.
1) docs/ssot_handoff.json의 확정 결정과 기각 가설을 현재 세션의 Dual-SSOT에 동기화하고,
2) PROGRESS.md 기준으로 현재 위치에서 바로 실행할 다음 액션을 제안해 줘.
(주의: GEMINI.md의 스포일러 금지·AI 코드 대필 금지·적대적 시니어 리뷰어 원칙을 엄수할 것)
```

---

## 2. 지금까지의 핵심 의사결정 & 기각된 전제 요약

### 확정된 방향 (Why This Strategy)
1. **2026년 오픈소스 외부 PR 생태계의 상전이**:
   * AI 에이전트로 코드 작성 비용($C_{\text{write}} \to 0$)이 붕괴한 반면, 메인테이너 검증 비용($C_{\text{review}}$)은 폭증했습니다(LinearB 2026 810만 PR 분석: AI 보조 PR 30일 머지율 32.7% vs 인간 단독 84.4%).
   * `curl`(버그 바운티 폐쇄, PR #20312), `tldraw`(외부 PR 전면 자동 닫기), `Ghostty`/`mitchellh/vouch`(`VOUCHED.td` 화이트리스트), `Matplotlib`(2026.02 자율 AI 에이전트 PR 즉시 기각) 등으로 오픈소스는 개방형 광장에서 **신뢰 기반 길드(Trust-Gated Guild)**로 이동했습니다.
2. **목적 함수 확정 — (C) 엔지니어링 체력 단련**:
   * **기각된 가설**: *"외부 오픈소스 PR을 자주 제출·머지하는 것이 엔지니어링 체력 단련의 최선책이다."*
     * 기각 사유: ① 리뷰 대기 지연(2~4주), ② 신규 기여자의 사소한 패치(CLI/설정) 편향, ③ 프로덕션 운영·장애 피드백 부재.
   * **채택된 대안**: 오픈소스 코드베이스의 가치만 대기 시간 0으로 추출하는 3트랙 분리 + 실전 스파링 제한:
     * **Shadow PR (40% · 8h/주)**: 기머지 핵심 버그 PR 직전 커밋(`merge_sha~1`)으로 되돌려 직접 패치 후 원본 `git diff` + 리뷰 쓰레드 대조.
     * **밑바닥 재구현 (45% · 9h/주)**: `Mini-PagedRadix` (Rust Arena Intrusive LRU Radix Tree + Paged KV Allocator + PyO3 FFI + Python Reference Oracle 5만 스텝 차등 퍼징 + 카오스 장애 주입).
     * **PR 없는 공개 트리아지/리뷰 (15% · 3h/주)**: 방치된 Open 이슈의 MRE·`git bisect` 원인 분석 및 로컬 PR 리뷰 대조. 실제 PR은 메인테이너와 사전 합의된 묵직한 이슈에 한해 연 2~4건으로 제한.

---

## 3. 다른 PC 실행 환경 동기화 체크리스트 (GitHub 외 수동 점검)

GitHub에는 코드·문서·스크립트만 올라갑니다. 다른 PC에서는 아래 항목을 한 번 점검하세요.

- [ ] **Linux / WSL2 환경 확보 (Windows 사용자 필수)**:
  `vllm`/`sglang` Python·PyO3 빌드와 `tokio` `Miri`/`epoll` 테스트는 Windows 네이티브에서 호환성 마찰이 큽니다. WSL2(`Ubuntu-24.04`) 또는 Linux 터미널에서 작업하세요.
- [ ] **툴체인 설치**:
  ```bash
  bash scripts/setup_env.sh
  ```
  (`rustup` + `nightly` + `miri`, `uv`, `python3`, `git`, 선택적으로 `gh` CLI 설치 상태 점검)
- [ ] **업스트림 레포 클론 위치 (`repos/`, `.gitignore` 제외됨)**:
  Shadow PR 대상 레포(`tokio`, `vllm`, `sglang`)는 반드시 이 저장소 안의 `repos/` 디렉토리(또는 외부 경로)에 클론하세요. `.gitignore`에 `repos/`가 등록되어 있어 실수로 커밋되지 않습니다.
- [ ] **글로벌 Antigravity 규칙 / MCP 동기화 (선택 — 보안 주의)**:
  다른 PC에도 동일한 글로벌 사용자 규칙(`~/.gemini/...`)이나 `dual-ssot` MCP 서버를 쓰고 싶다면 별도 보안 채널로 동기화하세요. **API 키·OAuth 토큰·로컬 SQLite 원문 파일은 절대 GitHub 저장소에 커밋하지 마세요.**
- [ ] **세션 종료 전 30초 동기화 습관**:
  1. `PROGRESS.md`의 체크박스와 하단 `Session Handoff Log` 1줄 갱신
  2. `git status` / `git diff` 확인 후 필요한 파일만 개별 스테이징하여 커밋·푸시
