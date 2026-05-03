"""
MAIN CPC CLASSIFICATION PIPELINE
Adapted from MCP_cpc_classes for standalone LangGraph agent use.
"""

import logging
import os
import re
import math
import json
from typing import Dict, Any, Set, List, Tuple
from collections import Counter

from .ollama_client import OllamaClient
from .extracting_cpc import CPCExtractor
from .cpc_xml_parser import CPCXMLParser
from .prompts import label_claims, rerank_prompt

logger = logging.getLogger(__name__)


def _resolve_xml_dir() -> str:
    """Resolve the CPC XML directory relative to MCP_cpc_classes project."""
    # This agent is in: patent_application_anlayse_langgraph/agents/agent5_cpc_classify/
    # XML files are in: MCP_cpc_classes/patent_cpc_fastapi/app/cpc_classification/resources/cpc_scheme_2026/
    # Relative path from this file:
    here = os.path.dirname(os.path.abspath(__file__))
    # Go up 3 levels (agents -> patent_application_anlayse_langgraph -> AI-projects) then into MCP_cpc_classes
    xml_dir = os.path.join(
        here,
        "..",
        "..",
        "..",
        "MCP_cpc_classes",
        "patent_cpc_fastapi",
        "app",
        "cpc_classification",
        "resources",
        "cpc_scheme_2026",
    )
    xml_dir = os.path.normpath(xml_dir)

    # Fallback: if not found, check environment variable
    if not os.path.exists(xml_dir):
        env_dir = os.environ.get("CPC_XML_DIR")
        if env_dir and os.path.exists(env_dir):
            xml_dir = env_dir

    return xml_dir


def _normalize_word(word: str) -> str:
    """Normalize a word for matching: lowercase, strip punctuation, basic stemming."""
    word = word.lower().strip(".,;:!?()[]{}()")
    if word.endswith("ing") and len(word) > 5:
        word = word[:-3]
    elif word.endswith("ed") and len(word) > 4:
        word = word[:-2]
    elif word.endswith("s") and len(word) > 3:
        word = word[:-1]
    elif word.endswith("es") and len(word) > 4:
        word = word[:-2]
    return word


def _tokenize(text: str) -> Set[str]:
    """Tokenize text into normalized words."""
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return {_normalize_word(w) for w in words if len(w) > 2}


CPC_SYNONYMS = {
    "venting": ["deaeration", "degassing", "air removal", "bleeding", "vent"],
    "bleeding": ["deaeration", "degassing", "venting", "air removal"],
    "self-bleeding": ["deaeration", "self-venting", "auto-bleeding", "auto-venting"],
    "air venting": ["deaeration", "degassing", "air removal"],
    "deaeration": ["venting", "degassing", "air removal", "bleeding"],
    "degassing": ["deaeration", "venting", "air removal"],
    "air removal": ["deaeration", "venting", "degassing"],
    "cooling": [
        "temperature control",
        "heat removal",
        "thermal management",
        "coolant",
        "radiator",
    ],
    "coolant": ["cooling", "heat transfer fluid", "thermal medium"],
    "heat removal": ["cooling", "thermal management"],
    "thermal management": ["cooling", "heat removal", "temperature control"],
    "radiator": ["heat exchanger", "cooling device"],
    "sealing": ["gasketing", "packing", "jointing", "seal"],
    "seal": ["sealing", "gasket", "packing"],
    "valve": ["tap", "cock", "vent", "shut-off"],
    "venting valve": ["bleed valve", "air valve", "deaeration valve"],
    "bleed": ["vent", "deaerate", "air release"],
    "battery": ["accumulator", "cell", "electrochemical storage"],
    "electric vehicle": ["ev", "battery vehicle", "electromobile"],
    "wellhead": [
        "well head",
        "blowout preventer",
        "christmas tree",
        "wellhead assembly",
    ],
    "tubing hanger": ["tubing support", "casing hanger", "production hanger"],
    "drilling": ["boring", "earth drilling", "well drilling"],
    "oil well": ["petroleum well", "hydrocarbon well", "production well"],
    "gas well": ["natural gas well", "petroleum well"],
    "annulus": ["annular space", "annular void", "borehole annulus"],
    "casing": ["well casing", "borehole lining"],
    "downhole": ["subsurface", "down hole", "borehole"],
    "explosive": ["charge", "detonation", "blast", "explosion"],
    "explosive charge": ["shaped charge", "detonating charge", "blast charge"],
    "shaped charge": ["explosive charge", "lined cavity charge", "hollow charge"],
    "cutter": ["cutting tool", "perforator", "radial cutter", "pipe cutter"],
    "cutting": ["severing", "destroying", "perforating", "fracturing"],
    "partial radial cutter": ["explosive cutter", "pipe cutter", "tubing cutter"],
    "well completion": ["completion", "wellbore completion", "tubing completion"],
    "idling": ["abandoning", "plugging", "shutting in", "well idling"],
    "accessory conduit": ["conduit", "tubing", "line", "cable"],
    "liquid": ["fluid", "coolant"],
    "fluid": ["liquid", "coolant"],
    "device": ["apparatus", "equipment", "unit"],
    "apparatus": ["device", "equipment", "unit"],
}


