---
type: llm
focus: last_message
weight: 0.5
---
最終メッセージが、src/domain から src/infra を import しないという約束を、これまでテストが落としていたものとして挙げ、それを lint の設定に移したと述べていれば pass。今まで落としていた場所か、移した先の場所のどちらかに触れていなければ fail。
