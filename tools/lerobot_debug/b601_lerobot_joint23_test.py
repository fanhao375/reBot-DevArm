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


def make_action(**overrides: float) -> dict[str, float]:
    action = {f"{joint}.pos": 0.0 for joint in JOINTS}
    for joint, value in overrides.items():
        action[f"{joint}.pos"] = value
    return action


def print_obs(label: str, follower: SeeedB601DMFollower) -> None:
    obs = follower.get_observation()
    print(label)
    for joint in ("shoulder_lift", "elbow_flex"):
        print(f"  {joint}: {obs[f'{joint}.pos']:.2f}")


def send_and_read(label: str, follower: SeeedB601DMFollower, action: dict[str, float]) -> None:
    print(label)
    sent = follower.send_action(action)
    for joint in ("shoulder_lift", "elbow_flex"):
        print(f"  sent {joint}: {sent[f'{joint}.pos']:.2f}")
    time.sleep(1.2)
    print_obs("  feedback", follower)


def main() -> None:
    follower = SeeedB601DMFollower(
        SeeedB601DMFollowerConfig(
            id="follower1",
            port="/dev/ttyACM0",
            can_adapter="damiao",
            dm_serial_baud=921600,
            cameras={},
            max_relative_target=10.0,
            disable_torque_on_disconnect=True,
        )
    )

    follower.connect(calibrate=False)
    try:
        print_obs("before", follower)
        send_and_read("send shoulder_lift +5", follower, make_action(shoulder_lift=5.0))
        send_and_read("return zero", follower, make_action())
        send_and_read("send elbow_flex -5", follower, make_action(elbow_flex=-5.0))
        send_and_read("return zero", follower, make_action())
    finally:
        follower.disconnect()


if __name__ == "__main__":
    main()
