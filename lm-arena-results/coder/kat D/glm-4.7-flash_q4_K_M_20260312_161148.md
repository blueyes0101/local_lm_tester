# Model: glm-4.7-flash:q4_K_M
**Test Date:** 2026-03-13 00:56:01
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
Here is the complete REST API design for the Multi-Tenant SaaS Project Management tool.

### 1. Base Configuration
*   **Base URL:** `https://api.{domain}.com/v1`
*   **Authentication:** Bearer Token (JWT) in the `Authorization` header.
*   **ID Formats:** All IDs are UUIDs.
*   **Casing:** JSON bodies use `camelCase`. Query parameters use `snake_case`.

---

### 2. Endpoints (RESTful Design)

#### Users
*   **GET** `/users/me`
    *   Returns details of the currently authenticated user.
*   **GET** `/workspaces/{workspace_id}/members`
    *   Lists all users belonging to a specific workspace.

#### Workspaces
*   **GET** `/workspaces`
    *   Lists workspaces the current user is a member of.
*   **POST** `/workspaces`
    *   Creates a new workspace.
*   **GET** `/workspaces/{workspace_id}`
    *   Returns workspace details.

#### Projects
*   **GET** `/workspaces/{workspace_id}/projects`
    *   Lists all projects within a workspace.
*   **POST** `/workspaces/{workspace_id}/projects`
    *   Creates a new project.
*   **GET** `/projects/{project_id}`
    *   Returns a specific project.
*   **PUT** `/projects/{project_id}`
    *   Updates a project.

#### Tasks
*   **GET** `/projects/{project_id}/tasks`
    *   Lists tasks for a specific project with filters (see section 4).
*   **POST** `/projects/{project_id}/tasks`
    *   Creates a new task.
*   **GET** `/tasks/{task_id}`
    *   Returns a specific task.
*   **PUT** `/tasks/{task_id}`
    *   Updates a task.

#### Comments
*   **GET** `/tasks/{task_id}/comments`
    *   Lists comments for a specific task.
*   **POST** `/tasks/{task_id}/comments`
    *   Adds a comment to a specific task.
*   **DELETE** `/comments/{comment_id}`
    *   Deletes a comment (only if the user owns it).

---

### 3. Request/Response JSON Shapes

#### A. Create Task
**Request (POST)**
```json
{
  "title": "Design System Audit",
  "description": "Review colors and typography for consistency.",
  "due_date": "2023-12-01T17:00:00Z",
  "priority": "high",
  "status": "todo",
  "assignee_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response (201 Created)**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Design System Audit",
  "description": "Review colors and typography for consistency.",
  "status": "todo",
  "priority": "high",
  "due_date": "2023-12-01T17:00:00Z",
  "assignee_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2023-10-27T10:00:00Z",
  "updated_at": "2023-10-27T10:00:00Z",
  "project_id": "987f6543-e21b-43d4-a716-426614174000"
}
```

#### B. Update Task Status
**Request (PUT)**
```json
{
  "status": "in_progress",
  "assignee_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

**Response (200 OK)**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Design System Audit",
  "status": "in_progress",
  "priority": "high",
  "due_date": "2023-12-01T17:00:00Z",
  "assignee_id": "550e8400-e29b-41d4-a716-446655440001",
  "updated_at": "2023-10-27T11:30:00Z"
}
```

#### C. List Tasks with Filters
**Request (GET)**
`/projects/987f6543-e21b-43d4-a716-426614174000/tasks?status=todo&assignee_id=550e8400-e29b-41d4-a716-446655440000&due_date=2023-11-01`

**Response (200 OK)**
```json
{
  "data": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Fix Navigation Bug",
      "status": "todo",
      "priority": "medium",
      "due_date": "2023-11-01T17:00:00Z"
    }
  ]
}
```

#### D. Add Comment
**Request (POST)**
```json
{
  "body": "I've updated the color palette, please review.",
  "mentions": ["550e8400-e29b-41d4-a716-446655440000"]
}
```

**Response (201 Created)**
```json
{
  "id": "111e2222-3333-4444-5555-666677778888",
  "body": "I've updated the color palette, please review.",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2023-10-27T12:00:00Z"
}
```

---

### 4. Error Response Format
*All error responses use the following structure.*

**Body:**
```json
{
  "error": {
    "code": "INVALID_PAYLOAD",
    "message": "Validation failed for field 'due_date'. Date is in the past.",
    "details": [
      {
        "field": "due_date",
        "message": "Date cannot be in the past"
      }
    ]
  }
}
```

**Possible Error Codes:**
*   `UNAUTHORIZED`: Token missing or invalid.
*   `FORBIDDEN`: User does not have permission to access this resource.
*   `NOT_FOUND`: The requested ID does not exist.
*   `INVALID_PAYLOAD`: Request body is malformed or validation fails.
*   `WORKSPACE_NOT_MEMBER`: User is not part of the workspace.

---

### 5. Pagination Response Envelope
*When fetching lists (`GET /tasks`, `GET /workspaces`, etc.), always return the envelope.*

**Body:**
```json
{
  "data": [...array of objects...],
  "pagination": {
    "total_count": 150,
    "page": 2,
    "limit": 20,
    "total_pages": 8,
    "has_next_page": true,
    "has_prev_page": false
  }
}
```

*The `limit` is optional in the request query params (e.g., `?limit=50`). If not provided, a default limit applies.*

---

### 6. HTTP Status Code Strategy

