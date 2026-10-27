import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION, WD_ORIENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def apply_table_formatting(tbl, col_widths=None):
    """Sets cantSplit on all rows, tblHeader on header, and sets explicit column widths."""
    if len(tbl.rows) > 0:
        header_tr = tbl.rows[0]._tr.get_or_add_trPr()
        header_tr.append(parse_xml(r'<w:tblHeader xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'))
    
    for row in tbl.rows:
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(r'<w:cantSplit xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'))
    
    if col_widths:
        for row in tbl.rows:
            for c_i, w in enumerate(col_widths):
                if c_i < len(row.cells):
                    row.cells[c_i].width = w

def clone_table(src_tbl, dest_doc, col_widths=None):
    """Clones a table into dest_doc with all formatting intact."""
    new_tbl = dest_doc.add_table(rows=len(src_tbl.rows), cols=len(src_tbl.columns))
    new_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_i, r in enumerate(src_tbl.rows):
        for c_i, c in enumerate(r.cells):
            cell = new_tbl.cell(r_i, c_i)
            cell.text = c.text
            # Style text
            if len(cell.paragraphs) > 0 and len(cell.paragraphs[0].runs) > 0:
                p = cell.paragraphs[0]
                p.runs[0].font.name = 'Calibri'
                if r_i == 0:
                    p.runs[0].bold = True
                    p.runs[0].font.size = Pt(9.0)
                else:
                    p.runs[0].font.size = Pt(8.0 if len(src_tbl.columns) > 8 else 8.5)
    apply_table_formatting(new_tbl, col_widths)
    return new_tbl

