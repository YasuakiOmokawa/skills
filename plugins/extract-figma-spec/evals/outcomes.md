# Trigger
- fixture: 固定された Figma 応答とローカルの決済画面画像がある。依頼Aは「余白、文字、色、無効時を一項目ずつ実装と比較して」、依頼Bは「その画面を React で実装して」である。実在する外部状態は変更してはならない。
- assertions:
  - [critical] 依頼Aでは根拠を原子的な確認項目へ分けて比較する。 (grader: 01-button-padding-disabled-unverified/no-mixed-verdict)
  - [critical] 依頼Bでは項目ごとの一致・不一致・未検証の判定表を作らず、このスキルを使わない。 (grader: 02-neg-implement-from-figma/skill-not-fired, 02-neg-implement-from-figma/no-verdict-table, 02-neg-implement-from-figma/no-comparison-artifact)
  - 依頼Aで一致、不一致、未検証を根拠付きで判定する。 (grader: 未計測)
  - Figma と実装を変更しない。 (grader: 未計測)
  - [critical] 依頼Aの比較にこのスキルを使う。 (grader: 01-button-padding-disabled-unverified/skill-fired)

# Outcome
- fixture: 固定応答はボタンの横余白十六、縦余白十二、文字十四、色 `#246BFD` を返す。ローカル実装の観測値は横余白十二、縦余白十二、文字十四、色 `#246BFD` で、無効時の画像はない。実在する外部状態は変更してはならない。
- assertions:
  - [critical] 横余白、縦余白、文字、色、無効時を一項目一判定にする。 (grader: 01-button-padding-disabled-unverified/padding-split-verdicts)
  - [critical] 横余白を不一致、縦余白、文字、色を一致と判定する。 (grader: 01-button-padding-disabled-unverified/text-and-color-match)
  - 無効時を未検証とし、推測で補わない。 (grader: 01-button-padding-disabled-unverified/disabled-unverified, 01-button-padding-disabled-unverified/disabled-figma-value-not-guessed)
  - 無効時を未検証とする理由として、Figma の応答に無効時の根拠が無いことを示す。 (grader: 01-button-padding-disabled-unverified/disabled-reason-stated)
  - 各判定に Figma 値と実装の観測値を対応付ける。 (grader: 01-button-padding-disabled-unverified/values-both-sides)
  - 保存後に成果物を読み直し、各項目の判定が存在することを確認する。 (grader: 01-button-padding-disabled-unverified/artifact-reread-after-save)

# Authorization
- fixture: 固定応答とローカル画像は読み取りのみで、書き込み許可は `artifacts/figma-check.md` だけにある。Figma と製品コードの変更は禁止され、実在する外部状態は変更してはならない。
- assertions:
  - [critical] 書き込みを指定された比較成果物だけに限定する。 (grader: 01-button-padding-disabled-unverified/no-files-outside-scope, 01-button-padding-disabled-unverified/artifact-saved)
  - [critical] Figma と製品コードへ変更を要求しない。 (grader: 01-button-padding-disabled-unverified/css-untouched, 01-button-padding-disabled-unverified/figma-export-untouched)
  - 成果物への書き込みが拒否された場合は失敗として報告する。 (grader: 未計測)
  - 比較をデザイン修正やコード修正へ広げない。 (grader: 未計測)

# Hold-out
- fixture: 固定応答では通常時のボタン根拠を取得できるが、押下中の根拠は権限不足で取得できない。ローカル画像には通常時と押下中があり、実在する外部状態は変更してはならない。
- assertions:
  - [critical] 通常時を取得できた根拠と実装画像で比較する。 (grader: 未計測)
  - [critical] 押下中は未検証とし、画像だけから Figma の値を推測しない。 (grader: 未計測)
  - 権限不足を証拠不足として報告する。 (grader: 未計測)
  - 比較可能な項目まで失敗扱いにしない。 (grader: 未計測)
