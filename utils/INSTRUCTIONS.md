# 指引：如何更新 Gemini 模型

您好，看来我使用的模型信息已经过时，非常抱歉。

为了解决这个问题，我创建了一个名为 `check_models.py` 的新脚本来获取您账户下所有可用的最新模型。

## 请按以下步骤操作：

### 1. 运行模型检查脚本

请在您的终端中运行以下命令：

```bash
python check_models.py
```

这个脚本会连接到 Google API 并打印出所有支持 `generateContent` 的模型列表。输出结果可能像这样：

```
模型名称: models/gemini-1.0-pro
模型名称: models/gemini-1.5-flash-001
模型名称: models/gemini-1.5-pro-latest
...
```

### 2. 更新处理器文件

从上一步的输出列表中，选择一个您希望使用的模型（通常推荐选择带有 `latest` 标签的 `flash` 或 `pro` 模型）。

然后，请打开 `gemini_processor.py` 文件，找到下面这一行：

```python
MODEL_NAME = "models/gemini-1.5-flash-latest" 
```

将 `"models/gemini-1.5-flash-latest"` 替换为您从列表中选择的**正确模型名称**。

### 3. 完成

完成以上步骤后，翻译和分类功能应该就可以正常工作了。

对于之前使用过时模型名称给您带来的不便，我再次表示歉意。
