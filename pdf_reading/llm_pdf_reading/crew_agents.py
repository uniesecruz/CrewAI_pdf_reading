"""
Agentes CrewAI para processamento de PDFs
"""
from crewai import Agent, Task, Crew
from crewai.agent import Agent
from crewai.task import Task
from langchain.llms import OpenAI
from typing import List, Dict, Any

class PDFAnalysisAgents:
    """Classe que define os agentes para análise de PDF"""
    
    def __init__(self, llm=None):
        self.llm = llm or OpenAI(temperature=0.7)
    
    def create_pdf_reader_agent(self) -> Agent:
        """Agente especializado em leitura de PDFs"""
        return Agent(
            role="PDF Reader Specialist",
            goal="Extract and understand content from PDF documents efficiently",
            backstory="""You are an expert in reading and extracting information from PDF documents.
            You have extensive experience in understanding document structure, extracting key information,
            and organizing content in a meaningful way.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def create_content_analyzer_agent(self) -> Agent:
        """Agente especializado em análise de conteúdo"""
        return Agent(
            role="Content Analysis Expert",
            goal="Analyze and summarize extracted content from documents",
            backstory="""You are a content analysis expert with deep knowledge in text processing,
            summarization, and information extraction. You excel at identifying key themes,
            important information, and creating comprehensive summaries.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def create_qa_agent(self) -> Agent:
        """Agente especializado em responder perguntas sobre o conteúdo"""
        return Agent(
            role="Question Answering Specialist",
            goal="Provide accurate answers based on document content",
            backstory="""You are a question-answering specialist who excels at understanding
            document content and providing precise, well-reasoned answers based on the
            information available in the documents.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

class PDFAnalysisTasks:
    """Classe que define as tarefas para análise de PDF"""
    
    @staticmethod
    def create_extraction_task(pdf_content: str, agent: Agent) -> Task:
        """Cria tarefa de extração de conteúdo"""
        return Task(
            description=f"""
            Extract and organize the main content from the following PDF text:
            
            {pdf_content}
            
            Please provide:
            1. A structured summary of the main topics
            2. Key information and data points
            3. Important conclusions or findings
            4. Any actionable items or recommendations
            """,
            agent=agent
        )
    
    @staticmethod
    def create_analysis_task(extracted_content: str, agent: Agent) -> Task:
        """Cria tarefa de análise de conteúdo"""
        return Task(
            description=f"""
            Analyze the following extracted content and provide insights:
            
            {extracted_content}
            
            Please provide:
            1. In-depth analysis of the main themes
            2. Relationships between different concepts
            3. Critical insights and implications
            4. Suggestions for further exploration
            """,
            agent=agent
        )
    
    @staticmethod
    def create_qa_task(content: str, question: str, agent: Agent) -> Task:
        """Cria tarefa de resposta a perguntas"""
        return Task(
            description=f"""
            Based on the following document content, answer this question:
            
            Question: {question}
            
            Document Content:
            {content}
            
            Provide a comprehensive and accurate answer based solely on the information
            available in the document. If the information is not available, clearly state so.
            """,
            agent=agent
        )
