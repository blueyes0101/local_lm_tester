# Model: qwen2.5-coder:1.5b
**Test Date:** 2026-03-10 20:49:16
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
### API Design for Multi-Tenant SaaS Project Management Tool

#### 1. Define All Endpoints (Method + Path) Following REST Conventions

#### Create Task
**POST /tasks**
- Request Body:
  ```json
  {
    "workspaceId": "WS-123",
    "projectId": "PRJ-456",
    "title": "Design UI",
    "description": "Implement the user interface.",
    "assigneeId": "USER-789",
    "status": "Pending",
    "dueDate": "2023-10-31T12:00:00"
  }
  ```
- Response:
  ```json
  {
    "taskId": "TASK-101",
    "workspaceId": "WS-123",
    "projectId": "PRJ-456",
    "title": "Design UI",
    "description": "Implement the user interface.",
    "assigneeId": "USER-789",
    "status": "Pending",
    "dueDate": "2023-10-31T12:00:00",
    "createdAt": "2023-10-01T12:00:00"
  }
  ```

#### Update Task Status
**PUT /tasks/:taskId**
- Request Body:
  ```json
  {
    "status": "In Progress"
  }
  ```
- Response:
  ```json
  {
    "taskId": "TASK-101",
    "workspaceId": "WS-123",
    "projectId": "PRJ-456",
    "title": "Design UI",
    "description": "Implement the user interface.",
    "assigneeId": "USER-789",
    "status": "In Progress",
    "dueDate": "2023-10-31T12:00:00",
    "createdAt": "2023-10-01T12:00:00"
  }
  ```

#### List Tasks with Filters (Assignee, Status, Due Date)
**GET /tasks**
- Query Parameters:
  - `assigneeId` (optional): Filter by assignee
  - `status` (optional): Filter by status
  - `dueDate` (optional): Filter by due date
  - `page` (optional): Pagination (default: 1)
  - `limit` (optional): Pagination (default: 10)
- Response:
  ```json
  {
    "tasks": [
      {
        "taskId": "TASK-101",
        "workspaceId": "WS-123",
        "projectId": "PRJ-456",
        "title": "Design UI",
        "description": "Implement the user interface.",
        "assigneeId": "USER-789",
        "status": "Pending",
        "dueDate": "2023-10-31T12:00:00",
        "createdAt": "2023-10-01T12:00:00"
      },
      {
        "taskId": "TASK-102",
        "workspaceId": "WS-123",
        "projectId": "PRJ-456",
        "title": "Code Review",
        "description": "Review the code for bugs.",
        "assigneeId": "USER-789",
        "status": "Assigned",
        "dueDate": "2023-10-15T12:00:00",
        "createdAt": "2023-10-01T12:00:00"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "totalPages": 2,
      "totalItems": 2
    }
  }
  ```

#### Add Comment
**POST /tasks/:taskId/comments**
- Request Body:
  ```json
  {
    "content": "Task is assigned to the new team member."
  }
  ```
- Response:
  ```json
  {
    "commentId": "COM-101",
    "taskId": "TASK-101",
    "content": "Task is assigned to the new team member."
    "createdAt": "2023-10-01T12:00:00"
  }
  ```

### Define Error Response Format

```json
{
  "error": {
    "code": "400",
    "message": "Invalid request"
  }
}
```

### Handle Pagination

Pagination is handled using the `page` and `limit` query parameters. The response envelope includes the `tasks` array, `pagination` object, and `totalItems` to help clients understand the total number of items and the current page.

### HTTP Status Codes

- **201 Created**: Task created successfully.
- **200 OK**: Task updated successfully.
- **200 OK**: Tasks fetched successfully with pagination.
- **201 Created**: Comment added successfully.
- **400 Bad Request**: Invalid request.
- **404 Not Found**: Resource not found.
- **403 Forbidden**: Access denied.
- **401 Unauthorized**: Authentication required.

### Example of Pagination Response

```json
{
  "tasks": [
    {
      "taskId": "TASK-101",
      "workspaceId": "WS-123",
      "projectId": "PRJ-456",
      "title": "Design UI",
      "description": "Implement the user interface.",
      "assigneeId": "USER-789",
      "status": "Pending",
      "dueDate": "2023-10-31T12:00:00",
      "createdAt": "2023-10-01T12:00:00"
    },
    {
      "taskId": "TASK-102",
      "workspaceId": "WS-123",
      "projectId": "PRJ-456",
      "title": "Code Review",
      "description": "Review the code for bugs.",
      "assigneeId": "USER-789",
      "status": "Assigned",
      "dueDate": "2023-10-15T12:00:00",
      "createdAt": "2023-10-01T12:00:00"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "totalPages": 2,
    "totalItems": 2
  }
}
```

### Additional Considerations

- **Authentication**: Use OAuth2 or JWT for user authentication.
- **Scopes**: Define scopes for different actions (e.g., `tasks:read`, `tasks:write`, `comments:read`, `comments:write`).
- **Rate Limiting**: Implement rate limiting to prevent abuse.
- **Security**: Use HTTPS to encrypt data in transit and use encryption at rest for sensitive data.

*Response time: 12.1s*

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
To implement the required endpoint in Node.js + Express + TypeScript, we will follow these steps:

1. Install the necessary dependencies:
```bash
npm install express zod @types/express
```

2. Create the `server.ts` file:

```typescript
import express from 'express';
import z from 'zod';
import { Task } from './models/task'; // Assuming this is a custom type for task data

const app = express();
app.use(express.json());

// Define the validation schema
const taskSchema = z.object({
  title: z.string().min(1).max(200),
  status: z.enum(['todo', 'in_progress', 'done', 'cancelled']),
  assignee_id: z.number().nullable(),
  due_date: z.string().optional().nullable(),
});

// Middleware to validate the request body
const validateTask = (req, res, next) => {
  const { title, status, assignee_id, due_date } = req.body;
  const validatedTask = taskSchema.parse({ title, status, assignee_id, due_date });
  req.task = validatedTask;
  next();
};

// Route to update a task
app.patch('/workspaces/:workspaceId/tasks/:taskId', validateTask, async (req, res) => {
  const { workspaceId, taskId } = req.params;
  const task = await Task.findOne({ workspaceId, id: taskId });

  if (!task) {
    return res.status(404).json({ message: 'Task not found' });
  }

  if (req.body.status === 'cancelled' && task.subtasks.length > 0) {
    return res.status(409).json({ message: 'Cannot cancel a task with open subtasks' });
  }

  const updatedTask = await Task.findByIdAndUpdate(taskId, req.task, { new: true });
  res.status(200).json(updatedTask);
});

// Error middleware
app.use((err, req, res, next) => {
  if (err instanceof z.ZodError) {
    return res.status(400).json({ message: err.issues.map((issue) => issue.message) });
  }
  next(err);
});

// Start the server
const port = 3000;
app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});
```

