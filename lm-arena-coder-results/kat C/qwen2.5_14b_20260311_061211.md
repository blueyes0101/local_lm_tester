# Model: qwen2.5:14b
**Test Date:** 2026-03-11 10:41:27
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
### 1. Define all endpoints (method + path) following REST conventions

#### Workspaces
- **Create a Workspace**: `POST /workspaces`
- **Get Workspace by ID**: `GET /workspaces/{workspace_id}`
- **List Workspaces for User**: `GET /users/{user_id}/workspaces`
- **Update Workspace**: `PUT /workspaces/{workspace_id}`
- **Delete Workspace**: `DELETE /workspaces/{workspace_id}`

#### Projects
- **Create a Project**: `POST /workspaces/{workspace_id}/projects`
- **Get Project by ID**: `GET /projects/{project_id}`
- **List Projects for Workspace**: `GET /workspaces/{workspace_id}/projects`
- **Update Project**: `PUT /projects/{project_id}`
- **Delete Project**: `DELETE /projects/{project_id}`

#### Tasks
- **Create a Task**: `POST /projects/{project_id}/tasks`
- **Get Task by ID**: `GET /tasks/{task_id}`
- **List Tasks for Project**: `GET /projects/{project_id}/tasks`
- **Update Task**: `PUT /tasks/{task_id}`
- **Delete Task**: `DELETE /tasks/{task_id}`

#### Users
- **Get User by ID**: `GET /users/{user_id}`
- **List Users in Workspace**: `GET /workspaces/{workspace_id}/users`
- **Update User**: `PUT /users/{user_id}`

#### Comments
- **Create a Comment**: `POST /tasks/{task_id}/comments`
- **Get Comment by ID**: `GET /comments/{comment_id}`
- **List Comments for Task**: `GET /tasks/{task_id}/comments`
- **Update Comment**: `PUT /comments/{comment_id}`
- **Delete Comment**: `DELETE /comments/{comment_id}`

### 2. Show request/response JSON shapes

#### Create Task
- **Request**:
  ```json
  {
    "title": "Write documentation",
    "description": "Write documentation for the project management API",
    "assignee_id": "user123",
    "due_date": "2023-12-31T17:00:00Z",
    "status": "TODO"
  }
  ```
- **Response**:
  ```json
  {
    "id": "task456",
    "title": "Write documentation",
    "description": "Write documentation for the project management API",
    "assignee_id": "user123",
    "due_date": "2023-12-31T17:00:00Z",
    "status": "TODO",
    "project_id": "proj789",
    "created_at": "2023-11-15T09:00:00Z",
    "updated_at": "2023-11-15T09:00:00Z"
  }
  ```

#### Update Task Status
- **Request**:
  ```json
  {
    "status": "IN_PROGRESS"
  }
  ```
- **Response**:
  ```json
  {
    "id": "task456",
    "title": "Write documentation",
    "description": "Write documentation for the project management API",
    "assignee_id": "user123",
    "due_date": "2023-12-31T17:00:00Z",
    "status": "IN_PROGRESS",
    "project_id": "proj789",
    "created_at": "2023-11-15T09:00:00Z",
    "updated_at": "2023-11-16T09:00:00Z"
  }
  ```

#### List Tasks with Filters
- **Request**: `GET /projects/{project_id}/tasks?assignee=user123&status=TODO&due_date=2023-12-31T17:00:00Z`
- **Response**:
  ```json
  {
    "tasks": [
      {
        "id": "task456",
        "title": "Write documentation",
        "description": "Write documentation for the project management API",
        "assignee_id": "user123",
        "due_date": "2023-12-31T17:00:00Z",
        "status": "TODO",
        "project_id": "proj789",
        "created_at": "2023-11-15T09:00:00Z",
        "updated_at": "2023-11-15T09:00:00Z"
      }
    ]
  }
  ```

#### Add Comment
- **Request**:
  ```json
  {
    "content": "This task needs more information.",
    "author_id": "user456"
  }
  ```
- **Response**:
  ```json
  {
    "id": "comment789",
    "content": "This task needs more information.",
    "author_id": "user456",
    "task_id": "task456",
    "created_at": "2023-11-15T09:00:00Z",
    "updated_at": "2023-11-15T09:00:00Z"
  }
  ```

### 2. Define your error response format

**Error Response**:
```json
{
  "errors": [
    {
      "code": "400",
      "message": "Bad Request",
      "details": "The request could not be understood by the server due to malformed syntax."
    },
    {
      "code": "401",
      "message": "Unauthorized",
      "details": "Authentication is required and has not been provided."
    },
    {
      "code": "403",
      "message": "Forbidden",
      "details": "The server understood the request but refuses to authorize it."
    },
    {
      "code": "404",
      "message": "Not Found",
      "details": "The server can not find the requested resource."
    },
    {
      "code": "500",
      "message": "Internal Server Error",
      "details": "The server encountered an unexpected condition which prevented it from fulfilling the request."
    }
  ]
}
```

### 3. How do you handle pagination?

**Pagination Response Envelope**:
```json
{
  "tasks": [
    {
      "id": "task456",
      "title": "Write documentation",
      "description": "Write documentation for the project management API",
      "assignee_id": "user123",
      "due_date": "2023-12-31T17:00:00Z",
      "status": "TODO",
      "project_id": "proj789",
      "created_at": "2023-11-15T09:00:00Z",
      "updated_at": "2023-11-15T09:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total_items": 15,
    "total_pages": 2,
    "next_page": "http://api.example.com/tasks?page=2&per_page=10",
    "prev_page": null
  }
}
```

### 4. Which endpoints need which HTTP status codes and when?

- **200 OK**: Successful response for GET requests.
- **201 Created**: Successful response for POST requests.
- **204 No Content**: Successful response for DELETE requests (no content to return).
- **202 Accepted**: Successful response for POST/PUT requests that are asynchronous and will complete later.
- **400 Bad Request**: The request could not be understood by the server due to malformed syntax.
- **401 Unauthorized**: Authentication is required and has not been provided.
- **403 Forbidden**: The server understood the request but refuses to authorize it.
- **404 Not Found**: The server can not find the requested resource.
- **409 Conflict**: The request could not be completed due to a conflict with the current state of the target resource.
- **500 Internal Server Error**: The server encountered an unexpected condition which prevented it from fulfilling the request.

By following these conventions, the API will be easy to understand and use, providing consistent behavior across all endpoints.

*Response time: 207.6s*

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
Below is an example implementation of the described PATCH endpoint in Node.js using Express and TypeScript, along with Zod for validation and unit tests using Jest and Supertest for testing the endpoint.

### 1. Project Setup

First, ensure you have a basic Express TypeScript project set up. You can install the necessary dependencies with:

```bash
npm init -y
npm install express body-parser zod @zod-i/core
npm install --save-dev typescript @types/node @types/express ts-node jest @types/jest supertest
npx tsc --init
```