papers_30_data = [
        # --- 8 FOUNDATIONAL SEMINAL PAPERS (1997–2020) [EXEMPTED FROM RECENCY] ---
        ["1", "Hochreiter, S., & Schmidhuber, J.", "1997", "Long Short-Term Memory",
         "Recurrent neural network with constant error carrousels and multiplicative input, forget, and output gating.",
         "Synthetic and grammatical sequence benchmarks.",
         "Hidden units, cell states, backpropagation through time truncation.",
         "Overcomes error gradient decay/explosion across extended sequence lags.",
         "Foundational recurrent cell; does not dynamically weight informative temporal time steps.",
         "Journal (Neural Computation) — Foundational",
         "Supplies the recurrent temporal sequence modeling cell adopted across baseline and proposed models."],

        ["2", "Vaswani, A., et al.", "2017", "Attention Is All You Need",
         "Dot-product self-attention and multi-head attention architecture.",
         "WMT 2014 translation benchmark corpora.",
         "Attention heads, key/query/value dimensions d_k, sequence positional encodings.",
         "Demonstrated that attention mechanisms effectively weight variable-length temporal sequence representations.",
         "Formulated for natural language translation; not tailored for continuous multi-client IoT streams.",
         "Conference (NeurIPS) — Foundational",
         "Supplies the mathematical foundation for temporal attention weighting across sequence intervals."],

        ["3", "McMahan, H. B., et al.", "2017", "Communication-Efficient Learning of Deep Networks from Decentralized Data",
         "Federated Averaging (FedAvg) combining decentralized local SGD with server-side weight aggregation.",
         "MNIST image and Shakespeare language modeling benchmarks.",
         "Communication rounds, client participation fraction C, local epochs E, local batch size B.",
         "Proved robust collaborative model training without centralizing or sharing raw training data.",
         "Assumes static client distributions; does not incorporate client personalization for non-IID drift.",
         "Conference (AISTATS / PMLR) — Foundational",
         "Primary collaborative aggregation mechanism adopted across our simulated multi-lot parking clients."],

        ["4", "Bonawitz, K., et al.", "2017", "Practical Secure Aggregation for Privacy-Preserving Machine Learning",
         "Cryptographic secret sharing and multi-party computation for secure federated aggregation.",
         "Simulated mobile edge device federated environments.",
         "Cryptographic key length, communication round overhead, dropped client tolerance.",
         "Guarantees that the central server aggregates model updates without inspecting individual client vectors.",
         "Introduces substantial cryptographic computational overhead; scoped out of Review 1 prototype.",
         "Conference (ACM CCS) — Foundational",
         "Positions cryptographic privacy extensions beyond baseline data locality for future production deployment."],

        ["5", "Stolfi, D. H., Alba, E., & Yao, X.", "2017", "Predicting Car Park Occupancy Rates in Smart Cities",
         "Polynomial regression, Fourier series fitting, and shallow time-series models.",
         "Birmingham Parking Dataset (30 municipal car parks, UK).",
         "Occupancy count, facility capacity, 30-min daytime observation intervals.",
         "Demonstrated that municipal car park occupancy follows predictable diurnal and weekly rhythms.",
         "Shallow models struggle with abrupt demand shifts; centralized, single-operator analysis.",
         "Conference (Springer LNCS, Smart-CT) — Foundational",
         "Supplies the primary empirical testbed (dataset.csv) and historical reference baseline for our study."],

        ["6", "Yu, B., Yin, H., & Zhu, Z.", "2018", "Spatio-Temporal Graph Convolutional Networks (STGCN)",
         "Spatio-temporal graph convolutional networks combining spatial graph convolutions with temporal convolutions.",
         "PeMSD7 traffic speed sensor network dataset.",
         "Adjacency graph matrix, temporal receptive field, RMSE, MAE.",
         "Simultaneously captured spatial road network topologies and dynamic temporal traffic flows.",
         "Requires fixed spatial graph topology; inapplicable to independent, non-adjacent parking facilities.",
         "Conference (IJCAI) — Foundational",
         "Justifies our decision to focus on temporal modeling and federated decentralization rather than graph adjacency."],

        ["7", "Li, T., Sahu, A. K., et al.", "2020", "Federated Optimization in Heterogeneous Networks (FedProx)",
         "FedProx: Local proximal regularization term added to local client optimization objectives.",
         "Synthetic non-IID and Sent140 federated datasets.",
         "Proximal regularization parameter mu, local epochs, gradient variance under heterogeneity.",
         "Guarantees stable federated convergence under severe statistical and system client heterogeneity.",
         "Generic optimization formulation; does not evaluate sequence regression or temporal personalization.",
         "Conference (MLSys) — Foundational",
         "Informs our strategy for handling inter-lot statistical heterogeneity across municipal parking clients."],

        ["8", "Fallah, A., Mokhtari, A., & Ozdaglar, A.", "2020", "Personalized Federated Learning (Per-FedAvg)",
         "Model-Agnostic Meta-Learning (MAML) integrated into decentralized federated averaging.",
         "Distributed synthetic and vision classification benchmarks.",
         "Meta-learning rate alpha, adaptation steps, gradient similarity across clients.",
         "Proved that local fine-tuning after global aggregation substantially mitigates non-IID client drift.",
         "Incurs high second-order Hessian computation cost on constrained edge IoT hardware.",
         "Conference (NeurIPS) — Foundational",
         "Supplies the theoretical foundation for our local fine-tuning personalization stage."],

        # --- 22 RECENT QUALIFYING PAPERS (2021–2026, 73.3% RECENCY) ---
        ["9", "Huang, X., Li, P., Yu, R., Wu, Y., Xie, K., & Xie, S.", "2021", "FedParking: Federated Learning Based Parking Space Estimation",
         "Federated edge computing with parked vehicles for distributed parking space estimation using LSTM.",
         "Parking lot sensor testbed with parked vehicular edge computing nodes.",
         "Edge communication overhead, aggregation interval, LSTM hidden units, estimation error.",
         "Pioneered federated learning for parking space estimation without sharing raw vehicular records.",
         "Omits temporal attention mechanisms; does not incorporate client personalization or multi-tier benchmarking.",
         "Journal (IEEE TVT)",
         "Seminal benchmark paper for federated parking; directly motivates our attention, personalization, and 6-model benchmark."],

        ["10", "Paliari, I., Karanikola, A., & Kotsiantis, S.", "2021", "A Comparison of Optimized LSTM, XGBOOST and ARIMA in Time Series",
         "Empirical multi-tier time-series benchmark comparing optimized ARIMA, XGBoost, and LSTM models.",
         "Diverse continuous temporal time-series benchmark datasets.",
         "Hyperparameter tuning grids, lag features, window sizes, MAE, RMSE, MAPE.",
         "Proved XGBoost captures non-linear tabular patterns while LSTM excels at sequential dependencies.",
         "Evaluated only in centralized settings; does not investigate attention mechanisms or federated learning.",
         "Conference (IEEE IISA)",
         "Directly supplies the multi-tier benchmarking protocol for our ARIMA, XGBoost, and LSTM baselines."],

        ["11", "Dahiya, S., et al.", "2021", "Evaluation of Data Mining Techniques for IoT-Enabled Parking Prediction",
         "Data mining and supervised classification algorithms for smart parking slot availability.",
         "IoT sensor-enabled municipal smart parking testbed.",
         "Classification accuracy, precision, recall, execution time across data mining algorithms.",
         "Demonstrated that municipal IoT sensor streams enable proactive parking guidance with ML classifiers.",
         "Evaluates categorical availability rather than continuous sequence regression; centralized data pooling.",
         "Journal (IJECES)",
         "Demonstrates the practical necessity for predictive availability in municipal IoT parking systems."],

        ["12", "Zhao, D., Ju, C., Zhu, G., & Ning, J.", "2022", "MePark: Using Meters as Sensors for Citywide Parking Prediction",
         "Deep spatio-temporal network utilizing parking meters as distributed IoT sensors for citywide availability.",
         "Citywide on-street parking meter transaction streams.",
         "Transaction intervals, spatial meter clustering, arrival/departure rates, MAE, RMSE.",
         "Demonstrated that existing municipal billing and metering infrastructure provides dense parking availability forecasting.",
         "Requires centralized aggregation of citywide meter transactions; assumes contiguous on-street graph topology.",
         "Journal (IEEE T-ITS)",
         "Establishes on-street parking availability forecasting principles and municipal sensor stream integration."],

        ["13", "Huang, Y.-H., & Hsieh, C.-H.", "2022", "Decision Support System for Available Roadside Parking Slots",
         "Computer vision object detection combined with mathematical optimization for roadside parking slots.",
         "Roadside camera imagery and sensor logs in Taipei, Taiwan.",
         "Detection precision, allocation latency, slot assignment efficiency.",
         "Proved automated detection and optimization improves driver guidance and parking allocation efficiency.",
         "Focuses on current detection and slot allocation; does not perform multi-step sequence forecasting or distributed learning.",
         "Journal (Elsevier ESWA)",
         "Demonstrates practical downstream utility of parking forecasting for intelligent allocation and decision support."],

        ["14", "Zeng, C., Ma, C., Wang, K., & Cui, Z.", "2022", "Parking Occupancy Prediction Based on Stacked GRU-LSTM",
         "Multi-factor stacked recurrent network combining Gated Recurrent Units (GRU) and LSTM.",
         "Municipal parking lot occupancy time series with weather and temporal covariates.",
         "Hidden layer units, stacking depth, time-step lag, MAE, RMSE, MAPE.",
         "Confirmed stacked recurrent layers outperform single-layer models by capturing complex temporal transitions.",
         "Centralized cloud training requiring raw data pooling; lacks dynamic attention weighting and client federation.",
         "Journal (IEEE Access)",
         "Validates recurrent deep-learning efficacy for municipal parking occupancy sequences."],

        ["15", "Li, B.", "2022", "Stochastic Modeling and Adaptive Forecasting for Parking Availability",
         "Non-stationary stochastic arrival/departure queuing model with adaptive filtering for parking availability.",
         "Empirical parking garage entry/exit time series under time-varying driver behavior.",
         "Arrival rate lambda(t), departure rate mu(t), queuing capacity, forecasting horizon.",
         "Modeled stochastic dynamics of parking turnover, proving adaptive updates improve multi-horizon accuracy.",
         "Relies on mathematical queuing assumptions that do not generalize to unmetered multi-lot streams; centralized.",
         "Journal (Elsevier TR-B)",
         "Provides theoretical foundation for time-varying turnover dynamics in parking availability."],

        ["16", "Li, Z., Xu, H., Gao, X., Wang, Z., & Xu, W.", "2022", "Fusion Attention Mechanism Bidirectional LSTM for Traffic Flow",
         "Bidirectional LSTM network integrated with a fused temporal attention mechanism.",
         "Urban arterial and highway sensor traffic flow streams.",
         "Attention weight vectors, bidirectional hidden units, sequence length, MAPE, RMSE.",
         "Proved temporal attention dynamically weights peak rush-hour transitions, significantly reducing forecast lag.",
         "Formulated for continuous highway traffic flow in a centralized cloud; lacks client decentralization.",
         "Journal (Taylor & Francis JITS)",
         "Primary architectural basis for our temporal attention layer over recurrent hidden states."],

        ["17", "Zhang, C., Cui, L., Yu, S., & Yu, J. J. Q.", "2022", "Communication-Efficient Federated Learning for IoT Traffic",
         "Communication-efficient FedAvg featuring gradient compression and event-triggered updates.",
         "Decentralized IoT traffic-sensor stream logs across edge devices.",
         "Compression ratio, communication rounds, transmission bandwidth, RMSE, MAE.",
         "Proved distributed federated learning achieves predictive accuracy competitive with centralized pooling while saving bandwidth.",
         "Evaluates generic traffic sensors; does not incorporate temporal attention or client personalization.",
         "Journal (IEEE IoT-J)",
         "Confirms communication round efficiency metric for evaluating federated edge models."],

        ["18", "Paidi, V.", "2022", "Short-term Prediction of Parking Availability in an Open Lot Using LSTM",
         "Long Short-Term Memory recurrent neural network for short-term parking availability prediction.",
         "Real-world open parking lot sensor stream time series.",
         "Look-back window, hidden layer dimensions, dropout rate, epochs, MAE, RMSE.",
         "Demonstrated standard LSTM accurately captures daily occupancy curves better than shallow regression.",
         "Evaluated strictly on a single parking lot; requires centralized data storage and lacks attention weighting.",
         "Journal (De Gruyter JISYS)",
         "Directly supports LSTM as a core temporal deep-learning baseline for parking occupancy."],

        ["19", "Xia, M., Jin, D., & Chen, J.", "2023", "Short-Term Traffic Flow Prediction Based on GCN and Federated Learning",
         "Spatio-temporal federated learning combining graph convolutional networks with FedAvg for traffic prediction.",
         "Multi-region municipal traffic sensor stream datasets.",
         "Graph adjacency matrix, local training epochs, communication rounds, MAE, RMSE.",
         "Validated that collaborative federated training matches centralized accuracy while keeping traffic streams decentralized.",
         "Relies on road network graph topology; inapplicable to independent, disconnected parking facilities.",
         "Journal (IEEE T-ITS)",
         "Proves federated learning successfully coordinates multiple traffic sensing nodes without raw data sharing."],

        ["20", "Xiao, X., Peng, Z., Lin, Y., Jin, Z., Shao, W., Chen, R., Cheng, N., & Mao, G.", "2023", "Parking Prediction in Smart Cities: A Survey",
         "Comprehensive systematic survey of parking prediction methodologies, architectures, and datasets.",
         "Literature meta-analysis across 100+ smart city parking research articles.",
         "Taxonomy: availability, demand, duration; sensing layers, ML/DL models, evaluation metrics.",
         "Identified that continuous multi-lot forecasting and cross-facility privacy preservation are critical open challenges.",
         "Survey article; does not formulate or implement an empirical experimental model.",
         "Journal (IEEE T-ITS)",
         "Establishes the authoritative state-of-the-art framework and confirms our identified research gaps."],

        ["21", "Kaur, R., Roul, R. K., & Batra, S.", "2023", "Hybrid Deep Learning CNN-ELM Approach for Parking Detection",
         "Hybrid deep architecture combining CNN spatial feature extraction with Extreme Learning Machines (ELM).",
         "PKLot and CNR-EXT smart-parking camera image benchmark datasets.",
         "Classification accuracy, detection F1-score, processing latency.",
         "Proved hybrid deep models achieve high space-occupancy detection accuracy under fluctuating lighting and weather.",
         "Focuses on computer-vision slot classification; does not address temporal sequence forecasting or federated learning.",
         "Journal (Springer NCA)",
         "Highlights contrast between front-end visual detection and downstream temporal sequence forecasting."],

        ["22", "Pandya, S., et al.", "2023", "Federated Learning for Smart Cities: A Comprehensive Survey",
         "Comprehensive survey of federated learning architectures across smart-city infrastructure domains.",
         "Systematic review of 100+ distributed smart-city deployments.",
         "Privacy taxonomy, aggregation mechanisms, communication overhead, urban application sectors.",
         "FL adoption is growing rapidly across smart mobility, but standardized comparative benchmarks remain scarce.",
         "Survey paper; does not formulate or test a specific parking forecasting model.",
         "Journal (Elsevier SETA)",
         "Frames our project within the broader smart-city decentralized AI landscape."],

        ["23", "Zhang, F., Shang, K., Yan, L., Nan, H., & Miao, Z.", "2024", "Parking Space Availability Prediction Using MAT-LSTM",
         "Multi-head Attention Temporal LSTM (MAT-LSTM) for parking space availability forecasting.",
         "Real-world smart parking sensor streams in urban core.",
         "Multi-head attention heads, sequence length, hidden units, MAE, RMSE, MAPE.",
         "Proved multi-head attention over LSTM yields a 48% accuracy gain over standard LSTM by capturing sudden occupancy shifts.",
         "Centralized training requiring all parking data in a single database; lacks federated aggregation.",
         "Journal (MDPI IJGI)",
         "Validates our core Attention-LSTM design and demonstrates attention superiority on parking occupancy."],

        ["24", "Kemik, H., Dalyan, T., & Aydogan, M.", "2024", "Smart Solutions for Mega-Cities: Utilizing LSTM and Multi-Head Attention",
         "Comparative evaluation of LSTM and Multi-Head Attention (MHA) for parking occupancy rate forecasting.",
         "CityPulse smart city parking sensor dataset with environmental covariates.",
         "Sequence window length, attention heads, parameter count, model size, MAE.",
         "Proved attention-augmented models achieve superior accuracy (MAE 0.0589) with fewer parameters and lower latency.",
         "Centralized cloud implementation; does not investigate multi-client federation or client personalization.",
         "Journal (MDPI IJGI)",
         "Directly supports our focus on attention-augmented sequence models for parking availability."],

        ["25", "Sharma, M., & Kaur, P.", "2024", "Fog-Based Federated Time Series Forecasting for IoT Data",
         "Hierarchical fog-based federated learning for decentralized non-IID time series forecasting.",
         "Decentralized IoT sensor time-series benchmarks across fog nodes.",
         "Fog node hierarchy, local LSTM units, RMSE, MAE, communication latency.",
         "Proved federated sequence models converge effectively on non-IID temporal streams without raw data pooling.",
         "Generic IoT benchmark; does not incorporate temporal attention or parking domain personalization.",
         "Journal (Springer JNSM)",
         "Directly supports empirical feasibility of federated time-series learning on non-IID edge nodes."],

        ["26", "Chen, Y., & Zhang, W.", "2024", "Intelligent Transportation Systems: Machine Learning for Urban Mobility",
         "Systematic review of machine learning applications in ITS and urban mobility management.",
         "Meta-analysis of smart city transportation literature and policy frameworks.",
         "Application domain, IoT sensing layer, machine learning paradigms, policy impact.",
         "Highlighted that cross-operator collaboration remains severely under-explored due to commercial data governance barriers.",
         "Review paper; does not propose an empirical model.",
         "Journal (Elsevier SCS)",
         "Reinforces our motivation and justified linkage to SDG 11 and SDG 9."],

        ["27", "Attiah, A., Alahmadi, S., Hakeem, A., & Mohaisen, L.", "2025", "FedPark: Federated Crowdsensing for On-Street Parking",
         "Federated learning crowdsensing framework for on-street parking availability detection and prediction.",
         "Crowdsensed vehicular mobility traces and parking sensor streams.",
         "Client participation rate, local epochs, communication overhead, prediction accuracy.",
         "Demonstrated federated learning enables privacy-preserving collaborative parking availability estimation across participants.",
         "Focuses on mobile crowdsensing rather than stationary multi-lot IoT streams; lacks temporal attention and personalization.",
         "Journal (IEEE Access)",
         "Direct 2025 precedent confirming federated learning relevance for decentralized parking availability."],

        ["28", "Cao, R., Chen, H., & Wang, D. Z. W.", "2025", "Attention-Based Dynamic Graph Model for On-Street Parking",
         "Dynamic spatio-temporal graph neural network with attention mechanisms for parking availability.",
         "Large-scale on-street sensor stream dataset.",
         "Dynamic adjacency matrix, temporal attention weights, spatial convolutions, MAE, RMSE.",
         "Proved attention-guided spatio-temporal modeling dynamically adapts to fluctuating urban parking demand.",
         "Requires high-density contiguous sensor networks; centralized training; high computational overhead.",
         "Journal (Elsevier TR-A)",
         "Confirms that dynamic attention is vital for capturing sudden demand fluctuations in parking."],

        ["29", "Rocco di Torrepadula, F., Fisichella, M., Di Martino, S., & Mazzocca, N.", "2025", "Fedflow: Personalized Federated Framework for Passenger Flow",
         "Personalized federated learning with client-similarity-based local fine-tuning for mobility forecasting.",
         "Multi-operator public transit passenger flow demand records.",
         "Client similarity weights, local fine-tuning epochs, MAE, RMSE, client performance disparity.",
         "Proved personalized federated learning outperforms purely local models and standard FedAvg across competing operators.",
         "Evaluates transit passenger flows; untested on continuous parking bay sensor streams.",
         "Journal (Springer Machine Learning)",
         "Direct structural analogue for our multi-operator personalized federated parking architecture."],

        ["30", "Alterkawi, L., & Dib, F. K.", "2025", "Federated Learning for Smart Cities: A Thematic Review",
         "Systematic PRISMA-guided thematic review of 116 smart city federated learning implementations.",
         "Meta-analysis of smart city federated learning literature.",
         "Data heterogeneity, simulation-to-real gap, evaluation reproducibility, privacy mechanisms.",
         "Found 62% of studies remain simulation-only, identifying data heterogeneity and lack of standardized benchmarking as key open gaps.",
         "Review paper; does not introduce an empirical model.",
         "Journal (MDPI Future Internet)",
         "Confirms that addressing data heterogeneity via personalization and providing transparent benchmarking are top open research priorities."]
    ]

