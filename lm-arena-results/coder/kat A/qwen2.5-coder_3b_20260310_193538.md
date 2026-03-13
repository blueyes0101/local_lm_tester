# Model: qwen2.5-coder:3b
**Test Date:** 2026-03-10 20:53:23
**Total Questions:** 12

---

## Question 1
**Q:** You are designing a REST API for a multi-tenant SaaS project management tool.
Entities: Workspace, Project, Task, User, Comment.

Rules:
- A user can belong to multiple workspaces
- Projects belong to a workspace
- Tasks belong to a project and can be assigned to users
- Comments belong to tasks

Design the complete API:
1. Define all endpoints (method + path) following REST conventions
2. Show request/response JSON shapes for: create task, update task status, list tasks with filters (assignee, status, due date), add comment
3. Define your error response format — be consistent across all endpoints
4. How do you handle pagination? Show the response envelope
5. Which endpoints need which HTTP status codes and when?

Do NOT write server code — this is a design question. Clarity and consistency matter most.

**A:**
**API Design for a Multi-Tenant SaaS Project Management Tool**

### 1. Endpoints Design

#### a. Workspace API

- **Create Workspace:**
  - **Method:** POST
  - **Path:** `/api/workspaces`
  - **Request Body:** `{ "name": "Workspace Name", "description": "Description of the workspace" }`
  - **Response:** `{ "workspace_id": "12345", "name": "Workspace Name", "description": "Description of the workspace" }`

#### b. Project API

- **Create Project:**
  - **Method:** POST
  - **Path:** `/api/projects`
  - **Request Body:** `{ "workspace_id": "12345", "name": "Project Name", "description": "Description of the project" }`
  - **Response:** `{ "project_id": "67890", "workspace_id": "12345", "name": "Project Name", "description": "Description of the project" }`

#### c. Task API

- **Create Task:**
  - **Method:** POST
  - **Path:** `/api/tasks`
  - **Request Body:** `{ "project_id": "67890", "assignee": "user_id

*Response time: 3.9s*

---

## Question 2
**Q:** Implement the following endpoint in Node.js + Express + TypeScript:

PATCH /workspaces/:workspaceId/tasks/:taskId

Requirements:
- Partial update: only fields provided in the body should change
- Allowed fields: title (string, 1-200 chars), status (todo|in_progress|done|cancelled), assignee_id (integer or null), due_date (ISO8601 or null)
- Validate that workspaceId and taskId are valid integers
- Validate that the task belongs to the workspace (return 404 if not)
- Validate that assignee_id (if provided) is a member of the workspace
- Return 400 with field-level validation errors if validation fails
- Return 409 if trying to set status to 'cancelled' when task has open subtasks
- Use Zod for validation
- Write the complete handler + validation schema + error middleware
- Write 4 unit tests covering: success, validation error, 404, 409

**A:**
To implement the `/workspaces/:workspaceId/tasks/:taskId` endpoint in Node.js + Express + TypeScript, we need to follow these steps:

1. Set up the Express server and define the route.
2. Use Zod for validation of the request body.
3. Implement the logic to update the task partially.
4. Write error middleware to handle validation errors, 404s, and 409s.
5. Write unit tests using a testing framework like Jest.

Here's a complete implementation:

### Step 1: Set Up the Express Server

First, ensure you have Node.js and npm installed. Create a new directory for your project and initialize it:

```bash
mkdir task-api
cd task-api
npm init -y
```

Install the required packages:

```bash
npm install express zod @types/express @types/zod
```

Create the main server file `server.ts`:

```typescript
import express from 'express';
import { ZodError } from 'zod';
import { v4 as uuidv4 } from 'uuid';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

const app = express();
app.use(express.json());

// Define validation schemas
const TaskSchema = Zod.object({
  title: Zod.string().min(1).max(200),
  status: Zod.enum(['todo', 'in_progress', 'done', 'cancelled']),
  assignee_id: Zod.union([Zod.number(), Zod.null()]),
  due_date: Zod.string().optional().nullable(),
});

