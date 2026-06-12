import time

from lerobot_robot_seeed_b601 import SeeedB601DMFollower, SeeedB601DMFollowerConfig


def main() -> None:
    follower = SeeedB601DMFollower(
        SeeedB601DMFollowerConfig(
            id="follower1",
            port="/dev/ttyACM0",
            can_adapter="damiao",
            dm_serial_baud=921600,
            cameras={},
            disable_torque_on_disconnect=True,
        )
    )
    follower.connect(calibrate=False)
    try:
        for round_idx in range(3):
            print(f"round {round_idx + 1}")
            obs = follower.get_observation()
            for joint in follower.motor_names:
                print(f"  {joint}: {obs[f'{joint}.pos']:.2f}")
            time.sleep(0.2)
    finally:
        follower.disconnect()


if __name__ == "__main__":
    main()