| Method | URL | Status Code | Condition |
| :--- | :--- | :--- | :--- |
| **GET** | `/users/me` | **200** | Successful retrieval. |
| **GET** | `/workspaces` | **200** | List retrieved successfully. |
| **POST** | `/tasks` | **201** | Task created successfully. |
| **POST** | `/workspaces/{id}/members` | **201** | Member added successfully. |
| **GET** | `/tasks?...` | **200** | List retrieved with pagination. |
| **GET** | `/tasks/{id}` | **200** | Single task retrieved successfully. |
| **PUT** | `/tasks/{id}` | **200** | Task updated successfully. |
| **DELETE** | `/comments/{id}` | **204** | Comment deleted successfully (No content to return). |
| **GET** | `/tasks/{id}` | **404** | Task does not exist. |
| **POST** | `/tasks` | **403** | User lacks permission to create task in this Project. |
| **POST** | `/workspaces` | **403** | User is not an Admin of their Workspace. |
| **GET** | `/workspaces/{id}` | **404** | Workspace does not exist. |
| **PUT** | `/tasks/{id}` | **400** | Body validation fails (e.g., `due_date` is missing). |
| **PUT** | `/tasks/{id}` | **422** | Business rule failed (e.g., Trying to assign a user not in the workspace). |
| **ANY** | **/** | **401** | Missing or invalid Bearer Token. |
| **ANY** | **/** | **403** | Authenticated user, but insufficient permissions for the endpoint logic. |
| **ANY** | **/** | **500** | Internal server error (e.g., Database connection lost). |

*Response time: 270.7s*

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
Here is the complete implementation including the endpoint, Zod validation, error handling, and unit tests using Jest.

### Project Structure
I have separated the logic into a clean structure:
1.  **`types.ts`**: TypeScript interfaces.
2.  **`schemas.ts`**: Zod validation schemas.
3.  **`services.ts`**: Mock business logic (fetching tasks, checking members, checking subtasks).
4.  **`handler.ts`**: The Express controller.
5.  **`middleware.ts`**: Error formatting.
6.  **`endpoint.test.ts`**: The unit tests.

### 1. Dependencies
You will need to install these packages:
```bash
npm install express zod ts-node @types/express @types/node @types/jest ts-jest ts-node-dev --save-dev
```

### 2. Implementation

**`src/types.ts`**
```typescript
export interface Task {
  id: number;
  workspaceId: number;
  title: string;
  status: 'todo' | 'in_progress' | 'done' | 'cancelled';
  assignee_id: number | null;
  due_date: string | null;
  subtasks: number; // Number of subtasks
}

export interface Workspace {
  id: number;
  members: number[]; // List of member IDs
}
```

**`src/schemas.ts`**
```typescript
import { z } from 'zod';

// URL Params validation
export const WorkspaceIdParamSchema = z.coerce.number().int().positive('workspaceId must be a positive integer');
export const TaskIdParamSchema = z.coerce.number().int().positive('taskId must be a positive integer');

// Body validation
export const UpdateTaskBodySchema = z.object({
  title: z.string().min(1, 'Title is required').max(200, 'Title is too long').optional(),
  status: z.enum(['todo', 'in_progress', 'done', 'cancelled']).optional(),
  assignee_id: z.coerce.number().int().nullable().optional(),
  due_date: z.string().datetime('Invalid date format').optional(),
});

export type UpdateTaskBody = z.infer<typeof UpdateTaskBodySchema>;
```

**`src/services.ts`**
```typescript
import { Task, Workspace } from './types';

// Simulated Database
export const mockDb: { tasks: Task[], workspaces: Workspace[] } = {
  tasks: [
    { id: 1, workspaceId: 10, title: 'Old Task', status: 'in_progress', assignee_id: 100, due_date: '2023-10-01T00:00:00Z', subtasks: 0 },
    { id: 2, workspaceId: 10, title: 'Task with Subtasks', status: 'todo', assignee_id: 101, due_date: '2023-10-02T00:00:00Z', subtasks: 2 },
  ],
  workspaces: [
    { id: 10, members: [100, 101, 102] },
  ],
};

export const getTask = (id: number): Task | undefined => mockDb.tasks.find(t => t.id === id);
export const getWorkspace = (id: number): Workspace | undefined => mockDb.workspaces.find(w => w.id === id);
export const updateTaskInDb = (task: Task): void => {
    const index = mockDb.tasks.findIndex(t => t.id === task.id);
    if (index !== -1) mockDb.tasks[index] = task;
};
```

**`src/handlers.ts`**
```typescript
import { Request, Response, NextFunction } from 'express';
import { WorkspaceIdParamSchema, TaskIdParamSchema, UpdateTaskBodySchema } from './schemas';
import { Task, UpdateTaskBody } from './types';
import { getTask, getWorkspace, updateTaskInDb } from './services';

export const updateTaskHandler = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    // 1. Validate URL Params
    const { workspaceId, taskId } = WorkspaceIdParamSchema.parse(req.params);
    const { taskId: taskIdFromBody } = TaskIdParamSchema.parse(req.params);
    
    if (taskId !== taskIdFromBody) {
        // Handle potential discrepancy if parsed types differ slightly, 
        // though Zod usually enforces types strictly.
        throw new Error('Task ID mismatch');
    }

    // 2. Validate Body
    const body: UpdateTaskBody = UpdateTaskBodySchema.parse(req.body);

    // 3. Fetch Task and Check Workspace
    const task = getTask(taskId);
    if (!task) {
        return res.status(404).json({ error: 'Task not found' });
    }
    if (task.workspaceId !== workspaceId) {
        return res.status(404).json({ error: 'Task does not belong to this workspace' });
    }

    // 4. Validate Assignee
    if (body.assignee_id !== null && body.assignee_id !== undefined) {
        const workspace = getWorkspace(workspaceId);
        if (!workspace || !workspace.members.includes(body.assignee_id)) {
            return res.status(400).json({ error: 'Assignee_id must be a member of the workspace' });
        }
    }

    // 5. Check Cancellation Logic
    if (body.status === 'cancelled' && task.subtasks > 0) {
        return res.status(409).json({ error: 'Cannot cancel task with open subtasks' });
    }

    // 6. Update Task
    const updatedTask: Task = {
        ...task,
        ...body,
    };

    updateTaskInDb(updatedTask);

    return res.status(200).json(updatedTask);

  } catch (error) {
    next(error);
  }
};
```

**`src/middleware.ts`**
```typescript
import { Request, Response, NextFunction } from 'express';
import { ZodError } from 'zod';

export const errorHandler = (err: Error, req: Request, res: Response, next: NextFunction) => {
  // Zod Validation Errors
  if (err instanceof ZodError) {
    return res.status(400).json({
      error: 'Validation failed',
      details: err.errors,
    });
  }

  // Custom Logic Errors (409, 404 handled in handler, but good practice to catch re-thrown)
  if (err.message) {
     // If the error is specific to business logic and not caught above, generic catch
     return res.status(400).json({ error: err.message });
  }

  console.error(err);
  res.status(500).json({ error: 'Internal Server Error' });
};
```

**`index.ts` (Entry Point)**
```typescript
import express from 'express';
import { updateTaskHandler } from './handlers';
import { errorHandler } from './middleware';

const app = express();
app.use(express.json());

app.patch(
  '/workspaces/:workspaceId/tasks/:taskId',
  updateTaskHandler
);

app.use(errorHandler);

// Mock the listener for testing
app.listen = () => {};

export default app;
```

### 3. Unit Tests

**`tests/endpoint.test.ts`**
```typescript
import request from 'supertest';
import app from '../src/index'; // Adjust path as needed
import { mockDb } from '../src/services'; // Adjust path as needed

describe('PATCH /workspaces/:workspaceId/tasks/:taskId', () => {
  
  let originalDbState: any;

  beforeEach(() => {
    // Store original state to reset between tests
    originalDbState = JSON.parse(JSON.stringify(mockDb));
    
    // Clear any modifications in tests
    mockDb.tasks = originalDbState.tasks;
    mockDb.workspaces = originalDbState.workspaces;
  });

  it('should successfully update task fields', async () => {
    const response = await request(app)
      .patch('/workspaces/10/tasks/1')
      .send({ title: 'Updated Title' });

    expect(response.status).toBe(200);
    expect(response.body.title).toBe('Updated Title');
    expect(response.body.status).toBe('in_progress'); // Unchanged
    expect(response.body.assignee_id).toBe(100); // Unchanged
  });

  it('should return 400 with field-level validation errors for invalid body', async () => {
    const response = await request(app)
      .patch('/workspaces/10/tasks/1')
      .send({ 
        title: '', // Too short (min 1)
        status: 'invalid_status',
        assignee_id: 'not_an_integer',
      });

    expect(response.status).toBe(400);
    expect(response.body.error).toBe('Validation failed');
    expect(response.body.details).toBeDefined();
  });

  it('should return 404 if task belongs to different workspace', async () => {
    // Task 1 is in workspace 10, but we request workspace 99
    const response = await request(app)
      .patch('/workspaces/99/tasks/1')
      .send({ title: 'Fake Update' });

    expect(response.status).toBe(404);
    expect(response.body.error).toBe('Task does not belong to this workspace');
  });

  it('should return 409 if trying to cancel with subtasks', async () => {
    // Task 2 has 2 subtasks
    const response = await request(app)
      .patch('/workspaces/10/tasks/2')
      .send({ status: 'cancelled' });

    expect(response.status).toBe(409);
    expect(response.body.error).toBe('Cannot cancel task with open subtasks');
  });

  it('should allow cancellation if subtasks are 0', async () => {
    const response = await request(app)
      .patch('/workspaces/10/tasks/1')
      .send({ status: 'cancelled' });

    expect(response.status).toBe(200);
    expect(response.body.status).toBe('cancelled');
    expect(response.body.subtasks).toBe(0);
  });
});
```

### Key Implementation Details
1.  **Validation**:
    *   **URL Params**: Uses `z.coerce.number().int().positive()` to strictly ensure integers and positive values.
    *   **Body**: Uses `zod` schemas to ensure `assignee_id` is an integer (coercion) and `due_date` is a valid ISO string.
2.  **Security & Logic**:
    *   **404 Handling**: Explicitly checks if the Task exists and if it matches the `workspaceId`.
    *   **Assignee Check**: Only validates the assignee if a new ID is provided.
    *   **Subtask Lock**: Prevents changing status to 'cancelled' if `subtasks > 0`.
3.  **Error Handling**: The `errorHandler` middleware catches `ZodError` from the controller and formats it cleanly into a 400 response with specific field errors.

*Response time: 325.6s*

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
Here is a complete implementation of the authentication system using Node.js, Express, and TypeScript.

### Prerequisites

You will need the following packages installed:

```bash
npm init -y
npm install express bcrypt jsonwebtoken cookie-parser dotenv
npm install -D typescript ts-node @types/express @types/bcrypt @types/jsonwebtoken @types/node
npx tsc --init
```

### Project Structure

```text
/src
  /types
    auth.ts
  /utils
    jwt.ts
  /middleware
    auth.ts
  /controllers
    auth.ts
  /routes
    auth.ts
  index.ts
```

---

### 1. Types (`src/types/auth.ts`)

Define the shapes of our data and JWT payload.

```typescript
export interface JWTPayload {
  userId: string;
  email: string;
  role: string;
}

export interface User {
  id: string;
  email: string;
  password: string; // Hashed password (never sent to client)
  role?: string;
}

export interface RegisterInput {
  email: string;
  password: string;
}

export interface LoginInput {
  email: string;
  password: string;
}

export interface AuthResponse {
  accessToken: string;
  user: Omit<User, 'password'>;
}
```

---

### 2. Utilities (`src/utils/jwt.ts`)

Simple wrappers for Bcrypt and JWT operations.

```typescript
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { JWTPayload } from '../types/auth';

const SALT_ROUNDS = 12;
const ACCESS_TOKEN_EXPIRY = '15m';
const REFRESH_TOKEN_EXPIRY = '7d';
const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';

export const hashPassword = async (password: string): Promise<string> => {
  return bcrypt.hash(password, SALT_ROUNDS);
};

export const comparePassword = async (
  password: string,
  hash: string
): Promise<boolean> => {
  return bcrypt.compare(password, hash);
};

export const generateAccessToken = (payload: JWTPayload): string => {
  return jwt.sign(payload, JWT_SECRET, { expiresIn: ACCESS_TOKEN_EXPIRY });
};

export const generateRefreshToken = (payload: JWTPayload): string => {
  return jwt.sign(payload, JWT_SECRET, { expiresIn: REFRESH_TOKEN_EXPIRY });
};

export const verifyAccessToken = (token: string): JWTPayload | null => {
  try {
    return jwt.verify(token, JWT_SECRET) as JW

*Response time: 138.8s*

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
Here is the implementation and strategy for the advanced refresh token features, focusing on security, rotation, and state management using Redis.

### 1. POST /auth/refresh
This endpoint performs the core refresh logic. It uses the cookie to identify the session, generates a new access token, and immediately rotates the refresh token.

**Assumption:** `jwt.sign()` and `bcrypt.hash()` are available utility functions.

```javascript
async function refreshToken(req, res) {
  const oldRefreshToken = req.cookies.refresh_token;

  if (!oldRefreshToken) {
    return res.status(401).json({ error: "No refresh token provided" });
  }

  // 1. Validate token structure (basic check)
  const tokenHash = hashToken(oldRefreshToken); // Custom function to hash the token for Redis lookup

  // 2. Check Redis for the token
  const userDataString = await redisClient.get(`refresh_token:${tokenHash}`);
  
  if (!userDataString) {
    return res.status(401).json({ error: "Invalid or expired refresh token" });
  }

  const userId = userDataString;

  // 3. Generate NEW tokens
  const newAccessToken = signAccessToken(userId);
  const newRefreshToken = signRefreshToken(userId);

  // 4. ROTATION LOGIC: Delete the old token and set the new one
  // We delete the specific token hash from Redis immediately
  await redisClient.del(`refresh_token:${tokenHash}`);
  
  // We store the new token
  await redisClient.set(
    `refresh_token:${hashToken(newRefreshToken)}`, 
    userId, 
    'EX', 
    60 * 60 * 24 * 7 // 7 Days TTL
  );

  // 5. Send new cookie
  res.cookie('refresh_token', newRefreshToken, { 
    httpOnly: true, 
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    maxAge: 60 * 60 * 24 * 7 * 1000 
  });

  res.json({ access_token: newAccessToken });
}
```

### 2. POST /auth/logout
This simply invalidates the session.

```javascript
async function logout(req, res) {
  const refreshToken = req.cookies.refresh_token;
  
  if (refreshToken) {
    const tokenHash = hashToken(refreshToken);
    // Delete the token from Redis
    await redisClient.del(`refresh_token:${tokenHash}`);
  }

  // Clear cookie
  res.clearCookie('refresh_token', {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict'
  });

  res.status(200).json({ message: "Logged out successfully" });
}
```

### 3. Redis Data Structure & TTL Strategy
To make rotation and blacklisting efficient, we use two keys per token:

**Data Structure:**
1.  **Primary Key:** `refresh_token:{SHA256(token_hash)}`
    *   **Type:** String
    *   **Value:** `User_ID`
    *   **Purpose:** Direct lookup to validate the token.
2.  **Index Key:** `user_tokens:{User_ID}`
    *   **Type:** Set
    *   **Value:** `{hash1, hash2, ...}`
    *   **Purpose:** To bulk delete all tokens for a user (e.g., when they change password).

**TTL Strategy:**
*   We set the TTL (`EX`) on the *Primary Key* (`refresh_token:{hash}`) immediately upon issuing the new token.
*   If a token is stolen but never used, it will automatically expire after the duration (e.g., 7 days).
*   If a token is used, it is deleted from the key immediately, effectively shortening its "life" to the duration of the *first* request, but since we rotate it, the session persists.

### 4. Token Reuse Detection
The standard pattern for detecting token reuse relies on the **immediate deletion** of the old token during the rotation process.

**The Attack Scenario:**
1.  Attacker steals Token A.
2.  Attacker uses Token A. Server validates it, issues Token B, and **deletes Token A**.
3.  Attacker immediately uses Token A again (or the client is stuck).
4.  Server receives Token A again.

**The Implementation (from `refreshToken` above):**
In step 4 of the `refreshToken` function, we execute `await redisClient.del(...)`.
If the Attacker tries to use Token A again:
1.  The lookup `redisClient.get` returns `null` (because it was deleted by the previous request).
2.  The server treats this as an **Immediate Reuse**.
3.  The server returns `401 Invalid/Expired`.

### 5. Password Change (Invalidate All Sessions)
When a user changes their password, we must wipe their active sessions. Using the Set data structure mentioned in Point 3, this is extremely fast.

```javascript
async function changePassword(userId, newPassword) {
  // 1. Update User Password in DB
  await db.updatePassword(userId, newPassword);

  // 2. Get all token hashes for this user
  // KEYS is slow in production, but SCAN is better. 
  // Assuming we have the set key:
  const setKey = `user_tokens:${userId}`;
  
  // Remove the entire index set (which acts as a bucket for all valid tokens)
  await redisClient.del(setKey);
  
  // Note: We don't need to explicitly delete every individual `refresh_token:{hash}` entry 
  // because they have a TTL, but doing so ensures no orphaned keys remain.
}

// Helper to clean up orphaned keys (optional)
async function cleanupOrphanedKeys(userId) {
    const setKey = `user_tokens:${userId}`;
    const keys = await redisClient.smembers(setKey);
    if (keys.length > 0) {
        await redisClient.del(...keys);
    }
}
```

### 6. Difference Between Token Blacklisting and Token Rotation

| Feature | Token Rotation | Token Blacklisting |
| :--- | :--- | :--- |
| **Mechanism** | Stateful. The server keeps track of valid tokens. If the old token is submitted, it is deleted and replaced. | Stateless (mostly) or Stateful. The server stores a list of revoked tokens (e.g., in Redis/DB) that rejects any request containing them. |
| **Performance** | **High Performance.** Looking up a token against a Set/Hash in Redis is extremely fast (O(1)). | **Variable Performance.** Requires checking a database list every time the token is used to see if it is on the blacklist. |
| **Reusability** | Implicitly prevents reuse. Once used, the token is deleted from the server's memory. | Explicitly prevents reuse if manually added to the blacklist. |
| **Usage Case** | **Best for Refresh Tokens.** Refresh tokens should only be used once to get a new access token. Rotation handles this naturally. | **Best for Access Tokens (short-lived).** If you need to revoke an action immediately (e.g., "Delete Account" or "Log out of all devices"), you add the specific access token to a blacklist. |
| **Storage Size** | Grows linearly with the number of active sessions. | Can grow indefinitely if not cleaned up, though you usually blacklist until expiration. |

**Summary:**
For **Refresh Tokens**, use **Rotation** (Stateful) because it is secure, prevents replay attacks, and is performant.
For **Access Tokens**, if you must handle session termination mid-session, use **Blacklisting** (with Redis) because access tokens expire quickly, and checking a blacklist is acceptable overhead.

*Response time: 255.1s*

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
Here is the complete implementation of a robust, generic `DataTable` component in React + TypeScript.

### 1. TypeScript Interfaces

We define interfaces for the column structure and the component props to ensure type safety.

```typescript
import React, { useMemo, useState, useCallback, useEffect } from 'react';

// Definition of a single column
export interface Column<T> {
  key: keyof T | string; // Allows for string keys if using dynamic property access
  header: React.ReactNode;
  width: string | number;
  sortable: boolean;
  renderCell?: (value: unknown, row: T) => React.ReactNode;
}

// Definition of the DataTable Props
export interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  // Controlled Props
  selectedRowKeys?: string[] | Set<string>;
  onSelectionChange?: (keys: string[]) => void;
  currentPage?: number;
  onPageChange?: (page: number) => void;
  controlled?: boolean; // False = internal state management (Uncontrolled), True = External state
  pageSizeOptions?: number[];
  loading?: boolean;
  rowKeyExtractor?: (row: T) => string;
}
```

### 2. Component Implementation

This component manages its own state for sorting, pagination, and selection unless `controlled` is set to true.

```typescript
export const DataTable = <T extends object>({
  columns,
  data,
  selectedRowKeys: controlledSelectedKeys,
  onSelectionChange: controlledOnSelectionChange,
  currentPage: controlledPage,
  onPageChange: controlledOnPageChange,
  controlled = false,
  pageSizeOptions = [10, 25, 50],
  loading = false,
  rowKeyExtractor = (row) => (row as any).id || JSON.stringify(row),
}: DataTableProps<T>) => {
  // --- Internal State (Uncontrolled Mode) ---
  const [sortColumn, setSortColumn] = useState<keyof T | string>('');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(pageSizeOptions[0]);
  const [selectedKeys, setSelectedKeys] = useState<Set<string>>(new Set());

  // --- Sync State (Uncontrolled to Controlled) ---
  // If controlled is true, sync internal state to external props
  useEffect(() => {
    if (controlled) {
      // Sync Selection
      if (controlledSelectedKeys) {
        setSelectedKeys(new Set(controlledSelectedKeys));
      }
      // Sync Page
      if (controlledPage) {
        setCurrentPage(controlledPage);
      }
    }
  }, [controlled, controlledSelectedKeys, controlledPage]);

  // --- Handlers ---

  const handleSort = (columnKey: keyof T | string) => {
    if (sortColumn === columnKey) {
      setSortOrder((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortColumn(columnKey);
      setSortOrder('asc');
    }
  };

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      const allKeys = new Set(data.map(rowKeyExtractor));
      setSelectedKeys(allKeys);
      if (controlled && controlledOnSelectionChange) controlledOnSelectionChange(Array.from(allKeys));
    } else {
      setSelectedKeys(new Set());
      if (controlled && controlledOnSelectionChange) controlledOnSelectionChange([]);
    }
  };

  const handleRowSelect = (key: string) => {
    const newKeys = new Set(selectedKeys);
    if (newKeys.has(key)) {
      newKeys.delete(key);
    } else

*Response time: 198.6s*

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
Here is the complete implementation using React Hooks, `useRef` for caching/cancellation, and `useEffect` for lifecycle management.

### 1. Custom Hook: `useSearch`

This hook handles fetching, debouncing, caching, error handling, and request cancellation.

```javascript
import { useState, useEffect, useRef, useCallback } from 'react';

const CACHE_EXPIRY_MS = 5 * 60 * 1000; // 5 minutes

export const useSearch = (query) => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Refs for mutable values
  const abortControllerRef = useRef(null);
  const cache = useRef(new Map());

  // Helper to check cache
  const getCachedResult = (cachedItem) => {
    if (!cachedItem) return null;
    const isExpired = Date.now() - cachedItem.timestamp > CACHE_EXPIRY_MS;
    return isExpired ? null : cachedItem.data;
  };

  // Debounced Effect
  useEffect(() => {
    // 1. Cleanup: Cancel previous request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // If query is empty, reset state
    if (!query) {
      setResults([]);
      setLoading(false);
      setError(null);
      return;
    }

    // 2. Check Cache
    const cachedItem = cache.current.get(query);
    const cachedData = getCachedResult(cachedItem);

    if (cachedData) {
      setResults(cachedData);
      setLoading(false);
      return;
    }

    // 3. Start Fetching
    setLoading(true);
    setError(null);
    
    const controller = new AbortController();
    abortControllerRef.current = controller;

    fetch(`/api/search?q=${encodeURIComponent(query)}`, {
      signal: controller.signal,
    })
      .then((res) => {
        if (!res.ok) throw new Error('Network response was not ok');
        return res.json();
      })
      .then((data) => {
        // Store in cache
        cache.current.set(query, { data, timestamp: Date.now() });
        setResults(data);
      })
      .catch((err) => {
        // Ignore AbortErrors (user typed something new)
        if (err.name !== 'AbortError') {
          setError(err);
        }
      })
      .finally(() => {
        setLoading(false);
      });

    // Cleanup on unmount or query change
    return () => {
      controller.abort();
    };
  }, [query]); // Triggered every time 'query' changes

  // Expose a function to refetch manually if needed
  const refetch = useCallback(() => {
    // Trigger the effect again by relying on the URL query sync or re-rendering
    // For simplicity, we can just re-trigger the hook via a ref or let parent handle it.
    // Here, we simply update the cache key or rely on the parent component calling it.
  }, [query]);

  return { results, loading, error, refetch };
};
```

### 2. Component: `SearchPage`

This component handles the UI, URL synchronization, and retry logic.

```jsx
import React, { useState, useEffect } from 'react';
import { useSearch } from './useSearch';

const SearchPage = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const { results, loading, error } = useSearch(searchTerm);

  // 1. URL Sync: Read URL on Mount
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const query = urlParams.get('q') || '';
    setSearchTerm(query);
  }, []);

  // 2. URL Sync: Update URL on Input Change
  const handleInputChange = (e) => {
    const val = e.target.value;
    setSearchTerm(val);
    
    // Use replaceState to avoid pushing new history entries with every keystroke
    const newUrl = val ? `?q=${encodeURIComponent(val)}` : window.location.pathname;
    window.history.replaceState({}, '', newUrl);
  };

  const handleRetry = () => {
    // We can trigger a refetch if needed, or simply clear error
    setError(null);
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>Search</h1>
      <input
        type="text"
        value={searchTerm}
        onChange={handleInputChange}
        placeholder="Type to search..."
        style={{ padding: '10px', width: '300px' }}
      />

      <div style={{ marginTop: '20px' }}>
        {loading && <p>Loading results...</p>}
        
        {error && (
          <div style={{ color: 'red', marginBottom: '10px' }}>
            Error: {error.message}. 
            <button onClick={handleRetry} style={{ marginLeft: '10px' }}>Retry</button>
          </div>
        )}

        {!loading && !error && results.length === 0 && (
          <p>No results found.</p>
        )}

        <ul>
          {results.map((item, index) => (
            <li key={index}>{item.name}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default SearchPage;
```

### 3. Why do we need `AbortController`? (The Bug It Prevents)

Using `AbortController` prevents a **Race Condition / Stale Data** bug.

**The Scenario:**
1.  User types: "apple" (300ms passes, request starts).
2.  User types: "banana" (300ms passes, request starts).
3.  **Result:** The request for "banana" takes longer than "apple" to complete.

**Without Cancellation:**
The "apple" request (which was sent first) would finish *after* the "banana" request. If you update your state with the result of the "apple" request, you will display "apple" in your list even though the user is currently looking at "banana". This is known as "stale data."

**With Cancellation:**
When the "banana" request starts, the `useEffect` cleanup function calls `abortControllerRef.current.abort()`. This cancels the "apple" request immediately. When the "apple" request's `catch` block fires, it receives an `AbortError`. We explicitly ignore this error (by checking `err.name !== 'AbortError'`), ensuring the UI remains stable and only shows the data for the latest input ("banana").

*Response time: 362.5s*

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
### 1. Prisma Query for Recent Published Posts

To fetch the 10 most recent published posts with author, tags, and comment count without triggering N+1 queries, we use `findMany` with an `include` block. To ensure efficiency, we select only the specific fields we need and use `select` on nested relations (like comments) to avoid fetching unnecessary data (like comment text) just to count them.

```typescript
const recentPosts = await prisma.post.findMany({
  where: {
    published: true,
  },
  orderBy: {
    createdAt: 'desc',
  },
  take: 10,
  include: {
    // Include the author object
    author: {
      select: {
        email: true, // Based on the provided schema, this is the 'name'
      },
    },
    // Include tags without fetching their specific nested relations
    tags: {
      select: {
        name: true,
      },
    },
    // Efficiently count comments by only fetching the ID (counting them is faster than fetching the text)
    comments: {
      select: {
        id: true, // Selecting only ID allows Prisma to use COUNT efficiently
      },
    },
  },
});

// Map the result to a cleaner format if needed
const formattedPosts = recentPosts.map(post => ({
  title: post.title,
  date: post.createdAt,
  author: post.author.email,
  tagCount: post.tags.length,
  commentCount: post.comments.length,
}));
```

### 2. Migration Scenario for "Non-Nullable" Slug

Since you cannot add a `NOT NULL` constraint directly to a column that already contains `NULL` values (e.g., existing data), and you need to maintain availability on a table with 10M rows, the standard procedure is:

1.  **Add the nullable column** to the database schema.
2.  **Create a Unique Index Concurrency** (`CREATE INDEX CONCURRENTLY`) to enforce uniqueness on the new column. This allows the operation to proceed without locking the table for updates, but since it ignores NULLs, it won't block reads or writes while the data is being populated.
3.  **Populate the data** (Update existing rows with valid slugs).
4.  **Set the column to `NOT NULL`**. Once the data is populated and the unique index is in place, setting the constraint is an online operation that will scan the table but won't block DML operations.

**SQL Scenario:**

```sql
-- 1. Add the new column as nullable
ALTER TABLE Post ADD COLUMN slug String;

-- 2. Create a unique index concurrently. 
-- This ignores NULLs, allowing the index to be built online without blocking writes/reads
-- while we prepare the data.
CREATE UNIQUE INDEX CONCURRENTLY post_slug_unique_idx ON Post(slug);

-- 3. Populate the data (Update existing rows)
UPDATE Post SET slug = slugify(title) WHERE slug IS NULL;

-- 4. Set the column to NOT NULL
-- This will scan the table once but does not block transactions
ALTER TABLE Post ALTER COLUMN slug SET NOT NULL;
```

### 3. Performance Diagnosis for Tag Filtering

**The Prisma Query:**
```typescript
await prisma.post.findMany({
  where: {
    tags: {
      some: {
        name: 'Technology',
      },
    },
  },
});
```

**The (Approximate) Raw SQL Generated:**
```sql
SELECT "Post".* 
FROM "Post"
INNER JOIN "PostTag" ON "Post"."id" = "PostTag"."postId"
INNER JOIN "Tag" ON "PostTag"."tagId" = "Tag"."id"
WHERE "Tag"."name" = 'Technology';
```

**Diagnosis:**
This query performs a join between the `Post` table and the `Tag` table via the junction table `PostTag`. If the `Tag` table is large, the database has to scan the `name` column repeatedly for every row it examines, or perform a join operation that scans both tables inefficiently.

**The Fix:**
You need an index on the `Tag` table to speed up the `WHERE` clause search.

**Solution SQL:**
```sql
-- Create an index on the 'name' column of the Tag table
CREATE INDEX idx_tag_name ON Tag(name);
```
*(Also ensure there is an index on the foreign key in `PostTag` for `tagId`, e.g., `CREATE INDEX idx_posttag_tagid ON PostTag(tagId);`)*

### 4. When to Drop to Raw SQL

You should drop to raw SQL (using `prisma.$queryRaw` or `prisma.$executeRaw`) when Prisma's ORM abstractions become too limiting for complex data retrieval or performance requirements.

**Real Example: "Top Authors by Engagement"**

*   **The Requirement:** Find the top 5 authors based on the total number of comments they have written, but only include authors who have published more than 10 posts.
*   **Why Prisma is difficult:** To achieve this in Prisma, you would typically have to perform a `count` operation across the `User`, `Post`, and `Comment` tables. This often requires creating complex subqueries or executing separate API calls to count posts and comments per user, leading to "N+1" query problems.
*   **Why Raw SQL is better:** You can perform a single, efficient `GROUP BY` and `HAVING` clause that aggregates the data in one database pass.

**Raw SQL Implementation:**
```sql
SELECT u.email, COUNT(c.id) AS total_comments
FROM User u
JOIN Comment c ON u.id = c.authorId
JOIN Post p ON u.id = p.authorId
GROUP BY u.id, u.email
HAVING COUNT(p.id) > 10
ORDER BY total_comments DESC
LIMIT 5;
```

*Response time: 385.1s*

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
Here is the complete solution for your requirements.

### 1. `docker-compose.yml` for Local Development

This configuration sets up a shared network so services can communicate by name. It uses `nodemon` for backend hot reloading and ensures the backend waits for Postgres.

**Create a `.env` file** in the root directory:
```env
# .env
POSTGRES_USER=dev_user
POSTGRES_PASSWORD=dev_password
POSTGRES_DB=dev_db
REDIS_URL=redis://redis:6379
```

**Create `docker-compose.yml`:**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: app_postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: app_redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    # Optional: Add healthcheck for redis if needed

  backend:
    build: ./backend
    container_name: app_backend
    restart: unless-stopped
    environment:
      DB_HOST: postgres
      DB_PORT: 5432
      DB_USER: ${POSTGRES_USER}
      DB_PASS: ${POSTGRES_PASSWORD}
      DB_NAME: ${POSTGRES_DB}
      REDIS_URL: ${REDIS_URL}
    ports:
      - "3000:3000"
    volumes:
      # Mounts source code for hot reload
      - ./backend:/app
      # Mounts node_modules to avoid permission issues or override local changes if using vendor mounts
      - /app/node_modules 
    command: npm run dev # Assumes "dev" script uses nodemon
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started

  frontend:
    build: ./frontend
    container_name: app_frontend
    restart: unless-stopped
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev

volumes:
  pgdata:
```

---

### 2. Production Dockerfile for Backend

This uses a multi-stage build to separate the compilation phase from the runtime phase, keeping the final image small and secure.

**Assumption:** You have a `build` script (e.g., for TypeScript compilation) and a start script.

**Create `backend/Dockerfile`:**
```dockerfile
# --- Stage 1: Builder ---
# Using Alpine to keep image size small
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies (including dev tools for build)
RUN npm ci

# Copy the rest of the application source
COPY . .

# Run the build script (compiles TS/JS if applicable)
RUN npm run build

# --- Stage 2: Runtime ---
FROM node:20-alpine AS runtime

# Install dumb-init for proper signal handling and security
RUN apk add --no-cache dumb-init

WORKDIR /app

# Install production dependencies only
COPY --from=builder /app/node_modules ./node_modules

# Copy only the build output (e.g., dist/ or build/) and package.json
COPY --from=builder /app/package.json ./
COPY --from=builder /app/dist ./dist

# Create a non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 node

# Change ownership of node_modules and app files to non-root user
RUN chown -R node:node /app

# Switch to non-root user
USER node

# Expose port
EXPOSE 3000

# Use dumb-init to handle signals gracefully
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "dist/index.js"]
```

---

### 3. Exit Code 137: Diagnosis

**What it means:**
Exit code `137` corresponds to the signal `SIGKILL`. It specifically indicates that the Docker daemon (or the host OS) explicitly killed the container. It is the industry standard code for **"Out of Memory" (OOM) Kill**. When the container uses more memory than allowed (either by Docker resource limits or system limits), the kernel forces a kill to protect the system from crashing.

**How to Diagnose:**

1.  **Check Logs for OOM Errors:**
    Run `docker logs <container_id>`. You might see a standard kernel message like `Out of memory: Kill process ...`.
2.  **Check Docker Stats:**
    Run `docker stats <container_id>` or `docker stats` (for all). Look at the `MEM %` column. If it hits 100%, the container is consuming more memory than the limit allows.
3.  **Inspect Container Configuration:**
    Run `docker inspect <container_id>`. Look at the `HostConfig.Memory` field. If you haven't set limits, the OS is enforcing a default limit (usually 64MB or 128MB for Docker on Linux), or if running on Kubernetes, check the `resources.limits.memory`.
4.  **Analyze Code:**
    If the limit seems high enough but it still happens, check your Node.js backend for memory leaks (e.g., global variables not being cleared, unclosed streams, large cached objects that grow indefinitely).
5.  **Verify the Signal:**
    In the logs, ensure it isn't actually being killed by a parent process (like `supervisord` or `pm2`) which also sends `SIGKILL`. However, Exit 137 is overwhelmingly associated with the OS OOM killer.

---

### 4. Zero Downtime Deployment with Additive DB Schema Change

Since the database change is **additive** (adding a new nullable column) and not destructive, the database migration itself typically takes milliseconds and has zero downtime. The challenge lies in upgrading the backend application.

**Deployment Sequence:**

1.  **Database Migration (Run on Primary DB):**
    *   Execute the migration script on your primary database. Adding a nullable column is a lightweight operation and does not block reads or writes to existing data.
    *   *Result:* Database is now ready for the new code.

2.  **Build New Backend Version:**
    *   Build the new Docker image containing the backend code that queries the new column.

3.  **Update Deployment Tool Configuration:**
    *   Update your CI/CD pipeline or Kubernetes deployment manifest to point to the new image tag.

4.  **Trigger Rolling Update:**
    *   Initiate a rolling update (via Kubernetes `kubectl rollout` or Docker Swarm).
    *   The orchestrator will gradually terminate old pods and launch new ones based on your replica count (e.g., if replicas=3, it might replace 1 pod at a time).

5.  **Health Checks:**
    *   The orchestrator will send health probes (Liveness/Readiness) to the new pods.
    *   The new pods must return `200 OK` to prove they are working and not crashing on the new database column.
    *   The load balancer (or ingress) starts sending traffic to the new pods only after they pass the readiness check.

6.  **Traffic Routing:**
    *   Traffic seamlessly shifts to the new pods. Old pods are terminated once they have no connections.

7.  **Verification:**
    *   Monitor logs for any errors related to the new column (e.g., if you are using an ORM that queries all columns, ensure you handle the new one gracefully, though it's `nullable` and usually harmless).

**Why this is Zero Downtime:**
Because the DB migration didn't lock tables and the application upgrade is a rolling restart, existing users maintain connections to the database and the old application versions. New requests are handled by the newer versions that understand the new schema.

*Response time: 239.2s*

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
Here is the implementation and explanation for a simplified collaborative editor server using Node.js and `ws`.

### 1. Conceptual Design

**1. Connection Handling**
To associate a WebSocket with a user and document, we maintain a global state map.
*   **`documents`**: Stores the state of every active document. It contains the content, a list of connected sockets (for broadcasting), and the cursor positions of all users.
*   **`connectionMap`**: Maps a unique `userId` (global identifier) to the specific WebSocket instance. This allows us to find the socket for a user who reconnects.

**2. Message Protocol**
All messages are JSON strings with a specific type field.

*   **`JOIN`**:
    ```json
    { "type": "JOIN", "userId": "u123", "docId": "doc1" }
    ```
*   **`TEXT`** (Change to the document):
    ```json
    { "type": "TEXT", "userId": "u123", "text": "Hello" }
    ```
*   **`CURSOR`** (Position update):
    ```json
    { "type": "CURSOR", "userId": "u123", "position": { "x": 10, "y": 5 } }
    ```
*   **`USER_LEFT`** (Notification):
    ```json
    { "type": "USER_LEFT", "userId": "u123" }
    ```

**3. Broadcasting Logic**
When a user sends a `TEXT` or `CURSOR` message, we look up the document ID. We iterate through the list of sockets associated with that document and send the message. Crucially, we pass the `currentWs` object (sender) to a filter so it is excluded from the broadcast loop, ensuring no echo loop.

**4. Reconnection Logic**
1.  Client connects and sends `JOIN`.
2.  Server checks `documents[docId]`.
3.  If the user exists in the document, the server adds the *new* socket back to the document's socket list. (Other users see the cursor re-appear).
4.  The server sends the current document content to the new connection.

**5. Concurrent Editing (The Problem)**
**Problem:** If User A and User B both edit at position 5 simultaneously, User A's change overwrites User B's, or vice versa.
**Solutions:**
*   **Last Write Wins:** Easiest, but causes data loss. (Not implemented here).
*   **Operational Transformation (OT):** User A's change is transformed to work around User B's change before applying it.
*   **CRDT (Conflict-free Replicated Data Types):** Data structures (like Automata) that naturally resolve conflicts mathematically without needing a central coordinator to transform changes.

---

### 2. Server Implementation (`server.js`)

```javascript
const WebSocket = require('ws');

const wss = new WebSocket.Server({ port: 8080 });

// State Management
// documents: key=docId, value= { content, sockets: [ws, ws], cursors: {userId: {x,y}} }
// users: key=userId, value={ docId, ws }
const documents = {};
const userMap = new Map();

console.log('Server running on ws://localhost:8080');

// Helper: Broadcast to all sockets in a specific document EXCEPT the sender
function broadcast(docId, messageObj, excludeWs) {
    if (!documents[docId]) return;
    
    const doc = documents[docId];
    
    // Iterate through sockets for this document
    for (const ws of doc.sockets) {
        if (ws !== excludeWs && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify(messageObj));
        }
    }
}

// Helper: Send message to a specific user
function sendToUser(userId, messageObj) {
    const connection = userMap.get(userId);
    if (connection && connection.ws.readyState === WebSocket.OPEN) {
        connection.ws.send(JSON.stringify(messageObj));
    }
}

// --- Event Listeners ---

wss.on('connection', (ws) => {
    
    // 1. Connection Handling
    // The connection is anonymous until they say which document and user they are.
    
    ws.on('message', (message) => {
        let data;
        try {
            data = JSON.parse(message);
        } catch (e) {
            return; // Ignore invalid JSON
        }

        const { type } = data;

        switch (type) {
            case 'JOIN':
                handleJoin(ws, data.userId, data.docId);
                break;
                
            case 'TEXT':
                handleTextChange(ws, data.userId, data.docId, data.text);
                break;
                
            case 'CURSOR':
                handleCursorMove(ws, data.userId, data.docId, data.position);
                break;
        }
    });

    ws.on('close', () => {
        handleDisconnect(ws);
    });
});

// Logic: Handle User Joining or Reconnecting
function handleJoin(ws, userId, docId) {
    // Initialize document state if it doesn't exist
    if (!documents[docId]) {
        documents[docId] = {
            content: "",
            sockets: [],
            cursors: {}
        };
    }

    const doc = documents[docId];

    // Check if user is already in document (Reconnection case)
    if (userMap.has(userId)) {
        const existingConn = userMap.get(userId);
        
        // Update the socket to the new connection (the old one is gone)
        existingConn.ws = ws;
        
        // Ensure the socket is in the doc's list
        if (!doc.sockets.includes(ws)) {
            doc.sockets.push(ws);
        }

        // Send the current content to the new connection
        ws.send(JSON.stringify({ type: 'DOC_SYNC', content: doc.content }));

        // Broadcast CURSOR of this user back to everyone (so others see them reappear)
        broadcast(docId, { type: 'CURSOR', userId, position: doc.cursors[userId] }, ws);

    } else {
        // New User
        userMap.set(userId, { ws, docId });
        doc.sockets.push(ws);

        // Send current content to the new user
        ws.send(JSON.stringify({ type: 'DOC_SYNC', content: doc.content }));

        // Broadcast that a new user joined (with empty cursor initially)
        broadcast(docId, { type: 'USER_JOINED', userId }, ws);
    }
}

// Logic: Handle Text Changes
function handleTextChange(ws, userId, docId, newText) {
    if (!documents[docId]) return;
    
    const doc = documents[docId];
    
    // In a real app, you would apply OT/CRDTs here.
    // Here, we just do a simple last-write-wins replace for the simplified demo.
    doc.content = newText;

    // Broadcast the text change to everyone else
    // Exclude the sender (ws)
    broadcast(docId, { type: 'TEXT', userId, text: newText }, ws);
}

// Logic: Handle Cursor Movement
function handleCursorMove(ws, userId, docId, position) {
    if (!documents[docId]) return;
    
    const doc = documents[docId];
    
    // Update the cursor state in the document
    doc.cursors[userId] = position;

    // Broadcast the cursor position to everyone else
    broadcast(docId, { type: 'CURSOR', userId, position }, ws);
}

// Logic: Handle Disconnect
function handleDisconnect(ws) {
    // Find which user this ws belongs to
    // (Simple linear search, O(n). For production, maintain inverse maps)
    let disconnectedUserId = null;
    for (const [uid, conn] of userMap) {
        if (conn.ws === ws) {
            disconnectedUserId = uid;
            break;
        }
    }

    if (disconnectedUserId) {
        const docId = userMap.get(disconnectedUserId).docId;
        
        // Remove socket from document list
        if (documents[docId]) {
            documents[docId].sockets = documents[docId].sockets.filter(s => s !== ws);
            
            // Remove cursor from view
            delete documents[docId].cursors[disconnectedUserId];
            
            // Notify others
            broadcast(docId, { type: 'USER_LEFT', userId: disconnectedUserId }, ws);
        }

        // Remove from global map
        userMap.delete(disconnectedUserId);
    }
}
```

### How to Run

1.  Install dependencies:
    ```bash
    npm install ws
    ```
2.  Save the code above as `server.js`.
3.  Run the server:
    ```bash
    node server.js
    ```
4.  Open two different terminals (or a local web app connected to `ws://localhost:8080`) and test sending messages.

*Response time: 277.4s*

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
Here is the complete solution for the recipe platform GraphQL API.

### 1. GraphQL Schema (SDL)

This schema defines the types, queries, mutations, and input types required to support the requested features.

```graphql
# Types
type Recipe {
  id: ID!
  title: String!
  ingredients: [Ingredient!]!
  steps: [String!]!
  author: Author!
  tags: [String!]
  ratings: [Rating!]!
  averageRating: Float
}

type Ingredient {
  name: String!
  amount: Float
  unit: String
}

type Rating {
  score: Float!
  comment: String
  id: ID! # Adding ID for consistency
}

type Author {
  id: ID!
  name: String!
}

# Queries
type Query {
  recipes(filter: RecipeFilter, pagination: PaginationInput): [Recipe!]!
}

# Mutations
type Mutation {
  addRating(recipeId: ID!, score: Float!, comment: String): Recipe
}

# Inputs
input RecipeFilter {
  tag: String
  minRating: Float
}

input PaginationInput {
  page: Int
  limit: Int
}

# Scalars (Optional for this snippet, but good practice)
scalar Date
```

### 2. Resolvers

Here are the resolver implementations. I have assumed an in-memory data store (`recipes` and `authors` arrays) for demonstration purposes, but these can easily be swapped for database calls.

```javascript
const resolvers = {
  Query: {
    recipes: (parent, { filter, pagination }, { dataSources }) => {
      // Basic pagination logic
      const page = (pagination?.page || 1) - 1; // GraphQL pages are usually 1-based
      const limit = pagination?.limit || 10;
      const offset = page * limit;

      // 1. Filter by Tag
      let result = dataSources.recipes.filter(recipe => {
        if (filter?.tag && !recipe.tags?.includes(filter.tag)) return false;
        return true;
      });

      // 2. Filter by Min Rating
      if (filter?.minRating !== undefined) {
        result = result.filter(recipe => 
          recipe.averageRating >= filter.minRating
        );
      }

      // 3. Apply Pagination (Slice)
      const paginatedResult = result.slice(offset, offset + limit);

      // We return the paginated items. 
      // We will fetch authors in the Recipe resolver to avoid N+1.
      return paginatedResult;
    }
  },
  Mutation: {
    addRating: (parent, { recipeId, score, comment }, { dataSources }) => {
      const recipe = dataSources.recipes.find(r => r.id === recipeId);
      if (!recipe) throw new Error("Recipe not found");

      // Add new rating
      const newRating = {
        id: Math.random().toString(36).substr(2, 9),
        score,
        comment
      };
      recipe.ratings.push(newRating);

      // Recalculate average rating
      const sum = recipe.ratings.reduce((acc, r) => acc + r.score, 0);
      recipe.averageRating = sum / recipe.ratings.length;

      return recipe;
    }
  },
  Recipe: {
    averageRating: (recipe) => {
      if (!recipe.ratings || recipe.ratings.length === 0) return 0;
      const sum = recipe.ratings.reduce((acc, r) => acc + r.score, 0);
      return parseFloat((sum / recipe.ratings.length).toFixed(2));
    },
    // This resolver will be populated by DataLoader (see part 3)
    author: (recipe, args, { authorLoader }) => {
      return authorLoader.load(recipe.authorId);
    }
  }
};
```

### 3. The N+1 Problem and DataLoader Fix

**The Problem:**
When fetching a list of recipes, if we fetch `author` inside a loop for each recipe, we trigger a database query for *every single recipe*.

*   **Query 1:** Fetch all Recipes (from DB)
*   **Query 2:** Fetch Author for Recipe A (from DB)
*   **Query 3:** Fetch Author for Recipe B (from DB)
*   ...
*   **Query N:** Fetch Author for Recipe Z (from DB)

This results in $N+1$ queries.

**The Fix (DataLoader):**
`DataLoader` batches requests. Instead of firing a request for every recipe, it collects all author IDs, fires *one* database query for all unique IDs, and maps the results back to the recipes.

Here is how to implement the DataLoader for the Author field:

```javascript
// Simplified DataLoader implementation
class DataLoader {
  constructor(batchFn) {
    this.batchFn = batchFn;
    this.batch = new Map();
    this.pending = new Map();
  }

  load(key) {
    if (!this.batch.has(key)) {
      this.batch.set(key, new Promise((resolve) => {
        this.pending.set(key, resolve);
      }));
    }
    return this.batch.get(key);
  }

  flush() {
    if (this.batch.size === 0) return Promise.resolve();
    
    const keys = Array.from(this.batch.keys());
    const values = this.batch;
    this.batch = new Map();
    this.pending = new Map();

    return this.batchFn(keys).then(results => {
      keys.forEach(key => {
        this.pending.get(key)(results[key]);
      });
    });
  }
}

// In your context or resolvers setup
const createLoader = () => {
  const authorLoader = new DataLoader(async (authorIds) => {
    // ONE DATABASE QUERY to fetch all authors at once
    const authors = await db.query('SELECT * FROM authors WHERE id IN (?)', [authorIds]);
    
    // Create a map for O(1) lookup
    const authorMap = {};
    authors.forEach(author => {
      authorMap[author.id] = author;
    });

    return authorIds.map(id => authorMap[id]);
  });
  
  // Important: Flush at the end of request processing to execute batch
  // This is usually handled by the server framework (Apollo Server, etc)
  return authorLoader;
};
```

### 4. Client Query

A client wants the `title`, `author.name`, and the first 3 ingredients.

*Note: To strictly fetch "the first 3", the client would query a field specifically designed to handle limits, or the server resolves the list with a limit.* Assuming we have a field in the schema or a resolver that supports limits, or simply fetching all and filtering in code, here is the query. I will assume a hypothetical field `ingredients` returns a list, or we query it as is. To make the example accurate to the requirement, I will query the standard fields. In a real-world scenario, you would create a specific query like `recipePreview` or use a `limit` argument.

```graphql
query GetRecipeSummary {
  recipes {
    title
    author {
      name
    }
    ingredients {
      name
      amount
      # Assuming 'unit' is needed, though not explicitly requested, 
      # it helps identify ingredients.
    }
  }
}
```

*If the server needs to strictly enforce the "first 3" limit, the query remains the same, but the resolver would slice the list:*
```graphql
query {
  recipes {
    title
    author { name }
    # The resolver for this field would look like:
    # ingredients: (recipe) => recipe.ingredients.slice(0, 3)
    ingredients {
      name
      amount
    }
  }
}
```

### 5. When to use GraphQL vs REST

**Choose GraphQL when:**
1.  **Mobile/Frontend complexity:** You have a mobile app or frontend that needs to aggregate data from multiple services (e.g., User data + Order data + Product data) and only display a subset of that data. It reduces the number of network requests (round trips).
2.  **Strong Typing:** You want a strongly typed schema to enforce contracts between client and server and help with auto-completion and tooling.
3.  **Evolution:** You want to change your backend API (e.g., adding a new database column to an order) without breaking existing clients, as long as the requested fields are still present.

**Choose REST when:**
1.  **Caching is critical:** REST leverages HTTP caching (via `Cache-Control` headers) effectively, which is excellent for read-heavy operations. GraphQL is harder to cache because requests are dynamic.
2.  **Simplicity and Tooling:** You are building a standard CRUD API. REST has decades of maturity, existing libraries, and a vast ecosystem of tools.
3.  **Security:** REST provides easy enforcement of standard HTTP verbs (GET, POST, PUT, DELETE) and CORS policies. GraphQL allows fetching data beyond the intended entity (e.g., fetching user data inside a comment query) if not carefully guarded.

*Response time: 321.1s*

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
Here is the complete implementation using pure HTML and CSS.

### The Code

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fixed Header Layout</title>
    <style>
        /* --- Reset & Base Styles --- */
        :root {
            --header-height: 60px;
            --sidebar-width: 240px;
            --primary-color: #3b82f6;
            --bg-body: #f3f4f6;
            --bg-sidebar: #1f2937;
            --bg-card: #ffffff;
            --text-main: #111827;
            --text-muted: #6b7280;
            --border-color: #e5e7eb;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            height: 100vh;
            display: flex;
            flex-direction: column;
            background-color: var(--bg-body);
            overflow: hidden; /* Prevent body scroll, handle inside containers */
        }

        /* --- 1. HEADER (Fixed) --- */
        header {
            height: var(--header-height);
            background-color: #ffffff;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            padding: 0 24px;
            flex-shrink: 0; /* Prevent header from shrinking */
            z-index: 10;
        }

        header h1 {
            font-size: 1.25rem;
            color: var(--text-main);
            font-weight: 700;
        }

        /* --- Layout Container (Sidebar + Main) --- */
        .layout-container {
            display: flex;
            flex: 1; /* Fills remaining height below header */
            height: calc(100vh - var(--header-height));
        }

        /* --- 2. SIDEBAR (Fixed Width, Independent Scroll) --- */
        aside {
            width: var(--sidebar-width);
            background-color: var(--bg-sidebar);
            color: #e5e7eb;
            flex-shrink: 0; /* Prevent sidebar from shrinking */
            overflow-y: auto; /* Enable independent scrolling */
            display: flex;
            flex-direction: column;
        }

        .nav-item {
            padding: 16px 24px;
            cursor: pointer;
            transition: background 0.2s;
            font-size: 0.95rem;
        }

        .nav-item:hover {
            background-color: #374151;
        }

        .nav-item.active {
            background-color: #374151;
            border-left: 4px solid var(--primary-color);
        }

        /* --- 3. MAIN CONTENT (Fills remaining, Independent Scroll) --- */
        main {
            flex: 1; /* Takes up all remaining width */
            background-color: var(--bg-body);
            overflow-y: auto; /* Enable independent scrolling */
            padding: 24px;
        }

        /* --- 4. CARDS GRID (Responsive) --- */
        .card-grid {
            display: grid;
            grid-template-columns: 1fr; /* Default: 1 column */
            gap: 24px;
            max-width: 1200px;
            margin: 0 auto;
        }

        /* Media Query: 2 columns on desktop (≥768px) */
        @media (min-width: 768px) {
            .card-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }

        /* --- 5. CARD STYLING --- */
        .card {
            background-color: var(--bg-card);
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            border: 1px solid var(--border-color);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }

        /* Image Container - Maintains 16:9 Aspect Ratio */
        .card-image {
            width: 100%;
            aspect-ratio: 16 / 9; /* Requirement: 16:9 */
            overflow: hidden;
            background-color: #e5e7eb;
        }

        .card-image img {
            width: 100%;
            height: 100%;
            object-fit: cover; /* Ensures image fills the container without distortion */
            display: block;
        }

        .card-content {
            padding: 20px;
            display: flex;
            flex-direction: column;
            flex-grow: 1; /* Pushes footer to bottom */
        }

        .card-title {
            font-size: 1.125rem;
            font-weight: 600;
            color: var(--text-main);
            margin-bottom: 8px;
        }

        .card-desc {
            font-size: 0.875rem;
            color: var(--text-muted);
            line-height: 1.5;
            margin-bottom: 16px;
            flex-grow: 1; /* Spreads content between title and footer */
        }

        .card-footer {
            display: flex;
            justify-content: space-between; /* Requirement: Aligns buttons left/right */
            align-items: center;
            border-top: 1px solid var(--border-color);
            padding-top: 16px;
        }

        .btn {
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 0.875rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            text-decoration: none;
            border: none;
        }

        .btn-primary {
            background-color: var(--primary-color);
            color: white;
        }

        .btn-primary:hover {
            background-color: #2563eb;
        }

        .btn-outline {
            background-color: transparent;
            border: 1px solid var(--border-color);
            color: var(--text-main);
        }

        .btn-outline:hover {
            background-color: #f9fafb;
            border-color: #d1d5db;
        }

        /* Scrollbar Styling for Webkit */
        aside::-webkit-scrollbar,
        main::-webkit-scrollbar {
            width: 8px;
        }

        aside::-webkit-scrollbar-thumb,
        main::-webkit-scrollbar-thumb {
            background-color: #4b5563;
            border-radius: 4px;
        }

        aside::-webkit-scrollbar-track,
        main::-webkit-scrollbar-track {
            background-color: transparent;
        }
    </style>
