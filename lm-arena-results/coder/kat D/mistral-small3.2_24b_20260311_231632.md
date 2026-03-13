# Model: mistral-small3.2:24b
**Test Date:** 2026-03-12 00:56:43
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
# REST API Design for Multi-Tenant SaaS Project Management Tool

## 1. Endpoints

### Workspace Endpoints
- `GET /api/workspaces` - List all workspaces for the authenticated user
- `POST /api/workspaces` - Create a new workspace
- `GET /api/workspaces/{workspaceId}` - Get workspace details
- `PUT /api/workspaces/{workspaceId}` - Update workspace
- `DELETE /api/workspaces/{workspaceId}` - Delete workspace

### Project Endpoints
- `GET /api/workspaces/{workspaceId}/projects` - List all projects in a workspace
- `POST /api/workspaces/{workspaceId}/projects` - Create a new project
- `GET /api/workspaces/{workspaceId}/projects/{projectId}` - Get project details
- `PUT /api/workspaces/{workspaceId}/projects/{projectId}` - Update project
- `DELETE /api/workspaces/{workspaceId}/projects/{projectId}` - Delete project

### Task Endpoints
- `GET /api/workspaces/{workspaceId}/projects/{projectId}/tasks` - List all tasks in a project
- `POST /api/workspaces/{workspaceId}/projects/{projectId}/tasks` - Create a new task
- `GET /api/workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}` - Get task details
- `PUT /api/workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}` - Update task
- `DELETE /api/workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}` - Delete task
- `PATCH /api/workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/status` - Update task status

### User Endpoints
- `GET /api/users` - List all users in all workspaces the authenticated user belongs to
- `POST /api/users` - Invite a new user
- `GET /api/users/{userId}` - Get user details
- `PUT /api/users/{userId}` - Update user
- `DELETE /api/users/{userId}` - Remove user

### Comment Endpoints
- `GET /api/workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/comments` - List all comments for a task
- `POST /api/workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/comments` - Add a new comment
- `GET /api/workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/comments/{commentId}` - Get comment details
- `PUT /api/workspaces/{workspaceId

*Response time: 128.4s*

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
I'll implement the endpoint with all the requirements. Here's the complete solution:

1. First, let's create the validation schema using Zod:

```typescript
// src/schemas/taskUpdate.schema.ts
import { z } from 'zod';

export const taskUpdateSchema = z.object({
  title: z.string().min(1).max(200).optional(),
  status: z.enum(['todo', 'in_progress', 'done', 'cancelled']).optional(),
  assignee_id: z.number().int().positive().nullable().optional(),
  due_date: z.string().regex(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(.\d+)?Z$/).nullable().optional(),
});

export type TaskUpdateInput = z.infer<typeof taskUpdateSchema>;
```

2. Now, let's implement the handler:

```typescript
// src/controllers/tasks.controller.ts
import { Request, Response, NextFunction } from 'express';
import { taskUpdateSchema } from '../schemas/taskUpdate.schema';
import { Task, Workspace } from '../models'; // Assuming you have these models
import { AppError } from '../utils/AppError';

export const updateTask = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const workspaceId = parseInt(req.params.workspaceId);
    const taskId = parseInt(req.params.taskId);

    // Validate IDs are integers
    if (isNaN(workspaceId) || isNaN(taskId)) {
      return next(new AppError('Workspace ID and Task ID must be integers', 400));
    }

    // Validate input data
    const validatedData = taskUpdateSchema.parse(req.body);

    // Check if task exists in the workspace
    const task = await Task.findOne({
      where: { id: taskId, workspaceId },
      include: ['subtasks', 'assignee']
    });

    if (!task) {
      return next(new AppError('Task not found in workspace', 404));
    }

    // Check if assignee exists in workspace (if provided)
    if (validatedData.assignee_id !== undefined && validatedData.assignee_id !== null) {
      const assigneeExists = await Workspace.hasMember(req.params.workspaceId, validatedData.assignee_id);
      if (!assigneeExists) {
        return next(new AppError('Assignee is not a member of this workspace', 400));
      }
    }

    // Check for open subtasks if status is being set to cancelled
    if (validatedData.status === 'cancelled' && task.subtasks.some(subtask => subtask.status !== 'done')) {
      return next(new AppError('Cannot cancel task with open subtasks', 409));
    }

    // Update the task
    await task.update(validatedData);

    res.json({
      success: true,
      data: {
        task: {
          id: task.id,
          title: task.title,
          status: task.status,
          assignee_id: task.assignee_id,
          due_date: task.due_date,
          workspaceId: task.workspaceId
        }
      }
    });
  } catch (error) {
    next(error);
  }
};
```

3. Let's create the error middleware:

```typescript
// src/middleware/error.middleware.ts
import { Request, Response, NextFunction } from 'express';
import { ZodError } from 'zod';

export const errorHandler = (err: any, req: Request, res: Response, next: NextFunction) => {
  console.error(err.stack);

  if (err instanceof ZodError) {
    const errors = err.errors.map(error => ({
      field: error.path.join('.'),
      message: error.message
    }));
    return res.status(400).json({
      success: false,
      errors
    });
  }

  res.status(err.statusCode || 500).json({
    success: false,
    message: err.message || 'Something went wrong'
  });
};
```

4. And the AppError utility:

```typescript
// src/utils/AppError.ts
export class AppError extends Error {
  public statusCode: number;
  public isOperational: boolean;

  constructor(message: string, statusCode: number = 500, isOperational: boolean = true) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = isOperational;
    Error.captureStackTrace(this, this.constructor);
  }
}
```

5. Finally, let's write the unit tests:

```typescript
// src/controllers/tasks.controller.test.ts
import { updateTask } from './tasks.controller';
import { Task, Workspace } from '../models';
import { AppError } from '../utils/AppError';
import { Request, Response } from 'express';

jest.mock('../models');

describe('updateTask', () => {
  const mockRequest = (params: any, body: any) => ({
    params,
    body
  }) as Request;

  const mockResponse = () => {
    const res: Partial<Response> = {};
    res.status = jest.fn().mockReturnThis();
    res.json = jest.fn().mockReturnThis();
    return res as Response;
  };

  const mockNext = jest.fn();

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should update task successfully', async () => {
    const task = {
      id: 1,
      title: 'Old title',
      status: 'todo',
      assignee_id: null,
      due_date: null,
      workspaceId: 1,
      subtasks: [],
      update: jest.fn().mockResolvedValue(true)
    };

    (Task.findOne as jest.Mock).mockResolvedValue(task);
    (Workspace.hasMember as jest.Mock).mockResolvedValue(true);

    const req = mockRequest(
      { workspaceId: '1', taskId: '1' },
      { title: 'New title' }
    );
    const res = mockResponse();

    await updateTask(req, res, mockNext);

    expect(Task.findOne).toHaveBeenCalledWith({
      where: { id: 1, workspaceId: 1 },
      include: ['subtasks', 'assignee']
    });
    expect(task.update).toHaveBeenCalledWith({ title: 'New title' });
    expect(res.status).toHaveBeenCalledWith(200);
    expect(res.json).toHaveBeenCalledWith({
      success: true,
      data: {
        task: {
          id: 1,
          title: 'New title',
          status: 'todo',
          assignee_id: null,
          due_date: null,
          workspaceId: 1
        }
      }
    });
  });

  it('should return 400 for invalid IDs', async () => {
    const req = mockRequest(
      { workspaceId: 'invalid', taskId: '1' },
      { title: 'New title' }
    );
    const res = mockResponse();

    await updateTask(req, res, mockNext);

    expect(mockNext).toHaveBeenCalledWith(
      expect.objectContaining({
        statusCode: 400,
        message: 'Workspace ID and Task ID must be integers'
      })
    );
  });

  it('should return 404 if task not found', async () => {
    (Task.findOne as jest.Mock).mockResolvedValue(null);

    const req = mockRequest(
      { workspaceId: '1', taskId: '1' },
      { title: 'New title' }
    );
    const res = mockResponse();

    await updateTask(req, res, mockNext);

    expect(mockNext).toHaveBeenCalledWith(
      expect.objectContaining({
        statusCode: 404,
        message: 'Task not found in workspace'
      })
    );
  });

  it('should return 409 if trying to cancel task with open subtasks', async () => {
    const task = {
      id: 1,
      title: 'Old title',
      status: 'todo',
      assignee_id: null,
      due_date: null,
      workspaceId: 1,
      subtasks: [{ status: 'in_progress' }],
      update: jest.fn().mockResolvedValue(true)
    };

    (Task.findOne as jest.Mock).mockResolvedValue(task);

    const req = mockRequest(
      { workspaceId: '1', taskId: '1' },
      { status: 'cancelled' }
    );
    const res = mockResponse();

    await updateTask(req, res, mockNext);

    expect(mockNext).toHaveBeenCalledWith(
      expect.objectContaining({
        statusCode: 409,
        message: 'Cannot cancel task with open subtasks'
      })
    );
  });
});
```

6. Finally, you'll need to set up your routes:

```typescript
// src/routes/tasks.routes.ts
import { Router } from 'express';
import { updateTask } from '../controllers/tasks.controller';
import { errorHandler } from '../middleware/error.middleware';

