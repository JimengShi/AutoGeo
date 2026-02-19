"""
GEOAGENT Orchestrator using LangGraph
Multi-agent orchestration for geospatial data science workflows
"""

import logging
from typing import TypedDict, Annotated, Sequence, Optional
from typing_extensions import Literal
import operator
from pathlib import Path
import json

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

try:
    # Try relative imports first (when used as a package)
    from .agents.search_agent import SearchAgent
    from .agents.download_agent import DownloadAgent
    from .agents.spatial_query_agent import SpatialQueryAgent
    from .agents.transform_agent import TransformAgent
    from .agents.process_agent import ProcessAgent
    from .agents.analysis_agent import AnalysisAgent
    from .agents.visualization_agent import VisualizationAgent
    from .agents.export_agent import ExportAgent
except ImportError:
    # Fall back to absolute imports (when run directly)
    from geospatial_agents.agents.search_agent import SearchAgent
    from geospatial_agents.agents.download_agent import DownloadAgent
    from geospatial_agents.agents.spatial_query_agent import SpatialQueryAgent
    from geospatial_agents.agents.transform_agent import TransformAgent
    from geospatial_agents.agents.process_agent import ProcessAgent
    from geospatial_agents.agents.analysis_agent import AnalysisAgent
    from geospatial_agents.agents.visualization_agent import VisualizationAgent
    from geospatial_agents.agents.export_agent import ExportAgent

logger = logging.getLogger(__name__)


class WorkflowState(TypedDict):
    """State maintained throughout the workflow"""
    user_request: str
    workflow_plan: list
    current_step: int
    total_steps: int
    search_results: list
    downloaded_data: dict  # {dataset_id: path}
    processed_data: dict  # {step_id: data}
    spatial_queries: list
    transformations: list
    analysis_results: dict
    visualizations: list
    exports: list
    errors: list
    messages: Annotated[Sequence, operator.add]  # Conversation history
    final_outputs: list


