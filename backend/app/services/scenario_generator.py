"""
Scenario Generator Orchestrator

Registry and orchestration layer for scenario-based population generation.
Lists available scenarios, instantiates them, and manages the generation pipeline
while maintaining compatibility with existing OASIS output formats.
"""

import os
import json
from typing import Dict, Any, List, Optional, Callable

from ..config import Config
from ..utils.logger import get_logger
from .oasis_profile_generator import OasisProfileGenerator, OasisAgentProfile
from .scenarios.base import (
    SCENARIO_REGISTRY,
    get_scenario,
    list_scenarios,
    SimulationScenario,
)

# Import scenarios to trigger registration
from .scenarios.maxstream_worldcup import MaxstreamWorldCupScenario
from .scenarios.capcut_bundle import CapCutBundleScenario

logger = get_logger('mirofish.scenario_generator')


class ScenarioGenerator:
    """
    Orchestrates scenario-based synthetic population generation.

    Provides:
    - List available scenarios
    - Generate profiles for a given scenario
    - Save output in OASIS-compatible format (Reddit JSON / Twitter CSV)
    """

    def __init__(self):
        self._profile_saver = OasisProfileGenerator.__new__(OasisProfileGenerator)
        self._profile_saver._normalize_gender = OasisProfileGenerator._normalize_gender

    @staticmethod
    def list_available_scenarios() -> List[Dict[str, str]]:
        """List all registered scenarios with name and description."""
        return list_scenarios()

    @staticmethod
    def get_scenario_info(scenario_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed info about a scenario including its archetypes."""
        scenario = get_scenario(scenario_name)
        if not scenario:
            return None

        archetypes = scenario.get_archetypes()
        demographics = scenario.get_demographic_distribution()

        return {
            "name": scenario.name,
            "description": scenario.description,
            "archetypes": [
                {
                    "key": a.key,
                    "label": a.label,
                    "description": a.description,
                    "percentage": a.percentage,
                    "age_range": list(a.age_range),
                    "interested_topics": a.interested_topics,
                }
                for a in archetypes
            ],
            "demographics": {
                "country": demographics.country,
                "regions": demographics.regions,
                "age_range": list(demographics.age_range),
                "extra": demographics.extra,
            },
        }

    def generate(
        self,
        scenario_name: str,
        total_agents: int = 100,
        use_llm: bool = True,
        parallel_count: int = 5,
        output_dir: Optional[str] = None,
        output_platform: str = "reddit",
        progress_callback: Optional[Callable] = None,
        custom_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate profiles for a scenario and save to files.

        Args:
            scenario_name: registered scenario name
            total_agents: number of agents to generate
            use_llm: whether to use LLM for persona generation
            parallel_count: parallel LLM call count
            output_dir: directory to save output files
            output_platform: "reddit" (JSON) or "twitter" (CSV)
            progress_callback: callback(current, total, message)
            custom_params: scenario-specific overrides

        Returns:
            Dict with generation results and file paths
        """
        scenario = get_scenario(scenario_name)
        if not scenario:
            available = [s["name"] for s in list_scenarios()]
            raise ValueError(
                f"Scenario '{scenario_name}' not found. "
                f"Available scenarios: {available}"
            )

        # Determine output directory
        if not output_dir:
            output_dir = os.path.join(
                Config.OASIS_SIMULATION_DATA_DIR,
                f"scenario_{scenario_name}"
            )
        os.makedirs(output_dir, exist_ok=True)

        # Determine realtime output path
        if output_platform == "twitter":
            realtime_path = os.path.join(output_dir, "twitter_profiles.csv")
        else:
            realtime_path = os.path.join(output_dir, "reddit_profiles.json")

        logger.info(
            f"Starting scenario generation: {scenario_name}, "
            f"agents={total_agents}, llm={use_llm}, platform={output_platform}"
        )

        # Generate profiles
        profiles = scenario.generate_profiles(
            total_agents=total_agents,
            use_llm=use_llm,
            parallel_count=parallel_count,
            progress_callback=progress_callback,
            realtime_output_path=realtime_path,
            output_platform=output_platform,
            custom_params=custom_params,
        )

        # Final save using OasisProfileGenerator's format methods
        output_path = realtime_path
        self._save_profiles(profiles, output_path, output_platform)

        # Save scenario metadata
        metadata = {
            "scenario_name": scenario_name,
            "scenario_description": scenario.description,
            "total_agents": total_agents,
            "use_llm": use_llm,
            "output_platform": output_platform,
            "output_file": os.path.basename(output_path),
            "archetypes_distribution": {
                a.key: {
                    "label": a.label,
                    "percentage": a.percentage,
                    "count": sum(
                        1 for p in profiles
                        if p and p.source_entity_type and a.key in p.source_entity_type
                    ),
                }
                for a in scenario.get_archetypes()
            },
            "custom_params": custom_params,
        }

        metadata_path = os.path.join(output_dir, "scenario_metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        logger.info(
            f"Scenario generation complete: {len(profiles)} profiles saved to {output_path}"
        )

        return {
            "success": True,
            "scenario_name": scenario_name,
            "total_generated": len([p for p in profiles if p]),
            "output_path": output_path,
            "metadata_path": metadata_path,
            "output_dir": output_dir,
            "profiles": profiles,
        }

    def _save_profiles(
        self,
        profiles: List[OasisAgentProfile],
        file_path: str,
        platform: str
    ):
        """Save profiles using OasisProfileGenerator's format methods."""
        if platform == "twitter":
            self._save_twitter_csv(profiles, file_path)
        else:
            self._save_reddit_json(profiles, file_path)

    def _save_reddit_json(self, profiles: List[OasisAgentProfile], file_path: str):
        """Save as Reddit JSON format compatible with OASIS."""
        data = []
        for idx, profile in enumerate(profiles):
            if not profile:
                continue
            item = {
                "user_id": profile.user_id if profile.user_id is not None else idx,
                "username": profile.user_name,
                "name": profile.name,
                "bio": profile.bio[:150] if profile.bio else profile.name,
                "persona": profile.persona or "",
                "karma": profile.karma or 1000,
                "created_at": profile.created_at,
                "age": profile.age or 30,
                "gender": self._normalize_gender(profile.gender),
                "mbti": profile.mbti or "ISTJ",
                "country": profile.country or "Indonesia",
            }
            if profile.profession:
                item["profession"] = profile.profession
            if profile.interested_topics:
                item["interested_topics"] = profile.interested_topics
            data.append(item)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _save_twitter_csv(self, profiles: List[OasisAgentProfile], file_path: str):
        """Save as Twitter CSV format compatible with OASIS."""
        import csv

        if not file_path.endswith('.csv'):
            file_path = file_path.replace('.json', '.csv')

        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['user_id', 'name', 'username', 'user_char', 'description'])

            for idx, profile in enumerate(profiles):
                if not profile:
                    continue
                user_char = profile.bio
                if profile.persona and profile.persona != profile.bio:
                    user_char = f"{profile.bio} {profile.persona}"
                user_char = user_char.replace('\n', ' ').replace('\r', ' ')
                description = profile.bio.replace('\n', ' ').replace('\r', ' ')

                writer.writerow([
                    idx,
                    profile.name,
                    profile.user_name,
                    user_char,
                    description,
                ])

    @staticmethod
    def _normalize_gender(gender: Optional[str]) -> str:
        """Normalize gender to OASIS English format."""
        if not gender:
            return "other"
        gender_lower = gender.lower().strip()
        mapping = {
            "male": "male",
            "female": "female",
            "laki-laki": "male",
            "perempuan": "female",
            "pria": "male",
            "wanita": "female",
            "other": "other",
        }
        return mapping.get(gender_lower, "other")
