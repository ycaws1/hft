import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.simulation.manager import simulation_manager

router = APIRouter(tags=["websocket"])
logger = logging.getLogger(__name__)


@router.websocket("/ws/simulation/{simulation_id}")
async def simulation_ws(websocket: WebSocket, simulation_id: str):
    state = simulation_manager.get_simulation(simulation_id)
    if not state:
        await websocket.close(code=4004, reason="Simulation not found")
        return

    await websocket.accept()
    simulation_manager.subscribe_ws(simulation_id, websocket)
    logger.info("WS client connected to simulation %s", simulation_id)

    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                msg_type = msg.get("type")
                runner = simulation_manager.get_runner(simulation_id)
                if not runner:
                    continue

                if msg_type == "set_speed":
                    speed = float(msg.get("speed", 1.0))
                    runner.clock.set_speed(speed)
                elif msg_type == "pause":
                    runner.clock.pause()
                elif msg_type == "resume":
                    runner.clock.resume()
            except (json.JSONDecodeError, ValueError):
                pass
    except WebSocketDisconnect:
        logger.info("WS client disconnected from simulation %s", simulation_id)
    finally:
        simulation_manager.unsubscribe_ws(simulation_id, websocket)
