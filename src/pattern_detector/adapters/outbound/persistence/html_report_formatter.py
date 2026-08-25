"""Interactive HTML Observability HUD Formatter for Swift."""

from __future__ import annotations

import html
import json

from pattern_detector.adapters.outbound.persistence.llm_report_formatter import LlmReportFormatter
from pattern_detector.domain.detection import DetectionReport
from pattern_detector.domain.value_objects import ConfidenceLevel, PatternCategory, PatternType
from pattern_detector.ports.outbound import ReportFormatterPort

CATEGORY_COLORS: dict[PatternCategory, dict[str, str]] = {
    PatternCategory.PROTOCOL_ORIENTED: {
        "text": "#38bdf8",
        "bg": "#0c4a6e44",
        "border": "#0284c7",
        "accent": "#0ea5e9",
        "name": "Protocol-Oriented",
    },
    PatternCategory.CONCURRENCY: {
        "text": "#fb7185",
        "bg": "#88133744",
        "border": "#e11d48",
        "accent": "#f43f5e",
        "name": "Concurrency & Actors",
    },
    PatternCategory.DECLARATIVE_DSL: {
        "text": "#c084fc",
        "bg": "#581c8744",
        "border": "#9333ea",
        "accent": "#a855f7",
        "name": "SwiftUI & DSL",
    },
    PatternCategory.CREATIONAL: {
        "text": "#34d399",
        "bg": "#064e3b44",
        "border": "#059669",
        "accent": "#10b981",
        "name": "Creational",
    },
    PatternCategory.STRUCTURAL: {
        "text": "#67e8f9",
        "bg": "#164e6344",
        "border": "#0891b2",
        "accent": "#06b6d4",
        "name": "Structural",
    },
    PatternCategory.BEHAVIORAL: {
        "text": "#fbbf24",
        "bg": "#78350f44",
        "border": "#d97706",
        "accent": "#f59e0b",
        "name": "Behavioral",
    },
    PatternCategory.RESILIENCE: {
        "text": "#f87171",
        "bg": "#7f1d1d44",
        "border": "#dc2626",
        "accent": "#ef4444",
        "name": "Resilience & Safety",
    },
    PatternCategory.PRINCIPLE: {
        "text": "#818cf8",
        "bg": "#312e8144",
        "border": "#4f46e5",
        "accent": "#6366f1",
        "name": "SOLID Principles",
    },
}


