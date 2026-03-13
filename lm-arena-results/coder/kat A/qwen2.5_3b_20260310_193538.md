# Model: qwen2.5:3b
**Test Date:** 2026-03-10 19:50:02
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
### 1. Define All Endpoints (Method + Path) Following REST Conventions

1. **Create Task**
   - **HTTP Method:** POST
   - **Path:** `/tasks`
   - **Request JSON Shape:**
     ```json
     {
       "workspaceId": "string",
       "projectId": "string",
       "assigneeId": "string",
       "status": "string",
       "dueDate": "string",
       "title": "string",
       "description": "string"
     }
     ```
   - **Response JSON Shape:**
     ```json
     {
       "task": {
         "id": "string",
         "workspaceId": "string",
         "projectId": "string",
         "assigneeId": "string",
         "status": "string",
         "dueDate": "string",
         "title": "string",
         "description": "string"
       }
     }
     ```
   - **Error Response Shape:**
     ```json
     {
       "message": "string"
     }
     ```

2. **Update Task Status**
   - **HTTP Method:** PATCH
   - **Path:** `/tasks/{taskId}`
   - **Request JSON Shape:**
     ```json
     {
       "status": "string",
       "dueDate": "string"
     }
     ```
   - **Response JSON Shape:**
     ```json
     {
       "task": {
         "id": "string",
         "workspaceId": "string",
         "projectId": "string",
         "assigneeId": "string",
         "status": "string",
         "dueDate": "string",
         "title": "string",
         "description": "string"
       }
     }
     ```
   - **Error Response Shape:**
     ```json
     {
       "message": "string"
     }
     ```

3. **List Tasks with Filters (Assignee, Status, Due Date)**
   - **HTTP Method:** GET
   - **Path:** `/tasks`
   - **Request Parameters:**
     ```json
     {
       "assigneeId": "string",
       "status": "string",
       "dueDate": "string"
     }
     ```
   - **Response JSON Shape:**
     ```json
     {
       "tasks": [
         {
           "id": "string",
           "workspaceId": "string",
           "projectId": "string",
           "assigneeId": "string",
           "status": "string",
           "dueDate": "string",
           "title": "string",
           "description": "string"
         }
       ],
       "totalTasks": "number"
     }
     ```
   - **Error Response Shape:**
     ```json
     {
       "message": "string"
     }
     ```

4. **Add Comment**
   - **HTTP Method:** POST
   - **Path:** `/tasks/{taskId}/comments`
   - **Request JSON Shape:**
     ```json
     {
       "text": "string"
     }
     ```
   - **Response JSON Shape:**
     ```json
     {
       "comment": {
         "id": "string",
         "taskId": "string",
         "text": "string",
         "createdBy": "string",
         "createdAt": "string"
       }
     }
     ```
   - **Error Response Shape:**
     ```json
     {
       "message": "string"
     }
     ```

### 2. Define Your Error Response Format — Be Consistent Across All Endpoints

```json
{
  "error": {
    "status": "number",
    "message": "string"
  }
}
```

### 3. How Do You Handle Pagination? Show the Response Envelope

For pagination, we would include a `next` and `previous` field in the response, which would point to the next and previous pages of the task list.

Example Response:
```json
{
  "tasks": [
    {
      "id": "string",
      "workspaceId": "string",
      "projectId": "string",
      "assigneeId": "string",
      "status": "string",
      "dueDate": "string",
      "title": "string",
      "description": "string"
    }
  ],
  "next": "string",
  "previous": "string"
}
```

### 4. Which Endpoints Need Which HTTP Status Codes and When?

1. **Create Task**
   - **HTTP Method:** POST
   - **Path:** `/tasks`
   - **Status Codes:**
     - **201 Created:** When the task is created successfully.
     - **400 Bad Request:** When the request is malformed or invalid.
     - **409 Conflict:** When another task with the same title already exists in the workspace.
     - **500 Internal Server Error:** When an unexpected server error occurs.

2. **Update Task Status**
   - **HTTP Method:** PATCH
   - **Path:** `/tasks/{taskId}`
   - **Status Codes:**
     - **200 OK:** When the task is updated successfully.
     - **400 Bad Request:** When the request is malformed or invalid.
     - **404 Not Found:** When the task is not found.
     - **500 Internal Server Error:** When an unexpected server error occurs.

3. **List Tasks with Filters (Assignee, Status, Due Date)**
   - **HTTP Method:** GET
   - **Path:** `/tasks`
   - **Status Codes:**
     - **200 OK:** When the list of tasks is retrieved successfully.
     - **400 Bad Request:** When the request parameters are invalid.
     - **500 Internal Server Error:** When an unexpected server error occurs.

4. **Add Comment**
   - **HTTP Method:** POST
   - **Path:** `/tasks/{taskId}/comments`
   - **Status Codes:**
     - **201 Created:** When the comment is created successfully.
     - **400 Bad Request:** When the request is malformed or invalid.
     - **500 Internal Server Error:** When an unexpected server error occurs.

By following these conventions and error responses, your API will be clear and consistent, allowing for better user experience and error handling.

*Response time: 15.1s*

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
To implement the endpoint `/workspaces/:workspaceId/tasks/:taskId` in Node.js with Express and TypeScript, we need to follow the provided requirements. We will use Zod for validation and write the complete handler, validation schema, error middleware, and unit tests.

### Step 1: Install Required Packages

First, you need to install the necessary packages:

```sh
npm install express typescript zod @types/express
```

### Step 2: Set Up TypeScript and Express

We will create a basic Express server and set up TypeScript for our routes.