</head>
<body>

    <!-- HEADER -->
    <header>
        <h1>Dashboard</h1>
    </header>

    <!-- LAYOUT WRAPPER -->
    <div class="layout-container">
        
        <!-- SIDEBAR -->
        <aside>
            <div class="nav-item active">Overview</div>
            <div class="nav-item">Analytics</div>
            <div class="nav-item">Customers</div>
            <div class="nav-item">Settings</div>
            <div class="nav-item">Support</div>
        </aside>

        <!-- MAIN CONTENT -->
        <main>
            <div class="card-grid">
                <!-- Card 1 -->
                <article class="card">
                    <div class="card-image">
                        <!-- Picsum image with 16:9 aspect ratio -->
                        <img src="https://picsum.photos/seed/tech1/600/338" alt="Card Image 1">
                    </div>
                    <div class="card-content">
                        <h2 class="card-title">Project Alpha</h2>
                        <p class="card-desc">
                            This project involves developing a scalable web application architecture. We are focusing on performance optimization and user experience.
                        </p>
                        <div class="card-footer">
                            <button class="btn btn-primary">View Details</button>
                            <button class="btn btn-outline">Edit</button>
                        </div>
                    </div>
                </article>

                <!-- Card 2 -->
                <article class="card">
                    <div class="card-image">
                        <img src="https://picsum.photos/seed/tech2/600/338" alt="Card Image 2">
                    </div>
                    <div class="card-content">
                        <h2 class="card-title">Marketing Strategy</h2>
                        <p class="card-desc">
                            Q4 marketing campaigns are now live. We are tracking engagement metrics across all social platforms to ensure maximum reach.
                        </p>
                        <div class="card-footer">
                            <button class="btn btn-primary">View Analytics</button>
                            <button class="btn btn-outline">Edit</button>
                        </div>
                    </div>
                </article>

                <!-- Card 3 -->
                <article class="card">
                    <div class="card-image">
                        <img src="https://picsum.photos/seed/tech3/600/338" alt="Card Image 3">
                    </div>
                    <div class="card-content">
                        <h2 class="card-title">Team Growth</h2>
                        <p class="card-desc">
                            We have successfully onboarded three new developers and two designers this month. Check out our current team structure.
                        </p>
                        <div class="card-footer">
                            <button class="btn btn-primary">Team Page</button>
                            <button class="btn btn-outline">Edit</button>
                        </div>
                    </div>
                </article>

                <!-- Card 4 -->
                <article class="card">
                    <div class="card-image">
                        <img src="https://picsum.photos/seed/tech4/600/338" alt="Card Image 4">
                    </div>
                    <div class="card-content">
                        <h2 class="card-title">Client Feedback</h2>
                        <p class="card-desc">
                            Latest surveys show a 98% satisfaction rate. We have documented all feedback to improve our product roadmap for next year.
                        </p>
                        <div class="card-footer">
                            <button class="btn btn-primary">Read Reviews</button>
                            <button class="btn btn-outline">Edit</button>
                        </div>
                    </div>
                </article>
            </div>
        </main>
    </div>

