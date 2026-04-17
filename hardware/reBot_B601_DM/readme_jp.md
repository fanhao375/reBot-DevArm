# 🤖 reBot DevArm オープンソースハードウェア説明

<p align="center">
  <img src="../../media/v1.0.png" alt="reBot-DevArm バナー">
</p>
<p align="center">
  <strong>
    <a href="./readme_zh.md">简体中文</a> &nbsp;|&nbsp;
    <a href="./readme.md">English</a> &nbsp;|&nbsp;
    <a href="./readme_jp.md">日本語</a>&nbsp;|&nbsp;
    <a href="./readme_fr.md">français</a>&nbsp;|&nbsp;
    <a href="./readme_es.md">Español</a>
  </strong>
</p>


現在の BOM は、**Damiao 43 シリーズモーター**を使用する **reBot Arm B601 DM** ロボットアームの部品リストです。もう一つのバージョンである **reBot Arm B601 RS** ロボットアームは、**RobStride モーター**を使用しています。[一覧はこちらをご覧ください](../reBot_B601_RS/README_zh.md)


# 📦 ファイル構成

* `3D_Printed_Parts/`：すべての 3D プリント部品の STEP ファイル
* `Metal_Parts/`：すべての金属加工部品の STEP ファイル
* `Purchased_Parts/`：すべての購入部品の STEP ファイル
* `reBot_B601_DM_v1.0_20260331.step`：ロボットアーム全体の組立ファイル

# 📊 部品表（BOM）

> [!WARNING]
> ここに明記します：公開されている BOM は、Seeed が最終的に出荷するバージョンを**表していません**。この `v1.0` オープンソース版は、開発者が可能な限り低コストで設計を再現できるようにすることを目的としているため、細部に関わる一部の不要なコストを削減しています。Seeed が最終出荷するバージョンでは、金属部品へのレーザー刻印による誤組立防止マーク、耐久性向上のため一部 3D プリント部品を金属部品へ置き換えること、金属加工工場の公差に基づいたクリアランスや加工精度の調整（精度とコストのバランス）、ワイヤーハーネスの特別カスタマイズ（たとえば編組保護スリーブの追加）など、コストを増加させる細部最適化が含まれます。ただし、構造構成自体は同一です。

---

## 🖨️ 3Dプリント部品

| 部品説明 | Image | File Name | Material | Quantity | Notes |
|----------|------|--------|------|----------|------|
| ロボットアームベースプレート | <img src="./3D_Printed_Parts/images/02-BASE.png" width="80"> | `01_BASE_Plate.step` | Bambu ABS Black | 1 | 0.4 ノズル、0.2 レイヤー高、充填率 30% |
| ロボットアームベース | <img src="./3D_Printed_Parts/images/02-BASE_02.png" width="80"> | `01_BASE_Link.step` | Bambu ABS Black | 1 | 0.4 ノズル、0.2 レイヤー高、充填率 30% |
| 上腕左側フィラー | <img src="./3D_Printed_Parts/images/02-DOWN_TRIM_1.png" width="80"> | `01_Upper_Arm_Fuller_L.step` | Bambu PLA Black and Green | 1 | 0.4 ノズル、0.2 レイヤー高、充填率 15% |
| 上腕右側フィラー | <img src="./3D_Printed_Parts/images/02-DOWN_TRIM_2.png" width="80"> | `01_Upper_Arm_Fuller_R.step` | Bambu PLA Black and Green | 1 | 0.4 ノズル、0.2 レイヤー高、充填率 15% |
| 上腕中央フィラー | <img src="./3D_Printed_Parts/images/02-DOWN-FILLING.png" width="80"> | `01_Upper_Arm_Fuller_M.step` | Bambu ABS Black | 1 | 0.4 ノズル、0.2 レイヤー高、充填率 30% |
| 上腕水平リミットブロック | <img src="./3D_Printed_Parts/images/02-SPACER-DOWN.png" width="80"> | `01_Upper_Arm_Limit.step` | Bambu ABS Black | 1 | 0.4 ノズル、0.2 レイヤー高、充填率 30% |
| ロボットアームハンドル | <img src="./3D_Printed_Parts/images/02-HANDLE.png" width="80"> | `01_Arm_Handle.step` | Bambu ABS Black | 1 | 0.4 ノズル、0.2 レイヤー高、充填率 30% |
| 前腕左側フィラー | <img src="./3D_Printed_Parts/images/02-UP-TRIM_1.png" width="80"> | `01_Lower_Arm_Filler_L.step` | Bambu PLA Black and Green | 1 | 0.4 ノズル、0.2 レイヤー高、充填率 15% |
| 前腕右側フィラー | <img src="./3D_Printed_Parts/images/02-UP-TRIM_2.png" width="80"> | `01_Lower_Arm_Filler_R.step` | Bambu PLA Black and Green | 1 | 0.4 ノズル、0.2 レイヤー高、充填率 15% |
| 前腕中央フィラー | <img src="./3D_Printed_Parts/images/02-UP-FILLING.png" width="80"> | `01_Lower_Arm_Filler_M.step` | Bambu ABS Black | 1 | 0.4 ノズル、0.2 レイヤー高、充填率 30% |
| 上腕装飾カバー | <img src="./3D_Printed_Parts/images/02-DOWN-COVER.png" width="80"> | `01_Upper_Arm_Cover.step` | Bambu PLA Green | 1 | 0.4 ノズル、0.2 レイヤー高、充填率 15% |
| 前腕装飾カバー | <img src="./3D_Printed_Parts/images/02-UP-COVER.png" width="80"> | `01_Lower_Arm_Cover.step` | Bambu PLA Green | 1 | 0.4 ノズル、0.2 レイヤー高、充填率 15% |
| モーター No.5 保護カバー | <img src="./3D_Printed_Parts/images/02-MOTOR-COVER.png" width="80"> | `01_Motor_Cover.step` | Bambu ABS Black | 1 | 0.4 ノズル、0.2 レイヤー高、充填率 30% |
| グリッパー水平リミット | <img src="./3D_Printed_Parts/images/02-SPACER.png" width="80"> | `01_Lower_Arm_Limit.step` | Bambu PLA Green | 1 | 0.4 ノズル、0.2 レイヤー高、充填率 15% |
| グリッパースライダーフィラーブラケット | <img src="./3D_Printed_Parts/images/02-3D-RAIL-BRACKET.png" width="80"> | `01-Rail-Bracket.step` | Bambu PLA Green | 1 | 0.4 ノズル、0.2 レイヤー高、充填率 15% |
| グリッパー | <img src="./3D_Printed_Parts/images/02-CLIP_1.png" width="80"> | `01_Finger.step` | Bambu ABS Black | 2 | 0.4 ノズル、0.2 レイヤー高、充填率 45% |
|  | `Reference price` | 平均 **50 $** |  |  | 印刷材料価格や工場の印刷時間により価格は多少変動する場合があります |

