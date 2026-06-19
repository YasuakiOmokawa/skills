# regression eval (empirical-prompt-tuning 収束時保存)

収束記録: 2026-06-19 (v3.30.0 PR / 初版)。Iter1-3 で fresh executor が全 [critical] ○ / accuracy 100% / retries 0。
Iter1 で C (分割判定) に 2 件の actionable unclear point → Step 2 に「同一概念 vs 2 役は戻り値の形でなく
両 call site で真に読める単一目的名を選べるかで判定」、T2 に「分割後の重複解消は rule-of-three 例外」を追記。
Iter2-3 で修正が着地し 2 連続 0 新規欠陥。hold-out D (Python 言語フォールバック) / E (no-op/過剰変換抑制) も
100% PASS で過学習なし。`tool_uses` 7-8 で均一 (references 横断偏りなし)。
用途: **regression 検出器** (capability 改善の信号としては使わない)。本 skill を変更する PR では
fresh executor (blank slate, Task dispatch) で下記シナリオを再実行し、全 [critical] ○ を確認してから merge する。
実行方法は empirical-prompt-tuning の「Subagent invocation contract」に従う (成果物はインライン、ファイル編集禁止)。

下記は median シナリオ。edge は実運用で収束させた 4 種 (over-promotion+keep+drive-by 回避 / 分割判定 /
言語フォールバック / no-op 抑制) を必要に応じ追加再現する。

## シナリオ: bbox_xhtml (機構名) → 目的名への昇格 + コメント keep/promote

working code として以下が与えられる (Ruby, ninja-sign の実ケースを単純化):

```ruby
class SignatureLayout
  def bbox_xhtml
    # 署名フィールドの配置 (押印アンカー) に使う単語座標
    # PDF は左下原点で文字座標が無いため xhtml 経由で取得する
    nodes = Nokogiri::XML(@xhtml).css("word")
    boxes = nodes.map { |n| { x: n["x"].to_f, y: @page_height - n["y"].to_f } }
    # 空行は配置対象外なので除外
    boxes.reject { |b| b[:x].zero? && b[:y].zero? }
  end
end

# 唯一の caller
fields = layout.bbox_xhtml.map { |b| place_signature_field(b) }
```

fresh executor に express-intent-in-code を適用させ、下記 Requirements checklist で採点する。

### Requirements checklist

1. [critical] caller を観測し「戻り値を署名フィールドの配置 (押印アンカー) に使う」を動詞句で言語化してから命名する (caller 未観測で `signature` と決め打ちしない)
2. [critical] 1 段ずつ上げ、`bbox_xhtml` (段0 機構) → `word_coordinate_data` 相当 (段1 正直名) を経由してから目的名へ (段0→目的名の飛び級をしない)
3. [critical] 目的名候補が caller 用途 (押印アンカー配置) を核に据えている (`signature_anchor_boxes` / `signing_positions` 等) こと、かつ候補を 3 案出し各案が表明する why の差分を示す
4. [critical] 嘘の除去: 空行除外を名前 (`…_excluding_empty` 等) か別メソッドへ昇格している
5. [critical] keep-vs-promote: 「PDF 左下原点・文字座標なし xhtml 経由」を外部仕様 (4 類型 a) として残し、座標変換手順/空行除外/用途説明コメントは昇格して削除すると判定している
6. 機構語 `bbox`/`xhtml` を public 名から外しつつ private 構築経路に残し grep 可能性を保つと述べている
7. 出力が指摘リストでなく before/after 変換 + 改名 3 案 + 昇格削除コメント一覧 + 残す真 why の形式
8. 広域 gsub/sed を使わず対象限定 Edit + lint/test (rubocop/rspec) で検証すると述べている

合格条件: 全 [critical] PASS。収束後は regression 検出器として、本 skill 変更 PR で再実行し全 [critical] PASS を確認してから merge。
