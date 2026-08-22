# -*- coding: utf-8 -*-
"""Har bir postning oxiriga qo'shiladigan imzo."""

INSTAGRAM = "https://www.instagram.com/expert_sofia.mulladjanova"

IMZO = (
    "\n\n<b>Sofia Mulladjanova</b> — kosmetolog"
    '\n📸 <a href="{}">Instagram sahifam</a>'
).format(INSTAGRAM)


def qosh(matn):
    """Matn oxiriga imzo qo'shadi (agar allaqachon bo'lmasa)."""
    if "expert_sofia.mulladjanova" in matn:
        return matn
    return matn.rstrip() + IMZO