3. Define the `models/task.ts` file:

```typescript
export interface Task {
  id: number;
  title: string;
  status: 'todo' | 'in_progress' | 'done' | 'cancelled';
  assignee_id: number | null;
  due_date: string | null;
  subtasks: Task[];
}
```

4. Write the unit tests for the endpoint:

```typescript
import express from 'express';
import { app, validateTask } from './server';
import { Task } from './models/task';
import { z } from 'zod';
import { strict as assert } from 'assert';

// Define a sample task for testing
const sampleTask: Task = {
  id: 1,
  title: 'Complete the project',
  status: 'todo',
  assignee_id: null,
  due_date: '2023-10-31',
  subtasks: [],
};

// Mock the Task model methods
const mockTaskModel = {
  findOne: jest.fn().mockResolvedValue(sampleTask),
  findByIdAndUpdate: jest.fn(),
};

// Test the validateTask middleware
describe('validateTask middleware', () => {
  it('should validate the request body', async () => {
    const req = {
      body: {
        title: 'Complete the project',
        status: 'pending', // Invalid status
        assignee_id: 1,
        due_date: '2023-10-31',
      },
    };
    const res = { json: jest.fn() };
    const next = jest.fn();

    await validateTask(req, res, next);

    expect(req.task).toEqual({
      title: 'Complete the project',
      status: 'pending', // Updated status
      assignee_id: 1,
      due_date: '2023-10-31',
    });
    expect(next).toHaveBeenCalled();
  });

  it('should return a 400 with validation errors', async () => {
    const req = {
      body: {
        title: 'Complete the project',
        status: 'invalid', // Invalid status
        assignee_id: 1,
        due_date: '2023-10-31',
      },
    };
    const res = { json: jest.fn() };
    const next = jest.fn();

    await validateTask(req, res, next);

    expect(res.json).toHaveBeenCalledWith({ message: ['"status" must be one of [todo, in_progress, done, cancelled]'] });
    expect(next).not.toHaveBeenCalled();
  });
});

// Test the update task endpoint
describe('updateTask endpoint', () => {
  it('should update the task', async () => {
    jest.spyOn(mockTaskModel, 'findByIdAndUpdate');

    const req = {
      params: {
        workspaceId: '1',
        taskId: '1',
      },
      body: {
        title: 'Complete the project',
        status: 'in_progress',
        assignee_id: 2,
        due_date: '2023-11-01',
      },
    };
    const res = { json: jest.fn() };
    const next = jest.fn();

    await app.patch('/workspaces/:workspaceId/tasks/:taskId', validateTask, async (req, res) => {
      await mockTaskModel.findByIdAndUpdate(req.taskId, req.task, { new: true });
      res.status(200).json(req.task);
    });

    expect(req.task).toEqual({
      title: 'Complete the project',
      status: 'in_progress',
      assignee_id: 2,
      due_date: '2023-11-01',
    });
    expect(mockTaskModel.findByIdAndUpdate).toHaveBeenCalledWith('1', req.task, { new: true });
    expect(next).toHaveBeenCalled();
  });

  it('should return a 404 if the task is not found', async () => {
    jest.spyOn(mockTaskModel, 'findByIdAndUpdate').mockResolvedValue(null);

    const req = {
      params: {
        workspaceId: '1',
        taskId: '2',
      },
      body: {
        title: 'Complete the project',
        status: 'in_progress',
        assignee_id: 2,
        due_date: '2023-11-01',
      },
    };
    const res = { json: jest.fn() };
    const next = jest.fn();

    await app.patch('/workspaces/:workspaceId/tasks/:taskId', validateTask, async (req, res) => {
      await mockTaskModel.findByIdAndUpdate(req.taskId, req.task, { new: true });
      res.status(200).json(req.task);
    });

    expect(res.status).toBe(404);
    expect(next).not.toHaveBeenCalled();
  });

  it('should return a 409 if the task is cancelled and has open subtasks', async () => {
    jest.spyOn(mockTaskModel, 'findByIdAndUpdate').mockResolvedValue(sampleTask);

    const req = {
      params: {
        workspaceId: '1',
        taskId: '1',
      },
      body: {
        title: 'Complete the project',
        status: 'cancelled',
        assignee_id: 2,
        due_date: '2023-11-01',
      },
    };
    const res = { json: jest.fn() };
    const next = jest.fn();

    await app.patch('/workspaces/:workspaceId/tasks/:taskId', validateTask, async (req, res) => {
      await mockTaskModel.findByIdAndUpdate(req.taskId, req.task, { new: true });
      res.status(200).json(req.task);
    });

    expect(res.status).toBe(409);
    expect(next).not.toHaveBeenCalled();
  });
});
```

5. Run the tests:

```bash
npm test
```

This code snippet provides a complete implementation of the required endpoint with validation and error handling. The `server.ts` file contains the main application logic, the `validateTask` middleware handles the request body validation, the `Task` interface defines the task structure, and the `models/task.ts` file mocks the `Task` model methods for testing. The unit tests cover various scenarios, including successful updates, validation errors, 404 and 409 cases.

*Response time: 14.1s*

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
To implement a complete authentication system in Node.js + Express + TypeScript, we'll follow these steps:

1. **Set up the project**:
   - Install necessary dependencies: `express`, `bcrypt`, `jsonwebtoken`, `cors`.
   - Set up the Express app and middleware.

2. **Create the user model**:
   - Define the user schema and model.

3. **Implement the registration route**:
   - Hash the password using bcrypt.
   - Save the user to the database.

4. **Implement the login route**:
   - Validate the credentials.
   - Generate an access token and a refresh token.
   - Store the refresh token in a httpOnly cookie.
   - Return the access token and refresh token.

5. **Implement the protected route**:
   - Use the `authMiddleware` to validate the access token.
   - Attach the user to `req.user`.

6. **Handle expired tokens**:
   - Implement a middleware to check if the access token is expired.
   - Return an appropriate error response.

7. **Use httpOnly cookies for refresh tokens**:
   - Explain the security reasons for using httpOnly cookies for refresh tokens.

### Step 1: Set up the project

Create a new directory for your project and initialize it:

```bash
mkdir auth-app
cd auth-app
npm init -y
```

Install the required dependencies:

```bash
npm install express bcrypt jsonwebtoken cors
```

### Step 2: Create the user model

Create a new file `src/models/User.ts`:

```typescript
import mongoose from 'mongoose';

const UserSchema = new mongoose.Schema({
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true },
});

const User = mongoose.model('User', UserSchema);

export default User;
```

### Step 3: Implement the registration route

Create a new file `src/routes/auth.ts`:

