# Server Shutdown Guide

The `serve_viewer.py` server now supports clean shutdown with proper socket release, preventing "Address already in use" errors.

## Shutdown Methods

### 1. Ctrl+C (Keyboard Interrupt)
The traditional method still works and now performs a clean shutdown:
```bash
# In the terminal running the server
Press Ctrl+C
```

### 2. API Endpoint
Trigger shutdown programmatically or from a browser:
```bash
curl http://localhost:8000/api/shutdown
```

Or visit in your browser:
```
http://localhost:8000/api/shutdown
```

### 3. Shutdown Button Page
A dedicated HTML page with a shutdown button:
```
http://localhost:8000/shutdown_button.html
```

### 4. Kill Command
Use the system kill command (gracefully handled):
```bash
# Find the process ID
lsof -ti:8000

# Send termination signal
kill <PID>
```

## Features

### Clean Socket Release
- The server properly releases the socket on shutdown
- `allow_reuse_address` is enabled to prevent "Address already in use" errors
- No need to wait for TIME_WAIT state to expire

### Signal Handling
- Handles SIGINT (Ctrl+C) gracefully
- Handles SIGTERM (kill command) gracefully
- Ensures cleanup code runs before exit

### Thread-Safe Shutdown
- API shutdown runs in a separate thread
- Allows the HTTP response to be sent before shutdown
- Prevents connection errors during shutdown

## Testing

Run the test script to verify clean shutdown:
```bash
python3 test_server_shutdown.py
```

This will:
1. Start the server
2. Wait for it to initialize
3. Trigger shutdown via API
4. Verify clean termination

## Implementation Details

### Key Changes
1. **Signal handlers**: Registered for SIGINT and SIGTERM
2. **Global server reference**: Allows shutdown from signal handlers
3. **Socket reuse**: `TCPServer.allow_reuse_address = True`
4. **Shutdown endpoint**: `/api/shutdown` triggers graceful shutdown
5. **Finally block**: Ensures cleanup even on exceptions

### Code Structure
```python
# Signal handler
def signal_handler(signum, frame):
    if server_instance:
        server_instance.shutdown()
    sys.exit(0)

# Main function
def main():
    global server_instance
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        server_instance = httpd
        try:
            httpd.serve_forever()
        finally:
            print("Socket released.")
            server_instance = None
```

## Troubleshooting

### Port Still in Use
If you get "Address already in use" error:
```bash
# Kill any process using port 8000
lsof -ti:8000 | xargs kill -9
```

### Server Won't Stop
If the server doesn't respond to shutdown:
```bash
# Force kill
pkill -9 -f serve_viewer.py
```

## Benefits

1. **No manual cleanup**: Socket is automatically released
2. **Immediate restart**: Can restart server without waiting
3. **Multiple methods**: Choose the most convenient shutdown method
4. **User-friendly**: Clear messages about shutdown options
5. **Production-ready**: Proper signal handling for deployment