t2_data = [
        ["G1", "Single-location / limited multi-lot modelling", "P5, P11, P12, P14, P18",
         "How can forecasting be performed collaboratively across multiple independent parking lots while accounting for cross-facility operational differences?",
         "Federated multi-lot learning: each parking lot is treated as an independent simulated client partitioned by SystemCodeNumber (Section 22)."],

        ["G2", "Centralized training and raw-data sharing", "P13, P14, P15, P23, P24",
         "Can collaborative multi-lot forecasting be achieved without centralizing raw parking-occupancy data across competing or regulated municipal operators?",
         "Keep raw occupancy data local; only model parameters (weights) are communicated to the aggregator via FedAvg (Section 22-23)."],

        ["G3", "Limited integration of attention-based temporal forecasting with federated learning, specifically for parking", "P9, P16, P23, P26, P27",
         "Can temporal attention mechanisms be integrated with federated learning to capture diurnal rush-hour transitions in decentralized multi-lot parking forecasting?",
         "Design and evaluate a Federated Attention-LSTM tailored to per-lot occupancy sequences, benchmarking against FedParking (P9) and centralized Attention-LSTM (Section 21-22)."],

        ["G4", "Client heterogeneity / parking-lot personalization", "P7, P8, P17, P25, P29",
         "Does client-side local fine-tuning mitigate model degradation caused by non-IID parking capacity and demand pattern differences across heterogeneous facilities?",
         "Incorporate a two-stage Personalized Federated Learning strategy: train the global Attention-LSTM via FedAvg, then perform local fine-tuning per client using client-specific sequences (Section 24)."],

        ["G5", "Incomplete, non-standardized comparative evaluation across baseline tiers", "P10, P20, P22, P30",
         "What is the empirical predictive-performance, communication-round, and data-locality trade-off across classical, machine learning, deep learning, centralized, and federated paradigms under a single reproducible protocol?",
         "Execute a unified 6-model benchmark suite (ARIMA, XGBoost, LSTM, Centralized Attn-LSTM, FedAvg Attn-LSTM, Personalized FedAvg Attn-LSTM) under identical chronological splits and scale-free metrics (Section 29-30)."]
    ]

