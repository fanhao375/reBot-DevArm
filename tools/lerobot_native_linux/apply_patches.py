#!/usr/bin/env python3
"""Re-apply the local LeRobot teleop patches to the Seeed adapter clones.

These three fixes live in ~/rebot_lerobot (clones of Seeed-Projects repos that
are NOT tracked by reBot-DevArm), so a fresh `pip install -e` / re-clone wipes
them. Run this after re-installing the LeRobot env to restore the patches.

Idempotent: each fix is skipped if already present. Safe to run repeatedly.

Background / why each patch exists:
  1. Arm102 joints 2/3 (shoulder_lift, elbow_flex) are mounted opposite-sign vs
     the Seeed default ranges -> official teleop clipped them to ~0 (joints
     "didn't move"). Negate after unwrap so all axes track at 60Hz.
  2. The leader angle-unwrap window (= range-center +/-180) sat at ~80deg for
     elbow_flex, so past ~90deg the angle wrapped +/-360 and the follower
     snapped to 0 ("过90跳回0", violent jump). Symmetric ranges -> window +/-180,
     no wrap inside the real range of motion.
  (Note: max_relative_target is intentionally left at the upstream default None.
   An earlier local patch capped it at 12 deg/frame as a glitch net, but that
   code path reads all 7 motor states every frame AND clamps the goal to
   present±cap, which made the follower visibly LAG behind the leader. The
   violent-jump root cause is already fixed at source by patch 2 (symmetric
   leader ranges), so the cap is unnecessary — removing it cut the latency.)
See ../../LeRobot_Arm102LD_B601DM遥操作小白执行手册.md (native-Linux section).
"""
import os
import sys

HOME = os.path.expanduser("~")
TELEOP = f"{HOME}/rebot_lerobot/lerobot-teleoperator-rebot-arm-102/lerobot_teleoperator_rebot_arm_102"
ROBOT = f"{HOME}/rebot_lerobot/lerobot-robot-seeed-b601/lerobot_robot_seeed_b601"

PATCHES = [
    # (file, anchor-already-applied-marker, old, new, description)
    (
        f"{TELEOP}/rebot_arm_102_leader.py",
        'if motor_name in {"shoulder_lift", "elbow_flex"}:\n                position = -position',
        "            position = unwrapped\n            if k > 0:",
        "            position = unwrapped\n"
        '            # Local patch: Arm102 joints 2/3 mounted opposite-sign vs the\n'
        "            # Seeed default ranges; negate after unwrap so they track.\n"
        '            if motor_name in {"shoulder_lift", "elbow_flex"}:\n'
        "                position = -position\n"
        "            if k > 0:",
        "1. leader negate joints 2/3",
    ),
    (
        f"{TELEOP}/config_rebot_arm_102_leader.py",
        '"shoulder_lift": (-170.0, 170.0)',
        '"shoulder_lift": (-1.0, 170.0),\n            "elbow_flex":    (-200.0, 1.0),',
        '# Local patch: symmetric ranges center the unwrap window on 0 (+/-180)\n'
        "            # so joints 2/3 do not wrap +/-360 past ~90deg.\n"
        '            "shoulder_lift": (-170.0, 170.0),\n'
        '            "elbow_flex":    (-200.0, 200.0),',
        "2. leader symmetric joint_ranges",
    ),
]


def main():
    ok = True
    for path, marker, old, new, desc in PATCHES:
        if not os.path.exists(path):
            print(f"[MISS] {desc}: file not found {path}")
            ok = False
            continue
        with open(path, encoding="utf-8") as f:
            text = f.read()
        if marker in text:
            print(f"[SKIP] {desc}: already applied")
            continue
        if old not in text:
            print(f"[FAIL] {desc}: anchor not found (upstream changed?) {path}")
            ok = False
            continue
        text = text.replace(old, new, 1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"[DONE] {desc}")
    print("\nAll patches applied." if ok else "\nSome patches FAILED — see above.")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