const router = Router();

router.patch('/workspaces/:workspaceId/tasks/:taskId', updateTask);

router.use(errorHandler);

export default router;
```

This implementation covers all the requirements:
- Partial updates with only provided fields changing
- Field-level validation using Zod
- ID validation
- Workspace membership checks
- Subtask validation for cancellation
- Proper error handling and status codes
- Unit tests covering success, validation error, 404, and 409 cases

The solution assumes you have Sequelize models for Task and Workspace, and that you have a method `Workspace.hasMember()` to check if a user is a member of a workspace. You may need to adjust these parts to match your actual implementation.

*Response time: 496.5s*

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
# Authentication System in Node.js + Express + TypeScript

Here's a complete implementation of an authentication system with all the requirements you specified:

## 1. Setup and Dependencies

First, install the required dependencies:
```bash
npm install express express-async-errors cors cookie-parser jsonwebtoken bcryptjs dotenv
npm install --save-dev typescript @types/express @types/cors @types/cookie-parser @types/jsonwebtoken @types/bcryptjs ts-node nodemon
```

## 2. Project Structure

```
src/
├── config/
│   └── config.ts
├── controllers/
│   ├── auth.controller.ts
│   └── user.controller.ts
├── middlewares/
│   └── auth.middleware.ts
├── models/
│   └── user.model.ts
├── routes/
│   ├── auth.routes.ts
│   └── user.routes.ts
├── types/
│   └── custom.d.ts
├── utils/
│   └── jwt.utils.ts
├── app.ts
└── server.ts
```

## 3. Implementation

### config/config.ts
```typescript
import dotenv from 'dotenv';

dotenv.config();

const config = {
  jwt: {
    accessTokenSecret: process.env.ACCESS_TOKEN_SECRET || 'access-secret',
    refreshTokenSecret: process.env.REFRESH_TOKEN_SECRET || 'refresh-secret',
    accessTokenExpiry: process.env.ACCESS_TOKEN_EXPIRY || '15m',
    refreshTokenExpiry: process.env.REFRESH_TOKEN_EXPIRY || '7d',
  },
  bcrypt: {
    saltRounds: 12,
  },
};

export default config;
```

### models/user.model.ts
```typescript
import { Schema, model } from 'mongoose';
import bcrypt from 'bcryptjs';
import config from '../config/config';

interface IUser {
  email: string;
  password: string;
  role: string;
  comparePassword(candidatePassword: string): Promise<boolean>;
}

const userSchema = new Schema<IUser>(
  {
    email: { type: String, required: true, unique: true },
    password: { type: String, required: true },
    role: { type: String, default: 'user' },
  },
  { timestamps: true }
);

userSchema.pre('save', async function (next) {
  if (!this.isModified('password')) return next();

  const salt = await bcrypt.genSalt(config.bcrypt.saltRounds);
  this.password = await bcrypt.hash(this.password, salt);
  next();
});

userSchema.methods.comparePassword = async function (candidatePassword: string) {
  return await bcrypt.compare(candidatePassword, this.password);
};

export const User = model<IUser>('User', userSchema);
```

### utils/jwt.utils.ts
```typescript
import jwt from 'jsonwebtoken';
import config from '../config/config';

interface JwtPayload {
  userId: string;
  email: string;
  role: string;
  iat?: number;
  exp?: number;
}

export const generateAccessToken = (payload: JwtPayload) => {
  return jwt.sign(payload, config.jwt.accessTokenSecret, {
    expiresIn: config.jwt.accessTokenExpiry,
  });
};

export const generateRefreshToken = (payload: JwtPayload) => {
  return jwt.sign(payload, config.jwt.refreshTokenSecret, {
    expiresIn: config.jwt.refreshTokenExpiry,
  });
};

export const verifyAccessToken = (token: string) => {
  return jwt.verify(token, config.jwt.accessTokenSecret) as JwtPayload;
};

export const verifyRefreshToken = (token: string) => {
  return jwt.verify(token, config.jwt.refreshTokenSecret) as JwtPayload;
};
```

### middlewares/auth.middleware.ts
```typescript
import { Request, Response, NextFunction } from 'express';
import { verifyAccessToken } from '../utils/jwt.utils';

export const authMiddleware = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const token = req.headers.authorization?.split(' ')[1];

    if (!token) {
      return res.status(401).json({ message: 'No token provided' });
    }

    const decoded = verifyAccessToken(token);
    req.user = decoded;
    next();
  } catch (error) {
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({
        message: 'Token expired',
        error: 'TokenExpiredError',
        details: error.message
      });
    }
    if (error.name === 'JsonWebTokenError') {
      return res.status(401).json({
        message: 'Invalid token',
        error: 'JsonWebTokenError',
        details: error.message
      });
    }
    return res.status(401).json({ message: 'Authentication failed', error: error.message });
  }
};
```

### controllers/auth.controller.ts
```typescript
import { Request, Response } from 'express';
import { User } from '../models/user.model';
import { generateAccessToken, generateRefreshToken } from '../utils/jwt.utils';

export const register = async (req: Request, res: Response) => {
  try {
    const { email, password } = req.body;

    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(400).json({ message: 'User already exists' });
    }

    const user = new User({ email, password });
    await user.save();

    res.status(201).json({
      id: user._id,
      email: user.email,
      role: user.role,
    });
  } catch (error) {
    res.status(500).json({ message: 'Registration failed', error: error.message });
  }
};