```typescript
// main.ts
import express from 'express';
import { createZodSchema } from 'zod-validator';

const app = express();
app.use(express.json());

// Middleware for Zod validation
function validateZod(schema: any, path: string) {
    return (req: any, res: any, next: any) => {
        try {
            const data = schema.parse(req.body);
            next();
        } catch (error) {
            res.status(400).json({ errors: error.errors });
        }
    };
}

// Error handler
function errorHandler(err: any, req: any, res: any, next: any) {
    res.status(500).json({ error: err.message });
}

// Initialize Zod schemas
const taskSchema = createZodSchema({
    title: z.string().min(1).max(200),
    status: z.enum(['todo', 'in_progress', 'done', 'cancelled']),
    assignee_id: z.number().optional().or(z.string().refine((s) => s.trim().length > 0).optional().refine((s) => !isNaN(Number(s))),
    due_date: z.string().optional(),
});
const taskIdSchema = z.number();
const workspaceIdSchema = z.number();

// Routes
app.patch(
    '/workspaces/:workspaceId/tasks/:taskId',
    validateZod(taskSchema, '/workspaces/:workspaceId/tasks/:taskId'),
    validateZod(workspaceIdSchema, '/workspaces/:workspaceId/tasks/:taskId'),
    validateZod(taskIdSchema, '/workspaces/:workspaceId/tasks/:taskId'),
    validateZod(taskSchema, '/workspaces/:workspaceId/tasks/:taskId'),
    async (req: any, res: any) => {
        try {
            const { workspaceId, taskId, ...taskData } = req.body;
            const [workspace, task] = await Promise.all([
                getWorkspace(workspaceId),
                getTask(workspaceId, taskId),
            ]);

            if (!task) {
                res.status(404).json({ error: 'Task not found' });
                return;
            }

            if (task.status === 'cancelled' && !task.subtasks.every(subtask => subtask.status !== 'cancelled')) {
                res.status(409).json({ error: 'Cannot cancel a task with open subtasks' });
                return;
            }

            const updatedTask = await updateTask(taskId, { ...taskData, status: taskData.status });
            res.status(200).json(updatedTask);
        } catch (err) {
            errorHandler(err, req, res, next);
        }
    }
);

// Error handler
app.use(errorHandler);

export { app };
```

### Step 3: Create Validation Schemas

We'll create a function to generate Zod schemas:

```typescript
// utils.ts
import * as z from 'zod';

const createZodSchema = (schema: any) => {
    const validateSchema = z.object(schema);
    return validateSchema;
};

export default createZodSchema;
```

### Step 4: Create Mock Functions for Testing

We will create mock functions for `getWorkspace` and `getTask` to simulate the backend calls:

```typescript
// mocks.ts
export const getWorkspace = (workspaceId: number) => {
    return new Promise((resolve, reject) => {
        setTimeout(() => resolve({ id: workspaceId }), 100);
    });
};

export const getTask = (workspaceId: number, taskId: number) => {
    return new Promise((resolve, reject) => {
        setTimeout(() => resolve({ id: taskId, workspaceId: workspaceId, title: `Task ${taskId}`, status: 'todo' }), 100);
    });
};

export const updateTask = (taskId: number, changes: Partial

*Response time: 10.3s*

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
Let's implement a complete authentication system in Node.js using Express and TypeScript. We'll cover the following steps:

### Step 1: Project Setup
First, ensure you have the necessary dependencies installed. You can create a new TypeScript project using `typescript`, `express`, and `bcrypt`.

```bash
npm init -y
npm install express bcryptjs
npm install --save-dev @types/express @types/node
```

### Step 2: Create the Project Structure
Create the following directory structure:

```
.
├── auth
│   └── register.ts
├── auth
│   └── login.ts
├── auth
│   └── me.ts
├── auth
│   └── authMiddleware.ts
├── auth
│   └── authController.ts
├── auth
│   └── authRoutes.ts
├── auth
│   └── models.ts
├── lib
│   └── jwtConfig.ts
├── config
│   └── jwtConfig.ts
├── models
│   └── User.ts
├── app.ts
├── package.json
└── tsconfig.json
```

### Step 3: Implement Models
`models.ts` will contain the User model.

```typescript
// models.ts
import { Sequelize, DataTypes } from 'sequelize';

const sequelize = new Sequelize('database', 'username', 'password', {
    dialect: 'sqlite',
    storage: 'database.sqlite',
});

export type User = {
    id: number;
    email: string;
    password: string;
    role: string;
};

export type UserAttributes = {
    id: number;
    email: string;
    password: string;
    role: string;
};

