"""Rebuild factual judge media: pip install reportlab; render PDF with pdftoppm."""
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont("MediaSans", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("MediaBold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
from reportlab.lib.colors import HexColor
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from pathlib import Path

OUT = Path('assets/SentinelRx_Judge_OnePager.pdf')
c = canvas.Canvas(str(OUT), pagesize=(960, 640))
c.setTitle('SentinelRx | Evidence before confidence')
c.setFillColor(HexColor('#f1f5fa')); c.rect(0, 0, 960, 640, fill=1, stroke=0)

def text(x, y, value, size=12, color='#213650', width=850, bold=False):
    style = ParagraphStyle('text', fontName='MediaBold' if bold else 'MediaSans', fontSize=size, leading=size*1.38, textColor=HexColor(color))
    p = Paragraph(value, style); w, h = p.wrap(width, 500); p.drawOn(c, x, y-h)

text(40, 605, 'SentinelRx', 40, '#10233f', bold=True)
text(42, 544, 'Evidence-grounded medication-transition review', 20, '#2463b5')
text(42, 508, 'Rules flag discrepancies. Evidence checks gate findings. The clinician decides.', 14)

for x, title, body in [
    (40, '01 / REVIEW', 'Potential omissions, additions, duplicate records and dose-text changes across supplied admission and discharge lists.'),
    (340, '02 / CHECK EVIDENCE', 'Separate deterministic gate checks unique source references, medication identity, transition roles and the discrepancy predicate.'),
    (640, '03 / KNOW THE LIMIT', 'VERIFIED means bundle-local checks passed. It does not establish clinical correctness. Ambiguous evidence triggers ABSTAIN.')]:
    c.setFillColor(HexColor('#ffffff')); c.roundRect(x, 307, 280, 164, 12, fill=1, stroke=0)
    text(x+18, 453, title, 13, '#2463b5', width=244, bold=True)
    text(x+18, 422, body, 12, width=244)

text(42, 285, 'Reproducible software evaluation', 16, bold=True)
text(42, 252, '120 regression cases: F1 1.000 | set-only baseline F1 0.600<br/>90 generated failure cases: exact findings 1.000, abstention 1.000, crashes 0<br/>32 authored perturbations: exact findings 1.000, abstention 1.000, crashes 0', 12, width=560)
text(650, 285, 'Inspect the working demo', 16, bold=True, width=270)
text(650, 252, 'Safety Review / Medication Timeline<br/>Evidence Provenance / Counterfactual Lab<br/>Evaluation + missing-identity scenario', 12, width=270)
text(42, 177, 'Synthetic development tests only. Repeated templates and authored perturbations are not held-out or clinical validation.', 12, '#9b3c24', bold=True)
text(42, 129, 'Scope: active MedicationRequest/MedicationStatement; explicit transition tags; coded identity. No AI/LLM layer, general FHIR validation, prescribing or semantic dose equivalence. Absence assumes supplied lists are complete.', 10, width=865)
text(42, 84, 'Prior work: same problem family and safety principles as FHIRGuard. This separate implementation focuses on interactive review, evidence states and counterfactual testing; the underlying concept is not claimed as new.', 10, width=865)
text(42, 37, 'github.com/athena-kanellatou/sentinelrx  |  Research prototype  |  Media summary, not an application screenshot', 9, '#536579')
c.save()
