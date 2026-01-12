# Zinguo 浴霸 Home Assistant 集成
![Version](https://img.shields.io/badge/version-v1.0.0-blue)
![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)
## 项目简介

一个完整的 Zinguo 智能浴霸 Home Assistant 集成，通过用户友好界面和安全凭证存储，提供对浴霸的全面控制。

## ✨ 核心功能

### 🎛️ 完整设备控制

* ​**风扇实体**​：支持预设模式（关闭/吹风/暖风低档/暖风高档）
* ​**独立开关**​：灯光/换气/吹风/暖风1/暖风2 独立控制
* ​**温度传感器**​：实时温度监测（℃）
* ​**在线状态**​：设备连接状态实时显示
* ​**实体分组**​：自动创建设备实体组

### 🔒 安全与隐私

* 使用 Home Assistant 加密凭证存储
* 所有数据本地处理，无云端存储
* 直接与 Zinguo 官方 API 通信
* 自动令牌刷新，无手动操作
* 不收集任何用户使用数据

### 🚀 用户体验

* 图形化配置，无需编辑 YAML
* 智能错误处理（自动重试/网络恢复/错误提示）
* 多语言支持（含中文界面）
* 响应式设计（适配桌面/平板/手机）
* 控制指令秒级响应

### 🔄 智能功能

* 实时状态同步
* 场景记忆（记住用户偏好）
* 设备联动触发
* 可配置定时任务
* 远程控制

### 🛡️ 稳定性保证

* 自动保持设备连接
* 网络异常时自动重连
* 重启后自动恢复上次状态
* 兼容多种 Home Assistant 版本
* 支持无缝更新

## 📦 安装方法

### 方法一：HACS 安装（推荐）

1. 确保已安装 HACS（未安装请先访问 HACS 官网按教程安装）
2. 打开 Home Assistant 侧边栏 → 点击 HACS
3. 添加自定义仓库：
   
   * 点击「集成」→ 右上角 ⋮ 菜单 → 选择「自定义仓库」
   * 仓库：`https://github.com/jyz0501/hassio-zinguo`
   * 类别：集成
4. 搜索并安装：
   
   * 搜索框输入「Zinguo」→ 选择「Zinguo Bathroom Fan」
   * 点击「下载」→ 选择最新版本 → 点击「下载」
5. 重启 Home Assistant：设置 → 系统 → 重启
6. 验证：重启后检查是否出现「Zinguo Bathroom Fan」集成

### 方法二：Home Assistant 插件方式

1. 添加插件仓库：仓库地址 `https://github.com/jyz0501/hassio-zinguo`
2. 插件商店搜索「Zinguo Bathroom Fan」→ 点击安装
3. 启动插件并查看日志确保正常运行
4. 重启 Home Assistant

### 方法三：手动安装

1. 下载文件：
   
   ```bash
   # Git 克隆
   git clone https://github.com/jyz0501/hassio-zinguo.git
   
   # 或下载 ZIP
   # 访问 https://github.com/jyz0501/hassio-zinguo/releases 下载最新版 ZIP
   ```
2. 解压文件（ZIP 需先解压）
3. 复制文件：
   
   * 打开 Home Assistant 配置目录
   * 创建 `custom_components`文件夹（若不存在）
   * 将 `zinguo`文件夹复制到 `custom_components`
   * 目录结构示例：
     
     ```markdown
     config/
     └── custom_components/
         └── zinguo/
             ├── __init__.py
             ├── manifest.json
             ├── config_flow.py
             ├── const.py
             ├── switch.py
             ├── fan.py
             ├── sensor.py
             └── coordinator.py
     ```
4. 验证：重启 Home Assistant，检查日志无错误，确认集成出现在列表

## ⚙️ 配置步骤

### 第一步：添加集成

1. 进入 设置 → 设备与服务 → 点击右下角「添加集成」
2. 搜索框输入「Zinguo」→ 选择「Zinguo Bathroom Fan」
3. 点击集成名称开始配置

### 第二步：输入凭证信息

| 字段     | 说明                     | 示例           | 必填 |
| ---------- | -------------------------- | ---------------- | ------ |
| 账户     | 注册 Zinguo 应用的手机号 | 13800138000    | \*   |
| 密码     | Zinguo 账户密码          | your\_password | \*   |
| MAC 地址 | 浴霸设备 MAC 地址        | ABCDEF123456   | \*   |
| 名称     | 自定义设备名称           | 主卫浴霸       | \*   |

​**获取 MAC 地址**​：

打开 Zinguo 官方 App → 设备详情页 → 查看设备信息中的 MAC 地址（12位大写字母数字，无冒号/短横线）

​**注意事项**​：

* 账户密码会安全加密存储，不显示明文
* MAC 地址需完全匹配（含大小写）
* 设备名称将作为所有实体前缀

### 第三步：完成配置

1. 填写完信息后点击「提交」，系统验证账户和设备信息
2. 验证成功：显示配置成功，自动创建所有实体
3. 后续修改：点击集成「选项」可修改设备显示名称

## 🏠 创建的实体

### 风扇实体

* ​**实体ID**​：`fan.[设备名称]_fan`
* ​**名称**​：`[设备名称] Fan`
* ​**功能**​：主控制面板（含预设模式）
* ​**状态**​：开关状态、预设模式
* ​**属性**​：温度、在线状态等

### 开关实体

| 功能  | 实体ID                              | 名称                   | 图标           | 功能描述              |
| ------- | ------------------------------------- | ------------------------ | ---------------- | ----------------------- |
| 灯光  | `switch.[设备名称]_light`       | [设备名称] Light       | mdi:lightbulb  | 控制浴霸灯光          |
| 换气  | `switch.[设备名称]_ventilation` | [设备名称] Ventilation | mdi:air-filter | 控制换气功能          |
| 吹风  | `switch.[设备名称]_wind`        | [设备名称] Wind        | mdi:fan        | 控制吹风功能          |
| 暖风1 | `switch.[设备名称]_heater_1`    | [设备名称] Heater 1    | mdi:radiator   | 控制暖风1（低档加热） |
| 暖风2 | `switch.[设备名称]_heater_2`    | [设备名称] Heater 2    | mdi:radiator   | 控制暖风2（高档加热） |

### 传感器实体

| 功能       | 实体ID                                | 名称                     | 单位 | 精度   | 设备类      | 更新频率 |
| ------------ | --------------------------------------- | -------------------------- | ------ | -------- | ------------- | ---------- |
| 温度传感器 | `sensor.[设备名称]_temperature`   | [设备名称] Temperature   | °C  | 0.1°C | temperature | 5分钟    |
| 在线状态   | `sensor.[设备名称]_online_status` | [设备名称] Online Status | -    | -      | -           | 实时     |

​**设备注册**​：所有实体自动注册到同一设备下（名称=配置时设置的名称，制造商=Zinguo，型号=Smart Bathroom Fan，连接方式=云端）

## 🎮 使用方法

### 风扇控制

​**可用模式**​：`off`（关闭）、`cool`（吹风）、`heat_low`（暖风低档）、`heat_high`（暖风高档）

​**服务调用示例**​：

```yaml
# 开启吹风模式
service: fan.set_preset_mode
target:
  entity_id: fan.bathroom_fan
data:
  preset_mode: "cool"

# 开启暖风低档
service: fan.set_preset_mode
target:
  entity_id: fan.bathroom_fan
data:
  preset_mode: "heat_low"

# 关闭风扇
service: fan.turn_off
target:
  entity_id: fan.bathroom_fan
```

### 独立开关控制

​**服务调用示例**​：

```yaml
# 打开灯光
service: switch.turn_on
target:
  entity_id: switch.bathroom_light

# 打开换气
service: switch.turn_on
target:
  entity_id: switch.bathroom_ventilation

# 打开暖风1
service: switch.turn_on
target:
  entity_id: switch.bathroom_heater_1
```

## 🤖 自动化示例

### 示例1：早晨洗澡预热（工作日7点自动开启暖风20分钟）

```yaml
automation:
  - alias: "工作日早晨预热"
    description: "工作日7点自动开启暖风"
    trigger:
      platform: time
      at: "07:00:00"
    condition:
      - condition: time
        weekday: [mon, tue, wed, thu, fri]
      - condition: state
        entity_id: sensor.bathroom_temperature
        below: 22
    action:
      - service: fan.set_preset_mode
        target: {entity_id: fan.bathroom_fan}
        data: {preset_mode: "heat_low"}
      - delay: "00:20:00"
      - service: fan.set_preset_mode
        target: {entity_id: fan.bathroom_fan}
        data: {preset_mode: "off"}
    mode: single
```

### 示例2：湿度控制（湿度>75%自动换气25分钟）

```yaml
automation:
  - alias: "智能湿度控制"
    description: "湿度超过75%自动换气"
    trigger:
      - platform: numeric_state
        entity_id: sensor.bathroom_humidity
        above: 75
      - platform: state
        entity_id: binary_sensor.bathroom_motion
        to: "off"
        from: "on"
    condition:
      - condition: state
        entity_id: switch.bathroom_ventilation
        state: "off"
      - condition: template
        value_template: "{{ states('sensor.bathroom_humidity') | float > 75 }}"
    action:
      - service: switch.turn_on
        target: {entity_id: switch.bathroom_ventilation}
      - delay: "00:25:00"
      - service: switch.turn_off
        target: {entity_id: switch.bathroom_ventilation}
    mode: restart
```

### 示例3：回家自动预热（检测到回家且室温<20℃时预热15分钟）

```yaml
automation:
  - alias: "回家自动预热"
    description: "检测到即将回家时预热卫生间"
    trigger:
      platform: zone
      entity_id: device_tracker.person_name
      zone: zone.home
      event: enter
    condition:
      - condition: sun
        after: sunset
        before: sunrise
      - condition: template
        value_template: "{{ states('sensor.bathroom_temperature') | float < 20 }}"
    action:
      - service: fan.set_preset_mode
        target: {entity_id: fan.bathroom_fan}
        data: {preset_mode: "heat_low"}
      - delay: "00:15:00"
      - service: fan.set_preset_mode
        target: {entity_id: fan.bathroom_fan}
        data: {preset_mode: "off"}
```

### 示例4：温度保护（室温>35℃时自动关闭加热并通知）

```yaml
automation:
  - alias: "温度保护"
    description: "温度过高时自动关闭加热"
    trigger:
      platform: numeric_state
      entity_id: sensor.bathroom_temperature
      above: 35
    condition:
      - condition: or
        conditions:
          - condition: state
            entity_id: switch.bathroom_heater_1
            state: "on"
          - condition: state
            entity_id: switch.bathroom_heater_2
            state: "on"
    action:
      - service: fan.set_preset_mode
        target: {entity_id: fan.bathroom_fan}
        data: {preset_mode: "off"}
      - service: notify.mobile_app_phone
        data:
          message: "浴霸温度过高，已自动关闭加热功能"
          title: "安全提醒"
    mode: single
```

## 📱 Lovelace 卡片配置

### 简洁控制面板

```yaml
type: vertical-stack
cards:
  - type: entity
    entity: fan.bathroom_fan
    name: 浴霸控制
    icon: mdi:fan
    tap_action: {action: more-info}
  - type: horizontal-stack
    cards:
      - type: button
        entity: switch.bathroom_light
        name: 灯光
        icon: mdi:lightbulb
        tap_action: {action: toggle}
      - type: button
        entity: switch.bathroom_ventilation
        name: 换气
        icon: mdi:air-filter
        tap_action: {action: toggle}
  - type: entities
    entities:
      - entity: sensor.bathroom_temperature
        name: 当前温度
        icon: mdi:thermometer
      - entity: sensor.bathroom_online_status
        name: 设备状态
        icon: mdi:wifi
```

### 高级控制面板（需安装 Mushroom 卡片）

```yaml
type: custom:mushroom-title-card
title: 卫生间浴霸
subtitle: Zinguo 智能浴霸

type: custom:mushroom-chips-card
chips:
  - type: template
    icon: mdi:fan
    icon_color: |
      [[[
        if (states['fan.bathroom_fan'].state === 'off') return 'grey';
        else return 'blue';
      ]]]
    content: |
      [[[
        const state = states['fan.bathroom_fan'].state;
        if (state === 'off') return '关闭';
        if (state === 'cool') return '吹风';
        if (state === 'heat_low') return '暖风低档';
        if (state === 'heat_high') return '暖风高档';
        return state;
      ]]]
    tap_action: {action: more-info, entity: fan.bathroom_fan}

type: custom:mushroom-template-card
primary: 温度
secondary: "[[[ return states['sensor.bathroom_temperature'].state + '°C'; ]]]"
icon: mdi:thermometer
icon_color: |
  [[[
    const temp = parseFloat(states['sensor.bathroom_temperature'].state);
    if (temp < 20) return 'blue';
    if (temp > 30) return 'red';
    return 'green';
  ]]]

type: custom:mushroom-entity-card
entity: sensor.bathroom_online_status
name: 连接状态
icon: mdi:wifi
icon_color: |
  [[[
    if (states['sensor.bathroom_online_status'].state === 'Online') return 'green';
    else return 'red';
  ]]]
```

## 🔧 故障排除

### 常见问题

| 问题                       | 可能原因                                | 解决方法                                                                             |
| ---------------------------- | ----------------------------------------- | -------------------------------------------------------------------------------------- |
| 集成未出现在集成列表       | 未重启 HA/文件位置错误/权限问题         | 重启 HA；检查 `custom_components/zinguo`存在；`chmod -R 755`文件夹；查看日志 |
| 配置时提示"无法连接到设备" | MAC 错误/账户密码错误/设备离线/网络问题 | 确认 MAC（12位大写）；用 App 测试账户；检查设备在线；检查网络                        |
| 实体状态不更新             | 设备离线/API 令牌过期/网络不稳定        | 检查在线状态传感器；删除集成后重加；检查网络                                         |
| 控制指令执行失败           | 设备未响应/API 限制/并发控制            | 等待几秒重试；检查设备是否繁忙；避免频繁发指令                                       |

### 错误代码

| 错误代码       | 含义       | 解决方法         |
| ---------------- | ------------ | ------------------ |
| 401            | 认证失败   | 重新输入账户密码 |
| 404            | 设备未找到 | 检查 MAC 地址    |
| 500            | 服务器错误 | 等待后重试       |
| timeout        | 连接超时   | 检查网络连接     |
| invalid\_token | 令牌无效   | 重启集成         |

### 日志调试

1. 启用调试日志：在 `configuration.yaml`添加
   
   ```yaml
   logger:
     default: info
     logs:
       custom_components.zinguo: debug
   ```
2. 查看日志：SSH 执行 `tail -f config/home-assistant.log | grep zinguo`或通过 Web 界面（设置→系统→日志）

## 🔄 更新与维护

### 通过 HACS 更新

1. 打开 HACS → 集成
2. 找到「Zinguo Bathroom Fan」，有更新时显示「更新」按钮
3. 点击更新→选择版本→下载后重启 HA

### 手动更新

1. 备份当前配置
2. 下载最新版本
3. 替换 `custom_components/zinguo`文件夹
4. 重启 HA

### 备份配置

```bash
tar -czf zinguo-backup-$(date +%Y%m%d).tar.gz \
  config/custom_components/zinguo \
  config/.storage/core.config_entries
```

## 📊 技术细节

### API 接口

* ​**认证**​：POST `https://iot.zinguo.com/api/v1/customer/login`（参数：{"account":"手机号","password":"密码"}）
* ​**设备状态查询**​：GET `https://iot.zinguo.com/api/v1/customer/devices`（头部：x-access-token: [令牌]）
* ​**设备控制**​：PUT `https://iot.zinguo.com/api/v1/wifiyuba/yuBaControl`（头部：x-access-token: [令牌]，参数：含 MAC 和控制指令的 JSON）

### 工作原理

1. 认证：用账户密码获取访问令牌
2. 设备发现：查询账户设备，按 MAC 匹配
3. 状态轮询：每5分钟查询一次状态
4. 控制指令：发送指令后立即刷新状态
5. 错误处理：令牌过期时自动重新认证

### 安全机制

* 凭证安全：密码用 HA 加密存储
* 令牌管理：令牌存内存，不持久化
* 通信加密：所有 API 用 HTTPS
* 本地处理：所有数据本地处理
* 权限控制：遵循 HA 权限系统

## 🤝 参与贡献

### 报告问题

1. 访问 GitHub Issues
2. 点击「New Issue」→ 选择问题类型
3. 提供详细信息：HA 版本、集成版本、错误日志、复现步骤

### 功能建议

1. 创建 Feature Request Issue
2. 描述功能需求和使用场景，提供参考实现（如有）

### 代码贡献

1. Fork 仓库 → 创建功能分支 → 提交变更 → 创建 Pull Request
2. 代码规范：遵循 Python PEP 8，添加类型注解、文档注释，包含测试用例

## 📄 许可证

采用 MIT 许可证，详见 LICENSE文件。

## 🙏 致谢

感谢 Zinguo（优质智能浴霸产品）、Home Assistant 团队（优秀智能家居平台）、HACS 团队（便捷插件管理）、所有贡献者和测试用户。

## 📞 支持与帮助

* ​**GitHub Issues**​：报告问题和功能请求
* ​**Home Assistant 社区**​：论坛寻求帮助
* ​**Discussions**​：参与功能讨论
* ​**联系维护者**​：GitHub @jyz0501（Email 通过 GitHub 个人资料获取）

## 🔗 相关链接

* Home Assistant 官网
* HACS 官网
* Zinguo 官网
* Home Assistant 中文社区
* Home Assistant 官方论坛

---

**​感谢使用！​**​ 如果项目对您有帮助，请考虑 ⭐ 给项目 Star、📢 分享给朋友、🐛 报告问题或 💡 提出建议。祝您使用愉快！🚿✨

