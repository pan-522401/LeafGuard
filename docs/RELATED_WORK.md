# 相关开源项目调研与借鉴说明（RELATED WORK）

本文档记录 LeafGuard 在起步阶段对同类开源项目的调研、评估与借鉴方式，供成员 A、B 共同参考。原则：**参考借鉴，不整仓 fork**。

## 1. 目的
- 降低从零起步的返工风险，避免走弯路。
- 复用成熟的数据来源与工程结构，但**实验、结果与分析必须由本项目自己完成**。
- 明确合规边界（许可证、引用、学术诚信）。

## 2. 核心决策
| 选项 | 是否采用 | 原因 |
|---|---|---|
| 整仓 fork 替换现有仓库 | 否 | 许可不明、结构冲突、学术诚信风险、已搭好的 CI/分工会被推翻 |
| 参考数据 + 代码结构 + demo 思路 | 是 | 低风险、保留自主实验、符合课程要求 |

## 3. 调研方法（可复现）
- 日期：2026-11-16
- 方式：GitHub Search API（`/search/repositories`，按 stars 排序）
- 检索词：`plant disease classification`、`plantvillage`、`plant disease detection deep learning`
- 复核：对候选仓库读取顶层目录结构（`/repos/{owner}/{repo}/contents`）

## 4. 候选项目清单（实测）
| 项目 | Stars | 语言 | 许可 | 用途 |
|---|---|---|---|---|
| spMohanty/PlantVillage-Dataset | 1037 | Python | 无 LICENSE | 数据集本体（数据来源） |
| MarkoArsenovic/DeepLearning_PlantDiseases | 246 | Python | 自定义(待核实) | SOTA CNN 评测脚本、对比表 |
| mehra-deepak/Plant-Disease-Detection | 210 | Notebook | 无 LICENSE | 经典 ML 基线 |
| soumyajit4419/Plant_AI | 197 | Jupyter | MIT | 含 Flask Web demo |
| abdullahselek/plant-disease-classification-tf | 61 | Python | MIT | TF 版分类（可选） |
| AhmadJeddi/Plant-Disease-Classification | 51 | Python | MIT | ResNet + 可复现训练/评估，结构最贴合 |

> 顶层结构观察：AhmadJeddi = `src/ experiments/ data/ docs/ requirements.txt LICENSE`（最接近本项目布局）。

## 5. 评估维度
- 许可证是否明确、可借鉴（优先 MIT）
- 框架是否与本项目一致（PyTorch + torchvision）
- 是否基于 PlantVillage、类别数是否吻合
- 是否含可复现的训练/评估/混淆矩阵
- 是否含可直接对接的推理/demo
- 代码质量与活跃度

## 6. 采用策略（分层复用）
| 层 | 采用内容 | 来源 | 注意 |
|---|---|---|---|
| 数据 | PlantVillage 38 类（+ 可选 PlantDoc） | spMohanty 官方仓 / Kaggle 镜像 | 记录来源与引用；数据不进 Git |
| 代码参考 | 数据加载、评估、混淆矩阵、可视化写法 | AhmadJeddi / MarkoArsenovic | 保留版权、注明来源 |
| 演示 | 单图预测 Web demo 思路 | soumyajit4419/Plant_AI | 与 B 的 scripts/predict.py 对接 |
| 结构与实验 | **保持本项目自有**的 A/B 分工、接口合同、E1–E4 | 本仓库 | 不照搬他人结果 |

## 7. 借鉴流程（SOP）
1. 明确需求：缺的是数据、代码、还是 demo。
2. 用 GitHub API 检索候选，按 stars 与许可证筛选。
3. 读取候选的 README、LICENSE、requirements、目录结构。
4. 判定许可证是否允许借鉴（MIT/Apache 可；无 LICENSE 只读不抄）。
5. 抽取可借鉴的最小片段/思路，落到本项目对应模块。
6. 在提交说明与本文件中注明来源。
7. 用本项目数据与脚本重新实验，结果以真实运行为准。

## 8. 合规、许可与引用
- 数据集：记录来源、版本、许可、引用到 `docs/DATASET_NOTES.md`；使用前核实官方引用。
- 代码：MIT/Apache 可借鉴，需保留版权声明并注明出处；无 LICENSE 的仓库只作阅读参考。
- 结果：**不得**把他人论文/仓库的指标当作本项目结果。

## 9. 落地映射（本项目）
| 本项目位置 | 借鉴对象 | 说明 |
|---|---|---|
| src/data/ | AhmadJeddi 的数据组织 | 仅借鉴思路，代码自写 |
| src/training/ | AhmadJeddi / MarkoArsenovic 的评估 | 指标口径对齐 INTERFACE_CONTRACT |
| scripts/predict.py | Plant_AI 的推理/demo | B 负责实现 |
| docs/model_notes.md | 评估维度 | 记录真实结果 |

## 10. 学术诚信红线
- 所有指标、混淆矩阵、训练时长来自本项目真实运行。
- 引用真实存在的论文/仓库，不伪造 DOI、作者、链接。
- 借鉴代码需在提交中说明来源。

## 11. 后续维护
- 新增参考项目时更新第 4、6 节。
- 调研日期、检索词一并记录，保证可复现。
