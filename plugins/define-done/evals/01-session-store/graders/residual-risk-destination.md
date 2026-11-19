---
type: llm
focus: {source: file, path: plans/session-store.md}
---
`## MECE Review` 節だけを見る。外部ストアのクライアントの導入で `src/session/__tests__/containment.test.ts` の許可一覧が壊れるリスクについて、リスクとそれを守る先を対にした表の行があり、守る先が受け入れ基準の AC-ID、実装が直すか足すテスト、既存のテスト、規約、未検証のどれかとして書かれていれば pass。このリスクが `## Ground Review` 節にだけあり、`## MECE Review` 節にリスクと守る先を対にした行が無ければ fail。