export const login = async (req: Request, res: Response) => {
  try {
    const { email, password } = req.body;

    const user = await User.findOne({ email });
    if (!user) {
      return res.status(401).json({ message: 'Invalid credentials' });
    }

    const isMatch = await user.comparePassword(password);
    if (!isMatch) {
      return res.status(401).json({ message: 'Invalid credentials' });
    }

    const accessToken = generateAccessToken({
      userId: user._id.toString(),
      email: user.email,
      role: user.role,
    });

    const refreshToken = generate

*Response time: 320.2s*

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
Let's break down each of your requirements and implement them step by step. I'll provide the necessary code, Redis data structures, and explanations for each part.

### 1. POST /auth/refresh
This endpoint will use the refresh token from the cookie to issue a new access token and rotate the refresh token.

### 2. POST /auth/logout
This endpoint will invalidate the refresh token and clear the cookie.

### 3. Redis-based Token Store
We'll use Redis to store refresh tokens with a TTL (Time To Live) strategy. The data structure will be a Redis Hash where the key is the refresh token and the value is the user ID and other metadata.

### 4. Token Reuse Detection
We'll implement a mechanism to detect if a refresh token is used more than once. This can be done by storing the last used timestamp and comparing it with the current time.

### 5. Session Invalidation on Password Change
When a user changes their password, we'll invalidate all their existing sessions by deleting all their refresh tokens from Redis.

### 6. Token Blacklisting vs. Token Rotation
- **Token Blacklisting**: Maintain a list of invalidated tokens (e.g., in Redis) and check against this list for every request. This is useful for immediate revocation but can be resource-intensive for high-traffic applications.
- **Token Rotation**: Issue a new token and invalidate the old one. This is more scalable but doesn't provide immediate revocation.

Let's implement these requirements.

#### Redis Data Structure
We'll use a Redis Hash for each refresh token with the following fields:
- `userId`: The ID of the user the token belongs to.
- `lastUsed`: The timestamp of the last time the token was used.
- `expiresAt`: The expiration timestamp of the token.

#### TTL Strategy
We'll set a TTL on the Redis key to automatically expire the token when it's no longer valid.

#### Token Reuse Detection
We'll check the `lastUsed` field and compare it with the current time. If the token is used more than once within a short time frame, we'll consider it a reuse attempt and invalidate the token.

#### Session Invalidation on Password Change
We'll delete all refresh tokens associated with the user from Redis.

### Implementation

#### 1. POST /auth/refresh
```javascript
const express = require('express');
const jwt = require('jsonwebtoken');
const redis = require('redis');
const cookieParser = require('cookie-parser');

const app = express();
app.use(express.json());
app.use(cookieParser());

const redisClient = redis.createClient();
redisClient.connect().catch(console.error);

const ACCESS_TOKEN_SECRET = 'your_access_token_secret';
const REFRESH_TOKEN_SECRET = 'your_refresh_token_secret';
const REFRESH_TOKEN_EXPIRY = '7d'; // 7 days
const ACCESS_TOKEN_EXPIRY = '15m'; // 15 minutes

app.post('/auth/refresh', async (req, res) => {
  const refreshToken = req.cookies.refreshToken;

  if (!refreshToken) {
    return res.status(401).json({ message: 'Refresh token is missing' });
  }

  try {
    // Verify the refresh token
    const decoded = jwt.verify(refreshToken, REFRESH_TOKEN_SECRET);

    // Check if the token is in Redis
    const tokenData = await redisClient.hGetAll(`refresh_token:${refreshToken}`);

    if (!tokenData) {
      return res.status(401).json({ message: 'Invalid refresh token' });
    }

    // Check for token reuse
    const lastUsed = parseInt(tokenData.lastUsed);
    const currentTime = Math.floor(Date.now() / 1000);

    if (lastUsed > 0 && currentTime - lastUsed < 5) { // 5 seconds threshold
      await redisClient.del(`refresh_token:${refreshToken}`);
      return res.status(401).json({ message: 'Token reuse detected' });
    }

    // Update the last used timestamp
    await redisClient.hSet(`refresh_token:${refreshToken}`, {
      lastUsed: currentTime.toString(),
    });

    // Issue a new access token
    const accessToken = jwt.sign(
      { userId: decoded.userId },
      ACCESS_TOKEN_SECRET,
      { expiresIn: ACCESS_TOKEN_EXPIRY }
    );

    // Issue a new refresh token
    const newRefreshToken = jwt.sign(
      { userId: decoded.userId },
      REFRESH_TOKEN_SECRET,
      { expiresIn: REFRESH_TOKEN_EXPIRY }
    );

    // Store the new refresh token in Redis
    await redisClient.hSet(`refresh_token:${newRefreshToken}`, {
      userId: decoded.userId,
      lastUsed: '0',
      expiresAt: Math.floor(Date.now() / 1000 + 7 * 24 * 60 * 60).toString(),
    });

    // Set TTL for the new refresh token
    await redisClient.expire(`refresh_token:${newRefreshToken}`, 7 * 24 * 60 * 60);

    // Invalidate the old refresh token
    await redisClient.del(`refresh_token:${refreshToken}`);

    // Set the new refresh token in the cookie
    res.cookie('refreshToken', newRefreshToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: 7 * 24 * 60 * 60 * 1000,
    });

    res.json({ accessToken });
  } catch (error) {
    console.error(error);
    res.status(401).json({ message: 'Invalid refresh token' });
  }
});
```

#### 2. POST /auth/logout
```javascript
app.post('/auth/logout', async (req, res) => {
  const refreshToken = req.cookies.refreshToken;

  if (!refreshToken) {
    return res.status(400).json({ message: 'No refresh token provided' });
  }

  try {
    // Invalidate the refresh token
    await redisClient.del(`refresh_token:${refreshToken}`);

    // Clear the cookie
    res.clearCookie('refreshToken', {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
    });

    res.json({ message: 'Logged out successfully' });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Error during logout' });
  }
});
```

#### 3. Redis Data Structure and TTL Strategy
As mentioned earlier, we'll use a Redis Hash for each refresh token with the following fields:
- `userId`: The ID of the user the token belongs to.
- `lastUsed`: The timestamp of the last time the token was used.
- `expiresAt`: The expiration timestamp of the token.

We'll set a TTL on the Redis key to automatically expire the token when it's no longer valid.

#### 4. Token Reuse Detection
We've already implemented token reuse detection in the `/auth/refresh` endpoint by checking the `lastUsed` field and comparing it with the current time.

#### 5. Session Invalidation on Password Change
We'll add an endpoint to handle password changes and invalidate all existing sessions.

```javascript
app.post('/auth/change-password', async (req, res) => {
  const { userId, oldPassword, newPassword } = req.body;

  // Verify the old password (implementation depends on your user model)
  // ...

  // Invalidate all existing sessions
  const sessionKeys = await redisClient.keys(`refresh_token:*`);
  for (const key of sessionKeys) {
    const tokenData = await redisClient.hGetAll(key);
    if (tokenData.userId === userId) {
      await redisClient.del(key);
    }
  }

  // Update the password (implementation depends on your user model)
  // ...

  res.json({ message: 'Password changed successfully' });
});
```

#### 6. Token Blacklisting vs. Token Rotation
- **Token Blacklisting**: Maintain a list of invalidated tokens (e.g., in Redis) and check against this list for every request. This is useful for immediate revocation but can be resource-intensive for high-traffic applications.
- **Token Rotation**: Issue a new token and invalidate the old one. This is more scalable but doesn't provide immediate revocation.

**When to use each:**
- Use **token blacklisting** when you need immediate revocation of tokens, such as when a user logs out or changes their password.
- Use **token rotation** for regular token refreshes to maintain security without the overhead of blacklisting.

In our implementation, we're using a combination of both:
- We rotate refresh tokens on each use to maintain security.
- We invalidate all sessions on password change to ensure immediate revocation.

This provides a balance between security and scalability.

*Response time: 447.6s*

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
# DataTable Component Implementation

Here's a complete implementation of a DataTable component in React + TypeScript that meets all your requirements:

## 1. TypeScript Interface for Props

```typescript
import React, { ReactNode } from 'react';

export interface Column<T> {
  key: string;
  header: string;
  width?: string | number;
  sortable?: boolean;
  renderCell?: (row: T) => ReactNode;
}

export interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  rowKey?: string;
  pagination?: {
    pageSize?: number;
    pageSizeOptions?: number[];
    controlled?: boolean;
    currentPage?: number;
    onPageChange?: (page: number) => void;
  };
  selection?: {
    controlled?: boolean;
    selectedRows?: T[];
    onSelectionChange?: (selectedRows: T[]) => void;
    rowKey?: string;
  };
  sortable?: {
    controlled?: boolean;
    sortColumn?: string;
    sortDirection?: 'asc' | 'desc';
    onSortChange?: (column: string, direction: 'asc' | 'desc' | null) => void;
  };
  onRowClick?: (row: T) => void;
}
```

## 2. Complete Component Implementation

```typescript
import React, { useState, useMemo, useCallback } from 'react';
import { Column, DataTableProps } from './types';

const DataTable = <T,>({
  columns,
  data,
  rowKey = 'id',
  pagination = {
    pageSize: 10,
    pageSizeOptions: [10, 25, 50],
  },
  selection = {
    controlled: false,
  },
  sortable = {
    controlled: false,
  },
  onRowClick,
}: DataTableProps<T>) => {
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(pagination.pageSize || 10);

  // Selection state
  const [selectedRows, setSelectedRows] = useState<T[]>([]);

  // Sorting state
  const [sortColumn, setSortColumn] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc' | null>('asc');

  // Calculate pagination data
  const totalPages = Math.ceil(data.length / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = Math.min(startIndex + pageSize, data.length);
  const paginatedData = data.slice(startIndex, endIndex);

  // Handle page change
  const handlePageChange = (page: number) => {
    if (pagination.controlled && pagination.onPageChange) {
      pagination.onPageChange(page);
    } else {
      setCurrentPage(page);
    }
  };

  // Handle page size change
  const handlePageSizeChange = (size: number) => {
    setPageSize(size);
    setCurrentPage(1);
  };

  // Handle row selection
  const handleRowSelection = (row: T, isSelected: boolean) => {
    if (selection.controlled && selection.onSelectionChange) {
      const newSelectedRows = isSelected
        ? [...selectedRows, row]
        : selectedRows.filter((r) => r[rowKey] !== row[rowKey]);
      selection.onSelectionChange(newSelectedRows);
    } else {
      setSelectedRows((prev) =>
        isSelected
          ? [...prev, row]
          : prev.filter((r) => r[rowKey] !== row[rowKey])
      );
    }
  };

  // Handle select all
  const handleSelectAll = (isSelected: boolean) => {
    if (selection.controlled && selection.onSelectionChange) {
      const newSelectedRows = isSelected ? [...data] : [];
      selection.onSelectionChange(newSelectedRows);
    } else {
      setSelectedRows(isSelected ? [...data] : []);
    }
  };

  // Handle sorting
  const handleSort = (columnKey: string) => {
    if (!sortable.controlled || !sortable.onSortChange) {
      if (sortColumn === columnKey) {
        if (sortDirection === 'asc') {
          setSortDirection('desc');
        } else if (sortDirection === 'desc') {
          setSortColumn(null);
          setSortDirection(null);
        } else {
          setSortDirection('asc');
        }
      } else {
        setSortColumn(columnKey);
        setSortDirection('asc');
      }
    } else {
      let newDirection: 'asc' | 'desc' | null = 'asc';
      if (sortable.sortColumn === columnKey) {
        if (sortable.sortDirection === 'asc') {
          newDirection = 'desc';
        } else {
          newDirection = null;
        }
      }
      sortable.onSortChange(columnKey, newDirection);
    }
  };

  // Sort data
  const sortedData = useMemo(() => {
    if (!sortColumn) return data;

    return [...data].sort((a, b) => {
      const aValue = a[sortColumn as keyof T];
      const bValue = b[sortColumn as keyof T];

      if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
  }, [data, sortColumn, sortDirection]);

  // Check if all rows are selected
  const allRowsSelected = useMemo(() => {
    if (selectedRows.length === 0) return false;
    if (selectedRows.length === data.length) return true;
    return false;
  }, [selectedRows, data]);

  // Check if some rows are selected
  const someRowsSelected = useMemo(() => {
    return selectedRows.length > 0 && selectedRows.length < data.length;
  }, [selectedRows, data]);

  // Check if row is selected
  const isRowSelected = useCallback(
    (row: T) => {
      return selectedRows.some((r) => r[rowKey] === row[rowKey]);
    },
    [selectedRows, rowKey]
  );

  return (
    <div className="datatable-container">
      <div className="datatable-table-container">
        <table className="datatable">
          <thead>
            <tr>
              {selection && (
                <th style={{ width: '50px' }}>
                  <input
                    type="checkbox"
                    checked={allRowsSelected}
                    indeterminate={someRowsSelected}
                    onChange={(e) => handleSelectAll(e.target.checked)}
                  />
                </th>
              )}
              {columns.map((column) => (
                <th
                  key={column.key}
                  style={{ width: column.width }}
                  onClick={() => column.sortable && handleSort(column.key)}
                >
                  <div className="datatable-header">
                    {column.header}
                    {column.sortable && sortColumn === column.key && (
                      <span className="datatable-sort-icon">
                        {sortDirection === 'asc' ? '↑' : '↓'}
                      </span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paginatedData.map((row) => (
              <tr
                key={row[rowKey as keyof T]}
                onClick={() => onRowClick && onRowClick(row)}
                className={onRowClick ? 'datatable-clickable-row' : ''}
              >
                {selection && (
                  <td>
                    <input
                      type="checkbox"
                      checked={isRowSelected(row)}
                      onChange={(e) => handleRowSelection(row, e.target.checked)}
                    />
                  </td>
                )}
                {columns.map((column) => (
                  <td key={`${row[rowKey as keyof T]}-${column.key}`}>
                    {column.renderCell ? column.renderCell(row) : row[column.key as keyof T]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {pagination && (
        <div className="datatable-pagination">
          <div className="datatable-page-size">
            <label>Rows per page:</label>
            <select
              value={pageSize}
              onChange={(e) => handlePageSizeChange(Number(e.target.value))}
            >
              {pagination.pageSizeOptions?.map((size) => (
                <option key={size} value={size}>
                  {size}
                </option>
              ))}
            </select>
          </div>
          <div className="datatable-page-controls">
            <button
              disabled={currentPage === 1}
              onClick={() => handlePageChange(currentPage - 1)}
            >
              Previous
            </button>
            <span>
              Page {currentPage} of {totalPages}
            </span>
            <button
              disabled={currentPage === totalPages}
              onClick={() => handlePageChange(currentPage + 1)}
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default DataTable;
```

## 3. Usage Example

```typescript
import React from 'react';
import DataTable from './DataTable';

// Define your data type
interface User {
  id: number;
  name: string;
  email: string;
  status: 'active' | 'inactive';
}

// Sample data
const users: User[] = [
  { id: 1, name: 'John Doe', email: 'john@example.com', status: 'active' },
  { id: 2, name: 'Jane Smith', email: 'jane@example.com', status: 'inactive' },
  { id: 3, name: 'Bob Johnson', email: 'bob@example.com', status: 'active' },
  { id: 4, name: 'Alice Williams', email: 'alice@example.com', status: 'inactive' },
  { id: 5, name: 'Charlie Brown', email: 'charlie@example.com', status: 'active' },
  { id: 6, name: 'Diana Prince', email: 'diana@example.com', status: 'active' },
  { id: 7, name: 'Bruce Wayne', email: 'bruce@example.com', status: 'inactive' },
  { id: 8, name: 'Clark Kent', email: 'clark@example.com', status: 'active' },
  { id: 9, name: 'Peter Parker', email: 'peter@example.com', status: 'active' },
  { id: 10, name: 'Tony Stark', email: 'tony@example.com', status: 'inactive' },
];

const App = () => {
  const columns: Column<User>[] = [
    {
      key: 'name',
      header: 'Name',
      sortable: true,
    },
    {
      key: 'email',
      header: 'Email',
      sortable: true,
    },
    {
      key: 'status',
      header: 'Status',
      sortable: true,
      renderCell: (row) => (
        <div className={`status-badge ${

*Response time: 570.2s*

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
Here's a complete implementation of the search feature in React using hooks:

### 1. Custom Hook `useSearch`

```jsx
import { useState, useEffect, useCallback } from 'react';

const useSearch = () => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [cache, setCache] = useState(new Map());
  const [abortController, setAbortController] = useState(null);

  const fetchResults = useCallback(async (query) => {
    if (!query.trim()) {
      setResults([]);
      return;
    }

    // Check cache first
    const cachedResult = cache.get(query);
    if (cachedResult) {
      setResults(cachedResult);
      return;
    }

    // Create new abort controller for this request
    const controller = new AbortController();
    setAbortController(controller);

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`, {
        signal: controller.signal
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();

      // Only update state if this request hasn't been aborted
      if (!controller.signal.aborted) {
        setResults(data);
        // Cache the result
        setCache(prev => {
          const newCache = new Map(prev);
          newCache.set(query, data);
          return newCache;
        });
      }
    } catch (err) {
      if (err.name !== 'AbortError') {
        setError(err.message);
      }
    } finally {
      if (!controller.signal.aborted) {
        setLoading(false);
      }
    }
  }, [cache]);

  // Clean up any in-flight requests when the component unmounts or query changes
  useEffect(() => {
    return () => {
      if (abortController) {
        abortController.abort();
      }
    };
  }, [abortController]);

  // Cache cleanup - remove entries older than 5 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      const now = Date.now();
      cache.forEach((value, key) => {
        if (now - value.timestamp > 5 * 60 * 1000) {
          cache.delete(key);
        }
      });
    }, 60 * 1000); // Check every minute

    return () => clearInterval(interval);
  }, [cache]);

  return { results, loading, error, fetchResults };
};

