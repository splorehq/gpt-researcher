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
                    
                    for i in range(0, len(feedback)):
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