</body>
</html>
```

### Implementation Strategy

To satisfy all requirements without JavaScript, I utilized two primary CSS layout techniques:

1.  **Flexbox (For the Shell Layout):**
    *   **Header:** Placed as the first child of the body with a fixed height and `flex-shrink: 0`. This ensures it always stays at the top.
    *   **Main Container:** The `layout-container` uses `flex: 1` to fill the remaining screen space.
    *   **Independent Scrolling:** I applied `overflow-y: auto` to both the `<aside>` (sidebar) and `<main>` (content) containers. This allows the sidebar to scroll vertically while the main content stays fixed (if the main content is short), or vice versa. The body itself does not scroll (`overflow: hidden`), keeping the interface app-like.

2.  **CSS Grid (For the Card Layout):**
    *   **Responsiveness:** The `.card-grid` uses a media query `@media (min-width: 768px)`. By default, it is `1fr` (1 column). Above 768px, it switches to `repeat(2, 1fr)` (2 columns).
    *   **Card Image:** The `.card-image` container uses the `aspect-ratio: 16 / 9` property. This guarantees the image maintains the requested ratio regardless of the actual image dimensions. The `object-fit: cover` ensures the image fills the box without stretching.

*Response time: 443.8s*

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
Here is a comprehensive design for the real-time notification system tailored for your project management tool.

### 1. Transport Mechanism: Server-Sent Events (SSE)

**Choice:** **Server-Sent Events (SSE)**.

**Justification:**
*   **Unidirectional Flow:** Notifications are inherently "firehose" events (the server pushes data to the client). The client does not need to send back a request to trigger a notification.
*   **Automatic Reconnection:** If a user’s internet cuts out and reconnects, the `EventSource` API in the browser automatically attempts to reconnect. This is much easier to manage than WebSocket disconnection handling.
*   **Lightweight:** SSE runs over a standard HTTP connection. It does not require managing complex socket handshakes or handling binary data, making it lighter on the server than WebSockets.
*   **Built-in Retry Headers:** The protocol supports `Retry` headers, allowing the server to tell the browser how long to wait before retrying a connection.

*Note: If your project management tool requires a massive amount of two-way interaction (like a real-time chat), you would switch to WebSockets. For general project updates (comments, deadlines), SSE is the optimal choice.*

---

### 2. Database Schema Design

We need a centralized table to store notifications, as well as a way to track what a user has already seen.

**Table: `notifications`**
This table acts as a "firehose" of events. We index `user_id` and `created_at` to allow for fast filtering.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PK | Unique identifier |
| `user_id` | UUID | FK, Index | Recipient of the notification |
| `type` | VARCHAR | NOT NULL | Enum: `task_assigned`, `comment_added`, `deadline_warning` |
| `payload` | JSON | NOT NULL | Contextual data (e.g., `{ "task_id": "123", "task_title": "Fix Bug" }`) |
| `is_read` | BOOLEAN | DEFAULT FALSE | State tracking |
| `created_at` | TIMESTAMP | DEFAULT NOW() | For sorting and delta-syncing |

**Table: `user_preferences` (Optional)**
To reduce noise, users might want to disable deadline warnings for weekends.
| Column | Type | Constraints |
| :--- | :--- | :--- |
| `user_id` | UUID | PK |
| `enable_deadline_alerts` | BOOLEAN | DEFAULT TRUE |

---

### 3. Handling Offline Users (The "Delta" Strategy)

**Answer:** Yes, they do get notifications, but they are delivered **once** upon reconnecting, not repeatedly.

**Implementation:**
1.  **Client:** When the user connects (or refreshes the page), the client requests the server: `GET /notifications?since=timestamp`.
2.  **Server:** The server looks for any notifications where `created_at > last_seen_timestamp`.
3.  **Delivery:** The server streams these notifications via SSE.
4.  **Client:** As the user reads notifications, the client updates a local `last_notification_id` in its database (or LocalStorage).
5.  **Cleanup:** Old notifications should be archived or soft-deleted periodically to prevent the table from growing infinitely.

---

### 4. Implementing the Deadline Check

**Choice:** **Background Worker (Queue) with State Tracking.**

**Approach:**
We should not run the check synchronously in the main request loop. We need a background process. A simple Cron job is sufficient, but a **Worker Queue** allows for better handling of large datasets.

**Algorithm:**
1.  **Trigger:** A cron job runs every hour (or triggers on task update).
2.  **Query:** Select tasks that have a deadline *today* or *tomorrow* but have *not* yet triggered a warning for this specific user.
3.  **Notification Creation:** For every task found, insert a row into the `notifications` table.
4.  **Locking:** To ensure a user isn't spammed if the job runs twice in an hour, we need a way to mark a task as "warned for this cycle."

**Pseudocode (SQL approach):**
```sql
-- Mark tasks that we are about to process to avoid double-dipping
UPDATE tasks 
SET last_checked_at = NOW() 
WHERE deadline <= NOW() + INTERVAL '24 hours' 
AND last_checked_at < NOW();

