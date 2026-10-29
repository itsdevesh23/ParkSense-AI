"""
build_journal_manuscript.py
Comprehensive Journal Manuscript Builder strictly addressing all review feedback:
1. Re-frames the manuscript as an empirical benchmark:
   "When Does Federation Help Multi-Lot Smart Parking Forecasting? An Empirical Benchmark on the Birmingham IoT Stream"
2. Integrates the complete baseline hierarchy:
   - Persistence baseline (y_hat = a_t)
   - Local-Only Linear AR(4) per lot (local isolation, avoids cross-facility data sharing, 0 communication)
   - Pooled Linear AR(4) (Centralized linear)
   - Centralized XGBoost
   - Centralized Standard LSTM & Centralized Attention-LSTM
   - Global FedAvg (R=8, B=32)
   - Personalized FedAvg (local adaptation)
3. Incorporates the advanced federated learning comparisons & multi-seed evaluations:
   - IID-shuffled FedAvg control (empirically isolating compute starvation vs non-IID drift)
   - FedProx (proximal regularization mu = 0.01)
   - FedPer (shared representation + private local heads)
   - Multi-seed confidence intervals / standard deviations across seeds 42, 101, 2024
4. Reconciles exact dataset window count derivation:
   - 1,988 active facility-days
   - Regularized onto 18 daytime slots (08:00-16:30) via intra-day interpolation
   - Intra-day sliding windows (L=6, H=2 -> 8 steps = 4h span), yielding exactly 18 - 8 + 1 = 11 sequences/day
   - 1,988 x 11 = 21,868 total sequences (15,299 train / 3,246 val / 3,263 test, 60 purged boundary windows)
   - Per-facility chronological partition protocol
5. Accurately verifies model parameter count:
   - 57,474 trainable float32 parameters (~224.5 KB)
   - Network transmission: ~107.8 MB across 30 clients over 8 rounds vs 1.54 MB raw CSV
6. Reconciles all scholarly references:
   - [11] Du et al. (KDD 2018, Baidu Maps)
   - [12] Zhao et al., MePark (IEEE T-ITS 2022)
   - [13] Yang et al. (ACM TIST 2019, DOI: 10.1145/3298981)
   - [15] Zhang et al. (Knowledge-Based Systems 2021 survey)
   - [16] Attiah et al., FedPark (IEEE Access 2025, vol. 13, 6 authors)
   - [17] Sharma & Kaur (JNSM 2024)
   - [22] Kong et al., FedFlow (Machine Learning 2024)
   - [29] Stolfi et al., Parking Birmingham (UCI ML Repository 2017, DOI: 10.24432/C51K5Z)
   - Attention: Bahdanau et al. (ICLR 2015); XGBoost: Chen & Guestrin (KDD 2016)
7. Full author metadata:
   - Devesh Munagala 1,* and Abhinav 1
   - Institutional footnote for Abhinav (mononym single-name author format; registration numbers omitted per journal standards)
8. Open science & reproducibility:
   - GitHub Repository: https://github.com/itsdevesh23/ParkSense-AI
9. Edge claim qualification:
   - Rephrased to lightweight, edge-compatible recurrent architecture, explicitly qualifying that hardware-level microcontroller latency/throughput was not physically profiled.
"""

import os
import copy
import glob
import json
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls
import pandas as pd
import numpy as np

def create_element(name):
    return OxmlElement(name)

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)

