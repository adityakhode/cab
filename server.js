const WebSocket = require('ws');
const http = require('http');

// HTTP server for health checks
const server = http.createServer((req, res) => {
  res.writeHead(200);
  res.end('WhatsApp-like WebSocket Server');
});

// WebSocket server
const wss = new WebSocket.Server({ server });
const users = new Map(); // Stores all connected users

wss.on('connection', (ws) => {
  let username = null;

  // When a new user joins
  ws.on('message', (data) => {
    const message = JSON.parse(data);

    if (message.type === 'join') {
      username = message.username;
      users.set(username, ws);
      
      // Notify all users about the new connection
      broadcast({
        type: 'notification',
        text: `${username} joined the chat`,
        users: Array.from(users.keys())
      });
    }

    // When a user sends a message
    else if (message.type === 'message') {
      broadcast({
        type: 'message',
        username: username,
        text: message.text,
        timestamp: new Date().toLocaleTimeString()
      });
    }

    // When someone is typing
    else if (message.type === 'typing') {
      broadcast({
        type: 'typing',
        username: username,
        isTyping: message.isTyping
      });
    }
  });

  // When a user disconnects
  ws.on('close', () => {
    if (username) {
      users.delete(username);
      broadcast({
        type: 'notification',
        text: `${username} left the chat`,
        users: Array.from(users.keys())
      });
    }
  });
});

// Broadcast to all connected clients
function broadcast(message) {
  wss.clients.forEach(client => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(JSON.stringify(message));
    }
  });
}

// Start server
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => console.log(`Server running on ${PORT}`));
