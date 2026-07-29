"""
Scenario-based synthetic population generators for OASIS simulation.

Each scenario defines archetypes, demographic distributions, and decision logic
to generate agent populations from scratch without requiring Zep knowledge graph entities.
"""

from .base import (
    SimulationScenario,
    Archetype,
    DemographicDistribution,
    DemographicSample,
    SCENARIO_REGISTRY,
    get_scenario,
    list_scenarios,
)
from .maxstream_worldcup import MaxstreamWorldCupScenario
from .capcut_bundle import CapCutBundleScenario

__all__ = [
    'SimulationScenario',
    'Archetype',
    'DemographicDistribution',
    'DemographicSample',
    'SCENARIO_REGISTRY',
    'get_scenario',
    'list_scenarios',
    'MaxstreamWorldCupScenario',
    'CapCutBundleScenario',
]
