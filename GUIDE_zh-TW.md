# White Cat Visualizer 壓縮版使用手冊

這份手冊是給你本人看的，不是 Codex 的日常 context。根目錄 `AGENTS.md` 已經明確要求 Codex 除非你特別指定，否則不要讀這份文件。

這麼做的目的，是讓使用說明可以很完整，但不會讓每一次 coding 任務都多吃幾千 token。

---

## 1. 這個 starter 解決什麼

它把專案拆成三層：

1. **固定規則**：`AGENTS.md`
2. **特定任務流程**：`.agents/skills/`
3. **真正會執行與失敗的 harness**：`tests/`、`scripts/`

目前已經完成的產品核心只有：

- deterministic synthetic PCM
- immutable `AudioFrame`
- FFT 與 logarithmic bands
- attack/release smoothing
- immutable normalized `VisualizerFrame`
- unit tests
- core smoke test
- console visual demo
- analysis benchmark

目前刻意沒有完成：

- PySide6/QML 主視窗
- 貓咪 visualizer
- worker thread
- Windows WASAPI loopback
- packaging

這些由六個階段逐步加入。

---

## 2. 為什麼這版比較省 token

Codex 每次只需要讀：

- `AGENTS.md`
- 當前的 `prompts/0N-....md`
- 該 prompt 明確指定的一到兩份規格
- 實際要修改的程式碼

不需要每次把產品介紹、音訊教學、UI 規格、所有階段與完整手冊重新貼進 chat。

你下給 Codex 的訊息通常只有一行：

```text
Use $implement-slice. Implement prompts/01-shell.md exactly. Read only the files it references. Stop after this phase.
```

實際需求與 acceptance criteria 已經存在 repository 裡。Codex 直接讀檔案即可。

---

## 3. 目錄用途

```text
AGENTS.md
```

每次任務都成立的硬規則，包括架構方向、可讀性、效能、scope 與完成條件。這份文件盡量不要經常改。

```text
ARCHITECTURE.md
```

資料流、package layout、state ownership 與 threading model。只有當架構契約真的改變時才修改。

```text
docs/AUDIO.md
```

PCM、FFT、bands、smoothing、threading 與 Windows loopback 的專案規格。調整音訊契約或預設參數時修改。

```text
docs/UI.md
```

白色配色、2:8 layout、long cat、ball cat 與 QML 限制。改產品視覺或動畫契約時修改。

```text
.agents/skills/implement-slice/SKILL.md
```

告訴 Codex 如何只完成一個小階段、測試、驗證並停下。

```text
.agents/skills/audio-pipeline/SKILL.md
```

只有音訊、FFT、runtime、WASAPI 工作才使用。它補足你目前較不熟悉的 audio engineering 約束。

```text
.agents/skills/verify-change/SKILL.md
```

用另一個 thread 做只讀 review，不讓寫作者直接替自己背書。

```text
prompts/
```

六個開發階段的 scope、allowed area、non-goals 與 acceptance criteria。

```text
scripts/verify.py
```

唯一完整驗收入口。

```text
scripts/smoke_test.py
```

快速確認所有 synthetic mode 都能產生合法 frame。

```text
scripts/visual_demo.py
```

不用 GUI 也能在 terminal 看 deterministic spectrum 是否有反應。

```text
scripts/benchmark_analysis.py
```

測量 spectrum analysis 的 median、p95 與相對 frame budget。它不是一個容易受機器差異影響的硬門檻，而是 regression evidence。

---

## 4. 第一次安裝