// Define the task endpoint
app.patch('/workspaces/:workspaceId/tasks/:taskId', async (req, res) => {
  const { workspaceId, taskId } = req.params;
  const updatedTask: Partial<Task> = req.body;

  try {
    // Validate the input
    const validationError = TaskSchema.safeParse(updatedTask);
    if (!validationError.success) {
      return res.status(400).json({ errors: validationError.issues });
    }

    // Validate that workspaceId and taskId are valid integers
    if (!Number.isInteger(Number(workspaceId)) || !Number.isInteger(Number(taskId))) {
      return res.status(400).json({ error: 'Invalid workspaceId or taskId' });
    }

    // Find the task
    const task = await prisma.task.findUnique({
      where: {
        id: taskId,
      },
      include: {
        workspace: true,
        assignee: true,
      },
    });

    if (!task) {
      return res.status(404).json({ error: 'Task not found' });
    }

    // Validate that the task belongs to the workspace
    if (task.workspaceId !== Number(workspaceId)) {
      return res.status(404).json({ error: 'Task does not belong to this workspace' });
    }

    // Validate assignee_id if provided
    if (updatedTask.assignee_id !== null) {
      if (updatedTask.assignee_id !== task.assignee?.id) {
        const member = await prisma.member.findUnique({
          where: {
            userId: updatedTask.assignee_id,
            workspaceId: Number(workspaceId),
          },
        });

        if (!member) {
          return res.status(400).json({ error: 'Invalid assignee_id' });
        }
      }
    }

    // Check for open subtasks to prevent cancelling
    const openSubtasks = await prisma.task.findMany({
      where: {
        taskId,
        status: { not: 'cancelled' },
      },
    });

    if (updatedTask.status === 'cancelled' && openSubtasks.length > 0) {
      return res.status(409).json({ error: 'Cannot cancel task with open subtasks' });
    }

    // Update the task
    const updated = await prisma.task.update({
      where: {
        id: taskId,
      },
      data: updatedTask,
    });

    res.json(updated);
  } catch (error) {
    // Handle any unexpected errors
    if (error instanceof ZodError) {
      return res.status(400).json({ errors: error.issues });
    }
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Error middleware
app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  if (err instanceof ZodError) {
    return res.status(400).json({ errors: err.issues });
  }
  if (err.statusCode && err.message) {
    return res.status(err.statusCode).json({ error: err.message });
  }
  return res.status(500).json({ error: 'Internal server error' });
});

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
```

### Step 2: Define the Validation Schema

The `TaskSchema` uses Zod to define the validation rules for the task fields. It ensures that the `title` is between 1 and 200 characters, `status` is one of the allowed values, and `assignee_id` is either a number or `null`.

### Step 3: Implement the Task Endpoint

The `/workspaces/:workspaceId/tasks/:taskId` endpoint checks the validity of the input, validates the workspace and task, and updates the task if all checks pass.

### Step 4: Write Error Middleware

The error middleware handles `ZodError` instances, 400 errors, and any unexpected errors, returning appropriate JSON responses.

### Step 5: Write Unit Tests

Create a `tasks.test.ts` file to write unit tests using Jest:

```typescript
import { describe, it, expect } from 'jest';
import { PrismaClient } from '@prisma/client';
import { TaskSchema } from './server';

describe('Task API', () => {
  let prisma: PrismaClient;

  beforeAll(async () => {
    prisma = new PrismaClient();
    await prisma.$connect();
  });

  afterAll(async () => {
    await prisma.$disconnect();
  });

  describe('/workspaces/:workspaceId/tasks/:taskId', () => {
    it('should update a task', async () => {
      const taskId = uuidv4();
      const workspaceId = uuidv4();
      const task = await prisma.task.create({
        data: {
          id: taskId,
          title: 'Test Task',
          status: 'todo',
          assignee_id: null,
          due_date: new Date().toISOString(),
          workspaceId,
        },
      });

      const updatedTask = await prisma.task.update({
        where: {
          id: taskId,
        },
        data: {
          title: 'Updated Task',
          status: 'in_progress',
          assignee_id: 1,
          due_date: new Date().toISOString(),
        },
      });

      expect(updatedTask.title).toBe('Updated Task');
      expect(updatedTask.status).toBe('in_progress');
      expect(updatedTask.assignee_id).toBe(1);
    });

    it('should return 400 for invalid input', async () => {
      const taskId = uuidv4();
      const workspaceId = uuidv4();
      const task = await prisma.task.create({
        data: {
          id: taskId,
          title: 'Test Task',
          status: 'todo',
          assignee_id: null,
          due_date: new Date().toISOString(),
          workspaceId,
        },
      });

      const response = await fetch(`/workspaces/${workspaceId}/tasks/${taskId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: 123, // Invalid title
        }),
      });

      expect(response.status).toBe(400);
      const { errors } = await response.json();
      expect(errors[0].message).toBe('Title must be a string');
    });

    it('should return 404 for invalid workspaceId', async () => {
      const taskId = uuidv4();
      const workspaceId = uuidv4();
      const task = await prisma.task.create({
        data: {
          id: taskId,
          title: 'Test Task',
          status: 'todo',
          assignee_id: null,
          due_date: new Date().toISOString(),
          workspaceId,
        },
      });

      const response = await fetch(`/workspaces/invalidWorkspaceId/tasks/${taskId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: 'Updated Task',
        }),
      });

      expect(response.status).toBe(404);
      const { error } = await response.json();
      expect(error).toBe('Workspace not found');
    });

    it('should return 404 for invalid taskId', async () => {
      const taskId = uuidv4();
      const workspaceId = uuidv4();
      const task = await prisma.task.create({
        data: {
          id: taskId,
          title: 'Test Task',
          status: 'todo',
          assignee_id: null,
          due_date: new Date().toISOString(),
          workspaceId,
        },
      });

      const response = await fetch(`/workspaces/${workspaceId}/tasks/invalidTaskId`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: 'Updated Task',
        }),
      });

      expect(response.status).toBe(404);
      const { error } = await response.json();
      expect(error).toBe('Task not found');
    });

    it('should return 404 for task not belonging to workspace', async () => {
      const taskId = uuidv4();
      const workspaceId = uuidv4();
      const task = await prisma.task.create({
        data: {
          id: taskId,
          title: 'Test Task',
          status: 'todo',
          assignee_id: null,
          due_date: new Date().toISOString(),
          workspaceId,
        },
      });

      const response = await fetch(`/workspaces/otherWorkspaceId/tasks/${taskId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: 'Updated Task',
        }),
      });

      expect(response.status).toBe(404);
      const { error } = await response.json();
      expect(error).toBe('Task does not belong to this workspace');
    });

    it('should return 400 for invalid assignee_id', async () => {
      const taskId = uuidv4();
      const workspaceId = uuidv4();
      const task = await prisma.task.create({
        data: {
          id: taskId,
          title: 'Test Task',
          status: 'todo',
          assignee_id: null,
          due_date: new Date().toISOString(),
          workspaceId,
        },
      });

      const response = await fetch(`/workspaces/${workspaceId}/tasks/${taskId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: 'Updated Task',
          assignee_id: 'invalidId', // Invalid assignee_id
        }),
      });

      expect(response.status).toBe(400);
      const { error } = await response.json();
      expect(error).toBe('Invalid assignee_id');
    });

    it('should return 409 for canceling a task with open subtasks', async () => {
      const taskId = uuidv4();
      const workspaceId = uuidv4();
      const task = await prisma.task.create({
        data: {
          id: taskId,
          title: 'Test Task',
          status: 'todo',
          assignee_id: null,
          due_date: new Date().toISOString(),
          workspaceId,
        },
      });

      const subtaskId = uuidv4();
      await prisma.task.create({
        data: {
          id: subtaskId,
          title: 'Subtask',
          status: 'todo',
          assignee_id: null,
          due_date: new Date().toISOString(),
          workspaceId,
          parentId: taskId,
        },
      });

      const response = await fetch(`/workspaces/${workspaceId}/tasks/${taskId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          status: 'cancelled',
        }),
      });

      expect(response.status).toBe(409);
      const { error } = await response.json();
      expect(error).toBe('Cannot cancel task with open subtasks');
    });
  });
});
```

### Step 6: Run the Tests

Install Jest and add it to your project:

```bash
npm install jest @types/jest
npx tsc --init
```

Create a `jest.config.js` file to configure Jest:

```javascript
module.exports = {
  testEnvironment: 'node',
  transform: {
    '^.+\\.ts?$': 'ts-jest',
  },
  testMatch: ['**/*.test.(ts|js)'],
};
```

Run the tests:

```bash
npm test
```

This setup provides a complete implementation of the `/workspaces/:workspaceId/tasks/:taskId` endpoint with validation, error handling, and unit tests.

*Response time: 31.9s*

---

## Question 3
**Q:** Implement a complete authentication system in Node.js + Express + TypeScript:

1. POST /auth/register — email + password, hash password with bcrypt (cost factor 12), return user object (no password)
2. POST /auth/login — validate credentials, return access token (15min expiry) + refresh token (7 days), store refresh token in httpOnly cookie
3. GET /auth/me — protected route, return current user from token
4. JWT payload should contain: userId, email, role, iat, exp
5. Write authMiddleware that validates the access token and attaches user to req.user
6. What happens if someone sends an expired token? Show the exact error response.
7. Why httpOnly cookie for refresh token instead of localStorage? Explain the security reasoning.

**A:**
To implement a complete authentication system in Node.js using Express and TypeScript, we'll follow the steps outlined in your request. Below is a detailed implementation, including the necessary modules, configuration, and middleware.

### Step 1: Set Up Your Project

First, ensure you have the necessary dependencies installed:

```bash
npm init -y
npm install express @types/express jsonwebtoken bcryptjs dotenv
```

### Step 2: Create the Server

Create a file named `server.ts` and set up the basic server configuration:

```typescript
import express from 'express';
import bodyParser from 'body-parser';
import cors from 'cors';
import dotenv from 'dotenv';
import mongoose from 'mongoose';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(bodyParser.json());
app.use(cors());

// Connect to MongoDB
mongoose.connect(process.env.MONGO_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
});

// Example User model
const userSchema = new mongoose.Schema({
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true },
  role: { type: String, default: 'user' },
});

const User = mongoose.model('User', userSchema);

// Import other routes and middleware
import authRoutes from './routes/auth';

// Use authRoutes
app.use('/auth', authRoutes);

// Start the server
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
```

### Step 3: Implement User Authentication

Create a file named `routes/auth.ts` to handle user registration and login:

```typescript
import express from 'express';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { Request, Response } from 'express';
import User from '../models/User';

const router = express.Router();

// Register route
router.post('/register', async (req: Request, res: Response) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ error: 'Email and password are required' });
    }

    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(400).json({ error: 'Email already exists' });
    }

    const salt = await bcrypt.genSalt(12);
    const hashedPassword = await bcrypt.hash(password, salt);

    const user = new User({ email, password: hashedPassword });
    await user.save();

    res.status(201).json({ id: user.id, email: user.email, role: user.role });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Something went wrong' });
  }
});

// Login route
router.post('/login', async (req: Request, res: Response) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ error: 'Email and password are required' });
    }

    const user = await User.findOne({ email });
    if (!user) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const payload = { userId: user.id, email: user.email, role: user.role };

    const accessToken = jwt.sign(payload, process.env.ACCESS_TOKEN_SECRET, { expiresIn: '15m

*Response time: 8.7s*

---

## Question 4
**Q:** Continuing from the previous auth system:

1. POST /auth/refresh — use the refresh token from cookie to issue a new access token. Rotate the refresh token (issue new one, invalidate old one).
2. POST /auth/logout — invalidate the refresh token, clear the cookie
3. Implement refresh token rotation with a Redis-based token store (show the Redis data structure and TTL strategy)
4. How do you handle the case where a refresh token is used twice? (token reuse detection) — implement it
5. A user changes their password — how do you invalidate ALL their existing sessions? Implement it.
6. What is the difference between token blacklisting and token rotation? When would you use each?

**A:**
Let's continue implementing the authentication system with the specified requirements:

### 1. POST /auth/refresh — use the refresh token from cookie to issue a new access token. Rotate the refresh token (issue new one, invalidate old one).

To implement the refresh token rotation, we will use Redis as a token store. Redis will store the refresh token and access token with a TTL (Time To Live). When a refresh token is used, it will be invalidated, and a new access token will be issued.

**Redis Data Structure:**

- **Key:** `refresh_token:<token>`
- **Value:** `{access_token:<token>, last_used_time:<timestamp>}`

**TTL Strategy:**

- Set the TTL for each refresh token to a reasonable time (e.g., 1 hour).
- When a refresh token is used, update the last_used_time and set a new TTL for the refresh token.

**Implementation:**

```python
import redis
from datetime import datetime, timedelta

# Initialize Redis connection
r = redis.Redis(host='localhost', port=6379, db=0)

def refresh_token(token):
    refresh_token_key = f'refresh_token:{token}'
    refresh_token_data = r.get(refresh_token_key)

    if not refresh_token_data:
        return {'error': 'Invalid refresh token'}

    access_token = refresh_token_data.decode('utf-8')
    data = json.loads(access_token)

    # Rotate the refresh token
    new_refresh_token = generate_refresh_token()
    r.setex(refresh_token_key, 3600, f'{{access_token:"{new_refresh_token}", last_used_time:"{datetime.now().isoformat()}"}}')
    r.delete(refresh_token_key)

    return {'access_token': new_refresh_token}

def generate_refresh_token():
    # Implement refresh token generation logic
    pass
```

### 2. POST /auth/logout — invalidate the refresh token, clear the cookie

To invalidate the refresh token and clear the cookie, we will remove the refresh token from Redis and set the cookie to expire.

**Implementation:**

```python
def logout(token):
    refresh_token_key = f'refresh_token:{token}'
    r.delete(refresh_token_key)
    # Clear the cookie
    response = make_response('Logged out successfully')
    response.set_cookie('refresh_token', '', expires=0)
    return response
```

### 3. Implement refresh token rotation with a Redis-based token store (show the Redis data structure and TTL strategy)

We have already discussed the Redis data structure and TTL strategy in the previous point.

### 4. How do you handle the case where a refresh token is used twice? (token reuse detection)

To detect token reuse, we can track the last_used_time for each refresh token and compare it with the current time. If the last_used_time is within a certain threshold (e.g., 15 minutes), we can consider the token as reused.

**Implementation:**

```python
def is_token_reused(token):
    refresh_token_key = f'refresh_token:{token}'
    refresh_token_data = r.get(refresh_token_key)

    if not refresh_token_data:
        return False

    data = json.loads(refresh_token_data.decode('utf-8'))
    last_used_time = datetime.fromisoformat(data['last_used_time'])
    current_time = datetime.now()
    threshold = timedelta(minutes=15)

    return current_time - last_used_time < threshold
```

### 5. A user changes their password — how do you invalidate ALL their existing sessions? Implement it.

To invalidate all existing sessions when a user changes their password, we need to remove all access tokens associated with that user from Redis. Access tokens are typically stored in the user's session or a database, but for simplicity, let's assume they are stored in Redis.

**Implementation:**

```python
def invalidate_sessions(user_id):
    # Assuming access tokens are stored in Redis with user_id as a prefix
    pattern = f'access_token:{user_id}:*'
    keys = r.scan_iter(match=pattern)
    for key in keys:
        r.delete(key)
```

### 6. What is the difference between token blacklisting and token rotation? When would you use each?

- **Token Blacklisting:** Tokens are permanently invalidated and cannot be used again. It is used when a token is deemed invalid or compromised, such as when a user logs out or when a session is terminated. Token blacklisting is useful for security reasons, such as protecting against replay attacks.
- **Token Rotation:** Tokens are rotated periodically, and the old tokens are invalidated. It is used to maintain the security of tokens and to prevent token reuse. Token rotation is useful for managing token lifetimes and to improve performance by reducing the number of tokens to store.

You would use token blacklisting when a token is compromised or when a session is terminated, and token rotation when you want to manage token lifetimes and reduce the number of tokens to store.

*Response time: 11.5s*

---

## Question 5
**Q:** You are building a DataTable component in React + TypeScript that:
- Accepts columns (definition: key, header, width, sortable, renderCell?) and data (array of objects)
- Supports client-side sorting (click column header to sort asc/desc/none cycle)
- Supports row selection (checkbox per row + select all)
- Supports pagination (page size options: 10, 25, 50)
- Is fully controlled OR uncontrolled (caller chooses)
- Columns with renderCell receive the row data and return a ReactNode (e.g. for action buttons)

Implement the component. Show:
1. The TypeScript interface for props (generic, works for any row type)
2. The complete component implementation
3. A usage example with 3 columns (one with custom renderCell for an action button)
4. How would you memoize this correctly to avoid unnecessary re-renders?

**A:**
Sure! Below is the implementation of the `DataTable` component in React + TypeScript. The component includes the required features and is fully controlled or uncontrolled based on the caller's choice.

### TypeScript Interface for Props

```typescript
import React from 'react';
import { CSSProperties } from 'react';

export interface Column<T> {
  key: string;
  header: string;
  width?: string;
  sortable?: boolean;
  renderCell?: (rowData: T) => React.ReactNode;
}

export interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  controlled?: boolean;
  defaultSortColumn?: string;
  defaultSortOrder?: 'asc' | 'desc' | 'none';
  pageSize?: number;
  onPageChange?: (page: number) => void;
  onRowSelect?: (row: T) => void;
  onRowSelectAll?: (selected: boolean) => void;
}

export interface DataTableState<T> {
  sortBy: string;
  sortOrder: 'asc' | 'desc' | 'none';
  currentPage: number;
  selectedRows: T[];
}
```

### Complete Component Implementation

```tsx
import React, { useState, useEffect, useMemo } from 'react';
import './DataTable.css'; // Example CSS file for styling

interface DataTable<T> {
  data: T[];
  columns: Column<T>[];
  controlled?: boolean;
  defaultSortColumn?: string;
  defaultSortOrder?: 'asc' | 'desc' | 'none';
  pageSize?: number;
  onPageChange?: (page: number) => void;
  onRowSelect?: (row: T) => void;
  onRowSelectAll?: (selected: boolean) => void;
}

interface DataTableState<T> {
  sortBy: string;
  sortOrder: 'asc' | 'desc' | 'none';
  currentPage: number;
  selectedRows: T[];
}

const DataTable = <T extends {}>({
  data,
  columns,
  controlled = false,
  defaultSortColumn,
  defaultSortOrder = 'asc',
  pageSize = 10,
  onPageChange,
  onRowSelect,
  onRowSelectAll,
}: DataTable<T>) => {
  const [state, setState] = useState<DataTableState<T>>(() => ({
    sortBy: defaultSortColumn || '',
    sortOrder: defaultSortOrder,
    currentPage: 1,
    selectedRows: [],
  }));

  // Memoize data for performance
  const memoizedData = useMemo(() => [...data], [data]);

  // Sorting logic
  const sortedData = useMemo(() => {
    if (!state.sortBy || state.sortOrder === 'none') return memoizedData;

    return [...memoizedData].sort((a, b) => {
      if (typeof a[state.sortBy] === 'string' && typeof b[state.sortBy] === 'string') {
        return a[state.sortBy].localeCompare(b[state.sortBy]);
      } else if (typeof a[state.sortBy] === 'number' && typeof b[state.sortBy] === 'number') {
        return a[state.sortBy] - b[state.sortBy];
      }
      return 0;
    });

    return sortedData;
  }, [state.sortBy, state.sortOrder, memoizedData]);

  // Pagination logic
  const startIndex = (state.currentPage - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const paginatedData = sortedData.slice(startIndex, endIndex);

  // Handle row selection
  const handleRowSelect = (row: T) => {
    if (onRowSelect) {
      onRowSelect(row);
    }

    setState(prevState => ({
      ...prevState,
      selectedRows: prevState.selectedRows.includes(row)
        ? prevState.selectedRows.filter(r => r !== row)
        : [...prevState.selectedRows, row],
    }));
  };

  const handleRowSelectAll = (selected: boolean) => {
    if (onRowSelectAll) {
      onRowSelectAll(selected);
    }

    setState(prevState => ({
      ...prevState,
      selectedRows: selected ? data : [],
    }));
  };

  // Handle page change
  const handlePageChange = (page: number) => {
    if (onPageChange) {
      onPageChange(page);
    }

    setState(prevState => ({ ...prevState, currentPage: page }));
  };

  // Handle sorting
  const handleSort = (columnKey: string) => {
    const currentSortOrder = state.sortBy === columnKey ? state.sortOrder : 'asc';
    const newSortOrder = currentSortOrder === 'asc' ? 'desc' : currentSortOrder === 'desc' ? 'none' : 'asc';

    setState(prevState => ({
      ...prevState,
      sortBy: columnKey,
      sortOrder: newSortOrder,
    }));
  };

  return (
    <div className="dataTable">
      <div className="header">
        {columns.map(column => (
          <div key={column.key} className="header-cell" onClick={() => handleSort(column.key)}>
            {column.header}
            {column.sortable && (
              <span className={`sort-icon ${state.sortBy === column.key ? state.sortOrder : 'none'}`}>
                {state.sortOrder === 'asc' ? '↑' : state.sortOrder === 'desc' ? '↓' : ''}
              </span>
            )}
          </div>
        ))}
      </div>
      <div className="body">
        {paginatedData.map((row, index) => (
          <div key={index} className="row" onClick={() => handleRowSelect(row)}>
            {columns.map(column => (
              <div key={column.key} className="cell">
                {column.renderCell ? column.renderCell(row) : row[column.key]}
              </div>
            ))}
          </div>
        ))}
      </div>
      <div className="footer">
        <div className="pagination">
          <button onClick={() => handlePageChange(state.currentPage - 1)} disabled={state.currentPage === 1}>
            Previous
          </button>
          <span>Page {state.currentPage} of {Math.ceil(data.length / pageSize)}</span>
          <button onClick={() => handlePageChange(state.currentPage + 1)} disabled={state.currentPage === Math.ceil(data.length / pageSize)}>
            Next
          </button>
        </div>
        <div className="select-all">
          <input type="checkbox" checked={state.selectedRows.length === data.length} onChange={e => handleRowSelectAll(e.target.checked)} />
          Select All
        </div>
      </div>
    </div>
  );
};

export default DataTable;
```

### Usage Example

```tsx
import React from 'react';
import DataTable from './DataTable';

const Example = () => {
  const data = [
    { id: 1, name: 'Alice', age: 25, action: <button onClick={() => console.log('Edit')}>Edit</button> },
    { id: 2, name: 'Bob', age: 30, action: <button onClick={() => console.log('Delete')}>Delete</button> },
    { id: 3, name: 'Charlie', age: 35, action: <button onClick={() => console.log('Edit')}>Edit</button> },
    // Add more data as needed
  ];

  const columns = [
    { key: 'id', header: 'ID', width: '10%' },
    { key: 'name', header: 'Name', width: '30%' },
    { key: 'age', header: 'Age', width: '20%', sortable: true },
    { key: 'action', header: 'Action', renderCell: row => row.action },
  ];

  return (
    <div>
      <h1>Data Table Example</h1>
      <DataTable
        data={data}
        columns={columns}
        defaultSortColumn="name"
        defaultSortOrder="asc"
        pageSize={10}
        onRowSelect={row => console.log(`Row selected: ${row.name}`)}
        onRowSelectAll={selected => console.log(`Select all: ${selected ? 'Selected' : 'Deselected'}`)}
      />
    </div>
  );
};

export default Example;
```

### Memoization

To memoize the `DataTable` component correctly, you should use the `useMemo` hook to memoize the data and the sorting result. This ensures that the component only re-renders when the dependencies change. Here’s how you can do it:

```tsx
import React, { useState, useEffect, useMemo } from 'react';

// ... (rest of the DataTable component)

const DataTable = <T extends {}>({
  // ... (rest of the props)
}: DataTable<T>) => {
  // ... (rest of the state and logic)

  // Memoize data and sorting result
  const memoizedData = useMemo(() => [...data], [data]);
  const sortedData = useMemo(() => {
    // ... (rest of the sorting logic)
  }, [state.sortBy, state.sortOrder, memoizedData]);

  // ... (rest of the component logic)

  return (
    // ... (rest of the component JSX)
  );
};

export default DataTable;
```

By using `useMemo`, you ensure that the `DataTable` component does not re-render unnecessarily when the data or sorting configuration changes.

*Response time: 21.7s*

---

## Question 6
**Q:** You are building a search feature:
- User types in a search box
- After 300ms debounce, fetch results from GET /api/search?q=...
- Show loading spinner during fetch
- Show "No results" if empty array returned
- Show error message if fetch fails (with retry button)
- Cancel in-flight requests when a new search starts
- Cache results: if user types the same query again within 5 minutes, use cached result
- URL should stay in sync: ?q=searchterm (browser back/forward should work)

Implement this in React using hooks only (no external state library). Show:
1. Custom hook useSearch(query: string) that handles fetch, debounce, cache, cancellation
2. The SearchPage component using this hook
3. URL sync implementation
4. Why is cancelling in-flight requests important here? What bug does it prevent?

**A:**
To implement the search feature as described, we'll use custom hooks to manage the search logic, including debounce, caching, and URL synchronization. Here's how you can achieve this using React hooks only:

### Step 1: Create a Custom Hook `useSearch`

```javascript
import { useState, useEffect, useCallback, useRef } from 'react';

const useSearch = (query) => {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);
  const [retry, setRetry] = useState(false);
  const [cachedResults, setCachedResults] = useState(null);
  const cancelTokenSource = useRef(null);

  const fetchResults = useCallback(async (newQuery) => {
    try {
      setLoading(true);
      setError(null);
      cancelTokenSource.current?.abort();

      cancelTokenSource.current = new AbortController();
      const response = await fetch(`/api/search?q=${newQuery}`, {
        signal: cancelTokenSource.current.signal,
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  const debouncedFetchResults = useCallback((query) => {
    const handle = setTimeout(() => fetchResults(query), 300);
    return () => clearTimeout(handle);
  }, [fetchResults]);

  useEffect(() => {
    if (query !== cachedResults?.query) {
      setCachedResults(null);
    }
  }, [query]);

  useEffect(() => {
    if (query && !retry) {
      setCachedResults({ query, results });
    } else if (retry) {
      setRetry(false);
      fetchResults(query);
    }
  }, [query, retry, fetchResults]);

  return {
    loading,
    results,
    error,
    retry,
    fetchResults,
    debouncedFetchResults,
    cachedResults,
    cancelTokenSource,
  };
};

export default useSearch;
```

### Step 2: Implement the `SearchPage` Component

```javascript
import React, { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import useSearch from './useSearch';

const SearchPage = () => {
  const { searchParams } = useSearchParams();
  const { query, loading, results, error, retry, fetchResults, debouncedFetchResults, cachedResults, cancelTokenSource } = useSearch(searchParams.get('q'));

  const handleChange = (e) => {
    const newQuery = e.target.value;
    searchParams.set('q', newQuery);
    history.replaceState(null, '', searchParams.toString());
    debouncedFetchResults(newQuery);
  };

  const handleRetry = () => {
    retry = true;
  };

  const renderResults = () => {
    if (loading) {
      return <div>Loading...</div>;
    }

    if (error) {
      return (
        <div>
          {error.message} <button onClick={handleRetry}>Retry</button>
        </div>
      );
    }

    if (results.length === 0) {
      return <div>No results</div>;
    }

    return (
      <ul>
        {results.map((result) => (
          <li key={result.id}>{result.name}</li>
        ))}
      </ul>
    );
  };

  return (
    <div>
      <input type="text" value={query} onChange={handleChange} placeholder="Search..." />
      {renderResults()}
    </div>
  );
};

export default SearchPage;
```

### Step 3: URL Sync Implementation

The URL sync is handled by `useSearchParams` and `history.replaceState`. This ensures that the search query persists in the URL, allowing users to use browser back and forward to navigate through their search history.

### Step 4: Why is Cancelling In-Flight Requests Important?

Cancelling in-flight requests is important because it prevents a potential memory leak. When a new search is initiated before an in-flight request completes, the previous request would still be running, potentially using resources. Cancelling it ensures that the application doesn't hold onto resources unnecessarily, which can be beneficial for performance and reliability.

*Response time: 10.1s*

---

## Question 7
**Q:** You are using Prisma ORM with PostgreSQL for a blog platform.

Schema:
model User    { id Int @id @default(autoincrement()); email String @unique; posts Post[] }
model Post    { id Int @id; title String; content String; published Boolean @default(false); authorId Int; author User @relation(...); tags Tag[]; comments Comment[]; createdAt DateTime @default(now()) }
model Tag     { id Int @id; name String @unique; posts Post[] }
model Comment { id Int @id; content String; postId Int; post Post @relation(...); authorId Int; author User @relation(...); createdAt DateTime @default(now()) }

1. Write a Prisma query that fetches the 10 most recent published posts, including: author name, tag names, comment count (not the comments themselves). No N+1 queries.
2. Write a migration scenario: you need to add a slug field to Post — unique, non-nullable, but the table already has 10M rows. How do you do this safely without downtime?
3. A query is slow: findMany posts filtered by tag name takes 800ms. Walk through how you diagnose and fix this — show the Prisma query, the raw SQL it generates, and what index you add.
4. When would you drop down from Prisma to raw SQL? Give a real example from this schema.

**A:**
1. To fetch the 10 most recent published posts, including the author's name and tag names, while ensuring no N+1 queries, you can use a single query with a join and aggregation. Here's how you can write it in Prisma:

```prisma
query {
  posts(
    where: { published: true },
    orderBy: { createdAt: desc },
    take: 10
  ) {
    title
    content
    author {
      name
    }
    tags {
      name
    }
    commentCount: comments.count
  }
}
```

This query leverages Prisma's `count` aggregate function to calculate the number of comments for each post without hitting the database for each comment.

2. To safely add a `slug` field to the `Post` table without downtime, you can follow these steps:

- **Backup**: Make a backup of your database to ensure you can restore it if something goes wrong.
- **Create a New Column**: Add a new column `slug` to the `Post` table with the desired properties:
  ```sql
  ALTER TABLE Post ADD COLUMN slug TEXT NOT NULL UNIQUE;
  ```
- **Populate the Column**: Write a script to populate the `slug` column. You can use the `id` as a base and append a unique identifier (e.g., a UUID) to make it unique. Here's an example using Node.js and Prisma:
  ```javascript
  import { PrismaClient } from '@prisma/client';

  const prisma = new PrismaClient();

  async function generateSlugs() {
    const posts = await prisma.post.findMany();
    for (const post of posts) {
      const slug = `${post.id}-${Math.random().toString(36).substring(2, 7)}`;
      await prisma.post.update({
        where: { id: post.id },
        data: { slug },
      });
    }
  }

  generateSlugs();
  ```
- **Update Dependencies**: Update your Prisma schema to include the new `slug` field:
  ```prisma
  model Post {
    id Int @id @default(autoincrement());
    title String;
    content String;
    published Boolean @default(false);
    authorId Int;
    author User @relation(...);
    tags Tag[];
    comments Comment[];
    createdAt DateTime @default(now());
    slug String @unique;
  }
  ```
- **Deploy Changes**: Deploy your changes to your application, making sure to handle any potential downtime during the update process.

3. To diagnose and fix the slow query that takes 800ms to find all posts by a specific tag, you can follow these steps:

- **Analyze the Query**: Use Prisma's introspection tools to analyze the query and identify any inefficiencies.
- **Examine the Indexes**: Check if there is an index on the `tags` relation:
  ```prisma
  model Post {
    id Int @id @default(autoincrement());
    title String;
    content String;
    published Boolean @default(false);
    authorId Int;
    author User @relation(...);
    tags Tag[] @index;
    comments Comment[];
    createdAt DateTime @default(now());
    slug String @unique;
  }
  ```
- **Rewrite the Query**: If the index is missing or not being used effectively, you can rewrite the query to use an index. Here's an example:
  ```prisma
  query {
    posts(
      where: { tags: { some: { name: "your-tag-name" } } }
    ) {
      title
      content
      author {
        name
      }
      tags {
        name
      }
      commentCount: comments.count
    }
  }
  ```
- **Optimize the Index**: If the query is still slow, consider optimizing the index. This might involve rebuilding the index or creating a composite index that includes both the `tags` and `name` fields.

4. You would drop down from Prisma to raw SQL in situations where you need fine-grained control over the query execution or when the generated Prisma query is not performing well. For example, if you need to perform a complex query that cannot be expressed using Prisma's query builder, or if you need to execute a query that is not supported by Prisma, you might consider using raw SQL.

Here's an example where you might need to use raw SQL:

```javascript
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function getPostsByAuthorAndTag(authorId: number, tagName: string) {
  const sql = `
    SELECT 
      p.id, p.title, p.content, p.published, p.slug,
      a.name AS author_name,
      COUNT(c.id) AS comment_count
    FROM 
      Post p
    JOIN 
      User a ON p.authorId = a.id
    LEFT JOIN 
      Comment c ON p.id = c.postId
    WHERE 
      p.authorId = ? AND 
      p.tags.name = ?
    GROUP BY 
      p.id, p.title, p.content, p.published, p.slug, a.name, c.id
  `;

  const result = await prisma.$queryRaw<{ id: number, title: string, content: string, published: boolean, slug: string, author_name: string, comment_count: number }>(sql, [authorId, tagName]);

  return result;
}

getPostsByAuthorAndTag(1, 'your-tag-name');
```

This example demonstrates how to execute a raw SQL query using Prisma's `$queryRaw` method to handle complex queries that are not supported by Prisma's query builder.

*Response time: 13.8s*

---

## Question 8
**Q:** You have a full-stack app: React frontend (Vite), Node.js + Express backend, PostgreSQL, Redis.

1. Write a docker-compose.yml for local development with:
   - Hot reload for both frontend and backend
   - PostgreSQL with a named volume (data persists between restarts)
   - Redis
   - Environment variables via .env file
   - Backend waits for PostgreSQL to be healthy before starting (use healthcheck, not depends_on alone)

2. Write a production Dockerfile for the backend (Node.js):
   - Multi-stage build (builder + runtime)
   - Final image runs as non-root user
   - Only production dependencies in final image
   - Image size should be minimized

3. The backend crashes in production (exit code 137). What does this mean and how do you diagnose it?

4. You need to deploy a new version with zero downtime. The database schema changed (additive only — new nullable column). Describe the deployment sequence step by step.

**A:**
### Docker Compose for Local Development

To set up a Docker Compose file for local development, you can use the following configuration:

```yaml
version: '3.8'

services:
  frontend:
    image: vite:latest
    command: ["vite"]
    ports:
      - "3000:3000"
    depends_on:
      - backend
    volumes:
      - ./frontend:/app

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "3001:3001"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/mydb
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - db_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  db:
    image: postgres:latest
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=mydb
    volumes:
      - db_data:/var/lib/postgresql/data

  redis:
    image: redis:latest

volumes:
  db_data:
```

### Production Dockerfile for Backend

Here's a production Dockerfile for the backend using a multi-stage build:

```dockerfile
# Stage 1: Builder
FROM node:14-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install --only=production
COPY . .
RUN npm run build

# Stage 2: Runtime
FROM node:14-alpine
WORKDIR /app
COPY --from=builder /app/build .
COPY package*.json ./
RUN npm install --only=production
EXPOSE 3001
USER node
CMD ["node", "server.js"]
```

### Diagnosing the Crash (Exit Code 137)

Exit code 137 typically indicates that the process has been terminated by the operating system due to exceeding memory limits. Here are some steps to diagnose and fix this issue:

1. **Increase Memory Limits**:
   - Check the `docker run` command for the backend service and increase the memory limit, for example:
     ```bash
     docker run -d --memory=4g --memory-reservation=2g -p 3001:3001 backend
     ```

2. **Monitor Resource Usage**:
   - Use tools like `top` or `htop` to monitor the resource usage of the backend container while it is running.
   - Look for any signs of high memory usage or swapping.

3. **Review Logs**:
   - Check the logs of the backend container for any error messages or warnings that might indicate a memory issue.
   - Use `docker logs <container_id>` to view logs.

4. **Profile Memory Usage**:
   - Use a profiling tool like `pm2` or `node --inspect` to profile the memory usage of your application.
   - This can help identify where memory is being consumed.

5. **Optimize Code**:
   - Review your code for any inefficiencies or memory leaks.
   - Optimize database queries, reduce memory footprint, or use more efficient algorithms.

### Deployment Sequence for Database Schema Change

When deploying a new version of your application with a database schema change (additive only, new nullable column), follow these steps:

1. **Create a New Database Schema Migration**:
   - Use a migration tool like `sequelize` or `prisma` to create a migration file for the schema change.

2. **Run the Migration**:
   - Apply the migration to the existing database to ensure the schema is updated.
   - Ensure all data is compatible with the new schema.

3. **Update the Application**:
   - Deploy the new version of the application to a staging environment.
   - Ensure that the new version of the application is compatible with the updated schema.

4. **Test in Staging**:
   - Test the application in the staging environment to ensure that the schema change has no impact on the application.
   - Check for any bugs or issues that arise.

5. **Promote to Production**:
   - Once the staging environment is verified, promote the application to production.
   - Ensure that all production systems are updated to use the new version and the updated schema.

6. **Monitor Post-Deployment**:
   - Monitor the production environment for any issues that arise after the deployment.
   - Use logging and monitoring tools to ensure that everything is working as expected.

By following these steps, you can ensure a smooth and zero-downtime deployment of your application with a database schema change.

*Response time: 11.3s*

---

## Question 9
**Q:** You are building a collaborative document editor (like Google Docs, simplified):
- Multiple users can edit the same document simultaneously
- Each user sees others' cursors in realtime
- Changes are broadcast to all connected clients
- If a user disconnects and reconnects, they get the latest document state

Implement the server side in Node.js using the ws library:
1. Connection handling — how do you associate a WebSocket connection with a user and document?
2. Message protocol — define the message types (JSON) for: join document, text change, cursor move, user left
3. Broadcasting — when user A makes a change, how do you send it to all other users in the same document but NOT back to user A?
4. Reconnection — how do you handle a user rejoining after disconnect?
5. What happens if two users edit the exact same position simultaneously? You don't need to implement OT/CRDT — just explain the problem and name the solution approaches.

Write the core server implementation (connection map, message routing, broadcast logic).

**A:**
To implement a collaborative document editor using Node.js and the `ws` library, we need to handle several key components: connection management, message protocols, broadcasting, reconnection, and concurrent edits.

### 1. Connection Handling

To associate a WebSocket connection with a user and document, we can use a combination of connection IDs and document IDs. Each user can connect to multiple documents, and each document can have multiple users.

```javascript
const WebSocket = require('ws');
const connectionMap = new Map();

function createConnectionId() {
  return Math.random().toString(36).substr(2, 9);
}

function handleConnection(ws) {
  const connectionId = createConnectionId();
  connectionMap.set(connectionId, ws);

  // Handle disconnection
  ws.on('close', () => {
    connectionMap.delete(connectionId);
    // Optionally notify other users that this user has left
  });

  // Handle messages
  ws.on('message', (message) => {
    const data = JSON.parse(message);
    handleMessages(data, connectionId);
  });
}

// Example: Handle messages from clients
function handleMessages(data, connectionId) {
  const { type, documentId, payload } = data;

  switch (type) {
    case 'join-document':
      // Handle user joining a document
      break;
    case 'text-change':
      // Handle text change
      broadcastToDocument(documentId, connectionId, payload);
      break;
    case 'cursor-move':
      // Handle cursor move
      break;
    case 'user-left':
      // Handle user leaving
      break;
    default:
      console.error('Unknown message type:', type);
  }
}
```

### 2. Message Protocol

Define the message types in JSON format:

```json
{
  "type": "join-document",
  "documentId": "document123"
}

{
  "type": "text-change",
  "documentId": "document123",
  "position": 10,
  "text": "Hello"
}

{
  "type": "cursor-move",
  "documentId": "document123",
  "position": 20
}

{
  "type": "user-left",
  "documentId": "document123",
  "connectionId": "connection456"
}
```

### 3. Broadcasting

When a user makes a text change, we need to broadcast the change to all other users in the same document but not to the user who made the change.

```javascript
function broadcastToDocument(documentId, senderConnectionId, payload) {
  const usersInDocument = Array.from(connectionMap.values()).filter((ws) => {
    const data = JSON.parse(ws.readyState === WebSocket.OPEN ? ws.lastMessage : '');
    return data.documentId === documentId;
  });

  usersInDocument.forEach((ws) => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: 'text-change',
        documentId,
        position: payload.position,
        text: payload.text
      }));
    }
  });
}
```

### 4. Reconnection

When a user reconnects, we can use the connection ID to restore their state, typically by sending them the current document state.

```javascript
function handleReconnection(ws) {
  const connectionId = createConnectionId();
  connectionMap.set(connectionId, ws);

  // Handle disconnection
  ws.on('close', () => {
    connectionMap.delete(connectionId);
    // Optionally notify other users that this user has left
  });

  // Handle messages
  ws.on('message', (message) => {
    const data = JSON.parse(message);
    handleMessages(data, connectionId);
  });

  // Restore user's state by sending the current document state
  const documentState = getCurrentDocumentState(connectionId);
  ws.send(JSON.stringify({
    type: 'join-document',
    documentId: documentState.documentId,
    payload: documentState.payload
  }));
}

// Example: Get the current document state for a user
function getCurrentDocumentState(connectionId) {
  // Implement logic to retrieve the current document state for the given connection
}
```

### 5. Concurrent Edits

If two users edit the exact same position simultaneously, the document state can become inconsistent. To handle this, you can implement a versioning system or use optimistic concurrency control (OT/CRDT) techniques. However, since we don't implement OT/CRDT here, you should provide a mechanism to detect and resolve conflicts manually or automatically, such as locking the document during concurrent edits or using timestamps to decide which change takes precedence.

By following these steps, you can implement a basic collaborative document editor server using Node.js and the `ws` library.

*Response time: 11.3s*

---

## Question 10
**Q:** You are building a GraphQL API for a recipe platform. A recipe has: title, ingredients (each with name, amount, unit), steps, author, tags, ratings (each with score and comment).

1. Write the complete GraphQL schema (SDL) for this domain
2. Write resolvers for:
   - Query.recipes(filter: {tag: String, minRating: Float}, pagination: {page: Int, limit: Int})
   - Mutation.addRating(recipeId: ID!, score: Float!, comment: String)
   - The Recipe.averageRating computed field
3. The recipes query causes N+1 problem when fetching authors. Show the problem with a concrete example, then fix it using DataLoader.
4. A client wants to fetch recipe title + author name + first 3 ingredients in one request. Show the exact GraphQL query they would write.
5. When would you choose GraphQL over REST? When would you NOT?

**A:**
Sure, let's go through the requirements step by step.

### 1. GraphQL Schema (SDL)

```graphql
type Author {
  id: ID!
  name: String!
  bio: String
}

type Ingredient {
  name: String!
  amount: String!
  unit: String!
}

type Step {
  description: String!
  order: Int!
}

type Rating {
  id: ID!
  score: Float!
  comment: String
}

type Recipe {
  id: ID!
  title: String!
  ingredients: [Ingredient!]!
  steps: [Step!]!
  author: Author!
  tags: [String!]!
  ratings: [Rating!]!
  averageRating: Float
}

type Query {
  recipes(filter: RecipeFilter, pagination: PaginationInput): [Recipe!]!
}

input RecipeFilter {
  tag: String
  minRating: Float
}

input PaginationInput {
  page: Int!
  limit: Int!
}

type Mutation {
  addRating(recipeId: ID!, score: Float!, comment: String): Rating!
}

type Subscription {
  ratingAdded(recipeId: ID!): Rating
}
```

### 2. Resolvers

```graphql
schema {
  query: Query
  mutation: Mutation
  subscription: Subscription
}

type Query {
  recipes(filter: RecipeFilter, pagination: PaginationInput): [Recipe!]!
}

type Mutation {
  addRating(recipeId: ID!, score: Float!, comment: String): Rating!
}

type Subscription {
  ratingAdded(recipeId: ID!): Rating
}

type Author {
  id: ID!
  name: String!
  bio: String
}

type Ingredient {
  name: String!
  amount: String!
  unit: String!
}

type Step {
  description: String!
  order: Int!
}

type Rating {
  id: ID!
  score: Float!
  comment: String
}

type Recipe {
  id: ID!
  title: String!
  ingredients: [Ingredient!]!
  steps: [Step!]!
  author: Author!
  tags: [String!]!
  ratings: [Rating!]!
  averageRating: Float
}

type RecipeFilter {
  tag: String
  minRating: Float
}

input RecipeFilter {
  tag: String
  minRating: Float
}

input PaginationInput {
  page: Int!
  limit: Int!
}

type Rating {
  id: ID!
  score: Float!
  comment: String
}

type Subscription {
  ratingAdded(recipeId: ID!): Rating
}
```

### 3. Fixing the N+1 Problem with DataLoader

To fix the N+1 problem, we can use `DataLoader` to load authors in batches. Here's how you can modify the resolver for `recipes`:

```graphql
type Query {
  recipes(filter: RecipeFilter, pagination: PaginationInput): [Recipe!]!
}

type Mutation {
  addRating(recipeId: ID!, score: Float!, comment: String): Rating!
}

type Subscription {
  ratingAdded(recipeId: ID!): Rating
}

type Author {
  id: ID!
  name: String!
  bio: String
}

type Ingredient {
  name: String!
  amount: String!
  unit: String!
}

type Step {
  description: String!
  order: Int!
}

type Rating {
  id: ID!
  score: Float!
  comment: String
}

type Recipe {
  id: ID!
  title: String!
  ingredients: [Ingredient!]!
  steps: [Step!]!
  author: Author!
  tags: [String!]!
  ratings: [Rating!]!
  averageRating: Float
}

type RecipeFilter {
  tag: String
  minRating: Float
}

input RecipeFilter {
  tag: String
  minRating: Float
}

input PaginationInput {
  page: Int!
  limit: Int!
}

type Rating {
  id: ID!
  score: Float!
  comment: String
}

type Subscription {
  ratingAdded(recipeId: ID!): Rating
}

import DataLoader from 'dataloader';

const recipeDataLoader = new DataLoader(async (recipeIds) => {
  const recipes = await Recipe.find({ where: { id: recipeIds } });
  const recipeMap = new Map(recipes.map(recipe => [recipe.id, recipe]));
  return recipeIds.map(id => recipeMap.get(id));
});

const recipeDataLoaderByAuthorId = new DataLoader(async (authorIds) => {
  const authors = await Author.find({ where: { id: authorIds } });
  const authorMap = new Map(authors.map(author => [author.id, author]));
  return authorIds.map(id => authorMap.get(id));
});

const resolvers = {
  Query: {
    recipes: async (root, args, context) => {
      const { filter, pagination } = args;
      // Filter recipes based on filter and pagination
      const recipes = await Recipe.find(filter, pagination);
      // Use DataLoader to load authors in batches
      const authors = await recipeDataLoaderByAuthorId.loadMany(recipes.map(recipe => recipe.authorId));
      recipes.forEach((recipe, index) => recipe.author = authors[index]);
      return recipes;
    }
  },
  Recipe: {
    author: async (recipe, args, context) => {
      // Use DataLoader to load author
      return await recipeDataLoaderByAuthorId.load(recipe.authorId);
    }
  }
};

export default resolvers;
```

### 4. Exact GraphQL Query

To fetch recipe title, author name, and first 3 ingredients in one request, you can write the following GraphQL query:

```graphql
query GetRecipe {
  recipes(id: "your_recipe_id") {
    title
    author {
      name
    }
    ingredients {
      name
      amount
      unit
    }
    firstThreeIngredients: ingredients(limit: 3) {
      name
      amount
      unit
    }
  }
}
```

### 5. Choosing GraphQL vs. REST

- **Use GraphQL when:**
  - You need complex queries that fetch related data efficiently.
  - You want to expose a flexible API that can be easily extended.
  - You need to provide a clear and concise interface to your data.

- **Do not use GraphQL when:**
  - You have a simple data model where queries can be easily expressed in REST.
  - You need a fast response time, and the overhead of a GraphQL server can be a performance bottleneck.
  - You want to optimize for API performance and have a clear understanding of your data structure.

*Response time: 15.3s*

---

## Question 11
**Q:** Implement the following UI layout using only CSS (no JavaScript, no CSS frameworks):

┌─────────────────────────────────────────┐
│  HEADER (fixed, full width, 60px tall)  │
├──────────┬──────────────────────────────┤
│          │                              │
│ SIDEBAR  │      MAIN CONTENT            │
│ (240px,  │  (fills remaining space,     │
│ scrolls  │   scrolls independently)     │
│ indepen- │                              │
│ dently)  │  ┌────────┐ ┌────────┐      │
│          │  │ CARD   │ │ CARD   │      │
│          │  └────────┘ └────────┘      │
│          │  ┌────────┐ ┌────────┐      │
│          │  │ CARD   │ │ CARD   │      │
│          │  └────────┘ └────────┘      │
│          │  (cards: responsive grid,    │
│          │   2 cols ≥768px, 1 col <768) │
└──────────┴──────────────────────────────┘

Requirements:
1. Header is fixed — content does not scroll behind it
2. Sidebar and main content fill the full viewport height below the header
3. Sidebar and main scroll independently
4. Cards use CSS Grid — 2 columns on desktop, 1 column on mobile (≤768px)
5. Each card has: image (16:9 ratio, always maintained), title, description, footer with two buttons (one left-aligned, one right-aligned)
6. No JavaScript. No frameworks. Valid HTML + CSS only.

Write the complete HTML + CSS. Explain your layout approach (Flexbox vs Grid choices).

**A:**
To implement the specified UI layout using only CSS, we'll use Flexbox for the main structure and Grid for the card layout. Here's the complete HTML + CSS:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Responsive Layout</title>
    <style>
        body, html {
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
        }
        
        .header {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 60px;
            background-color: #007BFF;
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .container {
            display: flex;
            height: calc(100vh - 60px);
            margin-top: 60px;
        }
        
        .sidebar {
            width: 240px;
            height: 100%;
            background-color: #343a40;
            color: white;
            overflow-y: auto;
        }
        
        .main-content {
            flex-grow: 1;
            height: 100%;
            background-color: #f8f9fa;
            overflow-y: auto;
        }
        
        .card {
            background-color: #ffffff;
            border: 1px solid #ddd;
            margin: 10px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            position: relative;
        }
        
        .card img {
            width: 100%;
            aspect-ratio: 16 / 9;
            object-fit: cover;
            border-radius: 5px;
        }
        
        .card__content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }
        
        .card__title {
            font-size: 1.2em;
            font-weight: bold;
        }
        
        .card__description {
            font-size: 1em;
            line-height: 1.6;
        }
        
        .card__footer {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            position: absolute;
            bottom: 10px;
            right: 10px;
        }
        
        .card__footer button {
            padding: 10px 20px;
            font-size: 1em;
            border: none;
            border-radius: 5px;
        }
        
        .card__footer button:first-child {
            background-color: #28a745;
            color: white;
        }
        
        .card__footer button:last-child {
            background-color: #dc3545;
            color: white;
        }
        
        @media (max-width: 767px) {
            .card {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        HEADER
    </div>
    <div class="container">
        <div class="sidebar">
            <!-- Sidebar content goes here -->
        </div>
        <div class="main-content">
            <div class="card">
                <img src="card-image-1.jpg" alt="Card Image">
                <div class="card__content">
                    <h2 class="card__title">Card Title</h2>
                    <p class="card__description">Card description goes here...</p>
                </div>
                <div class="card__footer">
                    <button>Button 1</button>
                    <button>Button 2</button>
                </div>
            </div>
            <div class="card">
                <img src="card-image-2.jpg" alt="Card Image">
                <div class="card__content">
                    <h2 class="card__title">Card Title</h2>
                    <p class="card__description">Card description goes here...</p>
                </div>
                <div class="card__footer">
                    <button>Button 1</button>
                    <button>Button 2</button>
                </div>
            </div>
            <!-- Add more cards as needed -->
        </div>
    </div>
</body>
</html>
```

### Explanation:

1. **Header**: The header is fixed using `position: fixed` and has a height of 60px. It spans the full width of the viewport.

2. **Container**: The container uses Flexbox to create a two-column layout. The sidebar takes up 240px width, and the main content takes up the remaining space.

3. **Sidebar**: The sidebar uses `overflow-y: auto` to allow it to scroll independently.

4. **Main Content**: The main content also uses `overflow-y: auto` to allow it to scroll independently.

5. **Cards**: Cards are styled using CSS Grid to arrange them in 2 columns on desktop and 1 column on mobile. The aspect ratio of the images is maintained using `aspect-ratio: 16 / 9`.

6. **Card Structure**: Each card contains an image, content, and footer. The content is divided into two columns using CSS Grid, and the footer is also styled using Grid to have two buttons arranged in a row.

7. **Responsive Design**: The media query at the end ensures that on screens with a maximum width of 767px, the cards stack vertically instead of being in a grid layout.

*Response time: 14.7s*

---

## Question 12
**Q:** You are asked to add real-time notifications to the existing project management tool. Users should be notified when: a task is assigned to them, a comment is added to their task, a deadline is approaching (within 24h).

Design the notification system:
1. What transport mechanism would you use and why? (WebSocket, SSE, polling, push notifications — compare and justify)
2. How do you store notifications? Design the database schema.
3. How do you handle a user who is offline — do they get missed notifications when they come back online?
4. The deadline check needs to run every hour for all tasks. How do you implement this? (cron job, queue, event-driven?) — show the implementation approach.
5. How do you scale this if there are 100,000 concurrent users?

**A:**
Designing a real-time notification system involves several components and considerations. Below is a comprehensive design of the notification system, addressing the key requirements and challenges.

### 1. Transport Mechanism

**WebSocket**
- **Why**: WebSocket provides a full-duplex communication channel over a single, long-lived connection. This allows for low latency and bidirectional communication, making it ideal for real-time notifications.
- **Comparison**: 
  - **SSE**: Server-Sent Events are simpler but only support unidirectional streaming from the server to the client. They are less efficient than WebSocket for real-time updates.
  - **Polling**: Regularly polling the server can be resource-intensive and less efficient.
  - **Push Notifications**: While useful for some purposes, they often require server-side setup and may not be suitable for real-time notifications, especially in mobile applications.

### 2. Database Schema

To store notifications, we can use a relational database like PostgreSQL or MySQL. The schema can include the following tables:

- **Users**: Contains user information.
- **Tasks**: Contains task details.
- **Notifications**: Stores notifications with the following fields:
  - `id`: Unique identifier for the notification.
  - `user_id`: Identifier of the user receiving the notification.
  - `task_id`: Identifier of the task to which the notification is related.
  - `type`: Type of notification (e.g., "task_assigned", "comment_added", "deadline_approaching").
  - `message`: Description of the notification.
  - `created_at`: Timestamp of when the notification was created.
  - `status`: Status of the notification (e.g., "pending", "sent").

### 3. Handling User Offline Notifications

To handle users who are offline, we can use a mechanism like:

- **Session State Tracking**: Maintain a session state on the server that tracks user connections. When a user goes offline, mark their session as inactive.
- **Persistent Notification Storage**: Store notifications in a database or cache. When a user comes back online, retrieve any pending notifications and send them to the user.
- **Push Notifications**: If push notifications are an option, set them up to send a notification when a user is back online.

### 4. Implementing the Deadline Check

To run the deadline check every hour, we can use:

- **Cron Job**: Set up a cron job to run a script every hour that checks all tasks with approaching deadlines.
- **Queue**: Use a message queue like RabbitMQ or Kafka to handle task deadline checks asynchronously.
- **Event-Driven Architecture**: Design a system where tasks are scheduled to check their deadlines in the background.

**Cron Job Implementation**:
```bash
# Create a shell script to run the deadline check
#!/bin/bash

# Check all tasks with a deadline within the next 24 hours
python3 check_deadlines.py
```

**check_deadlines.py**:
```python
import datetime
from database import get_tasks_with_deadline

def check_deadlines():
    current_time = datetime.datetime.now()
    threshold = current_time + datetime.timedelta(hours=24)

    tasks = get_tasks_with_deadline(threshold)

    for task in tasks:
        if task['deadline'] <= threshold:
            # Send notification to the user
            send_notification(task['user_id'], f"Task '{task['title']}' is approaching its deadline!")

# Main function to run the script
if __name__ == "__main__":
    check_deadlines()
```

### 5. Scaling the System

To scale the system for 100,000 concurrent users, consider the following:

- **Load Balancing**: Use a load balancer like Nginx or HAProxy to distribute incoming requests across multiple servers.
- **Horizontal Scaling**: Deploy the system across multiple servers to handle increased load.
- **Caching**: Implement caching solutions like Redis or Memcached to reduce database load and improve response times.
- **Database Optimization**: Optimize the database schema and use indexes to improve query performance.
- **Asynchronous Processing**: Use a message queue or task scheduler to handle background tasks and reduce the load on the main server.
- **Monitoring and Logging**: Implement monitoring and logging to track system performance and detect potential bottlenecks.

By following this design, you can create a robust real-time notification system that efficiently handles user interactions and deadlines, while also scaling effectively as the user base grows.

*Response time: 10.0s*

---
