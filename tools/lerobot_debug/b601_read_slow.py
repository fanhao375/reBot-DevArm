import math
import time

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


def main() -> None:
    print("connect dm serial /dev/ttyACM0 921600")
    bus = Controller.from_dm_serial("/dev/ttyACM0", 921600)
    motors = {}
    try:
        for name, (send_id, recv_id, model) in MOTORS.items():
            motor = bus.add_damiao_motor(send_id, recv_id, model)
            try:
                motor.set_can_timeout_ms(1000)
            except Exception as exc:
                print(f"{name} set timeout warning: {exc}")
            motors[name] = motor
            print("added", name, send_id, recv_id, model)

        for round_idx in range(3):
            print(f"round {round_idx + 1}")
            for name, motor in motors.items():
                try:
                    motor.request_feedback()
                    time.sleep(0.03)
                    for _ in range(3):
                        bus.poll_feedback_once()
                        time.sleep(0.01)
                except Exception as exc:
                    print(f"  {name}: ERROR {exc}")
                    continue

                state = motor.get_state()
                if state is None:
                    print(f"  {name}: NO_STATE")
                else:
                    print(
                        f"  {name}: pos_deg={math.degrees(state.pos):.2f} "
                        f"vel_deg={math.degrees(state.vel):.2f} torq={state.torq:.3f} "
                        f"status={state.status_code}"
                    )
            time.sleep(0.2)
    finally:
        print("close")
        for motor in motors.values():
            try:
                motor.close()
            except Exception as exc:
                print("motor close err", exc)
        try:
            bus.close()
        except Exception as exc:
            print("bus close err", exc)


if __name__ == "__main__":
    main()
