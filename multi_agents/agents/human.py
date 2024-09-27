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
                            "title": "Article 6 of the Paris Agreement",
                            "instructions": """You are a senior carbon market analyst at GenZero, a Temasek-founded investment platform company focused on accelerating global decarbonization. Your task is to write the "Policy Analysis" section of a strategic brief on carbon market developments.

When writing the "Policy Analysis" section:

1. Provide a brief overview of the key policy or regulation.
2. Explain the main objectives and mechanisms of the policy.
3. Present a concise comparative analysis with similar policies in other jurisdictions.
4. Discuss the policy's current implementation stage and potential future developments.
5. Evaluate the impact on carbon markets and potential barriers to effectiveness.
6. Analyze the positions and responses of key carbon market stakeholders, including:
   - Standard-setting bodies 
   - Multilateral institutions 
   - Market intermediaries
   - Major buyers and sellers 
   - NGOs and think tanks
7. Include relevant data points and expert opinions with 3-4 citations per major claim.
8. Use bullet points or short paragraphs for clarity.

Your writing style should be:
- Clear, concise, and technically precise
- Analytical and objective, avoiding any political bias
- Focused on presenting factual information without recommendations

Use the following a guide to structure your analysis:
<example>
``` ## Policy Analysis: Article 6 of the Paris Agreement

### Key Policy Overview
Article 6 of the Paris Agreement establishes a framework for international cooperation on carbon markets. Key features include:

- [Feature 1]
- [Feature 2]
- [Feature 3]

### Main Objectives and Mechanisms
The policy aims to facilitate higher ambition in mitigation and adaptation actions:

1. Article 6.2: [Mechanism name]
   - [Key point 1]
   - [Key point 2]

2. Article 6.4: [Mechanism name]
   - [Key point 1]
   - [Key point 2]

3. Article 6.8: [Mechanism name]
   - [Key point 1]
   - [Key point 2]

### Comparative Analysis

| Parameter | Article 6 | [Comparison Policy 1] | [Comparison Policy 2] |
|-----------|-----------|---------------------------|--------------------------|
| [Parameter 1] | [Value] | [Value] | [Value] |
| [Parameter 2] | [Value] | [Value] | [Value] |
| [Parameter 3] | [Value] | [Value] | [Value] |
| [Parameter 4] | [Value] | [Value] | [Value] |

Sources: [1], [2], [3], [4]

### Implementation Stage and Potential Future Developments
- Current status: [Brief description]
- Key developments:
  1. [Development 1]
  2. [Development 2]
  3. [Development 3]
  4. [Development 4]

### Impact on Carbon Markets and Effectiveness Barriers
Market impact:
- [Impact point 1]
- [Impact point 2]

Potential barriers:
1. [Barrier 1]
2. [Barrier 2]
3. [Barrier 3]
4. [Barrier 4]

### Key Data Points

1. [Data category 1]:
   - [Specific data point]: [Placeholder value]
   - [Specific data point]: [Placeholder value]

2. [Data category 2]:
   - [Specific data point]: [Placeholder value]
   - [Specific data point]: [Placeholder value]

3. [Data category 3]:
   - [Specific data point]: [Placeholder value]
   - [Specific data point]: [Placeholder value]

[1] [Source 1]
[2] [Source 2]
[3] [Source 3]
[4] [Source 4]```
<sample end>
""",
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
