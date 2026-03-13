# Model: qwen2.5-coder:32b
**Test Date:** 2026-03-12 14:32:12
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
### REST API Design for a Multi-Tenant SaaS Project Management Tool

#### 1. Endpoints

**Workspace:**
- `GET /workspaces`: List all workspaces a user belongs to.
- `POST /workspaces`: Create a new workspace.
- `GET /workspaces/{workspaceId}`: Retrieve a specific workspace.
- `PUT /workspaces/{workspaceId}`: Update a specific workspace.
- `DELETE /workspaces/{workspaceId}`: Delete a specific workspace.

**Project:**
- `GET /workspaces/{workspaceId}/projects`: List all projects in a workspace.
- `POST /workspaces/{workspaceId}/projects`: Create a new project in a workspace.
- `GET /workspaces/{workspaceId}/projects/{projectId}`: Retrieve a specific project.
- `PUT /workspaces/{workspaceId}/projects/{projectId}`: Update a specific project.
- `DELETE /workspaces/{workspaceId}/projects/{projectId}`: Delete a specific project.

**Task:**
- `GET /workspaces/{workspaceId}/projects/{projectId}/tasks`: List all tasks in a project.
- `POST /workspaces/{workspaceId}/projects/{projectId}/tasks`: Create a new task.
- `GET /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}`: Retrieve a specific task.
- `PUT /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}`: Update a specific task.
- `DELETE /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}`: Delete a specific task.

**User:**
- `GET /users`: List all users (for admin).
- `GET /users/{userId}`: Retrieve a specific user.
- `PUT /users/{userId}`: Update a specific user.
- `DELETE /users/{userId}`: Delete a specific user.
- `GET /workspaces/{workspaceId}/users`: List all users in a workspace.

**Comment:**
- `GET /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/comments`: List all comments on a task.
- `POST /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/comments`: Create a new comment on a task.
- `GET /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/comments/{commentId}`: Retrieve a specific comment.
- `PUT /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/comments/{commentId}`: Update a specific comment.
- `DELETE /workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}/comments/{commentId}`: Delete a specific comment.

#### 2. Request

*Response time: 193.3s*

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
To implement the specified `PATCH /workspaces/:workspaceId/tasks/:taskId` endpoint in Node.js + Express + TypeScript, we will follow these steps:

1. Define the validation schema using Zod.
2. Create the Express route handler with the necessary validations and logic.
3. Implement error handling middleware.
4. Write unit tests for the endpoint.

Let's start by defining the validation schema using Zod:

```typescript
import { z } from 'zod';

const taskUpdateSchema = z.object({
  title: z.string().min(1).max(200).optional(),
  status: z.enum(['todo', 'in_progress', 'done', 'cancelled']).optional(),
  assignee_id: z.union([z.number(), z.null()]).optional(),
  due_date: z.union([z.string().datetime({ offset: true }), z.null()]).optional(),
});

const paramsSchema = z.object({
  workspaceId: z.coerce.number().int().positive(),
  taskId: z.coerce.number().int().positive(),
});
```

Next, we will create the Express route handler:

```typescript
import express from 'express';
import { taskUpdateSchema, paramsSchema } from './validation'; // Adjust the import path as necessary
import { Task, Workspace, User } from './models'; // Adjust the import path as necessary

const router = express.Router();

router.patch('/workspaces/:workspaceId/tasks/:taskId', async (req, res, next) => {
  try {
    const { workspaceId, taskId } = paramsSchema.parse(req.params);
    const { title, status, assignee_id, due_date } = taskUpdateSchema.parse(req.body);

    const workspace = await Workspace.findByPk(workspaceId);
    if (!workspace) {
      return res.status(404).json({ error: 'Workspace not found' });
    }

    const task = await Task.findByPk(taskId);
    if (!task || task.workspaceId !== workspaceId) {
      return res.status(404).json({ error: 'Task not found' });
    }

    if (assignee_id !== undefined) {
      const assignee = await User.findByPk(assignee_id);
      if (!assignee || !workspace.members.includes(assignee_id)) {
        return res.status(400).json({ error: 'Invalid assignee' });
      }
    }

    if (status === 'cancelled') {
      const openSubtasks = await Task.count({ where: { parentId: taskId, status: { [Op.notIn]: ['done', 'cancelled'] } } });
      if (openSubtasks > 0) {
        return res.status(409).json({ error: 'Cannot cancel task with open subtasks' });
      }
    }

    await task.update({ title, status, assignee_id, due_date });
    res.json(task);
  } catch (error) {
    next(error);
  }
});

export default router;
```

Now, we'll implement the error handling middleware:

```typescript
import { Request, Response, NextFunction } from 'express';
import { ZodError } from 'zod';

function errorHandler(err: any, req: Request, res: Response, next: NextFunction) {
  if (err instanceof ZodError) {
    return res.status(400).json({ errors: err.issues.map(issue => ({ field: issue.path.join('.'), message: issue.message })) });
  }

  if (err.status) {
    return res.status(err.status).json({ error: err.message });
  }

  console.error(err);
  res.status(500).json({ error: 'Internal server error' });
}

export default errorHandler;
```

Finally, we'll write the unit tests. For simplicity, we'll use Jest and Supertest.

