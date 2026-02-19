"""
Main entry point for GEOAGENT
Multi-agent geospatial data science system
"""

import os
import sys
import logging
from pathlib import Path

# Add parent directory to path for imports if running directly
if __name__ == "__main__":
    parent_dir = Path(__file__).parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))

from geospatial_agents.orchestrator_langgraph import GeoOrchestratorLangGraph

# Set logging level to WARNING to hide INFO messages
logging.basicConfig(level=logging.WARNING, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)


def main():
    """Main entry point"""
    print("=" * 70)
    print("AutoGeo Agent: Autonomous Multi-Agent System for Geospatial Data Science Research")
    print("=" * 70)
    print()
    
    # Get API keys
    llm_api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    
    if not llm_api_key:
        print("Error: OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable required")
        return
    
    # Initialize orchestrator
    orchestrator = GeoOrchestratorLangGraph(
        llm_api_key=llm_api_key,
        # llm_model="gpt-4o-mini",
        llm_model="gpt-4o-mini-2024-07-18",
        llm_provider="openai",
        tavily_api_key=tavily_api_key,
        work_dir="./geospatial_data"
    )
    
    print("AutoGeo Agent initialized. Enter your geospatial data science requests.")
    print("Type 'quit' or 'exit' to stop.\n")
    
    # Interactive loop
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("\n🔄 Processing workflow...\n")
            
            # Execute workflow
            result = orchestrator.execute(user_input)
            
            # Display results
            print("\n" + "=" * 70)
            print("Workflow Results")
            print("=" * 70)
            
            if result["success"]:
                print("✅ Workflow completed successfully!\n")
                
                # Show search results if available
                if result.get("search_results"):
                    print("🔍 Search Results:")
                    for i, dataset in enumerate(result["search_results"][:10], 1):
                        print(f"\n   {i}. {dataset.get('name', 'Unknown Dataset')}")
                        if dataset.get('description'):
                            desc = dataset['description'][:150]
                            print(f"      Description: {desc}...")
                        if dataset.get('source'):
                            print(f"      Source: {dataset['source']}")
                        if dataset.get('spatial_coverage'):
                            print(f"      Coverage: {dataset['spatial_coverage']}")
                    print()
                
                # Show downloaded data
                if result.get("downloaded_data"):
                    print("📥 Downloaded Data:")
                    for name, path in result["downloaded_data"].items():
                        print(f"   - {name}: {path}")
                    print()
                
                # Show processed data
                if result.get("processed_data"):
                    print("⚙️  Processed Data:")
                    for step_id, data_path in result["processed_data"].items():
                        print(f"   - {step_id}: {data_path}")
                    print()
                
                if result.get("final_outputs"):
                    print("📁 Final Outputs:")
                    for output in result["final_outputs"]:
                        print(f"   - {output}")
                    print()
                
                if result.get("visualizations"):
                    print("🗺️  Visualizations:")
                    for viz in result.get("visualizations", []):
                        print(f"   - {viz}")
                    print()
                
                if result.get("analysis_results"):
                    print("📊 Analysis Results:")
                    for key, value in result["analysis_results"].items():
                        print(f"   {key}: {value}")
                    print()
                
                # Show messages from workflow
                if result.get("messages"):
                    print("💬 Workflow Messages:")
                    for msg in result["messages"][-5:]:  # Show last 5 messages
                        if hasattr(msg, 'content'):
                            content = str(msg.content)[:300]
                            print(f"   - {content}")
                    print()
            else:
                print("❌ Workflow completed with errors:\n")
                for error in result.get("errors", []):
                    print(f"   - {error}")
                print()
            
            print("=" * 70 + "\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"\n❌ Error: {str(e)}\n")


if __name__ == "__main__":
    main()