```typescript
import express from 'express';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { User } from '../models/User';

const authRouter = express.Router();

// Middleware to hash the password
const hashPassword = async (password: string): Promise<string> => {
  const salt = await bcrypt.genSalt(12);
  return bcrypt.hash(password, salt);
};

// Registration route
authRouter.post('/auth/register', async (req, res) => {
  const { email, password } = req.body;

  try {
    const user = new User({ email, password: await hashPassword(password) });
    await user.save();
    res.status(201).json(user);
  } catch (error) {
    res.status(500).json({ error: 'Failed to register user' });
  }
});

export default authRouter;
```

### Step 4: Implement the login route

Create a new file `src/routes/auth.ts`:

```typescript
import express from 'express';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { User } from '../models/User';

const authRouter = express.Router();

// Login route
authRouter.post('/auth/login', async (req, res) => {
  const { email, password } = req.body;

  try {
    const user = await User.findOne({ email });

    if (!user) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const isAuthenticated = await bcrypt.compare(password, user.password);

    if (!isAuthenticated) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const accessToken = jwt.sign(
      { userId: user._id, email, role: user.role, iat: Date.now(), exp: Date.now() + 900000 } // 15 minutes
    );

    const refreshToken

*Response time: 6.6s*

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
### 1. POST /auth/refresh — use the refresh token from cookie to issue a new access token. Rotate the refresh token (issue new one, invalidate old one).

#### Implementation:
To implement the refresh token rotation, you need to ensure that the refresh token is invalidated before issuing a new one. This can be done by storing the refresh tokens in Redis and checking for their existence before issuing a new one.

#### Redis Data Structure and TTL Strategy:
- **Data Structure:** Use a Redis set to store the refresh tokens. This set will help in efficiently checking if a refresh token exists.
- **TTL Strategy:** Set the TTL (Time to Live) for the refresh tokens to be relatively short, such as 10 minutes or 1 hour. This means that the refresh tokens will be valid for a short period, reducing the risk of token reuse.

#### Example Implementation:
```python
import redis
import time

# Initialize Redis client
r = redis.Redis(host='localhost', port=6379, db=0)

def refresh_token(request):
    # Get refresh token from cookie
    refresh_token = request.cookies.get('refresh_token')
    
    if not refresh_token:
        return {"error": "Missing refresh token"}, 401
    
    # Check if the refresh token exists in Redis
    if r.sismember('refresh_tokens', refresh_token):
        # Invalidate the existing refresh token
        r.srem('refresh_tokens', refresh_token)
        
        # Issue a new access token
        new_access_token = issue_access_token()
        
        # Store the new access token in Redis with a TTL
        r.setex('access_tokens:{}'.format(new_access_token), 60 * 15, 'true')  # 15 minutes
        
        # Rotate the refresh token
        new_refresh_token = issue_refresh_token()
        r.sadd('refresh_tokens', new_refresh_token)
        
        # Set the new refresh token in the cookie
        response = {'access_token': new_access_token, 'refresh_token': new_refresh_token}
        response['cookie'] = {'name': 'refresh_token', 'value': new_refresh_token, 'expires': time.time() + 60 * 60}  # 1 hour
        return response, 200
    else:
        return {"error": "Invalid refresh token"}, 401
```

### 2. POST /auth/logout — invalidate the refresh token, clear the cookie

#### Implementation:
To handle the logout request, you need to invalidate the refresh token and clear the cookie from the client.

#### Example Implementation:
```python
def logout(request):
    # Clear the refresh token from the cookie
    response = {'message': 'Logged out successfully'}
    response['cookie'] = {'name': 'refresh_token', 'value': '', 'expires': 0}  # Expire immediately
    return response, 200
```

### 3. Implement refresh token rotation with a Redis-based token store

#### Example Implementation:
```python
import redis
import time

# Initialize Redis client
r = redis.Redis(host='localhost', port=6379, db=0)

def issue_access_token():
    # Generate a new access token
    access_token = 'new_access_token'
    # Store the access token in Redis with a TTL
    r.setex('access_tokens:{}'.format(access_token), 60 * 15, 'true')  # 15 minutes
    return access_token

def issue_refresh_token():
    # Generate a new refresh token
    refresh_token = 'new_refresh_token'
    # Store the refresh token in Redis with a TTL
    r.sadd('refresh_tokens', refresh_token)
    return refresh_token
```

### 4. How do you handle the case where a refresh token is used twice? (token reuse detection)

#### Implementation:
To detect token reuse, you can use Redis to track the number of times a refresh token is used. If a refresh token is used more than once, you can invalidate it.

#### Example Implementation:
```python
import redis
import time

# Initialize Redis client
r = redis.Redis(host='localhost', port=6379, db=0)

def refresh_token(request):
    # Get refresh token from cookie
    refresh_token = request.cookies.get('refresh_token')
    
    if not refresh_token:
        return {"error": "Missing refresh token"}, 401
    
    # Check if the refresh token exists in Redis
    if r.sismember('refresh_tokens', refresh_token):
        # Increment the usage count for the refresh token
        current_usage = r.incr('usage_counts:{}'.format(refresh_token))
        
        if current_usage > 1:
            # Invalidate the refresh token
            r.srem('refresh_tokens', refresh_token)
            
            # Clear the cookie
            response = {'message': 'Logged out successfully'}
            response['cookie'] = {'name': 'refresh_token', 'value': '', 'expires': 0}  # Expire immediately
            return response, 200
        else:
            return {"message": 'Token is still valid'}, 200
    else:
        return {"error": "Invalid refresh token"}, 401
```

### 5. A user changes their password — how do you invalidate ALL their existing sessions?

#### Implementation:
To invalidate all existing sessions when a user changes their password, you can use Redis to clear the session tokens for the user.

#### Example Implementation:
```python
import redis
import time

# Initialize Redis client
r = redis.Redis(host='localhost', port=6379, db=0)

def invalidate_sessions(username):
    # Get all session tokens for the user
    session_tokens = r.smembers('sessions:{}'.format(username))
    
    if session_tokens:
        # Invalidate each session token
        for session_token in session_tokens:
            r.delete('session_tokens:{}'.format(session_token))
        
        # Clear the session tokens in Redis
        r.delete('sessions:{}'.format(username))
    
    return {"message": 'All sessions invalidated'}
