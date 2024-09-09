import asyncio
from typing import Dict, List

from fastapi import WebSocket

class WebSocketManager:
    """Manage websockets"""

    def __init__(self):
        """Initialize the WebSocketManager class."""
        self.active_connections: List[WebSocket] = []
        self.sender_tasks: Dict[WebSocket, asyncio.Task] = {}
        self.message_queues: Dict[WebSocket, asyncio.Queue] = {}
        self.active_task_connections: Dict[int, WebSocket] = {}  # Map task_id to initial websocket
        self.active_websocket_connections: Dict[WebSocket, WebSocket] = {}  # Map initial websocket to active websocket

    async def start_sender(self, websocket: WebSocket):
        """Start the sender task."""
        queue = self.message_queues.get(websocket)
        if not queue:
            return

        while True:
            message = await queue.get()
            if websocket in self.active_connections:
                try:
                    if message == "ping":
                        await (self.get_active_websocket(websocket)).send_text("pong")
                    else:
                        await (self.get_active_websocket(websocket)).send_text(message)
                except:
                    break
            else:
                break

    async def connect(self, websocket: WebSocket):
        """Connect a websocket."""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.message_queues[websocket] = asyncio.Queue()
        self.sender_tasks[websocket] = asyncio.create_task(self.start_sender(websocket))
    
    async def map_task_socket(self, task_id: int, new_websocket: WebSocket):
        """Connect a websocket."""
        if task_id in self.active_task_connections:
            old_websocket = self.active_task_connections[task_id]
            self.active_websocket_connections[old_websocket] = new_websocket
            if old_websocket != new_websocket:
                queue = self.message_queues.get(old_websocket)
                if queue:
                    while not queue.empty():
                        message = await queue.get()
                        await self.message_queues[new_websocket].put(message)
        else:
            self.active_websocket_connections[new_websocket] = new_websocket

        self.active_task_connections[task_id] = new_websocket

    async def disconnect_task_socket(self,task_id: int):
        #To:Do Kill task
        if task_id in self.active_task_connections:
            old_websocket = self.active_task_connections[task_id]
            await self.disconnect(old_websocket)
            self.active_task_connections.pop(task_id)

    async def disconnect(self, websocket: WebSocket):
        """Disconnect a websocket."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            self.sender_tasks[websocket].cancel()
            await self.message_queues[websocket].put(None)
            del self.sender_tasks[websocket]
            del self.message_queues[websocket]
        else:
            print('no websocket found')

    def get_active_websocket(self, websocket: WebSocket):
        return self.active_websocket_connections.get(websocket)

manager = WebSocketManager()


