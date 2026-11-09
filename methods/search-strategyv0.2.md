# 检索方法 v0.2（2026-11-09）

结论先说：v0.2 在 v0.1 上加了 7 项改动。其中 4 项已在 2026-11-09 实测验证（去重、预印本通道、FAP 同义词、肌肉词扩展），3 项是流程规则（分级、研究类型、图谱对接），随每周运行检验。

## v0.1 回顾
- PubMed E-utilities，`esearch db=pubmed datetype=edat reldate=7`，四主题分别检索，MeSH + 自由词
- 输出：每主题一张表（标题、期刊、PMID、一句话结论）
- 缺口：无跨周记录、无预印本源、主题 3 词表窄、无分级和归档字段

## v0.2 改动

| # | 改动 | 理由 | 状态 |
|---|---|---|---|
| 1 | **跨周去重**：以 `data/papers.csv` 的 PMID/DOI 为已归档集合，新候选先剔除 | edat 按收录日计，同一篇在修订、预印本转正式时会重复出现 | ✅ 已验证：本周 10 条候选中 3 条被识别为已归档 |
| 2 | **Europe PMC 预印本通道**：`SRC:PPR` + 放射词 + 肌肉/卫星细胞/FAP/EV 词 + `FIRST_IDATE` 近 7 天 | PubMed 只收部分 bioRxiv（NIH 资助），medRxiv/Research Square 多数不收 | ✅ 接口可用；本周 1 条，判为无关。⚠️ 噪声高，需人工/Agent 摘要筛选 |
| 3 | **主题 3 同义词扩充**：fibroadipogenic、mesenchymal progenitor(s)、muscle stem cell(s)、PDGFRA/PDGFRalpha，并要求同时出现 muscle | FAP 在文献中常以 PDGFRα⁺ 间充质祖细胞出现，原词表会漏 | ✅ 近 365 天回测：v0.1 3 篇 → 加同义词 4 篇 → 再加 PDGFRA 6 篇，增量小且无明显噪声 |
| 4 | **主题 1 肌肉词扩展**：sarcopenia、muscle loss、muscle atrophy、myopathy | 临床研究多用「肌少症」而非 muscle injury | ✅ 本周因此补检到 42997869（肛管癌放化疗肌少症 Meta 分析）；同时带入 3 条无关，需筛选 |
| 5 | **相关度 A/B/C + 精读规则** | 每周条目会累积，必须能快速筛出要读的 | 📋 建议，随运行检验 |
| 6 | **研究类型标注**：临床-前瞻/回顾、系统综述/Meta、动物、体外、类器官、综述 | 综述写作需要按证据层级引用（与整合修复综述的 study design × directness 分级一致） | 📋 建议 |
| 7 | **图谱对接**：涉及 radiation-muscle-pathway 节点（MuSC-FAP-ECM、DNA-redox、血管、免疫、衰老-p21、EV）标「候选入图谱」 | 让周报成为图谱的增量来源，而不是两套独立系统 | 📋 建议；入图谱前仍需全文核对与证据分级 |

另：每月第一个周一生成月度趋势小结（新增篇数、各主题分布、A 级清单、反复出现的研究不足）。理由：单周样本太少（本周 4 篇），趋势要按月看。状态：📋 建议。

## 分级规则

- **A 直接**：放射/放疗 + 骨骼肌（人或动物）为主要研究对象
- **B 相邻**：放射 + 邻近组织（骨、皮肤、软组织）；或骨骼肌 + 放疗人群但肌肉非主终点；或可迁移到肌肉的 EV/递送方法
- **C 背景**：其他组织的放射损伤、方法学、预印本中的间接证据
- **精读**：A 级默认「是」；B 级在方法可借鉴时「选读」；C 级「否」。每周最多推荐 1 篇「本周最值得精读」，优先：放射模型下 EV 治疗肌损伤、新生/年轻供体肌源 EV、FAP 衰老与辐射

## 检索式（v0.2）

```
RAD    = radiation[tiab] OR irradiat*[tiab] OR radiotherap*[tiab] OR "ionizing radiation"[tiab]
         OR "Radiation Injuries"[MeSH] OR "Radiotherapy"[MeSH]
主题1  = RAD AND ("Muscle, Skeletal"[MeSH] OR skeletal muscle OR myofiber* OR myopathy
         OR sarcopenia OR muscle atrophy OR muscle loss)
主题2  = RAD AND (fibrosis OR "radiation-induced fibrosis" OR "Fibrosis"[MeSH])
         AND (muscle OR "Muscle, Skeletal"[MeSH] OR soft tissue OR trismus)
主题3  = RAD AND (satellite cell(s) OR Pax7 OR fibro-adipogenic OR fibroadipogenic
         OR mesenchymal progenitor(s) OR muscle stem cell(s) OR PDGFRA OR PDGFRalpha)
         AND (muscle OR "Muscle, Skeletal"[MeSH])
主题4  = RAD AND ("Extracellular Vesicles"[MeSH] OR "Exosomes"[MeSH]
         OR extracellular vesicle* OR exosome*)
预印本 = Europe PMC: (SRC:PPR) AND (radiation OR irradiation OR radiotherapy)
         AND ("skeletal muscle" OR "satellite cell" OR "fibro-adipogenic" OR "muscle stem cell"
         OR "extracellular vesicle" OR exosome) AND FIRST_IDATE:[近7天]
```
完整实现见 `scripts/weekly-searchv0.2.py`。

## 影响因子规则
- 取 JCR 最新公布值（当前为 JCR 2025，2026-06 发布），先查 `data/journal-if.csv` 缓存；新期刊联网核对后写入缓存并注明来源
- 预印本写「无」；只有 ESCI 的期刊在来源列注明 ESCI

## 已知局限
- 只覆盖 PubMed 与 Europe PMC；Web of Science、Scopus、Embase、中文库不在每周流程内
- 「研究不足」「值得借鉴」基于摘要；A 级文献精读后应回填修正
- edat 窗口会收进发表很早但新近收录的文章（如 42972386 发表于 2026-08-06），表中同时记录发表时间与收录月份
