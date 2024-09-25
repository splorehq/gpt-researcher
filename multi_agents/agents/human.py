import json


class HumanAgent:
    def __init__(self, websocket=None, stream_output=None, headers=None):
        self.websocket = websocket
        self.stream_output = stream_output
        self.headers = headers or {}

    async def review_plan(self, research_state: dict):
        print(f"HumanAgent websocket: {self.websocket}")
        print(f"HumanAgent stream_output: {self.stream_output}")
        task = research_state.get("task")
        layout = research_state.get("sections")

        user_feedback = layout

        if task.get("include_human_feedback"):
            # Stream response to the user if a websocket is provided (such as from web app)
            if self.websocket and self.stream_output:
                try:
                    await self.stream_output("human_feedback", "request", layout, self.websocket)
                    response = await self.websocket.receive_text()
                    print(f"Received response: {response}", flush=True)
                    response_data = json.loads(response)
                    if response_data.get("type") == "human_feedback":
                        feedback = response_data.get("value")
                    user_feedback = [
                        {
                            "title": feedback[0],
                            "instructions": """You are a senior carbon market analyst at GenZero, a Temasek-founded investment platform company focused on accelerating global decarbonization. Your task is to write the "Policy Analysis" section of a strategic brief on carbon market developments.

When writing the "Policy Analysis" section:

1. Provide a brief overview of the key policy or regulation.
2. Explain the main objectives and mechanisms of the policy.
3. Present a concise comparative analysis with similar policies in other jurisdictions.
4. Discuss the policy's current implementation stage and potential future developments.
5. Evaluate the impact on carbon markets and potential barriers to effectiveness.
6. Analyze the positions and responses of key carbon market stakeholders, including:
   - Standard-setting bodies (e.g., Verra, Gold Standard, American Carbon Registry)
   - Multilateral institutions (e.g., World Bank, IFC, ADB)
   - Market intermediaries (e.g., exchanges, brokers)
   - Major buyers and sellers (e.g., oil & gas companies, airlines)
   - NGOs and think tanks (e.g., Environmental Defense Fund, World Resources Institute)
7. Include relevant data points and expert opinions with 3-4 citations per major claim.
8. Use bullet points or short paragraphs for clarity.

Your writing style should be:
- Clear, concise, and technically precise
- Analytical and objective, avoiding any political bias
- Focused on presenting factual information without recommendations

Sample Output:
## Policy Analysis: Article 6 of the Paris Agreement

### Key Policy Overview
Article 6 of the Paris Agreement establishes a framework for international cooperation on carbon markets. Key features include:

- Voluntary Cooperation: Allows countries to trade emission reductions [1]
- Environmental Integrity: Aims to prevent double-counting of emission reductions [2]
- Sustainable Development: Promotes sustainable development and poverty eradication [3]

### Main Objectives and Mechanisms
The policy aims to facilitate higher ambition in mitigation and adaptation actions:

1. Article 6.2: Cooperative Approaches
   - Enables bilateral and multilateral transfers of mitigation outcomes
   - Requires corresponding adjustments to prevent double-counting [4]

2. Article 6.4: Sustainable Development Mechanism
   - Establishes a centralized crediting mechanism
   - Allows both public and private sector participation [5]

3. Article 6.8: Non-market Approaches
   - Promotes integrated, holistic, and balanced non-market approaches
   - Focuses on areas such as technology transfer and capacity-building [6]

### Comparative Analysis

| Parameter | Article 6 | Clean Development Mechanism | Voluntary Carbon Market |
|-----------|-----------|---------------------------|--------------------------|
| Governance | UNFCCC | UNFCCC | Various standards bodies |
| Scope | International | Developed to developing countries | Global |
| Accounting | Corresponding adjustments | No corresponding adjustments | Varies by standard |
| Co-benefits | Emphasized | Secondary consideration | Often emphasized |

Sources: [1], [2], [7], [8]

### Implementation Stage and Potential Future Developments
- Current status: Rulebook adopted at COP26, implementation ongoing
- Key developments:
  1. Establishment of Article 6.4 Supervisory Body
  2. Development of methodologies for corresponding adjustments
  3. Ongoing negotiations on transition of CDM activities
  4. Exploration of digital infrastructure for tracking and reporting [9]

### Impact on Carbon Markets and Effectiveness Barriers
Market impact:
- Potential to mobilize $250 billion in climate finance annually by 2030 [10]
- Expected to reduce global mitigation costs by 59% by 2050 [11]

Potential barriers:
1. Technical challenges in implementing corresponding adjustments
2. Ensuring environmental integrity across diverse national circumstances
3. Balancing centralized oversight with country-driven approaches
4. Integrating existing voluntary market activities into the Article 6 framework

### Key Data Points

1. Market size projections:
   - Article 6.2 transactions: 50-80 MtCO2e/year by 2025
   - Article 6.4 credits: 35-75 MtCO2e/year by 2030 [12]

2. Emission reduction potential:
   - Additional 5 GtCO2e/year in global emission reductions by 2030
   - Represents 50% increase in current NDC ambitions [13]

3. Economic implications:
   - Cost savings of $250 billion/year in achieving NDCs by 2030
   - Potential to raise $3-5 trillion additional climate finance by 2050 [14]

[1] UNFCCC, "Paris Agreement", 2015
[2] Michaelowa et al., Climate Policy, 2022
[3] World Bank, "State and Trends of Carbon Pricing 2023", 2023
[4] OECD, "Corresponding Adjustments: Interpretation of the Article 6 Guidance", 2022
[5] Carbon Mechanisms Review, "The Article 6.4 Mechanism", 2023
[6] Climate Change Expert Group, "Non-Market Approaches under Article 6.8", 2022
[7] Greiner et al., Climate Policy, 2023
[8] Voluntary Carbon Markets Integrity Initiative, "VCM Global Dialogue Report", 2023
[9] UNFCCC, "Article 6 Implementation Updates", 2023
[10] International Emissions Trading Association, "The Economic Potential of Article 6", 2022
[11] Nature Climate Change, "Global cooperation through Article 6 could reduce climate mitigation costs", 2023
[12] NewClimate Institute, "Article 6 Market Projections", 2023
[13] IPCC, "Sixth Assessment Report", 2022
[14] McKinsey & Company, "The economic transformation potential of Article 6", 2023""",
                        }
                    ]
                    for i in range(1, len(feedback)):
                        user_feedback.append(
                            {
                                "title": feedback[i],
                                "instructions": ""
                            }
                        )
                    # else:
                    #     print(
                    #         f"Unexpected response type: {response_data.get('type')}",
                    #         flush=True,
                    #     )
                except Exception as e:
                    print(f"Error receiving human feedback: {e}", flush=True)
            # Otherwise, prompt the user for feedback in the console
            else:
                user_feedback = input(
                    f"Any feedback on this plan? {layout}? If not, please reply with 'no'.\n>> "
                )

        print(f"User feedback before return: {user_feedback}")

        return {"sections": user_feedback}