def _get_synonyms(word: str) -> List[str]:
    """Get CPC synonyms for a word."""
    return CPC_SYNONYMS.get(word.lower(), [])


def _get_expanded_terms(term: str) -> Set[str]:
    """Get all variants of a term including synonyms."""
    terms = {term.lower()}
    words = term.lower().split()

    for word in words:
        syns = _get_synonyms(word)
        for syn in syns:
            for w in words:
                variant = term.lower().replace(w, syn)
                terms.add(variant)
        terms.update(syns)

    return terms


def _is_system_first(system_context: str, core_function: str) -> bool:
    """Determine if this invention is application-specific equipment (system-first)."""
    system_context = system_context.lower()
    core_function = core_function.lower()

    strong_system_signals = [
        "wellhead",
        "tubing hanger",
        "blowout preventer",
        "christmas tree",
        "drilling rig",
        "drill bit",
        "drill string",
        "casing",
        "downhole tool",
        "explosive cutter",
        "shaped charge",
        "partial radial cutter",
        "engine",
        "motor",
        "turbine",
        "pump",
        "battery pack",
        "battery module",
        "battery cell",
        "reactor",
        "distillation column",
        "heat exchanger unit",
        "transmission",
        "gearbox",
        "drivetrain",
    ]

    for signal in strong_system_signals:
        if signal in system_context:
            return True

    if any(
        word in system_context
        for word in ["oil", "gas", "petroleum", "hydrocarbon", "well"]
    ):
        if any(
            word in system_context
            for word in ["drilling", "production", "extraction", "completion"]
        ):
            return True

    return False