### 2. Zod Validation Schema

Create a validation schema using Zod.

```typescript
import { z } from 'zod';

const taskUpdateSchema = z.object({
  title: z.string().min(1).max(200).optional(),
  status: z.union([z.literal('todo'), z.literal('in_progress'), z.literal('done'), z.literal('cancelled')]).optional(),
  assignee_id: z.number().nullable().optional(),
  due_date: z.string().or(z.null()).optional(),
});

const validateTaskUpdate = (body: unknown): z.infer<typeof taskUpdateSchema> => {
  return taskUpdateSchema.safeParse(body).success ? taskUpdateSchema.parse(body) : null;
};
```

### 3. Database Mock

For simplicity, we will mock the database layer. In a real application, you would connect to your database.

```typescript
interface Workspace {
  id: number;
  name: string;
  members: number[];
}

interface Task {
  id: number;
  workspaceId: number;
  title: string;
  status: string;
  assignee_id: number | null;
  due_date: string | null;
  subtasks: Task[];
}

const workspaces: Workspace[] = [
  { id: 1, name: 'Workspace 1', members: [1, 2, 3] },
  { id: 2, name: 'Workspace 2', members: [4, 5, 6] },
];

const tasks: Task[] = [
  { id: 1, workspaceId: 1, title: 'Task 1', status: 'todo', assignee_id: 1, due_date: null, subtasks: [] },
  { id: 2, workspaceId: 1, title: 'Task 2', status: 'in_progress', assignee_id: 2, due_date: null, subtasks: [] },
  { id: 3, workspaceId: 2, title: 'Task 3', status: 'done', assignee_id: null, due_date: null, subtasks: [] },
];

function getWorkspaceById(id: number): Workspace | undefined {
  return workspaces.find(ws => ws.id === id);
}

function getTaskById(taskId: number): Task | undefined {
  return tasks.find(task => task.id === taskId);
}

function checkTaskInWorkspace(workspaceId: number, taskId: number): boolean {
  const task = getTaskById(taskId);
  if (!task) return false;
  return task.workspaceId === workspaceId;
}

function checkAssigneeInWorkspace(workspaceId: number, assigneeId: number | null): boolean {
  const workspace = getWorkspaceById(workspaceId);
  if (!workspace) return false;
  return assigneeId === null || workspace.members.includes(assigneeId);
}

function checkNoOpenSubtasks(taskId: number): boolean {
  const task = getTaskById(taskId);
  if (!task) return false;
  return task.subtasks.every(subtask => subtask.status !== 'todo' && subtask.status !== 'in_progress');
}
```

### 4. Express Handler

Create the handler function for the PATCH endpoint.

```typescript
import express from 'express';
import { validateTaskUpdate } from './validation';
import { getWorkspaceById, getTaskById, checkTaskInWorkspace, checkAssigneeInWorkspace, checkNoOpenSubtasks } from './database';

const app = express();
app.use(express.json());

app.patch('/workspaces/:workspaceId/tasks/:taskId', (req, res) => {
  const { workspaceId, taskId } = req.params;
  const parsedWorkspaceId = parseInt(workspaceId);
  const parsedTaskId = parseInt(taskId);

  if (isNaN(parsedWorkspaceId) || isNaN(parsedTaskId)) {
    return res.status(400).json({ error: 'workspaceId and taskId must be integers' });
  }

  const task = getTaskById(parsedTaskId);
  if (!task) {
    return res.status(404).json({ error: 'Task not found' });
  }

  const workspace = getWorkspaceById(parsedWorkspaceId);
  if (!workspace || !checkTaskInWorkspace(parsedWorkspaceId, parsedTaskId)) {
    return res.status(404).json({ error: 'Task does not belong to the specified workspace' });
  }

  const validatedTaskUpdate = validateTaskUpdate(req.body);
  if (!validatedTaskUpdate) {
    return res.status(400).json({ error: 'Invalid task update data' });
  }

  if (validatedTaskUpdate.status === 'cancelled' && !checkNoOpenSubtasks(parsedTaskId)) {
    return res.status(409).json({ error: 'Cannot cancel task with open subtasks' });
  }

  if (validatedTaskUpdate.assignee_id !== undefined && !checkAssigneeInWorkspace(parsedWorkspaceId, validatedTaskUpdate.assignee_id)) {
    return res.status(400).json({ error: 'Assignee does not belong to the workspace' });
  }

  // Apply updates to the task (mocked)
  Object.assign(task, validatedTaskUpdate);

  res.status(200).json(task);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

### 5. Unit Tests

Create unit tests for the endpoint.

```typescript
import * as request from 'supertest';
import app from './app'; // Your app file

describe('PATCH /workspaces/:workspaceId/tasks/:taskId', () => {
  it('should successfully update a task', async () => {
    const response = await request(app)
      .patch('/workspaces/1/tasks/1')
      .send({ title: 'Updated Task' });
    expect(response.status).toBe(200);
    expect(response.body.title).toBe('Updated Task');
  });

  it('should return 400 for invalid task update data', async () => {
    const response = await request(app)
      .patch('/workspaces/1/tasks/1')
      .send({ status: 'invalid_status' });
    expect(response.status).toBe(400);
    expect(response.body.error).toBe('Invalid task update data');
  });

  it('should return 404 if task not found', async () => {
    const response = await request(app)
      .patch('/workspaces/1/tasks/999')
      .send({ title: 'Task' });
    expect(response.status).toBe(404);
    expect(response.body.error).toBe('Task not found');
  });

  it('should return 409 if trying to cancel a task with open subtasks', async () => {
    const response = await request(app)
      .patch('/workspaces/1/tasks/1')
      .send({ status: 'cancelled' });
    expect(response.status).toBe(409);
    expect(response.body.error).toBe('Cannot cancel task with open subtasks');
  });
});
```

### 6. Running Tests

Run the tests with:

```bash
npx jest
```

This setup provides a full solution including validation, database interaction, and testing for the PATCH endpoint in a Node.js + Express + TypeScript application.

*Response time: 181.0s*

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
To implement a complete authentication system in Node.js + Express + TypeScript with the requirements you've specified, you'll need to set up several key components:

### Prerequisites

Before you start, make sure you have the following installed:
- Node.js
- `npm` (Node Package Manager)
- TypeScript
- Express
- bcrypt
- jsonwebtoken
- cookie-parser
- dotenv

You can install these packages using npm:
```sh
npm install express bcrypt jsonwebtoken cookie-parser dotenv
npm install --save-dev typescript @types/express @types/bcrypt @types/jsonwebtoken @types/node
```

### Project Setup

1. **Directory Structure:**
   - `src`
     - `controllers`
     - `models`
     - `routes`
     - `utils`
     - `app.ts`
     - `database.ts`
   - `config`
     - `config.ts`
   - `.env`
   - `tsconfig.json`

2. **Environment Configuration:**
   - Create a `.env` file to store environment variables.
   ```env
   PORT=3000
   SECRET_KEY=your_jwt_secret
   REFRESH_SECRET_KEY=your_refresh_jwt_secret
   DB_URI=mongodb://localhost:27017/yourdb
   ```

### Implementation

#### 1. Setup Express Application (`src/app.ts`)

```typescript
import express, { Request, Response } from 'express';
import mongoose from 'mongoose';
import cookieParser from 'cookie-parser';
import authRoutes from './routes/authRoutes';
import { errorHandler } from './utils/errorHandler';
import { connectDB } from './database';
import { authMiddleware } from './utils/authMiddleware';