```

### 6. What is the difference between token blacklisting and token rotation? When would you use each?

#### Token Blacklisting:
- **Definition:** Token blacklisting is a technique where a refresh token is marked as invalid when it is used. This is done to prevent token reuse and ensure that the refresh token cannot be used again.
- **Implementation:** You can use Redis to mark a refresh token as invalid by setting a flag in Redis. For example, you can use a set to store the refresh tokens and set a flag in Redis for each refresh token.
- **Use Case:** Token blacklisting is typically used when you want to ensure that a refresh token cannot be used again after it has been used, regardless of the time it has been unused.
- **When to Use:** Token blacklisting is typically used when you want to ensure that a refresh token cannot be used again after it has been used, regardless of the time it has been unused.

#### Token Rotation:
- **Definition:** Token rotation is a technique where

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
1. **TypeScript Interface for Props**:
   We'll define the props for our DataTable component, including columns and data, along with optional properties for client-side sorting, row selection, pagination, and custom renderCell for action buttons.

   ```typescript
   interface DataTableProps<T> {
     columns: ColumnDef<T>[]; // Array of column definitions
     data: T[]; // Array of objects representing table rows
     defaultSort?: string; // Default column to sort by
     pageSizeOptions?: number[]; // Available page size options
     onChangeSort?: (columnKey: string, direction: 'asc' | 'desc' | 'none') => void; // Callback for sorting change
     onChangeSelectAll?: (selectAll: boolean) => void; // Callback for select all change
     onChangePage?: (pageNumber: number) => void; // Callback for page change
     renderCell?: (data: T, rowIndex: number) => ReactNode; // Optional renderCell for action button
   }

   interface ColumnDef<T> {
     key: string; // Unique key for the column
     header: string; // Header text for the column
     width?: number; // Width of the column
     sortable?: boolean; // Whether the column is sortable
     renderCell?: (data: T, rowIndex: number) => ReactNode; // Optional renderCell for custom column
   }
   ```

2. **Complete Component Implementation**:
   We'll implement the DataTable component with the necessary state, functionality, and event handlers.

   ```typescript
   import React, { useState, useMemo, useEffect } from 'react';
   import { Table, TableHeader, TableBody, TableCell, TablePagination } from 'react-table';
   import 'react-table/react-table.css';

   const DataTable: React.FC<DataTableProps<any>> = ({
     columns,
     data,
     defaultSort,
     pageSizeOptions = [10, 25, 50],
     onChangeSort,
     onChangeSelectAll,
     onChangePage,
     renderCell,
   }) => {
     const [selectedRows, setSelectedRows] = useState<number[]>([]);
     const [sortedColumnKey, setSortedColumnKey] = useState<string | undefined>(defaultSort);
     const [pageSize, setPageSize] = useState(pageSizeOptions[0]);
     const [currentPage, setCurrentPage] = useState(0);

     const handleColumnClick = (columnKey: string) => {
       if (sortedColumnKey === columnKey) {
         setSortedColumnKey('none');
       } else {
         setSortedColumnKey(columnKey);
       }
       onChangeSort?.(columnKey, sortedColumnKey === 'none' ? 'none' : sortedColumnKey === 'asc' ? 'desc' : 'asc');
     };

     const handleSelectAll = (selectAll: boolean) => {
       if (selectAll) {
         setSelectedRows(data.map((row) => row.id));
       } else {
         setSelectedRows([]);
       }
       onChangeSelectAll?.(selectAll);
     };

     const handlePageChange = (pageNumber: number) => {
       setCurrentPage(pageNumber);
       onChangePage?.(pageNumber);
     };

     const rows = useMemo(() => {
       return data.slice(currentPage * pageSize, currentPage * pageSize + pageSize);
     }, [data, currentPage, pageSize]);

     const headerCells = useMemo(() => columns.map((column) => (
       <TableHeader key={column.key}>
         <button onClick={() => handleColumnClick(column.key)}>
           {column.header}
           {sortedColumnKey === column.key && sortedColumnKey !== 'none' ? (
             <span className="sort-icon" style={{ transform: `rotate(${sortedColumnKey === 'asc' ? '180deg' : '0deg'})` }} />
           ) : (
             <span className="sort-icon" />
           )}
         </button>
       </TableHeader>
     )));

     const rowCells = useMemo(() => {
       return rows.map((row, rowIndex) => (
         <TableRow key={row.id}>
           {columns.map((column, columnIndex) => (
             <TableCell key={column.key}>
               {column.renderCell ? column.renderCell(row, rowIndex) : row[column.key]}
             </TableCell>
           ))}
           {renderCell ? renderCell(row, rowIndex) : null}
         </TableRow>
       ));
     }, [rows, columns, renderCell]);

     const selectAllCheckbox = useMemo(() => (
       <Checkbox
         checked={selectedRows.length === data.length}
         onChange={(event) => handleSelectAll(event.target.checked)}
       />
     ), [selectedRows, data]);

     const pagination = useMemo(() => (
       <TablePagination
         rowsPerPageOptions={pageSizeOptions}
         count={data.length}
         page={currentPage}
         onChangePage={handlePageChange}
       />
     ), [pageSizeOptions, data.length, currentPage, handlePageChange]);

     return (
       <div>
         <Table
           columns={headerCells}
           data={rowCells}
           sortable
           pagination
         />
         {selectAllCheckbox}
         {pagination}
       </div>
     );
   };

   export default DataTable;
   ```

3. **Usage Example**:
   Let's use the DataTable component with an example data structure and a custom renderCell for an action button.

   ```typescript
   interface Product {
     id: number;
     name: string;
     price: number;
   }

   const products: Product[] = [
     { id: 1, name: 'Laptop', price: 1200 },
     { id: 2, name: 'Smartphone', price: 800 },
     { id: 3, name: 'Tablet', price: 400 },
     // Add more products as needed
   ];

   const ProductDataTable: React.FC = () => (
     <DataTable
       columns={[
         {
           key: 'name',
           header: 'Name',
         },
         {
           key: 'price',
           header: 'Price',
           sortable: true,
         },
         {
           key: 'actions',
           header: 'Actions',
           renderCell: (data, rowIndex) => (
             <div>
               <button onClick={() => console.log(`Delete ${data.name}`)}>Delete</button>
               <button onClick={() => console.log(`Edit ${data.name}`)}>Edit</button>
             </div>
           ),
         },
       ]}
       data={products}
       pageSizeOptions={[10, 25, 50]}
       onChangeSort={(columnKey, direction) => console.log(`Sorted by ${columnKey} in ${direction}`)}
       onChangeSelectAll={(selectAll) => console.log(`Select all: ${selectAll}`)}
       onChangePage={(pageNumber) => console.log(`Page changed to ${pageNumber}`)}
     />
   );

   export default ProductDataTable;
   ```

4. **Memoizing the Component**:
   Since the DataTable component is quite complex and has several stateful components, we can memoize it to avoid unnecessary re-renders. We can use React.memo to wrap the DataTable component and pass a custom comparison function.

   ```typescript
   import React, { useMemo, useEffect } from 'react';
   import { Table, TableHeader, TableBody, TableCell, TablePagination } from 'react-table';
   import 'react-table/react-table.css';

   const DataTable: React.FC<DataTableProps<any>> = React.memo(({ columns, data, ...props }) => {
     const [selectedRows, setSelectedRows] = useState<number[]>([]);
     const [sortedColumnKey, setSortedColumnKey] = useState<string | undefined>(props.defaultSort);
     const [pageSize, setPageSize] = useState(props.pageSizeOptions[0]);
     const [currentPage, setCurrentPage] = useState(0);

     const handleColumnClick = (columnKey: string) => {
       if (sortedColumnKey === columnKey) {
         setSortedColumnKey('none');
       } else {
         setSortedColumnKey(columnKey);
       }
       props.onChangeSort?.(columnKey, sortedColumnKey === 'none' ? 'none' : sortedColumnKey === 'asc' ? 'desc' : 'asc');
     };

     const handleSelectAll = (selectAll: boolean) => {
       if (selectAll) {
         setSelectedRows(data.map((row) => row.id));
       } else {
         setSelectedRows([]);
       }
       props.onChangeSelectAll?.(selectAll);
     };

     const handlePageChange = (pageNumber: number) => {
       setCurrentPage(pageNumber);
       props.onChangePage?.(pageNumber);
     };

     const rows = useMemo(() => {
       return data.slice(currentPage * pageSize, currentPage * pageSize + pageSize);
     }, [data, currentPage, pageSize]);

     const headerCells = useMemo(() => columns.map((column) => (
       <TableHeader key={column.key}>
         <button onClick={() => handleColumnClick(column.key)}>
           {column.header}
           {sortedColumnKey === column.key && sortedColumnKey !== 'none' ? (
             <span className="sort-icon" style={{ transform: `rotate(${sortedColumnKey === 'asc' ? '180deg' : '0deg'})` }} />
           ) : (
             <span className="sort-icon" />
           )}
         </button>
       </TableHeader>
     )));

     const rowCells = useMemo(() => {
       return rows.map((row, rowIndex) => (
         <TableRow key={row.id}>
           {columns.map((column, columnIndex) => (
             <TableCell key={column.key}>
               {column.renderCell ? column.renderCell(row, rowIndex) : row[column.key]}
             </TableCell>
           ))}
           {props.renderCell ? props.renderCell(row, rowIndex) : null}
         </TableRow>
       ));
     }, [rows, columns, props.renderCell]);

     const selectAllCheckbox = useMemo(() => (
       <Checkbox
         checked={selectedRows.length === data.length}
         onChange={(event) => handleSelectAll(event.target.checked)}
       />
     ), [selectedRows, data]);

     const pagination = useMemo(() => (
       <TablePagination
         rowsPerPageOptions={props.pageSizeOptions}
         count={data.length}
         page={currentPage}
         onChangePage={handlePageChange}
       />
     ), [props.pageSizeOptions, data.length, currentPage, handlePageChange]);

     return (
       <div>
         <Table
           columns={headerCells}
           data={rowCells}
           sortable
           pagination
         />
         {selectAllCheckbox}
         {pagination}
       </div>
     );
   }, [props]);

   export default DataTable;
   ```

   By using `React.memo`, we ensure that the DataTable component re-renders only when its props change. This helps in optimizing the performance of our application by reducing unnecessary re-renders.

*Response time: 16.8s*

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
Sure, let's break down the implementation into detailed steps and then write the code.

### Step 1: Create the `useSearch` Custom Hook

This hook will handle the fetch, debounce, cache, cancellation, and URL sync functionality.

```javascript
import { useState, useEffect, useRef, useCallback } from 'react';

