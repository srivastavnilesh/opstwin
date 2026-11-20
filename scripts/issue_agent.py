"""Answer a GitHub Issue question with the guarded agent; write a Markdown reply."""
from __future__ import annotations

import os
from pathlib import Path

from src.agent.ask import ask

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    question = (os.getenv("QUESTION") or "").strip()
    if not question:
        raise SystemExit("Empty issue body")

    result = ask(question)
    if result["status"] == "ok":
        rows = "\n".join("| " + " | ".join(str(c) for c in r) + " |" for r in result["rows"][:10])
        header = "| " + " | ".join(f"col{i+1}" for i in range(len(result["rows"][0]))) + " |" if result["rows"] else ""
        sep = "|" + "---|" * (len(result["rows"][0]) if result["rows"] else 1)
        table = f"{header}\n{sep}\n{rows}" if rows else "_no rows returned_"
        body = (
            f"**Question:** {question}\n\n"
            f"**SQL executed (read-only, guardrailed):**\n```sql\n{result['sql']}\n```\n\n"
            f"**Result:**\n\n{table}\n\n"
            f"**Plain-English answer:** {result['narrative']}\n\n"
            "---\n*Answered autonomously by the OpsTwin agent via GitHub Actions. "
            "Only SELECT/WITH queries against allowlisted marts, on a read-only connection.*"
        )
    else:
        body = (
            f"**Question:** {question}\n\n"
            f"**Refused.** Reason: {result['reason']}\n\n"
            "---\n*The OpsTwin agent only executes read-only, allowlisted SELECT queries. "
            "This refusal is the guardrail working as designed.*"
        )

    out = ROOT / "outputs" / "agent_answer.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(body)
    print(body)


if __name__ == "__main__":
    main()