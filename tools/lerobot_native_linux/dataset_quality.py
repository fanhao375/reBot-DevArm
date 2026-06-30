#!/usr/bin/env python3
# 网页"看数据站"调用：读 LeRobot 数据集的 parquet，按 episode 算主臂(action)/从臂(observation.state)
# 的幅度(max-min)，判有效/废条。逻辑搬自 LeRobot_模仿学习全流程_小白教程.md 的"录完验收"。
# [Added by fanhao375 2026-06-30]
#   用法: python3 dataset_quality.py <数据集目录>
#   输出: 一行 JSON {"ok":true,"episodes":[{episode,frames,leaderAmp,followerAmp,verdict,reason}, ...]}
#   判废: 主臂≈0=空条(没动102) / 主臂动从臂没动=601没跟 / 幅度<30°=判废
import sys, os, glob, json


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"ok": False, "error": "用法: dataset_quality.py <数据集目录>"}))
        return
    D = sys.argv[1]
    if not os.path.isdir(D):
        print(json.dumps({"ok": False, "error": "目录不存在: %s" % D}))
        return
    try:
        import pandas as pd
        import numpy as np
    except Exception as e:
        print(json.dumps({"ok": False, "error": "缺 pandas/numpy（请在 lerobot 环境跑本服务）: %s" % e}))
        return
    files = sorted(glob.glob(os.path.join(D, "data", "**", "*.parquet"), recursive=True))
    if not files:
        print(json.dumps({"ok": False, "error": "没找到 parquet（%s/data/**）。该路径不是 LeRobot 数据集？" % D}))
        return
    try:
        df = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
        if 'episode_index' not in df.columns or 'action' not in df.columns or 'observation.state' not in df.columns:
            print(json.dumps({"ok": False, "error": "parquet 缺 episode_index/action/observation.state 列"}))
            return
        eps = []
        for ep in sorted(df['episode_index'].unique()):
            s = df[df['episode_index'] == ep]
            act = np.stack(s['action'].values)
            st = np.stack(s['observation.state'].values)
            a = float((act.max(0) - act.min(0)).max())
            sm = float((st.max(0) - st.min(0)).max())
            ok = a > 30 and sm > 30
            reason = ''
            if a <= 30:
                reason = '主臂≈0°，空条（当时没动 102）'
            elif sm <= 30:
                reason = '主臂动了、从臂没跟（601 当时没跟上）'
            elif not ok:
                reason = '幅度偏小'
            eps.append({
                "episode": int(ep), "frames": int(len(s)),
                "leaderAmp": round(a, 1), "followerAmp": round(sm, 1),
                "verdict": "ok" if ok else "bad", "reason": reason
            })
        print(json.dumps({"ok": True, "count": len(eps), "episodes": eps}))
    except Exception as e:
        print(json.dumps({"ok": False, "error": "读取/分析失败: %s" % e}))


if __name__ == "__main__":
    main()