### 🧩 印刷推奨

- レイヤー高：0.2 mm
- ノズル：0.4 mm
- サポート：必要に応じて追加
- 材料：熱や一定の力に耐える必要がある部品には、30%〜80% 充填の ABS 材料を使用し、ナイロン / 炭素繊維強化材料に変更することも可能です；外観・装飾部品には 15% 充填の PLA を使用します。
- 荷重を受ける部品に推奨される材料：

---

## 🔩 金属加工部品

> [!WARNING]
> 以下の注記には、3D プリントで代替可能な部品が一部示されており、これによりさらに大幅なコスト削減が可能です。

| 部品説明 | Image | File Name | Material | Quantity | Manufacturing Process | Notes |
|----------|------|--------|----------|------|------|------|
| モーター1 ベアリング取付位置 | <img src="./Metal_Parts/images/02_Base_Motor_Shim.png" width="80"> | `02_Base_Motor_Shim.step` | アルミニウム合金 5052 | 1 | CNC | コスト削減のため、充填率を上げた 3D プリント ABS に置き換え可能 |
| モーター1 回転シャフト | <img src="./Metal_Parts/images/02_Arm_Yaw_Limit.png" width="80"> | `02_Arm_Yaw_Limit.step` | アルミニウム合金 5052 | 1 | CNC | ヨー角動作制限を追加 |
| モーター2-5 用フロントスペーサー | <img src="./Metal_Parts/images/02_Motor_Front_Spacer.png" width="80"> | `02_Motor_Front_Spacer.step` | アルミニウム合金 5052 | 4 | CNC | コスト削減のため、充填率 30% の 3D プリント ABS に置き換え可能 |
| モーター2-4 用リアスペーサー | <img src="./Metal_Parts/images/02_Motor_Back_Spacer.png" width="80"> | `02_Motor_Back_Spacer.step` | アルミニウム合金 5052 | 3 | CNC |  |
| モーター2-4 用リアフランジ | <img src="./Metal_Parts/images/02_FLANGE.png" width="80"> | `02_FLANGE.step` | アルミニウム合金 5052 | 3 | CNC |  |
| 手首モーター5 ベース | <img src="./Metal_Parts/images/02_Wrist_Bracket.png" width="80"> | `02_Wrist_Bracket.step` | アルミニウム合金 5052 | 1 | CNC |  |
| グリッパーコネクター A | <img src="./Metal_Parts/images/02_Gripper_Connector_A.png" width="80"> | `02_Gripper_Connector_A.step` | アルミニウム合金 5052 | 1 | CNC |  |
| グリッパーコネクター B | <img src="./Metal_Parts/images/02_Gripper_Connector_B.png" width="80"> | `02_Gripper_Connector_B.step` | アルミニウム合金 5052 | 1 | CNC |  |
| グリッパースライダー金属ブラケット | <img src="./Metal_Parts/images/02_Slider_Bracket.png" width="80"> | `02_Slider_Bracket.step` | アルミニウム合金 5052 | 1 | CNC | コスト削減のため、充填率を上げた 3D プリント ABS に置き換え可能ですが、長期使用には非推奨 |
| スライダーおよびグリッパーコネクター | <img src="./Metal_Parts/images/02_Slider_Extension.png" width="80"> | `02_Slider_Extension.step` | アルミニウム合金 5052 | 2 | CNC |  |
| 上下アーム関節コネクター 左 | <img src="./Metal_Parts/images/02_Lower_Upper_Link_L.png" width="80"> | `02_Lower_Upper_Link_L.step` | アルミニウム合金 5052 | 1 | CNC |  |
| 上下アーム関節コネクター 右 | <img src="./Metal_Parts/images/02_Lower_Upper_Link_R.png" width="80"> | `02_Lower_Upper_Link_R.step` | アルミニウム合金 5052 | 1 | CNC |  |
| 前腕と手首の関節コネクター 左 | <img src="./Metal_Parts/images/02_Lower_Wrist_Link_L.png" width="80"> | `02_Lower_Wrist_Link_L.step` | アルミニウム合金 5052 | 1 | CNC |  |
| 前腕と手首の関節コネクター 右 | <img src="./Metal_Parts/images/02_Lower_Wrist_Link_R.png" width="80"> | `02_Lower_Wrist_Link_R.step` | アルミニウム合金 5052 | 1 | CNC |  |
| ギアコネクター | <img src="./Metal_Parts/images/02-8MM.png" width="80"> | `02_Gear_Connector.step` | アルミニウム合金 5052 | 1 | CNC | 低荷重用途では、コスト削減のため充填率 80% の 3D プリント ABS を使用可能；高荷重用途では CNC 金属加工を推奨 |
| ラック | <img src="./Metal_Parts/images/Rack.png" width="80"> | `02_Rack.step` | アルミニウム合金 5052 | 2 | CNC |  |
| Link 1 | <img src="./Metal_Parts/images/Link1.png" width="80"> | `03-Link1.step` | アルミニウム合金 5052 | 1 | CNC + 板金 |  |
| Link 2 | <img src="./Metal_Parts/images/Link2.png" width="80"> | `03-Link2.step` | アルミニウム合金 5052 | 2 | CNC + 板金 |  |
| Link 3 左 | <img src="./Metal_Parts/images/Link3_L.png" width="80"> | `03-Link3_L.step` | アルミニウム合金 5052 | 1 | CNC + 板金 |  |
| Link 3 右 | <img src="./Metal_Parts/images/Link3_R.png" width="80"> | `03-Link3_R.step` | アルミニウム合金 5052 | 1 | CNC + 板金 |  |
| Link 5 | <img src="./Metal_Parts/images/Link5.png" width="80"> | `03-Link5.step` | アルミニウム合金 5052 | 1 | CNC + 板金 |  |
| 市場参考価格（複数市場） |  | 平均 **250 $** |  |  |  | アルミニウム 5052 の価格変動、加工精度要件、工場納期などにより価格は多少変動する場合があります。 |

