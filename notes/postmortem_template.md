# Shadow PR Postmortem Template

* **Repo / PR**: `<owner/repo>#<pr_number>`
* **Parent Commit Checked Out**: `<merge_sha>~1`
* **Date / Time Spent**: `YYYY-MM-DD` / `___ min` (90분 타임박스 준수 여부: Y/N, 테스트 diff 선공개 여부: Y/N)
* **Issue Symptom (1~2줄)**:

---

## 1. 내 가설과 로컬 패치 접근
* **추정한 근본 원인**:
* **작성한 실패 재현 테스트**:
* **내가 택한 수정 방향과 트레이드오프**:

## 2. 실제 업스트림 `git diff` 및 리뷰 쓰레드 대조
* **업스트림이 택한 해결책**:
* **리뷰 쓰레드에서 기각된 대안 / 지적된 엣지케이스**:

## 3. 내 패치가 업스트림에서 반려됐을 이유 3줄 (필수 — 미작성 시 완료 불인정)
1.
2.
3.

## 4. 추출한 재사용 불변식 / 시스템 원칙 (1~2줄)
*
