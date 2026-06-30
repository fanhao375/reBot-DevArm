#!/usr/bin/env python3
# 网页"看数据站"调用：读 LeRobot 数据集(v3.0)的 parquet，按 episode 算主臂(action)/从臂(observation.state)
# 的幅度(max-min)判有效/废条；并从 meta/episodes 取每条每路相机的视频定位(chunk/file/起止时间)。
# [Added by fanhao375 2026-06-30 · v3.0 视频定位 by 2026-06-30 审核修复]
#   用法: python3 dataset_quality.py <数据集目录>
#   输出: 一行 JSON {"ok":true,"episodes":[{episode,frames,leaderAmp,followerAmp,verdict,reason,
#                    videos:{top:{chunk,file,from,to}, wrist:{...}}}, ...]}
#   质检判废: 主臂≈0=空条(没动102) / 主臂动从臂没动=601没跟 / 幅度<30°=判废（搬自小白教程"录完验收"）
#   v3.0 关键: 一条 episode 不是一个 mp4，多条拼进 videos/<vid_key>/chunk-NNN/file-NNN.mp4，
#              靠 meta/episodes 的 videos/<vid_key>/{chunk_index,file_index,from_timestamp,to_timestamp} 定位+截段。
import sys, os, glob, json, re


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

    data_files = sorted(glob.glob(os.path.join(D, "data", "**", "*.parquet"), recursive=True))
    if not data_files:
        print(json.dumps({"ok": False, "error": "没找到 parquet（%s/data/**）。该路径不是 LeRobot 数据集？" % D}))
        return

    # ---- 视频定位：读 meta/episodes，发现相机 vid_key（videos/<vk>/chunk_index 列）----
    vid_meta = None
    cam_keys = []  # [(short, vid_key)]  short 给前端用，如 top/wrist
    try:
        meta_files = sorted(glob.glob(os.path.join(D, "meta", "episodes", "**", "*.parquet"), recursive=True))
        if meta_files:
            vid_meta = pd.concat([pd.read_parquet(f) for f in meta_files], ignore_index=True)
            for col in vid_meta.columns:
                m = re.match(r"videos/(.+)/chunk_index$", col)
                if m:
                    vk = m.group(1)
                    short = vk.split(".")[-1]
                    cam_keys.append((short, vk))
    except Exception:
        vid_meta = None  # 无 meta 也能出质检，只是没视频定位

    def vids_for(ep):
        out = {}
        if vid_meta is None or not cam_keys:
            return out
        try:
            row = vid_meta[vid_meta["episode_index"] == ep]
            if not len(row):
                return out
            r = row.iloc[0]
            for short, vk in cam_keys:
                ci = r.get("videos/%s/chunk_index" % vk)
                fi = r.get("videos/%s/file_index" % vk)
                ft = r.get("videos/%s/from_timestamp" % vk)
                tt = r.get("videos/%s/to_timestamp" % vk)
                if ci is None or fi is None or (isinstance(ci, float) and ci != ci):
                    continue
                out[short] = {
                    "chunk": int(ci), "file": int(fi),
                    "from": round(float(ft), 3) if ft is not None and ft == ft else 0.0,
                    "to": round(float(tt), 3) if tt is not None and tt == tt else 0.0,
                }
        except Exception:
            return out
        return out

    # ---- 质检：只读需要的列省内存 ----
    try:
        cols = ["episode_index", "action", "observation.state"]
        df = pd.concat([pd.read_parquet(f, columns=cols) for f in data_files], ignore_index=True)
    except Exception as e:
        print(json.dumps({"ok": False, "error": "读 parquet 失败（缺 episode_index/action/observation.state 列？）: %s" % e}))
        return

    eps = []
    for ep in sorted(df["episode_index"].unique()):
        try:
            s = df[df["episode_index"] == ep]
            act = np.stack(s["action"].values)
            st = np.stack(s["observation.state"].values)
            a = float((act.max(0) - act.min(0)).max())
            sm = float((st.max(0) - st.min(0)).max())
            ok = a > 30 and sm > 30
            reason = ""
            if a <= 30:
                reason = "主臂≈0°，空条（当时没动 102）"
            elif sm <= 30:
                reason = "主臂动了、从臂没跟（601 当时没跟上）"
            elif not ok:
                reason = "幅度偏小"
            eps.append({
                "episode": int(ep), "frames": int(len(s)),
                "leaderAmp": round(a, 1), "followerAmp": round(sm, 1),
                "verdict": "ok" if ok else "bad", "reason": reason,
                "videos": vids_for(int(ep)),
            })
        except Exception as e:
            # 一条脏数据不拖垮整份报告：标 bad 继续
            eps.append({
                "episode": int(ep), "frames": 0, "leaderAmp": 0, "followerAmp": 0,
                "verdict": "bad", "reason": "该条解析失败: %s" % str(e)[:120], "videos": vids_for(int(ep)),
            })

    print(json.dumps({"ok": True, "count": len(eps), "episodes": eps}))


if __name__ == "__main__":
    main()