### 🧩 加工指示

- 重要寸法公差：±0.02 mm、GB/T1840-M；
- 表面処理：陽極酸化 / サンドブラスト
- 嵌合部品には H7 / しまりばめの使用を推奨

---

## 🛒 購入部品（標準部品）

> [!WARNING]
> 本製品はお客様ご自身で組み立て・ネジ締めを行う仕様のため、標準的な六角穴付きネジを採用しています。長時間の動作によりネジが緩み、ロボットアームの精度に影響が出る可能性があります。
そのため、ネジにネジロック剤を塗布するか、あるいはゆるみ止めネジを別途ご購入ください。
ゆるみ止めネジを使用する場合は電動ドライバーの使用を推奨しますが、ネジのネジ山をつぶして修復不能な損傷を引き起こさないよう、トルクを弱～中に設定して使用してください。（非常に重要）


| Name | Specification / Model | Quantity | Reference Price | Notes |
|------|----------|------|----------|------|
| ブラシレスモーター | DM4310(V4) | 4 | 120 $/unit | [SeeedStudio](https://www.seeedstudio.com/DIP-Servo-Motor-24V-120RPM-Brushless-98-9mm-4P-L56-W56-H46mm-p-6660.html) |
| ブラシレスモーター | DM4340P(V4) | 3 | 175 $/unit |  [SeeedStudio](https://www.seeedstudio.com/DM4340P-Actuator-p-6663.html)  |
| CAN-USB ドライバーボード |  | 1 | 15 $/unit |   [SeeedStudio](https://www.seeedstudio.com/DM-CAN-USB-Driver-Borad-p-6706.html)   |
| ベアリング | 6707ZZ | 1 | 13 $/unit | [Amazong](https://www.amazon.com/uxcell-35x44x5mm-Shielded-Precision-Lubricated/dp/B0D6WBMW3F/ref=sr_1_1?crid=3J03FBU7MI31J&dib=eyJ2IjoiMSJ9.sfX192-ZSyqh-VJEgq6jR02DrJcdVTxBbKWn5TLypwoK7NyklXkZSQT-3V42_zTm98_Y8dLCtnTzJ9JVnPuBG7bfvUYv0ctrasWhZgU5DFtl2y0CtKLOUOoukmlHqCfonkjZLapmfzSVAaV-3CJYhqizbjedl6zGoDUNo2ryKd4RbtRhJXndBmf96HwTPrPH8g8KB2NPyhnPaP36r6C0Ehdb0xrqjNzKt7YcM7xkZ_8.QvCzMQ0EPe3-5SBYNcuoO5L-Yx0CSr9Vmjc-Ma7FzbY&dib_tag=se&keywords=6707ZZ&qid=1774771772&sprefix=6707zz%2Caps%2C376&sr=8-1) |
| ベアリング | 6803ZZ | 3 | 13 $/unit | [Amazong](https://www.amazon.com/uxcell-17x26x5mm-Shielded-Precision-Lubricated/dp/B0D54JSWBZ/ref=sr_1_1?crid=17L94NDI1JCC0&dib=eyJ2IjoiMSJ9.xH_s9Ui7VlS40EZvr-HektqY3VOJsM-VjyE6JaJEScIWuFZ2UYSM7G8j1fC0HSmbb7YlA0YfUxxCkUzBptwrEEdEHsP94TGplNpPAWwhnH8b76HapXR_uHbr1vu3xe0AYSYP30Quk9LMQrGjUh84bXL82z2mORuiri0VHqo5DmSguK0cHubmVaXtbR_eJ43Z7L2nNqWfgltqzmHsYm7DQvrnIBg9UMlD1o9559nCSKA.E_N7CDPQhShckT-1vHDhYvNgiqRKusa12d43hqATQ5A&dib_tag=se&keywords=6803ZZ&qid=1774771801&sprefix=6803zz%2Caps%2C397&sr=8-1) |
| ベアリング | AXK5578 | 1 | 12 $/unit | [Amazong](https://www.amazon.com/PZRT-AXK5578-Thrust-Bearings-Washers/dp/B0B3M3RZGW/ref=sr_1_1?dib=eyJ2IjoiMSJ9.TatYkzOvpYAJ5K23C7Qr9JKJsPhpJE8p1L3k5_1YqQ7ozSLNgOBEeG9pTYz-WXOWiHkbJq_zZR4FxNHAJZ4euyfOGXkOKycOyN0pUD0_WkJia0PekbRy0sYvyQbE7KZByR-40WiPSPuUcysFewSngPoDGQZzESFOUz__V9ViGCIQAPfdUe2OxVpvtbKZYCQsrSDm8b8okR25bavCvpDbBfPh0He2PEBEpl55L8RtYKmlv62XJyfYT1o29A7wO5n8-g3hpJOrKmmWCybdEEWSmquAT1cjvsPTJDaT_TICsso.6xR5pEGJgTR-u_NOyXxi8VTphoLytGd8zugy1-xu-fE&dib_tag=se&keywords=AXK5578&qid=1774771826&sr=8-1&th=1) |
| リニアレール | MGN9-170mm | 1 | 23 $/unit | [Amazong](https://www.amazon.com/uxcell-Sliding-Carriage-Bearing-Printers/dp/B0D54L45WM/ref=sr_1_1?dib=eyJ2IjoiMSJ9.qNphfY5r4UgLDHslIliMBhC45qBKTl37lJseObJSBp79RJ4VJnAH-lYAMo-rwPiu_uqWmkN7ms4kfAokYvod1seWb5-z2_kVgVuzrCXdiRycNXjrdv3qi5Awuno0_vEqjT4WJ569tAmqm_Rujrdxss7VfpLizFxq6-R8DucuvqZ0M0Y4go9PzRFEFPu4csskz7-UkM1CUidHoKmrT-I7R1Ta0dijj2SYlR_zW0si75k.nRJTebbqw-bFyzkdU8MztHnGdt9qwnHr_gIqa-MDxEQ&dib_tag=se&keywords=MGN9&qid=1774771864&sr=8-1) |
| スライダーブロック | MGN9 | 2 | 10 $/unit | [Amazong](https://www.amazon.com/uxcell-Bearing-Sliding-Carriage-Anti-Fall/dp/B0D9QBQDKB/ref=sr_1_8?dib=eyJ2IjoiMSJ9.qNphfY5r4UgLDHslIliMBhC45qBKTl37lJseObJSBp79RJ4VJnAH-lYAMo-rwPiu_uqWmkN7ms4kfAokYvod1seWb5-z2_kVgVuzrCXdiRycNXjrdv3qi5Awuno0_vEqjT4WJ569tAmqm_Rujrdxss7VfpLizFxq6-R8DucuvqZ0M0Y4go9PzRFEFPu4csskz7-UkM1CUidHoKmrT-I7R1Ta0dijj2SYlR_zW0si75k.nRJTebbqw-bFyzkdU8MztHnGdt9qwnHr_gIqa-MDxEQ&dib_tag=se&keywords=MGN9&qid=1774771864&sr=8-8) |
| ギア | モジュール 1、ボスタイプ、16 歯、6 mm ボア | 1 | 44$/unit | [Amazong](https://www.amazon.com/Module-15-Teeth-Finished-Perforation/dp/B0GDSR1LKM/ref=sr_1_1?crid=2EN1YHE8TEC58&dib=eyJ2IjoiMSJ9.54N73iSlush8K1a_teRazjBGZaQnbFM4MLysEbIq430CEYcVs0slm8KhpC_JlmjyVMocPA3vLANjERYZWweRag36NhX2GGldVTpd31kAWW4.ws8l0qBABmSVrUGX4g2o3sBbUgOnNhl3Nx_Nt-d1HT8&dib_tag=se&keywords=1%2Bmodule16%2Bteeth&qid=1774772022&sprefix=1%2BModule16%2Bteeth%2Caps%2C403&sr=8-1&th=1)  |
| シリコンパッド | 30*9*2mm | 1 | 10 $ | [Amazong](https://www.amazon.com/Self-Adhesive-Anti-Sliding-Anti-Scratch-Protectors-Appliances/dp/B0F9KVYXFZ/ref=sr_1_3?crid=LVY2LLBFQT6J&dib=eyJ2IjoiMSJ9.4qjOEtjEph1QxS_kJF2vIYqvD_8Lzt4GZ2rrywWbrAhniBvp_8YrEsVNcCPQofO4jVqBxFE8Yplyg2XXgAXlUZwzqE-Gp8MYcaPmphL8Mc1n-ARSCNaTq5gc7ZIWsS6u-kR0G2BzIlBo6NF88KvASjKYJfTHpPXHfNCPVw13P-PseVbUZwlVAO9zMHa3a84gHRd-I-mGB8SCmek9mXjN-c-bFxKvJXlz4C5YBBdt9cH3QkSmLgiLZ_iD4K1mh-MwI5WuVOXr5ZOwJ0bVpmHpc_vpbKLr7CkVack3nsC-TM0.40ujhwS5ConOfA8io_c5hcdos70HOKjMFqqKLKgNwI8&dib_tag=se&keywords=silicone%2Bsticker&qid=1774772199&sprefix=silicone%2Bsticker%2Caps%2C380&sr=8-3&th=1) |
| 銅製スペーサー | M4x50mm | 4 | 8 $ | [Amazong](https://www.amazon.com/Female-Standoff-Quadcopter-Computer-Circuit/dp/B09V2CYDMG/ref=pd_bxgy_thbs_d_sccl_2/143-1519846-1961845?pd_rd_w=PozMT&content-id=amzn1.sym.9bef5913-5870-4504-8883-3ba89d7f8e39&pf_rd_p=9bef5913-5870-4504-8883-3ba89d7f8e39&pf_rd_r=0EFDXBJRP1YKJ1QZP2ZW&pd_rd_wg=ARxCM&pd_rd_r=e182821b-861c-468b-889a-961171840b9e&pd_rd_i=B09NDJJJT8&th=1) |
| ネジ | M3*22mm ネジ | Several |  | [Amazong](https://www.amazon.com/METERXITY-50-Pack-Stainless-Threaded-Fasteners/dp/B0FLYG7WZ7/ref=sr_1_3?crid=19X2IQA3ZLJ0S&dib=eyJ2IjoiMSJ9.d4sRDJZ5dCEYkeD4R4dK1WKv6ingc4WOzs0gSnaRNSZsH8aZ-O4uPZZMCurzxm51bzHA3eFgbeHeAp8Syk9BeSPW7epijY_Xce0qqzjA6ewZVIyEozLiMf4t_dMlWFwksFEH0PXNLm6kX4mnwevDmzYKQ6Hz9CNWW_GGQ9_N_LLHJ04qCgwiB4r-RCYG_nUTGj_MeKYAgcx_Kyq0LrKhWWtoYKuYEk4YCbup2_A__OmImZsH8gHwf60F290kPib8LM2ZS1eYZOs8pKCYcC2aTv1rgCW--NrSaTNzVyrzzA4.kHLelL_2m16mzL_HV_7le-Z4zVN7ugxUhS7CLEf1Kc0&dib_tag=se&keywords=M3*22mm%2Bscrew&qid=1774772349&s=industrial&sprefix=m3%2B22mm%2Bscrew%2Cindustrial%2C360&sr=1-3&th=1)  |
| ネジ | M4*16mm ネジ | Several |  | [Amazong](amazon.com/BNUOK-120pcs-Stainless-Threads-Spanner/dp/B0DYNFFB7Q/ref=sr_1_9?crid=W94HLTGLCH57&dib=eyJ2IjoiMSJ9.jg07IMpJdHhW8vR9Ewx53UNnQs_QkpENya6ZqIQWoB6rsXjPLmfWMgAytRy7neNPJJHQzVyP9H7FO5sm9KN9I34nKUQsLRZAG48Rs2rSHwlh2mpA2IPlezHLRlvLN49IIbiHgk5Y63iPwAaxKT27sG3dhyXpf-EABXWIlgUu0FBQ3IIA5kiQDccrsIPN06nR6XBFnNeTu1ogpvhiaZsK7R-VRXcFAsrQvOc4tnzXLlTSM68gR8hBmGYZtQUoOJrRo93U1xfGf7kODnnOqUBWI3VhQIMgnl8Rtt4pl3H7IK0._jHfn0N3UQ0z_FJlv4C8jBXiadkqdO-IHWJzQ3xlm0w&dib_tag=se&keywords=M4*16mm+screw&qid=1774772422&s=industrial&sprefix=m4+16mm+screw%2Cindustrial%2C364&sr=1-9)  |
| ネジ | M3*8mm イモネジ | 5 | 5$ | [Amazong](https://www.amazon.com/Headless-Internal-Stainless-Concave-External/dp/B0D8TGXG9D/ref=sr_1_2?crid=1ZC6Q386LVVYI&dib=eyJ2IjoiMSJ9.3gxD3z1pacUWn2K2NhP0E3OT3j4eoX5mgRDnPfjcCROA7jaVGInIa78o3sE6xleew-Wst2XDHDbExBsltVm2HBiZc6DrUZXO1flMeCHVwKlfksjVw4v-AKoqjonhSsu_t8ocxlmxeRcF95IvvYtaZUZEGpUlhz0Rcx4C5Sk_ZpdHwDUQKgKz_mktcerkTMZ8zMoXGAp8wlHXNXytlXmaoMd16wx--KynCDbtUzeyk_EZErs_9mFVhlP-00-_J-GH0GFshobV-_k9clpEvm4jwS0KDBKuFT0wVWu9QAL2MKE.MKnBsq9xbFeTfdL0mlkBNCjnaBj09nS25kBcpRqfW1k&dib_tag=se&keywords=M3*8mm+set+screw&qid=1774772443&s=industrial&sprefix=m3+8mm+set+screw%2Cindustrial%2C353&sr=1-2)  |
| ネジ | M3*22mm 皿ネジ | Several |  |  [Amazong](https://www.amazon.com/Countersunk-DIN7991-Stainless-Threaded-Fasteners/dp/B0CG1PV6SH/ref=sr_1_1?crid=3LW6LGEBQ9V1R&dib=eyJ2IjoiMSJ9.w_eVqGVJleAAwAsk9U038mfQNN_9V1CiCXnQYShTV_vUp6a9tEFQZ6RX1A1NKWY41iluavltyZG2bhZkdfW1DTIao0AMmdXD1iPDMumzmWqlepecA_oe0vRvmjJGJUUGqH6yBLEXoHgljlHmisrfetu6TOiLw6JBF7U4URcGOWiU5WZej0N9hSmyl9YbyDliozDIK1OSrhnE4K5Qa3mdDig34gt7Rz_fz3bOA-azhWt0TpwFGBiGfGKIwHt9bFJYBf1Jeuiqr2JTp93e6lyJ1Dyzzz1ODiVIFXJ4Z2H1T18.7HlJR0GjprXvY6P4G75sFNvjGApEFl73kwBfhV923jM&dib_tag=se&keywords=M3*22mm%2Bcountersunk%2Bscrew&qid=1774772466&s=industrial&sprefix=m3%2B22mm%2Bcountersunk%2Bscrew%2Cindustrial%2C372&sr=1-1&th=1) |
| ネジ | M3*8mm 皿ネジ | Several |  | [Amazong](https://www.amazon.com/Countersunk-DIN7991-Stainless-Threaded-Fasteners/dp/B0CG1PV6SH/ref=sr_1_1?crid=3LW6LGEBQ9V1R&dib=eyJ2IjoiMSJ9.w_eVqGVJleAAwAsk9U038mfQNN_9V1CiCXnQYShTV_vUp6a9tEFQZ6RX1A1NKWY41iluavltyZG2bhZkdfW1DTIao0AMmdXD1iPDMumzmWqlepecA_oe0vRvmjJGJUUGqH6yBLEXoHgljlHmisrfetu6TOiLw6JBF7U4URcGOWiU5WZej0N9hSmyl9YbyDliozDIK1OSrhnE4K5Qa3mdDig34gt7Rz_fz3bOA-azhWt0TpwFGBiGfGKIwHt9bFJYBf1Jeuiqr2JTp93e6lyJ1Dyzzz1ODiVIFXJ4Z2H1T18.7HlJR0GjprXvY6P4G75sFNvjGApEFl73kwBfhV923jM&dib_tag=se&keywords=M3*22mm%2Bcountersunk%2Bscrew&qid=1774772466&s=industrial&sprefix=m3%2B22mm%2Bcountersunk%2Bscrew%2Cindustrial%2C372&sr=1-1&th=1)  |
| ネジ | M3*16mm 皿ネジ | Several |  |[Amazong](https://www.amazon.com/Countersunk-DIN7991-Stainless-Threaded-Fasteners/dp/B0CG1PV6SH/ref=sr_1_1?crid=3LW6LGEBQ9V1R&dib=eyJ2IjoiMSJ9.w_eVqGVJleAAwAsk9U038mfQNN_9V1CiCXnQYShTV_vUp6a9tEFQZ6RX1A1NKWY41iluavltyZG2bhZkdfW1DTIao0AMmdXD1iPDMumzmWqlepecA_oe0vRvmjJGJUUGqH6yBLEXoHgljlHmisrfetu6TOiLw6JBF7U4URcGOWiU5WZej0N9hSmyl9YbyDliozDIK1OSrhnE4K5Qa3mdDig34gt7Rz_fz3bOA-azhWt0TpwFGBiGfGKIwHt9bFJYBf1Jeuiqr2JTp93e6lyJ1Dyzzz1ODiVIFXJ4Z2H1T18.7HlJR0GjprXvY6P4G75sFNvjGApEFl73kwBfhV923jM&dib_tag=se&keywords=M3*22mm%2Bcountersunk%2Bscrew&qid=1774772466&s=industrial&sprefix=m3%2B22mm%2Bcountersunk%2Bscrew%2Cindustrial%2C372&sr=1-1&th=1)   |
| ネジ | M3*12mm タッピングネジ | Several |  | [Amazong](https://www.amazon.com/Countersunk-DIN7991-Stainless-Threaded-Fasteners/dp/B0CG1PV6SH/ref=sr_1_1?crid=3LW6LGEBQ9V1R&dib=eyJ2IjoiMSJ9.w_eVqGVJleAAwAsk9U038mfQNN_9V1CiCXnQYShTV_vUp6a9tEFQZ6RX1A1NKWY41iluavltyZG2bhZkdfW1DTIao0AMmdXD1iPDMumzmWqlepecA_oe0vRvmjJGJUUGqH6yBLEXoHgljlHmisrfetu6TOiLw6JBF7U4URcGOWiU5WZej0N9hSmyl9YbyDliozDIK1OSrhnE4K5Qa3mdDig34gt7Rz_fz3bOA-azhWt0TpwFGBiGfGKIwHt9bFJYBf1Jeuiqr2JTp93e6lyJ1Dyzzz1ODiVIFXJ4Z2H1T18.7HlJR0GjprXvY6P4G75sFNvjGApEFl73kwBfhV923jM&dib_tag=se&keywords=M3*22mm%2Bcountersunk%2Bscrew&qid=1774772466&s=industrial&sprefix=m3%2B22mm%2Bcountersunk%2Bscrew%2Cindustrial%2C372&sr=1-1&th=1)  |
| ダウエルピン | M4*8mm | Several |  | [Amazong](https://www.amazon.com/Countersunk-DIN7991-Stainless-Threaded-Fasteners/dp/B0CG1PV6SH/ref=sr_1_1?crid=3LW6LGEBQ9V1R&dib=eyJ2IjoiMSJ9.w_eVqGVJleAAwAsk9U038mfQNN_9V1CiCXnQYShTV_vUp6a9tEFQZ6RX1A1NKWY41iluavltyZG2bhZkdfW1DTIao0AMmdXD1iPDMumzmWqlepecA_oe0vRvmjJGJUUGqH6yBLEXoHgljlHmisrfetu6TOiLw6JBF7U4URcGOWiU5WZej0N9hSmyl9YbyDliozDIK1OSrhnE4K5Qa3mdDig34gt7Rz_fz3bOA-azhWt0TpwFGBiGfGKIwHt9bFJYBf1Jeuiqr2JTp93e6lyJ1Dyzzz1ODiVIFXJ4Z2H1T18.7HlJR0GjprXvY6P4G75sFNvjGApEFl73kwBfhV923jM&dib_tag=se&keywords=M3*22mm%2Bcountersunk%2Bscrew&qid=1774772466&s=industrial&sprefix=m3%2B22mm%2Bcountersunk%2Bscrew%2Cindustrial%2C372&sr=1-1&th=1)  |
| ダウエルピン | M4*12mm | Several |  | [Amazong](https://www.amazon.com/Countersunk-DIN7991-Stainless-Threaded-Fasteners/dp/B0CG1PV6SH/ref=sr_1_1?crid=3LW6LGEBQ9V1R&dib=eyJ2IjoiMSJ9.w_eVqGVJleAAwAsk9U038mfQNN_9V1CiCXnQYShTV_vUp6a9tEFQZ6RX1A1NKWY41iluavltyZG2bhZkdfW1DTIao0AMmdXD1iPDMumzmWqlepecA_oe0vRvmjJGJUUGqH6yBLEXoHgljlHmisrfetu6TOiLw6JBF7U4URcGOWiU5WZej0N9hSmyl9YbyDliozDIK1OSrhnE4K5Qa3mdDig34gt7Rz_fz3bOA-azhWt0TpwFGBiGfGKIwHt9bFJYBf1Jeuiqr2JTp93e6lyJ1Dyzzz1ODiVIFXJ4Z2H1T18.7HlJR0GjprXvY6P4G75sFNvjGApEFl73kwBfhV923jM&dib_tag=se&keywords=M3*22mm%2Bcountersunk%2Bscrew&qid=1774772466&s=industrial&sprefix=m3%2B22mm%2Bcountersunk%2Bscrew%2Cindustrial%2C372&sr=1-1&th=1)  |
| ドライバーセット | 六角レンチセット | 1 | 16$  | [Amazong](amazon.com/Amazon-Basics-Ratcheting-Electronics-Screwdriver/dp/B07V4TFWFZ/ref=sr_1_2?crid=ADAY70RZDSLN&dib=eyJ2IjoiMSJ9.jcLL4o6IXTnPlPfTTzbCZCBuZx2sLkvdUQCwlL58aq__GOyLxVPnwLI0mvGptba_HeVz6ctLQ_ziQw56BMDH9IOaw-4PVJGMktQM74mWficwggm3ckDGyAH-agN_zkB3K0_W-wrS56jfcMYFbZSWhWxr-iSOC4sdXwMGlt4rYGtenyn9yAFYBIHqjU2El5_OAKuspsrF0yQvfyfQPQHs46SClWN8zlSemGVZRuVSU26f0f9yApF6BfWHANKNNhT0Mfb6bQ8oM2XUMvwaazrrKoHeTARuoflVaVZvMU776bs.r8gy_gMINEy0qy4JyK--z-IbPZEv-SWeMGohOOE7M60&dib_tag=se&keywords=Screwdriver+set&qid=1774772499&s=industrial&sprefix=screwdriver+set+%2Cindustrial%2C374&sr=1-2)  |
|  <img src="./Purchased_Parts/XT30_2+2.png" width="80">  | XT30 2+2 350mm | 2 | 4 $/cable | 両端とも L 字 |
|  <img src="./Purchased_Parts/XT30_2+2.png" width="80">  | XT30 2+2 350mm | 1 | 4 $/cable | 一方が L 字、もう一方がストレート |
|  <img src="./Purchased_Parts/XT30_2+2.png" width="80">  | XT30 2+2 200mm | 3 | 4 $/cable | 両端とも L 字 |
| カスタム必要 | XT30 2+2 200mm | 1 | 3 $/cable | 両端ともストレート |
| 木工クランプ | 6 インチ G クランプ | 2 | 20 $/unit | [Amazong](https://www.amazon.com/gp/aw/d/B092J1YW2M/?_encoding=UTF8&pd_rd_plhdr=t&aaxitk=3557c048ce58e7dbb50b40c3af69f1d6&hsa_cr_id=0&qid=1774772748&sr=1-1-9e67e56a-6f64-441f-a281-df67fc737124&ref_=sbx_s_sparkle_sbtcd_asin_0_img&pd_rd_w=bNqtC&content-id=amzn1.sym.2fb72bc8-96ef-420d-b08f-c04b69f36507%3Aamzn1.sym.2fb72bc8-96ef-420d-b08f-c04b69f36507&pf_rd_p=2fb72bc8-96ef-420d-b08f-c04b69f36507&pf_rd_r=KDCPNZRHFWEWBWVHWSTR&pd_rd_wg=sBvfF&pd_rd_r=52b946ee-46e2-4e74-86ee-99e291552e44) |
| 電源 | 24V 14.6A | 1 | 30$ | [Amazong](https://www.amazon.com/MEAN-WELL-LRS-350-24-350-4W-Switchable/dp/B013ETVO12/ref=sr_1_1?crid=2559HZMZF6ZUS&dib=eyJ2IjoiMSJ9.vpZwmjb4m5KMNcsg2Kb7wtfqG-A8US11Eaq0B9JOtKBwPyL6ZyUXh5oUrc5lyVLibya9NQ3n4OUjZ1INKKXLtwJWsRJbA_cPohVKu19q3esXrAY8YFpA4teehMNx3zdrt_WhXZyo1zxQUEHgh558m0vuZ0G1KjW3Rk9LOUVn0olRD-nnyvOwhNycxZqoO9KHkTt4q3kkDNEtn_iAH3x1C6wSv97gxI3nFKhXETsCou11G6_97-PJwk6cEkm2aOT2Yg-xm-uYfNMg85_QRFEDdsY-yeC_8n55d_auTSqqc38.SwYH_qOo0fEt9xkz_H6RWeZ78kxrOs9QKhGEKhmfRBs&dib_tag=se&keywords=Power+supply+24V+14.6A&qid=1774772552&s=industrial&sprefix=power+supply+24v+14.6a%2Cindustrial%2C333&sr=1-1) |
| 電源ケーブル | 12AWG | 1 | 30 $ | [Amazong](https://www.amazon.com/Pinfox-Universal-Appliance-Replacement-Pigtail/dp/B0F5PW5SJG/ref=sr_1_6?crid=1EIU51YZCRLT9&dib=eyJ2IjoiMSJ9.SAX2wYEran7eecwu4SDFfugT8z0m8kjFOv972WAv1aoYMTB-us_RgARfoKz3G9hpFqw3p4dtTfzyPzH-pQoitReEJ_DMB-xmLUg3nA3uRNNmYF9Zl9d9iX6yCcU6lCpE_GL9-oqRlTC4A2t1--_88yskpiLLBpx50I08Ze8ql2L6fVikg6k6wx6rTvhpLEHZHqDyITCApEDPPygOu4x8BkY68RpMAM1_Fsd_1M-GMb0YlT2p2u6ywbO08KJg0c3QMfTApauxKjB5INgnxKV9EspudalX0FbQUF1DBc8Fh7s.jtylu4ii8VEhu1FJG6P7h6vw5M7rNci4iQPj8IhOfr8&dib_tag=se&keywords=Power%2BCable&qid=1774772590&s=industrial&sprefix=power%2Bcab%2Cindustrial%2C413&sr=1-6&th=1) |
| 電源ケーブル | XT30 16awg | 1 | 9 $ | [Amazong](https://www.amazon.com/RioRand-Connector-Pigtail-Silicone-Aircraft/dp/B0FY2ZCR83/ref=sr_1_8?crid=1I8XB5AF5YIPA&dib=eyJ2IjoiMSJ9.8Cx4Olln9I8dGnZGL6MRb6AdEsUY70emHKd_NuuvYCBdrZWbUbSmWDDnYirfmFQVEexy0_clLKn2bi2DcGzjf_OEu1RM9j71jZ0-eL2Hgr0AOzFRl06OY7dQE0eMIXesWqJhHUkUoQFTA6EIegYoIUURzHkZAbT3CZyTpQoWYHOfVECyAsKDsKLoekybImOwDe1X9Ub4vawG56Ov7nBLWXf81DpwV-bH9H0kM1jTJaacHHII9eFWdd-50tChIRSI6Ld0kUIvOqbWOWHMshFgK7lHSa76icMJwJOZaruti0c.erWlQgcCcuEDYLFVqRIp7CpmiONST0SMW8W1OT-OnMg&dib_tag=se&keywords=XT30%2B14awg&qid=1774772667&s=industrial&sprefix=xt30%2B14a%2Cindustrial%2C350&sr=1-8&th=1) |


---
