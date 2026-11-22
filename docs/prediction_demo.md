# 预测与演示使用说明

预测依赖 A 产出的 checkpoint（字段见 `docs/INTERFACE_CONTRACT.md`）。  
所有输出中的分数都是 **softmax 值，不是校准后的诊断概率**。

## 1. 单图预测

```powershell
python scripts/predict.py --image data/plantvillage/Tomato___healthy/xxxx.jpg --checkpoint results/checkpoints/<model>.pth
```

输出 JSON，包含：

- 预测类别
- Top-3 类别与 softmax 分数
- 使用的 checkpoint / 类别映射来源

## 2. 批量预测（演示用）

```powershell
python scripts/batch_predict.py --input data/plantdoc/Tomato\ leaf --checkpoint results/checkpoints/<model>.pth
```

输出：

- `results/predictions/batch_predictions.csv`
  - `path,pred_class,pred_label,confidence,top_k_classes,top_k_scores,error`
- `results/predictions/batch_summary.json`
  - 图片总数、成功/失败数、预测类别计数、失败文件列表

常用参数：

- `--input`：图片文件或目录
- `--recursive` / `--no-recursive`：是否递归子目录（默认递归）
- `--limit N`：只预测前 N 张，方便演示
- `--top-k`：默认 3
- `--device auto|cpu|cuda`
- `--batch-size`、`--num-workers`

示例（只跑 8 张）：

```powershell
python scripts/batch_predict.py --input data/plantdoc --limit 8 --checkpoint results/checkpoints/<model>.pth
```

## 3. 演示建议

1. A 训练完成后，选 5–10 张不同病害图片放在一个文件夹
2. 运行 `batch_predict.py`，打开 `batch_predictions.csv` 展示预测类别和置信度
3. 需要讲解时，用 `predict.py` 对单张图输出 Top-3

## 4. 注意事项

- 没有 checkpoint 时不要编造预测结果；可用临时 checkpoint 只验证流程，数值无意义
- 外部数据（PlantDoc）只用于评估/演示，不参与训练或调参
- 预测结果不能作为真实农业诊断结论