```typescript
import request from 'supertest';
import app from './app'; // Adjust the import path as necessary
import { Task, Workspace, User } from './models'; // Adjust the import path as necessary
import { sequelize } from './sequelize'; // Adjust the import path as necessary

describe('PATCH /workspaces/:workspaceId/tasks/:taskId', () => {
  beforeAll(async () => {
    await sequelize.sync({ force: true });
  });

  afterEach(async () => {
    await Task.destroy({ where: {} });
    await Workspace.destroy({ where: {} });
    await User.destroy({ where: {} });
  });

  it('should update task successfully', async () => {
    const workspace = await Workspace.create({ name: 'Test Workspace' });
    const user = await User.create({ name: 'John Doe' });
    await workspace.addMember(user);
    const task = await Task.create({ title: 'Initial Title', status: 'todo', workspaceId: workspace.id, assignee_id: user.id });

    const response = await request(app)
      .patch(`/workspaces/${workspace.id}/tasks/${task.id}`)
      .send({ title: 'Updated Title', status: 'done' });

    expect(response.status).toBe(200);
    expect(response.body.title).toBe('Updated Title');
    expect(response.body.status).toBe('done');
  });

  it('should return 400 on validation error', async () => {
    const workspace = await Workspace.create({ name: 'Test Workspace' });
    const user = await User.create({ name: 'John Doe' });
    await workspace.addMember(user);
    const task = await Task.create({ title: 'Initial Title', status: 'todo', workspaceId: workspace.id, assignee_id: user.id });

    const response = await request(app)
      .patch(`/workspaces/${workspace.id}/tasks/${task.id}`)
      .send({ title: 'a'.repeat(201) });

    expect(response.status).toBe(400);
    expect(response.body.errors).toHaveLength(1);
    expect(response.body.errors[0].field).toBe('title');
  });

  it('should return 404 if task not found', async () => {
    const response = await request(app)
      .patch('/workspaces/1/tasks/1')
      .send({ title: 'Updated Title' });

    expect(response.status).toBe(404);
    expect(response.body.error).toBe('Workspace not found');
  });

  it('should return 409 if trying to cancel task with open subtasks', async () => {
    const workspace = await Workspace.create({ name: 'Test Workspace' });
    const user = await User.create({ name: 'John Doe' });
    await workspace.addMember(user);
    const task = await Task.create({ title: 'Initial Title', status: 'todo', workspaceId: workspace.id, assignee_id: user.id });
    const subtask = await Task.create({ title: 'Subtask', status: 'todo', workspaceId: workspace.id, parentId: task.id });

    const response = await request(app)
      .patch(`/workspaces/${workspace.id}/tasks/${task.id}`)
      .send({ status: 'cancelled' });

    expect(response.status).toBe(409);
    expect(response.body.error).toBe('Cannot cancel task with open subtasks');
  });
});
```

This implementation covers the requirements and includes a basic setup for the application structure. Adjust the import paths and database models as necessary for your project.

*Response time: 548.8s*

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
To implement a complete authentication system in Node.js with Express and TypeScript, you'll need to set up several components: a user model, routes for registration, login, and protected routes, middleware for authentication, and JWT handling. Below is a step-by-step implementation:

### Step 1: Set up the project

First, initialize your project:

```bash
mkdir auth-system
cd auth-system
npm init -y
npm install express bcryptjs jsonwebtoken cookie-parser @types/express @types/bcryptjs @types/jsonwebtoken @types/cookie-parser typescript ts-node-dev
npx tsc --init
```

### Step 2: Create a basic Express server

Create a `src` directory and a `server.ts` file:

```typescript
// src/server.ts
import express from 'express';
import cookieParser from 'cookie-parser';
import 'dotenv/config';

const app = express();
app.use(express.json());
app.use(cookieParser());

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

### Step 3: Set up environment variables

Create a `.env` file to store your secret keys:

```
JWT_ACCESS_SECRET=your_access_secret_key
JWT_REFRESH_SECRET=your_refresh_secret_key
```

### Step 4: Create a User Model

Create a `models/User.ts` file:

```typescript
// src/models/User.ts
export interface User {
  id: number;
  email: string;
  password: string;
  role: string;
}

export const users: User[] = []; // In-memory user store for simplicity
```

### Step 5: Implement Authentication Routes

Create an `auth` directory and `authController.ts` file:

```typescript
// src/auth/authController.ts
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { users } from '../models/User';
import { Request, Response } from 'express';
import dotenv from 'dotenv';

dotenv.config();

const ACCESS_TOKEN_SECRET = process.env.JWT_ACCESS_SECRET!;
const REFRESH_TOKEN_SECRET = process.env.JWT_REFRESH_SECRET!;

export const register = async (req: Request, res: Response) => {
  const { email, password } = req.body;

  if (!email || !password) {
    return res.status(400).json({ message: 'Email and password are required' });
  }

  const hashedPassword = await bcrypt.hash(password, 12);
  const user: User = { id: users.length + 1, email, password: hashedPassword, role: 'user' };
  users.push(user);

  res.status(201).json({ id: user.id, email: user.email, role: user.role });
};

