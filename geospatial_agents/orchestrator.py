"""
GEOAGENT Orchestrator
Main coordinator for multi-agent geospatial data science workflows
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Types of agents in the system"""
    SEARCH = "search"
    DOWNLOAD = "download"
    SPATIAL_QUERY = "spatial_query"
    TRANSFORM = "transform"
    PROCESS = "process"
    ANALYSIS = "analysis"
    VISUALIZATION = "visualization"
    EXPORT = "export"


@dataclass
class AgentTask:
    """Represents a task for an agent"""
    agent_type: AgentType
    task_description: str
    parameters: Dict[str, Any]
    dependencies: List[str] = None  # Task IDs this depends on
    task_id: str = None


@dataclass
class WorkflowPlan:
    """Represents a complete workflow plan"""
    tasks: List[AgentTask]
    estimated_steps: int
    workflow_type: str


@dataclass
class WorkflowResult:
    """Result of workflow execution"""
    success: bool
    results: Dict[str, Any]
    intermediate_data: Dict[str, Any]
    final_outputs: List[str]
    errors: List[str] = None


class GeoOrchestrator:
    """Orchestrator for geospatial multi-agent workflows"""
    
    def __init__(
        self,
        llm_api_key: Optional[str] = None,
        llm_model: str = "gpt-4o-mini",
        llm_provider: str = "openai",
        work_dir: str = "./geospatial_data"
    ):
        """
        Initialize the orchestrator
        
        Args:
            llm_api_key: API key for LLM service
            llm_model: LLM model name
            llm_provider: LLM provider ('openai', 'anthropic')
            work_dir: Working directory for data storage
        """
        self.llm_api_key = llm_api_key
        self.llm_model = llm_model
        self.llm_provider = llm_provider
        self.work_dir = work_dir
        
        # Initialize agents (to be implemented)
        self.agents = {}
        self.workflow_state = {}
        
        logger.info("GeoOrchestrator initialized")
    
    def plan_workflow(self, user_request: str) -> WorkflowPlan:
        """
        Parse user request and create a workflow plan
        
        Args:
            user_request: Natural language request from user
            
        Returns:
            WorkflowPlan with ordered tasks
        """
        logger.info(f"Planning workflow for: {user_request}")
        
        # Use LLM to understand the request and generate workflow plan
        workflow_plan = self._llm_plan_workflow(user_request)
        
        return workflow_plan
    
    def _llm_plan_workflow(self, request: str) -> WorkflowPlan:
        """
        Use LLM to generate workflow plan
        
        Args:
            request: User's natural language request
            
        Returns:
            WorkflowPlan
        """
        # This would use LLM to analyze the request and generate a plan
        # For now, return a placeholder structure
        
        prompt = f"""Analyze this geospatial data science request and create a workflow plan: "{request}"

Determine:
1. What geospatial data is needed
2. What operations need to be performed
3. The order of operations
4. Which agents should handle each step

Return a structured workflow plan with:
- List of tasks in execution order
- Agent type for each task
- Parameters for each task
- Dependencies between tasks

Example workflow types:
- "land_use_analysis": Analyze land use changes
- "spatial_query": Query and filter spatial data
- "visualization": Create maps and visualizations
- "risk_assessment": Assess spatial risks
"""
        
        # TODO: Call LLM to generate plan
        # For now, return example structure
        tasks = [
            AgentTask(
                agent_type=AgentType.SEARCH,
                task_description="Search for geospatial datasets",
                parameters={"query": request, "data_type": "auto"},
                task_id="task_1"
            ),
            AgentTask(
                agent_type=AgentType.DOWNLOAD,
                task_description="Download identified datasets",
                parameters={},
                dependencies=["task_1"],
                task_id="task_2"
            )
        ]
        
        return WorkflowPlan(
            tasks=tasks,
            estimated_steps=len(tasks),
            workflow_type="general"
        )
    
    def execute_workflow(self, plan: WorkflowPlan) -> WorkflowResult:
        """
        Execute a workflow plan
        
        Args:
            plan: WorkflowPlan to execute
            
        Returns:
            WorkflowResult with execution results
        """
        logger.info(f"Executing workflow with {len(plan.tasks)} tasks")
        
        results = {}
        intermediate_data = {}
        errors = []
        
        # Execute tasks in order, respecting dependencies
        for task in plan.tasks:
            try:
                # Check dependencies
                if task.dependencies:
                    for dep_id in task.dependencies:
                        if dep_id not in results:
                            raise ValueError(f"Dependency {dep_id} not completed")
                
                # Execute task
                logger.info(f"Executing {task.agent_type.value}: {task.task_description}")
                task_result = self._execute_agent_task(task, intermediate_data)
                
                results[task.task_id] = task_result
                if 'data' in task_result:
                    intermediate_data[task.task_id] = task_result['data']
                    
            except Exception as e:
                error_msg = f"Error in {task.task_id}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
                # Decide whether to continue or abort
        
        # Determine final outputs
        final_outputs = self._extract_final_outputs(results)
        
        return WorkflowResult(
            success=len(errors) == 0,
            results=results,
            intermediate_data=intermediate_data,
            final_outputs=final_outputs,
            errors=errors if errors else None
        )
    
    def _execute_agent_task(
        self,
        task: AgentTask,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a single agent task
        
        Args:
            task: AgentTask to execute
            context: Context from previous tasks
            
        Returns:
            Task execution result
        """
        agent = self._get_agent(task.agent_type)
        
        # Merge context into parameters
        params = {**task.parameters}
        params['context'] = context
        
        # Execute agent
        result = agent.execute(task.task_description, params)
        
        return {
            'agent': task.agent_type.value,
            'task_id': task.task_id,
            'result': result,
            'data': result.get('data') if isinstance(result, dict) else None
        }
    
    def _get_agent(self, agent_type: AgentType):
        """Get agent instance for given type"""
        if agent_type not in self.agents:
            # Lazy load agent
            self.agents[agent_type] = self._create_agent(agent_type)
        return self.agents[agent_type]
    
    def _create_agent(self, agent_type: AgentType):
        """Create agent instance"""
        # TODO: Implement actual agent creation
        # This is a placeholder
        from geospatial_agents.agents.base_agent import BaseAgent
        return BaseAgent(
            agent_type=agent_type,
            llm_api_key=self.llm_api_key,
            llm_model=self.llm_model,
            llm_provider=self.llm_provider
        )
    
    def _extract_final_outputs(self, results: Dict[str, Any]) -> List[str]:
        """Extract final output paths from results"""
        outputs = []
        for task_id, result in results.items():
            if 'result' in result and isinstance(result['result'], dict):
                if 'output_path' in result['result']:
                    outputs.append(result['result']['output_path'])
        return outputs
    
    def chat(self, user_input: str) -> str:
        """
        Interactive chat interface for workflow execution
        
        Args:
            user_input: User's natural language input
            
        Returns:
            Response message
        """
        try:
            # Plan workflow
            plan = self.plan_workflow(user_input)
            
            # Execute workflow
            result = self.execute_workflow(plan)
            
            if result.success:
                response = f"✅ Workflow completed successfully!\n\n"
                response += f"📊 Executed {len(plan.tasks)} tasks\n"
                if result.final_outputs:
                    response += f"📁 Outputs:\n"
                    for output in result.final_outputs:
                        response += f"  - {output}\n"
                return response
            else:
                return f"❌ Workflow completed with errors:\n" + "\n".join(result.errors)
                
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return f"❌ Error: {str(e)}"