export const User = sequelize.define<User, UserAttributes>('User', {
    id: {
        type: DataTypes.INTEGER,
        autoIncrement: true,
        allowNull: false,


*Response time: 5.2s*

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
### 1. Refresh Token Rotation with Redis

#### Data Structure in Redis:
- **refresh_tokens:** A hash map where the key is the refresh token and the value is the corresponding access token.
- **user_tokens:** A hash map where the key is the user ID and the value is a set of refresh tokens associated with that user.

#### TTL Strategy:
- **access_tokens:** A field in the user_tokens hash map, storing the TTL (time-to-live) of the access token issued for each refresh token.
- **refresh_tokens:** A field in the refresh_tokens hash map, storing the TTL of the refresh token.

### 2. Handling Token Reuse and Logout

#### Token Reuse Detection:
- Implement a mechanism to detect if a refresh token is used more than once within a certain window (e.g., 1 hour).
- If a token is reused, invalidate the refresh token and invalidate the associated access token and session (if needed).

#### Logout Functionality:
- Invalidate the refresh token in Redis.
- Clear the refresh token cookie.
- Optionally, clear the user session if it is still active (e.g., in a database).

### 3. Handling Password Changes

#### Invalidate All Sessions:
- When a user changes their password, invalidate all refresh tokens associated with that user.
- Update the `user_tokens` hash map in Redis to remove all refresh tokens associated with the user.
- Optionally, clear the user session in the database.

### 4. Token Blacklisting vs. Token Rotation

#### Token Blacklisting:
- **Definition:** Blacklisting involves removing a token from active sessions and marking it as invalid. This does not involve revoking the token or changing its state.
- **Use Case:** When a token is compromised or known to be compromised, you can mark it as invalid without needing to revoke or invalidate other tokens.

#### Token Rotation:
- **Definition:** Rotating a token involves issuing a new token when an old token is used. This ensures that no matter when or how the old token was used, it cannot be used anymore.
- **Use Case:** To prevent replay attacks and ensure tokens are not reused.

### When to Use Each:
- **Token Blacklisting:** When you need to invalidate a token without revoking it, such as in the case of a token being compromised. It is useful for quick fixes or when the token is only used for a specific operation.
- **Token Rotation:** To prevent reuse of old tokens and ensure all old tokens are invalid. It is more suitable for user sessions and authentication flows where tokens are used to maintain user sessions.

### Implementation Example (POST /auth/refresh)
```python
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from redis import Redis

app = Flask(__name__)
redis_client = Redis()

@app.route('/auth/refresh', methods=['POST'])
def refresh_token():
    refresh_token = request.json.get('refresh_token')
    if not refresh_token:
        return jsonify({"error": "Missing refresh token"}), 400

    if not redis_client.exists('refresh_tokens:' + refresh_token):
        return jsonify({"error": "Invalid refresh token"}), 401

    user_id = redis_client.hget('refresh_tokens:' + refresh_token, 'user_id')
    if not user_id:
        return jsonify({"error": "Invalid refresh token"}), 401

    # Generate new access token and refresh token
    new_access_token = generate_jwt_access_token(user_id)
    new_refresh_token = generate_jwt_refresh_token(user_id)

    # Update Redis
    redis_client.hset('refresh_tokens:' + refresh_token, 'user_id', user_id)
    redis_client.hset('refresh_tokens:' + new_refresh_token, 'user_id', user_id)
    redis_client.expire('refresh_tokens:' + new_refresh_token, 60 * 60 * 24)  # 1 day TTL

    # Rotate refresh token
    redis_client.hdel('user_tokens:' + user_id, 'refresh_tokens')
    redis_client.rpush('user_tokens:' + user_id, new_refresh_token)

    return jsonify({
        "access_token": new_access_token,
        "refresh_token": new_refresh_token
    })

def generate_jwt_access_token(user_id):
    # Implement JWT access token generation
    pass

def generate_jwt_refresh_token(user_id):
    # Implement JWT refresh token generation
    pass
```

### Logout Endpoint (POST /auth/logout)
```python
@app.route('/auth/logout', methods=['POST'])
def logout():
    refresh_token = request.json.get('refresh_token')
    if not refresh_token:
        return jsonify({"error": "Missing refresh token"}), 400

    if not redis_client.exists('refresh_tokens:' + refresh_token):
        return jsonify({"error": "Invalid refresh token"}), 401

    user_id = redis_client.hget('refresh_tokens:' + refresh_token, 'user_id')

    # Invalidate refresh token in Redis
    redis_client.hdel('refresh_tokens:' + refresh_token, 'user_id')

    # Clear refresh token cookie
    response = jsonify({"message": "Logout successful"})
    response.set_cookie('refresh_token', '', expires=0)

    # Clear user session (if needed)
    redis_client.hdel('user_tokens:' + user_id, 'refresh_tokens')

    return response
```

### Password Change Endpoint (POST /auth/change_password)
```python
@app.route('/auth/change_password', methods=['POST'])
def change_password():
    user_id = request.json.get('user_id')
    old_password = request.json.get('old_password')
    new_password = request.json.get('new_password')

    if not user_id or not old_password or not new_password:
        return jsonify({"error": "Missing parameters"}), 400

    # Validate user and old password (e.g., check with database)
    if not check_password_hash(redis_client.hget('users:' + user_id, 'password'), old_password):
        return jsonify({"error": "Invalid old password"}), 400

    # Hash and store new password
    hashed_new_password = generate_password_hash(new_password)

    # Update the user's password in Redis
    redis_client.hset('users:' + user_id, 'password', hashed_new_password)

    # Invalidate all refresh tokens for this user
    user_tokens = redis_client.hget('user_tokens:' + user_id, 'refresh_tokens')
    if user_tokens:
        redis_client.hdel('user_tokens:' + user_id, 'refresh_tokens')
        redis_client.rpop('user_tokens:' + user_id)

    # Clear user session (if needed)
    redis_client.hdel('user_tokens:' + user_id, 'refresh_tokens')

    return jsonify({"message": "Password changed successfully"})
```

### Summary
- **Refresh Token Rotation:** Uses Redis to store and manage refresh tokens. Each refresh token is associated with a user and an access token. Refresh tokens are rotated by issuing a new token when the old one is used.
- **Token Reuse Detection:** Checks if a refresh token is reused within a certain window and invalidates the refresh token if it is.
- **Password Changes:** Invalidate all refresh tokens for the user to ensure the new password is used.
- **Token Blacklisting:** Mark a token as invalid without revoking it. Useful for compromised tokens.
- **Token Rotation:** Revokes and invalidates old tokens to ensure new tokens are used. Useful for maintaining session security.

By implementing these strategies, you can effectively manage authentication flows and user sessions in your application.

*Response time: 18.0s*

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
Certainly! Let's break down the implementation step by step.

### 1. TypeScript Interface for Props

```typescript
interface DataTableColumn<T> {
  key: string;
  header: string;
  width?: number;
  sortable?: boolean;
  renderCell?: (rowData: T, rowIndex: number) => React.ReactNode;
}

interface DataTableProps<T> {
  columns: DataTableColumn<T>[];
  data: T[];
  pageSizeOptions: number[];
  onPageChange: (page: number) => void;
  onSortChange: (columnKey: string, sortBy: 'asc' | 'desc' | 'none') => void;
  onSelectionChange: (selected: boolean) => void;
  selected: boolean;
  selectedRows: T[];
}
```

### 2. Complete Component Implementation

```typescript
import React, { useEffect, useState, useCallback, useMemo, useRef } from 'react';

type T = { id: number; name: string; description: string };

const DataTable: React.FC<DataTableProps<T>> = ({
  columns,
  data,
  pageSizeOptions,
  onPageChange,
  onSortChange,
  onSelectionChange,
  selected,
  selectedRows,
}) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [sortKey, setSortKey] = useState('');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc' | 'none'>('none');
  const [selectedRowsIds, setSelectedRowsIds] = useState<number[]>([]);
  const selectedRowsRef = useRef<number[]>(selectedRows.map((row) => row.id));

  const filteredData = useMemo(() => {
    let filtered = data;
    if (sortKey && sortOrder) {
      const sortFn = sortOrder === 'asc' ? (a, b) => (a[sortKey] as any).localeCompare(b[sortKey] as any) : (a, b) => -(a[sortKey] as any).localeCompare(b[sortKey] as any);
      filtered = sorted(filtered, sortFn);
    }
    return filtered;
  }, [data, sortKey, sortOrder]);

  const sorted = (array: T[], sortFn: (a: T, b: T) => number): T[] => {
    const sortedArray = [...array];
    sortedArray.sort(sortFn);
    return sortedArray;
  };

  useEffect(() => {
    const sortFn = sortOrder === 'asc' ? (a, b) => (a[sortKey] as any).localeCompare(b[sortKey] as any) : (a, b) => -(a[sortKey] as any).localeCompare(b[sortKey] as any);
    setSortOrder(sortKey && sortKey === sortKey ? 'asc' : 'desc');
    setSortKey('');
    onPageChange(1);
  }, [sortOrder, sortKey, onPageChange]);

  const onPageChangeHandler = useCallback((page: number) => {
    setCurrentPage(page);
  }, []);

  const onSortChangeHandler = useCallback((columnKey: string, sortBy: 'asc' | 'desc' | 'none') => {
    setSortKey(columnKey);
    setSortOrder(sortBy);
  }, []);

  const renderCell = (column: DataTableColumn<T>) => {
    if (column.renderCell) {
      const data = column.key === sortKey ? sorted(filteredData, (a, b) => column.renderCell(a, a.id)!.localeCompare(column.renderCell(b, b.id)!) * (sortOrder === 'asc' ? 1 : -1)) : filteredData;
      return column.renderCell(data[column.key], column.key);
    }
    return null;
  };

  const handleSelectChange = (row: T) => {
    if (!selected) {
      setSelectedRowsIds((prevIds) => [...prevIds, row.id]);
      setSelectedRows((prevRows) => [...prevRows, row]);
    } else {
      setSelectedRowsIds((prevIds) => prevIds.filter((id) => id !== row.id));
      setSelectedRows((prevRows) => prevRows.filter((row) => row !== row));
    }
    onSelectionChange(selected);
  };

  const selectedRowsIdsFiltered = useMemo(() => {
    return selectedRowsIds.filter((id) => selectedRows.find((row) => row.id === id));
  }, [selectedRowsIds, selectedRows]);

  const selectedRowsFiltered = useMemo(() => {
    return selectedRowsIdsFiltered.map((id) => selectedRows.find((row) => row.id === id));
  }, [selectedRowsIdsFiltered, selectedRows]);

  const getRowKey = useCallback((row: T) => row.id, []);

  return (
    <div>
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key} onClick={() => onSortChangeHandler(column.key, sortOrder === column.key ? 'none' : 'asc')}>{column.header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {filteredData.map((row, index) => (
            <tr key={row.id} data-testid={`row-${row.id}`} style={{ width: column.width ? `${column.width}px` : 'fit-content' }}>
              {columns.map((column) => (
                <td key={`${column.key}-${index}`} style={{ width: column.width ? `${column.width}px` : 'fit-content' }}>
                  {renderCell(column)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <div style={{ display: 'flex

*Response time: 13.1s*

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
Certainly! Below is a comprehensive implementation of the search feature in React, using custom hooks to manage the search functionality, caching, and cancellations. I'll also demonstrate how to implement URL sync and the importance of cancelling in-flight requests.

### Step 1: Custom Hook `useSearch`

```javascript
import { useState, useEffect, useMemo, useRef } from 'react';

function useSearch(query, { debounceTime = 300, cacheTime = 5 * 60 * 1000, urlKey = 'q' } = {}) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState([]);
  const [cachedResults, setCachedResults] = useState(null);
  const [cachedLoading, setCachedLoading] = useState(null);
  const [cachedError, setCachedError] = useState(null);
  const cachedQueryRef = useRef(query);
  const inFlight = useRef(false);

  useEffect(() => {
    if (cachedQueryRef.current === query && !inFlight.current) {
      const cachedResults = localStorage.getItem(urlKey + '=' + encodeURIComponent(query));
      if (cachedResults) {
        const cachedData = JSON.parse(cachedResults);
        setCachedResults(cachedData);
        setCachedLoading(cachedData.loading);
        setCachedError(cachedData.error);
      }
    }
  }, [query, inFlight]);

  const fetchSearch = async () => {
    if (inFlight.current) return;

    inFlight.current = true;
    setCachedLoading(true);
    setCachedError(null);
    setCachedResults(null);

    try {
      setLoading(true);
      const response = await fetch(`https://api.example.com/search?q=${encodeURIComponent(query)}`);
      const data = await response.json();
      setResults(data);
      setCachedResults({ loading: false, error: null, results: data });
      setCachedLoading(false);
      setCachedError(null);
    } catch (err) {
      setLoading(false);
      setCachedLoading(false);
      setCachedError(err);
    } finally {
      inFlight.current = false;
      setCachedLoading(false);
      setCachedError(null);
      setCachedResults(null);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      if (cachedQueryRef.current === query) {
        fetchSearch();
      }
    }, debounceTime);

    return () => {
      clearTimeout(timer);
    };
  }, [query, cachedQueryRef, debounceTime]);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (cachedQueryRef.current === query) {
        fetchSearch();
      }
    }, cacheTime);

    return () => {
      clearTimeout(timer);
    };
  }, [query, cachedQueryRef, cacheTime]);

  useEffect(() => {
    return () => {
      clearTimeout(timer);
      clearTimeout(fetchTimer);
    };
  }, [query, cachedQueryRef, cachedLoading, cachedError, cachedResults, cachedResults.loading, cachedResults.error]);

  const clearCache = () => {
    localStorage.removeItem(urlKey + '=' + encodeURIComponent(query));
  };

  const clearInFlight = () => {
    clearTimeout(fetchTimer);
  };

  return {
    loading,
    error,
    results,
    cachedLoading,
    cachedError,
    clearCache,
    clearInFlight,
    fetchSearch,
  };
}
```

### Step 2: SearchPage Component

```javascript
import React, { useState, useEffect } from 'react';
import useSearch from './useSearch';