def _parse_llm_json(response) -> dict:
    """Parse JSON from LLM response with multiple fallback strategies."""
    if not response:
        return {}

    try:
        return json.loads(response)
    except Exception:
        pass

    cleaned = re.sub(r"^```(?:json)?\s*", "", response.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except Exception:
        pass

    match = re.search(r"\{.*\}", response, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass

    return {}


class CPCClassifier:
    """MAIN CPC CLASSIFICATION PIPELINE"""

    def __init__(self, model_name: str = "gpt-oss:120b-cloud"):
        self.llm = OllamaClient(model_name=model_name)
        self.extractor = CPCExtractor(self.llm)
        xml_dir = _resolve_xml_dir()
        if os.path.exists(xml_dir):
            self.xml_parser = CPCXMLParser(xml_dir)
            logger.info("CPC XML parser initialized with: %s", xml_dir)
        else:
            self.xml_parser = None
            logger.warning(
                "CPC XML directory not found at: %s. Phase 2 will be skipped.", xml_dir
            )

    def classify(self, text: str, claims: str = "") -> Dict[str, Any]:
        # PHASE 1: LLM extraction
        description = text
        labeled_claims = ""
        if claims:
            labeled_claims = label_claims(claims)
        elif "CLAIMS:" in text or "claims:" in text.lower():
            parts = re.split(r"CLAIMS:|claims:", text, flags=re.IGNORECASE, maxsplit=1)
            if len(parts) == 2:
                description = parts[0].strip()
                claims_text = parts[1].strip()
                labeled_claims = label_claims(claims_text)

        phase1 = self.extractor.extract(description, labeled_claims)

        cpc_classes = phase1.get("cpc_classes", [])
        terms = phase1.get("essential_terms", phase1.get("terms", []))

        system_context = phase1.get("system_context", "").lower()
        core_function = phase1.get("core_function", "").lower()
        strategy = phase1.get("classification_strategy", "").lower()

        is_system_first_flag = "system-first" in strategy or _is_system_first(
            system_context, core_function
        )

        negative_signals = [s.lower() for s in phase1.get("negative_signals", [])]
        negative_domains = [d.lower() for d in phase1.get("negative_domains", [])]
        logger.info("Negative signals from Phase 1: %s", negative_signals)
        logger.info("Negative domains from Phase 1: %s", negative_domains)

        # POST-PROCESSING: Smart class injection
        primary_injections = []
        secondary_injections = []

        if is_system_first_flag:
            if any(
                word in system_context
                for word in [
                    "wellhead",
                    "tubing hanger",
                    "drilling",
                    "oil well",
                    "gas well",
                    "hydrocarbon",
                    "petroleum",
                    "borehole",
                    "downhole",
                    "annulus",
                ]
            ):
                if "E21B" not in cpc_classes:
                    primary_injections.append("E21B")
                    logger.info(
                        "Post-processing: Injecting E21B as PRIMARY for wellhead/drilling system"
                    )

            if any(
                word in system_context
                for word in [
                    "completion",
                    "workover",
                    "abandonment",
                    "idling",
                    "plugging",
                    "well idling",
                    "well completion",
                ]
            ) or any(
                word in core_function
                for word in ["complete", "workover", "abandon", "idle", "plug"]
            ):
                if "E21B43" not in cpc_classes and "E21B" not in cpc_classes:
                    primary_injections.append("E21B43")
                    logger.info(
                        "Post-processing: Injecting E21B43 for well completion/abandonment"
                    )

            if any(
                word in core_function
                for word in [
                    "explosive",
                    "charge",
                    "detonate",
                    "blast",
                    "cut",
                    "cutter",
                    "sever",
                    "destroy",
                    "perforate",
                ]
            ) or any(
                word in system_context
                for word in [
                    "explosive",
                    "shaped charge",
                    "detonation",
                    "cutter",
                    "cutting",
                ]
            ):
                if "E21B29" not in cpc_classes and "E21B" not in cpc_classes:
                    primary_injections.append("E21B29")
                    logger.info(
                        "Post-processing: Injecting E21B29 for explosive cutting/perforation"
                    )

            if any(
                word in system_context
                for word in ["vehicle", "automotive", "car", "truck", "aircraft"]
            ):
                if "B60" not in cpc_classes and not any(
                    c.startswith("B60") for c in cpc_classes
                ):
                    primary_injections.append("B60")
                    logger.info(
                        "Post-processing: Injecting B60 as PRIMARY for vehicle system"
                    )

        if any(
            word in core_function
            for word in [
                "cool",
                "cooling",
                "heat removal",
                "thermal management",
                "temperature control",
                "radiator",
                "coolant",
            ]
        ):
            if "F01P" not in cpc_classes:
                if is_system_first_flag:
                    secondary_injections.append("F01P")
                else:
                    primary_injections.append("F01P")
                logger.info("Post-processing: Injecting F01P for cooling function")

        if any(
            word in core_function
            for word in ["seal", "sealing", "prevent leakage", "gasket", "packing"]
        ):
            if "F16J" not in cpc_classes:
                if is_system_first_flag and "E21B" in (
                    primary_injections + cpc_classes
                ):
                    secondary_injections.append("F16J")
                    logger.info(
                        "Post-processing: Injecting F16J as SECONDARY for sealing in wellhead system"
                    )
                else:
                    primary_injections.append("F16J")
                    logger.info("Post-processing: Injecting F16J for sealing function")

        if any(
            word in core_function
            for word in ["valve", "vent", "venting", "bleed", "tap", "cock"]
        ):
            if "F16K" not in cpc_classes:
                if is_system_first_flag and "E21B" in (
                    primary_injections + cpc_classes
                ):
                    secondary_injections.append("F16K")
                    logger.info(
                        "Post-processing: Injecting F16K as SECONDARY for valve in wellhead system"
                    )
                else:
                    primary_injections.append("F16K")
                    logger.info(
                        "Post-processing: Injecting F16K for valve/venting function"
                    )

        if any(
            word in system_context
            for word in [
                "electrical",
                "battery",
                "batteries",
                "electric vehicle",
                "electric motor",
                "ev ",
                "powertrain",
            ]
        ):
            if "B60L" not in cpc_classes:
                if is_system_first_flag:
                    primary_injections.append("B60L")
                else:
                    secondary_injections.append("B60L")
                logger.info(
                    "Post-processing: Injecting B60L for electrical system context"
                )

        if primary_injections:
            cpc_classes = primary_injections + [
                c for c in cpc_classes if c not in primary_injections
            ]
        if secondary_injections:
            cpc_classes = cpc_classes + [
                c for c in secondary_injections if c not in cpc_classes
            ]

        logger.info("Post-processing: Final class list: %s", cpc_classes)

        if "F25" in cpc_classes and "F01P" in cpc_classes:
            cpc_classes = [c for c in cpc_classes if c != "F25"]
            logger.info(
                "Post-processing: Removed F25 in favor of F01P for machine cooling"
            )

        logger.info("Phase 1: System context: %s", system_context)
        logger.info("Phase 1: Core function: %s", core_function)
        logger.info(
            "Phase 1: Strategy: %s",
            "system-first" if is_system_first_flag else "function-first",
        )

        term_importance = {}
        for t in terms:
            if isinstance(t, dict):
                term = t.get("term", "").lower()
                importance = t.get("importance", 5)
                if term and len(term) > 3:
                    term_importance[term] = importance
            else:
                term = str(t).lower()
                if term and len(term) > 3:
                    term_importance[term] = 5

        # PHASE 2: XML expansion + improved scoring with negative signals
        logger.info("Phase 2: Expanding classes %s", cpc_classes)

        candidates = []
        xml_available = self.xml_parser is not None

        if xml_available:
            try:
                all_subgroups = self.xml_parser.expand_classes(
                    cpc_classes, include_non_allocatable=False
                )
                logger.info("Phase 2: Found %d total subgroups", len(all_subgroups))

                if all_subgroups:
                    title_count = len(all_subgroups)
                    doc_freq = Counter()
                    all_tokens = []

                    for sg in all_subgroups:
                        context = sg.get("full_context", sg.get("title", "")).lower()
                        tokens = _tokenize(context)
                        all_tokens.append(tokens)
                        for token in tokens:
                            doc_freq[token] += 1

                    scored = []
                    for idx, sg in enumerate(all_subgroups):
                        symbol = sg.get("symbol", "")
                        title = sg.get("title", "").lower()
                        context = sg.get("full_context", title).lower()
                        context_tokens = all_tokens[idx]
                        score = 0.0

                        # NEGATIVE SIGNAL PENALTY
                        negative_match = False
                        for neg in negative_signals:
                            if neg in context or neg in title:
                                score -= 5.0
                                negative_match = True

                        for neg_domain in negative_domains:
                            if neg_domain in context or neg_domain in title:
                                score -= 3.0
                                negative_match = True

                        # DOMAIN-SPECIFIC FILTERING: B60L
                        if symbol.startswith("B60L"):
                            is_electrical_patent = any(
                                w in system_context or w in core_function
                                for w in [
                                    "electrical",
                                    "electric",
                                    "battery",
                                    "vehicle",
                                    "automotive",
                                    "powertrain",
                                    "ev ",
                                    "charging",
                                ]
                            )
                            if not is_electrical_patent:
                                continue
                            cooling_related = any(
                                w in context
                                for w in [
                                    "cool",
                                    "heat",
                                    "thermal",
                                    "temperature",
                                    "battery",
                                    "propulsion",
                                ]
                            )
                            if not cooling_related:
                                continue

                        # F16J in wellhead context
                        if (
                            symbol.startswith("F16J")
                            and is_system_first_flag
                            and "E21B" in cpc_classes
                        ):
                            wellhead_seal_related = any(
                                w in context
                                for w in [
                                    "metal",
                                    "dynamic",
                                    "packing",
                                    "gasket",
                                    "seal ring",
                                    "casing",
                                    "tubing",
                                    "wellhead",
                                    "annulus",
                                ]
                            )
                            if not wellhead_seal_related:
                                pass

                        # TERM MATCHING
                        for term, importance in term_importance.items():
                            term_score = 0.0
                            term_tokens = _tokenize(term)
                            if not term_tokens:
                                continue

                            overlap = term_tokens & context_tokens
                            if overlap:
                                overlap_idf = sum(
                                    math.log(title_count / max(doc_freq.get(t, 1), 1))
                                    for t in overlap
                                )
                                term_score += overlap_idf * (importance / 5.0) * 3

                            if term in context:
                                avg_df = sum(
                                    doc_freq.get(t, 1) for t in term_tokens
                                ) / len(term_tokens)
                                idf = math.log(title_count / max(avg_df, 1))
                                importance_weight = importance / 5.0
                                term_score += idf * importance_weight * 5

                            synonyms = _get_expanded_terms(term)
                            for syn in synonyms:
                                if syn != term and syn in context:
                                    syn_tokens = _tokenize(syn)
                                    avg_df = sum(
                                        doc_freq.get(t, 1) for t in syn_tokens
                                    ) / max(len(syn_tokens), 1)
                                    idf = math.log(title_count / max(avg_df, 1))
                                    importance_weight = importance / 5.0
                                    term_score += idf * importance_weight * 4

                            score += term_score

                        # SYSTEM CONTEXT BOOST
                        sys_tokens = _tokenize(system_context)
                        sys_overlap = sys_tokens & context_tokens
                        for token in sys_overlap:
                            idf = math.log(title_count / max(doc_freq.get(token, 1), 1))
                            score += idf * 2

                        # CORE FUNCTION BOOST
                        func_tokens = _tokenize(core_function)
                        func_overlap = func_tokens & context_tokens
                        for token in func_overlap:
                            idf = math.log(title_count / max(doc_freq.get(token, 1), 1))
                            score += idf * 4

                        # CLASS-SPECIFIC BOOSTS
                        if symbol.startswith("E21B"):
                            if any(
                                w in context
                                for w in [
                                    "wellhead",
                                    "tubing hanger",
                                    "casing",
                                    "annulus",
                                    "blowout",
                                    "christmas tree",
                                    "drilling",
                                ]
                            ):
                                score *= 2.0
                            elif any(
                                w in context for w in ["well", "borehole", "downhole"]
                            ):
                                score *= 1.5
                            elif any(
                                w in context for w in ["valve", "seal", "packing"]
                            ):
                                score *= 1.3

                        if symbol.startswith("E21B29"):
                            has_explosive = any(
                                w in context
                                for w in [
                                    "explosive",
                                    "explosives",
                                    "charge",
                                    "detonat",
                                    "blast",
                                    "shaped",
                                ]
                            )
                            has_cutter = any(
                                w in context
                                for w in ["cutter", "cutting", "sever", "destroy"]
                            )
                            has_perforat = "perforat" in context
                            if has_explosive and has_cutter:
                                score *= 3.0
                            elif has_explosive:
                                score *= 2.5
                            elif has_cutter:
                                score *= 2.0
                            elif has_perforat:
                                score *= 1.8
                            elif any(
                                w in context
                                for w in ["pipe", "tubing", "casing", "cable"]
                            ):
                                score *= 1.5
                            if "/02" in symbol and has_explosive:
                                score *= 1.3

                        if symbol.startswith("E21B43"):
                            if any(
                                w in context
                                for w in [
                                    "completion",
                                    "workover",
                                    "abandon",
                                    "idle",
                                    "plug",
                                    "accessory",
                                    "conduit",
                                ]
                            ):
                                score *= 2.0
                            elif any(
                                w in context
                                for w in ["well", "borehole", "downhole", "tubing"]
                            ):
                                score *= 1.3

                        if symbol.startswith("E21B") and not any(
                            symbol.startswith(prefix)
                            for prefix in ["E21B29", "E21B33", "E21B34", "E21B43"]
                        ):
                            if any(
                                w in core_function
                                for w in ["explosive", "charge", "cut", "cutter"]
                            ):
                                if not any(
                                    w in context
                                    for w in [
                                        "explosive",
                                        "charge",
                                        "cut",
                                        "cutter",
                                        "perforat",
                                    ]
                                ):
                                    continue
                            if any(
                                w in system_context
                                for w in ["completion", "idling", "abandon", "plug"]
                            ):
                                if "multilateral" in context or "lateral" in context:
                                    continue

                        if symbol.startswith("F01P"):
                            if any(
                                w in context
                                for w in [
                                    "vent",
                                    "deaerat",
                                    "degas",
                                    "air",
                                    "filling",
                                    "overflow",
                                ]
                            ):
                                score *= 1.6
                            elif any(
                                w in context
                                for w in [
                                    "cool",
                                    "heat",
                                    "thermal",
                                    "coolant",
                                    "radiator",
                                ]
                            ):
                                score *= 1.3

                        if symbol.startswith("F16K"):
                            if any(
                                w in context
                                for w in ["vent", "air", "bleed", "deaerat", "degas"]
                            ):
                                score *= 1.6
                            elif any(w in context for w in ["valve", "tap", "cock"]):
                                score *= 1.2

                        if symbol.startswith("B60L"):
                            if any(
                                w in context
                                for w in [
                                    "battery",
                                    "thermal",
                                    "cool",
                                    "heat",
                                    "temperature",
                                ]
                            ):
                                score *= 1.4

                        if symbol.startswith("F16J"):
                            if any(
                                w in context
                                for w in ["metal", "dynamic", "mtm", "metal-to-metal"]
                            ):
                                score *= 1.5
                            elif any(
                                w in context for w in ["seal", "packing", "gasket"]
                            ):
                                score *= 1.2

                        # SPECIFICITY BONUS
                        symbol_depth = symbol.count("/") + sum(
                            symbol.count(d) for d in "0123456789"
                        )
                        depth_bonus = min(symbol_depth * 0.5, 3.0)
                        score += depth_bonus

                        if score > 0 and not negative_match:
                            scored.append((score, sg))
                        elif score > 0 and negative_match:
                            scored.append((score, sg))

                    scored.sort(key=lambda x: -x[0])

                    if scored:
                        scores = [s[0] for s in scored]
                        max_score = max(scores)
                        median_score = (
                            sorted(scores)[len(scores) // 2]
                            if len(scores) > 1
                            else max_score
                        )
                        denom = max_score + median_score * 0.5

                        for score, sg in scored[:7]:
                            normalized_score = min(score / denom, 1.0)
                            candidates.append(
                                {
                                    "symbol": sg["symbol"],
                                    "title": sg["title"],
                                    "level": sg["level"],
                                    "score": round(normalized_score, 4),
                                }
                            )

                    logger.info(
                        "Phase 2: Selected %d matching candidates", len(candidates)
                    )
            except Exception as e:
                logger.error("Phase 2 expansion failed: %s", e)
        else:
            logger.warning(
                "Phase 2 skipped: CPC XML files not available. Degrading to Phase 1 + Phase 4."
            )

        # PHASE 3: Ranking
        ranked = sorted(candidates, key=lambda x: x.get("score", 0), reverse=True)[:7]

        # PHASE 4: Post-Ranking LLM Re-ranking
        best_code = None
        re_ranked = []
        try:
            if ranked:
                rerank_prompt_text = rerank_prompt(phase1, ranked)
                rerank_response = self.llm.chat(
                    system_prompt="You are a patent examiner with deep expertise in CPC classification.",
                    user_message=rerank_prompt_text,
                    temperature=0.1,
                    max_tokens=2000,
                )
                rerank_data = _parse_llm_json(rerank_response)
                re_ranked = rerank_data.get("re_ranked", [])
                best_code = rerank_data.get("best_code", {})
                logger.info("Phase 4: Best code: %s", best_code.get("symbol", "N/A"))
        except Exception as e:
            logger.warning("Phase 4 re-ranking failed: %s", e)

        cpc = [
            {"code": node["symbol"], "score": node.get("score", 0.0)} for node in ranked
        ]

        phase2 = {
            "codes": [node["symbol"] for node in ranked],
            "reasoning": (
                "Ranked by improved TF-IDF scoring with word-level matching, parent context, "
                "expanded synonyms, class-specific boosts, and negative signal penalties. "
                "Claims terms weighted 2x. System-first strategy applied where appropriate."
            ),
        }

        result = {
            "phase1": phase1,
            "phase2": phase2,
            "phase3": ranked,
            "cpc": cpc,
        }

        if re_ranked:
            result["phase4"] = {
                "re_ranked": re_ranked,
                "best_code": best_code,
            }

        return result