const useSearch = (query: string) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState([]);
  const queryRef = useRef(query);
  const timeoutId = useRef(null);

  const fetchResults = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`/api/search?q=${queryRef.current}`);
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      setResults(data);
    } catch (error) {
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  }, [queryRef]);

  const cancelInFlightRequests = useCallback(() => {
    clearTimeout(timeoutId.current);
  }, []);

  const clearCachedResults = useCallback(() => {
    queryRef.current = query;
    setResults([]);
  }, [queryRef]);

  useEffect(() => {
    // If the query has changed, cancel the in-flight request and clear cached results
    if (query !== queryRef.current) {
      cancelInFlightRequests();
      clearCachedResults();
    }

    // Cancel any existing timeout and set a new one
    clearTimeout(timeoutId.current);
    timeoutId.current = setTimeout(() => {
      fetchResults();
    }, 300);
  }, [query, fetchResults, timeoutId]);

  useEffect(() => {
    // Cache results for 5 minutes
    const cacheData = { query, results };
    const cacheKey = `${query}:${Date.now()}`;

    localStorage.setItem(cacheKey, JSON.stringify(cacheData));

    return () => {
      // Clear the cache when the component unmounts
      localStorage.removeItem(cacheKey);
    };
  }, [query, results]);

  return {
    isLoading,
    error,
    results,
    clearCachedResults,
  };
};
```

### Step 2: Create the `SearchPage` Component

This component will use the `useSearch` hook and render the UI based on the search results.

```javascript
import React, { useEffect, useRef, useState } from 'react';
import { useSearch } from './useSearch';

const SearchPage = () => {
  const query = useRef('');
  const { isLoading, error, results, clearCachedResults } = useSearch(query.current);

  useEffect(() => {
    // Restore query from URL if available
    const searchParams = new URLSearchParams(window.location.search);
    const term = searchParams.get('q');
    if (term) {
      query.current = term;
    }
  }, []);

  const handleSearch = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    query.current = e.target.search.value;
    clearCachedResults();
  };

  const handleCacheClear = () => {
    clearCachedResults();
  };

  return (
    <div>
      <form onSubmit={handleSearch}>
        <input type="text" name="search" />
        <button type="submit">Search</button>
      </form>
      {isLoading && <div>Loading...</div>}
      {error && <div>Error: {error}</div>}
      {results.length === 0 && <div>No results</div>}
      {results.length > 0 && (
        <div>
          <h2>Search Results</h2>
          {results.map((result) => (
            <div key={result.id}>{result.title}</div>
          ))}
        </div>
      )}
      <button onClick={handleCacheClear}>Clear Cache</button>
    </div>
  );
};

