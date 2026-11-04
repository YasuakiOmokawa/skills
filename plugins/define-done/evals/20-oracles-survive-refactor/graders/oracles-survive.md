---
type: llm
focus: last_message
---
エージェントの最終報告を評価する。`sh tools/implement.sh` の後に、計画の Verification Plan の Oracle を AC ごとに観測した結果を報告していて、計画が名指しした関数、ファイル、試験が存在しない (実装の名前や置き場所が計画と違う) ことを理由に、落ちた、または観測できなかった Oracle が 1 件も無ければ pass。そうした Oracle が 1 件でもあれば fail。Oracle ごとの観測結果を報告していなければ fail。名前以外の理由 (sandbox で npm が起動できない、など) で観測できなかった Oracle は数えない。