export const login = async (req: Request, res: Response) => {
  const { email, password } = req.body;

  if (!email || !password) {
    return res.status(400).json({ message: 'Email and password are required' });
  }

  const user = users.find(u => u.email === email);
  if (!user) {
    return res.status(400).json({ message: 'Invalid credentials' });
  }

  const isPasswordValid = await bcrypt.compare(password, user.password);
  if (!isPasswordValid) {
    return res.status(400).json({ message: 'Invalid credentials' });
  }

  const accessToken = jwt.sign({ userId: user.id, email: user.email, role: user.role }, ACCESS_TOKEN_SECRET, { expiresIn: '15m' });
  const refreshToken = jwt.sign({ userId

*Response time: 260.4s*

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
Let's delve into the implementation details for each of the points you've outlined.

### 1. POST /auth/refresh — Rotate the Refresh Token

#### Implementation Steps:
- Validate the refresh token stored in the cookie.
- If valid, issue a new access token.
- Generate a new refresh token.
- Invalidate the old refresh token.
- Store the new refresh token in Redis with a TTL (Time To Live) strategy.
- Set the new refresh token in the cookie.

#### Example Code:
```python
from flask import request, jsonify, make_response
import jwt
import datetime
import redis

# Assume `redis_client` is a Redis client instance
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

def refresh_token():
    cookie = request.cookies.get('refresh_token')
    if not cookie:
        return jsonify({'message': 'No refresh token in cookie'}), 401

    try:
        payload = jwt.decode(cookie, 'refresh_secret_key', algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Refresh token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid refresh token'}), 401

    user_id = payload['user_id']

    # Check if the refresh token is still valid in Redis
    stored_refresh_token = redis_client.get(f'refresh_token:{user_id}')
    if not stored_refresh_token or stored_refresh_token.decode('utf-8') != cookie:
        return jsonify({'message': 'Refresh token invalid'}), 401

    # Invalidate the old refresh token by deleting it from Redis
    redis_client.delete(f'refresh_token:{user_id}')

    # Generate a new access token
    new_access_token = jwt.encode({
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    }, 'access_secret_key', algorithm='HS256')

    # Generate a new refresh token
    new_refresh_token = jwt.encode({
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
    }, 'refresh_secret_key', algorithm='HS256')

    # Store the new refresh token in Redis with a TTL
    redis_client.setex(f're

*Response time: 173.0s*

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
Certainly! Let's break this down step by step.

### 1. TypeScript Interface for Props

First, we'll define the TypeScript interfaces for the `DataTable` component props. This will be generic to work with any row type.

```typescript
import React from 'react';

type SortDirection = 'asc' | 'desc' | 'none';

interface ColumnDefinition<T> {
  key: keyof T;
  header: string;
  width?: number;
  sortable?: boolean;
  renderCell?: (rowData: T) => React.ReactNode;
}

interface DataTableProps<T> {
  columns: ColumnDefinition<T>[];
  data: T[];
  currentPage?: number;
  pageSize?: number;
  onSort?: (columnKey: keyof T, direction: SortDirection) => void;
  onSelectRow?: (selectedRows: T[]) => void;
  onSelectAll?: (selectAll: boolean) => void;
  onPageChange?: (page: number) => void;
  onPageSizeChange?: (pageSize: number) => void;
}
```

### 2. Complete Component Implementation

Here's the complete implementation of the `DataTable` component:

```typescript
import React, { useState, useMemo, useCallback } from 'react';

const DataTable = <T,>({
  columns,
  data,
  currentPage = 1,
  pageSize = 10,
  onSort,
  onSelectRow,
  onSelectAll,
  onPageChange,
  onPageSizeChange,
}: DataTableProps<T>) => {
  const [sortConfig, setSortConfig] = useState<{ key: keyof T; direction: SortDirection }>({
    key: columns.find(col => col.sortable)?.key || (columns[0].key as keyof T),
    direction: 'none',
  });
  const [selectedRows, setSelectedRows] = useState<T[]>([]);

  const sortedData = useMemo(() => {
    let sortableData = [...data];
    if (sortConfig.direction !== 'none') {
      sortableData.sort((a, b) => {
        if (a[sortConfig.key] < b[sortConfig.key]) {
          return sortConfig.direction === 'asc' ? -1 : 1;
        }
        if (a[sortConfig.key] > b[sortConfig.key]) {
          return sortConfig.direction === 'asc' ? 1 : -1;
        }
        return 0;
      });
    }
    return sortableData;
  }, [data, sortConfig]);

  const handleSort = useCallback(
    (key: keyof T) => {
      let direction: SortDirection = 'asc';
      if (sortConfig.key === key) {
        if (sortConfig.direction === 'asc') {
          direction = 'desc';
        } else if (sortConfig.direction === 'desc') {
          direction = 'none';
        }
      }
      setSortConfig({ key, direction });
      onSort?.(key, direction);
    },
    [sortConfig, onSort]
  );

  const handleSelectRow = useCallback(
    (row: T) => {
      const newSelectedRows = selectedRows.includes(row)
        ? selectedRows.filter(r => r !== row)
        : [...selectedRows, row];
      setSelectedRows(newSelectedRows);
      onSelectRow?.(newSelectedRows);
    },
    [selectedRows, onSelectRow]
  );

  const handleSelectAll = useCallback(() => {
    const newSelectedRows = selectedRows.length === data.length ? [] : [...data];
    setSelectedRows(newSelectedRows);
    onSelectAll?.(newSelectedRows.length === data.length);
  }, [data, selectedRows, onSelectAll]);

  const handlePageChange = useCallback(
    (page: number) => {
      onPageChange?.(page);
    },
    [onPageChange]
  );

  const handlePageSizeChange = useCallback(
    (pageSize: number) => {
      onPageSizeChange?.(pageSize);
    },
    [onPageSizeChange]
  );

  const paginatedData = useMemo(() => {
    const startIndex = (currentPage - 1) * pageSize;
    return sortedData.slice(startIndex, startIndex + pageSize);
  }, [sortedData, currentPage, pageSize]);

  return (
    <div>
      <table>
        <thead>
          <tr>
            <th>
              <input
                type="checkbox"
                checked={selectedRows.length === data.length}
                onChange={handleSelectAll}
              />
            </th>
            {columns.map(column => (
              <th
                key={column.key.toString()}
                style={{ width: column.width ? `${column.width}px` : undefined }}
                onClick={() => column.sortable && handleSort(column.key)}
              >
                {column.header}
                {column.sortable && (
                  <span>
                    {sortConfig.key === column.key && sortConfig.direction === 'asc' ? ' 🔼' : ''}
                    {sortConfig.key === column.key && sortConfig.direction === 'desc' ? ' 🔽' : ''}
                  </span>
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {paginated

*Response time: 373.3s*

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
Sure, let's break down the implementation step-by-step.

### 1. Custom Hook `useSearch(query: string)`

This hook will handle fetching, debouncing, caching, and cancellation of requests. We'll use the `useEffect` and `useState` hooks for this purpose. Here's how we can implement it:

```jsx
import { useState, useEffect, useCallback } from 'react';

const useSearch = (query) => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [cache, setCache] = useState({});

  // Function to fetch results
  const fetchResults = useCallback(async (q) => {
    const cachedResult = cache[q];
    if (cachedResult) {
      setResults(cachedResult);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      setResults(data);
      setCache((prevCache) => ({ ...prevCache, [q]: data }));
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  }, [query, cache]);

  // Debounce logic
  useEffect(() => {
    let debounceTimeout;

    if (query) {
      debounceTimeout = setTimeout(() => {
        fetchResults(query);
      }, 300);
    } else {
      setResults([]);
    }

    return () => clearTimeout(debounceTimeout);
  }, [query, fetchResults]);

  // Cancel in-flight requests
  useEffect(() => {
    let controller = new AbortController();

    const fetchWithAbort = async (q) => {
      try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(q)}`, { signal: controller.signal });
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        setResults(data);
        setCache((prevCache) => ({ ...prevCache, [q]: data }));
      } catch (err) {
        if (!controller.signal.aborted) {
          setError(err.message);
        }
      } finally {
        setLoading(false);
      }
    };

    if (query) {
      setLoading(true);
      setError(null);
      fetchWithAbort(query);
    } else {
      setResults([]);
    }

    return () => controller.abort();
  }, [query]);

  return { results, loading, error };
};

export default useSearch;
```

### 2. SearchPage Component

This component will use the `useSearch` hook and handle URL sync using the `useLocation` and `useHistory` hooks from `react-router-dom`.

```jsx
import { useEffect, useState } from 'react';
import { useLocation, useHistory } from 'react-router-dom';
import useSearch from './useSearch';

const SearchPage = () => {
  const history = useHistory();
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const initialQuery = queryParams.get('q') || '';
  const [query, setQuery] = useState(initialQuery);
  const { results, loading, error } = useSearch(query);

  useEffect(() => {
    const newQueryParams = new URLSearchParams();
    if (query) {
      newQueryParams.append('q', query);
    }
    history.push({ search: newQueryParams.toString() });
  }, [query, history]);

  return (
    <div>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search..."
      />
      {loading && <div>Loading...</div>}
      {error && (
        <div>
          {error}{' '}
          <button onClick={() => useSearch(query)}>Retry</button>
        </div>
      )}
      {results.length === 0 && !loading && !error && <div>No results</div>}
      {results.length > 0 && (
        <ul>
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

The `SearchPage` component uses the `useHistory` and `useLocation` hooks to keep the URL in sync with the search query. When the query changes, the URL is updated accordingly, and vice versa when navigating back and forth.

### 4. Why Cancelling In-Flight Requests is Important

Cancelling in-flight requests is important to prevent race conditions. Imagine the following scenario:

1. User types "foo" in the search box.
2. A request is sent to fetch results for "foo".
3. User types "bar" before the response for "foo" is received.
4. A request is sent to fetch results for "bar".
5. The response for "bar" is received first and displayed.
6. The response for "foo" is received after and overwrites the results for "bar".

By cancelling the in-flight request when a new search starts, we ensure that only the results for the most recent query are displayed, preventing outdated or incorrect data from being shown to the user.

*Response time: 425.1s*

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
Sure, let's go through each of your requests step by step:

### 1. Fetching the 10 most recent published posts with author name, tag names, and comment count (not the comments themselves)

To fetch the required data efficiently, we can use Prisma's `include` and `select` features along with aggregation functions to avoid N+1 queries. Here's how you can write the query:

```typescript
const recentPosts = await prisma.post.findMany({
  where: { published: true },
  orderBy: { createdAt: 'desc' },
  take: 10,
  select: {
    id: true,
    title: true,
    content: true,
    createdAt: true,
    author: { select: { email: true } },  // Assuming you want the author's email as the name
    tags: { select: { name: true } },
    _count: { select: { comments: true } },
  },
});
```

### 2. Migration scenario: Adding a `slug` field to `Post`

Adding a non-nullable `slug` field to a table with 10M rows can be tricky to do without downtime. Here's a safe step-by-step process:

1. **Add a nullable `slug` field**: First, add the `slug` field as nullable to allow existing rows to exist without it.
   
   ```prisma
   model Post {
     id        Int       @id
     title     String
     content   String
     published Boolean   @default(false)
     authorId  Int
     author    User      @relation(fields: [authorId], references: [id])
     tags      Tag[]
     comments  Comment[]
     createdAt DateTime  @default(now())
     slug      String?   // Initially nullable
   }
   ```

2. **Run the migration**: This will add the `slug` column to the `Post` table without affecting existing data.
   
   ```bash
   npx prisma migrate dev --name add_slug_to_post
   ```

3. **Populate the `slug` field**: Write a script to populate the `slug` field for all existing posts. You might want to run this in batches to avoid locking the table for too long.
   
   ```typescript
   const batchSize = 1000;
   let offset = 0;

   async function populateSlugs() {
     while (true) {
       const posts = await prisma.post.findMany({
         where: { slug: null },
         take: batchSize,
         skip: offset,
       });

       if (posts.length === 0) break;

       const updates = posts.map(post => ({
         where: { id: post.id },
         data: { slug: generateSlug(post.title) },  // You'll need to implement generateSlug
       }));

       await prisma.$transaction(updates.map(update => prisma.post.update(update)));

       offset += batchSize;
     }
   }

   populateSlugs().then(() => console.log('Slugs populated successfully'));
   ```

4. **Make the `slug` field non-nullable**: Once all posts have slugs, you can make the field non-nullable.
   
   ```prisma
   model Post {
     id        Int       @id
     title     String
     content   String
     published Boolean   @default(false)
     authorId  Int
     author    User      @relation(fields: [authorId], references: [id])
     tags      Tag[]
     comments  Comment[]
     createdAt DateTime  @default(now())
     slug      String    @unique  // Now non-nullable and unique
   }
   ```

5. **Run the migration**: This will enforce the `slug` field to be non-nullable.
   
   ```bash
   npx prisma migrate dev --name make_slug_non_nullable
   ```

### 3. Diagnosing and fixing slow query for `findMany` posts filtered by tag name

Let's start by writing the Prisma query and then look at the raw SQL generated.

#### Prisma Query

```typescript
const posts = await prisma.post.findMany({
  where: {
    tags: {
      some: {
        name: 'someTagName',
      },
    },
  },
  include: {
    tags: true,
  },
});
```

#### Raw SQL

The above Prisma query might translate to something like this in raw SQL:

```sql
SELECT *
FROM "Post"
WHERE EXISTS (
  SELECT 1
  FROM "_PostToTag"
  INNER JOIN "Tag" ON "_PostToTag"."B" = "Tag"."id"
  WHERE "_PostToTag"."A" = "Post"."id"
  AND "Tag"."name" = 'someTagName'
)
```

#### Diagnosing the Slow Query

To diagnose why the query is slow, you can use the `EXPLAIN` statement in PostgreSQL to see the execution plan:

```sql
EXPLAIN SELECT *
FROM "Post"
WHERE EXISTS (
  SELECT 1
  FROM "_PostToTag"
  INNER JOIN "Tag" ON "_PostToTag"."B" = "Tag"."id"
  WHERE "_PostToTag"."A" = "Post"."id"
  AND "Tag"."name" = 'someTagName'
);
```

You'll look for any full table scans or missing indexes. Based on the execution plan, you might see that the query is slow because it is doing a full scan on the `_PostToTag` and `Tag` tables.

#### Adding an Index

To fix this, you can add an index on the `name` column of the `Tag` table and the `B` column of the `_PostToTag` table:

```sql
CREATE INDEX "Tag_name_idx" ON "Tag"("name");
CREATE INDEX "_PostToTag_B_idx" ON "_PostToTag"("B");
```

Run these SQL commands using Prisma migrations:

```prisma
model Tag {
  id Int @id
  name String @unique
  posts Post[]
}

model _PostToTag {
  A Int
  B Int
  post Post @relation(fields: [A], references: [id])
  tag Tag @relation(fields: [B], references: [id])

  @@id(fields: [A, B])
  @@index([B])  // Add this index
}

@@index([name], name: "Tag_name_idx")  // Add this index
```

Run the migration:

```bash
npx prisma migrate dev --name add_indexes
```

### 4. Dropping down from Prisma to Raw SQL

You might drop down to raw SQL when you need to execute a query that Prisma doesn't support, or when you need to optimize performance for a very complex query. Here's an example:

If you want to get the top 5 most commented posts with their

*Response time: 570.3s*

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
Sure, let's address each part of your request step-by-step.

### 1. Docker Compose for Local Development

Create a `docker-compose.yml` file for local development that includes hot reloading, PostgreSQL with a named volume, Redis, and environment variables from a `.env` file. We'll use a health check to ensure PostgreSQL is ready before starting the backend.

```yaml
version: '3.8'

services:
  frontend:
    image: node:18-alpine
    container_name: react-app
    working_dir: /app
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
      - VITE_API_URL=http://backend:3000
    ports:
      - "3001:3000"
    command: >
      sh -c "npm install && npm run dev"

  backend:
    image: node:18-alpine
    container_name: node-app
    working_dir: /app
    volumes:
      - ./backend:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_NAME=${DB_NAME}
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    ports:
      - "3000:3000"
    command: >
      sh -c "npm install && npm run dev"
    depends_on:
      postgres:
        condition: service_healthy

  postgres:
    image: postgres:13
    container_name: postgres
    environment:
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=${DB_NAME}
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:6
    container_name: redis
    ports:
      - "6379:6379"

volumes:
  postgres-data:
```

### 2. Production Dockerfile for the Backend (Node.js)

Create a `Dockerfile` in the `backend` directory for a multi-stage build that results in a small production image.

```dockerfile
# Stage 1: Build
FROM node:18-alpine AS builder
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy the rest of the application code
COPY . .

# Build the application (if necessary)
# RUN npm run build

# Stage 2: Run
FROM node:18-alpine
WORKDIR /app

# Copy production dependencies from the builder stage
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/dist ./dist

# Create a non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Change ownership of the application directory to the non-root user
RUN chown -R appuser:appgroup /app

# Switch to the non-root user
USER appuser

# Expose the port the app runs on
EXPOSE 3000

# Run the application
CMD ["node", "dist/index.js"]
```

### 3. Backend Crashes with Exit Code 137

Exit code 137 typically indicates that the container was killed by Docker due to an out-of-memory (OOM) condition. To diagnose this:

1. **Check Docker Logs:** Use `docker logs <container_id>` to see any error messages logged before the container was killed.
2. **Monitor Memory Usage:** Use `docker stats` to monitor memory usage in real-time.
3. **Increase Memory Limits:** If the application is genuinely memory-intensive, consider increasing the memory limits in Docker settings.
4. **Profile Memory Usage:** Use profiling tools to identify memory leaks or excessive memory usage within the application.
5. **Optimize Code:** Look for ways to optimize code and reduce memory consumption.

### 4. Zero-Downtime Deployment with Database Schema Change

Deploying a new version with a zero-downtime strategy and handling an additive schema change involves the following steps:

1. **Prepare Database Migration:**
   - Write a migration script to add the new nullable column in the database.
   - Ensure the migration script is idempotent.

2. **Deploy New Backend Version:**
   - Build the new backend image and push it to the container registry.
   - Update the deployment configuration to use the new image version.
   - Use a rolling update strategy to deploy the new version, ensuring that old instances are not terminated until new ones are ready and serving traffic.
   - Monitor the new instances to ensure they are running correctly and handling requests.

3. **Apply Database Migration:**
   - After the new backend version is fully deployed and running, apply the database migration script.
   - Ensure that the migration is applied only once and is safe to run while the application is running.
   - Optionally, you can run the migration script as part of the deployment pipeline if it is safe to do so.

4. **Verify and Rollback if Necessary:**
   - Verify that the application is functioning correctly with the new schema.
   - If any issues are detected, rollback to the previous version and address the problems.
   - Monitor the application and database for any issues that arise from the schema change.

5. **Final Checks:**
   - Ensure that all instances are running the new version and are healthy.
   - Confirm that the database schema change has been applied successfully.

By following these steps, you can ensure a smooth, zero-downtime deployment with an additive schema change.

*Response time: 473.5s*

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
To build a collaborative document editor using Node.js and the `ws` library, we need to address several core functionalities: connection handling, message protocol, broadcasting, reconnection, and handling simultaneous edits. Below is a simplified implementation of the server-side logic.

### 1. Connection Handling
We'll use a `Map` to associate each WebSocket connection with a user and document. Each user will be uniquely identified by a `userId`, and each document will have a `documentId`. We'll store these associations in a `Map`.

### 2. Message Protocol
We'll define the following message types:
- `join`: When a user joins a document.
- `textChange`: When a user makes a text change in the document.
- `cursorMove`: When a user moves their cursor.
- `userLeft`: When a user leaves the document.

### 3. Broadcasting
We'll broadcast messages to all other users in the same document but not back to the sender.

### 4. Reconnection
When a user reconnects, they will send a `join` message again, and we'll send them the latest document state.

### 5. Simultaneous Edits
If two users edit the same position simultaneously, conflicts may arise. Solutions include Operational Transformation (OT) and Conflict-Free Replicated Data Types (CRDT). For simplicity, we won't implement these here, but we'll acknowledge the issue.

### Core Server Implementation

```javascript
const WebSocket = require('ws');

const wss = new WebSocket.Server({ port: 8080 });

// Map to store document state
const documents = new Map();

// Map to store user connections
const userConnections = new Map();

wss.on('connection', (ws) => {
  ws.on('message', (message) => {
    const data = JSON.parse(message);

    switch (data.type) {
      case 'join':
        handleJoin(ws, data.userId, data.documentId);
        break;
      case 'textChange':
        handleTextChange(ws, data.userId, data.documentId, data.change);
        break;
      case 'cursorMove':
        handleCursorMove(ws, data.userId, data.documentId, data.position);
        break;
      case 'userLeft':
        handleUserLeft(ws, data.userId, data.documentId);
        break;
      default:
        console.log('Unknown message type:', data.type);
    }
  });

  ws.on('close', () => {
    // Handle user disconnection
    for (const [documentId, users] of userConnections.entries()) {
      for (const [userId, connection] of users.entries()) {
        if (connection === ws) {
          handleUserLeft(ws, userId, documentId);
          return;
        }
      }
    }
  });
});

function handleJoin(ws, userId, documentId) {
  if (!documents.has(documentId)) {
    documents.set(documentId, { content: '', users: new Map() });
  }

  const document = documents.get(documentId);
  document.users.set(userId, ws);

  if (!userConnections.has(userId)) {
    userConnections.set(userId, new Map());
  }

  userConnections.get(userId).set(documentId, ws);

  // Send the latest document content to the user
  ws.send(JSON.stringify({ type: 'documentState', content: document.content }));

  // Broadcast to other users in the document
  broadcastToOthers(ws, documentId, { type: 'userJoined', userId });
}

function handleTextChange(ws, userId, documentId, change) {
  const document = documents.get(documentId);
  document.content = applyChange(document.content, change);

  // Broadcast the change to all other users in the document
  broadcastToOthers(ws, documentId, { type: 'textChange', userId, change });
}

function handleCursorMove(ws, userId, documentId, position) {
  // Broadcast the cursor move to all other users in the document
  broadcastToOthers(ws, documentId, { type: 'cursorMove', userId, position });
}

function handleUserLeft(ws, userId, documentId) {
  const document = documents.get(documentId);
  document.users.delete(userId);

 

*Response time: 289.2s*

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
Sure, let's tackle each part of your request step by step.

### 1. GraphQL Schema (SDL)

Here's the complete GraphQL schema for your recipe platform:

```graphql
type Ingredient {
  name: String!
  amount: Float!
  unit: String!
}

type Rating {
  score: Float!
  comment: String
}

type Author {
  id: ID!
  name: String!
  bio: String
}

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

type Query {
  recipes(filter: RecipeFilter, pagination: Pagination): [Recipe!]!
}

type Mutation {
  addRating(recipeId: ID!, score: Float!, comment: String): Recipe!
}

input RecipeFilter {
  tag: String
  minRating: Float
}

input Pagination {
  page: Int
  limit: Int
}
```

### 2. Resolvers

Here are the resolvers for the specified operations:

```javascript
const DataLoader = require('dataloader');

// Assuming you have a data source like this:
const { getRecipes, getAuthorById, addRating } = require('./data-source');

const authorLoader = new DataLoader(async (authorIds) => {
  const authors = await Promise.all(authorIds.map(getAuthorById));
  return authors;
});

const resolvers = {
  Query: {
    recipes: async (_, { filter, pagination }) => {
      let recipes = await getRecipes(filter, pagination);
      return recipes;
    },
  },
  Mutation: {
    addRating: async (_, { recipeId, score, comment }) => {
      return addRating(recipeId, score, comment);
    },
  },
  Recipe: {
    averageRating: (recipe) => {
      if (!recipe.ratings || recipe.ratings.length === 0) return 0;
      const total = recipe.ratings.reduce((sum, rating) => sum + rating.score, 0);
      return total / recipe.ratings.length;
    },
    author: async (recipe) => {
      return authorLoader.load(recipe.authorId);
    },
  },
};

module.exports = resolvers;
```

### 3. N+1 Problem and Fix with DataLoader

**N+1 Problem Example:**

Imagine we have a query fetching 10 recipes and their authors. The resolver would look something like this:

```javascript
Recipe: {
  author: (recipe) => getAuthorById(recipe.authorId),
}
```

In this case, for each recipe, the resolver will call `getAuthorById`, leading to 10 calls to the database.

**Fix with DataLoader:**

Using DataLoader, we batch and cache the author fetching calls. This is already implemented in the resolvers above with `authorLoader`. DataLoader batches multiple calls into one and caches results, thus reducing the number of database calls from N+1 to 2 (one for the recipes and one for the authors).

### 4. GraphQL Query for Specific Data

The client wants to fetch the recipe title, author name, and the first 3 ingredients. Here is the exact GraphQL query they would write:

```graphql
query {
  recipes {
    title
    author {
      name
    }
    ingredients(limit: 3) {
      name
      amount
      unit
    }
  }
}
```

### 5. Choosing GraphQL over REST and Vice Versa

**When to Choose GraphQL:**

- **Complex Data Fetching:** When clients need to fetch complex, nested data in a single request.
- **Efficient Data Retrieval:** When you want to avoid over-fetching or under-fetching data.
- **Single Endpoint:** When a unified API endpoint is desired for all data operations.
- **Real-time Data:** When real-time data subscription capabilities are needed.

**When NOT to Choose GraphQL:**

- **Performance:** When performance is critical and every millisecond counts, as GraphQL can add complexity to the server.
- **Tooling Ecosystem:** When your team is not familiar with GraphQL and the additional tooling it requires.
- **Simplicity:** For simple APIs where REST might be more straightforward and easier to understand.
- **Legacy Systems:** When integrating with legacy systems that are tightly coupled with REST.

GraphQL and REST each have their strengths and are suitable for different scenarios. Choosing the right one depends on the specific requirements and constraints of your project.

*Response time: 307.9s*

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
To achieve the specified UI layout, we will use a combination of CSS Flexbox and Grid. Flexbox is ideal for creating the main layout that involves the header, sidebar, and main content. CSS Grid will be used for the responsive card layout within the main content area.

### HTML Structure

Here is the HTML structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Responsive UI Layout</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        HEADER
    </header>
    <div class="container">
        <aside class="sidebar">
            SIDEBAR
        </aside>
        <main class="main-content">
            <div class="card-grid">
                <div class="card">
                    <div class="card-image"></div>
                    <div class="card-title">Title 1</div>
                    <div class="card-description">Description 1</div>
                    <div class="card-footer">
                        <button class="left-button">Left</button>
                        <button class="right-button">Right</button>
                    </div>
                </div>
                <div class="card">
                    <div class="card-image"></div>
                    <div class="card-title">Title 2</div>
                    <div class="card-description">Description 2</div>
                    <div class="card-footer">
                        <button class="left-button">Left</button>
                        <button class="right-button">Right</button>
                    </div>
                </div>
                <div class="card">
                    <div class="card-image"></div>
                    <div class="card-title">Title 3</div>
                    <div class="card-description">Description 3</div>
                    <div class="card-footer">
                        <button class="left-button">Left</button>
                        <button class="right-button">Right</button>
                    </div>
                </div>
                <div class="card">
                    <div class="card-image"></div>
                    <div class="card-title">Title 4</div>
                    <div class="card-description">Description 4</div>
                    <div class="card-footer">
                        <button class="left-button">Left</button>
                        <button class="right-button">Right</button>
                    </div>
                </div>
            </div>
        </main>
    </div>
</body>
</html>
```

### CSS Styles

Here is the CSS to style the layout:

```css
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
    width: 100%;
    height: 60px;
    background-color: #333;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.container {
    display: flex;
    margin-top: 60px; /* Height of the header */
    height: calc(100vh - 60px);
}

.sidebar {
    width: 240px;
    background-color: #f4f4f4;
    overflow-y: auto;
    padding: 20px;
}

.main-content {
    flex: 1;
    background-color: #fff;
    overflow-y: auto;
    padding: 20px;
}

.card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
}

.card {
    border: 1px solid #ddd;
    border-radius: 5px;
    overflow: hidden;
}

.card-image {
    position: relative;
    width: 100%;
    padding-top: 56.25%; /* 16:9 Aspect Ratio */
    background-color: #ccc;
}

.card-title {
    padding: 10px;
    font-size: 18px;
    font-weight: bold;
}

.card-description {
    padding: 0 10px 10px;
    font-size: 14px;
    color: #555;
}

.card-footer {
    display: flex;
    justify-content: space-between;
    padding: 10px;
    background-color: #f9f9f9;
    border-top: 1px solid #ddd;
}

button {
    padding: 8px 16px;
    border: none;
    background-color: #007bff;
    color: white;
    cursor: pointer;
    border-radius: 3px;
}

button:hover {
    background-color: #0056b3;
}

.left-button {
    align-self: flex-start;
}

.right-button {
    align-self: flex-end;
}
```

### Explanation of Layout Approach

1. **Header**: The header is fixed at the top using `position: fixed`, and it spans the full width of the viewport. We set a height of 60px and use Flexbox to center the content both vertically and horizontally.

2. **Container**: The `.container` div is a flex container that holds the sidebar and the main content. The `margin-top` is set to 60px to ensure that the content does not overlap with the fixed header. The height is calculated to fill the remaining viewport height below the header.

3. **Sidebar**: The sidebar has a fixed width of 240px and uses `overflow-y: auto` to allow scrolling if the content exceeds the viewport height. Padding is added for better spacing.

4. **Main Content**: The main content area is a flex item that takes up the remaining space using `flex: 1`. It also uses `overflow-y: auto` to allow independent scrolling. Padding is added for better spacing.

5. **Card Grid**: The `.card-grid` uses CSS Grid to create a responsive layout for the cards. The `grid-template-columns` property with `repeat(auto-fill, minmax(250px, 1fr))` ensures that there are at least 2 columns on larger screens and a single column on smaller screens (≤768px).

6. **Cards**: Each card has a 16:9 aspect ratio image, a title, a description, and a footer with two buttons. The footer uses Flexbox to align the buttons to the left and right.

This layout approach leverages the strengths of both Flexbox and Grid to achieve a responsive and flexible design without the need for JavaScript or CSS frameworks.

*Response time: 518.8s*

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

#### WebSocket
**Pros:**
- Full-duplex communication, allowing real-time data exchange.
- Low latency and efficient data transfer, especially beneficial for real-time updates.

**Cons:**
- Requires a persistent connection, which can be resource-intensive for a large number of users.

#### Server-Sent Events (SSE)
**Pros:**
- Simpler to implement than WebSockets for server-to-client communication.
- Better support for long-lived connections without the overhead of maintaining a full-duplex connection.

**Cons:**
- Not suitable for client-to-server communication.
- Less efficient for bidirectional communication.

#### Polling
**Pros:**
- Simple and easy to implement.

**Cons:**
- High latency and high server load, especially with frequent polling intervals.
- Inefficient for real-time updates.

#### Push Notifications
**Pros:**
- Suitable for mobile users to receive notifications even when the app is closed.
- Can be used alongside other mechanisms for web users.

**Cons:**
- Requires additional setup and handling for different platforms (iOS, Android).
- Limited by platform-specific restrictions and limitations.

**Conclusion:**
For real-time notifications in a web-based project management tool, **WebSockets** would be the best choice due to its efficiency and real-time capabilities. For mobile users, **push notifications** should be used in conjunction with WebSockets.

### 2. Database Schema for Notifications

```sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    -- other user fields
);

CREATE TABLE tasks (
    task_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    deadline TIMESTAMP,
    assigned_user_id INT,
    FOREIGN KEY (assigned_user_id) REFERENCES users(user_id)
);

CREATE TABLE notifications (
    notification_id SERIAL PRIMARY KEY,
    user_id INT,
    task_id INT,
    notification_type VARCHAR(50), -- e.g., 'task_assigned', 'comment_added', 'deadline_approaching'
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (task_id) REFERENCES tasks(task_id)
);

CREATE TABLE comments (
    comment_id SERIAL PRIMARY KEY,
    task_id INT,
    user_id INT,
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

### 3. Handling Offline Users

When a user is offline, their notifications should be stored in the `notifications` table and marked as `is_read = FALSE`. When the user comes back online, the application should fetch and display all unread notifications to them. To ensure efficiency, this can be handled using a combination of database queries and WebSockets:

1. **On User Login:**
   - Fetch all unread notifications for the user from the database.
   - Send these notifications to the user via WebSocket.

2. **On Notification Creation:**
   - If the user is online, send the notification via WebSocket.
   - If the user is offline, store the notification in the database.

### 4. Implementing the Deadline Check

**Cron Job:**
- **Pros:** Simple to implement and manage.
- **Cons:** Can be less efficient if there are many tasks to process in a short time.

**Queue (e.g., RabbitMQ, AWS SQS):**
- **Pros:** Can handle tasks asynchronously and scale better.
- **Cons:** Requires additional setup and management.

**Event-Driven (e.g., AWS Lambda, Google Cloud Functions):**
- **Pros:** Can handle tasks in a serverless manner without managing infrastructure.
- **Cons:** Cost can be higher, and cold start latency might be an issue.

**Conclusion:**
For a scalable and efficient implementation, **using a queue system** like RabbitMQ or AWS SQS would be the best choice. Here’s an example using RabbitMQ:

1. **Create a Task:**
   - When a task is created or updated, enqueue a message with the task ID and deadline.

2. **Worker Process:**
   - A worker process listens to the queue and processes messages.
   - For each message, check if the deadline is within 24 hours.
   - If it is, create a notification for the assigned user.

**Example Code (Python with Pika for RabbitMQ):**

```python
import pika
import datetime
import psycopg2
from psycopg2 import extras

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='task_deadlines')

# Connect to PostgreSQL
db_connection = psycopg2.connect(database="project_management", user="user", password="password", host="127.0.0.1", port="5432")
cursor = db_connection.cursor(cursor_factory=extras.DictCursor)

def check_task_deadlines():
    cursor.execute("SELECT task_id, assigned_user_id, deadline FROM tasks WHERE deadline >= NOW() AND deadline < NOW() + INTERVAL '24 hours'")
    tasks = cursor.fetchall()
    for task in tasks:
        cursor.execute("INSERT INTO notifications (user_id, task_id, notification_type, message) VALUES (%s, %s, %s, %s)",
                       (task['assigned_user_id'], task['task_id'], 'deadline_approaching', f'Task deadline is approaching: {task["deadline"]}.'))
    db_connection.commit()

def callback(ch, method, properties, body):
    task_id = body
    check_task_deadlines()
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue='task_deadlines', on_message_callback=callback)
print('Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
```

### 5. Scaling for 100,000 Concurrent Users

**WebSockets:**
- Use WebSocket servers that can handle large numbers of connections, such as `Socket.IO` with a scalable backend.
- Deploy WebSocket servers behind a load balancer to distribute connections evenly.

**Database:**
- Use a scalable database solution like Amazon Aurora, Google Cloud SQL, or a managed PostgreSQL service.
- Implement database sharding or partitioning if necessary.

**Queues:**
- Use a managed queue service like AWS SQS or RabbitMQ in a clustered configuration.

**Event-Driven Architecture:**
- Use serverless functions for handling notifications, which can scale automatically.

**Additional Considerations:**
- Implement caching strategies (e.g., Redis) to reduce database load.
- Use a content delivery network (CDN) to serve static assets efficiently.
- Monitor and optimize performance regularly to handle increased load.

By implementing these strategies, the notification system can efficiently scale to handle 100,000 concurrent users.

*Response time: 530.8s*

---