function SearchPage() {
  const [query, setQuery] = useState('');
  const { loading, error, results, cachedLoading, cachedError, fetchSearch, clearCache, clearInFlight } = useSearch(query);

  useEffect(() => {
    if (cachedLoading || cachedError) {
      setLoading(false);
      setError(null);
    }
  }, [cachedLoading, cachedError]);

  useEffect(() => {
    if (cachedLoading) {
      clearCache();
      clearInFlight();
    }
  }, [cachedLoading]);

  const handleSearch = async (event) => {
    event.preventDefault();
    if (query !== '') {
      fetchSearch();
    }
  };

  const handleClearSearch = () => {
    setQuery('');
    clearCache();
    clearInFlight();
  };

  const handleTypeChange = (event) => {
    setQuery(event.target.value);
  };

  const handleRetry = () => {
    fetchSearch();
  };

  const showResults = () => {
    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error.message}</div>;
    if (!results.length) return <div>No results</div>;
    return <div>{results.map(result => <div key={result.id}>{result.title}</div>)}</div>;
  };

  return (
    <div>
      <form onSubmit={handleSearch}>
        <input type="text" value={query} onChange={handleTypeChange} />
        <button type="submit">Search</button>
      </form>
      <button onClick={handleClearSearch}>Clear</button>
      <button onClick={handleRetry}>Retry</button>
      {showResults()}
    </div>
  );
}

