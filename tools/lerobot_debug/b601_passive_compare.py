import math
import time

from lerobot_teleoperator_rebot_arm_102 import RebotArm102Leader, RebotArm102LeaderConfig
from motorbridge import Controller


MOTORS = {
    "shoulder_pan": (1, 17, "4340P"),
    "shoulder_lift": (2, 18, "4340P"),
    "elbow_flex": (3, 19, "4340P"),
    "wrist_flex": (4, 20, "4310"),
    "wrist_yaw": (5, 21, "4310"),
    "wrist_roll": (6, 22, "4310"),
    "gripper": (7, 23, "4310"),
}

JOINT_DIRECTIONS = {
    "shoulder_pan": -1.0,
    "shoulder_lift": -1.0,
    "elbow_flex": 1.0,
    "wrist_flex": 1.0,
    "wrist_yaw": 1.0,
    "wrist_roll": -1.0,
    "gripper": -6.0,
}


def read_leader_with_retry(leader: RebotArm102Leader, attempts: int = 20, delay_s: float = 0.1) -> dict[str, float]:
    last_error: Exception | None = None
    for _ in range(attempts):
        try:
            return leader._read_raw_positions()
        except RuntimeError as exc:
            last_error = exc
            time.sleep(delay_s)
    raise RuntimeError(f"Leader did not return all joints after {attempts} attempts: {last_error}")


def raw_to_action(leader: RebotArm102Leader, raw_positions: dict[str, float]) -> dict[str, float]:
    action: dict[str, float] = {}
    for joint in leader.motor_names:
        range_min, range_max = leader.config.joint_ranges[joint]
        unwrapped, _ = leader._round_to_valid_range(raw_positions[joint], float(range_min), float(range_max))
        action[f"{joint}.pos"] = leader._clamp(unwrapped, float(range_min), float(range_max))
    return action


def read_b601_positions(rounds: int = 8) -> dict[str, float]:
    bus = Controller.from_dm_serial("/dev/ttyACM0", 921600)
    motors = {}
    positions: dict[str, float] = {}
    try:
        for name, (send_id, recv_id, model) in MOTORS.items():
            motors[name] = bus.add_damiao_motor(send_id, recv_id, model)

        for _ in range(rounds):
            for motor in motors.values():
                try:
                    motor.request_feedback()
                except Exception as exc:
                    print(f"request_feedback warning: {exc}")

            for _ in range(3):
                try:
                    bus.poll_feedback_once()
                except Exception as exc:
                    print(f"poll warning: {exc}")
                time.sleep(0.01)

            for name, motor in motors.items():
                state = motor.get_state()
                if state is not None:
                    positions[name] = math.degrees(state.pos)

            if set(positions) == set(MOTORS):
                break
            time.sleep(0.05)

        return positions
    finally:
        for motor in motors.values():
            try:
                motor.close()
            except Exception as exc:
                print(f"motor close warning: {exc}")
        try:
            bus.close()
        except Exception as exc:
            print(f"bus close warning: {exc}")


def main() -> None:
    leader = RebotArm102Leader(
        RebotArm102LeaderConfig(
            id="rebot_arm_102_leader",
            port="/dev/ttyUSB0",
            baudrate=1000000,
        )
    )

    leader.connect(calibrate=False)
    try:
        raw_positions = read_leader_with_retry(leader)
        leader_action = raw_to_action(leader, raw_positions)
    finally:
        leader.disconnect()

    follower_positions = read_b601_positions()

    print(f"{'joint':<16} {'leader':>8} {'f.dir':>6} {'mapped':>8} {'follower':>9} {'delta':>8}")
    print(f"{'-' * 16} {'-' * 8} {'-' * 6} {'-' * 8} {'-' * 9} {'-' * 8}")
    for joint in MOTORS:
        leader_pos = leader_action[f"{joint}.pos"]
        follower_direction = JOINT_DIRECTIONS[joint]
        mapped = leader_pos * follower_direction
        follower_pos = follower_positions.get(joint)
        if follower_pos is None:
            print(f"{joint:<16} {leader_pos:8.2f} {follower_direction:6.1f} {mapped:8.2f} {'NO_STATE':>9} {'':>8}")
        else:
            delta = follower_pos - mapped
            print(
                f"{joint:<16} {leader_pos:8.2f} {follower_direction:6.1f} "
                f"{mapped:8.2f} {follower_pos:9.2f} {delta:8.2f}"
            )


if __name__ == "__main__":
    main()
