# ScriptForge AI 剧本 YAML Schema

ScriptForge 的 YAML Schema 目标是让小说改编结果既像剧本，又能被程序稳定读取、校验和二次编辑。Schema 采用 JSON Schema 2020-12 描述，实际内容以 YAML 输出，兼顾作者可读性和工程可验证性。

## 顶层结构

```yaml
metadata: {}
characters: []
locations: []
episodes: []
adaptation_notes: []
```

## 字段说明

`metadata` 描述剧本整体信息，包括标题、剧本类型、语言、来源章节数和一句话故事。`source_chapters` 要求不小于 3，用于直接对应赛题要求。

`characters` 是角色表。每个角色必须有 `id`、`name`、`role`、`motivation`，可选 `voice`。设计角色表是为了让对白引用稳定，不让同一个人物在不同场景里出现多个名字。

`locations` 是地点表。每个地点包含 `id`、`name`、`description`。地点独立成表，可以支持后续的场景统计、拍摄预算估算和地点复用。

`episodes` 用于承载剧本正文。即使只生成一集，也保留 episode 层级，方便短剧、网剧或章节式剧本继续扩展。

`scenes` 是剧本的核心单元。每场戏必须包含：

```yaml
id: SC001
heading: 内景 - 旧书房 - 夜
time: 夜
location: loc_1
characters: [char_1, char_2]
source_chapters: [1]
objective: 主角在本场想达成的目标
conflict: 本场的阻力或对立关系
beats: []
```

`source_chapters` 是可追溯设计。作者能知道某场戏来自哪些原文章节，方便回看原文和局部重写。

`beats` 表示场景内部的动作、对白、旁白和转场。`type` 只允许：

- `action`：可拍摄动作或场面调度
- `dialogue`：角色台词，必须带 `speaker`
- `narration`：旁白或保留的小说叙述
- `transition`：转场提示

`adaptation_notes` 记录改编决策，例如压缩了哪些叙述、强化了哪些冲突、保留了哪些旁白。这让 AI 生成结果更透明，也利于作者继续打磨。

## 设计原因

1. **先结构化再创作**：小说转剧本不是简单改写，必须先拆人物、地点、场景和动作。Schema 让 AI 输出可被校验的结构，而不是一段难以编辑的长文本。
2. **支持局部编辑**：场景和 beat 都有明确边界，用户可以只重写某一场、某段对白或某个动作。
3. **减少 AI 幻觉影响**：角色和地点集中定义，校验器能检查 speaker 是否引用了不存在的角色。
4. **保留原文追溯**：`source_chapters` 让作者知道改编来源，适合长篇小说的持续创作。
5. **适配多剧本形态**：`script_type` 和 `episodes` 兼容影视剧、短剧、舞台剧和广播剧。

完整机器可读 Schema 位于 `backend/app/schemas/script_schema.json`。