export default SearchPage;
```

### Step 3: URL Sync Implementation

To implement URL sync, we'll use the `useEffect` hook to update the URL whenever the `query` state changes:

```javascript
import { useNavigate, useLocation } from 'react-router-dom';

function SearchPage() {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const query = location.state?.query || '';
    setQuery(query);
  }, [location]);

  const handleSearch = async (event) => {
    event.preventDefault();
    if (query !== '') {
      const newQuery = encodeURIComponent(query);
      navigate(`/search/${newQuery}`, { state: { query: query } });
      await fetchSearch();
    }
  };

  // Rest of the component code...
}

// In your main app component
function App() {
  return (
    <div>
      <SearchPage />
      <Route path="/search/:query" element={<SearchPage />} />
    </div>
  );
}
```

### Step 4: Why Cancellation is Important and What Bug It Prevents

**Cancelling In-Flight Requests:**

- **Importance:** Cancellation is crucial because it prevents the same request from being made multiple times. This avoids wasting resources and unnecessary network requests, which can be time-consuming and expensive.
- **Bug Prevention:** The primary bug this prevents is an infinite loop of requests. Imagine if a user starts a search, and the results come back. If the same search is triggered again without cancelling the previous request, it would create an infinite loop of fetches. This not only consumes resources but can also cause the server to timeout, leading to a 504 Gateway Timeout error.
- **Resource Management:** Cancellation ensures that resources are freed up when unnecessary, preventing deadlocks and ensuring that the application remains responsive and stable.
- **Error Handling:** If a request fails due to a network issue, cancelling it ensures that the application doesn’t retry the failed request, which would be unnecessary and could lead to further errors.

By implementing cancellation, you ensure that your application remains clean, responsive, and efficient, providing a better user experience.

*Response time: 17.0s*

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
### 1. Prisma Query to Fetch 10 Most Recent Published Posts

To fetch the 10 most recent published posts along with the author's name, tag names, and the comment count (without N+1 queries), you can use the following Prisma query:

```prisma
query fetchMostRecentPosts {
  posts(where: { published: true }, orderBy: { createdAt: desc }, limit: 10) {
    id
    title
    content
    author {
      id
      email
    }
    tags {
      name
    }
    commentsCount: commentsCount // Assuming the database already provides a commentsCount field
  }
}
```

### 2. Migration Scenario: Add a Slug Field to Posts

To safely add a unique, non-nullable `slug` field to the `Post` table without downtime, you can use a sequence migration approach. This avoids modifying the schema directly.

1. **Create a Prisma schema file with the migration plan**:
   - We will define the migration plan and add the `slug` field without changing the existing schema directly.

2. **Migrate the schema to add the field**:

```prisma
// prisma/schema.prisma
@version "1.0.0"
scalar String @default("")
scalar Int @default(0)
scalar DateTime @default(now)

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model Post {
  id        Int      @id @default(autoincrement())
  title     String
  content   String
  published Boolean @default(false)
  authorId  Int
  author    User @relation("PostAuthor")
  tags      Tag[]
  comments  Comment[]
  createdAt DateTime @default(now)
  slug      String   @unique @default(slugField)
}

# prisma/migrations/2023-08-01-000001_create_posts_add_slug.prisma
@version "2023-08-01-000001"
model Post {
  id        Int      @id @default(autoincrement())
  title     String
  content   String
  published Boolean @default(false)
  authorId  Int
  author    User @relation("PostAuthor")
  tags      Tag[]
  comments  Comment[]
  createdAt DateTime @default(now)
  slug      String   @unique @default(slugField)
}

