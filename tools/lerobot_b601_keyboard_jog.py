#!/usr/bin/env python3
"""Small-step keyboard jog for Seeed B601 follower through the LeRobot adapter."""

from __future__ import annotations

import argparse
import select
import sys
import termios
import tty
from dataclasses import fields

import lerobot_robot_seeed_b601  # noqa: F401 - registers Seeed robot configs
from lerobot.robots import make_robot_from_config
from lerobot_robot_seeed_b601 import SeeedB601DMFollowerConfig


KEY_BINDINGS = {
    "1": ("shoulder_pan.pos", -1),
    "q": ("shoulder_pan.pos", 1),
    "2": ("shoulder_lift.pos", -1),
    "w": ("shoulder_lift.pos", 1),
    "3": ("elbow_flex.pos", -1),
    "e": ("elbow_flex.pos", 1),
    "4": ("wrist_flex.pos", -1),
    "r": ("wrist_flex.pos", 1),
    "5": ("wrist_yaw.pos", -1),
    "t": ("wrist_yaw.pos", 1),
    "6": ("wrist_roll.pos", -1),
    "y": ("wrist_roll.pos", 1),
    "7": ("gripper.pos", -1),
    "u": ("gripper.pos", 1),
}


def read_key(timeout_s: float = 0.1) -> str | None:
    ready, _, _ = select.select([sys.stdin], [], [], timeout_s)
    if not ready:
        return None
    return sys.stdin.read(1)


def build_config(args: argparse.Namespace) -> SeeedB601DMFollowerConfig:
    kwargs = {
        "port": args.port,
        "can_adapter": args.can_adapter,
        "dm_serial_baud": args.baud,
        "id": args.robot_id,
        "max_relative_target": args.max_relative_target,
        "disable_torque_on_disconnect": True,
    }
    valid_fields = {field.name for field in fields(SeeedB601DMFollowerConfig)}
    return SeeedB601DMFollowerConfig(**{k: v for k, v in kwargs.items() if k in valid_fields})


def print_help(step_deg: float) -> None:
    print(
        f"""
Keyboard jog ready. Step = {step_deg:.2f} deg

Keys:
  1/q  shoulder_pan   -/+
  2/w  shoulder_lift  -/+
  3/e  elbow_flex     -/+
  4/r  wrist_flex     -/+
  5/t  wrist_yaw      -/+
  6/y  wrist_roll     -/+
  7/u  gripper        -/+

  h    show this help
  s    print current joint positions
  x    quit safely

Keep one hand near power. Press x or Ctrl+C to stop.
"""
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", default="/dev/ttyACM0")
    parser.add_argument("--can-adapter", default="damiao")
    parser.add_argument("--baud", type=int, default=921600)
    parser.add_argument("--robot-id", default="follower1")
    parser.add_argument("--step-deg", type=float, default=1.0)
    parser.add_argument("--max-relative-target", type=float, default=2.0)
    args = parser.parse_args()

    cfg = build_config(args)
    robot = make_robot_from_config(cfg)

    old_settings = termios.tcgetattr(sys.stdin)
    try:
        print("Connecting robot...")
        robot.connect()
        obs = robot.get_observation()
        target = {key: obs[key] for key in robot.action_features if key in obs}
        print_help(args.step_deg)

        tty.setcbreak(sys.stdin.fileno())
        while True:
            key = read_key()
            if key is None:
                continue
            if key == "x":
                print("\nStopping...")
                break
            if key == "h":
                print_help(args.step_deg)
                continue
            if key == "s":
                obs = robot.get_observation()
                for name in sorted(robot.action_features):
                    print(f"{name}: {obs.get(name, 0.0):8.2f}")
                continue
            if key not in KEY_BINDINGS:
                continue

            action_key, direction = KEY_BINDINGS[key]
            target[action_key] = target.get(action_key, 0.0) + direction * args.step_deg
            sent = robot.send_action(target)
            print(f"{action_key} -> {sent.get(action_key, target[action_key]):.2f} deg")
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        try:
            robot.disconnect()
        except Exception:
            pass
        print("Disconnected.")


if __name__ == "__main__":
    main()
