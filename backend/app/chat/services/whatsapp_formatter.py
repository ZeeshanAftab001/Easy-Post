# app/chat/services/whatsapp_formatter.py
#
# WhatsApp Cloud API formatting rules:
#   *bold*          → bold
#   _italic_        → italic
#   ~strikethrough~ → strikethrough
#   ```code```      → monospace
#   > quote         → block quote
#   - item          → unordered list
#   1. item         → ordered list
#   *heading*\n     → bold heading (WA has no real headings)
#
# NOTE: WhatsApp does NOT render standard Markdown (# ## ** etc.)
# This module converts AI output into WA-safe formatted strings.

from __future__ import annotations
import re


# ─────────────────────────────────────────────
# Core converter  (Markdown → WhatsApp syntax)
# ─────────────────────────────────────────────

def md_to_wa(text: str) -> str:
    """
    Convert a standard Markdown string produced by the LLM
    into WhatsApp-compatible formatting.
    """
    lines   = text.split("\n")
    output  = []

    for line in lines:
        # ── Headings  (#, ##, ###)  → *bold* line ──────────────
        line = re.sub(r"^#{1,3}\s+(.+)$", r"*\1*", line)

        # ── Bold  **text** or __text__  → *text* ───────────────
        line = re.sub(r"\*\*(.+?)\*\*", r"*\1*", line)
        line = re.sub(r"__(.+?)__",     r"*\1*", line)

        # ── Italic  *text* or _text_  → _text_ ─────────────────
        # careful: only single * that aren't already WA bold
        line = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"_\1_", line)
        line = re.sub(r"(?<!_)_(?!_)(.+?)(?<!_)_(?!_)",       r"_\1_", line)

        # ── Strikethrough  ~~text~~  → ~text~ ──────────────────
        line = re.sub(r"~~(.+?)~~", r"~\1~", line)

        # ── Inline code  `code`  → ```code``` ──────────────────
        line = re.sub(r"`([^`]+)`", r"```\1```", line)

        # ── Unordered lists  -/*/+ item  → • item ──────────────
        line = re.sub(r"^\s*[-*+]\s+", "• ", line)

        # ── Ordered lists  1. item  → 1. item (already fine) ───
        # WhatsApp renders numbered lists natively — no change needed.

        # ── Blockquotes  > text  → > text (already fine) ───────
        # WhatsApp supports > for quotes natively.

        output.append(line)

    return "\n".join(output)


# ─────────────────────────────────────────────
# Pre-built message templates
# ─────────────────────────────────────────────

def approval_request(summary: str, steps: list[str]) -> str:
    """
    Formatted HITL approval prompt.

    Example output:
        ⏸ *Action Required*

        Here's what I'm about to do:
        📋 Post a funny cricket caption on Instagram

        *Steps:*
        1. post_instagram — Generate caption
        2. add_hashtags   — Add 5 hashtags

        Reply *approve* ✅ or *cancel* ❌
    """
    steps_text = "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps))
    return (
        f"⏸ *Action Required*\n\n"
        f"Here's what I'm about to do:\n"
        f"📋 {summary}\n\n"
        f"*Steps:*\n{steps_text}\n\n"
        f"Reply *approve* ✅ or *cancel* ❌"
    )


def success_message(action: str, detail: str = "") -> str:
    """
    ✅ *Posted successfully!*
    Instagram caption is live.
    """
    body = f"\n{detail}" if detail else ""
    return f"✅ *{action}*{body}"


def error_message(reason: str) -> str:
    """
    ❌ *Something went wrong*
    Could not connect to Instagram API.
    """
    return f"❌ *Something went wrong*\n{reason}"


def cancelled_message() -> str:
    return "🚫 *Action cancelled.* What else can I help with?"


def analytics_card(
    followers: int,
    engagement: str,
    best_time: str,
    top_post: str = "",
) -> str:
    """
    📊 *Account Analytics*

    👥 Followers:   12,000
    💬 Engagement:  5.4%
    ⏰ Best time:   9 PM
    🏆 Top post:    Cricket match reel
    """
    lines = [
        "📊 *Account Analytics*\n",
        f"👥 *Followers:*   {followers:,}",
        f"💬 *Engagement:*  {engagement}",
        f"⏰ *Best time:*   {best_time}",
    ]
    if top_post:
        lines.append(f"🏆 *Top post:*    {top_post}")
    return "\n".join(lines)


def scheduled_confirmation(cron_human: str, preview: str) -> str:
    """
    ⏰ *Scheduled!*
    Posts daily at 9 PM.

    _Preview:_
    "Your caption here..."
    """
    return (
        f"⏰ *Scheduled!*\n"
        f"Posts {cron_human}.\n\n"
        f"_Preview:_\n\"{preview}\""
    )


def caption_preview(platform: str, caption: str, hashtags: list[str]) -> str:
    """
    📝 *Caption Preview — Instagram*

    Your funny cricket caption here with emojis 🏏

    #cricket #Pakistan #funny #viral

    Reply *approve* ✅ to post, *edit* ✏️ to change, or *cancel* ❌
    """
    tag_line = " ".join(f"#{t.lstrip('#')}" for t in hashtags)
    return (
        f"📝 *Caption Preview — {platform.capitalize()}*\n\n"
        f"{caption}\n\n"
        f"{tag_line}\n\n"
        f"Reply *approve* ✅ to post, *edit* ✏️ to change, or *cancel* ❌"
    )


def typing_indicator() -> str:
    """Lightweight 'thinking' message to send before a slow response."""
    return "⏳ _Working on it…_"
