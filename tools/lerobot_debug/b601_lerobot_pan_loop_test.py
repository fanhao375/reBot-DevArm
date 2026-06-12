import time

from lerobot_robot_seeed_b601 import SeeedB601DMFollower, SeeedB601DMFollowerConfig


JOINTS = [
    "shoulder_pan",
    "shoulder_lift",
    "elbow_flex",
    "wrist_flex",
    "wrist_yaw",
    "wrist_roll",
    "gripper",
]


def make_action(shoulder_pan: float) -> dict[str, float]:
    action = {f"{joint}.pos": 0.0 for joint in JOINTS}
    action["shoulder_pan.pos"] = shoulder_pan
    return action


def read_pan(follower: SeeedB601DMFollower) -> float:
    obs = follower.get_observation()
    return obs["shoulder_pan.pos"]


def main() -> None:
    follower = SeeedB601DMFollower(
        SeeedB601DMFollowerConfig(
            id="follower1",
            port="/dev/ttyACM0",
            can_adapter="damiao",
            dm_serial_baud=921600,
            cameras={},
            max_relative_target=15.0,
            disable_torque_on_disconnect=True,
        )
    )

    follower.connect(calibrate=False)
    try:
        print(f"start pan={read_pan(follower):.2f}")
        sequence = [10.0, -10.0, 10.0, -10.0, 10.0, -10.0, 0.0]
        for target in sequence:
            print(f"send shoulder_pan.pos={target:.1f}")
            sent = follower.send_action(make_action(target))
            print(f"  sent shoulder_pan.pos={sent['shoulder_pan.pos']:.2f}")
            time.sleep(1.2)
            print(f"  feedback pan={read_pan(follower):.2f}")
        print("done")
    finally:
        follower.disconnect()


if __name__ == "__main__":
    main()
