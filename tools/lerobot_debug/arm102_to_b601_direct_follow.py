import argparse
import time

from lerobot_robot_seeed_b601 import SeeedB601DMFollower, SeeedB601DMFollowerConfig
from lerobot_teleoperator_rebot_arm_102 import RebotArm102Leader, RebotArm102LeaderConfig


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Direct Arm102 -> B601 teleop test. This intentionally skips the "
            "per-frame B601 get_observation() call used by lerobot-teleoperate."
        )
    )
    parser.add_argument("--leader-port", default="/dev/ttyUSB0")
    parser.add_argument("--follower-port", default="/dev/ttyACM0")
    parser.add_argument("--fps", type=float, default=8.0)
    parser.add_argument("--duration", type=float, default=None)
    parser.add_argument("--print-every", type=float, default=1.0)
    parser.add_argument("--leader-id", default="rebot_arm_102_leader")
    parser.add_argument("--follower-id", default="follower1")
    return parser.parse_args()


def format_action(action: dict[str, float]) -> str:
    joints = [
        "shoulder_pan",
        "shoulder_lift",
        "elbow_flex",
        "wrist_flex",
        "wrist_yaw",
        "wrist_roll",
        "gripper",
    ]
    return "  ".join(f"{joint}={action.get(f'{joint}.pos', 0.0):7.2f}" for joint in joints)


def main() -> None:
    args = parse_args()

    if args.fps <= 0:
        raise ValueError("--fps must be greater than 0")

    leader = RebotArm102Leader(
        RebotArm102LeaderConfig(
            id=args.leader_id,
            port=args.leader_port,
            baudrate=1_000_000,
        )
    )
    follower = SeeedB601DMFollower(
        SeeedB601DMFollowerConfig(
            id=args.follower_id,
            port=args.follower_port,
            can_adapter="damiao",
            dm_serial_baud=921600,
            cameras={},
            max_relative_target=None,
            disable_torque_on_disconnect=True,
        )
    )

    period_s = 1.0 / args.fps
    start_s = time.perf_counter()
    next_print_s = start_s
    count = 0

    print("Direct Arm102 -> B601 follow test.")
    print("This skips B601 feedback reads inside the control loop.")
    print("Press Ctrl+C to stop.")

    leader.connect(calibrate=False)
    try:
        follower.connect(calibrate=False)
        try:
            while True:
                loop_start_s = time.perf_counter()
                action = leader.get_action()
                follower.send_action(action)
                count += 1

                now_s = time.perf_counter()
                if now_s >= next_print_s:
                    loop_ms = (now_s - loop_start_s) * 1000.0
                    print(f"loop={loop_ms:7.2f}ms  {format_action(action)}")
                    next_print_s = now_s + args.print_every

                if args.duration is not None and now_s - start_s >= args.duration:
                    break

                sleep_s = period_s - (time.perf_counter() - loop_start_s)
                if sleep_s > 0:
                    time.sleep(sleep_s)
        finally:
            follower.disconnect()
    finally:
        leader.disconnect()

    elapsed_s = max(time.perf_counter() - start_s, 1e-9)
    print(f"Stopped. Sent {count} frames in {elapsed_s:.1f}s ({count / elapsed_s:.1f} Hz).")


if __name__ == "__main__":
    main()
