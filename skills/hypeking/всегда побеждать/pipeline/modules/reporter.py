#!/usr/bin/env python3
"""
AXIOM REPORT ENGINE — Phase 7 of Web Pwn Pipeline
Generates structured reports of findings, exploits, and breach status.
"""

import os, json, datetime
from typing import Dict, List, Optional


class ReportEngine:
    """Generates comprehensive penetration test reports."""

    BREACH_LEVELS = {
        0: "No Breach — Target secure or not vulnerable",
        1: "Information Disclosure — Low-risk findings only",
        2: "Partial Breach — Medium-risk vulnerabilities confirmed",
        3: "Significant Breach — High-risk exploitation achieved",
        4: "Critical Breach — Remote code execution or equivalent",
        5: "Full PWN — Complete system compromise"
    }

    def __init__(self, target: str, output_dir: str,
                 recon: Dict, vulns: List[Dict],
                 exploits: List[Dict], breach_level: int):
        self.target = target
        self.output_dir = output_dir
        self.recon = recon
        self.vulns = vulns
        self.exploits = exploits
        self.breach_level = breach_level

    def run(self) -> str:
        """Generate all report formats."""
        print("  ┌─ Report Generation")
        html_path = self._html_report()
        json_path = self._json_report()
        summary_path = self._summary_report()
        print(f"  ├─ HTML:  {html_path}")
        print(f"  ├─ JSON:  {json_path}")
        print(f"  ├─ Summary: {summary_path}")
        print(f"  └─ Report complete")
        return html_path

    def _html_report(self) -> str:
        """Generate HTML report."""
        vuln_rows = ""
        for v in self.vulns:
            vuln_rows += f"""
            <tr>
                <td><span class="severity-{v.get('severity', 'low')}">{v.get('severity', 'unknown')}</span></td>
                <td>{v.get('type', 'unknown')}</td>
                <td>{v.get('url', self.target)}</td>
                <td>{v.get('evidence', '')[:100]}</td>
            </tr>"""

        exploit_items = ""
        for e in self.exploits:
            icon = "✅" if e.get("success") else "❌"
            exploit_items += f"<li>{icon} {e.get('type')} (level {e.get('level')})</li>"

        tech_list = ", ".join([t.get("name", "") for t in self.recon.get("technologies", [])]) or "none detected"

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AXIOM Web Pwn Report — {self.target}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', monospace; background: #0a0a0f; color: #e0e0e0; padding: 40px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ border-bottom: 2px solid #00ff88; padding-bottom: 20px; margin-bottom: 30px; }}
        .header h1 {{ color: #00ff88; font-size: 28px; }}
        .header .meta {{ color: #888; margin-top: 10px; }}
        .breach-badge {{ display: inline-block; padding: 8px 20px; border-radius: 4px; font-weight: bold; font-size: 14px; }}
        .breach-0 {{ background: #333; color: #888; }}
        .breach-1 {{ background: #665500; color: #ffd700; }}
        .breach-2 {{ background: #664400; color: #ff8800; }}
        .breach-3 {{ background: #662200; color: #ff4400; }}
        .breach-4 {{ background: #660000; color: #ff0000; }}
        .breach-5 {{ background: #330000; color: #ff0044; }}
        .section {{ margin: 30px 0; }}
        .section h2 {{ color: #00aaff; margin-bottom: 15px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #222; }}
        th {{ background: #111; color: #00aaff; }}
        tr:hover {{ background: #111; }}
        .severity-critical {{ color: #ff0044; }}
        .severity-high {{ color: #ff4400; }}
        .severity-medium {{ color: #ffaa00; }}
        .severity-low {{ color: #88aa00; }}
        .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: #111; padding: 20px; border-radius: 8px; border: 1px solid #222; }}
        .stat-card .num {{ font-size: 36px; font-weight: bold; color: #00ff88; }}
        .stat-card .label {{ color: #888; font-size: 12px; margin-top: 5px; }}
        ul {{ list-style: none; }}
        ul li {{ padding: 5px 0; }}
        .footer {{ margin-top: 50px; padding-top: 20px; border-top: 1px solid #222; color: #555; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⬡ AXIOM WEB PWN REPORT</h1>
            <div class="meta">
                <strong>Target:</strong> {self.target}<br>
                <strong>Date:</strong> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
                <strong>Status:</strong> <span class="breach-badge breach-{self.breach_level}">{self.BREACH_LEVELS.get(self.breach_level, 'Unknown')}</span>
            </div>
        </div>

        <div class="stats">
            <div class="stat-card"><div class="num">{len(self.vulns)}</div><div class="label">Vulnerabilities</div></div>
            <div class="stat-card"><div class="num">{len(self.exploits)}</div><div class="label">Exploits Run</div></div>
            <div class="stat-card"><div class="num">{self.breach_level}</div><div class="label">Breach Level /5</div></div>
            <div class="stat-card"><div class="num">{len(self.recon.get('technologies', []))}</div><div class="label">Technologies</div></div>
        </div>

        <div class="section">
            <h2>🔍 Recon Summary</h2>
            <table>
                <tr><th>Property</th><th>Value</th></tr>
                <tr><td>Status Code</td><td>{self.recon.get('status_code', 'N/A')}</td></tr>
                <tr><td>Server</td><td>{self.recon.get('server', 'unknown')}</td></tr>
                <tr><td>Title</td><td>{self.recon.get('title', 'N/A')}</td></tr>
                <tr><td>Technologies</td><td>{tech_list}</td></tr>
                <tr><td>Forms Found</td><td>{len(self.recon.get('forms', []))}</td></tr>
                <tr><td>Endpoints</td><td>{len(self.recon.get('endpoints', []))}</td></tr>
            </table>
        </div>

        <div class="section">
            <h2>⚠ Vulnerabilities</h2>
            <table>
                <tr><th>Severity</th><th>Type</th><th>URL</th><th>Evidence</th></tr>
                {vuln_rows if vuln_rows else '<tr><td colspan="4">No vulnerabilities detected</td></tr>'}
            </table>
        </div>

        <div class="section">
            <h2>💥 Exploitation Results</h2>
            <ul>{exploit_items if exploit_items else '<li>No exploits executed</li>'}</ul>
        </div>

        <div class="section">
            <h2>📋 Recommendations</h2>
            <ul>
                {self._recommendations()}
            </ul>
        </div>

        <div class="footer">
            Generated by AXIOM Web Pwn Pipeline | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>"""
        path = f"{self.output_dir}/report.html"
        with open(path, "w") as f:
            f.write(html)
        return path

    def _json_report(self) -> str:
        """Generate JSON report."""
        report = {
            "report": {
                "target": self.target,
                "generated": datetime.datetime.now().isoformat(),
                "breach_level": self.breach_level,
                "breach_status": self.BREACH_LEVELS.get(self.breach_level, "Unknown"),
                "tool": "AXIOM Web Pwn Pipeline v2.0"
            },
            "recon": self.recon,
            "vulnerabilities": self.vulns,
            "exploits": self.exploits
        }
        path = f"{self.output_dir}/report.json"
        with open(path, "w") as f:
            json.dump(report, f, indent=2, default=str)
        return path

    def _summary_report(self) -> str:
        """Generate short summary."""
        successful = [e for e in self.exploits if e.get("success")]
        lines = [
            "=" * 50,
            "AXIOM WEB PWN — SUMMARY",
            "=" * 50,
            f"Target:         {self.target}",
            f"Date:           {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Technologies:   {len(self.recon.get('technologies', []))}",
            f"Vulnerabilities: {len(self.vulns)}",
            f"Exploits:       {len(self.exploits)} ({len(successful)} successful)",
            f"Breach Level:   {self.breach_level}/5",
            f"Status:         {self.BREACH_LEVELS.get(self.breach_level, 'Unknown')}",
            "-" * 50,
            "VULNERABILITIES:"
        ]
        if self.vulns:
            for v in self.vulns:
                lines.append(f"  [{v.get('severity', 'info').upper():>8}] {v.get('type', 'unknown')}")
        else:
            lines.append("  (none detected)")

        lines += ["-" * 50, "EXPLOITS:"]
        if self.exploits:
            for e in self.exploits:
                s = "✓" if e.get("success") else "✗"
                lines.append(f"  {s} {e.get('type')} (level {e.get('level')})")
        else:
            lines.append("  (none executed)")

        lines += ["=" * 50]
        path = f"{self.output_dir}/summary.txt"
        with open(path, "w") as f:
            f.write("\n".join(lines))
        return path

    def _recommendations(self) -> str:
        """Generate fix recommendations based on vulns."""
        recs = {
            "sql_injection": "<li>Use parameterized queries / prepared statements</li>",
            "cross_site_scripting": "<li>Implement Content-Security-Policy and output encoding</li>",
            "ssrf": "<li>Whitelist allowed URLs and disable internal network access</li>",
            "lfi": "<li>Validate file paths and use allowlist for includes</li>",
            "ssti": "<li>Sanitize template input and disable sandbox escapes</li>",
            "command_injection": "<li>Never pass user input to system commands</li>",
            "idor": "<li>Implement proper access control checks</li>",
            "open_redirect": "<li>Validate redirect URLs against an allowlist</li>",
            "http_smuggling": "<li>Disable HTTP/1.1 keep-alive or use HTTP/2 exclusively</li>",
            "graphql_introspection": "<li>Disable introspection in production</li>"
        }
        seen = set()
        result = ""
        for v in self.vulns:
            t = v.get("type")
            if t and t not in seen and t in recs:
                result += recs[t]
                seen.add(t)
        if not result:
            result = "<li>No vulnerabilities to remediate</li>"
        return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AXIOM Report Engine")
    parser.add_argument("-t", "--target", required=True)
    parser.add_argument("-o", "--output", default=".")
    args = parser.parse_args()
    engine = ReportEngine(args.target, args.output, {}, [], [], 0)
    engine.run()
