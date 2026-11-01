# -*- coding: utf-8 -*-
"""
Agent 3B: Görsel Metafor & İkon Yönetmeni (Visual Metaphor & Icon Director)
Görevi:
  1. Sahnedeki soyut kavramları minimalist sembollere eşler:
     - Zenginlik -> Kasa / Altın
     - Kısıtlama -> Kafes / Pranga
     - Hicret -> Harita üzerinde hareket eden ışıklı rota
     - Hakikat / İlim -> Açık Kitap / İlahi Meşale
  2. Gerekli ikonları SVG kütüphanesinden seçer veya saf, ölçeklenebilir <svg> kodu üretir.
  3. Remotion motoru için spring ve path-drawing animasyon parametrelerini hazırlar.
"""
import re
import json
from typing import Optional, Callable, List
from .base_agent import BaseAgent
from .state import (
    ProjectState, PipelinePhase, SvgIconDefinition, MetaphorMapping, VectorDirectorData
)


# Standard Built-in Minimalist Geometric SVG Library (ViewBox 0 0 100 100)
SVG_METAPHOR_CATALOG = {
    "wealth_chest": SvgIconDefinition(
        icon_id="wealth_chest",
        name="Altın Sandık & Zenginlik",
        view_box="0 0 100 100",
        stroke_color="#f59e0b",
        svg_body=(
            '<rect x="20" y="40" width="60" height="40" rx="6" stroke="#f59e0b" stroke-width="3" fill="none"/>'
            '<path d="M20 52 H80" stroke="#f59e0b" stroke-width="2.5"/>'
            '<circle cx="50" cy="52" r="5" fill="#f59e0b"/>'
            '<path d="M30 40 V28 C30 22 70 22 70 28 V40" stroke="#f59e0b" stroke-width="3" fill="none"/>'
        )
    ),
    "cage_restraint": SvgIconDefinition(
        icon_id="cage_restraint",
        name="Kafes & Kısıtlama",
        view_box="0 0 100 100",
        stroke_color="#ef4444",
        svg_body=(
            '<rect x="22" y="25" width="56" height="55" rx="8" stroke="#ef4444" stroke-width="3" fill="none"/>'
            '<line x1="36" y1="25" x2="36" y2="80" stroke="#ef4444" stroke-width="2.5"/>'
            '<line x1="50" y1="25" x2="50" y2="80" stroke="#ef4444" stroke-width="2.5"/>'
            '<line x1="64" y1="25" x2="64" y2="80" stroke="#ef4444" stroke-width="2.5"/>'
            '<circle cx="50" cy="18" r="4" stroke="#ef4444" stroke-width="2" fill="none"/>'
        )
    ),
    "migration_route": SvgIconDefinition(
        icon_id="migration_route",
        name="Hicret & Işıklı Rota",
        view_box="0 0 100 100",
        stroke_color="#06b6d4",
        svg_body=(
            '<circle cx="25" cy="75" r="6" fill="#06b6d4"/>'
            '<path d="M25 75 Q40 30 75 25" stroke="#06b6d4" stroke-width="3" stroke-dasharray="4 4" fill="none"/>'
            '<polygon points="75,20 85,25 75,30" fill="#06b6d4"/>'
            '<circle cx="75" cy="25" r="3" fill="#f59e0b"/>'
        )
    ),
    "knowledge_book": SvgIconDefinition(
        icon_id="knowledge_book",
        name="Kadim İlim & Kitap",
        view_box="0 0 100 100",
        stroke_color="#10b981",
        svg_body=(
            '<path d="M50 30 C40 22 20 25 15 28 V75 C20 72 40 70 50 78 C60 70 80 72 85 75 V28 C80 25 60 22 50 30 Z" '
            'stroke="#10b981" stroke-width="3" fill="none"/>'
            '<line x1="50" y1="30" x2="50" y2="78" stroke="#10b981" stroke-width="3"/>'
        )
    ),
    "balance_scale": SvgIconDefinition(
        icon_id="balance_scale",
        name="Adalet & Denge Terazisi",
        view_box="0 0 100 100",
        stroke_color="#eab308",
        svg_body=(
            '<line x1="50" y1="20" x2="50" y2="80" stroke="#eab308" stroke-width="3"/>'
            '<line x1="25" y1="35" x2="75" y2="35" stroke="#eab308" stroke-width="3"/>'
            '<path d="M25 35 L15 55 H35 Z" stroke="#eab308" stroke-width="2.5" fill="none"/>'
            '<path d="M75 35 L65 55 H85 Z" stroke="#eab308" stroke-width="2.5" fill="none"/>'
            '<rect x="40" y="80" width="20" height="6" rx="2" fill="#eab308"/>'
        )
    ),
    "heart_sacrifice": SvgIconDefinition(
        icon_id="heart_sacrifice",
        name="Fedakarlık & Adanmışlık",
        view_box="0 0 100 100",
        stroke_color="#ec4899",
        svg_body=(
            '<path d="M50 82 L20 50 C10 40 10 24 25 18 C35 14 45 20 50 28 C55 20 65 14 75 18 C90 24 90 40 80 50 Z" '
            'stroke="#ec4899" stroke-width="3" fill="none"/>'
            '<line x1="50" y1="35" x2="50" y2="65" stroke="#ec4899" stroke-width="2"/>'
        )
    )
}


class VectorMetaphorDirectorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id=3,
            name="Vektörel Metafor & İkon Yönetmeni (Ajan 3B)",
            required_phase=PipelinePhase.PHASE_2_BRANCH_SELECTED,
            target_phase=PipelinePhase.PHASE_3B_METAPHORS_COMPOSED
        )

    def can_execute(self, state: ProjectState):
        if state.selected_track != "vector_infographic":
            return False, f"Seçilen dal '{state.selected_track}'. Ajan 3B yalnızca 'vector_infographic' dalında çalışabilir."
        return super().can_execute(state)

    def _process(
        self,
        state: ProjectState,
        on_progress: Optional[Callable[[int, str, dict], None]] = None
    ) -> ProjectState:
        if on_progress:
            on_progress(self.agent_id, "running", {
                "message": "Soyut kavramlar minimalist SVG sembollerine ve dinamik animasyonlara eşleniyor..."
            })

        scenes = state.storyboard.scenes
        mappings: List[MetaphorMapping] = []

        for idx, sc in enumerate(scenes):
            txt = (sc.spoken_text or sc.concept).lower()
            
            # Map semantic concepts to symbolic metaphor icons
            if any(k in txt for k in ["zengin", "para", "mal", "mülk", "altın", "kasa", "dünya", "servet"]):
                icon = SVG_METAPHOR_CATALOG["wealth_chest"]
                anim = "spring_pop"
                concept = "Maddi Zenginlik & Dünyalık"
                symbol = "Altın Sandık"
                explanation = "Kişinin ardında bıraktığı fani dünyalık ve zenginlik sembolize edilir."
            elif any(k in txt for k in ["kısıtla", "hapis", "baskı", "engel", "kafes", "pranga", "zorluk"]):
                icon = SVG_METAPHOR_CATALOG["cage_restraint"]
                anim = "scale_fade"
                concept = "Baskı & Kısıtlama"
                symbol = "Kafes"
                explanation = "İnanç yolunda karşılaşılan hapsedilme ve aile baskısı vurgulanır."
            elif any(k in txt for k in ["hicret", "yol", "sefer", "medine", "mekke", "göç", "rota", "harita"]):
                icon = SVG_METAPHOR_CATALOG["migration_route"]
                anim = "path_draw"
                concept = "Hicret & Manevi Yolculuk"
                symbol = "Işıklı Rota"
                explanation = "Harita üzerinde karanlıktan nura doğru uzanan kesikli ışık rotası çizilir."
            elif any(k in txt for k in ["ilim", "kitap", "oku", "ayet", "hadis", "hikmet", "hakikat", "alim"]):
                icon = SVG_METAPHOR_CATALOG["knowledge_book"]
                anim = "spring_pop"
                concept = "İlim & Hakikat"
                symbol = "Açık Mushaf / Kitap"
                explanation = "Zihni aydınlatan ilahi hakikat ve bilgi pınarı sembolize edilir."
            elif any(k in txt for k in ["adalet", "hüküm", "denge", "hak", "terazi", "ölçü"]):
                icon = SVG_METAPHOR_CATALOG["balance_scale"]
                anim = "counter_spin"
                concept = "Adalet & Hakikat Terazisi"
                symbol = "Denge Terazisi"
                explanation = "Her nefsin kendi vazifesini adaletle tarttığı ilahi nizam temsil edilir."
            else:
                icon = SVG_METAPHOR_CATALOG["heart_sacrifice"]
                anim = "spring_pop"
                concept = "Adanmışlık & Dava şuuru"
                symbol = "Sadakat Kalbi"
                explanation = "Hak yoluna adanmış kalbin sarsılmaz samimiyeti yansıtılır."

            mappings.append(
                MetaphorMapping(
                    scene_id=sc.scene_id,
                    concept=concept,
                    symbol_name=symbol,
                    metaphor_explanation=explanation,
                    icon=icon,
                    animation_type=anim,
                    spring_damping=12.0,
                    spring_stiffness=120.0
                )
            )

        state.vector_direction = VectorDirectorData(
            metaphors=mappings,
            primary_color="#070a13",
            accent_gold="#f59e0b",
            accent_cyan="#06b6d4",
            bg_style="dark_isometric_grid"
        )

        return state

    def _validate_contract(self, state: ProjectState) -> None:
        if not state.vector_direction or not state.vector_direction.metaphors:
            raise ValueError("VectorMetaphorDirectorAgent kontrat hatası: metaphors listesi boş!")