export default useSearch;
```

### 2. SearchPage Component

```jsx
import React, { useState, useEffect } from 'react';
import useSearch from './useSearch';

const SearchPage = () => {
  const [query, setQuery] = useState('');
  const { results, loading, error, fetchResults } = useSearch();

  // Debounce the search input
  useEffect(() => {
    const timer = setTimeout(() => {
      fetchResults(query);
    }, 300);

    return () => {
      clearTimeout(timer);
    };
  }, [query, fetchResults]);

  // Sync URL with search query
  useEffect(() => {
    const url = new URL(window.location);
    if (query) {
      url.searchParams.set('q', query);
    } else {
      url.searchParams.delete('q');
    }
    window.history.pushState({}, '', url);
  }, [query]);

  // Sync URL with initial load
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const initialQuery = urlParams.get('q') || '';
    setQuery(initialQuery);
    if (initialQuery) {
      fetchResults(initialQuery);
    }
  }, [fetchResults]);

  const handleRetry = () => {
    fetchResults(query);
  };

  return (
    <div className="search-page">
      <h1>Search</h1>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search..."
      />

      {loading && <div className="spinner">Loading...</div>}
      {error && (
        <div className="error">
          {error}
          <button onClick={handleRetry}>Retry</button>
        </div>
      )}
      {!loading && !error && results.length === 0 && query && (
        <div className="no-results">No results found</div>
      )}
      {!loading && !error && results.length > 0 && (
        <ul className="results">
          {results.map((result, index) => (
            <li key={index}>{result}</li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default SearchPage;
```

### 3. URL Sync Implementation

The URL sync is implemented in two parts:

1. **Updating URL when query changes**:
   ```jsx
   useEffect(() => {
     const url = new URL(window.location);
     if (query) {
       url.searchParams.set('q', query);
     } else {
       url.searchParams.delete('q');
     }
     window.history.pushState({}, '', url);
   }, [query]);
   ```

2. **Reading URL on initial load**:
   ```jsx
   useEffect(() => {
     const urlParams = new URLSearchParams(window.location.search);
     const initialQuery = urlParams.get('q') || '';
     setQuery(initialQuery);
     if (initialQuery) {
       fetchResults(initialQuery);
     }
   }, [fetchResults]);
   ```

### 4. Why Cancelling In-flight Requests is Important

Cancelling in-flight requests is crucial in this implementation to prevent several potential issues:

**The Bug It Prevents**: Race conditions where multiple requests are made in quick succession, and the last request's response might update the state with older data.

**Scenario Without Cancellation**:
1. User types "a" → request 1 is sent
2. User types "ap" → request 2 is sent
3. User types "app" → request 3 is sent
4. Request 1 completes and updates state with results for "a"
5. Request 2 completes and updates state with results for "ap"
6. Request 3 completes and updates state with results for "app"

Without cancellation, the user would see the UI flicker through multiple intermediate states before settling on the final state. This creates a poor user experience and can be confusing.

**With Cancellation**:
- When a new request is made, the previous one is aborted
- Only the most recent request's response will update the state
- The UI only shows the results for the final query the user typed

This ensures the UI stays in sync with the user's current input and prevents unnecessary network traffic and state updates.

*Response time: 316.1s*

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
Let me address each of your questions one by one:

### 1. Prisma query for 10 most recent published posts

Here's a Prisma query that fetches the 10 most recent published posts with author name, tag names, and comment count (without N+1 queries):

```typescript
const recentPosts = await prisma.post.findMany({
  take: 10,
  orderBy: {
    createdAt: 'desc',
  },
  where: {
    published: true,
  },
  include: {
    author: {
      select: {
        email: true,
      },
    },
    tags: {
      select: {
        name: true,
      },
    },
    _count: {
      select: {
        comments: true,
      },
    },
  },
});
```

### 2. Migration scenario for adding a slug field

To add a slug field to Post with 10M rows safely without downtime:

1. First, add the column as nullable:
```prisma
model Post {
  id        Int    @id @default(autoincrement())
  slug      String @unique
  // other fields...
}
```

2. Create a migration:
```bash
npx prisma migrate dev --name add_slug_column
```

3. In the migration file, modify the `up` function to:
   - Add the column as nullable
   - Create a unique index
   - Backfill the data in batches
   - Update the index to be non-nullable

Example migration:
```sql
-- Up migration
CREATE TABLE "_PostNew" (
  "id" INTEGER NOT NULL,
  "slug" TEXT,
  PRIMARY KEY ("id")
);

CREATE UNIQUE INDEX "_PostNew_slug_key" ON "_PostNew"("slug");

-- Copy data in batches
DO $$
DECLARE
  batch_size INTEGER := 10000;
  min_id INTEGER;
  max_id INTEGER;
BEGIN
  SELECT MIN(id) INTO min_id FROM "Post";
  SELECT MAX(id) INTO max_id FROM "Post";

  FOR i IN 0..(max_id - min_id)::NUMERIC / batch_size
  LOOP
    INSERT INTO "_PostNew"
    SELECT p.id, generate_slug(p.title) -- You'll need a function to generate slugs
    FROM "Post" p
    WHERE p.id BETWEEN (min_id + (i * batch_size)) AND (min_id + ((i + 1) * batch_size))
    ON CONFLICT DO NOTHING;

    -- Commit after each batch
    COMMIT;
  END LOOP;

  -- Rename tables
  ALTER TABLE "Post" RENAME TO "_PostOld";
  ALTER TABLE "_PostNew" RENAME TO "Post";

  -- Recreate indexes and constraints
  CREATE UNIQUE INDEX "_Post_slug_key" ON "Post"("slug");
  ALTER TABLE "Post" ADD CONSTRAINT "Post_slug_unique" UNIQUE ("slug");
END $$;

-- Down migration
DROP TABLE "Post";
ALTER TABLE "_PostOld" RENAME TO "Post";
```

### 3. Diagnosing and fixing a slow query

**Prisma query:**
```typescript
const posts = await prisma.post.findMany({
  where: {
    tags: {
      some: {
        name: 'prisma',
      },
    },
  },
});
```

**Generated SQL:**
```sql
SELECT * FROM "Post"
WHERE "Post"."id" IN (
  SELECT "PostToTag"."postId"
  FROM "Tag"
  INNER JOIN "PostToTag" ON "Tag"."id" = "PostToTag"."tagId"
  WHERE "Tag"."name" = 'prisma'
)
```

**Diagnosis and fix:**

1. Check the execution plan:
```sql
EXPLAIN ANALYZE
SELECT * FROM "Post"
WHERE "Post"."id" IN (
  SELECT "PostToTag"."postId"
  FROM "Tag"
  INNER JOIN "PostToTag" ON "Tag"."id" = "PostToTag"."tagId"
  WHERE "Tag"."name" = 'prisma'
)
```

2. If the plan shows a sequential scan on Post or PostToTag, add these indexes:
```sql
CREATE INDEX "PostToTag_tagId_index" ON "PostToTag"("tagId");
CREATE INDEX "PostToTag_postId_index" ON "PostToTag"("postId");
CREATE INDEX "Tag_name_index" ON "Tag"("name");
```

3. Consider rewriting the query to use a join instead of IN:
```typescript
const posts = await prisma.post.findMany({
  where: {
    tags: {
      some: {
        name: 'prisma',
      },
    },
  },
  include: {
    tags: true,
  },
});
```

### 4. When to drop to raw SQL

A good example from this schema would be when you need to perform complex aggregations or calculations that Prisma doesn't support well. For example:

```typescript
// Raw SQL query for complex analytics
const tagPopularity = await prisma.$queryRaw`
  SELECT
    t.name AS tag_name,
    COUNT(DISTINCT p.id) AS post_count,
    COUNT(DISTINCT c.id) AS comment_count,
    AVG(
      DATEDIFF(
        day,
        p.createdAt,
        (SELECT MAX(c.createdAt) FROM "Comment" c WHERE c.postId = p.id)
      )
    ) AS avg_days_to_first_comment
  FROM "Tag" t
  JOIN "PostToTag" pt ON t.id = pt.tagId
  JOIN "Post" p ON pt.postId = p.id
  LEFT JOIN "Comment" c ON p.id = c.postId
  WHERE p.published = true
  GROUP BY t.name
  ORDER BY post_count DESC
`;
```

This query calculates complex metrics about tag popularity that would be difficult to express with Prisma's query builder.

*Response time: 271.2s*

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
Here are the answers to your questions:

### 1. Docker Compose for Local Development

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
    depends_on:
      - backend
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    ports:
      - "5000:5000"
    volumes:
      - ./backend:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/mydb
      - REDIS_URL=redis://redis:6379
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    restart: unless-stopped

  db:
    image: postgres:13
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  redis:
    image: redis:6
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### 2. Production Dockerfile for Backend

```dockerfile
# Stage 1: Builder
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# Stage 2: Runtime
FROM node:18-alpine

WORKDIR /app

# Create a non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

# Copy only necessary files from builder
COPY --from=builder --chown=appuser:appgroup /app/package*.json ./
COPY --from=builder --chown=appuser:appgroup /app/node_modules ./node_modules
COPY --from=builder --chown=appuser:appgroup /app/dist ./dist

EXPOSE 5000

CMD ["node", "dist/index.js"]
```

### 3. Backend Crashes in Production (Exit Code 137)

**Meaning:**
Exit code 137 typically indicates that the process was killed by the operating system, usually due to an OOM (Out Of Memory) killer event. This happens when the system runs out of memory and terminates processes to free up resources.

**Diagnosis Steps:**
1. **Check Logs:** Review the application logs to see if there were any memory-related errors or warnings before the crash.
2. **Monitor System Resources:** Use tools like `docker stats`, `htop`, or cloud provider monitoring tools to check memory usage patterns.
3. **Adjust Memory Limits:** If using Docker, ensure the container has enough memory allocated. You can set memory limits in the `docker run` command or in your orchestration tool (e.g., Kubernetes).
4. **Profile the Application:** Use memory profiling tools like `node --inspect` with Chrome DevTools or `heapdump` to identify memory leaks.
5. **Optimize Code:** Review the code for memory-intensive operations or leaks, especially in long-running processes.

### 4. Zero-Downtime Deployment with Schema Change

**Deployment Sequence:**

1. **Prepare the New Version:**
   - Build the new version of the application with the schema migration included.
   - Test the new version thoroughly in a staging environment.

2. **Deploy the New Version:**
   - Start the new version of the application on a different port or instance (e.g., `backend-new`).
   - Ensure the new version is running and healthy before proceeding.

3. **Database Migration:**
   - Run the schema migration on the database. Since the change is additive (new nullable column), it is safe to apply while the old version is still running.
   - Verify the migration was successful and the database is in a healthy state.

4. **Update Load Balancer:**
   - Update the load balancer or reverse proxy to route traffic to the new version of the application.
   - This can be done gradually (e.g., canary deployment) or all at once, depending on your strategy.

5. **Verify the New Version:**
   - Monitor the new version for any issues or errors.
   - Check application logs and system metrics to ensure everything is working as expected.

6. **Decommission the Old Version:**
   - Once the new version is stable and verified, decommission the old version.
   - Remove the old containers or instances to free up resources.

7. **Clean Up:**
   - Remove any temporary resources or configurations used during the deployment.
   - Update any documentation or monitoring tools to reflect the new version.

This sequence ensures that the application remains available throughout the deployment process, minimizing downtime and risk.

*Response time: 267.3s*

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
# Collaborative Document Editor Server Implementation

Here's a Node.js implementation using the `ws` library for a simplified collaborative document editor:

```javascript
const WebSocket = require('ws');
const crypto = require('crypto');

// In-memory storage for documents and connections
const documents = new Map(); // documentId -> { content, users: Set }
const userConnections = new Map(); // userId -> WebSocket

// Message types
const MESSAGE_TYPES = {
  JOIN_DOCUMENT: 'JOIN_DOCUMENT',
  TEXT_CHANGE: 'TEXT_CHANGE',
  CURSOR_MOVE: 'CURSOR_MOVE',
  USER_LEFT: 'USER_LEFT',
  DOCUMENT_STATE: 'DOCUMENT_STATE',
  USER_JOINED: 'USER_JOINED'
};

class CollaborativeEditorServer {
  constructor(port) {
    this.wss = new WebSocket.Server({ port });
    this.wss.on('connection', this.handleConnection.bind(this));
    console.log(`Server started on port ${port}`);
  }

  handleConnection(ws) {
    console.log('New connection established');

    ws.on('message', this.handleMessage.bind(this, ws));
    ws.on('close', this.handleDisconnect.bind(this, ws));
  }

  handleMessage(ws, message) {
    try {
      const data = JSON.parse(message);
      const messageType = data.type;

      switch (messageType) {
        case MESSAGE_TYPES.JOIN_DOCUMENT:
          this.handleJoinDocument(ws, data);
          break;
        case MESSAGE_TYPES.TEXT_CHANGE:
          this.handleTextChange(ws, data);
          break;
        case MESSAGE_TYPES.CURSOR_MOVE:
          this.handleCursorMove(ws, data);
          break;
        default:
          console.error('Unknown message type:', messageType);
      }
    } catch (error) {
      console.error('Error processing message:', error);
    }
  }

  handleJoinDocument(ws, data) {
    const { documentId, userId } = data;

    // Generate a unique userId if not provided
    const finalUserId = userId || crypto.randomUUID();

    // Initialize document if it doesn't exist
    if (!documents.has(documentId)) {
      documents.set(documentId, {
        content: '',
        users: new Set()
      });
    }

    const document = documents.get(documentId);
    document.users.add(finalUserId);

    // Associate user with connection
    userConnections.set(finalUserId, ws);

    // Send current document state to the new user
    const response = {
      type: MESSAGE_TYPES.DOCUMENT_STATE,
      documentId,
      content: document.content,
      users: Array.from(document.users).filter(id => id !== finalUserId)
    };
    ws.send(JSON.stringify(response));

    // Notify other users about the new user
    this.broadcastToDocument(documentId, {
      type: MESSAGE_TYPES.USER_JOINED,
      userId: finalUserId
    }, ws);
  }

  handleTextChange(ws, data) {
    const { documentId, userId, changes } = data;

    if (!documents.has(documentId)) {
      ws.send(JSON.stringify({
        type: 'ERROR',
        message: 'Document not found'
      }));
      return;
    }

    const document = documents.get(documentId);

    // Apply changes to the document
    // In a real implementation, you would use Operational Transformation or CRDT here
    document.content = changes.newContent;

    // Broadcast changes to all other users in the document
    this.broadcastToDocument(documentId, {
      type: MESSAGE_TYPES.TEXT_CHANGE,
      userId,
      changes
    }, ws);
  }

  handleCursorMove(ws, data) {
    const { documentId, userId, cursorPosition } = data;

    if (!documents.has(documentId)) return;

    // Broadcast cursor position to all other users in the document
    this.broadcastToDocument(documentId, {
      type: MESSAGE_TYPES.CURSOR_MOVE,
      userId,
      cursorPosition
    }, ws);
  }

  handleDisconnect(ws) {
    // Find which user disconnected
    for (const [userId, connection] of userConnections.entries()) {
      if (connection === ws) {
        // Find which document the user was in
        for (const [documentId, document] of documents.entries()) {
          if (document.users.has(userId)) {
            document.users.delete(userId);
            // Notify other users that this user left
            this.broadcastToDocument(documentId, {
              type: MESSAGE_TYPES.USER_LEFT,
              userId
            });
          }
        }

        // Remove the user from the connections map
        userConnections.delete(userId);
        break;
      }
    }
  }

  broadcastToDocument(documentId, message, excludeWs = null) {
    if (!documents.has(documentId)) return;

    const document = documents.get(documentId);

    for (const userId of document.users) {
      const ws = userConnections.get(userId);
      if (ws && ws !== excludeWs) {
        ws.send(JSON.stringify(message));
      }
    }
  }
}

// Start the server
const server = new CollaborativeEditorServer(8080);
```

## Implementation Details

### 1. Connection Handling
- Each WebSocket connection is associated with a user ID and document ID when they join
- We use two Maps:
  - `documents`: Tracks all documents and their current state and connected users
  - `userConnections`: Maps user IDs to their WebSocket connections

### 2. Message Protocol
We define the following message types in JSON format:

**Join Document:**
```json
{
  "type": "JOIN_DOCUMENT",
  "documentId": "doc123",
  "userId": "user456" // optional - server will generate if not provided
}
```

**Text Change:**
```json
{
  "type": "TEXT_CHANGE",
  "documentId": "doc123",
  "userId": "user456",
  "changes": {
    "start": 5,
    "end": 10,
    "newContent": "new text"
  }
}
```

**Cursor Move:**
```json
{
  "type": "CURSOR_MOVE",
  "documentId": "doc123",
  "userId": "user456",
  "cursorPosition": 15
}
```

**User Left:**
```json
{
  "type": "USER_LEFT",
  "userId": "user456"
}
```

**Document State (server to client):**
```json
{
  "type": "DOCUMENT_STATE",
  "documentId": "doc123",
  "content": "The current document content",
  "users": ["user1", "user2"]
}
```

**User Joined (server to client):**
```json
{
  "type": "USER_JOINED",
  "userId": "user456"
}
```

### 3. Broadcasting
- When a user makes a change, we broadcast it to all other users in the same document
- We exclude the originating user by passing their WebSocket connection to `broadcastToDocument`
- The `broadcastToDocument` method filters out the excludeWs parameter

### 4. Reconnection
- When a user reconnects, they send a JOIN_DOCUMENT message
- The server checks if the document exists and sends the current state
- The user ID should be the same as before to maintain consistency
- If the user ID changes, they'll be treated as a new user

### 5. Simultaneous Edits Problem
**Problem:** When two users edit the exact same position simultaneously, their changes can conflict and overwrite each other.

**Solution Approaches:**
1. **Operational Transformation (OT):** Transform operations so they can be applied in any order while maintaining consistency.
2. **Conflict-free Replicated Data Types (CRDTs):** Data structures designed to resolve conflicts automatically.
3. **Last Write Wins:** Simple but loses information (not recommended for collaborative editing).
4. **Merge Strategies:** Combine changes in a meaningful way (e.g., for text, merge adjacent changes).

In this simplified implementation, we don't implement OT or CRDT, but in a production system you would need to incorporate one of these solutions to handle concurrent edits properly.

This implementation provides the core functionality for a collaborative document editor with real-time cursor tracking and change propagation.

*Response time: 376.6s*

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

```graphql
type Ingredient {
  name: String!
  amount: Float!
  unit: String!
}

type Step {
  description: String!
}

type Author {
  id: ID!
  name: String!
}

type Tag {
  name: String!
}

type Rating {
  id: ID!
  score: Float!
  comment: String
  author: Author!
  createdAt: String!
}

type Recipe {
  id: ID!
  title: String!
  ingredients: [Ingredient!]!
  steps: [Step!]!
  author: Author!
  tags: [Tag!]!
  ratings: [Rating!]!
  averageRating: Float!
  createdAt: String!
}

input IngredientInput {
  name: String!
  amount: Float!
  unit: String!
}

input StepInput {
  description: String!
}

input TagInput {
  name: String!
}

input RatingInput {
  score: Float!
  comment: String
}

input FilterInput {
  tag: String
  minRating: Float
}

input PaginationInput {
  page: Int
  limit: Int
}

type Query {
  recipes(filter: FilterInput, pagination: PaginationInput): [Recipe!]!
  recipe(id: ID!): Recipe
}

type Mutation {
  addRating(recipeId: ID!, rating: RatingInput!): Rating!
}

type Subscription {
  ratingAdded(recipeId: ID!): Rating!
}
```

### 2. Resolvers

#### Query.recipes

```javascript
Query: {
  recipes: async (_, { filter, pagination }, { dataSources }) => {
    const { page = 1, limit = 10 } = pagination || {};
    const { tag, minRating } = filter || {};

    const recipes = await dataSources.recipesAPI.getRecipes({
      page,
      limit,
      tag,
      minRating,
    });

    return recipes;
  },
},
```

#### Mutation.addRating

```javascript
Mutation: {
  addRating: async (_, { recipeId, rating }, { dataSources, user }) => {
    if (!user) {
      throw new Error('Authentication required');
    }

    return dataSources.recipesAPI.addRating(recipeId, {
      ...rating,
      authorId: user.id,
    });
  },
},
```

#### Recipe.averageRating

```javascript
Recipe: {
  averageRating: (recipe) => {
    if (!recipe.ratings || recipe.ratings.length === 0) {
      return 0;
    }

    const sum = recipe.ratings.reduce((acc, rating) => acc + rating.score, 0);
    return sum / recipe.ratings.length;
  },
},
```

### 3. N+1 Problem and DataLoader Solution

#### Problem Example

Without DataLoader, fetching authors for multiple recipes would result in N+1 queries:
- 1 query to get recipes
- N queries to get authors for each recipe

```javascript
// Without DataLoader
Recipe: {
  author: async (recipe) => {
    return await dataSources.authorsAPI.getAuthorById(recipe.authorId);
  },
},
```

#### Solution with DataLoader

```javascript
// With DataLoader
const authorLoader = new DataLoader(async (authorIds) => {
  const authors = await dataSources.authorsAPI.getAuthorsByIds(authorIds);
  return authorIds.map(id => authors.find(author => author.id === id));
});

Recipe: {
  author: (recipe) => {
    return authorLoader.load(recipe.authorId);
  },
},
```

### 4. Client Query Example

```graphql
query GetRecipeSummary($recipeId: ID!) {
  recipe(id: $recipeId) {
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

### 5. GraphQL vs REST

#### Choose GraphQL when:
1. You need flexible queries where clients can request exactly the data they need
2. You have complex data requirements with nested resources
3. You want to reduce over-fetching or under-fetching of data
4. You need real-time data with subscriptions
5. You have multiple client applications with different data needs

#### Choose REST when:
1. You need simple, cacheable endpoints
2. You prioritize performance and simplicity over flexibility
3. You're working with simple data structures
4. You need better support for browser caching
5. You're building a public API where you want to control exactly what clients can access

#### Don't use GraphQL when:
1. You need simple CRUD operations with uniform data requirements
2. You prioritize maximum performance for simple requests
3. You're working with very large datasets where query complexity could become an issue
4. You need built-in support for content negotiation and multiple response formats
5. You're building a system where you want to strictly control the API surface area

*Response time: 232.8s*

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
Here's the complete HTML and CSS implementation for your layout:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CSS Layout</title>
    <style>
        /* Reset and base styles */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: Arial, sans-serif;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }

        /* Header styles */
        header {
            height: 60px;
            background-color: #333;
            color: white;
            padding: 0 20px;
            display: flex;
            align-items: center;
            position: fixed;
            width: 100%;
            top: 0;
            z-index: 100;
        }

        /* Main content area */
        .container {
            display: flex;
            flex: 1;
            margin-top: 60px; /* To account for fixed header */
        }

        /* Sidebar styles */
        .sidebar {
            width: 240px;
            background-color: #f0f0f0;
            overflow-y: auto;
            padding: 20px;
        }

        /* Main content styles */
        .main-content {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }

        /* Card styles */
        .card {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }

        .card-image {
            width: 100%;
            height: 0;
            padding-bottom: 56.25%; /* 16:9 aspect ratio */
            background-color: #ddd;
            background-size: cover;
            background-position: center;
        }

        .card-content {
            padding: 15px;
            flex: 1;
        }

        .card-title {
            font-size: 1.2em;
            margin-bottom: 10px;
        }

        .card-description {
            color: #666;
            margin-bottom: 15px;
        }

        .card-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 15px;
            border-top: 1px solid #eee;
        }

        .card-button {
            padding: 5px 10px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }

        .card-button-left {
            background-color: #4CAF50;
            color: white;
        }

        .card-button-right {
            background-color: #f44336;
            color: white;
        }

        /* Responsive adjustments */
        @media (max-width: 768px) {
            .container {
                flex-direction: column;
            }

            .sidebar {
                width: 100%;
                order: 1;
            }

            .main-content {
                grid-template-columns: 1fr;
                order: 2;
            }
        }
    </style>
</head>
<body>
    <header>
        HEADER (fixed, full width, 60px tall)
    </header>

    <div class="container">
        <aside class="sidebar">
            SIDEBAR (240px, scrolls independently)
        </aside>

        <main class="main-content">
            <article class="card">
                <div class="card-image" style="background-image: url('https://via.placeholder.com/600x338');"></div>
                <div class="card-content">
                    <h3 class="card-title">Card Title</h3>
                    <p class="card-description">This is a sample card description that provides some information about the content of this card.</p>
                </div>
                <div class="card-footer">
                    <button class="card-button card-button-left">Left Button</button>
                    <button class="card-button card-button-right">Right Button</button>
                </div>
            </article>

            <article class="card">
                <div class="card-image" style="background-image: url('https://via.placeholder.com/600x338');"></div>
                <div class="card-content">
                    <h3 class="card-title">Card Title</h3>
                    <p class="card-description">This is a sample card description that provides some information about the content of this card.</p>
                </div>
                <div class="card-footer">
                    <button class="card-button card-button-left">Left Button</button>
                    <button class="card-button card-button-right">Right Button</button>
                </div>
            </article>

            <article class="card">
                <div class="card-image" style="background-image: url('https://via.placeholder.com/600x338');"></div>
                <div class="card-content">
                    <h3 class="card-title">Card Title</h3>
                    <p class="card-description">This is a sample card description that provides some information about the content of this card.</p>
                </div>
                <div class="card-footer">
                    <button class="card-button card-button-left">Left Button</button>
                    <button class="card-button card-button-right">Right Button</button>
                </div>
            </article>

            <article class="card">
                <div class="card-image" style="background-image: url('https://via.placeholder.com/600x338');"></div>
                <div class="card-content">
                    <h3 class="card-title">Card Title</h3>
                    <p class="card-description">This is a sample card description that provides some information about the content of this card.</p>
                </div>
                <div class="card-footer">
                    <button class="card-button card-button-left">Left Button</button>
                    <button class="card-button card-button-right">Right Button</button>
                </div>
            </article>
        </main>
    </div>
</body>
</html>
```

### Layout Approach Explanation:

1. **Overall Structure**:
   - I used Flexbox for the overall page layout because it's excellent for creating flexible container layouts that need to adapt to different screen sizes.
   - The body is a flex container with column direction, containing the header and the main container.

2. **Header**:
   - The header is fixed using `position: fixed` to ensure it stays at the top of the viewport.
   - It has a fixed height of 60px as specified.

3. **Main Container**:
   - The `.container` class uses flexbox to create a row layout for the sidebar and main content.
   - On mobile (≤768px), it switches to a column layout using a media query.

4. **Sidebar**:
   - The sidebar has a fixed width of 240px and uses `overflow-y: auto` to enable independent scrolling.
   - It's placed first in the flex container to ensure it appears on the left on desktop.

5. **Main Content**:
   - The main content area uses CSS Grid to create the responsive card layout.
   - On desktop (≥768px), it uses `grid-template-columns: repeat(auto-fill, minmax(300px, 1fr))` to create a 2-column layout.
   - On mobile (≤768px), it switches to a single column layout.

6. **Cards**:
   - Each card is a flex container with column direction to stack its elements vertically.
   - The image maintains a 16:9 aspect ratio using padding-bottom percentage.
   - The footer uses flexbox to align buttons to opposite sides.

7. **Responsive Design**:
   - Media queries adjust the layout for mobile devices, switching from a side-by-side layout to a stacked layout.
   - The card grid changes from 2 columns to 1 column on mobile.

This approach combines the strengths of both Flexbox and Grid:
- Flexbox for overall page layout and component internal layout
- Grid for the responsive card layout
- No JavaScript or frameworks needed, just pure CSS

*Response time: 436.5s*

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
Let's break down the design of the notification system for your project management tool:

### 1. Transport Mechanism
For real-time notifications, I recommend using **WebSockets** for the following reasons:
- **Full-duplex communication**: WebSockets allow for two-way communication between the client and server, which is ideal for real-time updates.
- **Low latency**: Unlike polling, WebSockets provide instant updates without the need for constant requests.
- **Efficiency**: WebSockets reduce the overhead of HTTP headers and keep the connection open for continuous data exchange.

**Alternatives**:
- **Server-Sent Events (SSE)**: Good for one-way communication from server to client, but lacks the ability for the client to send messages to the server.
- **Polling**: Inefficient due to constant requests and higher latency.
- **Push Notifications**: Useful for mobile devices but not ideal for web applications as they require additional setup and are less flexible.

### 2. Database Schema
Here’s a proposed schema for storing notifications:

```sql
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    task_id INTEGER NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'task_assigned', 'comment_added', 'deadline_approaching'
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);

CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_task_id ON notifications(task_id);
```

### 3. Handling Offline Users
To ensure offline users receive missed notifications when they come back online:
- **Store notifications in the database**: As shown in the schema above, all notifications are stored and can be retrieved when the user reconnects.
- **Queue missed notifications**: Use a queue system (e.g., RabbitMQ, Kafka) to hold notifications for offline users and deliver them upon reconnection.
- **WebSocket reconnection**: Implement a mechanism in the WebSocket client to reconnect and fetch any missed notifications from the server.

### 4. Deadline Check Implementation
To check deadlines every hour for all tasks, you can use a **cron job** or an **event-driven** approach:

#### Cron Job Approach
```python
# Example using Python with APScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime, timedelta

def check_deadlines():
    tasks = get_all_tasks()  # Fetch all tasks from the database
    for task in tasks:
        if task.deadline and (task.deadline - datetime.now()) <= timedelta(hours=24):
            notify_user(task.assigned_to, 'deadline_approaching', f"Deadline approaching for task {task.id}")

scheduler = BlockingScheduler()
scheduler.add_job(check_deadlines, 'interval', hours=1)
scheduler.start()
```

#### Event-Driven Approach
- **Use a message queue** (e.g., RabbitMQ, Kafka) to trigger deadline checks.
- **Publish an event** when a task is created or updated, and have a consumer process these events to check deadlines.
- **Scale consumers** to handle the load.

### 5. Scaling to 100,000 Concurrent Users
To scale the notification system for 100,000 concurrent users:
- **Load Balancing**: Use a load balancer to distribute WebSocket connections across multiple servers.
- **Horizontal Scaling**: Deploy multiple instances of the WebSocket server and use a message broker (e.g., Redis, RabbitMQ) to manage connections.
- **Database Optimization**: Use read replicas for the notification database to handle high read loads.
- **Caching**: Cache frequently accessed notifications using Redis or Memcached.
- **Sharding**: Shard the notification database by user ID to distribute the load.

### Summary
- **Transport Mechanism**: WebSockets for real-time, low-latency communication.
- **Database Schema**: Store notifications with user and task references, and index for performance.
- **Offline Users**: Queue notifications and deliver upon reconnection.
- **Deadline Check**: Use a cron job or event-driven approach to check deadlines hourly.
- **Scaling**: Use load balancing, horizontal scaling, database optimization, caching, and sharding to handle 100,000 concurrent users.

*Response time: 218.6s*

---
