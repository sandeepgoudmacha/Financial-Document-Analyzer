# Importing libraries and files
from agents import *
from tools import *

from crewai import Task
from agents import financial_analyst, verifier


# Creating a task to analyze financial documents
analyze_financial_document = Task(
    description="""Analyze the user's query: "{query}" and the financial document located at "{file_path}". \
Use sound financial analysis methods to extract key data (revenues, profitability, debt, cash flow, and trends). \
Use the Financial Document Reader tool to parse the report. \
If relevant, search the internet for recent market or industry benchmarks to compare performance. \
Always provide a clear, professional financial analysis.""",
    expected_output="""1. Extract and summarize key financial metrics (e.g., revenue, net income, margins, liquidity ratios, debt ratios).
2. Provide a concise summary of the company's financial health.
3. Highlight at least 3 major opportunities or risks detected in the document.
4. Offer 2–3 actionable investment insights based on the findings.
5. Use clear, structured language suitable for investors and analysts.""",
    agent=financial_analyst,
    tools=[FinancialDocumentTool(), search_tool],
    async_execution=False,
)

# Creating an investment analysis task
investment_analysis = Task(
    description="""Review the financial document located at "{file_path}" and provide a structured investment analysis. \
Use the Financial Document Reader tool to extract relevant information. \
Identify investment opportunities, risks, and make clear buy/hold/sell recommendations. \
Support your advice with financial reasoning and, if relevant, industry comparisons.""",
    expected_output="""1. Summarize at least 3 investment opportunities or red flags identified in the document.
2. Provide at least 2 buy/hold/sell recommendations, with reasoning.
3. Highlight key ratios or performance trends that influenced your decisions.
4. Offer a balanced outlook, noting both strengths and weaknesses.
5. Ensure advice is realistic and based on evidence from the document.""",
    agent=investment_advisor,
    tools=[FinancialDocumentTool(), search_tool],
    async_execution=False,
)

# Creating a risk assessment task
risk_assessment = Task(
    description="""Perform a comprehensive risk assessment of the financial document located at "{file_path}" in relation to the user's query "{query}". \
Use the Financial Document Reader tool to identify risks in areas such as liquidity, debt management, profitability, and market exposure. \
Provide practical risk mitigation recommendations.""",
    expected_output="""1. List at least 3 major financial or operational risks identified.
2. Summarize market/industry risks relevant to the company.
3. Provide a rating (low/medium/high) for overall financial risk.
4. Recommend at least 2 practical risk mitigation strategies.
5. Use structured, investor-friendly language.""",
    agent=risk_assessor,
    tools=[FinancialDocumentTool(), search_tool],
    async_execution=False,
)

# Creating a document verification task
verification = Task(
    description="""Verify the uploaded document at "{file_path}" to confirm it is a legitimate, complete financial report. \
Use the Financial Document Reader tool to parse the file. \
Check for the presence of key financial statements (income statement, balance sheet, cash flow) and at least 10 financial parameters. \
Flag any missing or suspicious data.""",
    expected_output="""1. State whether the document is a valid financial report (yes/no).
2. List the key financial statements and metrics found (up to 10).
3. Note any missing or suspicious elements.
4. Provide a brief summary of the report's completeness and reliability.""",
    agent=verifier,
    tools=[FinancialDocumentTool()],
    async_execution=False,
)
