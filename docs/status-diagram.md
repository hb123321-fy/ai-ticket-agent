# Agent 状态流转图

```mermaid
graph TD
    START([开始]) --> COLLECTING[COLLECTING_INFORMATION<br/>收集信息]

    COLLECTING -->|信息不足| COLLECTING
    COLLECTING -->|信息完整| INVESTIGATING[INVESTIGATING<br/>调查证据]

    INVESTIGATING -->|调用工具| INVESTIGATING
    INVESTIGATING -->|证据收集完成| PROPOSING[PROPOSING_PLAN<br/>生成方案]

    PROPOSING -->|需要确认| WAITING[WAITING_FOR_APPROVAL<br/>等待人工确认]
    PROPOSING -->|无需确认/转人工| ESCALATED[ESCALATED<br/>已转人工]
    PROPOSING -->|无法判断| FAILED[FAILED<br/>处理失败]

    WAITING -->|批准| EXECUTING[EXECUTING<br/>执行操作]
    WAITING -->|拒绝| FAILED

    EXECUTING -->|执行完成| VERIFYING[VERIFYING<br/>复核结果]

    VERIFYING -->|成功| RESOLVED[RESOLVED<br/>已解决]
    VERIFYING -->|失败| ESCALATED

    RESOLVED --> END([结束])
    ESCALATED --> END
    FAILED --> END

    BLOCKED[BLOCKED<br/>恶意拦截] -.->|检测到恶意指令| END