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


def zero_action() -> dict[str, float]:
    return {f"{joint}.pos": 0.0 for joint in JOINTS}


def print_observation(label: str, follower: SeeedB601DMFollower) -> None:
    obs = follower.get_observation()
    print(label)
    for joint in JOINTS:
        print(f"  {joint}: {obs[f'{joint}.pos']:.2f}")


def main() -> None:
    follower = SeeedB601DMFollower(
        SeeedB601DMFollowerConfig(
            id="follower1",
            port="/dev/ttyACM0",
            can_adapter="damiao",
            dm_serial_baud=921600,
            cameras={},
            max_relative_target=5.0,
            disable_torque_on_disconnect=True,
        )
    )

    follower.connect(calibrate=False)
    try:
        print_observation("before", follower)

        action = zero_action()
        action["shoulder_pan.pos"] = 2.0
        print("send shoulder_pan.pos = 2.0 deg")
        sent = follower.send_action(action)
        for key in sorted(sent):
            print(f"  sent {key}: {sent[key]:.2f}")
        time.sleep(1.0)
        print_observation("after +2 deg", follower)

        print("send all joints back to 0.0 deg")
        sent = follower.send_action(zero_action())
        for key in sorted(sent):
            print(f"  sent {key}: {sent[key]:.2f}")
        time.sleep(1.0)
        print_observation("after return", follower)
    finally:
        follower.disconnect()


if __name__ == "__main__":
    main()
