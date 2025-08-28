# Importing libraries and files
from typing import Type
from pydantic import BaseModel, Field
from langchain_community.document_loaders import PyPDFLoader
from crewai.tools import BaseTool
from crewai_tools.tools import SerperDevTool
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()


# ------------------------------
# Creating Search Tool
# ------------------------------
search_tool = SerperDevTool()


# ------------------------------
# Financial Document Reader Tool
# ------------------------------
class FinancialDocumentToolInput(BaseModel):
    path: str = Field(description="Path of the financial PDF file to read.")


class FinancialDocumentTool(BaseTool):
    name: str = "Financial Document Reader"
    description: str = "Reads and extracts data from a financial PDF report."
    args_schema: Type[BaseModel] = FinancialDocumentToolInput

    def _run(self, path: str) -> str:
        return asyncio.run(self.read_data_tool(path=path))

    async def read_data_tool(self, path: str) -> str:
        """Tool to read data from a financial PDF file."""
        docs = PyPDFLoader(file_path=path).load()

        full_report = ""
        for data in docs:
            content = data.page_content.strip()
            # Normalize extra line breaks
            while "\n\n" in content:
                content = content.replace("\n\n", "\n")
            full_report += content + "\n"

        return full_report


# ------------------------------
# Investment Analysis Tool
# ------------------------------
class InvestmentToolInput(BaseModel):
    financial_document_data: str = Field(
        description="Financial document data to analyze for investments."
    )


class InvestmentTool(BaseTool):
    name: str = "Investment Analysis Tool"
    description: str = "Analyzes financial document data to provide investment insights."
    args_schema: Type[BaseModel] = InvestmentToolInput

    def _run(self, financial_document_data: str) -> str:
        return asyncio.run(self.analyze_investment_tool(financial_document_data=financial_document_data))

    async def analyze_investment_tool(self, financial_document_data: str) -> str:
        """Analyze financial document data for investment opportunities."""
        processed_data = " ".join(financial_document_data.split())

        # 🔑 Placeholder logic for now
        # TODO: Add valuation ratios, trend analysis, sector comparison, etc.
        return (
            f"📊 Investment analysis placeholder.\n"
            f"Processed {len(processed_data)} characters of financial data.\n"
            f"Further detailed logic (ROI, growth, sector analysis) to be implemented."
        )


# ------------------------------
# Risk Assessment Tool
# ------------------------------
class RiskToolInput(BaseModel):
    financial_document_data: str = Field(
        description="Financial document data to analyze for risks."
    )


class RiskTool(BaseTool):
    name: str = "Risk Assessment Tool"
    description: str = "Analyzes financial document data to provide risk assessment."
    args_schema: Type[BaseModel] = RiskToolInput

    def _run(self, financial_document_data: str) -> str:
        return asyncio.run(self.create_risk_assessment_tool(financial_document_data=financial_document_data))

    async def create_risk_assessment_tool(self, financial_document_data: str) -> str:
        """Create a risk assessment from financial document data."""
        processed_data = " ".join(financial_document_data.split())

        # 🔑 Placeholder logic for now
        # TODO: Add credit risk, liquidity risk, volatility, debt ratio, etc.
        return (
            f"⚠️ Risk assessment placeholder.\n"
            f"Processed {len(processed_data)} characters of financial data.\n"
            f"Further detailed logic (market risk, operational risk, financial ratios) to be implemented."
        )
