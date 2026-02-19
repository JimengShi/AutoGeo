"""
Example usage of GEOAGENT
Demonstrates various geospatial workflows
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from geospatial_agents import GeoOrchestratorLangGraph

def example_1_spatial_query():
    """Example: Simple spatial query"""
    print("\n" + "="*70)
    print("Example 1: Find parks near downtown Seattle")
    print("="*70 + "\n")
    
    orchestrator = GeoOrchestratorLangGraph(
        llm_api_key=os.getenv("OPENAI_API_KEY"),
        tavily_api_key=os.getenv("TAVILY_API_KEY")
    )
    
    result = orchestrator.execute(
        "Find all parks within 5 miles of downtown Seattle and create a map"
    )
    
    print_result(result)


def example_2_land_use_analysis():
    """Example: Land use change analysis"""
    print("\n" + "="*70)
    print("Example 2: Land use change analysis")
    print("="*70 + "\n")
    
    orchestrator = GeoOrchestratorLangGraph(
        llm_api_key=os.getenv("OPENAI_API_KEY"),
        tavily_api_key=os.getenv("TAVILY_API_KEY")
    )
    
    result = orchestrator.execute(
        "Analyze land use change in California from 2020 to 2024 using satellite imagery"
    )
    
    print_result(result)


def example_3_flood_risk():
    """Example: Flood risk assessment"""
    print("\n" + "="*70)
    print("Example 3: Flood risk assessment")
    print("="*70 + "\n")
    
    orchestrator = GeoOrchestratorLangGraph(
        llm_api_key=os.getenv("OPENAI_API_KEY"),
        tavily_api_key=os.getenv("TAVILY_API_KEY")
    )
    
    result = orchestrator.execute(
        "Assess flood risk for areas within 5km of major rivers in Texas using elevation data"
    )
    
    print_result(result)


def print_result(result: dict):
    """Print workflow result"""
    if result["success"]:
        print("✅ Workflow completed successfully!\n")
        
        if result.get("final_outputs"):
            print("📁 Final Outputs:")
            for output in result["final_outputs"]:
                print(f"   - {output}")
            print()
        
        if result.get("visualizations"):
            print("🗺️  Visualizations:")
            for viz in result["visualizations"]:
                print(f"   - {viz}")
            print()
        
        if result.get("analysis_results"):
            print("📊 Analysis Results:")
            for key, value in result["analysis_results"].items():
                print(f"   {key}: {value}")
            print()
    else:
        print("❌ Workflow completed with errors:\n")
        for error in result.get("errors", []):
            print(f"   - {error}")
        print()


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: OPENAI_API_KEY or ANTHROPIC_API_KEY required")
        exit(1)
    
    # Run examples
    example_1_spatial_query()
    # example_2_land_use_analysis()
    # example_3_flood_risk()
