# 🦈 SharkBrowser API

A lightweight, cloud-deployable browser automation service that provides programmatic control of headless Chromium sessions via RESTful APIs. Perfect for AWS EC2 deployment with Docker containerization.

## 🎯 Features

- **RESTful API**: Simple HTTP endpoints for browser session management
- **Docker-based**: Each browser runs in isolated containers
- **Chrome DevTools Protocol**: Full CDP WebSocket access for automation
- **Scalable**: Support for multiple concurrent browser sessions
- **EC2 Ready**: Optimized for AWS EC2 deployment
- **Health Monitoring**: Built-in health checks and session monitoring
- **Auto-cleanup**: Automatic container cleanup and resource management

## 🚀 Quick Start

### Prerequisites

- Docker installed
- AWS EC2 instance (Ubuntu recommended)
- Ports 8000 and 9100-9120 available

### Deployment

1. **Clone and deploy**:
```bash
git clone <repolink>
cd Shakbrowser
chmod +x deploy.sh
./deploy.sh
```

2. **Access the API**:
- **API Documentation**: `http://YOUR_EC2_IP:8000/docs`
- **Health Check**: `http://YOUR_EC2_IP:8000/health`

## 📚 API Endpoints

### Session Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/v1/sessions/` | Create a new browser session |
| `GET` | `/v1/sessions/` | List all active sessions |
| `GET` | `/v1/sessions/{session_id}` | Get specific session info |
| `POST` | `/v1/sessions/release` | Release a session |
| `POST` | `/v1/sessions/multiple` | Create 5 browsers at once |
| `POST` | `/v1/sessions/cleanup` | Clean up all sessions |

### Health & Monitoring

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | API health status |

## 🔧 Usage Examples

### Create a Browser Session

```bash
curl -X POST "http://YOUR_EC2_IP:8000/v1/sessions/" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "my-session"}'
```

**Response**:
```json
{
  "session_id": "my-session",
  "port": 9100,
  "cdp_endpoint": "ws://YOUR_EC2_IP:9100",
  "cdp_websocket_url": "ws://YOUR_EC2_IP:9100/devtools/browser/abc123",
  "cdp_discovery_url": "http://YOUR_EC2_IP:9100/json",
  "message": "Session 'my-session' created successfully"
}
```

### List Active Sessions

```bash
curl "http://YOUR_EC2_IP:8000/v1/sessions/"
```

### Create Multiple Browsers

```bash
curl -X POST "http://YOUR_EC2_IP:8000/v1/sessions/multiple"
```

### Release a Session

```bash
curl -X POST "http://YOUR_EC2_IP:8000/v1/sessions/release" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "my-session"}'
```

## 🌐 Chrome DevTools Protocol Integration

Each browser session provides a WebSocket URL for direct CDP access:

```javascript
// Connect to browser via WebSocket
const ws = new WebSocket('ws://YOUR_EC2_IP:9100/devtools/browser/abc123');



## 🐳 Docker Architecture

### Main API Container
- **Image**: `sharkbrowser-api`
- **Ports**: 8000 (API), 9100-9120 (Browser sessions)
- **Features**: FastAPI server, Docker client, session management

### Browser Containers
- **Image**: `chromium-cdp`
- **Port**: 9222 (mapped to host ports 9100-9120)
- **Features**: Headless Chromium with CDP enabled

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_BROWSERS` | 20 | Maximum concurrent sessions |
| `PORT_START` | 9100 | Starting port for browser sessions |
| `PORT_END` | 9120 | Ending port for browser sessions |
| `HOST` | 0.0.0.0 | API server host |
| `PORT` | 8000 | API server port |

### Port Range
- **API Port**: 8000
- **Browser Ports**: 9100-9120 (21 ports available)
- **Max Sessions**: 20 (configurable)

## 🔍 Monitoring & Debugging

### Health Check Response
```json
{
  "status": "healthy",
  "timestamp": "2025-01-27T16:48:09.701584",
  "uptime_seconds": 70,
  "active_sessions": 3,
  "max_sessions": 20,
  "available_ports": 18
}
```

### Container Logs
```bash
# Check API logs
docker logs sharkbrowser

# Check specific browser container
docker logs browser-my-session
```

### Debug Information
```bash
# Get Docker container status
docker ps


## 🚨 Troubleshooting

### Common Issues

1. **Port Already Allocated**
   ```bash
   # Clean up containers
   docker container prune -f
   docker system prune -f
   ```

2. **Permission Denied**
   ```bash
   # Add user to docker group
   sudo usermod -aG docker $USER
   newgrp docker
   ```

3. **Container Restarting**
   ```bash
   # Check logs for errors
   docker logs sharkbrowser
   
   # Rebuild if needed
   docker build -t sharkbrowser-api .
   ```

### Performance Tips

- **Resource Limits**: Monitor EC2 instance resources
- **Session Cleanup**: Regularly clean up unused sessions
- **Port Management**: Use the cleanup endpoint to free ports
- **Health Monitoring**: Monitor the health endpoint

## 🔒 Security Considerations

- **Network Security**: Configure EC2 security groups properly
- **Container Isolation**: Each browser runs in isolated containers
- **Resource Limits**: Built-in session limits prevent resource exhaustion
- **Auto-cleanup**: Containers auto-remove when stopped

## 📈 Scaling

### Horizontal Scaling
- Deploy multiple API instances behind a load balancer
- Use different port ranges for each instance

### Vertical Scaling
- Increase EC2 instance size
- Adjust `MAX_BROWSERS` configuration
- Expand port range if needed

---

**Made with ❤️ for browser automation on AWS EC2**