const app = express();
app.use(express.json());
app.use(cookieParser());

connectDB();

// Middleware to authenticate JWT tokens
app.use(authMiddleware);

app.use('/auth', authRoutes);

// Error handler middleware
app.use(errorHandler);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
```

#### 2. Database Connection (`src/database.ts`)

```typescript
import mongoose from 'mongoose';
import { config } from 'config';

const dbURI = config.get('DB_URI');

const connectDB = async (): Promise<void> => {
  try {
    await mongoose.connect(dbURI, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });
    console.log('Database connected');
  } catch (err) {
    console.error('Database connection error:', err);
  }
};

export { connectDB };
```

#### 3. User Model (`src/models/user.ts`)

```typescript
import mongoose from 'mongoose';

const UserSchema = new mongoose.Schema({
  email: { type: String, unique: true, required: true },
  password: { type: String, required: true, select: false }, // password is not returned in queries
  role: { type: String, default: 'user' },
}, { timestamps: true });

export default mongoose.model('User', UserSchema);
```

#### 4. Authentication Routes (`src/routes/authRoutes.ts`)

```typescript
import express from 'express';
import { register, login, refreshToken, me } from '../controllers/authController';
import { protect } from '../utils/authMiddleware';

const router = express.Router();

router.post('/register', register);
router.post('/login', login);
router.get('/me', protect, me);
router.post('/refresh-token', refreshToken);

export default router;
```

#### 5. Authentication Controller (`src/controllers/authController.ts`)

```typescript
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import cookieParser from 'cookie-parser';
import { User } from '../models/user';
import { config } from 'config';
import { Request, Response } from 'express';

export const register = async (req: Request, res: Response) => {
  const { email, password } = req.body;

  const hashedPassword = await bcrypt.hash(password, 12);
  const user = await User.create({ email, password: hashedPassword });
  res.status(201).json({ user });
};

export const login = async (req: Request, res: Response) => {
  const { email, password } = req.body;
  const user = await User.findOne({ email }).select('+password');

  if (!user || !(await bcrypt.compare(password, user.password))) {
    return res.status(401).json({ message: 'Invalid credentials' });
  }

  const accessToken = jwt.sign(
    { userId: user._id, email: user.email, role: user.role },
    config.get('SECRET_KEY'),
    { expiresIn: '15m' }
  );

  const refreshToken = jwt.sign(
    { userId: user._id },
    config.get('REFRESH_SECRET_KEY'),
    { expiresIn: '7d' }
  );

  res.cookie('refreshToken', refreshToken, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production', // true in prod
    maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days in milliseconds
  });

  res.json({ accessToken });
};

export const refreshToken = async (req: Request, res: Response) => {
  const { refreshToken } = req.cookies;

  if (!refreshToken) return res.status(401).json({ message: 'No refresh token found' });

  jwt.verify(refreshToken, config.get('REFRESH_SECRET_KEY'), async (err, decoded) => {
    if (err) return res.status(403).json({ message: 'Invalid refresh token' });

    const user = await User.findById(decoded.userId).select('+password');
    if (!user) return res.status(404).json({ message: 'User not found' });

    const accessToken = jwt.sign(
      { userId: user._id, email: user.email, role: user.role },
      config.get('SECRET_KEY'),
      { expiresIn: '15m' }
    );

    res.json({ accessToken });
  });
};

export const me = async (req: Request, res: Response) => {
  res.json(req.user);
};
```

#### 6. Auth Middleware (`src/utils/authMiddleware.ts`)

```typescript
import jwt from 'jsonwebtoken';
import { Request, Response, NextFunction } from 'express';
import { User } from '../models/user';

export const authMiddleware = (req: Request, res: Response, next: NextFunction) => {
  const token = req.headers.authorization?.split(' ')[1];

  if (!token) {
    return res.status(401).json({ message: 'No token provided' });
  }

  try {
    const decoded = jwt.verify(token, process.env.SECRET_KEY as string);
    const user = await User.findById(decoded.userId).select('-password');
    if (!user) return res.status(404).json({ message: 'User not found' });

    req.user = user;
    next();
  } catch (err) {
    res.status(401).json({ message: 'Token is not valid' });
  }
};
```

#### 7. Error Handling Middleware (`src/utils/errorHandler.ts`)

```typescript
import { Request, Response, NextFunction } from 'express';

export const errorHandler = (err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error(err.stack);
  res.status(500).json({ error: err.message });
};
```

### Explanation and Security Considerations

**HTTP-Only Cookie for Refresh Token:**
- **Security Reasoning:** Using HTTP-only cookies prevents JavaScript on the client side from accessing the cookie. This mitigates the risk of XSS (Cross-Site Scripting) attacks, where an attacker could steal the refresh token from an HTTP-only cookie if it were stored in `localStorage`.

**Expired Tokens:**
- When an expired access token is sent, the middleware will fail to verify it, and the request will be rejected with a 401 Unauthorized status, returning an error message like `{ message: 'Token is not valid' }`.

### Conclusion

This setup provides a basic but secure authentication system in Node.js + Express + TypeScript. It includes password hashing, token-based authentication, and secure handling of refresh tokens. Always ensure to follow security best practices and consider additional measures such as rate limiting, input validation, and more complex session management strategies as needed.

*Response time: 194.9s*

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
### 1. POST /auth/refresh

When a user sends a POST request to `/auth/refresh`, the system checks the refresh token in the request cookies. If the token is valid, it generates a new access token and a new refresh token. The old refresh token is invalidated, and the new refresh token is stored in Redis along with a short expiry (TTL). The new refresh token is also sent back to the user in a cookie.

### 2. POST /auth/logout

When a user logs out, the system invalidates the refresh token by deleting it from Redis. The system also clears the refresh token from the user's cookies.

### 3. Redis-based Token Store Data Structure and TTL Strategy

#### Redis Data Structure
- **Key Format**: `refresh_token:<token_id>`
- **Value**: JSON object with fields `user_id`, `expiry`, `is_blacklisted` (default is `false`)

#### TTL Strategy
- Refresh tokens have a short expiry period (e.g., 7 days) and a time-to-live (TTL) set in Redis.
- Each refresh token is stored with a TTL of 7 days to ensure it is automatically invalidated if not used within that time.

### 4. Handling Token Reuse Detection

To detect token reuse, you can modify the Redis key for each refresh token to include the token's usage status. Here's how:

#### Redis Key for Reuse Detection
- **Key Format**: `refresh_token:<token_id>:usage`
- **Value**: A counter that increments each time the token is used.

#### Implementation
```python
import redis
import json