@operation Post {
  findUnique(where: { id: value }, include: { tags: { include: { name: true } }, comments: { include: { author: { include: { email: true } } } }) {
    id
    title
    content
    published
    authorId
    author: { email }
    tags: { name }
    comments: { author: { email } }
  }
}

@query PostCollection {
  findMany(where: { published: true }, orderBy: { createdAt: desc }, limit: 10) {
    id
    title
    content
    published
    authorId
    author: { email }
    tags: { name }
    comments: { author: { email } }
  }
}

@mutation createPost {
  createOne(data: { title: value, content: value, published: value, authorId: value

*Response time: 8.6s*

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
### 1. Docker Compose for Local Development

Below is the `docker-compose.yml` file for local development, ensuring hot reloading for both the frontend and backend, persistence for PostgreSQL data using a named volume, Redis, and environment variables from a `.env` file.

```yaml
version: '3.8'

services:
  api:
    container_name: api
    image: api:latest
    build:
      context: .
      dockerfile: Dockerfile
      args:
        NODE_ENV: development
    volumes:
      - type: bind
        source: ./backend/build
        target: /app
    environment:
      - NODE_ENV=development
      - NODE_APP_INSTANCE=api
      - PORT=3000
    ports:
      - "3000:3000"
    command: npm run serve
    networks:
      - app-network

  frontend:
    container_name: frontend
    image: frontend:latest
    volumes:
      - type: bind
        source: ./frontend
        target: /app
    networks:
      - app-network

  db:
    container_name: db
    image: postgres:latest
    environment:
      POSTGRES_USER: api
      POSTGRES_DB: api
      POSTGRES_PASSWORD: password
    volumes:
      - db_data:/var/lib/postgresql/data
    networks:
      - app-network

  redis:
    container_name: redis
    image: redis:alpine
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  db_data:
```

### 2. Dockerfile for Production Backend

Here is the production Dockerfile for the backend (Node.js), which uses a multi-stage build, final image runs as a non-root user, and only production dependencies are included in the final image.

```dockerfile
# Stage 1: Build (Builder)
FROM node:14 as builder

WORKDIR /app
COPY . /app
RUN npm install
RUN npm ci --only-production
RUN npm run build

# Stage 2: Final Image
FROM node:14

WORKDIR /app
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./
COPY --from=builder /app/build ./
USER node
EXPOSE 3000

CMD ["npm", "start"]
```

### 3. Understanding Exit Code 137 in Production

Exit code `137` generally indicates that a process was terminated by the `SIGTERM` signal. The SIGTERM signal is sent to a process group when a program is asked to exit, usually from a service manager like `systemd` or `supervisor`. This is often seen when a process is restarted, which can be a sign of unexpected behavior or a misconfigured service.

**Diagnosis Steps:**
1. **Check System Logs:** Review the logs of your service manager (e.g., `systemd`, `supervisord`) to see if there are any error messages.
2. **Review Service Configuration:** Ensure the service configuration is correct (e.g., health checks, restart policies).
3. **Check Logs of the Process:** Look at the logs of the `npm run start` command in the Docker container to see if there are any errors.
4. **Check Environment:** Ensure the environment variables and configuration are correct.
5. **Restart Service:** Temporarily restart the service to see if the issue persists.

### 4. Deployment Sequence for Schema Change (Additive Only)

To deploy a new version with zero downtime, we will use PostgreSQL's [hot standby](https://www.postgresql.org/docs/current/warm-standby.html) feature. Here's the step-by-step deployment sequence:

1. **Prepare the New Version:**
   - Ensure the new version is fully functional and tested.
   - Make sure all changes are reviewed and approved.
   - Update any database migrations to handle the new nullable column.

2. **Create a Hot Standby Configuration:**
   - Configure PostgreSQL to act as a hot standby.
   - You can use `pg_hba.conf` to allow connections from the hot standby server.
   - Ensure the `postgresql.conf` file has the correct settings for hot standby.

3. **Migrate Data:**
   - Use `pg_dump` to take a backup of the current production database.
   - Use `pg_dump` and `pg_restore` to restore the backup to the hot standby server.

4. **Test Hot Standby:**
   - Ensure the hot standby server can replicate from the primary.
   - Verify the hot standby server is functioning correctly.

5. **Rollback Plan:**
   - Keep the rollback plan in place. Ensure the hot standby server can be safely shut down if needed.

6. **Deploy New Version:**
   - Update the production environment to the new version.
   - Ensure all services are correctly configured to use the new version.

7. **Promote Hot Standby:**
   - Once the new version is stable, promote the hot standby to the primary.
   - Stop the current primary server.
   - Switch the configuration to use the hot standby as the new primary.

8. **Verify:**
   - Verify that all services are working correctly with the new schema.
   - Monitor the system for any issues.

**Example of Promotion Script:**

```bash
#!/bin/bash

# Stop the current primary PostgreSQL server
pg_ctl -D /var/lib/postgresql/12/main -m fast -w stop

# Set up the hot standby to become the primary
pg_ctl -D /var/lib/postgresql/12/main -w set_primary

# Verify the hot standby becomes the primary
psql -c "SELECT version()"

# Start the new primary PostgreSQL server
pg_ctl -D /var/lib/postgresql/12/main -w start
```

This sequence ensures that the deployment is performed with zero downtime and minimal disruption.

*Response time: 14.0s*

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
Sure, let's break down each of the points and implement the core server logic for the collaborative document editor. We will use Node.js and the `ws` library for WebSocket support.

### 1. Connection Handling

We need to associate each WebSocket connection with a user and a document. The `ws` library provides an event `connection` that we can use to handle connections.

```javascript
const WebSocket = require('ws');
const http = require('http');

const server = http.createServer();
const wsServer = new WebSocket.Server({ server });

const connectionMap = new Map();

wsServer.on('connection', (ws, req) => {
  const clientId = req.connection.remoteAddress;
  const userName = req.headers['user-name']; // This can be a UUID or a username.
  const documentId = req.headers['document-id']; // This can be a UUID or a unique identifier for the document.

  ws.on('message', (message) => {
    console.log(`Received message from ${clientId}: ${message}`);
    handleMessage(message, clientId, userName, documentId);
  });

  ws.on('close', () => {
    console.log(`Client ${clientId} disconnected`);
    connectionMap.delete(clientId);
  });

  connectionMap.set(clientId, { ws, userName, documentId });
});
```

### 2. Message Protocol

We need to define the message types for join, text change, cursor move, and user leave. Here's an example using JSON:

```json
{
  "type": "JOIN",
  "userId": "user123",
  "userName": "JohnDoe",
  "documentId": "doc456"
}
```

```json
{
  "type": "TEXT_CHANGE",
  "userId": "user123",
  "documentId": "doc456",
  "textChange": {
    "position": { "line": 5, "character": 10 },
    "text": "new text",
    "from": "user123"
  }
}
```

```json
{
  "type": "CURSOR_MOVE",
  "userId": "user123",
  "documentId": "doc456",
  "position": { "line": 5, "character": 10 }
}
```

```json
{
  "type": "USER_LEAVE",
  "userId": "user123",
  "documentId": "doc456"
}
```

### 3. Broadcasting

We need to broadcast changes to other connected users in the same document. Let's implement the `broadcastChanges` function.

```javascript
function broadcastChanges(documentId, changes) {
  connectionMap.forEach((user, clientId) => {
    if (user.documentId === documentId) {
      user.ws.send(JSON.stringify(changes));
    }
  });
}
```

### 4. Reconnection Handling

When a user disconnects and reconnects, they should get the latest document state. We can achieve this by listening for `reconnect` events and using the documentId to find the correct user and document.

```javascript
wsServer.on('connection', (ws, req) => {
  const clientId = req.connection.remoteAddress;
  const userName = req.headers['user-name'];
  const documentId = req.headers['document-id'];

  ws.on('message', (message) => {
    console.log(`Received message from ${clientId}: ${message}`);
    handleMessage(message, clientId, userName, documentId);
  });

  ws.on('close', () => {
    console.log(`Client ${clientId} disconnected`);
    connectionMap.delete(clientId);
  });

  ws.on('reconnect', () => {
    // Find the user in the connection map and ensure they have the correct document state.
    const user = connectionMap.get(clientId);
    if (user) {
      const document = findDocumentByUserId(user.userId);
      user.documentId = document.documentId;
    }
  });

  ws.on('reconnectAttempt', () => {
    console.log(`Client ${clientId} attempted to reconnect`);
  });
});

function findDocumentByUserId(userId) {
  // This function would find the documentId of the user with the given userId.
  // For simplicity, let's assume we have a map of userId to documentId.
  // In a real-world scenario, this would likely involve querying a database.
  return connectionMap.get(userId).documentId;
}
```

### 5. Handling Concurrent Edits

If two users edit the exact same position simultaneously, we need to implement a conflict resolution strategy. Here are some possible approaches:

- **Simple Overwrite:** The last change wins. This is easy to implement but can cause conflicts if edits are close together.
- **Sequence Number:** Each edit includes a sequence number. The editor with the higher sequence number wins.
- **Versioning:** Each document has a version number. Editors need to ensure they are editing the latest version.

For simplicity, let's use a versioning approach.

```javascript
const versionCounter = 0;

function broadcastChanges(documentId, changes, version) {
  const changesWithVersion = changes.map(change => ({
    ...change,
    version,
  }));
  broadcastChanges(documentId, changesWithVersion);
}

function handleTextChange(userId, documentId, position, text, version) {
  const user = connectionMap.get(userId);
  if (user) {
    const change = { type: 'TEXT_CHANGE', position, text, from: user.userName, version };
    broadcastChanges(documentId, [change]);
  }
}

function handleCursorMove(userId, documentId, position, version) {
  const user = connectionMap.get(userId);
  if (user) {
    const change = { type: 'CURSOR_MOVE', position, from: user.userName, version };
    broadcastChanges(documentId, [change]);
  }
}
```

### Summary

The core server implementation focuses on associating WebSocket connections with users and documents, handling messages, broadcasting changes, managing reconnections, and resolving concurrent edits using a versioning strategy.

*Response time: 14.2s*

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

Below is a complete GraphQL schema (SDL) for the recipe platform described.

```graphql
type Author {
  id: ID!
  name: String!
}

type Ingredient {
  name: String!
  amount: Float
  unit: String!
}

type Rating {
  score: Float!
  comment: String
}

type Recipe {
  id: ID!
  title: String!
  ingredients: [Ingredient!]!
  steps: String
  author: Author!
  tags: [String!]!
  ratings: [Rating!]!
}

type Query {
  recipes(filter: RecipesFilter, pagination: Pagination): [Recipe!]!
  recipeById(id: ID!): Recipe!
  authorById(id: ID!): Author!
}

type Mutation {
  addRating(recipeId: ID!, score: Float!, comment: String): Recipe!
  deleteRating(recipeId: ID!, score: Float!): Recipe!
  createRecipe(title: String!, ingredients: [IngredientInput]!, steps: String, authorId: ID!, tags: [String]!): Recipe!
  deleteRecipe(id: ID!): Recipe!
}

type RecipesFilter {
  tag: String
  minRating: Float
}

type Pagination {
  page: Int
  limit: Int
}

input IngredientInput {
  name: String!
  amount: Float
  unit: String
}

input RecipeInput {
  title: String
  ingredients: [IngredientInput]
  steps: String
  authorId: ID
  tags: [String]
}

enum RecipeStatus {
  DRAFT
  PUBLISHED
}

type RecipeStatusFilter {
  status: RecipeStatus
}

type RecipeFilter {
  title: String
  ingredients: [String]
  authorId: ID
  tags: [String]
  status: RecipeStatusFilter
  minRating: Float
  maxRating: Float
  published: Boolean
}

type AuthorFilter {
  name: String
}

type AuthorFilterByRecipe {
  recipe: Recipe
  recipes: [Recipe!]!
}

type RatingFilter {
  recipe: Recipe
  recipes: [Recipe!]!
}

type Author {
  id: ID!
  name: String!
  recipes: [Recipe!]!
  recipesByFilter: [RecipeFilter!]!
}

type AuthorWithRecipeCount {
  id: ID!
  name: String!
  recipeCount: Int
}

type AuthorFilterByRecipeCount {
  recipeCount: Int
  recipes: [Recipe!]!
}

type AuthorFilterByRecipeCountWithAuthor {
  id: ID!
  name: String!
  recipeCount: Int
  recipes: [Recipe!]!
}

type AuthorFilterByRecipeStatusCount {
  recipeCount: Int
  recipes: [Recipe!]!
}

type AuthorFilterByRecipeStatusCountWithAuthor {
  id: ID!
  name: String!
  recipeCount: Int
  recipes: [Recipe!]!
}

type AuthorFilterByRecipeFilter {
  recipes: [Recipe!]!
}

type RecipeStatusFilterWith

*Response time: 7.8s*

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
Certainly! Below is the complete HTML and CSS code for the UI layout you described. I'll also explain the layout approach, including the choices of Flexbox and Grid.

### HTML Structure
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="styles.css">
    <title>Custom Layout</title>
</head>
<body>
    <header>
        <h1>Header</h1>
    </header>
    <aside id="sidebar">
        <h2>Sidebar</h2>
        <div class="card">
            <div class="card-content">
                <img src="image1.jpg" alt="Card Image">
                <div class="card-info">
                    <h3>Title 1</h3>
                    <p>Description 1</p>
                    <div class="card-footer">
                        <button>Button Left</button>
                        <button>Button Right</button>
                    </div>
                </div>
            </div>
        </div>
        <div class="card">
            <div class="card-content">
                <img src="image2.jpg" alt="Card Image">
                <div class="card-info">
                    <h3>Title 2</h3>
                    <p>Description 2</p>
                    <div class="card-footer">
                        <button>Button Left</button>
                        <button>Button Right</button>
                    </div>
                </div>
            </div>
        </div>
    </aside>
    <main id="main-content">
        <div class="row">
            <div class="col">
                <div class="card">
                    <div class="card-content">
                        <img src="image3.jpg" alt="Card Image">
                        <div class="card-info">
                            <h3>Title 3</h3>
                            <p>Description 3</p>
                            <div class="card-footer">
                                <button>Button Left</button>
                                <button>Button Right</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col">
                <div class="card">
                    <div class="card-content">
                        <img src="image4.jpg" alt="Card Image">
                        <div class="card-info">
                            <h3>Title 4</h3>
                            <p>Description 4</p>
                            <div class="card-footer">
                                <button>Button Left</button>
                                <button>Button Right</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </main>
</body>
</html>
```

### CSS Styling
```css
/* Reset */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body, html {
    height: 100%;
    font-family: Arial, sans-serif;
}

header {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 60px;
    background-color: #333;
    color: #fff;
    display: flex;
    justify-content: center;
    align-items: center;
}

header h1 {
    margin: 0;
}

aside {
    background-color: #f5f5f5;
    position: fixed;
    top: 60px;
    left: 0;
    width: 240px;
    height: 100%;
    display: flex;
    flex-direction: column;
    overflow-y: auto;
}

aside h2 {
    margin: 10px 0;
}

.card {
    display: flex;
    flex-direction: column;
}

.card-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.card-content img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.card-info {
    padding: 10px;
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.card-footer {
    display: flex;
    justify-content: space-between;
    margin-top: 10px;
}

.card-footer button {
    padding: 5px 10px;
    margin: 5px;
    background-color: #4CAF50;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}

main {
    background-color: #f5f5f5;
    padding: 10px;
    width: 100%;
    height: 100%;
    overflow: hidden;
}

.row {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
    margin: 0 auto;
    max-width: 1200px;
    padding: 0 20px;
    grid-template-rows: repeat(auto-fit, minmax(300px, 1fr));
}

.col {
    width: 100%;
}

.card {
    margin-bottom: 10px;
}

.card:last-child {
    margin-bottom: 0;
}
```

### Explanation

1. **Header Fixed Positioning**: 
   - The `header` is set to `position: fixed;` at the top, ensuring it remains fixed at the top while the content scrolls.

2. **Sidebar and Main Content Layout**:
   - The `aside` is set to `position: fixed;` to remain fixed at the top alongside the header.
   - The `main` section uses Flexbox to ensure that the cards fill the remaining space on the main content area. The `row` and `col` classes are used to create a grid system for the cards, ensuring that they stack in a 2-column layout on larger screens and 1-column on smaller screens (≤768px).

3. **Card Layout**:
   - Each card uses Flexbox to stack the image, title, description, and buttons vertically. The card's contents (`card-content`, `card-info`, and `card-footer`) are flex items that can be aligned as needed.
   - The `card-info` section is set to `flex: 1;` to ensure that the content inside the card fills the available space, and then `grid` is used to create a responsive grid system using `grid-template-columns` and `grid-template-rows`.

This approach ensures that the layout is responsive and that the cards stack correctly based on screen size. The CSS Grid system is used for the cards, as it offers more control over the layout and can handle the responsive aspect with ease. 

**Flexbox is used for the main content to create a simple grid structure that works well with the card layout.**

*Response time: 17.0s*

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
### 1. Transport Mechanism

For real-time notifications, **WebSocket** is the most appropriate choice for the following reasons:
- **Low Latency:** WebSocket allows bi-directional communication, which is essential for real-time notifications. It provides a persistent connection that keeps the server in constant communication with the client, reducing the latency compared to other mechanisms like polling.
- **Efficient Communication:** Unlike polling, which requires the client to repeatedly request updates from the server, WebSocket can push updates directly to the client, minimizing the overhead of frequent requests.
- **Scalability:** WebSockets can handle a high volume of concurrent connections without significant performance degradation. They are less prone to issues like packet loss and reconnections compared to other methods.

### 2. Database Schema for Notifications

To store notifications efficiently, a database schema should be designed to include the following tables:

- **Users Table (users):**
```sql
CREATE TABLE users (
    user_id INT PRIMARY KEY,
    user_name VARCHAR(100),
    user_email VARCHAR(100),
    user_status BOOLEAN DEFAULT FALSE  -- Indicate if user is offline
);
```

- **Tasks Table (tasks):**
```sql
CREATE TABLE tasks (
    task_id INT PRIMARY KEY,
    task_name VARCHAR(255),
    task_description TEXT,
    task_status VARCHAR(50),
    task_deadline DATE,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

- **Notifications Table (notifications):**
```sql
CREATE TABLE notifications (
    notification_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    task_id INT,
    notification_type VARCHAR(50),
    notification_content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (task_id) REFERENCES tasks(task_id)
);
```

### 3. Handling Offline Users

To manage notifications for users who are offline, you can implement the following approach:

1. **Store Notifications:** Notifications can be stored in the `notifications` table until the user comes back online.
2. **Offline User Management:** When a user goes offline, any unsent notifications are temporarily stored. When the user comes back online, you can re-send these notifications.
3. **Synchronization Mechanism:** Implement a background task that runs periodically (e.g., every hour) to fetch unsent notifications from the `notifications` table and send them to the user using WebSocket.
4. **User Status Management:** Update the `users` table to track the status of users (e.g., offline, online) and manage the state transition between these statuses.

### 4. Implementing the Deadline Check

To run the deadline check for tasks every hour, you can use a **Cron Job**:

1. **Cron Job Approach:** Set up a cron job that runs a script to check all tasks that are due within the next 24 hours and generate corresponding notifications.
2. **Script to Generate Notifications:** This script would query the database for tasks due in the next 24 hours and then insert a notification into the `notifications` table.

Example of a cron job setup:
```bash
# Schedule a cron job to run every hour
0 * * * * /path/to/script/check_deadlines.sh
```

### 5. Scaling the Notification System

To scale the system for 100,000 concurrent users, you can adopt the following strategies:

1. **Database Scaling:** Use a database with high scalability, such as MySQL with InnoDB, or MariaDB with the same features. Consider sharding or replication for high availability.
2. **Load Balancing:** Use a load balancer (e.g., Nginx, HAProxy) to distribute incoming requests across multiple instances.
3. **Caching:** Implement caching (e.g., Redis) to reduce database load and improve response times. Caching can be used for frequently accessed data like user information, tasks, and notifications.
4. **WebSocket Server:** Use a WebSocket server (e.g., Socket.IO) that can handle multiple connections efficiently. Socket.IO can scale well with multiple clients.
5. **Microservices Architecture:** Break the system into microservices that can be independently scaled and managed. For example, use separate services for user management, task management, and notification handling.
6. **Monitoring and Logging:** Implement monitoring and logging solutions to track the system's performance and identify bottlenecks proactively.

By implementing these strategies, you can ensure the system can handle the load efficiently and scale as needed.

*Response time: 11.3s*

---
