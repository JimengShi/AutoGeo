"""
Example workflow execution for GEOAGENT
Demonstrates how to use the multi-agent system
"""

from geospatial_agents.orchestrator import GeoOrchestrator
import os

def main():
    """Example workflow execution"""
    
    # Initialize orchestrator
    orchestrator = GeoOrchestrator(
        llm_api_key=os.getenv("OPENAI_API_KEY"),
        llm_model="gpt-4o-mini-2024-07-18",
        llm_provider="openai",
        work_dir="./geospatial_data"
    )
    
    # Example 1: Simple spatial query
    print("=" * 60)
    print("Example 1: Find parks near downtown Seattle")
    print("=" * 60)
    
    request1 = "Find all parks within 5 miles of downtown Seattle"
    result1 = orchestrator.chat(request1)
    print(result1)
    print()
    
    # Example 2: Land use analysis
    print("=" * 60)
    print("Example 2: Land use change analysis")
    print("=" * 60)
    
    request2 = "Analyze land use change in California from 2020 to 2024 using satellite imagery"
    result2 = orchestrator.chat(request2)
    print(result2)
    print()
    
    # Example 3: Flood risk assessment
    print("=" * 60)
    print("Example 3: Flood risk assessment")
    print("=" * 60)
    
    request3 = "Assess flood risk for areas within 5km of major rivers in Texas using elevation data"
    result3 = orchestrator.chat(request3)
    print(result3)


if __name__ == "__main__":
    main()
