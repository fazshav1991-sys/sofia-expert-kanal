# -*- coding: utf-8 -*-
"""Har bir postning oxiriga qo'shiladigan imzo."""

INSTAGRAM = "https://www.instagram.com/expert_sofia.mulladjanova"

IMZO = (
    "\n\n<b>Sofia Mulladjanova</b> — Integrative Aesthetic Medicine"
    '\n📸 <a href="{}">Instagram sahifam</a>'
).format(INSTAGRAM)


def qosh(matn, kredit=None):
    """
    Matn oxiriga imzoni qo'shadi.
    Rasm krediti bo'lsa, u imzodan KEYIN, eng oxirida turadi.
    """
    if "expert_sofia.mulladjanova" not in matn:
        matn = matn.rstrip() + IMZO
    if kredit and kredit not in matn:
        matn = matn.rstrip() + "\n" + kredit
    return matn