r = redis.Redis(host='localhost', port=6379, db=0)

def refresh_access_token(refresh_token):
    token_key = f'refresh_token:{refresh_token}'
    usage_key = f'refresh_token:{refresh_token}:usage'
    
    # Check if the token is valid and not blacklisted
    if not r.exists(token_key) or r.hget(token_key, 'is_blacklisted') == 'true':
        return {'error': 'Invalid refresh token'}, 401
    
    # Check token reuse
    if r.hexists(usage_key, 'count'):
        usage_count = int(r.hget(usage_key, 'count'))
        if usage_count > 0:
            return {'error': 'Token has been used before'}, 401
    
    # Generate new tokens
    new_access_token = generate_access_token()
    new_refresh_token = generate_refresh_token()
    
    # Invalidate old refresh token
    r.hset(token_key, 'is_blacklisted', 'true')
    
    # Store new refresh token with TTL
    new_token_key = f'refresh_token:{new_refresh_token}'
    r.hset(new_token_key, 'user_id', r.hget(token_key, 'user_id'))
    r.expire(new_token_key, 604800)  # 7 days
    
    # Set usage count for new token
    r.hset(f'refresh_token:{new_refresh_token}:usage', 'count', '1')
    
    return {'access_token': new_access_token, 'refresh_token': new_refresh_token}
```

### 5. Invalidate All Existing Sessions When a Password is Changed

When a user changes their password, you can invalidate all their existing sessions by blacklisting their refresh tokens. This involves iterating through all the refresh tokens associated with the user and setting their `is_blacklisted` flag to `true`.

#### Implementation
```python
def invalidate_user_sessions(user_id):
    # Get all refresh tokens for the user
    user_tokens = r.keys(f'refresh_token:*')
    user_tokens = [token.decode() for token in user_tokens if r.hget(token, 'user_id') == user_id]
    
    # Invalidate all tokens
    for token in user_tokens:
        r.hset(token, 'is_blacklisted', 'true')
    
    # Clear cookies and other session storage
    # (This part is typically handled on the client side by clearing cookies)
```

### 6. Token Blacklisting vs. Token Rotation

**Token Blacklisting**:
- **Mechanism**: Mark tokens as invalid in a list or set.
- **Usage**: Useful when you need to invalidate a token immediately (e.g., after a password change) but don't need to generate new tokens.
- **Advantages**: Simplicity in implementation and no need to manage token lifecycles.
- **Disadvantages**: Can lead to a large number of blacklisted tokens over time, increasing storage requirements and lookup times.

**Token Rotation**:
- **Mechanism**: Replace old tokens with new ones and invalidate old tokens.
- **Usage**: Suitable when you want to manage token lifecycles and reduce the risk of token reuse.
- **Advantages**: Provides better security by reducing the lifetime of tokens and ensuring regular refreshes.
- **Disadvantages**: Requires more complex logic for token generation and management.

**When to Use Each**:
- **Blacklisting**: When immediate token invalidation is required due to security breaches or password changes.
- **Rotation**: When you need to manage token lifecycles and ensure regular security checks (e.g., rotating access tokens).

In summary, both mechanisms serve different purposes and should be chosen based on the specific security requirements and operational constraints of the application.

*Response time: 120.2s*

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
### 1. TypeScript Interface for Props

First, let's define the TypeScript interface for the props of the DataTable component. This interface will be generic to support different row types and columns with varying configurations.

```typescript
import React from 'react';

// Define the type for the column configuration
type Column<T> = {
  key: keyof T;
  header: string;
  width?: string;
  sortable?: boolean;
  renderCell?: (rowData: T) => React.ReactNode;
};

// Define the type for the pagination configuration
type PaginationConfig = {
  pageSize: number;
  currentPage: number;
};

// Define the type for the selection configuration
type SelectionConfig = {
  selectedRows: Set<number>;
  toggleSelection: (rowIndex: number) => void;
  selectAll: (selectAll: boolean) => void;
};

// Define the type for the DataTable props
type DataTableProps<T> = {
  columns: Column<T>[];
  data: T[];
  selectedRows?: SelectionConfig['selectedRows'];
  onSelect?: SelectionConfig['toggleSelection'];
  onSelectAll?: SelectionConfig['selectAll'];
  onSort?: (columnKey: keyof T, sortDirection: 'asc' | 'desc' | undefined) => void;
  pagination?: PaginationConfig;
};
```

### 2. Complete Component Implementation

Now let's implement the `DataTable` component.

```typescript
import React, { useState, useMemo, useCallback } from 'react';

