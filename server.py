#!/usr/bin/env python

import asyncio
from websockets.asyncio.server import serve
import websockets

connected_clients = {}  # map websocket -> username

async def broadcast(message, sender_ws):
    to_remove = set()
    sender_name = connected_clients.get(sender_ws, "Unknown")
    full_message = f"{sender_name}: {message}"

    for client in connected_clients:
        if client == sender_ws:
            continue  # don't send to sender
        asyncio.create_task(send_safe(client, full_message, to_remove))

    for client in to_remove:
        connected_clients.pop(client, None)

async def send_safe(client, message, to_remove):
    try:
        await client.send(message)
    except websockets.exceptions.ConnectionClosed:
        to_remove.add(client)

async def handle_client(websocket):
    # Ask for a unique username
    while True:
        await websocket.send("Enter your username:")
        username = await websocket.recv()
        if username.strip() == "":
            await websocket.send("Username cannot be empty. Try again.")
        elif username in connected_clients.values():
            await websocket.send("Username already taken. Try another one.")
            print(f"Someone tried to connect using the username {username}, but the username was taken.")
        else:
            connected_clients[websocket] = username
            await websocket.send(f"Welcome, {username}! You can start chatting.")
            print(f"{username} has successfully connected.")
            break

    try:
        async for message in websocket:
            print(f"{username} says: {message}")
            await broadcast(message, websocket)
    finally:
        connected_clients.pop(websocket, None)
        print(f"{username} disconnected.")

async def main():
    async with serve(handle_client, "0.0.0.0", 5000):
        print("Server running on port 5000")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())



