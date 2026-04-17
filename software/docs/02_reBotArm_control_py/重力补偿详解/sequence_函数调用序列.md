# 重力补偿函数调用序列图

展示从用户代码到 Pinocchio 底层的完整函数调用链。

```mermaid
sequenceDiagram
    autonumber
    actor User as 用户代码
    participant Example as 9_gravity_compensation.py<br/>(控制循环)
    participant API as dynamics/__init__.py<br/>(API 封装)
    participant InvDyn as inverse_dynamics.py<br/>(逆动力学)
    participant Pin as Pinocchio<br/>(底层库)

    User->>Example: 启动程序
    activate Example

    Note over Example: 初始化阶段
    Example->>Example: load_dynamics_model()
    Example->>Example: arm.connect()
    Example->>Example: arm.enable()
    Example->>Example: start_control_loop(500Hz)

    loop 每 2ms (500Hz)
        Example->>Example: q = arm.get_positions()
        Note right of Example: 读取 6 个关节角度

        Example->>API: compute_generalized_gravity(q)
        activate API

        API->>InvDyn: compute_generalized_gravity(model, q, data)
        activate InvDyn

        InvDyn->>Pin: pin.computeGeneralizedGravity(model, data, q)
        activate Pin
        Note right of Pin: RNEA 算法<br/>O(n) 递归牛顿欧拉
        Pin-->>InvDyn: data.g (重力向量)
        deactivate Pin

        InvDyn-->>API: tau_g (6 个力矩值)
        deactivate InvDyn

        API-->>Example: tau_g
        deactivate API

        Example->>Example: arm.mit(pos=q, vel=0,<br/>kp=2, kd=1, tau=tau_g)
        Note right of Example: MIT 模式控制<br/>前馈重力力矩

        Example->>Example: print(tau_g) 每 20 周期
    end

    User->>Example: Ctrl+C
    Example->>Example: arm.disconnect()
    deactivate Example
```

## 关键调用链

1. **用户代码** → 启动 `9_gravity_compensation.py`
2. **控制循环** (500Hz) → 每 2ms 执行一次
3. **读取关节位置** → `arm.get_positions()` 获取 q
4. **计算重力补偿** → `compute_generalized_gravity(q)`
   - 经过 `dynamics/__init__.py` 封装层
   - 调用 `inverse_dynamics.py` 计算层
   - 最终调用 Pinocchio 的 `pin.computeGeneralizedGravity()`
5. **MIT 控制** → 前馈重力力矩 `tau_g`
6. **循环** → 直到用户按 Ctrl+C

## 性能特点

- **RNEA 算法**：O(n) 时间复杂度，n=6（关节数）
- **500Hz 控制频率**：每 2ms 执行一次，实时性强
- **零拷贝优化**：`data.g.copy()` 避免数据竞争

## 调用层次图（简化）

```mermaid
flowchart LR
    A[用户代码<br/>example/9_*.py] --> B[API 封装层<br/>dynamics/__init__.py]
    B --> C[计算层<br/>inverse_dynamics.py]
    C --> D[Pinocchio<br/>RNEA 算法]
    D -.返回 tau_g.-> C
    C -.返回 tau_g.-> B
    B -.返回 tau_g.-> A

    classDef userStyle fill:#E3F2FD,stroke:#1976D2,stroke-width:2px,color:#000
    classDef apiStyle fill:#FFF9C4,stroke:#F9A825,stroke-width:2px,color:#000
    classDef calcStyle fill:#FFCDD2,stroke:#C62828,stroke-width:2px,color:#000
    classDef libStyle fill:#C8E6C9,stroke:#2E7D32,stroke-width:2px,color:#000

    class A userStyle
    class B apiStyle
    class C calcStyle
    class D libStyle
```

> 提示：mermaid 图在 VS Code（已安装 `bierner.markdown-mermaid` 插件）、GitHub、Typora 中都能直接渲染，无需额外配置。
