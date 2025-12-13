"""Weekly digest PDF generator."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from reportlab.lib.pagesizes import letter  # type: ignore
    from reportlab.pdfgen import canvas  # type: ignore
except ImportError:  # pragma: no cover
    letter = None  # type: ignore
    canvas = None  # type: ignore


class DigestBuilder:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.export_dir = base_dir / "digests"
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def build(self, summary: dict[str, Any], filename: str | None = None) -> Path:
        filename = filename or f"weekly_digest_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        if canvas and letter:
            output_path = self.export_dir / f"{filename}.pdf"
            self._build_pdf(summary, output_path)
        else:
            output_path = self.export_dir / f"{filename}.txt"
            self._build_text(summary, output_path)
        return output_path

    def _build_pdf(self, summary: dict[str, Any], output_path: Path) -> None:
        pdf = canvas.Canvas(str(output_path), pagesize=letter)
        width, height = letter
        y = height - 72
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(72, y, "EQ12 Commander++ Weekly Digest")
        y -= 36
        pdf.setFont("Helvetica", 11)
        pdf.drawString(72, y, f"Generated: {datetime.utcnow().isoformat()}Z")
        y -= 24

        def draw_line(text_line: str, offset: int = 14) -> None:
            nonlocal y
            if y < 72:
                pdf.showPage()
                pdf.setFont("Helvetica", 11)
                y = height - 72
            pdf.drawString(72, y, text_line)
            y -= offset

        for section, content in summary.items():
            draw_line(f"[{section.upper()}]", 18)
            if isinstance(content, dict):
                for key, value in content.items():
                    draw_line(f"- {key}: {value}")
            elif isinstance(content, list):
                for item in content:
                    draw_line(f"- {item}")
            else:
                draw_line(str(content))
            y -= 10

        pdf.save()

    def _build_text(self, summary: dict[str, Any], output_path: Path) -> None:
        lines = [
            "EQ12 Commander++ Weekly Digest",
            f"Generated: {datetime.utcnow().isoformat()}Z",
            "",
        ]
        for section, content in summary.items():
            lines.append(f"[{section.upper()}]")
            if isinstance(content, dict):
                for key, value in content.items():
                    lines.append(f"- {key}: {value}")
            elif isinstance(content, list):
                for item in content:
                    lines.append(f"- {item}")
            else:
                lines.append(str(content))
            lines.append("")
        output_path.write_text("\n".join(lines), encoding="utf-8")


def build_digest_builder(config: dict, base_dir: Path) -> DigestBuilder:
    return DigestBuilder(base_dir)
