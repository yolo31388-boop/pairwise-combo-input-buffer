"""连招输入缓冲的纯函数契约。

设计要点（对应 README 中的问题清单）：

* 缓冲保存多帧按键队列，避免只留最后一帧导致连打丢输入；
* 有效期以时间（秒/毫秒均可，只要单位一致）计算，不受帧率波动影响；
* 动画事件按时间采样，低帧率下跨越多个事件时仍能取到应在当前时刻生效的那个；
* 同一帧内的输入按到达时间戳稳定排序，搓招顺序不再随机；
* 分支表按姿态（浮空/地面）分表，互不覆盖；
* 服务器权威窗口用本地时间减去延迟回退，客户端不提前进入下一段；
* 摇杆加死区，抖动不再被当成方向输入；
* UI 获得焦点时不吞战斗输入；
* 输入优先级显式定义，同时按下时结果确定；
* 连招失败回退到待机，不留收招僵直。
"""


def buffer_push(queue, item, maxlen):
    """把一次按键压入多帧输入队列，返回新的定长队列。

    只保留最近的 ``maxlen`` 个输入，超出的旧输入被丢弃。
    不修改传入的 ``queue``，便于在回滚/重放时保留历史快照。
    """
    if maxlen <= 0:
        return []
    buffered = list(queue) + [item]
    return buffered[-maxlen:]


def buffer_expire(timestamp, now, window):
    """判断一条缓冲输入在 ``now`` 时刻是否仍然有效。

    有效期为时间窗口而非帧数，因此高帧率下不会提前过期。
    """
    elapsed = now - timestamp
    return bool(0 <= elapsed <= window)


def event_sample(events, t):
    """按时间采样动画事件：返回 ``t`` 时刻应生效的最后一个事件值。

    事件形如 ``(time, value)``，允许乱序传入，内部按时间稳定排序。
    若 ``t`` 之前没有事件则返回 ``None``。
    """
    active = None
    for event_time, value in sorted(events, key=lambda e: e[0]):
        if event_time > t:
            break
        active = value
    return active


def sort_inputs(inputs):
    """对同一帧内到达的输入按时间戳稳定排序。

    相同时间戳保持原始到达顺序，搓招判定因此可复现。
    """
    return sorted(inputs, key=lambda item: item[0])


def stance_table(stance, tables):
    """按姿态（如 ``"air"`` / ``"ground"``）取独立的分支表。

    浮空与地面不再共用一张表互相覆盖；未知姿态返回 ``None``。
    """
    return tables.get(stance)


def server_window(local_time, lag):
    """服务器权威窗口：把本地时间按延迟回退到服务器已确认的时刻。

    客户端只能在 ``local_time - lag`` 之前的状态上继续连招，
    避免在服务器仍处于上一段硬直时提前进入下一段。
    """
    return local_time - lag


def deadzone(value, threshold):
    """摇杆死区：幅度小于阈值视为 0，避免抖动被当成方向输入。"""
    return 0.0 if abs(value) < threshold else value


def should_pass(focused):
    """UI 焦点判定：返回输入是否应交给 UI 的默认处理路径。

    UI 获得焦点时返回 ``False``，战斗输入由路由层直接送到 gameplay，
    不会被 UI 吞掉，玩家不会觉得“掉输入”。
    """
    return not focused


def priority(a, b):
    """显式输入优先级：数值大者优先，同时按下时结果确定。"""
    return a if a >= b else b


def fallback(state, valid):
    """连招失败回退：当前段不合法时回到待机，避免卡在收招姿势。"""
    return state if valid else "idle"


def combo_step(index, length):
    """连招推进到下一段；到达末尾后回绕到第一段。"""
    if length <= 0:
        return 0
    return (index + 1) % length


def combo_id(seed, index):
    """生成连招段的稳定 id，用于分支表索引与网络同步。"""
    return f"{seed}:{index}"


def input_key(time, key):
    """把一次输入编码成 ``时间:按键`` 的稳定键，便于去重与回放。"""
    return f"{time}:{key}"


def combo_window(start, end, t):
    """判断 ``t`` 是否落在连招/取消窗口 ``[start, end]`` 内。"""
    return bool(start <= t <= end)


def chain_length(states):
    """连招链长度。"""
    return len(states)