class HtmlReportFormatter(ReportFormatterPort):
    """Renders a standalone, responsive, interactive HTML dashboard for DetectionReport with AI Prompt Generator."""

    def format(self, report: DetectionReport, verbose: bool = False) -> str:
        vh_count = sum(1 for d in report.detections if d.level == ConfidenceLevel.VERY_HIGH)
        h_count = sum(1 for d in report.detections if d.level == ConfidenceLevel.HIGH)
        m_count = sum(1 for d in report.detections if d.level == ConfidenceLevel.MEDIUM)
        l_count = sum(1 for d in report.detections if d.level == ConfidenceLevel.LOW)

        llm_formatter = LlmReportFormatter()
        llm_prompt_text = llm_formatter.format_scan_report(report)

        cards_html: list[str] = []
        for idx, det in enumerate(report.detections, 1):
            cat_style = CATEGORY_COLORS.get(
                det.pattern_category,
                {"text": "#94a3b8", "bg": "#1e293b44", "border": "#475569", "accent": "#64748b", "name": "Other"},
            )

            badge_class = {
                ConfidenceLevel.VERY_HIGH: "badge-vh",
                ConfidenceLevel.HIGH: "badge-h",
                ConfidenceLevel.MEDIUM: "badge-m",
                ConfidenceLevel.LOW: "badge-l",
            }.get(det.level, "badge-vh")

            evidences_html: list[str] = []
            for ev in det.evidences:
                pct = int(ev.weight * 100)
                loc_str = f'<span class="location-tag">📍 {html.escape(str(ev.location))}</span>' if ev.location else ""
                evidences_html.append(
                    f'<li class="evidence-item" style="border-left-color: {cat_style["accent"]};">'
                    f'<span class="weight-tag" style="color: {cat_style["text"]};">+{pct}%</span> '
                    f'<span class="rule-code">[{html.escape(ev.rule_code)}]</span> '
                    f'{html.escape(ev.description)} {loc_str}'
                    f"</li>"
                )

            related_html = ""
            if det.related_locations:
                rel_items = "".join(f"<li><code>{html.escape(str(loc))}</code></li>" for loc in det.related_locations)
                related_html = f'<div class="related-locs"><strong>Related Locations:</strong><ul>{rel_items}</ul></div>'

            finding_prompt = (
                f"Refactor and review the following Swift pattern/violation:\n"
                f"- Pattern: {det.pattern_type.value} ({cat_style['name']})\n"
                f"- Target: {det.target_name} ({det.target_kind})\n"
                f"- Location: {det.primary_location}\n"
                f"- Summary: {det.summary}\n\n"
                f"Please provide an idiomatic Swift 5.5 - 6.0+ clean architecture refactoring adhering to POP, Concurrency, and SOLID principles."
            )

            cards_html.append(
                f"""
                <div class="pattern-card" data-pattern="{html.escape(det.pattern_type.value)}" data-category="{html.escape(det.pattern_category.value)}" data-target="{html.escape(det.target_name)}" style="border-left: 4px solid {cat_style["accent"]};">
                    <div class="card-header">
                        <div class="header-left">
                            <span class="card-index">#{idx}</span>
                            <span class="category-badge" style="color: {cat_style["text"]}; background: {cat_style["bg"]}; border: 1px solid {cat_style["border"]};">
                                {html.escape(cat_style["name"].upper())}
                            </span>
                            <span class="pattern-badge" style="color: {cat_style["text"]}; background: {cat_style["bg"]}; border: 1px solid {cat_style["border"]};">
                                {html.escape(det.pattern_type.value.upper())}
                            </span>
                            <span class="target-name">{html.escape(det.target_kind)}: <strong>{html.escape(det.target_name)}</strong></span>
                        </div>
                        <div class="header-right">
                            <span class="confidence-badge {badge_class}">{det.confidence.percentage_str} [{det.level.value}]</span>
                            <button class="btn-copy-card-ai" onclick='copySingleAiPrompt({json.dumps(finding_prompt)})' title="Copy AI Refactoring Prompt">🤖 Copy for AI</button>
                        </div>
                    </div>
                    <div class="card-body">
                        <p class="summary-text"><strong>Summary:</strong> {html.escape(det.summary)}</p>
                        <p class="primary-loc"><strong>Primary Location:</strong> <code>{html.escape(str(det.primary_location))}</code></p>
                        <div class="evidence-section">
                            <strong>Evidence Trail ({len(det.evidences)} heuristics):</strong>
                            <ul class="evidence-list">
                                {"".join(evidences_html)}
                            </ul>
                        </div>
                        {related_html}
                    </div>
                </div>
                """
            )

        category_cards = []
        for cat_enum, style in CATEGORY_COLORS.items():
            count = report.summary_by_category.get(cat_enum.value, 0)
            if count > 0:
                category_cards.append(
                    f"""
                    <button class="cat-filter-btn" data-filter="{cat_enum.value}" style="border-color: {style['border']}; background: {style['bg']}; color: {style['text']};">
                        <span class="cat-dot" style="background: {style['accent']};"></span>
                        <strong>{style['name']}</strong>: {count}
                    </button>
                    """
                )

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pattern Scanner Report - DPX-Swift Architecture HUD - {html.escape(report.project_path or "Codebase")}</title>
    <style>
        :root {{
            --bg: #090d13;
            --card-bg: #121822;
            --border: #232d3d;
            --text: #cbd5e1;
            --heading: #f8fafc;
            --accent: #f97316;
            --green: #22c55e;
            --cyan: #0ea5e9;
            --yellow: #f59e0b;
            --red: #ef4444;
            --swift-orange: #ff5238;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace, sans-serif; }}
        body {{ background: var(--bg); color: var(--text); padding: 30px 20px; line-height: 1.5; }}
        .container {{ max-width: 1280px; margin: 0 auto; }}
        
        header {{ 
            border-bottom: 1px solid var(--border); 
            padding-bottom: 20px; 
            margin-bottom: 25px; 
            display: flex; 
            justify-content: space-between; 
            align-items: flex-start;
            flex-wrap: wrap;
            gap: 15px;
        }}
        h1 {{ color: var(--heading); font-size: 26px; display: flex; align-items: center; gap: 10px; }}
        .subtitle {{ color: #94a3b8; font-size: 14px; margin-top: 5px; }}
        
        .header-actions {{ display: flex; gap: 10px; align-items: center; }}
        .btn-ai-context {{
            background: linear-gradient(135deg, #f97316 0%, #ef4444 100%);
            color: #ffffff;
            border: none;
            padding: 10px 18px;
            border-radius: 8px;
            font-weight: 700;
            font-size: 13.5px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            box-shadow: 0 4px 14px rgba(249, 115, 22, 0.35);
            transition: transform 0.15s, box-shadow 0.15s;
        }}
        .btn-ai-context:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(249, 115, 22, 0.5);
        }}
        .btn-view-prompt {{
            background: var(--card-bg);
            color: var(--heading);
            border: 1px solid var(--border);
            padding: 10px 14px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.15s;
        }}
        .btn-view-prompt:hover {{
            border-color: var(--swift-orange);
            color: var(--swift-orange);
        }}

        .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 25px; }}
        .kpi-card {{ background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 18px; }}
        .kpi-title {{ font-size: 12px; text-transform: uppercase; color: #94a3b8; font-weight: 600; letter-spacing: 0.5px; }}
        .kpi-value {{ font-size: 28px; font-weight: 700; color: var(--heading); margin-top: 5px; }}

        .category-filters {{ display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px; align-items: center; }}
        .cat-filter-btn {{ padding: 8px 14px; border-radius: 20px; border: 1px solid var(--border); background: var(--card-bg); color: var(--heading); font-size: 13px; cursor: pointer; display: flex; align-items: center; gap: 8px; transition: transform 0.1s, opacity 0.2s; }}
        .cat-filter-btn:hover {{ transform: translateY(-1px); opacity: 0.9; }}
        .cat-dot {{ width: 8px; height: 8px; border-radius: 50%; display: inline-block; }}
        .btn-all {{ background: #1e293b; color: #f8fafc; border-color: #475569; }}

        .search-bar {{ width: 100%; padding: 14px 18px; background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; color: var(--heading); font-size: 14px; margin-bottom: 25px; outline: none; transition: border-color 0.2s; }}
        .search-bar:focus {{ border-color: var(--swift-orange); }}

        .pattern-card {{ background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; margin-bottom: 15px; overflow: hidden; transition: border-color 0.2s, box-shadow 0.2s; }}
        .pattern-card:hover {{ border-color: #f9731688; box-shadow: 0 4px 20px rgba(0,0,0,0.3); }}
        .card-header {{ background: #17202e; padding: 12px 18px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; border-bottom: 1px solid var(--border); }}
        .header-left {{ display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }}
        .header-right {{ display: flex; align-items: center; gap: 10px; }}
        .card-index {{ color: #64748b; font-weight: 700; font-size: 13px; }}
        
        .category-badge {{ padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 11px; letter-spacing: 0.5px; }}
        .pattern-badge {{ padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 12px; }}
        .target-name {{ color: var(--heading); font-size: 14px; }}
        
        .confidence-badge {{ font-size: 12px; font-weight: 700; padding: 4px 10px; border-radius: 20px; }}
        .badge-vh {{ background: #14532d55; color: #4ade80; border: 1px solid #22c55e; }}
        .badge-h {{ background: #0c4a6e55; color: #38bdf8; border: 1px solid #0284c7; }}
        .badge-m {{ background: #78350f55; color: #fbbf24; border: 1px solid #d97706; }}
        .badge-l {{ background: #7f1d1d55; color: #f87171; border: 1px solid #dc2626; }}

        .btn-copy-card-ai {{
            background: rgba(249, 115, 22, 0.15);
            color: #fb923c;
            border: 1px solid rgba(249, 115, 22, 0.35);
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 11.5px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s;
        }}
        .btn-copy-card-ai:hover {{
            background: rgba(249, 115, 22, 0.3);
            color: #ffffff;
            border-color: #f97316;
        }}

        .card-body {{ padding: 16px 18px; font-size: 13px; }}
        .summary-text {{ margin-bottom: 10px; color: #e2e8f0; font-size: 14px; }}
        .primary-loc {{ margin-bottom: 12px; color: #94a3b8; }}
        code {{ background: #0b0f17; padding: 3px 6px; border-radius: 4px; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; color: #fdba74; border: 1px solid #1e293b; }}

        .evidence-section {{ margin-top: 14px; }}
        .evidence-list {{ list-style: none; margin-top: 8px; }}
        .evidence-item {{ margin-bottom: 7px; padding-left: 12px; border-left: 3px solid; }}
        .weight-tag {{ font-weight: 700; font-family: monospace; font-size: 13px; }}
        .rule-code {{ color: #94a3b8; font-size: 11px; font-family: monospace; }}
        .location-tag {{ color: #fdba74; font-size: 11px; margin-left: 6px; }}
        .related-locs {{ margin-top: 12px; color: #94a3b8; }}
        .related-locs ul {{ margin-left: 20px; margin-top: 4px; }}

        /* Toast notification */
        .toast {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: #10b981;
            color: #ffffff;
            padding: 14px 22px;
            border-radius: 8px;
            font-weight: 700;
            font-size: 14px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            display: flex;
            align-items: center;
            gap: 10px;
            opacity: 0;
            transform: translateY(20px);
            transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
            pointer-events: none;
            z-index: 9999;
        }}
        .toast.show {{
            opacity: 1;
            transform: translateY(0);
        }}

        /* Modal Preview */
        .modal-overlay {{
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.75);
            backdrop-filter: blur(4px);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 9998;
            padding: 20px;
        }}
        .modal-box {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            width: 100%;
            max-width: 900px;
            max-height: 85vh;
            display: flex;
            flex-direction: column;
            box-shadow: 0 20px 50px rgba(0,0,0,0.6);
        }}
        .modal-header {{
            padding: 18px 22px;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .modal-title {{ color: var(--heading); font-size: 18px; font-weight: 700; }}
        .modal-close {{ background: none; border: none; color: #94a3b8; font-size: 24px; cursor: pointer; }}
        .modal-body {{ padding: 20px 22px; overflow-y: auto; flex: 1; }}
        .prompt-textarea {{
            width: 100%;
            height: 400px;
            background: #090d13;
            color: #fdba74;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 16px;
            font-family: ui-monospace, monospace;
            font-size: 12.5px;
            line-height: 1.4;
            resize: vertical;
            outline: none;
        }}
        .modal-footer {{
            padding: 16px 22px;
            border-top: 1px solid var(--border);
            display: flex;
            justify-content: flex-end;
            gap: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>🍏 DPX-Swift Architecture & Concurrency Observability HUD</h1>
                <div class="subtitle">Protocol-Oriented Programming, Actor Concurrency & SwiftUI Engine • Target: <code>{html.escape(report.project_path or "Target Repository")}</code></div>
            </div>
            <div class="header-actions">
                <button class="btn-view-prompt" onclick="openPromptModal()">👁️ View AI Context</button>
                <button class="btn-ai-context" onclick="copyFullAiContext()">🤖 Copy AI Context Prompt</button>
            </div>
        </header>

        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">Total Detections</div>
                <div class="kpi-value">{report.total_detections_count}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">High Confidence (≥70%)</div>
                <div class="kpi-value" style="color: #4ade80;">{vh_count + h_count}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Med / Low (<70%)</div>
                <div class="kpi-value" style="color: #fbbf24;">{m_count + l_count}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Files Scanned</div>
                <div class="kpi-value">{report.scanned_files_count}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Scan Duration</div>
                <div class="kpi-value">{report.elapsed_seconds:.3f}s</div>
            </div>
        </div>

        <div class="category-filters">
            <button class="cat-filter-btn btn-all" data-filter="all"><strong>All Categories</strong>: {report.total_detections_count}</button>
            {"".join(category_cards)}
        </div>

        <input type="text" id="searchInput" class="search-bar" placeholder="🔎 Instant search by pattern name, category, target type, or rule (e.g. actor, mainactor, propertywrapper, retaincycle)...">

        <div id="cardsContainer">
            {"".join(cards_html)}
        </div>
    </div>

    <!-- Toast Notification -->
    <div id="toast" class="toast">
        <span>✅</span>
        <span id="toastMsg">AI Context Prompt Copied to Clipboard!</span>
    </div>

    <!-- AI Prompt Preview Modal -->
    <div id="promptModal" class="modal-overlay" onclick="closeModalOnOverlay(event)">
        <div class="modal-box">
            <div class="modal-header">
                <div class="modal-title">🤖 AI Architect Context Prompt (Swift)</div>
                <button class="modal-close" onclick="closePromptModal()">&times;</button>
            </div>
            <div class="modal-body">
                <p style="font-size: 13px; color: #94a3b8; margin-bottom: 12px;">Structured XML/Markdown context for LLMs (Claude, GPT-4, Gemini) including POP extensions, actor concurrency, and memory safety analysis.</p>
                <textarea id="modalPromptArea" class="prompt-textarea" readonly>{html.escape(llm_prompt_text)}</textarea>
            </div>
            <div class="modal-footer">
                <button class="btn-view-prompt" onclick="closePromptModal()">Close</button>
                <button class="btn-ai-context" onclick="copyModalPrompt()">📋 Copy Prompt</button>
            </div>
        </div>
    </div>

    <script>
        const FULL_LLM_PROMPT = {json.dumps(llm_prompt_text)};

        function showToast(message) {{
            const toast = document.getElementById('toast');
            const msgSpan = document.getElementById('toastMsg');
            msgSpan.textContent = message;
            toast.classList.add('show');
            setTimeout(() => {{
                toast.classList.remove('show');
            }}, 2500);
        }}

        function copyFullAiContext() {{
            navigator.clipboard.writeText(FULL_LLM_PROMPT).then(() => {{
                showToast("✅ Full AI Context Prompt copied to clipboard!");
            }}).catch(err => {{
                console.error("Failed to copy", err);
            }});
        }}

        function copySingleAiPrompt(promptText) {{
            navigator.clipboard.writeText(promptText).then(() => {{
                showToast("✅ Finding refactoring prompt copied for AI!");
            }}).catch(err => {{
                console.error("Failed to copy", err);
            }});
        }}

        function openPromptModal() {{
            document.getElementById('promptModal').style.display = 'flex';
        }}

        function closePromptModal() {{
            document.getElementById('promptModal').style.display = 'none';
        }}

        function closeModalOnOverlay(e) {{
            if (e.target.id === 'promptModal') {{
                closePromptModal();
            }}
        }}

        function copyModalPrompt() {{
            const textarea = document.getElementById('modalPromptArea');
            navigator.clipboard.writeText(textarea.value).then(() => {{
                showToast("✅ Prompt copied to clipboard!");
                closePromptModal();
            }});
        }}

        const searchInput = document.getElementById('searchInput');
        const cards = document.querySelectorAll('.pattern-card');
        const filterBtns = document.querySelectorAll('.cat-filter-btn');
        let selectedCategory = 'all';

        function filterCards() {{
            const query = searchInput.value.toLowerCase();
            cards.forEach(card => {{
                const text = card.textContent.toLowerCase();
                const pattern = card.dataset.pattern || '';
                const category = card.dataset.category || '';
                const target = card.dataset.target || '';

                const matchesCategory = (selectedCategory === 'all' || category === selectedCategory);
                const matchesSearch = (text.includes(query) || pattern.includes(query) || category.includes(query) || target.includes(query));

                if (matchesCategory && matchesSearch) {{
                    card.style.display = 'block';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }}

        searchInput.addEventListener('input', filterCards);

        filterBtns.forEach(btn => {{
            btn.addEventListener('click', () => {{
                selectedCategory = btn.dataset.filter;
                filterBtns.forEach(b => b.style.outline = 'none');
                btn.style.outline = '2px solid #f97316';
                filterCards();
            }});
        }});
    </script>
</body>
</html>
"""