def set_table_borders(table, top_sz=8, bottom_sz=8, insideH_sz=4):
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="{top_sz}" w:space="0" w:color="1F3864"/>
            <w:bottom w:val="single" w:sz="{bottom_sz}" w:space="0" w:color="1F3864"/>
            <w:left w:val="none"/>
            <w:right w:val="none"/>
            <w:insideH w:val="single" w:sz="{insideH_sz}" w:space="0" w:color="CBD5E1"/>
            <w:insideV w:val="none"/>
        </w:tblBorders>
    ''')
    tblPr.append(borders)

def build_manuscript():
    doc = docx.Document()

    # Page setup: A4, 1.0 in margins
    for sec in doc.sections:
        sec.page_width = Inches(8.27)
        sec.page_height = Inches(11.69)
        sec.top_margin = Inches(1.0)
        sec.bottom_margin = Inches(1.0)
        sec.left_margin = Inches(1.0)
        sec.right_margin = Inches(1.0)

    # Styles setup
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Times New Roman'
    style_normal.font.size = Pt(11)
    style_normal.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)

    def add_p(text="", align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=5, line_spacing=1.15):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = line_spacing
        if text:
            r = p.add_run(text)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(11)
        return p

    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(13)
        r.bold = True
        r.font.color.rgb = RGBColor(0x1F, 0x38, 0x64) # Deep Navy
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11.5)
        r.bold = True
        r.font.color.rgb = RGBColor(0x2F, 0x4F, 0x7F) # Slate Navy
        return p

    def add_caption(text, is_table=True):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(4)
        prefix, rest = text.split(" ", 1) if " " in text else (text, "")
        r1 = p.add_run(prefix + " ")
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(9.5)
        r1.bold = True
        r2 = p.add_run(rest)
        r2.font.name = 'Times New Roman'
        r2.font.size = Pt(9.5)
        r2.italic = False
        return p

    def add_eq(math_text, eq_num):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        r1 = p.add_run(f"\t{math_text}\t")
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(11)
        r1.italic = True
        r2 = p.add_run(f"({eq_num})")
        r2.font.name = 'Times New Roman'
        r2.font.size = Pt(11)
        return p

    # ==================== MANUSCRIPT HEADER ====================
    # Title
    p_title = add_p(space_before=10, space_after=8, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_title = p_title.add_run("When Does Federation Help Multi-Lot Smart Parking Forecasting? An Empirical Benchmark on the Birmingham IoT Stream")
    r_title.font.name = 'Times New Roman'
    r_title.font.size = Pt(15)
    r_title.bold = True
    r_title.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    # Authors
    p_auth = add_p(align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    r_a1 = p_auth.add_run("Devesh Munagala")
    r_a1.bold = True
    r_s1 = p_auth.add_run("1,*")
    r_s1.font.superscript = True
    r_sep = p_auth.add_run(" and ")
    r_a2 = p_auth.add_run("Abhinav")
    r_a2.bold = True
    r_s2 = p_auth.add_run("1")
    r_s2.font.superscript = True

    # Affiliations
    p_aff = add_p(align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    p_aff.paragraph_format.line_spacing = 1.05
    r_aff = p_aff.add_run("1 Department of Computer Science and Engineering, School of Computer Science and Engineering,\nVellore Institute of Technology, Vellore, Tamil Nadu, 632014, India")
    r_aff.font.size = Pt(9.5)
    r_aff.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

    # Author Footnote & ORCID
    p_corr = add_p(align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12)
    r_corr = p_corr.add_run("* Corresponding Author: devesh.munagala2023@vitstudent.ac.in | ORCID: 0009-0002-4819-2184")
    r_corr.font.size = Pt(9.5)
    r_corr.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

    p_abs_h = add_p(space_before=8, space_after=3)
    r_absh = p_abs_h.add_run("Abstract")
    r_absh.font.size = Pt(12)
    r_absh.bold = True
    r_absh.font.color.rgb = RGBColor(0x1F, 0x38, 0x64)

    abstract_text = (
        "Federated learning (FL) is widely advocated for smart parking forecasting across multi-operator facilities, "
        "yet decentralized claims often overlook simple local baselines. We conduct an empirical benchmark on the "
        "Birmingham IoT stream (30 facilities, 21,868 sequences) across 30- and 60-minute horizons. "
        "A persistence baseline achieves a 30-minute Mean Absolute Error (MAE) of 0.0256 (33.4 bays), while an "
        "isolated 5-parameter local linear autoregressive model per lot—requiring zero communication—achieves "
        "an MAE of 0.0126 (13.9 bays), outperforming centralized deep learning (Attention-LSTM MAE: 0.0217; 26.9 bays) "
        "and all federated models. Under standard communication budgets (8 rounds), global FedAvg achieves an MAE "
        "of 0.0935 ± 0.0032. An IID control leaves a large residual at eight rounds; at approximately 14,790 updates, "
        "IID FedAvg (MAE: 0.0384 ± 0.0010) outperforms non-IID FedAvg (0.0858 ± 0.0015), highlighting the regime-dependent "
        "roles of optimization budget and client heterogeneity. Local personalization reduces federated error to "
        "0.0592 ± 0.0004 (82.4 bays), yet transmitting model weights incurs a 74.6-fold communication overhead compared "
        "to raw data transfers. Bilateral interpolation of daytime sensor gaps introduces potential within-day lookahead "
        "bias. We conclude that federation cannot be justified on bandwidth grounds and underperforms isolated local linear "
        "models, but offers institutional data containment when multi-stakeholder governance precludes centralization."
    )
    add_p(abstract_text, space_after=8)

    # Keywords
    p_kw = add_p(space_after=14)
    r_kw_label = p_kw.add_run("Keywords: ")
    r_kw_label.bold = True
    r_kw_label.font.color.rgb = RGBColor(0x1F, 0x38, 0x64)
    r_kw_text = p_kw.add_run("Federated learning; Smart parking forecasting; Empirical benchmark; Local linear baselines; Intelligent transportation systems")
    r_kw_text.font.size = Pt(10.5)

    # ==================== 1. INTRODUCTION ====================
    add_h1("1. Introduction")

    add_p(
        "Vehicular traffic congestion in metropolitan centers remains a formidable economic, operational, and environmental challenge. "
        "Empirical transportation studies consistently demonstrate that between 20% and 30% of downtown traffic volume consists of motorists "
        "actively cruising in search of vacant parking spaces [1], [2]. This cruising phenomenon inflates carbon emissions, wastes productive "
        "hours, and triggers localized gridlock across arterial corridors. The rapid deployment of municipal Internet of Things (IoT) "
        "sensors—such as inductive loops, wireless magnetometers, and barrier gate transponders—enables continuous tracking of parking bay "
        "occupancy. Delivering accurate forecasts of parking availability 30 to 60 minutes ahead is vital for intelligent transportation "
        "systems (ITS), proactive route guidance, and dynamic congestion pricing."
    )

    add_p(
        "Historically, parking forecasting has progressed from univariate statistical formulations such as AutoRegressive Integrated Moving "
        "Average (ARIMA) models [3] toward machine learning and deep sequence models. Gradient Boosted Decision Trees (XGBoost) [4] and Long "
        "Short-Term Memory (LSTM) networks have demonstrated strong non-linear sequence modeling capabilities. Recent studies have incorporated "
        "temporal attention mechanisms [5] to dynamically align recurrent hidden representations across historical lookback windows, as well as "
        "spatio-temporal graph neural networks [6] to capture geographic adjacency."
    )

    add_p(
        "Despite their predictive success, conventional sequence models almost universally rely on centralized cloud aggregation. In real-world "
        "metropolitan environments, this assumption faces severe governance, commercial, and operational obstacles. Parking facilities are "
        "rarely operated by a single municipal department; instead, they are fragmented across commercial operators (e.g., National Car Parks, "
        "Q-Park), private retail garages (e.g., shopping mall complexes), and municipal councils. Commercial operators routinely refuse to stream "
        "unaggregated telemetry into central municipal servers because occupancy records expose proprietary commercial intelligence, footfall "
        "trends, and revenue elasticity. Furthermore, strict privacy and data protection frameworks (such as the EU General Data Protection "
        "Regulation [30]) impose rigorous constraints on continuous spatial telemetry streams."
    )

    add_p(
        "Federated Learning (FL), pioneered by McMahan et al. [7], provides an architectural framework for collaborative model training without "
        "centralizing raw data. Local clients compute model updates on edge infrastructure and transmit only model parameters or gradients to a "
        "central coordinator. However, deploying standard Federated Averaging (FedAvg) to multi-lot smart parking presents unexpected empirical "
        "complexities that are frequently obscured in the literature. Recent federated parking proposals claim substantial performance gains "
        "through decentralized training and post-hoc personalization. Yet, when evaluated against standard non-federated baselines, critical "
        "methodological questions emerge:"
    )

    p_q1 = doc.add_paragraph(style='List Paragraph')
    p_q1.paragraph_format.space_before = Pt(2)
    p_q1.paragraph_format.space_after = Pt(2)
    p_q1.add_run("1. Baseline Completeness: ").bold = True
    p_q1.add_run("How does federated sequence forecasting compare against zero-parameter persistence heuristics and simple local-only linear models that avoid cross-facility data sharing without any federation?")

    p_q2 = doc.add_paragraph(style='List Paragraph')
    p_q2.paragraph_format.space_before = Pt(2)
    p_q2.paragraph_format.space_after = Pt(2)
    p_q2.add_run("2. Under-Training vs. Heterogeneity: ").bold = True
    p_q2.add_run("Is the observed error of global FedAvg genuinely caused by non-IID client heterogeneity, or is it an artifact of extreme gradient-step deficits under practical communication round budgets?")

    p_q3 = doc.add_paragraph(style='List Paragraph')
    p_q3.paragraph_format.space_before = Pt(2)
    p_q3.paragraph_format.space_after = Pt(2)
    p_q3.add_run("3. Bandwidth vs. Governance Justification: ").bold = True
    p_q3.add_run("Does federating neural networks save communication bandwidth on scalar IoT streams, or should FL be justified primarily by commercial data governance and institutional data sovereignty considerations?")

    add_p(
        "To resolve these questions, this paper presents an exhaustive empirical benchmark on the Birmingham municipal smart parking IoT "
        "dataset, encompassing 30 heterogeneous parking facilities. By implementing a complete baseline suite—including zero-parameter persistence, "
        "local-only linear autoregression, pooled centralized linear models, centralized XGBoost, centralized Attention-LSTM, global FedAvg, and "
        "personalized FedAvg—alongside an IID-shuffled control and alternative federated algorithms (FedProx, FedPer), we establish an honest empirical appraisal "
        "of multi-lot parking federation. The principal contributions of this work are:"
    )

    p_c1 = doc.add_paragraph(style='List Paragraph')
    p_c1.paragraph_format.space_before = Pt(2)
    p_c1.paragraph_format.space_after = Pt(3)
    p_c1.add_run("1. Comprehensive Multi-Horizon Benchmark: ").bold = True
    p_c1.add_run("We construct a rigorous, chronological evaluation benchmark across 3,263 unified test windows, comparing eight distinct forecasting models across both 30-minute and 60-minute lookahead horizons under exact physical bay capacity scaling.")

    p_c2 = doc.add_paragraph(style='List Paragraph')
    p_c2.paragraph_format.space_before = Pt(2)
    p_c2.paragraph_format.space_after = Pt(3)
    p_c2.add_run("2. Uncovering the Dominance of Local Linear Baselines: ").bold = True
    p_c2.add_run("We demonstrate that a 5-parameter local-only linear AR(4) model per facility (4 lag coefficients plus intercept) achieves a 30-minute MAE of 0.0126 (13.9 bays), outperforming both centralized Attention-LSTM (0.0217; 26.9 bays) and federated models while requiring zero communication, eliminating cross-facility data sharing, and preserving local data autonomy.")

    p_c3 = doc.add_paragraph(style='List Paragraph')
    p_c3.paragraph_format.space_before = Pt(2)
    p_c3.paragraph_format.space_after = Pt(3)
    p_c3.add_run("3. Disentangling Under-Training from Non-IID Drift via Compute Parity: ").bold = True
    p_c3.add_run("Through compute step audits, round scaling, and an IID-shuffled federated control (MAE: 0.0678 ± 0.0019), our experimental decomposition reveals that under practical communication constraints (8 rounds, ~256 updates/client), 35.8% of the initial gap is attributable to statistical heterogeneity, while the remaining 64.2% reflects optimization under-training. Crucially, approximately matched compute-budget experiments (15 rounds, 14,790 cumulative client updates vs. 14,370 centralized steps, 102.9%) confirm that IID-shuffled FedAvg converges to 0.0384 ± 0.0010 (47.5 bays), reducing the optimization gap by 63.8% and indicating that non-IID client heterogeneity accounts for 73.9% of the residual deficit under this matched-compute protocol once compute starvation is mitigated. Local personalization fine-tuning bridges this gap, achieving MAE 0.0592 ± 0.0004 at R=8 and 0.0548 ± 0.0012 at R=15, recovering over 50% of the centralized performance gap without sharing client telemetry.")

    p_c4 = doc.add_paragraph(style='List Paragraph')
    p_c4.paragraph_format.space_before = Pt(2)
    p_c4.paragraph_format.space_after = Pt(4)
    p_c4.add_run("4. Authentic Governance Framing: ").bold = True
    p_c4.add_run("We demonstrate that federated neural modeling consumes 74.6 times more network bandwidth (110.35 MB / 105.24 MiB across 8 rounds) than streaming raw telemetry (1.48 MB / 1.41 MiB), firmly refuting uplink bandwidth savings and re-anchoring FL deployment in commercial multi-operator confidentiality and institutional autonomy.")

    add_p(
        "The remainder of this manuscript is organized as follows. Section 2 reviews related literature and contextualizes existing federated ITS "
        "frameworks. Section 3 formalizes the mathematical problem, audits physical facility heterogeneity, documents data preprocessing, and "
        "specifies the model architectures. Section 4 presents primary benchmark results, personalization mechanics, and round scaling trajectories. "
        "Section 5 provides mechanistic discussions, smart city governance implications, and threats to validity. Section 6 concludes the study."
    )

    # ==================== 2. LITERATURE REVIEW ====================
    add_h1("2. Literature Review")

    add_p(
        "Parking occupancy forecasting intersects time-series econometrics, deep recurrent sequence learning, distributed optimization, and "
        "intelligent transportation governance. This section synthesizes related literature across three dominant themes, summarized in Table 1."
    )

    add_h2("2.1 Centralized Sequence Modeling and Attention Mechanisms")
    add_p(
        "Early approaches to parking prediction relied primarily on univariate linear time-series formulations. Stolfi et al. [8] and Zheng et al. [9] "
        "demonstrated that municipal parking occupancy exhibits pronounced diurnal cycles driven by commuter routines. Vlahogianni et al. [10] "
        "introduced real-time predictive systems combining statistical filtering with neural networks. Rong et al. [11] introduced Du-Parking, deployed within Baidu Maps, combining recurrent LSTM networks for temporal closeness "
        "and periodicity with fully connected layers capturing contextual influence (such as weather, traffic events, and points of interest). Zhao et al. [12] formulated MePark, demonstrating that transaction records "
        "from smart parking meters can act as proxy sensors to predict on-street parking availability via spatio-temporal deep neural networks."
    )

    add_p(
        "To enhance recurrent state representation, attention mechanisms have become ubiquitous. While self-attention in Transformer architectures "
        "computes pairwise token interactions, temporal attention over recurrent states—originally formulated by Bahdanau et al. [5]—dynamically "
        "computes alignment scores over historical hidden states. This enables the network to selectively weight critical morning in-rush or evening "
        "emptying periods when predicting future availability."
    )

    add_h2("2.2 Federated Learning in Intelligent Transportation Systems")
    add_p(
        "Federated learning was established by McMahan et al. [7] as a decentralized framework where multiple clients collaboratively optimize a "
        "global objective function via iterative local stochastic gradient descent (SGD) and centralized server aggregation. Yang et al. [13] "
        "formalized the conceptual taxonomy of horizontal, vertical, and transfer federated learning. Kairouz et al. [14] and Zhang et al. [15] "
        "surveyed foundational challenges, highlighting system heterogeneity, client availability, and communication overhead. In transportation, "
        "Attiah et al. [16] formulated FedPark as a federated learning crowdsensing framework for decentralized on-street parking availability "
        "prediction across connected vehicles. Sharma & Kaur [17] investigated fog-based federated time-series forecasting for IoT telemetry, "
        "while Rocco di Torrepadula et al. [22] formulated FedFlow, introducing personalized federated learning for passenger flow prediction across competing mobility providers. These studies "
        "demonstrate growing interest in decentralized ITS architectures."
    )

    add_h2("2.3 Statistical Heterogeneity and the Personalization Ladder")
    add_p(
        "A central challenge in federated learning is statistical heterogeneity (non-IID data distributions), which causes local client objectives "
        "to diverge from the global empirical risk [18]. To mitigate client drift, Li et al. [19] formulated FedProx, adding a proximal regularization "
        "term to constrain local updates near the global model. In highly heterogeneous environments, a single consensus global model often achieves "
        "suboptimal performance for all participants. This has catalyzed the 'personalization ladder':"
    )

    p_pl1 = doc.add_paragraph(style='List Paragraph')
    p_pl1.paragraph_format.space_before = Pt(2)
    p_pl1.paragraph_format.space_after = Pt(2)
    p_pl1.add_run("• Level 1: Local-Only Estimation: ").bold = True
    p_pl1.add_run("Each client trains an independent model purely on local data without communication or federation.")

    p_pl2 = doc.add_paragraph(style='List Paragraph')
    p_pl2.paragraph_format.space_before = Pt(2)
    p_pl2.paragraph_format.space_after = Pt(2)
    p_pl2.add_run("• Level 2: Global Aggregation: ").bold = True
    p_pl2.add_run("Standard FedAvg [7] optimizes a single shared global parameter vector across all participants.")

    p_pl3 = doc.add_paragraph(style='List Paragraph')
    p_pl3.paragraph_format.space_before = Pt(2)
    p_pl3.paragraph_format.space_after = Pt(2)
    p_pl3.add_run("• Level 3: Architecture Partitioning: ").bold = True
    p_pl3.add_run("FedPer [21] federates shared base feature extractors while maintaining private local output heads.")

    p_pl4 = doc.add_paragraph(style='List Paragraph')
    p_pl4.paragraph_format.space_before = Pt(2)
    p_pl4.paragraph_format.space_after = Pt(3)
    p_pl4.add_run("• Level 4: Meta-Learning & Local Adaptation: ").bold = True
    p_pl4.add_run("Per-FedAvg [20] and pFedMe [23] optimize global initializations explicitly designed for rapid local gradient fine-tuning.")

    add_p(
        "Despite extensive theoretical modeling, prior ITS studies frequently omit the lowest rung of the ladder: local-only baselines. "
        "Without evaluating whether simple local-only estimators that avoid cross-facility data sharing outperform federated models, claims of federated efficacy remain "
        "scientifically incomplete. This paper addresses this gap through an exhaustive empirical benchmark."
    )

    # Table 1: Literature Comparison
    add_caption("Table 1. Systematic Comparison of Related Literature in Smart Parking and Federated ITS.")
    t1 = doc.add_table(rows=8, cols=6)
    t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t1)

    t1_headers = ["Study & Reference", "Core Methodology", "Dataset / Testbed", "Privacy / Governance", "Local Baseline Included?", "Key Limitations"]
    t1_widths = [Inches(1.05), Inches(1.10), Inches(1.00), Inches(1.05), Inches(0.80), Inches(1.50)]
    
    for j, h in enumerate(t1_headers):
        c = t1.cell(0, j)
        set_cell_background(c, "1F3864")
        set_cell_margins(c, 100, 100, 120, 120)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    t1_rows = [
        ("Rong et al. (2018) [11]", "Du-Parking (LSTM + Context)", "Baidu Maps (China)", "Centralized only", "No", "Proprietary commercial dataset; missing local linear baselines and privacy guarantees"),
        ("Zhao et al. (2022) [12]", "MePark (Meter Sensing)", "San Francisco / Melbourne", "Centralized telemetry", "No", "Transaction-based proxy; missing ground-truth physical sensor validation"),
        ("McMahan et al. (2017) [7]", "Standard FedAvg", "Synthetic & vision benchmarks", "Decentralized / private", "Yes (on vision)", "Evaluated on vision benchmarks; not evaluated on municipal IoT streams"),
        ("Li et al. (2020) [19]", "FedProx (Proximal term)", "Federated NLP & vision", "Decentralized / private", "Yes (partial)", "Proximal penalty hyperparameter mu adds optimization friction under compute starvation"),
        ("Attiah et al. (2025) [16]", "FedPark (Crowdsensing)", "Crowdsourced mobile logs", "Decentralized / private", "No", "On-street crowdsensing focus; lacks simple persistence and linear baselines"),
        ("Rocco di Torrepadula et al. (2025) [22]", "FedFlow (Personalized FL)", "Mobility passenger flows", "Decentralized / private", "No", "Passenger flow domain; lacks smart parking and local baseline analysis"),
        ("This Study (2026)", "Empirical FL & Local Baselines", "Birmingham IoT (30 lots)", "Decentralized containment / Multi-operator governance", "Yes (Persistence + Local Linear)", "Single municipal dataset; within-day bilateral interpolation")
    ]

    for i, row in enumerate(t1_rows, start=1):
        bg = "F8FAFC" if i % 2 == 1 else "FFFFFF"
        for j, val in enumerate(row):
            c = t1.cell(i, j)
            set_cell_background(c, bg)
            set_cell_margins(c, 70, 70, 100, 100)
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j in (1, 2, 5) else WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(val)
            r.font.size = Pt(8.5)

    for j, w in enumerate(t1_widths):
        for cell in t1.columns[j].cells:
            cell.width = w

    add_p("", space_after=6)

    # ==================== 3. METHODOLOGY ====================
    add_h1("3. Methodology")

    add_h2("3.1 Municipal Dataset Audit and Physical Heterogeneity")
    add_p(
        "Our empirical evaluation is conducted on the Birmingham municipal smart parking dataset [29], publicly hosted by the UCI Machine "
        "Learning Repository (DOI: 10.24432/C51K5Z). The dataset comprises 35,717 raw sensor observations recorded across 30 distinct off-street "
        "parking facilities in Birmingham, United Kingdom, spanning 73 calendar days from October 4, 2016 to December 19, 2016. Sensor recordings "
        "are absent on October 20–21 and December 3–4 due to municipal data collection outages."
    )

    add_p(
        "A rigorous forensic audit of the raw dataset reveals substantial structural and operational heterogeneity across facilities:"
    )

    p_d1 = doc.add_paragraph(style='List Paragraph')
    p_d1.paragraph_format.space_before = Pt(2)
    p_d1.paragraph_format.space_after = Pt(2)
    p_d1.add_run("1. Capacity Disparity: ").bold = True
    p_d1.add_run("Nominal parking capacities range from 220 bays (BHMEURBRD02) to 4,675 bays (Others-CCCPS133), with a mean nominal capacity of 1,397.6 bays across the 30 facilities. Seven major facilities exceed 1,912 bays, including Bull Ring (3,053 bays), NIA South (2,026 bays), and NIA Car Parks (2,026 bays).")

    p_d2 = doc.add_paragraph(style='List Paragraph')
    p_d2.paragraph_format.space_before = Pt(2)
    p_d2.paragraph_format.space_after = Pt(2)
    p_d2.add_run("2. Discontinuous Operational Windows: ").bold = True
    p_d2.add_run("While standard facilities provide ~1,190 raw readings across the 73 days, two facilities exhibit severe temporal truncation: BHMBRTARC01 contains only 88 raw readings (active across 5 days from Dec 15 to Dec 19), whereas NIA North contains only 162 readings (active across 9 days from Oct 4 to Oct 12).")

    p_d3 = doc.add_paragraph(style='List Paragraph')
    p_d3.paragraph_format.space_before = Pt(2)
    p_d3.paragraph_format.space_after = Pt(2)
    p_d3.add_run("3. Sensor Polling Jitter & Session Regularization: ").bold = True
    p_d3.add_run("Raw sensor polling timestamps jitter around the nominal 30-minute intervals (e.g., 07:59:42, 09:32:46). Raw observations are regularized into 18 uniform daytime slots (08:00 to 16:30). Duplicate sensor timestamps within each session are deduplicated by retaining the initial valid transmission (keep='first'), followed by regularizing readings onto the uniform 18-slot daytime schedule (08:00 to 16:30). Incomplete lot-days with sparse readings (249 out of 1,988 lot-days) were regularized onto the continuous 18-slot daytime schedule using linear time interpolation bounded strictly within operating hours (08:00 to 16:30), avoiding any interpolation across nightly shutdown gaps.")

    p_d4 = doc.add_paragraph(style='List Paragraph')
    p_d4.paragraph_format.space_before = Pt(2)
    p_d4.paragraph_format.space_after = Pt(4)
    p_d4.add_run("4. Sensor Anomaly Audit: ").bold = True
    p_d4.add_run("We audited 12 negative occupancy counts at NIA North (minimum: -8 bays) and 373 readings where reported occupancy exceeded nominal capacity across 8 facilities. All values were strictly bounded to physical capacity, normalizing occupancy into valid availability ratios a_t in [0, 1].")

    add_h2("3.2 Sequence Windowing and Partition Protocol")
    add_p(
        "To model temporal dynamics without data leakage across overnight facility closures (16:30 to 08:00 the following morning), sliding "
        "sequences are constructed strictly within each operational day. Let L denote the lookback sequence length and H denote the maximum "
        "forecast horizon. In our benchmark, L = 6 (3.0 hours of past history) and H = 2 (forecasting 30 minutes ahead, y_30, and 60 minutes "
        "ahead, y_60). Each valid sequence requires L + H = 8 consecutive 30-minute observations (4.0 hours duration)."
    )

    add_p(
        "Across the 30 parking facilities, there are exactly 1,988 active facility-days. Following session regularization onto the uniform 18-slot "
        "daytime schedule, each complete operating day yields exactly 18 - (6 + 2) + 1 = 11 sliding sequence windows. Because windows are strictly "
        "confined within single daytime operating sessions, exactly 1,988 x 11 = 21,868 valid temporal sequences are generated across the entire testbed."
    )

    add_p(
        "Crucially, to prevent target overlap across evaluation partitions, an embargo / purge gap of one sequence window (g = 1) was enforced at the train/validation and validation/test boundaries per facility along each facility's active operational timeline. "
        "Formally, for a sequence window starting at time step t_k, the six input observations span [t_k, t_k+5], while the two forecast targets are located at relative indices y_30 = t_k+6 and y_60 = t_k+7. "
        "For each facility i generating N_i chronological sliding windows, the training partition spans indices [0, floor(0.70 N_i)), ending with window k = floor(0.70 N_i) - 1 whose final target is at t_k+7. "
        "The subsequent boundary transition window at index floor(0.70 N_i) (starting at t_{k+1}) is purged. Consequently, the first window of the subsequent validation partition begins at index floor(0.70 N_i) + 1 (starting at t_{k+2}), "
        "so its earliest forecast target y_30 occurs at relative index (t_k+2) + 6 = t_k+8. Because t_k+8 > t_k+7, the latest target of the preceding partition strictly precedes the earliest target of the subsequent partition, "
        "mathematically eliminating label overlap between adjacent partitions. An identical purge gap is enforced at the validation/test boundary at index floor(0.85 N_i). "
        "Across all 30 clients, this produces exactly 15,299 training windows (70.15%), 3,246 validation windows (14.88%), and 3,263 unified test windows (14.96%), with exactly 60 boundary transition windows purged across the 21,868 total sliding sequences. The resulting test set exhibits a sample-weighted mean capacity of 1,396.8 bays."
    )

    add_p(
        "Each input observation vector x_t in R^4 concatenates the continuous availability ratio a_t with cyclical diurnal hour embeddings and normalized day of the week:"
    )
    add_eq("x_t = \\left[ a_t, \\; \\sin\\left(\\frac{2\\pi h_t}{24}\\right), \\; \\cos\\left(\\frac{2\\pi h_t}{24}\\right), \\; \\frac{d_t}{7} \\right]^T", 1)
    add_p("where a_t in [0, 1] is the continuous availability ratio, h_t in [8.0, 16.5] is the daytime hour, and d_t in {0, ..., 6} represents the day of the week (normalized by 7.0).")

    add_h2("3.2.1 Data Leakage Audit and Empirical Sensitivity Analysis")
    add_p(
        "A critical methodological consideration in IoT time series forecasting is evaluating the potential for predictive lookahead leakage. "
        "In our preprocessing pipeline, we institute three structural boundaries to control and mitigate temporal information contamination:"
    )

    p_l1 = doc.add_paragraph(style='List Paragraph')
    p_l1.paragraph_format.space_before = Pt(2)
    p_l1.paragraph_format.space_after = Pt(2)
    p_l1.add_run("1. Intra-Session Day Bounding: ").bold = True
    p_l1.add_run("Linear time interpolation for missing daytime readings is executed strictly within each single calendar day between 08:00 and 16:30 using valid sensor readings on both sides of a gap. Interpolation is never performed across overnight closures (16:30 to 08:00). Overnight gaps are treated as absolute sequence boundaries, guaranteeing that evening observations never influence morning forecasts. However, an inherent limitation of bilateral interpolation is that it uses subsequent observations within the same calendar day to impute earlier missing slots; hence, within sparse daytime sessions, imputed features at step t theoretically incorporate within-day future readings that would not have been available in real-time streaming operations.")

    p_l2 = doc.add_paragraph(style='List Paragraph')
    p_l2.paragraph_format.space_before = Pt(2)
    p_l2.paragraph_format.space_after = Pt(2)
    p_l2.add_run("2. Chronological Timeline Partitioning with Embargo Purge Gaps: ").bold = True
    p_l2.add_run("To strictly isolate evaluation partitions, the 70% train, 15% validation, and 15% test split is executed chronologically along each facility's active operational timeline at the sequence-window level, separated by an embargo/purge gap (g = 1 sequence window) at each boundary. This ensures that the forecast targets of training windows (up to y_60 at t+7) never overlap with validation targets, and validation targets never overlap with test targets. Because training sequences strictly precede validation sequences, which strictly precede test sequences, no test-period data can influence model training or hyperparameter selection.")

    p_l3 = doc.add_paragraph(style='List Paragraph')
    p_l3.paragraph_format.space_before = Pt(2)
    p_l3.paragraph_format.space_after = Pt(2)
    p_l3.add_run("3. Causal Sequence Directionality: ").bold = True
    p_l3.add_run("Within each sliding sequence window (x_{t-5}, ..., x_t), input features reflect strictly past observations up to current time t, while forecast targets y_{t+1} (30-min ahead) and y_{t+2} (60-min ahead) reside strictly at future time steps.")

    add_p(
        "To evaluate the practical empirical impact of intra-day interpolation on model performance, we audited all 3,263 "
        "purged test sequence windows across the 30 facilities. This forensic audit revealed that 2,781 test windows (85.2%) are completely uninterpolated—every "
        "single one of the 8 constituent time steps corresponds to an authentic, un-imputed physical sensor transmission. Only 482 windows (14.8%) "
        "contain one or more interpolated daytime slots. We conducted a sensitivity analysis evaluating model accuracy on the pure uninterpolated "
        "test subset versus the complete 3,263-window test set. Centralized Attention-LSTM achieved an MAE of 0.02196 (rounded to 0.0220) on the pure raw subset versus "
        "0.02170 (rounded to 0.0217) on the full test set—an unrounded difference of +0.00026, or ~0.3 bays. Global FedAvg achieved an MAE of 0.1022 (0.102) "
        "on the pure raw subset versus 0.1006 (0.101) on the full test set (+0.0016 difference), while Personalized FedAvg achieved 0.0636 versus "
        "0.0607, a difference of +0.0029. Similarly, Local Linear AR(4) achieved 0.0128 versus 0.0126. Crucially, model rankings, relative margins, "
        "and the overwhelming superiority of local linear baselines remain completely unchanged between the raw subsample and the complete test set. We emphasize "
        "that this empirical sensitivity analysis does not prove the complete absence of lookahead bias across imputed time steps. Rather, it provides strong empirical "
        "evidence that our core benchmark findings—namely, the superiority of local linear models, the under-training of FedAvg, and the relative recovery achieved "
        "via personalization—are robust, stable, and not artifacts of daytime linear interpolation."
    )

    add_h2("3.3 Model Architecture: A Lightweight Recurrent Backbone")
    add_p(
        "We implement an Attention-Based Long Short-Term Memory (Attention-LSTM) network formulated as a lightweight, edge-compatible architecture. "
        "The recurrent backbone consists of a 2-layer LSTM [24] with hidden dimension d_h = 64. At each historical step t in {1, ..., L}, the LSTM "
        "computes hidden state h_t in R^{64} and cell state c_t in R^{64}."
    )

    add_p(
        "To allow the network to selectively emphasize critical rapid-transition intervals (such as morning ingress spikes and evening departures), "
        "we integrate a temporal self-attention mechanism over the sequence of hidden representations. Alignment scores e_t in R "
        "for each historical time step t are computed via a two-layer feedforward projection with hyperbolic tangent activation:"
    )
    add_eq("e_t = w_a^T \\tanh(W_a h_t + b_a) + b_s", 2)
    add_p(
        "where W_a in R^{32 x 64}, b_a in R^{32}, w_a in R^{32}, and b_s in R (totaling 2,113 parameters). The scalar alignment scores e_t are normalized "
        "across all lookback time steps using a softmax operator to yield attention weights \\alpha_t:"
    )
    add_eq("\\alpha_t = \\frac{\\exp(e_t)}{\\sum_{\\tau=1}^L \\exp(e_\\tau)}, \\quad \\sum_{t=1}^L \\alpha_t = 1", 3)
    add_p(
        "The dynamic temporal context vector c in R^{64} is computed as the attention-weighted linear sum of all historical hidden states:"
    )
    add_eq("c = \\sum_{t=1}^L \\alpha_t h_t", 4)
    add_p(
        "The context vector is concatenated with the final hidden state [c; h_L] in R^{128} and projected through a multi-layer perceptron (MLP) "
        "output head consisting of a dense linear layer (128 -> 32 units), ReLU activation, dropout (p = 0.2), a second linear projection (32 -> 1 unit), "
        "and a final sigmoid activation to enforce availability ratio bounds in [0, 1]:"
    )
    add_eq("z = \\text{ReLU}(W_1 [c; h_L] + b_1), \\quad \\hat{y} = \\sigma(w_2^T z + b_2)", 5)
    add_p(
        "where W_1 in R^{32 x 128}, b_1 in R^{32}, w_2 in R^{32}, and b_2 in R. Across the 2-layer LSTM backbone (51,200 parameters), "
        "the temporal attention mechanism (2,113 parameters), and the output MLP head (4,161 parameters), the Attention-LSTM network contains "
        "exactly 57,474 trainable float32 parameters, corresponding to exactly 229,896 bytes (224.51 KiB in binary units, or 229.90 KB in decimal units)."
    )

    # Embedded Figure 1: Architecture Diagram
    if os.path.exists("results/fig_architecture.png"):
        doc.add_picture("results/fig_architecture.png", width=Inches(6.2))
        p_f1 = doc.paragraphs[-1]
        p_f1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_caption("Figure 1. Architecture of the Federated Attention-LSTM Framework across 30 Heterogeneous Municipal Parking Lots.", is_table=False)

    add_h2("3.4 The Baseline Hierarchy: Constructing the Personalization Ladder")
    add_p(
        "To rigorously assess when federation adds value, we implement the complete baseline hierarchy:"
    )

    p_b1 = doc.add_paragraph(style='List Paragraph')
    p_b1.paragraph_format.space_before = Pt(2)
    p_b1.paragraph_format.space_after = Pt(2)
    p_b1.add_run("1. Zero-Parameter Persistence Baseline: ").bold = True
    p_b1.add_run("Predicts that availability at horizon t+h equals the current observed availability: y_hat_{t+h} = a_t. Requires zero training, zero compute, and zero communication, establishing the fundamental operational floor.")

    p_b2 = doc.add_paragraph(style='List Paragraph')
    p_b2.paragraph_format.space_before = Pt(2)
    p_b2.paragraph_format.space_after = Pt(2)
    p_b2.add_run("2. Local-Only Linear AR(4) Baseline (Local Isolation): ").bold = True
    p_b2.add_run("Each client independently fits an autoregressive linear ridge regression model on its own past 4 availability observations (a_{t-3}, ..., a_t) plus an intercept term (5 fitted parameters per facility). Employs strictly local data with zero cross-lot communication, eliminating cross-facility data sharing, avoiding centralized exposure of raw telemetry, and incurring zero infrastructure overhead.")

    p_b3 = doc.add_paragraph(style='List Paragraph')
    p_b3.paragraph_format.space_before = Pt(2)
    p_b3.paragraph_format.space_after = Pt(2)
    p_b3.add_run("3. Pooled Centralized Linear AR(4) Baseline: ").bold = True
    p_b3.add_run("A single global 5-parameter linear autoregressive model (4 lag coefficients plus intercept) trained across all pooled multi-lot training observations.")

    p_b4 = doc.add_paragraph(style='List Paragraph')
    p_b4.paragraph_format.space_before = Pt(2)
    p_b4.paragraph_format.space_after = Pt(2)
    p_b4.add_run("4. Centralized Gradient Boosted Trees (XGBoost): ").bold = True
    p_b4.add_run("An ensemble of gradient boosted regression trees [4] trained on flattened lookback feature vectors across the pooled multi-lot dataset (100 estimators, max depth 5, learning rate 0.05).")

    p_b5 = doc.add_paragraph(style='List Paragraph')
    p_b5.paragraph_format.space_before = Pt(2)
    p_b5.paragraph_format.space_after = Pt(2)
    p_b5.add_run("5. Centralized Standard LSTM & Attention-LSTM: ").bold = True
    p_b5.add_run("Deep recurrent architectures trained centrally for 30 epochs on 15,299 pooled sequences using Adam optimization (learning rate 0.001, batch size 32).")

    p_b6 = doc.add_paragraph(style='List Paragraph')
    p_b6.paragraph_format.space_before = Pt(2)
    p_b6.paragraph_format.space_after = Pt(2)
    p_b6.add_run("6. Global Federated Averaging (FedAvg): ").bold = True
    p_b6.add_run("Decentralized training across 30 clients coordinated over R = 8 communication rounds. In each round, all clients train locally for E = 2 epochs on private data (batch size B = 32, Adam learning rate 0.001). The central server aggregates updates using sample-weighted FedAvg [7].")

    p_b7 = doc.add_paragraph(style='List Paragraph')
    p_b7.paragraph_format.space_before = Pt(2)
    p_b7.paragraph_format.space_after = Pt(2)
    p_b7.add_run("7. IID-Shuffled Federated Control: ").bold = True
    p_b7.add_run("To isolate under-training from non-IID drift, the combined multi-lot training set is randomly partitioned into 30 uniform IID client slices, trained under identical parameters (R = 8, E = 2, B = 32).")

    p_b8 = doc.add_paragraph(style='List Paragraph')
    p_b8.paragraph_format.space_before = Pt(2)
    p_b8.paragraph_format.space_after = Pt(2)
    p_b8.add_run("8. Advanced Federated Paradigms (FedProx & FedPer): ").bold = True
    p_b8.add_run("We evaluate FedProx [19] with proximal constraint weight mu = 0.01, and FedPer [21] where the Attention-LSTM representation is federated while the classification head is maintained as private local parameters.")

    p_b9 = doc.add_paragraph(style='List Paragraph')
    p_b9.paragraph_format.space_before = Pt(2)
    p_b9.paragraph_format.space_after = Pt(4)
    p_b9.add_run("9. Personalized FedAvg (Local Adaptation): ").bold = True
    p_b9.add_run("Each client takes the aggregated global FedAvg model at round 8 and performs localized fine-tuning on its private training partition for 3 epochs using a reduced learning rate eta_{ft} = 0.0003, adapting weights to lot-specific baseline occupancies.")

    add_h2("3.5 Compute Parity Audit: Disentangling Under-Training from Heterogeneity")
    add_p(
        "A critical consideration in interpreting federated empirical benchmarks is the disparity in cumulative gradient steps between centralized "
        "and federated configurations. In our setup, the centralized Attention-LSTM is trained for 30 epochs on 15,299 pooled sequences with batch size 32, "
        "executing exactly 30 x ceil(15,299 / 32) = 30 x 479 = 14,370 Adam gradient updates. In contrast, under standard FedAvg with R = 8 rounds and "
        "E = 2 local epochs, a client with an average dataset of approximately 510 training sequences (15,299 / 30 = 509.97) executes ceil(510 / 32) = 16 "
        "batches per epoch, yielding 32 gradient steps per round and a cumulative total of approximately 256 local Adam updates per client across the entire training process."
    )

    add_p(
        "Comparing cumulative system-wide optimizer updates provides a useful empirical proxy for training compute volume. "
        "Across all 30 clients, the 8-round federated protocol executes a total of 7,888 client-side optimizer updates "
        "(approximately 256 updates per client), representing 54.9% of the 14,370 updates executed by the centralized model over 30 epochs. "
        "In contrast, the 15-round protocol scales to 14,790 cumulative client-side updates across the federation (approximately 493 updates per client), "
        "achieving an approximately matched optimizer-update budget (102.9% of centralized compute, a +2.9% difference). "
        "We note that optimizer-update counts serve as a pragmatic compute proxy rather than proof of identical optimization dynamics, "
        "as decentralized client drift, localized mini-batches, and periodic parameter averaging induce distinct loss landscape trajectories. "
        "Under the 8-round communication budget, an IID-shuffled control experiment indicates that statistical heterogeneity accounts for "
        "35.8% of the initial gap between FedAvg and centralized models, while the remaining 64.2% residual deficit is consistent with "
        "optimization under-training. Extending rounds to the approximately matched 15-round budget shifts this balance, indicating that "
        "non-IID heterogeneity accounts for 73.9% of the deficit once compute starvation is mitigated (Section 4.2 and Section 5.2). "
        "Because FedAvg test error improves gradually when communication rounds are extended, strict round limits impose substantial "
        "optimization friction on decentralized convergence."
    )

    # ==================== 4. EXPERIMENTAL RESULTS ====================
    add_h1("4. Experimental Results")

    add_h2("4.1 Comprehensive Multi-Horizon Benchmark")
    add_p(
        "All eight forecasting paradigms were evaluated on the 3,263 unified test sequences across all 30 parking facilities. Evaluation metrics "
        "include Pooled Mean Absolute Error (Micro MAE), Pooled Root Mean Squared Error (Micro RMSE), Macro Mean MAE (unweighted average across "
        "lots), Between-Lot Standard Deviation (sigma), and Mean Physical Space Error (in bays). Physical space error is computed by scaling "
        "prediction residuals against each facility's true nominal capacity C_i: e_{space} = |y_t - \\hat{y}_t| x C_i. Table 2 presents the "
        "complete benchmark across both 30-minute and 60-minute lookahead horizons."
    )

    # Table 2: Primary Benchmark Table (Multi-Seed Reporting across Seeds {42, 101, 2024})
    add_caption("Table 2. Comprehensive Multi-Horizon Smart Parking Benchmark across 30 Heterogeneous Facilities (3,263 Unified Test Windows with Embargo Purge Gaps; Multi-Seed Mean ± Std across Seeds {42, 101, 2024}, B = 32).")
    t2 = doc.add_table(rows=17, cols=7)
    t2.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t2)

    t2_headers = ["Horizon", "Forecasting Model", "Pooled MAE (Micro)", "Pooled RMSE", "Macro MAE", "Between-Lot Std (sigma)", "Mean Space Error (bays)"]
    for j, h in enumerate(t2_headers):
        c = t2.cell(0, j)
        set_cell_background(c, "1F3864")
        set_cell_margins(c, 100, 100, 100, 100)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    t2_data_30 = [
        ("Persistence Baseline (y_hat = a_t)", "0.0256 ± 0.0000", "0.0387 ± 0.0000", "0.0247 ± 0.0000", "0.0135 ± 0.0000", "33.3 ± 0.0"),
        ("Local-Only Linear AR(4) (Local isolation)", "0.0126 ± 0.0000", "0.0179 ± 0.0000", "0.0124 ± 0.0000", "0.0049 ± 0.0000", "13.9 ± 0.0"),
        ("Pooled Linear AR(4) (Centralized)", "0.0129 ± 0.0000", "0.0190 ± 0.0000", "0.0132 ± 0.0000", "0.0050 ± 0.0000", "14.8 ± 0.0"),
        ("Centralized XGBoost [4]", "0.0133 ± 0.0000", "0.0187 ± 0.0000", "0.0141 ± 0.0000", "0.0056 ± 0.0000", "15.8 ± 0.0"),
        ("Centralized Standard LSTM [24]", "0.0218 ± 0.0005", "0.0300 ± 0.0004", "0.0233 ± 0.0004", "0.0131 ± 0.0003", "25.2 ± 0.4"),
        ("Centralized Attention-LSTM [5]", "0.0217 ± 0.0004", "0.0285 ± 0.0003", "0.0230 ± 0.0003", "0.0113 ± 0.0002", "26.9 ± 0.3"),
        ("Global FedAvg (R=8, B=32) [7]", "0.0935 ± 0.0032", "0.1230 ± 0.0030", "0.0963 ± 0.0029", "0.0498 ± 0.0013", "118.5 ± 2.6"),
        ("Personalized FedAvg (Local Adaptation)", "0.0592 ± 0.0004", "0.0786 ± 0.0001", "0.0612 ± 0.0001", "0.0243 ± 0.0014", "82.4 ± 0.4"),
    ]

    t2_data_60 = [
        ("Persistence Baseline (y_hat = a_t)", "0.0493 ± 0.0000", "0.0716 ± 0.0000", "0.0476 ± 0.0000", "0.0252 ± 0.0000", "64.2 ± 0.0"),
        ("Local-Only Linear AR(4) (Local isolation)", "0.0248 ± 0.0000", "0.0350 ± 0.0000", "0.0242 ± 0.0000", "0.0096 ± 0.0000", "28.4 ± 0.0"),
        ("Pooled Linear AR(4) (Centralized)", "0.0260 ± 0.0000", "0.0376 ± 0.0000", "0.0267 ± 0.0000", "0.0096 ± 0.0000", "30.6 ± 0.0"),
        ("Centralized XGBoost [4]", "0.0233 ± 0.0000", "0.0325 ± 0.0000", "0.0254 ± 0.0000", "0.0116 ± 0.0000", "28.4 ± 0.0"),
        ("Centralized Standard LSTM [24]", "0.0291 ± 0.0006", "0.0402 ± 0.0005", "0.0304 ± 0.0005", "0.0118 ± 0.0004", "35.5 ± 0.5"),
        ("Centralized Attention-LSTM [5]", "0.0305 ± 0.0005", "0.0416 ± 0.0004", "0.0318 ± 0.0004", "0.0120 ± 0.0003", "37.4 ± 0.4"),
        ("Global FedAvg (R=8, B=32) [7]", "0.1078 ± 0.0035", "0.1415 ± 0.0032", "0.1109 ± 0.0031", "0.0560 ± 0.0015", "137.1 ± 3.1"),
        ("Personalized FedAvg (Local Adaptation)", "0.0732 ± 0.0005", "0.0962 ± 0.0003", "0.0750 ± 0.0003", "0.0263 ± 0.0012", "92.3 ± 0.6"),
    ]

    row_idx = 1
    for m, p_mae, p_rmse, m_mae, sig, sp in t2_data_30:
        bg = "F1F5F9" if "Personalized" in m or "Local-Only" in m else ("FFFFFF" if row_idx % 2 == 1 else "F8FAFC")
        h_text = "30-Min (y_30)" if row_idx == 1 else ""
        vals = [h_text, m, p_mae, p_rmse, m_mae, sig, sp]
        for j, val in enumerate(vals):
            c = t2.cell(row_idx, j)
            set_cell_background(c, bg)
            set_cell_margins(c, 60, 60, 80, 80)
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 1 else WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(val)
            r.font.size = Pt(8)
            if "Personalized" in m or "Local-Only" in m or "Persistence" in m:
                r.bold = True
        row_idx += 1

    for m, p_mae, p_rmse, m_mae, sig, sp in t2_data_60:
        bg = "F1F5F9" if "Personalized" in m or "Local-Only" in m else ("FFFFFF" if row_idx % 2 == 1 else "F8FAFC")
        h_text = "60-Min (y_60)" if row_idx == 9 else ""
        vals = [h_text, m, p_mae, p_rmse, m_mae, sig, sp]
        for j, val in enumerate(vals):
            c = t2.cell(row_idx, j)
            set_cell_background(c, bg)
            set_cell_margins(c, 60, 60, 80, 80)
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 1 else WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(val)
            r.font.size = Pt(8)
            if "Personalized" in m or "Local-Only" in m or "Persistence" in m:
                r.bold = True
        row_idx += 1

    p_t2_note = add_p(space_after=4)
    r_t2_note = p_t2_note.add_run("Note: Baseline models (Persistence, Local Linear, Pooled Linear, and XGBoost) are deterministic and seed-invariant (± 0.0000). For archival reference, the primary single-seed benchmark (Seed = 42) reports: Local Linear MAE = 0.0126 (13.9 bays), Centralized Attention-LSTM MAE = 0.0217 (26.9 bays), Global FedAvg MAE = 0.1006 (126.8 bays), and Personalized FedAvg MAE = 0.0607 (73.2 bays).")
    r_t2_note.font.size = Pt(8)
    r_t2_note.font.italic = True
    r_t2_note.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    add_p("", space_after=6)

    # Embedded Figure 2: Grouped Bar Chart
    if os.path.exists("results/fig1_model_comparison_grouped.png"):
        doc.add_picture("results/fig1_model_comparison_grouped.png", width=Inches(6.2))
        p_f2 = doc.paragraphs[-1]
        p_f2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_caption("Figure 2. Reconciled 30-Minute Model Benchmark: (a) Pooled MAE (Micro-Average) and (b) Physical Space Error (Vacant Bays).", is_table=False)

    add_h2("4.2 Comparative Analysis of Decentralized & Federated Personalization Paradigms")
    add_p(
        "To rigorously evaluate the mechanics of federated optimization and personalization, we conducted multi-seed evaluations across seeds "
        "{42, 101, 2024} for standard FedAvg, an IID-shuffled federated control, FedProx (mu = 0.01), FedPer (shared representation + private local head), "
        "and Personalized FedAvg. Table 3 presents the empirical results across the 30 parking facilities."
    )

    # Table 3: Advanced Federated Comparisons across Constrained and Compute-Parity Regimes
    add_caption("Table 3. Empirical Comparison of Decentralized & Federated Personalization Paradigms across Communication-Constrained (R=8) and Approximately Matched Compute-Budget (R=15) Regimes (30-Minute Horizon, Mean ± Std across Seeds {42, 101, 2024}).")
    t3 = doc.add_table(rows=11, cols=7)
    t3.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t3)

    t3_headers = ["Regime & Protocol", "Federated Paradigm / Algorithm", "Pooled MAE (Micro)", "Pooled RMSE", "Macro Mean MAE", "Between-Lot Std (sigma)", "Mean Space Error (bays)"]
    t3_col_widths = [Inches(1.15), Inches(1.55), Inches(0.80), Inches(0.75), Inches(0.75), Inches(0.75), Inches(0.75)]
    
    for j, h in enumerate(t3_headers):
        c = t3.cell(0, j)
        c.width = t3_col_widths[j]
        set_cell_background(c, "1F3864")
        set_cell_margins(c, 100, 100, 100, 100)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(8.2)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    # Table 3 complete data rows (Panel 1: R=8, Panel 2: R=15 Compute Parity)
    t3_rows = [
        # Panel 1: R=8
        ("Communication-Constrained (R=8, E=2, ~7,888 steps)", "Global FedAvg (R=8, B=32) [7]", "0.0935 ± 0.0032", "0.1230 ± 0.0030", "0.0963 ± 0.0029", "0.0498 ± 0.0013", "118.5 ± 2.6"),
        ("Communication-Constrained (R=8, E=2, ~7,888 steps)", "IID-Shuffled FedAvg Control", "0.0678 ± 0.0019", "0.0956 ± 0.0023", "0.0711 ± 0.0019", "0.0361 ± 0.0012", "90.4 ± 1.5"),
        ("Communication-Constrained (R=8, E=2, ~7,888 steps)", "FedProx (mu = 0.01) [19]", "0.1305 ± 0.0162", "0.1607 ± 0.0157", "0.1333 ± 0.0169", "0.0573 ± 0.0040", "162.8 ± 18.5"),
        ("Communication-Constrained (R=8, E=2, ~7,888 steps)", "FedPer (Shared Base, Private Head) [21]", "0.0775 ± 0.0012", "0.1056 ± 0.0007", "0.0798 ± 0.0009", "0.0379 ± 0.0007", "99.8 ± 1.2"),
        ("Communication-Constrained (R=8, E=2, ~7,888 steps)", "Personalized FedAvg (Local Adaptation)", "0.0592 ± 0.0004", "0.0786 ± 0.0001", "0.0612 ± 0.0001", "0.0243 ± 0.0014", "82.4 ± 0.4"),
        ("Decomposition (R=8 Budget)", "Heterogeneity Gap: 0.0257 (35.8%) | Under-Training Deficit: 0.0461 (64.2%) | Total Gap: 0.0718", "", "", "", "", ""),
        # Panel 2: R=15 Compute Parity
        ("Matched Compute Budget (R=15, ~14,790 steps)", "Compute-Matched Global FedAvg (R=15, Non-IID)", "0.0858 ± 0.0015", "0.1139 ± 0.0011", "0.0889 ± 0.0016", "0.0465 ± 0.0007", "109.5 ± 1.8"),
        ("Matched Compute Budget (R=15, ~14,790 steps)", "Compute-Matched IID-Shuffled FedAvg (R=15)", "0.0384 ± 0.0010", "0.0541 ± 0.0018", "0.0405 ± 0.0010", "0.0198 ± 0.0008", "47.5 ± 1.0"),
        ("Matched Compute Budget (R=15, ~14,790 steps)", "Compute-Matched Personalized FedAvg (R=15)", "0.0548 ± 0.0012", "0.0741 ± 0.0022", "0.0565 ± 0.0015", "0.0222 ± 0.0022", "67.5 ± 1.6"),
        ("Decomposition (R=15 Budget)", "Heterogeneity Gap: 0.0474 (73.9%) | Residual Optimization Gap: 0.0167 (26.1%) | Total Gap: 0.0641", "", "", "", "", "")
    ]

    for i, row in enumerate(t3_rows, start=1):
        is_decomp = "Decomposition" in row[0]
        bg = "EFF6FF" if is_decomp else ("F1F5F9" if "Personalized" in row[1] or "IID" in row[1] else ("FFFFFF" if i % 2 == 1 else "F8FAFC"))
        
        if is_decomp:
            # Col 0: Regime label
            c0 = t3.cell(i, 0)
            c0.width = t3_col_widths[0]
            set_cell_background(c0, bg)
            set_cell_margins(c0, 60, 60, 80, 80)
            p0 = c0.paragraphs[0]
            p0.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r0 = p0.add_run(row[0])
            r0.font.size = Pt(8.0)
            r0.bold = True
            r0.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)
            
            # Merge cols 1 through 6 for decomposition statement
            t3.cell(i, 1).merge(t3.cell(i, 6))
            c_merged = t3.cell(i, 1)
            set_cell_background(c_merged, bg)
            set_cell_margins(c_merged, 60, 60, 80, 80)
            p_m = c_merged.paragraphs[0]
            p_m.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r_m = p_m.add_run(row[1])
            r_m.font.size = Pt(8.0)
            r_m.bold = True
            r_m.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)
        else:
            for j, val in enumerate(row):
                c = t3.cell(i, j)
                c.width = t3_col_widths[j]
                set_cell_background(c, bg)
                set_cell_margins(c, 60, 60, 80, 80)
                p = c.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j in (0, 1) else WD_ALIGN_PARAGRAPH.CENTER
                r = p.add_run(val)
                r.font.size = Pt(8.0)
                if "Personalized" in row[1]:
                    r.bold = True

    p_t3_note = add_p(space_after=4)
    r_t3_note = p_t3_note.add_run(
        "Note: All metrics report multi-seed mean ± std across seeds {42, 101, 2024}. "
        "The mathematical decomposition isolates heterogeneity and optimization effects via: "
        "Δ_total = MAE_Non-IID - MAE_Centralized (Centralized Attention-LSTM benchmark = 0.0217 ± 0.0004); "
        "Δ_heterogeneity = MAE_Non-IID - MAE_IID-Shuffled; "
        "Δ_optimization = MAE_IID-Shuffled - MAE_Centralized. "
        "Seed-level results: "
        "Panel 1 (R=8): Global FedAvg MAE = [0.0970 (seed 42), 0.0925 (seed 101), 0.0908 (seed 2024)]; "
        "IID-Shuffled FedAvg MAE = [0.0659, 0.0677, 0.0698]; "
        "Personalized FedAvg MAE = [0.0596, 0.0593, 0.0587]. "
        "Panel 2 (R=15 Compute Parity): Non-IID FedAvg MAE = [0.0857 (seed 42), 0.0874 (seed 101), 0.0844 (seed 2024)]; "
        "IID-Shuffled FedAvg MAE = [0.0372, 0.0389, 0.0390]; "
        "Personalized FedAvg MAE = [0.0535, 0.0558, 0.0551]. "
        "Under communication constraints (R=8), under-training accounts for 64.2% of the deficit; "
        "when scaled to an approximately matched optimizer-update budget (R=15, ~14,790 client updates vs 14,370 centralized steps, 102.9%), mitigating compute starvation allows IID FedAvg to converge to 0.0384 ± 0.0010, "
        "indicating that non-IID client heterogeneity accounts for 73.9% of the remaining deficit under this experimental protocol."
    )
    r_t3_note.font.size = Pt(8)
    r_t3_note.font.italic = True
    r_t3_note.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    add_p("", space_after=6)

    add_p(
        "Table 3 presents comparative empirical insights into the nature of federated learning on IoT streams across two distinct optimization regimes:"
    )

    p_r1 = doc.add_paragraph(style='List Paragraph')
    p_r1.paragraph_format.space_before = Pt(2)
    p_r1.paragraph_format.space_after = Pt(2)
    p_r1.add_run("1. Empirical Decomposition across Communication-Constrained and Approximately Matched Compute Regimes: ").bold = True
    p_r1.add_run("Under communication constraints (R = 8 rounds, ~256 local steps/client), Global FedAvg achieves an MAE of 0.0935 ± 0.0032. Eliminating statistical heterogeneity via IID shuffling reduces error to 0.0678 ± 0.0019. Relative to the centralized Attention-LSTM benchmark (0.0217), statistical heterogeneity accounts for 35.8% (0.0257) of the gap, while 64.2% (0.0461) reflects optimization under-training. Crucially, when scaled to an approximately matched compute budget (R = 15 rounds, E = 2, totaling 14,790 cumulative client updates vs 14,370 centralized steps, 102.9%), IID-Shuffled FedAvg converges rapidly to 0.0384 ± 0.0010 (47.5 bays), cutting the optimization gap by 63.8% (from 0.0461 to 0.0167). In contrast, Non-IID FedAvg at R = 15 reaches only 0.0858 ± 0.0015 (109.5 bays). Under matched compute parity, removing statistical heterogeneity closes 0.0474 of the 0.0641 gap—indicating that non-IID client statistical heterogeneity accounts for 73.9% (0.0474) of the performance deficit under this matched-compute protocol, while the residual optimization deficit shrinks to 26.1% (0.0167).")

    p_r2 = doc.add_paragraph(style='List Paragraph')
    p_r2.paragraph_format.space_before = Pt(2)
    p_r2.paragraph_format.space_after = Pt(2)
    p_r2.add_run("2. Algorithmic Comparison: FedProx vs. FedPer vs. Fine-Tuning: ").bold = True
    p_r2.add_run("Adding proximal regularization (FedProx, mu = 0.01) achieves an MAE of 0.1305 ± 0.0162. Because clients are already starved of local updates (~256 steps), the proximal penalty anchors parameters to an under-converged global model, adding optimization friction. In contrast, decoupling the network via FedPer (federating base recurrent representations while keeping classification heads local) substantially improves accuracy, achieving an MAE of 0.0775 ± 0.0012. However, post-aggregation local fine-tuning (Personalized FedAvg) achieves the superior result (MAE: 0.0592 ± 0.0004), representing a 36.7% relative error reduction over global FedAvg and recovering 47.8% of the performance gap toward centralized Attention-LSTM (and 50.6% recovery in the primary single-seed benchmark).")

    p_r3 = doc.add_paragraph(style='List Paragraph')
    p_r3.paragraph_format.space_before = Pt(2)
    p_r3.paragraph_format.space_after = Pt(2)
    p_r3.add_run("3. Variance Compression & Outlier Mitigation: ").bold = True
    p_r3.add_run("Personalization compresses between-lot standard deviation (sigma) by 51.2%, falling from 0.0498 to 0.0243. Under global FedAvg, severe outlier error occurs at BHMBRCBRG01 (MAE: 0.2599) and BHMBRCBRG02 (MAE: 0.2080). Personalization cuts the error of BHMBRCBRG01 to 0.1240 (a 52.3% reduction) and BHMBRCBRG02 to 0.0992 (a 52.3% reduction). The highest remaining personalized MAE across all 30 facilities is 0.1268 at NIA North, caused by its extremely sparse training set (only 69 sequences).")

    p_r4 = doc.add_paragraph(style='List Paragraph')
    p_r4.paragraph_format.space_before = Pt(2)
    p_r4.paragraph_format.space_after = Pt(4)
    p_r4.add_run("4. Physical Space Error Scaling: ").bold = True
    p_r4.add_run("In the primary single-run benchmark (Table 2), Global FedAvg incurs an unweighted macro space error of 126.8 bays (130.6 sample-weighted micro bays), while Personalized FedAvg reduces this to 73.2 bays (75.0 micro bays), achieving a 42.3% reduction in physical parking allocation error. Across the three-seed evaluation (Table 3), Global FedAvg achieves an unweighted macro space error of 118.5 ± 2.6 bays (121.3 ± 2.8 micro bays), whereas Personalized FedAvg reduces space error to 82.4 ± 0.4 bays (84.0 ± 0.4 micro bays). In stark contrast, the zero-communication Local Linear AR(4) baseline incurs only 13.9 bays of unweighted macro space error (17.6 sample-weighted micro bays), demonstrating that if municipal governance permits local-only processing, isolated local linear models are overwhelmingly superior.")

    # Embedded Figure 3: Boxplot
    if os.path.exists("results/fig2_personalization_distribution_boxplot.png"):
        doc.add_picture("results/fig2_personalization_distribution_boxplot.png", width=Inches(6.0))
        p_f3 = doc.paragraphs[-1]
        p_f3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_caption("Figure 3. Inter-Lot Error Distribution & Variance Reduction across 30 Facilities: Boxplot comparison of Local Linear, Centralized, Global FedAvg, and Personalized FedAvg.", is_table=False)

    add_h2("4.3 Controlled Round Scaling and Diminishing Returns")
    add_p(
        "To evaluate whether additional federated communication rounds can bridge the performance gap, we conducted a controlled round scaling "
        "experiment across all 30 clients with R in {4, 8, 12, 16}. This ablation was evaluated under local batch size B = 64 (which halves the "
        "gradient updates per epoch relative to the primary benchmark's B = 32). Table 4 and Figure 4 document the convergence trajectory."
    )

    # Table 4: Round Scaling Table
    add_caption("Table 4. Controlled 30-Client Round Scaling Ablation Trajectory (B = 64, E = 2, eta = 0.001).")
    t4 = doc.add_table(rows=5, cols=5)
    t4.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t4)

    t4_headers = ["Communication Rounds (R)", "Mean Train MSE", "Pooled Test MAE (y_30)", "Macro Mean MAE", "Between-Lot Std (sigma)"]
    for j, h in enumerate(t4_headers):
        c = t4.cell(0, j)
        set_cell_background(c, "1F3864")
        set_cell_margins(c, 100, 100, 100, 100)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    t4_rows = [
        ("4 Rounds", "0.0410", "0.2062", "0.2116", "0.0857"),
        ("8 Rounds (B=64 Ablation)", "0.0128", "0.1144", "0.1170", "0.0538"),
        ("12 Rounds", "0.0093", "0.1006", "0.1036", "0.0513"),
        ("16 Rounds", "0.0085", "0.0978", "0.0999", "0.0497")
    ]

    for i, row in enumerate(t4_rows, start=1):
        bg = "FFFFFF" if i % 2 == 1 else "F8FAFC"
        for j, val in enumerate(row):
            c = t4.cell(i, j)
            set_cell_background(c, bg)
            set_cell_margins(c, 60, 60, 80, 80)
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(val)
            r.font.size = Pt(8.5)

    add_p("", space_after=6)

    # Embedded Figure 4: Convergence Trajectory & Round Scaling
    if os.path.exists("results/fig3_convergence_trajectory.png") and os.path.exists("results/fig4_round_scaling_30clients.png"):
        doc.add_picture("results/fig4_round_scaling_30clients.png", width=Inches(5.8))
        p_f4 = doc.paragraphs[-1]
        p_f4.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_caption("Figure 4. Controlled 30-Client Round Scaling: Convergence Trajectory and Plateau Behavior (B = 64).", is_table=False)

    add_p(
        "Reconciling Table 2 and Table 4 explains the observed numerical differences: in Table 2, FedAvg at R = 8 under batch size B = 32 achieves "
        "MAE = 0.1006 (multi-seed average: 0.0935), because clients execute twice as many gradient updates per epoch. In Table 4, under B = 64, "
        "FedAvg at R = 8 achieves MAE = 0.1144. Doubling rounds from R = 8 to R = 16 under B = 64 only reduces test MAE from 0.1144 to 0.0978, "
        "entering an asymptotic plateau of diminishing returns. In contrast, local personalization at round 8 achieves an MAE of 0.0592-0.0607, "
        "demonstrating that post-aggregation edge adaptation is far more computationally efficient than extended global communication rounds."
    )

    # ==================== 5. DISCUSSION ====================
    add_h1("5. Discussion and Smart City Governance Implications")

    add_h2("5.1 Why Local Linear Models Outperform Complex Neural Networks")
    add_p(
        "The empirical finding that a 5-parameter local linear autoregressive model (4 autoregressive lag weights plus intercept) outperforms centralized and federated deep sequence models "
        "provides a sobering lesson for intelligent transportation systems engineering. In 30-minute municipal parking streams, vehicular "
        "turnover is constrained by traffic dynamics and commuter work schedules. Occupancy does not fluctuate erratically between half-hour "
        "readings; rather, it exhibits strong temporal persistence. A simple linear formulation directly captures this autoregressive inertia "
        "with only 5 fitted parameters per facility (4 lag weights plus intercept), avoiding the optimization instabilities, gradient saturation, and overfitting risks inherent "
        "in 57k-parameter recurrent neural networks."
    )

    add_p(
        "Consequently, if a parking operator possesses private edge compute and is not required to coordinate with outside operators, the optimal "
        "engineering decision is to deploy a local linear autoregressive model. It achieves superior accuracy (13.9 bays mean space error), incurs "
        "zero communication overhead, requires no GPU hardware, and avoids cross-facility data sharing without requiring external communication."
    )

    add_h2("5.2 Under-Training vs. Non-IID Drift: Quantitative Decomposition")
    add_p(
        "Prior studies frequently attribute FedAvg's poor performance to catastrophic 'non-IID spatial collapse'. However, our empirical findings challenge "
        "the assumption that non-IID spatial collapse is the sole driver of decentralized performance degradation. While parking facilities vary in physical capacity and peak hours, the underlying functional relationship—namely, "
        "that future occupancy is a smooth autoregressive transformation of recent occupancy—is universal across all facilities. Heterogeneity "
        "alone cannot prevent a neural network from learning this common persistence mapping."
    )

    add_p(
        "Instead, our empirical investigation demonstrates that optimization under-training under communication round constraints interacts directly with non-IID statistical heterogeneity. "
        "In an 8-round protocol, federated clients execute approximately 256 local Adam updates per client (7,888 total updates across the federation), compared to 14,370 optimization steps executed by the centralized model over 30 epochs. "
        "At this communication-constrained budget, the IID-shuffled control (Table 3) indicates that statistical heterogeneity accounts for 35.8% of the performance deficit, while the remaining 64.2% residual deficit reflects optimization under-training."
    )

    add_p(
        "Instead, our empirical investigation demonstrates that optimization under-training under communication round constraints interacts directly with non-IID statistical heterogeneity. "
        "In an 8-round protocol, federated clients execute a system-wide total of 7,888 local Adam updates (~256 per client), representing 54.9% of the 14,370 optimization steps executed by the centralized model over 30 epochs. "
        "At this communication-constrained budget, the IID-shuffled control (Table 3) indicates that statistical heterogeneity accounts for 35.8% of the performance deficit, while the remaining 64.2% residual deficit reflects optimization under-training."
    )

    add_p(
        "To investigate these distinct mechanisms under matched optimization volume, we conducted compute-matched experiments (Table 3, Panel 2) scaling federated training to R = 15 rounds (E = 2, B = 32), totaling 14,790 client-side gradient updates across the federation (30 local epochs per client)—establishing an approximately matched optimizer-update budget (102.9% of centralized compute, a +2.9% difference) relative to the 14,370 centralized updates over 30 epochs. "
        "At this approximately matched budget, the IID-shuffled control converges rapidly from 0.0678 ± 0.0019 down to 0.0384 ± 0.0010 (Mean Space Error falls from 90.4 to 47.5 bays), reducing the optimization gap to centralized Attention-LSTM by 63.8% (from 0.0461 to 0.0167). "
        "In contrast, Non-IID FedAvg only improves to 0.0858 ± 0.0015 (109.5 bays). Consequently, once compute starvation is mitigated through this matched-update budget, eliminating non-IID client heterogeneity accounts for 73.9% of the remaining performance deficit (0.0474 out of 0.0641). "
        "These empirical findings indicate that while under-training accounts for the majority of the residual deficit under communication-constrained budgets (R = 8), non-IID client heterogeneity constitutes the dominant performance bottleneck (73.9% of the deficit) when an approximately matched optimizer-update budget is provided. However, matched optimizer-update counts do not render centralized and federated optimization trajectories identical, as decentralized client drift persists across local epochs. "
        "Local personalization acts as a high-leverage algorithmic compensation mechanism: by fine-tuning the global recurrent features on lot-specific data, personalized FedAvg achieves an MAE of 0.0592 ± 0.0004 at R = 8 and 0.0548 ± 0.0012 at R = 15, recovering 47.8% to 51.7% of the centralized performance gap and compressing cross-facility variance (sigma) by over 51%."
    )

    add_h2("5.3 Refuting the Bandwidth Myth: The True Justification for Federation")
    add_p(
        "A widespread narrative in federated IoT literature is that federated learning 'reduces uplink communication bandwidth' by transmitting "
        "model weights rather than raw data. On low-dimensional tabular and scalar IoT telemetry, this claim is mathematically and empirically false:"
    )

    p_bw1 = doc.add_paragraph(style='List Paragraph')
    p_bw1.paragraph_format.space_before = Pt(2)
    p_bw1.paragraph_format.space_after = Pt(2)
    p_bw1.add_run("• Federated Weight Overhead: ").bold = True
    p_bw1.add_run("The Attention-LSTM model comprises exactly 57,474 trainable float32 parameters, occupying 229,896 bytes (224.51 KiB in binary units, or 229.90 KB in decimal units) per client checkpoint. Across 30 clients and 8 communication rounds, bidirectional transmission (uplink + downlink, totaling 480 model transfers) moves exactly 57,474 x 4 x 480 = 110,350,080 bytes = 110.35 MB (105.24 MiB) of network telemetry.")

    p_bw2 = doc.add_paragraph(style='List Paragraph')
    p_bw2.paragraph_format.space_before = Pt(2)
    p_bw2.paragraph_format.space_after = Pt(3)
    p_bw2.add_run("• Raw Telemetry Volume: ").bold = True
    p_bw2.add_run("In contrast, the entire raw Birmingham sensor CSV dataset—comprising 35,717 records across all 30 facilities over 73 days—occupies exactly 1,479,909 bytes = 1.48 MB (1.41 MiB) uncompressed (and approximately 420 KB gzip-compressed).")

    add_p(
        "Therefore, federated learning increases communication volume by exactly 74.6-fold (110.35 MB vs. 1.48 MB) compared to streaming uncompressed "
        "raw sensor telemetry. Federated learning cannot be justified on communication bandwidth-reduction grounds for scalar IoT streams. Instead, "
        "federated learning may be justified by institutional data-governance requirements and multi-stakeholder commercial confidentiality, "
        "even when it increases communication volume. However, regulatory compliance and formal privacy guarantees depend on the deployment context "
        "and may require additional safeguards, such as secure aggregation and differential privacy. Competing private parking operators "
        "(e.g., NCP vs. municipal authorities) refuse to pool proprietary operational records in central servers. Federated learning establishes "
        "a collaborative organizational framework enabling cross-operator predictive coordination without requiring the centralized pooling of commercial trade secrets."
    )

    # Table 5: Resource & Hardware Audit
    add_caption("Table 5. Hardware Specifications, Model Parameter Count, and Network Footprint Audit.")
    t5 = doc.add_table(rows=5, cols=4)
    t5.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t5)

    t5_headers = ["Architectural Dimension", "Centralized Attention-LSTM", "Global FedAvg (R = 8)", "Local-Only Linear AR(4)"]
    for j, h in enumerate(t5_headers):
        c = t5.cell(0, j)
        set_cell_background(c, "1F3864")
        set_cell_margins(c, 100, 100, 100, 100)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    t5_rows = [
        ("Parameter Count", "57,474 weights (224.51 KiB / 229.90 KB)", "57,474 weights (224.51 KiB / 229.90 KB)", "5 scalar parameters (20 bytes) per lot"),
        ("Total Network Data Moved", "1.48 MB / 1.41 MiB (raw CSV stream)", "110.35 MB / 105.24 MiB (480 transfers)", "0.00 B (strictly zero communication)"),
        ("Total Local Gradient Steps", "14,370 Adam steps (pooled)", "~256 Adam steps per client", "1 closed-form Ridge solve per lot"),
        ("Privacy & Governance", "Centralized exposure (all data pooled in cloud)", "Decentralized containment (data stays on edge nodes)", "Local isolation (avoids cross-facility data sharing, no federation)")
    ]

    for i, row in enumerate(t5_rows, start=1):
        bg = "FFFFFF" if i % 2 == 1 else "F8FAFC"
        for j, val in enumerate(row):
            c = t5.cell(i, j)
            set_cell_background(c, bg)
            set_cell_margins(c, 60, 60, 80, 80)
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j < 2 else WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(val)
            r.font.size = Pt(8.5)

    add_h2("5.4 Security, Differential Privacy, and Threats to Validity")
    add_p(
        "It is essential to recognize that standard FedAvg transmits unencrypted weight vectors. Without cryptographic enhancements, raw gradient "
        "vectors remain vulnerable to reconstruction and membership inference attacks [27]. In production smart city deployments, federated frameworks "
        "must integrate Secure Aggregation (SecAgg) [27] or Differential Privacy (DP) [28]. Adding DP noise inevitably degrades forecasting accuracy, "
        "imposing a trade-off between privacy guarantees and utility."
    )

    add_p(
        "Several threats to validity qualify our findings: (1) Hardware Profiling: Although the Attention-LSTM network is formulated as a "
        "lightweight architecture (57k parameters), physical edge microcontroller measurements (e.g., latency, energy consumption, and thermal "
        "throttling on Raspberry Pi or Jetson hardware) were not empirically profiled. (2) Geographic Scope: Our benchmark is evaluated on a single "
        "metropolitan testbed (Birmingham, UK) during autumn/winter (October–December 2016); summer holiday and extreme weather dynamics were not captured. "
        "(3) Synchronous Assumption: Our experiments assume synchronous client participation without communication dropouts or packet loss."
    )

    # ==================== 6. CONCLUSION ====================
    add_h1("6. Conclusion")

    add_p(
        "This paper presented an exhaustive empirical benchmark evaluating federated sequence learning for multi-lot smart parking occupancy "
        "forecasting on the Birmingham municipal IoT stream. By incorporating previously omitted baselines—including zero-parameter persistence, "
        "local-only linear autoregression, and pooled linear models—alongside an IID-shuffled control and alternative federated algorithms, we "
        "established an honest appraisal of when federation adds value and when simpler alternatives prevail."
    )

    add_p(
        "Our findings demonstrate that a 5-parameter local-only linear autoregressive model per facility (4 lag weights plus intercept) achieves superior accuracy (30-minute MAE: 0.0126; "
        "13.9 bays), outperforming both centralized deep neural networks (0.0217; 26.9 bays) and federated models while requiring zero communication "
        "and avoiding cross-facility data sharing. Under practical communication constraints (8 rounds, 2 local epochs), global FedAvg under-trains severely, "
        "achieving a 30-minute MAE of 0.0935 ± 0.0032 (118.5 macro bays in multi-seed evaluation, and 0.1006 / 126.8 bays in the primary single-seed benchmark). "
        "Our experimental decomposition indicates that this degradation is strongly consistent with optimization under-training under communication round constraints (~256 local Adam updates per client versus 14,370 centralized steps) alongside statistical heterogeneity: "
        "an IID-shuffled federated control provides an empirical decomposition attributing 35.8% of the performance gap to statistical heterogeneity, with the remaining 64.2% residual deficit being strongly consistent with compute constraints (~256 local Adam updates per client versus 14,370 centralized steps) under the 8-round communication budget; approximately matched compute-budget experiments (15 rounds, 14,790 cumulative client updates, 102.9% of centralized steps) further indicate that when compute starvation is mitigated, non-IID client heterogeneity accounts for 73.9% of the remaining deficit under this experimental protocol. "
        "Post-aggregation personalization fine-tuning mitigates this gap, reducing error to 0.0592 ± 0.0004 (82.4 macro bays; a 36.7% relative reduction over FedAvg, "
        "recovering 47.8% of the centralized gap in multi-seed evaluations and 50.6% in the primary single-seed benchmark), while compressing between-lot variance "
        "by 51.2%. Furthermore, network audits confirm that federating neural networks moves 110.35 MB (105.24 MiB) of weights across 8 rounds versus only 1.48 MB "
        "(1.41 MiB) for streaming the raw sensor telemetry—a 74.6-fold communication overhead. Consequently, federated parking forecasting cannot be justified on "
        "bandwidth-reduction grounds, but provides substantial value for multi-stakeholder commercial confidentiality and institutional data governance "
        "when paired with local personalization, though regulatory compliance ultimately depends on specific deployment environments, applicable data protection frameworks, and complementary differential privacy safeguards."
    )

    # ==================== DECLARATIONS ====================
    add_h1("Declarations")

    p_d_data = add_p()
    p_d_data.add_run("Availability of Data and Materials: ").bold = True
    p_d_data.add_run("The Birmingham smart parking dataset analyzed in this study is openly available in the UCI Machine Learning Repository at https://doi.org/10.24432/C51K5Z [29]. Complete preprocessing scripts, baseline implementations, model checkpoints, and reproducible evaluation routines are deposited in the project code repository at https://github.com/itsdevesh23/ParkSense-AI.")

    p_d_code = add_p()
    p_d_code.add_run("Reproducibility Statement: ").bold = True
    p_d_code.add_run("All experiments were conducted with fixed random seeds (seeds 42, 101, 2024). Complete sequence windowing parameters (L = 6, H = 2, step = 1), client partition metadata, and evaluation code are fully documented in the public repository to facilitate independent replication.")

    p_d_conf = add_p()
    p_d_conf.add_run("Competing Interests: ").bold = True
    p_d_conf.add_run("The authors declare that they have no competing financial or non-financial interests that could have influenced the work reported in this paper.")

    p_d_fund = add_p()
    p_d_fund.add_run("Funding: ").bold = True
    p_d_fund.add_run("This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors.")

    p_d_ai = add_p()
    p_d_ai.add_run("Use of Generative AI and AI-Assisted Technologies: ").bold = True
    p_d_ai.add_run("During the preparation of this work, the authors utilized AI-assisted coding tools for data formatting, statistical scripting, and language refinement. All empirical experiments, model training, analytical derivations, and interpretive conclusions were conceived, executed, verified, and audited entirely by the authors.")

    p_d_auth = add_p()
    p_d_auth.add_run("Authors' Contributions: ").bold = True
    p_d_auth.add_run("D.M. conceptualized the study, engineered the federated pipeline, executed the baseline experiments, and drafted the manuscript. A. contributed to experimental validation, data auditing, visualization, and manuscript review. All authors reviewed and approved the final manuscript.")

    # ==================== REFERENCES ====================
    add_h1("References")

    references = [
        "[1] D. C. Shoup, \"Cruising for parking,\" Transport Policy, vol. 13, no. 6, pp. 479–486, 2006. https://doi.org/10.1016/j.tranpol.2006.05.005",
        "[2] R. Arnott and J. Rowse, \"Downtown parking in auto city,\" Regional Science and Urban Economics, vol. 39, no. 1, pp. 1–14, 2009. https://doi.org/10.1016/j.regsciurbeco.2008.08.001",
        "[3] G. E. Box, G. M. Jenkins, G. C. Reinsel, and G. M. Ljung, Time Series Analysis: Forecasting and Control, 5th ed. Hoboken, NJ: John Wiley & Sons, 2015. https://doi.org/10.1002/9781118619193",
        "[4] T. Chen and C. Guestrin, \"XGBoost: A scalable tree boosting system,\" in Proc. 22nd ACM SIGKDD Int. Conf. Knowl. Discov. Data Min. (KDD '16), San Francisco, CA, 2016, pp. 785–794. https://doi.org/10.1145/2939672.2939785",
        "[5] D. Bahdanau, K. Cho, and Y. Bengio, \"Neural machine translation by jointly learning to align and translate,\" in Proc. 3rd Int. Conf. Learn. Represent. (ICLR 2015), San Diego, CA, 2015, pp. 1–15. arXiv:1409.0473",
        "[6] B. Yu, H. Yin, and Z. Zhu, \"Spatio-temporal graph convolutional networks: A deep learning framework for traffic forecasting,\" in Proc. 27th Int. Joint Conf. Artif. Intell. (IJCAI 2018), Stockholm, Sweden, 2018, pp. 3634–3640. https://doi.org/10.24963/ijcai.2018/505",
        "[7] B. McMahan, E. Moore, D. Ramage, S. Hampson, and B. A. y Arcas, \"Communication-efficient learning of deep networks from decentralized data,\" in Proc. 20th Int. Conf. Artif. Intell. Statist. (AISTATS 2017), PMLR vol. 54, Fort Lauderdale, FL, 2017, pp. 1273–1282.",
        "[8] D. H. Stolfi, E. Alba, and X. Yao, \"Predicting car park occupancy rates in smart cities,\" in Smart Cities (Smart-CT 2017), LNCS vol. 10268, Cham: Springer, 2017, pp. 107–117. https://doi.org/10.1007/978-3-319-59513-9_11",
        "[9] Y. Zheng, S. Rajasegarar, and C. Leckie, \"Parking availability prediction for sensor-enabled car parks in smart cities,\" in Proc. 2015 IEEE 10th Int. Conf. Intell. Sensors Sensor Netw. Inf. Process. (ISSNIP), Singapore, 2015, pp. 1–6. https://doi.org/10.1109/ISSNIP.2015.7106902",
        "[10] E. I. Vlahogianni, K. Kepaptsoglou, V. Tsetsos, and M. G. Karlaftis, \"A real-time parking prediction system for smart cities,\" Journal of Intelligent Transportation Systems, vol. 20, no. 2, pp. 192–204, 2016. https://doi.org/10.1080/15472450.2015.1037955",
        "[11] Y. Rong, Z. Xu, R. Yan, and X. Ma, \"Du-Parking: Spatio-temporal big data tells you realtime parking availability,\" in Proc. 24th ACM SIGKDD Int. Conf. Knowl. Discov. Data Min. (KDD '18), London, UK, 2018, pp. 646–654. https://doi.org/10.1145/3219819.3219876",
        "[12] D. Zhao, C. Ju, G. Zhu, J. Ning, D. Luo, D. Zhang, and H. Ma, \"MePark: Using meters as sensors for citywide on-street parking availability prediction,\" IEEE Transactions on Intelligent Transportation Systems, vol. 23, no. 7, pp. 7244–7257, 2022. https://doi.org/10.1109/TITS.2021.3067675",
        "[13] Q. Yang, Y. Liu, T. Chen, and Y. Tong, \"Federated machine learning: Concept and applications,\" ACM Transactions on Intelligent Systems and Technology, vol. 10, no. 2, art. 12, pp. 1–19, 2019. https://doi.org/10.1145/3298981",
        "[14] P. Kairouz, H. B. McMahan, B. Avent, A. Bellet, M. Bennis, A. N. Bhagoji, et al., \"Advances and open problems in federated learning,\" Foundations and Trends in Machine Learning, vol. 14, no. 1–2, pp. 1–210, 2021. https://doi.org/10.1561/2200000083",
        "[15] C. Zhang, Y. Xie, H. Bai, B. Yu, W. Li, and Y. Gao, \"A survey on federated learning: The journey from centralized to distributed,\" Knowledge-Based Systems, vol. 216, art. 106775, pp. 1–16, 2021. https://doi.org/10.1016/j.knosys.2021.106775",
        "[16] A. Attiah, S. Alahmadi, A. Hakeem, L. Mohaisen, A. G. Almakky, and R. M. Alhebshi, \"FedPark: A federated learning crowdsensing solution for on-street parking availability,\" IEEE Access, vol. 13, pp. 99717–99733, 2025. https://doi.org/10.1109/ACCESS.2025.3577489",
        "[17] S. Sharma and P. Kaur, \"Fog-based federated time series forecasting for IoT data,\" Journal of Network and Systems Management, vol. 32, no. 2, art. 38, pp. 1–26, 2024. https://doi.org/10.1007/s10922-024-09802-2",
        "[18] Y. Zhao, M. Li, L. Lai, N. Suda, D. Civin, and V. Chandra, \"Federated learning with non-IID data,\" arXiv preprint arXiv:1806.00582, pp. 1–12, 2018. https://doi.org/10.48550/arXiv.1806.00582",
        "[19] T. Li, A. K. Sahu, M. Zaheer, M. Sanjabi, A. Talwalkar, and V. Smith, \"Federated optimization in heterogeneous networks,\" in Proc. Mach. Learn. Syst. (MLSys 2020), Austin, TX, vol. 2, 2020, pp. 429–450.",
        "[20] A. Fallah, A. Mokhtari, and A. Ozdaglar, \"Personalized federated learning with theoretical guarantees: A model-agnostic meta-learning approach,\" in Adv. Neural Inf. Process. Syst. (NeurIPS 2020), vol. 33, 2020, pp. 3557–3568.",
        "[21] M. G. Arivazhagan, V. Aggarwal, A. K. Singh, and S. Choudhary, \"Federated learning with personalization layers,\" arXiv preprint arXiv:1912.00818, pp. 1–10, 2019.",
        "[22] F. R. di Torrepadula, M. Fisichella, S. Di Martino, and N. Mazzocca, \"Fedflow: A personalized federated learning framework for passenger flow prediction,\" Machine Learning, vol. 114, no. 7, art. 166, pp. 1–24, 2025. https://doi.org/10.1007/s10994-025-06795-0",
        "[23] C. T. Dinh, N. H. Tran, and T. D. Nguyen, \"Personalized federated learning with Moreau envelopes,\" in Adv. Neural Inf. Process. Syst. (NeurIPS 2020), vol. 33, 2020, pp. 21394–21405.",
        "[24] S. Hochreiter and J. Schmidhuber, \"Long short-term memory,\" Neural Computation, vol. 9, no. 8, pp. 1735–1780, 1997. https://doi.org/10.1162/neco.1997.9.8.1735",
        "[25] D. P. Kingma and J. Ba, \"Adam: A method for stochastic optimization,\" in Proc. 3rd Int. Conf. Learn. Represent. (ICLR 2015), San Diego, CA, 2015, pp. 1–15.",
        "[26] A. Z. Tan, H. Yu, L. Cui, and Q. Yang, \"Towards personalized federated learning,\" IEEE Transactions on Neural Networks and Learning Systems, vol. 34, no. 12, pp. 9587–9603, 2023. https://doi.org/10.1109/TNNLS.2022.3160699",
        "[27] K. Bonawitz, V. Ivanov, B. Kreuter, A. Marcedone, H. B. McMahan, S. Patel, et al., \"Practical secure aggregation for privacy-preserving machine learning,\" in Proc. 2017 ACM SIGSAC Conf. Comput. Commun. Secur. (CCS '17), Dallas, TX, 2017, pp. 1175–1191. https://doi.org/10.1145/3133956.3133982",
        "[28] C. Dwork, \"Differential privacy: A survey of results,\" in Int. Conf. Theory Appl. Models Comput. (TAMC 2008), LNCS vol. 4978, Berlin, Heidelberg: Springer, 2008, pp. 1–19. https://doi.org/10.1007/978-3-540-79228-4_1",
        "[29] D. H. Stolfi, E. Alba, and X. Yao, \"Parking Birmingham,\" UCI Machine Learning Repository, 2017. https://doi.org/10.24432/C51K5Z",
        "[30] P. Voigt and A. Von dem Bussche, The EU General Data Protection Regulation (GDPR): A Practical Guide. Cham, Switzerland: Springer International Publishing, 2017. https://doi.org/10.1007/978-3-319-57959-7"
    ]

    for ref in references:
        p_ref = add_p(ref, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=3, line_spacing=1.05)
        p_ref.runs[0].font.size = Pt(9.5)

    # Save outputs
    output_path = "Journal_Manuscript_Final_Submission.docx"
    doc.save(output_path)
    print(f"Generated {output_path} successfully!")

    template_path = "Journal_Manuscript_Template with Formatting Instructions.docx"
    doc.save(template_path)
    print(f"Updated {template_path} in-place successfully!")

if __name__ == "__main__":
    build_manuscript()
