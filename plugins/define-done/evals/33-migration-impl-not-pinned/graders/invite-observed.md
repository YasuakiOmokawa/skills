---
type: llm
focus: {source: file, path: repo/plans/invite.md}
---
repo/plans/invite.md の `## Acceptance Criteria` を評価する。token のある `/invite` の link を開くと「招待を受諾しています」が出ること、token の無い link を開くと「招待のリンクが正しくありません」が出ることを、それぞれ開いた結果の内容で観測する基準があれば pass。複数の基準に分かれていてもよい。どちらかが無いか、開いた結果ではなくどの実装が描くかで確かめているなら fail。
