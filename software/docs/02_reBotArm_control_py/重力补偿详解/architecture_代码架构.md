# 重力补偿代码架构

<div style="font-family: 'Segoe UI', system-ui, sans-serif; max-width: 900px; margin: 0 auto; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px; border-radius: 16px;">
<style scoped>
.arch-layer { margin-bottom: 20px; border-radius: 12px; padding: 20px; background: rgba(255, 255, 255, 0.95); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); }
.arch-layer-title { font-size: 18px; font-weight: bold; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 3px solid; }
.arch-grid { display: grid; gap: 12px; }
.arch-grid-2 { grid-template-columns: repeat(2, 1fr); }
.arch-box { padding: 15px; border-radius: 8px; background: rgba(255, 255, 255, 0.9); border: 2px solid; font-size: 14px; line-height: 1.6; }
.arch-box small { display: block; margin-top: 8px; font-size: 12px; opacity: 0.8; }
.layer-example .arch-layer-title { color: #4A90E2; border-color: #4A90E2; }
.layer-example .arch-box { border-color: #4A90E2; background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); }
.layer-api .arch-layer-title { color: #7B68EE; border-color: #7B68EE; }
.layer-api .arch-box { border-color: #7B68EE; background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%); }
.layer-algo .arch-layer-title { color: #50C878; border-color: #50C878; }
.layer-algo .arch-box { border-color: #50C878; background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); }
.layer-pinocchio .arch-layer-title { color: #FF6B6B; border-color: #FF6B6B; }
.layer-pinocchio .arch-box { border-color: #FF6B6B; background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%); }
</style>
<div class="arch-layer layer-example">
<div class="arch-layer-title">🎯 业务层 (Example)</div>
<div class="arch-grid arch-grid-2">
<div class="arch-box">
<strong>9_gravity_compensation.py</strong>
<small>500Hz 控制循环<br>读 q → 算 g(q) → MIT 控制</small>
</div>
<div class="arch-box">
<strong>10_gravity_compensation_lock.py</strong>
<small>末端速度锁止版<br>+ 雅可比 + 积分项</small>
</div>
</div>
</div>
<div class="arch-layer layer-api">
<div class="arch-layer-title">📦 封装层 (Dynamics API)</div>
<div class="arch-grid arch-grid-2">
<div class="arch-box">
<strong>dynamics/__init__.py</strong>
<small>统一导出接口<br>compute_generalized_gravity</small>
</div>
<div class="arch-box">
<strong>dynamics/robot_model.py</strong>
<small>加载 URDF<br>设置重力 (0,0,-9.81)</small>
</div>
</div>
</div>
<div class="arch-layer layer-algo">
<div class="arch-layer-title">⚙️ 计算层 (Algorithms)</div>
<div class="arch-grid arch-grid-2">
<div class="arch-box">
<strong>inverse_dynamics.py</strong>
<small>逆动力学<br>τ = M·q̈ + C·q̇ + g(q)</small>
</div>
<div class="arch-box">
<strong>inertia.py</strong>
<small>M(q), C(q,q̇), g(q)<br>CRBA + RNEA</small>
</div>
</div>
</div>
<div class="arch-layer layer-pinocchio">
<div class="arch-layer-title">🔧 底层 (Pinocchio)</div>
<div class="arch-grid arch-grid-2">
<div class="arch-box">
<strong>pin.computeGeneralizedGravity</strong>
<small>RNEA 算法<br>O(n) 递归牛顿欧拉</small>
</div>
<div class="arch-box">
<strong>pin.crba / pin.rnea</strong>
<small>质量矩阵 / 完整逆动力学</small>
</div>
</div>
</div>
</div>