export default SearchPage;
```

### Step 3: URL Sync Implementation

The `useEffect` hook in `SearchPage` listens to the URL's search parameters and restores the query state accordingly. This ensures that the search results are preserved when the user navigates back to the page.

### Why Canceling In-Flight Requests is Important and What Bug It Prevents

**Canceling In-Flight Requests:**
- **Why Important:** In-flight requests can lead to outdated or invalid results if the user types a different query while the previous request is still being processed. This can happen due to user interactions like typing in the search box, changing the query manually, or navigating away and returning.
- **Bug It Prevents:** If in-flight requests are not canceled when a new search starts, the old request will continue to fetch results even if the user types a different query. This can lead to incorrect or irrelevant results being displayed to the user.

**Why Cancelling in-Flight Requests is Important:**
- **Why Important:** Cancellation of in-flight requests helps in maintaining the freshness and accuracy of the search results. It ensures that the user is presented with the most up-to-date and relevant information based on their current search query.
- **Bug It Prevents:** If in-flight requests are not cancelled, the previous search results might still be in the cache, which could lead to outdated or irrelevant results being displayed to the user. This can prevent the user from benefiting from the latest search results and can create a confusing experience.

*Response time: 9.2s*

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
Sure, I'd be happy to help you with those questions!

### 1. Fetch the 10 most recent published posts with author name, tag names, and comment count

To fetch the 10 most recent published posts with the required details, you can use a combination of Prisma's `findMany` and `join` operations. Here's how you can do it:

```prisma
const posts = await prisma.post.findMany({
  take: 10,
  orderBy: { createdAt: 'desc' },
  include: {
    author: {
      select: {
        name: true,
      },
    },
    tags: true,
    comments: {
      select: {
        content: true,
      },
    },
  },
});
```

### 2. Add a slug field to Post safely without downtime

To add a unique, non-nullable slug field to the `Post` model safely without downtime, you can use a `CreatePost` mutation in Prisma. Here's how you can do it:

```prisma
const newPost = await prisma.post.create({
  data: {
    title: 'New Post',
    content: 'This is the content of the new post.',
    published: true,
    tags: {
      connect: [
        { name: 'Tag1' },
        { name: 'Tag2' },
      ],
    },
  },
});
```

### 3. Diagnose and fix a slow query

To diagnose and fix the slow query that takes 800ms, follow these steps:

#### Prisma Query

```prisma
const slowQuery = await prisma.post.findMany({
  where: {
    tags: {
      some: {
        name: 'Tag1',
      },
    },
  },
  select: {
    title: true,
    content: true,
    published: true,
    tags: {
      connect: [
        { name: 'Tag1' },
      ],
    },
  },
});
```

#### Raw SQL Generation

To see the raw SQL generated by Prisma, you can use the `introspect` command to inspect your database and generate a schema based on it. Then, you can use the `query` command to generate SQL from your Prisma queries.

```sh
prisma introspect
prisma query findMany --model Post --where tags.name='Tag1' --select title,content,published,tags.name
```

#### Indexing

To improve performance, you can add an index on the `tags` field. Here's how you can do it:

```prisma
model Post {
  id Int @id @default(autoincrement())
  title String
  content String
  published Boolean @default(false)
  authorId Int
  author User @relation(...)
  tags Tag[] @index(name: "tag_post_idx")
  comments Comment[] @relation(...)

  @@id([id, published])
}
```

### 4. When would you drop down from Prisma to raw SQL

When you would drop down from Prisma to raw SQL depends on the specific scenario and the impact on your application. Here are some common scenarios:

1. **Complex Queries**: If a Prisma query becomes too complex or slow to maintain, you might consider switching to raw SQL.
2. **Performance Issues**: If the database is experiencing high traffic or performance issues, you might need to optimize your Prisma queries or use raw SQL to improve performance.
3. **Database Changes**: If a database change is required, such as adding a new table or column, you might need to use raw SQL to perform the change.
4. **API Integration**: If you need to integrate with a database that Prisma does not support, you might need to use raw SQL.

In your case, if the slow query is related to the `tags` field, you might need to add an index on the `tags` field to improve performance. This would be a common scenario where Prisma queries can become slow due to complex joins or nested queries.

*Response time: 7.2s*

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
### 1. Local Development Docker Compose

```yaml
version: '3.9'

services:
  db:
    image: postgres:13-alpine
    container_name: my_db
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=my_db
    volumes:
      - db_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -h localhost -U postgres -p 5432"]
      interval: 10s
      timeout: 5s
      retries: 3
    ports:
      - "5432:5432"

  redis:
    image: redis:alpine
    container_name: my_redis

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    command: npm run dev
    ports:
      - "3000:3000"
    depends_on:
      - db
      - redis
    environment:
      - NODE_ENV=development
      - REACT_APP_API_URL=http://localhost:3000/api

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: npm run start
    ports:
      - "8080:8080"
    depends_on:
      - db
      - redis
    environment:
      - NODE_ENV=production
```

### 2. Production Dockerfile

```Dockerfile
# Stage 1: Build the application
FROM node:14 as builder
WORKDIR /app
COPY package*.json ./
RUN npm install

# Stage 2: Create a non-root user and install production dependencies
FROM builder as runtime
WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY . .

# Set the non-root user
RUN chown -R $USER:$USER /app

# Expose the backend port
EXPOSE 8080

# Run the application
CMD ["node", "src/server.js"]
```

### 3. Backend Crash in Production

When a backend crashes in production, it typically indicates a serious error in the application. Here are some steps to diagnose and resolve the issue:

1. **Check Logs**:
   - Access the backend container logs using `docker logs my_backend`.
   - Look for any error messages or stack traces that provide clues about what went wrong.

2. **Analyze the Error**:
   - If the error is due to a specific condition, try to reproduce the issue locally using the same code and environment.
   - Look at the stack trace to understand the root cause of the problem.

3. **Update Dependencies**:
   - Ensure that all dependencies are up-to-date. Sometimes, bugs in dependencies can lead to crashes.
   - Check for any known issues or updates related to the dependencies in the project.

4. **Health Checks**:
   - Verify that the PostgreSQL and Redis containers are healthy before starting the backend. You can use the `healthcheck` feature in Docker Compose to ensure this.

5. **Restart the Backend**:
   - Sometimes, simply restarting the backend container can resolve transient issues.
   - Use `docker restart my_backend`.

6. **Review Code Changes**:
   - If the issue persists, review the recent code changes to identify any potential issues that might have led to the crash.
   - Ensure that the new nullable column is added correctly and does not break any existing functionality.

7. **Use a Debugger**:
   - If the issue is complex, consider using a debugger to step through the code and identify the exact location where the crash occurs.

### 4. Deploy a New Version with Zero Downtime

To deploy a new version with zero downtime, follow these steps:

1. **Update Dockerfile**:
   - Update the Dockerfile to include the new nullable column in the database schema.
   - Ensure that the new column is nullable and has a default value if necessary.

2. **Build the New Image**:
   - Build the new image using the updated Dockerfile.
   - Use the same tag as the existing image (e.g., `my_backend:latest`).

3. **Push the New Image to Docker Hub**:
   - Push the new image to Docker Hub using the `docker push my_backend:latest`.

4. **Update the Deployment Configuration**:
   - Update the deployment configuration to use the new tag of the image.
   - Use a strategy like rolling updates or blue/green deployment to ensure minimal downtime.

5. **Rollout the Deployment**:
   - Apply the deployment changes to the Kubernetes deployment.
   - Monitor the application to ensure that it is running smoothly and without any downtime.

By following these steps, you can deploy a new version of your application with zero downtime, ensuring that the service remains available to users.

*Response time: 8.5s*

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
### 1. Connection Handling

To handle multiple connections and associate them with a user and document, we can use a dictionary to map each user's socket to a document object. Here's a basic implementation:

```javascript
const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 3000 });

