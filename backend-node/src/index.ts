import 'dotenv/config';
import express, { Request, Response } from 'express';
import cors from 'cors';
import { handleSendMessage } from './routes/chat';

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors({
  origin: 'http://localhost:3000', // Next.js default port
  credentials: true
}));
app.use(express.json());

// Routes
app.get('/', (req: Request, res: Response) => {
  res.json({ message: 'Hello from Express/TypeScript backend' });
});

app.get('/health', (req: Request, res: Response) => {
  res.json({ status: 'healthy' });
});

// Chat API endpoint
app.post('/api/chat/:id/send', handleSendMessage);

// Start server
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});

