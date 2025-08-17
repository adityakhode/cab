const WebSocket = require('ws');
const http = require('http');

// Create HTTP server for health checks
const server = http.createServer((req, res) => {
  res.writeHead(200);
  res.end('WebSocket Server Running');
});

// Create WebSocket server
const wss = new WebSocket.Server({ server });

wss.on('connection', (ws) => {
  ws.send('Connected to Render WebSocket!');
  
  ws.on('message', (data) => {
    // Broadcast to all clients
    wss.clients.forEach(client => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(`User: ${data}`);
      }
    });
  });
});

// Start server
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => 
  console.log(`Server running on port ${PORT}`));
