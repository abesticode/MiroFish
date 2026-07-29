"""
Base class for scenario-based synthetic population generation.

Scenarios generate agent populations from predefined archetypes and demographic
distributions, without requiring existing Zep knowledge graph entities.
"""

import json
import random
import concurrent.futures
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from threading import Lock

from openai import OpenAI

from ...config import Config
from ...utils.logger import get_logger
from ...utils.locale import get_language_instruction, get_locale, set_locale
from ..oasis_profile_generator import OasisAgentProfile

logger = get_logger('mirofish.scenario')

SCENARIO_REGISTRY: Dict[str, type] = {}


def register_scenario(cls):
    """Decorator to register a scenario class in the global registry."""
    SCENARIO_REGISTRY[cls.name] = cls
    return cls


def get_scenario(name: str) -> Optional['SimulationScenario']:
    """Instantiate a scenario by name."""
    cls = SCENARIO_REGISTRY.get(name)
    if cls:
        return cls()
    return None


def list_scenarios() -> List[Dict[str, str]]:
    """List all registered scenarios."""
    return [
        {"name": cls.name, "description": cls.description}
        for cls in SCENARIO_REGISTRY.values()
    ]


@dataclass
class Archetype:
    """A persona archetype within a scenario."""
    key: str
    label: str
    description: str
    percentage: float  # 0.0 - 1.0
    age_range: tuple = (18, 55)
    gender_distribution: Dict[str, float] = field(default_factory=lambda: {"male": 0.7, "female": 0.3})
    professions: List[str] = field(default_factory=list)
    interested_topics: List[str] = field(default_factory=list)
    mbti_pool: List[str] = field(default_factory=lambda: [
        "INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP",
        "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP"
    ])
    extra_attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DemographicDistribution:
    """Demographic constraints and distributions for a scenario."""
    country: str = "Indonesia"
    regions: Dict[str, float] = field(default_factory=dict)
    age_range: tuple = (16, 60)
    gender_distribution: Dict[str, float] = field(default_factory=lambda: {"male": 0.7, "female": 0.3})
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DemographicSample:
    """A sampled demographic for a single agent."""
    age: int
    gender: str
    region: str
    profession: str
    mbti: str
    archetype_key: str
    extra: Dict[str, Any] = field(default_factory=dict)


