"""
Venue and Places tool adapter for VoyageOS.
Provides activity catalogs, operational statuses, pricing, indoor/outdoor tags,
and query filtering for alternative discovery.
"""
from typing import List, Dict, Any, Optional
from app.tools.fallback import execute_with_resilience, ToolCallResult


class PlacesTool:
    """Provides activity discovery and venue operational checks."""

    def __init__(self):
        # High quality database of venues and activities
        # Structured with indoor/outdoor flags, cost, duration, and risk profile
        self._catalog: Dict[str, List[Dict[str, Any]]] = {
            "rishikesh": [
                {
                    "id": "act_rafting_shivpuri",
                    "name": "River Rafting at Shivpuri (16 km)",
                    "category": "adventure",
                    "cost": 1500.0,
                    "duration_hours": 3.5,
                    "location": "Shivpuri, Rishikesh",
                    "is_outdoor": True,
                    "disruption_risk": "HIGH",
                    "weather_dependent": True,
                    "operating_status": "OPEN",
                    "description": "Grade III & IV white water rafting down the Ganges.",
                },
                {
                    "id": "act_bungee_jumping",
                    "name": "Bungee Jumping at Mohan Chatti",
                    "category": "adventure",
                    "cost": 3700.0,
                    "duration_hours": 3.0,
                    "location": "Mohan Chatti",
                    "is_outdoor": True,
                    "disruption_risk": "HIGH",
                    "weather_dependent": True,
                    "operating_status": "OPEN",
                    "description": "83m fixed platform bungee jump with certified safety masters.",
                },
                {
                    "id": "act_indoor_climbing",
                    "name": "Indoor Rock Climbing & Bouldering Zone",
                    "category": "adventure",
                    "cost": 900.0,
                    "duration_hours": 2.5,
                    "location": "Tapovan, Rishikesh",
                    "is_outdoor": False,
                    "disruption_risk": "LOW",
                    "weather_dependent": False,
                    "operating_status": "OPEN",
                    "description": "Indoor artificial wall climbing and technical bouldering center.",
                },
                {
                    "id": "act_indoor_yoga_sound",
                    "name": "Tibetan Singing Bowl Sound Healing & Yin Yoga",
                    "category": "wellness",
                    "cost": 800.0,
                    "duration_hours": 2.0,
                    "location": "Laxman Jhula road",
                    "is_outdoor": False,
                    "disruption_risk": "LOW",
                    "weather_dependent": False,
                    "operating_status": "OPEN",
                    "description": "Acoustic meditation and therapeutic yoga inside a sheltered studio.",
                },
                {
                    "id": "act_cooking_workshop",
                    "name": "Authentic Himalayan Culinary Masterclass",
                    "category": "food",
                    "cost": 1200.0,
                    "duration_hours": 3.0,
                    "location": "Tapovan",
                    "is_outdoor": False,
                    "disruption_risk": "LOW",
                    "weather_dependent": False,
                    "operating_status": "OPEN",
                    "description": "Hands-on indoor workshop preparing traditional Garhwali cuisine.",
                },
                {
                    "id": "act_chotiwala_food",
                    "name": "Traditional Feast at Chotiwala",
                    "category": "food",
                    "cost": 650.0,
                    "duration_hours": 1.5,
                    "location": "Ram Jhula",
                    "is_outdoor": False,
                    "disruption_risk": "LOW",
                    "weather_dependent": False,
                    "operating_status": "OPEN",
                    "description": "Famous riverside restaurant serving authentic North Indian thalis.",
                },
                {
                    "id": "act_beatles_ashram",
                    "name": "Heritage Walk at The Beatles Ashram",
                    "category": "sightseeing",
                    "cost": 600.0,
                    "duration_hours": 2.5,
                    "location": "Swarg Ashram",
                    "is_outdoor": True,
                    "disruption_risk": "MEDIUM",
                    "weather_dependent": True,
                    "operating_status": "OPEN",
                    "description": "Historic Maharishi Mahesh Yogi ashram with graffiti art & mediation huts.",
                },
                {
                    "id": "act_triveni_ghat_aarti",
                    "name": "Ganga Aarti at Triveni Ghat",
                    "category": "culture",
                    "cost": 0.0,
                    "duration_hours": 1.5,
                    "location": "Triveni Ghat",
                    "is_outdoor": True,
                    "disruption_risk": "MEDIUM",
                    "weather_dependent": True,
                    "operating_status": "OPEN",
                    "description": "Dusk devotional ceremony with lamps, chanting, and drums along the river.",
                },
                {
                    "id": "act_neer_garh_waterfall",
                    "name": "Trek to Neer Garh Waterfall",
                    "category": "adventure",
                    "cost": 300.0,
                    "duration_hours": 3.0,
                    "location": "Neer Garh",
                    "is_outdoor": True,
                    "disruption_risk": "HIGH",
                    "weather_dependent": True,
                    "operating_status": "OPEN",
                    "description": "Scenic jungle trail with multiple natural swimming pools.",
                },
                {
                    "id": "act_cafe_hopping",
                    "name": "Artisanal Cafe Hopping in Tapovan",
                    "category": "food",
                    "cost": 950.0,
                    "duration_hours": 2.5,
                    "location": "Upper Tapovan",
                    "is_outdoor": False,
                    "disruption_risk": "LOW",
                    "weather_dependent": False,
                    "operating_status": "OPEN",
                    "description": "Sampling specialty mountain coffee, vegan bakery treats, and river views.",
                },
            ]
        }

    def get_activities_for_destination(
        self, destination: str, force_failure: bool = False
    ) -> ToolCallResult:
        def _primary_api() -> List[Dict[str, Any]]:
            # Real Places API could go here
            dest_key = destination.lower().strip()
            if dest_key in self._catalog:
                return self._catalog[dest_key]
            # Fallback catalog generator for any other destination
            return [
                {
                    "id": f"act_{dest_key}_outdoor_1",
                    "name": f"Highlights Sightseeing in {destination.title()}",
                    "category": "sightseeing",
                    "cost": 800.0,
                    "duration_hours": 3.0,
                    "location": f"Central {destination.title()}",
                    "is_outdoor": True,
                    "disruption_risk": "HIGH",
                    "weather_dependent": True,
                    "operating_status": "OPEN",
                },
                {
                    "id": f"act_{dest_key}_indoor_1",
                    "name": f"Local Heritage Museum & Gallery in {destination.title()}",
                    "category": "culture",
                    "cost": 400.0,
                    "duration_hours": 2.0,
                    "location": f"Old Town, {destination.title()}",
                    "is_outdoor": False,
                    "disruption_risk": "LOW",
                    "weather_dependent": False,
                    "operating_status": "OPEN",
                },
                {
                    "id": f"act_{dest_key}_food_1",
                    "name": f"Culinary Tasting & Market Walk in {destination.title()}",
                    "category": "food",
                    "cost": 750.0,
                    "duration_hours": 2.0,
                    "location": f"Food Street, {destination.title()}",
                    "is_outdoor": False,
                    "disruption_risk": "LOW",
                    "weather_dependent": False,
                    "operating_status": "OPEN",
                },
            ]

        def _fallback_provider() -> List[Dict[str, Any]]:
            return self._catalog.get("rishikesh", [])

        return execute_with_resilience(
            primary_fn=_primary_api,
            fallback_fn=_fallback_provider,
            tool_name="PLACES_TOOL",
            force_failure=force_failure,
        )

    def search_alternatives(
        self,
        destination: str,
        must_be_indoor: bool = False,
        preferred_category: Optional[str] = None,
        max_cost: Optional[float] = None,
        exclude_activity_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Searches and filters alternatives matching hard criteria.
        """
        res = self.get_activities_for_destination(destination)
        candidates = res.data or []
        excluded = set(exclude_activity_ids or [])

        filtered = []
        for c in candidates:
            if c["id"] in excluded:
                continue
            if c.get("operating_status") != "OPEN":
                continue
            if must_be_indoor and c.get("is_outdoor", True):
                continue
            if max_cost is not None and c.get("cost", 0.0) > max_cost:
                continue
            filtered.append(c)

        return filtered


places_tool = PlacesTool()
