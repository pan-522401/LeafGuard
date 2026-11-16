# 数据集来源

PlantVillage：https://github.com/spMohanty/PlantVillage-Dataset
PlantDoc（可选外部评估）：https://github.com/pratikkayal/PlantDoc-Dataset

下载前检查许可证、引用要求和版本。PlantDoc 类别不保证与 PlantVillage 一致，先做映射审核。记录来源、下载日期、版本、类别数量、排除样本。数据集本体不提交 Git。

## 获取方式
- PlantVillage（主数据集）：优先官方仓库；如用 Kaggle 镜像，需核对类别数（目标 38 类）与目录结构。
- PlantDoc（可选外部评估）：官方仓库；仅用于 E5 外部评估。

## 目录约定
- PlantVillage 放在 `data/plantvillage/<类别名>/<图片>`。
- PlantDoc 放在 `data/plantdoc/<类别名>/<图片>`。
- 两人目录结构必须一致（划分 CSV 中的 path 相对项目根）。

## 引用与许可
- 使用前核实数据集的官方引用信息（作者、年份、许可）并记录到本文件；不确定的信息不要臆造。
- 数据集本体不提交 Git；划分清单与类别映射放在 `splits/`（提交）。

## 相关文档
- 参考项目与借鉴方式：`docs/RELATED_WORK.md`
- 数据审计记录：`docs/data_audit.md`
