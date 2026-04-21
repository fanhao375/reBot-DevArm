# Damiao Motor Datasheets - reBot Arm B601 DM

## PDF Documents

| File | Description |
|------|-------------|
| `DM-J4310-2EC V1.2减速电机说明书V1.2定稿.pdf` | DM-J4310-2EC **V1.2** 减速电机说明书（官方最新，2025.11） |
| `DM-J4340-2ECV1.1减速电机说明书 V1.1 定稿.pdf` | DM-J4340-2EC **V1.1** 减速电机说明书（官方最新，2025.11，45页完整版） |

> 旧版（V1.0/V1.1）已归档到 `旧版/` 子目录。

Source: [Damiao Technology](https://www.mdmbot.com/) | [Damiao Gitee](https://gitee.com/kit-miao/damiao)

---

## Motor Specifications Summary

### DM-J4310-2EC V1.2 (x4，关节 2-5 小关节)

| Category | Parameter | Value |
|----------|-----------|-------|
| **Electrical** | Rated Voltage | 24V |
| | Rated Current | 2.5A |
| | Peak Current | 7.5A |
| **Torque** | Rated Torque | 3 Nm |
| | Peak Torque | 7 Nm |
| **Speed** | Rated Speed | 120 rpm |
| | No-Load Max Speed | 200 rpm |
| **Gearbox** | Gear Ratio | 10:1 |
| | Pole Pairs | 14 |
| | Phase Inductance | 340 uH |
| | Phase Resistance | 650 mOhm |
| **Mechanical** | Outer Diameter | 56 mm |
| | Height | 46 mm |
| | Weight | ~300 g |
| **Encoder** | Resolution | 14-bit |
| | Quantity | 2 (dual encoder) |
| | Type | Magnetic, single-turn absolute |
| **Communication** | Control Interface | CAN @ 1 Mbps |
| | Parameter Interface | UART @ 921600 bps |
| **Control Modes** | | MIT, Speed, Position |
| **Protection** | Driver Over-temp | 120 C |
| | Motor Over-temp | Recommended <= 100 C |
| | Over-voltage | Recommended <= 32V |
| | Under-voltage | Recommended >= 15V |
| | Over-current | Recommended <= 9.8A |
| | Communication Loss | Auto disable |

---

### DM-J4340-2EC V1.1 (x3，关节 1 和肩部大关节)

| Category | Parameter | 24V Version | 48V Version |
|----------|-----------|-------------|-------------|
| **Electrical** | Rated Voltage | 24V | 48V |
| | Rated Current | 2.5A | 2.5A |
| | Peak Current | 8A | 8A |
| **Torque** | Rated Torque | 9 Nm | 9 Nm |
| | Peak Torque | 27 Nm | 27 Nm |
| **Speed** | Rated Speed | 36 rpm | 36 rpm |
| | No-Load Max Speed | 52 rpm | 100 rpm |
| **Gearbox** | Gear Ratio | 40:1 | 40:1 |
| | Pole Pairs | 14 | 14 |
| | Phase Inductance | 360 uH | 360 uH |
| | Phase Resistance | 880 mOhm | 880 mOhm |
| **Mechanical** | Outer Diameter | 57 mm | 57 mm |
| | Height | 56.5 mm | 56.5 mm |
| | Weight | ~375 g | ~375 g |
| **Encoder** | Resolution | 14-bit | 14-bit |
| | Quantity | 2 (dual encoder) | 2 |
| | Type | Magnetic, single-turn absolute | Same |
| **Communication** | Control Interface | CAN @ 1 Mbps | Same |
| | Parameter Interface | UART @ 921600 bps | Same |
| **Control Modes** | | MIT, Speed, Position, Force-Position Hybrid |
| **Protection** | Driver Over-temp | 120 C | 120 C |
| | Motor Over-temp | Recommended <= 100 C | Same |
| | Over-voltage | Recommended <= 32V | Recommended <= 52V |
| | Under-voltage | Recommended >= 15V | Same |
| | Over-current | Recommended <= 9.8A | Same |
| | Communication Loss | Auto disable | Same |

> Note: reBot Arm B601 DM uses the **24V version**.

---

## Key Features (Both Models)

- **Integrated motor + driver**: No external driver board needed
- **Dual 14-bit absolute encoders**: Output shaft position retained after power loss
- **CAN bus daisy-chain**: Multiple motors connected in series via XT30(2+2) cables
- **CAN baud rate configurable**: 125K / 200K / 250K / 500K / 1M / 2M / 2.5M / 3.2M / 4M / 5M (CAN FD supported above 1M)
- **Firmware upgradeable** via UART debugging assistant
- **Register read/write** via CAN (PID tuning, protection thresholds, mode switching)

## CAN Communication Protocol

### Feedback Frame (same for all modes)

| Byte | D[0] | D[1] | D[2] | D[3] | D[4] | D[5] | D[6] | D[7] |
|------|------|------|------|------|------|------|------|------|
| Data | ID\|ERR<<4 | POS[15:8] | POS[7:0] | VEL[11:4] | VEL[3:0]\|T[11:8] | T[7:0] | T_MOS | T_Rotor |

- POS: 16-bit position
- VEL: 12-bit velocity
- T: 12-bit torque
- T_MOS: Driver MOS temperature (C)
- T_Rotor: Motor coil temperature (C)

### Control Frame IDs

| Mode | Frame ID | Data |
|------|----------|------|
| MIT | CAN_ID | p_des + v_des + Kp + Kd + t_ff (8 bytes packed) |
| Position-Speed | 0x100 + CAN_ID | p_des (float) + v_des (float) |
| Speed | 0x200 + CAN_ID | v_des (float) |
| Force-Position Hybrid (4340P only) | 0x300 + CAN_ID | p_des (float) + v_des (uint16) + i_des (uint16) |

### Common CAN Commands

| Command | Frame ID | D[0]-D[1] | D[2] | D[3] |
|---------|----------|-----------|------|------|
| Read Register | 0x7FF | CAN_ID (L/H) | 0x33 | Register Address |
| Write Register | 0x7FF | CAN_ID (L/H) | 0x55 | Register Address + 4-byte Data |
| Save Parameters | 0x7FF | CAN_ID (L/H) | 0xAA | 0x01 |

## Resources

- [Damiao Official Website](https://www.mdmbot.com/)
- [Damiao Gitee Repository (Firmware & Docs)](https://gitee.com/kit-miao/damiao)
- [SeeedStudio Wiki - Damiao Series](https://wiki.seeedstudio.com/cn/damiao_series/)
- [Debugging Assistant Protocol V1.4](https://gitee.com/kit-miao/damiao/tree/master/%E5%85%B3%E8%8A%82%E7%94%B5%E6%9C%BA/%E6%8E%A7%E5%88%B6%E5%8D%8F%E8%AE%AE)
