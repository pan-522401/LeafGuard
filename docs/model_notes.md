# 成员 A：模型实验记录

只记录真实运行结果；未运行的实验不得填写数值。

## 模型
- SmallCNN：4 段 Conv-BN-ReLU-Pool + AdaptiveAvgPool + Dropout + Linear，从零训练。
- ResNet18：torchvision ImageNet 权重，替换 `fc`；支持冻结 backbone 与解冻 layer4 微调。

## 实验计划
| 实验 | 模型/策略 | 用途 |
|---|---|---|
| E1 | SmallCNN 从零训练 | 基线 |
| E2 | ResNet18 冻结 backbone | 迁移学习基线 |
| E3 | ResNet18 微调 layer4 | 评估微调价值 |
| E4 | ResNet18 + 轻量增强 | 评估增强影响 |
| E5（可选） | PlantDoc 共同类别外部评估 | 域泛化 |

## 实验记录（实际运行后填写）
| 实验 | 模型 | 增强 | Seed | Epoch | Val Macro-F1 | Test Macro-F1 | 训练时长 | 备注 |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |

## 指标
Accuracy、Macro-F1、Macro Recall、混淆矩阵、训练时长。

## 进度
- [x] 实现 SmallCNN
- [x] 实现 ResNet18 分类头替换
- [x] 冻结 backbone / 解冻 layer4
- [x] 模型接口测试（logits / 冻结 / 微调）通过
- [x] 训练管线 + 单入口脚本 + smoke test 通过
- [ ] 真实数据训练（依赖 B 的 splits/*.csv 与 class_to_idx.json）
- [ ] 数据增强消融
- [ ] 混淆矩阵与误分类分析
- [ ] 外部评估（PlantDoc）

## 环境
- Python 3.13，torch 2.14.1+cu130，torchvision 0.29.1+cu130
- GPU：NVIDIA GeForce RTX 4060 Laptop GPU（8GB）
