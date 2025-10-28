# app/services/browser_manager.py
import asyncio
import uuid
import json
import aiohttp
import docker
import re
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional
from app.config import settings
from app.utils.port_helper import port_allocator
from app.models.session_model import SessionInfo
from app.repositories.session_repo import SessionRepository


class BrowserSession:
    """Represents a single browser session."""
    
    def __init__(self, session_id: str, port: int):
        self.session_id = session_id
        self.port = port
        self.created_at = datetime.now()
        self.status = "starting"
        self.cdp_websocket_url: Optional[str] = None
        self.container_id: Optional[str] = None
        self.browser_id: Optional[str] = None
    
    @property
    def cdp_endpoint(self) -> str:
        if self.cdp_websocket_url:
            return self.cdp_websocket_url
        return f"ws://localhost:{self.port}"
    
    @property
    def uptime_seconds(self) -> int:
        return int((datetime.now() - self.created_at).total_seconds())
    
    def get_public_ip(self) -> str:
        try:
            response = requests.get('http://169.254.169.254/latest/meta-data/public-ipv4', timeout=2)
            if response.status_code == 200:
                return response.text.strip()
        except:
            pass
        
        try:
            response = requests.get('https://api.ipify.org', timeout=5)
            if response.status_code == 200:
                return response.text.strip()
        except:
            pass
        
        return "localhost"
    
    async def get_cdp_websocket_url(self, container) -> Optional[str]:
        try:
            await asyncio.sleep(3)
            logs = container.logs().decode("utf-8")
            print(f"Container logs: {logs}")
            
            patterns = [
                r"ws://.*?/devtools/browser/([a-z0-9\-]+)",
                r"/devtools/browser/([a-z0-9\-]+)",
                r"browser/([a-z0-9\-]+)",
                r"Browser ID: ([a-z0-9\-]+)"
            ]
            
            browser_id = None
            for pattern in patterns:
                match = re.search(pattern, logs)
                if match:
                    browser_id = match.group(1)
                    break
            
            if browser_id:
                self.browser_id = browser_id
                public_ip = self.get_public_ip()
                websocket_url = f"ws://{public_ip}:{self.port}/devtools/browser/{browser_id}"
                return websocket_url
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"http://localhost:{self.port}/json") as response:
                        if response.status == 200:
                            tabs = await response.json()
                            if tabs and len(tabs) > 0:
                                websocket_url = tabs[0].get('webSocketDebuggerUrl')
                                if websocket_url:
                                    public_ip = self.get_public_ip()
                                    websocket_url = websocket_url.replace('localhost', public_ip)
                                    return websocket_url
            except Exception as e:
                print(f"Failed to query CDP discovery endpoint: {e}")
                
        except Exception as e:
            print(f"Failed to get CDP WebSocket URL: {e}")
        return None
    
    async def start(self) -> bool:
        try:
            client = docker.from_env()
            container = client.containers.run(
                "chromium-cdp",
                detach=True,
                ports={"9222/tcp": self.port},
                name=f"browser-{self.session_id}",
                remove=True,
                environment={"DISPLAY": ":99"}
            )
            self.container_id = container.id
            await asyncio.sleep(2)
            container.reload()
            if container.status != 'running':
                print(f"Container {self.container_id} is not running. Status: {container.status}")
                self.status = "error"
                return False
            
            self.cdp_websocket_url = await self.get_cdp_websocket_url(container)
            self.status = "active"
            return True
            
        except Exception as e:
            print(f"Failed to start browser session {self.session_id}: {e}")
            self.status = "error"
            await self.cleanup()
            return False
    
    async def cleanup(self):
        try:
            if self.container_id:
                client = docker.from_env()
                try:
                    container = client.containers.get(self.container_id)
                    container.stop(timeout=5)
                    container.remove()
                    print(f"Stopped and removed container {self.container_id}")
                except docker.errors.NotFound:
                    print(f"Container {self.container_id} not found")
                except Exception as e:
                    print(f"Error stopping container {self.container_id}: {e}")
        except Exception as e:
            print(f"Error during cleanup for session {self.session_id}: {e}")
        finally:
            port_allocator.release_port(self.port)
            self.status = "closed"


