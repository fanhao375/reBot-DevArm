import argparse
import math
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
    parser.add_argument(
        "--invert-raw-joints",
        default="",
        help=(
            "Comma-separated joints to invert before applying leader joint range clipping. "
            "Use shoulder_lift,elbow_flex if Arm102 joint 2/3 move opposite to Seeed defaults."
        ),
    )
    parser.add_argument(
        "--send-joints",
        default="",
        help="Optional comma-separated joints to send. Empty means send all joints.",
    )
    return parser.parse_args()


JOINTS = [
    "shoulder_pan",
    "shoulder_lift",
    "elbow_flex",
    "wrist_flex",
    "wrist_yaw",
    "wrist_roll",
    "gripper",
]


def parse_joint_set(value: str) -> set[str]:
    joints = {item.strip() for item in value.split(",") if item.strip()}
    unknown = joints - set(JOINTS)
    if unknown:
        raise ValueError(f"Unknown joint(s): {', '.join(sorted(unknown))}")
    return joints


def format_action(action: dict[str, float], joints: list[str] = JOINTS) -> str:
    return "  ".join(f"{joint}={action.get(f'{joint}.pos', 0.0):7.2f}" for joint in joints)


def get_action_from_raw(
    leader: RebotArm102Leader,
    invert_raw_joints: set[str],
    send_joints: set[str],
) -> tuple[dict[str, float], dict[str, float]]:
    """Read raw Arm102 angles and optionally invert selected joints before clipping.

    RebotArm102Leader.get_action() clips to the official Seeed joint ranges. If a
    physically installed joint reports the opposite sign, it can get clipped to
    -1/0/+1 before the follower ever sees a useful target. This path flips the
    raw angle first, then clips.
    """
    raw_positions = leader._read_raw_positions()
    leader._last_raw_positions = raw_positions
    action: dict[str, float] = {}

    for joint in leader.motor_names:
        if send_joints and joint not in send_joints:
            continue

        range_min, range_max = leader.config.joint_ranges[joint]
        position, _ = leader._round_to_valid_range(
            raw_positions[joint],
            float(range_min),
            float(range_max),
        )
        if joint in invert_raw_joints:
            position = -position
        action[f"{joint}.pos"] = leader._clamp(position, float(range_min), float(range_max))

    return action, raw_positions


def subset_action(action: dict[str, float], send_joints: set[str]) -> dict[str, float]:
    if not send_joints:
        return action
    return {key: value for key, value in action.items() if key.removesuffix(".pos") in send_joints}


def map_action_for_follower(
    follower: SeeedB601DMFollower,
    action: dict[str, float],
) -> dict[str, float]:
    targets: dict[str, float] = {}
    for key, value in action.items():
        if not key.endswith(".pos"):
            continue
        joint = key.removesuffix(".pos")
        position = value * follower.config.joint_directions.get(joint, 1.0)
        if joint in follower.config.joint_limits:
            min_limit, max_limit = follower.config.joint_limits[joint]
            position = max(min_limit, min(max_limit, position))
        targets[joint] = position
    return targets


def send_selected_action(
    follower: SeeedB601DMFollower,
    action: dict[str, float],
) -> dict[str, float]:
    """Send only the joints present in action.

    The official follower send_action() fills a missing wrist_yaw command with
    zero. That is convenient for some 6-DOF leaders, but noisy for per-joint
    debugging because it sends wrist_yaw even when we did not ask for it.
    """
    targets = map_action_for_follower(follower, action)
    for joint, position_degrees in targets.items():
        motor = follower.motors.get(joint)
        if motor is None:
            continue

        pos_rad = math.radians(position_degrees)
        if joint == "gripper":
            follower._try_serial_write(
                f"{joint} send_force_pos",
                lambda motor=motor, pos_rad=pos_rad: motor.send_force_pos(
                    pos_rad,
                    math.radians(32),
                    follower.config.force_pos_torque_ration,
                ),
            )
        else:
            follower._try_serial_write(
                f"{joint} send_pos_vel",
                lambda motor=motor, pos_rad=pos_rad: motor.send_pos_vel(pos_rad, 32),
            )
        time.sleep(0.03)
    return {f"{joint}.pos": value for joint, value in targets.items()}


def main() -> None:
    args = parse_args()

    if args.fps <= 0:
        raise ValueError("--fps must be greater than 0")

    invert_raw_joints = parse_joint_set(args.invert_raw_joints)
    send_joints = parse_joint_set(args.send_joints)
    print_joints = [joint for joint in JOINTS if not send_joints or joint in send_joints]

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
    if invert_raw_joints:
        print(f"Inverting raw leader joints before clipping: {', '.join(sorted(invert_raw_joints))}")
    if send_joints:
        print(f"Sending only joints: {', '.join(sorted(send_joints))}")
    print("Press Ctrl+C to stop.")

    leader.connect(calibrate=False)
    try:
        follower.connect(calibrate=False)
        try:
            try:
                while True:
                    loop_start_s = time.perf_counter()
                    if invert_raw_joints:
                        action, raw_positions = get_action_from_raw(leader, invert_raw_joints, send_joints)
                    else:
                        raw_positions = {}
                        action = subset_action(leader.get_action(), send_joints)
                    if send_joints:
                        sent = send_selected_action(follower, action)
                    else:
                        sent = follower.send_action(action)
                    count += 1

                    now_s = time.perf_counter()
                    if now_s >= next_print_s:
                        loop_ms = (now_s - loop_start_s) * 1000.0
                        parts = [
                            f"loop={loop_ms:7.2f}ms",
                            f"leader={format_action(action, print_joints)}",
                            f"follower_target={format_action(sent, print_joints)}",
                        ]
                        if raw_positions:
                            raw_subset = {f"{joint}.pos": raw_positions[joint] for joint in print_joints}
                            parts.append(f"raw={format_action(raw_subset, print_joints)}")
                        print("  ".join(parts))
                        next_print_s = now_s + args.print_every

                    if args.duration is not None and now_s - start_s >= args.duration:
                        break

                    sleep_s = period_s - (time.perf_counter() - loop_start_s)
                    if sleep_s > 0:
                        time.sleep(sleep_s)
            except KeyboardInterrupt:
                print("\nStopping...")
        finally:
            follower.disconnect()
    finally:
        leader.disconnect()

    elapsed_s = max(time.perf_counter() - start_s, 1e-9)
    print(f"Stopped. Sent {count} frames in {elapsed_s:.1f}s ({count / elapsed_s:.1f} Hz).")


if __name__ == "__main__":
    main()
