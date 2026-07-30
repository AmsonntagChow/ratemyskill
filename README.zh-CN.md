# RateMySkill

[English](README.md) | 简体中文

为 Agent Skill 提供以证据为依据的发布评审。

> 你的 Skill 已通过 YAML 验证。现在，请证明它值得被安装。

[![MIT 许可证](https://img.shields.io/badge/license-MIT-2f855a.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-5b5bd6.svg)](https://agentskills.io/)
[![skills.sh](https://skills.sh/b/AmsonntagChow/ratemyskill)](https://skills.sh/amsonntagchow/ratemyskill/ratemyskill)

RateMySkill 对具体 Agent Skill 的实际行为进行审计，而不只是检查 Markdown。它会检验：正确的请求能否发现它；与不使用该 Skill 完成同一任务相比，使用它能否带来可衡量的结果提升；其脚本和指令是否始终在权限范围内运行；以及最终软件包能否由其他人安装并复现。

## 安装

选择一种方式即可。不要在同一客户端的同一作用域内安装重复副本。

在 Codex 中，将此仓库添加为插件市场：

```bash
codex plugin marketplace add AmsonntagChow/ratemyskill
```

然后在 Codex CLI 中打开 `/plugins`，或在桌面应用中打开 Plugins Directory，安装 **RateMySkill**，并开始一个新会话。

对于 Claude Code：

```text
/plugin marketplace add AmsonntagChow/ratemyskill
/plugin install ratemyskill@amsonntagchow-ratemyskill
/reload-plugins
```

对于 Cursor、Codex、Claude Code 或其他 Agent Skills 客户端，也可以通过可移植的 `skills` CLI 安装：

```bash
npx skills add AmsonntagChow/ratemyskill --skill ratemyskill
```

也可以手动安装此 Skill：将 `skills/ratemyskill` 复制到智能体所使用的 Skill 目录中。

## 开始审计

向它提供真实的 Skill 文件夹、仓库、归档文件或已安装软件包。如果提示词尚未指定，RateMySkill 会先询问两个设置：

```text
1. 角色：Skill 用户 / Staff Agent 工程师 / 红队审查员 / 商店审核员 / 答辩老师
2. 程度：快速体检 / 严格评审 / 上架门禁 / 特权审查 / 生死审查
```

例如：

```text
作为 Staff Agent 工程师，审计 ./skills/my-skill 是否适合公开发布。不要修改它。告诉我最快能完成的三项修复。
```

可用角色分别侧重不同问题：

| 角色 | 主要判断 |
|---|---|
| Skill 用户 | 它能否以更少的工作量和更好的结果完成承诺的任务？ |
| Staff Agent 工程师 | 触发条件、指令、参考资料、脚本和失败路径是否可靠？ |
| 红队审查员 | 不可信内容、过度权限、机密信息、网络或依赖项是否会带来安全风险？ |
| 商店审核员 | 陌生人能否冷安装完全相同的最终软件包，并信任其公开声明？ |
| 答辩老师 | 作者是否理解这个制品中真实存在的风险？ |

作者的理解程度单独评分。薄弱的回答不会抹去经过独立验证的 Skill 行为，而精美的指令也不能证明作者真正理解。

## 与众不同之处

RateMySkill 将发现和执行分开评估：

1. **发现：** 预期请求是否会选中该 Skill，而仅共享关键词的相似非目标请求不会误触发？
2. **执行：** 一旦被明确选中，该 Skill 与条件相同但不使用 Skill 的基线相比，是否能可靠地改善任务结果？

显式调用 `$ratemyskill` 能证明执行能力，但不能证明自动发现能力。有效的文件夹、全绿的仓库 CI 和有效的评测 JSON 能证明结构正确，却不能证明有用。因此，团队批准和公开发布都需要一份最终软件包的运行记录，其中包括：经过重复测试的选择命中率和误触发率、使用 Skill 与不使用 Skill 的结果及提升幅度、声明的阈值和方差策略，以及主机、模型、数据集、评分标准、裁判和软件包摘要的标识。

它还会针对以下问题实施不可绕过的发布否决：机密信息外泄、未经授权的副作用、不受控的代码执行、隐藏的网络访问或遥测、伪造成功、核心软件包损坏、不安全的过度触发、信任倒置，以及许可证或来源违规。对于受影响的分发目标，良好的平均分不能抵消其中任何一项失败。

## 结论

完成评审后，首先用一行概述每个已验证问题；接着单独列出仍待验证的内容；最后给出决定和证据上限：

```text
问题列表：
- [S-002 · HIGH] 触发范围过于宽泛：普通写作请求可能激活该 Skill，并使无关工作偏离目标。
待验证：
- 尚未在全新会话中测试隐式选择，因此商店发现能力仍然未知。

证据面板：
- 确定性检查：PASS
- 关键路径端到端测试：PASS
- 概率性评测：UNVERIFIED
- 持续证据：N/A

请求的分发范围：
最高安全分发范围：
决定：READY | READY WITH CONDITIONS | NOT READY | BLOCKED | INSUFFICIENT EVIDENCE
Skill 评分：可选
发现质量：
执行提升：
证据覆盖率：
置信度：

阻断项：
已验证发现：
未验证风险：
最重要的 3 项行动：
复测计划：
```

开头的列表必须完整、按严重程度排序，并且每项仅用一句通俗的话说明严重程度、失败和后果。修复方法和证据留在详细发现中。四条证据通道绝不能相互替代；`N/A` 表示确实不在范围内，而未运行的检查应标记为 `UNVERIFIED`。如果没有验证出任何问题，评审会明确说明这一点，同时仍会列出有待验证的内容。每项详细发现都包括精确的复现步骤、预期行为和实际行为、证据强度、影响、最小安全修复、验收测试，以及一个相近的回归测试用例。

## 评分

数值评分是可选的。内置评分器仅使用 Python 标准库，会验证每条证据链接、应用特定于目标的证据上限、为评分标准生成指纹，并只针对声明的分发目标实施否决。

```bash
python3 skills/ratemyskill/scripts/score_review.py --pretty evals/scorecards/blocked-release.json
```

原始质量分数与受证据限制的发布决定彼此独立。评分卡 schema v2 会按证据通道和断言类型标注每条证据，拒绝跨通道替代以及互相矛盾的 PASS 通道，并根据记录的摘要计算行为命中率、误触发率和提升幅度。结构性证据不能满足运行时或高风险行为检查。必需的 `UNVERIFIED` 或 `N/A` 通道会继续作为明显缺口保留，而空洞的阈值不能自行授权发布。

在可选评分器中，schema v2 采用失败时默认拒绝（fail-closed）的迁移策略。现有 v1 评分卡必须为每条证据添加 `lane` 和 `assertion_type`，并补充完整的 `evidence_panel` 与 `behavioral_eval`；未经重新运行，不得把旧证据重新标记成新证据。评分器会返回清晰的 schema 版本错误，而不会猜测这些字段。

## 信任与安全

首次审计为只读。此 Skill 不会授予工具权限、授权 shell 命令、安装依赖项、发布软件包、发送遥测数据或运营托管服务。它把受审计的每个 Skill、脚本、夹具、仓库指令、网页、日志和生成输出都视为不可信证据。

请将宿主智能体的沙箱和权限控制作为真正的安全边界。参阅 [SECURITY.md](SECURITY.md)、[PRIVACY.md](PRIVACY.md) 和 [TERMS.md](TERMS.md)。

## 仓库结构

```text
.claude-plugin/              Claude Code 插件和商店清单
.agents/plugins/             Codex 仓库商店
plugins/ratemyskill/         自包含的通用 Codex 插件及上架素材
skills/ratemyskill/          规范的可移植 Skill、参考资料、UI 元数据和评分器
evals/trigger_cases.json     正向及相似非目标选择评测
evals/execution_cases.json   使用 Skill 与不使用 Skill 的行为评测
evals/fixtures/              安全的合成失败用例
submission/                  公开目录上架文案和评审测试
scripts/                     软件包同步和仓库验证
tests/                       确定性评分器测试
```

## 开发

```bash
python3 scripts/sync_codex_plugin.py --check
python3 scripts/validate_repo.py
python3 -m unittest discover -s tests -v
claude plugin validate . --strict
python3 /path/to/plugin-creator/scripts/validate_plugin.py plugins/ratemyskill
```

贡献必须包含行为证据，不能只有文字差异。请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

本仓库的编写方法参考了[《从零做一个高质量 Agent Skill，并把它当开源项目运营》](https://research.xishe.ai/skill-authoring-and-oss)，尤其是其中关于描述优先的发现机制、渐进式披露、分离触发与执行评测、参考资料完整性、零依赖脚本和开源分发的指导。

## 许可证

[MIT](LICENSE) © 2026 AmsonntagChow
