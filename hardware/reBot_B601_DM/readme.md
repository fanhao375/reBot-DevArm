
# 🤖 reBot DevArm Open-Source Hardware Description

<p align="center">
  <img src="../../media/v1.0.png" alt="reBot-DevArm Banner">
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

The current BOM is the component list for the **reBot Arm B601 DM** robotic arm, which uses the **Damiao 43 series motors**. Another version, the **reBot Arm B601 RS** robotic arm, uses **RobStride motors**. [Please see the list here](../reBot_B601_RS/README.md)


# 📦 File Structure

* `3D_Printed_Parts/`: STEP files for all 3D-printed parts.
* `Metal_Parts/`: STEP files for all metal machined parts.
* `Purchased_Parts/`: STEP files for all purchased parts.
* `reBot_B601_DM_v1.0_20260331.step`: Complete robotic arm assembly file.



# 📊 Bill of Materials (BOM)

> [!WARNING]
> Hereby declared: the published BOM does **not** represent the final version shipped by Seeed. This `v1.0` open-source version is intended to help developers reproduce the design themselves with the lowest possible cost, and therefore reduces some unnecessary detail-related expenses. The final version shipped by Seeed will include details that increase cost, such as laser-engraved anti-error markings on metal parts, replacement of some 3D-printed parts with metal parts for durability, clearance and machining precision adjustments based on the tolerances of metal processing factories (a balance between precision and cost), special customization of wire harnesses (for example, adding braided rope protection), and other detail optimizations. However, the structural configuration remains the same.

---

## 🖨️ 3D-Printed Parts

| Part Description | Image | File Name | Material | Quantity | Notes |
|----------|------|--------|------|----------|------|
| Robotic arm base platform | <img src="./3D_Printed_Parts/images/02-BASE.png" width="80"> | `01_BASE_Plate.step` | Bambu ABS Black | 1 | 0.4 nozzle, 0.2 layer height, 30% infill |
| Robotic arm base | <img src="./3D_Printed_Parts/images/02-BASE_02.png" width="80"> | `01_BASE_Link.step` | Bambu ABS Black | 1 | 0.4 nozzle, 0.2 layer height, 30% infill |
| Upper arm left filler | <img src="./3D_Printed_Parts/images/02-DOWN_TRIM_1.png" width="80"> | `01_Upper_Arm_Fuller_L.step` | Bambu PLA Black and Green | 1 | 0.4 nozzle, 0.2 layer height, 15% infill |
| Upper arm right filler | <img src="./3D_Printed_Parts/images/02-DOWN_TRIM_2.png" width="80"> | `01_Upper_Arm_Fuller_R.step` | Bambu PLA Black and Green | 1 | 0.4 nozzle, 0.2 layer height, 15% infill |
| Upper arm middle filler | <img src="./3D_Printed_Parts/images/02-DOWN-FILLING.png" width="80"> | `01_Upper_Arm_Fuller_M.step` | Bambu ABS Black | 1 | 0.4 nozzle, 0.2 layer height, 30% infill |
| Upper arm horizontal limit block | <img src="./3D_Printed_Parts/images/02-SPACER-DOWN.png" width="80"> | `01_Upper_Arm_Limit.step` | Bambu ABS Black | 1 | 0.4 nozzle, 0.2 layer height, 30% infill |
| Robotic arm handle | <img src="./3D_Printed_Parts/images/02-HANDLE.png" width="80"> | `01_Arm_Handle.step` | Bambu ABS Black | 1 | 0.4 nozzle, 0.2 layer height, 30% infill |
| Forearm left filler | <img src="./3D_Printed_Parts/images/02-UP-TRIM_1.png" width="80"> | `01_Lower_Arm_Filler_L.step` | Bambu PLA Black and Green | 1 | 0.4 nozzle, 0.2 layer height, 15% infill |
| Forearm right filler | <img src="./3D_Printed_Parts/images/02-UP-TRIM_2.png" width="80"> | `01_Lower_Arm_Filler_R.step` | Bambu PLA Black and Green | 1 | 0.4 nozzle, 0.2 layer height, 15% infill |
| Forearm middle filler | <img src="./3D_Printed_Parts/images/02-UP-FILLING.png" width="80"> | `01_Lower_Arm_Filler_M.step` | Bambu ABS Black | 1 | 0.4 nozzle, 0.2 layer height, 30% infill |
| Upper arm decorative cover | <img src="./3D_Printed_Parts/images/02-DOWN-COVER.png" width="80"> | `01_Upper_Arm_Cover.step` | Bambu PLA Green | 1 | 0.4 nozzle, 0.2 layer height, 15% infill |
| Forearm decorative cover | <img src="./3D_Printed_Parts/images/02-UP-COVER.png" width="80"> | `01_Lower_Arm_Cover.step` | Bambu PLA Green | 1 | 0.4 nozzle, 0.2 layer height, 15% infill |
| Motor No. 5 protective cover | <img src="./3D_Printed_Parts/images/02-MOTOR-COVER.png" width="80"> | `01_Motor_Cover.step` | Bambu ABS Black | 1 | 0.4 nozzle, 0.2 layer height, 30% infill |
| Gripper horizontal limit | <img src="./3D_Printed_Parts/images/02-SPACER.png" width="80"> | `01_Lower_Arm_Limit.step` | Bambu PLA Green | 1 | 0.4 nozzle, 0.2 layer height, 15% infill |
| Gripper slider filler bracket | <img src="./3D_Printed_Parts/images/02-3D-RAIL-BRACKET.png" width="80"> | `01-Rail-Bracket.step` | Bambu PLA Green | 1 | 0.4 nozzle, 0.2 layer height, 15% infill |
| Gripper | <img src="./3D_Printed_Parts/images/02-CLIP_1.png" width="80"> | `01_Finger.step` | Bambu ABS Black | 2 | 0.4 nozzle, 0.2 layer height, 45% infill |
|  | `Reference price` | Average **50 $** |  |  | Price may vary slightly depending on printing material prices and factory printing time |