const connections = {};

wss.on('connection', (ws) => {
  ws.on('message', (data) => {
    const message = JSON.parse(data);

    switch (message.type) {
      case 'join':
        const userId = data.userId;
        const documentId = data.documentId;

        if (!connections[userId]) {
          connections[userId] = {
            socket: ws,
            documents: {}
          };
        }

        if (!connections[userId].documents[documentId]) {
          connections[userId].documents[documentId] = {
            content: '',
            cursor: 0,
            users: []
          };
        }

        connections[userId].documents[documentId].users.push(userId);
        console.log(`${userId} has joined document ${documentId}`);
        break;

      case 'text':
        const userId = data.userId;
        const documentId = data.documentId;
        const text = data.text;
        const cursor = data.cursor;

        connections[userId].documents[documentId].content = connections[userId].documents[documentId].content.substring(0, cursor) + text + connections[userId].documents[documentId].content.substring(cursor);
        connections[userId].documents[documentId].cursor += text.length;

        broadcast({
          type: 'text',
          userId: userId,
          documentId: documentId,
          text: text,
          cursor: cursor
        });

        break;

      case 'cursor':
        const userId = data.userId;
        const documentId = data.documentId;
        const cursor = data.cursor;

        connections[userId].documents[documentId].cursor = cursor;
        broadcast({
          type: 'cursor',
          userId: userId,
          documentId: documentId,
          cursor: cursor
        });

        break;

      case 'userLeft':
        const userId = data.userId;
        const documentId = data.documentId;

        connections[userId].documents[documentId].users = connections[userId].documents[documentId].users.filter(u => u !== userId);

        broadcast({
          type: 'userLeft',
          userId: userId,
          documentId: documentId
        });

        if (!connections[userId].documents[documentId].users.length) {
          delete connections[userId].documents[documentId];
        }

        break;
    }
  });
});
```

### 2. Message Protocol

Here's a basic message protocol for the server:

- `join`: `{ userId: 'userId', documentId: 'documentId' }`
- `text`: `{ userId: 'userId', documentId: 'documentId', text: 'text', cursor: 'cursor' }`
- `cursor`: `{ userId: 'userId', documentId: 'documentId', cursor: 'cursor' }`
- `userLeft`: `{ userId: 'userId', documentId: 'documentId' }`

### 3. Broadcasting

To broadcast changes to all connected clients, we can use the `broadcast` function:

```javascript
function broadcast(message) {
  for (const userId in connections) {
    const userIdDocumentMap = connections[userId].documents;
    for (const documentId in userIdDocumentMap) {
      const document = userIdDocumentMap[documentId];
      const socket = connections[userId].socket;

      if (document && document.userId !== userId) {
        socket.send(JSON.stringify(message));
      }
    }
  }
}
```

### 4. Reconnection

To handle a user rejoining after disconnect, we can simply reattach the socket to the document:

```javascript
wss.on('close', (ws) => {
  console.log(`${ws.userId} disconnected`);
});

wss.on('connection', (ws) => {
  console.log(`${ws.userId} connected`);

  ws.on('message', (data) => {
    const message = JSON.parse(data);

    switch (message.type) {
      // Handle reconnection logic here
      // For example, find the document and reattach the socket
      break;
    }
  });
});
```

### 5. Handling Text Change Simultaneously

If two users edit the exact same position simultaneously, the solution approaches can vary depending on the specific requirements of your application. Here are some general approaches:

1. **Conflicting Text Selection**: If two users select the same range of text, you can choose to resolve the conflict by:
   - **Merge the Text**: Combine the text from both selections.
   - **Use a Time Stamp**: Assign a timestamp to each text change and allow the most recent change to win.
   - **Conflict Resolution Tool**: Provide a tool for users to manually resolve conflicts.

2. **Content Based Conflict Resolution**: Compare the content of the selected text and decide which version to keep.
   - **Auto Merge**: Use a library like `git-merge` to automatically merge the conflicts.
   - **Manual Intervention**: Require users to resolve conflicts manually.

3. **Text History**: Keep a history of all text changes and allow users to undo or redo conflicts.
   - **Undo Redo**: Implement undo and redo functionality using a stack or a versioning system.
   - **Conflict History**: Keep a history of conflicts and allow users to view and resolve them.

Implementing the specific conflict resolution algorithm will depend on your application's requirements and user base.

*Response time: 9.3s*

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
### 1. Complete GraphQL Schema (SDL)

```graphql
schema {
  query {
    recipes(filter: {tag: String, minRating: Float}, pagination: {page: Int, limit: Int}) {
      id
      title
      ingredients {
        name
        amount
        unit
      }
      steps
      author {
        id
        name
      }
      tags
      ratings {
        score
        comment
      }
    }
  }
  mutation {
    addRating(recipeId: ID!, score: Float!, comment: String) {
      recipe {
        title
        author {
          name
        }
      }
      ratings {
        score
        comment
      }
    }
  }
}
```

### 2. Resolvers

#### Query.recipes

```javascript
const { Recipe, Author, Rating } = require('./models'); // Adjust path accordingly

exports.recipes = async (parent, args, context) => {
  const { filter, pagination } = args;

  let query = Recipe.find();

  if (filter.tag) {
    query = query.where('tags').contains(filter.tag);
  }

  if (filter.minRating) {
    query = query.where('ratings.score').gte(filter.minRating);
  }

  const total = await query.count();

  const paginatedResults = await query.skip((pagination.page - 1) * pagination.limit).take(pagination.limit);

  return {
    recipes: paginatedResults,
    totalCount: total,
  };
};
```

#### Mutation.addRating

```javascript
const { Recipe, Author, Rating } = require('./models'); // Adjust path accordingly

exports.addRating = async (parent, args, context) => {
  const { recipeId, score, comment } = args;

  const recipe = await Recipe.findById(recipeId);

  if (!recipe) {
    throw new Error('Recipe not found');
  }

  const rating = new Rating({
    recipe,
    score,
    comment,
  });

  await rating.save();

  return {
    recipe: {
      title: recipe.title,
      author: recipe.author,
    },
    ratings: [rating],
  };
};
```

#### Recipe.averageRating

```javascript
const { Rating } = require('./models'); // Adjust path accordingly

