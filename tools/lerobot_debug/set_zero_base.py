"""只对 B601 从臂底座 (shoulder_pan, id 0x01/0x11) 操作的设零小工具。

全程不 enable_all（不上电保持），避免连接时底座先跳。

用法：
  python set_zero_base.py disable    # 松力 + 读当前底座角度（用来确认是松的、现在在哪）
  python set_zero_base.py setzero    # 松力 + 把当前底座物理位置设为新的零点 + 读结果
"""
import math
import sys
import time

from motorbridge import Controller as MotorBridgeController

PORT = "/dev/ttyACM0"
BAUD = 921600
BASE_SEND_ID = 0x01
BASE_RECV_ID = 0x11
BASE_MODEL = "4340P"


def read_base_deg(bus, motor) -> float | None:
    """请求一次反馈并读取底座电机角度（度）。"""
    for _ in range(3):
        try:
            motor.request_feedback()
        except Exception as exc:
            print("request_feedback 失败:", exc)
        time.sleep(0.02)
        for _ in range(5):
            try:
                bus.poll_feedback_once()
            except Exception as exc:
                print("poll_feedback_once 失败:", exc)
            time.sleep(0.01)
        state = motor.get_state()
        if state is not None:
            return math.degrees(state.pos)
    return None


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "disable"
    if mode not in ("disable", "setzero"):
        raise SystemExit(f"未知模式 {mode!r}，应为 disable 或 setzero")

    bus = MotorBridgeController.from_dm_serial(serial_port=PORT, baud=BAUD)
    motor = bus.add_damiao_motor(BASE_SEND_ID, BASE_RECV_ID, BASE_MODEL)

    # 关键：只松力，绝不 enable，保持底座可手动摆动 / 不跳
    bus.disable_all()
    time.sleep(0.1)

    before = read_base_deg(bus, motor)
    print(f"[底座] 当前电机角度（设零前） = {before}")

    if mode == "setzero":
        motor.set_zero_position()
        time.sleep(0.3)
        after = read_base_deg(bus, motor)
        print(f"[底座] 设零完成，当前电机角度（设零后） = {after}  (应接近 0)")

    # 再次确保松力后退出
    bus.disable_all()
    print("done")


if __name__ == "__main__":
    main()