### 🧩 Printing Recommendations

- Layer height: 0.2 mm
- Nozzle: 0.4 mm
- Supports: add as needed
- Materials: parts that need to withstand heat and certain force use ABS material with 30% to 80% infill, and may also be changed to nylon / carbon-fiber-reinforced materials; appearance/decorative parts use PLA with 15% infill.
- Recommended materials for load-bearing parts:

---

## 🔩 Metal Machined Parts

> [!WARNING]
> Some parts that can be replaced with 3D printing are indicated in the notes below, which can further greatly reduce costs.

| Part Description | Image | File Name | Material | Quantity | Manufacturing Process | Notes |
|----------|------|--------|----------|------|------|------|
| Motor 1 bearing mounting position | <img src="./Metal_Parts/images/02_Base_Motor_Shim.png" width="80"> | `02_Base_Motor_Shim.step` | Aluminum Alloy 5052 | 1 | CNC | Can be replaced with 3D-printed ABS with increased infill to reduce cost |
| Motor 1 rotating shaft | <img src="./Metal_Parts/images/02_Arm_Yaw_Limit.png" width="80"> | `02_Arm_Yaw_Limit.step` | Aluminum Alloy 5052 | 1 | CNC | Adds yaw angle motion limit |
| Front spacer for motors 2-5 | <img src="./Metal_Parts/images/02_Motor_Front_Spacer.png" width="80"> | `02_Motor_Front_Spacer.step` | Aluminum Alloy 5052 | 4 | CNC | Can be replaced with 3D-printed ABS, 30% infill, to reduce cost |
| Rear spacer for motors 2-4 | <img src="./Metal_Parts/images/02_Motor_Back_Spacer.png" width="80"> | `02_Motor_Back_Spacer.step` | Aluminum Alloy 5052 | 3 | CNC |  |
| Rear flange for motors 2-4 | <img src="./Metal_Parts/images/02_FLANGE.png" width="80"> | `02_FLANGE.step` | Aluminum Alloy 5052 | 3 | CNC |  |
| Wrist motor 5 base | <img src="./Metal_Parts/images/02_Wrist_Bracket.png" width="80"> | `02_Wrist_Bracket.step` | Aluminum Alloy 5052 | 1 | CNC |  |
| Gripper connector A | <img src="./Metal_Parts/images/02_Gripper_Connector_A.png" width="80"> | `02_Gripper_Connector_A.step` | Aluminum Alloy 5052 | 1 | CNC |  |
| Gripper connector B | <img src="./Metal_Parts/images/02_Gripper_Connector_B.png" width="80"> | `02_Gripper_Connector_B.step` | Aluminum Alloy 5052 | 1 | CNC |  |
| Gripper slider metal bracket | <img src="./Metal_Parts/images/02_Slider_Bracket.png" width="80"> | `02_Slider_Bracket.step` | Aluminum Alloy 5052 | 1 | CNC | Can be replaced with 3D-printed ABS with increased infill to reduce cost, but not recommended for long-term use |
| Slider and gripper connector | <img src="./Metal_Parts/images/02_Slider_Extension.png" width="80"> | `02_Slider_Extension.step` | Aluminum Alloy 5052 | 2 | CNC |  |
| Upper and lower arm joint connector left | <img src="./Metal_Parts/images/02_Lower_Upper_Link_L.png" width="80"> | `02_Lower_Upper_Link_L.step` | Aluminum Alloy 5052 | 1 | CNC |  |
| Upper and lower arm joint connector right | <img src="./Metal_Parts/images/02_Lower_Upper_Link_R.png" width="80"> | `02_Lower_Upper_Link_R.step` | Aluminum Alloy 5052 | 1 | CNC |  |
| Forearm and wrist joint connector left | <img src="./Metal_Parts/images/02_Lower_Wrist_Link_L.png" width="80"> | `02_Lower_Wrist_Link_L.step` | Aluminum Alloy 5052 | 1 | CNC |  |
| Forearm and wrist joint connector right | <img src="./Metal_Parts/images/02_Lower_Wrist_Link_R.png" width="80"> | `02_Lower_Wrist_Link_R.step` | Aluminum Alloy 5052 | 1 | CNC |  |
| Gear connector | <img src="./Metal_Parts/images/02-8MM.png" width="80"> | `02_Gear_Connector.step` | Aluminum Alloy 5052 | 1 | CNC | For low load, 3D-printed ABS with 80% infill can be used to reduce cost; for high load, CNC metal machining is recommended |
| Rack | <img src="./Metal_Parts/images/Rack.png" width="80"> | `02_Rack.step` | Aluminum Alloy 5052 | 2 | CNC |  |
| Link 1 | <img src="./Metal_Parts/images/Link1.png" width="80"> | `03-Link1.step` | Aluminum Alloy 5052 | 1 | CNC + Sheet Metal |  |
| Link 2 | <img src="./Metal_Parts/images/Link2.png" width="80"> | `03-Link2.step` | Aluminum Alloy 5052 | 2 | CNC + Sheet Metal |  |
| Link 3 left | <img src="./Metal_Parts/images/Link3_L.png" width="80"> | `03-Link3_L.step` | Aluminum Alloy 5052 | 1 | CNC + Sheet Metal |  |
| Link 3 right | <img src="./Metal_Parts/images/Link3_R.png" width="80"> | `03-Link3_R.step` | Aluminum Alloy 5052 | 1 | CNC + Sheet Metal |  |
| Link 5 | <img src="./Metal_Parts/images/Link5.png" width="80"> | `03-Link5.step` | Aluminum Alloy 5052 | 1 | CNC + Sheet Metal |  |
| Multiple market reference price |  | Average **250 $** |  |  |  | Price may vary slightly due to fluctuations in aluminum 5052 cost, machining precision requirements, factory lead time, etc. |