exports.averageRating = async (parent, args, context) => {
  const ratings = await Rating.find().sort('-createdAt');

  if (ratings.length === 0) {
    return 0;
  }

  let sum = 0;
  ratings.forEach(rating => {
    sum += rating.score;
  });

  return sum / ratings.length;
};
```

### 3. Handling N+1 Problem

When fetching authors, the N+1 problem occurs because the `Recipe` model has a `hasOne` relationship with the `Author` model. This means for each recipe, the database has to make a separate query to fetch the author. To fix this, we can use DataLoader.

#### Example of DataLoader

First, install DataLoader:

```bash
npm install dataloader
```

Then, configure DataLoader:

```javascript
const DataLoader = require('dataloader');

const recipeAuthorLoader = new DataLoader(async (recipeIds) => {
  const recipes = await Recipe.find().where('_id').in(recipeIds);
  const authorIds = recipes.map(recipe => recipe.author.id);
  const authors = await Author.find().where('_id').in(authorIds);
  return recipeIds.map(id => {
    const recipe = recipes.find(r => r.id === id);
    return authors.find(author => author.id === recipe.author.id);
  });
});
```

#### In Query.recipes Resolver

Replace the `author` field with the DataLoader:

```javascript
exports.recipes = async (parent, args, context) => {
  const { filter, pagination } = args;

  let query = Recipe.find();

  if (filter.tag) {
    query = query.where('tags').contains(filter.tag);
  }

  if (filter.minRating) {
    query = query.where('ratings.score').gte(filter.minRating);
  }

  const total = await query.count();

  const paginatedResults = await query.skip((pagination.page - 1) * pagination.limit).take(pagination.limit);

  return {
    recipes: paginatedResults,
    totalCount: total,
  };
};
```

### 4. Client Query

To fetch recipe title, author name, and first 3 ingredients in one request, the client would write:

```graphql
{
  recipeById(id: 1) {
    title
    author {
      name
    }
    ingredients {
      name
      amount
      unit
      first 3 {
        name
        amount
        unit
      }
    }
  }
}
```

### 5. Choosing GraphQL Over REST

GraphQL offers several advantages over REST:

- **Flexibility**: GraphQL allows clients to specify exactly what they need, reducing the amount of data transferred.
- **Data Caching**: GraphQL can cache data at the server level, reducing the number of database queries.
- **Complexity**: GraphQL is designed to handle complex queries and mutations, making it easier to manage complex systems.

When not to use GraphQL:

- **Small Data**: If the data is small, REST is sufficient.
- **Read-Only Operations**: If the data is read-only, REST is a good choice because it allows for more lightweight requests.
- **Non-Uniform Data**: If the data structure is not uniform, REST might be a better choice because it allows for more flexibility.

In summary, GraphQL is particularly suitable for scenarios where you need to fetch specific data, handle complex queries, and manage large datasets efficiently.

*Response time: 9.4s*

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
Here's the CSS code for the layout:

HTML:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Layout Example</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header class="header">
        <h1>HEADER</h1>
    </header>
    <div class="sidebar">
        <h2>Sidebar</h2>
        <!-- cards will be added dynamically -->
    </div>
    <div class="main-content">
        <h2>Main Content</h2>
        <!-- cards will be added dynamically -->
    </div>
</body>
</html>
```

CSS:

```css
/* base styles */

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html, body {
    height: 100%;
}

body {
    display: flex;
    flex-direction: column;
}

header {
    background-color: #f0f0f0;
    padding: 1rem;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 60px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.sidebar, .main-content {
    flex: 1;
    overflow-y: auto;
}

.sidebar {
    background-color: #e0e0e0;
    padding: 1rem;
    width: 240px;
    border-right: 1px solid #ccc;
}

.main-content {
    background-color: #fff;
    padding: 1rem;
}

/* card styles */

.card {
    margin-bottom: 1rem;
    padding: 1rem;
    background-color: #fff;
    border-radius: 5px;
}

.card img {
    width: 100%;
    height: auto;
    object-fit: cover;
    margin-bottom: 1rem;
}

.card h2 {
    margin: 0;
}

.card p {
    margin: 0;
    font-size: 0.9rem;
}

.card footer {
    display: flex;
    justify-content: space-between;
    margin-top: 1rem;
}

.card footer button {
    margin: 0;
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}

/* responsiveness */

@media (max-width: 768px) {
    .sidebar, .main-content {
        width: 100%;
    }

    .card {
        flex-direction: column;
        width: 100%;
    }
}
```

Explanation:

- The CSS uses Flexbox for the layout of the main content and sidebar. Flexbox is easier to control and maintain than Grid in this case.
- The header is fixed and takes up the full viewport height. The sidebar and main content take up the remaining space below the header.
- Each card uses CSS Grid to create a responsive grid of two columns. The cards are styled to maintain a 16:9 ratio and cover the entire card area. The footer contains two buttons that are aligned using Flexbox.
- Responsive design is achieved using media queries. When the viewport width is ≤768px, the sidebar and main content take up the full width of the container, and the cards are displayed in a single column.

*Response time: 6.4s*

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
1. Transport Mechanism: WebSocket
WebSocket is a full-duplex communication protocol between a client and a server. It provides a persistent connection, which makes it ideal for real-time communication. Since WebSocket supports both text and binary messages, it can handle both task notifications and comments.

Justification: WebSocket allows for real-time updates without the need for polling the server, which saves bandwidth and improves performance. It also maintains a persistent connection, which makes it ideal for real-time notifications where the user is likely to be online.

2. Database Schema:
```sql
CREATE TABLE Notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    task_id INT NOT NULL,
    comment TEXT,
    deadline DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id),
    FOREIGN KEY (task_id) REFERENCES Tasks(id)
);
```

This schema includes columns for the notification ID, user ID, task ID, comment, deadline, creation time, and foreign keys to the Users and Tasks tables.

3. Handling Offline Users:
If a user is offline, they can receive notifications using push notifications. This can be achieved using a push notification service like Firebase Cloud Messaging (FCM) or OneSignal.

4. Cron Job Implementation:
To run the deadline check every hour for all tasks, you can use a cron job. Cron jobs are a time-based scheduling utility that allows you to execute a command at a specific time or interval.

Implementation Approach:
1. Create a scheduled task in your application that runs every hour.
2. Use the FCM API to send a push notification to all users who have tasks with deadlines approaching within 24 hours.
3. Store the task ID and user ID in a cache or database to avoid sending multiple notifications for the same task.

5. Scaling:
To scale this system with 100,000 concurrent users, you can use a combination of load balancing, caching, and horizontal scaling. Load balancing distributes incoming traffic across multiple servers to ensure that no single server becomes overloaded. Caching can be used to store frequently accessed data in memory to reduce the load on the database. Horizontal scaling involves adding more servers to the system as the load increases, and can be achieved using cloud services like AWS, Google Cloud, or Azure.

*Response time: 4.4s*

---
