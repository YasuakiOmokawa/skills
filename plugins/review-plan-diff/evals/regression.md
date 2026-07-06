# regression eval

収束記録: 未実施（廃止されたオーケストレータからの移設時点では fresh executor による Iter1-3 再収束を行っていない。次回本 skill を変更する PR で下記シナリオを実行し、収束記録をこの節に追記すること）。

## シナリオ: QA-ID カバレッジマトリクスに計画されたテストが diff に無い (未実装の検出)

`plan-diff-reviewer` として、確定プランファイルの QA-ID カバレッジマトリクスに以下の行がある:

| QA-ID | 内容 | 割当PR | 実行コマンド |
|-------|------|--------|--------------|
| QA-E-01 | 権限が無いユーザーが更新APIを叩くと403を返す | PR1 | `bundle exec rspec spec/requests/x_spec.rb -e "QA-E-01"` |
| QA-E-02 | 正常系: 権限があるユーザーが更新に成功する | PR1 | `bundle exec rspec spec/requests/x_spec.rb -e "QA-E-02"` |

対象 diff (`git diff develop..HEAD`) は `spec/requests/x_spec.rb` に `it "QA-E-02"` のテストケースを追加しているが、`it "QA-E-01"` に相当するテストケースは diff 中のどこにも存在しない。プロダクションコード側は権限チェックの分岐を実装済み。

### Requirements checklist

1. [critical] QA-E-01 を「未実装」として Critical で検出する（QA-ID カバレッジマトリクスに記載の auto QA-ID が対応するテストを持たない、の判定基準に該当）
2. [critical] QA-E-01 の指摘に、diff 中に `it "QA-E-01"` に相当する記述が無いこと（grep 相当の確認結果）を diff 根拠として明示する。プロダクションコードの実装有無だけで判定せず、テストの不在を独立に指摘する
3. QA-E-02 は diff に対応するテストケースが存在するため、誤って未実装・乖離ありとして検出しない（実装済み項目の過検出をしない）
4. 総合判定を「Critical あり」とし、他の乖離 (計画外差異等) が無ければ乖離一覧に QA-E-01 の 1 行のみを含める