### 🧩 Machining Instructions

- Critical dimensional tolerance: ±0.02 mm, GB/T1840-M;
- Surface treatment: anodizing / sandblasting
- Mating parts are recommended to use H7 / interference fit

---

## 🛒 Purchased Parts (Standard Parts)

> [!WARNING]
> Since this robot arm is designed for self-assembly, we have selected standard hex socket screws. However, these screws may loosen after prolonged operation, which can affect the arm’s positioning accuracy. For this reason, we recommend that you either purchase thread locking adhesive to apply to the screws, or use pre-applied thread locking screws directly.
If you choose anti-loosening screws, we highly recommend using an electric screwdriver. Important: Always use low to medium torque settings to avoid screw stripping, which will cause irreversible damage.



| Name | Specification / Model | Quantity | Reference Price | Notes |
|------|----------|------|----------|------|
| Brushless motor | DM4310(V4) | 4 | 120 $/unit | [SeeedStudio](https://www.seeedstudio.com/DIP-Servo-Motor-24V-120RPM-Brushless-98-9mm-4P-L56-W56-H46mm-p-6660.html) |
| Brushless motor | DM4340P(V4) | 3 | 175 $/unit |  [SeeedStudio](https://www.seeedstudio.com/DM4340P-Actuator-p-6663.html)  |
| CAN-USB driver board |  | 1 | 15 $/unit |   [SeeedStudio](https://www.seeedstudio.com/DM-CAN-USB-Driver-Borad-p-6706.html)   |
| Bearing | 6707ZZ | 1 | 13 $/unit | [Amazong](https://www.amazon.com/uxcell-35x44x5mm-Shielded-Precision-Lubricated/dp/B0D6WBMW3F/ref=sr_1_1?crid=3J03FBU7MI31J&dib=eyJ2IjoiMSJ9.sfX192-ZSyqh-VJEgq6jR02DrJcdVTxBbKWn5TLypwoK7NyklXkZSQT-3V42_zTm98_Y8dLCtnTzJ9JVnPuBG7bfvUYv0ctrasWhZgU5DFtl2y0CtKLOUOoukmlHqCfonkjZLapmfzSVAaV-3CJYhqizbjedl6zGoDUNo2ryKd4RbtRhJXndBmf96HwTPrPH8g8KB2NPyhnPaP36r6C0Ehdb0xrqjNzKt7YcM7xkZ_8.QvCzMQ0EPe3-5SBYNcuoO5L-Yx0CSr9Vmjc-Ma7FzbY&dib_tag=se&keywords=6707ZZ&qid=1774771772&sprefix=6707zz%2Caps%2C376&sr=8-1) |
| Bearing | 6803ZZ | 3 | 13 $/unit | [Amazong](https://www.amazon.com/uxcell-17x26x5mm-Shielded-Precision-Lubricated/dp/B0D54JSWBZ/ref=sr_1_1?crid=17L94NDI1JCC0&dib=eyJ2IjoiMSJ9.xH_s9Ui7VlS40EZvr-HektqY3VOJsM-VjyE6JaJEScIWuFZ2UYSM7G8j1fC0HSmbb7YlA0YfUxxCkUzBptwrEEdEHsP94TGplNpPAWwhnH8b76HapXR_uHbr1vu3xe0AYSYP30Quk9LMQrGjUh84bXL82z2mORuiri0VHqo5DmSguK0cHubmVaXtbR_eJ43Z7L2nNqWfgltqzmHsYm7DQvrnIBg9UMlD1o9559nCSKA.E_N7CDPQhShckT-1vHDhYvNgiqRKusa12d43hqATQ5A&dib_tag=se&keywords=6803ZZ&qid=1774771801&sprefix=6803zz%2Caps%2C397&sr=8-1) |
| Bearing | AXK5578 | 1 | 12 $/unit | [Amazong](https://www.amazon.com/PZRT-AXK5578-Thrust-Bearings-Washers/dp/B0B3M3RZGW/ref=sr_1_1?dib=eyJ2IjoiMSJ9.TatYkzOvpYAJ5K23C7Qr9JKJsPhpJE8p1L3k5_1YqQ7ozSLNgOBEeG9pTYz-WXOWiHkbJq_zZR4FxNHAJZ4euyfOGXkOKycOyN0pUD0_WkJia0PekbRy0sYvyQbE7KZByR-40WiPSPuUcysFewSngPoDGQZzESFOUz__V9ViGCIQAPfdUe2OxVpvtbKZYCQsrSDm8b8okR25bavCvpDbBfPh0He2PEBEpl55L8RtYKmlv62XJyfYT1o29A7wO5n8-g3hpJOrKmmWCybdEEWSmquAT1cjvsPTJDaT_TICsso.6xR5pEGJgTR-u_NOyXxi8VTphoLytGd8zugy1-xu-fE&dib_tag=se&keywords=AXK5578&qid=1774771826&sr=8-1&th=1) |
| Linear rail | MGN9-170mm | 1 | 23 $/unit | [Amazong](https://www.amazon.com/uxcell-Sliding-Carriage-Bearing-Printers/dp/B0D54L45WM/ref=sr_1_1?dib=eyJ2IjoiMSJ9.qNphfY5r4UgLDHslIliMBhC45qBKTl37lJseObJSBp79RJ4VJnAH-lYAMo-rwPiu_uqWmkN7ms4kfAokYvod1seWb5-z2_kVgVuzrCXdiRycNXjrdv3qi5Awuno0_vEqjT4WJ569tAmqm_Rujrdxss7VfpLizFxq6-R8DucuvqZ0M0Y4go9PzRFEFPu4csskz7-UkM1CUidHoKmrT-I7R1Ta0dijj2SYlR_zW0si75k.nRJTebbqw-bFyzkdU8MztHnGdt9qwnHr_gIqa-MDxEQ&dib_tag=se&keywords=MGN9&qid=1774771864&sr=8-1) |
| Slider block | MGN9 | 2 | 10 $/unit | [Amazong](https://www.amazon.com/uxcell-Bearing-Sliding-Carriage-Anti-Fall/dp/B0D9QBQDKB/ref=sr_1_8?dib=eyJ2IjoiMSJ9.qNphfY5r4UgLDHslIliMBhC45qBKTl37lJseObJSBp79RJ4VJnAH-lYAMo-rwPiu_uqWmkN7ms4kfAokYvod1seWb5-z2_kVgVuzrCXdiRycNXjrdv3qi5Awuno0_vEqjT4WJ569tAmqm_Rujrdxss7VfpLizFxq6-R8DucuvqZ0M0Y4go9PzRFEFPu4csskz7-UkM1CUidHoKmrT-I7R1Ta0dijj2SYlR_zW0si75k.nRJTebbqw-bFyzkdU8MztHnGdt9qwnHr_gIqa-MDxEQ&dib_tag=se&keywords=MGN9&qid=1774771864&sr=8-8) |
| Gear | Module 1, boss type, 16 teeth, 6 mm bore | 1 | 44$/unit | [Amazong](https://www.amazon.com/Module-15-Teeth-Finished-Perforation/dp/B0GDSR1LKM/ref=sr_1_1?crid=2EN1YHE8TEC58&dib=eyJ2IjoiMSJ9.54N73iSlush8K1a_teRazjBGZaQnbFM4MLysEbIq430CEYcVs0slm8KhpC_JlmjyVMocPA3vLANjERYZWweRag36NhX2GGldVTpd31kAWW4.ws8l0qBABmSVrUGX4g2o3sBbUgOnNhl3Nx_Nt-d1HT8&dib_tag=se&keywords=1%2Bmodule16%2Bteeth&qid=1774772022&sprefix=1%2BModule16%2Bteeth%2Caps%2C403&sr=8-1&th=1)  |
| Silicone pad | 30*9*2mm | 1 | 10 $ | [Amazong](https://www.amazon.com/Self-Adhesive-Anti-Sliding-Anti-Scratch-Protectors-Appliances/dp/B0F9KVYXFZ/ref=sr_1_3?crid=LVY2LLBFQT6J&dib=eyJ2IjoiMSJ9.4qjOEtjEph1QxS_kJF2vIYqvD_8Lzt4GZ2rrywWbrAhniBvp_8YrEsVNcCPQofO4jVqBxFE8Yplyg2XXgAXlUZwzqE-Gp8MYcaPmphL8Mc1n-ARSCNaTq5gc7ZIWsS6u-kR0G2BzIlBo6NF88KvASjKYJfTHpPXHfNCPVw13P-PseVbUZwlVAO9zMHa3a84gHRd-I-mGB8SCmek9mXjN-c-bFxKvJXlz4C5YBBdt9cH3QkSmLgiLZ_iD4K1mh-MwI5WuVOXr5ZOwJ0bVpmHpc_vpbKLr7CkVack3nsC-TM0.40ujhwS5ConOfA8io_c5hcdos70HOKjMFqqKLKgNwI8&dib_tag=se&keywords=silicone%2Bsticker&qid=1774772199&sprefix=silicone%2Bsticker%2Caps%2C380&sr=8-3&th=1) |
| Copper standoff | M4x50mm | 4 | 8 $ | [Amazong](https://www.amazon.com/Female-Standoff-Quadcopter-Computer-Circuit/dp/B09V2CYDMG/ref=pd_bxgy_thbs_d_sccl_2/143-1519846-1961845?pd_rd_w=PozMT&content-id=amzn1.sym.9bef5913-5870-4504-8883-3ba89d7f8e39&pf_rd_p=9bef5913-5870-4504-8883-3ba89d7f8e39&pf_rd_r=0EFDXBJRP1YKJ1QZP2ZW&pd_rd_wg=ARxCM&pd_rd_r=e182821b-861c-468b-889a-961171840b9e&pd_rd_i=B09NDJJJT8&th=1) |
| Screw | M3*22mm screw | Several |  | [Amazong](https://www.amazon.com/METERXITY-50-Pack-Stainless-Threaded-Fasteners/dp/B0FLYG7WZ7/ref=sr_1_3?crid=19X2IQA3ZLJ0S&dib=eyJ2IjoiMSJ9.d4sRDJZ5dCEYkeD4R4dK1WKv6ingc4WOzs0gSnaRNSZsH8aZ-O4uPZZMCurzxm51bzHA3eFgbeHeAp8Syk9BeSPW7epijY_Xce0qqzjA6ewZVIyEozLiMf4t_dMlWFwksFEH0PXNLm6kX4mnwevDmzYKQ6Hz9CNWW_GGQ9_N_LLHJ04qCgwiB4r-RCYG_nUTGj_MeKYAgcx_Kyq0LrKhWWtoYKuYEk4YCbup2_A__OmImZsH8gHwf60F290kPib8LM2ZS1eYZOs8pKCYcC2aTv1rgCW--NrSaTNzVyrzzA4.kHLelL_2m16mzL_HV_7le-Z4zVN7ugxUhS7CLEf1Kc0&dib_tag=se&keywords=M3*22mm%2Bscrew&qid=1774772349&s=industrial&sprefix=m3%2B22mm%2Bscrew%2Cindustrial%2C360&sr=1-3&th=1)  |
| Screw | M4*16mm screw | Several |  | [Amazong](amazon.com/BNUOK-120pcs-Stainless-Threads-Spanner/dp/B0DYNFFB7Q/ref=sr_1_9?crid=W94HLTGLCH57&dib=eyJ2IjoiMSJ9.jg07IMpJdHhW8vR9Ewx53UNnQs_QkpENya6ZqIQWoB6rsXjPLmfWMgAytRy7neNPJJHQzVyP9H7FO5sm9KN9I34nKUQsLRZAG48Rs2rSHwlh2mpA2IPlezHLRlvLN49IIbiHgk5Y63iPwAaxKT27sG3dhyXpf-EABXWIlgUu0FBQ3IIA5kiQDccrsIPN06nR6XBFnNeTu1ogpvhiaZsK7R-VRXcFAsrQvOc4tnzXLlTSM68gR8hBmGYZtQUoOJrRo93U1xfGf7kODnnOqUBWI3VhQIMgnl8Rtt4pl3H7IK0._jHfn0N3UQ0z_FJlv4C8jBXiadkqdO-IHWJzQ3xlm0w&dib_tag=se&keywords=M4*16mm+screw&qid=1774772422&s=industrial&sprefix=m4+16mm+screw%2Cindustrial%2C364&sr=1-9)  |
| Screw | M3*8mm set screw | 5 | 5$ | [Amazong](https://www.amazon.com/Headless-Internal-Stainless-Concave-External/dp/B0D8TGXG9D/ref=sr_1_2?crid=1ZC6Q386LVVYI&dib=eyJ2IjoiMSJ9.3gxD3z1pacUWn2K2NhP0E3OT3j4eoX5mgRDnPfjcCROA7jaVGInIa78o3sE6xleew-Wst2XDHDbExBsltVm2HBiZc6DrUZXO1flMeCHVwKlfksjVw4v-AKoqjonhSsu_t8ocxlmxeRcF95IvvYtaZUZEGpUlhz0Rcx4C5Sk_ZpdHwDUQKgKz_mktcerkTMZ8zMoXGAp8wlHXNXytlXmaoMd16wx--KynCDbtUzeyk_EZErs_9mFVhlP-00-_J-GH0GFshobV-_k9clpEvm4jwS0KDBKuFT0wVWu9QAL2MKE.MKnBsq9xbFeTfdL0mlkBNCjnaBj09nS25kBcpRqfW1k&dib_tag=se&keywords=M3*8mm+set+screw&qid=1774772443&s=industrial&sprefix=m3+8mm+set+screw%2Cindustrial%2C353&sr=1-2)  |
| Screw | M3*22mm countersunk screw | Several |  |  [Amazong](https://www.amazon.com/Countersunk-DIN7991-Stainless-Threaded-Fasteners/dp/B0CG1PV6SH/ref=sr_1_1?crid=3LW6LGEBQ9V1R&dib=eyJ2IjoiMSJ9.w_eVqGVJleAAwAsk9U038mfQNN_9V1CiCXnQYShTV_vUp6a9tEFQZ6RX1A1NKWY41iluavltyZG2bhZkdfW1DTIao0AMmdXD1iPDMumzmWqlepecA_oe0vRvmjJGJUUGqH6yBLEXoHgljlHmisrfetu6TOiLw6JBF7U4URcGOWiU5WZej0N9hSmyl9YbyDliozDIK1OSrhnE4K5Qa3mdDig34gt7Rz_fz3bOA-azhWt0TpwFGBiGfGKIwHt9bFJYBf1Jeuiqr2JTp93e6lyJ1Dyzzz1ODiVIFXJ4Z2H1T18.7HlJR0GjprXvY6P4G75sFNvjGApEFl73kwBfhV923jM&dib_tag=se&keywords=M3*22mm%2Bcountersunk%2Bscrew&qid=1774772466&s=industrial&sprefix=m3%2B22mm%2Bcountersunk%2Bscrew%2Cindustrial%2C372&sr=1-1&th=1) |
| Screw | M3*8mm countersunk screw | Several |  | [Amazong](https://www.amazon.com/Countersunk-DIN7991-Stainless-Threaded-Fasteners/dp/B0CG1PV6SH/ref=sr_1_1?crid=3LW6LGEBQ9V1R&dib=eyJ2IjoiMSJ9.w_eVqGVJleAAwAsk9U038mfQNN_9V1CiCXnQYShTV_vUp6a9tEFQZ6RX1A1NKWY41iluavltyZG2bhZkdfW1DTIao0AMmdXD1iPDMumzmWqlepecA_oe0vRvmjJGJUUGqH6yBLEXoHgljlHmisrfetu6TOiLw6JBF7U4URcGOWiU5WZej0N9hSmyl9YbyDliozDIK1OSrhnE4K5Qa3mdDig34gt7Rz_fz3bOA-azhWt0TpwFGBiGfGKIwHt9bFJYBf1Jeuiqr2JTp93e6lyJ1Dyzzz1ODiVIFXJ4Z2H1T18.7HlJR0GjprXvY6P4G75sFNvjGApEFl73kwBfhV923jM&dib_tag=se&keywords=M3*22mm%2Bcountersunk%2Bscrew&qid=1774772466&s=industrial&sprefix=m3%2B22mm%2Bcountersunk%2Bscrew%2Cindustrial%2C372&sr=1-1&th=1)  |
| Screw | M3*16mm countersunk screw | Several |  |[Amazong](https://www.amazon.com/Countersunk-DIN7991-Stainless-Threaded-Fasteners/dp/B0CG1PV6SH/ref=sr_1_1?crid=3LW6LGEBQ9V1R&dib=eyJ2IjoiMSJ9.w_eVqGVJleAAwAsk9U038mfQNN_9V1CiCXnQYShTV_vUp6a9tEFQZ6RX1A1NKWY41iluavltyZG2bhZkdfW1DTIao0AMmdXD1iPDMumzmWqlepecA_oe0vRvmjJGJUUGqH6yBLEXoHgljlHmisrfetu6TOiLw6JBF7U4URcGOWiU5WZej0N9hSmyl9YbyDliozDIK1OSrhnE4K5Qa3mdDig34gt7Rz_fz3bOA-azhWt0TpwFGBiGfGKIwHt9bFJYBf1Jeuiqr2JTp93e6lyJ1Dyzzz1ODiVIFXJ4Z2H1T18.7HlJR0GjprXvY6P4G75sFNvjGApEFl73kwBfhV923jM&dib_tag=se&keywords=M3*22mm%2Bcountersunk%2Bscrew&qid=1774772466&s=industrial&sprefix=m3%2B22mm%2Bcountersunk%2Bscrew%2Cindustrial%2C372&sr=1-1&th=1)   |
| Screw | M3*12mm self-tapping screw | Several |  | [Amazong](https://www.amazon.com/Countersunk-DIN7991-Stainless-Threaded-Fasteners/dp/B0CG1PV6SH/ref=sr_1_1?crid=3LW6LGEBQ9V1R&dib=eyJ2IjoiMSJ9.w_eVqGVJleAAwAsk9U038mfQNN_9V1CiCXnQYShTV_vUp6a9tEFQZ6RX1A1NKWY41iluavltyZG2bhZkdfW1DTIao0AMmdXD1iPDMumzmWqlepecA_oe0vRvmjJGJUUGqH6yBLEXoHgljlHmisrfetu6TOiLw6JBF7U4URcGOWiU5WZej0N9hSmyl9YbyDliozDIK1OSrhnE4K5Qa3mdDig34gt7Rz_fz3bOA-azhWt0TpwFGBiGfGKIwHt9bFJYBf1Jeuiqr2JTp93e6lyJ1Dyzzz1ODiVIFXJ4Z2H1T18.7HlJR0GjprXvY6P4G75sFNvjGApEFl73kwBfhV923jM&dib_tag=se&keywords=M3*22mm%2Bcountersunk%2Bscrew&qid=1774772466&s=industrial&sprefix=m3%2B22mm%2Bcountersunk%2Bscrew%2Cindustrial%2C372&sr=1-1&th=1)  |
| Dowel pin | M4*8mm | Several |  | [Amazong](https://www.amazon.com/Countersunk-DIN7991-Stainless-Threaded-Fasteners/dp/B0CG1PV6SH/ref=sr_1_1?crid=3LW6LGEBQ9V1R&dib=eyJ2IjoiMSJ9.w_eVqGVJleAAwAsk9U038mfQNN_9V1CiCXnQYShTV_vUp6a9tEFQZ6RX1A1NKWY41iluavltyZG2bhZkdfW1DTIao0AMmdXD1iPDMumzmWqlepecA_oe0vRvmjJGJUUGqH6yBLEXoHgljlHmisrfetu6TOiLw6JBF7U4URcGOWiU5WZej0N9hSmyl9YbyDliozDIK1OSrhnE4K5Qa3mdDig34gt7Rz_fz3bOA-azhWt0TpwFGBiGfGKIwHt9bFJYBf1Jeuiqr2JTp93e6lyJ1Dyzzz1ODiVIFXJ4Z2H1T18.7HlJR0GjprXvY6P4G75sFNvjGApEFl73kwBfhV923jM&dib_tag=se&keywords=M3*22mm%2Bcountersunk%2Bscrew&qid=1774772466&s=industrial&sprefix=m3%2B22mm%2Bcountersunk%2Bscrew%2Cindustrial%2C372&sr=1-1&th=1)  |
| Dowel pin | M4*12mm | Several |  | [Amazong](https://www.amazon.com/Countersunk-DIN7991-Stainless-Threaded-Fasteners/dp/B0CG1PV6SH/ref=sr_1_1?crid=3LW6LGEBQ9V1R&dib=eyJ2IjoiMSJ9.w_eVqGVJleAAwAsk9U038mfQNN_9V1CiCXnQYShTV_vUp6a9tEFQZ6RX1A1NKWY41iluavltyZG2bhZkdfW1DTIao0AMmdXD1iPDMumzmWqlepecA_oe0vRvmjJGJUUGqH6yBLEXoHgljlHmisrfetu6TOiLw6JBF7U4URcGOWiU5WZej0N9hSmyl9YbyDliozDIK1OSrhnE4K5Qa3mdDig34gt7Rz_fz3bOA-azhWt0TpwFGBiGfGKIwHt9bFJYBf1Jeuiqr2JTp93e6lyJ1Dyzzz1ODiVIFXJ4Z2H1T18.7HlJR0GjprXvY6P4G75sFNvjGApEFl73kwBfhV923jM&dib_tag=se&keywords=M3*22mm%2Bcountersunk%2Bscrew&qid=1774772466&s=industrial&sprefix=m3%2B22mm%2Bcountersunk%2Bscrew%2Cindustrial%2C372&sr=1-1&th=1)  |
| Screwdriver set | Hex key set | 1 | 16$  | [Amazong](amazon.com/Amazon-Basics-Ratcheting-Electronics-Screwdriver/dp/B07V4TFWFZ/ref=sr_1_2?crid=ADAY70RZDSLN&dib=eyJ2IjoiMSJ9.jcLL4o6IXTnPlPfTTzbCZCBuZx2sLkvdUQCwlL58aq__GOyLxVPnwLI0mvGptba_HeVz6ctLQ_ziQw56BMDH9IOaw-4PVJGMktQM74mWficwggm3ckDGyAH-agN_zkB3K0_W-wrS56jfcMYFbZSWhWxr-iSOC4sdXwMGlt4rYGtenyn9yAFYBIHqjU2El5_OAKuspsrF0yQvfyfQPQHs46SClWN8zlSemGVZRuVSU26f0f9yApF6BfWHANKNNhT0Mfb6bQ8oM2XUMvwaazrrKoHeTARuoflVaVZvMU776bs.r8gy_gMINEy0qy4JyK--z-IbPZEv-SWeMGohOOE7M60&dib_tag=se&keywords=Screwdriver+set&qid=1774772499&s=industrial&sprefix=screwdriver+set+%2Cindustrial%2C374&sr=1-2)  |
| Custom required | XT30 2+2 350mm | 2 | 4 $/cable | Both ends angled |
| Custom required | XT30 2+2 350mm | 1 | 4 $/cable | One angled end and one straight end |
| Custom required | XT30 2+2 200mm | 3 | 4 $/cable | Both ends angled |
| Custom required | XT30 2+2 200mm | 1 | 3 $/cable | Both ends straight |
| Woodworking clamp | 6-inch G clamp | 2 | 20 $/unit | [Amazong](https://www.amazon.com/gp/aw/d/B092J1YW2M/?_encoding=UTF8&pd_rd_plhdr=t&aaxitk=3557c048ce58e7dbb50b40c3af69f1d6&hsa_cr_id=0&qid=1774772748&sr=1-1-9e67e56a-6f64-441f-a281-df67fc737124&ref_=sbx_s_sparkle_sbtcd_asin_0_img&pd_rd_w=bNqtC&content-id=amzn1.sym.2fb72bc8-96ef-420d-b08f-c04b69f36507%3Aamzn1.sym.2fb72bc8-96ef-420d-b08f-c04b69f36507&pf_rd_p=2fb72bc8-96ef-420d-b08f-c04b69f36507&pf_rd_r=KDCPNZRHFWEWBWVHWSTR&pd_rd_wg=sBvfF&pd_rd_r=52b946ee-46e2-4e74-86ee-99e291552e44) |
| Power supply | 24V 14.6A | 1 | 30$ | [Amazong](https://www.amazon.com/MEAN-WELL-LRS-350-24-350-4W-Switchable/dp/B013ETVO12/ref=sr_1_1?crid=2559HZMZF6ZUS&dib=eyJ2IjoiMSJ9.vpZwmjb4m5KMNcsg2Kb7wtfqG-A8US11Eaq0B9JOtKBwPyL6ZyUXh5oUrc5lyVLibya9NQ3n4OUjZ1INKKXLtwJWsRJbA_cPohVKu19q3esXrAY8YFpA4teehMNx3zdrt_WhXZyo1zxQUEHgh558m0vuZ0G1KjW3Rk9LOUVn0olRD-nnyvOwhNycxZqoO9KHkTt4q3kkDNEtn_iAH3x1C6wSv97gxI3nFKhXETsCou11G6_97-PJwk6cEkm2aOT2Yg-xm-uYfNMg85_QRFEDdsY-yeC_8n55d_auTSqqc38.SwYH_qOo0fEt9xkz_H6RWeZ78kxrOs9QKhGEKhmfRBs&dib_tag=se&keywords=Power+supply+24V+14.6A&qid=1774772552&s=industrial&sprefix=power+supply+24v+14.6a%2Cindustrial%2C333&sr=1-1) |
| Power Cable | 12AWG | 1 | 30 $ | [Amazong](https://www.amazon.com/Pinfox-Universal-Appliance-Replacement-Pigtail/dp/B0F5PW5SJG/ref=sr_1_6?crid=1EIU51YZCRLT9&dib=eyJ2IjoiMSJ9.SAX2wYEran7eecwu4SDFfugT8z0m8kjFOv972WAv1aoYMTB-us_RgARfoKz3G9hpFqw3p4dtTfzyPzH-pQoitReEJ_DMB-xmLUg3nA3uRNNmYF9Zl9d9iX6yCcU6lCpE_GL9-oqRlTC4A2t1--_88yskpiLLBpx50I08Ze8ql2L6fVikg6k6wx6rTvhpLEHZHqDyITCApEDPPygOu4x8BkY68RpMAM1_Fsd_1M-GMb0YlT2p2u6ywbO08KJg0c3QMfTApauxKjB5INgnxKV9EspudalX0FbQUF1DBc8Fh7s.jtylu4ii8VEhu1FJG6P7h6vw5M7rNci4iQPj8IhOfr8&dib_tag=se&keywords=Power%2BCable&qid=1774772590&s=industrial&sprefix=power%2Bcab%2Cindustrial%2C413&sr=1-6&th=1) |
| Power Cable | XT30 16awg | 1 | 9 $ | [Amazong](https://www.amazon.com/RioRand-Connector-Pigtail-Silicone-Aircraft/dp/B0FY2ZCR83/ref=sr_1_8?crid=1I8XB5AF5YIPA&dib=eyJ2IjoiMSJ9.8Cx4Olln9I8dGnZGL6MRb6AdEsUY70emHKd_NuuvYCBdrZWbUbSmWDDnYirfmFQVEexy0_clLKn2bi2DcGzjf_OEu1RM9j71jZ0-eL2Hgr0AOzFRl06OY7dQE0eMIXesWqJhHUkUoQFTA6EIegYoIUURzHkZAbT3CZyTpQoWYHOfVECyAsKDsKLoekybImOwDe1X9Ub4vawG56Ov7nBLWXf81DpwV-bH9H0kM1jTJaacHHII9eFWdd-50tChIRSI6Ld0kUIvOqbWOWHMshFgK7lHSa76icMJwJOZaruti0c.erWlQgcCcuEDYLFVqRIp7CpmiONST0SMW8W1OT-OnMg&dib_tag=se&keywords=XT30%2B14awg&qid=1774772667&s=industrial&sprefix=xt30%2B14a%2Cindustrial%2C350&sr=1-8&th=1) |


---
