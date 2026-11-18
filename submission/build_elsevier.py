"""Flatten paper/ into a single elsarticle TeX file with inlined tables and bibliography, PNG figures."""
import re, subprocess, pathlib, shutil
root = pathlib.Path(__file__).resolve().parent.parent
paper = root / "paper"
out = pathlib.Path(__file__).resolve().parent / "computer_networks"
out.mkdir(parents=True, exist_ok=True)

def read(p): return pathlib.Path(p).read_text()

def strip_comments(s):
    return "\n".join(l for l in s.split("\n") if not l.lstrip().startswith("%"))

def inline(s):
    def tab(m): return strip_comments(read(paper / "tables" / (m.group(1) + ".tex"))).strip()
    return re.sub(r"\\input\{tables/([A-Za-z0-9_]+)\}", tab, s)

abs_src = read(paper / "sections/abstract.tex")
abstract = re.search(r"\\begin\{abstract\}.*?\\end\{abstract\}", abs_src, re.S).group(0)
body = "\n\n".join(inline(read(paper / "sections" / f"{n}.tex")) for n in
        ["intro", "related", "model", "algorithm", "analysis", "experiments", "discussion"])
appendix = inline(read(paper / "sections/appendix.tex"))

def wrap_tabulars(s):
    pat = re.compile(r"(?<!\{)\\begin\{tabular\}(.*?)\\end\{tabular\}", re.S)
    return pat.sub(lambda m: "\\resizebox{\\linewidth}{!}{\\begin{tabular}" + m.group(1) + "\\end{tabular}}", s)
png = lambda s: re.sub(r"figures/(fig_[a-z_]+)\.pdf", r"\1.png", s)
def fix_math(s):
    pairs = [
        (r"a_{g,k}\,u_k\!\big(y_{g,k}/a_{g,k}\big)+\big(", r"a_{g,k}\,u_k\!\big(y_{g,k}/a_{g,k}\big)\\&\qquad+\big("),
        (r"\qquad\text{for each }j,", r",\ \forall j,"),
    ]
    for a, b in pairs:
        if a in s: s = s.replace(a, b)
    a = r"\begin{equation}\label{eq:app1}"
    if a in s:
        i = s.index(a); j = s.index(r"\end{equation}", i)
        blk = s[i:j].replace(a, a + r"\begin{aligned}", 1)
        blk = blk.replace(r"-VU_t\le B_0+", r"-VU_t&\le B_0+", 1).replace(r"e^{\mu}_{j,t}+\sum_{i,k}", r"e^{\mu}_{j,t}\\&\quad+\sum_{i,k}", 1) + r"\end{aligned}"
        s = s[:i] + blk + s[j:]
    for a, b in [(r"+\tfrac12N_{\max}|\cK|", r"\allowbreak+\tfrac12N_{\max}|\cK|"),
                 (r"=n[Vw\,u_k(\rmin_k)-\lambda'\rmin_k]>n\,", r"=n[Vw\,u_k(\rmin_k)-\lambda'\rmin_k]\allowbreak>n\,")]:
        if a in s: s = s.replace(a, b)
    return s
body, appendix = fix_math(body), fix_math(appendix)
body, appendix = png(wrap_tabulars(body)), png(wrap_tabulars(appendix))

# figures: 400 dpi PNG
for pdf in sorted((paper / "figures").glob("fig_*.pdf")):
    stem = pdf.stem
    if stem + ".png" not in body: continue
    subprocess.run(["pdftoppm", "-png", "-r", "400", "-singlefile", str(pdf), str(out / stem)], check=True)

macros = read(paper / "main.tex")
macros = macros[macros.index(r"\newtheorem{theorem}"):macros.index(r"\title")]

keywords = "online resource allocation \\sep network utility maximisation \\sep drift-plus-penalty \\sep fairness \\sep envy-freeness \\sep incentive compatibility \\sep quality of service \\sep access networks"

tex = r"""\documentclass[preprint,11pt]{elsarticle}
\usepackage[T1]{fontenc}
\usepackage{amsmath,amssymb,amsthm,mathtools}
\usepackage{booktabs,multirow,array}
\usepackage{graphicx}
\usepackage{algorithm}
\usepackage{algpseudocode}
\usepackage{xcolor}
\usepackage{enumitem}
\usepackage{url}
\biboptions{numbers,sort&compress}
\emergencystretch=2em

""" + macros + r"""
\journal{Computer Networks}

\begin{document}

\begin{frontmatter}

\title{Priority Now, Payback Later: Online Capacity Allocation with Bounded Class Envy for Tiered Internet Access}

\author[buv]{Quang-Vinh Dang\corref{cor1}}
\ead{vinh.dq4@buv.edu.vn}
\ead[url]{https://orcid.org/0000-0002-3877-8024}
\cortext[cor1]{Corresponding author. ORCID: 0000-0002-3877-8024}
\affiliation[buv]{organization={British University Vietnam},
            city={Hung Yen},
            country={Vietnam}}

""" + abstract + r"""

\begin{keyword}
""" + keywords + r"""
\end{keyword}

\end{frontmatter}

""" + body + r"""

\section*{Declaration of competing interest}
The author declares that he has no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

\section*{Data availability}
All code, random seeds and result files needed to reproduce the figures and tables are available at \url{https://github.com/vinhqdang/computer_network_optimization}. The public datasets used in Section~\ref{sec:exp-real} and the subsequent trace-driven scenarios are available from their publishers under the licences stated in the repository.

\section*{CRediT authorship contribution statement}
\textbf{Quang-Vinh Dang}: Conceptualization, Methodology, Software, Validation, Formal analysis, Investigation, Data curation, Writing -- original draft, Writing -- review \& editing, Visualization.

\appendix
""" + appendix + r"""

\begin{thebibliography}{99}
@@BIB@@
\end{thebibliography}

\end{document}
"""
(out / "manuscript.tex").write_text(tex)

# ---- bibliography: run bibtex with elsarticle-num on a temporary copy, inline the resulting .bbl
import tempfile
with tempfile.TemporaryDirectory() as td:
    td = pathlib.Path(td)
    t = (out / "manuscript.tex").read_text()
    t = re.sub(r"\\begin\{thebibliography\}.*?\\end\{thebibliography\}",
               r"\\bibliographystyle{elsarticle-num-names}\n\\bibliography{references}", t, flags=re.S)
    (td / "manuscript.tex").write_text(t)
    bib = (paper / "references.bib").read_text().replace("\u00c9", "{\\'E}")
    (td / "references.bib").write_text(bib)
    [shutil.copy(f, td / f.name) for f in out.glob("*.png")]
    for cmd in (["pdflatex", "-interaction=nonstopmode", "manuscript.tex"], ["bibtex", "manuscript"]):
        subprocess.run(cmd, cwd=td, capture_output=True)
    bbl = (td / "manuscript.bbl").read_text()
inner = re.search(r"\\begin\{thebibliography\}\{[^}]*\}(.*)\\end\{thebibliography\}", bbl, re.S).group(1)
final = (out / "manuscript.tex").read_text().replace("@@BIB@@", inner.strip())
(out / "manuscript.tex").write_text(final)
