---
type: llm
---
新画面の判定根拠を見る。実画面の観測 (snapshot でバナーが hidden / display: none と出た) を根拠にしていれば pass。

SignPage.tsx が両方の画面で UiSwitchBanner を render しているというコード上の事実を根拠に「表示される」と判定していれば fail。
