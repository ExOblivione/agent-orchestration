import os
from typing import Optional, AsyncIterator, Union
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

load_dotenv()

class AgentTemplate:
    """
    A simple, reusable agent template using Microsoft Agent Framework.
    
    This agent can be configured with custom instructions and capabilities,
    making it suitable for all orchestration patterns.
    
    Attributes:
        name: Unique identifier for the agent
        instructions: System instructions defining agent behavior
        credential: Azure credential for authentication
        client: Azure OpenAI Responses client
        agent: The underlying Microsoft Agent Framework agent
    """
    
    def __init__(
        self,
        name: str,
        instructions: str,
        deployment_name: Optional[str] = None,
        project_endpoint: Optional[str] = None
    ):
        """
        Initialize the agent template.
        
        Args:
            name: Name of the agent
            instructions: Instructions defining the agent's role and behavior
            deployment_name: Azure OpenAI deployment name (uses env var if not provided)
            project_endpoint: Azure AI project endpoint (uses env var if not provided)
        """
        self.name = name
        self.instructions = instructions
        
        # Initialize Azure credentials
        self.credential = AzureCliCredential()
        
        # Initialize client
        self.client = AzureOpenAIResponsesClient(
            project_endpoint=project_endpoint or os.environ["AZURE_AI_PROJECT_ENDPOINT"],
            deployment_name=deployment_name or os.environ["AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME"],
            credential=self.credential,
        )
        
        # Create the agent
        self.agent = self.client.as_agent(
            name=self.name,
            instructions=self.instructions,
        )
    
    async def run(
        self,
        message: str,
        stream: bool = False
    ) -> Union[str, AsyncIterator[str]]:
        """
        Execute the agent with a message.
        
        Args:
            message: Input message for the agent
            stream: Whether to stream the response (default: False)
        
        Returns:
            Complete response string or async iterator of response chunks
        """
        if stream:
            return self._stream_response(message)
        else:
            result = await self.agent.run(message)
            return str(result)
    
    async def _stream_response(self, message: str) -> AsyncIterator[str]:
        """
        Stream response tokens as they are generated.
        
        Args:
            message: Input message for the agent
            
        Yields:
            Response chunks as they are generated
        """
        async for chunk in self.agent.run(message, stream=True):
            if chunk.text:
                yield chunk.text
    
    def __repr__(self) -> str:
        """String representation of the agent."""
        return f"AgentTemplate(name='{self.name}')"