class BrowserManager:
    """Manages browser sessions and their lifecycle."""
    
    def __init__(self):
        self.sessions: Dict[str, BrowserSession] = {}  # Keep for cleanup
        self.start_time = datetime.now()
    
    async def create_session(self, repo: SessionRepository, session_id: Optional[str] = None) -> Optional[SessionInfo]:
        if len(self.sessions) >= settings.max_browsers:
            return None
        
        if not session_id:
            session_id = str(uuid.uuid4())
        
        if session_id in self.sessions:
            return None
        
        port = port_allocator.get_available_port()
        if not port:
            return None
        
        session = BrowserSession(session_id, port)
        
        if await session.start():
            session_info = SessionInfo(
                session_id=session.session_id,
                port=session.port,
                cdp_endpoint=session.cdp_endpoint,
                cdp_websocket_url=session.cdp_websocket_url,
                cdp_discovery_url=f"http://localhost:{session.port}/json",
                created_at=session.created_at,
                uptime_seconds=session.uptime_seconds,
                status=session.status,
                video_preview_link=None
            )
            await repo.create(session_info)
            self.sessions[session_id] = session
            return session_info
        
        return None
    
    async def release_session(self, repo: SessionRepository, session_id: str) -> bool:
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        await session.cleanup()
        await repo.delete(session_id)
        del self.sessions[session_id]
        return True
    
    async def get_session(self, repo: SessionRepository, session_id: str) -> Optional[SessionInfo]:
        return await repo.get(session_id)
    
    async def list_sessions(self, repo: SessionRepository) -> List[SessionInfo]:
        return await repo.list_all()
    
    def get_uptime_seconds(self) -> int:
        return int((datetime.now() - self.start_time).total_seconds())
    
    async def cleanup_all(self, repo: SessionRepository):
        for session in list(self.sessions.values()):
            await session.cleanup()
        self.sessions.clear()
        # Optional: clear DB
        # But better to let user manage via /cleanup
    
    async def create_multiple_browsers(self, repo: SessionRepository, count: int = 5) -> Dict:
        try:
            browsers = []
            ports = list(range(settings.port_start, settings.port_start + count))
            
            for i, port in enumerate(ports):
                try:
                    if not port_allocator.is_port_available(port):
                        browsers.append({
                            "browser_number": i + 1,
                            "host_port": port,
                            "error": "Port not available",
                            "status": "failed"
                        })
                        continue
                    
                    session_id = f"browser-{port}"
                    session = BrowserSession(session_id, port)
                    
                    if await session.start():
                        self.sessions[session_id] = session
                        session_info = SessionInfo(
                            session_id=session_id,
                            port=port,
                            cdp_endpoint=session.cdp_endpoint,
                            cdp_websocket_url=session.cdp_websocket_url,
                            cdp_discovery_url=f"http://localhost:{port}/json",
                            created_at=session.created_at,
                            uptime_seconds=session.uptime_seconds,
                            status=session.status,
                            video_preview_link=None
                        )
                        await repo.create(session_info)
                        browsers.append({
                            "browser_number": i + 1,
                            "session_id": session_id,
                            "container_id": session.container_id,
                            "host_port": port,
                            "browser_id": session.browser_id,
                            "ws_url": session.cdp_websocket_url,
                            "status": "created"
                        })
                    else:
                        browsers.append({
                            "browser_number": i + 1,
                            "host_port": port,
                            "error": "Failed to start browser",
                            "status": "failed"
                        })
                        
                except Exception as e:
                    browsers.append({
                        "browser_number": i + 1,
                        "host_port": port,
                        "error": str(e),
                        "status": "failed"
                    })
            
            return {
                "message": f"Created {len([b for b in browsers if b['status'] == 'created'])} browsers",
                "browsers": browsers,
                "total_ports": ports
            }
            
        except Exception as e:
            return {"error": str(e)}


# Global browser manager instance
browser_manager = BrowserManager()