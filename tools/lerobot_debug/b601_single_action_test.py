import time

from lerobot_teleoperator_rebot_arm_102 import RebotArm102Leader, RebotArm102LeaderConfig
from lerobot_robot_seeed_b601 import SeeedB601DMFollower, SeeedB601DMFollowerConfig


def main() -> None:
    leader = RebotArm102Leader(
        RebotArm102LeaderConfig(
            id="rebot_arm_102_leader",
            port="/dev/ttyUSB0",
            baudrate=1000000,
        )
    )
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

    leader.connect(calibrate=False)
    follower.connect(calibrate=False)
    try:
        action = leader.get_action()
        print("leader action")
        for key in sorted(action):
            print(f"  {key}: {action[key]:.2f}")

        sent = follower.send_action(action)
        print("sent action")
        for key in sorted(sent):
            print(f"  {key}: {sent[key]:.2f}")

        time.sleep(0.5)
        obs = follower.get_observation()
        print("follower observation")
        for joint in follower.motor_names:
            print(f"  {joint}: {obs[f'{joint}.pos']:.2f}")
    finally:
        follower.disconnect()
        leader.disconnect()


if __name__ == "__main__":
    main()