class GeoOrchestratorLangGraph:
    """LangGraph-based orchestrator for geospatial workflows"""
    
    def __init__(
        self,
        llm_api_key: str = None,
        llm_model: str = "gpt-4o-mini",
        llm_provider: str = "openai",
        tavily_api_key: str = None,
        work_dir: str = "./geospatial_data"
    ):
        """
        Initialize the orchestrator
        
        Args:
            llm_api_key: API key for LLM
            llm_model: LLM model name
            llm_provider: LLM provider ('openai', 'anthropic')
            tavily_api_key: API key for Tavily search
            work_dir: Working directory for data
        """
        import os
        
        self.llm_api_key = llm_api_key or os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        self.llm_model = llm_model
        self.llm_provider = llm_provider.lower()
        self.tavily_api_key = tavily_api_key or os.getenv("TAVILY_API_KEY")
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize LLM
        if self.llm_provider == "openai":
            self.llm = ChatOpenAI(
                api_key=self.llm_api_key,
                model=self.llm_model,
                temperature=0.3
            )
        elif self.llm_provider == "anthropic":
            self.llm = ChatAnthropic(
                api_key=self.llm_api_key,
                model=self.llm_model,
                temperature=0.3
            )
        else:
            raise ValueError(f"Unknown provider: {llm_provider}")
        
        # Initialize agents
        self.search_agent = SearchAgent(
            llm=self.llm,
            tavily_api_key=self.tavily_api_key,
            work_dir=self.work_dir
        )
        self.download_agent = DownloadAgent(
            llm=self.llm,
            work_dir=self.work_dir
        )
        self.spatial_query_agent = SpatialQueryAgent(
            llm=self.llm,
            work_dir=self.work_dir
        )
        self.transform_agent = TransformAgent(
            llm=self.llm,
            work_dir=self.work_dir
        )
        self.process_agent = ProcessAgent(
            llm=self.llm,
            work_dir=self.work_dir
        )
        self.analysis_agent = AnalysisAgent(
            llm=self.llm,
            work_dir=self.work_dir
        )
        self.visualization_agent = VisualizationAgent(
            llm=self.llm,
            work_dir=self.work_dir
        )
        self.export_agent = ExportAgent(
            llm=self.llm,
            work_dir=self.work_dir
        )
        
        # Build workflow graph
        self.workflow = self._build_workflow()
        
        logger.info("GeoOrchestratorLangGraph initialized")
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("planner", self._plan_workflow)
        workflow.add_node("search", self._execute_search)
        workflow.add_node("download", self._execute_download)
        workflow.add_node("spatial_query", self._execute_spatial_query)
        workflow.add_node("transform", self._execute_transform)
        workflow.add_node("process", self._execute_process)
        workflow.add_node("analysis", self._execute_analysis)
        workflow.add_node("visualization", self._execute_visualization)
        workflow.add_node("export", self._execute_export)
        workflow.add_node("router", self._route_next_step)
        
        # Set entry point
        workflow.set_entry_point("planner")
        
        # Add edges
        workflow.add_edge("planner", "router")
        workflow.add_conditional_edges(
            "router",
            self._should_continue,
            {
                "search": "search",
                "download": "download",
                "spatial_query": "spatial_query",
                "transform": "transform",
                "process": "process",
                "analysis": "analysis",
                "visualization": "visualization",
                "export": "export",
                "end": END
            }
        )
        
        # Add edges from agent nodes back to router
        workflow.add_edge("search", "router")
        workflow.add_edge("download", "router")
        workflow.add_edge("spatial_query", "router")
        workflow.add_edge("transform", "router")
        workflow.add_edge("process", "router")
        workflow.add_edge("analysis", "router")
        workflow.add_edge("visualization", "router")
        workflow.add_edge("export", "router")
        
        return workflow.compile()
    
    def _extract_urls(self, text: str) -> list:
        """Extract URLs from text"""
        import re
        # Pattern to match URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        return urls
    
    def _is_huggingface_url(self, url: str) -> bool:
        """Check if URL is a HuggingFace dataset URL"""
        return "huggingface.co" in url.lower() and "/datasets/" in url.lower()
    
    def _convert_github_blob_url(self, url: str) -> str:
        """Convert GitHub blob URL to raw URL (only for files, not directories)"""
        if "github.com" in url and "/blob/" in url:
            # Don't convert if it ends with / (it's a directory)
            if url.endswith("/"):
                return url  # Keep as-is, let download agent handle as directory
            
            # Convert: https://github.com/user/repo/blob/branch/path/file.ext
            # To: https://raw.githubusercontent.com/user/repo/branch/path/file.ext
            url = url.replace("github.com", "raw.githubusercontent.com")
            url = url.replace("/blob/", "/")
            return url
        return url
    
    def _create_smart_default_workflow(self, user_request: str, requested_limit: Optional[int] = None) -> list:
        """Create a smart default workflow based on keywords in user request"""
        request_lower = user_request.lower()
        default_limit = requested_limit if requested_limit else 10
        
        workflow = []
        
        # Extract URLs from user request
        urls = self._extract_urls(user_request)
        has_url = len(urls) > 0
        
        # Always start with search if not explicitly skipped and no direct URL
        if not has_url and ("download" not in request_lower or "search" in request_lower):
            workflow.append({
                "step_type": "search",
                "description": f"Search for geospatial datasets related to: {user_request}",
                "parameters": {"query": user_request, "limit": default_limit},
                "dependencies": []
            })
        
        # Check for download intent
        download_keywords = ["download", "get", "fetch", "retrieve", "obtain"]
        if any(keyword in request_lower for keyword in download_keywords) or has_url:
            download_params = {"limit": min(default_limit, 5)}
            
            # If URL is present, add it to parameters
            if has_url:
                # Don't convert HuggingFace URLs - they're handled specially
                converted_urls = []
                for url in urls:
                    if self._is_huggingface_url(url):
                        converted_urls.append(url)  # Keep HuggingFace URLs as-is
                    else:
                        converted_urls.append(self._convert_github_blob_url(url))
                
                download_params["url"] = converted_urls[0] if len(converted_urls) == 1 else converted_urls
                download_params["urls"] = converted_urls  # Support multiple URLs
                logger.info(f"Extracted URL(s) from request: {converted_urls}")
            
            workflow.append({
                "step_type": "download",
                "description": f"Download {'from URL' if has_url else 'the identified datasets'}",
                "parameters": download_params,
                "dependencies": [0] if workflow and not has_url else []
            })
        
        # Check for processing intent
        process_keywords = ["process", "analyze", "transform", "reproject", "clip", "calculate", "compute"]
        if any(keyword in request_lower for keyword in process_keywords):
            workflow.append({
                "step_type": "process",
                "description": f"Process the downloaded data: {user_request}",
                "parameters": {},
                "dependencies": [len(workflow) - 1] if workflow else []
            })
        
        # Check for visualization intent
        viz_keywords = ["visualize", "map", "plot", "show", "display", "create map", "risk map"]
        if any(keyword in request_lower for keyword in viz_keywords):
            # Ensure we have data before visualization - add download/process if needed
            has_data_step = any(step.get("step_type") in ["download", "process", "analysis"] for step in workflow)
            if not has_data_step and not has_url:
                # Add download step before visualization if not present
                workflow.append({
                    "step_type": "download",
                    "description": "Download datasets needed for visualization",
                    "parameters": {"limit": min(default_limit, 5)},
                    "dependencies": [0] if workflow and workflow[0].get("step_type") == "search" else []
                })
            
            workflow.append({
                "step_type": "visualization",
                "description": "Create visualization of the results",
                "parameters": {},
                "dependencies": [len(workflow) - 1] if workflow else []
            })
        
        # Check for export intent
        export_keywords = ["export", "save", "output"]
        if any(keyword in request_lower for keyword in export_keywords):
            # Ensure we have data before export - add download/process if needed
            has_data_step = any(step.get("step_type") in ["download", "process", "analysis", "visualization"] for step in workflow)
            if not has_data_step and not has_url:
                # Add download step before export if not present
                workflow.append({
                    "step_type": "download",
                    "description": "Download datasets needed for export",
                    "parameters": {"limit": min(default_limit, 5)},
                    "dependencies": [0] if workflow and workflow[0].get("step_type") == "search" else []
                })
            
            workflow.append({
                "step_type": "export",
                "description": "Export the results",
                "parameters": {"format": "geojson"},
                "dependencies": [len(workflow) - 1] if workflow else []
            })
        
        # If no specific intent found but user said "download", add download step
        if not workflow or (len(workflow) == 1 and workflow[0]["step_type"] == "search"):
            if "download" in request_lower:
                download_params = {"limit": min(default_limit, 5)}
                # Check if URL was extracted
                if has_url:
                    converted_urls = [self._convert_github_blob_url(url) for url in urls]
                    download_params["url"] = converted_urls[0] if len(converted_urls) == 1 else converted_urls
                    download_params["urls"] = converted_urls
                
                workflow.append({
                    "step_type": "download",
                    "description": f"Download {'from URL' if has_url else 'the identified datasets'}",
                    "parameters": download_params,
                    "dependencies": [0] if workflow else []
                })
        
        # If only URL download (no search needed)
        if has_url and not workflow:
            converted_urls = [self._convert_github_blob_url(url) for url in urls]
            return [{
                "step_type": "download",
                "description": "Download dataset from URL",
                "parameters": {
                    "url": converted_urls[0] if len(converted_urls) == 1 else converted_urls,
                    "urls": converted_urls
                },
                "dependencies": []
            }]
        
        return workflow if workflow else [{
            "step_type": "search",
            "description": f"Search for geospatial datasets related to: {user_request}",
            "parameters": {"query": user_request, "limit": default_limit},
            "dependencies": []
        }]
    
    def _extract_number(self, text: str) -> Optional[int]:
        """Extract a number from text (supports digits and English words)"""
        import re
        # First try to find digits
        numbers = re.findall(r'\b(\d+)\b', text)
        if numbers:
            return int(numbers[0])
        
        # Try to convert English words to numbers
        try:
            from word2number import w2n
            text_lower = text.lower()
            # Common patterns: "five", "ten datasets", "first five", etc.
            number_phrases = re.findall(
                r'\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|hundred|thousand)\b',
                text_lower
            )
            if number_phrases:
                # Try to convert the first number phrase found
                number_str = ' '.join(number_phrases[:3])  # Take up to 3 words
                return w2n.word_to_num(number_str)
        except (ImportError, ValueError):
            pass
        
        return None
    
    def _plan_workflow(self, state: WorkflowState) -> WorkflowState:
        """Plan the workflow based on user request"""
        logger.info(f"Planning workflow for: {state['user_request']}")
        
        # Extract number from user request if specified
        requested_limit = self._extract_number(state['user_request'])
        if requested_limit:
            logger.info(f"Extracted limit from user request: {requested_limit}")
        
        prompt = f"""Analyze this geospatial data science request and create a detailed workflow plan: "{state['user_request']}"

            IMPORTANT: The user explicitly requested to "{state['user_request']}". 
            If the request mentions "download", "get", "fetch", or similar, you MUST include a download step.
            If the request mentions "process", "analyze", "transform", "clip", "calculate", or similar, you MUST include processing steps.
            If the request mentions "map", "visualize", "show", or similar, you MUST include a visualization step.

            Determine the sequence of operations needed:
            1. What geospatial data needs to be searched/found?
            2. What data needs to be downloaded? (ALWAYS include if user said "download")
            3. What spatial queries or filters are needed?
            4. What coordinate transformations are required?
            5. What processing operations are needed? (ALWAYS include if user said "process", "analyze", etc.)
            6. What analysis should be performed?
            7. What visualizations should be created? (ALWAYS include if user said "map", "visualize", etc.)
            8. What should be exported?

            Return a JSON list of workflow steps, each with:
            - step_type: one of ["search", "download", "spatial_query", "transform", "process", "analysis", "visualization", "export"]
            - description: what this step does
            - parameters: relevant parameters for this step (for search steps, include "limit" if user specified a number)
            - dependencies: list of step indices this depends on (empty if none)

            {"IMPORTANT: If the user specified a number (e.g., 'show me 6 datasets', 'find 5 datasets'), include that number in the search step's 'limit' parameter." if requested_limit else ""}

            CRITICAL: If the user request contains words like "download", "get", "fetch", you MUST create a multi-step workflow with both search AND download steps.

            Example for "search and download":
            [
            {{
                "step_type": "search",
                "description": "Search for satellite imagery datasets",
                "parameters": {{"query": "Landsat imagery California 2020", "data_type": "satellite", "limit": 10}},
                "dependencies": []
            }},
            {{
                "step_type": "download",
                "description": "Download the identified datasets",
                "parameters": {{"limit": 5}},
                "dependencies": [0]
            }}
            ]

            Example for "search, download, and process":
            [
            {{
                "step_type": "search",
                "description": "Search for datasets",
                "parameters": {{"query": "elevation data", "limit": 10}},
                "dependencies": []
            }},
            {{
                "step_type": "download",
                "description": "Download the datasets",
                "parameters": {{"limit": 5}},
                "dependencies": [0]
            }},
            {{
                "step_type": "process",
                "description": "Process the downloaded data",
                "parameters": {{}},
                "dependencies": [1]
            }}
            ]
        """
        
        messages = [
            SystemMessage(content="You are an expert geospatial data science workflow planner. Always return valid JSON."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        plan_text = response.content
        
        # Parse workflow plan with better error handling
        workflow_plan = []
        try:
            import re
            import ast
            
            # Try to find JSON array in the response (greedy match to get full array)
            json_match = re.search(r'\[[\s\S]*?\]', plan_text)
            if json_match:
                json_str = json_match.group(0).strip()
                
                # First try direct JSON parsing
                try:
                    workflow_plan = json.loads(json_str)
                except json.JSONDecodeError:
                    # If that fails, try to fix common issues
                    # Remove trailing commas before } or ]
                    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
                    # Try replacing single quotes with double quotes (simple approach)
                    # But be careful - this might break strings with apostrophes
                    try:
                        # Try using ast.literal_eval for Python-like syntax
                        workflow_plan = ast.literal_eval(json_str)
                    except (ValueError, SyntaxError):
                        # Last resort: try JSON again after quote replacement
                        json_str = json_str.replace("'", '"')
                        json_str = re.sub(r',\s*}', '}', json_str)
                        json_str = re.sub(r',\s*]', ']', json_str)
                        workflow_plan = json.loads(json_str)
            else:
                # If no JSON found, create smart default workflow
                logger.warning("No JSON workflow plan found, creating smart default workflow")
                workflow_plan = self._create_smart_default_workflow(state['user_request'], requested_limit)
                logger.info(f"Created smart default workflow with {len(workflow_plan)} steps: {[s['step_type'] for s in workflow_plan]}")
        except (json.JSONDecodeError, ValueError, SyntaxError) as e:
            logger.warning(f"Failed to parse workflow plan: {e}")
            logger.debug(f"Plan text excerpt: {plan_text[:300]}")
            # Create smart default workflow on parse failure
            workflow_plan = self._create_smart_default_workflow(state['user_request'], requested_limit)
            logger.info(f"Created smart default workflow with {len(workflow_plan)} steps: {[s['step_type'] for s in workflow_plan]}")
        except Exception as e:
            logger.error(f"Unexpected error parsing workflow plan: {e}")
            workflow_plan = self._create_smart_default_workflow(state['user_request'], requested_limit)
        
        # Validate workflow plan structure and inject limit if needed
        if not isinstance(workflow_plan, list) or len(workflow_plan) == 0:
            logger.warning("Workflow plan is not a valid list, creating smart default")
            workflow_plan = self._create_smart_default_workflow(state['user_request'], requested_limit)
        else:
            # If user specified a limit, ensure search steps use it
            if requested_limit:
                for step in workflow_plan:
                    if step.get("step_type") == "search":
                        if "parameters" not in step:
                            step["parameters"] = {}
                        # Only override if limit not already specified
                        if "limit" not in step["parameters"]:
                            step["parameters"]["limit"] = requested_limit
                            logger.info(f"Injected limit {requested_limit} into search step")
        
        state["workflow_plan"] = workflow_plan
        state["total_steps"] = len(workflow_plan)
        state["current_step"] = 0
        
        # Log workflow plan
        step_types = [s.get("step_type", "unknown") for s in workflow_plan]
        logger.info(f"Workflow planned with {len(workflow_plan)} steps: {step_types}")
        print(f"\n📋 Workflow Plan ({len(workflow_plan)} steps):")
        for i, step in enumerate(workflow_plan, 1):
            print(f"   {i}. {step.get('step_type', 'unknown')}: {step.get('description', '')[:60]}...")
        print()
        
        state["messages"].append(AIMessage(content=f"Workflow planned with {len(workflow_plan)} steps: {', '.join(step_types)}"))
        
        return state
    
    def _route_next_step(self, state: WorkflowState) -> WorkflowState:
        """Route to the next step in the workflow"""
        # This node just passes through - routing happens in _should_continue
        return state
    
    def _should_continue(self, state: WorkflowState) -> str:
        """Determine which step to execute next"""
        current_step = state.get("current_step", 0)
        workflow_plan = state.get("workflow_plan", [])
        
        if current_step >= len(workflow_plan):
            return "end"
        
        step = workflow_plan[current_step]
        dependencies = step.get("dependencies", [])
        
        # Check if dependencies are met (all dependency steps must be < current_step)
        all_deps_met = True
        for dep_idx in dependencies:
            if dep_idx >= current_step:
                all_deps_met = False
                break
        
        if not all_deps_met:
            # Skip to next step if dependencies not met
            state["current_step"] = current_step + 1
            return self._should_continue(state)
        
        step_type = step.get("step_type", "")
        return step_type if step_type else "end"
    
    def _execute_search(self, state: WorkflowState) -> WorkflowState:
        """Execute search step"""
        current_step = state.get("current_step", 0)
        workflow_plan = state.get("workflow_plan", [])
        step = workflow_plan[current_step]
        
        try:
            print(f"🔍 Step {current_step + 1}/{state.get('total_steps', 1)}: Searching for datasets...")
            params = step.get("parameters", {})
            results = self.search_agent.execute(
                task_description=step.get("description", ""),
                parameters=params,
                context=state
            )
            
            search_results = results.get("results", [])
            state["search_results"] = search_results
            state["current_step"] = current_step + 1
            
            if search_results:
                print(f"   ✅ Found {len(search_results)} datasets\n")
                state["messages"].append(AIMessage(content=f"Search completed: found {len(search_results)} results"))
            else:
                print(f"   ⚠️  No datasets found\n")
                state["messages"].append(AIMessage(content="Search completed but no results found"))
        except Exception as e:
            logger.error(f"Search error: {e}")
            print(f"   ❌ Search failed: {str(e)}\n")
            state["errors"].append(f"Search step failed: {str(e)}")
            state["current_step"] = current_step + 1
        
        return state
    
    def _execute_download(self, state: WorkflowState) -> WorkflowState:
        """Execute download step"""
        current_step = state.get("current_step", 0)
        workflow_plan = state.get("workflow_plan", [])
        step = workflow_plan[current_step]
        
        try:
            print(f"📥 Step {current_step + 1}/{state.get('total_steps', 1)}: Downloading datasets...")
            params = step.get("parameters", {})
            # Use original user request for better context (contains location, dates, etc.)
            task_desc = state.get("user_request", step.get("description", ""))
            results = self.download_agent.execute(
                task_description=task_desc,
                parameters=params,
                context=state
            )
            
            # Update downloaded data
            downloaded_count = 0
            if "downloaded_data" in results:
                state["downloaded_data"].update(results["downloaded_data"])
                downloaded_count = len(results["downloaded_data"])
            
            state["current_step"] = current_step + 1
            if downloaded_count > 0:
                print(f"   ✅ Downloaded {downloaded_count} dataset(s)\n")
            else:
                print(f"   ⚠️  No datasets downloaded\n")
            state["messages"].append(AIMessage(content=f"Download completed: {downloaded_count} datasets"))
        except Exception as e:
            logger.error(f"Download error: {e}")
            print(f"   ❌ Download failed: {str(e)}\n")
            state["errors"].append(f"Download step failed: {str(e)}")
            state["current_step"] = current_step + 1
        
        return state
    
    def _execute_spatial_query(self, state: WorkflowState) -> WorkflowState:
        """Execute spatial query step"""
        current_step = state.get("current_step", 0)
        workflow_plan = state.get("workflow_plan", [])
        step = workflow_plan[current_step]
        
        try:
            params = step.get("parameters", {})
            results = self.spatial_query_agent.execute(
                task_description=step.get("description", ""),
                parameters=params,
                context=state
            )
            
            if "filtered_data" in results:
                state["processed_data"][f"spatial_query_{current_step}"] = results["filtered_data"]
            
            state["current_step"] = current_step + 1
            state["messages"].append(AIMessage(content="Spatial query completed"))
        except Exception as e:
            logger.error(f"Spatial query error: {e}")
            state["errors"].append(f"Spatial query step failed: {str(e)}")
            state["current_step"] = current_step + 1
        
        return state
    
    def _execute_transform(self, state: WorkflowState) -> WorkflowState:
        """Execute transform step"""
        current_step = state.get("current_step", 0)
        workflow_plan = state.get("workflow_plan", [])
        step = workflow_plan[current_step]
        
        try:
            params = step.get("parameters", {})
            results = self.transform_agent.execute(
                task_description=step.get("description", ""),
                parameters=params,
                context=state
            )
            
            if "transformed_data" in results:
                state["processed_data"][f"transform_{current_step}"] = results["transformed_data"]
            
            state["current_step"] = current_step + 1
            state["messages"].append(AIMessage(content="Transform completed"))
        except Exception as e:
            logger.error(f"Transform error: {e}")
            state["errors"].append(f"Transform step failed: {str(e)}")
            state["current_step"] = current_step + 1
        
        return state
    
    def _execute_process(self, state: WorkflowState) -> WorkflowState:
        """Execute process step"""
        current_step = state.get("current_step", 0)
        workflow_plan = state.get("workflow_plan", [])
        step = workflow_plan[current_step]
        
        try:
            params = step.get("parameters", {})
            results = self.process_agent.execute(
                task_description=step.get("description", ""),
                parameters=params,
                context=state
            )
            
            if "processed_data" in results:
                state["processed_data"][f"process_{current_step}"] = results["processed_data"]
            
            state["current_step"] = current_step + 1
            state["messages"].append(AIMessage(content="Processing completed"))
        except Exception as e:
            logger.error(f"Process error: {e}")
            state["errors"].append(f"Process step failed: {str(e)}")
            state["current_step"] = current_step + 1
        
        return state
    
    def _execute_analysis(self, state: WorkflowState) -> WorkflowState:
        """Execute analysis step"""
        current_step = state.get("current_step", 0)
        workflow_plan = state.get("workflow_plan", [])
        step = workflow_plan[current_step]
        
        try:
            params = step.get("parameters", {})
            results = self.analysis_agent.execute(
                task_description=step.get("description", ""),
                parameters=params,
                context=state
            )
            
            state["analysis_results"][f"analysis_{current_step}"] = results.get("analysis", {})
            state["current_step"] = current_step + 1
            state["messages"].append(AIMessage(content="Analysis completed"))
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            state["errors"].append(f"Analysis step failed: {str(e)}")
            state["current_step"] = current_step + 1
        
        return state
    
    def _execute_visualization(self, state: WorkflowState) -> WorkflowState:
        """Execute visualization step"""
        current_step = state.get("current_step", 0)
        workflow_plan = state.get("workflow_plan", [])
        step = workflow_plan[current_step]
        
        try:
            print(f"🗺️  Step {current_step + 1}/{state.get('total_steps', 1)}: Creating visualization...")
            params = step.get("parameters", {})
            results = self.visualization_agent.execute(
                task_description=step.get("description", ""),
                parameters=params,
                context=state
            )
            
            if "visualization_path" in results and results["visualization_path"]:
                state["visualizations"].append(str(results["visualization_path"]))
                print(f"   ✅ Created visualization: {results['visualization_path']}\n")
            elif "error" in results:
                print(f"   ⚠️  Visualization skipped: {results['error']}\n")
            else:
                print(f"   ⚠️  Visualization completed but no output file was created\n")
            
            state["current_step"] = current_step + 1
            state["messages"].append(AIMessage(content="Visualization completed"))
        except Exception as e:
            logger.error(f"Visualization error: {e}")
            print(f"   ❌ Visualization failed: {str(e)}\n")
            state["errors"].append(f"Visualization step failed: {str(e)}")
            state["current_step"] = current_step + 1
        
        return state
    
    def _execute_export(self, state: WorkflowState) -> WorkflowState:
        """Execute export step"""
        current_step = state.get("current_step", 0)
        workflow_plan = state.get("workflow_plan", [])
        step = workflow_plan[current_step]
        
        try:
            params = step.get("parameters", {})
            results = self.export_agent.execute(
                task_description=step.get("description", ""),
                parameters=params,
                context=state
            )
            
            if "export_path" in results and results["export_path"]:
                state["exports"].append(str(results["export_path"]))
                state["final_outputs"].append(str(results["export_path"]))
                print(f"   ✅ Exported to: {results['export_path']}\n")
            elif "error" in results:
                print(f"   ⚠️  Export skipped: {results['error']}\n")
            else:
                print(f"   ⚠️  Export completed but no output file was created\n")
            
            state["current_step"] = current_step + 1
            state["messages"].append(AIMessage(content="Export completed"))
        except Exception as e:
            logger.error(f"Export error: {e}")
            state["errors"].append(f"Export step failed: {str(e)}")
            state["current_step"] = current_step + 1
        
        return state
    
    def execute(self, user_request: str) -> dict:
        """
        Execute a complete workflow
        
        Args:
            user_request: Natural language request
            
        Returns:
            Final workflow state
        """
        initial_state = WorkflowState(
            user_request=user_request,
            workflow_plan=[],
            current_step=0,
            total_steps=0,
            search_results=[],
            downloaded_data={},
            processed_data={},
            spatial_queries=[],
            transformations=[],
            analysis_results={},
            visualizations=[],
            exports=[],
            errors=[],
            messages=[HumanMessage(content=user_request)],
            final_outputs=[]
        )
        
        # Run workflow
        final_state = self.workflow.invoke(initial_state)
        
        return {
            "success": len(final_state.get("errors", [])) == 0,
            "search_results": final_state.get("search_results", []),
            "downloaded_data": final_state.get("downloaded_data", {}),
            "processed_data": final_state.get("processed_data", {}),
            "final_outputs": final_state.get("final_outputs", []),
            "visualizations": final_state.get("visualizations", []),
            "analysis_results": final_state.get("analysis_results", {}),
            "errors": final_state.get("errors", []),
            "messages": final_state.get("messages", [])
        }
