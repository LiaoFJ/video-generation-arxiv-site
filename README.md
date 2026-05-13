# Video Generation Arxiv Site

一个本地运行的论文日报网站。

项目会从 Hugging Face Daily Papers 获取每日论文榜单，筛出与 video generation 相关的论文，下载对应 arXiv PDF，提取正文，并调用兼容 OpenAI API 的模型生成中文整理结果。生成后的内容会按日期保存，并通过 FastAPI 网站展示。

## 功能概览

- 每日抓取 Hugging Face Daily Papers 榜单
- 拉取 arXiv 元数据与 PDF
- 提取 PDF 正文文本
- 生成结构化中文总结
- 按日期归档论文内容
- 提供首页、归档页、详情页
- 提供本地单用户登录保护

## 技术栈

- Python 3.12+
- FastAPI
- Jinja2
- httpx
- PyMuPDF
- Pydantic Settings

## 目录说明

- `app/`: 网站、抓取与总结逻辑
- `content/`: 运行后生成的论文归档内容
- `scripts/run_daily.py`: 每日抓取与发布入口
- `docs/operations/local-run.md`: 本地运行补充说明
- `.env.example`: 环境变量模板

## 1. 安装依赖

建议先创建虚拟环境，然后安装项目依赖：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

如果你使用 Conda，也可以直接在现有环境里执行：

```powershell
python -m pip install -e ".[dev]"
```

## 2. 配置环境变量

先复制模板文件：

```powershell
Copy-Item .env.example .env
```

然后编辑 `.env`，至少填写下面几项：

- `OPENAI_API_KEY`
- `APP_USERNAME`
- `APP_PASSWORD`

默认模板使用 DeepSeek 兼容接口：

- `OPENAI_BASE_URL=https://api.deepseek.com`
- `OPENAI_MODEL=deepseek-v4-flash`

如果你想切到别的兼容 OpenAI API 的服务，可以修改这两个字段。

## 3. 启动网站

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

浏览器打开：

[http://127.0.0.1:8000](http://127.0.0.1:8000)

网站默认会要求登录，账号密码来自 `.env` 中的：

- `APP_USERNAME`
- `APP_PASSWORD`

## 4. 运行每日抓取与发布

```powershell
python scripts/run_daily.py
```

脚本完成后会输出类似：

```text
Published 3 paper(s).
```

生成内容会保存到：

```text
content/YYYY-MM-DD/
```

其中通常包含：

- `index.json`
- 每篇论文的详情 JSON 文件

## 5. 排行榜来源

默认情况下，项目会使用：

[https://huggingface.co/papers?date=YYYY-MM-DD](https://huggingface.co/papers?date=2026-05-01)

如果某天没有条目，程序会自动向前回退到最近一个有内容的日期。周末或节假日出现空榜单时，这个逻辑尤其有用。

如果你有自己的榜单页面，可以通过 `.env` 中的 `RANKING_URL_TEMPLATE` 覆盖默认来源。

## 6. Windows 定时任务

仓库内提供了一个本地调度入口：

- `scripts/run_daily_task.cmd`

你可以手动执行：

```powershell
cmd /c scripts\run_daily_task.cmd
```

如果要配置成每天自动运行，可以在 Windows 计划任务里调用这个脚本，或者直接调用：

```powershell
python scripts/run_daily.py
```

本项目作者本地曾使用 `10:00` 的日常调度，但这不是仓库强制行为；拉到新机器后需要你自行配置计划任务。

## 7. 运行测试

```powershell
$env:TMP="$PWD\.tmp"
$env:TEMP="$PWD\.tmp"
python -m pytest -v --basetemp=.tmp_test_run -p no:cacheprovider
```

Windows 下如果 `pytest` 清理临时目录时报权限错误，换一个新的 `--basetemp` 目录名通常就可以。

## 8. 注意事项

- `.env` 不会被提交到 Git，请只在本地保存真实密钥
- `content/` 是运行产物，是否提交由你自己决定
- 如果 PDF 解析失败或模型返回结果不完整，该论文不会被发布
- 当前站点是“单用户本地登录”方案，适合本机使用，不是完整的多用户系统

## 9. 常见使用流程

1. 复制 `.env.example` 为 `.env`
2. 填写 API key 和登录账号密码
3. 安装依赖
4. 执行 `python scripts/run_daily.py` 生成内容
5. 执行 `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`
6. 打开浏览器登录查看结果