def build_faculty_report():
    print("Reading source documents...")
    src_rep = docx.Document('Review_1_Report.docx.bak')
    src_orig = docx.Document('41746af9-90c1-4a81-8a93-5cd1a4b523b9.docx')
    
    doc = docx.Document()
    
    # Configure Section 0 (Portrait)
    sec0 = doc.sections[0]
    sec0.orientation = WD_ORIENT.PORTRAIT
    sec0.page_width = Inches(8.5)
    sec0.page_height = Inches(11.0)
    sec0.top_margin = Inches(0.7)
    sec0.bottom_margin = Inches(0.7)
    sec0.left_margin = Inches(0.75)
    sec0.right_margin = Inches(0.75)
    
    # Colors
    NAVY = RGBColor(15, 23, 42)
    BLUE = RGBColor(30, 58, 138)
    MUTED = RGBColor(100, 116, 139)

    # =========================================================================
    # COVER PAGE / HEADER
    # =========================================================================
    p = doc.add_paragraph()
    r = p.add_run("PROJECT REVIEW 1 REPORT")
    r.bold = True
    r.font.size = Pt(13)
    r.font.color.rgb = BLUE

    p = doc.add_paragraph()
    r = p.add_run("Federated Multi-Lot Smart Parking Forecasting Using Attention-Based LSTM on IoT Streams")
    r.bold = True
    r.font.size = Pt(22)
    r.font.color.rgb = NAVY
    p.space_after = Pt(6)

    p = doc.add_paragraph()
    r = p.add_run("Domain: ")
    r.bold = True
    p.add_run("Smart Cities · IoT Sensor Networks · Machine Learning / Deep Learning · Federated Learning · Time-Series Forecasting\n")
    r = p.add_run("Team Number: ")
    r.bold = True
    p.add_run("Team 4 (Devesh Munagala - 23BCT0149, Abhinav - 23BCT0142)\n")
    r = p.add_run("SDG Alignment: ")
    r.bold = True
    p.add_run("SDG 11 (Sustainable Cities and Communities) · SDG 9 (Industry, Innovation and Infrastructure)")
    p.space_after = Pt(14)

    # Document Map
    p = doc.add_paragraph()
    r = p.add_run("Document Map")
    r.bold = True
    r.font.size = Pt(12)
    r.font.color.rgb = BLUE
    
    doc_map_items = [
        "1. Team / Project Information",
        "2. Executive Summary",
        "3. Introduction and Problem Context",
        "4. IoT Environment and Justified SDG Alignment",
        "5. Literature Survey Method and Thematic Review",
        "6. Literature Comparison Table",
        "7. Literature Synthesis and Research Gaps",
        "8. Research-Gap Traceability Matrix",
        "9. Problem Statement, Research Question and Objectives",
        "10. Scope and Boundaries",
        "11. Proposed Methodology and System Architecture",
        "12. Comparative Models, FedAvg Algorithm and Personalization Strategy",
        "13. Dataset Description and Preprocessing Plan",
        "14. Experimental Design and Evaluation Metrics",
        "15. Expected Outcomes, Hypotheses and Feasibility",
        "16. Proposed Work Plan / Timeline and Publication Potential",
        "17. References"
    ]
    for item in doc_map_items:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.2)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(item)
        r.font.size = Pt(9.5)
    
    doc.add_page_break()

    # =========================================================================
    # 1. TEAM / PROJECT INFORMATION
    # =========================================================================
    doc.add_heading("1. Team / Project Information", level=1)
    clone_table(src_rep.tables[0], doc, [Inches(2.2), Inches(4.8)])
    doc.add_paragraph()

    # =========================================================================
    # 2. EXECUTIVE SUMMARY
    # =========================================================================
    doc.add_heading("2. Executive Summary", level=1)
    p = doc.add_paragraph(
        "Cities increasingly rely on IoT sensors to track parking-space occupancy in real time, yet the resulting data is fragmented "
        "across independently operated lots that often cannot, or will not, share raw occupancy records with one another or with a third party. "
        "This project investigates whether an attention-augmented LSTM model can forecast parking-space availability 30-60 minutes ahead by training "
        "collaboratively across multiple parking-lot “clients” using Federated Averaging (FedAvg), so that no lot's raw occupancy data ever leaves its own "
        "system, and whether a further personalization step (local fine-tuning) can compensate for the fact that different lots have different demand patterns."
    )
    p = doc.add_paragraph(
        "The contribution is not a new algorithm but an investigated combination and evaluation: Attention-LSTM + FedAvg + personalization, applied "
        "specifically to multi-lot, multi-operator parking-availability forecasting, and benchmarked against ARIMA, XGBoost, plain LSTM and a centrally trained "
        "Attention-LSTM under one common, reproducible evaluation protocol (MAE, RMSE, MAPE, per-lot performance, communication rounds, and the "
        "centralized-vs-federated performance gap). The deliverable is a research prototype together with these comparative experiments, using the Birmingham "
        "parking dataset as the primary experimental testbed and the Melbourne and San Francisco (SFpark) datasets as secondary, reference-context data (Section 13)."
    )
    p = doc.add_paragraph(
        "This document constitutes the formal Project Review 1 report. It establishes an audited and verified 30-paper literature survey meeting the 70% "
        "recency rubric floor (73.3% recent, 8 foundational works exempted), formalizes the one-sentence problem statement and four measurable objectives, "
        "and details the experimental design, dataset protocol, and six-model comparative benchmark for Review 2 execution."
    )

    # =========================================================================
    # 3. INTRODUCTION AND PROBLEM CONTEXT
    # =========================================================================
    doc.add_heading("3. Introduction and Problem Context", level=1)
    doc.add_paragraph(
        "Urban parking search is a recurring source of congestion, driver frustration and wasted travel time, and it has become a well-established target "
        "for smart-city instrumentation. Municipalities and private operators increasingly install IoT occupancy sensors — in-ground magnetometers, camera-based "
        "detectors, or gate/entry counters — that continuously report whether a bay or lot is occupied. This produces exactly the kind of data smart-city research "
        "depends on: dense, timestamped, per-location occupancy time series."
    )
    doc.add_paragraph(
        "Two structural features of this setting motivate the specific approach taken in this project. First, parking occupancy is a time-series problem with clear "
        "short-term temporal structure (time-of-day and day-of-week patterns, gradual build-up and release of demand), which is well suited to sequence models such "
        "as LSTM, and to attention mechanisms that let a model weight the most informative past time steps rather than all of them equally. Second, and less "
        "commonly addressed in prior parking-forecasting work, a city's parking supply is rarely operated by a single entity: council-run car parks, private operators "
        "and on-street management authorities each hold their own occupancy logs, and there are real competitive and regulatory reasons why they may not wish to "
        "centralize that data. Federated learning is a natural fit for this second constraint: it lets multiple parking-lot clients collaboratively improve a shared "
        "forecasting model by exchanging only model parameters, never raw occupancy records."
    )
    doc.add_paragraph(
        "This project therefore combines an Attention-LSTM forecaster with Federated Averaging (FedAvg) across simulated parking-lot clients, and adds a "
        "personalization stage (local fine-tuning) to address the fact that different lots — a hospital car park, a shopping-centre lot, an on-street residential zone — "
        "are likely to have different occupancy patterns. The result is evaluated against classical (ARIMA) and machine-learning (XGBoost) baselines, a plain LSTM, "
        "and a centrally trained Attention-LSTM, to isolate the specific contribution of attention, of federation, and of personalization."
    )
    doc.add_heading("Problem Context", level=2)
    contexts = [
        ("Dynamic occupancy", "Parking occupancy changes continuously through the day, driven by commuting, retail and event patterns, so a static or infrequently updated availability estimate quickly becomes wrong."),
        ("IoT sensor granularity", "Sensors typically report at intervals of a few minutes to half an hour, which is fine-grained enough to support short-horizon forecasting but requires careful handling of missing readings and sensor gaps."),
        ("Short-term forecasting need", "Knowing current occupancy is useful, but knowing occupancy 30-60 minutes ahead is what actually helps a driver approaching a destination or an operator adjusting pricing/signage."),
        ("Multi-lot / multi-operator setting", "A realistic city has many independently managed parking facilities; pooling data into one central cloud database faces legal, privacy, and commercial resistance."),
        ("Centralized data-sharing limitation", "Pooling every operator's raw occupancy logs onto one central server introduces commercial confidentiality barriers, single-point-of-failure vulnerabilities, and governance overhead."),
        ("Heterogeneity across lots", "Different lot types (commuter, retail, residential) exhibit distinct occupancy curves, causing a single global model to suffer from non-IID client drift unless personalized.")
    ]
    for c_title, c_desc in contexts:
        p = doc.add_paragraph()
        r = p.add_run(f"• {c_title}: ")
        r.bold = True
        p.add_run(c_desc)

    # =========================================================================
    # 4. IOT ENVIRONMENT AND JUSTIFIED SDG ALIGNMENT
    # =========================================================================
    doc.add_heading("4. IoT Environment and Justified SDG Alignment", level=1)
    doc.add_heading("IoT / Smart Parking Environment", level=2)
    doc.add_paragraph(
        "The project's network/IoT setting can be summarized as follows, without assuming a specific hardware vendor:\n"
        "1. Parking sensors at each lot generate occupancy events or periodic measurements (e.g., bay-level ultrasonic/magnetometer sensors or barrier in/out counters aggregated to a lot-level count).\n"
        "2. These data streams originate at distributed parking lots that, in this project's design, act as independent edge clients. Each client maintains its own local historical time-series database.\n"
        "3. A coordination server performs FedAvg aggregation of model parameters received from participating parking-lot clients. It does not ingest raw sensor streams.\n"
        "4. Client-server communication is restricted to model weight updates at the end of each federated round, keeping network payload small and independent of raw stream volume."
    )
    doc.add_heading("Real-World Motivation", level=2)
    doc.add_paragraph(
        "Urban parking search contributes substantially to downtown traffic congestion, driver delays, and localized carbon emissions. While dynamic message signs "
        "display current counts, drivers require predictive intelligence: will a spot be vacant upon arrival 30 to 60 minutes later? A centralized municipal "
        "database is often unachievable due to commercial competition between private garage operators and municipal authorities. Federated learning resolves "
        "this impasse by enabling multi-operator model collaboration while preserving data sovereignty."
    )
    doc.add_heading("Justified SDG Alignment", level=2)
    doc.add_paragraph(
        "• SDG 11 — Sustainable Cities and Communities (Target 11.2 & 11.6): Accurate parking availability forecasts help drivers plan routes and identify free spaces "
        "in advance, which may help reduce vehicle cruising miles, mitigating downtown traffic congestion, fuel waste and associated greenhouse-gas emissions.\n"
        "• SDG 9 — Industry, Innovation and Infrastructure (Target 9.4 & 9.5): Applies innovative machine-learning methods (temporal attention mechanisms, federated learning) "
        "to upgrade municipal IoT sensor networks, demonstrating how existing urban infrastructure can deliver smarter services without expensive new hardware."
    )

    # =========================================================================
    # 5. LITERATURE SURVEY METHOD AND THEMATIC REVIEW
    # =========================================================================
    doc.add_heading("5. Literature Survey Method and Thematic Review", level=1)
    doc.add_paragraph(
        "The literature base was assembled through structured searches across IEEE Xplore, ScienceDirect, SpringerLink, ACM Digital Library, and MDPI. "
        "Peer-reviewed journal articles and reputable conference proceedings directly addressing smart parking, temporal attention, and federated time-series "
        "forecasting were included. Seminal foundational works (LSTM, Transformer-attention, FedAvg, FedProx, Per-FedAvg, STGCN, Secure Aggregation, Stolfi 2017) "
        "were cataloged and explicitly exempted per rubric guidelines. The final matrix contains 30 verified papers, of which 22 (73.3%) fall strictly in the 2021–2026 "
        "window, exceeding the 70% recency floor."
    )
    
    themes = [
        ("Theme A — Smart Parking and Parking Occupancy Forecasting", 
         "Originates from Stolfi, Alba and Yao (2017), who demonstrated that car park occupancy follows strong temporal periodicity using polynomial fitting and Fourier series on the Birmingham dataset. "
         "Subsequent research expanded into machine learning and deep sequential modeling: Dahiya et al. (2021) integrated data-mining classifiers with municipal IoT sensor streams; "
         "Zhao et al. (2022, MePark in IEEE T-ITS) utilized parking meters as distributed IoT sensors for citywide on-street availability forecasting; "
         "Huang and Hsieh (2022, Elsevier ESWA) developed an optimization and roadside parking decision support framework; Zeng et al. (2022, IEEE Access) "
         "demonstrated stacked GRU-LSTM networks for parking occupancy; Li (2022, Transportation Research Part B) formulated non-stationary stochastic "
         "queuing dynamics for time-varying parking turnover; Paidi (2022) applied LSTM to single-facility parking sequences; Xiao et al. (2023, IEEE T-ITS) "
         "provided an authoritative survey categorizing smart-city parking prediction challenges; and Kaur, Roul and Batra (2023, Springer NCA) combined "
         "CNNs with Extreme Learning Machines for space detection. Most recently, Zhang et al. (2024, MAT-LSTM in MDPI IJGI) proved that multi-head attention "
         "mechanisms improve LSTM parking prediction accuracy by 48% over standard recurrent baselines, and Kemik et al. (2024, MDPI IJGI) demonstrated "
         "superior occupancy forecasting using attention over recurrent units in mega-cities. Across Theme A, prior work predominantly trains on centralized "
         "databases for isolated individual facilities, leaving collaborative multi-facility forecasting unaddressed (G1, G2)."),

        ("Theme B — Time-Series and Deep-Learning Forecasting (with Attention)",
         "Attention mechanisms, formulated theoretically by Vaswani et al. (2017), were adapted to transportation time series by Li et al. (2022, JITS), "
         "who showed that temporal attention weights focus on critical rush-hour transition curves, drastically reducing prediction lag. In the parking "
         "domain specifically, Zhang et al. (2024) and Kemik et al. (2024) confirmed that attention-augmented LSTMs achieve state-of-the-art accuracy by "
         "isolating sudden temporal shifts. Spatio-temporal graph models (Yu, Yin & Zhu, 2018, STGCN; Cao et al., 2025, Transportation Research Part A) "
         "model spatial road correlations, but require fixed spatial adjacency graphs that do not exist between independent, physically separated parking "
         "lots. This justifies our deliberate decision to focus on temporal attention while treating facilities as decentralized federated clients (Section 10). "
         "Additionally, Paliari et al. (2021, IEEE IISA) provides the comparative benchmarking protocol comparing ARIMA, XGBoost, and LSTM across sequence horizons."),

        ("Theme C — Federated Learning for IoT / Smart Cities",
         "McMahan et al. (2017) established Federated Averaging (FedAvg) for decentralized optimization without exchanging raw training data; Bonawitz et al. "
         "(2017) introduced secure aggregation protocols; and Li et al. (2020, FedProx) and Fallah et al. (2020, Per-FedAvg) formulated mathematical "
         "guarantees for handling client heterogeneity and personalization. At the smart-city survey level, Pandya et al. (2023) cataloged federated learning "
         "deployments across municipal sectors, while Alterkawi and Dib (2025, MDPI Future Internet) reviewed 116 smart-city FL implementations, finding "
         "that 62% remain simulation-only and emphasizing that non-IID data heterogeneity and the absence of standardized, reproducible comparative "
         "benchmarks are the two most critical open research gaps."),

        ("Theme D — Federated Time-Series Forecasting",
         "Theme D represents the core technical foundation of this project. Huang et al. (2021, IEEE TVT) published FedParking, the seminal work establishing "
         "federated learning for parking space estimation using parked vehicles as edge computing nodes. While FedParking demonstrated the feasibility of "
         "federated parking estimation, it relied on standard LSTM units without temporal attention, lacked client personalization for inter-lot demand "
         "heterogeneity, and omitted comparative benchmarking against classical statistical and machine learning baselines. Subsequent federated mobility "
         "work includes Zhang et al. (2022, IEEE IoT-J) on communication-efficient traffic forecasting, Xia et al. (2023, IEEE T-ITS) on federated traffic flow "
         "prediction, Sharma and Kaur (2024, Springer JNSM) on fog-based federated time-series forecasting over non-IID IoT streams, Attiah et al. (2025, "
         "IEEE Access, FedPark) on crowdsensed on-street parking availability, and Rocco di Torrepadula et al. (2025, Springer Machine Learning, Fedflow) "
         "on personalized federated passenger-flow forecasting across competing transit operators. None of these works combine temporal attention with "
         "client-side personalization and multi-tier comparative benchmarking specifically for multi-lot stationary parking IoT streams (G3, G4, G5)."),

        ("Theme E — Intelligent Transportation Systems / Smart City Forecasting",
         "Chen and Zhang (2024, Sustainable Cities and Society) situate machine-learning-based ITS within the broader smart-city urban-mobility landscape, "
         "noting growing integration of IoT real-time monitoring but continued under-exploration of privacy-preserving, cross-operator collaborative learning "
         "for mobility services due to commercial data governance barriers — reinforcing our motivation and alignment with SDG 11 and SDG 9.")
    ]
    for t_head, t_body in themes:
        doc.add_heading(t_head, level=2)
        doc.add_paragraph(t_body)

    # =========================================================================
    # 6. LITERATURE COMPARISON TABLE (SECTION 1: LANDSCAPE)
    # =========================================================================
    # Add section break for Landscape table
    sec1 = doc.add_section(WD_SECTION.NEW_PAGE)
    sec1.orientation = WD_ORIENT.LANDSCAPE
    sec1.page_width = Inches(11.0)
    sec1.page_height = Inches(8.5)
    sec1.top_margin = Inches(0.5)
    sec1.bottom_margin = Inches(0.5)
    sec1.left_margin = Inches(0.5)
    sec1.right_margin = Inches(0.5)

    doc.add_heading("6. Literature Comparison Table", level=1)
    doc.add_paragraph(
        "Table numbering (P1–P30) serves as the persistent citation key referenced by the Research-Gap Traceability Matrix (Section 8) and References (Section 17). "
        "8 foundational seminal works (1997–2020) are explicitly labeled and exempted per rubric guidelines; 22 recent works (2021–2026) satisfy the 70% recency floor (73.3%)."
    )
    
    t1_widths = [
        Inches(0.40),  # No.
        Inches(1.10),  # Authors
        Inches(0.65),  # Yr (WIDENED: No year will split!)
        Inches(1.15),  # Paper / Topic
        Inches(1.05),  # Method
        Inches(1.00),  # Dataset
        Inches(0.85),  # Params
        Inches(1.05),  # Finding
        Inches(1.05),  # Limitation
        Inches(0.80),  # Venue
        Inches(0.90),  # Relevance
    ]
    # Build Table 1 from 30 papers
    headers_t1 = ['No.', 'Author(s)', 'Yr', 'Paper / Topic', 'Method', 'Dataset / Testbed', 'Parameters / Features', 'Key Finding', 'Limitation / Open Issue', 'Venue Type', 'Relevance to Our Project']
    t1 = doc.add_table(rows=1, cols=11)
    t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h in enumerate(headers_t1):
        cell = t1.cell(0, j)
        cell.text = h
        p = cell.paragraphs[0]
        p.runs[0].bold = True
        p.runs[0].font.size = Pt(8.5)
        p.runs[0].font.name = 'Calibri'
    for r_data in papers_30_data:
        row = t1.add_row()
        for c_idx, val in enumerate(r_data):
            cell = row.cells[c_idx]
            cell.text = val
            p = cell.paragraphs[0]
            p.runs[0].font.size = Pt(8.0)
            p.runs[0].font.name = 'Calibri'
    apply_table_formatting(t1, t1_widths)

    # =========================================================================
    # 7. LITERATURE SYNTHESIS AND RESEARCH GAPS (SECTION 2: PORTRAIT)
    # =========================================================================
    sec2 = doc.add_section(WD_SECTION.NEW_PAGE)
    sec2.orientation = WD_ORIENT.PORTRAIT
    sec2.page_width = Inches(8.5)
    sec2.page_height = Inches(11.0)
    sec2.top_margin = Inches(0.7)
    sec2.bottom_margin = Inches(0.7)
    sec2.left_margin = Inches(0.75)
    sec2.right_margin = Inches(0.75)

    doc.add_heading("7. Literature Synthesis and Research Gaps", level=1)
    doc.add_paragraph(
        "Read together, the 30 papers (P1–P30) show a clear, logical progression toward this project's research problem rather than a disjointed collection "
        "of smart-city studies. Foundational papers establish the architectural building blocks (LSTM in P1, Attention in P2, FedAvg in P3, FedProx in P7, "
        "Per-FedAvg in P8). Recent smart-parking studies establish that deep sequence models and attention mechanisms yield superior availability predictions "
        "(P5, P11, P12, P14, P18, P23, P24), but are constrained by centralized data architectures. Seminal federated works establish decentralized "
        "feasibility (FedParking in P9, FedPark in P27), yet leave temporal attention weighting, client personalization under non-IID demand, and unified "
        "cross-tier benchmarking unaddressed."
    )
    doc.add_heading("Centralized vs. Distributed Training", level=2)
    doc.add_paragraph(
        "While earlier and classical parking studies (P5, P11, P12, P13, P14, P15, P18, P23, P24) rely strictly on centralized dataset pooling, recent seminal "
        "efforts have begun exploring federated architectures in parking: Huang et al. (P9, FedParking) evaluated federated edge computing with parked vehicles "
        "for parking space estimation, and Attiah et al. (P27, FedPark) demonstrated mobile crowdsensing for on-street parking availability. However, these works "
        "either rely on opportunistic mobile/vehicular nodes without temporal sequence attention, or focus on space detection rather than continuous multi-step "
        "sequence forecasting, and neither provides client-side personalization to handle inter-lot demand heterogeneity across permanent municipal facilities. "
        "Federated time-series models elsewhere (P17, P19, P25, P29) focus primarily on highway road graphs or transit passenger flows. Our specific research "
        "contribution bridges this precise junction: applying attention-augmented sequential forecasting with client personalization to decentralized, "
        "multi-lot stationary municipal parking streams under a unified cross-tier benchmark."
    )
    doc.add_heading("Single-Lot vs. Multi-Lot Forecasting", level=2)
    doc.add_paragraph(
        "Most continuous sequence forecasters model single facilities in isolation or assume a single administrative entity. Where multi-facility collaboration "
        "has been investigated, facilities are either treated as homogeneous or pooled centrally. In contrast, our project models distinct parking facilities "
        "as heterogeneous federated clients that train collaboratively via FedAvg and personalize locally without centralizing raw records."
    )
    doc.add_heading("Identified Research Gaps (G1–G5)", level=2)
    gaps_def = [
        ("G1. Single-location / limited multi-lot modelling",
         "Finding from literature: Several parking-forecasting studies (P5, P11, P12, P14, P18) model one location or one dataset in isolation rather than multiple independently operated lots collaborating.\n"
         "Unresolved technical question: How can forecasting be performed collaboratively across multiple independent parking lots while accounting for cross-facility operational differences?\n"
         "Proposed response: Federated multi-lot learning: each parking lot is treated as an independent simulated client partitioned by SystemCodeNumber (Section 11)."),

        ("G2. Centralized training and raw-data sharing",
         "Finding from literature: Advanced machine learning and deep learning parking studies (P13, P14, P15, P23, P24) still require pooling raw sensor records into a single central database.\n"
         "Unresolved technical question: Can collaborative multi-lot forecasting be achieved without centralizing raw parking-occupancy data across competing or regulated municipal operators?\n"
         "Proposed response: Decentralized FedAvg: raw occupancy data remains strictly local at each client; only model parameters (weights) are communicated to the aggregator (Section 11)."),

        ("G3. Limited integration of attention-based temporal forecasting with federated learning, specifically for parking",
         "Finding from literature: Attention-augmented models in parking (P16, P23 MAT-LSTM, P24) remain centralized. FedParking (P9) demonstrated vehicular edge FL for parking but omitted temporal attention, while crowdsensing FL (P27) focused on space detection. Federated attention mobility models (P19, P28) require road-network graphs.\n"
         "Unresolved technical question: Can temporal attention mechanisms be integrated with federated learning to capture diurnal rush-hour transitions in decentralized multi-lot parking forecasting?\n"
         "Proposed response: Design and evaluate a Federated Attention-LSTM tailored to per-lot occupancy sequences, benchmarking against FedParking (P9) and centralized Attention-LSTM (Section 11)."),

        ("G4. Client heterogeneity / parking-lot personalization",
         "Finding from literature: Theoretical personalized-FL formulations (P7 FedProx, P8 Per-FedAvg) and transit passenger-flow models (P29 Fedflow) show personalization mitigates non-IID client drift, but this has not been evaluated for multi-facility municipal parking lot time series.\n"
         "Unresolved technical question: Does client-side local fine-tuning mitigate model degradation caused by non-IID parking capacity and demand pattern differences across heterogeneous facilities?\n"
         "Proposed response: Incorporate a two-stage Personalized Federated Learning strategy: train the global Attention-LSTM via FedAvg, then perform local fine-tuning per client using client-specific historical sequences (Section 11)."),

        ("G5. Incomplete, non-standardized comparative evaluation across baseline tiers",
         "Finding from literature: Time-series baseline benchmarks (P10 Paliari) compare ARIMA, XGBoost, and LSTM in centralized settings; smart parking surveys (P20 Xiao) and smart-city FL surveys (P22 Pandya, P30 Alterkawi) explicitly identify the lack of standardized, reproducible cross-tier comparative benchmarking as the primary open research challenge.\n"
         "Unresolved technical question: What is the empirical predictive-performance, communication-round, and data-locality trade-off across classical, machine learning, deep learning, centralized, and federated paradigms under a single reproducible protocol?\n"
         "Proposed response: Execute a unified 6-model benchmark suite (ARIMA, XGBoost, LSTM, Centralized Attn-LSTM, FedAvg Attn-LSTM, Personalized FedAvg Attn-LSTM) under identical chronological splits and scale-free metrics (Section 12, 14).")
    ]
    for g_title, g_body in gaps_def:
        doc.add_heading(g_title, level=3)
        doc.add_paragraph(g_body)

    # =========================================================================
    # 8. RESEARCH-GAP TRACEABILITY MATRIX
    # =========================================================================
    doc.add_heading("8. Research-Gap Traceability Matrix", level=1)
    doc.add_paragraph(
        "Table 2 maps each identified technical gap to its supporting literature citations (P-IDs) from Table 1, the specific unresolved technical question, "
        "and our project's concrete engineering response."
    )
    # Build Table 2 from t2_data
    headers_t2 = ['Gap ID', 'Finding from Literature (short)', 'Supporting Papers', 'Unresolved Technical Question', 'Proposed Response in Our Project']
    t2_widths = [Inches(0.6), Inches(1.5), Inches(1.2), Inches(2.0), Inches(1.7)]
    t2 = doc.add_table(rows=1, cols=5)
    t2.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h in enumerate(headers_t2):
        cell = t2.cell(0, j)
        cell.text = h
        p = cell.paragraphs[0]
        p.runs[0].bold = True
        p.runs[0].font.size = Pt(9.0)
        p.runs[0].font.name = 'Calibri'
    for r_data in t2_data:
        row = t2.add_row()
        for c_idx, val in enumerate(r_data):
            cell = row.cells[c_idx]
            cell.text = val
            p = cell.paragraphs[0]
            p.runs[0].font.size = Pt(8.5)
            p.runs[0].font.name = 'Calibri'
    apply_table_formatting(t2, t2_widths)
    doc.add_paragraph()

    # =========================================================================
    # 9. PROBLEM STATEMENT, RESEARCH QUESTION AND OBJECTIVES
    # =========================================================================
    doc.add_heading("9. Problem Statement, Research Question and Objectives", level=1)
    doc.add_heading("One-Sentence Problem Statement", level=2)
    p = doc.add_paragraph()
    r = p.add_run(
        "\"To forecast short-term parking availability (30–60 minutes ahead) across multiple independently operated lots using an attention-augmented "
        "LSTM trained collaboratively via Federated Averaging (FedAvg) and personalized through local fine-tuning, so that no lot's raw occupancy data leaves "
        "its local system while achieving predictive performance competitive with centralized training.\""
    )
    r.bold = True
    r.font.color.rgb = BLUE

    doc.add_heading("Core Research Question", level=2)
    doc.add_paragraph(
        "Can an attention-augmented LSTM model collaboratively trained via Federated Averaging across multiple parking-lot clients, combined with local fine-tuning "
        "for personalization, achieve short-term availability forecasting accuracy competitive with a centrally trained model without centralizing raw occupancy data?"
    )

    doc.add_heading("Measurable Objectives", level=2)
    objectives = [
        ("Objective 1", "Implement and evaluate centralized baseline forecasting models (ARIMA, XGBoost, LSTM, and Attention-LSTM) on the primary multi-lot parking dataset to establish performance reference points and isolate the benefit of temporal attention."),
        ("Objective 2", "Implement federated collaborative training using FedAvg across multiple parking-lot clients, so that raw occupancy data never leaves the client and only model parameters are communicated to the aggregation server."),
        ("Objective 3", "Design and evaluate a personalized federated learning strategy (local fine-tuning per client) to address inter-lot occupancy pattern heterogeneity, comparing personalized vs. global federated performance."),
        ("Objective 4", "Perform a standardized comparative evaluation across all six model configurations using common preprocessing, identical chronological train/val/test splits, and scale-free metrics (MAE, RMSE, epsilon-smoothed MAPE, and the federated-centralized performance gap).")
    ]
    for o_num, o_text in objectives:
        p = doc.add_paragraph()
        r = p.add_run(f"• {o_num}: ")
        r.bold = True
        p.add_run(o_text)

    # =========================================================================
    # 10. SCOPE AND BOUNDARIES
    # =========================================================================
    doc.add_heading("10. Scope and Boundaries", level=1)
    doc.add_paragraph(
        "To maintain feasibility within semester timelines and hardware constraints, explicit boundaries are declared:\n"
        "• In Scope: Short-term availability forecasting (30 and 60 minutes ahead); time-series occupancy streams from stationary sensors; simulated multi-client federated learning partitioned by SystemCodeNumber on Birmingham data; 6-model comparative evaluation; client personalization via local fine-tuning; evaluation on normalized availability ratio in [0, 1].\n"
        "• Out of Scope: Real-time sensor hardware deployment or edge microcontrollers; cryptographic differential privacy or multi-party encryption (beyond data locality); live dynamic parking pricing / reservation algorithms; spatial road-network graph modeling (STGCN) requiring physical adjacency; computer-vision license plate recognition."
    )

    # =========================================================================
    # 11. PROPOSED METHODOLOGY AND SYSTEM ARCHITECTURE
    # =========================================================================
    doc.add_heading("11. Proposed Methodology and System Architecture", level=1)
    doc.add_paragraph(
        "The project methodology follows a structured 9-step progression:\n"
        "1. Dataset Acquisition: Secure Birmingham Parking time series (30 lots, 35,717 rows) as primary testbed; reference SFpark and Melbourne for contextual transferability.\n"
        "2. Data Cleaning & Session Handling: Forward-fill missing readings within operating windows (08:00–16:30); remove nocturnal hiatus periods.\n"
        "3. Feature Engineering & Tensor Construction: Calculate normalized availability ratio y_t = (Capacity - Occupancy)/Capacity in [0, 1]; append temporal cyclical features (hour, day-of-week); construct sliding sequences of shape [Batch, 12, 5].\n"
        "4. Classical & ML Baselines: Fit ARIMA(p,d,q) and XGBoost with lag features.\n"
        "5. Centralized Deep Recurrent Models: Train Centralized LSTM and Centralized Attention-LSTM on pooled training data.\n"
        "6. Distributed Federated Learning (FedAvg): Partition data across 30 simulated clients; train local models for E epochs; aggregate weights at coordination server.\n"
        "7. Client Personalization: Apply local fine-tuning on the converged global model using client-specific sequences.\n"
        "8. Multi-Horizon Forecasting: Generate predictions at 30-min (1 step) and 60-min (2 steps) horizons.\n"
        "9. Standardized Benchmark: Evaluate all 6 models under identical chronological test sets."
    )
    doc.add_heading("Attention-LSTM Architecture Formulation", level=2)
    doc.add_paragraph(
        "The client sequence model consists of an LSTM recurrent layer producing hidden states H = [h_1, h_2, ..., h_L] across sequence length L = 12. "
        "A temporal dot-product attention layer computes scalar alignment scores e_t = v^T tanh(W h_t + b), normalized via softmax to produce attention weights "
        "alpha_t = exp(e_t) / Sum exp(e_j). The temporal context vector c = Sum (alpha_t * h_t) aggregates historical hidden representations, weighting sudden "
        "morning and afternoon transition states, before feeding into a dense linear output layer predicting y_(t+h)."
    )
    doc.add_heading("System Architecture", level=2)
    doc.add_paragraph(
        "The distributed architecture consists of 30 Simulated Client Nodes and 1 Central Coordination Server:\n"
        "• Local Client Layer: Each client manages local data ingestion, normalization scaling, local SGD optimization, and local evaluation.\n"
        "• Communication Layer: Exchanges weight parameter tensors θ_k between clients and the server via simulated RPC/in-memory Flower protocol.\n"
        "• Central Aggregator: Executes FedAvg aggregation θ_global = Sum (n_k / N * θ_k) across participating client subsets at each round r."
    )

    # =========================================================================
    # 12. COMPARATIVE MODELS, FEDAVG ALGORITHM AND PERSONALIZATION STRATEGY
    # =========================================================================
    doc.add_heading("12. Comparative Models, FedAvg Algorithm and Personalization Strategy", level=1)
    doc.add_heading("Comparative Model Suite (6 Tiers)", level=2)
    clone_table(src_rep.tables[3], doc, [Inches(2.5), Inches(4.5)])
    doc.add_paragraph()

    doc.add_heading("Federated Averaging Algorithm Mechanics", level=2)
    doc.add_paragraph(
        "At each communication round r = 1, ..., R:\n"
        "1. Server broadcasts global weight vector θ_(r-1) to selected client fraction C (e.g., C = 1.0 or C = 0.5).\n"
        "2. Each selected client k sets θ_k^(0) = θ_(r-1) and executes local SGD across E local epochs with batch size B and learning rate eta.\n"
        "3. Clients transmit updated weights θ_k^(E) back to the server; raw sensor measurements never leave local storage.\n"
        "4. Server computes weighted global average θ_r = Sum_k (n_k / n) * θ_k^(E) and broadcasts for the subsequent round."
    )

    doc.add_heading("Client Personalization Strategy", level=2)
    doc.add_paragraph(
        "To mitigate client drift caused by non-IID parking demand patterns (e.g., shopping center lots with midday peaks vs. commuter station lots with morning/evening spikes), "
        "we implement localized fine-tuning: each client freezes lower feature-extraction LSTM layers of the converged global model θ_R and fine-tunes the upper attention and "
        "dense regression layers for K local adaptation epochs using its own validation/training split."
    )

    doc.add_heading("Algorithmic Pseudocode", level=2)
    doc.add_paragraph(
        "Algorithm 1: Local Attention-LSTM Training\n"
        "Input: Client k sequence tensor X_k in R^[N, 12, 5], target y_k, local epochs E, learning rate eta.\n"
        "1. For epoch e = 1 to E:\n"
        "2.   Compute hidden states H = LSTM(X_k)\n"
        "3.   Compute temporal attention weights alpha = Softmax(v^T tanh(W H + b))\n"
        "4.   Compute context vector c = Sum(alpha_t * h_t)\n"
        "5.   Generate prediction y_hat = Dense(c)\n"
        "6.   Compute loss L = MSE(y_k, y_hat) and update weights via Adam backpropagation.\n"
        "7. Return updated local weights θ_k.\n\n"
        "Algorithm 2: Federated Averaging (FedAvg) Server Orchestration\n"
        "Input: Number of clients K = 30, communication rounds R, local epochs E, client fraction C.\n"
        "1. Initialize global weights θ_0.\n"
        "2. For round r = 1 to R:\n"
        "3.   Sample client subset S_r of size max(C * K, 1).\n"
        "4.   For each client k in S_r in parallel: θ_k^r = LocalUpdate(k, θ_(r-1)).\n"
        "5.   Aggregate global model: θ_r = Sum_(k in S_r) (n_k / Sum n_j) * θ_k^r.\n"
        "6. Return final global model θ_R.\n\n"
        "Algorithm 3: Local Personalization via Fine-Tuning\n"
        "Input: Global model θ_R, client k local dataset D_k, adaptation epochs K_adapt, adaptation learning rate eta_adapt.\n"
        "1. For each client k = 1 to K:\n"
        "2.   Initialize personalized model θ_k^pers = Copy(θ_R).\n"
        "3.   Freeze base LSTM recurrent parameters in θ_k^pers.\n"
        "4.   Train attention and output layers on D_k for K_adapt epochs.\n"
        "5. Return personalized models {θ_1^pers, ..., θ_K^pers}."
    )

    # =========================================================================
    # 13. DATASET DESCRIPTION AND PREPROCESSING PLAN
    # =========================================================================
    doc.add_heading("13. Dataset Description and Preprocessing Plan", level=1)
    doc.add_heading("Dataset Roles & Structure", level=2)
    clone_table(src_rep.tables[4], doc, [Inches(1.2), Inches(1.3), Inches(1.5), Inches(1.0), Inches(1.0), Inches(1.0)])
    doc.add_paragraph()

    doc.add_heading("Empirical Dataset Audit (Birmingham Testbed)", level=2)
    doc.add_paragraph(
        "The Birmingham Parking dataset (dataset.csv) was acquired directly from the official UCI repository and verified via Python scripts:\n"
        "• Total Records: 35,717 rows across 4 attributes (SystemCodeNumber, Capacity, Occupancy, LastUpdated).\n"
        "• Facility Count: Exactly 30 unique parking facilities ranging in capacity from 220 to 4,675 spaces.\n"
        "• Temporal Sampling: Daytime operating hours (approx. 08:00 to 16:30) with observation intervals predominantly 27 to 33 minutes.\n"
        "• Missing Value Protocol: Missing steps within active daytime sessions are forward-filled; multi-day gaps between operating windows are maintained as distinct sequence boundaries to prevent cross-day sequence bleeding."
    )

    doc.add_heading("Target Variable Formulation & Chronological Split", level=2)
    doc.add_paragraph(
        "• Normalized Availability Ratio: y_t = (Capacity_k - Occupancy_t,k) / Capacity_k in [0, 1]. Normalizing by lot capacity ensures scale invariance across lots of varying sizes.\n"
        "• Chronological Partitioning: For each lot k, data is sorted strictly by timestamp and split into Train (first 70%), Validation (subsequent 15%), and Test (final 15%) without shuffling, avoiding temporal lookahead bias."
    )

    # =========================================================================
    # 14. EXPERIMENTAL DESIGN AND EVALUATION METRICS
    # =========================================================================
    doc.add_heading("14. Experimental Design and Evaluation Metrics", level=1)
    doc.add_heading("Standardized Evaluation Metrics", level=2)
    doc.add_paragraph(
        "1. Scale-Free Errors (Primary): MAE and RMSE are computed directly on the normalized availability ratio y_t in [0, 1] across all lots.\n"
        "2. Physical Space Error: To provide municipal interpretability, vacant bay error is computed per lot k: MAE_spaces^(k) = MAE_ratio^(k) * Capacity_k. Reported as macro-average and capacity-weighted mean.\n"
        "3. Zero-Smoothed Epsilon-MAPE: Classical MAPE divides by zero when a lot is 100% full (y_t = 0). We employ epsilon-smoothing (epsilon = 0.05): MAPE = (100% / N) * Sum (|y_t - y_hat_t| / max(y_t, 0.05)).\n"
        "4. Federated-to-Centralized Error Gap: Delta_FC = MAE(Fed) - MAE(Centralized), reported as absolute difference and percentage penalty to quantify the empirical cost of data locality.\n"
        "5. Inter-Lot Disparity: Evaluated as the standard deviation of MAE across all 30 parking clients to measure performance equity and confirm whether personalization reduces variance across lots.\n"
        "6. Communication Convergence: Number of federated communication rounds required to reach validation loss convergence."
    )

    # =========================================================================
    # 15. EXPECTED OUTCOMES, HYPOTHESES AND FEASIBILITY
    # =========================================================================
    doc.add_heading("15. Expected Outcomes, Hypotheses and Feasibility", level=1)
    doc.add_heading("Qualitative Research Hypotheses", level=2)
    hypotheses = [
        ("Hypothesis H1 (Attention Benefit)", "The Centralized Attention-LSTM will achieve lower MAE and RMSE than plain LSTM and XGBoost, particularly during morning entry and evening exit rush hours."),
        ("Hypothesis H2 (Data-Locality Trade-Off)", "Federated Attention-LSTM (FedAvg) will track the centralized model within an acceptable accuracy penalty (Delta_FC <= 5-8% relative MAE) while transmitting zero raw occupancy records."),
        ("Hypothesis H3 (Personalization Benefit)", "Personalized Federated Attention-LSTM will outperform the global federated model and reduce inter-lot performance variance across heterogeneous facilities."),
        ("Hypothesis H4 (Multi-Horizon Degradation)", "Forecasting accuracy across all models will degrade gracefully from 30 minutes to 60 minutes, with attention mechanisms maintaining superior stability over extended horizons.")
    ]
    for h_name, h_desc in hypotheses:
        p = doc.add_paragraph()
        r = p.add_run(f"• {h_name}: ")
        r.bold = True
        p.add_run(h_desc)

    doc.add_heading("Hardware, Software & Feasibility", level=2)
    clone_table(src_rep.tables[5], doc, [Inches(2.5), Inches(4.5)])
    doc.add_paragraph()

    # =========================================================================
    # 16. PROPOSED WORK PLAN / TIMELINE AND PUBLICATION POTENTIAL
    # =========================================================================
    doc.add_heading("16. Proposed Work Plan / Timeline and Publication Potential", level=1)
    doc.add_heading("Indicative Schedule Across Project Phases", level=2)
    clone_table(src_rep.tables[6], doc, [Inches(2.2), Inches(1.5), Inches(3.3)])
    doc.add_paragraph()

    doc.add_heading("Detailed Review 2 Implementation Work Sequence", level=2)
    steps_r2 = [
        ("Phase 1 — Data Preprocessing & Partitioning", "Implement automated data cleaning, forward-filling within operating sessions, availability ratio normalization, and 70/15/15 chronological split per lot."),
        ("Phase 2 — Multi-Tier Baseline Implementations", "Fit ARIMA(p,d,q) via Statsmodels and XGBoost with temporal lag features to establish reference statistical performance tiers."),
        ("Phase 3 — Centralized Deep Learning Models", "Implement Centralized LSTM and Attention-LSTM in PyTorch, tuning hidden dimensions, look-back windows, and dropout rates (testing H1)."),
        ("Phase 4 — Distributed Federated Simulation", "Build client-server FedAvg simulation across 30 parking clients partitioned by SystemCodeNumber, tracking loss convergence across communication rounds (testing H2)."),
        ("Phase 5 — Client Personalization Layer", "Implement localized fine-tuning per client on the global aggregated model, evaluating performance gains on client test sets (testing H3)."),
        ("Phase 6 — Comparative Evaluation Suite", "Run all 6 models under identical chronological test sets, computing MAE, RMSE, epsilon-smoothed MAPE, per-lot MAE_spaces, and delta_FC across 30- and 60-minute horizons."),
        ("Phase 7 — Results Compilation & Manuscript Preparation", "Draft comprehensive Review 2 report, generate benchmark comparison tables and convergence plots, and align findings with the publication roadmap.")
    ]
    for s_num, s_desc in steps_r2:
        p = doc.add_paragraph()
        r = p.add_run(f"• {s_num}: ")
        r.bold = True
        p.add_run(s_desc)

    doc.add_heading("Publication Potential & Roadmap", level=2)
    doc.add_paragraph(
        "Upon successful empirical completion in Review 2, the results are targeted for submission to reputable peer-reviewed venues (e.g., IEEE Transactions on Intelligent Transportation Systems, "
        "Elsevier Sustainable Cities and Society, or IEEE Internet of Things Journal). The planned manuscript contribution centers on: (1) an empirical multi-tier benchmark isolating the exact "
        "cost of data locality in multi-lot parking; (2) demonstrating temporal attention gains under federated optimization; and (3) validating personalized federated learning against non-IID municipal demand curves."
    )

    # =========================================================================
    # 17. REFERENCES
    # =========================================================================
    doc.add_heading("17. References", level=1)
    doc.add_paragraph(
        "All 30 references are cataloged in standard APA style with persistent identifiers [P1]–[P30] matching the Literature Comparison Table (Section 6) "
        "and Research-Gap Traceability Matrix (Section 8). 8 seminal foundational works are explicitly exempted; 22 recent works (2021–2026) satisfy the 70% recency floor (73.3%)."
    )
    
    bib_30 = [
        "[P1] Hochreiter, S., & Schmidhuber, J. (1997). Long Short-Term Memory. Neural Computation, 9(8), 1735–1780. https://doi.org/10.1162/neco.1997.9.8.1735 [Foundational / Exempt]",
        "[P2] Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, L., & Polosukhin, I. (2017). Attention Is All You Need. In Advances in Neural Information Processing Systems (NeurIPS 2017), 30, 5998–6008. [Foundational / Exempt]",
        "[P3] McMahan, H. B., Moore, E., Ramage, D., Hampson, S., & y Arcas, B. A. (2017). Communication-Efficient Learning of Deep Networks from Decentralized Data. In Proc. 20th International Conference on Artificial Intelligence and Statistics (AISTATS / PMLR), 54, 1273–1282. [Foundational / Exempt]",
        "[P4] Bonawitz, K., Ivanov, V., Kreuter, B., Marcedone, A., McMahan, H. B., Patel, S., Ramage, D., Segal, A., & Seth, K. (2017). Practical Secure Aggregation for Privacy-Preserving Machine Learning. In Proc. 2017 ACM SIGSAC Conference on Computer and Communications Security (CCS '17), 1175–1191. https://doi.org/10.1145/3133956.3134012 [Foundational / Exempt]",
        "[P5] Stolfi, D. H., Alba, E., & Yao, X. (2017). Predicting Car Park Occupancy Rates in Smart Cities. In Smart Cities (Smart-CT 2017), Lecture Notes in Computer Science, 10268, 107–117. Springer. https://doi.org/10.1007/978-3-319-59513-9_11 [Foundational / Exempt]",
        "[P6] Yu, B., Yin, H., & Zhu, Z. (2018). Spatio-Temporal Graph Convolutional Networks: A Deep Learning Framework for Traffic Forecasting. In Proc. 27th International Joint Conference on Artificial Intelligence (IJCAI-18), 3634–3640. https://doi.org/10.24963/ijcai.2018/505 [Foundational / Exempt]",
        "[P7] Li, T., Sahu, A. K., Zaheer, M., Sanjabi, M., Talwalkar, A., & Smith, V. (2020). Federated Optimization in Heterogeneous Networks (FedProx). In Proc. 3rd MLSys Conference, 429–450. [Foundational / Exempt]",
        "[P8] Fallah, A., Mokhtari, A., & Ozdaglar, A. (2020). Personalized Federated Learning with Theoretical Guarantees: A Model-Agnostic Meta-Learning Approach. In Advances in Neural Information Processing Systems (NeurIPS 2020), 33, 3557–3568. [Foundational / Exempt]",
        "[P9] Huang, X., Li, P., Yu, R., Wu, Y., Xie, K., & Xie, S. (2021). FedParking: A Federated Learning Based Parking Space Estimation With Parked Vehicle Assisted Edge Computing. IEEE Transactions on Vehicular Technology, 70(9), 9355–9368. https://doi.org/10.1109/TVT.2021.3098170",
        "[P10] Paliari, I., Karanikola, A., & Kotsiantis, S. (2021). A Comparison of the Optimized LSTM, XGBOOST and ARIMA in Time Series Forecasting. In Proc. 2021 12th International Conference on Information, Intelligence, Systems & Applications (IISA / IEEE), 1–7. https://doi.org/10.1109/iisa52424.2021.9555520",
        "[P11] Dahiya, S., et al. (2021). Evaluation of Data Mining Techniques and Its Fusion with IoT Enabled Smart Technologies for Effective Prediction of Available Parking Space. International Journal of Electrical and Computer Engineering Systems, 12(4), 205–216. https://doi.org/10.32985/ijeces.12.4.2",
        "[P12] Zhao, D., Ju, C., Zhu, G., & Ning, J. (2022). MePark: Using Meters as Sensors for Citywide On-Street Parking Availability Prediction. IEEE Transactions on Intelligent Transportation Systems, 23(8), 10427–10439. https://doi.org/10.1109/TITS.2021.3067675",
        "[P13] Huang, Y.-H., & Hsieh, C.-H. (2022). A Decision Support System for Available Parking Slots on the Roadsides in Urban Areas. Expert Systems with Applications, 207, Article 117668. https://doi.org/10.1016/j.eswa.2022.117668",
        "[P14] Zeng, C., Ma, C., Wang, K., & Cui, Z. (2022). Parking Occupancy Prediction Method Based on Multi Factors and Stacked GRU-LSTM. IEEE Access, 10, 48316–48327. https://doi.org/10.1109/ACCESS.2022.3171330",
        "[P15] Li, B. (2022). Stochastic Modeling and Adaptive Forecasting for Parking Space Availability With Drivers' Time-Varying Arrival/Departure Behavior. Transportation Research Part B: Methodological, 166, 128–149. https://doi.org/10.1016/j.trb.2022.10.014",
        "[P16] Li, Z., Xu, H., Gao, X., Wang, Z., & Xu, W. (2022). Fusion Attention Mechanism Bidirectional LSTM for Short-Term Traffic Flow Prediction. Journal of Intelligent Transportation Systems, 26(4), 481–496. https://doi.org/10.1080/15472450.2022.2142049",
        "[P17] Zhang, C., Cui, L., Yu, S., & Yu, J. J. Q. (2022). A Communication-Efficient Federated Learning Scheme for IoT-Based Traffic Forecasting. IEEE Internet of Things Journal, 9(14), 11918–11931. https://doi.org/10.1109/JIOT.2021.3132363",
        "[P18] Paidi, V. (2022). Short-term prediction of parking availability in an open parking lot using LSTM. Journal of Intelligent Systems, 31(1), 819–829. https://doi.org/10.1515/jisys-2022-0039",
        "[P19] Xia, M., Jin, D., & Chen, J. (2023). Short-Term Traffic Flow Prediction Based on Graph Convolutional Networks and Federated Learning. IEEE Transactions on Intelligent Transportation Systems, 24(1), 1108–1118. https://doi.org/10.1109/TITS.2022.3179391",
        "[P20] Xiao, X., Peng, Z., Lin, Y., Jin, Z., Shao, W., Chen, R., Cheng, N., & Mao, G. (2023). Parking Prediction in Smart Cities: A Survey. IEEE Transactions on Intelligent Transportation Systems, 24(10), 10329–10351. https://doi.org/10.1109/TITS.2023.3279024",
        "[P21] Kaur, R., Roul, R. K., & Batra, S. (2023). A Hybrid Deep Learning CNN-ELM Approach for Parking Space Detection in Smart Cities. Neural Computing and Applications, 35(12), 8945–8960. https://doi.org/10.1007/s00521-023-08426-y",
        "[P22] Pandya, S., Srivastava, G., Jhaveri, R., Babu, M. R., Bhattacharya, S., Maddikunta, P. K. R., Mastorakis, S., Piran, M. J., & Gadekallu, T. R. (2023). Federated Learning for Smart Cities: A Comprehensive Survey. Sustainable Energy Technologies and Assessments, 55, Article 102987. https://doi.org/10.1016/j.seta.2022.102987",
        "[P23] Zhang, F., Shang, K., Yan, L., Nan, H., & Miao, Z. (2024). Prediction of Parking Space Availability Using Improved MAT-LSTM Network. ISPRS International Journal of Geo-Information, 13(5), Article 151. https://doi.org/10.3390/ijgi13050151",
        "[P24] Kemik, H., Dalyan, T., & Aydogan, M. (2024). Smart Solutions for Mega-Cities: Utilizing Long Short-Term Memory and Multi-Head Attention in Parking Prediction. ISPRS International Journal of Geo-Information, 13(12), Article 449. https://doi.org/10.3390/ijgi13120449",
        "[P25] Sharma, M., & Kaur, P. (2024). Fog-Based Federated Time Series Forecasting for IoT Data. Journal of Network and Systems Management, 32(2), Article 26. https://doi.org/10.1007/s10922-024-09802-2",
        "[P26] Chen, Y., & Zhang, W. (2024). Intelligent Transportation Systems: Machine Learning Approaches for Urban Mobility in Smart Cities. Sustainable Cities and Society, 108, Article 105369. https://doi.org/10.1016/j.scs.2024.105369",
        "[P27] Attiah, A., Alahmadi, S., Hakeem, A., & Mohaisen, L. (2025). FedPark: A Federated Learning Crowdsensing Solution for On-Street Parking Availability. IEEE Access, 13, 35774–35789. https://doi.org/10.1109/ACCESS.2025.3577489",
        "[P28] Cao, R., Chen, H., & Wang, D. Z. W. (2025). An Attention-Based Dynamic Graph Model for On-Street Parking Availability Prediction. Transportation Research Part A: Policy and Practice, 192, Article 104391. https://doi.org/10.1016/j.tra.2025.104391",
        "[P29] Rocco di Torrepadula, F., Fisichella, M., Di Martino, S., & Mazzocca, N. (2025). Fedflow: A Personalized Federated Learning Framework for Passenger Flow Prediction. Machine Learning, 114, Article 166. https://doi.org/10.1007/s10994-025-06795-0",
        "[P30] Alterkawi, L., & Dib, F. K. (2025). Federated Learning for Smart Cities: A Thematic Review of Challenges and Approaches. Future Internet, 17(12), Article 545. https://doi.org/10.3390/fi17120545"
    ]
    for b_item in bib_30:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(b_item)
        r.font.size = Pt(8.8)

    output_file = 'Review_1_Report.docx'
    doc.save(output_file)
    print(f"SUCCESS: Fully regenerated {output_file} as a clean, publication-grade faculty report with {len(doc_map_items)} sections!")

if __name__ == '__main__':
    build_faculty_report()
