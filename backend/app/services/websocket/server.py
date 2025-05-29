import socketio
import logging
from typing import Dict, Any, List
from fastapi import FastAPI

logger = logging.getLogger(__name__)

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio)

connected_clients = {}

@sio.event
async def connect(sid, environ):
    """Handle client connection"""
    logger.info(f"Client connected: {sid}")
    connected_clients[sid] = {
        'id': sid,
        'subscriptions': []
    }
    await sio.emit('connection_success', {'status': 'connected'}, room=sid)

@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {sid}")
    if sid in connected_clients:
        del connected_clients[sid]

@sio.event
async def subscribe_to_dashboard(sid, data):
    """Subscribe client to dashboard updates"""
    logger.info(f"Client {sid} subscribed to dashboard updates")
    if sid in connected_clients:
        if 'compliance_dashboard' not in connected_clients[sid]['subscriptions']:
            connected_clients[sid]['subscriptions'].append('compliance_dashboard')
        await sio.emit('subscription_success', {'channel': 'compliance_dashboard'}, room=sid)

@sio.event
async def unsubscribe_from_dashboard(sid, data):
    """Unsubscribe client from dashboard updates"""
    logger.info(f"Client {sid} unsubscribed from dashboard updates")
    if sid in connected_clients:
        if 'compliance_dashboard' in connected_clients[sid]['subscriptions']:
            connected_clients[sid]['subscriptions'].remove('compliance_dashboard')
        await sio.emit('unsubscription_success', {'channel': 'compliance_dashboard'}, room=sid)

async def broadcast_dashboard_update(data: Dict[str, Any]):
    """Broadcast dashboard update to all subscribed clients"""
    subscribers = [sid for sid, client in connected_clients.items() 
                  if 'compliance_dashboard' in client['subscriptions']]
    
    if subscribers:
        logger.info(f"Broadcasting dashboard update to {len(subscribers)} clients")
        for sid in subscribers:
            await sio.emit('dashboard_update', data, room=sid)
    else:
        logger.info("No clients subscribed to dashboard updates")

def setup_socketio(app: FastAPI):
    """Mount Socket.IO app to FastAPI app"""
    app.mount('/ws', socket_app)
    logger.info("Socket.IO server mounted at /ws")
    return sio
