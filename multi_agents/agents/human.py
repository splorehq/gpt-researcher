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
            # Stream response to the user if a websocket is provided
            if self.websocket and self.stream_output:
                try:
                    await self.stream_output("human_feedback", "request", layout, self.websocket)
                    response = await self.websocket.receive_text()
                    response = json.loads(response)
                    # response = {
                    #     "type": 'human_feedback',
                    #     "value": layout
                    # }
                    # print(f"Received response: {response["value"]}")  # Add this line for debugging
                    user_feedback = response["value"]
                except Exception as e:
                    print(f"Error receiving human feedback: {e}")
            # Otherwise, prompt the user for feedback in the console
            else:
                user_feedback = input(f"Any feedback on this plan? {layout}? If not, please reply with 'no'.\n>> ")

        return {"sections": user_feedback}
