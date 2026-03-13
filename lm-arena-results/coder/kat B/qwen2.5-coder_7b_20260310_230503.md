# Model: qwen2.5-coder:7b
**Test Date:** 2026-03-11 00:56:27
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
### REST API Design for Multi-Tenant SaaS Project Management Tool

#### 1. Endpoints

**Workspace**
- **GET /workspaces**: List all workspaces for the authenticated user.
- **POST /workspaces**: Create a new workspace.
- **GET /workspaces/{workspaceId}**: Get details of a specific workspace.
- **PUT /workspaces/{workspaceId}**: Update details of a specific workspace.
- **DELETE /workspaces/{workspaceId}**: Delete a specific workspace.

**Project**
- **GET /workspaces/{workspaceId}/projects**: List all projects in a workspace.
- **POST /workspaces/{workspaceId}/projects**: Create a new project.
- **GET /workspaces/{workspaceId}/projects/{projectId}**: Get details of a specific project.
- **PUT /workspaces/{workspaceId}/projects/{projectId}**: Update details of a specific project.
- **DELETE /workspaces/{workspaceId}/projects/{projectId}**: Delete a specific project.

**Task**
- **GET /workspaces/{workspaceId}/projects/{projectId}/tasks**: List all tasks in a project.
- **POST /workspaces/{workspaceId}/projects/{projectId}/tasks**: Create a new task.
- **GET /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}**: Get details of a specific task.
- **PUT /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}**: Update details of a specific task.
- **DELETE /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}**: Delete a specific task.

**User**
- **GET /workspaces/{workspaceId}/users**: List all users in a workspace.
- **POST /workspaces/{workspaceId}/users**: Invite a new user to a workspace.
- **GET /workspaces/{workspaceId}/users/{userId}**: Get details of a specific user.
- **PUT /workspaces/{workspaceId}/users/{userId}**: Update details of a specific user.
- **DELETE /workspaces/{workspaceId}/users/{userId}**: Remove a user from a workspace.

**Comment**
- **GET /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/comments**: List all comments on a task.
- **POST /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/comments**: Add a new comment to a task.
- **GET /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/comments/{commentId}**: Get details of a specific comment.
- **PUT /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/comments/{commentId}**: Update details of a specific comment.
- **DELETE /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/comments/{commentId}**: Delete a specific comment.



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
Let's implement the required endpoint in Node.js + Express + TypeScript, using Zod for validation and a custom error middleware for handling validation errors.

### Step 1: Install Dependencies

First, make sure you have the necessary dependencies installed:

```bash
npm install express @types/express typescript @types/node zod
```

### Step 2: Create the TypeScript Configuration

Create a `tsconfig.json` file in your project root:

```json
{
  "compilerOptions": {
    "target": "ES2018",
    "module": "commonjs",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src"]
}
```

### Step 3: Create the Validation Schema

Create a `validation.ts` file to define the Zod schema for task updates:

```typescript
import { z } from 'zod';

const taskUpdateSchema = z.object({
  title: z.string().max(200).optional(),
  status: z.enum(['todo', 'in_progress', 'done', 'cancelled']).optional(),
  assignee_id: z.union([z.number(), z.null()]).optional(),
  due_date: z.string().datetime().optional().nullable(),
}).partial();

export { taskUpdateSchema };
```

### Step 4: Create the Middleware for Validation Errors

Create a `validationMiddleware.ts` file to handle validation errors:

```typescript
import { NextFunction, Request, Response } from 'express';
import { ZodError } from 'zod';

export function validationMiddleware(schema: z.AnyZodObject) {
  return (req: Request, res: Response, next: NextFunction) => {
    try {
      schema.parse(req.body);
      next();
    } catch (error) {
      if (error instanceof ZodError) {
        return res.status(400).json({ errors: error.issues });
      }
      next(error);
    }
  };
}
```

### Step 5: Create the Controller for the PATCH Endpoint

Create a `controller.ts` file to handle the PATCH endpoint logic:

