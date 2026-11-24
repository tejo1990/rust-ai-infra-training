# Rust Systems + Python AI Infra — 4-Week Deliberate Practice Hub

2026년 AI 코딩 시대에 맞춰 **드라이브바이 오픈소스 PR 대신 고밀도 엔지니어링 체력(독해·디버깅·설계·적대적 검증)**을 단련하기 위한 4주(주당 20시간) 훈련 워크스페이스입니다.

## Repository Layout

| Path | Role |
| :--- | :--- |
| [`HANDOFF.md`](HANDOFF.md) | **다른 PC에서 대화 복원용 부트스트랩 프롬프트** · 의사결정 요약 · 환경 체크리스트 |
| [`CURRICULUM.md`](CURRICULUM.md) | 3대 직교 레포 · GitHub 검색 필터 · `Mini-PagedRadix` 명세 · 4주 루틴 |
| [`PROGRESS.md`](PROGRESS.md) | 주차별 진행률 · 완료한 Shadow PR 기록 · PC 간 핸드오프 로그 |
| [`GEMINI.md`](GEMINI.md) | 이 워크스페이스 전용 에이전트 규칙 (구현 스포일러 금지 · 적대적 시니어 리뷰어 모드) |
| [`docs/ssot_handoff.json`](docs/ssot_handoff.json) | `Dual-SSOT` 확정 결정 3건 + 기각 가설(Negative Knowledge) 1건 스냅샷 |
| [`notes/postmortem_template.md`](notes/postmortem_template.md) | Shadow PR 완료 후 "업스트림 반려 사유 3줄" 오답노트 템플릿 |
| [`scripts/pick_shadow_pr.py`](scripts/pick_shadow_pr.py) | `gh` CLI 없이도 동작하는 스포일러 차단 Shadow PR 후보 추출기 (Python 표준 라이브러리) |
| [`scripts/setup_env.sh`](scripts/setup_env.sh) | WSL2 Ubuntu / Linux용 툴체인(`rustup` + `miri` + `uv` + `gh`) 1줄 점검·설치 스크립트 |

## Quickstart on Another PC

1. 저장소 클론:
   ```bash
   git clone https://github.com/tejo1990/rust-ai-infra-training.git
   cd rust-ai-infra-training
   ```
2. Antigravity에서 이 디렉토리를 **Active Workspace**로 엽니다 (`GEMINI.md` 자동 로드).
3. 새 채팅창 첫 턴에 [`HANDOFF.md`](HANDOFF.md) 상단의 **복붙용 부트스트랩 프롬프트**를 붙여넣어 즉시 이어서 진행합니다.
4. 작업 종료 시 `PROGRESS.md`와 `notes/`를 업데이트한 뒤 GitHub에 커밋·푸시합니다.