class SimulationScenario(ABC):
    """
    Abstract base for scenario-based population generation.

    Subclasses define archetypes, demographics, and LLM prompts.
    The base class handles orchestration: distributing agents across archetypes,
    sampling demographics, calling LLM or rule-based generation, and producing
    OasisAgentProfile output compatible with the existing pipeline.
    """

    name: str = "base"
    description: str = "Base scenario"

    @abstractmethod
    def get_archetypes(self) -> List[Archetype]:
        """Return the list of persona archetypes with distribution percentages."""
        ...

    @abstractmethod
    def get_demographic_distribution(self) -> DemographicDistribution:
        """Return demographic constraints for this scenario."""
        ...

    @abstractmethod
    def build_persona_prompt(self, archetype: Archetype, sample: DemographicSample, index: int) -> str:
        """Build the LLM prompt to generate a detailed persona for one agent."""
        ...

    def get_system_prompt(self) -> str:
        """System prompt for LLM persona generation."""
        lang_instruction = get_language_instruction()
        return (
            "Kamu adalah ahli dalam membuat profil pengguna media sosial Indonesia yang realistis. "
            "Generate persona yang sangat detail dan realistis untuk simulasi perilaku digital. "
            "Output HARUS berupa JSON valid. Semua string value TIDAK BOLEH mengandung newline.\n\n"
            f"{lang_instruction}"
        )

    def build_rule_based_profile(self, archetype: Archetype, sample: DemographicSample, index: int) -> Dict[str, Any]:
        """Fallback rule-based profile generation when LLM is unavailable."""
        return {
            "bio": f"{archetype.label} dari {sample.region}, Indonesia. {archetype.description[:100]}",
            "persona": (
                f"{archetype.label} berusia {sample.age} tahun, {sample.gender}, "
                f"tinggal di {sample.region}. Profesi: {sample.profession}. "
                f"{archetype.description}"
            ),
            "age": sample.age,
            "gender": sample.gender,
            "mbti": sample.mbti,
            "country": "Indonesia",
            "profession": sample.profession,
            "interested_topics": archetype.interested_topics,
        }

    def sample_demographic(self, archetype: Archetype, demographics: DemographicDistribution) -> DemographicSample:
        """Sample a demographic profile for one agent within an archetype."""
        age = random.randint(archetype.age_range[0], archetype.age_range[1])

        gender_roll = random.random()
        cumulative = 0.0
        gender = "male"
        for g, prob in archetype.gender_distribution.items():
            cumulative += prob
            if gender_roll <= cumulative:
                gender = g
                break

        region_roll = random.random()
        cumulative = 0.0
        region = list(demographics.regions.keys())[0] if demographics.regions else "WIB"
        for r, prob in demographics.regions.items():
            cumulative += prob
            if region_roll <= cumulative:
                region = r
                break

        profession = random.choice(archetype.professions) if archetype.professions else "Umum"
        mbti = random.choice(archetype.mbti_pool)

        return DemographicSample(
            age=age,
            gender=gender,
            region=region,
            profession=profession,
            mbti=mbti,
            archetype_key=archetype.key,
            extra=archetype.extra_attributes.copy(),
        )

    def _distribute_agents(self, total: int, archetypes: List[Archetype]) -> List[tuple]:
        """Distribute total agent count across archetypes based on percentages."""
        assignments = []
        remaining = total

        for i, arch in enumerate(archetypes):
            if i == len(archetypes) - 1:
                count = remaining
            else:
                count = round(total * arch.percentage)
                remaining -= count

            for _ in range(count):
                assignments.append(arch)

        random.shuffle(assignments)
        return assignments

    def _generate_username(self, name_hint: str) -> str:
        """Generate a plausible Indonesian username."""
        base = name_hint.lower().replace(" ", "_")
        base = ''.join(c for c in base if c.isalnum() or c == '_')
        suffix = random.randint(100, 9999)
        return f"{base}_{suffix}"

    def _call_llm(
        self,
        client: OpenAI,
        model: str,
        system_prompt: str,
        user_prompt: str,
        attempt: int = 0
    ) -> Optional[Dict[str, Any]]:
        """Call LLM and parse JSON response."""
        try:
            kwargs = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.8 - (attempt * 0.1),
            }
            try:
                kwargs["response_format"] = {"type": "json_object"}
                response = client.chat.completions.create(**kwargs)
            except Exception:
                del kwargs["response_format"]
                response = client.chat.completions.create(**kwargs)

            content = response.choices[0].message.content

            if response.choices[0].finish_reason == 'length':
                content = self._fix_truncated_json(content)

            return json.loads(content)
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"LLM call/parse failed (attempt {attempt+1}): {str(e)[:80]}")
            return None

    def _fix_truncated_json(self, content: str) -> str:
        """Attempt to close truncated JSON."""
        content = content.strip()
        open_braces = content.count('{') - content.count('}')
        open_brackets = content.count('[') - content.count(']')
        if content and content[-1] not in '",}]':
            content += '"'
        content += ']' * open_brackets
        content += '}' * open_braces
        return content

    def generate_profiles(
        self,
        total_agents: int = 100,
        use_llm: bool = True,
        parallel_count: int = 5,
        progress_callback: Optional[Callable] = None,
        realtime_output_path: Optional[str] = None,
        output_platform: str = "reddit",
        custom_params: Optional[Dict[str, Any]] = None,
    ) -> List[OasisAgentProfile]:
        """
        Generate synthetic agent profiles for this scenario.

        Args:
            total_agents: number of agents to generate
            use_llm: whether to use LLM for detailed persona generation
            parallel_count: number of parallel LLM calls
            progress_callback: callback(current, total, message)
            realtime_output_path: path to write profiles incrementally
            output_platform: "reddit" or "twitter"
            custom_params: scenario-specific parameter overrides

        Returns:
            List of OasisAgentProfile
        """
        archetypes = self.get_archetypes()
        demographics = self.get_demographic_distribution()
        assignments = self._distribute_agents(total_agents, archetypes)

        client = None
        model = None
        if use_llm:
            api_key = Config.LLM_API_KEY
            if not api_key:
                logger.warning("LLM_API_KEY not configured, falling back to rule-based generation")
                use_llm = False
            else:
                client = OpenAI(api_key=api_key, base_url=Config.LLM_BASE_URL)
                model = Config.LLM_MODEL_NAME

        system_prompt = self.get_system_prompt()
        profiles = [None] * total_agents
        completed_count = [0]
        lock = Lock()
        current_locale = get_locale()

        def save_realtime():
            if not realtime_output_path:
                return
            with lock:
                existing = [p for p in profiles if p is not None]
                if not existing:
                    return
                try:
                    if output_platform == "reddit":
                        from ..oasis_profile_generator import OasisProfileGenerator
                        gen = OasisProfileGenerator.__new__(OasisProfileGenerator)
                        gen._normalize_gender = OasisProfileGenerator._normalize_gender.__get__(gen)
                        data = []
                        for idx, p in enumerate(existing):
                            data.append({
                                "user_id": p.user_id,
                                "username": p.user_name,
                                "name": p.name,
                                "bio": p.bio[:150] if p.bio else p.name,
                                "persona": p.persona or "",
                                "karma": p.karma or 1000,
                                "created_at": p.created_at,
                                "age": p.age or 30,
                                "gender": gen._normalize_gender(p.gender),
                                "mbti": p.mbti or "ISTJ",
                                "country": p.country or "Indonesia",
                            })
                            if p.profession:
                                data[-1]["profession"] = p.profession
                            if p.interested_topics:
                                data[-1]["interested_topics"] = p.interested_topics
                        with open(realtime_output_path, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                    else:
                        import csv
                        existing_data = []
                        for p in existing:
                            user_char = p.bio
                            if p.persona and p.persona != p.bio:
                                user_char = f"{p.bio} {p.persona}"
                            user_char = user_char.replace('\n', ' ').replace('\r', ' ')
                            existing_data.append({
                                "user_id": p.user_id,
                                "name": p.name,
                                "username": p.user_name,
                                "user_char": user_char,
                                "description": p.bio.replace('\n', ' ').replace('\r', ' '),
                            })
                        if existing_data:
                            fieldnames = list(existing_data[0].keys())
                            with open(realtime_output_path, 'w', encoding='utf-8', newline='') as f:
                                writer = csv.DictWriter(f, fieldnames=fieldnames)
                                writer.writeheader()
                                writer.writerows(existing_data)
                except Exception as e:
                    logger.warning(f"Failed to save profiles realtime: {e}")

        def generate_single(idx: int, archetype: Archetype):
            set_locale(current_locale)
            sample = self.sample_demographic(archetype, demographics)

            profile_data = None
            if use_llm and client:
                prompt = self.build_persona_prompt(archetype, sample, idx)
                for attempt in range(3):
                    result = self._call_llm(client, model, system_prompt, prompt, attempt)
                    if result and result.get("persona"):
                        profile_data = result
                        break
                    import time
                    time.sleep(1 * (attempt + 1))

            if not profile_data:
                profile_data = self.build_rule_based_profile(archetype, sample, idx)

            name = profile_data.get("name", f"User_{idx}")
            username = self._generate_username(name)

            profile = OasisAgentProfile(
                user_id=idx,
                user_name=username,
                name=name,
                bio=profile_data.get("bio", archetype.description[:150]),
                persona=profile_data.get("persona", archetype.description),
                karma=profile_data.get("karma", random.randint(500, 5000)),
                friend_count=profile_data.get("friend_count", random.randint(50, 500)),
                follower_count=profile_data.get("follower_count", random.randint(100, 1000)),
                statuses_count=profile_data.get("statuses_count", random.randint(100, 2000)),
                age=profile_data.get("age", sample.age),
                gender=profile_data.get("gender", sample.gender),
                mbti=profile_data.get("mbti", sample.mbti),
                country=profile_data.get("country", "Indonesia"),
                profession=profile_data.get("profession", sample.profession),
                interested_topics=profile_data.get("interested_topics", archetype.interested_topics),
                source_entity_uuid=None,
                source_entity_type=f"scenario:{self.name}:{archetype.key}",
            )

            return idx, profile

        logger.info(f"Starting scenario generation: {self.name}, {total_agents} agents, parallel={parallel_count}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=parallel_count) as executor:
            futures = {
                executor.submit(generate_single, idx, archetype): idx
                for idx, archetype in enumerate(assignments)
            }

            for future in concurrent.futures.as_completed(futures):
                try:
                    idx, profile = future.result()
                    profiles[idx] = profile

                    with lock:
                        completed_count[0] += 1
                        current = completed_count[0]

                    save_realtime()

                    if progress_callback:
                        progress_callback(
                            current, total_agents,
                            f"Generated {current}/{total_agents}: {profile.name} ({profile.source_entity_type})"
                        )

                except Exception as e:
                    idx = futures[future]
                    logger.error(f"Failed to generate agent {idx}: {e}")
                    with lock:
                        completed_count[0] += 1
                    archetype = assignments[idx]
                    sample = self.sample_demographic(archetype, demographics)
                    profiles[idx] = OasisAgentProfile(
                        user_id=idx,
                        user_name=self._generate_username(f"user_{idx}"),
                        name=f"User {idx}",
                        bio=archetype.description[:150],
                        persona=archetype.description,
                        source_entity_type=f"scenario:{self.name}:{archetype.key}",
                    )
                    save_realtime()

        logger.info(f"Scenario generation complete: {len([p for p in profiles if p])} profiles generated")
        return profiles