在 Windows PowerShell 中進入 repository：

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev,gui]"
python scripts/verify.py
```

你也可以直接執行：

```powershell
.\scripts\bootstrap.ps1
```

確認 core demo：

```powershell
python scripts/visual_demo.py --mode bass-pulse
python scripts/visual_demo.py --mode frequency-sweep
```

確認 benchmark：

```powershell
python scripts/benchmark_analysis.py
```

Phase 5 才安裝 Windows loopback dependency：

```powershell
python -m pip install -e ".[dev,gui,windows-audio]"
```

不要一開始就接真實音訊。synthetic source 是後面所有 UI、threading 和 backend 的 reference harness。

---

## 5. 每個階段的固定工作循環

每個階段都使用新的 implementation thread：

1. 確認上一階段已 commit，工作區乾淨。
2. 開一個新的 Codex thread。
3. 下達該階段的一行 prompt。
4. Codex 應先給簡短 plan，再實作、測試、執行完整 verify。
5. 你自己進行該階段的 manual checks。
6. 另開一個新的 review thread，使用 `$verify-change`。
7. 有 material finding 時，回到 implementation thread 只修 findings。
8. 再跑 review。
9. 全部通過後 commit。
10. 才進入下一階段。

不要在同一個巨大 thread 連續做六個階段。新的 thread 可以避免前一階段的大量對話繼續占用 context，也讓 review 角度較乾淨。

---

## 6. Phase 0：你自己先做的 baseline

這不是 coding phase，不需要讓 Codex 修改檔案。

執行：

```powershell
python scripts/verify.py
python scripts/visual_demo.py --mode bass-pulse --frames 40
python scripts/benchmark_analysis.py
```

再問 Codex：

```text
Read AGENTS.md, ARCHITECTURE.md, prompts/README.md, and the current source tree. Summarize the current verified data flow, the three available skills, and the six phase boundaries. Do not modify files.
```

你應該確認它理解：

- analysis 不依賴 Qt
- QML 只吃 normalized values
- 真實音訊是 Phase 5
- per-app capture 不在 MVP
- 一次只能做一個 phase

不需要讓它寫額外 audit 文件。

---

## 7. Phase 1：Static shell + GUI harness

### 目標

建立最小 PySide6/QML app、白色 2:8 layout、static controller，以及 offscreen GUI smoke test。

### 開始前讀哪些文件

Codex 會依 prompt 讀：

- `AGENTS.md`
- `ARCHITECTURE.md`
- `docs/UI.md`
- `prompts/01-shell.md`

### 發給 Codex

```text
Use $implement-slice. Implement prompts/01-shell.md exactly. Read only the files it references. Stop after this phase.
```

### 允許主要修改

- `pyproject.toml`
- `src/white_cat_visualizer/app.py`
- `src/white_cat_visualizer/presentation/`
- `src/white_cat_visualizer/ui/qml/`
- GUI 相關 tests
- `scripts/gui_smoke_test.py`
- 必要的 package exports

### 不應修改

- FFT algorithm
- synthetic source behavior
- audio runtime
- Windows backend
- `AGENTS.md`
- `ARCHITECTURE.md`
- `docs/*.md`
- 其他 phase prompts

### 你親自檢查

- 視窗是否真的約 2:8。
- 窄視窗 controls 是否重疊。
- 白色貓之後放上去是否會與 canvas 有足夠對比。
- QML console 是否有 binding/unqualified access 錯誤。
- 關閉視窗是否能乾淨退出。

### Review prompt

```text
Use $verify-change. Review Phase 1 against prompts/01-shell.md. Do not modify files.
```

### 建議 commit

```text
feat(ui): add minimal QML shell and GUI smoke harness
```

---

## 8. Phase 2：Synthetic pipeline + ordinary bars

### 目標

先用普通 bar 證明完整資料流正確。這是 debug reference，不要直接跳過去畫貓。

### 發給 Codex

```text
Use $implement-slice and $audio-pipeline. Implement prompts/02-bars.md exactly. Read only the files it references. Stop after this phase.
```

### 允許主要修改

- `app.py`
- `presentation/`
- `ui/qml/`
- controller/GUI tests
- smoke/demo scripts
- 現有 audio/analysis，僅限 integration 發現真實 contract 缺口時

### 不應修改

- worker thread
- Windows backend
- cat component
- generic source registry/plugin system

### 這階段暫時允許什麼

可以用 QTimer 在 UI thread 拉 synthetic frame 與執行 analyzer。這是明確的 prototype，只允許存在到 Phase 4。

原因是先把資料流、controls 和 QML 更新驗證清楚，再引入 threading，問題比較容易定位。

### 你親自檢查

```powershell
python scripts/visual_demo.py --mode silence
python scripts/visual_demo.py --mode bass-pulse
python scripts/visual_demo.py --mode frequency-sweep
python scripts/benchmark_analysis.py
```

在 GUI 中確認：

- silence 幾乎靜止。
- bass pulse 主要讓低頻 bars 有節奏。
- sweep 能由低頻往高頻移動。
- start/stop 不會殘留舊高度。
- 換 synthetic mode 時行為可預期。
- resize 不會重建一堆 QML objects。

### Review prompt

```text
Use $verify-change. Review Phase 2 against prompts/02-bars.md. Pay special attention to duplicate state, per-frame model replacement, and analyzer integration. Do not modify files.
```

### 建議 commit

```text
feat(visualizer): connect synthetic spectrum to reference bars
```

---

## 9. Phase 3：Long cat + bouncing cat

### 目標

保留普通 bars 作 debug mode，再加入兩種正式貓咪 visualizer。

### 發給 Codex

```text
Use $implement-slice. Implement prompts/03-cats.md exactly. Read only the files it references. Stop after this phase.
```

### 允許主要修改

- visualizer mode property/signal
- `ui/qml/components/`
- `ui/qml/visualizers/`
- GUI tests
- visual demo/smoke script

### 不應修改

- analyzer math
- audio source contract
- runtime/threading
- WASAPI

### 你親自檢查

Long Cat Bars：

- 身體高度、頭部位置、耳朵、squash 是否是分開反應。
- 是否像貓在跳，而非長條貼耳朵。
- 最低高度時頭與耳朵不會擠爛。
- 高 peak 時不超出 canvas。

Bouncing Cat Heads：

- silence 時共用 baseline。
- 不會左右亂飄。
- peak squash 不會造成閃爍。
- 各頻段仍然看得出差異。

三個視窗尺寸都檢查：

- narrow
- default
- wide

### Review prompt

```text
Use $verify-change. Review Phase 3 against prompts/03-cats.md. Focus on QML per-frame allocations, JavaScript work, binding loops, component reuse, and resize behavior. Do not modify files.
```

### 建議 commit

```text
feat(ui): add long-cat and bouncing-cat visualizers
```

---

## 10. Phase 4：Bounded runtime/threading

### 目標

把 source reading 與 FFT 移出 UI thread，但只用最簡單且可理解的 worker + single-slot handoff。

### 發給 Codex

```text
Use $implement-slice and $audio-pipeline. Implement prompts/04-runtime.md exactly. Read only the files it references. Stop after this phase.
```

### 允許主要修改

- `runtime/latest_frame.py`
- `runtime/analysis_worker.py`
- source lifecycle contract 的必要小修改
- controller
- composition root
- runtime tests

### 禁止出現

- unbounded `queue.Queue()`
- 通用 job scheduler
- asyncio framework
- event bus
- callback 直接呼叫 QML
- worker 無法可靠停止

### 你應該能看懂的核心邏輯

理想結構只有：

1. source 產生最新 PCM。
2. single-slot 保存或覆蓋 pending frame。
3. worker 取最新 frame 做 analyze。
4. single-slot 保存或覆蓋最新 visualizer frame。
5. controller 在 UI thread 讀取並 emit narrow signal。

不要接受複雜的多層 futures、task graph 或 generic executor abstraction。

### 你親自檢查

- 快速連按 start/stop 不會崩潰。
- 關閉 app 不會卡住。
- 高速 synthetic input 時 UI 仍能拖曳視窗。
- frame 跟不上時是 drop stale frame，不是延遲越堆越長。
- worker exception 能變成看得懂的 error state。

### Review prompt

```text
Use $verify-change. Review Phase 4 against prompts/04-runtime.md. Focus on fixed capacity, lifecycle races, shutdown, exception propagation, and whether the logic is more complex than necessary. Do not modify files.
```

### 建議 commit

```text
feat(runtime): add bounded background spectrum analysis
```

---

## 11. Phase 5：Windows WASAPI loopback

### 目標

讓使用者選擇 Windows 輸出 endpoint，例如喇叭或耳機，擷取該裝置正在播放的 system mix。

這不是指定某個 app 的音訊，也不是 Windows Volume Mixer 的逐程式 capture。

### 安裝 dependency

```powershell
python -m pip install -e ".[dev,gui,windows-audio]"
```

### 發給 Codex

```text
Use $implement-slice and $audio-pipeline. Implement prompts/05-windows-audio.md exactly. Read only the files it references. Stop after this phase.
```

### 允許主要修改

- `audio/windows_loopback.py`
- source model/controller
- composition root
- source/error UI 的必要部分
- tests using fake/mock backend
- `pyproject.toml`

### 不應修改

- cat animation design
- FFT 演算法，除非真實格式暴露經測試的 contract 問題
- per-app capture
- microphone
- recording
- audio routing/mixing

### 你親自檢查

在 Windows 上：

1. 選擇目前播放音樂的 output endpoint。
2. 啟動 visualizer。
3. 暫停音樂，確認 visualizer 釋放回低值。
4. 恢復播放。
5. 切換另一個 endpoint。
6. 停止再啟動。
7. 在可控情況下拔除或停用裝置，確認 UI 顯示錯誤而非凍結。
8. 切回 synthetic source，確認仍正常。

### Review prompt

```text
Use $verify-change. Review Phase 5 against prompts/05-windows-audio.md. Focus on callback safety, sample conversion, device IDs, disconnect handling, unsupported-platform imports, and repeated lifecycle operations. Do not modify files.
```

### 建議 commit

```text
feat(audio): add Windows output-device loopback capture
```

---

## 12. Phase 6：Release hardening，可選

Phase 5 完成後已經是可用 MVP。只有你確定要發佈，才進 Phase 6。

### 發給 Codex

```text
Use $implement-slice. Implement prompts/06-release.md exactly. Read only the files it references. Stop after this phase.
```

### 可以做

- 設定保存
- keyboard/focus/accessibility
- debug overlay，預設關閉
- measured performance fixes
- icon/metadata/build command
- README 與 known limitations

### 不可以趁機做

- 新 visualizer
- 多主題
- cloud sync
- 錄音
- per-app capture
- plugin marketplace
- 大重構

### Review prompt

```text
Use $verify-change. Review Phase 6 against prompts/06-release.md. Focus on regressions, default-disabled diagnostics, settings failure behavior, clean-build reproducibility, and unrequested scope. Do not modify files.
```

### 建議 commit

```text
chore(release): harden settings, accessibility, and Windows build
```

---

## 13. 什麼時候修改哪份規格

### 只改畫面或動畫需求

先修改：

```text
docs/UI.md
```

若 acceptance criteria 也改變，再修改當前尚未開始的 phase prompt。

例子：你決定取消尾巴，不需要改 `AGENTS.md` 或 `ARCHITECTURE.md`，只改 `docs/UI.md`。

### 改 FFT、band 數、頻率範圍、smoothing

先修改：

```text
docs/AUDIO.md
```

然後要求 Codex：

```text
Use $audio-pipeline. Review the proposed contract change in docs/AUDIO.md against the current tests and architecture. Do not modify code. Report compatibility, test changes, and performance risks.
```

確認後才另開 implementation task。

### 改 layer、state ownership 或 threading 模型

修改：

```text
ARCHITECTURE.md
```

這類變更風險最高，應先 review 設計，不要直接叫 Codex 重寫。

### 改 Codex 永久行為

才修改：

```text
AGENTS.md
```

不要把單一功能需求放進 `AGENTS.md`。它只放所有任務都成立的規則。

### 改某個階段 scope

修改對應的：

```text
prompts/0N-....md
```

已經完成並 commit 的 phase prompt 通常不要回頭改，除非你在修正專案歷史規格。

---

## 14. 如何要求 Codex 修 review finding

Reviewer 只報問題，不直接修改。你把 findings 帶回 implementation thread：

```text
Address only the material findings from the Phase N review below. Preserve the phase scope and current public contracts. Add regression tests where applicable, run focused tests and python scripts/verify.py, then stop.

<貼上 findings>
```

修完後再開 reviewer thread，或在原 reviewer thread 要求重新檢查最新 diff。

不要說：

```text
fix everything and improve the code
```

這會讓 scope 再度擴張。

---

## 15. 如何判斷 Codex 寫得太難懂

看到以下特徵應該退回：

- 一個簡單 source selector 出現 registry、factory factory、service container。
- worker 用多層 future/callback/event bus，卻只有一個 producer 和 consumer。
- QML 每 frame 建新 object 或 map 整個 array。
- 同一個 state 在 Python 與 QML 各保存一份。
- 為「未來可能多 backend」先建立大量 abstract base classes。
- 一個 expression 同時做 validation、conversion、normalization 與 state mutation。
- exception 被廣泛 catch 後只印 log。
- 為了幾微秒換成難以驗證的技巧，卻沒有 benchmark。

你可以直接下：

```text
Simplify this implementation without changing behavior. Prefer one explicit code path, named intermediate values, and the smallest real boundary. Remove speculative abstractions. Preserve or improve the measured benchmark and run all verification.
```

但應先要求 reviewer 指出具體檔案與理由，不要無差別「clean up」。

---

## 16. 可讀性與效能如何平衡

這個 starter 的規則不是「可讀性永遠比效能重要」，而是：

1. 先寫直接、正確、可測的版本。
2. 用 benchmark 找真正 hot path。
3. DSP 優先使用清楚的 NumPy vectorization、cache 與固定 buffer。
4. QML 優先避免 allocation、model replacement 與大 JavaScript loop。
5. 只有測量證明需要，才接受更複雜實作。
6. 複雜版必須保留測試、benchmark 與簡短 why comment。

這能避免兩個極端：

- 為了「clean」把 per-frame code 拆成大量動態物件，導致慢。
- 為了想像中的速度寫出你自己無法維護的 micro-optimization。

---

## 17. 驗證命令

開發中快速跑 focused tests：

```powershell
python -m pytest tests/audio tests/analysis
```

完整驗證：

```powershell
python scripts/verify.py
```

分析 benchmark：

```powershell
python scripts/benchmark_analysis.py
```

console demo：

```powershell
python scripts/visual_demo.py --mode silence
python scripts/visual_demo.py --mode bass-pulse
python scripts/visual_demo.py --mode frequency-sweep
```

QML 建立後，`verify.py` 會在存在時執行 GUI smoke script；本機找不到 `qmllint` 時顯示警告，CI 模式則視為失敗。

---

## 18. Git 建議

每一 phase 一個 branch 或至少一個獨立 commit：

```text
feature/phase-1-shell
feature/phase-2-bars
feature/phase-3-cats
feature/phase-4-runtime
feature/phase-5-wasapi
release/phase-6
```

每階段開始前：

```powershell
git status --short
```

應該是乾淨的。

每階段結束後：

```powershell
git diff --check
git status --short
python scripts/verify.py
```

再 commit。這樣若某階段的 Codex 實作失控，可以整段回退，而不是在巨大混合 diff 裡找問題。

---

## 19. 最終 MVP 定義

Phase 5 完成且以下項目成立，就算 MVP：

- 可選 synthetic 或 Windows output endpoint。
- 可 start/stop。
- 有 ordinary bars、long cat bars、bouncing cat heads。
- silence、bass pulse、sweep 行為可信。
- UI resize 正常。
- 音訊與分析不阻塞 UI。
- handoff 固定容量。
- device error 可見且可恢復。
- app 能乾淨關閉。
- 完整 verify 通過。
- 你本人能讀懂 source、analyzer、worker、controller 四條主要路徑。

不需要 per-app capture、錄音、cloud、plugin、主題系統或複雜 DSP 才叫完成。

---

## 20. 你每階段真正需要記住的只有三句

實作：

```text
Use $implement-slice [...]. Implement prompts/0N-....md exactly. Read only the files it references. Stop after this phase.
```

驗收：

```text
Use $verify-change. Review Phase N against prompts/0N-....md. Do not modify files.
```

機械式 gate：

```powershell
python scripts/verify.py
```

其餘細節都已經放在 repository 裡，不需要靠你每次重新組一大段 prompt。
