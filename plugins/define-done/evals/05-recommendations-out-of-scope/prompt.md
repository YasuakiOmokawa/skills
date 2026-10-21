---
max_turns: 60
timeout_seconds: 1800
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p plans
cat > plans/confirm-on-post.md <<'EOF'
# 確認済みチェックを POST にも通す 設計

## 1. 目的
受信者が承認画面と同意画面を開くとき (GET) は、電話番号の確認が済んでいるかを確かめている。しかし POST を直接送ると、この確認を通らずに承認・同意できてしまう。承認と同意の POST でも入口と同じ確認を通し、未確認なら処理しない。

## 2. 仕様
- S-1: 電話番号の確認が済んでいない受信者が承認の POST (`POST /approvals`) を送ると、303 で確認画面 (`/confirmations/new`) へ戻され、承認の状態は変わらない。
- S-2: 電話番号の確認が済んでいない受信者が同意の POST (`POST /agreements`) を送ると、303 で確認画面へ戻され、同意の状態は変わらない。
- S-3: 確認が済んでいる受信者の承認と同意は、これまでどおり成功する。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| app/controllers/approvals_controller.rb | POST 時に確認済みかを確かめる |
| app/controllers/agreements_controller.rb | POST 時に確認済みかを確かめる |

## 4. セキュリティレビューからの推奨
- P-1: 保存境界 (モデルの保存時) でも確認済みかを確かめ、フェイルクローズにする。
- P-2: 未確認のまま送られた POST を監査ログへ記録する。
- P-3: 確認コードの入力にレート制限を掛ける。

## 5. 別チケット
- 確認コードの確定時に、他人の確認リクエストに対しても SMS を送れてしまう認可漏れがある。別チケットで直す。
EOF
```

plans/confirm-on-post.md の設計を /define-done して、設計を確定する。実装は指示まで禁止。