const DataTable: React.FC<DataTableProps<any>> = (props) => {
  const [sortColumn, setSortColumn] = useState<keyof any | undefined>(undefined);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc' | undefined>(undefined);

  const columns = useMemo(() => props.columns.map(col => ({...col, sortable: col.sortable ?? true})), [props.columns]);

  const handleSort = useCallback((columnKey: keyof any) => {
    if (sortColumn === columnKey) {
      setSortDirection(prev => (prev === 'asc' ? 'desc' : undefined));
    } else {
      setSortColumn(columnKey);
      setSortDirection('asc');
    }
    if (props.onSort) {
      props.onSort(columnKey, sortDirection);
    }
  }, [sortColumn, sortDirection, props.onSort]);

  const handleSelect = useCallback((rowIndex: number) => {
    if (props.onSelect) {
      props.onSelect(rowIndex);
    }
  }, [props.onSelect]);

  const handleSelectAll = useCallback((selectAll: boolean) => {
    if (props.onSelectAll) {
      props.onSelectAll(selectAll);
    }
  }, [props.onSelectAll]);

  const sortedData = useMemo(() => {
    if (!sortColumn) return props.data;

    const isAsc = sortDirection === 'asc';
    const sorted = [...props.data].sort((a, b) => {
      const keyA = a[sortColumn as keyof any];
      const keyB = b[sortColumn as keyof any];
      if (typeof keyA === 'number' && typeof keyB === 'number') {
        return isAsc ? keyA - keyB : keyB - keyA;
      } else if (typeof keyA === 'string' && typeof keyB === 'string') {
        return isAsc ? keyA.localeCompare(keyB) : keyB.localeCompare(keyA);
      }
      return 0;
    });
    return sorted;
  }, [props.data, sortColumn, sortDirection]);

  return (
    <div>
      <table>
        <thead>
          <tr>
            {columns.map(column => (
              <th
                key={column.key}
                style={{ width: column.width }}
                onClick={() => handleSort(column.key as keyof any)}
              >
                {column.header}
                {column.sortable && (
                  <span>
                    {sortColumn === column.key && (sortDirection === 'asc' ? '▲' : '▼')}
                  </span>
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sortedData.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {columns.map(column => (
                <td key={column.key}>
                  {column.renderCell ? column.renderCell(row) : row[column.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <div>
        <input type="checkbox" onChange={(e) => handleSelectAll(e.target.checked)} />
        <button onClick={() => handleSelectAll(true)}>Select All</button>
        <button onClick={() => handleSelectAll(false)}>Deselect All</button>
      </div>
    </div>
  );
};

export default DataTable;
```

### 3. Usage Example

Let's create a usage example for the `DataTable` component with 3 columns, one of which uses a custom `renderCell` function to display an action button.

```typescript
import React from 'react';
import DataTable from './DataTable';

interface RowType {
  id: number;
  name: string;
  age: number;
}

const App = () => {
  const rows: RowType[] = [
    { id: 1, name: 'Alice', age: 30 },
    { id: 2, name: 'Bob', age: 25 },
    { id: 3, name: 'Charlie', age: 35 },
  ];

  const columns: Column<RowType>[] = [
    { key: 'id', header: 'ID' },
    { key: 'name', header: 'Name' },
    {
      key: 'age',
      header: 'Age',
      renderCell: (rowData) => (
        <button onClick={() => console.log(`Action on row ${rowData.id}`)}>View Details</button>
      )
    },
  ];

  return (
    <div>
      <DataTable columns={columns} data={rows} />
    </div>
  );
};

export default App;
```

### 4. Memoization for Avoiding Unnecessary Re-renders

To optimize performance and avoid unnecessary re-renders, you can make use of `React.memo` and `useMemo` effectively.

- **React.memo** is used on the `DataTable` component to ensure that it only re-renders when its props change.
- **useMemo** is used to memoize the `sortedData` and `columns` arrays to ensure that they are only recalculated when necessary.

Here is how you can apply `React.memo` to the `DataTable` component:

```typescript
import React, { memo, useState, useMemo, useCallback } from 'react';

const DataTableMemoized = memo<React.FC<DataTableProps<any>>>(DataTable);

export default DataTableMemoized;
```

By applying `React.memo`, the `DataTable` component will only re-render when its props change, which is a significant performance optimization for large datasets or complex components.

*Response time: 162.8s*

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
To implement the described search feature in React using hooks, we will break down the solution into the following parts:

1. **Custom Hook `useSearch(query: string)`**: This hook will manage the debouncing, fetching, caching, and cancellation of requests.
2. **SearchPage Component**: This component will use the `useSearch` hook to handle the search logic and display the results.
3. **URL Sync Implementation**: Using the `useSearchParams` and `useNavigate` hooks from `react-router-dom` to keep the URL in sync with the search query.
4. **Cancelling In-Flight Requests**: Explanation and implementation of cancelling in-flight requests and the importance of this practice.

### Custom Hook `useSearch(query: string)`

Let's start with the custom hook `useSearch`. This hook will manage the debouncing logic, fetching data from the API, caching results, and handling cancellations.

```javascript
import { useEffect, useState, useCallback } from 'react';

const useSearch = (query) => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const [fetchTimeout, setFetchTimeout] = useState(null);
  const [cancelRequest, setCancelRequest] = useState(null);

  useEffect(() => {
    if (query !== debouncedQuery) {
      setDebouncedQuery(query);
    }
  }, [query]);

  useEffect(() => {
    if (debouncedQuery) {
      clearTimeout(fetchTimeout);
      setFetchTimeout(setTimeout(async () => {
        setLoading(true);
        setError(null);
        const controller = new AbortController();
        setCancelRequest(controller.abort);
        try {
          const response = await fetch(`/api/search?q=${debouncedQuery}`, {
            signal: controller.signal,
          });
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          const data = await response.json();
          if (data.length === 0) {
            setResults([]);
            setError('No results found');
          } else {
            setResults(data);
            setError(null);
          }
        } catch (err) {
          setError(err.message);
        } finally {
          setLoading(false);
        }
      }, 300));
    }
  }, [debouncedQuery]);

  const cancelCurrentRequest = useCallback(() => {
    if (cancelRequest) {
      cancelRequest();
      setCancelRequest(null);
    }
  }, [cancelRequest]);

  useEffect(() => {
    return cancelCurrentRequest;
  }, [cancelCurrentRequest]);

  return { results, loading, error, cancelCurrentRequest };
};
```

### SearchPage Component

The `SearchPage` component will use the `useSearch` hook and implement URL sync using `react-router-dom`.

```javascript
import React, { useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import useSearch from './useSearch';

const SearchPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const query = searchParams.get('q') || '';
  const { results, loading, error, cancelCurrentRequest } = useSearch(query);

  const handleSearch = (e) => {
    e.preventDefault();
    setSearchParams({ q: e.target.search.value });
    cancelCurrentRequest(); // Cancel any existing request
  };

  const clearQuery = () => {
    setSearchParams({});
  };

  const retrySearch = () => {
    setSearchParams({ q: query });
  };

  return (
    <div>
      <form onSubmit={handleSearch}>
        <input type="search" name="search" placeholder="Search..." />
        <button type="submit">Search</button>
      </form>
      {loading && <div>Loading...</div>}
      {error && <div>{error} <button onClick={retrySearch}>Retry</button></div>}
      {results.length === 0 && <div>No results</div>}
      {results.length > 0 && (
        <div>
          {results.map((result, index) => (
            <div key={index}>{result}</div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SearchPage;
```

### URL Sync Implementation

The `useSearchParams` hook from `react-router-dom` is used to manage the URL query parameters. The `setSearchParams` function updates the URL and triggers re-renders, ensuring that the search term is always visible in the URL. When the user navigates back or forward, React Router will automatically update the component state based on the URL query parameters.

### Cancelling In-Flight Requests

Cancelling in-flight requests is crucial to avoid displaying stale data or waiting for a response from an outdated query. This is particularly important in scenarios like search features where users can quickly change the search term. If a new search request is made while the previous one is still in progress, without cancelling the previous request, you might end up displaying old results for a query the user no longer cares about.

By cancelling the previous request, you ensure that the most recent and relevant results are fetched and displayed to the user, providing a better user experience.

*Response time: 123.1s*

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
### 1. Prisma Query for 10 Most Recent Published Posts

To fetch the 10 most recent published posts along with the author's name, tag names, and comment count, you can use Prisma's nested queries to avoid N+1 queries. Here's how you can write the query:

```typescript
const posts = await prisma.post.findMany({
  where: { published: true },
  orderBy: { createdAt: 'desc' },
  take: 10,
  include: {
    author: { select: { email: true } },
    tags: { select: { name: true } },
    comments: { select: { id: true } },
  },
});

const postsWithDetails = posts.map(post => ({
  ...post,
  authorName: post.author.email,
  tagNames: post.tags.map(tag => tag.name),
  commentCount: post.comments.length,
}));
```

This query includes the necessary data and avoids fetching the entire comment objects and author details, which helps in reducing the response time and data transfer.

### 2. Migration Scenario: Adding a Slug Field to Post

To add a unique, non-nullable `slug` field to the `Post` table, you need to take a phased approach to ensure that the migration is safe and that the system can handle the transition without downtime. Here's how you can do it:

1. **Create a Nullable Slug Field**: First, add the `slug` field as nullable to allow data insertion without breaking existing entries.
2. **Populate the Slug Field**: Use a script or scheduled job to generate and populate the `slug` field for all existing posts.
3. **Make Slug Non-Nullable and Unique**: Once the field is populated and validated, make the `slug` field non-nullable and unique.

Here's a step-by-step approach:

#### Step 1: Add Nullable Slug Field
```sql
ALTER TABLE "Post" ADD COLUMN "slug" VARCHAR;
```

#### Step 2: Populate the Slug Field
You can use a script or a scheduled job to populate the `slug` field. Here's an example of how you might do it using a Prisma migration:

```typescript
const posts = await prisma.post.findMany({ where: { slug: null } });

for (const post of posts) {
  const slug = generateSlug(post.title); // Custom function to generate slug
  await prisma.post.update({
    where: { id: post.id },
    data: { slug },
  });
}
```

#### Step 3: Make Slug Non-Nullable and Unique
```sql
ALTER TABLE "Post" ALTER COLUMN "slug" SET NOT NULL;
ALTER TABLE "Post" ADD CONSTRAINT "unique_slug" UNIQUE ("slug");
```

### 3. Diagnosing and Fixing Slow Query: `findMany` Posts by Tag Name

If the query `findMany` posts filtered by tag name is slow, it's likely due to missing indexes. Here's how you can diagnose and fix it:

#### Prisma Query
```typescript
const posts = await prisma.post.findMany({
  where: { tags: { some: { name: 'some-tag-name' } } },
});
```

#### Generated Raw SQL
```sql
SELECT "Post".* FROM "Post"
JOIN "PostToTag" ON "Post"."id" = "PostToTag"."postId"
JOIN "Tag" ON "PostToTag"."tagId" = "Tag"."id"
WHERE "Tag"."name" = 'some-tag-name'
```

#### Index Addition
To speed up this query, you should add an index on the `name` column of the `Tag` table and a composite index on the join table `PostToTag`.

```sql
CREATE INDEX idx_tag_name ON "Tag"("name");
CREATE INDEX idx_post_to_tag ON "PostToTag"("postId", "tagId");
```

After adding these indexes, the query should be significantly faster.

### 4. When Would You Drop Down to Raw SQL?

You would drop down to raw SQL when you need to perform complex operations that are not easily achievable with Prisma's ORM, such as bulk operations, custom queries, or when you need to fine-tune performance with database-specific features.

#### Example: Bulk Update of Posts

Suppose you need to update a large number of posts to set `published` to true. Prisma might not be optimized for such large bulk updates, so you might use raw SQL:

```sql
BEGIN;
UPDATE "Post" SET "published" = true WHERE "published" = false;
COMMIT;
```

This example shows a transaction to safely update a large number of posts without causing issues with ORM limitations.

*Response time: 106.9s*

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
### 1. Docker Compose Configuration for Local Development

To set up a local development environment with the requirements specified, you can create a `docker-compose.yml` file as follows:

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev  # This should handle hot reload
    ports:
      - '3000:3000'
    environment:
      - VITE_API_URL=http://backend:3001
    volumes:
      - ./frontend:/app
      - /app/node_modules
    networks:
      - mynetwork

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile  # Default Dockerfile for the backend
    ports:
      - '3001:3001'
    environment:
      - NODE_ENV=development
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_USER=postgres
      - DB_PASS=postgres
      - DB_NAME=postgres
    volumes:
      - ./backend:/app
      - /app/node_modules
    depends_on:
      - postgres
    networks:
      - mynetwork
    healthcheck:
      test: ["CMD", "pg_isready", "-h", "postgres", "-U", "postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  postgres:
    image: postgres:13
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=postgres
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - mynetwork
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:6
    ports:
      - '6379:6379'
    networks:
      - mynetwork

volumes:
  postgres-data:

networks:
  mynetwork:
```

### 2. Production Dockerfile for the Backend

The production Dockerfile for the backend can be written as follows:

```Dockerfile
# Builder stage
FROM node:16-alpine as builder

WORKDIR /app

# Install production dependencies
COPY package.json yarn.lock ./
RUN yarn --frozen-lockfile

# Copy application code
COPY . .

# Build the application
RUN yarn build

# Runtime stage
FROM node:16-alpine

WORKDIR /app

# Install production dependencies
COPY --from=builder /app/package.json ./
RUN yarn --frozen-lockfile --production

# Copy the built application from the builder stage
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/build ./build

# Create a non-root user and switch to it
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

# Expose the port
EXPOSE 3001

# Set the working directory
WORKDIR /app

# Start the application
CMD ["node", "dist/index.js"]
```

### 3. Backend Crashes with Exit Code 137 in Production

Exit code 137 typically indicates that the process was killed due to an out-of-memory (OOM) condition. This usually happens when the container's memory usage exceeds the limits set for it. To diagnose this issue:

1. **Check Container Logs**: Look at the logs of the backend container to see if there are any memory-related warnings or errors before the crash.
2. **Memory Limit**: Verify if the memory limit set for the container is too low for the application to run smoothly.
3. **Profiling**: Use tools like `docker stats` or `kubectl top` (if running in a Kubernetes environment) to monitor the memory usage of the container.
4. **Optimization**: Optimize the application code and configuration to reduce memory usage, especially focusing on the backend.

### 4. Zero-Downtime Deployment with Schema Change

When deploying a new version of the application with a schema change (adding a new nullable column), follow these steps:

1. **Create a Migration**: Write a migration script that adds the new column to the existing table.
2. **Deploy the Migration**:
   - Ensure the database schema migration tool (e.g., Knex, Sequelize) is configured to run migrations before starting the application.
   - Deploy the migration to the database before deploying the new version of the application.
3. **Zero-Downtime Deployment**:
   - Use a deployment strategy like Blue/Green or Canary to ensure that the new version can be rolled back without affecting users.
   - Roll out the new version to a small subset of users (Canary deployment) and monitor for issues.
   - Gradually roll out to more users if everything is working fine.
   - Once the new version is stable, switch the routing to the new version and decommission the old version.

By following these steps, you can ensure that the deployment happens smoothly with minimal disruption to users and without any downtime.

*Response time: 115.7s*

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
To build a collaborative document editor, we'll follow the steps outlined and use the `ws` library for WebSocket communication in Node.js. Below is the core implementation based on the requirements:

1. **Connection Handling**
   We will maintain a connection map that associates WebSocket connections with users and documents. Each document will have a list of connected users.

2. **Message Protocol**
   Define the message types in JSON format:
   - `join`: `{ type: 'join', documentId: '...', userId: '...' }`
   - `text-change`: `{ type: 'text-change', userId: '...', position: '...', text: '...' }`
   - `cursor-move`: `{ type: 'cursor-move', userId: '...', position: '...' }`
   - `user-left`: `{ type: 'user-left', userId: '...' }`

3. **Broadcasting**
   When a user makes a change, we need to send the change to all other users in the same document but not back to the user who made the change. We'll maintain a document map to store the state and the list of users.

4. **Reconnection**
   When a user reconnects, we'll send them the latest document state and the current cursor positions of all users in the document.

5. **Conflict Handling**
   If two users edit the exact same position simultaneously, we face the problem of concurrent editing conflicts. Solutions like Operational Transformation (OT) or Conflict-Free Replicated Data Types (CRDT) can be used to resolve such conflicts. For simplicity, we'll acknowledge the problem and suggest OT as a solution.

Here's the server implementation:

```javascript
const WebSocket = require('ws');
const uuid = require('uuid');

const wss = new WebSocket.Server({ port: 8080 });

const connections = new Map(); // Map<WebSocket, { userId: string, documentId: string }>
const documents = new Map();   // Map<string, { text: string, users: Set<string>, cursors: Map<string, number> }>

wss.on('connection', (ws) => {
    ws.on('message', (message) => {
        const data = JSON.parse(message);
        handleMessage(ws, data);
    });

    ws.on('close', () => {
        const { userId, documentId } = connections.get(ws);
        leaveDocument(ws, userId, documentId);
    });
});

function handleMessage(ws, message) {
    switch (message.type) {
        case 'join':
            joinDocument(ws, message.documentId, message.userId);
            break;
        case 'text-change':
            applyTextChange(ws, message.documentId, message.userId, message.position, message.text);
            break;
        case 'cursor-move':
            updateCursor(ws, message.documentId, message.userId, message.position);
            break;
    }
}

function joinDocument(ws, documentId, userId) {
    if (!connections.has(ws)) {
        connections.set(ws, { userId, documentId });

        if (!documents.has(documentId)) {
            documents.set(documentId, { text: '', users: new Set([userId]), cursors: new Map() });
        } else {
            const doc = documents.get(documentId);
            doc.users.add(userId);
            doc.cursors.set(userId, doc.text.length); // Place new user's cursor at the end

            // Send initial document state to new user
            ws.send(JSON.stringify({ type: 'document-state', documentId, text: doc.text, users: Array.from(doc.users), cursors: Array.from(doc.cursors.entries()) }));

            // Broadcast new user's join to existing users
            broadcastToDocument(documentId, { type: 'join', userId, documentId });
        }
    }
}

function applyTextChange(ws, documentId, userId, position, text) {
    if (documents.has(documentId)) {
        const doc = documents.get(documentId);
        if (doc.users.has(userId) && userId !== ws.userId) {
            doc.text = doc.text.slice(0, position) + text + doc.text.slice(position);
            broadcastToDocument(documentId, { type: 'text-change', userId, position, text });
        }
    }
}

function updateCursor(ws, documentId, userId, position) {
    if (documents.has(documentId)) {
        const doc = documents.get(documentId);
        doc.cursors.set(userId, position);
        broadcastToDocument(documentId, { type: 'cursor-move', userId, position });
    }
}

function leaveDocument(ws, userId, documentId) {
    if (documents.has(documentId)) {
        const doc = documents.get(documentId);
        doc.users.delete(userId);
        doc.cursors.delete(userId);

        ws.send(JSON.stringify({ type: 'user-left', userId, documentId }));

        if (doc.users.size === 0) {
            documents.delete(documentId);
        } else {
            broadcastToDocument(documentId, { type: 'user-left', userId, documentId });
        }
        connections.delete(ws);
    }
}

function broadcastToDocument(documentId, message) {
    if (documents.has(documentId)) {
        const doc = documents.get(documentId);
        for (const [ws] of connections.entries()) {
            if (connections.get(ws).documentId === documentId) {
                if (ws.userId !== message.userId) {
                    ws.send(JSON.stringify(message));
                }
            }
        }
    }
}
```

### Explanation:
- **Connection Handling**: We keep track of connections using `connections` map where each key is a WebSocket instance and the value is an object containing the user ID and document ID.
- **Message Protocol**: Messages are JSON objects with a `type` and corresponding data fields. The `join` message registers a user with a document, `text-change` applies a change to the document, and `cursor-move` updates the user's cursor position.
- **Broadcasting**: Changes are broadcast to all users in the same document except the one making the change.
- **Reconnection**: When a user reconnects, they receive the current state of the document and the positions of all users.
- **Conflict Handling**: Concurrent edits are a known issue; solutions like OT can resolve these conflicts, but they are not implemented here.

This implementation provides a basic collaborative document editor with real-time updates and user reconnection support.

*Response time: 140.4s*

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
### 1. GraphQL Schema (SDL)

Here's the SDL for the recipe platform:

```graphql
type Query {
  recipes(filter: RecipeFilter, pagination: Pagination): [Recipe!]!
  recipe(id: ID!): Recipe
}

type Mutation {
  addRating(recipeId: ID!, score: Float!, comment: String): Rating
}

type Subscription {
  recipeRatingAdded(recipeId: ID!): Rating
}

type Recipe {
  id: ID!
  title: String!
  ingredients: [Ingredient!]!
  steps: [String!]!
  author: User!
  tags: [String!]!
  ratings: [Rating!]!
  averageRating: Float!
}

type Ingredient {
  name: String!
  amount: Float!
  unit: String!
}

type User {
  id: ID!
  name: String!
  recipes: [Recipe!]!
}

type Rating {
  id: ID!
  recipe: Recipe!
  score: Float!
  comment: String!
}

input RecipeFilter {
  tag: String
  minRating: Float
}

input Pagination {
  page: Int!
  limit: Int!
}
```

### 2. Resolvers

For the resolvers, let's assume we have a database or data source that we can interact with. For simplicity, I will use placeholder functions where database calls would be made.

#### Query.resolver
```javascript
const recipesResolver = async (parent, { filter, pagination }) => {
  const { page, limit } = pagination;
  const { tag, minRating } = filter;
  // Fetch recipes from the database based on the filter and pagination
  const recipes = await fetchRecipesFromDB({ tag, minRating, page, limit });
  return recipes;
};
```

#### Mutation.resolver
```javascript
const addRatingResolver = async (parent, { recipeId, score, comment }) => {
  // Add a new rating to the recipe in the database
  const newRating = await addRatingToDB(recipeId, score, comment);
  return newRating;
};
```

#### Recipe.averageRating resolver
```javascript
const getAverageRating = (recipe) => {
  const ratings = recipe.ratings;
  const totalScore = ratings.reduce((sum, rating) => sum + rating.score, 0);
  const average = ratings.length > 0 ? totalScore / ratings.length : 0;
  return average;
};
```

### 3. N+1 Problem and DataLoader Fix

**Problem Example:**
Fetching multiple recipes with their respective authors might lead to an N+1 problem. If there are 10 recipes, the resolver would make 1 query to fetch the recipes and then 10 additional queries to fetch each author. This can be very inefficient.

**Fix with DataLoader:**
```javascript
import DataLoader from 'dataloader';

const authorLoader = new DataLoader(async (authorIds) => {
  const authors = await fetchAuthorsByIds(authorIds);
  const authorMap = new Map(authors.map(author => [author.id, author]));
  return authorIds.map(id => authorMap.get(id));
});

const recipesResolver = async (parent, { filter, pagination }) => {
  const { page, limit } = pagination;
  const { tag, minRating } = filter;
  const recipes = await fetchRecipesFromDB({ tag, minRating, page, limit });
  const authorIds = recipes.map(recipe => recipe.authorId);
  const authors = await authorLoader.loadMany(authorIds);
  recipes.forEach(recipe => recipe.author = authors.find(author => author.id === recipe.authorId));
  return recipes;
};
```

### 4. Single Request for Title, Author Name, and Ingredients

A client would write the following query to fetch the title, author name, and the first three ingredients:

```graphql
query {
  recipe(id: "recipe123") {
    title
    author {
      name
    }
    ingredients(first: 3) {
      name
      amount
      unit
    }
  }
}
```

### 5. When to Choose GraphQL Over REST and Vice Versa

**GraphQL Over REST:**
- **Complex Data Structures:** When a client needs to fetch complex data structures in a single request, GraphQL is superior.
- **Data Aggregation:** For applications where data needs to be aggregated from multiple sources, GraphQL's ability to specify exactly what data is needed reduces the number of requests and improves performance.
- **API Evolution:** GraphQL allows for a more flexible API evolution without breaking existing clients, as clients specify exactly what they need rather than following a rigid contract.

**REST Over GraphQL:**
- **Simplicity:** For simpler applications or APIs where the data structure is straightforward, REST can be more straightforward to implement and understand.
- **Tooling and Browser Support:** REST has more mature tooling and better browser support, making it easier to test and debug.
- **Caching:** REST provides built-in caching mechanisms (via HTTP caching) which can be more straightforward to implement and manage compared to custom caching solutions in GraphQL.

*Response time: 109.5s*

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
To implement the UI layout described using CSS and HTML, we will use a combination of Flexbox and CSS Grid. Flexbox is ideal for the main layout structure to ensure that elements take up the correct space and are responsive. CSS Grid will be used within the main content area to manage the responsive card layout.

### HTML Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Responsive Layout</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header class="header">
        <h1>Header</h1>
    </header>
    <div class="container">
        <aside class="sidebar">
            <h2>Sidebar</h2>
            <div class="scroll-content">
                <p>Scrolling content...</p>
                <p>Scrolling content...</p>
                <p>Scrolling content...</p>
                <p>Scrolling content...</p>
            </div>
        </aside>
        <main class="main-content">
            <div class="card-grid">
                <article class="card">
                   

*Response time: 27.6s*

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
Designing a real-time notification system for a project management tool involves several considerations, including real-time communication, offline handling, background task scheduling, and scalability. Below is a detailed design for each aspect of the system.

### 1. Transport Mechanism for Real-Time Notifications

For real-time notifications, WebSocket is the most appropriate choice. Here's why:

- **WebSocket**: Provides full-duplex communication channels over a single, long-lived connection. This ensures low latency and efficient resource usage, making it ideal for real-time applications.
- **Server-Sent Events (SSE)**: While SSE allows servers to push updates to clients, it is unidirectional, which may limit the complexity of the notification system.
- **Polling**: Inefficient for real-time notifications as it requires frequent requests from the client, leading to increased server load and higher latency.
- **Push Notifications**: Useful for mobile devices but requires a different setup compared to web applications.

**Why WebSocket?**
- **Latency**: WebSocket has the lowest latency among the options, ensuring immediate delivery of notifications.
- **Bandwidth Efficiency**: Maintains a single, long-lived connection, reducing overhead and improving performance.
- **Bi-directional Communication**: Allows the server to push notifications to the client and also allows clients to send messages back to the server if needed.

### 2. Database Schema for Notifications

For storing notifications, a simple yet flexible schema is necessary. Consider the following schema:

```sql
CREATE TABLE notifications (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    task_id BIGINT NOT NULL,
    type ENUM('task_assigned', 'comment_added', 'deadline_approaching') NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);
```

- `user_id`: The ID of the user who receives the notification.
- `task_id`: The ID of the task related to the notification.
- `type`: The type of notification (e.g., task assigned, comment added, deadline approaching).
- `message`: A text message describing the notification.
- `is_read`: Boolean indicating whether the user has read the notification.
- `created_at`: The timestamp when the notification was created.

### 3. Handling Offline Users

To handle offline users:

- **Notification Queue**: Store notifications in the database or a message queue system (like Redis or RabbitMQ) until the user becomes online.
- **Batch Processing**: When a user comes online, use a script or server-side logic to fetch and deliver any missed notifications.

### 4. Implementing Deadline Check

To check deadlines every hour:

- **Cron Job**: Use a cron job to run a script that checks all tasks for deadlines within 24 hours.
- **Event-Driven**: Alternatively, use an event-driven architecture with a scheduler like Celery to trigger deadline checks periodically.

**Implementation Example (Cron Job)**:

1. **Create a Script**: Write a Python script that queries the database for tasks with deadlines within 24 hours and sends notifications using the WebSocket connection.
2. **Set Up Cron Job**: Configure a cron job to run the script hourly.

**Example Cron Job Entry**:
```cron
0 * * * * /path/to/python /path/to/your_script.py
```

### 5. Scaling the Notification System

For scaling the system to handle 100,000 concurrent users:

- **WebSocket Server**: Use a scalable WebSocket server like `nginx` with `uwsgi` or a dedicated WebSocket server like `wsproxy`.
- **Load Balancing**: Distribute WebSocket connections across multiple servers using load balancers.
- **Database Sharding**: If the database becomes a bottleneck, consider sharding it to distribute data across multiple servers.
- **Caching**: Implement caching (e.g., Redis) to reduce the load on the database for frequently accessed data.
- **Asynchronous Processing**: Use asynchronous programming techniques and message queues (e.g., RabbitMQ, Kafka) to handle tasks like deadline checking efficiently.

**Scalability Considerations**:
- Ensure WebSocket connections are managed efficiently to handle large numbers of concurrent users.
- Monitor and optimize the WebSocket server's performance to ensure low latency and high throughput.
- Use distributed systems principles to ensure the system can scale horizontally.

This design ensures that the project management tool can handle real-time notifications effectively, even as the number of users grows significantly.

*Response time: 96.1s*

---
