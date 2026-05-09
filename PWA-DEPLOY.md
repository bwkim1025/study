# PWA 배포 & 설치 가이드

> Daily Briefings를 GitHub Pages에 올리고, 아이폰·안드로이드에 앱처럼 설치하는 방법.

## 0. 옛 study/ 폴더 삭제 (한 번만)

이전 구조에서 남은 `study/` 폴더 잔여물을 먼저 정리:

```powershell
cd C:\Users\USER\Documents\GitHub\study
Remove-Item -Recurse -Force study
```

## 1. GitHub에 push

```bash
cd C:\Users\USER\Documents\GitHub\study
git add -A
git commit -m "feat: study 단독 리포 분리 + PWA 설정"
git push origin main
```

## 2. GitHub Pages 활성화 (한 번만)

1. https://github.com/bwkim1025/study 접속
2. 우측 상단 **Settings** 클릭
3. 좌측 메뉴 **Pages** 선택
4. **Source** 항목에서:
   - **Branch:** `main` (또는 `master`)
   - **Folder:** `/ (root)`
5. **Save** 클릭
6. 1~2분 후 상단에 `Your site is live at https://bwkim1025.github.io/study/` 표시됨

브라우저로 그 URL을 한번 열어 정상 표시 확인.

## 3. 아이폰에 앱처럼 설치 (Safari)

1. **Safari**로 `https://bwkim1025.github.io/study/` 열기 (Chrome 아님)
2. 하단 공유 버튼 (네모+화살표) 탭
3. 스크롤 → **홈 화면에 추가**
4. 이름은 `Briefings`로 미리 채워져 있음 → **추가**
5. 홈 화면에 navy 색 아이콘이 깔림 → 탭하면 풀스크린으로 열림 (Safari UI 없음)

## 4. 안드로이드에 앱처럼 설치 (Chrome)

1. **Chrome**으로 `https://bwkim1025.github.io/study/` 열기
2. 우측 상단 ⋮ → **앱 설치** 또는 **홈 화면에 추가**
3. 자동으로 앱 드로어와 홈 화면에 모두 추가됨

설치 후에는 알림창에 "Briefings 설치됨"이 뜨고, 일반 앱처럼 다중 작업 화면에서도 별도 창으로 표시됨.

## 5. 업데이트 흐름

`git push` 한 번이면 끝:
- GitHub Actions 없이 GitHub Pages가 자동 빌드 (1~2분)
- 사용자 폰에서 앱 다시 열면 service worker가 백그라운드에서 새 HTML/MD를 받아옴
- 다음 실행에서 즉시 반영됨

오프라인에서도 마지막에 본 페이지가 캐시에서 열림 (network-first, fall back to cache).

## 6. 캐시 강제 갱신 (필요 시)

PWA가 옛날 버전을 계속 보여주면:
- iOS: 홈 화면 아이콘 길게 누르고 삭제 → Safari로 다시 추가
- Android: 설정 → 앱 → Briefings → 저장공간 → 캐시 삭제

또는 `sw.js`의 `CACHE_VERSION = 'daily-briefings-v5'`를 `v6`로 올리고 push하면 모든 사용자가 다음 방문 시 자동 갱신.

## 7. 아이콘이 회색 사각형으로 보일 때

캐시 문제일 가능성 큼. 아이폰은 **홈 화면에서 한 번 삭제 → Safari 캐시 비우기 → 다시 추가**로 해결.

## 8. 카테고리 폴더가 아직 없는 경우

현재 `study/`만 만들어져 있고 `financial/`, `international/`, `medical/`, `health/`는 아직 없음. 메인 화면에서 카드를 탭하면 GitHub Pages 404가 뜸.

스케줄드 태스크가 매일 18:00에 각 카테고리 디렉토리에 브리핑을 만들어 줄 예정. 첫 실행 후엔 정상 동작.

만약 미리 빈 카테고리 페이지가 필요하면 다음 회차에서 같이 만들어 드릴 수 있음.