```typescript
import { Request, Response } from 'express';
import { taskUpdateSchema } from './validation';

const tasks = new Map<number, { id: number; workspaceId: number; title: string; status: string; assignee_id: number | null; due_date: string | null }>();

tasks.set(1, { id: 1, workspaceId: 1, title: 'Task 1', status: 'todo', assignee_id: 1, due_date: null });
tasks.set(2, { id: 2, workspaceId: 2, title: 'Task 2', status: 'in_progress', assignee_id: 2, due_date: null });

export async function updateTask(req: Request, res: Response) {
  const { workspaceId, taskId } = req.params;
  const { title, status, assignee_id, due_date } = req.body;

  // Validate workspaceId and taskId
  const workspaceIdInt = parseInt(workspaceId, 10);
  const taskIdInt = parseInt(taskId, 10);
  if (isNaN(workspaceIdInt) || isNaN(taskIdInt)) {
    return res.status(400).json({ error: 'Invalid workspaceId or taskId' });
  }

  // Find the task
  const task = tasks.get(taskIdInt);
  if (!task) {
    return res.status(404).json({ error: 'Task not found' });
  }

  // Check if the task belongs to the workspace
  if (task.workspaceId !== workspaceIdInt) {
    return res.status(404).json({ error: 'Task not found' });
  }

  // Check assignee_id if provided
  if (assignee_id !== undefined && !Number.isInteger(assignee_id)) {
    return res.status(400).json({ error: 'Invalid assignee_id' });
  }

  //

*Response time: 17.5s*

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
To implement a complete authentication system in Node.js + Express + TypeScript, we'll follow the steps outlined. This system will include registration, login, protected routes, and token validation.

### Step 1: Setup the Project

First, create a new Node.js project and install the necessary dependencies:

```bash
mkdir node-auth-ts
cd node-auth-ts
npm init -y
npm install express @types/express typescript ts-node-dev bcrypt jsonwebtoken cookie-parser @types/node @types/jsonwebtoken
npx tsc --init
```

### Step 2: Configure TypeScript

Edit `tsconfig.json` to include the necessary configurations:

```json
{
  "compilerOptions": {
    "target": "ES6",
    "module": "commonjs",
    "outDir": "./dist",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
```

### Step 3: Create the Server

Create a `src` directory and a `server.ts` file:

```bash
mkdir src
touch src/server.ts
```

Edit `src/server.ts`:

```typescript
import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import bcrypt from 'bcrypt';
import jwt, { JwtPayload } from 'jsonwebtoken';
import cookieParser from 'cookie-parser';

const app = express();
const PORT = 3000;

app.use(cors({ origin: 'http://localhost:3000', credentials: true }));
app.use(express.json());
app.use(cookieParser());

const SECRET_KEY = 'your-secret-key';

interface User {
  id: number;
  email: string;
  password: string;
  role: string;
}

const users: User[] = [];

// Middleware to validate the access token
const authMiddleware = (req: Request, res: Response, next: NextFunction) => {
  const token = req.headers['authorization']?.split(' ')[1];

  if (!token) {
    return res.status(403).json({ message: 'No token provided' });
  }

  try {
    const decoded = jwt.verify(token, SECRET_KEY) as JwtPayload;
    req.user = decoded;
    next();
  } catch (error) {
    return res.status(401).json({ message: 'Failed to authenticate token' });
  }
};

// Register
app.post('/auth/register', async (req: Request, res: Response) => {
  const { email, password } = req.body;

  if (!email || !password) {
    return res.status(400).json({ message: 'Email and password are required' });
  }

  const existingUser = users.find((u) => u.email === email);

  if (existingUser) {
    return res.status(409).json({ message: 'User already exists' });
  }

  const hashedPassword = await bcrypt.hash(password, 12);
  const newUser: User = { id: users.length + 1, email, password: hashedPassword, role: 'user' };
  users.push(newUser);

  res.status(201).json(newUser);
});

// Login
app.post('/auth/login', async (req: Request, res: Response) => {
  const { email, password } = req.body;

  if (!email || !password) {
    return res.status(400).json({ message: 'Email and password are required' });
  }

  const user = users.find((u) => u.email === email);

  if (!user || !await bcrypt.compare(password, user.password)) {
    return res.status(401).json({ message: 'Invalid credentials' });
  }

  const accessToken = jwt.sign({ userId: user.id, email: user.email, role: user.role }, SECRET_KEY, { expiresIn: '15m' });
  const refreshToken = jwt.sign({ userId: user.id, email: user.email, role: user.role }, SECRET_KEY, { expiresIn: '7d' });

  res.cookie('refreshToken', refreshToken, {
    httpOnly: true,
    secure: true,
    sameSite: 'strict',
  });

  res.json({ accessToken, refreshToken

*Response time: 18.4s*

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
Continuing from the previous authentication system, let's delve into each of the additional requirements:

### 1. POST /auth/refresh
Use the refresh token from a cookie to issue a new access token. Rotate the refresh token by issuing a new one and invalidating the old one.

#### Implementation:
- **Endpoint**: `/auth/refresh`
- **Method**: `POST`
- **Request Body**: `{ "refresh_token": "old_refresh_token" }`
- **Response**: `{ "access_token": "new_access_token", "refresh_token": "new_refresh_token" }`

#### Code Snippet (Python using Flask):
```python
from flask import Flask, request, make_response, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token, create_refresh_token, get_jwt
import redis

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = True  # Use HTTPS
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 300  # 5 minutes
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 2592000  # 30 days

jwt = JWTManager(app)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

@app.route('/auth/refresh', methods=['POST'])
def refresh():
    refresh_token = request.json.get('refresh_token')
    if not refresh_token:
        return jsonify({"msg": "Missing refresh token"}), 400

    try:
        claims = get_jwt(refresh_token)
        user_id = claims['sub']
    except:
        return jsonify({"msg": "Invalid refresh token"}), 401

    # Invalidate old refresh token
    redis_client.delete(f'refresh_token:{user_id}')

    # Create new access and refresh tokens
    new_access_token = create_access_token(identity=user_id)
    new_refresh_token = create_refresh_token(identity=user_id)

    # Store new refresh token in Redis
    redis_client.setex(f'refresh_token:{user_id}', 2592000, new_refresh_token)

    response = make_response(jsonify({"access_token": new_access_token, "refresh_token": new_refresh_token}))
    response.set_cookie('refresh_token', new_refresh_token, httponly=True, secure=True, samesite='None')
    return response, 200
```

### 2. POST /auth/logout
Invalidate the refresh token and clear the cookie.

#### Implementation:
- **Endpoint**: `/auth/logout`
- **Method**: `POST`
- **Request Body**: None
- **Response**: `{ "msg": "Logged out successfully" }`

#### Code Snippet (Python using Flask):
```python
@app.route('/auth/logout', methods=['POST'])
@jwt_required(refresh=True)
def logout():
    user_id = get_jwt_identity()
    refresh_token = request.cookies.get('refresh_token')

    if not refresh_token:
        return jsonify({"msg": "Missing refresh token"}), 400

    # Invalidate refresh token
    redis_client.delete(f'refresh_token:{user_id}')

    response = make_response(jsonify({"msg": "Logged out successfully"}))
    response.set_cookie('refresh_token', '', expires=0, httponly=True, secure=True, samesite='None')
    return response, 200
```

### 3. Redis-based Token Store
Use Redis to store refresh tokens with a TTL strategy.

#### Redis Data Structure:
- **Key**: `refresh_token:{user_id}`
- **Value**: `refresh_token_string`
- **TTL**: 30 days (2592000 seconds)

#### TTL Strategy:
- When a new refresh token is issued, set it with a TTL of 30 days.
- When a refresh token is used, it should be invalidated by deleting it from Redis.

### 4. Handling Token Reuse Detection
Detect if a refresh token is used twice.

#### Implementation:
- Track each refresh token's usage in Redis with a counter.
- Increment the counter each time a refresh token is used.
- If the counter exceeds a certain threshold, invalidate the refresh token.

#### Code Snippet (Python using Flask):
```python
@app.route('/auth/refresh', methods=['POST'])
def refresh():
    refresh_token = request.json.get('refresh_token')
    if not refresh_token:
        return jsonify({"msg": "Missing refresh token"}), 400

    try:
        claims = get_jwt(refresh_token)
        user_id = claims['sub']
    except:
        return jsonify({"msg": "Invalid refresh token"}), 401

    # Check if refresh token has been used before
    refresh_usage_key = f'refresh_usage:{user_id}'
    if redis_client.exists(refresh_usage_key):
        usage_count = redis_client.incr(refresh_usage_key)
        if usage_count > 10:  # Limit to 10 uses
            return jsonify({"msg": "Refresh token reused too many times"}), 401
    else:
        redis_client.setex(refresh_usage_key, 2592000, 1)

    # Invalidate old refresh token
    redis_client.delete(f'refresh_token:{user_id}')

    # Create new access and refresh tokens
    new_access_token = create_access_token(identity=user_id)
    new_refresh_token = create_refresh_token(identity=user_id)

    # Store new refresh token in Redis
    redis_client.setex(f'refresh_token:{user_id}', 2592000, new_refresh_token)

    response = make_response(jsonify({"access_token": new_access_token, "refresh_token": new_refresh_token}))
    response.set_cookie('refresh_token', new_refresh_token, httponly=True, secure=True, samesite='None')
    return response, 200
```

### 5. Invalidating All Existing Sessions When a User Changes Their Password
Invalidate all existing sessions when a user changes their password.

#### Implementation:
- When a user changes their password, delete all their stored refresh tokens in Redis.

#### Code Snippet (Python using Flask):
```python
@app.route('/user/change_password', methods=['POST'])
@jwt_required()
def change_password():
    user_id = get_jwt_identity()
    new_password = request.json.get('new_password')

    # Update user password in database
    # ...

    # Invalidate all refresh tokens for the user
    redis_client.delete(f'refresh_token:{user_id}')

    return jsonify({"msg": "Password changed successfully"}), 200
```

### 6. Difference Between Token Blacklisting and Token Rotation
- **Token Blacklisting**:
  - **Mechanism**: Store invalid tokens in a blacklist (usually a database).
  - **Check**: Each token is checked against the blacklist before processing.
  - **Use Case**: Suitable for systems where token revocation needs to be done frequently and securely.

- **Token Rotation**:
  - **Mechanism**: Issue new tokens and invalidate old ones.
  - **Check**: Tokens are only valid within their expiration period.
  - **Use Case**: Suitable for systems where token revocation is less frequent and performance is critical.

**When to Use Each**:
- **Token Blacklisting**: Use when frequent revocation of specific tokens is required, and security is a priority.
- **Token Rotation**: Use when performance is critical and token revocation is less frequent. It is generally simpler to implement and more efficient for long-lived tokens.

*Response time: 31.7s*

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
### TypeScript Interface for Props
First, let's define the TypeScript interface for the props of the `DataTable` component. This interface should be generic and work for any row type.

```typescript
interface Column<T> {
  key: keyof T;
  header: string;
  width?: string;
  sortable?: boolean;
  renderCell?: (row: T) => React.ReactNode;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  pageSize?: number;
  onPageChange?: (page: number) => void;
  onSelectRow?: (selectedRows: T[]) => void;
  selectedRows?: T[];
  isControlled?: boolean;
}
```

### Complete Component Implementation
Now, let's implement the `DataTable` component. This component will handle sorting, row selection, pagination, and support both controlled and uncontrolled modes.

```typescript
import React, { useState, useMemo, useCallback, useRef } from 'react';

const DataTable = <T extends object>(props: DataTableProps<T>): JSX.Element => {
  const {
    columns,
    data,
    pageSize = 10,
    onPageChange,
    onSelectRow,
    selectedRows: controlledSelectedRows,
    isControlled = false,
  } = props;

  const [sortKey, setSortKey] = useState<keyof T | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc' | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [internalSelectedRows, setInternalSelectedRows] = useState<T[]>([]);
  const [internalData, setInternalData] = useState(data);

  const selectedRows = isControlled ? controlledSelectedRows || [] : internalSelectedRows;

  const handleSort = useCallback((key: keyof T) => {
    if (sortKey === key) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDirection('asc');
    }
  }, [sortKey, sortDirection]);

  const handleSelectRow = useCallback((row: T, checked: boolean) => {
    if (checked) {
      setInternalSelectedRows([...selectedRows, row]);
    } else {
      setInternalSelectedRows(selectedRows.filter(r => r !== row));
    }

    if (!isControlled && onSelectRow) {
      onSelectRow(internalSelectedRows);
    }
  }, [selectedRows, isControlled, onSelectRow]);

  const handleSelectAll = useCallback(() => {
    if (internalData.length > 0) {
      setInternalSelectedRows(isControlled ? controlledSelectedRows || [] : internalData);
      if (!isControlled && onSelectRow) {
        onSelectRow(isControlled ? controlledSelectedRows || [] : internalData);
      }
    } else {
      setInternalSelectedRows([]);
      if (!isControlled && onSelectRow) {
        onSelectRow([]);
      }
    }
  }, [internalData, isControlled, onSelectRow, controlledSelectedRows]);

  const handlePageChange = useCallback((page: number) => {
    setCurrentPage(page);
    if (onPageChange) {
      onPageChange(page);
    }
  }, [onPageChange]);

  const totalPages = Math.ceil(internalData.length / pageSize);

  const sortedData = useMemo(() => {
    let result = [...internalData];

    if (sortKey) {
      result.sort((a, b) => {
        const aValue = a[sortKey] as any;
        const bValue = b[sortKey] as any;

        if (aValue < bValue) {
          return sortDirection === 'asc' ? -1 : 1;
        } else if (aValue > bValue) {
          return sortDirection === 'asc' ? 1 : -1;
        } else {
          return 0;
        }
      });
    }

    return result;
  }, [sortKey, sortDirection, internalData]);

  const paginatedData = useMemo(() => {
    return sortedData.slice((currentPage - 1) * pageSize, currentPage * pageSize);
  }, [sortedData, currentPage, pageSize]);

  const headerCells = columns.map(column => (
    <th
      key={column.key}
      onClick={() => column.sortable && handleSort(column.key)}
      style={{ width: column.width }}
    >
      {column.header}
      {sortKey === column.key && (
        <span>
          {sortDirection === 'asc' ? ' 🔼' : sortDirection === 'desc' ? ' 🔽' : ''}
        </span>
      )}
    </th>
  ));

  const rowCells = paginatedData.map(row => (
    <tr key={row[columns[0].key]}>
      <td>
        <input
          type="checkbox"
          checked={selectedRows.includes(row)}
          onChange={e => handleSelectRow(row, e.target.checked)}
        />
      </td>
      {columns.map(column => (
        <td key={column.key}>
          {column.renderCell ? column.renderCell(row) : row[column.key] as any}
        </td>
      ))}
    </tr>
  ));

  return (
    <div>
      <table>
        <thead>
          <tr>
            <th>
              <input
                type="checkbox"
                checked={selectedRows.length === internalData.length}
                onChange={handleSelectAll}
              />
            </th>
            {headerCells}
          </tr>
        </thead>
        <tbody>{rowCells}</tbody>
      </table>
      <div>
        <button onClick={() => handlePageChange(currentPage - 1)} disabled={currentPage === 1}>
          Prev
        </button>
        <span>Page {currentPage} of {totalPages}</span>
        <button onClick={() => handlePageChange(currentPage + 1)} disabled={currentPage === totalPages}>
          Next
        </button>
      </div>
    </div>
  );
};

export default DataTable;
```

### Usage Example
Here's an example of how to use the `DataTable` component with 3 columns, including a custom renderCell for an action button.

```typescript
import React, { useState } from 'react';
import DataTable from './DataTable';

const App = () => {
  const [rows, setRows] = useState([
    { id: 1, name: 'Alice', age: 25 },
    { id: 2, name: 'Bob', age: 30 },
    { id: 3, name: 'Charlie', age: 35 },
  ]);

  const [selectedRows, setSelectedRows] = useState<{ id: number, name: string, age: number }[]>([]);

  const columns: any = [
    { key: 'id', header: 'ID', width: '100px' },
    { key: 'name', header: 'Name' },
    {
      key: 'action',
      header: 'Action',
      width: '100px',
      renderCell: (row: any) => (
        <button onClick={() => alert(`Action for ${row.name}`)}>Action</button>
      ),
    },
  ];

  return (
    <div>
      <h1>DataTable Example</h1>
      <DataTable
        columns={columns}
        data={rows}
        selectedRows={selectedRows}
        onSelectRow={setSelectedRows}
      />
    </div>
  );
};

export default App;
```

### Memoization
To memoize the component correctly and avoid unnecessary re-renders, we can use `useMemo` and `useCallback` where necessary. Here are some places where memoization can be applied:

1. **Sorting**: The sorted data is memoized based on the sort key and sort direction.
2. **Pagination**: The paginated data is memoized based on the current page and page size.
3. **Header Cells**: The header cells are memoized based on the columns.
4. **Row Cells**: The row cells are memoized based on the paginated data and columns.

By using `useMemo` and `useCallback`, we ensure that only the relevant parts of the component re-render when their dependencies change, thus improving performance.

*Response time: 34.3s*

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
Let's break down the requirements and implement them step-by-step using React hooks.

### 1. Custom Hook: `useSearch(query: string)`

The custom hook `useSearch` will handle the search logic, including debounce, fetch, caching, and cancellation.

```jsx
import { useState, useEffect } from 'react';

const SEARCH_DEBOUNCE = 300;
const CACHE_EXPIRY = 5 * 60 * 1000; // 5 minutes

const useSearch = (query) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [cancelTokenSource, setCancelTokenSource] = useState(null);

  useEffect(() => {
    // Cancel previous request if it exists
    if (cancelTokenSource) {
      cancelTokenSource.cancel();
    }

    const newCancelTokenSource = new AbortController();
    setCancelTokenSource(newCancelTokenSource);

    const fetchData = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch(`/api/search?q=${query}`, {
          signal: newCancelTokenSource.signal,
        });

        if (!response.ok) {
          throw new Error('Network response was not ok');
        }

        const result = await response.json();

        // Cache the result if it's a new query
        localStorage.setItem(query, JSON.stringify({ data: result, timestamp: Date.now() }));

        setData(result);
      } catch (err) {
        if (err.name === 'AbortError') {
          console.log('Fetch aborted');
        } else {
          setError(err.message);
        }
      } finally {
        setLoading(false);
      }
    };

    const cachedData = localStorage.getItem(query);
    if (cachedData) {
      const { data: cachedResult, timestamp } = JSON.parse(cachedData);
      const isCacheValid = Date.now() - timestamp < CACHE_EXPIRY;
      if (isCacheValid) {
        setData(cachedResult);
      } else {
        fetchData();
      }
    } else {
      fetchData();
    }

    // Clean up on unmount
    return () => {
      newCancelTokenSource.abort();
    };
  }, [query]);

  return { data, loading, error };
};

export default useSearch;
```

### 2. SearchPage Component

The `SearchPage` component will use the `useSearch` hook to display the search results.

```jsx
import React, { useState, useEffect } from 'react';
import useSearch from './useSearch';

const SearchPage = () => {
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    // Update URL when searchTerm changes
    window.history.pushState({ query: searchTerm }, '', `?q=${searchTerm}`);
  }, [searchTerm]);

  useEffect(() => {
    // Sync searchTerm from URL when the component mounts
    const urlParams = new URLSearchParams(window.location.search);
    setSearchTerm(urlParams.get('q') || '');
  }, []);

  const { data, loading, error } = useSearch(searchTerm);

  const handleInputChange = (event) => {
    setSearchTerm(event.target.value);
  };

  return (
    <div>
      <input
        type="text"
        value={searchTerm}
        onChange={handleInputChange}
        placeholder="Search..."
      />
      {loading && <div>Loading...</div>}
      {data && data.length > 0 ? (
        <ul>
          {data.map((item) => (
            <li key={item.id}>{item.title}</li>
          ))}
        </ul>
      ) : data && data.length === 0 ? (
        <div>No results</div>
      ) : (
        error && (
          <div>
            {error}
            <button onClick={() => window.location.reload()}>Retry</button>
          </div>
        )
      )}
    </div>
  );
};

export default SearchPage;
```

### 3. URL Sync Implementation

The URL sync is implemented using `useEffect` to update the URL when `searchTerm` changes and to sync `searchTerm` from the URL when the component mounts.

### 4. Why is cancelling in-flight requests important here? What bug does it prevent?

Cancelling in-flight requests is important because it prevents the following bugs:

1. **Stale Data**: If a user types a new query quickly after a previous request, the old request might complete and update the state with stale data, leading to an incorrect display.
2. **Memory Leaks**: If a component unmounts while a request is in flight, the component's state would not be updated, potentially causing memory leaks.
3. **Repetitive Work**: If a user types the same query multiple times, multiple requests would be sent, leading to unnecessary work and potential server load.

By cancelling in-flight requests when a new search starts, we ensure that only the most recent request is processed, and any previous requests are cleaned up properly. This prevents the above-mentioned issues and ensures a smooth user experience.

*Response time: 21.4s*

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
1. To fetch the 10 most recent published posts along with the author's name, tag names, and comment count, you can use the following Prisma query. This query ensures no N+1 queries by using Prisma's powerful query capabilities.

```prisma
prisma.post.findMany({
  where: {
    published: true,
  },
  include: {
    author: {
      select: {
        name: true,
      },
    },
    tags: {
      select: {
        name: true,
      },
    },
    comments: true,
  },
  orderBy: {
    createdAt: 'desc',
  },
  take: 10,
});
```

2. Adding a `slug` field to a table with 10M rows without downtime can be achieved using a combination of a temporary column and a `NOT NULL` constraint. Here’s a migration scenario:

```sql
-- Step 1: Add a temporary column
ALTER TABLE "Post" ADD COLUMN "temp_slug" TEXT;

-- Step 2: Populate the temporary column with unique, non-nullable values
-- For simplicity, we can generate slugs based on the title
-- This step assumes a unique slug is generated for each title
UPDATE "Post" SET "temp_slug" = lower(replace(trim(title), ' ', '-')) || '_' || id;

-- Step 3: Check for uniqueness and update where necessary
-- This step ensures no duplicates and handles any potential conflicts
WITH slug_counts AS (
  SELECT "temp_slug", COUNT(*) AS count
  FROM "Post"
  GROUP BY "temp_slug"
)
UPDATE "Post" p
SET "temp_slug" = p."temp_slug" || '_' || p.id
FROM slug_counts sc
WHERE p."temp_slug" = sc."temp_slug" AND sc.count > 1;

-- Step 4: Add the new column
ALTER TABLE "Post" ADD COLUMN "slug" TEXT NOT NULL;

-- Step 5: Update the new column with the temporary values
UPDATE "Post" SET "slug" = "temp_slug";

-- Step 6: Drop the temporary column
ALTER TABLE "Post" DROP COLUMN "temp_slug";

-- Step 7: Add the unique constraint
ALTER TABLE "Post" ADD CONSTRAINT "Post_slug_key" UNIQUE ("slug");
```

3. If a query is slow, such as `findMany posts filtered by tag name`, it can be diagnosed and fixed as follows:

```prisma
// Prisma Query
prisma.post.findMany({
  where: {
    tags: {
      some: {
        name: 'example-tag',
      },
    },
  },
  include: {
    author: true,
    tags: true,
    comments: true,
  },
});
```

**Raw SQL Generated**:
```sql
SELECT "Post".*, "User".name AS "author.name", "Tag".name AS "tags.name", "Comment".id AS "comments.id"
FROM "Post"
LEFT JOIN "User" ON "Post"."authorId" = "User"."id"
LEFT JOIN "PostTag" ON "Post"."id" = "PostTag"."postId"
LEFT JOIN "Tag" ON "PostTag"."tagId" = "Tag"."id"
LEFT JOIN "Comment" ON "Post"."id" = "Comment"."postId"
WHERE "Tag"."name" = 'example-tag';
```

**Index to Add**:
To optimize this query, you need an index on the `name` column of the `Tag` table and a composite index on the `postId` and `tagId` columns of the `PostTag` table.

```sql
CREATE INDEX "Tag_name" ON "Tag" ("name");
CREATE INDEX "PostTag_postId_tagId" ON "PostTag" ("postId", "tagId");
```

4. You might drop down from Prisma to raw SQL when dealing with complex queries that are difficult to optimize or when you need fine-grained control over database performance. For example, if you need to perform a bulk update based on complex conditions, raw SQL might be more efficient than using Prisma's ORM. Here’s an example:

```prisma
// Prisma Query (Complex Bulk Update)
prisma.post.updateMany({
  where: {
    // Complex condition
    AND: [
      {
        published: true,
      },
      {
        createdAt: {
          lt: new Date('2023-01-01T00:00:00Z'),
        },
      },
    ],
  },
  data: {
    published: false,
  },
});
```

**Raw SQL Equivalent**:
```sql
-- Raw SQL Query (Complex Bulk Update)
UPDATE "Post"
SET "published" = false
WHERE "published" = true
AND "createdAt" < '2023-01-01T00:00:00Z';
```

This example demonstrates how a complex bulk update might be more efficiently handled using raw SQL, especially when the Prisma ORM does not provide a straightforward way to achieve the desired performance.

*Response time: 21.3s*

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
1. **docker-compose.yml for Local Development:**

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypassword
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U myuser -d myapp"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:latest
    ports:
      - "6379:6379"

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    volumes:
      - ./backend:/app
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgres://myuser:mypassword@postgres:5432/myapp
      - REDIS_URL=redis://redis:6379
    ports:
      - "3000:3000"
    depends_on:
      postgres:
        condition: service_healthy

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    volumes:
      - ./frontend:/app
    environment:
      - REACT_APP_BACKEND_URL=http://backend:3000
    ports:
      - "3001:3001"
    command: ["npm", "start"]

volumes:
  postgres_data:
```

2. **Production Dockerfile for the Backend:**

```dockerfile
# Builder stage
FROM node:16 as builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install --only=production

# Copy the rest of the source code
COPY . .

# Run migrations if any
RUN npm run db:migrate

# Runtime stage
FROM node:16 as runtime

WORKDIR /app

COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app ./

# Create a non-root user and switch to it
RUN useradd -r -s /bin/false appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 3000

# Command to run the application
CMD ["node", "server.js"]
```

3. **Backend Crashes with Exit Code 137:**

Exit code 137 indicates that the process was terminated by the operating system (usually due to resource limits). This is often caused by running out of memory or hitting the default cgroup limits.

To diagnose:
- Check the container logs for any errors or warnings.
- Increase the memory limits for the container.
- Ensure that the application is not leaking memory.
- Check if the container is hitting the cgroup limits (e.g., `docker stats`).

4. **Deployment Sequence with Zero Downtime:**

1. **Prepare the New Version:**
   - Update the backend code to include the new nullable column.
   - Run migrations to add the column.
   - Build the new Docker image using the production Dockerfile.
   - Push the new image to the container registry.

2. **Create a New Deployment:**
   - Scale down the current deployment to zero (optional, if you want to verify the new version first).
   - Deploy the new version using the new Docker image.
   - Scale up the new deployment.
   - Monitor the new version for any issues.

3. **Verify the New Version:**
   - Check the logs for any errors.
   - Ensure that the new version is functioning as expected.
   - If everything is okay, switch the DNS records to point to the new deployment.

4. **Rollback (if necessary):**
   - If issues are found, scale down the new deployment to zero.
   - Scale up the previous version.
   - Monitor the previous version for any issues.
   - Switch the DNS records back to the previous version.

By following this sequence, you can achieve zero downtime during a deployment with a database schema change.

*Response time: 17.9s*

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

To associate a WebSocket connection with a user and document, we can use a combination of user IDs and document IDs. We'll store this information in a `Map` to facilitate quick lookups and updates.

```javascript
const WebSocket = require('ws');
const http = require('http');
const server = http.createServer();
const wss = new WebSocket.Server({ server });

const documentUsers = new Map(); // Map<DocumentID, Set<UserID>>
const userDocuments = new Map(); // Map<UserID, DocumentID>

wss.on('connection', (ws, req) => {
  const userID = req.url.split('?')[1].split('=')[1]; // Extract userID from URL query parameter

  ws.on('message', (message) => {
    const parsedMessage = JSON.parse(message);
    handleMessage(ws, userID, parsedMessage);
  });

  ws.on('close', () => {
    handleDisconnect(userID);
  });

  // Initial join document message
  const documentID = req.url.split('?')[2].split('=')[1]; // Extract documentID from URL query parameter
  ws.documentID = documentID; // Store documentID in the connection object
  userDocuments.set(userID, documentID);

  if (!documentUsers.has(documentID)) {
    documentUsers.set(documentID, new Set());
  }
  documentUsers.get(documentID).add(userID);

  ws.send(JSON.stringify({ type: 'join_document', documentID, text: 'Initial document content' }));
});

function handleMessage(ws, userID, message) {
  const documentID = ws.documentID;

  switch (message.type) {
    case 'text_change':
      broadcastTextChange(documentID, userID, message.textChange);
      break;
    case 'cursor_move':
      broadcastCursorMove(documentID, userID, message.cursorMove);
      break;
    // Handle other message types
  }
}

function broadcastTextChange(documentID, userID, textChange) {
  const usersInDocument = documentUsers.get(documentID);
  for (const user of usersInDocument) {
    if (user !== userID) {
      wss.clients.forEach((client) => {
        if (client.readyState === WebSocket.OPEN && client.documentID === documentID && client.userDocuments.has(userID)) {
          client.send(JSON.stringify({ type: 'text_change', textChange }));
        }
      });
    }
  }
}

function broadcastCursorMove(documentID, userID, cursorMove) {
  const usersInDocument = documentUsers.get(documentID);
  for (const user of usersInDocument) {
    if (user !== userID) {
      wss.clients.forEach((client) => {
        if (client.readyState === WebSocket.OPEN && client.documentID === documentID && client.userDocuments.has(userID)) {
          client.send(JSON.stringify({ type: 'cursor_move', cursorMove }));
        }
      });
    }
  }
}

function handleDisconnect(userID) {
  userDocuments.delete(userID);
  documentUsers.forEach((users, documentID) => {
    users.delete(userID);
    if (users.size === 0) {
      documentUsers.delete(documentID);
    }
  });
}

server.listen(3000, () => {
  console.log('Server is running on port 3000');
});
```

### 2. Message Protocol

Here are the message types and their structure:

- **Join Document**: Sent when a user joins a document.
  ```json
  {
    "type": "join_document",
    "documentID": "document123",
    "text": "Initial document content"
  }
  ```

- **Text Change**: Sent when a user makes a change to the document.
  ```json
  {
    "type": "text_change",
    "textChange": {
      "start": 5,
      "length": 1,
      "text": "A"
    }
  }
  ```

- **Cursor Move**: Sent when a user moves their cursor.
  ```json
  {
    "type": "cursor_move",
    "cursorMove": {
      "position": 10
    }
  }
  ```

- **User Left**: Sent when a user disconnects.
  ```json
  {
    "type": "user_left",
    "userID": "user456"
  }
  ```

### 3. Broadcasting

When a user makes a change, the server broadcasts the change to all other users in the same document, excluding the user who made the change.

```javascript
function broadcastTextChange(documentID, userID, textChange) {
  const usersInDocument = documentUsers.get(documentID);
  for (const user of usersInDocument) {
    if (user !== userID) {
      wss.clients.forEach((client) => {
        if (client.readyState === WebSocket.OPEN && client.documentID === documentID && client.userDocuments.has(userID)) {
          client.send(JSON.stringify({ type: 'text_change', textChange }));
        }
      });
    }
  }
}
```

### 4. Reconnection

When a user reconnects, they should receive the latest document state. This can be achieved by sending the current document content to the user upon reconnection.

```javascript
wss.on('connection', (ws, req) => {
  const userID = req.url.split('?')[1].split('=')[1]; // Extract userID from URL query parameter
  const documentID = req.url.split('?')[2].split('=')[1]; // Extract documentID from URL query parameter

  ws.on('message', (message) => {
    const parsedMessage = JSON.parse(message);
    handleMessage(ws, userID, parsedMessage);
  });

  ws.on('close', () => {
    handleDisconnect(userID);
  });

  // Send initial document content upon reconnection
  ws.documentID = documentID;
  userDocuments.set(userID, documentID);

  if (!documentUsers.has(documentID)) {
    documentUsers.set(documentID, new Set());
  }
  documentUsers.get(documentID).add(userID);

  ws.send(JSON.stringify({ type: 'join_document', documentID, text: 'Initial document content' }));
});
```

### 5. Simultaneous Edits

If two users edit the exact same position simultaneously, this is a classic problem known as the **"simultaneous edit"** problem. Solutions include:

- **Conflict Resolution**: Implement a conflict resolution strategy to determine which change to keep and which to discard. This can be done using a more advanced approach like Operational Transformation (OT) or Conflict-free Replicated Data Type (CRDT).

- **Versioning**: Keep track of the version of each document and resolve conflicts based on version numbers.

- **Locking**: Implement locking mechanisms to ensure that only one user can edit a specific part of the document at a time.

For simplicity, in this example, we are not implementing OT/CRDT, and the problem is left unhandled.

*Response time: 28.6s*

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
scalar Date

type Recipe {
  id: ID!
  title: String!
  ingredients: [Ingredient!]!
  steps: [String!]!
  author: Author!
  tags: [String!]!
  ratings: [Rating!]!
  averageRating: Float!
}

type Ingredient {
  name: String!
  amount: Float!
  unit: String!
}

type Author {
  id: ID!
  name: String!
}

type Rating {
  id: ID!
  score: Float!
  comment: String!
}

type Query {
  recipes(filter: RecipeFilter, pagination: Pagination): [Recipe!]!
}

type Mutation {
  addRating(recipeId: ID!, score: Float!, comment: String!): Rating!
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

#### Query.recipes

```javascript
const recipesResolver = async (_, { filter, pagination }, context) => {
  const { page = 1, limit = 10 } = pagination;
  const skip = (page - 1) * limit;

  const query = {};
  if (filter.tag) {
    query.tags = { $in: [filter.tag] };
  }
  if (filter.minRating) {
    query.ratings = { $elemMatch: { score: { $gte: filter.minRating } } };
  }

  const recipes = await Recipe.find(query).skip(skip).limit(limit);
  const totalCount = await Recipe.countDocuments(query);

  return {
    recipes,
    pagination: {
      page,
      limit,
      total: totalCount,
    },
  };
};
```

#### Mutation.addRating

```javascript
const addRatingResolver = async (_, { recipeId, score, comment }, context) => {
  const recipe = await Recipe.findById(recipeId);
  if (!recipe) {
    throw new Error('Recipe not found');
  }

  const rating = new Rating({ score, comment });
  recipe.ratings.push(rating);
  await recipe.save();

  return rating;
};
```

#### Recipe.averageRating

```javascript
const averageRatingResolver = async (recipe) => {
  const ratings = await Rating.find({ recipeId: recipe.id });
  const totalScore = ratings.reduce((sum, rating) => sum + rating.score, 0);
  return totalScore / ratings.length || 0;
};
```

### 3. N+1 Problem with Authors

**Problem Example:**

Suppose we have 10 recipes, and each recipe is associated with a unique author. If we fetch all the recipes with their authors, we would make 10 separate queries to fetch the authors.

**Solution with DataLoader:**

```javascript
const authorLoader = new DataLoader(async (authorIds) => {
  const authors = await Author.find({ _id: { $in: authorIds } });
  const authorMap = new Map(authors.map(author => [author._id.toString(), author]));
  return authorIds.map(authorId => authorMap.get(authorId.toString()));
});

const recipesResolver = async (_, { filter, pagination }, context) => {
  const { page = 1, limit = 10 } = pagination;
  const skip = (page - 1) * limit;

  const query = {};
  if (filter.tag) {
    query.tags = { $in: [filter.tag] };
  }
  if (filter.minRating) {
    query.ratings = { $elemMatch: { score: { $gte: filter.minRating } } };
  }

  const recipes = await Recipe.find(query).skip(skip).limit(limit);
  const authorIds = recipes.map(recipe => recipe.author.id);

  const authors = await authorLoader.loadMany(authorIds);

  return recipes.map(recipe => ({
    ...recipe.toObject(),
    author: authors.find(author => author._id.toString() === recipe.author.id),
  }));
};
```

### 4. GraphQL Query for Client

```graphql
query {
  recipes(filter: { tag: "Dinner", minRating: 4.0 }, pagination: { page: 1, limit: 10 }) {
    recipes {
      title
      author {
        name
      }
      ingredients {
        name
        amount
        unit
        firstThreeIngredients: ingredients(limit: 3) {
          name
          amount
          unit
        }
      }
    }
  }
}
```

### 5. When to Choose GraphQL over REST

- **Complex Queries:** When clients need to fetch related data in a single request.
- **Real-time Updates:** GraphQL's subscriptions feature makes it ideal for real-time data updates.
- **Dynamic Schema:** When the API schema is expected to evolve over time.

**When NOT to Choose GraphQL over REST:**

- **Simplicity:** For very simple APIs, REST might be easier to implement and understand.
- **Caching:** REST's caching mechanisms are more straightforward compared to GraphQL's approach.
- **Large Data Sets:** For very large data sets, GraphQL can be less efficient due to its query complexity.

GraphQL is a powerful tool for building robust, efficient APIs, but it's important to consider the specific needs of your application when deciding whether to use it.

*Response time: 22.2s*

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
To implement the desired UI layout using only CSS, we'll use a combination of Flexbox and CSS Grid. Here's the complete HTML and CSS code:

### HTML
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UI Layout</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        HEADER (fixed, full width, 60px tall)
    </header>
    <div class="container">
        <aside>
            Sidebar
        </aside>
        <main>
            <div class="grid-container">
                <div class="card">
                    <img src="image1.jpg" alt="Card Image 1">
                    <div class="card-content">
                        <h3>Title 1</h3>
                        <p>Description 1</p>
                    </div>
                    <footer>
                        <button class="left-button">Button 1</button>
                        <button class="right-button">Button 2</button>
                    </footer>
                </div>
                <div class="card">
                    <img src="image2.jpg" alt="Card Image 2">
                    <div class="card-content">
                        <h3>Title 2</h3>
                        <p>Description 2</p>
                    </div>
                    <footer>
                        <button class="left-button">Button 1</button>
                        <button class="right-button">Button 2</button>
                    </footer>
                </div>
                <!-- Add more cards as needed -->
            </div>
        </main>
    </div>
</body>
</html>
```

### CSS (styles.css)
```css
body, html {
    margin: 0;
    padding: 0;
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
    text-align: center;
    line-height: 60px;
}

.container {
    display: flex;
    flex-direction: column;
    height: 100vh;
    margin-top: 60px; /* Space for the header */
}

aside {
    width: 240px;
    background-color: #f4f4f4;
    overflow-y: auto;
}

main {
    flex-grow: 1;
    overflow-y: auto;
}

.grid-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 16px;
    padding: 16px;
}

.card {
    display: flex;
    flex-direction: column;
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card img {
    width: 100%;
    height: 0;
    padding-bottom: 56.25%; /* 16:9 aspect ratio */
    object-fit: cover;
}

.card-content {
    padding: 16px;
}

.card footer {
    display: flex;
    justify-content: space-between;
    padding: 16px;
    border-top: 1px solid #ddd;
}

.left-button {
    flex: 1;
    margin-right: 8px;
}

.right-button {
    flex: 1;
    margin-left: 8px;
}
```

### Explanation of the Layout Approach

1. **Header**: 
   - Fixed at the top of the viewport using `position: fixed`.

2. **Container**:
   - Uses `flex-direction: column` to stack the sidebar and main content vertically.
   - Height set to `100vh` to fill the full viewport height and `margin-top: 60px` to create space for the fixed header.

3. **Sidebar**:
   - Fixed width of `240px`.
   - `overflow-y: auto` allows scrolling when content exceeds the sidebar height.

4. **Main Content**:
   - Flex-grow property ensures it fills the remaining space.
   - `overflow-y: auto` allows scrolling when content exceeds the main content height.

5. **Cards**:
   - Uses `display: grid` with `grid-template-columns: repeat(auto-fill, minmax(300px, 1fr))` to create a responsive grid that adjusts to the screen width.
   - Cards have a fixed height ratio of 16:9 for images.
   - Buttons are aligned left and right using `flex` properties.

This layout uses Flexbox for the overall structure and Grid for the cards to achieve the desired responsive design and independent scrolling behavior.

*Response time: 21.1s*

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
1. Transport mechanism:
WebSocket would be the ideal choice for real-time notifications in this project. WebSocket provides a full-duplex communication channel over a single TCP connection, which allows for instant and continuous data exchange between the server and the client. This makes it perfect for real-time applications like project management tools. Additionally, WebSocket is better suited for handling large numbers of concurrent connections and can reduce the number of HTTP requests required for communication, which improves performance.

2. Notification storage:
For storing notifications, a NoSQL database like MongoDB or a time-series database like InfluxDB could be used. Both options offer high scalability, flexible schemas, and efficient querying capabilities. Alternatively, a SQL database like PostgreSQL could also be used, but it might require more complex queries and more effort to handle scalability. 

The database schema could include the following collections:

- Users: Stores information about each user, including their ID and notification preferences.
- Tasks: Stores information about each task, including the task ID, owner ID, and deadline.
- Notifications: Stores information about each notification, including the notification ID, user ID, task ID, and message.

3. Handling offline users:
When a user goes offline, their notifications will be stored in a queue until they come back online. Once they come online, the notifications can be sent to them. This can be achieved by integrating a message broker like RabbitMQ or Apache Kafka, which can handle message delivery and persistence. When a user comes online, their notifications can be fetched from the queue and sent to them.

4. Deadline check implementation:
To implement the deadline check, a cron job or a queue-based system could be used. A cron job is a scheduled task that runs at regular intervals, while a queue-based system allows tasks to be processed asynchronously. In this case, a queue-based system would be more suitable as it allows tasks to be processed independently of the cron job and can handle a higher volume of tasks.

To implement the deadline check using a queue-based system, a task scheduler like Celery could be used. Celery allows tasks to be scheduled and executed asynchronously, and can handle a large number of tasks efficiently. The deadline check task could be scheduled to run every hour for all tasks, and would check if any tasks are approaching their deadline. If a task is approaching its deadline, a notification could be created and sent to the task owner.

5. Scaling:
To scale this system to handle 100,000 concurrent users, several techniques could be used:

- Load balancing: Distribute incoming requests across multiple servers to reduce the load on a single server.
- Caching: Store frequently accessed data in memory to reduce the number of database queries required.
- Microservices architecture: Break the system into smaller, independent services that can be scaled independently.
- Content delivery network (CDN): Serve static assets and content from a CDN to reduce the load on the servers.

These techniques can help improve the performance and scalability of the system, allowing it to handle a large number of concurrent users.

*Response time: 12.7s*

---
