Write-Host "Starting Arm102 -> B601 direct follow in WSL. Press Ctrl+C to stop."

wsl -d Ubuntu-22.04 -- bash -lc @'
source ~/miniforge3/etc/profile.d/conda.sh
conda activate lerobot
cd ~/rebot_lerobot
python -u /mnt/d/Robot/reBot-DevArm/tools/lerobot_debug/arm102_to_b601_direct_follow.py --leader-port /dev/ttyUSB0 --follower-port /dev/ttyACM0 --fps 5 --invert-raw-joints shoulder_lift,elbow_flex
'@

Write-Host ""
Write-Host "Teleoperation command exited. Press Enter to close this window."
Read-Host
