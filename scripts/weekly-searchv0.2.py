#!/usr/bin/env python3
"""每周检索 v0.2：PubMed（edat 近 N 天）+ Europe PMC 预印本，跨周按 PMID/DOI 去重。

用法：
    python3 scripts/weekly-searchv0.2.py --days 7 --out candidates.json
输出 candidates.json：每篇候选的主题、PMID、DOI、标题、期刊、日期、文章类型、摘要。
人工/Agent 再阅读摘要，写入 data/papers.csv 与 digests/。
只依赖 Python 标准库。
"""
import argparse, csv, json, os, sys, time, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

RAD = ('(radiation[tiab] OR irradiat*[tiab] OR radiotherap*[tiab] OR "ionizing radiation"[tiab] '
       'OR "Radiation Injuries"[MeSH] OR "Radiotherapy"[MeSH])')
MUSCLE = '("Muscle, Skeletal"[MeSH] OR skeletal muscle[tiab] OR myofiber*[tiab] OR myopathy[tiab] OR sarcopenia[tiab] OR muscle atrophy[tiab] OR muscle loss[tiab])'

TOPICS = {
    "1 放射性骨骼肌损伤": f"{RAD} AND {MUSCLE}",
    "2 放射性肌纤维化": f'{RAD} AND (fibrosis[tiab] OR "radiation-induced fibrosis"[tiab] OR "Fibrosis"[MeSH]) '
                         f'AND (muscle[tiab] OR "Muscle, Skeletal"[MeSH] OR soft tissue[tiab] OR trismus[tiab])',
    "3 卫星细胞/FAPs 与辐射": f'{RAD} AND (satellite cell[tiab] OR satellite cells[tiab] OR Pax7[tiab] '
                         'OR fibro-adipogenic[tiab] OR fibroadipogenic[tiab] OR mesenchymal progenitor[tiab] '
                         'OR mesenchymal progenitors[tiab] OR muscle stem cell[tiab] OR muscle stem cells[tiab] '
                         'OR PDGFRA[tiab] OR PDGFRalpha[tiab]) AND (muscle[tiab] OR "Muscle, Skeletal"[MeSH])',
    "4 EV/外泌体治疗放射损伤": f'{RAD} AND ("Extracellular Vesicles"[MeSH] OR "Exosomes"[MeSH] '
                         'OR extracellular vesicle*[tiab] OR exosome*[tiab])',
}

EPMC_QUERY = ('(SRC:PPR) AND (radiation OR irradiation OR radiotherapy) AND '
              '("skeletal muscle" OR "satellite cell" OR "fibro-adipogenic" OR "muscle stem cell" '
              'OR "extracellular vesicle" OR exosome) AND FIRST_IDATE:[{a} TO {b}]')


def get(url, params):
    q = url + "?" + urllib.parse.urlencode(params)
    for i in range(3):
        try:
            with urllib.request.urlopen(q, timeout=40) as r:
                return r.read().decode("utf-8")
        except Exception:
            time.sleep(2 * (i + 1))
    raise RuntimeError("request failed: " + q)


def seen_ids():
    p = os.path.join(ROOT, "data", "papers.csv")
    ids = set()
    if os.path.exists(p):
        with open(p, encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                if r.get("PMID"): ids.add(r["PMID"].strip())
                if r.get("DOI"): ids.add(r["DOI"].strip().lower())
    return ids


def pubmed(days):
    hits = {}
    for topic, term in TOPICS.items():
        js = json.loads(get(EUTILS + "esearch.fcgi", {"db": "pubmed", "datetype": "edat", "reldate": days,
                                                      "retmax": 200, "retmode": "json", "term": term}))
        for pmid in js["esearchresult"]["idlist"]:
            hits.setdefault(pmid, []).append(topic)
        time.sleep(0.4)
    out = []
    if not hits:
        return out, ""
    ids = ",".join(hits)
    summ = json.loads(get(EUTILS + "esummary.fcgi", {"db": "pubmed", "id": ids, "retmode": "json"}))["result"]
    abst = get(EUTILS + "efetch.fcgi", {"db": "pubmed", "id": ids, "rettype": "abstract", "retmode": "text"})
    for pmid, topics in hits.items():
        r = summ.get(pmid, {})
        doi = next((a["value"] for a in r.get("articleids", []) if a["idtype"] == "doi"), "")
        out.append({"source": "PubMed", "topics": topics, "pmid": pmid, "doi": doi,
                    "title": r.get("title", ""), "journal": r.get("fulljournalname", ""),
                    "pubdate": r.get("pubdate", ""), "pubtype": r.get("pubtype", []),
                    "first_author": (r.get("authors") or [{}])[0].get("name", "")})
    return out, abst


def europepmc(days):
    import datetime
    b = datetime.date.today(); a = b - datetime.timedelta(days=days)
    js = json.loads(get(EPMC, {"query": EPMC_QUERY.format(a=a, b=b), "format": "json",
                               "pageSize": 100, "resultType": "core"}))
    out = []
    for r in js.get("resultList", {}).get("result", []):
        out.append({"source": "EuropePMC-preprint", "topics": ["待人工分配"], "pmid": r.get("pmid", ""),
                    "doi": r.get("doi", ""), "title": r.get("title", ""),
                    "journal": (r.get("bookOrReportDetails") or {}).get("publisher", "preprint"),
                    "pubdate": r.get("firstPublicationDate", ""), "pubtype": ["Preprint"],
                    "first_author": (r.get("authorString") or "").split(",")[0],
                    "abstract": r.get("abstractText", "")})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--out", default="candidates.json")
    a = ap.parse_args()
    seen = seen_ids()
    pm, abst = pubmed(a.days)
    pp = europepmc(a.days)
    pm_dois = {x["doi"].lower() for x in pm if x["doi"]}
    pp = [x for x in pp if x["doi"].lower() not in pm_dois and x["pmid"] not in {y["pmid"] for y in pm}]
    allc = pm + pp
    new = [x for x in allc if x["pmid"] not in seen and (not x["doi"] or x["doi"].lower() not in seen)]
    dup = len(allc) - len(new)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump({"days": a.days, "n_pubmed": len(pm), "n_preprint": len(pp), "n_already_archived": dup,
                   "candidates": new, "pubmed_abstracts_text": abst}, f, ensure_ascii=False, indent=1)
    print(f"PubMed {len(pm)} | 预印本 {len(pp)} | 已归档跳过 {dup} | 新候选 {len(new)} -> {a.out}")


if __name__ == "__main__":
    sys.exit(main())