-- Check for new tasks that need warnings (those updated in the last hour)
SELECT t.id, t.deadline, u.id as user_id
FROM tasks t
JOIN project_members pm ON t.project_id = pm.project_id
JOIN users u ON pm.user_id = u.id
WHERE t.deadline BETWEEN NOW() AND NOW() + INTERVAL '24 hours'
AND t.last_checked_at < NOW();
```

**Refined Approach (Event-Driven + Scheduled):**
To be "real-time" accurate, the "Update Task" action should trigger the worker immediately. The cron job serves as a safety net for tasks created while the server was down.

---

### 5. Scaling to 100,000 Concurrent Users

Handling 100k concurrent SSE connections is a significant engineering challenge.

**1. Stateless API Architecture:**
The API nodes must be stateless. They cannot rely on local variables to track if a user is connected. The "connection state" lives in the Load Balancer or a dedicated Service Registry (like Consul or ZooKeeper), or more commonly, we use a **Redis-backed Pub/Sub** pattern.

**2. The Pub/Sub Pattern (The Key to Scaling):**
*   **Client A** connects to API Node 1.
*   **Client B** connects to API Node 2.
*   **Event:** A comment is added on Node 1.
*   **Logic:** Node 1 publishes the notification event to a Redis channel named `user:123:notifications`.
*   **Logic:** Node 2 (which holds Client B) listens to `user:123:notifications`.
*   **Result:** Node 2 instantly pushes the new notification to Client B via its active SSE connection. No database read is needed for this specific action.

**3. Read Replicas for List Fetching:**
When a user loads their notification center, the API must query the database. This query should be routed to a **Read Replica** database, never the primary (Write) database, to ensure high availability and speed.

**4. Connection Pooling & Nginx:**
*   Use Nginx (or HAProxy) with HTTP/2 enabled to multiplex many SSE connections over a single TCP connection to the backend.
*   Tune your database connection pool to allow enough connections for your worker processes without starving the main API.

**Summary of Architecture:**
[Client] <--(SSE)--> [API Node] <--(Redis Pub/Sub)--> [API Node]
                                       |
                                  [Read Replica DB]

*Response time: 244.7s*

---
