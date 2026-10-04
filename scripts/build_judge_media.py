"""Rebuild both submission PDFs with ReportLab, then visually review rendered output."""
from pathlib import Path
from html import escape
import textwrap
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont("DejaVu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuMono", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"))
pdfmetrics.registerFontFamily("DejaVu", normal="DejaVu", bold="DejaVu-Bold", italic="DejaVu", boldItalic="DejaVu-Bold")
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Preformatted

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets'
styles = getSampleStyleSheet()
for name in ["Heading2"]:
    styles[name].fontName = "DejaVu-Bold"
styles.add(ParagraphStyle('SmallBody', fontName='DejaVu', fontSize=9, leading=12, spaceAfter=8))
styles.add(ParagraphStyle('Brand', fontName='DejaVu-Bold', fontSize=30, leading=36, textColor=colors.HexColor('#12304a'), spaceAfter=10))
styles.add(ParagraphStyle('Section', fontName='DejaVu-Bold', fontSize=12, leading=15, spaceBefore=9, spaceAfter=7, textColor=colors.HexColor('#156b81')))


def p(text, style='SmallBody'):
    return Paragraph(text, styles[style])


def footer(canvas, doc):
    canvas.setFont('DejaVu',8)
    canvas.setFillColor(colors.HexColor('#526575'))
    canvas.drawString(36,24,'SentinelRx v0.5 | Synthetic research prototype | athena-kanellatou/sentinelrx')
    canvas.drawRightString(doc.pagesize[0]-36,24,str(doc.page))

story=[p('SentinelRx','Brand'),p('AI-assisted medication review with visible source evidence','Heading2'),
       p('<b>AI reads the note. Rules check the records. The reviewer decides.</b>'),
       p('THE PROBLEM','Section'),
       p('A medication absent from a discharge list could be an error, an intended stop, or incomplete information. The reviewer needs to inspect both the records and the note without treating an AI interpretation as clinical proof.'),
       p('THE WORKING PROTOTYPE','Section'),
       p('<b>1 / Record checks.</b> Deterministic predicates surface potential omissions, additions, duplicate records and dose-text changes. Namespace-safe identity, patient/order checks and source references gate EVIDENCE-CHECKED versus ABSTAIN.'),
       p('<b>2 / Learned note review.</b> A local TF-IDF + logistic-regression model proposes stop, continue, change or start from a short synthetic note. The user supplies the medication link. Exact source text and uncertainty stay visible.'),
       p('<b>3 / Human review.</b> The AI cannot hide, resolve or upgrade a record finding. A reviewer can annotate the comparison and export an audit JSON with source hashes and model version. Counterfactual controls rerun changed synthetic records.'),
       p('MEASURED DEVELOPMENT EVIDENCE','Section'),
       p('<b>78 passing tests.</b> Learned note split: <b>23/24</b> exact outputs including abstention, with proposals on <b>15/24</b> notes. All 15 proposals matched authored labels. One positive case was abstained on. All predictions and data hashes are published.'),
       p('Record suites: 120 generated regression cases, 90 edge/incomplete cases and 32 authored perturbations. These repeat known patterns; their perfect agreement is software regression evidence, not clinical validation.'),
       p('SCOPE AND PRIOR WORK','Section'),
       p('Synthetic data only. Small author-written model corpus and evaluation split, not independent clinical labels. Custom transition tags; assumed list completeness; text-only dose comparison; shared parser/gate assumptions. No autonomous prescribing or clinical effectiveness claim.'),
       p('FHIRGuard predates this work and shares reconciliation, provenance, abstention and constrained-model concepts. This compact implementation adds the local learned note workflow, source-hashed review export and stricter record checks; the underlying concepts are not claimed as new.'),
       p('Project summary, not an application screenshot.'),
       p('<b>Inspect:</b> github.com/athena-kanellatou/sentinelrx<br/><b>Run:</b> python -m streamlit run sentinelrx/ui.py')]
SimpleDocTemplate(str(OUT/'SentinelRx_Judge_OnePager.pdf'),pagesize=A4,rightMargin=40,leftMargin=40,topMargin=30,bottomMargin=38).build(story,onFirstPage=footer,onLaterPages=footer)

code_style=ParagraphStyle('Code',fontName='DejaVuMono',fontSize=7,leading=9)
paths=sorted([*ROOT.glob('sentinelrx/*.py'),*ROOT.glob('scripts/*.py'),*ROOT.glob('tests/*.py'),ROOT/'pyproject.toml',*ROOT.glob('sentinelrx/data/*.json')])
code=[p('SentinelRx - source code','Brand'),p('v0.5 submission snapshot. Canonical, executable source and change history remain in the GitHub repository. This PDF includes package code, scripts, tests, project configuration and authored model data.'),p('github.com/athena-kanellatou/sentinelrx')]
for path in paths:
    code.extend([PageBreak(),p(escape(str(path.relative_to(ROOT))),'Heading2')])
    for number,line in enumerate(path.read_text().splitlines(),1):
        parts=textwrap.wrap(line.expandtabs(4),width=150,replace_whitespace=False,drop_whitespace=False) or ['']
        for i,part in enumerate(parts):
            code.append(Preformatted((f'{number:4}  ' if i==0 else '      ')+part,code_style))
SimpleDocTemplate(str(OUT/'SentinelRx_Code.pdf'),pagesize=landscape(A4),rightMargin=36,leftMargin=36,topMargin=30,bottomMargin=38).build(code,onFirstPage=footer,onLaterPages=footer)
print('Built judge and source PDFs')
