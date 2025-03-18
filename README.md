# BPMN Code Generation and Verification Framework

## 项目简介
本仓库用于实现基于 AI 和机器学习的 BPMN 代码生成与验证框架，
其核心功能包括：
- **BPMN 生成**：利用 LLM 生成 BPMN 相关组件。
- **模型验证**：调用验证工具验证生成的 BPMN 质量。

## 仓库结构
```
.
├── generation/        # 生成 BPMN 相关组件的脚本
├── verification/         # 验证工具的调用脚本
├── .secret          # 记录 GPT API 号的文件（需手动创建）
├── README.md        # 项目说明文件
```

### `generator/`
该文件夹包含用于生成 BPMN 组件的一系列 Python 脚本。

### `verifier/`
该文件夹包含调用验证工具的一系列 Python 脚本，用于检查 BPMN 模型的正确性。

### `.secret`
该文件用于存储 GPT 的 API 号，确保生成过程能够正常访问 API。
> **注意**：此文件不应提交到版本控制系统（如 Git），请在 `.gitignore` 文件中添加 `.secret` 以避免泄露敏感信息。

## 许可证
本项目基于 MIT 许可证发布，详见 [LICENSE](LICENSE) 文件。
