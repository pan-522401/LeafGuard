# 数据集来源

## PlantVillage（主数据集，已下载）

- 来源：https://github.com/spMohanty/PlantVillage-Dataset
- 使用子集：`raw/color`
- 版本：`master` @ `7f7ecc7e1eaca78107e3affe7cb5abd9427e139a`（上游提交日期 2026-02-05）
- 下载日期：2026-11-11
- 本地相对路径：`data/plantvillage/<类别名>/<图片>`
- 类别数：38；图片数：54305（详细统计见 `docs/data_audit.md`）
- 许可证：上游仓库未声明 License（GitHub API 返回 `license: null`），使用与再分发前需按课程要求核对
- 引用：Mohanty, Hughes, Salathé (2016), *Using deep learning for image-based plant disease detection*, Frontiers in Plant Science, DOI 10.3389/fpls.2016.01419

## PlantDoc（可选外部评估，尚未下载）

- 来源：https://github.com/pratikkayal/PlantDoc-Dataset
- 仅作外部评估，不参与训练或调参
- 类别不保证与 PlantVillage 一致，使用前先做人工类别映射审核

## 通用约定

- 数据集本体不提交 Git（`data/` 已忽略）。
- 记录来源、下载日期、版本、类别数量与排除样本；未扫描前不要填写推测数值。
