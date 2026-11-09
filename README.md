<div align="center">

# 放射性骨骼肌损伤文献周报 · Radiation Muscle Literature Weekly

**每周一自动检索、按周归档、可直接调用的放射性肌损伤文献库**
**A weekly, archived, query-ready literature log on radiation-induced skeletal muscle injury**

`PubMed E-utilities` · `Europe PMC 预印本` · `跨周去重` · `A/B/C 相关度` · `候选入图谱`

[用在哪里](#用在哪里) · [目录结构](#目录结构) · [字段说明](#字段说明) · [怎么调用](#怎么调用) · [检索方法](#检索方法) · [更新规则](#更新规则)

</div>

> 内容基于 PubMed/Europe PMC 摘要整理，「研究不足」「值得借鉴」为基于摘要的判断，引用前请回到原文核对。影响因子取 JCR 最新公布值，并在 `data/journal-if.csv` 记录核对来源与日期。

## 用在哪里

| 场景 | 怎么用 |
|---|---|
| 写综述（IJRB 机制综述、Burns & Trauma 整合修复综述） | 按主题、相关度筛 `data/papers.csv`，直接取 PMID/DOI 与核心结论 |
| 每周跟进 | 读 `digests/` 当周文件，只看相关度 A 与「精读：是」 |
| 更新图谱 | 筛「候选入图谱」列，同步到 radiation-muscle-pathway |
| 找课题 | 汇总「研究不足」列，看哪些空白反复出现 |

## 目录结构

```
README.md                     本说明
digests/YYYY-MM-DD.md         每周速递（按主题分组，每篇一张卡片表）
data/papers.csv               累计文献总表（UTF-8 BOM，Excel 可直接打开）
data/journal-if.csv           期刊影响因子缓存（含 JCR 年度与核对来源）
methods/search-strategyv0.2.md  当前检索方法与优化说明
scripts/weekly-searchv0.2.py  每周检索脚本（仅标准库）
```

## 字段说明

`data/papers.csv` 一行一篇，按 PMID（无 PMID 用 DOI）去重：

| 字段 | 含义 |
|---|---|
| 周次 / 检索日期 | ISO 周（如 2026-W46）/ 北京时间检索日 |
| 主题 | 1 放射性骨骼肌损伤；2 放射性肌纤维化；3 卫星细胞/FAPs 与辐射；4 EV/外泌体治疗放射损伤 |
| PMID / DOI / 题目 / 第一作者 | 来自 E-utilities esummary |
| 发表时间 / PubMed收录 | 期刊发表日期 / 进入 PubMed 的月份（可能晚于发表） |
| 期刊 / 影响因子 / IF来源 | 预印本写「无」 |
| 文章类型 / 研究类型 / 是否预印本 | 临床、动物、体外、综述、Meta 分析等 |
| 核心内容 | 基于摘要的关键发现，含原文数字 |
| 研究不足 | 样本、模型、剂量、对照、随访、机制等缺口 |
| 值得借鉴 | 对 Bruce 的综述、课题或实验设计有用的点 |
| 相关度 | A 直接（放射 + 骨骼肌）；B 相邻（放射 + 邻近组织或肌肉但非放射）；C 方法/背景 |
| 是否精读 | 是 / 选读 / 否 |
| 候选入图谱 | 涉及图谱节点（MuSC-FAP-ECM、DNA-redox、血管、免疫、衰老-p21、EV）则标「候选」 |

## 怎么调用

```bash
# 所有 A 级文献
python3 -c "import csv;[print(r['PMID'],r['题目']) for r in csv.DictReader(open('data/papers.csv',encoding='utf-8-sig')) if r['相关度']=='A']"

# 某主题全部研究不足（找课题）
python3 -c "import csv;[print(r['PMID'],r['研究不足']) for r in csv.DictReader(open('data/papers.csv',encoding='utf-8-sig')) if r['主题'].startswith('3')]"

# 手动跑一次检索（近 14 天）
python3 scripts/weekly-searchv0.2.py --days 14 --out candidates.json
```

也可以直接在 Hark 里说「查周报里所有 FAP 相关文献」或「列出精读清单」。

## 检索方法

当前 v0.2，见 [methods/search-strategyv0.2.md](methods/search-strategyv0.2.md)：PubMed edat 近 7 天 + Europe PMC 预印本，跨周去重，主题 3 扩充 FAP/MuSC 同义词，A/B/C 分级与精读规则。

## 更新规则

- 每周一北京时间约 08:30 由 Hark 自动检索、整理并推送；commit 信息带 `[skip ci]`
- 每月第一个周一追加月度趋势小结（`digests/YYYY-MM-monthly.md`）
- 某周无新文献也会提交当周 digest，注明「本周无新文献」，保证时间线连续
